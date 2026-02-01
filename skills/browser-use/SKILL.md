---
name: browser-use
description: >
  Use when interacting with any website via agent-web-interface MCP tools. Reference for tool usage,
  XML response formats, selector extraction from get_element_details, form analysis patterns, and
  snapshot workflows.
user-invocable: false
---

# Browser Use Reference

## MCP Tools Overview

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

---

## Response Format Examples

### 1. State/Snapshot

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

**Key fields:**
- `id` attributes are eids for interaction
- `<region name="...">` indicates page section (nav, main, header, footer)

---

### 2. After Actions (click/type)

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

**Key fields:**
- `<diff>` shows what changed
- `<observations><appeared>` contains new visible text - **report these**
- Element attributes like `expanded`, `focused`, `checked` show state changes

---

### 3. get_element_details (Playwright Selectors)

```xml
<node eid="3e9a1da76faa" kind="button" label="Shopping Bag">
  <where region="nav" group_path="Global" heading="Quick Links" />
  <layout x="1100" y="0" w="30" h="44" zone="top-right" />
  <state visible="true" enabled="true" expanded="true" />
  <find primary="role=button[name=&quot;Shopping Bag&quot;]"
        alternates="#globalnav-menubutton-link-bag;[aria-label=&quot;Shopping Bag&quot;]" />
</node>
```

**Key fields:**
- `<find primary="...">` → **Playwright-compatible selector** (extract and report)
- `alternates` → semicolon-separated fallback selectors
- `<state>` → current element state

**Selector extraction:**
```
primary="role=button[name=&quot;Shopping Bag&quot;]"
→ Playwright: role=button[name="Shopping Bag"]
```

---

### 4. find_elements

```xml
<result type="find_elements" count="5">
  <match eid="b366be1381dd" kind="button" label="Store menu"
         region="nav" selector="role=button[name=&quot;Store menu&quot;]"
         visible="true" enabled="true" />
  <match eid="c7f9a2b3c4d5" kind="button" label="Search"
         region="nav" selector="role=button[name=&quot;Search&quot;]"
         visible="true" enabled="true" />
</result>
```

**Key fields:**
- `eid` for interaction
- `selector` attribute is Playwright-ready
- `region` for scope context

---

### 5. get_form_understanding

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

**Key fields:**
- `intent`: login, signup, search, checkout, contact, etc.
- `completion`: percentage of form filled
- `can_submit`: whether form is ready to submit
- `fields[purpose]`: name, email, password, phone, address, etc.
- `next_action`: suggested next field to interact with

---

### 6. get_field_context

```xml
<field_context eid="108">
  <field label="Username" kind="input" purpose="name" purpose_confidence="0.70">
    <purpose_signals>
      <signal>label contains "name"</signal>
    </purpose_signals>
    <state filled="false" valid="true" enabled="true" />
    <constraints required="false" />
  </field>
  <next_action eid="108" label="Username" reason="Optional field" />
</field_context>
```

**Key fields:**
- `purpose` + `purpose_confidence`: field type inference
- `purpose_signals`: why it inferred this purpose
- `constraints`: validation rules (required, pattern, etc.)

---

## Workflow Patterns

### Extract Playwright Selector for Element

1. Find element: `find_elements(kind="button", label="Submit")`
2. Get details: `get_element_details(eid="...")`
3. Extract: `<find primary="role=button[name=&quot;Submit&quot;]">`
4. Report: `role=button[name="Submit"]`

### Understand Form Before Filling

1. Analyze: `get_form_understanding()`
2. Check `intent` and `fields[purpose]`
3. Note `completion` and `can_submit`
4. Fill fields based on `purpose` (email, password, etc.)

### Track Action Effects

1. Perform action: `click(eid="...")`
2. Check response for `<observations><appeared>`
3. Report what appeared to user
4. Note state changes in element attributes

---

## Best Practices

1. **Action tools return snapshots** — `navigate`, `click`, `type` etc. already return fresh state; use `capture_snapshot` only when the page may have changed on its own (timers, live updates)
2. **Use get_element_details** to get Playwright selectors for any element you interact with
3. **Report `<appeared>` content** - these are user-visible changes
4. **Analyze forms** with get_form_understanding before filling
5. **Document blockers** (auth walls, captcha) in notes
6. **Extract selectors** using the `<find primary="...">` pattern
