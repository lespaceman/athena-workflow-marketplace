---
name: add-e2e-tests
description: >
  Use when the user wants the full end-to-end pipeline for adding Playwright tests to an existing codebase.
  Triggers: "add E2E tests for this feature", "add end-to-end tests", "create Playwright tests for my app",
  "set up E2E testing", "I need tests for this feature from scratch", "build test coverage for",
  "full test pipeline for", "analyze my codebase and write tests".
  This skill orchestrates the complete workflow: (1) analyze existing Playwright codebase conventions,
  (2) plan test coverage with priorities, (3) explore the live site to discover all testable paths,
  (4) generate structured test case specs, (5) write executable Playwright tests.
  Uses subagent-driven development — delegates heavy browser exploration and test writing to general-purpose
  subagents via Task tool to save main context.
  Iterative and resumable — detects progress from files and picks up where it left off.
user-invocable: true
argument-hint: <url> <feature to test>
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - mcp__plugin_e2e-test-builder_agent-web-interface__ping
  - mcp__plugin_e2e-test-builder_agent-web-interface__navigate
  - mcp__plugin_e2e-test-builder_agent-web-interface__find_elements
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_element_details
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__click
  - mcp__plugin_e2e-test-builder_agent-web-interface__type
  - mcp__plugin_e2e-test-builder_agent-web-interface__press
  - mcp__plugin_e2e-test-builder_agent-web-interface__select
  - mcp__plugin_e2e-test-builder_agent-web-interface__hover
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_session
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_form_understanding
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_field_context
  - mcp__plugin_e2e-test-builder_agent-web-interface__capture_snapshot
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_back
  - mcp__plugin_e2e-test-builder_agent-web-interface__reload
  - mcp__plugin_e2e-test-builder_agent-web-interface__take_screenshot
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_element_into_view
---

# Add E2E Tests — Tracker-Based Pipeline

You are an E2E test builder that uses `e2e-tracker.md` as the source of truth for progress. In this interactive session, you execute ALL steps in sequence, updating the tracker after each one.

## Input

Parse the target URL and feature description from: $ARGUMENTS

Derive the **feature slug** from the feature description (e.g., "Login flow" → `login`, "Checkout with payment" → `checkout`). Use this slug for file naming throughout.

## State Detection

### Primary: Read Tracker

Check if `e2e-tracker.md` exists in the project root.

- If it EXISTS → read it, find the first step whose status is NOT `done`, and resume from that step.
- If it does NOT exist → go to **Bootstrap**.

### Bootstrap (No Tracker)

1. Check that a Playwright config exists: `Glob: playwright.config.{ts,js,mjs}`
   - If NOT found: scaffold from the boilerplate repo `git@github.com:lespaceman/playwright-typescript-e2e-boilerplate.git` — clone it, copy config/fixtures/pages/utils into the project, update `baseURL` to the target URL, remove example tests, merge devDependencies into package.json, run `npm install` and `npx playwright install --with-deps chromium`, then clean up the temp clone. Log the scaffolding in the first session log entry.
2. Create the `e2e-plan/` directory
3. Create `e2e-tracker.md` using this exact template:

```markdown
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
```

4. Proceed to Step 1.

### Fallback: File-Based Detection

If the tracker exists but is corrupted or unreadable, fall back to checking files directly:
- `e2e-plan/conventions.md` exists → step 1 done
- `e2e-plan/coverage-plan.md` exists → step 2 done
- `test-cases/<feature-slug>.md` exists → step 3 done
- `**/<feature-slug>*.spec.{ts,js}` exists → step 4 done

Recreate the tracker with the correct statuses and continue from the first incomplete step.

---

## Step Definitions

Execute each step in sequence. After completing each step, update the tracker table status to `done` and append a session log entry before moving to the next step.

### Step 1: Analyze Codebase (do directly — lightweight)

1. Find and read `playwright.config.*` — extract `baseURL`, `testDir`, `projects`, `use` settings
2. Glob for existing test files, read 2-3 to understand conventions:
   - Naming pattern (e.g., `feature.spec.ts`)
   - Locator strategy (semantic `getByRole` vs `data-testid` vs CSS)
   - Test structure (AAA, page objects, fixtures, auth setup)
   - Import patterns, helper utilities
3. Write findings to `e2e-plan/conventions.md`
4. Update tracker: set step 1 status to `done`

### Step 2: Plan Test Coverage (do directly with quick browser check)

1. Read `e2e-plan/conventions.md` for context
2. Grep existing tests for the target feature keywords to find existing coverage
3. Navigate to the URL, use `find_elements` to catalog interactive elements
4. Close the browser session
5. Categorize test cases with priorities:
   - **P0 Critical path**: Happy path flows that must work
   - **P1 Validation**: Error states, required fields, format validation
   - **P2 Edge cases**: Boundary conditions, concurrent actions, unusual inputs
6. Write the plan to `e2e-plan/coverage-plan.md`
7. Update tracker: set step 2 status to `done`

### Step 3: Explore Site & Generate Specs (delegate to subagent)

**Delegate to a general-purpose subagent** via Task tool:

Prompt the subagent with:
- Target URL and the coverage plan from `e2e-plan/coverage-plan.md`
- Instructions to explore happy paths using `navigate`, `find_elements`, `get_form_understanding`, `click`, `type`
- Instructions to probe failure paths: empty fields, invalid formats, boundary values
- TC-ID format: `TC-<FEATURE>-<NNN>` (e.g., `TC-LOGIN-001`)
- Output file: `test-cases/<feature-slug>.md`
- Each test case must have: TC-ID, title, priority, preconditions, steps (with concrete selectors/values), expected results
- Quality: independently executable, concrete observable assertions, no vague "verify it works"

After the subagent completes, verify `test-cases/<feature-slug>.md` was created and contains TC-IDs.

Update tracker: set step 3 status to `done`.

### Step 4: Write Tests (delegate to subagent)

**Delegate to a general-purpose subagent** via Task tool:

Prompt the subagent with:
- Path to `test-cases/<feature-slug>.md`
- Codebase conventions from `e2e-plan/conventions.md`:
  - Config path, test directory, naming convention
  - Locator strategy, page object patterns, fixtures, auth
- Playwright principles:
  - Semantic locators: `getByRole` > `getByLabel` > `getByTestId` > text > CSS
  - No `waitForTimeout` — use `waitForURL`, `waitForSelector`, `expect().toBeVisible()`
  - AAA structure (Arrange, Act, Assert)
  - Include TC-ID in test title: `test('TC-LOGIN-001: should login with valid credentials', ...)`
- Instructions to write test file(s) to the project's test directory following naming conventions
- If the project has API endpoints, use `request` fixture for test data setup instead of clicking through UI
- Set up auth via storageState (if applicable) rather than logging in per test
- Include at least one error path test per feature (mock 500 via `page.route`, mock empty state)
- Use `page.route()` for network mocking when testing error scenarios
- Instructions to run tests after writing: `npx playwright test <file> --reporter=list`

If the tracker notes specific uncovered TC-IDs (set by step 6), write tests only for those IDs.

Note the test file path in the tracker's Artifact column for step 4.

Update tracker: set step 4 status to `done`.

### Step 5: Verify & Fix

1. Read `e2e-plan/conventions.md` for context
2. Find test files for this feature: `Glob: **/<feature-slug>*.spec.{ts,js}`
3. Run: `npx playwright test <test-file> --reporter=list 2>&1`
4. If tests pass → mark step 5 as `done`, proceed to step 6
5. If tests fail:
   a. Read the failure output carefully. Common issues:
      - **Selector not found**: re-explore the page with `find_elements` to get current selectors
      - **Timeout**: add proper `waitForURL` or `waitForLoadState`
      - **Assertion mismatch**: verify against live site
      - **Auth/state issue**: make tests independent
   b. Edit the test file with fixes
   c. Re-run tests
   d. Maximum 2 fix-and-rerun cycles
   e. If still failing after 2 cycles: mark step 5 as `in-progress`, log the failures, and continue to step 6 anyway

Update tracker: set step 5 status to `done` (or `in-progress` if fixes exhausted).

### Step 6: Coverage Check

1. Read `test-cases/<feature-slug>.md` and extract all `TC-<FEATURE>-NNN` IDs
2. Grep test files for each TC-ID
3. If ALL TC-IDs are found in test files AND all tests pass:
   - Update tracker: set step 6 status to `done`
   - Write `<!-- E2E_COMPLETE -->` as the last line of `e2e-tracker.md`
   - Output summary: files created, TC-IDs covered, how to run
   - DONE.
4. If uncovered TC-IDs exist:
   - Log which TC-IDs are missing in the tracker session log
   - Set step 4 back to `pending` in the tracker with a note: "Missing: TC-XXX-001, TC-XXX-005"
   - Set step 5 back to `pending`
   - Set step 6 back to `pending`
   - Loop back to Step 4 to write the missing tests (one retry loop max)

---

## Tracker Updates

After completing each step, you MUST:

1. Update the step's Status in the tracker table to `done`, `in-progress`, or `blocked`
2. If the step produced an artifact, ensure the Artifact column is filled
3. Append a session log entry under `## Log`:

```markdown
### Step N completed — <YYYY-MM-DDTHH:MM:SSZ>
- Completed: <what was accomplished>
- Found: <key discoveries, if any>
- Blocker: <issue preventing progress, if any>
- Next: <what happens next>
```

Status values: `pending`, `in-progress`, `done`, `blocked`

---

## Principles

- **Tracker is the source of truth** — `e2e-tracker.md` records progress. Always read it first, always update it after each step.
- **Idempotent** — each step checks what exists and only does what's missing. Safe to re-run.
- **Subagent-driven** — heavy browser exploration and test writing delegated to Task tool subagents to save main context.
- **Follow existing conventions** — match the project's test style, not a generic template.
- **Traceable** — every test links back to a TC-ID from the spec.
- **No arbitrary waits** — use Playwright's built-in auto-wait and explicit event-driven waits.
- **API before UI for setup** — use API calls (`request` fixture) to create test data; reserve UI for what you are verifying.
- **Auth setup once** — use storageState or worker-scoped fixtures, not login UI in every test.
- **Test failures, not just success** — every feature needs error path coverage (mock 500s, empty states, network timeouts).
- **Artifacts live in standard locations** — `e2e-plan/` for analysis, `test-cases/` for specs, project test dir for test files.

## Example Usage

```
/add-e2e-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
/add-e2e-tests https://myapp.com/login User authentication including social login
```

