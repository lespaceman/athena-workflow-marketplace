# Athena Plugin Marketplace

Marketplace repository for:

1. Claude Code plugins (`plugins/`)
2. Athena workflows (`workflows/`)

## Spec

Workflow and manifest contracts are defined in:

- [RFC 0001: Long-Running Workflow Definition (Claude Plugin Compatible)](docs/rfcs/0001-workflow-marketplace-spec.md)
- [RFC 0002: Cross-Runtime Workflow And Plugin Packaging](docs/rfcs/0002-cross-runtime-packaging-spec.md)

Use this RFC as the source of truth for workflow behavior, lifecycle, and
cross-runtime plugin compatibility (skills, tools, and sub-agent/task
patterns).

## Repository Structure

```text
.
├── .claude-plugin/
│   └── marketplace.json            # Plugin catalog
├── .athena-workflow/
│   └── marketplace.json            # Workflow catalog
├── workflows/
│   └── e2e-test-builder/
│       ├── workflow.json
│       └── system_prompt.md
└── plugins/
    ├── e2e-test-builder/
    ├── md-export/
    └── site-knowledge/
```

## Skill Compatibility And Validation

This repo uses a split skill metadata model so the same skills stay compatible with both Claude and Codex:

- Portable skill core lives in `SKILL.md`
- Claude-specific invocation metadata lives in `agents/claude.yaml`
- OpenAI/Codex UI metadata lives in `agents/openai.yaml`

For the full conventions, see [docs/skills-compatibility.md](docs/skills-compatibility.md).

### Official Vendor Config vs Repo Overlays

Official vendor-aligned configuration lives outside this packaging layer:

- Claude Code officially documents project config in `.claude/settings.json` and `.claude/settings.local.json`
- Codex officially documents MCP/client configuration via `codex mcp add ...` and `~/.codex/config.toml`

This repo also defines its own packaging overlays for distributing skills and plugins across runtimes:

- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json`
- `agents/openai.yaml`
- `agents/claude.yaml`

These repo overlay files are conventions used by this repository. They are not presented here as official vendor-standard file formats.

### Local Environment

The repo includes a local Python 3.12 virtualenv at `.venv` for running the official Agent Skills validator.

Activate it with:

```shell
source .venv/bin/activate
```

### Validation Commands

Run the official portable validator across all plugin skills:

```shell
scripts/validate-skills-portable.sh
```

Run the repo-specific compatibility checks:

```shell
scripts/validate-skills-repo.sh
```

Run the lightweight local validator on a single skill:

```shell
scripts/quick-validate-skill.sh plugins/e2e-test-builder/skills/write-test-code
```

### Authoring Commands

Create a new repo-compatible skill scaffold:

```shell
scripts/init-compatible-skill.py my-skill --path plugins/my-plugin/skills --interface display_name="My Skill" --interface short_description="Describe the skill in the UI" --interface default_prompt="Run my skill." --argument-hint "<arg>"
```

Generate or update Claude-only overlay metadata for an existing skill:

```shell
scripts/generate-claude-yaml.py plugins/my-plugin/skills/my-skill --frontmatter user-invocable=true --frontmatter argument-hint="<arg>"
```

### Metadata Placement

Use these rules when editing or adding skills:

- Put only portable Agent Skills frontmatter in `SKILL.md`
- Put Claude-only fields like `argument-hint` and `user-invocable` in `agents/claude.yaml`
- Put menu copy like `display_name`, `short_description`, and `default_prompt` in `agents/openai.yaml`

### Source Of Truth And Regeneration

- Treat `SKILL.md` as the hand-authored source of truth for the skill itself
- `scripts/init-compatible-skill.py` scaffolds `SKILL.md`, `agents/openai.yaml`, and `agents/claude.yaml`
- `scripts/generate-claude-yaml.py` regenerates `agents/claude.yaml` for an existing skill
- `agents/claude.yaml` should be treated as generated overlay metadata and may be overwritten when regenerated
- `agents/openai.yaml` is created during scaffolding and may also be replaced if you rerun scaffold or metadata-generation flows for that skill
- If you hand-edit generated metadata files, assume those edits can be lost on regeneration unless you also update the generator inputs or process

## Install This Marketplace (Claude Plugin Consumers)

```shell
# From GitHub
claude plugin marketplace add lespaceman/athena-workflow-marketplace

# From local clone
claude plugin marketplace add ./athena-workflow-marketplace
```

## Install a Plugin

```shell
claude plugin install e2e-test-builder@athena-workflow-marketplace
```

### Installation Scopes

```shell
claude plugin install e2e-test-builder@athena-workflow-marketplace --scope user
claude plugin install e2e-test-builder@athena-workflow-marketplace --scope project
claude plugin install e2e-test-builder@athena-workflow-marketplace --scope local
```

## Available Plugins

### e2e-test-builder

Skills for building Playwright E2E tests for existing codebases.

| Skill | Description |
|-------|-------------|
| `add-e2e-tests` | Full pipeline orchestrator. Claude: `/add-e2e-tests`, Codex: `$add-e2e-tests` |
| `analyze-test-codebase` | Detect Playwright config and conventions. Claude: `/analyze-test-codebase`, Codex: `$analyze-test-codebase` |
| `plan-test-coverage` | Build prioritized coverage plan. Claude: `/plan-test-coverage`, Codex: `$plan-test-coverage` |
| `agent-web-interface-guide` | Extract selectors and behavior via browser interaction. Claude: `/agent-web-interface-guide`, Codex: `$agent-web-interface-guide` |
| `generate-test-cases` | Generate TC-ID based structured specs. Claude: `/generate-test-cases`, Codex: `$generate-test-cases` |
| `write-test-code` | Implement executable Playwright tests. Claude: `/write-test-code`, Codex: `$write-test-code` |

### site-knowledge

Auto-applied site-specific automation patterns.

| Skill | Description |
|-------|-------------|
| `airbnb` | Airbnb automation patterns |
| `amazon` | Amazon automation patterns |
| `apple-store` | Apple Store flow patterns |
| `apple-testing-guide` | Apple testing-specific guidance |

## Available Workflows

Workflows are registered in `.athena-workflow/marketplace.json` and implemented under `workflows/`.

| Workflow | Source |
|----------|--------|
| `e2e-test-builder` | `workflows/e2e-test-builder/workflow.json` |

Workflow intent:

- Orchestrate long-running multi-session execution
- Reuse existing Claude plugin capabilities
- Keep tracker-based progress and completion semantics portable across runtimes

## Add a New Plugin

1. Create a plugin directory under `plugins/<name>/`.
2. Add `plugins/<name>/.claude-plugin/plugin.json`.
3. Add `plugins/<name>/.codex-plugin/plugin.json` if the plugin needs Codex-specific metadata.
4. Register plugin in `.claude-plugin/marketplace.json` under `plugins[]`.

Minimal `plugin.json`:

```json
{
  "name": "my-new-plugin",
  "description": "What this plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

## Add a New Workflow

1. Create `workflows/<workflow-name>/workflow.json`.
2. Add any workflow-local assets in the same directory.
3. Register workflow in `.athena-workflow/marketplace.json` under `workflows[]`.
4. Keep schema/behavior aligned with RFC 0001.

Workflow registration example:

```json
{
  "workflows": [
    {
      "name": "my-workflow",
      "source": "./workflows/my-workflow/workflow.json",
      "description": "My reusable workflow"
    }
  ]
}
```

## Manage Plugin Marketplace (Claude)

```shell
claude plugin marketplace list
claude plugin marketplace update athena-workflow-marketplace
claude plugin marketplace remove athena-workflow-marketplace
claude plugin list
claude plugin disable e2e-test-builder@athena-workflow-marketplace
claude plugin enable e2e-test-builder@athena-workflow-marketplace
claude plugin update e2e-test-builder@athena-workflow-marketplace
claude plugin uninstall e2e-test-builder@athena-workflow-marketplace
claude plugin validate ./plugins/my-plugin
```
