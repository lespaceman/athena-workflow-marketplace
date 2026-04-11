# Mapping Tables

Standard translations for converting journey specs and exploration results to Browser library keywords.

## Scope-to-Locator

| Journey Scope | Browser Library Scoping |
|---------------|------------------------|
| `page` | No scoping needed |
| `header` | `header >> ...` |
| `main` | `main >> ...` |
| `nav` | `nav >> ...` |
| `dialog` | `[role="dialog"] >> ...` |

`>>` is Browser library's chain combinator — scope a parent container first, then chain the target locator after it.

## Action-to-Keyword

| Journey Action | Browser Library Keyword |
|----------------|------------------------|
| `goto` | `Go To    ${url}` |
| `click` | `Click    <locator>` |
| `fill` | `Fill Text    <locator>    ${value}` |
| `fill secret` | `Fill Secret    <locator>    $VAR` |
| `select` | `Select Options By    <locator>    value    ${value}` |
| `check` | `Check Checkbox    <locator>` |
| `hover` | `Hover    <locator>` |
| `assert visible` | `Get Element States    <locator>    *=    visible` |

## Assertion Mapping

| Observed Effect | Browser Library Assertion |
|----------------|--------------------------|
| `url changed to /cart` | `Get Url    contains    /cart` |
| `text 'Added' visible` | `Get Text    role=alert    contains    Added` |
| `radio 256GB checked` | `Get Checkbox State    role=radio[name="256GB"]    ==    checked` |
| `button now enabled` | `Get Element States    <locator>    *=    enabled` |
| `element count is N` | `Get Element Count    <locator>    ==    ${N}` |

## Target Kind to Locator

| Target Kind | Value Pattern | Browser Library Locator |
|-------------|--------------|------------------------|
| `role` | `button name~Add to Bag` | `role=button[name="Add to Bag"]` |
| `role` | `radio name~256GB` | `role=radio[name="256GB"]` |
| `label` | `Email address` | `label=Email address` |
| `testid` | `checkout-button` | `[data-testid="checkout-button"]` |
| `text` | `Welcome back` | `text="Welcome back"` or `text=/welcome/i` |

## Low Confidence Handling (<0.7)

When journey step confidence is low:
1. Add extra assertions to verify state
2. Include fallback locators in comments
3. Consider keyword-level retry via `Wait For Elements State` instead of a single-shot action

```robotframework
# Primary locator (fallback: label=256GB)
${storage_radio}=    Set Variable    role=radio[name="256GB"]
Click    ${storage_radio}
Get Checkbox State    ${storage_radio}    ==    checked    timeout=5s
```
