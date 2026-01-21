---
name: add-to-bag
description: Add configured Apple product to shopping bag and verify cart contents.
---

# Add to Bag

Add the currently configured product to the Apple Store shopping bag.

## Usage

```
/athena-browser:apple/add-to-bag [--verify]
```

## Options

- `--verify`: Verify cart contents after adding (default: true)

## Prerequisites

- Browser must be launched (`/athena-browser:common/launch`)
- Product must be configured (e.g., via `/athena-browser:apple/configure-iphone`)

## Workflow Steps

1. **Verify Configuration Complete**
   - Capture snapshot
   - Ensure all required options selected
   - Check for "Add to Bag" button availability

2. **Skip Optional Steps** (if present)
   - Trade-in prompt: Click "Skip" or "No trade-in"
   - AppleCare: Click "No AppleCare" or skip

3. **Add to Bag**
   - Find "Add to Bag" button: `kind: "button"`, `label: "Add to Bag"`
   - Click the button
   - Wait for confirmation

4. **Handle Confirmation Modal**
   - Modal may appear with options:
     - "Continue Shopping"
     - "Review Bag" / "Check Out"
   - Click appropriate option based on workflow

5. **Verify Cart** (if --verify)
   - Navigate to bag/cart
   - Capture snapshot
   - Extract cart contents:
     - Product name and configuration
     - Quantity
     - Price
     - Subtotal

## Element Patterns

- **Add to Bag Button**: `kind: "button"`, `label: "Add to Bag"`
- **Skip Trade-in**: `kind: "button"` or `kind: "link"`, label contains "Skip" or "No"
- **Skip AppleCare**: `kind: "button"`, label contains "No" or "Skip"
- **Confirmation Modal**: Overlay with cart preview
- **Review Bag Link**: `kind: "link"`, `label: "Review Bag"` or bag icon
- **Cart Icon**: Usually in header, shows item count

## MCP Tools Used

- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__capture_snapshot`
- `mcp__athena-browser-mcp-local__navigate`

## Cart Verification

After adding to bag, verify:
- Product added correctly
- Configuration matches selection
- Price is correct
- Quantity is accurate

## Example Workflow

```
Assistant: I'll add the configured iPhone to your bag.

[Click "Add to Bag" button]
[Handle any prompts for trade-in/AppleCare]
[Wait for confirmation]

Product added to bag successfully!
- iPhone 16 Pro Max
- 256GB, Black Titanium
- Unlocked
- Price: $1,199.00

Would you like to continue shopping or proceed to checkout?
```

## Error Handling

- **Button not found**: Scroll to ensure button is visible
- **Configuration incomplete**: Prompt to complete required selections
- **Out of stock**: Report availability issue
- **Session timeout**: Refresh page and retry

## Notes

- Add to Bag button may be disabled until all required options selected
- Some products have quantity limits
- Bag contents persist for limited time
- Sign in recommended for cart persistence across sessions
