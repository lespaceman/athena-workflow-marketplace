---
name: write-robot-code
description: >
  Use when writing, refactoring, or modifying Robot Framework E2E test code with the Browser
  library. Covers creating `.robot` suites from TC-ID specs, converting browser exploration
  results to executable keywords, refactoring locators or resources, adding network mocking
  via `Route`, test data setup with RequestsLibrary, `e2e-plan/conventions.yaml` adherence,
  smoke-first implementation, auth patterns, and parallel-safe isolation for `pabot`.
  Triggers: "write a Robot test for", "add a Robot test case", "refactor this locator",
  "add error path tests", "convert specs to .robot code", "add network mocking in Robot",
  "set up auth for Robot tests".
  NOT for: full pipeline from scratch (use add-robot-tests), exploring live sites (use
  agent-web-interface-guide), generating specs without code (use plan-test-coverage or
  generate-test-cases), diagnosing flaky tests (use fix-flaky-tests).
allowed-tools: Read Write Edit Bash Glob Grep Task
---

# Write Robot Framework Tests

Write, refactor, or fix Robot Framework E2E tests using the Browser library. Convert browser exploration results or test case specifications into executable, stable `.robot` suites.

## Input

Parse the test description or spec file path from: $ARGUMENTS

## Workflow

### 1. Understand the Request
- Identify the user journey to test and success criteria
- Identify preconditions (auth, seeded data, feature flags, env)
- If a test case spec file path is provided, read it for TC-IDs and expected behaviors

### 2. Inspect Repo Conventions
- Read `e2e-plan/conventions.yaml` first if it exists. Validate it against `plugins/robot-automation/schemas/conventions.schema.json` and treat it as the source of truth for locator style, resource pattern, auth strategy, tag vocabulary, and parallel mode.
- If `e2e-plan/conventions.yaml` does not exist and the project already has Robot code, stop and run `analyze-test-codebase` first.
- Search for `robot.toml`, `pyproject.toml`, `requirements*.txt`, `__init__.robot`, and CI scripts to confirm `robotframework-browser` is installed and extract `outputdir`, default tags, listeners, and retry config
- Search for existing suites under `tests/**/*.robot` and resources under `resources/**/*.resource`
- Read 2-3 existing `.robot` files to match the project's naming, structure, locator style, and keyword granularity
- Check for `variables.py`, stored browser state, RequestsLibrary session helpers, and existing auth/resource patterns
- Follow the project's existing style unless it clearly causes flakiness or conflicts with the validated conventions contract

### 3. Verify Key Selectors Against the Live Site
- If a test case spec file includes **Selectors observed**, use those as your starting point
- If no spec or selectors are available, browse the target page using `agent-web-interface-guide` to discover the actual selectors before writing code
- Spot-check critical selectors with `find` or `get_element` to confirm they resolve to the intended elements
- Record canonical Browser-library locators in one of these forms:
  - `Get Element By Role    button    name=Submit`
  - `Get Element By Label    Email`
  - `Get Element By Placeholder    Search`
  - `Get Element By Test Id    submit`
  - `text=Welcome`, `css=.legacy-selector`, `xpath=...`, or `id=username` only when the project convention or DOM requires a prefixed engine
- If `conventions.yaml` says `css_first`, keep using that dialect in the file. If it says `get_element_by_role_first`, prefer the `Get Element By *` family and locator variables.

### 4. Implement Tests
- Add or adjust shared keywords in `resources/` first when needed
- Put the HOW into resource keywords; keep the test case body focused on user-visible behavior and outcomes
- Write tests in a clear Arrange, Act, Assert flow
- Before expanding to the full spec, write ONE happy-path test end-to-end and run it. Get it green first. Then add the rest of the tests.
- For large suites, use subagents to write independent `.robot` files in parallel. Pass each subagent the spec path, conventions, and the operating principles from this skill.

### 5. Stabilize
- Replace any `Sleep` calls with `Wait For Elements State`, `Promise To    Wait For Response`, or Browser-library retrying assertions
- Tighten locators to avoid ambiguity with `parent=` or `>>` scoping, not `>> nth=0`
- For network-driven flows, attach waits before the action with `Promise To` + action + `Wait For`
- Keep strict mode on unless there is a documented project-specific exception with a `# WHY:` comment

### 6. Verify
- Run the smallest relevant suite: `robot -d results tests/<feature>.robot 2>&1`
- For a single test within a suite: `robot -d results -t "TC-LOGIN-001*" tests/login.robot`
- In CI or headless environments, pass `--variable HEADLESS:true` or keep headless as the default
- Use `HEADLESS=False` only during local interactive debugging
- Inspect `results/log.html` and `results/report.html`
- For workflow signoff, run the suite 3 total times after the first green run. Any flake sends the work to `fix-flaky-tests`.

### 7. Summarize
Return:
1. What changed
2. Test case IDs added
3. Why it is stable
4. How to run
5. Notes or follow-ups

## Operating Principles

### Test User Outcomes
Assert what the user sees: visible text, URL changes, enabled or disabled states, presence or absence, counts, and successful backend-driven state changes. Do not assert CSS classes or component internals.

### No `Sleep`
Avoid `Sleep` except as a temporary debug aid that is removed before completion.

### Locator Strategy
| Priority | Method | When to Use |
|----------|--------|-------------|
| 1 | `Get Element By Role    button    name=Submit` | Buttons, links, headings, form controls with accessible roles |
| 2 | `Get Element By Label    Email` | Form fields with visible labels |
| 3 | `Get Element By Placeholder    Search` | Inputs identified by placeholder |
| 4 | `Get Element By Test Id    submit` | Stable test IDs |
| 5 | `text=Welcome` or `text=/welcome/i` | Short, stable text |
| 6 | `css=...`, `xpath=...`, `id=...` | Last resort, always scoped tightly and matched to project convention |

Avoid fake selector-engine prefixes such as `role=`, `label=`, `placeholder=`, `alt=`, `title=`, or `testid=`. Those are not the canonical Browser-library dialect this skill should teach.

Prefer parent scoping over positional selection:

```robotframework
${dialog}=    Get Element By Role    dialog    name=Confirm delete
${submit}=    Get Element By Role    button    name=Submit    parent=${dialog}
Click    ${submit}
```

### Waiting Strategy
- Prefer Browser-library auto-waits where possible
- Use `Wait For Elements State    <locator>    <state>` for explicit readiness
- For network-driven UI, attach the wait before the action:

```robotframework
${promise}=    Promise To    Wait For Response    matcher=**/api/items    timeout=10s
Click    ${submit_button}
${resp}=    Wait For    ${promise}
```

- Do not rely on blanket network-idle semantics

### Test Case IDs
- Every test must have a unique `TC-<FEATURE>-<NNN>` ID
- Put the TC-ID in the test name
- Also surface it in `[Documentation]` and `[Tags]`
- Continue existing sequences when editing an existing file

### Resources and Keywords
- If the project has `resources/`, reuse it instead of duplicating inline keywords
- Resource keywords contain HOW
- Test cases contain WHAT
- Keep resource keywords thin and composable
- If shared infrastructure exists but is unused, either use it intentionally or flag it as dead infrastructure

### Determinism and Isolation
- Tests must not depend on execution order
- Use unique test data per test or suite
- For `pabot`, assert on the specific entity you created, not on list position or global count

### Assertions
- Prefer retrying Browser-library assertions:
  - `Get Text    ${alert}    ==    Invalid email`
  - `Get Element States    ${submit_button}    *=    enabled`
  - `Get Url    contains    /dashboard`
- Avoid one-shot snapshot assertions when a retrying form exists

### Configuration Hygiene
- Use `${BASE_URL}` and relative navigation
- Avoid hardcoded domains
- Preserve project-local listener and retry setup
- Prefer `tracing=retain-on-failure`, `run_on_failure`, and stable context config where the project supports them
- Keep `Suite Teardown    Close Browser` or rely on `auto_closing_level=SUITE`

### Authentication Setup
Use persisted browser state for most projects. Use per-test login only when testing the login flow itself. Use separate contexts for multi-role tests. Never hardcode tokens.

See [references/auth-patterns.md](references/auth-patterns.md).

### API-Driven Test Setup and Teardown
Use `RequestsLibrary` to seed and clean up data whenever the UI flow itself is not under test.

See [references/api-setup-teardown.md](references/api-setup-teardown.md).

### Network Interception and Error Paths
Use `Route URL` to mock server errors, patch responses, assert backend calls, or block heavy resources.

See [references/network-interception.md](references/network-interception.md).

### Mapping Tables
When converting journey specs or exploration results to `.robot` code, use the mapping tables as the canonical translation guide.

See [references/mapping-tables.md](references/mapping-tables.md).

## Test Template

```robotframework
*** Settings ***
Documentation     Login feature E2E suite
Resource          ../resources/common.resource
Resource          ../resources/login.resource
Suite Setup       Open Browser To Base URL
Suite Teardown    Close Browser
Test Tags         login    smoke

*** Variables ***
${VALID_EMAIL}       user@example.com
${VALID_PASSWORD}    %{TEST_USER_PASSWORD}

*** Test Cases ***
TC-LOGIN-001 User can log in with valid credentials
    [Documentation]    Happy path login redirects to dashboard.
    [Tags]    TC-LOGIN-001    critical
    Go To    ${BASE_URL}/login
    ${email}=       Get Element By Label    Email
    ${password}=    Get Element By Label    Password
    ${submit}=      Get Element By Role     button    name=Sign in
    Fill Text       ${email}                ${VALID_EMAIL}
    Fill Secret     ${password}             $VALID_PASSWORD
    ${promise}=     Promise To    Wait For Response    matcher=**/api/session    timeout=10s
    Click           ${submit}
    ${resp}=        Wait For    ${promise}
    Get Url         contains    /dashboard
    ${welcome}=     Get Element By Role     heading    name=Welcome
    Get Text        ${welcome}              contains    Welcome
```

Always check for project resources before importing directly. If custom resources exist, import them so the tests use the project's real setup and conventions.

## Anti-Patterns
1. Fake selector prefixes such as `role=` or `label=`
2. Raw CSS or XPath where a semantic Browser locator would work
3. `Sleep`
4. Fragile `>> nth=0`
5. Exact long text matches
6. Unscoped locators
7. Login via UI in every test
8. UI clicks for test-data setup
9. No error path tests
10. Hardcoded test data
11. Tests depending on execution order
12. `Run Keyword And Ignore Error` hiding assertion failures
13. `force=True` on actions without justification
14. Post-action `Wait For Response` instead of `Promise To`
15. Utility-class selectors
16. Exact server-computed numeric assertions without seeded data

See [references/anti-patterns.md](references/anti-patterns.md).
