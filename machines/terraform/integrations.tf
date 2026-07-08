# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# INTEGRATIONS FOR THE OWNED COMPONENTS

resource "juju_integration" "mysql_server_router" {
  model_uuid = var.model
  count      = local.mysql_router_enabled ? 1 : 0

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.provides.database
  }
  application {
    name     = module.mysql_router[0].app_name
    endpoint = module.mysql_router[0].requires.backend_database
  }
}

# INTEGRATIONS FOR THE MYSQL SERVER CHARM

resource "juju_integration" "mysql_server_s3_integrator" {
  model_uuid = var.model

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.requires.s3_parameters
  }
  application {
    name     = juju_application.s3_integrator.name
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "mysql_server_certificates" {
  model_uuid = var.model
  count      = local.tls_enabled && var.mysql_server.units > 0 ? 1 : 0

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.requires.client_certificates
  }
  application {
    name     = juju_application.certificates[0].name
    endpoint = var.tls_offer
  }
}

resource "juju_integration" "mysql_server_dashboard" {
  model_uuid = var.model
  count      = local.cos_enabled && var.mysql_server.units > 0 ? 1 : 0

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.provides.cos_agent
  }
  application {
    name     = juju_application.observability[0].name
    endpoint = var.cos_offers.dashboard
  }
}

# INTEGRATIONS FOR THE MYSQL ROUTER CHARM

resource "juju_integration" "mysql_router_certificates" {
  model_uuid = var.model
  count      = local.tls_enabled && local.mysql_router_enabled && var.mysql_router.units > 0 ? 1 : 0

  application {
    name     = module.mysql_router[0].app_name
    endpoint = module.mysql_router[0].requires.certificates
  }
  application {
    name     = juju_application.certificates[0].name
    endpoint = var.tls_offer
  }
}

resource "juju_integration" "mysql_router_dashboard" {
  model_uuid = var.model
  count      = local.cos_enabled && local.mysql_router_enabled && var.mysql_router.units > 0 ? 1 : 0

  application {
    name     = module.mysql_router[0].app_name
    endpoint = module.mysql_router[0].provides.cos_agent
  }
  application {
    name     = juju_application.observability[0].name
    endpoint = var.cos_offers.dashboard
  }
}

# CROSS-MODEL OFFER FOR THE MYSQL CLIENT ENDPOINT

resource "juju_offer" "mysql_client" {
  model_uuid = var.model
  count      = local.mysql_client_offered ? 1 : 0

  name             = var.mysql_client_offer
  application_name = module.mysql_server.app_name
  endpoints        = [module.mysql_server.provides.database]
}
