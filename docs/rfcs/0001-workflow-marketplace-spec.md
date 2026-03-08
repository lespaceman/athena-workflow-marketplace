# RFC 0001: Long-Running Workflow Definition (Claude Plugin Compatible)

- Status: Draft
- Author: Athena Workflow Marketplace Maintainers
- Created: 2026-02-27
- Audience: Athena CLI maintainers and tool builders

## Abstract

This RFC defines a workflow contract for long-running, multi-session automation. A workflow orchestrates existing Claude plugin capabilities (skills, tools, and sub-agent/task patterns) into resumable execution.

The workflow layer does not replace plugin standards. It is an orchestration layer on top of today's Anthropic Claude plugin model, with a forward path to future open plugin standards.

## Problem Statement

Single-session agent runs are not enough for complex automation like:

- multi-step E2E generation and verification
- retries and repair loops
- progress across context resets

We need a portable workflow definition that:

- keeps durable state across sessions
- composes plugin-defined capabilities
- remains compatible with current Claude plugin conventions

## Goals

- Define what a "workflow" is and why it exists
- Define workflow execution lifecycle for long-running tasks
- Define a minimal `workflow.json` contract for consumers
- Define interoperability with Claude plugin capabilities today
- Preserve compatibility with future plugin standardization

## Non-Goals

- Re-defining skill format or plugin manifest format
- Standardizing MCP transport or packaging internals
- Replacing plugin installers with a new package manager

## Design Principles

1. Reuse existing standards first
- Skills, plugin manifests, and MCP config stay in Claude plugin format.

2. Workflow is orchestration
- Workflow defines execution order, loop policy, and completion logic.

3. Stateless compute, stateful progress
- Each run can be stateless; tracker artifacts persist progress.

4. Tooling portability
- Workflow definitions should be readable by multiple runtimes.

## Terminology

- Workflow: A declarative long-running execution contract
- Plugin Capability: Skill/tool/sub-agent behavior provided by a plugin
- Tracker: Persistent artifact used as cross-session memory
- Completion Marker: String token indicating terminal workflow state
- Workflow Reference: `<workflow-name>@<owner>/<repo>`

## Why Workflows

Workflows provide:

- resumability across process restarts and context resets
- deterministic progression through named steps
- explicit completion and blocked semantics
- repeatable behavior across CLI tools

Without workflows, orchestration logic stays implicit in prompts and is difficult to maintain.

## Interoperability Model (Current State)

Workflows use Claude plugin capabilities as-is:

- Skills: Existing slash-command or auto-applied skills
- Tools: Existing allowed tools declared by plugins/skills
- Sub-agent definitions: Existing task delegation patterns used by skills

Normative requirements:

- A workflow runtime MUST treat plugin capability loading as a plugin-layer concern.
- A workflow runtime MUST NOT require a new plugin format to execute workflows.
- A workflow MAY require specific plugins, referenced through the runtime's plugin resolver.

## MCP Guidance (Interim)

MCP is part of plugin capability loading, but cross-tool install/resolve behavior is not fully standardized yet.

Interim guidance:

- Workflow definitions SHOULD NOT encode MCP install commands directly.
- Workflow runtimes SHOULD delegate MCP resolution to plugin/runtime installers.
- If a required MCP server cannot be resolved, runtimes SHOULD fail with actionable error messages.

## Workflow Definition Contract

Path convention in this repository: `/.workflows/<workflow-name>/workflow.json`

Example:

```json
{
  "name": "e2e-test-builder",
  "description": "Iterative E2E workflow with tracker-based state",
  "promptTemplate": "{input}",
  "systemPromptFile": "system_prompt.md",
  "plugins": ["e2e-test-builder@lespaceman/athena-workflow-marketplace"],
  "loop": {
    "enabled": true,
    "completionMarker": "E2E_COMPLETE",
    "blockedMarker": "E2E_BLOCKED",
    "trackerPath": "e2e-tracker.md",
    "maxIterations": 15
  },
  "isolation": "minimal"
}
```

### Field Semantics

- `name` (required, string): Stable workflow identifier.
- `description` (optional, string): Human-readable summary.
- `promptTemplate` (required, string): User input mapping template. MUST include `{input}`.
- `systemPromptFile` (optional, string): Relative path from workflow directory.
- `plugins` (required, array): Plugin refs/paths consumable by the runtime.
- `loop` (optional, object): Loop execution behavior.
- `isolation` (optional, string): Runtime isolation preference.

### Loop Semantics

If `loop.enabled` is true:

- Runtime SHOULD iterate until completion, blocked, or `maxIterations` reached.
- Runtime SHOULD evaluate `completionMarker` and `blockedMarker` against tracker/output state.
- Runtime SHOULD persist state between iterations using `trackerPath` or equivalent state artifact.

## Execution Lifecycle

Recommended per-iteration lifecycle:

1. Load workflow definition.
2. Resolve and load required plugins.
3. Read tracker/state artifact.
4. Execute next actionable step.
5. Persist step status and logs.
6. Evaluate completion or blocked conditions.
7. Continue or exit.

Terminal states:

- Complete: success marker found.
- Blocked: unrecoverable marker/reason found.
- Exhausted: `maxIterations` reached without terminal marker.

## Registry and Discovery

This repository uses:

- `/.athena-workflow/marketplace.json` as workflow registry
- `/.workflows/` as workflow definition root

These are packaging conventions for discovery. The core workflow contract is the `workflow.json` behavior above.

## Forward Compatibility

This RFC intentionally binds workflow behavior to stable orchestration concepts, not to any single plugin packaging implementation.

When broader open plugin standards mature:

- plugin references in `plugins[]` can be resolved by alternative resolvers
- workflow semantics and lifecycle remain unchanged

## Security Considerations

- Runtimes MUST validate and sanitize resolved paths.
- Runtimes SHOULD treat workflow and registry files as untrusted input.
- Runtimes SHOULD avoid executing shell commands directly from workflow fields.

## Open Questions

- Canonical cross-runtime plugin reference format beyond current marketplace refs
- Portable MCP resolution contract across toolchains
- Standard schema publication and version negotiation strategy
