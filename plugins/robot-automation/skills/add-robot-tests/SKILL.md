---
name: add-robot-tests
description: >
  THE DEFAULT ENTRY POINT for the Robot Framework execution layer in the split testing suite. Use this skill whenever Codex needs to add, create, or set up Robot Framework end-to-end tests for a feature, page, or application. It orchestrates the Robot-specific workflow after shared exploration and planning: analyze the `.robot` codebase, consume `e2e-plan/exploration-report.md`, `e2e-plan/coverage-plan.md`, and `test-cases/*.md`, write production-grade `.robot` suites, review them, and verify them with real execution. Delegates to `analyze-test-codebase`, `write-robot-code`, `review-test-code`, and `fix-flaky-tests`, while relying on shared `explore-app`, `plan-test-coverage`, `generate-test-cases`, and `review-test-cases`.
allowed-tools: Read Write Edit Glob Grep Bash Task
---

# Add Robot Framework Tests

Go from feature request to verified Robot Framework tests while honoring the new suite layering:

- `explore-app` owns live product exploration and evidence capture
- `test-analysis` owns coverage planning, spec generation, and spec review
- `robot-automation` owns Robot-specific analysis, authoring, code review, and flake repair

## Input

Parse the target URL and feature description from: $ARGUMENTS

Derive a **feature slug** from the feature description (for example, "Login flow" -> `login`).
Use this slug for file naming throughout (`tests/<slug>.robot`, `resources/<slug>.resource`).

## 1. Orient

Before planning or coding, understand the Robot codebase, the shared artifacts, and the execution
constraints.

### Understand the Robot codebase

- Does a Robot Framework setup exist? Look for `robot.toml`, `pyproject.toml` with Robot
  dependencies, `tests/*.robot`, `resources/*.resource`, `__init__.robot`, and browser-library
  setup.
- Are there existing suites, shared resources, auth helpers, or tag conventions to reuse?
- Load `analyze-test-codebase` and follow its workflow.
- If no Robot project exists at all, only suggest the optional external scaffold repository when
  the user wants a greenfield bootstrap.

### Understand the product through shared evidence

- Read `e2e-plan/exploration-report.md` if it exists.
- If required product evidence is missing or stale, run `explore-app` before continuing.
- Read `e2e-plan/coverage-plan.md` and `test-cases/*.md` files for the feature if they exist.

The execution layer should not improvise product behavior that the shared exploration and planning
layers were supposed to establish. If real product understanding is missing, stop and refresh the
shared artifacts first.

### Know your skill boundaries

| Activity | Skill |
|----------|-------|
| Shared exploration and blocker capture | `explore-app` |
| Robot codebase analysis | `analyze-test-codebase` |
| Shared coverage planning | `plan-test-coverage` |
| Shared TC-ID spec generation | `generate-test-cases` |
| Shared spec review gate | `review-test-cases` |
| Write or refactor `.robot` code | `write-robot-code` |
| Review `.robot` code | `review-test-code` |
| Fix flaky or failing Robot tests | `fix-flaky-tests` |

## 2. Prepare The Artifact Chain

Before you write Robot Framework code, make sure the shared handoff artifacts exist and are
current:

- `e2e-plan/exploration-report.md`
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md`

If any required artifact is missing:
1. Run `explore-app` when product evidence is missing
2. Run `plan-test-coverage` to produce the coverage plan
3. Run `generate-test-cases` to produce TC-ID specs
4. Run `review-test-cases` and stop if the verdict is `NEEDS REVISION`

Do not jump straight to `write-robot-code` from a user request when the shared artifacts are still
missing.

## 3. Plan

Refine the work into granular checkpoints based on what orientation revealed. Include:

- conventions analysis
- artifact refreshes
- `.robot` implementation steps
- review gates
- real execution and reruns

Update task status as each checkpoint completes.

## 4. Execute

Once the shared artifacts are ready:

- Load `write-robot-code` and implement the `.robot` tests
- Preserve traceability from every test back to one or more TC-IDs
- Reuse the project's existing resources, auth setup, libraries, listeners, and helper keywords
- Keep selectors aligned with the evidence gathered during exploration

Delegate heavy implementation work to subagents when that saves context, but pass the relevant
artifacts:

- `e2e-plan/exploration-report.md`
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md`
- `e2e-plan/conventions.yaml` when available

## Quality Gates

### Gate 1: Spec review

If spec review has not happened yet, run `review-test-cases` before implementation proceeds.

### Gate 2: Code review

After `write-robot-code`, run `review-test-code`.

- If the verdict is `NEEDS REVISION`, fix blockers before execution.
- If the verdict is `PASS WITH WARNINGS`, fix stability-critical warnings before execution.

### Gate 3: Real execution

Run the suite directly in the main agent:

```bash
robot -d results tests/<feature>.robot 2>&1
```

- Treat green Robot output plus `results/log.html` and `results/report.html` as the proof artifact.
- If tests fail, load `fix-flaky-tests` and follow its structured workflow.
- After the first green run, rerun the same suite two more times before signoff.
- Do not delegate Robot execution or coverage checks to subagents.

## Greenfield Bootstrap

If Robot Framework + Browser library is not set up in the target project, you have two paths:

- If the user wants an all-at-once bootstrap, clone the optional external scaffold repository and
  use it to create the starting Robot project.
- If the user already has a Robot codebase, or wants changes made directly in an existing
  repository, do not scaffold. Use the shipped skills to analyze the current setup and write the
  best possible `.robot` automation in place.

## Authentication

If the target feature requires login, follow [references/authentication.md](references/authentication.md).
Never hardcode credentials.

## Principles

- Respect the suite layering: exploration and planning are shared, execution is framework-specific.
- Consume shared artifacts instead of recreating them ad hoc.
- Keep Robot work traceable to TC-IDs and grounded in observed product behavior.
- Use existing project infrastructure before inventing new helpers.
- Avoid arbitrary waits; prefer Browser library waiting primitives.

## Example Usage

```text
Claude Code: /add-robot-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
Codex: $add-robot-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
```
