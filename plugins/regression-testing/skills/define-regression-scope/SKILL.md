---
name: define-regression-scope
description: >
  Use when the user wants to define rerunnable regression confidence across changed, fragile, or
  business-critical areas. Triggers include "regression scope for...", "what should be in
  regression", "what do we need to rerun before release", "changed-area test scope", or "high-risk
  regression plan". This skill owns regression intent and scope definition; it does NOT own
  exploration evidence, shared coverage planning, detailed TC-ID specs, or framework-specific
  automation.
---

# Define Regression Scope

## What this skill is for

Regression testing is about choosing the broader set of checks that should be rerun because change
or risk makes them worth the time. This skill defines that scope and explains why each area
belongs in it.

It produces a **regression charter** that ties changed areas, historical fragility, and business
criticality into a practical rerun scope.

**This skill does NOT:**
- Explore live apps (use `explore-app` from app-exploration)
- Write coverage plans (use `plan-test-coverage` from test-analysis)
- Generate test case specs (use `generate-test-cases` from test-analysis)
- Write Playwright or Robot code
- Orchestrate the full cross-plugin workflow (workflow sequencing lives in `workflow.md`)

## Integration with shared artifacts

This skill **consumes**:
- `e2e-plan/exploration-report.md` when available
- `e2e-plan/coverage-plan.md` when available
- existing `test-cases/*.md` specs when available
- existing automated coverage and repo evidence about changed areas

This skill **produces**:
- `e2e-plan/regression-charter.md` — an optional plugin-owned artifact. It is not part of the core
  shared artifact contract.

## Workflow

### 1. Build the risk picture

- Read the exploration report, coverage plan, and existing test specs first.
- Search the codebase for changed modules, routes, shared dependencies, and existing automated
  coverage.
- Note fragile or recently changed areas surfaced by the user, repo history, or code structure.
- If critical product evidence is missing, recommend `explore-app` before locking scope.

### 2. Group the candidates

Organize regression candidates into buckets such as:

- changed features
- adjacent/shared dependency features
- historically fragile flows
- business-critical paths
- cross-feature integration points

Not every bucket needs equal depth. The point is to justify why a flow is being rerun.

### 3. Classify each area

For every area, capture:

| Area | Why rerun it | Evidence basis | Suggested depth | Include? |
|---|---|---|---|---|
| Checkout totals | Shared pricing helper changed | Repo diff + existing coverage | Full end-to-end + edge validation | Yes |

Suggested depth can be: smoke-only, standard rerun, or deep rerun.

### 4. Keep the scope practical

Regression is broader than smoke, but it still needs discipline. Explicitly call out:

- what must be rerun on every release
- what is only needed because of the current change or risk
- what remains out of scope for this cycle

### 5. Write the charter

Write `e2e-plan/regression-charter.md`:

```markdown
# Regression Charter: <Feature/Product/Release>

**Date:** <date>
**Evidence basis:** exploration-report | coverage-plan | existing-specs | repo-change-analysis | mixed

## Change / Risk Summary

<what changed or why regression scope is needed>

## Included Regression Areas

| # | Area | Why Included | Evidence Basis | Suggested Depth | Suggested Downstream Target |
|---|------|--------------|----------------|-----------------|-----------------------------|
| 1 | ... | ... | ... | ... | Playwright / Robot / manual |

## Out Of Scope This Cycle

- <what is intentionally excluded>

## Evidence Gaps

- <where more exploration or clarification is still needed>

## Recommended Next Steps

- Run `explore-app` if evidence gaps block confident prioritization
- Run `plan-test-coverage` if shared prioritization still needs to be updated
- Hand the included regression areas to the execution workflow if runnable automation is requested
```

## Quality bar

- Every included area has a concrete reason tied to change, fragility, or business impact.
- The scope distinguishes always-rerun checks from change-triggered checks.
- Depth recommendations are proportional to risk.
- The charter is practical enough that a team could actually execute it.

## What to avoid

- Treating regression as "run everything."
- Pulling in low-signal areas without a reason.
- Writing framework-specific automation here.
- Claiming ownership of `coverage-plan.md` or `test-cases/*.md`.
