# Plugin Suite Immediate Split

This document is the decision-complete phase-1 migration plan for splitting the current testing plugins into shared layers plus framework execution layers.

See also:
- [Plugin Suite Plan](plugin-suite-plan.md)
- [Future Suite Catalog](plugin-suite-future-suite.md)

## Phase 1 Goal

Phase 1 creates a clean shared/framework split without introducing testing-intent plugins yet.

Phase 1 must:

- introduce `app-exploration`
- introduce `test-analysis`
- introduce `playwright-automation`
- retain and slim `robot-automation`
- keep `agent-web-interface` unchanged
- preserve workflow continuity where practical

Phase 1 must not:

- create concrete `exploratory-testing`, `smoke-testing`, or `regression-testing` plugins
- redesign unrelated plugins such as `site-knowledge`, `md-export`, or `web-bench`
- rename the `robot-automation` workflow

## Exact Plugin Layout After Split

The target plugin set after phase 1 is:

- `agent-web-interface`
- `app-exploration`
- `test-analysis`
- `playwright-automation`
- `robot-automation`

The legacy `e2e-test-builder` name survives only as a workflow identifier for continuity.

### Canonical ownership by plugin

| Plugin | Canonical responsibility |
|---|---|
| `agent-web-interface` | Browser tooling only |
| `app-exploration` | Live product exploration and evidence capture |
| `test-analysis` | Shared planning/specification/review |
| `playwright-automation` | Playwright-specific analysis, authoring, review, and flake repair |
| `robot-automation` | Robot-specific analysis, authoring, review, and flake repair |

### New shared artifact contract

All future implementations in the split suite must use these artifact handoffs:

- `e2e-plan/exploration-report.md`
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md`

Ownership of those artifacts:

| Artifact | Producer | Consumer |
|---|---|---|
| `e2e-plan/exploration-report.md` | `app-exploration` | `test-analysis`, execution plugins when selector verification is needed |
| `e2e-plan/coverage-plan.md` | `test-analysis` | execution plugins |
| `test-cases/<feature>.md` | `test-analysis` | execution plugins |

## Skill Ownership Mapping

This section records the ownership map used to move skills into their canonical homes. It includes
the historical `plugins/e2e-test-builder/skills/` source paths that were removed during cleanup.

### New skills introduced in phase 1

| Future plugin | Skill | Purpose |
|---|---|---|
| `app-exploration` | `explore-app` | Explore the live app, capture evidence, record blockers, and write `e2e-plan/exploration-report.md` |
| `playwright-automation` | `add-playwright-tests` | Canonical Playwright workflow entry skill |

### Historical `e2e-test-builder` skill mapping

| Current skill path | Future canonical owner | Future canonical skill |
|---|---|---|
| `plugins/e2e-test-builder/skills/add-e2e-tests/SKILL.md` | `playwright-automation` | `add-playwright-tests` |
| `plugins/e2e-test-builder/skills/analyze-test-codebase/SKILL.md` | `playwright-automation` | `analyze-test-codebase` |
| `plugins/e2e-test-builder/skills/fix-flaky-tests/SKILL.md` | `playwright-automation` | `fix-flaky-tests` |
| `plugins/e2e-test-builder/skills/generate-test-cases/SKILL.md` | `test-analysis` | `generate-test-cases` |
| `plugins/e2e-test-builder/skills/plan-test-coverage/SKILL.md` | `test-analysis` | `plan-test-coverage` |
| `plugins/e2e-test-builder/skills/review-test-cases/SKILL.md` | `test-analysis` | `review-test-cases` |
| `plugins/e2e-test-builder/skills/review-test-code/SKILL.md` | `playwright-automation` | `review-test-code` |
| `plugins/e2e-test-builder/skills/write-test-code/SKILL.md` | `playwright-automation` | `write-test-code` |

### Current `robot-automation` execution-skill mapping

| Active skill path | Canonical owner after cleanup | Canonical skill |
|---|---|---|
| `plugins/robot-automation/skills/add-robot-tests/SKILL.md` | `robot-automation` | `add-robot-tests` |
| `plugins/robot-automation/skills/analyze-test-codebase/SKILL.md` | `robot-automation` | `analyze-test-codebase` |
| `plugins/robot-automation/skills/fix-flaky-tests/SKILL.md` | `robot-automation` | `fix-flaky-tests` |
| `plugins/robot-automation/skills/review-test-code/SKILL.md` | `robot-automation` | `review-test-code` |
| `plugins/robot-automation/skills/write-robot-code/SKILL.md` | `robot-automation` | `write-robot-code` |

### Historical `robot-automation` shared-skill mapping

| Removed skill path | Canonical owner after cleanup | Canonical skill |
|---|---|---|
| `plugins/robot-automation/skills/generate-test-cases/SKILL.md` | `test-analysis` | `generate-test-cases` |
| `plugins/robot-automation/skills/plan-test-coverage/SKILL.md` | `test-analysis` | `plan-test-coverage` |
| `plugins/robot-automation/skills/review-test-cases/SKILL.md` | `test-analysis` | `review-test-cases` |

### Rules for the moved shared skills

The moved shared skills are:

- `plan-test-coverage`
- `generate-test-cases`
- `review-test-cases`

After the split:

- they exist canonically under `test-analysis`
- they are no longer canonically owned by either framework plugin
- Playwright and Robot workflows consume them through `test-analysis`

### `plan-test-coverage` behavioral rewrite

`plan-test-coverage` must be rewritten as a planning skill that depends on exploration evidence.

It must:

- read `e2e-plan/exploration-report.md` when real product evidence is required
- produce `e2e-plan/coverage-plan.md`
- clearly state when planning is blocked because required exploration evidence is missing

It must not:

- behave as the exploration skill
- perform only a lightweight pseudo-exploration and then plan from partial assumptions
- replace `explore-app`

## Workflow And Marketplace Changes

This section names the exact repo touchpoints that later implementation must update.

### New plugin directories

Later implementation must introduce:

- `plugins/app-exploration/`
- `plugins/test-analysis/`
- `plugins/playwright-automation/`

Later implementation must keep:

- `plugins/agent-web-interface/`
- `plugins/robot-automation/`

### Marketplace manifests

Later implementation must update these marketplace registries:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `.athena-workflow/marketplace.json`

Required outcomes:

- register the new shared plugins
- register `playwright-automation`
- preserve `robot-automation`
- remove the installable `e2e-test-builder` plugin surface

### Workflow dependency refs

Later implementation must update these workflow manifests:

- `workflows/e2e-test-builder/workflow.json`
- `workflows/robot-automation/workflow.json`

#### Phase-1 workflow behavior

The `e2e-test-builder` workflow keeps its current workflow name for continuity, but its plugin dependencies change to:

- `agent-web-interface`
- `app-exploration`
- `test-analysis`
- `playwright-automation`

The `robot-automation` workflow keeps its current workflow name and changes its plugin dependencies to:

- `agent-web-interface`
- `app-exploration`
- `test-analysis`
- `robot-automation`

### Top-level docs and inventories

Later implementation must update any docs that enumerate plugins, workflows, or skill ownership. At minimum:

- `README.md`
- `docs/skills-compatibility.md`
- any future skill inventory, architecture, or migration docs that still describe `e2e-test-builder` as the canonical Playwright owner of shared planning/spec skills

## Compatibility Shape

`e2e-test-builder` no longer exists as an installable plugin. Phase 1 preserves continuity through
the workflow name, not through a plugin alias.

### Phase-1 compatibility policy

- `playwright-automation` is the canonical Playwright execution plugin.
- `e2e-test-builder` is not an installable plugin surface.
- New architecture docs must treat `e2e-test-builder` as a workflow-only legacy name.
- The `e2e-test-builder` workflow name stays in place initially.

### Expected role of the legacy name

During this phase, `e2e-test-builder` should behave as a workflow continuity label rather than a
plugin alias or a second canonical home for the architecture.

That means:

- it should not remain the authoritative owner of shared planning/spec skills
- it should not exist as an installable plugin surface
- it may remain only as a workflow name while users move to `playwright-automation`

## Non-Goals

Phase 1 does not include:

- creation of `exploratory-testing`, `smoke-testing`, or `regression-testing` plugins
- introduction of Cypress, Appium, API, or performance execution plugins
- restructuring unrelated plugins such as `site-knowledge`, `md-export`, or `web-bench`
- renaming the `robot-automation` plugin or workflow

Those items belong to the long-term suite design in [Future Suite Catalog](plugin-suite-future-suite.md).
