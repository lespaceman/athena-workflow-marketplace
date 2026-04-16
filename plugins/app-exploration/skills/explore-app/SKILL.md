---
name: explore-app
description: >
  Explore a live app and capture grounded evidence in `e2e-plan/exploration-report.md`. Use when downstream planning, test-case generation, or test implementation needs real product understanding before specs or code are written: mapping journeys, capturing selectors and form fields, recording validation or error states, checking auth gates, or documenting blockers that prevent confident planning. This skill owns product exploration; it should be used before `plan-test-coverage` when real product evidence matters.
allowed-tools: Read Write Edit Glob Grep Task
---

# Explore App

Capture real product evidence for the target journey and hand it off in a stable artifact that the
rest of the testing suite can consume.

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
- Run `plan-test-coverage` using this report
```

### 4. Stop cleanly when evidence is missing

If you cannot gather the evidence needed for safe planning:
- still write the exploration report
- mark the report `BLOCKED` or `PARTIAL`
- record the exact blocker
- tell downstream skills to stop instead of inventing behavior

## Quality Bar

- Prefer semantic selector candidates such as role, accessible name, label, placeholder, or test id
  over raw CSS when recording controls.
- Record exact validation or error copy only when it was directly observed.
- Do not silently replace blocked exploration with assumptions.
- Keep the report reusable by future planning and execution skills.
