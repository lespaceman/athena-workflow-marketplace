---
name: apple
description: Patterns and best practices for automating Apple Store - products, configuration, checkout
---

# Apple Store Automation Skill

This skill provides patterns and knowledge for automating interactions with apple.com/store.

## Site Structure

### Main Sections

| Section | URL Path |
|---------|----------|
| Store Home | /store |
| Mac | /shop/buy-mac |
| iPhone | /shop/buy-iphone |
| iPad | /shop/buy-ipad |
| Watch | /shop/buy-watch |
| AirPods | /shop/buy-airpods |
| Accessories | /shop/accessories |
| Bag | /shop/bag |

### URL Patterns
- Product listing: `/shop/buy-{product}`
- Product config: `/shop/buy-{product}/{model}`
- Bag/Cart: `/shop/bag`
- Checkout: `/shop/checkout`
- Order status: `/shop/order/list`

## Element Patterns

### Navigation

| Element | Selector |
|---------|----------|
| Header nav | Product category links (Mac, iPhone, etc.) |
| Shop link | kind: "link", label contains "Shop" or "Buy" |
| Store link | kind: "link", label: "Store" |
| Bag icon | kind: "link", bag/cart icon in header |
| Search | kind: "textbox", search icon |

### Product Tiles

| Element | Selector |
|---------|----------|
| Product card | kind: "link", contains product name |
| Product image | Within card, clickable |
| Price display | "$X,XXX" or "From $X,XXX" |
| Colors preview | Small color swatches on card |
| "Buy" link | Direct link to configurator |

### Product Configurator

#### Model Selection

| Element | Selector |
|---------|----------|
| Model tiles | Large cards for each model variant |
| Model name | iPhone 16 Pro, iPhone 16 Pro Max, etc. |
| Starting price | "From $999" display |
| Select button | kind: "button" or clickable card |

#### Color Selection

| Element | Selector |
|---------|----------|
| Color swatches | kind: "radio", circular color buttons |
| Color name | Label appears on hover/selection |
| Selected state | Ring/border around selected color |

#### Storage Selection

| Element | Selector |
|---------|----------|
| Storage options | kind: "radio", grouped buttons |
| Capacity text | "128GB", "256GB", "512GB", "1TB" |
| Price delta | Shows additional cost (+$100, etc.) |

#### Carrier/SIM Selection (iPhone)

| Element | Selector |
|---------|----------|
| Carrier options | kind: "radio" |
| Carriers | AT&T, Verizon, T-Mobile |
| Unlocked | "Connect to any carrier later" |

### Cart/Bag

| Element | Selector |
|---------|----------|
| Bag link | Header icon with item count |
| Product list | Items in bag |
| Configuration | Selected options for each item |
| Price each | Individual item price |
| Remove link | kind: "link", "Remove" |
| Check Out button | kind: "button", "Check Out" |

### Optional Add-ons

#### Trade-in

| Element | Selector |
|---------|----------|
| Trade-in prompt | Modal or inline section |
| "Get credit" option | Trade device for credit |
| "No trade-in" option | Skip trade-in |

#### AppleCare

| Element | Selector |
|---------|----------|
| AppleCare options | kind: "radio" |
| AppleCare+ option | Extended warranty |
| No AppleCare | Decline coverage |

## Configuration Flow

Standard Apple product configuration follows this pattern:

1. **Model Selection** → Select base model
2. **Color** → Choose color option
3. **Storage/Memory** → Select capacity
4. **Carrier/SIM** → Choose carrier (iPhone only)
5. **Trade-in** → Skip or trade device
6. **AppleCare** → Add or decline
7. **Add to Bag** → Complete configuration

Each step may require:
- Page stabilization (wait for dynamic updates)
- Scrolling to see all options
- Price verification after selection

## Form Patterns

### Product Configuration Workflow
1. Find color swatches (kind: "radio")
2. Click desired color
3. Find storage options (kind: "radio")
4. Click desired storage
5. Find carrier options (kind: "radio")
6. Click carrier preference
7. Verify price updated

### Add to Bag Workflow
1. Find "Add to Bag" button (kind: "button")
2. Click Add to Bag
3. Handle trade-in prompt (click skip/no)
4. Handle AppleCare prompt (click no or select)
5. Capture snapshot for confirmation

### Checkout Workflow
1. Navigate to bag
2. Find "Check Out" button
3. Click Check Out
4. Choose sign in or guest
5. Fill shipping address
6. Select shipping method
7. Fill payment details
8. Review order summary
9. Click Place Order (with user confirmation)

## Data Extraction

### From Product Page
- Product name and model
- Available colors with names
- Storage options with prices
- Carrier options
- Base price and configured price
- Availability/shipping estimate

### From Bag
- Product name
- Full configuration (color, storage, etc.)
- Quantity
- Unit price
- Subtotal
- Estimated tax
- Total

### From Order Confirmation
- Order number
- Items ordered
- Shipping address
- Estimated delivery
- Payment method (last 4 digits)
- Order total

## Best Practices

1. **Wait for dynamic updates**: Apple pages use heavy JavaScript - prices update dynamically
2. **Verify each selection**: After clicking an option, verify it's selected in snapshot
3. **Handle sticky headers**: May need to scroll elements into view accounting for header
4. **Check availability**: Some configurations may be out of stock
5. **Confirm before purchase**: Always show user final price and get confirmation
6. **Handle modals**: Trade-in and AppleCare prompts appear as modals
7. **Save configuration**: Options may reset on navigation - complete config before leaving

## Common Issues

| Issue | Solution |
|-------|----------|
| Price not updating | Page needs time to update - capture new snapshot |
| Option not selectable | May be out of stock or incompatible |
| Add to Bag disabled | Required options not selected |
| Session timeout | Re-authenticate with Apple ID |
| Checkout errors | Address or payment validation failures |
| Regional restrictions | Some products vary by region |
