---
name: write-e2e-tests
description: >
  This skill should be used when the user asks to "write tests", "create Playwright tests", "write e2e tests",
  "convert selectors to tests", "turn exploration into tests", "fix a flaky test", "add a test for this flow",
  or wants to convert browser exploration results or test case specs into executable Playwright test code.
user-invocable: true
argument-hint: <test description or path to test case spec file>
allowed-tools:
  # MCP browser tools
  - mcp__plugin_web-testing-toolkit_agent-web-interface__ping
  - mcp__plugin_web-testing-toolkit_agent-web-interface__navigate
  - mcp__plugin_web-testing-toolkit_agent-web-interface__go_back
  - mcp__plugin_web-testing-toolkit_agent-web-interface__go_forward
  - mcp__plugin_web-testing-toolkit_agent-web-interface__reload
  - mcp__plugin_web-testing-toolkit_agent-web-interface__capture_snapshot
  - mcp__plugin_web-testing-toolkit_agent-web-interface__find_elements
  - mcp__plugin_web-testing-toolkit_agent-web-interface__get_element_details
  - mcp__plugin_web-testing-toolkit_agent-web-interface__scroll_element_into_view
  - mcp__plugin_web-testing-toolkit_agent-web-interface__scroll_page
  - mcp__plugin_web-testing-toolkit_agent-web-interface__click
  - mcp__plugin_web-testing-toolkit_agent-web-interface__type
  - mcp__plugin_web-testing-toolkit_agent-web-interface__press
  - mcp__plugin_web-testing-toolkit_agent-web-interface__select
  - mcp__plugin_web-testing-toolkit_agent-web-interface__hover
  - mcp__plugin_web-testing-toolkit_agent-web-interface__get_form_understanding
  - mcp__plugin_web-testing-toolkit_agent-web-interface__get_field_context
  - mcp__plugin_web-testing-toolkit_agent-web-interface__list_pages
  - mcp__plugin_web-testing-toolkit_agent-web-interface__close_page
  - mcp__plugin_web-testing-toolkit_agent-web-interface__close_session
  - mcp__plugin_web-testing-toolkit_agent-web-interface__take_screenshot
  # File operation tools for writing Playwright tests
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Write E2E Tests

Write, refactor, or fix Playwright E2E tests by converting browser exploration results or test case specifications into executable test code.

## Workflow

1. **Parse the input** — extract the test description or test case spec file path from the arguments: $ARGUMENTS
2. **Launch the playwright-test-writer agent** — use the Task tool to invoke the `playwright-test-writer` agent with the test description
3. **The agent will**:
   - Understand the user journey to test and success criteria
   - Inspect repo conventions (existing tests, fixtures, page objects, locator patterns)
   - Write tests using stable locators and event-driven waits
   - Assign unique test case IDs (`TC-<FEATURE>-<NUMBER>`) to every test
   - Run the tests to verify they pass
4. **Output** — the agent creates Playwright test files and returns a summary of changes, test case IDs, stability notes, and run commands

## Example Usage

```
/write-e2e-tests Write a login flow test for https://example.com/login
```

```
/write-e2e-tests Convert test-cases/checkout.md into Playwright tests
```

```
/write-e2e-tests Fix the flaky timeout in tests/e2e/cart.spec.ts
```

## Locator Priority Strategy

Use locators in this order of preference:

| Priority | Method | When to Use |
|----------|--------|-------------|
| 1 | `getByRole('role', { name })` | Buttons, links, headings, form controls |
| 2 | `getByLabel()` | Form fields with visible labels |
| 3 | `getByPlaceholder()` | Inputs with placeholder text |
| 4 | `getByTestId()` | When data-testid is available |
| 5 | `getByText()` | Short, stable text (avoid marketing copy) |
| 6 | CSS selectors | Last resort, always scoped tightly |

## Scope-to-Locator Mapping

| Journey Scope | Playwright Scoping |
|---------------|-------------------|
| `page` | No scoping needed |
| `header` | `page.locator('header')` |
| `main` | `page.locator('main')` |
| `nav` | `page.locator('nav')` |
| `dialog` | `page.locator('[role="dialog"]')` |
| `footer` | `page.locator('footer')` |

## Action-to-Playwright Mapping

| Journey Action | Playwright Code |
|----------------|-----------------|
| `goto` | `await page.goto(url)` |
| `click` | `await locator.click()` |
| `fill` | `await locator.fill(value)` |
| `select` | `await locator.selectOption(value)` |
| `assert` | `await expect(locator).toBeVisible()` |

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

## Assertion Mapping (from observed effects)

| Observed Effect | Playwright Assertion |
|----------------|---------------------|
| `url changed to /cart` | `await expect(page).toHaveURL(/cart/)` |
| `text 'Added' visible` | `await expect(page.getByText(/added/i)).toBeVisible()` |
| `radio 256GB now checked` | `await expect(locator).toBeChecked()` |
| `button now enabled` | `await expect(locator).toBeEnabled()` |
| `cart badge shows '1'` | `await expect(page.getByText('1')).toBeVisible()` |

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

## Test Template

```typescript
import { test, expect } from '@playwright/test';

test.use({
  viewport: { width: 1280, height: 800 },
  locale: 'en-US',
  timezoneId: 'America/Los_Angeles',
});

test('TC-FEATURE-001: Description of test case', async ({ page }) => {
  // s1: Navigate to target page
  await page.goto('https://example.com');

  // s2: Perform action
  await page.locator('main').getByRole('button', { name: /submit/i }).click();

  // Final assertions
  await expect(page.getByText(/success/i)).toBeVisible();
});
```

## Selector Map Format

For complex journeys, document primary and fallback locators:

```
- s2: primary `nav >> getByRole('link', { name: /iphone/i })`, fallback `getByText(/^iPhone$/i)`
- s5: primary `getByRole('radio', { name: /256gb/i })`, fallback `getByLabel(/256gb/i)`
```

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
    await page.getByRole('textbox', { name: /email/i }).fill('test@example.com');
    await page.getByRole('textbox', { name: /password/i }).fill('password');
    await page.getByRole('button', { name: /log in|sign in|submit/i }).click();
    await use(page);
  },
});
```

## Defaults Reference

| Setting | Default Value |
|---------|---------------|
| Language | TypeScript |
| Viewport | 1280x800 |
| Locale | en-US |
| Timezone | UTC |
| Test file | `tests/e2e/{goal-slug}.spec.ts` |

## Anti-Patterns to Avoid

1. **Raw CSS selectors** - Use semantic locators
2. **`waitForTimeout()`** - Use proper assertions instead
3. **Fragile `nth()`** - Add comment if unavoidable
4. **Exact long text** - Use regex with key words
5. **Unscoped locators** - Always scope to main/nav/dialog when possible
