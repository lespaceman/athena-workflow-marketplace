---
name: exploratory-test-writer
description: >
  Define an exploratory testing charter: frame what to investigate, why it matters, and which risk
  hypotheses to test before or alongside the shared testing workflow. Triggers include
  "exploratory testing for...", "what should I investigate in this app", "help me think about what
  could go wrong", "risk hypotheses for...", "testing charter for...", "where should I probe
  deeper", or any request that needs structured thinking about test intent before coverage
  planning begins. This skill owns exploratory intent, risk framing, investigation order, and
  concrete follow-up asks for missing evidence; it does NOT own exploration evidence
  (explore-app), final coverage prioritization (plan-test-coverage), or test case specs
  (generate-test-cases).
---

# Exploratory Test Writer

## What this skill is for

Exploratory testing is a thinking activity. Before planning coverage or writing test cases, someone
needs to decide *what to investigate and why*. This skill owns that decision.

It produces an **exploratory charter** — a structured document that frames the risks, hypotheses,
and investigation focus areas for a product or feature. The charter feeds into the shared testing
workflow but does not replace any part of it.

This skill is the owner of exploratory risk framing and investigation order. It turns evidence,
interviews, and repo context into investigation intent; it does not collect the canonical live-app
evidence itself, and it does not assign the final P0/P1/P2 coverage plan.

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
- `e2e-plan/exploratory-charter.md` — an artifact owned by this plugin. It complements, rather than
  replaces, the core shared artifact chain (`exploration-report.md`, `coverage-plan.md`,
  `test-cases/*.md`). Downstream skills may consume it for context but do not depend on it.

Before doing anything, check whether these artifacts already exist. Prior exploration work is
valuable evidence — don't discard it.

## Calibrating depth

Match your effort to the ask:

- **"What should I look at in X?"** — Quick charter. Identify the top 3-5 risk areas, frame one
  hypothesis per area. 10-minute exercise.
- **"Exploratory testing plan for X"** — Standard charter. Map risk areas systematically, frame
  hypotheses with rationale, identify where deeper exploration is needed. Ask targeted questions
  when context is missing.
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
- If no exploration report exists and product context is still missing, note this as a gap and
  recommend running `explore-app` first. You can still produce a preliminary charter from the
  available request context, but label ungrounded hypotheses clearly.
- If grounded product behavior is required for confident prioritization, stop and request
  `explore-app` before presenting a high-confidence charter.

### Evidence sufficiency rule

- Treat code reading, old test specs, and user descriptions as supporting context, not as a
  substitute for observed product behavior.
- If selector choices, validation behavior, redirects, auth walls, conditional UI, or error states
  materially affect prioritization, require fresh or clearly relevant `explore-app` evidence.
- If the available exploration report is missing, stale, or incomplete for the decision you need to
  make, do one of two things only:
  - run `explore-app` to close the gap, or
  - produce a clearly labeled preliminary charter with explicit evidence gaps
- Do not present a high-confidence charter when those gaps remain open.

### 2. Gather missing context

Ask questions to understand test intent:

- "What part of this scares you most?"
- "Which personas matter most, and what's the most critical path for each?"
- "What's gone wrong before?"
- "What's the worst case if this breaks?"
- "Are there areas you know are fragile or recently changed?"
- "What's out of scope — what should I NOT spend time on?"

A 2-minute exchange often surfaces risks that no amount of code reading would reveal.

### 3. Frame risk hypotheses

For each area of the product, frame a testable hypothesis:

| Area | Hypothesis | Basis | Investigate when |
|------|-----------|-------|------------------|
| Login validation | Server-side validation may be missing — client-only checks were observed | Exploration report: empty name/message submitted successfully | First |
| Payment flow | Concurrent submissions may create duplicate charges | User interview: "this happened once in staging" | First |
| Settings page | Config changes may not persist across sessions | Inference — no exploration evidence yet | Next |

**Basis** must cite its source: exploration report, user interview, codebase search, or inference.
Inferences are valid but must be labeled as such.

**Investigation order** uses exploratory language:
- **First** — highest-risk or highest-uncertainty area to probe before planning coverage
- **Next** — important area to investigate after the first-pass risks are clarified
- **Later** — worthwhile if time remains or if later evidence makes it more urgent

This skill owns that exploratory ordering. Final P0/P1/P2 coverage priority belongs to
`plan-test-coverage`. Do not restate raw UI inventory here unless it directly supports a
hypothesis.

### 4. Identify exploration gaps

Based on your hypotheses, identify where evidence is missing:

- Which hypotheses are grounded in observed behavior?
- Which are inferences that need exploration to confirm?
- Which areas of the product haven't been explored at all?

For each gap, recommend what `explore-app` should focus on. Be specific: "Explore the password
reset flow — we have no evidence of its validation behavior" is useful. "Explore more" is not.

Each gap should be directly handoff-ready and include:
- the area or flow that needs evidence
- the exact behavior that needs confirmation
- why that evidence changes what should be investigated first
- a concrete starting point when known (entry URL, role, precondition, or state)

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

| # | Area | Hypothesis | Basis | Investigate when |
|---|------|-----------|-------|------------------|
| 1 | ... | ... | ... | First |
| 2 | ... | ... | ... | Next |

## Exploration Gaps

- <gap title> — Need evidence for <specific behavior>. Ask `explore-app` to start at <entry point
  or URL>, exercise <path or state>, and confirm <unknown behavior>.
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

Share the charter for review. The charter is a conversation artifact — it's meant to be reviewed,
questioned, and refined before downstream skills consume it.

## Quality bar

- Every hypothesis cites its basis (observed, interviewed, inferred).
- Investigation order traces to impact, uncertainty, and user concern, not gut feel.
- Exploration gaps are specific enough to hand directly to `explore-app` without reinterpretation.
- The charter is honest about what's unknown and what's assumed.
- The mission statement would make sense to someone who hasn't seen the app.
- The charter does not duplicate the exploration report's UI inventory or selector detail.
- The charter does not assign final P0/P1/P2 coverage priority; that handoff belongs to
  `plan-test-coverage`.
- The charter does not treat repo context or prior specs as proof of current live behavior.

## What to avoid

- Writing test cases directly — that's `generate-test-cases`'s job.
- Producing a coverage plan — that's `plan-test-coverage`'s job.
- Exploring the live app — that's `explore-app`'s job.
- Orchestrating the full workflow — that's `workflow.md`'s job.
- Assigning final P0/P1/P2 coverage priority — that's `plan-test-coverage`'s job.
- Presenting inferences as confirmed risks.
- Presenting a repo-only charter as high-confidence when live evidence is required.
- Ignoring existing artifacts and starting from zero.
- Rewriting raw exploration notes instead of converting them into hypotheses and follow-up asks.
