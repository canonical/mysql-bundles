#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the terraform module."""

import logging
import shutil

import pytest
from pytest_operator.plugin import OpsTest

from .helpers import (
    Scenario,
    TF_BINARY,
    clean_terraform_state,
    ensure_state,
    get_common_vars,
    terraform_apply,
)

logger = logging.getLogger(__name__)

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


@pytest.fixture(scope="module", autouse=True)
def _terraform_setup() -> None:
    """Skip if the terraform binary is missing, then clean stale state.

    Snap installation is handled by Concierge; this fixture only ensures the
    configured terraform (or OpenTofu, via TF_BINARY) is available and that no
    stale state referencing a since-destroyed model is carried over.
    """
    if not shutil.which(TF_BINARY):
        pytest.skip(f"{TF_BINARY} not found on PATH")
    clean_terraform_state()


@pytest.mark.abort_on_fail
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.name for s in SCENARIOS])
async def test_terraform(ops_test: OpsTest, scenario: Scenario) -> None:
    """Deploy the terraform module for the given scenario and verify its state."""
    logger.info(f"Deploying terraform module for scenario '{scenario.name}'")
    terraform_apply({**get_common_vars(ops_test), **scenario.vars})
    await ensure_state(ops_test, scenario)
