---
status: accepted
---

# Marketplace Registries are projections, not hand-edited sources

The three Marketplace Registries (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `.athena-workflow/marketplace.json`) are runtime-specific catalogs consumed by Claude Code, Codex, and athena-cli respectively. They overlap heavily on Shared Fields (`name`, `version`, `description`, `category`) and diverge on runtime-specific fields (`source` shape, `policy`, `keywords`, `interface`).

We treat the Per-plugin Manifests and per-Workflow `workflow.json` files as **canonical sources** and the three Marketplace Registries as **projections** generated from them. A `MarketplaceModel` module owns the projection logic and enforces Shared Field equality at load time.

## Considered options

- **Synchronizer (rejected).** Keep all three registries hand-edited; a script flags drift after the fact. Rejected because drift was already happening in practice — `app-exploration` had three different descriptions and a version drift (0.1.8 vs 0.1.6) across the four locations carrying its Shared Fields. A synchronizer catches this *after* it lands; projections make it impossible by construction.
- **Single per-plugin source file (deferred).** Replace both Per-plugin Manifests with one `plugin.yaml` per plugin and project both runtime manifests from it. Defers cleanly behind the `MarketplaceModel` interface — adopt later as an internal refactor without touching callers.

## Why this is worth recording

The Marketplace Registries look like authoritative source files (they're checked in, hand-readable JSON) but are not. Without this ADR, a future maintainer's natural instinct on seeing "the marketplace.json is wrong" will be to edit it directly. The decision is to instead fix the canonical source and re-project.
