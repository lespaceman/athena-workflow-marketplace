---
name: generate-test-cases
description: >
  Use when the user wants structured test case specifications (not executable code) for a web application feature.
  Triggers: "generate test cases", "create test cases", "write test specs", "map all test paths",
  "what should I test on this page", "discover testable scenarios", "explore and create test specs",
  "find edge cases for this feature", "test case specifications for", "TC-IDs for".
  This skill explores a live website via browser automation, systematically discovers all testable paths —
  happy paths, validation errors, edge cases, boundary conditions — and outputs structured test case specs
  in TC-ID format to test-cases/<feature>.md. It does NOT write executable Playwright code — use write-e2e-tests for that.
  It does NOT do general browsing without test intent — use explore-website for that.
user-invocable: true
argument-hint: <url> <user journey description>
allowed-tools:
  # MCP browser tools
  - mcp__plugin_e2e-test-builder_agent-web-interface__ping
  - mcp__plugin_e2e-test-builder_agent-web-interface__navigate
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_back
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_forward
  - mcp__plugin_e2e-test-builder_agent-web-interface__reload
  - mcp__plugin_e2e-test-builder_agent-web-interface__capture_snapshot
  - mcp__plugin_e2e-test-builder_agent-web-interface__find_elements
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_element_details
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_element_into_view
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__click
  - mcp__plugin_e2e-test-builder_agent-web-interface__type
  - mcp__plugin_e2e-test-builder_agent-web-interface__press
  - mcp__plugin_e2e-test-builder_agent-web-interface__select
  - mcp__plugin_e2e-test-builder_agent-web-interface__hover
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_form_understanding
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_field_context
  - mcp__plugin_e2e-test-builder_agent-web-interface__list_pages
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_session
  - mcp__plugin_e2e-test-builder_agent-web-interface__take_screenshot
  # File tools
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
---

# Generate Test Cases

Generate comprehensive, structured test case specifications for a web application by exploring it live in a browser.

## Input

Parse the target URL and user journey description from: $ARGUMENTS

## Workflow

### Step 1: Understand the Journey and Existing Coverage

Parse the journey description to identify:
- **Base URL** and target feature area
- **Primary user goal** (what the happy path achieves)
- **Key interaction points** (forms, buttons, navigation, selections)
- **Implicit requirements** (validation, authentication, authorization)

Check for existing test coverage before exploring:
- Search for existing test files related to this feature (`Grep` for feature keywords in `**/*.spec.ts`, `**/*.test.ts`)
- Read any existing `test-cases/*.md` spec files for this feature
- Note existing TC-IDs to avoid conflicts — continue numbering from the highest existing ID
- Focus on gaps in existing coverage

### Step 2: Explore the Happy Path

Use a **general-purpose subagent** via the Task tool for browser exploration to save context. Pass it:
- The URL and journey description
- Instructions to walk through each step using `find_elements`, `get_form_understanding`, `get_field_context`
- Instructions to catalog all interactive elements, form fields, navigation options
- Instructions to document each step: what was done, what appeared, what selectors were found

### Step 3: Explore Alternative and Failure Paths

Launch another subagent to systematically probe beyond the happy path:

**Validation & Error Handling:**
- Submit forms with empty required fields
- Enter invalid formats (wrong email, short passwords, letters in number fields)
- Exceed field length limits, use special characters and Unicode

**Boundary Conditions:**
- Min/max values for numeric fields
- Single character and max length strings
- Zero quantities, negative numbers, date boundaries

**State & Navigation:**
- Browser back/forward during multi-step flows
- Page refresh mid-flow
- Accessing later steps directly via URL

**UI & Interaction:**
- Rapid repeated clicks on submit buttons
- Dropdown default values, empty options
- Loading states, disabled states, conditional visibility

**Access & Authorization (observe only):**
- Redirect behavior for unauthenticated users
- Permission-related error messages

### Step 4: Reason About Additional Scenarios

After exploration, reason about scenarios that could not be directly tested:
- Concurrent access / race conditions
- Network failure during submission
- Session expiry mid-flow
- Accessibility concerns (screen reader flows, keyboard-only navigation)

### Step 5: Generate Test Case Specifications

Write structured test cases to `test-cases/<feature-name>.md`.

## Test Case Format

```markdown
### TC-<FEATURE>-<NUMBER>: <Descriptive title>

**Priority:** Critical | High | Medium | Low
**Category:** Happy Path | Validation | Error Handling | Edge Case | Boundary | Security | Accessibility | UX
**Preconditions:**
- <What must be true before this test>

**Steps:**
1. <Action the tester performs>
2. <Next action>

**Expected Result:**
- <What should happen>

**Notes:**
- <Additional context discovered during exploration>
```

## Output Organization

```markdown
# Test Cases: <Feature Name>

**URL:** <base URL>
**Generated:** <date>
**Journey:** <brief description>

## Summary
- Total test cases: <count>
- Critical: <count> | High: <count> | Medium: <count> | Low: <count>

## Happy Path
## Validation & Error Handling
## Edge Cases
## Boundary Conditions
## Security & Access
## Accessibility & UX
```

## TC-ID Convention

- Format: `TC-<FEATURE>-<NNN>` where NNN is zero-padded to 3 digits
- Feature abbreviation: short and clear (LOGIN, CHECKOUT, SEARCH, SIGNUP)
- Start at 001, sequential, unique within the document
- Happy path first, then validation, then edge cases

## Quality Standards

- Every test case must be **independently executable** — no hidden dependencies
- Steps must be **concrete and unambiguous** — "click the Submit button" not "submit the form"
- Expected results must be **observable and verifiable** — include actual error messages observed
- Priority must be **justified** — Critical = blocks core journey, High = significant, Medium = secondary, Low = cosmetic

## Blocking Conditions

Report and work around:
- **Login/auth walls**: Document as precondition, test observable behavior
- **CAPTCHA**: Report, skip, note in preconditions
- **Payment gateways**: Don't enter real data, document flow up to that point
- **Rate limiting**: Slow down, note rate limit behavior as a test case

## Example Usage

```
/generate-test-cases https://example.com/login User logs in with email and password, sees dashboard
/generate-test-cases https://shop.example.com User searches for product, adds to cart, proceeds to checkout
```
