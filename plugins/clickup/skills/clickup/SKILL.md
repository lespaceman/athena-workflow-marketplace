---
name: clickup
description: >
  MUST load BEFORE reading from or writing to ClickUp and BEFORE any mcp__plugin_clickup_clickup__ tool call. Use when the user asks to create, inspect, update, triage, plan, comment on, assign, or close ClickUp tasks, subtasks, lists, folders, spaces, docs, checklists, custom fields, statuses, sprints, goals, or time-tracking entries; when a workflow needs task-tracker context; when converting plans or PRDs into ClickUp work; when syncing delivery status back to ClickUp; or when the user says "ClickUp", "task", "subtask", "list", "folder", "space", "workspace", "doc", "checklist", "custom field", "status", "sprint", "goal", "time tracking", "due date", "assignee", or a ClickUp task ID such as 86abc1234 or a custom ID like GH-123. This skill teaches agent workflow discipline for ClickUp; it does not replace project-specific planning, code review, tests, or browser verification.
---

# ClickUp

Use the ClickUp MCP tools as the structured interface to the team's work tracker. The tool is not a scratchpad: keep ClickUp concise, current, and tied to real work.

## Operating Principles

- Optimize for execution, not reporting. Do not add busy-work fields, synthetic updates, or fake history.
- Write tasks, not user stories. Prefer direct task titles and concrete outcomes over "As a user..." templates.
- Keep work small. Tasks should be independently shippable vertical slices whenever possible.
- Connect daily work to purpose. Use spaces, folders, and lists for meaningful product surfaces, not tags as a substitute for structure.
- Decide and move on. When the user has made a call, encode the result and proceed instead of repeatedly reopening the same planning question.
- Preserve board honesty. If work shipped before the task existed, annotate the task with what is already true and track only remaining work forward.

## Tool Use

The MCP server is configured as `clickup`, so plugin tool names follow:

```text
mcp__plugin_clickup_clickup__<tool>
```

The plugin ships a Codex-compatible stdio MCP bridge:

```json
{
  "mcpServers": {
    "clickup": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.clickup.com/mcp"]
    }
  }
}
```

ClickUp's MCP server authenticates with **OAuth** — there is no API-key field. On first connection the runtime opens a browser consent flow; complete it once and the session is authorized. Do not paste personal API tokens into the config; they are not supported.

For Codex/Athena sessions, keep ClickUp in this stdio `mcp-remote` form. Do not replace it with a bare `url = "https://mcp.clickup.com/mcp"` entry unless the runtime explicitly supports streamable HTTP for that path; older Athena/Codex app-server paths reject direct `url` fields when they are normalized as stdio servers.

Before making changes:

1. Read the current workspace/space/folder/list/task state needed for the task.
2. Resolve human names, list names, statuses, tags, and custom fields through ClickUp instead of guessing IDs.
3. Summarize the intended write if it affects multiple tasks, lists, statuses, or dates.

Prefer structured MCP calls over browser or shell access. If a needed action is not exposed by the MCP tools, report the exact missing operation and whether it must be done in the ClickUp UI.

## Hierarchy

ClickUp nests work as **Workspace → Space → Folder → List → Task → Subtask**. Folders are optional (lists can live directly in a space). Plan against this shape:

- Resolve the target **list** before creating a task — a task always belongs to exactly one list.
- Use **spaces** for major product or team boundaries, **folders** to group related lists, and **lists** for the actual backlog/board.
- Use **subtasks** and **checklists** for decomposition inside a task, not separate top-level tasks.

## Task Discipline

Create or update tasks with:

- Name: imperative, scoped, and searchable.
- Description: context, links to relevant docs/designs/code, and acceptance criteria.
- List: place every task in the list that matches its product surface; do not dump work into a catch-all list.
- Status: drive status from real progress (see lifecycle below). Custom statuses vary per space — read the list's available statuses before setting one.
- Tags: keep the taxonomy small; use tags for cross-cutting filters, not as a replacement for spaces/folders/lists.
- Assignee: assign on pickup. Backlog tasks may remain unassigned; anything in progress should have an owner.
- Priority: use sparingly to spotlight blockers and next work, not to rank the whole backlog.
- Relationships: use task dependencies (blocking / waiting-on) and subtasks for ordering instead of encoding order in titles.
- Custom fields: only set fields that already exist on the list; read the list's field definitions first rather than inventing fields.

Do not bulk-create a large backlog from a vague idea. First produce or confirm a project spec, then create a small set of vertical slices the team can actually pull.

## Status Lifecycle And Gates

Drive task status from real progress, and treat the engineering gates as hard preconditions for forward transitions. ClickUp statuses are custom per space, so map these stages onto the list's actual statuses:

- **Open / To Do → In Progress:** on pickup, once the task is assigned to you.
- **In Progress → In Review:** when the change is code-complete and code review is requested. Comment with a link to the diff/PR and the verification run.
- **In Review → Closed / Done:** only after **both** gates pass — the **code-review gate** (review findings resolved, no unresolved critical findings) and the **QA / verification gate** (tests green, required browser/QA evidence captured) — and the work is merged, or the user has explicitly waived a gate.
- Never skip In Review to mark a task Done. Never close a task with unresolved critical review findings or missing QA evidence.

Comment at each transition with the evidence that justifies it: decisions made, commands run, review outcome, QA artifacts, and any blocker (with a dependency pointing to the blocking task).

## Engineering Workflow Integration

On picking up a task — always, not only when handed a task ID:

1. Load the task in full: description, comments, tags, status, assignees, priority, custom fields, and dependencies (blocking / waiting-on / subtasks).
2. **Read the surrounding list and any linked doc.** A task is rarely self-contained — the list and its docs carry the intent the task assumes, so never plan from the task title alone. Use the doc/comment MCP tools rather than inferring contents; if an attachment cannot be retrieved, say so explicitly instead of guessing.
3. **Assign the task to yourself and move it to In Progress before writing code.** Resolve your own ClickUp user through the MCP; if acting on a human's account, assign to that user. Anything being worked must have an owner and an in-progress status.
4. If there is no task and the work is more than a small local edit, ask whether to create one (then assign to self and move to In Progress) or proceed with local artifacts.
5. Record the task and list context in the workflow alignment artifact or local tracker.

During execution:

- Move tasks only when the status matches reality.
- Comment with evidence, decisions, blockers, and handoff notes when they would help a teammate resume.
- Do not close tasks until tests, review, and required QA evidence are complete or explicitly waived.
- When a blocker appears, add a dependency or comment that points to the concrete blocking task.

At delivery:

- Add a short comment with what changed, the verification run, and remaining risk when useful.
- Only move to Done after the implementation is actually merged or the user explicitly wants ClickUp to reflect local completion.

If the repo has local ClickUp guidance, read and follow it before writing to ClickUp. If local docs conflict with these defaults, the local docs win.
