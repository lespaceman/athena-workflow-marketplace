# Issue tracker: Linear

Issues and PRDs for this repo live in Linear. Load the `linear` skill before any read or write — it owns the MCP tool names, the issue-pickup procedure, and the status transitions. Use the MCP tools, never the web UI.

## Conventions

- **Team / project**: `<team key>` (issue keys look like `<TEAM>-123`). Default project for new engineering work: `<project name or "none">`.
- **Create an issue**: via the Linear MCP in the team above. Direct task titles and concrete outcomes; independently shippable vertical slices; no "As a user…" template.
- **Read an issue**: follow the `linear` skill's pickup procedure — the issue with its comments and relations, its parent project, and every linked document or attachment; assign yourself and move it to In Progress before writing code.
- **Comment on an issue**: at every gate transition, with the evidence that justifies it (command output location, commit SHA, PR link, browser proof).
- **Labels**: Linear labels on the team. The triage roles in `docs/agents/triage-labels.md` map to label names that already exist there — create none silently.
- **Status**: Backlog / Todo → In Progress on pickup (assign yourself) → In Review when code-complete → Done only after both the Verification and Review gates pass or the user waives one.

## When a skill says "publish to the issue tracker"

Create a Linear issue. For a PRD, create a Linear project (or document) holding the PRD and one issue per vertical slice.

## When a skill says "fetch the relevant ticket"

Fetch the Linear issue by key with comments, relations, parent project, and linked documents — the `linear` skill's full pickup read, not the issue body alone.
