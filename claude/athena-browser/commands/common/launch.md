---
name: launch
description: Launch a new browser instance for automation. Supports headless and visible modes.
---

# Launch Browser

Launch a new browser instance using athena-browser-mcp for automation tasks.

## Usage

```
/athena-browser:common/launch [--headless] [--visible]
```

## Options

- `--headless`: Launch browser in headless mode (default)
- `--visible`: Launch browser with visible UI for debugging

## Instructions

1. Use the `launch_browser` MCP tool to start a new browser instance
2. By default, launch in headless mode unless `--visible` is specified
3. Store the returned page_id for subsequent operations
4. Report the browser status and page_id to the user

## MCP Tool Reference

**Tool**: `launch_browser`

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headless` | boolean | true | Run browser without visible window |

## Example Workflow

```
1. Call launch_browser with headless: true (or false for visible)
2. Receive page_id in response
3. Report to user:
   - Browser launched successfully
   - Page ID: {page_id}
   - Mode: Headless/Visible
   - Ready for navigation
```

## Notes

- Always launch a browser before performing any navigation or interaction
- Use visible mode (`--visible`) when debugging complex workflows
- The browser instance persists until explicitly closed with `/athena-browser:common/close`
- Store the page_id for use with other commands
