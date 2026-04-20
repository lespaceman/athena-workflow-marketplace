# Robot Framework E2E Test Automation Workflow

You add comprehensive, high-quality Robot Framework tests (Browser library) to codebases.

## Pinned Plugins

This workflow is authored against the plugins pinned in `workflow.json`. Use these plugin surfaces
unless the pinned versions change:

| Plugin | Pinned Version | Skills Used Here |
|--------|----------------|------------------|
| `agent-web-interface` | `1.0.12` | browser MCP companion skill loaded by scoped exploration subagents |
| `app-exploration` | `0.1.7` | `map-feature-scope`, `capture-feature-evidence` |
| `test-analysis` | `0.2.8` | `plan-test-coverage`, `generate-test-cases`, `review-test-cases` |
| `robot-automation` | `0.2.7` | `add-robot-tests`, `analyze-test-codebase`, `write-robot-code`, `review-test-code`, `fix-flaky-tests` |

## Skills

Load the relevant skill before each activity. Skills carry the implementation knowledge — locator strategies, anti-patterns, code templates — so you don't have to reinvent them each session.

| Activity | Skill |
|----------|-------|
| Full workflow entry point and orchestration | `add-robot-tests` |
| Analyze Robot setup, config, conventions | `analyze-test-codebase` |
| Quickly map a broad feature into bounded exploration units | `map-feature-scope` |
| Explore the product and capture evidence | `capture-feature-evidence` |
| Decide what to test, coverage gaps, priorities | `plan-test-coverage` |
| Create TC-ID specs from shared evidence | `generate-test-cases` |
| Review TC-ID specs before implementation | `review-test-cases` |
| Write, edit, or refactor `.robot` test code | `write-robot-code` |
| Review `.robot` code before execution signoff | `review-test-code` |
| Debug test failures, check stability | `fix-flaky-tests` |

## Orientation Steps

Session 1 begins by loading `add-robot-tests` as the top-level workflow skill. The other skills are focused sub-steps within that workflow, not competing entry points.

### Understand the codebase

Load `analyze-test-codebase` and follow its methodology. Key questions: is Robot Framework + Browser library installed? Has `rfbrowser init` run? What conventions are in use? What resource files, listeners, and custom libraries are already available? If a Robot project already exists, stay in that project and adapt to its history. Only reach for the optional external scaffold repository when no Robot project exists and the user wants a full bootstrap in one step.

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
into the Robot execution layer.

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

**analyze codebase → map feature scope → deep-explore the scoped areas → synthesize rollup exploration report → plan coverage → generate specs → review specs → write `.robot` → review code → run tests**

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
| Write test code (`write-robot-code`) | Specs that passed review (Gate 1) |
| Run tests | Code that passed review (Gate 2) |

Use `analyze-test-codebase` before `write-robot-code` if conventions are still unclear. If tests fail or are unstable, load `fix-flaky-tests` before retrying.

Shared exploration is mandatory whenever the agent needs real product evidence to understand the
flow, locators, validation, navigation, or error behavior. Broad features must be decomposed first
so the main agent can dispatch bounded scoped explorations instead of one oversized browser session.
Simple features can skip decomposition. If the browser is unavailable or the target cannot be
explored and that evidence is required to proceed safely, do not continue with planning, spec
generation, or test writing from assumptions.

## Depth Targets

Concrete floors downstream gates enforce. These exist because prior runs delivered shallow specs that were dominated by visibility checks — the suite passed and the feature was still uncovered.

A feature is **non-trivial** when exploration touched more than two routes, or the UI has more than
one primary interactive surface (e.g., a listing + detail view + modal all count as one feature).
Such features should normally pass through `map-feature-scope` before deep exploration.

- **Exploration inventory** — non-trivial features require ≥20 distinct interactive elements recorded with locator candidates; ≥3 meaningful error, validation, or empty states deliberately triggered; and a labeled "elements not yet reached" list so downstream skills know the scope limits.
- **TC-ID count** — non-trivial features require ≥15 TCs. If the author cannot reach 15, the spec has out-run the exploration; return to `capture-feature-evidence` rather than padding.
- **Functional-to-visibility ratio** — ≥60% of TCs in a spec must assert a state change (URL transition, data mutation, observable side effect, element value change after action). Render-existence assertions count toward the remaining ≤40%. A test that only checks an element is present without interacting with it is visibility, not functional coverage.

These targets are not soft suggestions. Gate 1 rejects specs that violate them with feedback pointing back at the gap.

## Quality Gates

Four gates are mandatory. The first two are review-only — they produce findings but do not modify files. Gate 4 runs after tests pass and audits coverage against exploration. These gates exist because prior experience showed that skipping review leads to cascading rework: bad specs produce bad tests, bad tests produce confusing failures, and "suite passed" can still mean the feature is uncovered.

### Gate 1: Review specs

After `generate-test-cases`, before `write-robot-code`:
- Load `review-test-cases` and run against `test-cases/<feature>.md`
- If **NEEDS REVISION** — revise the spec, then rerun `review-test-cases` before writing code

### Gate 2: Review code

After `write-robot-code`, before running tests:
- Load `review-test-code` and run against the `.robot` files
- If **NEEDS REVISION** — revise the code, then rerun `review-test-code` before running tests

### Gate 3: Test execution

Run `robot -d results tests/<feature>.robot 2>&1` directly in the main agent. Inspect both the CLI output and the generated `results/log.html` / `results/report.html`. If tests fail, load `fix-flaky-tests`.

**Retry limit:** maximum 3 fix-and-rerun cycles per suite per session. Beyond that, the failure usually signals a deeper issue (wrong locator strategy, misunderstood flow, missing test infrastructure) that another retry won't fix.

### Gate 4: Coverage gap audit

After Gate 3 passes (and the three consecutive green runs required for signoff), dispatch a fresh subagent to run a coverage audit. It receives the exploration report's element inventory and the executed `.robot` suite as inputs, and classifies each observed element as one of:

- `covered-functional` — at least one test triggers the action and asserts a state change
- `covered-visibility-only` — a test references the element but does not exercise it functionally
- `uncovered` — no test touches it

The audit writes `e2e-plan/coverage-audit.md` and returns a verdict:

- **GREEN** — every inventory element is `covered-functional`, or gaps are explicitly classified and justified
- **YELLOW** — gaps exist but each is explicitly accepted by the operator with reasoning
- **RED** — uncovered or visibility-only elements without justification; work is not done

"Suite passed three times" does not mean done. Gate 4 decides done.

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
runs `robot` directly so it can verify the output is real and interpret failures in context. A
subagent's summary of test results isn't trustworthy enough to gate completion.

Gate 4 (coverage audit) follows rule 2: dispatch a fresh subagent, feed it the exploration report and `.robot` suite, let it produce `coverage-audit.md`.

Pass file paths, conventions, and concrete output expectations into every Task call. Instruct each subagent to load the appropriate skill before acting.

## Guardrails

Quick-reference checklist — in addition to the session protocol's guardrails:

- Browse the product before writing specs or tests
- **Decompose broad features before deep exploration** — use `map-feature-scope`
- **Delegate scoped exploration to subagents** — the main agent does not call browser tools directly
- Record observed behavior before turning exploration into specs or code
- **Each review gate runs in a fresh subagent**, not the artifact's author
- Spec meets depth targets: ≥15 TCs for non-trivial features, ≥60% functional assertions
- Run tests before marking test work as done
- **Run the Gate 4 coverage audit after the suite is green** — tests passing is necessary but not sufficient
