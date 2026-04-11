---
name: generate-test-cases
description: >
  Use when the user wants detailed TC-ID test case specifications for a Robot Framework target,
  not executable code. It explores the target flow, covers happy paths, validation failures,
  edge cases, and required error states, then writes structured specs under `test-cases/`.
  Use it after coverage planning or when the user explicitly asks for test cases or TC-IDs.
  It does not write `.robot` code.
allowed-tools: Read Write Bash Glob Grep Task
---

# Generate Test Cases

Generate structured test case specifications for a web application by exploring it live in a browser. The specs feed `write-robot-code`.

## Input

Parse the target URL and user journey description from: $ARGUMENTS

## Workflow

### Step 1: Understand the Journey and Existing Coverage
- Parse the base URL, feature area, primary user goal, key interaction points, and implicit requirements
- Search for existing suites related to the feature
- Read any existing `test-cases/*.md` files for this feature
- Read `e2e-plan/conventions.yaml` if it exists so observed selectors are recorded in the dialect downstream skills expect
- Continue TC-ID numbering from the highest existing ID

### Step 2: Explore the Happy Path
Use a subagent for browser exploration when that saves context. Ask it to return results in this structure:

```text
Step: <what was done>
URL: <current URL after action>
Elements found:
  - Submit button: Get Element By Role    button    name=Submit
  - Email field: Get Element By Label    Email
  - Error message: Get Element By Role    alert
Observations: <what appeared, validation messages, state changes>
```

If `conventions.yaml` says `css_first`, record selectors in that dialect instead. Otherwise prefer canonical `Get Element By *` forms.

### Step 3: Explore Alternative and Failure Paths
Probe beyond the happy path:
- Validation and error handling
- Boundary conditions
- State and navigation
- UI and interaction edge cases
- Access and authorization behavior

### Step 4: Reason About Additional Scenarios
After exploration, add scenarios that are strongly implied but not directly triggered:
- Network and performance
- Accessibility
- Visual consistency
- Cross-browser
- Concurrent and session behavior

Mark non-observed scenarios clearly as inferred, mock-required, or environment-dependent. Do not invent exact UI copy or backend behavior.

### Step 5: Generate Test Case Specifications
Write structured test cases to `test-cases/<feature-name>.md`.

## Output Specification

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
- <Observable outcome>

**Selectors observed:**
- <element>: `Get Element By Role    button    name=Submit`
- <element>: `Get Element By Label    Email`
- Or justified `css=` / `xpath=` / `text=` / `id=` when the project convention or DOM requires it

**Notes:**
- <Context discovered during exploration>
```

Organize the output under:
- Summary
- Happy Path
- Validation and Error Handling
- Edge Cases
- Boundary Conditions
- Security and Access
- Network Error Scenarios
- Visual and Responsive
- Performance and Loading
- Accessibility and UX

## Quality Standards
- Every test case must be independently executable
- Steps must be concrete and unambiguous
- Expected results must be observable and verifiable
- Priorities must be justified
- Include meaningful negative-path coverage when applicable
- Prefer breadth of category coverage over padding one category

## Blocking Conditions
- Login and auth walls
- CAPTCHA
- Payment gateways
- Rate limiting

Document blockers rather than guessing through them.
