# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

# Write-only secret value. The value is supplied via value_wo, which is never
# stored in Terraform state. Bumping value_wo_version triggers an update of the
# secret value. This requires Terraform >= 1.11 and pairs well with ephemeral
# resources/values.
resource "juju_secret" "s3_integrator_credentials" {
  model_uuid = var.model
  name       = "s3-credentials"

  value_wo = {
    access-key = var.s3_integrator_credentials.access_key
    secret-key = var.s3_integrator_credentials.secret_key
  }
  value_wo_version = var.s3_integrator_credentials_version
}

resource "juju_access_secret" "s3_integrator_credentials" {
  model_uuid = var.model

  applications = [
    juju_application.s3_integrator.name,
  ]

  secret_id = juju_secret.s3_integrator_credentials.secret_id
}
