# Plugin Suite Immediate Split

This document is the decision-complete execution plan for moving the marketplace from the old
framework-centric testing layout to the layered end-state plugin suite.

See also:
- [Plugin Suite Plan](plugin-suite-plan.md)
- [Future Suite Catalog](plugin-suite-future-suite.md)

## Current Program Goal

The current program creates the clean shared/framework split and introduces the intent layer now.

The current program must:

- introduce `app-exploration`
- introduce `test-analysis`
- introduce `exploratory-testing`
- introduce `smoke-testing`
- introduce `regression-testing`
- introduce `playwright-automation`
- retain and slim `robot-automation`
- keep `agent-web-interface` unchanged
- preserve workflow continuity where practical

The current program must not:

- redesign unrelated plugins such as `site-knowledge`, `md-export`, or `web-bench`
- rename the `robot-automation` workflow

## Exact Plugin Layout For The Active End-State

The target plugin set for the active end-state is:

- `agent-web-interface`
- `app-exploration`
- `test-analysis`
- `exploratory-testing`
- `smoke-testing`
- `regression-testing`
- `playwright-automation`
- `robot-automation`

The legacy `e2e-test-builder` name survives only as a workflow identifier for continuity.

### Canonical ownership by plugin

| Plugin | Canonical responsibility |
|---|---|
| `agent-web-interface` | Browser tooling only |
| `app-exploration` | Live product exploration and evidence capture |
| `test-analysis` | Shared planning/specification/review |
| `exploratory-testing` | Exploratory charters — risk hypotheses and investigation focus |
| `smoke-testing` | Minimum critical-path confidence selection and smoke-scope governance |
| `regression-testing` | Broader rerunnable confidence planning and regression-scope governance |
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

### New skills introduced in the active end-state program

| Plugin | Skill | Purpose |
|---|---|---|
| `app-exploration` | `capture-feature-evidence` | Explore the live app, capture evidence, record blockers, and write `e2e-plan/exploration-report.md` |
| `exploratory-testing` | `exploratory-test-writer` | Frame risk hypotheses and investigation focus via exploratory charters |
| `smoke-testing` | `define-smoke-scope` | Define the minimum critical-path confidence scope and write `e2e-plan/smoke-charter.md` |
| `regression-testing` | `define-regression-scope` | Define rerunnable regression scope and write `e2e-plan/regression-charter.md` |
| `playwright-automation` | `add-playwright-tests` | Canonical Playwright workflow entry skill |

Optional plugin-owned intent artifacts:

- `e2e-plan/exploratory-charter.md`
- `e2e-plan/smoke-charter.md`
- `e2e-plan/regression-charter.md`

These are not part of the core shared artifact contract. They are intent-layer planning aids owned
by their respective plugins.

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
- replace `capture-feature-evidence`

## Workflow And Marketplace Changes

This section names the exact repo touchpoints that later implementation must update.

### New plugin directories

The repository now includes or is completing:

- `plugins/app-exploration/`
- `plugins/test-analysis/`
- `plugins/exploratory-testing/`
- `plugins/smoke-testing/`
- `plugins/regression-testing/`
- `plugins/playwright-automation/`

The repository continues to keep:

- `plugins/agent-web-interface/`
- `plugins/robot-automation/`

### Marketplace manifests

The implementation updates these marketplace registries:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `.athena-workflow/marketplace.json`

Required outcomes:

- register the new shared plugins
- register `exploratory-testing`
- register `smoke-testing`
- register `regression-testing`
- register `playwright-automation`
- preserve `robot-automation`
- remove the installable `e2e-test-builder` plugin surface

### Workflow dependency refs

The implementation now includes these workflow manifests:

- `workflows/e2e-test-builder/workflow.json`
- `workflows/robot-automation/workflow.json`
- `workflows/exploratory-testing/workflow.json`
- `workflows/smoke-testing/workflow.json`
- `workflows/regression-testing/workflow.json`

#### Current workflow behavior

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

Intent workflows own sequencing for the intent layer and hand off to the appropriate execution
workflow when runnable automation is requested.

## Implementation Checklist

The current execution backlog to reach the active end-state is:

1. Finish aligning active docs and inventories to the same plugin set:
   `agent-web-interface`, `app-exploration`, `test-analysis`, `exploratory-testing`,
   `smoke-testing`, `regression-testing`, `playwright-automation`, and `robot-automation`.
2. Keep the shared artifact contract stable and enforce it in skills, workflows, and validators:
   `app-exploration` owns `e2e-plan/exploration-report.md`, and `test-analysis` owns
   `e2e-plan/coverage-plan.md` plus `test-cases/<feature>.md`.
3. Narrow `exploratory-testing` so it contributes exploratory intent, risk framing, and
   hypothesis-driven guidance without replacing `capture-feature-evidence` or `test-analysis`.
4. Keep `smoke-testing` and `regression-testing` plugin ownership narrow and free of framework
   authoring duplication.
5. Keep workflow sequencing in `workflow.md` and plugin skills capability-local.
6. Keep Playwright and Robot plugins limited to framework-local analysis, authoring, review, and
   flake repair.
7. Extend suite validators so they catch stale ownership drift, registry mismatches, workflow
   dependency mistakes, and legacy-surface regressions.

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

The current program does not include:

- introduction of Cypress, Appium, API, or performance execution plugins
- restructuring unrelated plugins such as `site-knowledge`, `md-export`, or `web-bench`
- renaming the `robot-automation` plugin or workflow

Those items belong to the long-term suite design in [Future Suite Catalog](plugin-suite-future-suite.md).
