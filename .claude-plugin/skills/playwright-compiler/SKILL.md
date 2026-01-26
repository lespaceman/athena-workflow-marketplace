---
name: playwright-compiler
description: Detailed patterns for the playwright-test-compiler agent. Reference for locator strategies, scope mapping, action mapping, and test templates.
user-invocable: false
allowed_tools:
  - mcp__athena-browser-mcp__launch_browser
  - mcp__athena-browser-mcp__connect_browser
  - mcp__athena-browser-mcp__close_session
  - mcp__athena-browser-mcp__navigate
  - mcp__athena-browser-mcp__go_back
  - mcp__athena-browser-mcp__click
  - mcp__athena-browser-mcp__type
  - mcp__athena-browser-mcp__select
  - mcp__athena-browser-mcp__press
  - mcp__athena-browser-mcp__hover
  - mcp__athena-browser-mcp__capture_snapshot
  - mcp__athena-browser-mcp__scroll_page
  - mcp__athena-browser-mcp__scroll_element_into_view
  - mcp__athena-browser-mcp__find_elements
  - mcp__athena-browser-mcp__get_node_details
  - mcp__athena-browser-mcp__get_form_understanding
  - mcp__athena-browser-mcp__get_field_context
---

# Playwright Test Compiler Skill Reference

## Locator Priority Strategy

Use locators in this order of preference:

| Priority | Method | When to Use |
|----------|--------|-------------|
| 1 | `getByRole('role', { name })` | Buttons, links, headings, form controls |
| 2 | `getByLabel()` | Form fields with visible labels |
| 3 | `getByPlaceholder()` | Inputs with placeholder text |
| 4 | `getByTestId()` | When data-testid is available in journey JSON |
| 5 | `getByText()` | Short, stable text (avoid marketing copy) |
| 6 | CSS selectors | Last resort, always scoped tightly |

---

## Scope-to-Locator Mapping

| Journey Scope | Playwright Scoping |
|---------------|-------------------|
| `page` | No scoping needed |
| `header` | `page.locator('header')` |
| `main` | `page.locator('main')` |
| `nav` | `page.locator('nav')` |
| `dialog` | `page.locator('[role="dialog"]')` |
| `footer` | `page.locator('footer')` |

Example with scoping:
```typescript
await page.locator('main').getByRole('button', { name: /add to bag/i }).click();
```

---

## Action-to-Playwright Mapping

| Journey Action | Playwright Code |
|----------------|-----------------|
| `goto` | `await page.goto(url)` |
| `click` | `await locator.click()` |
| `fill` | `await locator.fill(value)` |
| `select` | `await locator.selectOption(value)` |
| `assert` | `await expect(locator).toBeVisible()` |

---

## Target Kind to Locator Mapping

| Target Kind | Value Pattern | Playwright Locator |
|-------------|--------------|-------------------|
| `role` | `link name~iPhone` | `getByRole('link', { name: /iphone/i })` |
| `role` | `button name~Add to Bag` | `getByRole('button', { name: /add to bag/i })` |
| `role` | `radio name~256GB` | `getByRole('radio', { name: /256gb/i })` |
| `role` | `textbox name~Email` | `getByRole('textbox', { name: /email/i })` |
| `label` | `Email address` | `getByLabel(/email address/i)` |
| `text` | `Continue` | `getByText(/continue/i)` |
| `testid` | `checkout-button` | `getByTestId('checkout-button')` |

---

## Assertion Mapping (from observed effects)

| Observed Effect | Playwright Assertion |
|----------------|---------------------|
| `url changed to /cart` | `await expect(page).toHaveURL(/cart/)` |
| `text 'Added' visible` | `await expect(page.getByText(/added/i)).toBeVisible()` |
| `radio 256GB now checked` | `await expect(locator).toBeChecked()` |
| `button now enabled` | `await expect(locator).toBeEnabled()` |
| `cart badge shows '1'` | `await expect(page.getByText('1')).toBeVisible()` |

---

## Low Confidence Handling (<0.7)

When journey step confidence is low:

1. **Add extra assertions** to verify state
2. **Include fallback locators** as comments
3. **Consider retry logic** for flaky interactions

```typescript
// s3: Select storage option (confidence: 0.65)
// Primary locator
const storageRadio = page.getByRole('radio', { name: /256gb/i });
// Fallback: page.getByLabel(/256gb/i)
await storageRadio.click();
await expect(storageRadio).toBeChecked({ timeout: 5000 });
```

---

## Test Template

```typescript
import { test, expect } from '@playwright/test';

test.use({
  viewport: { width: 1280, height: 800 },
  locale: 'en-US',
  timezoneId: 'America/Los_Angeles',
});

test('add iPhone 16 Pro to cart', async ({ page }) => {
  // s1: Navigate to Apple Store
  await page.goto('https://www.apple.com/store');

  // s2: Click iPhone link in navigation
  await page.locator('nav').getByRole('link', { name: /iphone/i }).click();
  await expect(page).toHaveURL(/\/iphone/);

  // s3: Select iPhone 16 Pro
  await page.locator('main').getByRole('link', { name: /iphone 16 pro/i }).click();
  await expect(page).toHaveURL(/\/iphone-16-pro/);

  // s4: Click Buy button
  await page.getByRole('link', { name: /buy/i }).first().click();

  // s5: Select 256GB storage
  await page.getByRole('radio', { name: /256gb/i }).click();
  await expect(page.getByRole('radio', { name: /256gb/i })).toBeChecked();

  // s6: Add to Bag
  await page.getByRole('button', { name: /add to bag/i }).click();

  // Final assertions
  await expect(page.getByText(/added to bag/i)).toBeVisible();
});
```

---

## Selector Map Format

For complex journeys, document primary and fallback locators:

```
- s2: primary `nav >> getByRole('link', { name: /iphone/i })`, fallback `getByText(/^iPhone$/i)`
- s5: primary `getByRole('radio', { name: /256gb/i })`, fallback `getByLabel(/256gb/i)`
```

---

## Fixtures Policy

| Use Fixtures When | Avoid Fixtures When |
|-------------------|---------------------|
| Setup repeats across tests | Single test only |
| Auth state needed | No shared state |
| Specific locale/timezone | Inline `test.use()` suffices |

Keep fixtures minimal:
```typescript
// fixtures.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('#email', 'test@example.com');
    await page.fill('#password', 'password');
    await page.click('button[type="submit"]');
    await use(page);
  },
});
```

---

## Defaults Reference

| Setting | Default Value |
|---------|---------------|
| Language | TypeScript |
| Viewport | 1280x800 |
| Locale | en-US |
| Timezone | UTC |
| Test file | `tests/e2e/{goal-slug}.spec.ts` |

---

## Anti-Patterns to Avoid

1. **Raw CSS selectors** - Use semantic locators
2. **`waitForTimeout()`** - Use proper assertions instead
3. **Fragile `nth()`** - Add comment if unavoidable
4. **Exact long text** - Use regex with key words
5. **Unscoped locators** - Always scope to main/nav/dialog when possible
