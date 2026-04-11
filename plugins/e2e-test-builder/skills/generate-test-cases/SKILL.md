---
name: generate-test-cases
description: >
  Use when the user wants detailed TC-ID test case specifications for a web app feature, not executable code. It explores the target flow, covers happy paths, validation failures, edge cases, and required error states, then writes structured specs under `test-cases/`. Use it after coverage planning or when the user explicitly asks for test cases or TC-IDs. It does not write Playwright code.
allowed-tools: Read Write Bash Glob Grep Task
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

Use a subagent for browser exploration when that saves context. Pass it:
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

Launch another subagent, or continue in the main thread if the flow is small, to systematically probe beyond the happy path:

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

After exploration, reason about scenarios that could not be directly triggered but may still need coverage:

- **Network & Performance** — failure modes, slow responses, large data sets, offline behavior
- **Accessibility (WCAG 2.1 AA)** — keyboard navigation, screen reader support, focus management, contrast
- **Visual Consistency** — layout stability, responsive breakpoints, dark mode
- **Cross-browser** — Safari/Firefox/mobile-specific behavioral differences
- **Concurrent & Session** — session expiry, multi-tab conflicts, race conditions

For scenarios that were not directly observed:
- label them clearly as inferred, mock-required, or environment-dependent in the spec notes
- avoid inventing exact UI text, validation copy, or server behavior you did not observe
- phrase expected results at the right confidence level (for example, "shows an error state" rather than exact copy if the exact message was not seen)
- prefer these scenarios when they are strongly implied by the architecture or are standard negative paths the implementation will need to simulate

See [references/scenario-categories.md](references/scenario-categories.md) for detailed checklists within each category.

### Step 5: Generate Test Case Specifications

Write structured test cases to `test-cases/<feature-name>.md`.

## Output Specification

### Test Case Format

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

### Output Organization

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

### File Naming Convention

When generating specs that span multiple roles or test categories, recommend role-based file naming (`*.admin.spec.ts`, `*.user.spec.ts`) or Playwright tag annotations (`@admin`, `@smoke`) in the spec. This enables selective execution via `--grep @admin` or glob patterns instead of fragile `testIgnore` regex in playwright.config.ts. NEVER recommend a `testIgnore` regex that must be updated for every new test file.

### TC-ID Convention

- Format: `TC-<FEATURE>-<NNN>` where NNN is zero-padded to 3 digits
- Feature abbreviation: short and clear (LOGIN, CHECKOUT, SEARCH, SIGNUP)
- Start at 001, sequential, unique within the document
- Happy path first, then validation, then edge cases

## Quality Standards

- Every test case must be **independently executable** — no hidden dependencies
- Steps must be **concrete and unambiguous** — "click the Submit button" not "submit the form"
- Expected results must be **observable and verifiable** — include actual error messages observed
- Priority must be **justified** — Critical = blocks core journey, High = significant, Medium = secondary, Low = cosmetic
- Include at minimum one network/server failure scenario, one empty state scenario, and one session/auth edge case when those scenarios meaningfully apply to the feature. If a category is not applicable, say so explicitly in the spec rather than inventing coverage.
- **Test case count guidance:** Aim for 15-30 test cases per feature area as a baseline. Fewer than 10 suggests missing error paths or edge cases. More than 40 suggests the feature should be split into sub-features with separate spec files. Prioritize breadth of category coverage over depth within a single category.

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
