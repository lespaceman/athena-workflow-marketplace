# Task: Add sentry MCP to engineering workflow

## Plan
- [x] Create plugins/sentry/ with all required plugin files (SKILL.md, manifests, package.json, openai.yaml, claude.yaml)
- [x] Register sentry in .claude-plugin/marketplace.json
- [x] Register sentry in .agents/plugins/marketplace.json
- [x] Add sentry@0.1.0 to workflows/fullstack-engineering/workflow.json plugins list
- [x] Update CLAUDE.md plugin inventory table
- [x] Validate skill (passed)
- [ ] Write plugins/sentry/.mcp.json (blocked by permission prompt — user must approve sensitive file)
- [x] Commit to main

## Current Status

All files created and validated. The `.mcp.json` (which configures the MCP server command) was blocked by the harness permission system on two attempts — the user must approve it via the permission prompt. All other files are complete and valid.

## Notes

- MCP server config pattern follows linear/clickup: `npx -y mcp-remote https://mcp.sentry.dev/mcp` (stdio bridge for Athena/Codex compatibility).
- Skill validated with quick-validate-skill.sh: "Skill is valid!"
- Workflow version not bumped (CI handles this per convention).
- `.mcp.json` content to write:
  ```json
  {
    "mcpServers": {
      "sentry": {
        "command": "npx",
        "args": ["-y", "mcp-remote", "https://mcp.sentry.dev/mcp"]
      }
    }
  }
  ```

<!-- WORKFLOW_COMPLETE -->
