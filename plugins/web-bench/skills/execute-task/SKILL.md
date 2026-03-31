---
name: execute-task
description: >
  Execute a single WebBench benchmark task via browser automation.
  Triggers: "execute task", "run task", "perform benchmark task", "browser task".
  Navigates to the Starting_URL, interprets the natural-language task description,
  performs the required browser actions, and captures the final state (screenshot + snapshot).
  Records an execution trace with actions taken and errors encountered.
  Does NOT evaluate success — use evaluate-task for that.
allowed-tools: Read Write Edit Bash mcp__plugin_web-bench_agent-web-interface__ping mcp__plugin_web-bench_agent-web-interface__navigate mcp__plugin_web-bench_agent-web-interface__find mcp__plugin_web-bench_agent-web-interface__get_element mcp__plugin_web-bench_agent-web-interface__get_form mcp__plugin_web-bench_agent-web-interface__get_field mcp__plugin_web-bench_agent-web-interface__click mcp__plugin_web-bench_agent-web-interface__type mcp__plugin_web-bench_agent-web-interface__press mcp__plugin_web-bench_agent-web-interface__select mcp__plugin_web-bench_agent-web-interface__hover mcp__plugin_web-bench_agent-web-interface__drag mcp__plugin_web-bench_agent-web-interface__scroll mcp__plugin_web-bench_agent-web-interface__scroll_to mcp__plugin_web-bench_agent-web-interface__wheel mcp__plugin_web-bench_agent-web-interface__snapshot mcp__plugin_web-bench_agent-web-interface__screenshot mcp__plugin_web-bench_agent-web-interface__go_back mcp__plugin_web-bench_agent-web-interface__go_forward mcp__plugin_web-bench_agent-web-interface__reload mcp__plugin_web-bench_agent-web-interface__list_pages mcp__plugin_web-bench_agent-web-interface__close_page
---

# Execute WebBench Task

Execute a single WebBench task via browser automation. This skill handles the browser interaction — navigating, clicking, typing, extracting data — required to complete the task.

## Input

You receive a single task object:

```json
{"id": 42, "url": "https://acehardware.com", "category": "READ", "task": "Navigate to the news section and summarize..."}
```

## Execution Protocol

### 1. Record Start Time

Before any browser interaction:

```bash
date +%s%3N
```

Save this as `start_time_ms`. You will need it for the result record.

### 2. Navigate to Starting URL

```
navigate → task.url
```

Wait for the page to load. Take an initial snapshot to understand the page structure.

### 3. Interpret the Task

Read the task description carefully. Classify it:

| Category | What to Do |
|----------|------------|
| **READ** | Navigate to the right page/section, extract the requested information. Your "result" is the extracted data. |
| **CREATE** | Fill forms, create accounts/entries/posts as described. Your "result" is confirmation the item was created. |
| **UPDATE** | Find existing data and modify it as described. Your "result" is confirmation the update was applied. |
| **DELETE** | Find and remove the specified item. Your "result" is confirmation of deletion. |
| **FILE_MANIPULATION** | Download the specified file. Your "result" is the filename and confirmation of download. |

### 4. Execute Browser Actions

Work through the task step by step:

1. **Observe** — Use `snapshot` or `find` to understand the current page state
2. **Plan** — Decide the next action based on what you see
3. **Act** — Use the appropriate MCP tool (click, type, select, etc.)
4. **Verify** — Check that the action had the expected effect

**Key principles:**

- **Use `find` with `kind` filters** to locate interactive elements (buttons, links, textboxes)
- **Use `snapshot`** to get a full page state when you need orientation
- **Use `screenshot`** to visually verify state when snapshots are ambiguous
- **Handle pop-ups and modals** — cookie banners, newsletter pop-ups, chat widgets. Dismiss them before proceeding
- **Stay on the specified site** — Tasks often say "Only use [site] to achieve the task." Respect this constraint
- **Handle pagination** — If data spans multiple pages, navigate through them
- **Be patient with slow sites** — Some sites load content dynamically. If elements aren't found immediately, try scrolling or waiting

### 5. Handle Common Obstacles

| Obstacle | Strategy |
|----------|----------|
| **Cookie consent banner** | Find and click "Accept" or "Close" |
| **Login required** | Record as blocker — do not attempt to create accounts or guess credentials |
| **CAPTCHA** | Record as blocker — cannot solve programmatically |
| **Paywall** | Record as blocker |
| **Geo-restricted content** | Record as blocker |
| **Site down / 404** | Record as error |
| **Pop-up / overlay blocking interaction** | Dismiss it, then continue |

### 6. Capture Final State

After completing the task (or hitting a blocker):

1. Take a **screenshot** of the final page state
2. Take a **snapshot** of the final DOM state
3. Record the **current URL**

### 7. Record End Time

```bash
date +%s%3N
```

Save as `end_time_ms`. Compute `duration_ms = end_time_ms - start_time_ms`.

### 8. Build Execution Trace

Construct a structured trace of what happened:

```json
{
  "task_id": 42,
  "actions": [
    {"step": 1, "action": "navigate", "target": "https://acehardware.com", "result": "loaded"},
    {"step": 2, "action": "click", "target": "News section link", "result": "navigated to /news"},
    {"step": 3, "action": "extract", "target": "headline text", "result": "Black Friday Deals..."}
  ],
  "final_url": "https://acehardware.com/news",
  "blockers": [],
  "extracted_data": "The headline is 'Black Friday Deals'...",
  "duration_ms": 34200
}
```

## Output

Return the execution trace to the calling context (system prompt / run-benchmark skill). Do NOT write results to disk — that is the system prompt's responsibility after evaluation.

## Guardrails

- **One task only.** Execute exactly the task given. Do not browse further or attempt other tasks.
- **No account creation.** If a task requires login, record it as a blocker. Do not create accounts.
- **No credential guessing.** Never attempt to guess passwords or bypass authentication.
- **Time limit awareness.** If a task is taking an unreasonable number of steps (>20 actions), consider it likely stuck and record what you have.
- **No destructive actions on real sites.** For WRITE/UPDATE/DELETE tasks on production sites, be aware these are real websites. If the task would create real accounts or modify real data, record this concern but still attempt the task as specified (this is the nature of the benchmark).
