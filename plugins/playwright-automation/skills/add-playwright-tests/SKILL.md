---
name: add-playwright-tests
description: >
  THE DEFAULT ENTRY POINT for the Playwright execution layer in the split testing suite. Use this
  skill whenever Codex needs to add, create, or set up Playwright end-to-end tests for a feature,
  page, or application. It orchestrates the full Playwright workflow after shared exploration and
  planning: analyze the Playwright codebase, consume `e2e-plan/exploration-report.md`,
  `e2e-plan/coverage-plan.md`, and `test-cases/*.md`, write production-grade test code, review it,
  and verify it with real execution. Delegates to `analyze-test-codebase`, `write-test-code`,
  `review-test-code`, and `fix-flaky-tests`, while relying on shared `explore-app`,
  `plan-test-coverage`, `generate-test-cases`, and `review-test-cases`.
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
- If the required product evidence is missing or stale, run `explore-app` before continuing.
- Read `e2e-plan/coverage-plan.md` and `test-cases/*.md` files for the feature if they exist.

The execution layer should not improvise product behavior that the exploration layer was supposed to
establish. If real product understanding is missing, stop and create or refresh the shared
artifacts first.

### Know your skill boundaries

| Activity | Skill |
|----------|-------|
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

- `e2e-plan/exploration-report.md`
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md`

If any required artifact is missing:
1. Run `explore-app` when product evidence is missing
2. Run `plan-test-coverage` to produce the coverage plan
3. Run `generate-test-cases` to produce TC-ID specs
4. Run `review-test-cases` and stop if the verdict is `NEEDS REVISION`

Do not jump straight to `write-test-code` from a user request when the shared artifacts are still
missing.

## 3. Implement The Playwright Layer

Once the shared artifacts are ready:

- Load `write-test-code` and implement the Playwright tests
- Preserve traceability from every test back to one or more TC-IDs
- Reuse the project's existing fixtures, auth setup, page objects, and helper utilities
- Keep selectors aligned with the evidence gathered during exploration

Delegate heavy writing to subagents when that saves context, but pass the relevant artifacts:
- `e2e-plan/exploration-report.md`
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md`
- any conventions or analysis files emitted by `analyze-test-codebase`

## 4. Run The Mandatory Quality Gates

### Gate 1: Spec review

If spec review has not happened yet, run `review-test-cases` before implementation proceeds.

### Gate 2: Code review

After `write-test-code`, run `review-test-code`.

- If the verdict is `NEEDS REVISION`, fix blockers before execution.
- If the verdict is `PASS WITH WARNINGS`, fix stability-critical warnings before execution.

### Gate 3: Real execution

Run the tests directly in the main agent:

```bash
npx playwright test <file> --reporter=list 2>&1
```

- Treat green Playwright output as the proof artifact.
- If tests fail, load `fix-flaky-tests` and follow its structured workflow.
- Do not delegate Playwright execution or coverage checks to subagents.

## Authentication

If the target feature requires login, follow [references/authentication.md](references/authentication.md).
Never hardcode credentials.

## Principles

- Respect the suite layering: exploration and planning are shared, execution is framework-specific.
- Consume shared artifacts instead of recreating them ad hoc.
- Keep Playwright work traceable to TC-IDs and grounded in observed product behavior.
- Use existing project infrastructure before inventing new helpers.
- Avoid arbitrary sleeps; prefer Playwright's built-in waiting model.

## Example Usage

```text
Claude Code: /add-playwright-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
Codex: $add-playwright-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
```
