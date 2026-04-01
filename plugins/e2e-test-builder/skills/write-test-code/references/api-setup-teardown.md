# API-Driven Test Setup and Teardown

## API-Driven Test Setup

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

## Test Data Teardown

Tests that create persistent data (database records, uploaded files, user accounts) MUST clean up after themselves. Leaked test data accumulates across runs and causes false positives/negatives in other tests (pagination counts drift, filter results change, list assertions break).

### Strategy 1: API teardown in afterEach (Recommended)

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

### Strategy 2: Fixture with automatic cleanup

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

### Strategy 3: Bulk cleanup in globalTeardown

For environments where individual deletion is impractical, tag test data (e.g., `title LIKE 'Test %'`) and delete in batch during `globalTeardown.ts`.

If the cleanup API endpoint is unknown, do not invent one. Leave a clear `TODO` with the missing endpoint details, document the cleanup gap in the test file or tracker, and prefer fixture-scoped or environment reset strategies that you can verify. If cleanup is genuinely impossible (no API, no database access), document this as a known limitation in the test file header AND add an `afterEach` that logs a warning.
