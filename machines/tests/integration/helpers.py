# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import base64
import json
import logging
import os
import subprocess
from dataclasses import (
    dataclass,
    field,
)
from pathlib import Path
from typing import (
    Dict,
    List,
    Set,
)

from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)

TF_BINARY = os.getenv("TF_BINARY") or "terraform"

TIMEOUT = 20 * 60
SHORT_TIMEOUT = 5 * 60
APPLY_TIMEOUT = 10 * 60


@dataclass
class Scenario:
    """A terraform deploy scenario and its expected model state."""

    name: str
    vars: Dict[str, str] = field(default_factory=dict)
    active_apps: List[str] = field(default_factory=list)
    blocked_apps: List[str] = field(default_factory=list)
    unknown_apps: List[str] = field(default_factory=list)
    absent_apps: List[str] = field(default_factory=list)
    offers: List[str] = field(default_factory=list)


def get_app_statuses(ops_test: OpsTest, app_names: List[str]) -> Set[str]:
    """Get statuses of applications."""
    return {ops_test.model.applications[app].status for app in app_names}


def get_offer_names(ops_test: OpsTest) -> Set[str]:
    """Get the names of cross-model offers deployed in the model."""
    result = subprocess.check_output(
        ["juju", "offers", "--model", ops_test.model.name, "--format", "json"],
        text=True,
    )
    offers = json.loads(result) or []
    return {offer.get("Offer", offer.get("offer", "")) for offer in offers}


def get_model_uuid(ops_test: OpsTest) -> str:
    """Get the UUID of the test model."""
    model_info = subprocess.check_output(
        ["juju", "show-model", ops_test.model.name],
        text=True,
        input=None,
    )
    return subprocess.check_output(
        ["yq", f'."{ops_test.model.name}"."model-uuid"'],
        text=True,
        input=model_info,
    ).strip()


def get_s3_credentials() -> str:
    """Build the s3 integrator credentials JSON from environment variables."""
    return json.dumps({
        "access_key": os.getenv("AWS_ACCESS_KEY"),
        "secret_key": os.getenv("AWS_SECRET_KEY"),
    })


def get_s3_config() -> Dict[str, str]:
    """Build the s3 integrator config from environment variables, if any."""
    s3_config: Dict[str, str] = {}
    if endpoint := os.getenv("AWS_ENDPOINT_URL"):
        s3_config["endpoint"] = endpoint
    if ca_cert := os.getenv("CA_CERT"):
        ca_path = Path(ca_cert)
        ca_pem = ca_path.read_text() if ca_path.exists() else ca_cert
        s3_config["tls-ca-chain"] = base64.b64encode(ca_pem.encode()).decode()
    return s3_config


def get_common_vars(ops_test: OpsTest) -> Dict[str, str]:
    """Build the terraform vars shared across all scenarios."""
    common: Dict[str, str] = {
        "model": get_model_uuid(ops_test),
        "s3_integrator_credentials": get_s3_credentials(),
    }
    if s3_config := get_s3_config():
        common["s3_integrator"] = json.dumps({"config": s3_config})
    if storage_size := os.getenv("TF_MYSQL_STORAGE_SIZE"):
        common["mysql_server"] = json.dumps({"storage_size": storage_size})
    return common


def terraform_apply(terraform_vars: Dict[str, str]) -> None:
    """Run terraform init and apply with the given variables."""
    logger.info("Running terraform init")
    subprocess.run(
        [TF_BINARY, "init"],
        cwd="terraform",
        check=True,
        timeout=APPLY_TIMEOUT,
    )

    args = [TF_BINARY, "apply", "-auto-approve"]
    for key, value in terraform_vars.items():
        args.extend(["-var", f"{key}={value}"])

    logger.info("Running terraform apply")
    subprocess.run(
        args,
        cwd="terraform",
        check=True,
        timeout=APPLY_TIMEOUT,
    )


def clean_terraform_state() -> None:
    """Remove stale terraform state files to ensure a fresh deploy.

    Wiping the state before the first apply guarantees a clean start.
    """
    for state_file in ("terraform.tfstate", "terraform.tfstate.backup"):
        path = os.path.join("terraform", state_file)
        if os.path.exists(path):
            logger.info(f"Removing stale terraform state file: {path}")
            os.remove(path)


async def ensure_state(ops_test: OpsTest, scenario: Scenario) -> None:
    """Ensure the model matches the expected state for the given scenario."""
    present_apps = {
        *scenario.active_apps,
        *scenario.blocked_apps,
        *scenario.unknown_apps,
    }

    logger.info(f"Waiting for apps to settle: {', '.join(sorted(present_apps))}")
    await ops_test.model.block_until(
        lambda: set(ops_test.model.applications) == present_apps,
        timeout=SHORT_TIMEOUT,
    )

    if scenario.active_apps:
        logger.info(f"Waiting for active: {', '.join(scenario.active_apps)}")
        await ops_test.model.block_until(
            lambda: get_app_statuses(ops_test, scenario.active_apps) == {"active"},
            timeout=TIMEOUT,
        )

    if scenario.blocked_apps:
        logger.info(f"Waiting for blocked: {', '.join(scenario.blocked_apps)}")
        await ops_test.model.block_until(
            lambda: get_app_statuses(ops_test, scenario.blocked_apps) == {"blocked"},
            timeout=SHORT_TIMEOUT,
        )

    if scenario.unknown_apps:
        logger.info(f"Waiting for unknown: {', '.join(scenario.unknown_apps)}")
        await ops_test.model.block_until(
            lambda: get_app_statuses(ops_test, scenario.unknown_apps) == {"unknown"},
            timeout=SHORT_TIMEOUT,
        )

    for app in scenario.absent_apps:
        logger.info(f"Ensuring {app} was not deployed")
        assert app not in ops_test.model.applications

    if scenario.offers:
        logger.info(f"Ensuring offers: {', '.join(scenario.offers)}")

        def offers_present() -> bool:
            return set(scenario.offers).issubset(get_offer_names(ops_test))

        await ops_test.model.block_until(offers_present, timeout=SHORT_TIMEOUT)
