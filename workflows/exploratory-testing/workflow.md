# Exploratory Testing Workflow

You define exploratory testing intent before the suite moves into detailed planning or automation.

## Skills

| Activity | Skill |
|----------|-------|
| Define exploratory charter, risk hypotheses, investigation order, and exploration gaps | `exploratory-test-writer` |
| Gather grounded product evidence | `explore-app` |
| Turn confirmed risks into shared coverage planning and final P0/P1/P2 prioritization | `plan-test-coverage` |
| Turn shared plans into detailed specs | `generate-test-cases` |

## Workflow Sequence

The default progression is:

**write exploratory charter → run explore app when needed to close evidence gaps → finalize charter → optionally plan coverage → optionally generate specs**

### Orientation

- Load `exploratory-test-writer` as the intent-layer entry point.
- Use the first charter pass to decide whether grounded product evidence is missing, stale, or too
  thin to support confident risk framing.
- If the charter depends on grounded product behavior and `e2e-plan/exploration-report.md` is
  missing or stale, run `explore-app`, then return to `exploratory-test-writer` to finalize the
  charter.
- Use the completed charter to identify what still needs deeper probing and what should be handed to
  shared planning next.

## Handoff Rules

- `exploratory-test-writer` owns `e2e-plan/exploratory-charter.md`, including mission, risk
  hypotheses, exploratory ordering, and evidence gaps.
- `plan-test-coverage` may consume that charter as optional context, but it owns the final
  P0/P1/P2 coverage priority and it does not let the charter replace the required grounded evidence
  in `e2e-plan/exploration-report.md`.
- `explore-app` owns `e2e-plan/exploration-report.md`.
- `plan-test-coverage` owns `e2e-plan/coverage-plan.md`.
- `generate-test-cases` owns `test-cases/<feature>.md`.

If the user explicitly asks for shared coverage planning or test-case specs, load the shared
`test-analysis` skills after the charter is complete. Do not encode that sequencing inside the
plugin skill itself.

If runnable automation is requested after the exploratory charter is finalized, stop with an
explicit recommendation to move into the appropriate execution workflow:

- `e2e-test-builder` for Playwright
- `robot-automation` for Robot Framework

This workflow does not load execution-layer plugins itself, so it must not claim to implement or
run framework automation in the same workflow session.

## Guardrails

- Do not present inferences as observed evidence.
- Do not write framework-specific automation from this workflow.
- Stop and recommend deeper exploration if the charter depends on evidence that has not been
  gathered yet.
