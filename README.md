# Athena Workflow Marketplace

Marketplace repository for:

1. Claude plugins (`plugins/`)
2. Athena workflows (`.workflows/`)

## Spec

Workflow and manifest contracts are defined in:

- [RFC 0001: Long-Running Workflow Definition (Claude Plugin Compatible)](docs/rfcs/0001-workflow-marketplace-spec.md)

Use this RFC as the source of truth for workflow behavior, lifecycle, and
Claude plugin compatibility (skills, tools, and sub-agent/task patterns).

## Repository Structure

```text
.
├── .claude-plugin/
│   └── marketplace.json            # Plugin catalog
├── .athena-workflow/
│   └── marketplace.json            # Workflow catalog
├── .workflows/
│   └── e2e-test-builder/
│       ├── workflow.json
│       └── system_prompt.md
└── plugins/
    ├── e2e-test-builder/
    └── site-knowledge/
```

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

Iterative workflow runner for adding Playwright E2E tests to existing codebases.

| Skill | Description |
|-------|-------------|
| `/add-e2e-tests <url> <feature>` | Full pipeline orchestrator |
| `/analyze-test-codebase [path]` | Detect Playwright config and conventions |
| `/plan-test-coverage <url> <feature>` | Build prioritized coverage plan |
| `/explore-website <url> <goal>` | Extract selectors and behavior via browser interaction |
| `/generate-test-cases <url> <journey>` | Generate TC-ID based structured specs |
| `/write-e2e-tests <description>` | Implement executable Playwright tests |

### site-knowledge

Auto-applied site-specific automation patterns.

| Skill | Description |
|-------|-------------|
| `airbnb` | Airbnb automation patterns |
| `amazon` | Amazon automation patterns |
| `apple-store` | Apple Store flow patterns |
| `apple-testing-guide` | Apple testing-specific guidance |

## Available Workflows

Workflows are registered in `.athena-workflow/marketplace.json` and implemented under `.workflows/`.

| Workflow | Source |
|----------|--------|
| `e2e-test-builder` | `.workflows/e2e-test-builder/workflow.json` |

Workflow intent:

- Orchestrate long-running multi-session execution
- Reuse existing Claude plugin capabilities
- Keep tracker-based progress and completion semantics portable across runtimes

## Add a New Plugin

1. Create a plugin directory under `plugins/<name>/`.
2. Add `plugins/<name>/.claude-plugin/plugin.json`.
3. Register plugin in `.claude-plugin/marketplace.json` under `plugins[]`.

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

1. Create `.workflows/<workflow-name>/workflow.json`.
2. Add any workflow-local assets in the same directory.
3. Register workflow in `.athena-workflow/marketplace.json` under `workflows[]`.
4. Keep schema/behavior aligned with RFC 0001.

Workflow registration example:

```json
{
  "workflows": [
    {
      "name": "my-workflow",
      "source": "./.workflows/my-workflow/workflow.json",
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
