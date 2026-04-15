---
name: write-test-code
description: >
  This skill should be used when writing, refactoring, or modifying Playwright E2E test code.
  It covers creating test files from TC-ID specs, converting browser exploration results to
  executable tests, refactoring locators or fixtures, adding API mocking, test data
  setup/teardown, and parallel-safe isolation. Includes locator strategy hierarchy, auth setup
  patterns, fixture design, teardown strategies, and network interception recipes.
  Triggers: "write a test for", "add a test case", "refactor this locator", "add error path
  tests", "convert specs to code", "add API mocking", "set up auth for tests".
  NOT for: full pipeline from scratch (use add-playwright-tests), exploring live sites (use
  agent-web-interface-guide), generating specs without code (use plan-test-coverage or
  generate-test-cases), diagnosing flaky tests (use fix-flaky-tests).
allowed-tools: Read Write Edit Bash Glob Grep Task
---

# Write E2E Tests

Write, refactor, or fix Playwright E2E tests. Convert browser exploration results or test case specifications into executable, stable test code.

## Input

Parse the test description or spec file path from: $ARGUMENTS

## Workflow

### 1. Understand the Request
- Identify the user journey to test and success criteria
- Identify preconditions (auth, seeded data, feature flags, env)
- If a test case spec file path is provided, read it for TC-IDs and expected behaviors

### 2. Inspect Repo Conventions (CRITICAL — before writing any code)
- Search for `playwright.config.ts` / `playwright.config.js` — extract `baseURL`, `testDir`, projects
- Search for existing tests, fixtures, page objects, locator patterns, test data modules
- Read 2-3 existing test files to match the project's naming, structure, and locator strategy
- Check for custom fixtures, POM patterns, auth setup (storageState, global setup)
- Follow the project's existing style unless it clearly causes flakiness

### 3. Verify Key Selectors Against the Live Site
- If a test case spec file includes **Selectors observed**, use those as your starting point
- If no spec or selectors are available, browse the target page using `agent-web-interface-guide` to discover the actual selectors before writing code — do not guess
- Spot-check 2-3 critical selectors with `find` or `get_element` to confirm they resolve to the intended elements

### 4. Implement Tests
- Add/adjust fixtures and page objects first (if needed)
- Write tests in a story-like flow with AAA structure: Arrange → Act → Assert
- Add assertions that represent user outcomes
- **For large suites:** Use subagents (Task tool) to write individual test files in parallel.
  Pass each subagent the test case spec path, codebase conventions from Step 2, and the
  operating principles from this skill. Only split when files have independent responsibilities.

### 5. Stabilize
- Replace any sleeps with meaningful waits
- Tighten locators to avoid ambiguity
- For network-driven flows, use `page.waitForResponse` for critical checkpoints

### 6. Verify
- Run the smallest relevant test command: `npx playwright test <file> --reporter=list 2>&1`
- In CI or headless environments (no display), never use `--headed` — it will fail silently or hang
- Use `--headed` only during local interactive debugging when you need to visually observe the test
- Fix root causes rather than extending timeouts

### 7. Summarize
Return:
1. **What I changed** (bullets)
2. **Test case IDs added** (list all new TC-IDs with brief description)
3. **Why it's stable** (locator/wait strategy used)
4. **How to run** (exact commands)
5. **Notes / follow-ups** (optional)

## Operating Principles (Non-Negotiable)

### Test User Outcomes
Assert what the user sees — visible text, URL changes, enabled/disabled states — not internal state, CSS classes, or component hierarchy.

### No Arbitrary Sleeps
Avoid `page.waitForTimeout()` except as a last-resort debug aid — remove before finishing.

### Locator Strategy
| Priority | Method | When to Use |
|----------|--------|-------------|
| 1 | `getByRole('role', { name })` | Buttons, links, headings, form controls |
| 2 | `getByLabel()` | Form fields with visible labels |
| 3 | `getByPlaceholder()` | Inputs with placeholder text |
| 4 | `getByTestId()` | When data-testid is available |
| 5 | `getByText()` | Short, stable text (avoid marketing copy) |
| 6 | CSS selectors | Last resort, always scoped tightly |

Avoid `.first()` / `.nth()` unless a strong, documented reason exists — scope locators to a container instead.

**Within-file consistency:** Every test file must use ONE locator approach for equivalent elements. Do not mix `getByPlaceholder('Email')` in one test with `page.locator('input[placeholder="Email"]')` in another test within the same file. When adding tests to an existing file, match the locator style already in use. If the existing style is suboptimal, refactor all locators in the file together — do not create inconsistency.

### Waiting Strategy
- Prefer Playwright auto-waits via actions and `expect(...)` assertions
- If explicit waiting needed, wait for meaningful state: visibility, enabled, URL, specific network response, spinner gone

### Test Case IDs
- Every test MUST have a unique TC-ID: `TC-<FEATURE>-<NNN>`
- Include in test title: `test('TC-LOGIN-001: User can log in with valid credentials', ...)`
- Sequential within feature area, never reused
- When adding to existing file, check existing IDs and continue the sequence

### POM + Fixtures
- If the project has a `pages/` directory or BasePage class, ALL new tests MUST use Page Objects for interactions
- Page Objects contain HOW (locators + interactions)
- Tests contain WHAT (behavior/outcome to verify)
- Keep page objects thin and composable
- If the boilerplate shipped a BasePage that no tests reference, either extend it for your feature or flag it for removal — do not leave dead infrastructure

### Determinism and Isolation
- Tests must not depend on execution order
- Use unique test data per test or suite
- **Parallel-safe mutations:** When `fullyParallel: true` is configured, tests run concurrently across workers. A test that creates a record (e.g., a ticket) and then asserts it appears in a list WILL race with other tests creating records. Solutions: (a) assert on the specific record you created (filter/search by the unique ID from your API setup), not on list position or count; (b) use `test.describe.serial` for flows that genuinely require sequence (create-then-verify); (c) scope list assertions with `.filter({ hasText: uniqueIdentifier })` to avoid seeing other workers' data.

### Assertions
- Use Playwright `expect` matchers (auto-retry, better error messages)
- Avoid `isVisible()` + `expect(true)` pattern

### Configuration Hygiene
- Use `baseURL` and relative navigation (`page.goto('/')`)
- Avoid hardcoded domains/URLs in tests
- Configure `trace: 'on-first-retry'`, `screenshot: 'only-on-failure'`, `video: 'on-first-retry'` for CI debugging
- Set `retries: process.env.CI ? 2 : 0` — retries in CI only
- View traces with `npx playwright show-trace trace.zip` to time-travel through failures
- If `tsconfig.json` defines path aliases (e.g., `@pages/*`, `@fixtures/*`, `@utils/*`), use them in imports instead of relative paths. Check tsconfig paths before writing any import statement.

### Authentication Setup
Use `storageState` for most projects (log in once in global setup, reuse across tests).
For parallel workers needing separate accounts, use worker-scoped fixtures.
For multi-role tests (admin + user), create separate browser contexts.
Per-test login is only for testing the login flow itself.
Never hardcode tokens — use environment variables or `.env.test`.

See [references/auth-patterns.md](references/auth-patterns.md) for full patterns with code examples.

### API-Driven Test Setup and Teardown
Use API calls (not UI clicks) to seed test data — 10-50x faster and more reliable.
Use UI setup only when the creation flow IS the test. Tests that create persistent data
MUST clean up: use `afterEach` API deletion, fixture-with-cleanup, or bulk `globalTeardown`.
If no cleanup endpoint exists, document the gap with a TODO.

See [references/api-setup-teardown.md](references/api-setup-teardown.md) for full patterns with code examples.

### Network Interception and Error Paths
Use `page.route()` to mock server errors, patch responses, assert backend calls, or block
heavy resources. Add error path tests when they meaningfully apply to the feature: for example,
server/network failures for backend-driven flows, empty states for collection/data-driven UIs,
and session/auth cases for gated features. If a category is not applicable, do not invent it.

See [references/network-interception.md](references/network-interception.md) for full patterns with code examples.

### Custom Fixtures (test.extend)

Use `test.extend` to create reusable test setup without duplicating code:

```typescript
// fixtures/index.ts
import { test as base, Page } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

export const test = base.extend<{
  loginPage: LoginPage;
  authenticatedPage: Page;
}>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'tests/.auth/user.json'
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});
export { expect } from '@playwright/test';
```

Import `test` from your fixtures file, not from `@playwright/test`, in test files that need custom fixtures.

### Mapping Tables
When converting journey specs or exploration results to code, consult the mapping tables
for standard translations of scopes, actions, assertions, and target kinds to Playwright API calls.
For low-confidence journey steps (<0.7), add extra assertions and include fallback locators as comments.

See [references/mapping-tables.md](references/mapping-tables.md) for the full tables.

## Test Template

```typescript
// If the project has custom fixtures (fixtures/index.ts), import from there:
//   import { test, expect } from '@fixtures/index';
// Otherwise, use the default:
import { test, expect } from '@playwright/test';

test('TC-FEATURE-001: Description of test case', async ({ page }) => {
  // Arrange
  await page.goto('/feature-path');

  // Act
  await page.getByRole('button', { name: /submit/i }).click();

  // Assert
  await expect(page.getByText(/success/i)).toBeVisible();
});
```

Always check for a project fixtures file before using the default import. If custom fixtures exist, you MUST import from them to get access to page objects and custom setup.

## Anti-Patterns (Quick Reference)
1. Raw CSS selectors — use semantic locators
2. `waitForTimeout()` — use proper assertions/waits
3. Fragile `.nth()` / `.first()` — scope to container
4. Exact long text matches — use regex with key words
5. Unscoped locators — scope to container
6. Login via UI in every test — use storageState
7. UI clicks for test data setup — use API
8. No error path tests — add failure scenarios
9. Hardcoded test data — use API setup + dynamic values
10. Tests depending on execution order
11. `expect(await el.isVisible()).toBe(true)` — use `await expect(el).toBeVisible()`
12. `{ force: true }` — diagnose root cause instead
13. `networkidle` as default wait — use specific response waits
14. CSS utility class selectors (Tailwind/Bootstrap)
15. Asserting exact server-computed values — use patterns or seed data

See [references/anti-patterns.md](references/anti-patterns.md) for detailed explanations and fix strategies.
