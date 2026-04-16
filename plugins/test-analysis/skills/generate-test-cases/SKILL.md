---
name: generate-test-cases
description: >
  Use when the user wants detailed TC-ID test case specifications for a web app feature, not executable code. This shared skill consumes `e2e-plan/exploration-report.md`, `e2e-plan/coverage-plan.md`, and existing coverage artifacts to write structured specs under `test-cases/`. Use it after coverage planning or when the user explicitly asks for test cases or TC-IDs. It does not write framework-specific test code.
allowed-tools: Read Write Bash Glob Grep Task
---

# Generate Test Cases

Generate comprehensive, structured test case specifications from shared evidence and coverage plans.

## Input

Parse the target URL and user journey description from: $ARGUMENTS

## Workflow

### Step 1: Load The Evidence Base

Read and reconcile:
- `e2e-plan/exploration-report.md`
- `e2e-plan/coverage-plan.md`
- existing `test-cases/*.md` specs for the feature
- existing automated coverage if needed to avoid duplicate TC-IDs

If the feature clearly needs real product evidence and `e2e-plan/exploration-report.md` is missing,
stop and run `explore-app` first.

Parse the journey description to identify:
- base URL and target feature area
- primary user goal
- key interaction points
- implicit requirements such as validation, authentication, and authorization

### Step 2: Convert Evidence Into Testable Scenarios

Work from the exploration report first:
- use directly observed flows for happy-path and validation scenarios
- preserve observed URLs, labels, copy, and control names when they were seen
- continue TC-ID numbering from the highest existing ID

When a specific detail remains unclear, you may run a bounded spot-check via a subagent with
browser access. Ask it to verify only the uncertain claim and return structured evidence like:

```
Claim checked: <what needed confirmation>
Observed step: <what was done>
URL: <current URL after action>
Observed controls:
  - Submit button: role=button, name=/submit/i
  - Email field: label "Email"
Observed result: <what actually happened>
```

### Test-design techniques

Apply standard techniques, choosing based on what each feature needs:

- **Equivalence partitioning + boundary values** for inputs (0, -1, max, max+1, empty, very long,
  unicode, `'`, `"`, `\`, emoji, RTL). Use on every input field found in the exploration report.
- **Decision tables** for multi-condition features (e.g., "refund allowed if order < 30 days AND
  item unused AND receipt uploaded").
- **State transitions** for workflows (signup -> verify -> login -> 2FA -> logout). Map these from
  the observed journey.
- **Use cases / user journeys** for end-to-end flows per persona. These cross feature boundaries
  and belong in their own "Integration / E2E" section.
- **Negative testing** — explicitly cover what happens when things go wrong within each feature.

### Step 3: Expand To Alternative And Failure Paths

Use the coverage plan to make sure you cover more than the happy path:

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

**Observed controls / selector candidates:**
- <element>: `role=button`, name `/submit/i`
- <element>: label `Email`
- <element>: test id `checkout-submit`
- (Include the semantic evidence the execution layer will translate into framework-specific locators)

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
- Distinguish clearly between **observed** and **inferred** behavior
- Priority must be **justified** — Critical = blocks core journey, High = significant, Medium = secondary, Low = cosmetic
- Include at minimum one network/server failure scenario, one empty state scenario, and one session/auth edge case when those scenarios meaningfully apply to the feature. If a category is not applicable, say so explicitly in the spec rather than inventing coverage.
- **Non-happy-path ratio:** Aim for at least 30% of cases within each feature to be non-happy-path.
  Include: invalid inputs, permission errors, network failures, concurrent actions, session
  timeouts, back-button/refresh mid-action, empty states, maximum limits, and interrupt cases.
- **Test case count guidance:** Aim for 15-30 test cases per feature area as a baseline. Fewer than 10 suggests missing error paths or edge cases. More than 40 suggests the feature should be split into sub-features with separate spec files. Prioritize breadth of category coverage over depth within a single category.

## Blocking Conditions

Report and work around:
- **Login/auth walls**: Document as precondition, test observable behavior
- **CAPTCHA**: Report, skip, note in preconditions
- **Payment gateways**: Don't enter real data, document flow up to that point
- **Rate limiting**: Slow down, note rate limit behavior as a test case

## Worked Example

Here's a compressed example showing evidence-to-spec flow for a simple contact form:

**Exploration evidence** (from `e2e-plan/exploration-report.md`):
Visited the contact page. Found: name field (text, no visible limit), email field (validates format
client-side), message textarea (maxlength=500 in HTML), submit button, success toast, no CAPTCHA.
Network traffic shows POST to `/api/contact` returning 200 with `{"status":"queued"}`. Console
clean. Tried empty submit -> client-side validation fires on email only, name and message submit
empty.

**Coverage plan** (from `e2e-plan/coverage-plan.md`):

| Area | Impact | Likelihood | Priority |
|------|--------|------------|----------|
| Input validation (name, message) | Medium (junk submissions) | High (no validation observed) | P0 |
| Email validation | High (spam vector) | Medium (client-only check) | P0 |
| Input security (XSS) | High (security) | Medium | P0 |
| Message length limits | Low (truncation) | Medium (server limit unknown) | P1 |
| Rate limiting / abuse | Medium (abuse) | Unknown | P1 |

**Generated test cases** (written to `test-cases/contact-form.md`):

### Input Validation
**TC-CONTACT-001** — Submit with empty name and message (P0)
*Category:* Validation
*Preconditions:* On contact page
*Steps:* Clear all fields, enter valid email, click Submit
*Expected:* Validation error; form should not submit. (Currently fails — this is a bug.)
*Observed controls:* `input[name="name"]`, `input[name="email"]`, `textarea[name="message"]`,
`button[type="submit"]`

### Email Validation
**TC-CONTACT-002** — Email validation bypass via direct API call (P0)
*Category:* Security
*Preconditions:* None
*Steps:* POST to /api/contact with body `{"name":"test","email":"not-an-email","message":"hi"}`
*Expected:* 400 error with validation message. If 200, server-side validation is missing.

### Input Security
**TC-CONTACT-003** — XSS in name field (P0)
*Category:* Security
*Preconditions:* On contact page
*Steps:* Enter `<script>alert(1)</script>` in name, valid email, any message, submit
*Expected:* Input sanitized or escaped; no script execution anywhere the name is displayed.

Notice how every test traces to a specific observation and risk, and TC-IDs follow the
`TC-<FEATURE>-<NNN>` convention.

## What good looks like

- Test cases are grouped by feature, with each group's size proportional to its risk.
- Cases reference specific things actually observed in the app (real field names, real error
  messages, real API endpoints, real selectors).
- Priorities are tied to the risk map, not picked at random.
- Non-happy-path and boundary cases are at least 30% of the suite within each feature.
- Cross-feature E2E journeys are tested separately from individual features.
- The user can read the top 5 tests and say "yes, those are the things that scare me too."

## What to avoid

- Generic cases like "TC-01: User can log in" with no reference to the actual login mechanism.
- A flat list of cases with no feature grouping or structure.
- All-happy-path, no negative cases.
- No risk ranking, or ranking that doesn't correspond to anything observed.
- Producing 50 tests for a simple form, or 5 tests for a complex multi-role app. Match the scale.
- Ignoring existing exploration or coverage artifacts and starting from zero.

## Example Usage

```
Claude Code: /generate-test-cases https://example.com/login User logs in with email and password, sees dashboard
Codex: $generate-test-cases https://example.com/login User logs in with email and password, sees dashboard

Claude Code: /generate-test-cases https://shop.example.com User searches for product, adds to cart, proceeds to checkout
Codex: $generate-test-cases https://shop.example.com User searches for product, adds to cart, proceeds to checkout
```
