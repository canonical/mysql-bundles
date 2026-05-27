# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.


resource "juju_secret" "s3_integrator_credentials" {
  model_uuid = var.model
  name       = "s3-credentials"

  value = {
    access-key = var.s3_integrator_credentials.access_key
    secret-key = var.s3_integrator_credentials.secret_key
  }
}

resource "juju_access_secret" "s3_integrator_credentials" {
  model_uuid = var.model

  applications = [
    juju_application.s3_integrator.name,
  ]

  secret_id = juju_secret.s3_integrator_credentials.secret_id
}
