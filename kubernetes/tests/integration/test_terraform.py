#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the terraform module."""

import logging
import subprocess

import pytest
from pytest_operator.plugin import OpsTest

from .helpers import (
    Scenario,
    clean_terraform_state,
    ensure_state,
    get_common_vars,
    terraform_apply,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def _fresh_terraform_state() -> None:
    """Remove stale terraform state before the scenarios run.

    Wiping the state once before the first scenario guarantees a clean start
    against the current model; subsequent scenarios re-apply incrementally
    (terraform apply is convergent) on that shared state.
    """
    clean_terraform_state()


# Matrix of terraform deploy scenarios and their expected model state.
# Each scenario re-applies on the shared model; terraform apply is convergent,
# so each apply brings the model to the scenario's declared state.
SCENARIOS = [
    Scenario(
        name="default",
        active_apps=["mysql-k8s", "s3-integrator"],
        blocked_apps=["mysql-router-k8s"],
    ),
    Scenario(
        name="optional_router",
        vars={"deploy_mysql_router": "false"},
        active_apps=["mysql-k8s", "s3-integrator"],
        absent_apps=["mysql-router-k8s"],
    ),
    Scenario(
        name="mysql_client_offer",
        vars={
            "deploy_mysql_router": "false",
            "mysql_client_offer": "mysql-client",
        },
        active_apps=["mysql-k8s", "s3-integrator"],
        absent_apps=["mysql-router-k8s"],
        offers=["mysql-client"],
    ),
]


@pytest.mark.abort_on_fail
async def test_snap_install(ops_test: OpsTest) -> None:
    """Install necessary binaries."""
    logger.info("Installing terraform binary")
    subprocess.check_call(
        ["sudo", "snap", "install", "terraform", "--classic"],
    )

    logger.info("Installing YQ binary")
    subprocess.check_call(
        ["sudo", "snap", "install", "yq"],
    )


@pytest.mark.abort_on_fail
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.name for s in SCENARIOS])
async def test_terraform(ops_test: OpsTest, scenario: Scenario) -> None:
    """Deploy the terraform module for the given scenario and verify its state."""
    logger.info(f"Deploying terraform module for scenario '{scenario.name}'")
    terraform_apply({**get_common_vars(ops_test), **scenario.vars})
    await ensure_state(ops_test, scenario)
