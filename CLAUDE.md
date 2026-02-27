# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code Workflow Marketplace** — a collection of AI-powered browser automation workflows.

- **e2e-test-builder** — Workflow runner for adding Playwright E2E tests to existing codebases. Full pipeline: analyze codebase → plan coverage → explore site → generate test specs → write tests. Uses subagent-driven development to save context.
- **site-knowledge** — Site-specific automation patterns for popular websites (Airbnb, Amazon, Apple Store).

This is not a Node.js project with build/test scripts. It is a metadata-driven plugin marketplace where runtime is managed by Claude Code and the `agent-web-interface` MCP server (installed dynamically via `npx`).

## Architecture

### Marketplace Structure

- `.claude-plugin/marketplace.json` — Central registry listing all plugins with `pluginRoot: ./plugins`
- `.athena-workflow/marketplace.json` — Central registry listing Athena workflows
- Each plugin lives under `plugins/<plugin-name>/` with its own `.claude-plugin/plugin.json` manifest

### e2e-test-builder Plugin

**Skills** (`plugins/e2e-test-builder/skills/<skill-name>/SKILL.md`): Each skill is a self-contained workflow with full knowledge embedded. Heavy browser/file work is delegated to general-purpose subagents via Task tool.

User-invocable skills (slash commands):
- `/add-e2e-tests <url> <feature>` — **Full pipeline orchestrator**: analyze → plan → explore → generate → write (uses subagents)
- `/analyze-test-codebase [path]` — Detect Playwright config, test conventions, existing patterns
- `/plan-test-coverage <url> <feature>` — Plan what to test based on existing coverage gaps
- `/explore-website <url> <goal>` — Live browser interaction, selector extraction, form analysis
- `/generate-test-cases <url> <user-journey>` — Explore site and produce structured TC-ID test specs
- `/write-e2e-tests <test-description>` — Write executable Playwright test code following project conventions

Reference skill (not user-invocable): `agent-web-interface-guide` — Documents MCP response patterns (state snapshots, observations, sequential forms, element attributes).

**Hooks** (`plugins/e2e-test-builder/hooks/hooks.json`): PostToolUse hooks that log browser events (navigation, clicks, type, select, session close) to `${CLAUDE_PLUGIN_ROOT}/logs/browser-log.txt`.

**MCP Config** (`plugins/e2e-test-builder/.mcp.json`): Configures `agent-web-interface` MCP server. All MCP tool names follow the pattern `mcp__plugin_e2e-test-builder_agent-web-interface__<tool>`.

**Workflow** (`.workflows/e2e-test-builder/workflow.json`): Athena-cli integration for stateless looping.
- `.workflows/e2e-test-builder/e2e-workflow-prompt.md` — system prompt appended via `--append-system-prompt-file`
- `e2e-tracker.md` (created in target project root) — tracker file, single source of truth across sessions
- `e2e-plan/` — planning artifacts: `conventions.md` (codebase analysis), `coverage-plan.md` (test plan)
- Completion markers in tracker: `<!-- E2E_COMPLETE -->` (success) or `<!-- E2E_BLOCKED: reason -->` (abort)
- Each stateless session: read tracker → execute one step → update tracker → exit

### site-knowledge Plugin

**Skills** (`plugins/site-knowledge/skills/<site-name>/SKILL.md`): Auto-applied site knowledge (not user-invocable) — injected as context when relevant sites are detected.

- `airbnb` — Airbnb.com automation patterns, element selectors, modal handling
- `amazon` — Amazon.com product search, cart, buying options patterns
- `apple-store` — Apple Store configuration flows, sequential form handling
- `apple-testing-guide` — Learnings from implementing Playwright tests for apple.com

## Adding a New Plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`, and optionally `skills/`, `hooks/`, `.mcp.json`
2. Register in `.claude-plugin/marketplace.json` under the `plugins` array
3. Skill files: YAML frontmatter with `name`, `description`, `user-invocable`, `argument-hint`, `allowed-tools` + markdown content

## Key Conventions

- Test case IDs use `TC-<FEATURE>-<NUMBER>` format (e.g., `TC-LOGIN-001`)
- Playwright locator preference: semantic (`getByRole`, `getByLabel`) > `data-testid` > text > CSS selectors
- No arbitrary `waitForTimeout` sleeps in generated tests — use event-driven waits
- Skill `allowed-tools` must explicitly list every MCP tool the skill needs
- Skills delegate heavy work to general-purpose subagents via Task tool to save main context
- Skill descriptions must include exhaustive trigger phrases and clearly state what the skill does vs doesn't do
