---
name: explore-website
description: >
  This skill should be used when the user asks to "explore a website", "browse a page", "navigate a site",
  "interact with a web app", "extract selectors from a page", "fill out a form on a website", or provides
  a URL and wants live browser interaction, selector extraction, or form analysis.
user-invocable: true
argument-hint: <url> <what to explore or do>
allowed-tools:
  - mcp__agent-web-interface__ping
  - mcp__agent-web-interface__navigate
  - mcp__agent-web-interface__go_back
  - mcp__agent-web-interface__go_forward
  - mcp__agent-web-interface__reload
  - mcp__agent-web-interface__capture_snapshot
  - mcp__agent-web-interface__find_elements
  - mcp__agent-web-interface__get_element_details
  - mcp__agent-web-interface__scroll_element_into_view
  - mcp__agent-web-interface__scroll_page
  - mcp__agent-web-interface__click
  - mcp__agent-web-interface__type
  - mcp__agent-web-interface__press
  - mcp__agent-web-interface__select
  - mcp__agent-web-interface__hover
  - mcp__agent-web-interface__get_form_understanding
  - mcp__agent-web-interface__get_field_context
  - mcp__agent-web-interface__list_pages
  - mcp__agent-web-interface__close_page
  - mcp__agent-web-interface__close_session
---

# Explore Website

Explore and interact with a live website using a browser, reporting observations, extracting Playwright selectors, and analyzing forms.

## Workflow

1. **Parse the input** — extract the target URL and exploration goal from the arguments: $ARGUMENTS
2. **Launch the web-explorer agent** — use the Task tool to invoke the `web-explorer` agent with the URL and goal
3. **The agent will**:
   - Navigate to the URL and interact as a real user would
   - Use structured accessibility-tree snapshots to understand page structure
   - Extract Playwright-compatible selectors via `get_element_details`
   - Analyze forms with `get_form_understanding` and `get_field_context`
   - Report observations from `<appeared>` tags and state diffs
   - Note blockers (auth walls, CAPTCHA, geo restrictions)
4. **Output** — the agent returns a structured exploration report with selectors, form insights, and recommendations

## Example Usage

```
/explore-website https://airbnb.com Walk through the search and booking flow for stays in Tokyo
```

```
/explore-website https://apple.com/store Find the iPhone purchase flow and extract all form selectors
```

```
/explore-website https://example.com/login Extract the login form selectors and field purposes
```

## MCP Tools Reference

| Tool | Purpose | Key Response Elements |
|------|---------|----------------------|
| `navigate` | Go to URL | Returns snapshot with regions, elements |
| `capture_snapshot` | Re-capture page state (use when page changed on its own) | `<state>` with full structure |
| `click` | Click element by eid | Returns updated snapshot with `<diff>`, `<observations>` |
| `type` | Enter text | Returns updated snapshot with state changes |
| `find_elements` | Search for elements by kind/label/region | `<match selector="...">` per result |
| `get_element_details` | Full element info + Playwright selectors | `<find primary="..." alternates="...">` |
| `get_form_understanding` | Form analysis | `intent`, `completion`, `fields[purpose]`, `next_action` |
| `get_field_context` | Field details | `purpose`, `purpose_confidence`, `constraints` |
| `scroll_page` | Scroll viewport up/down | Returns updated snapshot |
| `scroll_element_into_view` | Scroll element into viewport | Use before interacting with off-screen elements |
| `list_pages` | List open browser pages | Page IDs, URLs, titles |
| `close_page` / `close_session` | Close page or entire session | Cleanup |

## Response Format Examples

### State/Snapshot

After `navigate` or `capture_snapshot`:

```xml
<state step="2" title="Apple Store Online" url="https://www.apple.com/store">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <baseline reason="first" />
  <region name="nav">
    <link id="478e4edc6d2d" href="/iphone/">iPhone</link>
    <btn id="3e9a1da76faa">Shopping Bag</btn>
  </region>
  <region name="main">
    <link id="cd1f7f982cc5" href="/shop/buy-iphone/iphone-17-pro">iPhone 17 Pro</link>
  </region>
</state>
```

### After Actions (click/type)

```xml
<state step="3" title="..." url="...">
  <diff type="mutation" added="4" />
  <observations>
    <appeared when="action">Your Bag is empty. Sign in to see saved items</appeared>
  </observations>
  <region name="nav">
    <btn id="3e9a1da76faa" expanded="true" focused="true">Shopping Bag</btn>
  </region>
</state>
```

### get_element_details (Playwright Selectors)

```xml
<node eid="3e9a1da76faa" kind="button" label="Shopping Bag">
  <where region="nav" group_path="Global" heading="Quick Links" />
  <layout x="1100" y="0" w="30" h="44" zone="top-right" />
  <state visible="true" enabled="true" expanded="true" />
  <find primary="role=button[name=&quot;Shopping Bag&quot;]"
        alternates="#globalnav-menubutton-link-bag;[aria-label=&quot;Shopping Bag&quot;]" />
</node>
```

### find_elements

```xml
<result type="find_elements" count="5">
  <match eid="b366be1381dd" kind="button" label="Store menu"
         region="nav" selector="role=button[name=&quot;Store menu&quot;]"
         visible="true" enabled="true" />
</result>
```

### get_form_understanding

```xml
<form_understanding>
  <form id="form-ddd3e113" intent="login" pattern="single_page" confidence="0.49">
    <state completion="0%" can_submit="false" errors="0" />
    <fields count="2">
      <field eid="108" label="Username" kind="input" purpose="name"
             filled="false" enabled="true" />
      <field eid="113" label="Password" kind="input" purpose="password"
             filled="false" enabled="true" />
    </fields>
    <next_action eid="108" label="Username" reason="Optional field" />
  </form>
</form_understanding>
```

## Best Practices

1. **Action tools return snapshots** — `navigate`, `click`, `type` etc. already return fresh state; use `capture_snapshot` only when the page may have changed on its own (timers, live updates)
2. **Use get_element_details** to get Playwright selectors for any element you interact with
3. **Report `<appeared>` content** - these are user-visible changes
4. **Analyze forms** with get_form_understanding before filling
5. **Document blockers** (auth walls, captcha) in notes
6. **Extract selectors** using the `<find primary="...">` pattern
