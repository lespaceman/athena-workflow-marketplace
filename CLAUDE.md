# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo is a **cross-runtime marketplace** that packages Claude Code plugins, Codex plugins, and Athena workflows from the same source tree. There is no application runtime here — the repo ships metadata, skills, and workflow definitions that are consumed by the Claude Code CLI, Codex, and `athena-cli`. Runtime execution is provided by those clients plus the `agent-web-interface` MCP server (installed dynamically via `npx`).

Contracts are defined in `docs/rfcs/0001-workflow-marketplace-spec.md` (workflow) and `docs/rfcs/0002-cross-runtime-packaging-spec.md` (cross-runtime packaging). Treat those RFCs as the source of truth when in doubt.

## Architecture

### Three parallel registries

Every deliverable is registered in exactly one of these catalogs — editing only one of the three will silently break one runtime:

1. `.claude-plugin/marketplace.json` — Claude Code plugins (`pluginRoot: ./plugins`).
2. `.agents/plugins/marketplace.json` — Codex plugins (one entry per plugin, `source.path: ./plugins/<name>`).
3. `.athena-workflow/marketplace.json` — Athena workflow definitions (`workflowRoot: ./workflows`).

### Plugin source layout

Each plugin under `plugins/<name>/` has:

- `.claude-plugin/plugin.json` — Claude Code manifest (keywords, repository, license).
- `.codex-plugin/plugin.json` — Codex manifest (`interface`, skills path, `mcpServers`).
- `.mcp.json` — MCP server config (only when the plugin ships an MCP server, e.g. `agent-web-interface`).
- `skills/<skill>/` — portable skills.
- `package.json` — npm package that builds versioned runtime artifacts.
- `dist/<version>/` — generated release artifacts (`release.json`, `claude/plugin/`, `codex/plugin/`, `codex/marketplace.json`). Output of `scripts/build-plugin-artifacts.mjs`; do not hand-edit.

Shared fields (`name`, `version`, `description`) must stay identical across both manifests. Use `scripts/bump-versions.sh` to sync versions across manifests and `package.json` files, and across all three marketplace registries.

### Split skill metadata

Skills use a three-file model so the same skill works on Claude and Codex:

- `skills/<skill>/SKILL.md` — portable Agent Skills core. Frontmatter limited to `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` (space-delimited string). Hand-authored.
- `skills/<skill>/agents/claude.yaml` — Claude-only overlay (`argument-hint`, `user-invocable`, `disable-model-invocation`, `model`, `hooks`, etc.). **Treated as generated** — regeneration via `scripts/generate-claude-yaml.py` may overwrite hand edits.
- `skills/<skill>/agents/openai.yaml` — Codex UI metadata (`display_name`, `short_description`, `default_prompt`). Also regenerable.

Use `scripts/init-compatible-skill.py` to scaffold all three.

### Plugin inventory

| Plugin | Role |
|--------|------|
| `agent-web-interface` | MCP browser server (Puppeteer/CDP) + live-interaction skill. Other plugins delegate browser work here. |
| `app-exploration` | Shared live-product exploration. Owns `e2e-plan/exploration-report.md`. |
| `test-analysis` | Shared coverage planning, TC-ID spec generation, spec review. Owns `e2e-plan/coverage-plan.md` and `test-cases/<feature>.md`. |
| `exploratory-testing` / `smoke-testing` / `regression-testing` | Intent layer — risk/scope charters before execution layer is chosen. |
| `playwright-automation` | Playwright execution layer: analyze codebase, write, review, fix flake. |
| `robot-automation` | Robot Framework (Browser library) execution layer with the same skill shape. |
| `site-knowledge` | Auto-applied site patterns (Airbnb, Amazon, Apple Store). Not user-invocable. |
| `md-export` | Markdown → dark-themed PDF (has `node_modules/` and `scripts/`; only plugin with runtime JS deps). |
| `web-bench` | WebBench benchmark runner and LLM-as-judge report pipeline. |

The canonical testing pipeline is layered: `app-exploration` → `test-analysis` → execution layer (`playwright-automation` or `robot-automation`). Installing only an execution plugin does not pull in the shared layers.

### Workflows

`workflows/<name>/` contains a `workflow.json` (RFC 0001 contract) and a `workflow.md` that is appended to the runtime's workflow prompt. `workflow.json` references plugins as `<plugin-name>@<owner>/<repo>` with a pinned version. `e2e-test-builder` and `robot-automation` are the primary long-running workflows; `exploratory-testing` / `smoke-testing` / `regression-testing` are intent workflows that hand off to execution workflows; `loop-test` and `web-bench` are specialized.

Note: `e2e-test-builder` exists only as a workflow name — there is no longer a plugin of that name. The execution plugins are `playwright-automation` and `robot-automation`.

## Build and validation

A local Python 3.12 virtualenv at `.venv` hosts the official Agent Skills validator:

```shell
source .venv/bin/activate
```

Validation:

```shell
scripts/validate-skills-portable.sh                      # official portable validator across all skills
scripts/validate-skills-repo.sh                          # repo-specific compatibility checks
scripts/quick-validate-skill.sh plugins/<p>/skills/<s>   # single-skill lightweight validator
node scripts/validate-playwright-suite.mjs               # layered Playwright suite
node scripts/validate-robot-suite.mjs                    # layered Robot suite
node scripts/validate-intent-suite.mjs                   # intent (charter) suite
```

Authoring and release:

```shell
scripts/init-compatible-skill.py <name> --path plugins/<plugin>/skills \
  --interface display_name="..." --interface short_description="..." \
  --interface default_prompt="..." --argument-hint "<arg>"

scripts/generate-claude-yaml.py plugins/<p>/skills/<s> \
  --frontmatter user-invocable=true --frontmatter argument-hint="<arg>"

scripts/bump-versions.sh                                 # sync versions across manifests + registries

cd plugins/<plugin> && npm run build:artifacts           # emits dist/<version>/ (also runs on prepack)
```

## Key conventions

- **Every plugin change touches three files minimum:** `plugins/<name>/.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and the matching registry entry in one or more of the three `marketplace.json` files. Version fields must match across them.
- **Test case IDs** use `TC-<FEATURE>-<NUMBER>` (e.g. `TC-LOGIN-001`).
- **Playwright locators:** semantic (`getByRole`, `getByLabel`) > `data-testid` > text > CSS. No arbitrary `waitForTimeout` — use event-driven waits.
- **Skill `allowed-tools`** must explicitly enumerate every tool (no wildcards). MCP tool names must match `mcp__plugin_<plugin-name>_<server-name>__<tool>` exactly.
- **Skills delegate heavy work to subagents via the Task tool** to protect main context. Browser tools live only in `agent-web-interface`; other plugins' skills reach them through subagents.
- **Test execution is never delegated.** In the `e2e-test-builder` / `robot-automation` workflows, the main agent must run `npx playwright test` (or `robot ...`) directly and keep the output as proof.
- **Skill descriptions** must include exhaustive trigger phrases and state what the skill does vs. does not do — skill dispatch depends on matching trigger language.
- `dist/` artifacts and `.venv/` are generated; do not commit hand edits to them.
