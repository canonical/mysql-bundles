# MySQL plans
[![Charmhub](https://charmhub.io/mysql-bundle/badge.svg?channel=8.0/edge)](https://charmhub.io/mysql-bundle)
[![Charmhub](https://charmhub.io/mysql-k8s-bundle/badge.svg?channel=8.0/edge)](https://charmhub.io/mysql-k8s-bundle)
[![Release](https://github.com/canonical/mysql-plans/actions/workflows/release.yaml/badge.svg?branch=8.0/edge)](https://github.com/canonical/mysql-plans/actions/workflows/release.yaml)
[![Tests](https://github.com/canonical/mysql-plans/actions/workflows/ci.yaml/badge.svg?branch=8.0/edge)](https://github.com/canonical/mysql-plans/actions/workflows/ci.yaml)

Welcome to the Canonical Distribution of MySQL Server + MySQL Router.

The objective of this page is to provide directions to
get up and running with Canonical MySQL charms.

## Description

To get started, please take Ubuntu 22.04 LTS and install the necessary components. It can be deployed
on bare metal (using a [LXD](https://canonical.com/lxd) controller) or 
on Kubernetes (using a [microk8s](https://canonical.com/microk8s) controller).

## Usage

Deploying this charm depends on the substrate of choice

### Kubernetes
```shell
juju add-model mysql
juju deploy mysql-k8s-bundle --channel 8.0/edge
juju status --watch 1s
```

### Bare metal
```shell
juju add-model mysql
juju deploy mysql-bundle --channel 8.0/edge
juju status --watch 1s
```

To remove the deployment, run:
```shell
juju destroy-model mysql --destroy-storage --yes
```

## Bundle Components

- MySQL Server - Charm to deploy MySQL Server with Group Replication.
- MySQL Router - Charm to deploy MySQL Router.
- Grafana Agent - Charm to collect MySQL Server metrics.
- S3 Integrator - Charm to connect MySQL Server with a S3 bucket.
- TLS Certificates - Charm to provide MySQL Server with TLS encryption.

Note: The TLS settings in bundles use self-signed-certificates which are not recommended for production clusters, the tls-certificates-operator charm offers a variety of configurations, read more on the TLS charm [here](https://charmhub.io/tls-certificates-operator).
