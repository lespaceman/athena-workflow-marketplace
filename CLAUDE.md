# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code Plugin Marketplace** — a collection of plugins with skills for browser automation, Playwright E2E testing, and developer tooling.

- **agent-web-interface** — Semantic browser interface for LLM agents — token-efficient page snapshots via Puppeteer/CDP (`agent-web-interface` via npx), with a skill for live page interaction, selector extraction, form analysis, and multi-page recovery.
- **e2e-test-builder** — Skills for building Playwright E2E tests. Full pipeline: analyze codebase → plan coverage → explore site → generate test specs → **review specs** → write tests → **review code** → execute. Delegates browser work to subagents via Task tool (browser tools live in the `agent-web-interface` plugin).
- **site-knowledge** — Site-specific automation patterns for popular websites (Airbnb, Amazon, Apple Store).

This is primarily a metadata-driven plugin marketplace. Plugin packages now generate versioned runtime artifacts during `npm pack` / `npm publish` via `scripts/build-plugin-artifacts.mjs`, while runtime execution is still managed by Claude Code, Codex, and the `agent-web-interface` MCP server (installed dynamically via `npx`).

## Architecture

### Three Parallel Registries

1. **Claude Plugin Marketplace** — `.claude-plugin/marketplace.json` — registers plugins for `claude plugin` CLI (`pluginRoot: ./plugins`)
2. **Codex Plugin Marketplace** — `.agents/plugins/marketplace.json` — registers plugins for Codex (`source.path: ./plugins/<name>`)
3. **Athena Workflow Marketplace** — `.athena-workflow/marketplace.json` — registers workflow definitions for `athena-cli` (`workflowRoot: ./workflows`)

Each plugin has two manifests: `.claude-plugin/plugin.json` (Claude Code) and `.codex-plugin/plugin.json` (Codex). Shared fields (`name`, `version`, `description`) are kept identical. Claude-specific metadata (`keywords`, `repository`, `license`) lives in `.claude-plugin/`. Codex-specific metadata (`interface`, `skills` path, `mcpServers` path) lives in `.codex-plugin/`. `scripts/build-plugin-artifacts.mjs` emits versioned `dist/<version>/release.json`, `claude/plugin`, and `codex/{plugin,marketplace.json}` artifacts, and `scripts/bump-versions.sh` syncs source version numbers across manifests and plugin packages.

These marketplace and overlay files are repo conventions for packaging this marketplace. Treat them separately from official vendor runtime config such as `.claude/settings.json` or Codex MCP client config.

### agent-web-interface Plugin

**MCP Config** (`plugins/agent-web-interface/.mcp.json`): Configures `agent-web-interface` MCP server with server key `browser`. All MCP tool names follow the pattern `mcp__plugin_agent-web-interface_browser__<tool>`.

**Skills** (`plugins/agent-web-interface/skills/`):
- `/agent-web-interface-guide <url> <goal>` — Live browser interaction, selector extraction, form analysis. Operational guide for state snapshots, observations, sequential forms, element attributes, and multi-page recovery.

### e2e-test-builder Plugin

**Skills** (`plugins/e2e-test-builder/skills/<skill-name>/SKILL.md`): Each skill is a domain guide covering one activity (analysis, planning, test writing, review, debugging). Browser work is delegated to subagents via Task tool (browser tools live in the `agent-web-interface` plugin). Skills only have file tools (Read, Write, Edit, Bash, Glob, Grep) and Task.

User-invocable skills (slash commands):
- `/add-e2e-tests <url> <feature>` — **Full pipeline orchestrator**: analyze → plan → explore → generate → write (uses subagents)
- `/analyze-test-codebase [path]` — Detect Playwright config, test conventions, existing patterns
- `/plan-test-coverage <url> <feature>` — Plan what to test based on existing coverage gaps
- `/generate-test-cases <url> <user-journey>` — Explore site and produce structured TC-ID test specs
- `/review-test-cases <spec-file>` — **Quality gate**: review TC-ID specs for gaps, duplication, and invented scenarios before implementation
- `/write-test-code <test-description>` — Write executable Playwright test code following project conventions
- `/review-test-code <test-file>` — **Quality gate**: review Playwright code for brittle selectors, missing assertions, convention divergence before execution
- `/fix-flaky-tests <test-file-or-name>` — Diagnose and fix intermittent test failures

**Workflow** (`workflows/e2e-test-builder/workflow.json`): Athena-cli integration for stateless looping.
- `workflows/e2e-test-builder/workflow.md` — workflow-specific orchestration, appended to the runtime's workflow/state-machine prompt
- Depends on both `agent-web-interface` and `e2e-test-builder` plugins
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

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`, and optionally `skills/` and `.mcp.json`
2. Register in `.claude-plugin/marketplace.json` under the `plugins` array
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
