---
name: browser-journey-recording
description: Patterns and schemas for recording browser journeys. Reference for JSON output format, confidence scoring, target specifications, and MCP tool usage.
user-invocable: false
allowed_tools:
  - mcp__athena-browser-mcp__launch_browser
  - mcp__athena-browser-mcp__connect_browser
  - mcp__athena-browser-mcp__close_session
  - mcp__athena-browser-mcp__navigate
  - mcp__athena-browser-mcp__go_back
  - mcp__athena-browser-mcp__click
  - mcp__athena-browser-mcp__type
  - mcp__athena-browser-mcp__select
  - mcp__athena-browser-mcp__press
  - mcp__athena-browser-mcp__hover
  - mcp__athena-browser-mcp__capture_snapshot
  - mcp__athena-browser-mcp__scroll_page
  - mcp__athena-browser-mcp__scroll_element_into_view
  - mcp__athena-browser-mcp__find_elements
  - mcp__athena-browser-mcp__get_node_details
  - mcp__athena-browser-mcp__get_form_understanding
  - mcp__athena-browser-mcp__get_field_context
---

# Browser Journey Recording Reference

## MCP Tools Reference

| Tool | Purpose |
|------|---------|
| `launch_browser` | Start a browser session |
| `navigate` | Go to URL directly |
| `capture_snapshot` | Get full page state and structure |
| `find_elements` | Find elements by kind, label, or region |
| `get_node_details` | Get detailed element info |
| `click` | Click elements by eid |
| `type` | Enter text into fields |
| `select` | Select dropdown options |
| `press` | Press keyboard keys (Enter, Tab, Escape, etc.) |
| `hover` | Hover over elements |
| `scroll_page` | Scroll to reveal content |
| `scroll_element_into_view` | Scroll specific element visible |
| `get_form_understanding` | Analyze form structure |
| `close_session` | End browser session |

---

## JSON Output Schema

```json
{
  "goal": "Add iPhone 16 Pro to cart",
  "start_url": "https://www.apple.com/store",
  "steps": [
    {
      "id": "s1",
      "action": "goto",
      "target": null,
      "value": "https://www.apple.com/store",
      "observed": ["page loaded", "Apple Store header visible"],
      "confidence": 1.0
    },
    {
      "id": "s2",
      "action": "click",
      "target": {
        "kind": "role",
        "value": "link name~iPhone",
        "scope": "nav"
      },
      "observed": ["url changed to /iphone", "iPhone product grid visible"],
      "confidence": 0.95
    },
    {
      "id": "s3",
      "action": "fill",
      "target": {
        "kind": "role",
        "value": "textbox name~Email",
        "scope": "main"
      },
      "value": "test@example.com",
      "observed": ["input value set", "validation passed"],
      "confidence": 0.9
    }
  ],
  "final_state": ["Cart badge shows '1'", "Total displayed"],
  "notes": ["Modal dismissed on first visit", "Site uses dynamic pricing"]
}
```

---

## Step IDs

Use sequential, stable IDs: `s1`, `s2`, `s3`, ...

---

## Target Specification

### `target.kind`

| Kind | Value Pattern | Example |
|------|--------------|---------|
| `role` | `{role} name~{text}` | `"link name~iPhone"`, `"button name~Add to Bag"` |
| `role` | `{role} name~{text}` (radio) | `"radio name~256GB"` |
| `role` | `{role} name~{text}` (textbox) | `"textbox name~Email"` |
| `label` | `{label text}` | `"Email address"` |
| `text` | `{visible text}` | `"Continue to checkout"` |
| `testid` | `{data-testid value}` | `"checkout-button"` |

### `target.scope`

| Scope | Description |
|-------|-------------|
| `page` | Entire page (default) |
| `header` | Page header region |
| `main` | Main content area |
| `nav` | Navigation region |
| `dialog` | Modal or dialog |
| `footer` | Page footer |

---

## Observed Effects Requirements

Every step MUST include at least one concrete observation:

| Type | Examples |
|------|----------|
| URL change | `"url changed to /checkout"` |
| Text appearance | `"confirmation text 'Added to bag' visible"` |
| State change | `"radio button 256GB now checked"` |
| Counter update | `"cart badge shows '1'"` |
| Element visibility | `"checkout button now enabled"` |
| Content load | `"product grid with 12 items visible"` |

---

## Confidence Scoring

| Score | Meaning |
|-------|---------|
| `1.0` | Action succeeded with unambiguous evidence |
| `0.8-0.9` | Action likely succeeded, strong but not definitive evidence |
| `0.6-0.7` | Action may have succeeded, evidence is indirect |
| `<0.6` | Uncertain - document in notes, consider alternatives |

---

## Failure Handling Patterns

### Retry Strategies

1. **Element not found**: Scroll page, wait, then retry `find_elements`
2. **Click no effect**: Try alternative target (different selector, nearby element)
3. **Modal/popup blocking**: Dismiss it first, document in notes
4. **Dynamic content**: Wait for content to load with `capture_snapshot`

### When to Stop

- Cannot reliably complete a step after 2-3 retries
- Required element never appears
- Site requires authentication not provided

### Recording Failures

```json
{
  "id": "s5",
  "action": "click",
  "target": { "kind": "role", "value": "button name~Submit", "scope": "main" },
  "observed": ["button clicked but no response"],
  "confidence": 0.4
}
```

Add explanation in `notes`: `"Submit button may require login"`

---

## Best Practices

1. **Always capture_snapshot** after navigation or significant actions
2. **Use find_elements** with specific filters (kind + label) for accurate targeting
3. **Prefer main region** over header/footer for primary actions
4. **Document popups/modals** that appear unexpectedly
5. **Note scroll requirements** if elements need scrolling to become visible
6. **Keep JSON minimal** - no commentary outside the JSON structure
7. **Semantic targets only** - never use CSS selectors or XPath
