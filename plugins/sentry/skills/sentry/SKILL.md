---
name: sentry
description: >
  MUST load BEFORE reading from Sentry and BEFORE any mcp__plugin_sentry_sentry__ tool call. Use when the user asks to inspect, search, or triage Sentry issues, events, stack traces, performance transactions, releases, environments, or error trends; when diagnosing a production bug or regression; when a workflow needs error-context from Sentry; when mapping a stack trace to source code; or when the user says "Sentry", "error", "exception", "stack trace", "performance", "transaction", "release", "environment", "DSN", "fingerprint", "issue group", or a Sentry issue ID. This skill teaches agent workflow discipline for Sentry; it does not replace code-review, test runs, or browser verification.
---

# Sentry

Use the Sentry MCP tools as the read-oriented interface to error and performance data. Sentry is a source of truth for production symptoms — not a scratchpad or a ticketing system.

## Operating Principles

- Read before concluding. Always fetch the full issue, event, and stack trace before diagnosing a bug.
- Reproduce from evidence. Use the stack trace, breadcrumbs, and affected release to locate the code, not intuition.
- Stay grounded. Sentry shows symptoms; root cause is in the code. Don't stop at the Sentry report.
- Link issues to work. When triaging or fixing, connect the Sentry issue to the team's issue tracker (Linear, GitHub Issues, ClickUp) rather than keeping context only in chat.
- Don't fabricate data. If a Sentry query returns no results, say so rather than guessing.

## Tool Use

The MCP server is configured as `sentry`, so plugin tool names follow:

```text
mcp__plugin_sentry_sentry__<tool>
```

The plugin ships a Codex-compatible stdio MCP bridge:

```json
{
  "mcpServers": {
    "sentry": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.sentry.dev/mcp"]
    }
  }
}
```

Sentry's MCP server authenticates with **OAuth** — on first connection the runtime opens a browser consent flow; complete it once and the session is authorized.

For Codex/Athena sessions, keep Sentry in this stdio `mcp-remote` form. Do not replace it with a bare `url = "https://mcp.sentry.dev/mcp"` entry unless the runtime explicitly supports streamable HTTP for that path; older Athena/Codex app-server paths reject direct `url` fields when they are normalized as stdio servers.

Before drawing conclusions:

1. Read the current issue/event state: title, culprit, first seen, last seen, event count, affected users, tags, and assigned team or person.
2. Fetch at least one raw event with its full stack trace, breadcrumbs, and request context.
3. Resolve release tags, environment filters, and fingerprint rules through Sentry rather than guessing.

Prefer structured MCP calls over browser or shell access. If a needed action is not exposed by the MCP tools, report the exact missing operation and whether it must be done in the Sentry UI.

## Workflow: Diagnosing a Production Error

When asked to investigate a Sentry error or stack trace:

1. **Locate the issue.** Search by error type, message substring, or Sentry issue ID. If the user pastes a URL, extract the project slug and issue ID from it.
2. **Read the full issue.** Fetch issue metadata: status, assignee, first/last seen, event count, affected release.
3. **Fetch a representative event.** Pull the most recent or the oldest event with a full stack trace. Read every frame: file, line, function, in-app flag, and local variables if available.
4. **Map to source.** Cross-reference the stack frames to the actual source files in the repo. Check if the culprit line matches the current HEAD or an older release.
5. **Check breadcrumbs.** Read the breadcrumbs leading up to the event — HTTP requests, DB queries, console logs — to understand the sequence of actions.
6. **Check tags and context.** Note the OS, browser, release version, environment, user ID, and any custom tags to understand the blast radius.
7. **Form a hypothesis.** State the probable root cause and the specific file/line/function implicated, with evidence from the stack trace.
8. **Link to work.** If a fix is warranted, reference or create an issue in the team's tracker and note the Sentry issue ID.

## Workflow: Release Health

When asked to check release health or error trends:

1. List the relevant releases for the project and environment.
2. Compare error counts, crash-free session rate, and adoption between the current and prior release.
3. Identify new issues introduced in the current release (first seen ≥ release date).
4. Flag any issue with a significant spike in event volume.

## Issue Discipline

When referencing Sentry issues in comments or tracker items:

- Include the Sentry issue ID and a short title.
- Include the first-seen and last-seen timestamps.
- Include the culprit (file and function) from the stack trace.
- Include the affected release and environment.
- Link directly to the Sentry issue URL when possible.

Do not summarize a Sentry issue from memory. Always fetch the current state — issue status and event counts change after you first read them.

## Engineering Workflow Integration

On picking up a task that involves a production bug:

1. Ask for the Sentry issue ID or URL if not provided. If the user describes symptoms, search Sentry first before reading code.
2. Load the full issue and at least one event before opening any source files.
3. Record the Sentry issue ID and culprit in the workflow alignment artifact or local tracker so context survives context resets.
4. After a fix is implemented and merged, confirm the issue is resolved or declining in Sentry — do not assume the fix worked.

If the repo has local Sentry guidance (DSN setup, project slug conventions, custom tags), read and follow it. If local docs conflict with these defaults, the local docs win.
