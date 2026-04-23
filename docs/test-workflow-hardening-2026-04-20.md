# Test Workflow Hardening Proposal

**Date:** 2026-04-20
**Scope:** `workflows/playwright-automation/workflow.md`, `workflows/robot-automation/workflow.md`, `plugins/*/skills/add-*-tests/SKILL.md`, `plugins/*/skills/fix-flaky-tests/SKILL.md`, shared exploration/planning/review skills
**Status:** Implemented in live workflow and skill instructions on 2026-04-23

## Why This Exists

A recent map-feature run exposed a class of failures that the current workflow and skill
instructions do not prevent strongly enough:

- scope changed during Gate 3 and the run still advanced toward signoff
- tests were deferred based on weak or stale evidence instead of fresh exploration
- Gate 4 allowed a `GREEN` verdict even when promoted coverage was deferred for unresolved DOM
  blockers
- new-test verification and pre-existing suite stabilization got mixed together
- final reporting drifted from what actually changed during execution

The issue is not one bad agent decision. The current instructions leave too much room for those
decisions to look acceptable.

## Failure Modes Seen In The Transcript

### 1. Mid-run scope drift

During Gate 3, multiple TCs were removed or deferred after execution had already started. The run
continued toward signoff without clearly resetting the gate sequence.

### 2. Deferral used as an execution escape hatch

The run deferred tests when the true conclusion was "we need fresh browser evidence at the actual
execution viewport / DOM state." The workflow currently says deferred items need justification, but
it does not clearly say when deferral is forbidden.

### 3. Coverage verdict inflation

Gate 4 ended at `GREEN` even though several promoted cases were deferred due to unresolved
automation blockers. The current `GREEN` definition is too permissive.

### 4. New coverage work mixed with unrelated suite repair

Pre-existing flaky tests and leaking state from existing tests influenced whether the new work could
sign off. The run eventually repaired old tests inline, which is sometimes useful, but it muddied
what was actually being validated.

### 5. Weak retry governance

Removing the fixed retry cap was correct, but the replacement guidance is still too high-level. It
does not force the agent to distinguish:

- "new evidence, keep going"
- "same experiment again, stop"
- "blocked on missing exploration, bounce back to evidence gathering"

### 6. Final reporting was not strongly constrained

The run produced inconsistent statements about counts and modified files. Current instructions do
not require a strict run ledger or artifact-change summary.

## Root Causes In The Current Instructions

### Workflows

Both execution workflows define Gate 3 as "fix and rerun while progress continues," but neither
defines what happens when the target suite changes after Gate 2 has already passed.

Both workflows also let Gate 4 mark `GREEN` when gaps are merely "classified and justified." That
is too loose when the missing coverage was already promoted into planned TC work.

### Entry skills

`add-playwright-tests` and `add-robot-tests` do not explicitly require:

- re-running Gate 2 after materially changing test scope or test code during Gate 3
- splitting "new tests in isolation" from "full suite regression"
- returning to exploration when execution exposes selector/viewport/DOM uncertainty

### Fix-flaky skills

The flake-fix skills tell the agent to keep iterating while new evidence exists, but they do not
state that some blockers are evidence gaps, not flakiness. That invites guess-based fixes such as:

- coordinate clicks without fresh verification
- page-wide text oracles
- force-clicking through overlays
- JavaScript-dispatched clicks as a first resort

### Shared exploration and planning skills

`capture-feature-evidence` requires grounded observations, but it does not explicitly require
recording the viewport, layout assumptions, or execution-relevant selector constraints for brittle
surfaces.

`plan-test-coverage` and `review-test-cases` govern deferrals in the spec stage, but there is no
equally strong rule for execution-time deferrals discovered later.

## Proposed Instruction Changes

## 1. Add A "Gate Reset" Rule

Add this rule to both workflow docs and both `add-*-tests` skills:

> **Gate reset rule:** if the planned TC set, spec, coverage plan, or executed test file changes in
> a way that adds, removes, defers, or materially rewrites covered behavior after Gate 2, the run
> must reset to the earliest affected gate. At minimum:
> - rerun Gate 2 for changed test code
> - rerun Gate 1 if the spec or deferral set changed
> - restart the consecutive-green counter for Gate 3
>
> Do not count pre-change runs toward post-change signoff.

Why: this directly prevents the "drop tests mid-run and keep counting" failure.

## 2. Add An "Execution-Time Deferral" Policy

Add this rule to both workflow docs, both `add-*-tests` skills, and `fix-flaky-tests`:

> **Execution-time deferral is exceptional.** A test discovered during Gate 3 may be deferred only
> when:
> - the blocker is concrete and external to the current test implementation
> - the blocker is documented in the spec and coverage plan with blocker, un-defer plan, and scope
> - the run returns to the required earlier gate(s) before signoff
>
> Do not defer a test to avoid re-exploration, locator verification, or code review. If the blocker
> is "selector uncertain", "DOM differs from exploration", "viewport/layout mismatch", or "needs
> browser confirmation", stop execution and refresh exploration evidence first.

Why: this closes the gap that let uncertainty masquerade as a valid deferral.

## 3. Tighten Gate 4 Verdict Definitions

Replace the current Gate 4 verdict language with:

> **GREEN** — every promoted P0/P1 inventory-backed behavior is covered functionally, or any
> uncovered item is explicitly out of current scope and was never promoted into the accepted spec or
> coverage plan.
>
> **YELLOW** — one or more promoted items remain deferred or covered only partially, but the
> operator has explicitly accepted those gaps with written reasoning.
>
> **RED** — uncovered, visibility-only, or deferred promoted items remain without explicit
> acceptance, or the exploration/spec/execution chain is inconsistent.

Additional rule:

> A promoted TC deferred during or after execution cannot end in `GREEN` unless the spec and
> coverage plan are revised, re-reviewed, and explicitly re-baselined before Gate 4.

Why: this prevents "justified gap" from collapsing into "green coverage."

## 4. Separate New-Test Signoff From Baseline Stabilization

Add this execution sequence to both workflow docs and both `add-*-tests` skills:

> **Execution order for brownfield suites:**
> 1. Run the newly added or changed tests in isolation until they are stable.
> 2. Run the relevant feature suite or file.
> 3. Run broader regression only after the new coverage is green in isolation.
>
> If unrelated pre-existing tests fail, classify them separately as baseline instability. Do not let
> unrelated failures silently merge into the new coverage verdict.

Add a companion rule:

> If a pre-existing test blocks signoff for the new work because of shared-state leakage or broken
> shared infrastructure, fix that explicitly as baseline stabilization and report it separately from
> the new TC implementation set.

Why: the transcript showed useful opportunistic fixes, but the reporting and gate logic did not
keep them separate.

## 5. Strengthen Re-Exploration Triggers

Add these triggers to `fix-flaky-tests`, `capture-feature-evidence`, and the workflows:

> **Mandatory re-exploration triggers:**
> - execution viewport differs materially from the explored viewport and the interaction is
>   coordinate- or layout-sensitive
> - selector uniqueness observed during exploration no longer holds
> - control text/labels are absent, duplicated, or rendered outside the explored container
> - the run is considering coordinate clicks, force-clicks, JavaScript-dispatched clicks, or
>   text-count oracles because semantic selection failed
>
> In these cases, stop guessing and refresh evidence with browser access before continuing.

Why: these were the exact signals that should have sent the run back to exploration.

## 6. Reclassify Workaround Severity

Update `review-test-code` and `fix-flaky-tests` to treat the following as default `BLOCKER` or
`WARNING` conditions unless backed by explicit evidence:

- coordinate click based on guessed bounding boxes
- force click / `force=True`
- JavaScript-dispatched click
- page-wide text-count oracle used as a functional signal
- broad CSS selectors adopted because semantic ones failed

Recommended wording:

> These are evidence-sensitive workarounds, not normal locator strategies. They require one of:
> - a fresh browser verification note in the exploration artifact
> - a documented platform limitation
> - explicit reviewer acceptance with rationale

Why: the current skills mention some of these as anti-patterns, but not strongly enough to force a
workflow decision.

## 7. Add Viewport And Locator Constraints To Exploration Artifacts

Extend `capture-feature-evidence` output requirements with:

> **Execution-relevant environment**
> - viewport size used during exploration
> - whether the surface is responsive / layout-sensitive
> - any controls that only appear, move, or change labels across breakpoints
> - any elements whose selector viability depends on hover, canvas coordinates, overlays, or
>   appended-icon DOM structures

And in the element inventory, add a field:

> `selector-confidence`: high | medium | low

And for low-confidence controls:

> `re-explore-before-automation`: yes | no

Why: the transcript exposed that exploration knew less than execution needed, especially for the
page kebab, toggle label, and clear icon.

## 8. Require A Run Ledger During Gate 3

Add to both workflows and both `add-*-tests` skills:

> Maintain a Gate 3 run ledger in the session tracker or final execution notes. For each counted
> run record:
> - exact command
> - exact test set / include filter
> - whether this run is eligible for signoff
> - files changed since the prior run
> - pass/fail counts
> - whether the consecutive-green counter resets

Why: it prevents ambiguous signoff stories and forces the agent to be honest about resets.

## 9. Tighten Final Reporting

Add a final reporting checklist to both `add-*-tests` skills:

> Final summary must explicitly separate:
> - new tests added or changed
> - pre-existing tests repaired
> - tests deferred
> - files modified in this run
> - which runs counted toward signoff
> - Gate 4 verdict and why
>
> Do not claim `GREEN`, "all accounted for", or "no files modified" unless the artifact chain and
> git/worktree state support those statements.

Why: this directly addresses the inconsistent final summary from the transcript.

## Recommended File-Level Changes

### `workflows/playwright-automation/workflow.md`

Add:

- Gate reset rule
- execution-time deferral policy
- brownfield execution order
- mandatory re-exploration triggers
- stricter Gate 4 verdict language
- Gate 3 run ledger requirement

### `workflows/robot-automation/workflow.md`

Add the same changes as Playwright.

### `plugins/playwright-automation/skills/add-playwright-tests/SKILL.md`

Add:

- "isolate new tests first, then run broader suite"
- "scope change resets earlier gates"
- final-report checklist

### `plugins/robot-automation/skills/add-robot-tests/SKILL.md`

Add the same changes as Playwright.

### `plugins/playwright-automation/skills/fix-flaky-tests/SKILL.md`

Add:

- mandatory re-exploration triggers
- distinction between flakiness and missing evidence
- warning against workaround escalation without browser confirmation

### `plugins/robot-automation/skills/fix-flaky-tests/SKILL.md`

Add the same changes as Playwright.

### `plugins/*/skills/review-test-code/SKILL.md`

Strengthen severity rules for:

- `force` / `force=True`
- coordinate clicks
- JS click dispatch
- weak text oracles
- broad fallback selectors used due to failed semantic selection

### `plugins/app-exploration/skills/capture-feature-evidence/SKILL.md`

Add:

- viewport and layout notes
- selector-confidence field
- `re-explore-before-automation` flag
- explicit note that exploration must capture DOM/viewport blockers needed for automation, not just
  feature behavior

### `plugins/test-analysis/skills/review-test-cases/SKILL.md`

Add:

- note that promoted TC coverage deferred later during execution must return through spec review if
  the spec changed materially

### `plugins/test-analysis/skills/plan-test-coverage/SKILL.md`

Add:

- a "candidate for execution-time fragility" note for controls that rely on canvas coordinates,
  hover-only affordances, responsive labels, or unstable DOM append slots

## Recommended Rollout Order

1. Patch both workflow docs first.
2. Patch both execution entry skills (`add-*`).
3. Patch both `fix-flaky-tests` skills.
4. Patch `review-test-code`.
5. Patch `capture-feature-evidence`.
6. Patch shared planning/spec-review skills.

This order gives immediate protection at the orchestration layer even before every deeper skill is
updated.

## Success Criteria For The Next Similar Run

The changes worked if a future run does all of the following:

- refuses to keep counting Gate 3 runs after removing or deferring planned TCs
- bounces back to exploration when viewport/selector evidence is stale
- reports pre-existing suite repairs separately from new coverage work
- does not grant `GREEN` when promoted coverage remains deferred without explicit acceptance
- produces a final summary whose counts and modified-file claims match the actual run
