# Network Interception and Error Path Testing

## Network Interception

Use Browser library's route-handling keywords to intercept and mock network requests for deterministic error testing.

**Mock server errors:**
```robotframework
Mock Checkout 500 Error
    Route URL    **/api/checkout
    ...    Response    status=500    body={"error": "Payment declined"}
```

**Abort a request (network timeout / offline):**
```robotframework
Simulate Network Timeout
    Route URL    **/api/orders    Abort
```

**Patch real responses (modify, don't replace):**
```robotframework
Reduce Products To One Item
    Route URL    **/api/products    Patch Response
    ...    body_transform=reduce_results_to_one
```

(Patch transforms are typically defined in a Python module imported via `Library    patches.py` — Browser library's `Route URL` supports a callback when you need to mutate the response body.)

**Assert backend was called:**
```robotframework
Place Order And Verify API Call
    ${promise}=    Promise To    Wait For Response
    ...    matcher=**/api/order    timeout=10s
    ${submit}=    Get Element By Role    button    name=Place order
    Click    ${submit}
    ${response}=    Wait For    ${promise}
    Should Be Equal As Integers    ${response}[status]    201
```

**Block heavy resources to speed up tests:**
```robotframework
Block Images
    Route URL    **/*.{png,jpg,jpeg,gif,svg}    Abort
```

Apply `Route URL` before the navigation that triggers the request (typically in `[Setup]` or at the top of the test body).

## Error Path Testing

Every feature needs error path tests. Use route mocking (see above) to simulate failures. At minimum, every feature suite should cover:

- **Server error** — `Route URL    **/api    Response    status=500    body=...` — verify error UI appears
- **Aborted request** — `Route URL    **/api    Abort` — verify retry option or error message
- **Empty state** — `Route URL    **/api/items    Response    status=200    body={"items": []}` — verify empty state UI

```robotframework
TC-DASHBOARD-005 Shows empty state when no data
    [Documentation]    Dashboard renders empty state when API returns no items.
    Route URL    **/api/items    Response    status=200    body={"items": []}
    Go To    ${BASE_URL}/dashboard
    ${empty_state}=    Get Element By Role    status    name=No items
    Get Element States    ${empty_state}    *=    visible
```
