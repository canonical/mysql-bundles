# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import (
    List,
    Set,
)

from pytest_operator.plugin import OpsTest


def get_app_statuses(ops_test: OpsTest, app_names: List[str]) -> Set[str]:
    """Get statuses of applications."""
    return {ops_test.model.applications[app].status for app in app_names}
