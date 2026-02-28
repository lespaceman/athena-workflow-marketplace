---
name: explore-website
description: >
  Use when the user provides a URL and wants to interact with a live website using a real browser.
  Triggers: "explore a website", "browse a page", "navigate a site", "open this URL", "interact with a web app",
  "extract selectors", "fill out a form", "find elements on", "check what's on this page", "what does this site look like",
  "click through the flow", "inspect the UI".
  This skill drives a headless browser via agent-web-interface MCP tools to navigate, click, type, extract
  Playwright-compatible selectors, and analyze forms. It does NOT generate test case specs or write test code —
  use generate-test-cases or write-e2e-tests for those.
user-invocable: true
argument-hint: <url> <what to explore or do>
allowed-tools:
  - mcp__plugin_e2e-test-builder_agent-web-interface__ping
  - mcp__plugin_e2e-test-builder_agent-web-interface__navigate
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_back
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_forward
  - mcp__plugin_e2e-test-builder_agent-web-interface__reload
  - mcp__plugin_e2e-test-builder_agent-web-interface__capture_snapshot
  - mcp__plugin_e2e-test-builder_agent-web-interface__find_elements
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_element_details
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_element_into_view
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__click
  - mcp__plugin_e2e-test-builder_agent-web-interface__type
  - mcp__plugin_e2e-test-builder_agent-web-interface__press
  - mcp__plugin_e2e-test-builder_agent-web-interface__select
  - mcp__plugin_e2e-test-builder_agent-web-interface__hover
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_form_understanding
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_field_context
  - mcp__plugin_e2e-test-builder_agent-web-interface__list_pages
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_session
  - mcp__plugin_e2e-test-builder_agent-web-interface__take_screenshot
---

# Explore Website

Explore and interact with a live website using the browser, reporting observations, extracting Playwright selectors, and analyzing forms.

## Input

Parse the target URL and exploration goal from: $ARGUMENTS

## Workflow

1. **Navigate** to the URL
2. **Complete the task** — interact as needed (click, fill forms, navigate pages)
3. **Extract selectors** — use `get_element_details` on key elements to get the `primary` Playwright selector from the `<find primary="...">` attribute
4. **Analyze forms** — use `get_form_understanding` to understand form intent, fields, completion state, and suggested next actions
5. **Report** what you did, found, and observed

## Browser Operation Principles

- **Action tools return fresh snapshots** — `navigate`, `click`, `type` etc. already return state; only use `capture_snapshot` when the page may have changed on its own (timers, live updates)
- **Use `find_elements`** when a snapshot shows `<!-- trimmed N items -->` — filter by `kind`, `label`, or `region`
- **Check `enabled` attribute** before clicking — sequential forms disable options until prerequisites are selected
- **Watch `<observations>`** — `<appeared>` and `<disappeared>` tags show what changed after actions
- **Use `region` filter** to narrow searches: `main`, `nav`, `header`, `footer`
- **Report blockers** (login walls, CAPTCHA, payment gateways, geo-restrictions) clearly and stop

## Selector Extraction

Use `get_element_details` with the element's eid to get Playwright-compatible selectors:

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
- **ARIA landmarks**: Check for `role="main"`, `role="navigation"`, `role="banner"` using `find_elements`
- **Dynamic content announcements**: After actions (form submit, modal open), check for `aria-live` regions in observations
- **Form labels**: Note any inputs without visible labels or `aria-label` — use `get_field_context` to check
- **Error association**: When form validation triggers, check if errors are linked to fields via `aria-describedby`
- **Heading hierarchy**: Use `find_elements` with `kind: "heading"` to verify h1 > h2 > h3 (no level skips)

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
