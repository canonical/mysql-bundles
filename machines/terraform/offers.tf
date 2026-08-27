# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_offer" "mysql_database_offer" {
  model_uuid = var.model
  name       = "mysql-database-offer"

  application_name = var.router_enabled ? module.mysql_router[0].app_name : module.mysql_server.app_name
  endpoints = [
    var.router_enabled ? module.mysql_router[0].provides.database : module.mysql_server.provides.database,
  ]
}
