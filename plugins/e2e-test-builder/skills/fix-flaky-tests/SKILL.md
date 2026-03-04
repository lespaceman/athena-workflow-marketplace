---
name: fix-flaky-tests
description: >
  Use to fix any existing Playwright test that is failing, flaky, timing out, or behaving
  inconsistently. Invoke whenever a user needs to: stabilize a test that passes sometimes and
  fails other times, debug a timeout (e.g. "Test timeout of 30000ms exceeded"), fix a race
  condition in test code, investigate why a test works locally but fails in CI or headless mode,
  or run tests repeatedly (--repeat-each) to check for non-deterministic behavior before merging.
  IMPORTANT: If you find yourself running tests with --repeat-each, --retries, or running the same
  test suite multiple times to check stability, STOP and load this skill first — you are doing
  flakiness investigation and this skill has structured root cause analysis that prevents brute-force
  "run it 3x and hope" approaches.
  If the user says "stabilize", "intermittent", "flaky", "keeps failing", "fails in CI", "timeout on",
  "race condition", "run N times to check stability", or "verify tests are stable" — this is the right
  skill. NOT for writing new tests from scratch (use write-e2e-tests) or analyzing test setup
  (use analyze-test-codebase).
user-invocable: true
argument-hint: <path to flaky test file or test name>
allowed-tools:
  # MCP browser tools (for verifying selectors and reproducing flakiness against live site)
  - mcp__plugin_e2e-test-builder_agent-web-interface__ping
  - mcp__plugin_e2e-test-builder_agent-web-interface__navigate
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_back
  - mcp__plugin_e2e-test-builder_agent-web-interface__go_forward
  - mcp__plugin_e2e-test-builder_agent-web-interface__reload
  - mcp__plugin_e2e-test-builder_agent-web-interface__snapshot
  - mcp__plugin_e2e-test-builder_agent-web-interface__find
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_element
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_to
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll
  - mcp__plugin_e2e-test-builder_agent-web-interface__click
  - mcp__plugin_e2e-test-builder_agent-web-interface__type
  - mcp__plugin_e2e-test-builder_agent-web-interface__press
  - mcp__plugin_e2e-test-builder_agent-web-interface__select
  - mcp__plugin_e2e-test-builder_agent-web-interface__hover
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_form
  - mcp__plugin_e2e-test-builder_agent-web-interface__get_field
  - mcp__plugin_e2e-test-builder_agent-web-interface__list_pages
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_session
  - mcp__plugin_e2e-test-builder_agent-web-interface__screenshot
  # File tools
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
---

# Fix Flaky Tests

Systematically diagnose and fix intermittent Playwright test failures using root cause analysis. A flaky test is worse than no test — it trains teams to ignore failures.

## Input

Parse the test file path or test name from: $ARGUMENTS

If no argument provided, ask: "Which test file or test name is flaky?"

## Workflow

### Step 1: Reproduce and Classify

1. **Read the test file** to understand what it tests and how
2. **Run the test multiple times** to observe the failure pattern:
   ```bash
   npx playwright test <file> --repeat-each=5 --reporter=list 2>&1
   ```
3. **Run in isolation** if it passed above — it may only fail with other tests:
   ```bash
   npx playwright test --reporter=list 2>&1
   ```
4. **Classify the failure** into one of these root cause categories:

| Category | Symptoms |
|----------|----------|
| **Timing** | Timeout errors, "element not found", "not visible yet" |
| **State leakage** | Passes alone, fails when run with other tests |
| **Data dependency** | Fails when expected data doesn't exist or has changed |
| **Race condition** | Action fires before page is ready (hydration, animation) |
| **Selector fragility** | Element found but wrong one, or `.first()` picks different element |
| **Environment** | Passes locally, fails in CI (viewport, speed, resources) |

### Step 2: Root Cause Analysis

Investigate based on the classification:

**Timing issues:**
- Look for assertions immediately after actions with no wait for the resulting state change
- Check if the test asserts before an API response arrives — search for missing `waitForResponse`
- Look for animations/transitions that affect element state (CSS transitions, skeleton screens)
- Check for `waitForTimeout` being used as a "fix" — this is a symptom, not a cure
- Check if `networkidle` or `load` waitUntil would help for navigation

**State leakage:**
- Run the failing test alone: `npx playwright test --grep "<test name>"`
- Check if tests share mutable state: global variables, database rows, cookies, localStorage
- Look for missing cleanup in `afterEach`/`afterAll`
- Check if `storageState` bleeds between tests or test files
- Check for test data created by one test that another test depends on

**Race conditions:**
- Identify the race: what two things are happening concurrently?
- Check for click handlers that fire before JavaScript hydration completes
- Look for optimistic UI updates that revert on API response
- Check for actions during navigation transitions (click during page load)
- Look for double-clicks or rapid interactions that trigger duplicate actions

**Selector fragility:**
- Navigate to the page in the browser and verify the selector currently matches the intended element
- Check if the selector matches multiple elements — `.first()` or `.nth()` is a smell
- Look for dynamically generated IDs, classes, or attributes
- Check for conditional rendering that changes element order or presence
- Verify locators against current DOM structure using `find` and `get_element`

**Environment issues:**
- Compare CI viewport size vs local — element may be off-screen in CI
- Check for timezone-dependent assertions (dates, timestamps)
- Check for locale-dependent formatting (numbers, currency)
- Check if CI has slower network/CPU affecting timing
- Look for third-party scripts (analytics, chat widgets) that load differently in CI

### Step 3: Apply the Correct Fix

Use the right fix pattern for the diagnosed root cause. **Never apply a fix without understanding the cause.**

**Timing fixes — replace sleeps with event-driven waits:**
```typescript
// BAD: arbitrary sleep
await page.waitForTimeout(2000);
await expect(element).toBeVisible();

// GOOD: wait for the network event that loads the content
await page.waitForResponse(resp => resp.url().includes('/api/data'));
await expect(element).toBeVisible();

// GOOD: wait for loading indicator to disappear
await expect(page.getByRole('progressbar')).toBeHidden();
await expect(element).toBeVisible();

// GOOD: wait for navigation to complete
await page.goto('/page', { waitUntil: 'networkidle' });

// GOOD: use auto-retrying assertion (retries until timeout)
await expect(page.getByText(/loaded/i)).toBeVisible({ timeout: 10000 });
```

**State isolation fixes:**
```typescript
// Unique data per test
const uniqueEmail = `test-${Date.now()}@example.com`;

// Reset state via API before each test
test.beforeEach(async ({ request }) => {
  await request.post('/api/test/reset');
});

// Use fresh browser context (default in Playwright, but verify)
// Do NOT share page or context between tests
```

**Race condition fixes:**
```typescript
// Wait for hydration/framework readiness
await page.waitForFunction(() =>
  document.querySelector('[data-hydrated="true"]')
);

// Use Promise.all for action + expected response
const [response] = await Promise.all([
  page.waitForResponse('**/api/submit'),
  submitButton.click(),
]);

// Wait for animation/transition to complete
await expect(modal).toBeVisible();
await page.waitForFunction(() =>
  !document.querySelector('.modal-animating')
);
```

**Selector fixes:**
```typescript
// BAD: position-dependent, matches wrong element if order changes
page.locator('.item').first();

// GOOD: scoped to container with unique content
page.getByRole('listitem').filter({ hasText: 'Specific Item' });

// GOOD: use test IDs for ambiguous elements
page.getByTestId('cart-item-sku-123');

// GOOD: scope to a region first, then find within
page.locator('main').getByRole('button', { name: /submit/i });
```

**Environment fixes:**
```typescript
// Set explicit viewport in test or config
test.use({ viewport: { width: 1280, height: 720 } });

// Use timezone-agnostic assertions
await expect(dateElement).toContainText(/\d{4}/); // year, not full date string

// Block third-party scripts that interfere
await page.route('**/analytics/**', route => route.abort());
await page.route('**/chat-widget/**', route => route.abort());
```

### Step 4: Verify the Fix

1. **Run the test 5+ times** to confirm stability:
   ```bash
   npx playwright test <file> --repeat-each=5 --reporter=list 2>&1
   ```
2. **Run with the full test suite** to verify no state leakage:
   ```bash
   npx playwright test --reporter=list 2>&1
   ```
3. If still flaky → return to Step 2 with the new failure output. The initial classification may have been wrong.

### Step 5: Summarize

Report:
1. **Root cause** — what made the test flaky and why
2. **Fix applied** — what changed and why this fix addresses the root cause
3. **Verification** — how many consecutive runs passed
4. **Prevention** — what pattern to follow in future tests to avoid this class of flakiness

## Flakiness Checklist (Less Obvious Causes)

When the standard categories don't fit, check these:

- [ ] **Viewport size** — element off-screen in CI (smaller viewport)
- [ ] **Font rendering** — text matching fails due to font differences across OS
- [ ] **Timezone** — date/time assertions fail in different timezones
- [ ] **Locale** — number/currency formatting differs (1,000 vs 1.000)
- [ ] **Third-party scripts** — analytics/chat widgets change DOM or block clicks
- [ ] **Cookie consent banners** — overlay blocks click targets
- [ ] **Feature flags** — different features enabled in different environments
- [ ] **Database state** — shared test database with stale or conflicting data
- [ ] **Parallel execution** — tests interfere when run in parallel workers
- [ ] **Browser caching** — cached responses differ from fresh ones
- [ ] **Service workers** — intercepting requests differently than expected
- [ ] **Lazy loading** — elements not yet in DOM when test tries to interact

## Anti-Patterns: What is NOT a Fix

These mask the problem. Never apply them without a real fix:

## Multiple Flaky Tests

For suites with multiple flaky tests, use the Task tool to delegate individual test fixes to general-purpose subagents. Pass each subagent the test file path, this diagnostic workflow, and the root cause classification table.

## Anti-Patterns: What is NOT a Fix

| "Fix" | Why It's Wrong | Real Fix |
|-------|---------------|----------|
| `waitForTimeout(3000)` | Hides timing race, will break under load | Wait for the specific event |
| `.first()` added | Hides selector ambiguity | Narrow the selector |
| Increased timeout to 30s | Hides missing wait or slow setup | Find what you're actually waiting for |
| `test.skip()` | Ignoring the problem | Diagnose and fix |
| `retries: 3` without fix | Masks real failures, wastes CI time | Fix the root cause, then keep retries as safety net |
| `try/catch` swallowing errors | Test passes but doesn't verify anything | Fix the assertion |
