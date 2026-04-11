# E2E Test Builder Audit

Date: 2026-04-10
Scope: `plugins/e2e-test-builder/`, `workflows/e2e-test-builder/`, marketplace metadata, packaging/docs references
Purpose: Consolidate all issues and gaps found during this review session and propose the best fix for each.

## Executive Summary

The `e2e-test-builder` plugin is structurally strong: the plugin manifest, workflow, and skill set all point toward the same high-level user outcome, and the workflow sequence is well thought out. The main risks are not missing architecture, but drift:

- drift between skills
- drift between the workflow and public docs
- drift between source conventions and packaging conventions
- lack of automated checks to catch future drift

The highest-value fixes are:

1. Normalize shared conventions across all skills, especially TC-ID formatting and waiting guidance.
2. Relax over-prescriptive review/spec rules so they apply only when relevant to the feature under test.
3. Keep Athena-facing docs and marketplace docs aligned on the workflow's full skill inventory and execution rules.
4. Add lightweight validation so these issues are caught automatically.

## Athena CLI Reassessment

After the initial audit, the Athena CLI implementation was reviewed to verify what the runtime actually owns versus what the marketplace package must describe.

What Athena CLI clearly owns:

- stateless session protocol and tracker lifecycle
- completion and blocked markers
- loop control and max-iteration enforcement
- task-list projection into harness-specific task tools
- workflow plugin installation into Claude/Codex harness layouts

Relevant Athena evidence:

- `~/athena/cli/src/core/workflows/stateMachine.ts`
- `~/athena/cli/src/core/workflows/loopManager.ts`
- `~/athena/cli/src/core/workflows/installer.ts`
- `~/athena/cli/src/infra/plugins/loader.ts`
- `~/athena/cli/src/infra/plugins/marketplace.ts`
- `~/athena/cli/qa/qa-results.md`

Corrections to the initial assessment:

- The manifest-directory drift finding was overstated. This repository does contain `.claude-plugin/` and `.codex-plugin/` in `plugins/e2e-test-builder/`, which matches Athena CLI expectations.
- Findings about missing tracker/state-machine guidance should not be treated as plugin defects, because Athena CLI injects the canonical state-machine protocol at runtime.
- The `workflow.json` description finding should be treated as a documentation polish item, not a functional workflow inconsistency. Athena executes the workflow from `workflow.md` plus the runtime state-machine layer, not from the short description text.

Findings that remain valid after Athena review:

- TC-ID convention drift across skills
- over-rigid mandatory scenario rules in spec generation/review
- `networkidle` guidance conflict in flaky-test repair
- over-broad completeness rule in `review-test-cases`
- README under-documenting the actual skill inventory and workflow gates
- lack of automated consistency validation for this documentation-driven plugin
- lack of packaging smoke tests / artifact validation
- absence of a concise maintainer-oriented contract doc

## Findings

### 1. TC-ID convention is inconsistent across skills

Priority: P1

Problem:
- `plan-test-coverage` uses category-specific IDs like `TC-FEATURE-A01` and `TC-FEATURE-V01`.
- `generate-test-cases`, `write-test-code`, and `review-test-code` all require `TC-<FEATURE>-<NNN>`.

Why it matters:
- breaks traceability from plan -> spec -> code -> review
- can cause downstream skills to classify planned IDs as invalid or orphaned
- creates ambiguity for users and agents about the canonical format

Evidence:
- `plugins/e2e-test-builder/skills/plan-test-coverage/SKILL.md`
- `plugins/e2e-test-builder/skills/generate-test-cases/SKILL.md`
- `plugins/e2e-test-builder/skills/write-test-code/SKILL.md`
- `plugins/e2e-test-builder/skills/review-test-code/SKILL.md`

Best fix:
- Adopt a single TC-ID convention for the whole plugin: `TC-<FEATURE>-<NNN>`.
- Update `plan-test-coverage` examples so accessibility, visual, and other categories remain normal plan sections but reuse the same numeric ID format.
- Add one canonical statement of the TC-ID contract to:
  - `add-e2e-tests`
  - `plan-test-coverage`
  - `generate-test-cases`
  - `review-test-cases`
  - `write-test-code`
  - `review-test-code`

Recommended wording:
- "All test cases use `TC-<FEATURE>-<NNN>` regardless of category. Category is expressed in the plan/spec metadata, not the ID format."

### 2. Spec generation and review are too rigid about mandatory scenarios

Priority: P1

Problem:
- `generate-test-cases` requires every feature spec to include a network error scenario, empty state scenario, and session/auth edge case where applicable.
- `review-test-cases` treats missing server error, network failure, empty state, and sometimes session expiry as blockers.
- This is too rigid for features that do not naturally have those states.

Why it matters:
- encourages invented scenarios instead of evidence-based specs
- conflicts with the plugin's own "invented vs observed" quality standard
- produces bloated specs for simple or static flows

Evidence:
- `plugins/e2e-test-builder/skills/generate-test-cases/SKILL.md`
- `plugins/e2e-test-builder/skills/review-test-cases/SKILL.md`

Best fix:
- Change "mandatory for every feature" to "mandatory when applicable to the feature's real behavior or architecture".
- Introduce explicit applicability rules:
  - empty state required only when the feature renders a list, result set, inbox, dashboard, or other collection/data-dependent UI
  - network/server failure scenarios required only when the feature depends on backend data submission or retrieval that can be meaningfully simulated or observed
  - session/auth scenarios required only when auth gates the feature or session state materially affects the flow
- Update the review checklist so absence of a non-applicable category is not a blocker if the spec explains why it is out of scope.

Recommended wording:
- "Include these scenarios when the feature meaningfully supports them. If not applicable, state that explicitly in the spec rather than inventing coverage."

### 3. `fix-flaky-tests` conflicts with the plugin's broader anti-`networkidle` guidance

Priority: P1

Problem:
- `fix-flaky-tests` suggests checking whether `networkidle` or `load` would help for navigation timing.
- `write-test-code` and `review-test-code` both frame `networkidle` as a fragile anti-pattern except in narrow cases.

Why it matters:
- flaky-test repair is a high-risk moment for bad advice
- agents are likely to reach for `networkidle` as a generic fix if the skill mentions it
- inconsistent guidance reduces trust in the workflow

Evidence:
- `plugins/e2e-test-builder/skills/fix-flaky-tests/SKILL.md`
- `plugins/e2e-test-builder/skills/write-test-code/SKILL.md`
- `plugins/e2e-test-builder/skills/review-test-code/SKILL.md`
- `plugins/e2e-test-builder/skills/write-test-code/references/anti-patterns.md`

Best fix:
- Remove `networkidle` from generic diagnostic guidance in `fix-flaky-tests`.
- Replace it with:
  - targeted `waitForResponse`
  - URL/state assertions
  - waiting for a specific loading indicator to disappear
  - waiting for hydration markers or specific UI readiness conditions
- If `networkidle` remains mentioned at all, constrain it to a narrow note:
  - "Only consider for initial page load on apps without long-polling, analytics chatter, or persistent sockets."

### 4. `review-test-cases` overstates coverage completeness by requiring every interactive element to appear in a test

Priority: P2

Problem:
- the review skill says every interactive element on the page should appear in at least one test case

Why it matters:
- encourages UI-surface coverage instead of risk-based coverage
- conflicts with the planning skill's guidance to keep plans focused
- will over-penalize intentionally scoped E2E plans

Evidence:
- `plugins/e2e-test-builder/skills/review-test-cases/SKILL.md`
- `plugins/e2e-test-builder/skills/plan-test-coverage/SKILL.md`

Best fix:
- replace the requirement with a risk-based rule:
  - all user-critical actions and state-changing interactions should be covered
  - secondary controls should be covered only when material to the feature, risky, or historically brittle
- update the review wording to flag missing high-value interactions rather than all interactive elements

Recommended wording:
- "Every critical user action in scope should appear in at least one test case. Ancillary controls may be omitted when they do not materially affect the target journey."

### 5. README under-documents the actual `e2e-test-builder` workflow

Priority: P1

Problem:
- the README lists only part of the skill inventory for `e2e-test-builder`
- it omits:
  - `review-test-cases`
  - `review-test-code`
  - `fix-flaky-tests`
- it also does not explain that the workflow has mandatory review gates and non-delegable test execution

Why it matters:
- users and contributors get an incomplete model of how the plugin is intended to work
- makes the workflow look optional/linear instead of gated
- increases misuse by anyone reading README before the workflow doc

Evidence:
- `README.md`
- `workflows/e2e-test-builder/workflow.md`

Best fix:
- expand the README section for `e2e-test-builder` to include the full skill set
- add a short workflow summary paragraph covering:
  - required sequence
  - mandatory review gates
  - test execution must happen in the main agent
  - browser exploration is required when real product evidence is needed

Recommended structure:
- one table with all skills
- one "Workflow Rules" subsection with 4-6 bullets

### 6. `workflow.json` summary does not fully reflect the actual workflow contract

Priority: P3

Problem:
- the workflow manifest description mentions analysis, exploration, planning, spec generation, writing, and stabilization
- it does not mention the mandatory review gates or the non-delegable execution rule that the workflow markdown treats as core behavior

Why it matters:
- short manifest descriptions are often what registry UIs and humans read first
- this increases the chance of partial or incorrect mental models
- Athena CLI does not rely on this text for actual loop behavior, so this is a documentation polish issue rather than a runtime defect

Evidence:
- `workflows/e2e-test-builder/workflow.json`
- `workflows/e2e-test-builder/workflow.md`

Best fix:
- update the `workflow.json` description to mention:
  - reviewed specs
  - reviewed code
  - direct test execution
- optionally update example prompts to better reflect end-to-end gated execution

Recommended description:
- "Adds Playwright E2E tests end to end: analyze setup, explore the live product, plan coverage, generate and review specs, write and review tests, then execute and stabilize them across multiple sessions."

### 7. There is no automated consistency validation for the `e2e-test-builder` skill/workflow contract

Priority: P1

Problem:
- there is a manual skill validator, but no automated repo validation for:
  - shared TC-ID convention
  - complete skill inventory in README
  - workflow/README consistency
  - source manifest path consistency
  - contradictory guidance across skills

Why it matters:
- this plugin is documentation-driven
- its product behavior lives in authored text, not only in executable code
- without checks, contradiction is easy and regression is likely

Evidence:
- `scripts/quick-validate-skill.sh`
- absence of repo tests/validation targeting `e2e-test-builder`

Best fix:
- add a lightweight validation script, for example `scripts/validate-e2e-test-builder.mjs`, that checks:
  - every expected skill directory exists
  - README skill table includes the full inventory
  - all TC-ID references match the canonical regex
  - `workflow.md` mandatory gates are represented in README summary text
  - manifest files exist in expected locations
  - no banned contradictory phrases remain, such as generic `networkidle` repair guidance
- run this script in CI on changes under:
- `plugins/e2e-test-builder/**`
- `workflows/e2e-test-builder/**`
- `README.md`
- packaging scripts

### 8. There are no dedicated tests or fixture-based checks for generated `dist/` artifacts

Priority: P2

Problem:
- release artifacts exist under `plugins/e2e-test-builder/dist/`
- there is no visible test coverage asserting that packaged artifacts contain the expected files and metadata

Why it matters:
- artifact generation is a core delivery path
- packaging regressions may not be caught until publish/install time

Evidence:
- `plugins/e2e-test-builder/dist/`
- `scripts/build-plugin-artifacts.mjs`

Best fix:
- add a packaging smoke test that:
  - builds artifacts for `e2e-test-builder`
  - asserts expected files exist in the versioned output
  - verifies packaged plugin manifests match source name/version/description
  - optionally checks that packaged skills and references are present

Suggested test targets:
- `dist/<version>/release.json`
- `dist/<version>/claude/plugin/...`
- `dist/<version>/codex/plugin/...`
- `dist/<version>/.agents/plugins/marketplace.json`

### 9. There is no concise contributor-facing reference for the canonical `e2e-test-builder` contract

Priority: P2

Problem:
- the rules are spread across multiple skills and the workflow doc
- contributors editing one file can easily miss a related contract elsewhere

Why it matters:
- increases maintenance cost
- makes future skill additions more error-prone
- contributes directly to the drift already observed

Best fix:
- add a short contributor-oriented reference doc, for example:
  - `docs/e2e-test-builder-maintainer-guide.md`
- include:
  - canonical workflow sequence
  - mandatory gates
  - TC-ID contract
  - applicability rules for optional scenarios
  - delegation rules
  - packaging/manifest expectations
  - validation commands to run before merging

## Recommended Remediation Plan

### Phase 1: Correct the source-of-truth content

1. Normalize TC-ID format across all skills.
2. Relax and clarify applicability rules for network/empty/auth scenarios.
3. Remove or heavily constrain `networkidle` guidance in flaky-test docs.
4. Change the review-test-cases completeness rule from "all interactive elements" to "all critical interactions in scope".

### Phase 2: Align workflow, docs, and packaging

1. Expand README to document the full skill inventory and workflow rules.
2. Update `workflow.json` description to reflect actual gates and execution rules.
3. Add a maintainer guide for `e2e-test-builder`.
4. Keep packaging docs aligned with Athena CLI expectations, but do not treat the runtime-owned state-machine protocol as a plugin-doc obligation.

### Phase 3: Add automated protection

1. Add `scripts/validate-e2e-test-builder.mjs`.
2. Add a packaging smoke test for `scripts/build-plugin-artifacts.mjs`.
3. Run validation in CI for changes touching `e2e-test-builder`, its workflow, or shared packaging/docs files.

## Proposed Validation Checklist

Before shipping future `e2e-test-builder` changes, validate:

- TC-ID format is identical in planning, spec, writing, and review skills
- workflow sequence matches README summary
- review gates are documented in both workflow and README
- test execution is still explicitly non-delegable
- browser exploration requirements are consistently stated
- packaged artifacts contain expected manifests and metadata

## Suggested Follow-Up Work Items

1. Patch the authored skill files to resolve the four content-level contradictions.
2. Patch `README.md` and `workflows/e2e-test-builder/workflow.json` for public-facing consistency.
3. Add automated validation and packaging smoke tests.

## Files Most Likely To Change

- `plugins/e2e-test-builder/skills/plan-test-coverage/SKILL.md`
- `plugins/e2e-test-builder/skills/generate-test-cases/SKILL.md`
- `plugins/e2e-test-builder/skills/review-test-cases/SKILL.md`
- `plugins/e2e-test-builder/skills/fix-flaky-tests/SKILL.md`
- `README.md`
- `workflows/e2e-test-builder/workflow.json`
- `scripts/quick-validate-skill.sh`
- new validation/test files under `scripts/` and/or a repo test directory

## Notes

- This audit focused on authored content and packaging/documentation consistency, not on changing runtime behavior in an external consumer.
- No fixes are implemented by this document itself; it is intended to serve as the remediation backlog and decision record.
