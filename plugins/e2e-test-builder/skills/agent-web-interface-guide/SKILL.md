---
name: agent-web-interface-guide
description: Guide to using the agent-web-interface MCP server for browser automation - understanding state snapshots, element interactions, form handling, and response patterns
user-invocable: false
---

# agent-web-interface MCP Server Guide

This skill documents how to work with the `agent-web-interface` MCP server, which provides browser automation tools (`navigate`, `click`, `type`, `find_elements`, `get_form_understanding`, etc.) for web exploration, form filling, and UI interaction.

## State Snapshot Structure

Every navigation or action returns a `<state>` snapshot:

```xml
<state step="N" title="Page Title" url="https://...">
  <meta view="1521x752" scroll="0,0" layer="main" />
  <baseline reason="first|navigation" />
  <diff type="mutation" added="N" removed="N" />
  <observations>...</observations>
  <region name="main">...</region>
</state>
```

### Key Elements

| Element | Purpose |
|---------|---------|
| `<meta>` | Viewport size, scroll position, active layer |
| `<baseline reason="...">` | Fresh snapshot - `"first"` (initial load) or `"navigation"` (URL change) |
| `<diff type="mutation">` | Incremental update with `added`/`removed` counts |
| `<observations>` | What appeared/disappeared after the action |
| `<region>` | Semantic page areas with interactive elements |

## Observations

After actions (click, type, select), watch for changes:

```xml
<observations>
  <appeared when="action">Your Bag is empty</appeared>
  <appeared when="action" role="status"></appeared>
  <disappeared when="action" role="status"></disappeared>
</observations>
```

- `<appeared>`: New content visible after action
- `<disappeared>`: Content removed after action
- `role` attribute: Semantic role (status, alert, dialog)

## Regions

Page content is organized into semantic regions:

```xml
<region name="main">
  <link id="..." href="...">Link text</link>
  <btn id="...">Button text</btn>
  <!-- trimmed 50 items. Use find_elements with region=main to see all -->
</region>
<region name="nav" unchanged="true" count="90" />
```

### Region Types
- `main` - Primary content area
- `nav` - Navigation menus
- `header` - Page header
- `footer` - Page footer
- `form` - Form containers
- `aside` - Sidebars
- `search` - Search areas

### Optimization Hints
- `unchanged="true" count="N"` - Region didn't change, shows element count
- `<!-- trimmed N items -->` - Use `find_elements` with `region` filter to see all

## Element Types in Snapshots

| Tag | Element | Key Attributes |
|-----|---------|----------------|
| `<link>` | Hyperlink | `id`, `href` |
| `<btn>` | Button | `id`, `val`, `enabled` |
| `<rad>` | Radio button | `id`, `val`, `checked`, `focused` |
| `<sel>` | Dropdown/select | `id`, `expanded`, `focused` |
| `<elt>` | Input/generic | `id`, `type`, `val`, `focused`, `enabled`, `selected` |

### Common Attributes

| Attribute | Meaning |
|-----------|---------|
| `id` | Element ID (eid) - use this to target the element |
| `enabled="false"` | Element is disabled (common in sequential forms) |
| `checked="true"` | Radio/checkbox is selected |
| `focused="true"` | Element has keyboard focus |
| `expanded="true"` | Dropdown is open |
| `selected="true"` | Option/tab is selected |
| `val` | Element value |

## Sequential Form Pattern

Many sites (especially Apple Store) use sequential enablement - options are disabled until prerequisites are selected:

```xml
<!-- Step 1: Model selection enabled -->
<rad id="model1" val="pro">iPhone 17 Pro</rad>
<rad id="color1" enabled="false" val="silver">Silver</rad>  <!-- disabled -->

<!-- After selecting model, colors become enabled -->
<rad id="model1" checked="true" val="pro">iPhone 17 Pro</rad>
<rad id="color1" val="silver">Silver</rad>  <!-- now enabled -->
```

**Strategy**: Check for `enabled="false"` and work through the form sequentially.

## find_elements Response

```xml
<result type="find_elements" page_id="..." snapshot_id="..." count="N">
  <match eid="abc123"
         kind="button|link|radio|checkbox|textbox|combobox|heading|image"
         label="Button text"
         region="main|nav|header|footer"
         selector="role=button[name=&quot;...&quot;]"
         visible="true"
         enabled="true"
         href="..." />
</result>
```

### Filter Parameters
- `kind`: Element type filter
- `label`: Case-insensitive substring match
- `region`: Restrict to semantic area
- `limit`: Max results (default 10)
- `include_readable`: Include text content (default true)

## get_element_details Response

```xml
<node eid="abc123" kind="link" region="main" group="tbody-28"
      x="147.875" y="11.5" w="97.97" h="16.5"
      display="inline" zone="top-left">
  Element label text
  <selector primary='role=link[name="..."]' />
  <attrs href="..." />
</node>
```

- `primary`: Best Playwright selector
- Position info: `x`, `y`, `w`, `h`, `zone`
- `group`: Logical grouping (for tables, lists)

## get_form_understanding Response

```xml
<forms page="page-id">
  <form id="form-xxx" intent="search|login|signup|checkout" completion="100%">
    <input eid="748" purpose="search">Search Wikipedia</input>
    <combobox eid="750" purpose="selection" filled="true">EN</combobox>
    <button eid="820" type="submit" primary="true">Search</button>
    <next eid="748" reason="Optional field" />
  </form>
</forms>
```

- `intent`: Form purpose (search, login, checkout, etc.)
- `completion`: Percentage filled
- `next`: Suggested next field to fill with reason

## list_pages Response

```xml
<result type="list_pages" status="success">
  <pages count="N">
    <page page_id="page-xxx" url="https://..." title="Page Title" />
  </pages>
</result>
```

Use `page_id` to target specific browser tabs.

## Action Response Patterns

### After Click/Type (mutation)
```xml
<state step="N" ...>
  <diff type="mutation" added="2" removed="1" />
  <observations>
    <appeared when="action">New content</appeared>
  </observations>
  <region name="main">
    <!-- Only changed elements shown -->
  </region>
</state>
```

### After Navigation
```xml
<state step="N" title="New Page" url="https://new-url">
  <baseline reason="navigation" />
  <!-- Full page snapshot -->
</state>
```

## Session Recovery

The MCP server uses a persistent browser that survives across conversation sessions. Pages opened in previous sessions remain as open tabs. This means:

- **No active page on new session**: When starting a new conversation, there is no "current" page. Calling `capture_snapshot` or actions without `page_id` may target an arbitrary tab from a prior session — not the page expected.
- **"No page/session" errors**: If the MCP reports no page or session exists, this does not mean the browser is dead. It means no page is currently targeted.

### Recovery Strategy

When encountering a "no page/session" error or when resuming work from a prior session:

1. **Call `list_pages`** to see all open tabs with their `page_id`, URL, and title
2. **Identify the target page** by matching the URL or title
3. **Pass `page_id` explicitly** to subsequent tool calls (`capture_snapshot`, `find_elements`, `click`, etc.) to target the correct tab
4. **If the page is not found**, navigate fresh — the tab may have been closed or the browser restarted

### Important Behaviors

- **Tab URLs may be stale**: `list_pages` shows the URL at the time the tab was opened. If in-page navigation occurred (e.g., clicking links within a single-page app or Wikipedia), the listed URL may not reflect the current page content. Use `capture_snapshot` with the `page_id` to see actual current state.
- **Many tabs may exist**: The persistent browser accumulates tabs across sessions (37+ tabs observed in testing). Always use `page_id` to target the correct one rather than relying on default tab selection.
- **`close_session`** closes the entire browser and all tabs. Use `close_page` to close individual tabs without affecting others.

### Example: Resuming a Previous Session

```
# 1. No active page — check what's open
list_pages
# Returns: page-abc123 url="https://example.com" title="Example"

# 2. Target the specific page
capture_snapshot(page_id="page-abc123")
# Returns current state of that tab

# 3. Continue interacting with page_id
click(eid="some-element", page_id="page-abc123")
```

## Error Responses

```xml
<error>Field not found in any form: abc123</error>
```

Common errors:
- Element ID not found (page may have changed)
- Element not visible/enabled
- Form field not in any form context
- No page/session (see Session Recovery above)

## Best Practices

1. **Check `enabled` attribute** before clicking disabled elements
2. **Use `find_elements`** when snapshot shows `<!-- trimmed -->`
3. **Watch `<observations>`** to understand action effects
4. **Use `region` filter** to narrow searches in large pages
5. **Handle sequential forms** by checking which options become enabled
6. **Track `<baseline>` vs `<diff>`** to know if you have full or partial state
7. **Always pass `page_id`** when working across sessions or with multiple tabs
8. **Use `list_pages` first** when starting a new session to discover existing tabs
