#!/usr/bin/env bash
# PreToolUse hook for agent-web-interface browser MCP tools.
# Injects a one-time reminder per session telling Claude to load the
# agent-web-interface-guide skill before using these tools. The skill
# documents selector capture, state observation, and recovery patterns
# that downstream exploration / test-writing skills depend on.

set -euo pipefail

STATE_DIR="${TMPDIR:-/tmp}/agent-web-interface-hook"
mkdir -p "$STATE_DIR"

# Scope the marker to the current Claude session so the reminder fires
# once per session, not once per tool call.
SESSION_ID="${CLAUDE_SESSION_ID:-${CLAUDE_CONVERSATION_ID:-default}}"
MARKER="$STATE_DIR/reminded-$SESSION_ID"

if [[ -f "$MARKER" ]]; then
  # Already reminded this session — allow the tool call silently.
  exit 0
fi

touch "$MARKER"

# Emit JSON additionalContext so Claude sees the reminder in-context
# without blocking the tool call.
cat <<'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "REMINDER: Before using agent-web-interface browser MCP tools, load the `agent-web-interface-guide` skill (via the Skill tool). It teaches the selector-capture, state-observation, eid-reacquisition, and multi-page recovery patterns that downstream exploration and test-writing skills depend on. Skipping it produces brittle CSS selectors, prose instead of structured observations, and stale `eid` reuse. Load it now, then proceed."
  }
}
JSON
