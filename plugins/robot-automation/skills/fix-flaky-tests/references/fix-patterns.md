# Fix Patterns by Root Cause

Code examples for each root cause category. Apply only after diagnosing the cause in Step 2.

## Timing Fixes — Replace Sleeps with Event-Driven Waits

```robotframework
# BAD: arbitrary sleep
Sleep    2s
Get Element States    ${element}    *=    visible

# GOOD: attach the response wait before the triggering action
${promise}=    Promise To    Wait For Response    matcher=**/api/data    timeout=10s
# trigger action here
${resp}=    Wait For    ${promise}
Get Element States    ${element}    *=    visible

# GOOD: wait for loading indicator to disappear
Wait For Elements State    css=[role="progressbar"]    hidden    timeout=10s
Get Element States    ${element}    *=    visible

# GOOD: wait for a specific readiness signal after navigation
Go To    ${BASE_URL}/page
${dashboard}=    Get Element By Role    heading    name=Dashboard
Wait For Elements State    ${dashboard}    visible    timeout=10s

# GOOD: use auto-retrying Browser assertion (retries until timeout)
Get Text    text=/loaded/i    contains    loaded    timeout=10s
```

## State Isolation Fixes

```robotframework
# Unique data per test
${unique_email}=    Evaluate    f"test-{time.time_ns()}@example.com"    modules=time

# Reset state via API before each test
Test Setup    Reset Test State

*** Keywords ***
Reset Test State
    Create Session    api    ${API_BASE_URL}    headers=&{API_HEADERS}
    POST On Session   api    /test/reset

# Use fresh browser context per test (Browser library: New Context inside Test Setup)
*** Keywords ***
Fresh Authenticated Context
    New Context    storageState=${EXECDIR}/auth/user.json
    New Page    ${BASE_URL}
```

## Race Condition Fixes

```robotframework
# Wait for hydration / framework readiness
Wait For Elements State    [data-hydrated="true"]    attached    timeout=10s

# Use Promise To + Wait For for action + expected response
${promise}=    Promise To    Wait For Response    matcher=**/api/submit    timeout=10s
Click    ${submit_button}
${resp}=    Wait For    ${promise}

# Wait for animation/transition to complete
Wait For Elements State    ${dialog}    visible    timeout=5s
Wait For Elements State    .modal-animating    detached    timeout=5s
```

## Locator Fixes

```robotframework
# BAD: position-dependent, matches wrong element if order changes
Click    css=[role="listitem"] >> nth=0

# GOOD: scoped to container with unique content
${item}=    Get Element By Text    Specific Item
Click    ${item}

# GOOD: use test IDs for ambiguous elements
${cart_item}=    Get Element By Test Id    cart-item-sku-123
Click    ${cart_item}

# GOOD: scope to a region first, then find within
${main}=      Set Variable    css=main
${submit}=    Get Element By Role    button    name=Submit    parent=${main}
Click    ${submit}
```

## Environment Fixes

```robotframework
# Set explicit viewport in the context
New Context    viewport={'width': 1280, 'height': 720}

# Use timezone-agnostic assertions (match year only, not full date string)
Get Text    ${date_element}    matches    \\d{4}

# Block third-party scripts that interfere
Route URL    **/analytics/**    Abort
Route URL    **/chat-widget/**    Abort
```
