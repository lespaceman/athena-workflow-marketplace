---
title: Introduce MarketplaceModel as canonical source for the three Marketplace Registries
labels: [ready-for-human, architecture]
depends_on: []
---

# Introduce `MarketplaceModel` as canonical source for the three Marketplace Registries

## Context

This repo carries Shared Fields (`name`, `version`, `description`, `category`) for each Plugin in **four** locations: both Per-plugin Manifests (`.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`) and both plugin Marketplace Registries (`.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`). Drift is already happening — `app-exploration` currently has three different descriptions and a version drift (0.1.8 vs 0.1.6) across these locations.

See `docs/adr/0001-marketplace-registries-as-projections.md` for the rationale: registries are projections, not hand-edited sources.

## Deepening

Introduce a `MarketplaceModel` module under `scripts/marketplace/` (Python). The module's interface is the seam between hand-edited canonical sources and the three runtime-consumed Marketplace Registries.

### Interface

- `MarketplaceModel.load() -> MarketplaceModel` — walks `plugins/*` and `workflows/*`, reads Per-plugin Manifests and `workflow.json` files, **errors** on Shared Field disagreement.
- `model.plugin(name) -> Plugin`, `model.plugins() -> list[Plugin]`
- `model.workflow(name) -> Workflow`, `model.workflows() -> list[Workflow]`
- `model.bump_plugin(name, part)` — mutates in-memory model, writes both Per-plugin Manifests, cascades Plugin Pins in dependent Workflows.
- `model.bump_workflow(name, part)` — bumps workflow version.
- `model.write_registries()` — projects all three Marketplace Registries from the canonical model.
- `model.write_dist(version)` — projects `dist/<version>/` artifacts (folds in #06).

### Behind the seam

- Registry triplication.
- Shared Field consistency rule (currently informal in CLAUDE.md).
- Semver arithmetic (currently 11 inline `python -c` blocks across `scripts/bump-versions.sh`).
- Workflow Plugin Pin cascade (currently 40 lines of embedded Python in `bump-versions.sh` lines 138–178).

### Tests

- Unit tests on each projection (Plugin → Claude entry, Plugin → Codex entry, Workflow → Athena entry) — pure functions, table-driven.
- Unit tests on the consistency validator (description mismatch → error; version mismatch → error).
- Integration test: load the actual repo and assert `model.write_registries()` is a no-op when registries are in sync.

### Deletion test

Delete the module → `bump-versions.sh` regrows inline Python; three suite validators regrow registry walking; drift detection vanishes; the description-mismatch defect surfaced during architecture review stays uncaught.

## Out of scope

- Replacing Per-plugin Manifests with a single `plugin.yaml` per plugin (Shape A1). Deferred — can land later as an internal refactor of the loader without touching callers.

## Sequencing

This is the load-bearing change. Issues #03, #04, #05, #06 are downstream consequences.
