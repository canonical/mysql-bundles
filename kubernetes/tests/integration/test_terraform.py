#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the terraform module."""

import json
import logging
import os
import subprocess

import pytest
from pytest_operator.plugin import OpsTest

from .helpers import get_app_statuses

logger = logging.getLogger(__name__)

active_apps = [
    "mysql-k8s",
    "s3-integrator",
]
blocked_apps = [
    "mysql-router-k8s",
]

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

    logger.info("Deploying terraform module")
    subprocess.check_call(
        ["terraform", "init"],
        cwd="terraform",
    )
    subprocess.check_call(
        [
            "terraform",
            "apply",
            "-auto-approve",
            "-var",
            f"model={model_uuid}",
            "-var",
            f"s3_integrator_credentials={credentials}",
        ],
        cwd="terraform",
    )

    # Terraform deployed apps do not show right away.
    # We must wait before checking for their statuses.
    await ops_test.model.block_until(
        lambda: set(ops_test.model.applications) == {*active_apps, *blocked_apps},
        timeout=SHORT_TIMEOUT,
    )

    await ensure_statuses(ops_test)
