---
title: Delete hardcoded expectedRefs arrays in suite validators
labels: [ready-for-agent, architecture]
depends_on: [01]
---

# Delete hardcoded `expectedRefs` arrays in suite validators

## Context

`scripts/validate-playwright-suite.mjs` (lines 58–68), `scripts/validate-robot-suite.mjs`, and `scripts/validate-intent-suite.mjs` (lines 83–100) each hardcode the expected Plugin Pin set for their workflow:

```javascript
const expectedRefs = [
  'agent-web-interface@lespaceman/athena-workflow-marketplace',
  'app-exploration@lespaceman/athena-workflow-marketplace',
  'test-analysis@lespaceman/athena-workflow-marketplace',
  'playwright-automation@lespaceman/athena-workflow-marketplace',
];
```

This duplicates what `workflow.json` already declares. Adding a Plugin Pin requires editing `workflow.json` **and** the array. Mismatches surface only at test runtime.

## Change

Replace the hardcoded arrays with assertions over `MarketplaceModel`:

> *For each Plugin Pin in this Workflow's `workflow.json`, the referenced Plugin exists in `model.plugins()` and the pinned version equals the Plugin's current version.*

If a "stable contract" check is wanted (so a Workflow can't silently lose a dep), make it a **snapshot test**: a golden file under `scripts/marketplace/snapshots/<workflow>.json` regenerated from `workflow.json` on demand. A snapshot drifts intentionally with the source rather than rotting in two places.

## Rationale

Pure deletion + consolidation behind `MarketplaceModel`. No new interface.

## Sequencing

Blocked by #01.
