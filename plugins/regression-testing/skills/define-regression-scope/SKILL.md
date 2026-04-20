---
name: define-regression-scope
description: >
  Use to define impact-based regression scope for a release, hotfix, changed area, or risky
  feature: decide what should be rerun beyond smoke, why it belongs in regression, and how deep
  each area should go. Triggers include "regression scope for...", "what should we rerun after
  this change", "what belongs in release regression", "impact-based rerun plan", "high-risk
  regression plan", "what's beyond smoke", or "pre-release regression checklist". This skill owns
  regression intent, included areas, and rerun depth; it does NOT own live exploration, shared
  coverage planning, detailed TC-ID specs, or framework-specific automation.
---

# Define Regression Scope

Define a practical rerunnable regression charter from change, risk, and business criticality.

Regression is broader than smoke. Use this skill to answer: "What do we need to rerun now, and how
deep should each area go?" Prefer a justified rerun list over a blanket "run everything" answer.

## Calibrate scope depth

Match the output to the ask:

- **"What should we rerun after X?"** — Produce a light charter. Focus on changed areas plus the
  highest-risk adjacent fallout.
- **"Define regression scope for this release"** — Produce a standard charter. Include the
  always-rerun baseline plus change-triggered additions.
- **"Comprehensive pre-release regression"** — Produce a deep charter. Expand shared dependencies,
  integration points, and historically fragile flows, but still justify every area.

If the request is for the smallest release gate, switch to `define-smoke-scope` instead of
shrinking regression until it becomes smoke.

## Boundaries

This skill does:

- define rerunnable regression areas
- explain why each area is included
- recommend rerun depth
- identify evidence gaps and downstream targets

This skill does not:

- explore live apps (use `capture-feature-evidence` from app-exploration)
- write coverage plans (use `plan-test-coverage` from test-analysis)
- generate test case specs (use `generate-test-cases` from test-analysis)
- write Playwright or Robot code
- orchestrate the full cross-plugin workflow (workflow sequencing lives in `workflow.md`)

## Integration with shared artifacts

This skill consumes:

- `e2e-plan/exploration-report.md` when available
- `e2e-plan/coverage-plan.md` when available
- existing `test-cases/*.md` specs when available
- existing automated coverage and repo evidence about changed areas

This skill produces:

- `e2e-plan/regression-charter.md` — an optional plugin-owned artifact. It is not part of the core
  shared artifact contract.

## Workflow

### 1. Load the evidence base

- Read the exploration report, coverage plan, and existing test specs first.
- Search the codebase for changed modules, routes, shared dependencies, feature flags,
  integrations, and existing automated coverage.
- Note fragile or recently changed areas surfaced in the request, repo history, or code structure.
- Mark which signals are observed versus inferred.

### Evidence sufficiency rule

- Treat repo diffs, old specs, and existing automation as change signals and supporting context, not
  as proof of current live behavior.
- If rerun depth depends on current validation behavior, redirects, auth walls, conditional UI,
  cross-feature interaction, or end-to-end path shape, require fresh or clearly relevant
  `capture-feature-evidence` evidence.
- If `e2e-plan/exploration-report.md` is missing, stale, or incomplete for an included area, do one
  of two things only:
  - run `capture-feature-evidence` to close the gap, or
  - publish a clearly labeled preliminary regression charter with explicit evidence gaps
- Do not present a high-confidence final charter when key included areas still rely on inference.

### 2. Build candidate buckets

Organize candidates into buckets such as:

- changed features
- adjacent or shared dependency features
- business-critical baseline flows
- historically fragile or recently repaired flows
- cross-feature integration points
- role-specific or configuration-specific paths touched by the change

Not every bucket needs equal depth. The point is to justify why a flow is worth rerunning.

### 3. Decide inclusion and rerun depth

Capture each candidate in a working table:

| Area | Why rerun it | Evidence basis | Suggested depth | Include? |
|---|---|---|---|---|
| Checkout totals | Shared pricing helper changed | Repo diff + existing coverage | Deep rerun | Yes |

Use these depth labels:

- `smoke-only` — a narrow sanity check is enough because the blast radius is small
- `standard rerun` — rerun the full happy path plus common validation or error handling
- `deep rerun` — cover multiple states, roles, or edge conditions because risk is high

Promote depth when one or more of these are true:

- a shared dependency or cross-cutting helper changed
- the area is revenue-critical, trust-critical, or release-blocking
- the area has recent incidents, flaky coverage, or weak existing automation
- the change touches multi-step integration behavior

Reduce depth only when the change is clearly isolated, the blast radius is low, and existing
coverage is strong enough to justify a narrower rerun.

### 4. Separate baseline from change-triggered scope

Explicitly distinguish:

- what should rerun on every release as the baseline regression layer
- what is added only because of the current change or risk profile
- what remains out of scope for this cycle

If everything lands in one bucket, the charter is usually too vague to be actionable.

### 5. Write the charter

Write `e2e-plan/regression-charter.md`:

```markdown
# Regression Charter: <Feature/Product/Release>

**Date:** <date>
**Evidence basis:** exploration-report | coverage-plan | existing-specs | repo-change-analysis | mixed
**Status:** FINAL | PRELIMINARY

## Change / Risk Summary

<what changed or why regression scope is needed>

## Included Regression Areas

| # | Scope Lane | Area | Why Included | Evidence Basis | Suggested Depth | Suggested Downstream Target |
|---|------------|------|--------------|----------------|-----------------|-----------------------------|
| 1 | Always rerun | Login/session establishment | Core release confidence | Exploration report + existing automation | Standard rerun | Playwright / Robot / manual |
| 2 | Change-triggered | Checkout totals | Shared pricing helper changed | Repo diff + coverage plan | Deep rerun | Playwright / Robot / manual |

## Out Of Scope This Cycle

- <what is intentionally excluded>

## Evidence Gaps

- <where more exploration or clarification is still needed>

## Recommended Next Steps

- Run `capture-feature-evidence` if evidence gaps block confident prioritization
- Run `plan-test-coverage` if shared prioritization still needs to be updated
- Expand or refresh `test-cases/*.md` if deeper shared specs are still missing
- Hand the included regression areas to the execution workflow if runnable automation is requested
```

## Quality bar

- Every included area has a concrete reason tied to change, fragility, business impact, or
  baseline release confidence.
- The charter separates always-rerun baseline checks from current-change additions.
- Depth recommendations are proportional to risk.
- The charter is practical enough that a team could actually execute it.
- The charter does not treat repo change analysis as proof that the current live flow behaves the
  same way.

## What to avoid

- Treating regression as "run everything."
- Pulling in low-signal areas without a reason.
- Collapsing regression and smoke into the same artifact.
- Writing framework-specific automation here.
- Claiming ownership of `coverage-plan.md` or `test-cases/*.md`.
- Presenting inferred rerun depth as confirmed when live evidence is still missing.
