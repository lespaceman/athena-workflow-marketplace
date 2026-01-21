---
description: Close the browser session and clean up resources.
---

# Close Browser Session

Terminate the browser session and release all associated resources.

## Usage

```
/athena-browser:common/close [--page-id <id>]
```

## Options

- `--page-id <id>`: Close a specific page (closes entire session if not provided)

## Instructions

1. Use `close_session` to close the entire browser session
2. Or use `close_page` to close a specific page by page_id
3. Confirm closure to the user

## MCP Tool Reference

### Close Entire Session

**Tool**: `close_session`

**Parameters**: None

### Close Specific Page

**Tool**: `close_page`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_id` | string | Yes | Page identifier to close |

## Example Workflow

```
1. Call close_session (or close_page with page_id)
2. Receive confirmation
3. Report to user:
   - Browser session closed successfully
   - All pages terminated
   - Resources released
```

## When to Use

- After completing automation tasks
- When switching to a different website workflow
- To free up system resources
- When encountering unrecoverable browser errors

## Notes

- Always close browser sessions when done to prevent resource leaks
- Closing a session invalidates all page IDs associated with it
- Consider saving any needed data before closing
