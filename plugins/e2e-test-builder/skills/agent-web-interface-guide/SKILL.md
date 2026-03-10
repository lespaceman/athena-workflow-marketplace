---
name: agent-web-interface-guide
description: >
  REQUIRED for any task that involves opening, visiting, or viewing a live web page in a browser with
  the agent-web-interface MCP server. Use this skill whenever the user includes a URL or page reference
  and wants to see, check, verify, inspect, extract selectors from, or interact with that page. This
  skill combines live browser exploration with the operational guide for agent-web-interface response
  patterns, state snapshots, forms, selectors, and multi-page recovery. If you are about to call any
  mcp__plugin_e2e-test-builder_agent-web-interface__* tool directly, load this skill first.
user-invocable: true
argument-hint: <url> <what to explore or do>
allowed-tools:
  - mcp__plugin_e2e-test-builder_agent-web-interface__ping
  - mcp__plugin_e2e-test-builder_agent-web-interface__navigate
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_back
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_forward
  - mcp__plugin_e2e-test-builder_agent-web-interface__reload
  - mcp__plugin_e2e-test-builder_agent-web-interface__snapshot
  - mcp__plugin_e2e-test-builder_agent-web-interface__find
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_element
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_to
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll
  - mcp__plugin_e2e-test-builder_agent-web-interface__click
  - mcp__plugin_e2e-test-builder_agent-web-interface__type
  - mcp__plugin_e2e-test-builder_agent-web-interface__press
  - mcp__plugin_e2e-test-builder_agent-web-interface__select
  - mcp__plugin_e2e-test-builder_agent-web-interface__hover
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_form
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_field
  - mcp__plugin_e2e-test-builder_agent-web-interface__list_pages
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_session
  - mcp__plugin_e2e-test-builder_agent-web-interface__screenshot
---

# agent-web-interface MCP Server Guide

This skill documents how to work with the `agent-web-interface` MCP server, which provides browser automation tools (`navigate`, `click`, `type`, `find`, `get_form`, etc.) for web exploration, form filling, and UI interaction.

## Input

Parse the target URL and exploration goal from: $ARGUMENTS

## Workflow

1. **Navigate** to the URL
2. **Complete the task** — interact as needed (click, fill forms, navigate pages)
3. **Extract selectors** — use `get_element` on key elements to capture the best Playwright selector
4. **Analyze forms** — use `get_form` and `get_field` to understand intent, completion state, and validation
5. **Report** what you did, found, and observed

## Output Format

Always include:
1. **What you accomplished** — the result, finding, or outcome
2. **Steps taken** — pages visited, buttons clicked, forms filled
3. **Observations** — notable page states, messages, and behaviors
4. **Selectors** (when relevant) — Playwright-compatible selectors for key elements

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
  <!-- trimmed 50 items. Use find with region=main to see all -->
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
- `<!-- trimmed N items -->` - Use `find` with `region` filter to see all

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

## find Response

```xml
<result type="find" page_id="..." snapshot_id="..." count="N">
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

## get_element Response

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

## get_form Response

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

## Session Recovery

The browser persists across conversation sessions — tabs from prior sessions remain open. On a new session, there is no "current" page; actions without `page_id` may target an arbitrary tab.

When encountering a "no page/session" error or resuming from a prior session:

1. Call `list_pages` to see all open tabs with `page_id`, URL, and title
2. Identify the target page by URL or title
3. Pass `page_id` explicitly to all subsequent calls (`snapshot`, `find`, `click`, etc.)
4. If the page is not found, navigate fresh — the tab may have been closed

**Caveats:**
- **Stale tab URLs**: `list_pages` shows the URL at open time. For SPAs, use `snapshot` with `page_id` to see actual current state.
- **Tab accumulation**: The browser accumulates tabs across sessions. Always use `page_id` to target the correct one.
- **`close_session`** closes the entire browser. Use `close_page` to close individual tabs.

## Error Responses

```xml
<error>Field not found in any form: abc123</error>
```

Common errors:
- Element ID not found (page may have changed)
- Element not visible/enabled
- Form field not in any form context
- No page/session (see Session Recovery above)

## Canvas Interactions

`<canvas>` elements render pixels, not DOM nodes — standard selectors don't work inside them. Use these tools for canvas-based UIs (drawing apps, games, visualizations):

- **`inspect_canvas`** — the key tool. Pass a canvas `eid` and it auto-detects the rendering library (Fabric.js, Konva, PixiJS, Phaser, Three.js, EaselJS, or raw canvas), queries the scene graph for objects with positions/sizes/labels, and returns an annotated screenshot with coordinate grid overlay and bounding boxes. Supports configurable `grid_spacing` (use 10px for precise handle targeting).
- **`click`** with `eid` + `x`/`y` — click at offset relative to canvas top-left (e.g., select a shape)
- **`drag`** with `eid` + source/target coordinates — drag within canvas (e.g., move objects, scale/rotate handles)
- **`screenshot`** with `eid` — capture just the canvas to visually verify state

**Workflow:** `find` → `get_element` (position) → `inspect_canvas` (discover objects) → `click`/`drag` (interact) → re-inspect to verify.

## Best Practices

1. **Use `find`** when snapshot shows `<!-- trimmed -->`
2. **Track `<baseline>` vs `<diff>`** to know if you have full or partial state
3. **Always pass `page_id`** when working across sessions or with multiple tabs

## Example Usage

```
Claude Code: /agent-web-interface-guide https://airbnb.com Walk through the search and booking flow for stays in Tokyo
Codex: $agent-web-interface-guide https://airbnb.com Walk through the search and booking flow for stays in Tokyo

Claude Code: /agent-web-interface-guide https://apple.com/store Find the iPhone purchase flow and extract all form selectors
Codex: $agent-web-interface-guide https://apple.com/store Find the iPhone purchase flow and extract all form selectors

Claude Code: /agent-web-interface-guide https://example.com/login Extract the login form selectors and field purposes
Codex: $agent-web-interface-guide https://example.com/login Extract the login form selectors and field purposes
```
