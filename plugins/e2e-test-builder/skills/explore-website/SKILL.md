---
name: explore-website
description: >
  REQUIRED for any task that involves opening, visiting, or viewing a live web page in a browser.
  This is the ONLY skill with browser access. Invoke this skill BEFORE any other skill whenever the
  user's request includes a URL or page reference AND wants to see, check, verify, inspect, or interact
  with that page. Common patterns: viewing page content or layout, checking if a page loads, logging
  into a site, extracting form fields or selectors, verifying behavior after a change, or understanding
  a page before writing tests. If the user mentions a localhost URL or asks you to "look at", "go to",
  "open", "browse to", "check", "take a look at", "investigate", or "verify" any web page, use this
  skill. IMPORTANT: If you are about to call any mcp__plugin_e2e-test-builder_agent-web-interface__*
  tool directly, load this skill first — it provides structured browser interaction patterns that prevent
  ad-hoc clicking. Does NOT write test code or generate test specs — use write-e2e-tests or
  generate-test-cases for those.
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

# Explore Website

Explore and interact with a live website using the browser, reporting observations, extracting Playwright selectors, and analyzing forms.

## Input

Parse the target URL and exploration goal from: $ARGUMENTS

## Workflow

1. **Navigate** to the URL
2. **Complete the task** — interact as needed (click, fill forms, navigate pages)
3. **Extract selectors** — use `get_element` on key elements to get the `primary` Playwright selector from the `<find primary="...">` attribute
4. **Analyze forms** — use `get_form` to understand form intent, fields, completion state, and suggested next actions
5. **Report** what you did, found, and observed

## Browser Operation Principles

- **Action tools return fresh snapshots** — `navigate`, `click`, `type` etc. already return state; only use `snapshot` when the page may have changed on its own (timers, live updates)
- **Use `find`** when a snapshot shows `<!-- trimmed N items -->` — filter by `kind`, `label`, or `region`
- **Check `enabled` attribute** before clicking — sequential forms disable options until prerequisites are selected
- **Watch `<observations>`** — `<appeared>` and `<disappeared>` tags show what changed after actions
- **Use `region` filter** to narrow searches: `main`, `nav`, `header`, `footer`
- **Report blockers** (login walls, CAPTCHA, payment gateways, geo-restrictions) clearly and stop

## Selector Extraction

Use `get_element` with the element's eid to get Playwright-compatible selectors:

```xml
<node eid="abc123" kind="button" label="Shopping Bag">
  <find primary="role=button[name=&quot;Shopping Bag&quot;]"
        alternates="#globalnav-menubutton-link-bag;[aria-label=&quot;Shopping Bag&quot;]" />
</node>
```

The `primary` attribute is the best Playwright locator. Record alternates as fallbacks.

## Accessibility Observation

When exploring, note accessibility-relevant patterns:
- **Focus order**: Tab through interactive elements and note if focus order is logical
- **ARIA landmarks**: Check for `role="main"`, `role="navigation"`, `role="banner"` using `find`
- **Dynamic content announcements**: After actions (form submit, modal open), check for `aria-live` regions in observations
- **Form labels**: Note any inputs without visible labels or `aria-label` — use `get_field` to check
- **Error association**: When form validation triggers, check if errors are linked to fields via `aria-describedby`
- **Heading hierarchy**: Use `find` with `kind: "heading"` to verify h1 > h2 > h3 (no level skips)

## Form Validation Discovery

When exploring forms, systematically trigger validation to document error patterns:
1. **Submit the form empty** — observe which fields show required-field errors and what messages appear
2. **Enter invalid formats** — wrong email, short password, letters in number fields — note inline validation messages
3. **Note WHERE errors appear** — inline under field, toast notification, summary banner at top of form
4. **Note WHEN errors appear** — on blur (leaving field), on submit, on keypress (real-time)
5. **Record exact error message text** — these are used for assertion writing in test code

## Output Format

Always include:
1. **What you accomplished** — the result, finding, or outcome
2. **Steps taken** — pages visited, buttons clicked, forms filled
3. **Observations** — notable page states, messages, behaviors
4. **Selectors** (when relevant) — Playwright-compatible selectors for key elements

## Example Usage

```
/explore-website https://airbnb.com Walk through the search and booking flow for stays in Tokyo
/explore-website https://apple.com/store Find the iPhone purchase flow and extract all form selectors
/explore-website https://example.com/login Extract the login form selectors and field purposes
```

## Context-Saving Strategy

For multi-step explorations that consume significant context, use the Task tool with a `general-purpose` subagent to perform the browser work. Pass the URL, goal, and these browser operation principles in the prompt. The subagent handles the interaction and returns a summary.
