# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import (
    Dict,
    List,
    Optional,
    Set,
)

from juju.unit import Unit
from pytest_operator.plugin import OpsTest


def get_app_statuses(ops_test: OpsTest, app_names: List[str]) -> Set[str]:
    """Get statuses of applications."""
    return {ops_test.model.applications[app].status for app in app_names}


async def get_leader_unit(ops_test: OpsTest, app_name: str) -> Optional[Unit]:
    """Get the leader unit of a given application.

    Args:
        ops_test: The ops test framework instance
        app_name: The name of the application
    """
    for unit in ops_test.model.applications[app_name].units:
        if await unit.is_leader_from_status():
            return unit


async def get_unit_ip(ops_test: OpsTest, unit_name: str) -> str:
    """Get unit IP address."""
    status = await ops_test.model.get_status()
    return status["applications"][unit_name.split("/")[0]].units[unit_name]["address"]


async def get_credentials(unit: Unit, username: str) -> Dict:
    """Helper to run an action to retrieve server config credentials."""
    action = await unit.run_action(action_name="get-password", username=username)
    result = await action.wait()
    return result.results
