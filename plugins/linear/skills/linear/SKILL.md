---
name: linear
description: >
  MUST load BEFORE reading from or writing to Linear and BEFORE any mcp__plugin_linear_linear__ tool call. Use when the user asks to create, inspect, update, triage, plan, comment on, or close Linear issues, projects, milestones, cycles, labels, teams, or backlog items; when a workflow needs issue-tracker context; when converting plans or PRDs into Linear work; when syncing delivery status back to Linear; or when the user says "Linear", "ticket", "issue", "project board", "backlog", "triage", "cycle", "roadmap", "blocked by", "branch from issue", or an issue key such as ABC-123. This skill teaches agent workflow discipline for Linear; it does not replace project-specific planning, code review, tests, or browser verification.
---

# Linear

Use the Linear MCP tools as the structured interface to the team's issue tracker. The tool is not a scratchpad: keep Linear concise, current, and tied to real work.

## Operating Principles

- Optimize for execution, not reporting. Do not add busy-work fields, synthetic updates, or fake history.
- Write issues, not user stories. Prefer direct task titles and concrete outcomes over "As a user..." templates.
- Keep work small. Issues should be independently shippable vertical slices whenever possible.
- Connect daily work to purpose. Use projects and milestones for meaningful product surfaces, not labels as a substitute for structure.
- Decide and move on. When the user has made a call, encode the result and proceed instead of repeatedly reopening the same planning question.
- Preserve board honesty. If work shipped before the issue existed, annotate the issue with what is already true and track only remaining work forward.

## Tool Use

The MCP server is configured as `linear`, so plugin tool names follow:

```text
mcp__plugin_linear_linear__<tool>
```

The plugin ships a Codex-compatible stdio MCP bridge:

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"]
    }
  }
}
```

For Codex/Athena sessions, keep Linear in this stdio `mcp-remote` form. Do not replace it with a bare `url = "https://mcp.linear.app/mcp"` entry unless the runtime explicitly supports streamable HTTP for that path; older Athena/Codex app-server paths reject direct `url` fields when they are normalized as stdio servers.

Before making changes:

1. Read the current workspace/team/project/issue state needed for the task.
2. Resolve human names, team keys, labels, workflow states, and project IDs through Linear instead of guessing IDs.
3. Summarize the intended write if it affects multiple issues, projects, labels, or dates.

Prefer structured MCP calls over browser or shell access. If a needed action is not exposed by the MCP tools, report the exact missing operation and whether it must be done in the Linear UI.

## Issue Discipline

Create or update issues with:

- Title: imperative, scoped, and searchable.
- Description: context, links to relevant docs/designs/code, and acceptance criteria.
- Project: set for any non-trivial work that belongs to a product surface.
- Labels: keep taxonomy small; use labels for cross-cutting filters, not as a replacement for projects.
- Assignee: assign on pickup. Backlog issues may remain unassigned; anything In Progress should have an owner.
- Priority: use sparingly to spotlight blockers and next work, not to rank the whole backlog.
- Relations: use blocks / blocked-by and sub-issues for dependencies instead of encoding order in titles.

Do not bulk-create a large backlog from a vague idea. First produce or confirm a project spec, then create a small set of vertical slices the team can actually pull.

## Project And Planning Guidance

Use Linear projects for time-bound deliverables or product surfaces. A good project has:

- A single owner.
- A concise problem statement or linked spec.
- Milestones only when there are meaningful phases.
- Target dates only for the active horizon.
- Issues that prove progress through actual implementation, design, docs, or operational work.

Use cycles only when the team already has enough throughput for timeboxing to be useful. Do not enable or depend on cycles just because they exist.

## Engineering Workflow Integration

On picking up an issue — always, not only when handed an issue key:

1. Load the issue in full: description, comments, labels, state, assignee, priority, and linked relations (blocks / blocked-by / sub-issues).
2. **Read the parent project of the issue.** Pull its problem statement / linked spec, status, milestones, and target dates with `get_project`. An issue is rarely self-contained — the project carries the intent the issue assumes, so never plan from the issue title alone.
3. **Read every attachment and document on both the issue and its project** — specs, designs, screenshots, linked docs. Use the document/attachment MCP tools (`list_documents`, `get_document`, `get_attachment`, `extract_images`) rather than inferring their contents. If an attachment cannot be retrieved, say so explicitly instead of guessing.
4. **Assign the issue to yourself and move it to In Progress before writing code.** Resolve your own Linear user through the MCP (current user / `get_user` / `list_users`); if acting on a human's account, assign to that user. Anything being worked must have an owner and an In-Progress state.
5. If there is no issue and the work is more than a small local edit, ask whether to create one (then assign to self and move to In Progress) or proceed with local artifacts.
6. Record the issue **and project** context in the workflow alignment artifact or local tracker.
7. Use the issue branch name when the repo and Linear integration support it.

During execution:

- Move issues only when the state matches reality.
- Comment with evidence, decisions, blockers, and handoff notes when they would help a teammate resume.
- Do not close issues until tests, review, and required QA evidence are complete or explicitly waived.
- When a blocker appears, add a relation or comment that points to the concrete blocked work.

## Status Lifecycle And Gates

Drive issue state from real progress, and treat the engineering gates as hard preconditions for forward transitions:

- **Backlog / Todo → In Progress:** on pickup, once the issue is assigned to you.
- **In Progress → In Review:** when the change is code-complete and code review is requested. Comment with a link to the diff/PR and the verification run.
- **In Review → Done:** only after **both** gates pass — the **code-review gate** (review findings resolved, no unresolved critical findings) and the **QA / verification gate** (tests green, required browser/QA evidence captured) — and the work is merged, or the user has explicitly waived a gate.
- Never skip In Review to mark Done. Never close an issue with unresolved critical review findings or missing QA evidence.

Comment at each transition with the evidence that justifies it: decisions made, commands run, review outcome, QA artifacts, and any blocker (with a relation to the blocking issue).

At delivery:

- Add a short comment with what changed, verification run, and remaining risk when useful.
- Leave final state transitions to the GitHub integration when the repo is configured for automatic PR/merge updates.
- If manual transition is required, only move to Done after the implementation is actually merged or the user explicitly wants Linear to reflect local completion.

## Telex-Style Defaults

When a repo has local Linear guidance, read and follow it before writing to Linear. For Telex-like boards, use these defaults unless the repo says otherwise:

- One team is enough until separate cadence or triage is genuinely needed.
- Projects mirror product surfaces.
- Issues are vertical slices, not horizontal layers.
- Backlog issues are assigned on pickup.
- Priorities spotlight the active blocker chain.
- Dates belong only on the active horizon.
- Board honesty beats retroactive cleanup.

If local docs conflict with these defaults, the local docs win.
