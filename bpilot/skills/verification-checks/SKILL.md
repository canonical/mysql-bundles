---
name: verification-checks
description: Format, lint, and unit-test commands to run after a backport. Used by bpilot to verify a ported change and to drive the LLM repair loop on failure.
---
## Verification Checks
- Format: `(cd kubernetes && tox run -e format) && (cd machines && tox run -e format)`
- Lint: `(cd kubernetes && tox run -e lint) && (cd machines && tox run -e lint)`
- Lint Terraform: `(cd kubernetes && tox run -e lint-terraform) && (cd machines && tox run -e lint-terraform)`

## Test Commands
<!-- Unit test command not evidenced in provided files; CONTRIBUTING.md only shows integration tests via `charmcraft test lxd-vm`. -->
