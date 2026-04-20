# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

This is a **Codex Plugin Marketplace** — a collection of plugins with skills for browser automation, Playwright E2E testing, and developer tooling.

- **agent-web-interface** — Semantic browser interface for LLM agents — token-efficient page snapshots via Puppeteer/CDP (`agent-web-interface` via npx), with a skill for live page interaction, selector extraction, form analysis, and multi-page recovery.
- **playwright-automation** — Playwright execution layer and long-running workflow surface for building Playwright E2E tests. Full pipeline: analyze codebase → map scope → capture evidence → generate and review test specs → write tests → review code → execute. Browser work is delegated to subagents via Task tool (browser tools live in the `agent-web-interface` plugin).
- **site-knowledge** — Site-specific automation patterns for popular websites (Airbnb, Amazon, Apple Store).

This is primarily a metadata-driven plugin marketplace. Plugin packages now generate versioned runtime artifacts during `npm pack` / `npm publish` via `scripts/build-plugin-artifacts.mjs`, while runtime execution is still managed by Codex, Codex, and the `agent-web-interface` MCP server (installed dynamically via `npx`).

## Architecture

### Three Parallel Registries

1. **Codex Plugin Marketplace** — `.Codex-plugin/marketplace.json` — registers plugins for `Codex plugin` CLI (`pluginRoot: ./plugins`)
2. **Codex Plugin Marketplace** — `.agents/plugins/marketplace.json` — registers plugins for Codex (`source.path: ./plugins/<name>`)
3. **Athena Workflow Marketplace** — `.athena-workflow/marketplace.json` — registers workflow definitions for `athena-cli` (`workflowRoot: ./workflows`)

Each plugin has two manifests: `.Codex-plugin/plugin.json` (Codex) and `.codex-plugin/plugin.json` (Codex). Shared fields (`name`, `version`, `description`) are kept identical. Codex-specific metadata (`keywords`, `repository`, `license`) lives in `.Codex-plugin/`. Codex-specific metadata (`interface`, `skills` path, `mcpServers` path) lives in `.codex-plugin/`. `scripts/build-plugin-artifacts.mjs` emits versioned `dist/<version>/release.json`, `Codex/plugin`, and `codex/{plugin,marketplace.json}` artifacts, and `scripts/bump-versions.sh` syncs source version numbers across manifests and plugin packages.

These marketplace and overlay files are repo conventions for packaging this marketplace. Treat them separately from official vendor runtime config such as `.Codex/settings.json` or Codex MCP client config.

### agent-web-interface Plugin

**MCP Config** (`plugins/agent-web-interface/.mcp.json`): Configures `agent-web-interface` MCP server with server key `browser`. All MCP tool names follow the pattern `mcp__plugin_agent-web-interface_browser__<tool>`.

**Skills** (`plugins/agent-web-interface/skills/`):
- `/agent-web-interface-guide <url> <goal>` — Live browser interaction, selector extraction, form analysis. Operational guide for state snapshots, observations, sequential forms, element attributes, and multi-page recovery.

### Playwright Automation Workflow And Plugin

**Skills** (`plugins/playwright-automation/skills/<skill-name>/SKILL.md`): Each skill is a domain guide covering one activity (analysis, test writing, review, debugging). Shared exploration and planning live in `app-exploration` and `test-analysis`. Browser work is delegated to subagents via Task tool (browser tools live in the `agent-web-interface` plugin). Skills only have file tools (Read, Write, Edit, Bash, Glob, Grep) and Task.

User-invocable skills (slash commands):
- `/add-playwright-tests <url> <feature>` — **Full pipeline orchestrator**: analyze → map scope → explore → generate → write (uses subagents)
- `/analyze-test-codebase [path]` — Detect Playwright config, test conventions, existing patterns
- `/map-feature-scope <url> <feature>` — Quickly decompose broad product areas into bounded exploration units
- `/capture-feature-evidence <url> <feature-or-subfeature>` — Explore a scoped product area and write grounded evidence artifacts
- `/plan-test-coverage <feature>` — Plan what to test based on existing coverage gaps
- `/generate-test-cases <feature>` — Produce structured TC-ID test specs from exploration and coverage artifacts
- `/review-test-cases <spec-file>` — **Quality gate**: review TC-ID specs for gaps, duplication, and invented scenarios before implementation
- `/write-test-code <test-description>` — Write executable Playwright test code following project conventions
- `/review-test-code <test-file>` — **Quality gate**: review Playwright code for brittle selectors, missing assertions, convention divergence before execution
- `/fix-flaky-tests <test-file-or-name>` — Diagnose and fix intermittent test failures

**Workflow** (`workflows/playwright-automation/workflow.json`): Athena-cli integration for stateless looping.
- `workflows/playwright-automation/workflow.md` — workflow-specific orchestration, appended to the runtime's workflow/state-machine prompt
- Depends on `agent-web-interface`, `app-exploration`, `test-analysis`, and `playwright-automation`
- Test execution and coverage checks are NEVER delegated to subagents — the main agent must run `npx playwright test` directly and record output as proof

### site-knowledge Plugin

**Skills** (`plugins/site-knowledge/skills/<site-name>/SKILL.md`): Auto-applied site knowledge (not user-invocable) — injected as context when relevant sites are detected. Covers Airbnb, Amazon, Apple Store, and Apple testing patterns.

## Workflow System (RFC 0001)

Workflows have two authored layers in this repo: the **workflow doc** (`workflows/<name>/workflow.md`) defines domain-specific orchestration, and **skills** carry implementation knowledge for each activity. Session orchestration is runtime-owned, not stored in this marketplace.

The `workflow.json` contract defines execution config:
- `workflowFile` — domain-specific orchestration doc, appended to the runtime's workflow/system prompt
- `loop.maxIterations` — safety cap on session count
- `plugins[]` — references plugins as `<plugin-name>@<owner>/<repo>`

## Adding a New Plugin

1. Create `plugins/<name>/` with `.Codex-plugin/plugin.json`, and optionally `skills/` and `.mcp.json`
2. Register in `.Codex-plugin/marketplace.json` under the `plugins` array
3. Skill files: YAML frontmatter with `name`, `description`, `user-invocable`, `argument-hint`, `allowed-tools` + markdown content

## Adding a New Workflow

1. Create `workflows/<name>/workflow.json` following the RFC 0001 contract
2. Add a `workflow.md` in the same directory with domain-specific orchestration
3. Register in `.athena-workflow/marketplace.json` under `workflows[]`

## Key Conventions

- Test case IDs use `TC-<FEATURE>-<NUMBER>` format (e.g., `TC-LOGIN-001`)
- Playwright locator preference: semantic (`getByRole`, `getByLabel`) > `data-testid` > text > CSS selectors
- No arbitrary `waitForTimeout` sleeps in generated tests — use event-driven waits
- Skill `allowed-tools` must explicitly list every MCP tool the skill needs (no wildcards)
- MCP tool names must match exactly: `mcp__plugin_<plugin-name>_<server-name>__<tool>`
- Skills delegate heavy work to general-purpose subagents via Task tool to save main context
- Skill descriptions must include exhaustive trigger phrases and clearly state what the skill does vs doesn't do
