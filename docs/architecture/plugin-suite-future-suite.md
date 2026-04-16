# Plugin Suite Future Suite

This document defines the broader testing-plugin catalog beyond the current core suite. The core
end-state now includes the shared layers, intent layers, and Playwright/Robot execution plugins;
this catalog records their boundaries and the later expansion families that may follow.

See also:
- [Plugin Suite Plan](plugin-suite-plan.md)
- [Immediate Split Plan](plugin-suite-immediate-split.md)

## Plugin Family Catalog

The catalog is organized by responsibility, not only by framework.

### Tooling

#### `agent-web-interface`

Responsibility boundary:
- browser interaction and inspection capabilities
- live page state, selectors, forms, and navigation tooling

Owns skills such as:
- `agent-web-interface-guide`

Depends on:
- its own MCP/browser tooling only

Must not own:
- coverage planning
- framework-specific authoring
- testing-intent policy

### Shared layers

#### `app-exploration`

Responsibility boundary:
- product exploration
- evidence capture
- blocker reporting
- durable observation handoff

Owns skills such as:
- `explore-app`
- future exploration-oriented support skills if needed

Depends on:
- `agent-web-interface` when live browser interaction is needed

Must not own:
- framework-specific test code
- regression/smoke policy
- executable test review logic

#### `test-analysis`

Responsibility boundary:
- deciding what should be tested
- turning evidence into plans/specs
- reviewing test-case quality before implementation

Owns skills such as:
- `plan-test-coverage`
- `generate-test-cases`
- `review-test-cases`

Depends on:
- `app-exploration` when real product evidence is required

Must not own:
- framework-specific code authoring
- framework-specific flake repair
- live app exploration as its primary mode

### Testing-intent plugins in the active core suite

#### `exploratory-testing`

Responsibility boundary:
- exploratory charter definition — framing what to investigate and why
- risk hypothesis formulation and prioritization
- investigation focus guidance (where to probe deeper)

Does NOT own:
- live product exploration (owned by `explore-app` in `app-exploration`)
- coverage planning (owned by `plan-test-coverage` in `test-analysis`)
- test case generation (owned by `generate-test-cases` in `test-analysis`)

Owns skills such as:
- `exploratory-test-writer` — produces `e2e-plan/exploratory-charter.md` (optional, plugin-owned artifact)
- future risk-focused exploratory probes

Depends on:
- `agent-web-interface`
- `app-exploration`

Must not own:
- Playwright/Robot/Cypress/Appium authoring
- broad regression-suite management

#### `smoke-testing`

Responsibility boundary:
- defining and maintaining minimum critical confidence checks
- optimizing for fast, high-signal validation

Owns skills such as:
- `define-smoke-scope` — produces `e2e-plan/smoke-charter.md` (optional, plugin-owned artifact)
- future smoke coverage review helpers
- future candidate smoke selection helpers

Depends on:
- `test-analysis`
- one execution plugin when smoke suites are automated

Must not own:
- product exploration as a primary responsibility
- framework-specific authoring patterns

#### `regression-testing`

Responsibility boundary:
- broad confidence planning across changed or high-risk areas
- selecting and maintaining rerunnable regression scope

Owns skills such as:
- `define-regression-scope` — produces `e2e-plan/regression-charter.md` (optional, plugin-owned artifact)
- future regression gap review helpers
- future rerun recommendation helpers

Depends on:
- `test-analysis`
- one execution plugin when regression suites are automated

Must not own:
- framework-specific authoring
- exploratory-session execution logic

### Framework and platform execution plugins

#### `playwright-automation`

Responsibility boundary:
- Playwright-specific codebase analysis
- Playwright test authoring
- Playwright code review
- Playwright flake diagnosis

Owns skills such as:
- `add-playwright-tests`
- `analyze-test-codebase`
- `write-test-code`
- `review-test-code`
- `fix-flaky-tests`

Depends on:
- `test-analysis`
- `app-exploration` when evidence-backed selector/flow validation is required

Must not own:
- canonical shared planning/specification skills
- intent-specific smoke/regression policy

#### `robot-automation`

Responsibility boundary:
- Robot-specific codebase analysis
- Robot suite authoring
- Robot code review
- Robot flake diagnosis

Owns skills such as:
- `add-robot-tests`
- `analyze-test-codebase`
- `write-robot-code`
- `review-test-code`
- `fix-flaky-tests`

Depends on:
- `test-analysis`
- `app-exploration` when evidence-backed selector/flow validation is required

Must not own:
- canonical shared planning/specification skills
- intent-specific smoke/regression policy

#### `cypress-automation`

Responsibility boundary:
- Cypress-specific analysis, authoring, review, and stabilization

Owns skills such as:
- `add-cypress-tests`
- `analyze-test-codebase`
- `write-test-code`
- `review-test-code`
- `fix-flaky-tests`

Depends on:
- `test-analysis`
- `app-exploration` when live product evidence is required

Must not own:
- shared planning/specification
- intent-layer policy

#### `appium-automation`

Responsibility boundary:
- Appium/mobile execution analysis and authoring

Owns skills such as:
- `add-appium-tests`
- `analyze-test-codebase`
- `write-test-code`
- `review-test-code`
- `fix-flaky-tests`

Depends on:
- shared analysis/exploration layers
- any future platform-specific mobile tooling plugin if one is introduced

Must not own:
- shared planning/specification
- intent-layer policy

#### `api-test-automation`

Responsibility boundary:
- API test execution analysis and authoring

Owns skills such as:
- `add-api-tests`
- `analyze-test-codebase`
- `write-test-code`
- `review-test-code`
- `fix-flaky-tests`

Depends on:
- `test-analysis`
- `app-exploration` only when UI or product behavior is part of the contract under test

Must not own:
- shared planning/specification
- browser tooling

#### `performance-automation`

Responsibility boundary:
- performance test authoring, execution planning, and result analysis

Owns skills such as:
- performance test planning
- performance test authoring
- performance result review and analysis

Depends on:
- `test-analysis` for scope and risk framing
- future performance tooling or runners

Must not own:
- generic framework authoring for Playwright/Robot/Cypress/Appium
- shared planning/specification as a canonical home

### Out of scope for the current program

These existing plugins remain outside this architecture change:

- `site-knowledge`
- `md-export`
- `web-bench`

They can coexist with the suite, but they are not part of the testing-plugin split.

## Responsibility Matrix

| Family | Defines what to test | Explores live product | Writes executable tests | Reviews executable tests | Fixes flaky execution |
|---|---:|---:|---:|---:|---:|
| `agent-web-interface` | No | Tooling only | No | No | No |
| `app-exploration` | No | Yes | No | No | No |
| `test-analysis` | Yes | No, except evidence consumption | No | No | No |
| `exploratory-testing` | Intent only | No, consumes evidence | No | No | No |
| `smoke-testing` | Yes, smoke scope | No | No | No | No |
| `regression-testing` | Yes, regression scope | No | No | No | No |
| execution plugins | No, except framework feasibility feedback | Only when validating implementation assumptions | Yes | Yes | Yes |

## Dependency Rules

The full catalog follows these dependency rules.

1. Tooling plugins provide control surfaces; they do not define test strategy.
2. `app-exploration` depends on tooling when live interaction is required.
3. `test-analysis` depends on shared evidence, not on execution-framework ownership.
4. Testing-intent plugins depend on shared layers and optionally on one execution layer when they need runnable outputs.
5. Framework plugins depend on shared layers but do not canonically own shared planning/specification skills.

### Explicit anti-duplication rules

- intent plugins must not duplicate framework authoring logic
- framework plugins must not duplicate exploration/spec logic
- tooling plugins must not absorb planning/spec responsibilities

## Workflow Composition Rules

Workflows should be composed from layers instead of being owned by one large plugin.

### Standard composition model

When applicable, a workflow should combine:

1. one tooling dependency when live interaction is required
2. one shared exploration layer when product evidence is required
3. one shared analysis layer for plans/specs
4. one testing-intent layer when the task is defined by a confidence goal
5. one execution layer when the task produces automated assets

### Example composition patterns

Exploration-only workflow:
- `agent-web-interface`
- `app-exploration`

Playwright authoring workflow:
- `agent-web-interface`
- `app-exploration`
- `test-analysis`
- `playwright-automation`

Robot regression workflow:
- `agent-web-interface`
- `app-exploration`
- `test-analysis`
- `regression-testing`
- `robot-automation`

Smoke validation workflow:
- `test-analysis`
- `smoke-testing`
- one execution plugin when runnable assets are required

## Candidate Expansion Workflows

These are candidate workflow families beyond the current core suite, not immediate implementation
commitments.

- `playwright-automation` workflow family
  - shared analysis + Playwright execution
- `robot-automation` workflow family
  - shared analysis + Robot execution
- `playwright-smoke` workflow family
  - shared analysis + smoke intent + Playwright execution
- `robot-regression` workflow family
  - shared analysis + regression intent + Robot execution
- `cypress-automation` workflow family
  - shared analysis + Cypress execution
- `appium-automation` workflow family
  - shared analysis + Appium execution
- `api-regression` workflow family
  - shared analysis + regression intent + API execution
- `performance-baseline` workflow family
  - shared analysis + performance execution

The suite is intentionally moderately broad. It names the likely next families without overcommitting to a larger ecosystem of dedicated security, accessibility, visual-regression, or acceptance plugins at this stage.
