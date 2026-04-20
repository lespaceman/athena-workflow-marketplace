---
name: define-smoke-scope
description: >
  Use to define the smallest high-signal confidence slice for a product, feature, or release.
  Triggers include "what should be in smoke", "define the minimum checks", "smoke scope for...",
  "critical-path confidence for...", or "what must never break before release". This skill owns
  smoke intent and prioritization; it does NOT own exploration evidence, shared coverage planning,
  detailed TC-ID specs, or framework-specific automation.
---

# Define Smoke Scope

## What this skill is for

Smoke testing is about identifying the smallest set of checks that proves the product's most
critical paths still work. This skill defines that scope and the reasoning behind it.

It produces a **smoke charter** that names the must-not-break flows, what confidence they provide,
and what downstream automation should target first.

**This skill does NOT:**
- Explore live apps (use `capture-feature-evidence` from app-exploration)
- Write coverage plans (use `plan-test-coverage` from test-analysis)
- Generate test case specs (use `generate-test-cases` from test-analysis)
- Write Playwright or Robot code
- Orchestrate the full cross-plugin workflow (workflow sequencing lives in `workflow.md`)

## Integration with shared artifacts

This skill **consumes**:
- `e2e-plan/exploration-report.md` when available
- `e2e-plan/coverage-plan.md` when available
- existing `test-cases/*.md` specs and automated coverage when available

This skill **produces**:
- `e2e-plan/smoke-charter.md` — an optional plugin-owned artifact. It is not part of the core
  shared artifact contract.

## Workflow

### 1. Gather evidence

- Read the exploration report first when real product evidence exists.
- Read the coverage plan and existing specs to avoid redefining work that is already prioritized.
- Search the repo for existing automated coverage so the smoke scope reflects what is already
  runnable.
- If evidence is missing for a risky critical path, call that out and recommend `capture-feature-evidence`
  rather than guessing.

### Evidence sufficiency rule

- Treat repo context, existing specs, and prior automation as supporting evidence, not as proof of
  current live behavior.
- If the smoke decision depends on current validation behavior, redirects, auth walls, conditional
  UI, or the actual entry/completion path, require fresh or clearly relevant `capture-feature-evidence`
  evidence.
- If `e2e-plan/exploration-report.md` is missing, stale, or incomplete for a must-not-break flow,
  do one of two things only:
  - run `capture-feature-evidence` before finalizing the scope, or
  - publish a clearly labeled preliminary smoke charter with explicit evidence gaps
- Do not present a high-confidence smoke scope when critical-path evidence is still inferred.

### 2. Identify the must-not-break paths

Define the flows that would block release confidence if they failed. Typical candidates:

- sign in or session establishment
- the primary revenue or submission flow
- one critical read path that confirms the system is usable after entry
- one failure-handling path when it is central to trust or safety

Prefer 3-7 smoke scenarios. If the list is getting longer, it is probably regression scope instead.

### 3. Score each candidate

For every candidate scenario, capture:

| Flow | Why it matters | Failure impact | Evidence basis | Include in smoke? |
|---|---|---|---|---|
| Login | Users cannot access anything without it | Release blocker | Exploration report + existing test coverage | Yes |

Use evidence basis labels like: exploration report, coverage plan, existing automation, user input,
or inference.

### 4. Decide what stays out

A good smoke scope is small on purpose. Explicitly exclude:

- long-tail validation variants
- rare edge cases
- broad cross-role matrices
- non-critical cosmetic checks

If an excluded area is still important, name it as regression follow-up rather than forcing it into
smoke.

### 5. Write the charter

Write `e2e-plan/smoke-charter.md`:

```markdown
# Smoke Charter: <Feature/Product>

**Date:** <date>
**Evidence basis:** exploration-report | coverage-plan | existing-automation | mixed

## Release Mission

<one paragraph on what this smoke scope proves>

## Included Smoke Scenarios

| # | Flow | Why Included | Evidence Basis | Suggested Downstream Target |
|---|------|--------------|----------------|-----------------------------|
| 1 | ... | ... | ... | Playwright / Robot / manual |

## Explicitly Out Of Scope

- <what is intentionally excluded from smoke>

## Evidence Gaps

- <what still needs exploration or clarification>

## Recommended Next Steps

- Run `capture-feature-evidence` if critical evidence gaps remain
- Run `plan-test-coverage` if the product still needs shared prioritization
- Hand the included smoke scenarios to the execution workflow if runnable automation is requested
```

## Quality bar

- Smoke scope is small enough to run quickly and often.
- Every included flow has a concrete reason tied to release confidence.
- Exclusions are explicit, not accidental.
- The charter uses evidence where available and labels inferences honestly.
- The charter does not treat old specs or existing automation as proof that the live path still
  works.

## What to avoid

- Turning smoke into a full regression suite.
- Including every validation rule just because it exists.
- Writing framework-specific automation steps here.
- Claiming ownership of `coverage-plan.md` or `test-cases/*.md`.
- Presenting an inferred critical path as confirmed when live evidence is missing.
