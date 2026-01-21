---
description: End-to-end Apple Store purchase - navigate, configure, add to bag, and checkout.
---

# Complete Apple Store Purchase

Full workflow to browse, configure, and purchase an Apple product.

## Usage

```
/athena-browser:apple/complete-purchase --product <product> [--model <model>] [--color <color>] [--storage <storage>] [--carrier <carrier>]
```

## Options

- `--product <product>`: Product category (iphone, mac, ipad, watch) - REQUIRED
- `--model <model>`: Specific model name
- `--color <color>`: Color preference
- `--storage <storage>`: Storage capacity
- `--carrier <carrier>`: Carrier (for iPhone)

## Prerequisites

- Browser must be launched (`/athena-browser:common/launch`)
- Apple ID for checkout (or guest checkout)
- Payment method

## Workflow Steps

### Phase 1: Navigation

1. **Navigate to Apple Store**
   - Go to `https://www.apple.com/store`
   - Handle any cookie consent

2. **Navigate to Product Category**
   - Find and click product section (iPhone, Mac, etc.)
   - Wait for product listing page

3. **Select Product Model**
   - Find the specific model
   - Click to open configurator

### Phase 2: Configuration

4. **Configure Product**
   - Select color (if applicable)
   - Select storage/memory
   - Select carrier/connectivity (if applicable)
   - Handle trade-in prompts
   - Handle AppleCare prompts

5. **Review Configuration**
   - Verify all selections
   - Check price
   - Confirm availability

### Phase 3: Cart

6. **Add to Bag**
   - Click "Add to Bag"
   - Confirm addition

7. **Review Bag**
   - Navigate to bag
   - Verify contents
   - Check totals

### Phase 4: Checkout

8. **Initiate Checkout**
   - Click "Check Out"
   - Choose: Sign in with Apple ID or Guest checkout

9. **Authentication** (if signing in)
   - Enter Apple ID
   - Enter password
   - Handle 2FA if enabled

10. **Shipping Information**
    - Enter/confirm shipping address
    - Select shipping method
    - Note delivery estimate

11. **Payment**
    - Select payment method
    - Enter payment details (or use Apple Pay)
    - Enter billing address

12. **Review Order**
    - Verify all details:
      - Product configuration
      - Shipping address
      - Payment method
      - Total amount

13. **Place Order**
    - Click "Place Order" / "Buy"
    - Wait for confirmation

### Phase 5: Confirmation

14. **Order Confirmation**
    - Capture confirmation page
    - Extract:
      - Order number
      - Estimated delivery
      - Order summary
    - Report to user

## Element Patterns

- **Check Out Button**: `kind: "button"`, `label: "Check Out"`
- **Apple ID Input**: `kind: "textbox"`, for email/Apple ID
- **Password Input**: `kind: "textbox"`, type password
- **Address Fields**: Standard form inputs
- **Payment Fields**: Credit card inputs
- **Place Order Button**: `kind: "button"`, `label: "Place Order"` or similar

## MCP Tools Used

- `mcp__athena-browser-mcp-local__navigate`
- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__type`
- `mcp__athena-browser-mcp-local__select`
- `mcp__athena-browser-mcp-local__scroll_page`
- `mcp__athena-browser-mcp-local__capture_snapshot`

## User Interaction Points

Pause for user input at:
1. Configuration confirmation
2. Apple ID credentials
3. Payment information
4. Final order confirmation

## Safety Notes

- Show order total before confirming
- Verify shipping address is correct
- Never store payment credentials
- Confirm user wants to proceed at each major step
- Check for promo codes / discounts

## Error Handling

- **Product unavailable**: Suggest alternatives or waitlist
- **Payment declined**: Prompt for alternative payment
- **Address validation failed**: Assist with correction
- **Session timeout**: Re-authenticate and restore cart

## Notes

- Apple Pay significantly simplifies checkout on supported devices
- Guest checkout available but order tracking limited
- Corporate/education discounts may apply
- Financing options (Apple Card, installments) available
