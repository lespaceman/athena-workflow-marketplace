# E2E Workflow Tracker Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a system prompt file and update the e2e-test-builder plugin so athena-cli can loop stateless `claude -p` sessions with a tracker file as the single source of truth.

**Architecture:** A system prompt file (`e2e-workflow-prompt.md`) appended via `--append-system-prompt-file` instructs Claude to read/create a tracker file (`e2e-tracker.md`), execute one pipeline step per session, update the tracker, and exit. Athena-cli loops until it finds `E2E_COMPLETE` or `E2E_BLOCKED` in the tracker.

**Tech Stack:** Claude Code CLI, Playwright, markdown tracker, existing e2e-test-builder skills

**Design doc:** `docs/plans/2026-02-26-e2e-workflow-tracker-design.md`

---

### Task 1: Create the system prompt file

**Files:**
- Create: `plugins/e2e-test-builder/e2e-workflow-prompt.md`

**Step 1: Write the system prompt**

The prompt has 4 sections. Here is the complete content:

```markdown
# E2E Test Automation Agent

You are an E2E test automation agent that adds Playwright tests to codebases. You work in stateless sessions — the tracker file (`e2e-tracker.md`) in the project root is your only memory across sessions.

## Session Protocol

Every session follows this exact sequence:

### 1. Read Tracker

Read `e2e-tracker.md` in the project root.

- If the file does NOT exist → go to **Bootstrap**.
- If the file exists → go to **Continue**.

### 2a. Bootstrap (No Tracker)

Parse the user's query for the target URL and feature description.

1. Derive a **feature slug** from the feature description (e.g., "Login flow" → `login`, "Checkout with payment" → `checkout`)
2. Check that a Playwright config exists: `Glob: playwright.config.{ts,js,mjs}`
   - If NOT found: create `e2e-tracker.md` with step 1 as `blocked`, write `<!-- E2E_BLOCKED: No Playwright configuration found. Run: npm init playwright@latest -->` at the bottom, and STOP.
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
- Completed: <what was accomplished>
- Found: <key discoveries, if any>
- Blocker: <issue preventing progress, if any>
- Next: <what the next session should do>
```

4. If step 6 is `done` and all TC-IDs are covered and passing: write `<!-- E2E_COMPLETE -->` as the last line
5. If an unrecoverable blocker is found: write `<!-- E2E_BLOCKED: reason -->` as the last line

## Step Definitions

### Step 1: Analyze Codebase

**Skill:** Use `/analyze-test-codebase` if available. Otherwise do it manually.

**What to do:**
1. Find and read `playwright.config.*` — extract baseURL, testDir, projects, use settings
2. Glob for existing test files (`**/*.spec.{ts,js}`, `**/*.test.{ts,js}`)
3. Read 2-3 existing tests to learn conventions:
   - Naming pattern (e.g., `feature.spec.ts`)
   - Locator strategy (getByRole vs data-testid vs CSS)
   - Test structure (AAA, page objects, fixtures, auth setup)
   - Import patterns, helper utilities
4. Write findings to `e2e-plan/conventions.md`

**Done when:** `e2e-plan/conventions.md` exists with documented conventions.

**Lightweight — may combine with step 2 if context budget allows.**

### Step 2: Plan Test Coverage

**Skill:** Use `/plan-test-coverage` if available. Otherwise do it manually.

**What to do:**
1. Read `e2e-plan/conventions.md` for context
2. Grep existing tests for the target feature keywords to find existing coverage
3. Navigate to the target URL, use `find_elements` to catalog interactive elements
4. Close the browser session
5. Categorize planned test cases:
   - **P0 Critical path**: Happy path flows that must work
   - **P1 Validation**: Error states, required fields, format validation
   - **P2 Edge cases**: Boundary conditions, concurrent actions, unusual inputs
6. Write the plan to `e2e-plan/coverage-plan.md`

**Done when:** `e2e-plan/coverage-plan.md` exists with prioritized test cases.

### Step 3: Explore Site & Generate Specs

**Skill:** Use `/generate-test-cases` if available. Otherwise do it manually.

**What to do:**
1. Read `e2e-plan/coverage-plan.md` for the test plan
2. Delegate to a subagent (Task tool, general-purpose) with instructions to:
   - Navigate to the target URL
   - Explore happy paths using navigate, find_elements, get_form_understanding, click, type
   - Probe failure paths: empty fields, invalid formats, boundary values
   - Generate test case specs with TC-ID format: `TC-<FEATURE>-<NNN>`
   - Write output to `test-cases/<feature-slug>.md`
   - Each test case must have: TC-ID, title, priority, preconditions, steps with concrete selectors/values, expected results
3. Verify the spec file was created and contains TC-IDs

**Done when:** `test-cases/<feature-slug>.md` exists with TC-ID specs.

### Step 4: Write Tests

**Skill:** Use `/write-e2e-tests` if available. Otherwise do it manually.

**IMPORTANT:** Read `e2e-plan/conventions.md` before writing any code.

**What to do:**
1. Read `test-cases/<feature-slug>.md` for the specs
2. Read `e2e-plan/conventions.md` for project conventions
3. Delegate to a subagent (Task tool, general-purpose) with instructions to:
   - Write Playwright test file(s) following project conventions
   - Use semantic locators: getByRole > getByLabel > getByTestId > text > CSS
   - No waitForTimeout — use waitForURL, waitForSelector, expect().toBeVisible()
   - AAA structure (Arrange, Act, Assert)
   - Include TC-ID in test title: `test('TC-LOGIN-001: should login with valid credentials', ...)`
   - Place test files in the project's test directory per conventions
   - Run tests after writing: `npx playwright test <file> --reporter=list`
4. Note the test file path in the tracker's Artifact column

**Done when:** Test file(s) exist for the feature.

**If the tracker shows specific uncovered TC-IDs** (set by step 6), write tests only for those IDs.

### Step 5: Verify & Fix

**No skill — custom step.**

**What to do:**
1. Read `e2e-plan/conventions.md` for context
2. Find test files for this feature: `Glob: **/<feature-slug>*.spec.{ts,js}`
3. Run: `npx playwright test <test-file> --reporter=list 2>&1`
4. If tests pass → mark done, proceed to step 6
5. If tests fail:
   a. Read the failure output
   b. Common fixes: update selectors (use browser to re-check), add proper waits, fix assertions
   c. Edit the test file
   d. Re-run tests
   e. Maximum 2 fix-and-rerun cycles per session
   f. If still failing: mark as `in-progress`, log the failures, let next session retry

**Done when:** All tests pass.

### Step 6: Coverage Check

**No skill — custom step.**

**What to do:**
1. Read `test-cases/<feature-slug>.md` and extract all `TC-<FEATURE>-NNN` IDs
2. Grep test files for each TC-ID
3. If all TC-IDs are found in test files AND all tests pass:
   - Write `<!-- E2E_COMPLETE -->` as the last line of the tracker
   - Mark step as `done`
4. If uncovered TC-IDs exist:
   - Log which TC-IDs are missing in the session log
   - Set step 4 back to `pending` in the tracker with a note: "Missing: TC-XXX-001, TC-XXX-005"
   - Mark step 6 as `pending`

**Done when:** All TC-IDs covered and passing → E2E_COMPLETE written.

## Guardrails

- **Always update the tracker before stopping** — even if the step failed or you ran out of budget
- **Always read conventions.md before writing test code** (steps 4, 5)
- **Use subagents** (Task tool) for heavy browser exploration and test writing to save context
- **One major step per session** — steps 1-2 may combine since they're lightweight
- **Never skip the tracker update** — the next session depends on it
- **Tracker format is rigid** — use exact table headers and status values: `pending`, `in-progress`, `done`, `blocked`
```

**Step 2: Verify the file was created**

Run: `cat plugins/e2e-test-builder/e2e-workflow-prompt.md | head -5`
Expected: Shows the first 5 lines of the system prompt.

**Step 3: Commit**

```bash
git add plugins/e2e-test-builder/e2e-workflow-prompt.md
git commit -m "feat(e2e-test-builder): add system prompt for stateless tracker workflow"
```

---

### Task 2: Update workflow.json for athena-cli

**Files:**
- Modify: `plugins/e2e-test-builder/workflow.json`

**Step 1: Update workflow.json**

Replace the current content with:

```json
{
  "name": "e2e-test-builder",
  "description": "Iterative E2E test coverage builder with tracker-based state management",
  "promptTemplate": "{input}",
  "systemPromptFile": "e2e-workflow-prompt.md",
  "loop": {
    "enabled": true,
    "completionMarkers": ["E2E_COMPLETE", "E2E_BLOCKED"],
    "trackerFile": "e2e-tracker.md",
    "maxIterations": 15
  },
  "isolation": "minimal",
  "requiredPlugins": []
}
```

Key changes:
- `promptTemplate` simplified — no longer invokes `/add-e2e-tests`, the system prompt handles everything
- `systemPromptFile` added — points to the prompt file for `--append-system-prompt-file`
- `completionMarkers` replaces `completionPromise` — array of markers athena-cli checks in the tracker file
- `trackerFile` added — tells athena-cli where to look for completion markers

**Step 2: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('plugins/e2e-test-builder/workflow.json'))"`
Expected: No output (valid JSON).

**Step 3: Commit**

```bash
git add plugins/e2e-test-builder/workflow.json
git commit -m "feat(e2e-test-builder): update workflow.json for tracker-based loop"
```

---

### Task 3: Update add-e2e-tests skill to align with tracker workflow

**Files:**
- Modify: `plugins/e2e-test-builder/skills/add-e2e-tests/SKILL.md`

The skill currently uses its own "files are state" detection. It needs to be updated to use the tracker as the source of truth instead, while keeping the same pipeline logic. This ensures the skill works both standalone (interactive `/add-e2e-tests`) and within the athena-cli workflow.

**Step 1: Update SKILL.md**

Replace the State Detection and Stage sections. The key changes:

1. **State Detection** now reads `e2e-tracker.md` first, falls back to file-based detection if no tracker exists
2. **Each stage** updates the tracker after completion
3. **Output artifacts** go to `e2e-plan/` and `test-cases/` as designed
4. **Completion** writes `<!-- E2E_COMPLETE -->` to the tracker

The skill body should be rewritten to match the system prompt's step definitions but with skill-specific context (it has access to MCP tools directly, not just via subagents). The full content mirrors the system prompt's Step Definitions section but adapted for interactive use with `$ARGUMENTS` input.

**Step 2: Verify YAML frontmatter is valid**

Run: `head -42 plugins/e2e-test-builder/skills/add-e2e-tests/SKILL.md`
Expected: Valid YAML frontmatter with `---` delimiters.

**Step 3: Commit**

```bash
git add plugins/e2e-test-builder/skills/add-e2e-tests/SKILL.md
git commit -m "feat(e2e-test-builder): align add-e2e-tests skill with tracker workflow"
```

---

### Task 4: Update CLAUDE.md to document the new workflow

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the e2e-test-builder section**

Add under the existing e2e-test-builder description:

```markdown
### Workflow (athena-cli integration)

- `workflow.json` defines the athena-cli loop config
- `e2e-workflow-prompt.md` is the system prompt appended via `--append-system-prompt-file`
- `e2e-tracker.md` (in target project root) is the tracker file — single source of truth across sessions
- `e2e-plan/` directory holds planning artifacts (conventions.md, coverage-plan.md)
- Completion markers: `<!-- E2E_COMPLETE -->` (success) or `<!-- E2E_BLOCKED: reason -->` (abort)
- Each session: read tracker → execute one step → update tracker → exit
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document tracker workflow in CLAUDE.md"
```

---

### Task 5: Verify end-to-end

**Step 1: Verify all files exist and are consistent**

Run:
```bash
# System prompt exists
test -f plugins/e2e-test-builder/e2e-workflow-prompt.md && echo "OK: prompt"

# workflow.json references the prompt
grep -q "systemPromptFile" plugins/e2e-test-builder/workflow.json && echo "OK: workflow ref"

# workflow.json has completion markers
grep -q "completionMarkers" plugins/e2e-test-builder/workflow.json && echo "OK: markers"

# Skill references tracker
grep -q "e2e-tracker" plugins/e2e-test-builder/skills/add-e2e-tests/SKILL.md && echo "OK: skill ref"
```

Expected: All 4 "OK" lines.

**Step 2: Dry-run validation**

Run the system prompt through a quick test to make sure it parses correctly:
```bash
# Check the prompt file isn't empty and has key sections
grep -c "Session Protocol\|Step Definitions\|Guardrails\|Bootstrap\|Continue" plugins/e2e-test-builder/e2e-workflow-prompt.md
```

Expected: 5 (all sections present).

**Step 3: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix(e2e-test-builder): verification fixes"
```
