---
name: add-robot-tests
description: >
  THE DEFAULT ENTRY POINT for the Robot Framework execution layer in the split testing suite. Use
  to add, create, or set up Robot Framework end-to-end tests for a feature, page, or application.
  It orchestrates the Robot-specific workflow after shared exploration and planning: analyze the
  `.robot` codebase, consume `e2e-plan/exploration-report.md`, `e2e-plan/coverage-plan.md`, and
  `test-cases/*.md`, write production-grade `.robot` suites, review them, and verify them with
  real execution. Delegates to `analyze-test-codebase`, `write-robot-code`, `review-test-code`,
  and `fix-flaky-tests`, while relying on shared `explore-app`, `plan-test-coverage`,
  `generate-test-cases`, and `review-test-cases`.
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
- If no Robot project exists at all, only suggest the optional external scaffold repository when a
  greenfield bootstrap is requested.

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

If any required artifact is missing, dispatch each shared skill via a Task-tool subagent — the orchestrator coordinates, subagents produce:

1. **Run `explore-app` in a subagent** when product evidence is missing. Invoke the subagent with browser MCP access — its companion browsing-interface skill auto-loads when those tools come into scope. The subagent returns a structured report with a ≥20-row element inventory for non-trivial features. The main agent does not browse.
2. Run `plan-test-coverage` to produce the coverage plan (delegate if heavy).
3. Run `generate-test-cases` to produce TC-ID specs (delegate if heavy).
4. **Run `review-test-cases` in a fresh subagent** — not the agent that authored the spec. Stop if the verdict is `NEEDS REVISION`.

Do not jump straight to `write-robot-code` from a direct request when the shared artifacts are still missing. Do not browse or review-your-own-spec inline in the main agent — those are the shortcuts that have produced shallow, visibility-dominated specs.

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

Delegate implementation to subagents when the suite is large — the main orchestrator coordinates review gates and the coverage audit; the writing subagent focuses on translating specs to `.robot` code. Pass the relevant artifacts into each writing call:

- `e2e-plan/exploration-report.md`
- `e2e-plan/coverage-plan.md`
- `test-cases/<feature>.md`
- `e2e-plan/conventions.yaml` when available

## Quality Gates

### Gate 1: Spec review

If spec review has not happened yet, dispatch `review-test-cases` **in a fresh subagent** (not the agent that authored the spec). Pass only the spec path and the exploration report path; do not pass the authoring transcript.

### Gate 2: Code review

After `write-robot-code`, dispatch `review-test-code` **in a fresh subagent** (not the agent that authored the code).

- If the verdict is `NEEDS REVISION`, fix blockers before execution.
- If the verdict is `PASS WITH WARNINGS`, fix stability-critical warnings before execution.

### Gate 3: Real execution

Run the suite directly in the main agent:

```bash
robot -d results tests/<feature>.robot 2>&1
```

- If tests fail, load `fix-flaky-tests` and follow its structured workflow.
- After the first green run, rerun the same suite two more times before signoff (three consecutive green runs required).
- Do not delegate Robot execution to subagents — the main agent needs the raw output plus `results/log.html` and `results/report.html` to interpret failures in context.

### Gate 4: Coverage gap audit

Three green runs is necessary but not sufficient. Dispatch a fresh subagent with the following inputs:

- `e2e-plan/exploration-report.md` (specifically the Element Inventory and Elements Not Yet Reached sections)
- the executed `.robot` suite file(s)

The subagent's job is to classify each inventory element as one of:

- `covered-functional` — a test triggers the action and asserts a state change
- `covered-visibility-only` — a test references the element but does not exercise it functionally
- `uncovered` — no test touches the element

Output: `e2e-plan/coverage-audit.md` with the classification table and one of three verdicts:

- **GREEN** — every inventory element is `covered-functional`, or gaps are explicitly deferred with justification
- **YELLOW** — gaps exist but each is explicitly accepted with reasoning the operator has seen
- **RED** — uncovered or visibility-only elements without justification; work is not done

The Robot workflow is complete only when Gate 4 returns GREEN or YELLOW-with-acknowledgment. "Suite passed three times" is not the completion signal — the coverage audit is.

## Greenfield Bootstrap

If Robot Framework + Browser library is not set up in the target project, you have two paths:

- If an all-at-once bootstrap is requested, clone the optional external scaffold repository and use
  it to create the starting Robot project.
- If a Robot codebase already exists, or changes should be made directly in an existing
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
/add-robot-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
```
