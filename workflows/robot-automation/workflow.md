# Robot Framework E2E Test Automation Workflow

You add comprehensive, high-quality Robot Framework tests (Browser library) to codebases.

## Plugins

This workflow is authored against the plugins pinned in `workflow.json`. The markdown lists the
plugin surfaces, while `workflow.json` remains the source of truth for versions.

| Plugin | Skills Used Here |
|--------|------------------|
| `agent-web-interface` | `agent-web-interface-guide` |
| `app-exploration` | `map-feature-scope`, `capture-feature-evidence` |
| `test-analysis` | `plan-test-coverage`, `generate-test-cases`, `review-test-cases` |
| `robot-automation` | `add-robot-tests`, `analyze-test-codebase`, `write-robot-code`, `review-test-code`, `review-robot-best-practices`, `fix-flaky-tests` |

## Skills

Load the relevant skill before each activity, and err on the side of loading a skill whenever the
task even partially overlaps its scope. Skills carry the implementation knowledge — browser
interaction discipline, selector strategies, wait idioms, anti-patterns, code templates, review
gates, and repair workflow — so do not rely on memory or ad hoc reasoning when a listed skill
applies.

| Activity | Skill |
|----------|-------|
| Full workflow entry point and orchestration | `add-robot-tests` |
| Browser MCP interaction and live app observation | `agent-web-interface-guide` |
| Analyze Robot setup, config, conventions | `analyze-test-codebase` |
| Quickly map a broad feature into bounded exploration units | `map-feature-scope` |
| Explore the product and capture evidence | `capture-feature-evidence` |
| Decide what to test, coverage gaps, priorities | `plan-test-coverage` |
| Create TC-ID specs from shared evidence | `generate-test-cases` |
| Review TC-ID specs before implementation | `review-test-cases` |
| Write, edit, or refactor `.robot` test code | `write-robot-code` |
| Review `.robot` code before execution signoff | `review-test-code` |
| Review Robot Framework best-practice compliance | `review-robot-best-practices` |
| Debug test failures, check stability | `fix-flaky-tests` |

## Task Tracker Discipline

This workflow spans long sessions, harness boundaries (Athena, sub-Claude, Codex), and `--continue`
resumes. Progress must be recoverable from the runtime tracker when one is provided, or from explicit
execution notes when no tracker tool exists. A stale tracker or missing notes can hide incomplete
gates and cause repeated work.

**On every session start (fresh, `--continue`, harness sub-session, or delegated subagent that owns its own tracker):**

1. Read the existing tracker or execution notes before continuing work.
2. Reconcile observed state with recorded state: completed work, in-flight work, blocked work, and the next gate.
3. If the harness exposes a task tool, update it. If not, write the same status into execution notes.
4. Surface mismatches before picking the next task.

**On receipt of a large task:**

1. Decompose into granular sub-tasks **immediately**, before starting real work. Granular means a sub-task is a single coherent step that finishes in a small number of tool calls (analyze one file, write one suite, run one gate). If a sub-task plausibly spans more than that, split it again.
2. Record the full breakdown in the tracker or execution notes in one batch so the plan is visible up front.
3. Then work each sub-task independently — start it, mark `in_progress`, finish it, mark `completed` immediately. Do not batch status updates to end-of-session.

**Update cadence:**

- Flip a task to `in_progress` the moment you start it, not partway in.
- Flip it to `completed` the moment it's done, not at the next checkpoint.
- The instant new work surfaces — a new sub-task, a Gate reset, a re-exploration trigger, a deferral, a Gate 3 failure-triage outcome — add it to the tracker or execution notes before acting on it.
- Granular decomposition exists specifically so updates stay frequent. If the tracker is going long stretches between updates, the breakdown is too coarse; split current items further.

Every Gate reset, brownfield rerun, and cross-session handoff depends on being able to recover
"what's done, what's in flight, what's next" from the recorded state.

## Orientation Steps

Session 1 begins by loading `add-robot-tests` as the top-level workflow skill. The other skills are focused sub-steps within that workflow, not competing entry points.

### Understand the codebase

Load `analyze-test-codebase` and follow its methodology. Key questions: is Robot Framework + Browser library installed? Has `rfbrowser init` run? What conventions are in use? What resource files, listeners, and custom libraries are already available? If a Robot project already exists, stay in that project and adapt to its history. Only reach for the optional external scaffold repository when no Robot project exists and the user wants a full bootstrap in one step.

### Understand the product

Choose the lightest safe exploration path for the requested problem. Browser-backed evidence is
required both for new coverage and for fixing existing suites when the failure may involve product
state, DOM shape, labels, roles, selectors, navigation, timing, or data.

- If the request is narrow and obviously single-surface, go straight to `capture-feature-evidence`.
- If the request may span multiple routes, tabs, overlays, roles, or primary interactive surfaces,
  load `map-feature-scope` first. It writes `e2e-plan/feature-map.md`, which tells the
  orchestrator whether one exploration run is enough or whether multiple scoped `capture-feature-evidence` runs
  should follow.
- If the request is to fix, stabilize, update, or repair existing suites, first identify the failing
  user flow from the `.robot` test and recent output, then dispatch a browser subagent to reproduce
  that flow against the current app before changing selectors or waits.

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

For existing-suite repair, stale or missing exploration is not a reason to skip the browser. Refresh
the relevant evidence first, even when the apparent fix is "just update the selector."

## Workflow Sequence

The common progression is:

**analyze codebase → map feature scope → deep-explore the scoped areas → synthesize rollup exploration report → plan coverage → generate specs → review specs → write code → review code → run tests**

Treat that as a dependency graph, not a rigid script. The right path depends on the problem:

- Narrow single-surface feature: `analyze codebase → capture-feature-evidence → plan → specs → review → write → review → run`
- Broad multi-surface feature: `analyze codebase → map-feature-scope → parallel/serial scoped capture-feature-evidence runs → rollup → plan → specs → review → write → review → run`
- Existing mature codebase with current artifacts: reuse valid `feature-map.md`, exploration, or
  spec artifacts instead of regenerating them
- Direct debugging request: run or inspect the failing test output, dispatch browser-backed current
  app triage for the failing flow, then load `fix-flaky-tests` with that evidence. Do not treat code
  inspection alone as proof that a selector, wait, or assertion should change.

Each step has prerequisites. The important gating relationships:

| Before you can... | You must have... |
|---|---|
| Generate specs (`generate-test-cases`) | `e2e-plan/exploration-report.md`, plus mapped `e2e-plan/exploration/*.md` files when the feature was decomposed |
| Write test code (`write-robot-code`) | Specs that passed review (Gate 1) |
| Run tests | Code that passed review (Gate 2) |

Use `analyze-test-codebase` before `write-robot-code` if conventions are still unclear. If tests fail or are unstable, load `fix-flaky-tests` before retrying.

Shared exploration is mandatory whenever the agent needs real product evidence to understand the
flow, selectors, validation, navigation, or error behavior. Broad features must be decomposed first
so the main agent can dispatch bounded scoped explorations instead of one oversized browser session.
Simple features can skip decomposition. If the browser is unavailable or the target cannot be
explored and that evidence is required to proceed safely, do not continue with planning, spec
generation, or test writing from assumptions.

Existing suites do not waive this requirement. Any change to a selector, text assertion, visibility
assertion, navigation assertion, Browser-library wait, or keyword that encodes page behavior must be
grounded in current browser evidence or in a freshly recorded failure-triage verdict.

## Depth Targets

Concrete floors downstream gates enforce. These exist because prior runs delivered shallow specs that were dominated by visibility checks — the suite passed and the feature was still uncovered.

A feature is **non-trivial** when exploration touched more than two routes, or the UI has more than
one primary interactive surface (e.g., a listing + detail view + modal all count as one feature).
Such features should normally pass through `map-feature-scope` before deep exploration.

- **Exploration inventory** — non-trivial features require ≥20 distinct interactive elements recorded with selector candidates (the form Browser library keywords take, e.g. `text=Submit`, `id=login`, `xpath=//button[@data-testid='submit']`); ≥3 meaningful error, validation, or empty states deliberately triggered; and a labeled "elements not yet reached" list so downstream skills know the scope limits.
- **TC-ID count** — non-trivial features require ≥15 TCs. If the author cannot reach 15, the spec has out-run the exploration; return to `capture-feature-evidence` rather than padding.
- **Functional-to-visibility ratio** — ≥60% of TCs in a spec must assert a state change (URL transition, data mutation, observable side effect, element value change after action). Render-existence assertions count toward the remaining ≤40%. A test that only checks an element is present without interacting with it is visibility, not functional coverage.

These targets are not soft suggestions. Gate 1 rejects specs that violate them with feedback pointing back at the gap.

## Deferred Governance

"Deferred" is a scope boundary, not an escape valve. Every deferred TC must carry three fields in the spec:

- **blocker** — the concrete thing preventing automation (e.g., "requires seeded data", "Browser library cannot reach element inside a native dialog", "production-only API")
- **un-defer plan** — what changes would make the case testable (e.g., "add fixture once backend ticket APM-412 lands")
- **scope** — `this-sprint` or `out-of-scope`

Cap: at most **20% of TCs** in a spec may be deferred. Over that, the spec fails Gate 1 with "scope too narrow — revisit exploration"; the fix is more evidence, not more deferrals.

## Quality Gates

Four gates are mandatory. The first two are review-only — they produce findings but do not modify files. Gate 4 runs after tests pass and audits coverage against exploration. These gates exist because prior experience showed that skipping review leads to cascading rework: bad specs produce bad tests, bad tests produce confusing failures, and "suite passed" can still mean the feature is uncovered.

### Gate 1: Review specs

After `generate-test-cases`, before `write-robot-code`:
- Load `review-test-cases` and run against `test-cases/<feature>.md`
- If **NEEDS REVISION** — revise the spec, then rerun `review-test-cases` before writing code

### Gate 2: Review code

After `write-robot-code`, before running tests:
- Load `review-test-code` and run against the `.robot` files
- Load `review-robot-best-practices` generously for Robot dialect, keyword structure, selector
  strategy, wait idiom, resource organization, or maintainability concerns; run it alongside Gate 2
  whenever the change is more than a narrow one-line repair.
- If **NEEDS REVISION** — revise the code, then rerun `review-test-code` before running tests
- Gate 2 applies to every implementation or repair edit, including selector changes, assertion
  rewrites, resource/keyword updates, fixture/auth changes, and Browser-library wait changes made
  after browser triage. Do not run or rerun tests after code changes until `review-test-code` has
  passed for the changed files.

### Gate 3: Test execution

Run `robot -d results tests/<feature>.robot 2>&1` directly in the main agent. Inspect both the CLI output and the generated `results/log.html`, `results/report.html`, and `results/output.xml` (the last is the machine-readable feed for `--rerunfailed`). To run only the new or changed cases in isolation (the brownfield order below), use Robot's filters: `--include <tag>` (short form `-i`) for tag-based selection, or `-t "<test name>"` / `--test "<test name>"` for a specific test. Record the exact filter in the run ledger. During stabilization, `--rerunfailed results/output.xml` re-runs only the previously failed tests against the same selection, and `--exitonfailure` short-circuits a run on the first failure when you want a fast signal. If tests fail, load `fix-flaky-tests`.

**Wait idiom (Browser library):** Browser library does **not** auto-wait on every action the way Playwright JS does. Use explicit waits — `Wait For Load State`, `Wait For Elements State`, `Wait For Condition`, `Wait For Response`, `Wait For Request` — keyed to the actual signal you're waiting on. Avoid `Sleep`; if a test relies on a fixed sleep to pass, that's flake waiting to surface and a re-exploration trigger.

**Signoff requires three consecutive green runs** of the new or changed test set on the same code, with no intervening file changes. Any change to `.robot` code, resource files, fixtures, or the test set itself resets the counter (see the Gate reset rule below).

**Retry policy:** no fixed numeric cap. The agent should continue fix-and-rerun cycles only while each cycle produces meaningful progress: a new root-cause hypothesis, a concrete code/config change, or materially new failure evidence. Stop when the issue is no longer moving, the next rerun would repeat the same experiment, or the blocker is external to the suite (missing environment, access, product bug, unclear requirements).

**Execution order for brownfield suites:**
- Run the newly added or changed tests in isolation until they are stable.
- Then run the relevant feature file or suite.
- Only run broader regression after the new coverage is green in isolation.
- If unrelated pre-existing tests fail, classify them separately as baseline instability. If they must be fixed because of shared-state leakage or broken shared infrastructure, report that work separately from the new TC implementation set.

**Gate reset rule:** if the planned TC set, spec, coverage plan, or executed suite changes after Gate 2 in a way that adds, removes, defers, or materially rewrites covered behavior, reset to the earliest affected gate:
- rerun Gate 2 for changed `.robot` or resource code
- rerun Gate 1 if the spec or deferral set changed
- restart the Gate 3 consecutive-green counter

Any code change made during Gate 3 failure repair also returns to Gate 2 before the next counted
execution. Browser triage explains what to change; it does not replace code review.

Do not count pre-change runs toward post-change signoff.

**Execution-time deferral policy:** deferral discovered during Gate 3 is exceptional. Only defer when the blocker is concrete and external to the current suite implementation, the spec and coverage plan are updated with blocker, un-defer plan, and scope, and the run returns to the required earlier gate(s) before signoff. Do not defer to avoid re-exploration, selector verification, or code review. If the blocker is selector uncertainty, DOM drift from exploration, viewport/layout mismatch, or "needs browser confirmation", stop execution and refresh exploration evidence first.

Mandatory re-exploration triggers include:
- execution viewport or layout drift for coordinate- or layout-sensitive interactions
- lost selector uniqueness compared with exploration
- labels or control text absent, duplicated, or rendered outside the explored container
- reliance on `Sleep` to make a test pass (event-driven waits are unavailable or unknown)
- workaround-heavy fixes such as `Click  selector  force=True`, `Evaluate JavaScript`-dispatched clicks, coordinate clicks, or page-wide text/count oracles becoming the only apparent path forward
- any proposed selector-only fix for an existing failing suite when no current browser evidence has
  been captured for the failing flow

**Failure triage via browser (mandatory before fixing).** When a test fails, do not patch selectors, add `Sleep`s, or label the failure as flake until the cause is classified against the live product. Dispatch a fresh subagent with `mcp__plugin_agent-web-interface_browser__*` access and the relevant `e2e-plan/exploration-report.md` (or `e2e-plan/exploration/<subfeature>.md`) section. The subagent must:

1. Navigate to the failing flow and reproduce the user action by hand.
2. Compare the current DOM against the recorded evidence — labels, roles, structure, selector candidates.
3. Return one verdict:
   - **product regression** — the feature itself is broken. Do not adjust the test to make it pass; escalate and capture the bug.
   - **selector / DOM drift** — the product still works but the controls moved or relabeled. Refresh the exploration artifact first, then update the test against the new evidence.
   - **test defect** — the product behaves correctly; the bug is in `.robot` code, keywords, resource files, or wait idioms.
   - **environment / data** — the flow is blocked by missing seed data, auth, or environment state; treat as a Gate 3 deferral candidate per the policy above.

Record the verdict and the subagent's evidence pointer in the run ledger before any code change. Patching selectors without triage is the failure mode this rule exists to prevent.

**Gate 3 run ledger:** maintain a ledger in the session tracker or execution notes. For each counted run record:
- exact command
- exact test set or include filter
- whether the run is eligible for signoff
- files changed since the prior run
- pass/fail counts
- whether the consecutive-green counter reset

### Gate 4: Coverage gap audit

After Gate 3 passes (and the three consecutive green runs required for signoff), dispatch a fresh subagent to run a coverage audit. It receives the exploration report's element inventory and the executed `.robot` suite as inputs, and classifies each observed element as one of:

- `covered-functional` — at least one test triggers the action and asserts a state change
- `covered-visibility-only` — a test references the element but does not exercise it functionally
- `uncovered` — no test touches it

The audit writes `e2e-plan/coverage-audit.md` and returns a verdict:

- **GREEN** — every promoted P0/P1 inventory-backed behavior is covered functionally, or any uncovered item is explicitly out of current scope and was never promoted into the accepted spec or coverage plan
- **YELLOW** — one or more promoted items remain deferred, partially covered, or visibility-only, but the operator has explicitly accepted those gaps with written reasoning
- **RED** — uncovered, visibility-only, or deferred promoted items remain without explicit acceptance, or the exploration/spec/execution chain is inconsistent

A promoted TC deferred during or after execution cannot end in **GREEN** unless the spec and coverage plan were revised, re-reviewed, and explicitly re-baselined before Gate 4.

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

Existing-suite fixes use the same browser discipline. A repair subagent may be narrower than a full
feature exploration, but it must still navigate the current app, reproduce the relevant user action,
and report current labels, roles, DOM structure, and selector candidates before implementation edits.

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
- **Browse the current product before fixing existing suites** — especially before changing
  selectors, text assertions, navigation assertions, Browser-library waits, or page-behavior keywords
- **Decompose broad features before deep exploration** — use `map-feature-scope`
- **Delegate scoped exploration to subagents** — the main agent does not call browser tools directly
- Record observed behavior before turning exploration into specs or code
- **Each review gate runs in a fresh subagent**, not the artifact's author
- **Run the code review gate after every suite repair** — no selector, wait, keyword, resource, or
  assertion edit goes straight to execution
- Spec meets depth targets: ≥15 TCs for non-trivial features, ≥60% functional assertions, ≤20% deferred
- **Stabilize new or changed tests in isolation before broader regression** in brownfield suites
- **Reset the affected gates if scope, spec, coverage plan, or executed suite changes after Gate 2**
- **Keep a Gate 3 run ledger** so signoff runs, resets, and file changes are auditable
- Run tests before marking test work as done
- **Run the Gate 4 coverage audit after the suite is green** — tests passing is necessary but not sufficient
