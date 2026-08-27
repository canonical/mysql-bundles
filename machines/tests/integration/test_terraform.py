#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the terraform module."""

import logging
import shutil

import jubilant
import pytest

from .helpers import (
    TF_BINARY,
    Scenario,
    _apps_match,
    _offers_match,
    _statuses_match,
    clean_terraform_state,
    get_common_vars,
    terraform_apply,
    terraform_init,
)

logger = logging.getLogger(__name__)

# Matrix of terraform deploy scenarios and their expected model state.
# Each scenario re-applies on the shared model.
SCENARIOS = [
    Scenario(
        name="default",
        active_apps=["mysql", "s3-integrator"],
        unknown_apps=["mysql-router"],
        offers={"mysql_database_offer": "mysql-router"},
    ),
    Scenario(
        name="optional_router",
        vars={"router_enabled": "false"},
        active_apps=["mysql", "s3-integrator"],
        absent_apps=["mysql-router"],
        offers={"mysql_database_offer": "mysql"},
    ),
]


@pytest.fixture(scope="module", autouse=True)
def _terraform_setup() -> None:
    """Skip if the terraform binary is missing, then clean stale state.

    Snap installation is handled by Concierge; this fixture ensures:
    1. configured terraform (or OpenTofu, via TF_BINARY) is available and
    2. no stale state referencing a since-destroyed model is carried over.
    """
    if not shutil.which(TF_BINARY):
        pytest.skip(f"{TF_BINARY} not found on PATH")
    clean_terraform_state()


@pytest.fixture(scope="module", autouse=True)
def _terraform_init(_terraform_setup) -> None:
    """Run terraform init once before the first scenario."""
    terraform_init()


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.name for s in SCENARIOS])
def test_terraform(juju: jubilant.Juju, scenario: Scenario) -> None:
    """Deploy the terraform module for the given scenario and verify its state."""
    logger.info(f"Deploying terraform module for scenario '{scenario.name}'")
    terraform_apply({**get_common_vars(juju), **scenario.vars})

    juju.wait(
        lambda status: _apps_match(status, scenario) and _statuses_match(status, scenario),
        error=jubilant.any_error,
    )

    assert _offers_match(juju, scenario), f"offers do not match scenario '{scenario.name}'"
