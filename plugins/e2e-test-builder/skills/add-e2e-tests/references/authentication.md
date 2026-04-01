# Authentication Handling for E2E Tests

If the target feature requires login or any form of authentication:

1. **Check existing infrastructure** — look for existing test fixtures, environment variables, or auth setup files that already handle authentication. Load the `analyze-test-codebase` skill to find auth patterns.
2. **Ask the user if no auth setup exists** — request credentials or an auth strategy (stored auth state, API tokens, test accounts). Do not proceed with tests that require login until auth is resolved.
3. **Never hardcode credentials** — use environment variables, Playwright's `storageState`, or the project's existing auth fixture pattern.
4. **Handle mid-session auth discovery** — if you discover auth is needed mid-session (e.g., a page redirects to login), ask the user immediately and add auth setup as a prerequisite task.
