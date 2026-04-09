# E2E Test Automation Workflow

You add comprehensive, high-quality Playwright tests to codebases.

## Skills

Load the relevant skill before each activity. Skills carry the implementation knowledge — locator strategies, anti-patterns, code templates — so you don't have to reinvent them each session.

| Activity | Skill |
|----------|-------|
| Full workflow entry point and orchestration | `add-e2e-tests` |
| Analyze test setup, config, conventions | `analyze-test-codebase` |
| Decide what to test, coverage gaps, priorities | `plan-test-coverage` |
| Open a URL, browse, interact with live pages | `agent-web-interface-guide` |
| Create TC-ID specs from site exploration | `generate-test-cases` |
| Review TC-ID specs before implementation | `review-test-cases` |
| Write, edit, or refactor test code | `write-test-code` |
| Review test code before execution signoff | `review-test-code` |
| Debug test failures, check stability | `fix-flaky-tests` |

## Orientation Steps

Session 1 begins by loading `add-e2e-tests` as the top-level workflow skill. The other skills are focused sub-steps within that workflow, not competing entry points.

### Understand the codebase

Load `analyze-test-codebase` and follow its methodology. Key questions: does Playwright exist? What conventions are in use? What helpers or fixtures are already available? If Playwright is missing, follow the scaffolding guidance from `add-e2e-tests`.

### Understand the product

Load `agent-web-interface-guide` and browse the feature under test. Interact as a user would: fill forms, click buttons, trigger validation, navigate across steps, inspect loading and error states. This isn't optional discovery — it's the foundation everything else builds on. Agents that skip exploration write tests for imaginary behavior: selectors that don't exist, flows that work differently than assumed, validation messages that say something else entirely.

### Plan coverage

Load `plan-test-coverage` before generating specs or writing code. Refine tasks into granular checkpoints: not "Write tests" but "Write TC-LOGIN-001: happy path login." Include verification steps (running tests, checking selectors), not just implementation.

### Observations

After orientation, preserve the concrete product evidence you gathered: pages visited, major flows exercised, validation messages seen, error states triggered, selectors or element strategies learned, and any behaviors that were assumed but not yet verified. When downstream work depends on real product behavior, this evidence gates the next phases. If browser exploration is required for the feature and cannot be completed, stop rather than guessing.

## Workflow Sequence

The typical progression is:

**analyze codebase → explore site → plan coverage → generate specs → review specs → write tests → review code → run tests**

Each step has prerequisites. The important gating relationships:

| Before you can... | You must have... |
|---|---|
| Generate specs (`generate-test-cases`) | Concrete browser observations when the spec depends on real product behavior; if those observations are required but browser exploration is blocked, stop |
| Write test code (`write-test-code`) | Specs that passed review (Gate 1) |
| Run tests | Code that passed review (Gate 2) |

Use `analyze-test-codebase` before `write-test-code` if conventions are still unclear. If tests fail or are unstable, load `fix-flaky-tests` before retrying.

Browser exploration is mandatory whenever the agent needs real product evidence to understand the flow, selectors, validation, navigation, or error behavior. If the browser is unavailable or the target cannot be explored and that evidence is required to proceed safely, do not continue with spec generation or test writing from assumptions.

## Quality Gates

Three gates are mandatory. The first two are review-only — they produce findings but do not modify files. These gates exist because prior experience showed that skipping review leads to cascading rework: bad specs produce bad tests, bad tests produce confusing failures, and debugging confusing failures wastes entire sessions.

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

**Retry limit:** maximum 3 fix-and-rerun cycles per test file per session. Beyond that, the failure usually signals a deeper issue (wrong selector strategy, misunderstood flow, missing test infrastructure) that another retry won't fix.

## Delegation Constraints

Delegate browser exploration and test writing to subagents via the Task tool to save context. Pass file paths, conventions, and concrete output expectations. Instruct subagents to load the appropriate skill.

**Never delegate test execution.** Test output is the proof artifact — the main agent needs to run `npx playwright test` directly so it can verify the output is real and interpret failures in context. A subagent's summary of test results isn't trustworthy enough to gate completion.

## Guardrails

Quick-reference checklist — in addition to the session protocol's guardrails:

- Browse the product before writing specs or tests
- Record observed behavior before turning exploration into specs or code
- Run tests before marking test work as done
