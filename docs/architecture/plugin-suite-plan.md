# Plugin Suite Plan

This document is the maintainers' source of truth for the testing-plugin suite. It explains why the current layout is too coupled, what the layered end-state should be, and what backlog remains to reach that end-state.

See also:
- [Immediate Split Plan](plugin-suite-immediate-split.md)
- [Future Suite Catalog](plugin-suite-future-suite.md)

## Overview

The current marketplace grew around two framework-specific testing plugins:

- `e2e-test-builder` for Playwright
- `robot-automation` for Robot Framework

Those plugins currently mix multiple responsibilities:

- live product exploration
- coverage planning
- test-case generation and review
- framework-specific authoring
- framework-specific code review
- framework-specific flake diagnosis

That layout worked for the first two execution frameworks, but it does not scale well. Shared testing cognition is duplicated across framework plugins, `plan-test-coverage` is forced to behave as both planner and pseudo-explorer, and workflows cannot cleanly express the difference between product understanding and framework execution.

The target state is a layered testing suite:

- tooling plugins that provide browser or platform control
- shared plugins that capture product evidence and define what should be tested
- framework/platform plugins that implement and stabilize executable tests
- intent plugins that express confidence goals such as exploratory, smoke, or regression testing

## Why The Current Split Is Wrong

### Duplicated shared skills

Before the plugin cleanup, the same planning/spec-review responsibilities lived in both
`plugins/e2e-test-builder/skills/` and `plugins/robot-automation/skills/`:

- `plan-test-coverage`
- `generate-test-cases`
- `review-test-cases`

That duplication creates drift risk. When one framework pipeline tightens an evidence rule, updates a review checklist, or changes the spec contract, the other pipeline can easily lag behind.

### Mixed responsibilities inside framework plugins

Both framework plugins currently own skills that belong to different conceptual layers:

- product discovery
- test design
- framework authoring
- runtime debugging

That makes plugin names less truthful. A framework plugin should primarily answer "how do we automate this in framework X?" It should not also be the canonical source of truth for product exploration and general test planning.

### Weak layering between exploration and planning

`plan-test-coverage` is currently asked to do too much. It performs a light site inspection, infers flows when browser tooling is unavailable, and produces a coverage plan. That weakens the evidence model:

- exploration evidence is not first-class
- planning can proceed without a durable observation artifact
- workflows do not clearly separate "understand reality" from "design coverage"

The target architecture makes `explore-app` the exploration skill and positions `plan-test-coverage` as an evidence-consuming planning skill.

### Workflow composition does not scale

Current workflows bind directly to framework plugins that still contain shared logic. That is manageable for two frameworks, but it becomes expensive once more execution families arrive:

- Playwright
- Robot Framework
- Cypress
- Appium
- API testing
- performance runners

The marketplace needs workflows that can compose shared layers plus a single execution layer, rather than forcing each execution plugin to clone the same shared testing logic.

## Target Layered Architecture

The target layered architecture is:

| Layer | Plugin(s) | Responsibility |
|---|---|---|
| Tooling | `agent-web-interface` | Live browser interaction and selector/form inspection |
| Shared product understanding | `app-exploration` | Product exploration, evidence capture, blocker reporting |
| Shared test thinking | `test-analysis` | Coverage planning, test-case generation, test-case review |
| Framework execution | `playwright-automation`, `robot-automation` | Codebase analysis, executable test authoring, code review, flake repair |
| Intent families | `exploratory-testing`, `smoke-testing`, `regression-testing` | Confidence-oriented layers such as exploratory, smoke, and regression testing |

### Design rules

These rules govern the split:

1. Exploration and evidence are separate from framework implementation.
2. `plan-test-coverage` is not the exploration skill. It consumes exploration evidence.
3. Shared skills have a single canonical owner. They are not duplicated per framework.
4. Framework plugins own framework-specific analysis, authoring, code review, and runtime debugging only.
5. Workflows compose shared plugins plus one execution plugin.
6. Intent plugins express confidence goals, not framework behavior.

## Naming And Ownership Rules

The canonical shared plugin names are:

- `app-exploration`
- `test-analysis`

The active execution plugin names are:

- `playwright-automation`
- `robot-automation`

The legacy Playwright name:

- `e2e-test-builder`

now survives only as a workflow identifier for continuity. The installable plugin surface has been
removed, and canonical ownership centers on `playwright-automation`.

### Skill ownership rule

Each testing skill must have exactly one canonical owner:

- exploration skills belong to `app-exploration`
- shared planning/spec skills belong to `test-analysis`
- Playwright execution skills belong to `playwright-automation`
- Robot execution skills belong to `robot-automation`

No shared planning/spec skill should remain canonically owned by both Playwright and Robot plugins after the split.

## Active End-State

The repository is now working toward the full core suite directly rather than treating intent
families as a later phase. The active target set is:

- `agent-web-interface`
- `app-exploration`
- `test-analysis`
- `exploratory-testing`
- `smoke-testing`
- `regression-testing`
- `playwright-automation`
- `robot-automation`

The implementation details for the current execution backlog live in
[Immediate Split Plan](plugin-suite-immediate-split.md).

## Later Expansion

After the core suite above is stable, the marketplace can add more execution families such as:

- `cypress-automation`
- `appium-automation`
- `api-test-automation`
- `performance-automation`

Additional expansion ideas and dependency rules live in
[Future Suite Catalog](plugin-suite-future-suite.md).

## Compatibility And Deprecation

The compatibility policy for this split is:

1. Preserve workflow continuity where practical.
2. Keep the `e2e-test-builder` workflow name initially.
3. Introduce `playwright-automation` as the canonical Playwright execution plugin.
4. Remove the `e2e-test-builder` plugin surface rather than keeping an installable compatibility alias.
5. Treat `e2e-test-builder` as workflow continuity only, not as a second plugin home for shared skills.

### Compatibility consequences

- New architecture docs, ownership maps, and future plugin additions should use `playwright-automation`, not `e2e-test-builder`, as the canonical Playwright name.
- Workflows may preserve old names longer than plugins if that improves user continuity.

### Shared contracts

The split depends on a stable shared artifact contract:

- `e2e-plan/exploration-report.md`
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md`

Those artifacts let workflows and plugins hand off work cleanly across layers:

- `app-exploration` produces exploration evidence
- `test-analysis` consumes evidence and produces plans/specs
- execution plugins consume plans/specs and produce executable tests

That contract is mandatory for future framework additions and should remain stable across the suite.

## Implementation Backlog

The remaining work to reach the active end-state is:

1. Make all active docs describe the same core plugin set:
   `agent-web-interface`, `app-exploration`, `test-analysis`, `exploratory-testing`,
   `smoke-testing`, `regression-testing`, `playwright-automation`, and `robot-automation`.
2. Keep canonical artifact ownership explicit and stable:
   `app-exploration` owns `e2e-plan/exploration-report.md`, and `test-analysis` owns
   `e2e-plan/coverage-plan.md` plus `test-cases/<feature>.md`.
3. Narrow every intent plugin so it adds intent-specific value without re-owning shared
   exploration or test-analysis artifacts.
4. Add workflow families for intent plugins where cross-plugin orchestration is required, and keep
   workflow sequencing in `workflow.md` rather than encoding the full sequence inside plugin skills.
5. Keep framework plugins focused on framework-local concerns only:
   codebase analysis, executable authoring, code review, and flake repair.
6. Add validator coverage for the full suite shape, including marketplace registration, workflow
   dependencies, artifact ownership, and stale legacy-surface detection.
7. Treat later execution families such as Cypress, Appium, API, and performance as expansion work
   after the core suite above is internally consistent.
