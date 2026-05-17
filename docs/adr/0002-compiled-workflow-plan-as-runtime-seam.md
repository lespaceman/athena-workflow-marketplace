---
status: accepted
---

# Compiled Workflow Plan is the runtime seam

Workflows are authored as shared `workflow.json` plus `workflow.md`, but a
Runtime cannot execute that pair directly without also resolving Plugin Pins,
Plugin roots, Runtime overlay manifests, Skill roots, MCP config, and loop
settings.

We treat the **Compiled Workflow Plan** as the seam between repository authoring
and runtime execution. `scripts/marketplace/compiler.py` owns this projection.
Callers ask for one Workflow compiled for one Runtime and receive a resolved
plan. They should not re-walk Marketplace Registries, Plugin directories, or
overlay manifests on every turn.

## Considered options

- **Runtime reads raw files directly (rejected).** This keeps every Runtime
  responsible for understanding `workflow.json`, Per-plugin Manifests, overlay
  paths, Skill roots, and MCP config. It is shallow: deleting the helper would
  spread the same path and Plugin Pin logic across consumers.
- **Marketplace Registry as execution input (rejected).** ADR-0001 already says
  Marketplace Registries are projections for discovery. Using them as execution
  sources would reintroduce drift and make checked-in catalogs look canonical.
- **Compiled Workflow Plan module (accepted).** One module resolves the authored
  Workflow and its Plugin Pins into a Runtime-specific projection. Runtime
  adapters can consume that projection without learning repository layout.

## Why this is worth recording

The RFCs already described a compiled plan, but the repository did not have a
module at that seam. Without this ADR, future maintainers could keep adding
validators or markdown instructions around the gap. The decision is to deepen
the seam: put resolution and validation behind the Compiled Workflow Plan
interface, then grow lifecycle policy and security checks there as the protocol
matures.
