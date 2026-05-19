# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# INTEGRATIONS FOR THE OWNED COMPONENTS

resource "juju_integration" "mysql_server_router" {
  model_uuid = var.model

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.provides.database
  }
  application {
    name     = module.mysql_router.app_name
    endpoint = module.mysql_router.requires.backend_database
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
    endpoint = module.mysql_server.requires.certificates
  }
  application {
    name     = juju_application.certificates[0].name
    endpoint = var.tls_offer
  }
}

resource "juju_integration" "mysql_server_cos_dashboard" {
  model_uuid = var.model
  count      = local.cos_enabled && var.mysql_server.units > 0 ? 1 : 0

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.provides.grafana_dashboard
  }
  application {
    name     = juju_application.observability[0].name
    endpoint = var.cos_offers.dashboard
  }
}

resource "juju_integration" "mysql_server_cos_metrics" {
  model_uuid = var.model
  count      = local.cos_enabled && var.mysql_server.units > 0 ? 1 : 0

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.provides.metrics_endpoint
  }
  application {
    name     = juju_application.observability[0].name
    endpoint = var.cos_offers.metrics
  }
}

# INTEGRATIONS FOR THE MYSQL ROUTER CHARM

resource "juju_integration" "mysql_router_certificates" {
  model_uuid = var.model
  count      = local.tls_enabled && var.mysql_router.units > 0 ? 1 : 0

  application {
    name     = module.mysql_router.app_name
    endpoint = module.mysql_router.requires.certificates
  }
  application {
    name     = juju_application.certificates[0].name
    endpoint = var.tls_offer
  }
}

resource "juju_integration" "mysql_router_cos_dashboard" {
  model_uuid = var.model
  count      = local.cos_enabled && var.mysql_router.units > 0 ? 1 : 0

  application {
    name     = module.mysql_router.app_name
    endpoint = module.mysql_router.provides.grafana_dashboard
  }
  application {
    name     = juju_application.observability[0].name
    endpoint = var.cos_offers.dashboard
  }
}

resource "juju_integration" "mysql_router_cos_metrics" {
  model_uuid = var.model
  count      = local.cos_enabled && var.mysql_router.units > 0 ? 1 : 0

  application {
    name     = module.mysql_router.app_name
    endpoint = module.mysql_router.provides.metrics_endpoint
  }
  application {
    name     = juju_application.observability[0].name
    endpoint = var.cos_offers.metrics
  }
}
