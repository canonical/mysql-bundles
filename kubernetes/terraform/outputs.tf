# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_names" {
  description = "Names of of all deployed applications."
  value = {
    mysql_server = module.mysql_server.app_name
    mysql_router = local.mysql_router_enabled ? module.mysql_router[0].app_name : null
  }
}

output "provides" {
  description = "Map of all the provided endpoints"
  value = {
    database = local.mysql_router_enabled ? module.mysql_router[0].provides.database : module.mysql_server.provides.database
  }
}

