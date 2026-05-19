# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "certificates" {
  count = local.tls_enabled ? 1 : 0

  charm {
    name     = var.certificates.app_name
    base     = var.certificates.base
    channel  = var.certificates.channel
    revision = var.certificates.revision
  }

  model_uuid  = var.model
  name        = var.certificates.app_name
  config      = var.certificates.config
  constraints = var.certificates.constraints
  units       = var.certificates.units
}

resource "juju_application" "observability" {
  count = local.cos_enabled ? 1 : 0

  charm {
    name     = var.observability.app_name
    base     = var.observability.base
    channel  = var.observability.channel
    revision = var.observability.revision
  }

  model_uuid  = var.model
  name        = var.observability.app_name
  config      = var.observability.config
  constraints = var.observability.constraints
  units       = var.observability.units
}

resource "juju_application" "s3_integrator" {
  charm {
    name     = "s3-integrator"
    base     = var.s3_integrator.base
    channel  = var.s3_integrator.channel
    revision = var.s3_integrator.revision
  }

  model_uuid  = var.model
  name        = var.s3_integrator.app_name
  config      = var.s3_integrator.config
  constraints = var.s3_integrator.constraints
  units       = var.s3_integrator.units
}
