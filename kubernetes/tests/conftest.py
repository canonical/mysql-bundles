#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Pytest fixtures for terraform integration tests."""

import json
import logging
from platform import machine

import jubilant
import pytest

CLOUD_TYPES = ("k8s", "kubernetes")

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Defines pytest parsers."""
    parser.addoption("--bundle", action="store", help="run specific bundle")
    parser.addoption(
        "--model",
        action="store",
        default="testing",
        help="model name or ':auto:' for temporary model, default to 'testing'",
        required=False,
    )


@pytest.fixture(scope="module")
def arch() -> str:
    """Return the platform architecture."""
    platforms = {
        "x86_64": "amd64",
        "aarch64": "arm64",
    }
    return platforms.get(machine(), "amd64")


@pytest.fixture(scope="module")
def juju(request: pytest.FixtureRequest, arch: str):
    """Use the model specified via ``--model`` (default ``testing``), or a temp model.

    Pass ``--model=:auto:`` to create a temporary model instead of using the
    concierge-provided ``testing`` model.
    """
    model = request.config.getoption("--model")

    # if existing model is present and set, use it
    if model != ":auto:":
        juju_model = jubilant.Juju(model=model, wait_timeout=1000)
        yield juju_model
        return

    # ...else, create a temporary model on a matching cloud
    temp_juju = jubilant.Juju()
    clouds = json.loads(temp_juju.cli("clouds", "--format", "json", include_model=False))
    matching_clouds = {
        cloud for cloud, details in clouds.items() if details.get("type") in CLOUD_TYPES
    }
    if not matching_clouds:
        pytest.fail(f"No {CLOUD_TYPES} cloud found")

    cloud_name = next(iter(matching_clouds))
    logger.info(f"Creating temp model on cloud {cloud_name}")
    with jubilant.temp_model(cloud=cloud_name) as juju_temp:
        juju_temp.wait_timeout = 1000
        juju_temp.model_constraints({"arch": arch})
        yield juju_temp
