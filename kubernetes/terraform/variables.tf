# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "UUID of the juju model to deploy to"
  type        = string
}

variable "cos_offers" {
  description = "COS provider offers to be used on client relations."
  type = object({
    dashboard = optional(string, null)
    metrics   = optional(string, null)
    logging   = optional(string, null)
    tracing   = optional(string, null)
  })

  default = {}
}

variable "tls_offer" {
  description = "TLS provider offer to be used on client relations."
  type        = string
  default     = null
}

variable "deploy_mysql_router" {
  description = "Whether to deploy the MySQL Router application, alongside the server, on this same model."
  type        = bool
  default     = true
}

variable "mysql_server" {
  description = "Defines the MySQL Server application configuration"
  type = object({
    app_name     = optional(string, "mysql-k8s")
    base         = optional(string, "ubuntu@26.04")
    channel      = optional(string, "8.4/edge")
    config       = optional(map(string), {})
    constraints  = optional(string, "arch=amd64")
    resources    = optional(map(string), {})
    revision     = optional(number, null)
    units        = optional(number, 3)
    storage_size = optional(string, "10G")
  })

  default = {}
}

variable "mysql_router" {
  description = "Defines the MySQL Router application configuration"
  type = object({
    app_name    = optional(string, "mysql-router-k8s")
    base        = optional(string, "ubuntu@26.04")
    channel     = optional(string, "8.4/edge")
    config      = optional(map(string), {})
    constraints = optional(string, "")
    resources   = optional(map(string), {})
    revision    = optional(number, null)
    units       = optional(number, 1)
  })

  default = {}
}

variable "certificates" {
  description = "Defines the certificates application configuration"
  type = object({
    app_name    = optional(string, "self-signed-certificates")
    base        = optional(string, "ubuntu@24.04")
    channel     = optional(string, "1/stable")
    config      = optional(map(string), { "ca-common-name" : "CA" })
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number, null)
    units       = optional(number, 1)
  })

  default = {}

  validation {
    condition     = var.certificates.units == 1
    error_message = "Units count should be 1"
  }
}

variable "observability" {
  description = "Defines the observability application configuration"
  type = object({
    app_name    = optional(string, "grafana-agent-k8s")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "1/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "")
    resources   = optional(map(string), {})
    revision    = optional(number, null)
    units       = optional(number, 1)
  })

  default = {}

  validation {
    condition     = var.observability.units == 1
    error_message = "Units count should be 1"
  }
}

variable "s3_integrator" {
  description = "Defines the S3 integrator application configuration"
  type = object({
    app_name    = optional(string, "s3-integrator")
    base        = optional(string, "ubuntu@24.04")
    channel     = optional(string, "2/edge")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number, null)
    units       = optional(number, 1)
  })

  default = {}

  validation {
    condition     = var.s3_integrator.units == 1
    error_message = "Units count should be 1"
  }
}

variable "s3_integrator_credentials" {
  description = "Defines the S3 integrator application credentials"
  type = object({
    access_key = optional(string, "")
    secret_key = optional(string, "")
  })
}
