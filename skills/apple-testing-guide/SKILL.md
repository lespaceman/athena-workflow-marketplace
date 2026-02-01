---
name: apple-testing-guide
description: >
  Use when creating or debugging Playwright tests for apple.com. Contains accumulated learnings about
  Apple's hidden radio inputs, React state handlers, sticky header interception, sequential form
  enablement, and dynamic IDs.
user-invocable: false
allowed-tools:
  - mcp__agent-web-interface__ping
  - mcp__agent-web-interface__navigate
  - mcp__agent-web-interface__go_back
  - mcp__agent-web-interface__go_forward
  - mcp__agent-web-interface__reload
  - mcp__agent-web-interface__capture_snapshot
  - mcp__agent-web-interface__find_elements
  - mcp__agent-web-interface__get_element_details
  - mcp__agent-web-interface__scroll_element_into_view
  - mcp__agent-web-interface__scroll_page
  - mcp__agent-web-interface__click
  - mcp__agent-web-interface__type
  - mcp__agent-web-interface__press
  - mcp__agent-web-interface__select
  - mcp__agent-web-interface__hover
  - mcp__agent-web-interface__get_form_understanding
  - mcp__agent-web-interface__get_field_context
  - mcp__agent-web-interface__list_pages
  - mcp__agent-web-interface__close_page
  - mcp__agent-web-interface__close_session
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

// KNOWN EXCEPTION: Apple's React state propagation requires this delay;
// no observable DOM event to wait for after dispatchEvent.
await page.waitForTimeout(300);
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
