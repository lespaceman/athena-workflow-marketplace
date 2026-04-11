# Authentication Setup Patterns

Choose the right auth strategy based on the project's needs.

## Strategy 1: Persisted browser state (Recommended for most projects)

Log in once, save the browser context storage state to a JSON file, and reuse across all tests:

```robotframework
*** Settings ***
Library    Browser
Suite Setup    Save Authenticated State

*** Keywords ***
Save Authenticated State
    New Browser    chromium    headless=${HEADLESS}
    New Context
    New Page    ${BASE_URL}/login
    ${email}=       Get Element By Label    Email
    ${password}=    Get Element By Label    Password
    ${submit}=      Get Element By Role     button    name=Sign in
    Fill Text       ${email}                %{TEST_USER_EMAIL}
    Fill Secret     ${password}             $TEST_USER_PASSWORD
    Click           ${submit}
    ${dashboard}=   Get Element By Role     heading    name=Dashboard
    Wait For Elements State    ${dashboard}    visible    timeout=10s
    Save Storage State    path=${EXECDIR}/auth/user.json
    Close Browser
```

Reference in later suites:

```robotframework
*** Keywords ***
Open Authenticated Page
    New Browser    chromium    headless=${HEADLESS}
    New Context    storageState=${EXECDIR}/auth/user.json
    New Page    ${BASE_URL}
```

Run the login suite first (or from a `__init__.robot` Suite Setup) so `auth/user.json` exists before feature suites run.

## Strategy 2: Per-pabot-process state (for parallel workers needing separate accounts)

```robotframework
*** Keywords ***
Open Authenticated Page For Worker
    ${worker_id}=    Get Environment Variable    PABOTQUEUEINDEX    default=0
    New Browser    chromium    headless=${HEADLESS}
    New Context    storageState=${EXECDIR}/auth/worker-${worker_id}.json
    New Page    ${BASE_URL}
```

Produce the worker-specific state files in a `pabot` prerun keyword or a one-off seed script, then reuse them across parallel suites.

## Strategy 3: Multi-role testing (admin + user in same test)

```robotframework
*** Test Cases ***
TC-ADMIN-001 Admin sees user profile
    [Documentation]    Admin inspecting a user from another context.
    New Browser    chromium    headless=${HEADLESS}
    ${admin_ctx}=    New Context    storageState=${EXECDIR}/auth/admin.json
    ${user_ctx}=     New Context    storageState=${EXECDIR}/auth/user.json
    Switch Context    ${admin_ctx}
    New Page    ${BASE_URL}/admin/users
    # …interact as admin…
    Switch Context    ${user_ctx}
    New Page    ${BASE_URL}/profile
    # …interact as user…
    [Teardown]    Close Browser
```

## Strategy 4: Per-test login

Only when testing login itself or permission-specific scenarios. Put the login steps in `resources/login.resource` so every suite can call the same `Log In As User` keyword.

**Never hardcode tokens.** Read them via `%{TEST_USER_PASSWORD}`, a `.env` file loaded through `variables.py`, or a vault listener. Use `Fill Secret` rather than `Fill Text` so the value is redacted in logs.
