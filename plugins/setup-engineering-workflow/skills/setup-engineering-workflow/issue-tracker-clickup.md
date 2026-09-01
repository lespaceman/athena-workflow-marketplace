# Issue tracker: ClickUp

Tasks and PRDs for this repo live in ClickUp. Load the `clickup` skill before any read or write — it owns the MCP tool names, the task-pickup procedure, and the status transitions. Use the MCP tools, never the web UI.

## Conventions

- **Workspace / space / list**: `<workspace>` → `<space>` → [`<folder>` →] `<list>`. Task IDs look like `86abc1234` or a custom ID like `<PREFIX>-123`.
- **Create a task**: via the ClickUp MCP in the list above. Direct task titles and concrete outcomes; independently shippable vertical slices; no "As a user…" template.
- **Read a task**: follow the `clickup` skill's pickup procedure — the task with its comments, subtasks, and linked docs, plus the surrounding list; assign yourself and move it to the list's in-progress status before writing code.
- **Comment on a task**: at every gate transition, with the evidence that justifies it (command output location, commit SHA, PR link, browser proof).
- **Tags / statuses**: the triage roles in `docs/agents/triage-labels.md` map to tags or statuses that already exist in the list — create none silently.
- **Status**: statuses are custom per space — read the list's actual statuses first, then map them: the equivalent of To Do → In Progress on pickup (assign yourself) → In Review when code-complete → Closed/Done only after both the Verification and Review gates pass or the user waives one.

## When a skill says "publish to the issue tracker"

Create a ClickUp task. For a PRD, create a ClickUp Doc holding the PRD and one task per vertical slice.

## When a skill says "fetch the relevant ticket"

Fetch the ClickUp task by ID with comments, subtasks, linked docs, and its surrounding list — the `clickup` skill's full pickup read.
