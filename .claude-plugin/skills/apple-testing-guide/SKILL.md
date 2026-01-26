---
name: apple-testing-guide
description: Accumulated learnings for writing Playwright tests on apple.com. Reference this when creating or debugging Apple Store automation tests.
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

# Apple.com Playwright Testing Guide

> **This is a living document.** Each section captures learnings from specific test implementations. Reference and apply relevant patterns when writing new tests for apple.com.

---

## iPhone Configuration Form (`/shop/buy-iphone/*`)

**Source:** Testing iPhone 17 color/storage/trade-in/payment/carrier/AppleCare selection flow.

### Problem
Apple uses hidden `<input type="radio">` with visible `<label>` overlays. React state handlers are bound to the label, not the input.

### What Fails
- `click()` / `click({ force: true })` - sets DOM state but doesn't trigger React
- `page.mouse.click(x, y)` - sticky header (`rf-bfe-stickybar`) intercepts
- Simple `dispatchEvent('click')` - incomplete event sequence

### Solution
Dispatch **full event sequence** on both label and radio:

```typescript
await page.evaluate((id) => {
  const radio = document.getElementById(id);
  const label = document.querySelector(`label[for="${id}"]`);

  // Events on LABEL (where React handlers are bound)
  ['mousedown', 'mouseup', 'click'].forEach(e =>
    label.dispatchEvent(new MouseEvent(e, { bubbles: true, cancelable: true, view: window }))
  );

  // State + events on RADIO
  radio.checked = true;
  radio.dispatchEvent(new Event('input', { bubbles: true }));
  radio.dispatchEvent(new Event('change', { bubbles: true }));
  radio.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
}, radioId);

await page.waitForTimeout(300); // Allow React state update
```

### Form Behavior
- Steps enable sequentially: Color → Storage → Trade-in → Payment → Carrier → AppleCare
- Wait for each step: `await expect(locator).toBeEnabled({ timeout: 10000 });`
- IDs are dynamic (`:rc:`, `:rf:`), use accessible names instead:
  ```typescript
  page.getByRole('radio', { name: 'White' })
  page.getByRole('radio', { name: /512GB/i })
  ```
- Use serial execution to avoid rate limiting:
  ```typescript
  test.describe.configure({ mode: 'serial' });
  ```

---

<!-- Add new sections below as more flows are tested -->
