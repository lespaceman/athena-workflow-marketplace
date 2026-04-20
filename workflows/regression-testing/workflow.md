# Regression Testing Workflow

You define the broader rerunnable confidence scope for changed, fragile, or business-critical
areas.

## Skills

| Activity | Skill |
|----------|-------|
| Define rerunnable regression scope and depth | `define-regression-scope` |
| Gather grounded product evidence | `capture-feature-evidence` |
| Update shared prioritization when needed | `plan-test-coverage` |
| Expand shared specs when required | `generate-test-cases` |

## Workflow Sequence

The default progression is:

**explore app when needed → define regression scope → optionally refresh shared planning/specs → produce an explicit handoff recommendation if runnable automation is requested**

### Orientation

- Load `define-regression-scope` as the workflow entry skill.
- If the regression decision depends on real product behavior and
  `e2e-plan/exploration-report.md` is missing or stale, load `capture-feature-evidence` first.
- If the regression decision exposes coverage gaps or changed-area work that needs updated shared
  planning, load `plan-test-coverage` and `generate-test-cases` after the charter is drafted.

## Handoff Rules

- `define-regression-scope` owns `e2e-plan/regression-charter.md`, not the shared artifact chain.
- `capture-feature-evidence` owns `e2e-plan/exploration-report.md`.
- `plan-test-coverage` owns `e2e-plan/coverage-plan.md`.
- `generate-test-cases` owns `test-cases/<feature>.md`.

If runnable automation is requested after the regression charter is finalized, stop with an
explicit recommendation to move into the appropriate execution workflow:

- `playwright-automation` for Playwright
- `robot-automation` for Robot Framework

This workflow does not load execution-layer plugins itself, so it must not claim to implement or
run the framework automation in the same workflow session.

## Guardrails

- Regression scope should be broader than smoke but still justified by risk, change, or criticality.
- Do not write framework-specific automation here.
- Do not claim ownership of `coverage-plan.md` or `test-cases/*.md`.
