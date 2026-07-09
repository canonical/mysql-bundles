#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the terraform module."""

import base64
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from pytest_operator.plugin import OpsTest

from .helpers import get_app_statuses

logger = logging.getLogger(__name__)

unknown_apps = [
    "mysql-router",
]
active_apps = [
    "mysql",
    "s3-integrator",
]
blocked_apps = []

TIMEOUT = 20 * 60
SHORT_TIMEOUT = 5 * 60


async def ensure_statuses(ops_test: OpsTest) -> None:
    """Ensure expected statuses of applications."""
    logger.info(f"Waiting for active: {', '.join(active_apps)}")
    await ops_test.model.block_until(
        lambda: get_app_statuses(ops_test, active_apps) == {"active"},
        timeout=TIMEOUT,
    )

    if blocked_apps:
        logger.info(f"Waiting for blocked: {', '.join(blocked_apps)}")
        await ops_test.model.block_until(
            lambda: get_app_statuses(ops_test, blocked_apps) == {"blocked"},
            timeout=SHORT_TIMEOUT,
        )

    if unknown_apps:
        logger.info(f"Waiting for unknown: {', '.join(unknown_apps)}")
        await ops_test.model.block_until(
            lambda: get_app_statuses(ops_test, unknown_apps) == {"unknown"},
            timeout=SHORT_TIMEOUT,
        )


TF_BINARY = os.getenv("TF_BINARY") or "terraform"


@pytest.mark.abort_on_fail
async def test_terraform(ops_test: OpsTest) -> None:
    """Deploy terraform module with app."""
    model_info = subprocess.check_output(
        ["juju", "show-model", ops_test.model.name],
        text=True,
        input=None,
    )
    model_uuid = subprocess.check_output(
        ["yq", f'."{ops_test.model.name}"."model-uuid"'],
        text=True,
        input=model_info,
    ).strip()

    credentials = json.dumps({
        "access_key": os.getenv("AWS_ACCESS_KEY"),
        "secret_key": os.getenv("AWS_SECRET_KEY"),
    })

    if not shutil.which(TF_BINARY):
        pytest.skip(f"{TF_BINARY} not found on PATH")

    s3_config = {}
    if endpoint := os.getenv("AWS_ENDPOINT_URL"):
        s3_config["endpoint"] = endpoint
    if ca_cert := os.getenv("CA_CERT"):
        ca_path = Path(ca_cert)
        ca_pem = ca_path.read_text() if ca_path.exists() else ca_cert
        s3_config["tls-ca-chain"] = base64.b64encode(ca_pem.encode()).decode()

    storage_size = os.getenv("TF_MYSQL_STORAGE_SIZE")

    apply_args = [
        TF_BINARY,
        "apply",
        "-auto-approve",
        "-var",
        f"model={model_uuid}",
        "-var",
        f"s3_integrator_credentials={credentials}",
    ]
    if storage_size:
        apply_args.extend(["-var", f"mysql_server={json.dumps({'storage_size': storage_size})}"])
    if s3_config:
        apply_args.extend(["-var", f"s3_integrator={json.dumps({'config': s3_config})}"])

    logger.info("Deploying terraform module")
    subprocess.run(
        [TF_BINARY, "init"],
        cwd="terraform",
        check=True,
        timeout=10 * 60,
    )
    subprocess.run(
        apply_args,
        cwd="terraform",
        check=True,
        timeout=10 * 60,
    )

    # Terraform deployed apps do not show right away.
    # We must wait before checking for their statuses.
    await ops_test.model.block_until(
        lambda: set(ops_test.model.applications) == {*active_apps, *blocked_apps, *unknown_apps},
        timeout=SHORT_TIMEOUT,
    )

    await ensure_statuses(ops_test)
