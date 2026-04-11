# API-Driven Test Setup and Teardown

## API-Driven Test Setup

Use `RequestsLibrary` to set up test data instead of clicking through UI. This is 10-50x faster and more reliable.

**When to use API setup:** Creating test users, products, orders, seed data. Setting feature flags. Resetting state between tests.

**When to use UI setup:** Only when the creation flow IS the test being verified.

```robotframework
*** Settings ***
Library    Browser
Library    RequestsLibrary
Library    Collections

*** Keywords ***
Seed Cart
    [Arguments]    ${sku}    ${quantity}
    Create Session    api    ${API_BASE_URL}    headers=&{API_HEADERS}
    ${resp}=    POST On Session    api    /cart/items
    ...    json=&{{'productId': '${sku}', 'quantity': ${quantity}}}
    Should Be Equal As Integers    ${resp.status_code}    201
    RETURN    ${resp.json()['id']}

*** Test Cases ***
TC-CART-001 User sees items in cart
    [Documentation]    Cart page renders seeded items.
    ${item_id}=    Seed Cart    SKU-123    2
    Go To    ${BASE_URL}/cart
    ${items}=    Set Variable    css=[role="listitem"]
    Get Element Count    ${items}    ==    2
```

Put `Create Session` and reusable keywords in `resources/api.resource` so every suite imports them once.

## Reusable API session pattern

```robotframework
*** Keywords ***
Authenticated Session
    ${headers}=    Create Dictionary    Authorization=Bearer %{API_TOKEN}
    Create Session    api    %{API_BASE_URL}    headers=${headers}
    RETURN    api
```

Call `Authenticated Session` from `Suite Setup` and reuse the returned alias across keywords.

## Test Data Teardown

Tests that create persistent data (database records, uploaded files, user accounts) MUST clean up after themselves. Leaked test data accumulates across runs and causes false positives/negatives in other tests (pagination counts drift, filter results change, list assertions break).

### Strategy 1: `[Teardown]` with API cleanup (Recommended)

```robotframework
*** Test Cases ***
TC-TICKET-001 User can create a ticket
    ${ticket_id}=    Create Ticket Via API    title=Test ${{time.time_ns()}}
    Set Test Variable    ${CREATED_TICKET_ID}    ${ticket_id}
    Go To    ${BASE_URL}/tickets
    ${ticket}=    Get Element By Test Id    ticket-${ticket_id}
    Get Text    ${ticket}    contains    Test
    [Teardown]    Delete Ticket Via API    ${CREATED_TICKET_ID}
```

### Strategy 2: Suite Teardown for bulk cleanup

When tests share a data scope, clean up once at the end:

```robotframework
*** Settings ***
Suite Setup       Seed Suite Data
Suite Teardown    Run Keywords
...    Delete All Suite Data
...    AND    Close Browser
```

### Strategy 3: Global cleanup via listener or `__init__.robot`

For environments where individual deletion is impractical, tag test data (e.g., `title LIKE 'Test %'`) and delete in batch from a suite-level `__init__.robot` teardown or a listener's `end_suite` hook.

If the cleanup API endpoint is unknown, do not invent one. Leave a clear `TODO` with the missing endpoint details, document the cleanup gap in the suite documentation or working notes, and prefer `[Teardown]` or environment-reset strategies that you can verify. If cleanup is genuinely impossible (no API, no database access), document this as a known limitation at the top of the suite AND add a `[Teardown]` that logs a warning via `Log    Known leaked data: <id>    WARN`.
