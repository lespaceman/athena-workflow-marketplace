---
name: write-e2e-tests
description: >
  Use when the user wants executable Playwright test code written, refactored, or fixed.
  Triggers: "write Playwright tests", "write e2e tests", "create test code", "implement these test cases",
  "convert test specs to code", "turn selectors into tests", "fix a flaky test", "stabilize this test",
  "add a test for this flow", "write tests for this feature", "convert TC-IDs to Playwright",
  "refactor this test", "improve test locators", "fix timeout in test".
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

## Context-Saving Strategy

For large test suites, use Task tool with `general-purpose` subagent to write individual test files. Pass the subagent:
- The test case spec (from `test-cases/<feature>.md`)
- Codebase conventions discovered in step 2
- These operating principles and mapping tables
