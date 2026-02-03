# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code Plugin Marketplace** — a collection of AI-powered browser automation plugins. The primary plugin is `web-testing-toolkit`, which provides browser automation for web exploration, test case generation, and Playwright E2E test writing.

This is not a Node.js project with build/test scripts. It is a metadata-driven plugin marketplace where runtime is managed by Claude Code and the `agent-web-interface` MCP server (installed dynamically via `npx`).

## Architecture

### Marketplace Structure

- `.claude-plugin/marketplace.json` — Central registry listing all plugins with `pluginRoot: ./plugins`
- Each plugin lives under `plugins/<plugin-name>/` with its own `.claude-plugin/plugin.json` manifest

### Plugin Components (web-testing-toolkit)

**Agents** (`plugins/web-testing-toolkit/agents/*.md`): Specialized AI sub-agents invoked via the Task tool. Each is a markdown file with YAML frontmatter (`name`, `description`, `model`, `color`) and a system prompt body.

- `web-explorer` — Live browser navigation, form filling, selector extraction. Does NOT generate test specs or write test code.
- `test-case-generator` — Systematic site exploration producing structured test case specs (TC-ID format). Does NOT write executable test code.
- `playwright-test-writer` — Converts test specs into Playwright TypeScript tests. Does NOT do live browser exploration.

These three agents have strict responsibility boundaries. Route work to the correct agent.

**Skills** (`plugins/web-testing-toolkit/skills/<skill-name>/SKILL.md`): Markdown files with YAML frontmatter (`name`, `description`, `user-invocable`, `argument-hint`, `allowed-tools`).

User-invocable skills (slash commands):
- `/explore-website <url> <goal>` — Delegates to web-explorer agent
- `/generate-test-cases <url> <user-journey>` — Delegates to test-case-generator agent
- `/write-e2e-tests <test-description>` — Delegates to playwright-test-writer agent

Auto-applied site knowledge (not user-invocable): `airbnb`, `amazon`, `apple-store`, `apple-testing-guide` — injected as context when relevant sites are detected.

**Hooks** (`plugins/web-testing-toolkit/hooks/hooks.json`): PostToolUse hooks that log browser events (navigation, clicks, session close) to `/tmp/agent-browser-log.txt`.

**MCP Config** (`plugins/web-testing-toolkit/.mcp.json`): Configures `agent-web-interface` MCP server providing browser control tools (navigate, click, type, find_elements, etc.). All MCP tool names follow the pattern `mcp__agent-web-interface__<tool>`.

## Adding a New Plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`, and optionally `agents/`, `skills/`, `hooks/`, `.mcp.json`
2. Register in `.claude-plugin/marketplace.json` under the `plugins` array
3. Agent files: YAML frontmatter with `name`, `description`, `model`, `color` + markdown system prompt
4. Skill files: YAML frontmatter with `name`, `description`, `user-invocable`, `argument-hint`, `allowed-tools` + markdown content

## Key Conventions

- Test case IDs use `TC-<FEATURE>-<NUMBER>` format (e.g., `TC-LOGIN-001`)
- Playwright locator preference: semantic (`getByRole`, `getByLabel`) > `data-testid` > text > CSS selectors
- No arbitrary `waitForTimeout` sleeps in generated tests — use event-driven waits
- Skill `allowed-tools` must explicitly list every MCP tool the skill needs
