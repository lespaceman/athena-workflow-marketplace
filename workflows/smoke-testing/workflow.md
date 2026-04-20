# Smoke Testing Workflow

You define the smallest high-signal set of checks that proves the product's critical paths still
work.

## Skills

| Activity | Skill |
|----------|-------|
| Define the smoke charter and included release checks | `define-smoke-scope` |
| Gather grounded product evidence | `capture-feature-evidence` |
| Update shared prioritization when needed | `plan-test-coverage` |

## Workflow Sequence

The default progression is:

**explore app when needed → define smoke scope → optionally refresh shared coverage plan → produce an explicit handoff recommendation if runnable automation is requested**

### Orientation

- Load `define-smoke-scope` as the workflow entry skill.
- If the smoke decision depends on real product behavior and `e2e-plan/exploration-report.md` is
  missing or stale, load `capture-feature-evidence` first.
- If the release still needs shared prioritization or updated TC-ID planning, load
  `plan-test-coverage` after the smoke charter is drafted.

## Handoff Rules

- `define-smoke-scope` owns `e2e-plan/smoke-charter.md`, not the shared artifact chain.
- `capture-feature-evidence` owns `e2e-plan/exploration-report.md`.
- `plan-test-coverage` owns `e2e-plan/coverage-plan.md`.

If runnable automation is requested after the smoke charter is finalized, stop with an explicit
recommendation to move into the appropriate execution workflow:

- `playwright-automation` for Playwright
- `robot-automation` for Robot Framework

This workflow does not load execution-layer plugins itself, so it must not claim to implement or
run the framework automation in the same workflow session.

## Guardrails

- Keep smoke intentionally small; if the scope keeps expanding, treat that as regression work.
- Do not write framework-specific automation here.
- Do not claim ownership of `coverage-plan.md` or `test-cases/*.md`.
