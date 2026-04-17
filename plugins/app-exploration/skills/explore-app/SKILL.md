---
name: explore-app
description: >
  Explore a live app and capture grounded evidence in `e2e-plan/exploration-report.md`. Use when downstream planning, test-case generation, or test implementation needs real product understanding before specs or code are written: mapping journeys, capturing selectors and form fields, recording validation or error states, checking auth gates, or documenting blockers that prevent confident planning. This skill owns observed product evidence and blockers; it does not frame exploratory charters, prioritize risks, or write coverage plans.
allowed-tools: Read Write Edit Glob Grep Task
---

# Explore App

Capture real product evidence for the target journey and hand it off in a stable artifact that the
rest of the testing suite can consume.

This skill owns observed product evidence and blockers. It does not own risk prioritization,
exploratory charters, smoke/regression scope, or coverage planning.

## Input

Parse the target URL and feature or journey description from: $ARGUMENTS

Derive a short feature slug from the journey so the evidence is easy to reference later.

## Workflow

### 1. Build context before browsing

- Read any existing `e2e-plan/exploration-report.md`, `e2e-plan/coverage-plan.md`, and
  `test-cases/*.md` files for the same feature so you do not duplicate stale assumptions.
- Search the codebase for feature keywords, route names, and existing test files to understand what
  is already known and where exploration should focus.
- State the evidence gap you are trying to close.

### 2. Explore the live product via browser tooling

- Delegate browser work to a subagent when that saves context. Instruct it to use
  `agent-web-interface-guide` and return structured observations rather than a narrative summary.
- Walk the target journey as a real user would:
  - visit the starting URL
  - identify the main entry points
  - click through the happy path
  - deliberately trigger meaningful validation, empty, and error states
  - note redirects, auth walls, and conditional UI
- Capture only grounded observations. If an outcome was inferred rather than observed, label it as
  an inference.

#### Recon pass

Before systematic touring, use the app with no agenda. Visit at minimum: the main user flow
end-to-end, one settings/config page, and one error state (bad input, empty state, or a 404). The
goal is intuition for what the app *is* before structured touring.

#### Structured touring

Look at the app through specific lenses. Pick tours based on complexity:

**Simple apps** (one main flow, < 5 pages): Feature + Data + Error tours are sufficient.
**Medium apps** (multiple features, user roles, settings): Add Interaction + Configuration tours.
**Complex apps** (many integrations, money involved, multi-role): Do all six.

The tours:

- **Feature Tour** — enumerate every button, menu, page, setting. Inventory, not depth. Tells you
  what features exist for downstream planning.
- **Data Tour** — what data goes in? Where does it come from? Where does it go? What are the limits
  (length, type, format)? This one catches the most bugs.
- **Error/Interrupt Tour** — close the tab mid-save, lose network, paste unicode, enter `<script>`,
  hit back button, refresh, log out from another session. Finds the bugs nobody wrote tests for.
- **Interaction Tour** — when feature A changes data, does feature B reflect it correctly? Important
  when features share state.
- **Configuration Tour** — settings, toggles, permissions, roles. Each config option is a
  test-matrix multiplier, so it matters to know what's configurable.
- **Money Tour** — what does the business actually make money from? What's the "crown jewel" path?
  This helps downstream prioritization later; do not prioritize it here.

#### Exploration notes

As you explore, maintain a running working document using this four-column format:

| Observation | Open question | Evidence gap | Notes |
|---|---|---|---|
| Login accepts email only, no username | Is there also an SSO path? | Password reset and SSO entry points were not explored yet | Email field label and submit button were directly observed |
| Form has no visible character limit on "name" field | Is the limit enforced server-side or only omitted from the UI? | Boundary behavior past 255 chars is still unknown | HTML/UI did not show a maxlength or helper copy |

Capture fast, don't polish. This table preserves factual loose ends for downstream chartering and
planning.

#### Clarify scope when needed

If additional context can be requested, ask clarifying questions that improve factual exploration:
"Which environment is safe to explore?" "Are there seeded accounts, roles, or data states I
should use?" "Which paths are in scope for this session?" A 2-minute exchange often saves an hour
of guessing.

Return browser findings in a structure like:

```text
Step: Submit empty login form
URL: https://example.com/login
Observed elements:
  - Email field: label "Email"
  - Submit button: role=button, name=/sign in/i
Observed result:
  - Inline message under Email: "Email is required"
Notes:
  - Password field shows a separate required message only after blur
```

### 3. Distill the evidence

Write or update `e2e-plan/exploration-report.md`.

The report must separate:
- **Observed evidence**: behavior directly seen in the browser or codebase
- **Inferences**: reasonable conclusions that still need confirmation
- **Blockers**: anything preventing confident downstream planning

Use this structure:

```markdown
# Exploration Report: <Feature>

**URL:** <url>
**Date:** <date>
**Scope:** <journey explored>
**Evidence status:** COMPLETE | PARTIAL | BLOCKED

## Summary
- <2-4 bullets with the main grounded findings>

## Journey Map
1. <entry step>
2. <next step>
3. <completion state>

## Observed Screens, States, And Controls
| Step | URL | User action | Observed result | Selector candidates / labels |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Validation And Error Evidence
- <empty-state behavior>
- <invalid-input behavior>
- <server/network/error-state observations or note that they were not reachable>

## Blockers
- <auth wall, CAPTCHA, missing environment, unavailable path, or "None">

## Inferences That Still Need Confirmation
- <only include if something remains unverified>

## Recommended Next Step
- <choose the next consumer of this evidence: `exploratory-test-writer`, `define-smoke-scope`,
  `define-regression-scope`, or `plan-test-coverage`>
```

### 4. Stop cleanly when evidence is missing

If you cannot gather the evidence needed for safe planning:
- still write the exploration report
- mark the report `BLOCKED` or `PARTIAL`
- record the exact blocker
- tell downstream skills to stop instead of inventing behavior

## Destructive actions

When exploring, avoid actions that would damage real data: don't delete anything, don't send
emails/messages to real contacts, don't submit payments. If the app is a production system (not a
sandbox), pause and ask which actions are safe before touring the error/interrupt cases. The
exploration is valuable, but not valuable enough to break live data.

## Quality Bar

- Prefer semantic selector candidates such as role, accessible name, label, placeholder, or test id
  over raw CSS when recording controls.
- Record exact validation or error copy only when it was directly observed.
- Do not silently replace blocked exploration with assumptions.
- Keep the report reusable by future planning and execution skills.
- Do not turn observations into prioritized risks, charters, or coverage decisions inside this
  artifact.
- Cases reference specific things actually observed in the app (real field names, real error
  messages, real API endpoints, real selectors).
- The exploration summary is honest about what wasn't covered and what's still unknown.
- Artifacts are written to the shared locations (`e2e-plan/`) so downstream skills can consume them.

## What to avoid

- Skipping exploration and hallucinating features that don't exist.
- Burying the exploration notes so it is unclear what was or wasn't looked at.
- Ignoring existing exploration artifacts and starting from zero.
- Turning raw observations into a prioritized test charter or coverage plan inside this skill.
