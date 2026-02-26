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

AI-driven browser automation for web exploration, test case generation, and Playwright E2E test writing.

**Slash Commands (user-invocable skills):**

| Command | Description |
|---------|-------------|
| `/explore-website` | Explore, navigate, and interact with a website using a browser |
| `/generate-test-cases` | Generate comprehensive test cases from a URL and user journey |
| `/write-e2e-tests` | Write, refactor, or fix Playwright E2E tests |

**Agents:**

| Agent | Description |
|-------|-------------|
| `browser-operator` | Completes browser tasks (add to cart, fill forms, find info), explores sites, extracts selectors |
| `test-case-generator` | Explores a live application and generates structured test cases from a user journey |
| `playwright-test-writer` | Converts discovered flows into Playwright test code, fixes flaky tests |

**Site-specific knowledge (auto-applied):**

- `airbnb` — Airbnb.com automation patterns
- `amazon` — Amazon.com automation patterns
- `apple-store` — Apple.com store automation patterns
- `apple-testing-guide` — Playwright testing patterns specific to Apple.com
- `agent-web-interface-guide` — MCP response patterns and best practices

**MCP Server:** Uses [agent-web-interface](https://github.com/lespaceman/agent-web-interface) for browser control.

## Adding a New Plugin

1. Create a directory under `plugins/`:

```
plugins/
└── my-new-plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── .mcp.json          # optional - MCP server config
    ├── agents/            # optional - agent definitions
    │   └── my-agent.md
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
