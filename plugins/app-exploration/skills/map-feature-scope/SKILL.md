---
name: map-feature-scope
description: >
  Quickly map a broad product feature into concrete sub-features before deep exploration begins. Use when a requested feature may span multiple routes, tabs, overlays, roles, or primary interactive surfaces and the agent needs to identify bounded exploration units, shared state, and blockers before spawning parallel browser subagents. This skill owns `e2e-plan/feature-map.md`; it does not produce the final deep exploration evidence, coverage plan, or test specs.
allowed-tools: Read Write Edit Glob Grep Task
---

# Map Feature Scope

Run a fast recon pass over the requested feature so downstream exploration can split large surfaces
into bounded sub-features instead of sending one browser subagent through an oversized flow.

This skill owns the decomposition artifact. It does not replace deep exploration.

## Input

Parse the target URL and requested feature or journey from: $ARGUMENTS

Derive:
- a short main-feature slug
- candidate sub-feature slugs
- the evidence gap that requires decomposition first

## Workflow

### 1. Build context before browsing

- Read any existing `e2e-plan/feature-map.md`, `e2e-plan/exploration-report.md`,
  `e2e-plan/exploration/*.md`, `e2e-plan/coverage-plan.md`, and `test-cases/*.md` files related to
  the same feature.
- Search the repo for route names, feature keywords, and existing tests so you can distinguish
  already-known surfaces from unknown ones.
- State whether the requested feature is likely simple or broad before dispatching the browser pass.

### 2. Run a bounded recon pass in a browser subagent

Dispatch browser work to a subagent via the Task tool. The main agent coordinates and writes the
artifact; the subagent gathers live observations.

The subagent contract:
- invoke it with access to the `mcp__plugin_agent-web-interface_browser__*` tools so the browser
  companion skill auto-loads
- ask it to identify routes, tabs, menus, dialogs, settings pages, role gates, and major entry
  points for the requested feature
- tell it not to perform full deep exploration; the goal is scope discovery, not exhaustive
  validation
- require a structured return, not a prose narrative

Recon expectations:
- visit the requested starting URL
- walk the happy-path skeleton far enough to reveal the main screens and branches
- open the obvious menus, tabs, overlays, and settings related to the feature
- note shared state and gating prerequisites
- record blockers that would prevent parallel exploration

### 3. Identify sub-features

Split the feature when one or more of these is true:
- more than two routes are involved
- more than one primary interactive surface exists
- one area depends on different setup, role, or seeded state than another
- the likely TC count would exceed 40 if kept in one spec

Do not create artificial sub-features. If the flow is genuinely narrow, say so and mark the
feature as a single-surface feature.

### 4. Write `e2e-plan/feature-map.md`

Use this structure:

```markdown
# Feature Map: <Feature>

**URL:** <url>
**Date:** <date>
**Scope request:** <feature or journey requested>
**Evidence status:** COMPLETE | PARTIAL | BLOCKED
**Decomposition verdict:** SINGLE-SURFACE | MULTI-SURFACE

## Summary
- <2-4 bullets on the feature shape and why decomposition is or is not needed>

## Recon Findings
| Area | Route / entry point | What was directly observed | Notes |
|---|---|---|---|
| ... | ... | ... | ... |

## Sub-Features
| Slug | Name | Entry route / action | Why separate | Shared dependencies / state | Recommended depth | Parallel-safe | Priority |
|---|---|---|---|---|---|---|---|
| overview | Overview dashboard | `/dashboard` | distinct primary surface | shared login state | deep | yes | P0 |
| filters | Advanced filters | open "Filters" drawer | isolated overlay with separate validation | requires list page loaded | medium | yes | P1 |
| export | Export flow | click "Export" | mutates server-side job state | depends on seeded data | deep | no | P0 |

## Shared Blockers And Prerequisites
- <auth wall, missing role, unsafe production action, or "None">

## Recommended Exploration Dispatch
1. <sub-feature slug> — parallel | serial — <why>
2. <sub-feature slug> — parallel | serial — <why>

## Rollup Guidance
- <what the orchestrator must merge into `e2e-plan/exploration-report.md` later>

## Recommended Next Step
- `explore-app` for each required sub-feature
```

### 5. Stop cleanly when decomposition is blocked

If you cannot safely identify bounded sub-features:
- still write `e2e-plan/feature-map.md`
- mark it `PARTIAL` or `BLOCKED`
- record the exact blocker
- recommend serial exploration only when parallelization cannot be justified

## Quality Bar

- The output must distinguish directly observed surfaces from inferred ones.
- The sub-feature table must be actionable enough that another agent can spawn one exploration task
  per row without guessing.
- Use `parallel-safe = no` whenever a sub-feature depends on state created by another sub-feature,
  unsafe mutations, or scarce test data.
- If the feature is simple, say so explicitly and justify the single-surface verdict in one line.
- Do not turn the map into a coverage plan or detailed test spec.
