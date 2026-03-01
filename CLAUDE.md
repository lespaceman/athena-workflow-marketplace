# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code Workflow Marketplace** — a collection of AI-powered browser automation workflows.

- **e2e-test-builder** — Workflow runner for adding Playwright E2E tests to existing codebases. Full pipeline: analyze codebase → plan coverage → explore site → generate test specs → write tests. Uses subagent-driven development to save context.
- **site-knowledge** — Site-specific automation patterns for popular websites (Airbnb, Amazon, Apple Store).

This is not a Node.js project with build/test scripts. It is a metadata-driven plugin marketplace where runtime is managed by Claude Code and the `agent-web-interface` MCP server (installed dynamically via `npx`).

## Architecture

### Two Parallel Registries

1. **Claude Plugin Marketplace** — `.claude-plugin/marketplace.json` — registers plugins for `claude plugin` CLI (`pluginRoot: ./plugins`)
2. **Athena Workflow Marketplace** — `.athena-workflow/marketplace.json` — registers workflow definitions for `athena-cli` (`workflowRoot: ./.workflows`)

### e2e-test-builder Plugin

**Skills** (`plugins/e2e-test-builder/skills/<skill-name>/SKILL.md`): Each skill is a self-contained workflow with full knowledge embedded. Heavy browser/file work is delegated to general-purpose subagents via Task tool.

User-invocable skills (slash commands):
- `/add-e2e-tests <url> <feature>` — **Full pipeline orchestrator**: analyze → plan → explore → generate → write (uses subagents)
- `/analyze-test-codebase [path]` — Detect Playwright config, test conventions, existing patterns
- `/plan-test-coverage <url> <feature>` — Plan what to test based on existing coverage gaps
- `/explore-website <url> <goal>` — Live browser interaction, selector extraction, form analysis
- `/generate-test-cases <url> <user-journey>` — Explore site and produce structured TC-ID test specs
- `/write-e2e-tests <test-description>` — Write executable Playwright test code following project conventions
- `/fix-flaky-tests <test-file-or-name>` — Diagnose and fix intermittent test failures

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

**Skills** (`plugins/site-knowledge/skills/<site-name>/SKILL.md`): Auto-applied site knowledge (not user-invocable) — injected as context when relevant sites are detected. Covers Airbnb, Amazon, Apple Store, and Apple testing patterns.

## Workflow System (RFC 0001)

The `workflow.json` contract defines stateless looping sessions:
- `loop.completionMarkers` — HTML comments (`E2E_COMPLETE`, `E2E_BLOCKED`) that signal termination
- `loop.trackerFile` — markdown file tracking step-by-step progress
- `loop.maxIterations` — safety cap on session count
- `plugins[]` — references plugins as `<plugin-name>@<owner>/<repo>`

Steps 5 and 6 (test execution and coverage check) are NEVER delegated to subagents — the main agent must run `npx playwright test` directly and record output as proof.

## Adding a New Plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`, and optionally `skills/`, `hooks/`, `.mcp.json`
2. Register in `.claude-plugin/marketplace.json` under the `plugins` array
3. Skill files: YAML frontmatter with `name`, `description`, `user-invocable`, `argument-hint`, `allowed-tools` + markdown content

## Adding a New Workflow

1. Create `.workflows/<name>/workflow.json` following the RFC 0001 contract
2. Add a system prompt file in the same directory if needed
3. Register in `.athena-workflow/marketplace.json` under `workflows[]`

## Key Conventions

- Test case IDs use `TC-<FEATURE>-<NUMBER>` format (e.g., `TC-LOGIN-001`)
- Playwright locator preference: semantic (`getByRole`, `getByLabel`) > `data-testid` > text > CSS selectors
- No arbitrary `waitForTimeout` sleeps in generated tests — use event-driven waits
- Skill `allowed-tools` must explicitly list every MCP tool the skill needs (no wildcards)
- MCP tool names must match exactly: `mcp__plugin_<plugin-name>_<server-name>__<tool>`
- Skills delegate heavy work to general-purpose subagents via Task tool to save main context
- Skill descriptions must include exhaustive trigger phrases and clearly state what the skill does vs doesn't do
