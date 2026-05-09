# Cross-Runtime Plugin Marketplace

This repo packages **Plugins**, **Skills**, and **Workflows** from one source tree for three external runtimes (Claude Code, Codex, athena-cli). There is no application runtime here — only metadata, skill definitions, and workflow definitions consumed by those clients.

## Language

**Plugin**:
A bundle of Skills (and optionally an MCP Server) shipped under `plugins/<name>/`, registered for one or more runtimes.
_Avoid_: package, module, extension.

**Skill**:
A portable agent capability authored as `SKILL.md` plus per-runtime overlay files. Lives under `plugins/<plugin>/skills/<skill>/`.
_Avoid_: command, prompt, tool.

**Workflow**:
A long-running, looping task definition (e.g. `playwright-automation`, `robot-automation`). Lives under `workflows/<name>/` with a `workflow.json` and `workflow.md`.
_Avoid_: pipeline, job, task.

**Per-plugin Manifest**:
The hand-edited metadata pair at `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/.codex-plugin/plugin.json`. Carries the plugin's identity for one runtime each.
_Avoid_: package.json (that's the npm artifact builder), plugin spec.

**Marketplace Registry**:
One of the three top-level catalog files — `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `.athena-workflow/marketplace.json` — consumed by an external runtime to discover what this repo ships.
_Avoid_: registry (alone — too generic), index, catalog.

**Plugin Pin**:
A `<plugin>@<owner>/<repo>` reference with a fixed `version`, recorded in a Workflow's `workflow.json` under `plugins[]`. Declares which Plugin versions a Workflow runs against.
_Avoid_: dependency, requirement.

**Shared Field**:
A field on a Plugin whose value must agree across both Per-plugin Manifests and the two plugin Marketplace Registries: `name`, `version`, `description`, `category`. Drift across these locations is a defect.
_Avoid_: common field, identity field.

**Runtime**:
One of the three external CLIs that consume this repo: Claude Code, Codex, athena-cli. Each consumes a different Marketplace Registry.
_Avoid_: client, host, target.

## Relationships

- A **Plugin** has exactly two **Per-plugin Manifests** (Claude and Codex) and appears in two **Marketplace Registries** (Claude and Codex).
- A **Plugin** contains zero or more **Skills**.
- A **Workflow** contains one or more **Plugin Pins** referencing **Plugins** at fixed versions.
- A **Workflow** appears in exactly one **Marketplace Registry** (Athena).
- A **Shared Field** must agree across a Plugin's two Per-plugin Manifests and its two Marketplace Registry entries — four locations.
- Each **Runtime** consumes exactly one **Marketplace Registry**.

## Example dialogue

> **Maintainer:** "I bumped `app-exploration` to 0.1.8."
> **Reviewer:** "Did you bump it in all four places? Both **Per-plugin Manifests** and both plugin **Marketplace Registries** carry the version as a **Shared Field**. The Codex registry currently lags at 0.1.6 — that's drift."
> **Maintainer:** "And the **Workflows** that pin it?"
> **Reviewer:** "Each **Workflow**'s `workflow.json` has a **Plugin Pin** for `app-exploration` — those need bumping too, and the Athena **Marketplace Registry** entry for the **Workflow** gets a new version because its pins changed."

## Flagged ambiguities

- "marketplace" alone is ambiguous (the repo, the three registry files, or one specific registry). Resolved: the repo is the **cross-runtime plugin marketplace**; the files are **Marketplace Registries**.
- "manifest" was used for both per-plugin metadata and `package.json`. Resolved: **Per-plugin Manifest** refers only to the `.claude-plugin/plugin.json` / `.codex-plugin/plugin.json` pair.
