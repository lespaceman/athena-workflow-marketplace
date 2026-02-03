# Athena Plugin Marketplace

A marketplace of AI-powered browser automation plugins for Claude Code.

## Install the Marketplace

Add this marketplace to Claude Code:

```shell
# From GitHub
/plugin marketplace add lespaceman/athena-plugin-marketplace

# From a local clone
/plugin marketplace add ./athena-plugin-marketplace
```

## Install a Plugin

Once the marketplace is added, install a plugin:

```shell
/plugin install web-testing-toolkit@athena-plugin-marketplace
```

### Installation Scopes

```shell
# For yourself across all projects (default)
/plugin install web-testing-toolkit@athena-plugin-marketplace --scope user

# For all collaborators on a project (writes to .claude/settings.json)
/plugin install web-testing-toolkit@athena-plugin-marketplace --scope project

# For yourself in this repo only
/plugin install web-testing-toolkit@athena-plugin-marketplace --scope local
```

## Available Plugins

### web-testing-toolkit

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
| `web-explorer` | Browses web pages, fills forms, clicks buttons, extracts page content and selectors |
| `test-case-generator` | Explores a live application and generates structured test cases from a user journey |
| `playwright-test-writer` | Converts discovered flows into Playwright test code, fixes flaky tests |

**Site-specific knowledge (auto-applied):**

- `airbnb` — Airbnb.com automation patterns
- `amazon` — Amazon.com automation patterns
- `apple-store` — Apple.com store automation patterns
- `apple-testing-guide` — Playwright testing patterns specific to Apple.com

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
/plugin marketplace update athena-plugin-marketplace
```

## Managing the Marketplace

```shell
# List configured marketplaces
/plugin marketplace list

# Update to pull latest plugins
/plugin marketplace update athena-plugin-marketplace

# Remove the marketplace
/plugin marketplace remove athena-plugin-marketplace

# Disable/enable a plugin
/plugin disable web-testing-toolkit@athena-plugin-marketplace
/plugin enable web-testing-toolkit@athena-plugin-marketplace

# Uninstall a plugin
/plugin uninstall web-testing-toolkit@athena-plugin-marketplace
```
