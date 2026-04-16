# Exploratory Testing Workflow

You define exploratory testing intent before the suite moves into detailed planning or automation.

## Skills

| Activity | Skill |
|----------|-------|
| Define exploratory charter, risk hypotheses, and exploration gaps | `exploratory-test-writer` |
| Gather grounded product evidence | `explore-app` |
| Turn confirmed risks into shared coverage planning | `plan-test-coverage` |
| Turn shared plans into detailed specs | `generate-test-cases` |

## Workflow Sequence

The default progression is:

**explore app when needed → write exploratory charter → optionally plan coverage → optionally generate specs**

### Orientation

- Load `exploratory-test-writer` as the intent-layer entry point.
- If grounded product evidence is required and `e2e-plan/exploration-report.md` is missing or stale,
  load `explore-app` first.
- Use the exploratory charter to identify what still needs deeper probing and what should be handed
  to shared planning next.

## Handoff Rules

- `exploratory-test-writer` owns `e2e-plan/exploratory-charter.md`, not the shared artifact chain.
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
