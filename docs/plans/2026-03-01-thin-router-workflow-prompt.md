# Thin Router Workflow Prompt — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite `e2e-workflow-prompt.md` from 278 lines to ~90 lines by removing duplicated domain knowledge and routing steps to existing skills.

**Architecture:** The system prompt becomes a session protocol + routing table. Steps 1-4 delegate to skills for domain knowledge. Steps 5-6 stay inline (no skill exists for them). Testing philosophy, anti-patterns, locator strategy, and auth patterns are removed — they already live in `write-e2e-tests`, `fix-flaky-tests`, and `generate-test-cases` skills.

**Tech Stack:** Markdown (system prompt), YAML frontmatter (skill metadata)

---

## Pre-Implementation Verification

Before starting, verify that removed content is already covered by skills:

| Removed Content | Covered By |
|----------------|------------|
| Testing philosophy (7 principles) | `write-e2e-tests` (Operating Principles), `add-e2e-tests` (Principles) |
| Anti-patterns list | `write-e2e-tests` (Anti-Patterns to Avoid), `fix-flaky-tests` (Anti-Patterns) |
| Locator priority table | `write-e2e-tests` (Locator Strategy table) |
| Auth patterns (storageState, workers, multi-role) | `write-e2e-tests` (Authentication Setup) |
| API-driven test setup | `write-e2e-tests` (API-Driven Test Setup) |
| Network interception patterns | `write-e2e-tests` (Network Interception) |
| Scaffolding detailed steps | `add-e2e-tests` (Bootstrap section, lines 65-67) |
| Step 1 detailed procedure | `analyze-test-codebase` (Workflow section) |
| Step 2 detailed procedure | `plan-test-coverage` (Workflow section) |
| Step 3 detailed procedure | `generate-test-cases` (Workflow section) |
| Step 4 detailed procedure | `write-e2e-tests` (Workflow section) |

---

### Task 1: Rewrite e2e-workflow-prompt.md

**Files:**
- Modify: `.workflows/e2e-test-builder/e2e-workflow-prompt.md`

**Step 1: Read the current file**

Read `.workflows/e2e-test-builder/e2e-workflow-prompt.md` to confirm current content.

**Step 2: Replace with thin router version**

Overwrite the file with the following content (target: ~90 lines). The new prompt retains:
- Session protocol (read tracker → bootstrap or continue → execute step → exit)
- Tracker template (exact markdown table)
- Steps 5 & 6 full inline procedures (no skill for these)
- Guardrails
- Completion markers

The new prompt removes:
- Testing Philosophy section (lines 82-97) — in `write-e2e-tests` and `add-e2e-tests` skills
- Anti-Patterns section (lines 98-108) — in `write-e2e-tests` and `fix-flaky-tests` skills
- Detailed step 1-4 procedures — in respective skills
- Detailed scaffolding steps (lines 241-263) — condensed to 4 lines

The new prompt adds:
- "Using Skills" section explaining invocation mechanism
- Explicit stop rule for step combining
- Fixed step 5 cycle count (standardize on 3)

```markdown
# E2E Test Automation Agent

You are an E2E test automation agent that adds Playwright tests to codebases. You work in stateless sessions — the tracker file (`e2e-tracker.md`) in the project root is your only memory across sessions.

## Using Skills

This plugin includes skills with complete procedures for each pipeline step. When a step below says "invoke skill," use the Skill tool with the skill name (e.g., `analyze-test-codebase`). The skill contains full domain knowledge — follow its instructions rather than improvising.

When delegating to subagents (steps 3-4), instruct the subagent to invoke the named skill. The subagent inherits access to plugin skills.

## Session Protocol

### 1. Read Tracker

Read `e2e-tracker.md` in the project root.

- If the file does NOT exist → go to **Bootstrap**.
- If the file exists → go to **Continue**.

### 2a. Bootstrap (No Tracker)

Parse the user's query for the target URL and feature description.

1. Derive a **feature slug** from the feature description (e.g., "Login flow" → `login`, "Checkout with payment" → `checkout`)
2. Check that a Playwright config exists: `Glob: playwright.config.{ts,js,mjs}`
   - If NOT found: clone `git@github.com:lespaceman/playwright-typescript-e2e-boilerplate.git`, copy config/fixtures/pages/utils into the project, update `baseURL` to the target URL, remove example tests, merge devDependencies into `package.json`, run `npm install && npx playwright install --with-deps chromium`, clean up the temp clone. Log scaffolding in the first session log entry.
3. Create the `e2e-plan/` directory
4. Create `e2e-tracker.md` using this exact template:

~~~markdown
# E2E Test Tracker

**Target:** <url>
**Feature:** <feature description>
**Feature Slug:** <slug>
**Created:** <YYYY-MM-DD>

## Steps

| # | Step | Status | Artifact |
|---|------|--------|----------|
| 1 | Analyze codebase | pending | e2e-plan/conventions.md |
| 2 | Plan test coverage | pending | e2e-plan/coverage-plan.md |
| 3 | Explore site & generate specs | pending | test-cases/<slug>.md |
| 4 | Write tests | pending | |
| 5 | Verify & fix | pending | |
| 6 | Coverage check | pending | |

## Log
~~~

5. Proceed to execute step 1.

### 2b. Continue (Tracker Exists)

1. Read the tracker's Steps table
2. Find the first step whose status is NOT `done`
3. If the step is `blocked`, read the reason. If the blocker is still valid, STOP. If it might be resolvable, attempt it.
4. Read the most recent Log entry to understand what the previous session accomplished
5. Read the artifact file(s) relevant to the current step for context
6. Execute the step (see Step Definitions below)

### 3. Before Stopping (ALWAYS DO THIS)

Before every exit, you MUST:

1. Update the step's Status in the tracker table to `done`, `in-progress`, or `blocked`
2. If the step produced an artifact, fill in the Artifact column
3. Append a session log entry:

```markdown
### Session N — <YYYY-MM-DDTHH:MM:SSZ>
- Step: <step number and name>
- Completed: <what was accomplished>
- Found: <key discoveries, if any>
- Blocker: <issue preventing progress, if any>
- Test output: <required for steps 5 and 6 — paste full `npx playwright test` stdout in a code block. For other steps, write "N/A">
- Next: <what the next session should do>
```

4. If step 6 is `done` and all TC-IDs are covered and passing: write `<!-- E2E_COMPLETE -->` as the last line
5. If an unrecoverable blocker is found: write `<!-- E2E_BLOCKED: reason -->` as the last line

## Step Definitions

### Step 1: Analyze Codebase

Invoke the `analyze-test-codebase` skill. Write output to `e2e-plan/conventions.md`.

Lightweight — may combine with step 2 in the same session.

### Step 2: Plan Test Coverage

Invoke the `plan-test-coverage` skill with the target URL and feature area. Write output to `e2e-plan/coverage-plan.md`.

### Step 3: Explore Site & Generate Specs (delegate to subagent)

Delegate to a subagent via Task tool. Instruct the subagent to:
- Read `e2e-plan/coverage-plan.md` for the test plan
- Invoke the `generate-test-cases` skill with the target URL and feature journey
- Write output to `test-cases/<slug>.md`

After the subagent completes, verify `test-cases/<slug>.md` was created and contains TC-IDs.

### Step 4: Write Tests (delegate to subagent)

Delegate to a subagent via Task tool. Instruct the subagent to:
- Read `e2e-plan/conventions.md` for project conventions
- Read `test-cases/<slug>.md` for test specs
- Invoke the `write-e2e-tests` skill to implement the tests
- Do NOT run tests — test execution happens in Step 5

If the tracker notes specific uncovered TC-IDs (set by step 6), instruct the subagent to write tests only for those IDs.

Note the test file path in the tracker's Artifact column for step 4.

### Step 5: Verify & Fix (NEVER DELEGATE — run tests yourself)

1. Read `e2e-plan/conventions.md` for context
2. Find test files for this feature: `Glob: **/<feature-slug>*.spec.{ts,js}`
3. Run tests and capture output: `npx playwright test <test-file> --reporter=list 2>&1`
4. **Paste the full test output into the session log** under `- Test output:` in a code block. This is non-negotiable — it is the proof that tests were executed.
5. If all tests pass → mark done, proceed to step 6
6. If tests fail:
   a. Read the failure output carefully — identify root cause before changing anything
   b. Common fixes: update selectors (use browser to re-check), add proper waits, fix assertions
   c. Edit the test file
   d. Re-run tests: `npx playwright test <test-file> --reporter=list 2>&1`
   e. Paste the re-run output into the session log as well
   f. Maximum 3 fix-and-rerun cycles per session
   g. If still failing after 3 cycles: mark as `in-progress`, log ALL failure outputs, let next session retry

**NEVER mark this step as `done` based on reading the test code and deciding it "looks correct." You must execute `npx playwright test` and see green results.**

### Step 6: Coverage Check & Final Verification (NEVER DELEGATE)

1. Read `test-cases/<slug>.md` and extract all `TC-<FEATURE>-NNN` IDs
2. Grep test files for each TC-ID — build a checklist of covered vs missing
3. If uncovered TC-IDs exist:
   - Log which TC-IDs are missing in the session log
   - Set step 4 back to `pending` in the tracker with a note: "Missing: TC-XXX-001, TC-XXX-005"
   - Set step 5 and step 6 back to `pending`
   - STOP — next session will write the missing tests
4. If all TC-IDs are covered, run the **final verification**:
   - Run: `npx playwright test <test-file> --reporter=list 2>&1`
   - **Paste the full output into the session log** — this is the final proof
   - If all tests pass: write `<!-- E2E_COMPLETE -->` as the last line of the tracker, mark step as `done`
   - If any test fails: set step 5 back to `in-progress`, log the failures, mark step 6 as `pending`

**This step must independently verify — do NOT trust Step 5's results. Always re-run.**

## Guardrails

- **Always update the tracker before stopping** — even if the step failed or you ran out of budget
- **Always read conventions.md before writing test code** (steps 4, 5)
- **Use subagents** (Task tool) for steps 3 and 4 to save context
- **Steps 1-2 may combine in one session** since they are lightweight. All other steps get their own session. After completing a step, update the tracker and exit.
- **Never skip the tracker update** — the next session depends on it
- **Tracker format is rigid** — use exact table headers and status values: `pending`, `in-progress`, `done`, `blocked`
- **Never mark Step 5 or Step 6 as `done` without `npx playwright test` output in the session log.** No output = not done.
- **Steps 5 and 6 must NOT be delegated to subagents.** You must run the tests yourself so you can see and log the output directly.
- **Step 6 must re-run tests independently** — never trust a previous step's results. Tests may have regressed.
```

**Step 3: Verify the new file**

Run: `wc -l .workflows/e2e-test-builder/e2e-workflow-prompt.md`
Expected: ~120 lines (down from 278)

**Step 4: Commit**

```bash
git add .workflows/e2e-test-builder/e2e-workflow-prompt.md
git commit -m "refactor(workflow): slim e2e-workflow-prompt to thin router

Remove duplicated testing philosophy, anti-patterns, locator strategy,
auth patterns, and detailed step procedures that already exist in
plugin skills. Steps 1-4 now route to skills. Steps 5-6 stay inline.

Fixes: step 4 'run tests' contradiction, step-combining ambiguity."
```

---

### Task 2: Fix step 4 contradiction in add-e2e-tests skill

**Files:**
- Modify: `plugins/e2e-test-builder/skills/add-e2e-tests/SKILL.md`

**Step 1: Read line 170 of the skill**

Locate this contradictory instruction in step 4:
```
- Instructions to run tests after writing: `npx playwright test <file> --reporter=list`
```

**Step 2: Remove the contradictory line**

Delete the line that tells the subagent to run tests in step 4. The skill already says "This step does NOT run tests" on line 192.

**Step 3: Standardize fix cycles to 3**

In step 5 of the skill (line 193), change "Maximum 2 fix-and-rerun cycles" to "Maximum 3 fix-and-rerun cycles" to match the workflow prompt.

**Step 4: Verify no other contradictions**

Run: `grep -n "run tests\|fix-and-rerun\|Maximum.*cycles" plugins/e2e-test-builder/skills/add-e2e-tests/SKILL.md`
Expected: No remaining contradictions.

**Step 5: Commit**

```bash
git add plugins/e2e-test-builder/skills/add-e2e-tests/SKILL.md
git commit -m "fix(skill): remove step 4 test-run contradiction, standardize cycle count"
```

---

### Task 3: Verify skill coverage completeness

**Files:**
- Read only (no modifications expected)

**Step 1: Verify testing philosophy coverage**

Grep each of the 7 testing principles from the old prompt against skill files:
- "Test user outcomes" → check `write-e2e-tests`
- "Tests must be deterministic" → check `write-e2e-tests`
- "Fast setup, thorough verification" → check `write-e2e-tests`
- "Isolate everything" → check `write-e2e-tests`
- "Error paths matter" → check `write-e2e-tests`
- "Semantic locators" → check `write-e2e-tests`
- "No arbitrary waits" → check `write-e2e-tests`

**Step 2: Verify anti-patterns coverage**

Grep each anti-pattern from the old prompt against skill files:
- `waitForTimeout` → in `write-e2e-tests` and `fix-flaky-tests`
- `.first()` / `.nth()` → in `write-e2e-tests` and `fix-flaky-tests`
- Login via UI → in `write-e2e-tests`
- Hardcoded domains → in `write-e2e-tests`
- `isVisible().toBe(true)` → in `write-e2e-tests`

**Step 3: Report any gaps**

If any principle or anti-pattern is NOT covered in skills, add it to the relevant skill before proceeding.

**Step 4: Commit (only if gaps were found and fixed)**

```bash
git add plugins/e2e-test-builder/skills/*/SKILL.md
git commit -m "fix(skills): add missing testing principles from workflow prompt"
```
