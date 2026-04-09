# RFC 0002: Cross-Runtime Workflow And Plugin Packaging

- Status: Draft
- Author: Athena Workflow Marketplace Maintainers
- Created: 2026-03-10
- Audience: Athena CLI maintainers, workflow authors, plugin authors

## Abstract

This RFC defines how a workflow marketplace package can support multiple
execution runtimes without forking its shared orchestration contract.

The core rule is:

- keep workflow orchestration in shared `workflow.json`
- keep shared plugin capability definitions in the normal marketplace layout
- allow optional runtime-specific assets at the plugin layer under directories
  such as `.claude/` and `.codex-plugin/`

This RFC complements RFC 0001. RFC 0001 defines what a workflow is. This RFC
defines how a workflow or plugin package can express runtime-specific execution
details while preserving one shared package.

## Problem Statement

The marketplace now targets more than one harness/runtime shape:

- Claude-style headless execution
- Codex app-server execution

These runtimes do not consume packaged capabilities in exactly the same way.
Examples:

- Codex has first-class skills metadata and `skill` input items.
- Claude packages commonly rely on `.claude/` assets and Claude-specific
  operational conventions.
- Some existing shared skills contain Claude-only invocation examples or
  environment assumptions.

Without a packaging contract, repositories drift toward one of two bad states:

1. duplicate workflows and plugins per runtime
2. shared skills that secretly depend on one runtime's behavior

We need a packaging model that keeps shared workflow semantics stable while
allowing runtime-specific execution hints and assets.

## Goals

- Define a packaging model for shared plus runtime-specific plugin assets
- Define how skills should expose Codex-facing metadata
- Define runtime expectations for consuming these packages
- Keep existing workflow references and registries stable

## Non-Goals

- Replacing RFC 0001
- Standardizing runtime protocol details such as Codex `turn/start`
- Defining a universal open plugin registry format
- Encoding runtime-specific transport configuration directly in `workflow.json`

## Design Principles

1. Shared first
- Shared workflow semantics belong in `workflow.json`.
- Shared skills should remain the default whenever their instructions can be
  runtime-neutral.

2. Explicit overlays
- Runtime-specific behavior should live in explicit directories such as
  `.claude/` and `.codex-plugin/`, not in hidden assumptions inside shared files.

3. One package, many consumers
- A single workflow reference SHOULD remain installable across multiple
  runtimes.

4. Compile once
- Runtimes SHOULD resolve and compile a workflow package once per session or
  bootstrap boundary, not re-resolve plugin packages on every turn.

5. Skill metadata matters
- Codex-facing skills SHOULD expose `agents/openai.yaml` when UI metadata or
  dependency hints improve invocation quality.

## Relationship To RFC 0001

RFC 0001 remains the source of truth for:

- workflow semantics
- workflow lifecycle
- loop behavior
- shared workflow fields

This RFC adds:

- packaging overlays
- runtime-specific asset conventions
- skill metadata conventions

If the two RFCs conflict, RFC 0001 governs workflow behavior and this RFC
governs packaging.

## Terminology

- Shared Asset: A file consumed by multiple runtimes without modification
- Runtime Overlay: A directory containing assets intended for one runtime
- Compiled Workflow Plan: A runtime-owned resolved view of workflow plus plugin
  assets
- Skill Metadata: Optional UI and dependency metadata such as
  `agents/openai.yaml`

## Repository Layout

Recommended repository shape:

```text
.
├── .athena-workflow/
│   └── marketplace.json
├── .claude-plugin/
│   └── marketplace.json
├── workflows/
│   └── <workflow-name>/
│       ├── workflow.json
│       └── workflow.md
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── .mcp.json
        ├── skills/
        │   └── <skill-name>/
        │       ├── SKILL.md
        │       └── agents/
        │           └── openai.yaml
        ├── .claude/
        │   └── ...
        └── .codex-plugin/
            └── plugin.json
```

Notes:

- Plugin-level `.claude/` and `.codex-plugin/` are optional overlays.
- Shared `skills/` remain valid without either overlay.
- `agents/openai.yaml` is optional but recommended for user-invocable Codex
  skills.

## Workflow Packaging Contract

### Shared workflow manifest

`workflows/<name>/workflow.json` remains the required workflow definition.

It SHOULD contain only shared orchestration concerns such as:

- workflow identity
- prompt templating
- system prompt file references
- plugin references
- loop configuration
- isolation preference

It MUST NOT encode runtime transport details.

### Workflow neutrality

`workflows/<name>/workflow.json` is Athena-owned and runtime-neutral.

Workflow packages in this repository SHOULD NOT define runtime-specific overlay
workflow manifests. Runtime-specific execution details belong in:

- the consuming runtime's compiled workflow plan
- plugin-level overlay metadata when needed

If a runtime needs extra routing or execution hints, those hints SHOULD be
derived from plugin assets or runtime configuration rather than from a
runtime-specific workflow manifest in the repository.

## Plugin Packaging Contract

### Shared plugin assets

Plugins continue to publish shared assets through:

- `.claude-plugin/plugin.json`
- `.mcp.json`
- `skills/`

This preserves compatibility with existing marketplace resolution.

### Runtime overlay plugin metadata

Plugins MAY include overlay metadata files such as:

- `plugins/<name>/.codex-plugin/plugin.json`

These files SHOULD describe runtime-specific metadata that is difficult or
undesirable to infer from shared Markdown alone. Examples:

- skill inventory
- runtime-facing aliases
- skill entrypoint hints
- runtime-specific dependency notes

Overlay metadata MUST augment shared assets rather than replace them.

## Skill Packaging Contract

### Shared skills

Shared skills live under:

- `plugins/<name>/skills/<skill-name>/SKILL.md`

Shared skills SHOULD:

- use runtime-neutral wording where practical
- avoid runtime-exclusive invocation syntax in examples
- avoid runtime-specific environment variable names unless explicitly marked as
  runtime-specific

### Codex metadata

If a skill is intended to be user-invocable or discoverable in Codex surfaces,
it SHOULD include:

- `plugins/<name>/skills/<skill-name>/agents/openai.yaml`

Recommended fields:

- `interface.display_name`
- `interface.short_description`
- `interface.default_prompt`
- `dependencies.tools` when the skill clearly depends on MCP or env vars

### Runtime-specific skill variants

If a shared skill body cannot remain runtime-neutral, authors MAY add
runtime-specific variants in overlays such as:

- `plugins/<name>/.claude/skills/...`
- `plugins/<name>/.codex-plugin/skills/...`

Runtimes SHOULD prefer a runtime-specific variant when present and otherwise
fall back to the shared `skills/` version.

## Runtime Consumption Model

Runtimes consuming this repository SHOULD:

1. Resolve the shared workflow manifest.
2. Resolve referenced plugins once.
3. Collect shared plugin assets.
4. Collect runtime-specific plugin overlay assets for the active runtime.
5. Compile a runtime-owned workflow plan from those inputs.

That compiled plan MAY include:

- resolved plugin directories
- merged MCP config
- shared plus runtime-specific instruction fragments
- skill inventory
- skill metadata
- runtime-specific routing hints

Runtimes SHOULD NOT perform marketplace/plugin resolution again on every turn.

## Environment And Script Portability

If a skill or script needs to refer to its plugin root, it SHOULD use an
Athena-neutral convention such as `ATHENA_PLUGIN_ROOT` when the runtime
provides one.

Shared skills SHOULD avoid hard-coding runtime-exclusive variables such as
`CLAUDE_PLUGIN_ROOT` unless the skill is intentionally runtime-specific.

## Migration Guidance

Repositories adopting this RFC SHOULD migrate in this order:

1. Keep the shared `workflow.json` unchanged.
2. Remove runtime-specific invocation syntax from shared skills where practical.
3. Add `agents/openai.yaml` to user-invocable Codex-facing skills.
4. Add `.codex-plugin/` overlays only for behavior that cannot stay shared.
5. Keep `.claude/` overlays for Claude-only behavior.

## Security Considerations

- Runtimes MUST treat overlay manifests as untrusted input.
- Runtimes MUST validate resolved paths before reading overlay assets.
- Overlay metadata SHOULD NOT cause direct shell execution by itself.
- MCP and script dependencies MUST continue to be mediated by the runtime's
  existing approval and sandbox model.

## Open Questions

- Whether shared `.claude-plugin/plugin.json` should eventually be renamed to a
  runtime-neutral marketplace manifest
- Whether Codex overlay metadata should eventually expose explicit skill-to-turn
  routing rules
- Whether runtime-specific skill overlays should be preferred over shared skills
  by path convention alone or by explicit manifest fields
