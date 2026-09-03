---
name: conflict-resolution
description: Known branch divergences and project-specific rules for resolving cherry-pick conflicts. Used by bpilot's resolver when a port produces a conflict.
---
## Skip Files
<!-- One glob pattern per line; the target branch's version is taken for matching files. -->
- poetry.lock
- *.lock
- package-lock.json
- Cargo.lock
- go.sum

## Merge Conflict Resolution Rules
<!-- Project-specific guidance the LLM should follow when resolving conflicts. -->
