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
  Ralph Loop compatible — detects progress from files and picks up where it left off. Outputs
  <promise>E2E COMPLETE</promise> when all TC-IDs have passing tests.
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

# Add E2E Tests — Ralph Loop Compatible Pipeline

You are an iterative E2E test builder. Each time you run, you detect your progress from existing files and advance to the next stage. You MUST follow this state detection logic exactly.

## Input

Parse the target URL and feature description from: $ARGUMENTS

Derive the **feature slug** from the feature description (e.g., "Login flow" → `login`, "Checkout with payment" → `checkout`). Use this slug for file naming throughout.

## State Detection — Files ARE the State

Check these signals IN ORDER to determine where you are in the pipeline:

### Check 1: Playwright config exists?

```
Glob: playwright.config.{ts,js,mjs}
```

If NO config found anywhere in the project:
- Report: "No Playwright configuration found. Please set up Playwright first: `npm init playwright@latest`"
- Output: `<promise>E2E COMPLETE</promise>`
- STOP.

### Check 2: Test case spec exists?

```
Glob: test-cases/<feature-slug>.md
```

If NO spec file → go to **Stage A: Analyze, Plan, Explore & Generate Specs**.

If spec file EXISTS → go to Check 3.

### Check 3: Test files exist for this feature?

```
Glob: **/<feature-slug>*.spec.{ts,js}
# Also check: **/tests/**/<feature-slug>*  and  **/e2e/**/<feature-slug>*
```

If NO test files → go to **Stage B: Write Tests from Specs**.

If test files EXIST → go to Check 4.

### Check 4: Do all tests pass?

Run the tests:
```bash
npx playwright test <test-file-path> --reporter=list 2>&1
```

If tests FAIL → go to **Stage C: Fix Failing Tests**.

If all tests PASS → go to Check 5.

### Check 5: Are all TC-IDs covered?

Read `test-cases/<feature-slug>.md` and extract all `TC-<FEATURE>-NNN` IDs.
Grep test files for each TC-ID. Any TC-ID not found in test code is uncovered.

If UNCOVERED TC-IDs exist → go to **Stage D: Write Remaining Tests**.

If ALL TC-IDs are covered and passing:
- Output summary: files created, TC-IDs covered, how to run
- Output: `<promise>E2E COMPLETE</promise>`
- DONE.

---

## Stage A: Analyze, Plan, Explore & Generate Specs

This stage does three things in sequence: understand the codebase, plan coverage, then explore the live site.

### A1: Analyze Codebase (do directly — lightweight)

1. Find and read `playwright.config.*` — extract `baseURL`, `testDir`, `projects`, `use` settings
2. Glob for existing test files, read 2-3 to understand conventions:
   - Naming pattern (e.g., `feature.spec.ts`)
   - Locator strategy (semantic `getByRole` vs `data-testid` vs CSS)
   - Test structure (AAA, page objects, fixtures, auth setup)
3. Note these conventions — all generated tests MUST follow them

### A2: Plan Coverage (do directly with quick browser check)

1. Grep existing tests for the target feature keywords to find existing coverage
2. Navigate to the URL, use `find_elements` to catalog interactive elements
3. Close the browser session
4. Categorize test cases with priorities:
   - **P0 Critical path**: Happy path flows that must work
   - **P1 Validation**: Error states, required fields, format validation
   - **P2 Edge cases**: Boundary conditions, concurrent actions, unusual inputs

### A3: Explore & Generate Specs (delegate to subagent)

**Delegate to a general-purpose subagent** via Task tool:

Prompt the subagent with:
- Target URL and the coverage plan from A2
- Instructions to explore happy paths using `navigate`, `find_elements`, `get_form_understanding`, `click`, `type`
- Instructions to probe failure paths: empty fields, invalid formats, boundary values
- TC-ID format: `TC-<FEATURE>-<NNN>` (e.g., `TC-LOGIN-001`)
- Output file: `test-cases/<feature-slug>.md`
- Each test case must have: TC-ID, title, preconditions, steps (with concrete selectors/values), expected results
- Quality: independently executable, concrete observable assertions, no vague "verify it works"

After the subagent completes, verify `test-cases/<feature-slug>.md` was created successfully.

**Then proceed immediately to Stage B** (no user prompt needed in Ralph Loop mode).

---

## Stage B: Write Tests from Specs

**Delegate to a general-purpose subagent** via Task tool:

Prompt the subagent with:
- Path to `test-cases/<feature-slug>.md`
- Codebase conventions discovered in Stage A (or re-analyze if this is a resumed iteration):
  - Config path, test directory, naming convention
  - Locator strategy, page object patterns, fixtures, auth
- Playwright principles:
  - Semantic locators: `getByRole` > `getByLabel` > `getByTestId` > text > CSS
  - No `waitForTimeout` — use `waitForURL`, `waitForSelector`, `expect().toBeVisible()`
  - AAA structure (Arrange, Act, Assert)
  - Include TC-ID in test title: `test('TC-LOGIN-001: should login with valid credentials', ...)`
- Instructions to write test file(s) to the project's test directory following naming conventions
- Instructions to run tests after writing: `npx playwright test <file> --reporter=list`

**Then proceed to Check 4** to verify results.

---

## Stage C: Fix Failing Tests

Read the test failure output carefully. Common issues and fixes:

1. **Selector not found**: Element changed — re-explore the page with `find_elements` to get current selectors
2. **Timeout**: Page load or navigation issue — add proper `waitForURL` or `waitForLoadState`
3. **Assertion mismatch**: Expected value wrong — verify against live site
4. **Auth/state issue**: Test depends on state from another test — make tests independent

Fix approach:
1. Read the failing test file
2. If selector issue: use browser tools to find correct selectors on the live site
3. Edit the test file with fixes
4. Run tests again: `npx playwright test <file> --reporter=list`

If tests still fail after fixes, note what's wrong and let the next iteration try again (Ralph Loop will re-invoke).

**Then proceed to Check 5** to see if coverage is complete.

---

## Stage D: Write Remaining Tests

Identify which TC-IDs from the spec are not yet in test files.

**Delegate to a general-purpose subagent** via Task tool:

Prompt the subagent with:
- The specific uncovered TC-IDs and their specs from `test-cases/<feature-slug>.md`
- Path to existing test file(s) so the subagent can follow the same style
- Instructions to ADD new test cases to existing file or create a new file if appropriate
- Same Playwright principles as Stage B
- Instructions to run all tests after writing

**Then proceed to Check 4** to verify.

---

## Principles

- **Files are state** — no separate progress file. The existence of `test-cases/*.md` and `*.spec.ts` tells you where you are.
- **Idempotent** — each iteration checks what exists and only does what's missing. Safe to re-run.
- **Subagent-driven** — heavy browser exploration and test writing delegated to Task tool subagents to save main context.
- **Follow existing conventions** — match the project's test style, not a generic template.
- **Traceable** — every test links back to a TC-ID from the spec.
- **No arbitrary waits** — use Playwright's built-in auto-wait and explicit event-driven waits.

## Example Usage

```
/add-e2e-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
/add-e2e-tests https://myapp.com/login User authentication including social login
```

### With Ralph Loop (fully autonomous):
```
/ralph-loop "Use /add-e2e-tests https://myapp.com/login Login flow" --completion-promise "E2E COMPLETE" --max-iterations 10
```
