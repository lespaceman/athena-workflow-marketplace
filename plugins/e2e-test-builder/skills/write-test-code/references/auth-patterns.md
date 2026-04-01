# Authentication Setup Patterns

Choose the right auth strategy based on the project's needs.

## Strategy 1: storageState (Recommended for most projects)

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

## Strategy 2: Worker-scoped fixture (for parallel workers needing separate accounts)

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

## Strategy 3: Multi-role testing (admin + user in same test)

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

## Strategy 4: Per-test login

Only when testing login itself or permission-specific scenarios.

Never hardcode tokens. Use environment variables or `.env.test`.
