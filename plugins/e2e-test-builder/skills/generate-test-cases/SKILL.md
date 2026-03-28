---
name: generate-test-cases
description: >
  Use when the user wants structured test case specifications (not executable code) for a web app feature.
  Explores a live website via browser automation, discovers all testable paths — happy paths, validation
  errors, edge cases, boundary conditions, network errors, empty states — and outputs TC-ID specs to
  test-cases/<feature>.md. Enforces minimum error path coverage (server error, network failure, empty state)
  and recommends role-based file naming conventions over testIgnore regex. Triggers: "generate test cases",
  "create test cases", "write test specs", "map all test paths", "what should I test on this page",
  "discover testable scenarios", "find edge cases for this feature", "TC-IDs for", "what are all the test
  scenarios", "map the user journeys", "document all test paths". Does NOT write executable Playwright code
  — use write-test-code. Does NOT do general browsing — use agent-web-interface-guide.
user-invocable: true
argument-hint: <url> <user journey description>
allowed-tools:
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
- Instructions to walk through each step using `find`, `get_form`, `get_field`
- Instructions to catalog all interactive elements, form fields, navigation options
- Instructions to use `get_element` on key elements to capture the best Playwright selector
- Instructions to return results in this structured format for each step:

```
Step: <what was done>
URL: <current URL after action>
Elements found:
  - Submit button: getByRole('button', { name: /submit/i })
  - Email field: getByLabel(/email/i)
  - Error message: getByText(/required/i)
Observations: <what appeared, validation messages, state changes>
```

This structured output ensures selectors survive the handoff to the spec file and ultimately to `write-test-code`.

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

After exploration, reason about scenarios that could not be directly triggered but must be covered:

**Network & Performance:**
- Network failure during form submission (mock 500, timeout)
- Slow API response (loading states, skeleton screens, spinners)
- Large data sets (pagination, infinite scroll, 100+ items)
- Offline behavior (if PWA or service worker is present)

**Accessibility (WCAG 2.1 AA):**
- Keyboard-only navigation through the entire flow (Tab, Enter, Escape)
- Screen reader announcements for dynamic content (ARIA live regions)
- Focus management after modal open/close, page transitions
- Color contrast for error states and disabled elements
- Form error association (`aria-describedby` linking errors to fields)

**Visual Consistency:**
- Layout stability (no unexpected content shifts after load)
- Responsive behavior at standard breakpoints (mobile 375px, tablet 768px, desktop 1280px)
- Dark mode rendering if supported

**Cross-browser Considerations:**
- Safari-specific behavior (date inputs, smooth scrolling, storage quirks)
- Firefox form validation differences
- Mobile browser touch targets and gestures

**Concurrent & Session:**
- Session expiry mid-flow (cookie cleared during multi-step)
- Concurrent access (two tabs, same user)
- Race conditions (double-click submit, rapid navigation)

### Step 5: Generate Test Case Specifications

Write structured test cases to `test-cases/<feature-name>.md`.

## Test Case Format

```markdown
### TC-<FEATURE>-<NUMBER>: <Descriptive title>

**Priority:** Critical | High | Medium | Low
**Category:** Happy Path | Validation | Error Handling | Edge Case | Boundary | Security | Accessibility | Visual | Performance | Network Error | UX
**Preconditions:**
- <What must be true before this test>

**Steps:**
1. <Action the tester performs>
2. <Next action>

**Expected Result:**
- <What should happen>

**Selectors observed:**
- <element>: `getByRole('button', { name: /submit/i })` or `getByLabel(/email/i)` — from `get_element`/`find` during exploration
- (Include selectors for key interactive elements so `write-test-code` doesn't have to rediscover them)

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
## Network Error Scenarios
## Visual & Responsive
## Performance & Loading
## Accessibility & UX
```

## File Naming Convention for Selective Execution

When generating specs that span multiple roles or test categories, recommend role-based file naming (`*.admin.spec.ts`, `*.user.spec.ts`) or Playwright tag annotations (`@admin`, `@smoke`) in the spec. This enables selective execution via `--grep @admin` or glob patterns instead of fragile `testIgnore` regex in playwright.config.ts. NEVER recommend a `testIgnore` regex that must be updated for every new test file.

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
- Every feature spec MUST include at minimum: one network error scenario (500/timeout), one empty state scenario, and one session/auth edge case (if the feature requires auth). These are non-negotiable — omitting them is a BLOCKER in the review-test-cases quality gate.

## Blocking Conditions

Report and work around:
- **Login/auth walls**: Document as precondition, test observable behavior
- **CAPTCHA**: Report, skip, note in preconditions
- **Payment gateways**: Don't enter real data, document flow up to that point
- **Rate limiting**: Slow down, note rate limit behavior as a test case

## Example Usage

```
Claude Code: /generate-test-cases https://example.com/login User logs in with email and password, sees dashboard
Codex: $generate-test-cases https://example.com/login User logs in with email and password, sees dashboard

Claude Code: /generate-test-cases https://shop.example.com User searches for product, adds to cart, proceeds to checkout
Codex: $generate-test-cases https://shop.example.com User searches for product, adds to cart, proceeds to checkout
```
