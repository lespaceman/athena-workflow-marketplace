---
name: workflow-builder
description: Scaffold, create, revise, or review complete Athena workflow packages, including workflow.md orchestration docs, workflow.json definitions, Plugin Pins, marketplace registration, and validation. Use when the user asks to create, scaffold, design, write, review, update, or package an Athena workflow, workflow.md, workflow.json, or end-to-end agent workflow definition.
---

# Workflow Builder

Build Athena workflow packages that an agent can run across sessions. A workflow is orchestration: it names phases, evidence gates, artifacts, skill routing, reset rules, and handoff behavior. It does not teach low-level implementation procedures that belong in Skills.

## Operating Principle

Write workflows as state machines with evidence gates.

Every phase must answer:

- What evidence allows entry?
- What action happens here?
- What artifact proves the phase happened?
- What gate allows progress?
- When should the agent loop, reset, stop, or hand off?

Do not rely on hidden runtime metadata. If an agent cannot see `workflow.json`, `workflow.md` must still be understandable and executable from visible context.

## Athena Workflow Package Steps

### 1. Determine Scope

Identify whether the user wants:

- A `workflow.md` only.
- A complete workflow package under `workflows/<name>/`.
- Plugin pins added to an existing workflow.
- `.athena-workflow/marketplace.json` registration.
- A review or revision of an existing workflow.

If the location is not obvious, default to the current repository when it already has `workflows/` and `.athena-workflow/marketplace.json`. Otherwise ask where to create the workflow.

### 2. Inspect Local Conventions

Before writing, read nearby workflow examples and registry files when present:

- `workflows/*/workflow.md`
- `workflows/*/workflow.json`
- `.athena-workflow/marketplace.json`
- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- Plugin skill folders that the workflow will route to
- Project instructions such as `AGENTS.md`

Follow local naming, JSON shape, plugin reference format, version style, and validation commands.

### 3. Select Plugins And Skills

Map workflow activities to visible plugin skills. Use local plugin manifests and skill folders as the source of truth.

For each required plugin pin, record:

- Plugin name
- Marketplace owner/repo ref format used locally
- Version from the plugin manifest or existing workflow examples
- Skills the workflow will route to
- Fallback or stop behavior when the skill is unavailable at runtime

Do not invent plugin references. If a required plugin is not present in the marketplace, stop and ask whether to add or omit it.

### 4. Scaffold Files

For a complete Athena workflow, create:

```text
workflows/<workflow-name>/
├── workflow.json
└── workflow.md
```

Use hyphen-case for workflow names. Keep machine-readable identity, versions, examples, loop settings, and plugin pins in `workflow.json`. Keep agent orchestration in `workflow.md`.

### 5. Write workflow.json

Include the local workflow metadata contract:

- `name`
- `version`
- `description`
- `marketplaceDescription`
- `promptTemplate`
- `workflowFile`
- `loop`
- `examplePrompts`
- `plugins`

Pin only plugins that the workflow actually needs. Match the local plugin pin format, for example:

```json
{
  "ref": "plugin-name@owner/repo",
  "version": "0.1.0"
}
```

Use existing workflows to determine owner/repo and version conventions. Do not duplicate plugin versions in `workflow.md`.

### 6. Write workflow.md

Use the structure in [workflow-md-template.md](references/workflow-md-template.md). Keep prose short and forceful.

Required sections:

- Operating Principle
- Capability Contract
- Skill Routing
- Task Tracker Discipline
- State Graph
- Phases
- Reset Rules
- Completion Gate
- Handoff Rules
- Guardrails

The workflow must be self-contained for the agent. It may mention visible Skills and Plugins, but must include fallback behavior when they are unavailable.

### 7. Register The Workflow

When `.athena-workflow/marketplace.json` exists, add or update an entry:

```json
{
  "name": "workflow-name",
  "source": "./workflows/workflow-name/workflow.json",
  "description": "Short marketplace description",
  "version": "0.1.0"
}
```

Append new workflows unless the user asks to reorder. Keep the registry version in sync with `workflow.json`.

### 8. Validate

Run the repository validation command when available. Prefer local conventions such as:

```shell
scripts/marketplace-cli validate
```

If plugin artifacts changed, run the plugin artifact build command used by the repo, such as:

```shell
npm run build:artifacts
```

Also inspect the final workflow manually for:

- Hidden metadata dependency in `workflow.md`
- Missing plugin pins in `workflow.json`
- Missing marketplace registration
- Missing artifact ownership
- Missing resume behavior
- Missing stop conditions
- Low-level procedure that belongs in a Skill
- Plugin or Skill names that are not visible locally

## Style Rules

- Be directive, not explanatory-first.
- Use phases, gates, artifacts, and stop conditions.
- Name anti-patterns directly.
- Require evidence before planning, implementation, review, and delivery.
- Describe the workflow as a dependency graph, not a rigid script.
- Keep detailed implementation methods in Skills.
- Include reset rules for invalidated assumptions.
- Include handoff behavior for context resets and blocked work.

## Common Fixes

- If `workflow.md` says `workflow.json` is the source of truth, replace that with a Capability Contract that works from visible context.
- If a default path ends in handoff after normal success, make handoff an alternate terminal state.
- If tracker discipline says "create notes" without saying where or what to include, define the minimum note fields and write-location rule.
- If phases can be skipped, state which evidence makes each shortcut valid.
- If `workflow.json` pins a plugin whose skills are never routed to, remove the pin or add the missing routing.
