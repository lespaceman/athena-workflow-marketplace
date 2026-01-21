---
name: snapshot
description: Capture a semantic snapshot of the current page state including elements and accessibility tree.
---

# Capture Snapshot

Capture the current state of the browser page for analysis and element discovery.

## Usage

```
/athena-browser:common/snapshot [--page-id <id>]
```

## Options

- `--page-id <id>`: Specify the page ID (uses default if not provided)

## Instructions

1. Use the `capture_snapshot` MCP tool to get the current page state
2. The snapshot includes:
   - Page URL and title
   - Semantic element tree
   - Interactive elements with their eids (element IDs)
   - Accessibility information
3. Use this snapshot to understand the page structure before interacting

## MCP Tool Reference

**Tool**: `capture_snapshot`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_id` | string | No | Page identifier (optional) |

## Example Workflow

```
1. Call capture_snapshot (optionally with page_id)
2. Receive page state including:
   - URL and title
   - Interactive elements with eids
   - Page structure
3. Report to user:
   - Current URL
   - Page title
   - Key interactive elements found
```

## When to Use

- After navigation to understand page structure
- Before clicking or typing to find correct element IDs (eids)
- When debugging interaction failures
- To verify page state after actions

## Notes

- Snapshots are point-in-time; re-capture after page changes
- Element IDs (eids) are required for click/type operations
- Use `find_elements` for targeted element discovery after snapshot
