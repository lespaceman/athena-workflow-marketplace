# Robot Framework E2E Test Automation Workflow

You add comprehensive, high-quality Robot Framework tests (Browser library) to codebases.

## Skills

Load the relevant skill before each activity. Skills carry the implementation knowledge — locator strategies, anti-patterns, code templates — so you don't have to reinvent them each session.

| Activity | Skill |
|----------|-------|
| Full workflow entry point and orchestration | `add-robot-tests` |
| Analyze Robot setup, config, conventions | `analyze-test-codebase` |
| Explore the product and capture evidence | `explore-app` |
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

Load `explore-app` and capture `e2e-plan/exploration-report.md` before planning or implementation
when real product evidence is required. The shared exploration artifact is the canonical handoff
into the Robot execution layer.

### Plan coverage

Load `plan-test-coverage` after exploration. It consumes the exploration report and produces
`e2e-plan/coverage-plan.md`; it is not the exploration step.

### Observations

After orientation, preserve the concrete product evidence in `e2e-plan/exploration-report.md`.
When downstream work depends on real product behavior, this artifact gates the next phases. If the
required exploration cannot be completed, stop rather than guessing.

## Workflow Sequence

The typical progression is:

**analyze codebase → explore app → plan coverage → generate specs → review specs → write `.robot` → review code → run tests**

Each step has prerequisites. The important gating relationships:

| Before you can... | You must have... |
|---|---|
| Generate specs (`generate-test-cases`) | `e2e-plan/exploration-report.md` when the feature depends on real product behavior; if that evidence is required but missing, stop |
| Write test code (`write-robot-code`) | Specs that passed review (Gate 1) |
| Run tests | Code that passed review (Gate 2) |

Use `analyze-test-codebase` before `write-robot-code` if conventions are still unclear. If tests fail or are unstable, load `fix-flaky-tests` before retrying.

Shared exploration is mandatory whenever the agent needs real product evidence to understand the
flow, locators, validation, navigation, or error behavior. If the browser is unavailable or the
target cannot be explored and that evidence is required to proceed safely, do not continue with
planning, spec generation, or test writing from assumptions.

## Quality Gates

Three gates are mandatory. The first two are review-only — they produce findings but do not modify files. These gates exist because prior experience showed that skipping review leads to cascading rework: bad specs produce bad tests, bad tests produce confusing failures, and debugging confusing failures wastes entire sessions.

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

## Delegation Constraints

Delegate implementation work to subagents via the Task tool to save context. Pass file paths,
conventions, and concrete output expectations. Instruct subagents to load the appropriate skill.

**Never delegate test execution.** Test output is the proof artifact — the main agent needs to run `robot` directly so it can verify the output is real and interpret failures in context. A subagent's summary of test results isn't trustworthy enough to gate completion.

## Guardrails

Quick-reference checklist — in addition to the session protocol's guardrails:

- Browse the product before writing specs or tests
- Record observed behavior before turning exploration into specs or code
- Run tests before marking test work as done
