# Network Interception and Error Path Testing

## Network Interception

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

## Error Path Testing

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
