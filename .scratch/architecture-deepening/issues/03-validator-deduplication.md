---
title: Collapse plugin-discovery duplication across the five validators
labels: [ready-for-human, architecture]
depends_on: [01]
---

# Collapse plugin-discovery duplication across the five validators

## Context

Five validator scripts each re-implement walking the plugin tree and reading registry files:

- `scripts/validate-skills-portable.sh` — walks `plugins/*/skills/*`.
- `scripts/validate-skills-repo.sh` — Python inline, walks `plugins/*/skills/*`.
- `scripts/validate-playwright-suite.mjs` — Node, hardcoded paths + registry lookups.
- `scripts/validate-robot-suite.mjs` — Node, structurally duplicates the Playwright suite.
- `scripts/validate-intent-suite.mjs` — Node, reads all three Marketplace Registries + hardcoded skill paths.

Total: ~587 lines, mostly duplicated structure. No shared discovery utility. Schema knowledge is embedded in each validator.

## Change

Once #01 lands, validators stop walking files and call `MarketplaceModel.load().plugins()`, `model.workflows()`, `model.skills()`. Specifically:

- **`validate-skills-portable.sh`** — keep as-is; it's the external Anthropic Agent Skills validator. Source the skill list from `model.skills()` instead of `find`.
- **`validate-skills-repo.sh`** → `python3 -m marketplace validate-skills`. Use `SkillSpec.validate()` (#02) per skill.
- **`validate-{playwright,robot,intent}-suite.mjs`** → rewrite as Python under `scripts/marketplace/validators/`. The three `.mjs` files are mostly file-walking + assertions; rewriting in Python that imports the model is shorter than maintaining the Node↔Python boundary.

## Rationale

This is mostly **deletion**. The deletion test passes because the complexity it removes concentrates in #01 — exactly what the deletion test is supposed to surface. No new module is needed; the new module is `MarketplaceModel`.

## Sequencing

Blocked by #01. Should ship immediately after.
