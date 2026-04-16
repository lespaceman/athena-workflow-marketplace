---
name: exploratory-test-writer
description: >
  Use when the user wants to define an exploratory testing charter — framing what to investigate,
  why, and what risk hypotheses to test — before or alongside the shared testing workflow. Triggers
  include "exploratory testing for...", "what should I investigate in this app", "help me think
  about what could go wrong", "risk hypotheses for...", "testing charter for...", "where should I
  probe deeper", or any request that needs structured thinking about test intent before coverage
  planning begins. This skill owns exploratory intent and risk framing; it does NOT own exploration
  evidence (explore-app), coverage plans (plan-test-coverage), or test case specs
  (generate-test-cases).
---

# Exploratory Test Writer

## What this skill is for

Exploratory testing is a thinking activity. Before planning coverage or writing test cases, someone
needs to decide *what to investigate and why*. This skill owns that decision.

It produces an **exploratory charter** — a structured document that frames the risks, hypotheses,
and investigation focus areas for a product or feature. The charter feeds into the shared testing
workflow but does not replace any part of it.

**This skill does NOT:**
- Explore live apps (use `explore-app` from app-exploration)
- Write coverage plans (use `plan-test-coverage` from test-analysis)
- Generate test case specs (use `generate-test-cases` from test-analysis)
- Orchestrate cross-plugin workflow (workflow orchestration lives in `workflow.md`)

It may recommend or require these downstream steps, but it does not become the authoritative
sequencer for them.

## Integration with shared artifacts

This skill **consumes**:
- `e2e-plan/exploration-report.md` — when available, uses it to ground risk hypotheses in observed
  behavior rather than speculation

This skill **produces**:
- `e2e-plan/exploratory-charter.md` — an optional artifact owned by this plugin. It is not part of
  the core shared artifact contract (`exploration-report.md`, `coverage-plan.md`,
  `test-cases/*.md`). Downstream skills may consume it for context but do not depend on it.

Before doing anything, check whether these artifacts already exist. Prior exploration work is
valuable evidence — don't discard it.

## Calibrating depth

Match your effort to the ask:

- **"What should I look at in X?"** — Quick charter. Identify the top 3-5 risk areas, frame one
  hypothesis per area. 10-minute exercise.
- **"Exploratory testing plan for X"** — Standard charter. Map risk areas systematically, frame
  hypotheses with rationale, identify where deeper exploration is needed. Interview the user.
- **"Comprehensive risk analysis for X"** — Deep charter. Full risk inventory, integration-point
  analysis, persona-based risk framing, explicit assumptions and unknowns.

When in doubt, start standard and ask: "I've framed the key risks — want me to go deeper on any
area?"

## Workflow

### 1. Gather context

- Read `e2e-plan/exploration-report.md` if it exists. Use observed behavior to ground your risk
  framing.
- Read `e2e-plan/coverage-plan.md` and `test-cases/*.md` if they exist, so you don't duplicate
  existing coverage thinking.
- Search the codebase for feature keywords, route names, and existing test files.
- If no exploration report exists and the user hasn't provided product context, note this as a gap
  and recommend running `explore-app` first. You can still produce a preliminary charter from what
  the user tells you, but label ungrounded hypotheses clearly.

### 2. Interview the user

Ask questions to understand test intent:

- "What part of this scares you most?"
- "Who are the users, and what's their most critical path?"
- "What's gone wrong before?"
- "What's the worst case if this breaks?"
- "Are there areas you know are fragile or recently changed?"
- "What's out of scope — what should I NOT spend time on?"

A 2-minute exchange often surfaces risks that no amount of code reading would reveal.

### 3. Frame risk hypotheses

For each area of the product, frame a testable hypothesis:

| Area | Hypothesis | Basis | Priority |
|------|-----------|-------|----------|
| Login validation | Server-side validation may be missing — client-only checks were observed | Exploration report: empty name/message submitted successfully | P0 |
| Payment flow | Concurrent submissions may create duplicate charges | User interview: "this happened once in staging" | P0 |
| Settings page | Config changes may not persist across sessions | Inference — no exploration evidence yet | P1 |

**Basis** must cite its source: exploration report, user interview, codebase search, or inference.
Inferences are valid but must be labeled as such.

**Priority** uses the suite convention:
- **P0** — High impact x high likelihood. Investigate first.
- **P1** — High impact x low likelihood, or low impact x high likelihood.
- **P2** — Low impact x low likelihood. Investigate if time allows.

### 4. Identify exploration gaps

Based on your hypotheses, identify where evidence is missing:

- Which hypotheses are grounded in observed behavior?
- Which are inferences that need exploration to confirm?
- Which areas of the product haven't been explored at all?

For each gap, recommend what `explore-app` should focus on. Be specific: "Explore the password
reset flow — we have no evidence of its validation behavior" is useful. "Explore more" is not.

### 5. Write the charter

Write `e2e-plan/exploratory-charter.md`:

```markdown
# Exploratory Charter: <Feature/Product>

**Date:** <date>
**Requested by:** <user context>
**Evidence basis:** exploration-report | user-interview | repo-only | none

## Mission

<1-2 sentences: what are we trying to learn, and why does it matter?>

## Risk Hypotheses

| # | Area | Hypothesis | Basis | Priority |
|---|------|-----------|-------|----------|
| 1 | ... | ... | ... | P0 |
| 2 | ... | ... | ... | P1 |

## Exploration Gaps

- <gap>: recommend `explore-app` focus on <specific area>
- ...

## Out of Scope

- <what we're deliberately not investigating, and why>

## Assumptions

- <what we're assuming to be true without evidence>

## Recommended Next Steps

- Run `explore-app` to close evidence gaps listed above
- Run `plan-test-coverage` to turn confirmed risks into a coverage plan
- Run `generate-test-cases` to produce specs from the coverage plan
```

### 6. Present and iterate

Share the charter with the user. The charter is a conversation artifact — it's meant to be
reviewed, questioned, and refined before downstream skills consume it.

## Quality bar

- Every hypothesis cites its basis (observed, interviewed, inferred).
- Priorities trace to impact and likelihood, not gut feeling.
- Exploration gaps are specific and actionable.
- The charter is honest about what's unknown and what's assumed.
- The mission statement would make sense to someone who hasn't seen the app.

## What to avoid

- Writing test cases directly — that's `generate-test-cases`'s job.
- Producing a coverage plan — that's `plan-test-coverage`'s job.
- Exploring the live app — that's `explore-app`'s job.
- Orchestrating the full workflow — that's `workflow.md`'s job.
- Presenting inferences as confirmed risks.
- Ignoring existing artifacts and starting from zero.
