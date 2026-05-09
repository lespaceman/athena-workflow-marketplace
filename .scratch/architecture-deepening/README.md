# Architecture Deepening — Issue Set

Six issues from an architecture review focused on cross-runtime registry sync, skill metadata projection, and validator deduplication. See `docs/adr/0001-marketplace-registries-as-projections.md` for the load-bearing decision.

## Issues

| # | Title | Label | Depends on | Status |
| - | ----- | ----- | ---------- | ------ |
| [01](issues/01-marketplace-model.md) | Introduce `MarketplaceModel` as canonical source for the three Marketplace Registries | ready-for-human | — | **done** — `scripts/marketplace/`, 25 unit tests, drift fixed |
| [02](issues/02-skill-spec.md) | Introduce `SkillSpec` for the SKILL.md ↔ claude.yaml ↔ openai.yaml triple | ready-for-human | — | **done** — `scripts/skill_model/`, 8 unit tests |
| [03](issues/03-validator-deduplication.md) | Collapse plugin-discovery duplication across the five validators | ready-for-human | #01 | **done** — `scripts/suite_validators/`, .mjs files now thin Node shims |
| [04](issues/04-delete-hardcoded-refs.md) | Delete hardcoded `expectedRefs` arrays in suite validators | ready-for-agent | #01 | **done** — replaced with `assert_workflow_pin_versions_match_model()` |
| [05](issues/05-decompose-bump-versions.md) | Decompose `bump-versions.sh` into a thin wrapper over `MarketplaceModel` | ready-for-agent | #01 | **done** — 264 LOC → 5-line wrapper |
| [06](issues/06-dist-marker.md) | Mark `dist/<version>/` outputs as generated | ready-for-agent | — | **done** — `GENERATED.md` written by builder + backfilled into 11 existing dist dirs |

## Sequencing

#01 is load-bearing. #03–#05 fall out of #01 almost mechanically. #02 and #06 can ship in parallel with #01.

## Why local markdown rather than GitHub

The repo is configured for GitHub Issues (see `docs/agents/issue-tracker.md`), but this batch was recorded locally on user instruction. Future architecture reviews should use the configured tracker unless the user redirects again.
