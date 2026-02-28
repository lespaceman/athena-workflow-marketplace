---
name: write-e2e-tests
description: >
  Use when the user wants executable Playwright test code written, refactored, or fixed.
  Triggers: "write Playwright tests", "write e2e tests", "create test code", "implement these test cases",
  "convert test specs to code", "turn selectors into tests", "add a test for this flow",
  "write tests for this feature", "convert TC-IDs to Playwright", "refactor this test",
  "improve test locators", "set up auth for Playwright tests", "mock API in test",
  "create test fixture", "add network interception", "write error path tests".
  For flaky/intermittent test failures, use fix-flaky-tests instead.
  This skill writes executable Playwright TypeScript tests following project conventions — semantic locators
  (getByRole > getByLabel > getByTestId), no arbitrary sleeps, AAA structure, TC-ID traceability.
  It does NOT generate test case specifications — use generate-test-cases for that.
  It does NOT do general browser exploration — use explore-website for that.
user-invocable: true
argument-hint: <test description or path to test case spec file>
allowed-tools:
  # MCP browser tools
  - mcp__plugin_e2e-test-builder_agent-web-interface__ping
  - mcp__plugin_e2e-test-builder_agent-web-interface__navigate
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_back
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_forward
  - mcp__plugin_e2e-test-builder_agent-web-interface__reload
  - mcp__plugin_e2e-test-builder_agent-web-interface__capture_snapshot
  - mcp__plugin_e2e-test-builder_agent-web-interface__find_elements
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_element_details
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_element_into_view
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__click
  - mcp__plugin_e2e-test-builder_agent-web-interface__type
  - mcp__plugin_e2e-test-builder_agent-web-interface__press
  - mcp__plugin_e2e-test-builder_agent-web-interface__select
  - mcp__plugin_e2e-test-builder_agent-web-interface__hover
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_form_understanding
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_field_context
  - mcp__plugin_e2e-test-builder_agent-web-interface__list_pages
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_session
  - mcp__plugin_e2e-test-builder_agent-web-interface__take_screenshot
  # File tools
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
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

### 3. Implement Tests
- Add/adjust fixtures and page objects first (if needed)
- Write tests in a story-like flow with AAA structure: Arrange → Act → Assert
- Add assertions that represent user outcomes

### 4. Stabilize
- Replace any sleeps with meaningful waits
- Tighten locators to avoid ambiguity
- For network-driven flows, use `page.waitForResponse` for critical checkpoints

### 5. Verify
- Run the smallest relevant test command: `npx playwright test <file> --headed` or single test
- Fix root causes rather than extending timeouts

### 6. Summarize
Return:
1. **What I changed** (bullets)
2. **Test case IDs added** (list all new TC-IDs with brief description)
3. **Why it's stable** (locator/wait strategy used)
4. **How to run** (exact commands)
5. **Notes / follow-ups** (optional)

## Operating Principles (Non-Negotiable)

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

### Waiting Strategy
- Prefer Playwright auto-waits via actions and `expect(...)` assertions
- If explicit waiting needed, wait for meaningful state: visibility, enabled, URL, specific network response, spinner gone

### Test Case IDs
- Every test MUST have a unique TC-ID: `TC-<FEATURE>-<NUMBER>`
- Include in test title: `test('TC-LOGIN-001: User can log in with valid credentials', ...)`
- Sequential within feature area, never reused
- When adding to existing file, check existing IDs and continue the sequence

### POM + Fixtures (if project uses it)
- Page Objects contain HOW (locators + interactions)
- Tests contain WHAT (behavior/outcome to verify)
- Keep page objects thin and composable

### Determinism and Isolation
- Tests must not depend on execution order
- Use unique test data per test or suite

### Assertions
- Use Playwright `expect` matchers (auto-retry, better error messages)
- Avoid `isVisible()` + `expect(true)` pattern

### Configuration Hygiene
- Use `baseURL` and relative navigation (`page.goto('/')`)
- Avoid hardcoded domains/URLs in tests
- Configure `trace: 'on-first-retry'`, `screenshot: 'only-on-failure'`, `video: 'on-first-retry'` for CI debugging
- Set `retries: process.env.CI ? 2 : 0` — retries in CI only
- View traces with `npx playwright show-trace trace.zip` to time-travel through failures

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

## Anti-Patterns to Avoid

1. **Raw CSS selectors** — use semantic locators
2. **`waitForTimeout()`** — use proper assertions
3. **Fragile `nth()`** — add comment if unavoidable
4. **Exact long text** — use regex with key words
5. **Unscoped locators** — scope to main/nav/dialog when possible
6. **Login via UI in every test** — use storageState or API-based auth setup
7. **UI clicks to set up test data** — use API requests for data seeding
8. **No error path tests** — every feature needs at least one failure scenario test
9. **Hardcoded test data** — use factories, unique IDs (`Date.now()`), or env vars
10. **Tests depending on execution order** — each test must be independently runnable
11. **`expect(await el.isVisible()).toBe(true)`** — use `await expect(el).toBeVisible()` (auto-retries)

## Context-Saving Strategy

For large test suites, use Task tool with `general-purpose` subagent to write individual test files. Pass the subagent:
- The test case spec (from `test-cases/<feature>.md`)
- Codebase conventions discovered in step 2
- These operating principles and mapping tables
