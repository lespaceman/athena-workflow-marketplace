# Fix Patterns by Root Cause

Code examples for each root cause category. Apply only after diagnosing the cause in Step 2.

## Timing Fixes — Replace Sleeps with Event-Driven Waits

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

// GOOD: wait for a specific readiness signal after navigation
await page.goto('/page');
await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

// GOOD: use auto-retrying assertion (retries until timeout)
await expect(page.getByText(/loaded/i)).toBeVisible({ timeout: 10000 });
```

## State Isolation Fixes

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

## Race Condition Fixes

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

## Selector Fixes

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

## Environment Fixes

```typescript
// Set explicit viewport in test or config
test.use({ viewport: { width: 1280, height: 720 } });

// Use timezone-agnostic assertions
await expect(dateElement).toContainText(/\d{4}/); // year, not full date string

// Block third-party scripts that interfere
await page.route('**/analytics/**', route => route.abort());
await page.route('**/chat-widget/**', route => route.abort());
```
