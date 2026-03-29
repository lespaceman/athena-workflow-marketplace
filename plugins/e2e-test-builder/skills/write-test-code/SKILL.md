---
name: write-test-code
description: >
  Invoke when the user wants executable Playwright test code produced or changed. This is the
  implementation skill for E2E tests, whether starting from a scenario or a TC-ID spec. If the task
  produces or modifies executable test code, use this skill. Covers: creating test files,
  converting TC-IDs to runnable code, refactoring locators or fixtures, adding API mocking, test data
  setup/teardown, parallel-safe isolation, modifying test infrastructure (testIgnore, config, fixtures,
  auth, helpers, path aliases). IMPORTANT: Load this skill before editing any test infrastructure — it
  has 15 anti-patterns to avoid (force:true, networkidle, Tailwind selectors, hardcoded data, exact
  numeric assertions) plus configuration hygiene and fixture design principles. Do NOT use for:
  exploring a live site (use agent-web-interface-guide), generating test plans/specs without code
  (use plan-test-coverage or generate-test-cases), diagnosing flaky tests (use fix-flaky-tests).
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
- Every test MUST have a unique TC-ID: `TC-<FEATURE>-<NUMBER>`
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

Choose the right auth strategy based on the project's needs:

**Strategy 1: storageState (Recommended for most projects)**
Log in once in global setup, save cookies/localStorage to a JSON file, and reuse across all tests:

```typescript
// global-setup.ts
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel(/password/i).fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: 'tests/.auth/user.json' });
  await browser.close();
}
export default globalSetup;
```

Reference in config: `use: { storageState: 'tests/.auth/user.json' }`

**Strategy 2: Worker-scoped fixture (for parallel workers needing separate accounts)**
```typescript
export const test = base.extend<{}, { workerStorageState: string }>({
  storageState: ({ workerStorageState }, use) => use(workerStorageState),
  workerStorageState: [async ({ browser }, use, testInfo) => {
    const page = await browser.newPage({ storageState: undefined });
    // Login with worker-specific account...
    const path = `tests/.auth/worker-${testInfo.parallelIndex}.json`;
    await page.context().storageState({ path });
    await use(path);
    await page.close();
  }, { scope: 'worker' }],
});
```

**Strategy 3: Multi-role testing (admin + user in same test)**
```typescript
test('TC-ADMIN-001: Admin sees user profile', async ({ browser }) => {
  const adminContext = await browser.newContext({ storageState: 'tests/.auth/admin.json' });
  const userContext = await browser.newContext({ storageState: 'tests/.auth/user.json' });
  const adminPage = await adminContext.newPage();
  const userPage = await userContext.newPage();
  // Interact with both pages...
  await adminContext.close();
  await userContext.close();
});
```

**Strategy 4: Per-test login** — only when testing login itself or permission-specific scenarios.

Never hardcode tokens. Use environment variables or `.env.test`.

### API-Driven Test Setup

Use API calls to set up test data instead of clicking through UI. This is 10-50x faster and more reliable.

**When to use API setup:** Creating test users, products, orders, seed data. Setting feature flags. Resetting state between tests.

**When to use UI setup:** Only when the creation flow IS the test being verified.

```typescript
test('TC-CART-001: User sees items in cart', async ({ page, request }) => {
  // Arrange: seed data via API (fast, deterministic)
  await request.post('/api/cart/items', {
    data: { productId: 'SKU-123', quantity: 2 }
  });

  // Act: navigate to verify UI
  await page.goto('/cart');

  // Assert
  await expect(page.getByRole('listitem')).toHaveCount(2);
});
```

**Reusable API fixture pattern:**
```typescript
export const test = base.extend<{ apiClient: APIRequestContext }>({
  apiClient: async ({ playwright }, use) => {
    const ctx = await playwright.request.newContext({
      baseURL: process.env.API_BASE_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${process.env.API_TOKEN}` },
    });
    await use(ctx);
    await ctx.dispose();
  },
});
```

### Test Data Teardown

Tests that create persistent data (database records, uploaded files, user accounts) MUST clean up after themselves. Leaked test data accumulates across runs and causes false positives/negatives in other tests (pagination counts drift, filter results change, list assertions break).

**Strategy 1: API teardown in afterEach (Recommended)**
```typescript
let createdTicketId: string;

test.beforeEach(async ({ request }) => {
  const resp = await request.post('/api/tickets', {
    data: { title: `Test ${Date.now()}` }
  });
  createdTicketId = (await resp.json()).id;
});

test.afterEach(async ({ request }) => {
  if (createdTicketId) {
    await request.delete(`/api/tickets/${createdTicketId}`);
  }
});
```

**Strategy 2: Fixture with automatic cleanup**
```typescript
export const test = base.extend<{ testTicket: { id: string; title: string } }>({
  testTicket: async ({ request }, use) => {
    const resp = await request.post('/api/tickets', {
      data: { title: `Test ${Date.now()}` }
    });
    const ticket = await resp.json();
    await use(ticket);
    // cleanup runs automatically when test finishes
    await request.delete(`/api/tickets/${ticket.id}`);
  },
});
```

**Strategy 3: Bulk cleanup in globalTeardown** — for environments where individual deletion is impractical, tag test data (e.g., `title LIKE 'Test %'`) and delete in batch during `globalTeardown.ts`.

If the cleanup API endpoint is unknown, still write the teardown code with the most likely endpoint and add a `// TODO: verify cleanup endpoint` comment. Never skip teardown entirely — a wrong endpoint that 404s is preferable to test data that accumulates silently. If cleanup is genuinely impossible (no API, no database access), document this as a known limitation in the test file header AND add an `afterEach` that logs a warning.

### Network Interception

Use `page.route()` to intercept and mock network requests for deterministic error testing.

**Mock server errors:**
```typescript
await page.route('**/api/checkout', route =>
  route.fulfill({ status: 500, body: JSON.stringify({ error: 'Payment declined' }) })
);
```

**Patch real responses (modify, don't replace):**
```typescript
await page.route('**/api/products', async route => {
  const response = await route.fetch();
  const json = await response.json();
  json.results = json.results.slice(0, 1); // reduce to 1 item
  await route.fulfill({ response, json });
});
```

**Assert backend was called:**
```typescript
const [response] = await Promise.all([
  page.waitForResponse(resp =>
    resp.url().includes('/api/order') && resp.status() === 201
  ),
  page.getByRole('button', { name: /place order/i }).click(),
]);
expect(response.status()).toBe(201);
```

**Block heavy resources to speed up tests:**
```typescript
await page.route('**/*.{png,jpg,jpeg,gif,svg}', route => route.abort());
```

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

### Error Path Testing

Every feature needs error path tests. Use network interception (see above) to simulate failures. At minimum, every feature test suite should cover:

- **Server error** — `route.fulfill({ status: 500, ... })` — verify error UI appears
- **Network timeout** — `route.abort('timedout')` — verify retry option or error message
- **Empty state** — `route.fulfill({ status: 200, json: { items: [] } })` — verify empty state UI

```typescript
test('TC-DASHBOARD-005: Shows empty state when no data', async ({ page }) => {
  await page.route('**/api/items', route =>
    route.fulfill({ status: 200, json: { items: [] } })
  );
  await page.goto('/dashboard');
  await expect(page.getByText(/no items/i)).toBeVisible();
});
```

## Mapping Tables

### Scope-to-Locator
| Journey Scope | Playwright Scoping |
|---------------|-------------------|
| `page` | No scoping needed |
| `header` | `page.locator('header')` |
| `main` | `page.locator('main')` |
| `nav` | `page.locator('nav')` |
| `dialog` | `page.locator('[role="dialog"]')` |

### Action-to-Playwright
| Journey Action | Playwright Code |
|----------------|-----------------|
| `goto` | `await page.goto(url)` |
| `click` | `await locator.click()` |
| `fill` | `await locator.fill(value)` |
| `select` | `await locator.selectOption(value)` |
| `assert` | `await expect(locator).toBeVisible()` |

### Assertion Mapping
| Observed Effect | Playwright Assertion |
|----------------|---------------------|
| `url changed to /cart` | `await expect(page).toHaveURL(/cart/)` |
| `text 'Added' visible` | `await expect(page.getByText(/added/i)).toBeVisible()` |
| `radio 256GB checked` | `await expect(locator).toBeChecked()` |
| `button now enabled` | `await expect(locator).toBeEnabled()` |

### Target Kind to Locator
| Target Kind | Value Pattern | Playwright Locator |
|-------------|--------------|-------------------|
| `role` | `button name~Add to Bag` | `getByRole('button', { name: /add to bag/i })` |
| `role` | `radio name~256GB` | `getByRole('radio', { name: /256gb/i })` |
| `label` | `Email address` | `getByLabel(/email address/i)` |
| `testid` | `checkout-button` | `getByTestId('checkout-button')` |

## Low Confidence Handling (<0.7)

When journey step confidence is low:
1. Add extra assertions to verify state
2. Include fallback locators as comments
3. Consider retry logic for flaky interactions

```typescript
// Primary locator
const storageRadio = page.getByRole('radio', { name: /256gb/i });
// Fallback: page.getByLabel(/256gb/i)
await storageRadio.click();
await expect(storageRadio).toBeChecked({ timeout: 5000 });
```

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

## Anti-Patterns to Avoid

1. **Raw CSS selectors** — use semantic locators
2. **`waitForTimeout()`** — use proper assertions
3. **Fragile `nth()`** — add comment if unavoidable
4. **Exact long text** — use regex with key words
5. **Unscoped locators** — scope to main/nav/dialog when possible
6. **Login via UI in every test** — use storageState or API-based auth setup
7. **UI clicks to set up test data** — use API requests for data seeding
8. **No error path tests** — every feature needs at least one failure scenario test
9. **Hardcoded test data** — NEVER embed real entity IDs (`'ACC-SUB-2026-00025'`), real user names (`'Anas Client 73'`), real monetary amounts, or environment-specific strings in test code. Instead: (a) create data via API in `beforeEach` and capture the returned ID, (b) use `Date.now()` or `crypto.randomUUID()` suffixes for uniqueness, (c) read values from `process.env` or a test data module, (d) for read-only assertions on existing data, use pattern matchers (`expect(text).toMatch(/ACC-SUB-\d{4}-\d{5}/)`) instead of exact values. If you find yourself typing a specific ID or name into test code, STOP — that is a hardcoded value.
10. **Tests depending on execution order** — each test must be independently runnable
11. **`expect(await el.isVisible()).toBe(true)`** — use `await expect(el).toBeVisible()` (auto-retries)
12. **`{ force: true }` on clicks/checks** — hides real interaction problems (overlapping elements, not scrolled into view, disabled state). Diagnose the root cause instead: use `scrollIntoViewIfNeeded()`, wait for overlay to disappear, or wait for element to be enabled. Only acceptable when interacting with a custom widget that Playwright cannot natively trigger (document why in a comment).
13. **`waitForLoadState('networkidle')` as default strategy** — `networkidle` waits for 500ms of no network activity, which breaks on long-polling, WebSockets, analytics beacons, or chat widgets. Use it ONLY for initial full-page loads where no streaming/polling exists. For post-action waits, use `waitForResponse` targeting the specific API call, or assert directly on the resulting UI state (Playwright auto-retries).
14. **CSS utility class selectors (Tailwind, Bootstrap, etc.)** — `button.rounded-l-lg`, `.flex.items-center`, `.bg-primary` are styling concerns that change during refactors. Treat ALL utility framework classes as volatile — never use them as selectors. If no semantic locator works, request a `data-testid` from the dev team.
15. **Asserting exact server-computed values** — `expect(revenue).toHaveText('12450')` will break when data changes. For dashboard counters, totals, and aggregates: (a) assert the element exists and contains a number (`toMatch(/\$[\d,]+/)`), (b) assert non-zero or within a range, (c) assert format correctness (`/^\d{1,3}(,\d{3})*$/`), (d) if exact value matters, seed the data via API first so you control the expected value.

## Context-Saving Strategy

For large test suites, use Task tool with `general-purpose` subagent to write individual test files. Pass the subagent:
- The test case spec (from `test-cases/<feature>.md`)
- Codebase conventions discovered in step 2
- These operating principles and mapping tables
