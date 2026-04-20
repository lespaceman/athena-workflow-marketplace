---
name: add-playwright-tests
description: >
  THE DEFAULT ENTRY POINT for the Playwright execution layer in the split testing suite. Use to
  add, create, or set up Playwright end-to-end tests for a feature, page, or application. It
  orchestrates the full Playwright workflow after shared exploration and planning: analyze the
  Playwright codebase, consume `e2e-plan/feature-map.md`, `e2e-plan/exploration-report.md`,
  `e2e-plan/coverage-plan.md`, and `test-cases/*.md`, write production-grade test code, review it,
  and verify it with real execution. Delegates to `analyze-test-codebase`, `write-test-code`,
  `review-test-code`, and `fix-flaky-tests`, while relying on shared `map-feature-scope`,
  `explore-app`, `plan-test-coverage`,
  `generate-test-cases`, and `review-test-cases`.
allowed-tools: Read Write Edit Bash Glob Grep Task
---

# Add Playwright Tests

Go from feature request to verified Playwright tests while honoring the new suite layering:

- `explore-app` owns live product exploration and evidence capture
- `test-analysis` owns coverage planning, spec generation, and spec review
- `playwright-automation` owns Playwright-specific analysis, authoring, code review, and flake repair

## Input

Parse the target URL and feature description from: $ARGUMENTS

Derive a **feature slug** from the feature description (for example, "Login flow" -> `login`).
Use the slug for file naming throughout.

## 1. Orient

Before planning or coding, understand the codebase, the shared artifacts, and the execution
constraints.

### Understand the Playwright codebase

- Does a Playwright config exist (`playwright.config.{ts,js,mjs}`)? If not, you may need to
  scaffold one. See [references/scaffolding.md](references/scaffolding.md).
- Are there existing tests, fixtures, page objects, auth helpers, or naming conventions?
- Load `analyze-test-codebase` and follow its workflow.

### Understand the product through shared evidence

- Read `e2e-plan/exploration-report.md` if it exists.
- Read `e2e-plan/feature-map.md` and any `e2e-plan/exploration/*.md` files if they exist.
- If the required product evidence is missing or stale, run `map-feature-scope` first for broad
  features, then run `explore-app` for each required scoped area before continuing.
- Read `e2e-plan/coverage-plan.md` and `test-cases/*.md` files for the feature if they exist.

The execution layer should not improvise product behavior that the exploration layer was supposed to
establish. If real product understanding is missing, stop and create or refresh the shared
artifacts first.

### Know your skill boundaries

| Activity | Skill |
|----------|-------|
| Shared feature decomposition before deep exploration | `map-feature-scope` |
| Shared exploration and blocker capture | `explore-app` |
| Playwright codebase analysis | `analyze-test-codebase` |
| Shared coverage planning | `plan-test-coverage` |
| Shared TC-ID spec generation | `generate-test-cases` |
| Shared spec review gate | `review-test-cases` |
| Write or refactor Playwright code | `write-test-code` |
| Review Playwright code | `review-test-code` |
| Fix flaky or failing Playwright tests | `fix-flaky-tests` |

## 2. Prepare The Artifact Chain

Before you write Playwright code, make sure the shared handoff artifacts exist and are current:

- `e2e-plan/feature-map.md` for broad multi-surface features
- `e2e-plan/exploration-report.md`
- `e2e-plan/exploration/*.md` for mapped sub-features
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md`

If any required artifact is missing, dispatch each shared skill via a Task-tool subagent — the orchestrator coordinates, subagents produce:

1. **Run `map-feature-scope` in a subagent** when the request may span multiple routes, tabs, overlays, roles, or primary interactive surfaces. The subagent writes `e2e-plan/feature-map.md`.
2. If the feature map says `SINGLE-SURFACE`, run one `explore-app` subagent and let it write `e2e-plan/exploration-report.md`.
3. If the feature map says `MULTI-SURFACE`, dispatch one fresh `explore-app` subagent per sub-feature marked `parallel-safe = yes`, then run any `parallel-safe = no` rows serially once their prerequisites are satisfied. Each subagent writes `e2e-plan/exploration/<subfeature>.md`.
4. Synthesize or refresh `e2e-plan/exploration-report.md` as a rollup over the mapped exploration artifacts. The rollup is an index and merged summary only; it does not invent observations.
5. Run `plan-test-coverage` to produce the coverage plan (delegate if heavy).
6. Run `generate-test-cases` to produce TC-ID specs (delegate if heavy).
7. **Run `review-test-cases` in a fresh subagent** — not the agent that authored the spec. Stop if the verdict is `NEEDS REVISION`.

Do not jump straight to `write-test-code` from a direct request when the shared artifacts are still missing. Do not browse or review-your-own-spec inline in the main agent — those are the exact shortcuts that have produced shallow 12-TC specs dominated by visibility checks.

## 3. Implement The Playwright Layer

Once the shared artifacts are ready:

- Load `write-test-code` and implement the Playwright tests
- Preserve traceability from every test back to one or more TC-IDs
- Reuse the project's existing fixtures, auth setup, page objects, and helper utilities
- Keep selectors aligned with the evidence gathered during exploration

Delegate writing to subagents when the test suite is large — the main orchestrator coordinates review gates and the coverage audit; the code-writing subagent focuses on translating specs to Playwright tests. Pass the relevant artifacts into each writing call:

- `e2e-plan/feature-map.md`
- `e2e-plan/exploration-report.md`
- relevant `e2e-plan/exploration/<subfeature>.md` files
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md` or `test-cases/<feature>/<subfeature>.md`
- any conventions or analysis files emitted by `analyze-test-codebase`

## 4. Run The Mandatory Quality Gates

### Gate 1: Spec review

If spec review has not happened yet, dispatch `review-test-cases` **in a fresh subagent** (not the agent that authored the spec). Pass only the spec path and the exploration report path; do not pass the authoring transcript.

### Gate 2: Code review

After `write-test-code`, dispatch `review-test-code` **in a fresh subagent** (not the agent that authored the code).

- If the verdict is `NEEDS REVISION`, fix blockers before execution.
- If the verdict is `PASS WITH WARNINGS`, fix stability-critical warnings before execution.

### Gate 3: Real execution

Run the tests directly in the main agent:

```bash
npx playwright test <file> --reporter=list 2>&1
```

- If tests fail, load `fix-flaky-tests` and follow its structured workflow.
- Do not delegate Playwright execution to subagents — the main agent needs the raw output to interpret failures in context.

### Gate 4: Coverage gap audit

Green test output is necessary but not sufficient. Dispatch a fresh subagent with the following inputs:

- `e2e-plan/exploration-report.md` (specifically the Element Inventory and Elements Not Yet Reached sections)
- relevant `e2e-plan/exploration/<subfeature>.md` files for mapped features
- the executed test file(s)

The subagent's job is to classify each inventory element as one of:

- `covered-functional` — a test triggers the action and asserts a state change
- `covered-visibility-only` — a test references the element but does not exercise it functionally
- `uncovered` — no test touches the element

Output: `e2e-plan/coverage-audit.md` with the classification table and one of three verdicts:

- **GREEN** — every inventory element is `covered-functional`, or gaps are explicitly deferred with justification
- **YELLOW** — gaps exist but each is explicitly accepted with reasoning the operator has seen
- **RED** — uncovered or visibility-only elements without justification; work is not done

The Playwright workflow is complete only when Gate 4 returns GREEN or YELLOW-with-acknowledgment. "Tests passed" is not the completion signal — the coverage audit is.

## Authentication

If the target feature requires login, follow [references/authentication.md](references/authentication.md).
Never hardcode credentials.

## Principles

- Respect the suite layering: exploration and planning are shared, execution is framework-specific.
- Use `map-feature-scope` before deep exploration whenever the requested feature is broad enough to
  risk one oversized browser session.
- Consume shared artifacts instead of recreating them ad hoc.
- Keep Playwright work traceable to TC-IDs and grounded in observed product behavior.
- Use existing project infrastructure before inventing new helpers.
- Avoid arbitrary sleeps; prefer Playwright's built-in waiting model.

## Example Usage

```text
/add-playwright-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
```
