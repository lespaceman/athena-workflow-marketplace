---
title: Decompose bump-versions.sh into a thin wrapper over MarketplaceModel
labels: [ready-for-agent, architecture]
depends_on: [01]
---

# Decompose `bump-versions.sh` into a thin wrapper over `MarketplaceModel`

## Context

`scripts/bump-versions.sh` is 264 lines doing three operations:

1. Bump Plugin versions (lines 26–94).
2. Sync Plugin Pin versions into `workflow.json` files (lines 131–184).
3. Bump Workflow versions (lines 186–263).

It mixes shell logic with **11 separate** inline `python -c` JSON-manipulation blocks. The three operations cannot be invoked independently. Reusing the workflow-pin-cascade logic from any other context is impossible without copy-paste.

## Change

After #01 lands, the script becomes a 5-line wrapper:

```bash
#!/usr/bin/env bash
set -euo pipefail
exec python3 -m marketplace bump "$@"
```

`python3 -m marketplace bump <target> <part>` figures out plugin vs workflow and dispatches to `model.bump_plugin()` or `model.bump_workflow()`. All three operations live behind one model method. Each is independently testable.

## What moves behind the seam

- Semver arithmetic (`bump_part(version, "minor") -> str`) — table-driven unit tests on edge cases (`0.1.9 → 0.1.10`, `0.9.0 → 0.10.0`, prerelease handling).
- Workflow Plugin Pin cascade — pure function on the model: "given Plugin X bumped to V, return the set of Workflow Plugin Pin updates required."
- Atomic write of all three Marketplace Registries.

## Tests gained

- "Bump Plugin X with no dependent Workflows touches no `workflow.json` files."
- "Bump Plugin X with two dependent Workflows updates exactly those two Plugin Pins and bumps both Workflow versions."
- Semver edge cases (currently untestable because logic is inline shell+Python).

## Why keep the shell entry point

Preserve `scripts/bump-versions.sh` as the documented invocation in CLAUDE.md and CI. The wrapper is one `exec` line; the complexity moves into the importable Python module.

## Sequencing

Blocked by #01.
