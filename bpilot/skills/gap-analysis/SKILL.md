---
name: gap-analysis
description: Checklist of things to verify when backporting (lifecycle hooks, upgrade paths, parity between flavours). Used by bpilot's gap analyzer to drive per-item checks.
---
## Things to Check When Backporting
<!-- One numbered item per line; each item becomes a single targeted LLM query. -->
1. S3 credentials handling: `8.4/edge` manages S3 integrator credentials via Juju secrets (`juju_secret`/`juju_access_secret` resources in `secrets.tf`, and an `s3_integrator_credentials` object variable in `variables.tf`); `8.0/edge` has only the `s3-credentials` integration endpoint in `integrations.tf`. When backporting to an older branch and the change touches S3 credential handling, adapt it to the non-secret approach used on the target; do not blindly port the secrets implementation. Also ensure the tests for S3 credential handling are adapted to the target branch's approach, and expected state of S3 integrator is adapted per target branch.
