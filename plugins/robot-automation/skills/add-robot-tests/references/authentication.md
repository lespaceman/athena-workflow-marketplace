# Authentication Handling for Robot Framework Tests

If the target feature requires login or any form of authentication:

1. **Check existing infrastructure** — look for existing keyword resources (e.g., `resources/auth.resource`), environment variables, stored browser state files (`auth/*.json`), or project-level authentication listeners. Load the `analyze-test-codebase` skill to find auth patterns.
2. **Ask the user if no auth setup exists** — request credentials or an auth strategy (stored browser state via `New Context    storageState=auth.json`, API tokens, test accounts). Do not proceed with tests that require login until auth is resolved.
3. **Never hardcode credentials** — pass them via `--variable EMAIL:... --variable PASSWORD:...`, read from a `.env` file via a listener or `variables.py`, or reuse the project's existing auth keyword/resource.
4. **Handle mid-session auth discovery** — if you discover auth is needed mid-session (e.g., a page redirects to login), ask the user immediately and add auth setup as a prerequisite task.
