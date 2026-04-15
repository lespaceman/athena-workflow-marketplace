# Anti-Patterns: Detailed Explanations and Fix Strategies

## 1. Raw CSS selectors
Use semantic locators (`getByRole`, `getByLabel`, `getByTestId`) instead of CSS selectors. CSS selectors are brittle and break when markup changes.

**Why:** A class rename, component refactor, or CSS-in-JS migration breaks every CSS-based selector overnight. Semantic locators survive these changes because they target accessible roles and labels, not implementation details.

**Fix:** Replace `page.locator('.submit-btn')` with `page.getByRole('button', { name: /submit/i })`. Follow the locator strategy hierarchy in the main skill.

## 2. `waitForTimeout()`
Use proper assertions and event-driven waits. `waitForTimeout()` adds arbitrary delays that slow tests and mask timing issues.

**Why:** A 2-second sleep that works locally may be too short in CI (slower machines) or too long everywhere (wasting time). It also hides the real question: "what am I actually waiting for?"

**Fix:** Replace with `waitForResponse` for API-dependent UI, `expect(el).toBeVisible()` for element appearance, or `expect(spinner).toBeHidden()` for loading states.

## 3. Fragile `.nth()` / `.first()`
Scope locators to a container instead of relying on position. If unavoidable, add a comment explaining why.

**Why:** Element order can change when the page adds a banner, reorders a list, or renders asynchronously. `.first()` silently picks the wrong element, causing false passes or mysterious failures.

**Fix:** Use `.filter({ hasText: 'Specific Item' })` or scope to a container: `page.locator('[data-testid="cart"]').getByRole('button')`.

## 4. Exact long text matches
Use regex with key words instead of matching entire strings. Marketing copy and UI text change frequently.

**Why:** A copywriter changes "Sign up for free today!" to "Create your free account" and every test matching the full string breaks, even though the feature works fine.

**Fix:** Use `page.getByText(/sign up/i)` or `page.getByRole('button', { name: /free/i })` — match the stable semantic keywords.

## 5. Unscoped locators
Scope locators to `main`, `nav`, `dialog`, or other containers when possible. Global locators match unintended elements.

**Why:** A page-wide `getByRole('button', { name: /submit/i })` may match a submit button in the header, footer, or a hidden modal — not just the one in your form. This causes the wrong click or ambiguous locator errors.

**Fix:** Scope first: `page.locator('main').getByRole('button', { name: /submit/i })` or `page.locator('[role="dialog"]').getByRole('button')`.

## 6. Login via UI in every test
Use `storageState` or API-based auth setup. UI login in every test wastes time and creates coupling to the login flow.

**Why:** If every test clicks through the login form, a single login page change breaks the entire suite. It also adds 3-10 seconds per test — multiplied across hundreds of tests, this becomes significant CI time.

**Fix:** Log in once in `globalSetup`, save `storageState` to a JSON file, and reuse it. See `references/auth-patterns.md` for the four auth strategies.

## 7. UI clicks to set up test data
Use API requests for data seeding. UI setup is 10-50x slower and more fragile than API calls.

**Why:** Creating a product via the admin UI takes 15+ seconds and 10+ actions. An API call takes 200ms and one line. UI setup also couples your test to two features instead of one — if the admin form breaks, your unrelated cart test fails too.

**Fix:** Use the `request` fixture: `await request.post('/api/products', { data: { ... } })`. See `references/api-setup-teardown.md`.

## 8. No error path tests
Every feature needs at least one failure scenario test. Cover server errors (500), network timeouts, and empty states.

**Why:** Happy-path-only suites give false confidence. The app may crash on a 500, show a blank screen on empty data, or hang on a timeout — none of which are caught without explicit error path tests.

**Fix:** Use `page.route()` to mock failures. At minimum: one 500 response, one timeout (`route.abort('timedout')`), one empty state (`route.fulfill({ json: { items: [] } })`). See `references/network-interception.md`.

## 9. Hardcoded test data
NEVER embed real entity IDs (`'ACC-SUB-2026-00025'`), real user names (`'Anas Client 73'`), real monetary amounts, or environment-specific strings in test code. Instead:
- Create data via API in `beforeEach` and capture the returned ID
- Use `Date.now()` or `crypto.randomUUID()` suffixes for uniqueness
- Read values from `process.env` or a test data module
- For read-only assertions on existing data, use pattern matchers (`expect(text).toMatch(/ACC-SUB-\d{4}-\d{5}/)`) instead of exact values

If you find yourself typing a specific ID or name into test code, STOP — that is a hardcoded value.

## 10. Tests depending on execution order
Each test must be independently runnable. Never rely on state left by a previous test.

## 11. `expect(await el.isVisible()).toBe(true)`
Use `await expect(el).toBeVisible()` instead. The Playwright assertion auto-retries, while the manual pattern checks once and fails on timing.

## 12. `{ force: true }` on clicks/checks
Hides real interaction problems (overlapping elements, not scrolled into view, disabled state). Diagnose the root cause instead: use `scrollIntoViewIfNeeded()`, wait for overlay to disappear, or wait for element to be enabled. Only acceptable when interacting with a custom widget that Playwright cannot natively trigger (document why in a comment).

## 13. `waitForLoadState('networkidle')` as default strategy
`networkidle` waits for 500ms of no network activity, which breaks on long-polling, WebSockets, analytics beacons, or chat widgets. Use it ONLY for initial full-page loads where no streaming/polling exists. For post-action waits, use `waitForResponse` targeting the specific API call, or assert directly on the resulting UI state (Playwright auto-retries).

## 14. CSS utility class selectors (Tailwind, Bootstrap, etc.)
`button.rounded-l-lg`, `.flex.items-center`, `.bg-primary` are styling concerns that change during refactors. Treat ALL utility framework classes as volatile — never use them as selectors. If no semantic locator works, request a `data-testid` from the dev team.

## 15. Asserting exact server-computed values
`expect(revenue).toHaveText('12450')` will break when data changes. For dashboard counters, totals, and aggregates:
- Assert the element exists and contains a number (`toMatch(/\$[\d,]+/)`)
- Assert non-zero or within a range
- Assert format correctness (`/^\d{1,3}(,\d{3})*$/`)
- If exact value matters, seed the data via API first so you control the expected value
