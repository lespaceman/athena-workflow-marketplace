# Athena Workflow Marketplace

A marketplace of AI-powered browser automation workflows for Claude Code.

## Install the Marketplace

Add this marketplace to Claude Code:

```shell
# From GitHub
claude plugin marketplace add lespaceman/athena-workflow-marketplace

# From a local clone
claude plugin marketplace add ./athena-workflow-marketplace
```

## Install a Plugin

Once the marketplace is added, install a plugin:

```shell
claude plugin install e2e-test-builder@athena-workflow-marketplace
```

### Installation Scopes

```shell
# For yourself across all projects (default)
claude plugin install e2e-test-builder@athena-workflow-marketplace --scope user

# For all collaborators on a project (writes to .claude/settings.json)
claude plugin install e2e-test-builder@athena-workflow-marketplace --scope project

# For yourself in this repo only
claude plugin install e2e-test-builder@athena-workflow-marketplace --scope local
```

## Available Plugins

### e2e-test-builder

Iterative workflow for adding Playwright E2E tests to existing codebases. Full pipeline: analyze codebase → plan coverage → explore site → generate test specs → write tests. Supports stateless looping via athena-cli with a tracker file for cross-session state.

**Skills:**

| Skill | Description |
|-------|-------------|
| `/add-e2e-tests <url> <feature>` | Full pipeline orchestrator — runs all stages, maintains tracker |
| `/analyze-test-codebase [path]` | Detect Playwright config, test conventions, existing patterns |
| `/plan-test-coverage <url> <feature>` | Plan what to test based on existing coverage gaps |
| `/explore-website <url> <goal>` | Live browser interaction, selector extraction, form analysis |
| `/generate-test-cases <url> <journey>` | Explore site and produce structured TC-ID test specs |
| `/write-e2e-tests <description>` | Write executable Playwright test code following project conventions |

**Reference skill (auto-applied):** `agent-web-interface-guide` — MCP response patterns and best practices.

**MCP Server:** Uses [agent-web-interface](https://github.com/lespaceman/agent-web-interface) for browser control.

**Scaffolding:** If no Playwright config exists in the target project, automatically scaffolds from [playwright-typescript-e2e-boilerplate](https://github.com/lespaceman/playwright-typescript-e2e-boilerplate) with POM pattern, fixtures, and helpers.

---

### site-knowledge

Site-specific automation patterns for popular websites. These skills are auto-applied when relevant sites are detected — no manual invocation needed.

| Skill | Description |
|-------|-------------|
| `airbnb` | Airbnb.com automation patterns, element selectors, modal handling |
| `amazon` | Amazon.com product search, cart, buying options patterns |
| `apple-store` | Apple Store configuration flows, sequential form handling |
| `apple-testing-guide` | Playwright testing patterns specific to Apple.com |

## Adding a New Plugin

1. Create a directory under `plugins/`:

```
plugins/
└── my-new-plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── .mcp.json          # optional - MCP server config
    ├── skills/            # optional - slash commands and knowledge
    │   └── my-skill/
    │       └── SKILL.md
    └── hooks/             # optional - event hooks
        └── hooks.json
```

2. Create `plugins/my-new-plugin/.claude-plugin/plugin.json`:

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

3. Register it in `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "my-new-plugin",
      "source": "./plugins/my-new-plugin",
      "description": "What this plugin does",
      "version": "1.0.0"
    }
  ]
}
```

4. Commit, push, and update the marketplace:

```shell
claude plugin marketplace update athena-workflow-marketplace
```

## Managing the Marketplace

```shell
# List configured marketplaces
claude plugin marketplace list

# Update to pull latest plugins
claude plugin marketplace update athena-workflow-marketplace

# Remove the marketplace
claude plugin marketplace remove athena-workflow-marketplace

# List installed plugins
claude plugin list

# Disable/enable a plugin
claude plugin disable e2e-test-builder@athena-workflow-marketplace
claude plugin enable e2e-test-builder@athena-workflow-marketplace

# Update a plugin
claude plugin update e2e-test-builder@athena-workflow-marketplace

# Uninstall a plugin
claude plugin uninstall e2e-test-builder@athena-workflow-marketplace

# Validate a plugin or marketplace manifest
claude plugin validate ./plugins/my-plugin
```
