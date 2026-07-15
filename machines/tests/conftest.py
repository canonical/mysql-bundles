#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Pytest fixtures for terraform integration tests."""

import json
import logging
from platform import machine

import jubilant
import pytest

CONCIERGE_MODEL_NAME = "testing"
CLOUD_TYPE = "lxd"

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Defines pytest parsers."""
    parser.addoption("--bundle", action="store", help="run specific bundle")


def pytest_generate_tests(metafunc):
    """Processes pytest parsers."""
    bundle = metafunc.config.option.bundle
    if "bundle" in metafunc.fixturenames and bundle is not None:
        metafunc.parametrize("bundle", [bundle])


@pytest.fixture(scope="module")
def arch() -> str:
    """Return the platform architecture."""
    platforms = {
        "x86_64": "amd64",
        "aarch64": "arm64",
    }
    return platforms.get(machine(), "amd64")


@pytest.fixture(scope="module")
def juju(arch: str):
    """Use the concierge 'testing' model if available, else create a temp model.

    On CI, Concierge bootstraps a controller and creates a 'testing' model.
    For local development, fall back to a temporary model on the LXD cloud.
    """
    temp_juju = jubilant.Juju()

    # Discover clouds matching our desired type
    clouds = json.loads(temp_juju.cli("clouds", "--format", "json", include_model=False))
    matching_clouds = {
        cloud for cloud, details in clouds.items() if CLOUD_TYPE == details.get("type")
    }
    if not matching_clouds:
        pytest.skip(f"No {CLOUD_TYPE} cloud found")

    # Check if the concierge "testing" model already exists on a matching cloud
    models = json.loads(temp_juju.cli("models", "--format", "json", include_model=False))
    for model in models["models"]:
        if CONCIERGE_MODEL_NAME == model["short-name"] and model.get("cloud") in matching_clouds:
            controller = model.get("controller", "")
            model_name = (
                f"{controller}:{CONCIERGE_MODEL_NAME}" if controller else CONCIERGE_MODEL_NAME
            )
            logger.info(f"Using concierge model: {model_name}")
            juju_concierge = jubilant.Juju(model=model_name, wait_timeout=1000)
            juju_concierge.cli("set-model-constraints", f"arch={arch}")
            yield juju_concierge
            return

    # Fall back to a temporary model on the relevant cloud
    cloud_name = next(iter(matching_clouds))
    logger.info(f"Creating temp model on cloud {cloud_name}")
    with jubilant.temp_model(cloud=cloud_name) as juju_temp:
        juju_temp.wait_timeout = 1000
        juju_temp.cli("set-model-constraints", f"arch={arch}")
        yield juju_temp
