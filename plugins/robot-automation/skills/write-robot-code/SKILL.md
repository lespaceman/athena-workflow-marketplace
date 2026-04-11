---
name: write-robot-code
description: >
  This skill should be used when writing, refactoring, or modifying Robot Framework E2E test
  code using the Browser library. It covers creating `.robot` suites from TC-ID specs,
  converting browser exploration results to executable keywords, refactoring locators or
  resource files, adding network mocking via `Route`, test data setup/teardown with
  RequestsLibrary, and parallel-safe isolation for `pabot`. Includes locator strategy
  hierarchy, auth setup patterns, resource/keyword design, teardown strategies, and network
  interception recipes.
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

### 2. Inspect Repo Conventions (CRITICAL — before writing any code)
- Search for `robot.toml`, `pyproject.toml`, `requirements*.txt` — confirm `robotframework-browser` is installed and extract any `outputdir`, default tags, and listeners
- Search for existing suites under `tests/**/*.robot` and resources under `resources/**/*.resource`
- Read 2-3 existing `.robot` files to match the project's naming, structure, locator style, and keyword granularity
- Check for `__init__.robot` suite-init files, custom listeners, `variables.py`, stored browser state, and RequestsLibrary session helpers
- Follow the project's existing style unless it clearly causes flakiness

### 3. Verify Key Selectors Against the Live Site
- If a test case spec file includes **Selectors observed**, use those as your starting point
- If no spec or selectors are available, browse the target page using `agent-web-interface-guide` to discover the actual selectors before writing code — do not guess
- Spot-check 2-3 critical selectors with `find` or `get_element` to confirm they resolve to the intended elements
- Translate exploration locators into Browser library syntax (`role=button[name="Submit"]`, `label=Email`, `text=/welcome/i`, `[data-testid="submit"]`)

### 4. Implement Tests
- Add/adjust shared keywords in `resources/` first (if needed)
- Write tests in a story-like flow with AAA structure: Arrange → Act → Assert
- Put the HOW (locators, interactions) into resource keywords; keep the test case body focused on WHAT (behavior/outcome)
- Add assertions that represent user outcomes
- **For large suites:** Use subagents (Task tool) to write individual `.robot` files in parallel.
  Pass each subagent the test case spec path, codebase conventions from Step 2, and the
  operating principles from this skill. Only split when files have independent responsibilities.

### 5. Stabilize
- Replace any `Sleep` calls with `Wait For Elements State` or `Wait For Response`
- Tighten locators to avoid ambiguity — scope with `>>` descendant combinators or parent locators
- For network-driven flows, wait on the specific response, not a blanket `networkidle`

### 6. Verify
- Run the smallest relevant suite: `robot -d results tests/<feature>.robot 2>&1`
- For a single test within a suite: `robot -d results -t "TC-LOGIN-001*" tests/login.robot`
- In CI or headless environments, pass `--variable HEADLESS:true` (or keep headless as the default)
- Use `HEADLESS=False` / headed mode only during local interactive debugging
- Inspect `results/log.html` and `results/report.html` — they are the canonical proof of run behavior
- Fix root causes rather than extending timeouts

### 7. Summarize
Return:
1. **What I changed** (bullets)
2. **Test case IDs added** (list all new TC-IDs with brief description)
3. **Why it's stable** (locator/wait strategy used)
4. **How to run** (exact `robot` commands)
5. **Notes / follow-ups** (optional)

## Operating Principles (Non-Negotiable)

### Test User Outcomes
Assert what the user sees — visible text, URL changes, enabled/disabled states, counts — not internal state, CSS class names, or component hierarchy.

### No `Sleep`
Avoid `Sleep` except as a last-resort debug aid — remove before finishing. `Sleep` hides timing races and is a leading cause of flaky Robot suites. Prefer `Wait For Elements State`, `Wait For Response`, or Browser library's built-in auto-waits.

### Locator Strategy (Browser library)
| Priority | Method | When to Use |
|----------|--------|-------------|
| 1 | `role=button[name="Submit"]` / `role=textbox[name="Email"]` | Buttons, links, headings, form controls (maps to ARIA roles) |
| 2 | `label=Email` | Form fields with visible labels |
| 3 | `placeholder=Search…` | Inputs identified by placeholder |
| 4 | `[data-testid="submit"]` | When `data-testid` is available |
| 5 | `text=/welcome/i` or `text="Welcome"` | Short, stable text (avoid marketing copy) |
| 6 | CSS / XPath | Last resort, always scoped tightly (e.g., `main >> role=button`) |

Avoid `>> nth=0` positional selectors unless a strong, documented reason exists — scope to a parent instead using `>>` chaining (`[data-testid="cart"] >> role=button[name="Remove"]`).

**Within-file consistency:** Every `.robot` file must use ONE locator approach for equivalent elements. Do not mix `label=Email` in one test with `css=input[name="email"]` in another test within the same file. When adding tests to an existing file, match the locator style already in use. If the existing style is suboptimal, refactor all locators in the file together — do not create inconsistency.

### Waiting Strategy
- Prefer Browser library auto-waits — most keywords wait for the element to be actionable automatically
- When explicit waiting is needed, use `Wait For Elements State    <locator>    <state>` (`visible`, `hidden`, `attached`, `enabled`)
- For network-driven UI, use `Wait For Response    matcher=**/api/items    timeout=10s` around the action
- Do NOT rely on `networkidle`-style waits — they break on long-polling, WebSockets, analytics beacons

### Test Case IDs
- Every test MUST have a unique TC-ID: `TC-<FEATURE>-<NNN>`
- Put the TC-ID in the test case name: `TC-LOGIN-001 User can log in with valid credentials`
- Also surface it in `[Documentation]` and as a `[Tags]` value so reports and `--include` filters work cleanly
- Sequential within feature area, never reused
- When adding to an existing file, check existing IDs and continue the sequence

### Resources + Keywords (Robot Framework's Page Object Model)
- If the project has a `resources/` directory or a `Base.resource`, ALL new tests MUST import them via `Resource    resources/common.resource`
- Resource keywords contain HOW (locators + interactions)
- Test cases contain WHAT (behavior/outcome to verify)
- Keep resource keywords thin and composable — one keyword per page-level action (`Submit Login Form`, not `Submit Login Form And Verify Dashboard`)
- If the scaffold shipped a `common.resource` that no tests reference, either extend it for your feature or flag it for removal — dead infrastructure causes confusion

### Determinism and Isolation
- Tests must not depend on execution order
- Use unique test data per test or suite (`${unique_id}=    Evaluate    str(time.time_ns())` or `Get Time    epoch`)
- **Parallel-safe mutations (pabot):** When using `pabot` for parallel execution, suites run concurrently across processes. A test that creates a record (e.g., a ticket) and then asserts it appears in a list WILL race with other pabot workers creating records. Solutions: (a) assert on the specific record you created (filter/search by the unique ID from your API setup), not on list position or count; (b) keep serial-dependent flows inside a single suite (pabot parallelizes at suite level by default); (c) scope list assertions with a `filter=${unique_id}` URL parameter or a keyword that walks the list looking for the unique identifier.

### Assertions (Browser library)
- Use Browser library assertion forms with the `==`, `!=`, `contains`, `matches`, `validate` operators:
  `Get Text    role=alert    ==    Invalid email`
  `Get Element States    role=button[name="Submit"]    *=    enabled`
  `Get Url    contains    /dashboard`
- These assertions auto-retry up to `timeout` before failing
- Avoid `Should Be Equal` on snapshot values without retry — it runs once and fails on any timing drift

### Configuration Hygiene
- Use a `${BASE_URL}` variable and relative navigation (`Go To    ${BASE_URL}/`)
- Avoid hardcoded domains / URLs in tests — pass via `--variable BASE_URL:...` or `variables.py`
- Enable tracing on failure via a `Browser` library listener or `trace=retain-on-failure` in `New Context`
- Configure retries via `--rerunfailed` workflow or a project-level listener, not by hardcoding sleeps
- Keep a `Suite Teardown    Close Browser` (or rely on `auto_closing_level=SUITE`) to release resources
- If `variables.py` exports computed variables, import it via `Variables    variables.py` — do not duplicate environment reads inside test cases

### Authentication Setup
Use persisted browser state for most projects (log in once, save context state JSON, reuse across suites).
For parallel pabot processes needing separate accounts, store per-process state files.
For multi-role tests (admin + user), create separate browser contexts in the same test.
Per-test login is only for testing the login flow itself.
Never hardcode tokens — use variables, listeners, or `.env` loaded via `variables.py`.

See [references/auth-patterns.md](references/auth-patterns.md) for full patterns with code examples.

### API-Driven Test Setup and Teardown
Use `RequestsLibrary` (not UI clicks) to seed test data — 10-50x faster and more reliable.
Use UI setup only when the creation flow IS the test. Tests that create persistent data
MUST clean up: use `[Teardown]`, `Suite Teardown`, or a listener-driven global cleanup.
If no cleanup endpoint exists, document the gap with a TODO.

See [references/api-setup-teardown.md](references/api-setup-teardown.md) for full patterns with code examples.

### Network Interception and Error Paths
Use Browser library's `Route` keyword to mock server errors, patch responses, assert backend calls, or block heavy resources. Add error path tests when they meaningfully apply to the feature: for example, server/network failures for backend-driven flows, empty states for collection/data-driven UIs, and session/auth cases for gated features. If a category is not applicable, do not invent it.

See [references/network-interception.md](references/network-interception.md) for full patterns with code examples.

### Mapping Tables
When converting journey specs or exploration results to Robot Framework code, consult the mapping tables for standard translations of scopes, actions, assertions, and target kinds to Browser library keywords.
For low-confidence journey steps (<0.7), add extra assertions and include fallback locators in comments.

See [references/mapping-tables.md](references/mapping-tables.md) for the full tables.

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
    Fill Text    label=Email       ${VALID_EMAIL}
    Fill Secret  label=Password    $VALID_PASSWORD
    Click        role=button[name="Sign in"]
    Wait For Response    matcher=**/api/session    timeout=10s
    Get Url      contains    /dashboard
    Get Text     role=heading[name="Welcome"]    contains    Welcome
```

Always check for project resources (`resources/common.resource`, `resources/<feature>.resource`, `variables.py`) before importing directly. If custom resources exist, you MUST import them to get access to shared keywords and configuration.

## Anti-Patterns (Quick Reference)
1. Raw CSS / XPath where a semantic Browser locator would work
2. `Sleep` — use `Wait For Elements State` / `Wait For Response`
3. Fragile `>> nth=0` — scope to a parent container
4. Exact long text matches — use `text=/regex/i` with key words
5. Unscoped locators — chain with `>>` and a container
6. Login via UI in every test — reuse persisted context state
7. UI clicks for test data setup — use `RequestsLibrary`
8. No error path tests — add failure scenarios via `Route`
9. Hardcoded test data — use API setup + dynamic values
10. Tests depending on execution order
11. `Run Keyword And Ignore Error` hiding assertion failures
12. `force=True` / `force=${True}` on actions without justification
13. `Sleep` after navigation instead of `Wait For Elements State` / `Wait For Response`
14. Utility-class selectors (`.bg-primary`, `.btn-lg`, Tailwind, Bootstrap)
15. Asserting exact server-computed values — use patterns, ranges, or seed via API

See [references/anti-patterns.md](references/anti-patterns.md) for detailed explanations and fix strategies.
