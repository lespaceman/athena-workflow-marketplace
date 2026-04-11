# Error Recovery for Infrastructure Failures

When infrastructure failures occur during Robot Framework test building, follow the general pattern: diagnose, attempt one known fix, if still stuck ask the user.

## Browser MCP unavailable

The browser MCP server (`agent-web-interface`) must be running for site exploration.

1. Verify the MCP server is configured in the project (check `.mcp.json` or plugin config).
2. Ask the user to confirm the MCP server is running or to restart it.
3. If unreachable after user intervention, this is an unrecoverable blocker — inform the user that browser exploration cannot proceed.

## `pip install robotframework-browser` fails

1. Check the Python version — `robotframework-browser` requires Python 3.8+. Run `python3 --version`.
2. Confirm `pip` resolves to the right interpreter (`python3 -m pip --version`).
3. If the target project uses a virtualenv or Poetry, install inside it (`poetry add --group dev robotframework-browser` or activate the venv first).
4. If dependency resolution fails, try `pip install --upgrade pip` first, then retry.

## `rfbrowser init` fails

`rfbrowser init` downloads the Playwright browsers that Browser library wraps. Common failure modes:

1. **Node.js missing** — Browser library needs Node.js 18+. Run `node --version`. If absent, ask the user to install Node 18+ before retrying.
2. **Corporate proxy / offline** — set `HTTPS_PROXY` or ask the user for the proxy configuration, then retry.
3. **Permission errors on browsers dir** — do not escalate to sudo silently; ask the user.
4. **Disk space** — Playwright browsers need ~1 GB. If the failure mentions space, ask the user.

As a last resort, ask the user to run `rfbrowser init` manually and confirm when done.

## `robot` command not found

1. Confirm `robotframework` is installed: `python3 -m pip show robotframework`.
2. If installed but `robot` is not on PATH, run tests via `python3 -m robot ...` instead.
3. If not installed, ask the user to run `pip install robotframework robotframework-browser` and retry.

## General pattern

For any infrastructure failure not listed above:

1. **Diagnose** — read the error message carefully, check logs, identify the root cause.
2. **Attempt one known fix** — apply the most likely solution based on the error.
3. **If still stuck** — ask the user for help with the full error output and diagnostic steps taken. Do not loop through multiple speculative fixes.
