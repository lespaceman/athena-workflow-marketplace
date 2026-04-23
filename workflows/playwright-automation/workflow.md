# Playwright Automation Workflow

You add comprehensive, high-quality Playwright tests to codebases.

## Pinned Plugins

This workflow is authored against the plugins pinned in `workflow.json`. Use these plugin surfaces
unless the pinned versions change:

| Plugin | Pinned Version | Skills Used Here |
|--------|----------------|------------------|
| `agent-web-interface` | `1.0.12` | browser MCP companion skill loaded by scoped exploration subagents |
| `app-exploration` | `0.1.7` | `map-feature-scope`, `capture-feature-evidence` |
| `test-analysis` | `0.2.8` | `plan-test-coverage`, `generate-test-cases`, `review-test-cases` |
| `playwright-automation` | `0.1.5` | `add-playwright-tests`, `analyze-test-codebase`, `write-test-code`, `review-test-code`, `fix-flaky-tests` |

## Skills

Load the relevant skill before each activity. Skills carry the implementation knowledge — locator strategies, anti-patterns, code templates — so you don't have to reinvent them each session.

| Activity | Skill |
|----------|-------|
| Full workflow entry point and orchestration | `add-playwright-tests` |
| Analyze test setup, config, conventions | `analyze-test-codebase` |
| Quickly map a broad feature into bounded exploration units | `map-feature-scope` |
| Explore the product and capture evidence | `capture-feature-evidence` |
| Decide what to test, coverage gaps, priorities | `plan-test-coverage` |
| Create TC-ID specs from shared evidence | `generate-test-cases` |
| Review TC-ID specs before implementation | `review-test-cases` |
| Write, edit, or refactor test code | `write-test-code` |
| Review test code before execution signoff | `review-test-code` |
| Debug test failures, check stability | `fix-flaky-tests` |

## Orientation Steps

Session 1 begins by loading `add-playwright-tests` as the top-level workflow skill. The other
skills are focused sub-steps within that workflow, not competing entry points.

### Understand the codebase

Load `analyze-test-codebase` and follow its methodology. Key questions: does Playwright exist?
What conventions are in use? What helpers or fixtures are already available? If Playwright is
missing, follow the scaffolding guidance from `add-playwright-tests`.

### Understand the product

Choose the lightest safe exploration path for the requested problem:

- If the request is narrow and obviously single-surface, go straight to `capture-feature-evidence`.
- If the request may span multiple routes, tabs, overlays, roles, or primary interactive surfaces,
  load `map-feature-scope` first. It writes `e2e-plan/feature-map.md`, which tells the
  orchestrator whether one exploration run is enough or whether multiple scoped `capture-feature-evidence` runs
  should follow.

Load `capture-feature-evidence` after scoping and capture either:
- `e2e-plan/exploration-report.md` for genuinely single-surface features
- `e2e-plan/exploration/<subfeature>.md` for mapped multi-surface features

The orchestrator then synthesizes `e2e-plan/exploration-report.md` as the canonical rollup handoff
into the Playwright execution layer.

### Plan coverage when evidence is sufficient

Load `plan-test-coverage` after exploration. It consumes the exploration report and produces
`e2e-plan/coverage-plan.md`; it is not the exploration step.

### Observations

After orientation, preserve the concrete product evidence in `e2e-plan/exploration-report.md` and,
for mapped features, the underlying `e2e-plan/exploration/*.md` files. When downstream work depends
on real product behavior, these artifacts gate the next phases. If the required exploration cannot
be completed, stop rather than guessing.

## Workflow Sequence

The common progression is:

**analyze codebase → map feature scope → deep-explore the scoped areas → synthesize rollup exploration report → plan coverage → generate specs → review specs → write tests → review code → run tests**

Treat that as a dependency graph, not a rigid script. The right path depends on the problem:

- Narrow single-surface feature: `analyze codebase → capture-feature-evidence → plan → specs → review → write → review → run`
- Broad multi-surface feature: `analyze codebase → map-feature-scope → parallel/serial scoped capture-feature-evidence runs → rollup → plan → specs → review → write → review → run`
- Existing mature codebase with current artifacts: reuse valid `feature-map.md`, exploration, or
  spec artifacts instead of regenerating them
- Direct debugging request: if tests already exist and the main problem is instability, load
  `fix-flaky-tests` after confirming the current artifacts and conventions are still trustworthy

Each step has prerequisites. The important gating relationships:

| Before you can... | You must have... |
|---|---|
| Generate specs (`generate-test-cases`) | `e2e-plan/exploration-report.md`, plus mapped `e2e-plan/exploration/*.md` files when the feature was decomposed |
| Write test code (`write-test-code`) | Specs that passed review (Gate 1) |
| Run tests | Code that passed review (Gate 2) |

Use `analyze-test-codebase` before `write-test-code` if conventions are still unclear. If tests fail or are unstable, load `fix-flaky-tests` before retrying.

Shared exploration is mandatory whenever the agent needs real product evidence to understand the
flow, selectors, validation, navigation, or error behavior. Broad features must be decomposed first
so the main agent can dispatch bounded scoped explorations instead of one oversized browser session.
Simple features can skip decomposition. If the browser is unavailable or the target cannot be
explored and that evidence is required to proceed safely, do not continue with planning, spec
generation, or test writing from assumptions.

## Depth Targets

Concrete floors downstream gates enforce. These exist because prior runs delivered 12-test specs that were 70% visibility checks — the suite passed, and the feature was still uncovered.

A feature is **non-trivial** when exploration touched more than two routes, or the UI has more than
one primary interactive surface (e.g., a timeline + playback controls + an overlay menu all count
as one feature). Such features should normally pass through `map-feature-scope` before deep
exploration.

- **Exploration inventory** — non-trivial features require ≥20 distinct interactive elements recorded with selector candidates; ≥3 meaningful error, validation, or empty states deliberately triggered; and a labeled "elements not yet reached" list so downstream skills know the scope limits.
- **TC-ID count** — non-trivial features require ≥15 TCs. If the author cannot reach 15, the spec has out-run the exploration; return to `capture-feature-evidence` rather than padding.
- **Functional-to-visibility ratio** — ≥60% of TCs in a spec must assert a state change (URL transition, data mutation, observable side effect, element value change after action). Render-existence assertions count toward the remaining ≤40%. A test that only checks `toBeVisible()` on an element the test never interacted with is visibility, not functional coverage.

These targets are not soft suggestions. Gate 1 rejects specs that violate them with feedback pointing back at the gap.

## Deferred Governance

"Deferred" is a scope boundary, not an escape valve. Every deferred TC must carry three fields in the spec:

- **blocker** — the concrete thing preventing automation (e.g., "requires seeded data", "third-party iframe with no test hook", "production-only API")
- **un-defer plan** — what changes to make this testable (e.g., "add fixture once backend ticket APM-412 lands")
- **scope** — `this-sprint` or `out-of-scope`

Cap: at most **20% of TCs** in a spec may be deferred. Over that, the spec fails Gate 1 with "scope too narrow — revisit exploration"; the fix is more evidence, not more deferrals.

## Quality Gates

Four gates are mandatory. The first two are review-only — they produce findings but do not modify files. Gate 4 runs after tests pass and audits coverage against exploration. These gates exist because prior experience showed that skipping review leads to cascading rework: bad specs produce bad tests, bad tests produce confusing failures, and "12 tests passed" can still mean the feature is uncovered.

### Gate 1: Review specs

After `generate-test-cases`, before `write-test-code`:
- Load `review-test-cases` and run against `test-cases/<feature>.md`
- If **NEEDS REVISION** — revise the spec, then rerun `review-test-cases` before writing code

### Gate 2: Review code

After `write-test-code`, before running tests:
- Load `review-test-code` and run against the test files
- If **NEEDS REVISION** — revise the code, then rerun `review-test-code` before running tests

### Gate 3: Test execution

Run `npx playwright test <file> --reporter=list 2>&1` directly in the main agent. If tests fail, load `fix-flaky-tests`.

**Retry policy:** no fixed numeric cap. The agent should continue fix-and-rerun cycles only while each cycle produces meaningful progress: a new root-cause hypothesis, a concrete code/config change, or materially new failure evidence. Stop when the issue is no longer moving, the next rerun would repeat the same experiment, or the blocker is external to the test code (missing environment, access, product bug, unclear requirements).

**Execution order for brownfield suites:**
- Run the newly added or changed tests in isolation until they are stable.
- Then run the relevant feature file or suite.
- Only run broader regression after the new coverage is green in isolation.
- If unrelated pre-existing tests fail, classify them separately as baseline instability. If they must be fixed because of shared-state leakage or broken shared infrastructure, report that work separately from the new TC implementation set.

**Gate reset rule:** if the planned TC set, spec, coverage plan, or executed test file changes after Gate 2 in a way that adds, removes, defers, or materially rewrites covered behavior, reset to the earliest affected gate:
- rerun Gate 2 for changed test code
- rerun Gate 1 if the spec or deferral set changed
- restart the Gate 3 consecutive-green counter

Do not count pre-change runs toward post-change signoff.

**Execution-time deferral policy:** deferral discovered during Gate 3 is exceptional. Only defer when the blocker is concrete and external to the current test implementation, the spec and coverage plan are updated with blocker, un-defer plan, and scope, and the run returns to the required earlier gate(s) before signoff. Do not defer to avoid re-exploration, locator verification, or code review. If the blocker is selector uncertainty, DOM drift from exploration, viewport/layout mismatch, or "needs browser confirmation", stop execution and refresh exploration evidence first.

Mandatory re-exploration triggers include:
- execution viewport or layout drift for coordinate- or layout-sensitive interactions
- lost selector uniqueness compared with exploration
- labels or control text absent, duplicated, or rendered outside the explored container
- workaround-heavy fixes such as force-clicks, JavaScript-dispatched clicks, coordinate clicks, or page-wide text/count oracles becoming the only apparent path forward

**Gate 3 run ledger:** maintain a ledger in the session tracker or execution notes. For each counted run record:
- exact command
- exact test set or filter
- whether the run is eligible for signoff
- files changed since the prior run
- pass/fail counts
- whether the consecutive-green counter reset

### Gate 4: Coverage gap audit

After Gate 3 passes, dispatch a fresh subagent to run a coverage audit. It receives the exploration report's element inventory and the executed test suite as inputs, and classifies each observed element as one of:

- `covered-functional` — at least one test triggers the action and asserts a state change
- `covered-visibility-only` — a test references the element but does not exercise it functionally
- `uncovered` — no test touches it

The audit writes `e2e-plan/coverage-audit.md` and returns a verdict:

- **GREEN** — every promoted P0/P1 inventory-backed behavior is covered functionally, or any uncovered item is explicitly out of current scope and was never promoted into the accepted spec or coverage plan
- **YELLOW** — one or more promoted items remain deferred, partially covered, or visibility-only, but the operator has explicitly accepted those gaps with written reasoning
- **RED** — uncovered, visibility-only, or deferred promoted items remain without explicit acceptance, or the exploration/spec/execution chain is inconsistent

A promoted TC deferred during or after execution cannot end in **GREEN** unless the spec and coverage plan were revised, re-reviewed, and explicitly re-baselined before Gate 4.

"Tests passed" does not mean done. Gate 4 decides done.

## Delegation Constraints

Four delegation rules are mandatory. Earlier runs treated delegation as optional and produced
shallow exploration (no element inventory), self-reviewed specs (gaps the author anchored on), and
completion signals the authoring agent could not honestly grade.

**1. Feature mapping runs before broad exploration, not before every exploration.** If the
requested feature may span multiple routes, tabs, overlays, roles, or primary interactive surfaces,
dispatch `map-feature-scope` first. For obviously narrow single-surface requests, skip it and go
straight to `capture-feature-evidence`. The output of mapping is `e2e-plan/feature-map.md`, not a deep evidence
report.

**2. Deep exploration runs in scoped subagents.** The main agent does not browse. Dispatch
`capture-feature-evidence` work via the Task tool and invoke each subagent with access to the
`mcp__plugin_agent-web-interface_browser__*` tools. If the feature map says `MULTI-SURFACE`,
dispatch one fresh subagent per `parallel-safe = yes` row and run `parallel-safe = no` rows
serially. Each subagent writes a structured scoped artifact, not a narrative summary.

**3. Each review gate runs in a fresh subagent.** The agent that wrote the spec does not run
`review-test-cases`. The agent that wrote the code does not run `review-test-code`. Dispatch each
review via a new Task call that receives only the artifact path and the review skill to load — not
the authoring transcript. Self-review consistently misses the gaps the author anchored on; a fresh
context is the cheapest way to get an independent read.

**4. Test execution stays in the main agent.** Test output is the proof artifact — the main agent
runs `npx playwright test` directly so it can verify the output is real and interpret failures in
context. A subagent's summary of test results isn't trustworthy enough to gate completion.

Gate 4 (coverage audit) follows rule 2: dispatch a fresh subagent, feed it the exploration report and test suite, let it produce `coverage-audit.md`.

Pass file paths, conventions, and concrete output expectations into every Task call. Instruct each subagent to load the appropriate skill before acting.

## Guardrails

Quick-reference checklist — in addition to the session protocol's guardrails:

- Browse the product before writing specs or tests
- **Decompose broad features before deep exploration** — use `map-feature-scope`
- **Delegate scoped exploration to subagents** — the main agent does not call browser tools directly
- Record observed behavior before turning exploration into specs or code
- **Each review gate runs in a fresh subagent**, not the artifact's author
- Spec meets depth targets: ≥15 TCs for non-trivial features, ≥60% functional assertions, ≤20% deferred
- **Stabilize new or changed tests in isolation before broader regression** in brownfield suites
- **Reset the affected gates if scope, spec, coverage plan, or executed test set changes after Gate 2**
- **Keep a Gate 3 run ledger** so signoff runs, resets, and file changes are auditable
- Run tests before marking test work as done
- **Run the Gate 4 coverage audit after tests pass** — tests passing is necessary but not sufficient
