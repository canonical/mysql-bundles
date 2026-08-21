#!/usr/bin/env python
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the mysql-k8s-bundle."""

import itertools
import logging

import jubilant

from .connector import MysqlConnector
from .helpers import (
    Scenario,
    _apps_match,
    _statuses_match,
    get_credentials,
    get_leader_unit_name,
    get_unit_address,
)

logger = logging.getLogger(__name__)

TIMEOUT = 30 * 60
SHORT_TIMEOUT = 5 * 60

# Each scenario represents a checkpoint in the bundle test progression.
# The bundle deploys all apps at once; subsequent scenarios reflect
# configuration changes that move apps from blocked/waiting to active.
SCENARIOS = [
    Scenario(
        name="deployed",
        active_apps=["mysql-k8s", "self-signed-certificates", "sysbench"],
        blocked_apps=[
            "data-integrator",
            "grafana-agent-k8s",
            "mysql-router-data-integrator",
            "s3-integrator",
        ],
        waiting_apps=["mysql-router-k8s"],
    ),
    Scenario(
        name="s3-configured",
        active_apps=[
            "mysql-k8s",
            "self-signed-certificates",
            "sysbench",
            "s3-integrator",
        ],
        blocked_apps=[
            "data-integrator",
            "grafana-agent-k8s",
            "mysql-router-data-integrator",
        ],
        waiting_apps=["mysql-router-k8s"],
    ),
    Scenario(
        name="data-integrator-configured",
        active_apps=[
            "mysql-k8s",
            "self-signed-certificates",
            "sysbench",
            "s3-integrator",
            "data-integrator",
        ],
        blocked_apps=["grafana-agent-k8s", "mysql-router-data-integrator"],
        waiting_apps=["mysql-router-k8s"],
    ),
    Scenario(
        name="router-configured",
        active_apps=[
            "mysql-k8s",
            "self-signed-certificates",
            "sysbench",
            "s3-integrator",
            "data-integrator",
            "mysql-router-data-integrator",
            "mysql-router-k8s",
        ],
        blocked_apps=["grafana-agent-k8s"],
    ),
    Scenario(
        name="test-app-unit-added",
        active_apps=[
            "mysql-k8s",
            "self-signed-certificates",
            "sysbench",
            "s3-integrator",
            "data-integrator",
            "mysql-router-data-integrator",
            "mysql-router-k8s",
        ],
        blocked_apps=["grafana-agent-k8s"],
        waiting_apps=["mysql-test-app"],
    ),
]


def _wait_for(juju: jubilant.Juju, scenario: Scenario, timeout: float = TIMEOUT) -> None:
    """Wait for the model to match the given scenario."""
    logger.info(f"Waiting for scenario '{scenario.name}'")
    juju.wait(
        lambda status: _apps_match(status, scenario) and _statuses_match(status, scenario),
        timeout=timeout,
        error=jubilant.any_error,
    )


def test_smoke(juju: jubilant.Juju) -> None:
    """Deploy bundle with apps and test various component integrations."""
    logger.info("Deploying bundle")
    juju.deploy("./releases/latest/mysql-k8s-bundle.yaml", trust=True)
    juju.config("mysql-k8s", {"profile": "testing"})
    _wait_for(juju, SCENARIOS[0])

    logger.info("Configuring s3-integrator credentials")
    juju.run(
        "s3-integrator/0",
        "sync-s3-credentials",
        {"access-key": "access", "secret-key": "secret"},
    )
    _wait_for(juju, SCENARIOS[1], timeout=SHORT_TIMEOUT)

    logger.info("Configuring data-integrator")
    juju.config("data-integrator", {"database-name": "mysql-database"})
    _wait_for(juju, SCENARIOS[2], timeout=SHORT_TIMEOUT)

    logger.info("Confirming data-integrator's database exists")
    mysql_leader = get_leader_unit_name(juju, "mysql-k8s")
    mysql_leader_address = get_unit_address(juju, mysql_leader)
    server_config_credentials = get_credentials(juju, mysql_leader, "serverconfig")

    database_config = {
        "user": server_config_credentials["username"],
        "password": server_config_credentials["password"],
        "host": mysql_leader_address,
        "raise_on_warnings": False,
    }

    with MysqlConnector(database_config, False) as cursor:
        cursor.execute("SHOW DATABASES;")
        databases = list(itertools.chain(*cursor.fetchall()))
        assert "mysql-database" in databases

    logger.info("Configuring mysql-router-data-integrator")
    juju.config("mysql-router-data-integrator", {"database-name": "mysql-router-database"})
    _wait_for(juju, SCENARIOS[3], timeout=SHORT_TIMEOUT)

    logger.info("Confirming mysql-router-data-integrator's database exists")
    with MysqlConnector(database_config, False) as cursor:
        cursor.execute("SHOW DATABASES;")
        databases = list(itertools.chain(*cursor.fetchall()))
        assert "mysql-router-database" in databases

    logger.info("Adding mysql-test-app unit")
    juju.add_unit("mysql-test-app")
    _wait_for(juju, SCENARIOS[4], timeout=SHORT_TIMEOUT)
