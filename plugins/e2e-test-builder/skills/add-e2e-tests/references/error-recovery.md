# Error Recovery for Infrastructure Failures

When infrastructure failures occur during E2E test building, follow the general pattern: diagnose, attempt one known fix, if still stuck record in tracker and ask the user.

## Browser MCP unavailable

The browser MCP server (`agent-web-interface`) must be running for site exploration.

1. Verify the MCP server is configured in the project (check `.mcp.json` or plugin config).
2. Ask the user to confirm the MCP server is running or to restart it.
3. If unreachable after user intervention, mark the session as blocked: `<!-- E2E_BLOCKED: browser MCP server unreachable -->`.

## Boilerplate clone fails

When `git clone git@github.com:lespaceman/playwright-typescript-e2e-boilerplate.git` fails:

1. Check if SSH keys are configured — the error will usually indicate `Permission denied (publickey)`.
2. Fall back to HTTPS: `git clone https://github.com/lespaceman/playwright-typescript-e2e-boilerplate.git`.
3. If both fail, ask the user to verify network access and GitHub authentication.

## npm install fails

1. Check the Node.js version — Playwright requires Node 18+. Run `node --version`.
2. Clear the npm cache: `npm cache clean --force`.
3. Check for lockfile conflicts — if both `package-lock.json` and `yarn.lock` exist, ask the user which package manager to use.
4. If dependency resolution fails, try `npm install --legacy-peer-deps` as a fallback.

## Playwright browser install fails

When `npx playwright install --with-deps chromium` fails:

1. Try installing just chromium without system deps: `npx playwright install chromium`.
2. Check permissions — on Linux, system dependency installation may require sudo.
3. If behind a corporate proxy, ask the user for proxy configuration.
4. As a last resort, ask the user to run the install command manually and confirm when done.

## General pattern

For any infrastructure failure not listed above:

1. **Diagnose** — read the error message carefully, check logs, identify the root cause.
2. **Attempt one known fix** — apply the most likely solution based on the error.
3. **If still stuck** — record the full error output and diagnostic steps taken in the tracker, then ask the user for help. Do not loop through multiple speculative fixes.
