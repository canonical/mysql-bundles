# Copyright 2023 Canonical Ltd.
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
    Any,
    Dict,
    List,
    Mapping,
)

import jubilant

logger = logging.getLogger(__name__)

TF_BINARY = os.getenv("TF_BINARY") or "terraform"

APPLY_TIMEOUT = 10 * 60


@dataclass
class Scenario:
    """A terraform deploy scenario and its expected model state."""

    name: str
    vars: Dict[str, Any] = field(default_factory=dict)
    active_apps: List[str] = field(default_factory=list)
    blocked_apps: List[str] = field(default_factory=list)
    unknown_apps: List[str] = field(default_factory=list)
    absent_apps: List[str] = field(default_factory=list)
    offers: Mapping[str, str] = field(default_factory=dict)


def get_model_uuid(juju: jubilant.Juju) -> str:
    """Get the UUID of the test model."""
    return juju.show_model().model_uuid


def get_s3_credentials() -> Dict[str, str]:
    """Build the s3 integrator credentials from environment variables."""
    return {
        "access_key": os.getenv("AWS_ACCESS_KEY"),
        "secret_key": os.getenv("AWS_SECRET_KEY"),
    }


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


def get_common_vars(juju: jubilant.Juju) -> Dict[str, Any]:
    """Build the terraform vars shared across all scenarios."""
    common: Dict[str, Any] = {
        "model": get_model_uuid(juju),
        "s3_integrator_credentials": get_s3_credentials(),
    }
    if s3_config := get_s3_config():
        common["s3_integrator"] = {"config": s3_config}
    if storage_size := os.getenv("TF_MYSQL_STORAGE_SIZE"):
        common["mysql_server"] = {
            "storage_sizes": {
                "archive": storage_size,
                "data": storage_size,
                "logs": storage_size,
                "temp": storage_size,
            },
        }
    return common


def _serialize_var(value: Any) -> str:
    """Serialize a terraform variable value to a CLI-compatible string."""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


def terraform_init() -> None:
    """Run terraform init."""
    logger.info("Running terraform init")
    subprocess.run(
        [TF_BINARY, "init"],
        cwd="terraform",
        check=True,
        timeout=APPLY_TIMEOUT,
    )


def terraform_apply(terraform_vars: Dict[str, Any]) -> None:
    """Run terraform apply with the given variables."""
    args = [TF_BINARY, "apply", "-auto-approve"]
    for key, value in terraform_vars.items():
        args.extend(["-var", f"{key}={_serialize_var(value)}"])

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


def _apps_match(status: jubilant.Status, scenario: Scenario) -> bool:
    """Check that present/absent apps match the scenario."""
    present_apps = {
        *scenario.active_apps,
        *scenario.blocked_apps,
        *scenario.unknown_apps,
    }
    if set(status.apps) != present_apps:
        return False
    for app in scenario.absent_apps:
        if app in status.apps:
            return False
    return True


def _statuses_match(status: jubilant.Status, scenario: Scenario) -> bool:
    """Check that app statuses match the scenario."""
    for app in scenario.active_apps:
        if status.apps[app].app_status.current != "active":
            return False
    for app in scenario.blocked_apps:
        if status.apps[app].app_status.current != "blocked":
            return False
    for app in scenario.unknown_apps:
        if status.apps[app].app_status.current != "unknown":
            return False
    return True


def _offers_match(status: jubilant.Status, scenario: Scenario) -> bool:
    """Check that the expected juju offers exist in the model.

    Each entry in ``scenario.offers`` maps an offer name to the application
    name the offer is expected to expose.
    """
    if not scenario.offers:
        return True

    available = {name: offer.app for name, offer in status.offers.items()}
    for offer_name, app_name in scenario.offers.items():
        if offer_name not in available:
            return False
        if app_name is not None and available[offer_name] != app_name:
            return False
    return True
