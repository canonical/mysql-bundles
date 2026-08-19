# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  cos_enabled = var.cos_offers.dashboard != null ? true : false
  tls_enabled = var.tls_offer != null ? true : false
}

module "mysql_server" {
  source        = "git::https://github.com/canonical/mysql-operators//machines/terraform?ref=sinclert/tf-storage-sizes-8.4"
  model         = var.model
  app_name      = var.mysql_server.app_name
  base          = var.mysql_server.base
  channel       = var.mysql_server.channel
  config        = var.mysql_server.config
  constraints   = var.mysql_server.constraints
  revision      = var.mysql_server.revision
  units         = var.mysql_server.units
  storage_sizes = var.mysql_server.storage_sizes
}

module "mysql_router" {
  count       = var.router_enabled ? 1 : 0
  source      = "git::https://github.com/canonical/mysql-router-operators//machines/terraform?ref=8.4/edge"
  model       = var.model
  app_name    = var.mysql_router.app_name
  base        = var.mysql_router.base
  channel     = var.mysql_router.channel
  config      = var.mysql_router.config
  constraints = var.mysql_router.constraints
  revision    = var.mysql_router.revision
  units       = var.mysql_router.units
}
