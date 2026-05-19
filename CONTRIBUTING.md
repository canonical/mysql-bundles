# Contributing

## Overview

This documents explains the processes and practices recommended for contributing enhancements to
this operator.

- Generally, before developing enhancements to this charm, you should consider
  [opening an issue](https://github.com/canonical/mysql-bundles/issues) explaining your use case.
- If you would like to chat with us about your use-cases or proposed implementation, you can reach
  us at the [Data Platform matrix room](https://matrix.to/#/#charmhub-data-platform:ubuntu.com).
- Familiarising yourself with the [Juju framework](https://documentation.ubuntu.com/juju/3.6/)
  library will help you a lot when working on new features or bug fixes.
- All enhancements require review before being merged. Code review typically examines:
  - Code quality
  - Test coverage
  - User experience for Juju administrators of this charm.
- Please help us out in ensuring easy to review branches by rebasing your pull request branch onto
  the `8.4/edge` branch. This also avoids merge commits and creates a linear Git commit history.

## Develop
Install `tox` and `poetry`

```shell
pipx install tox
pipx install poetry
```

You can create an environment for development:

```shell
(cd kubernetes && poetry install)
(cd machines && poetry install)
```

### Test

```shell
(cd kubernetes && tox run -e format)
(cd kubernetes && tox run -e lint)
(cd kubernetes && tox run -e lint-terraform)
(cd kubernetes && charmcraft test lxd-vm)

(cd machines && tox run -e format)
(cd machines && tox run -e lint)
(cd machines && tox run -e lint-terraform)
(cd machines && charmcraft test lxd-vm)
```

### Deploy

```shell
juju add-model mysql
juju model-config logging-config="<root>=INFO;unit=DEBUG"

# Deploy the K8s or VM charm
(cd kubernetes && juju deploy ./releases/latest/mysql-k8s-bundle.yaml)
(cd machines && juju deploy ./releases/latest/mysql-bundle.yaml)
```

## Canonical Contributor Agreement

Canonical welcomes contributions to the MySQL Operator. Please check out our
[contributor agreement](https://ubuntu.com/legal/contributors) if you are
interested in contributing to the solution.
