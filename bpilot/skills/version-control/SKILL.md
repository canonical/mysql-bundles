---
name: version-control
description: Repo-specific branch and commit-message conventions for backports. Used by bpilot to name backport branches and to validate commit message style when porting.
---
## Branch Conventions
- Active development branch: `8.4/edge`
- Release branches: `8.0/edge` (and similar `<version>/edge` patterns)
- Backport branch naming convention: `<short-sha>-to-<target-branch>` (e.g. `26f3d91-to-8.0-edge`)

## Commit Conventions
- Conventional-commits style prefixes (`feat:`, `fix:`, etc.)
- <!-- Additional sign-off or multi-line body conventions not clearly evidenced from history; fill in if required -->
