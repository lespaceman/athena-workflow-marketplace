---
description: Navigate to Apple Store sections - iPhone, Mac, iPad, Watch, and accessories.
---

# Navigate Apple Store

Navigate to specific sections of the Apple online store.

## Usage

```
/athena-browser:apple/navigate-store [--section <section>] [--product <product>]
```

## Options

- `--section <section>`: Store section (mac, iphone, ipad, watch, airpods, accessories)
- `--product <product>`: Specific product to navigate to

## Prerequisites

- Browser must be launched (`/athena-browser:common/launch`)

## Workflow Steps

1. **Navigate to Apple Store**
   - Use `navigate` to go to `https://www.apple.com/store`
   - Wait for page load

2. **Handle Cookie Consent** (if present)
   - Find cookie consent banner
   - Click accept button

3. **Navigate to Section** (if specified)
   - Find navigation menu
   - Click on the specified section
   - Wait for section page to load

4. **Navigate to Product** (if specified)
   - Find product tile/link
   - Click to open product page
   - Wait for page load

5. **Capture Page State**
   - Take snapshot
   - Report current location and available options

## Store Sections

| Section | URL Path | Products |
|---------|----------|----------|
| Mac | /shop/buy-mac | MacBook Air, MacBook Pro, iMac, Mac mini, Mac Studio, Mac Pro |
| iPhone | /shop/buy-iphone | iPhone 16 Pro, iPhone 16, iPhone 15, iPhone SE |
| iPad | /shop/buy-ipad | iPad Pro, iPad Air, iPad, iPad mini |
| Watch | /shop/buy-watch | Apple Watch Ultra, Series 10, SE |
| AirPods | /shop/buy-airpods | AirPods Pro, AirPods, AirPods Max |
| Accessories | /shop/accessories | Cases, chargers, cables, etc. |

## Element Patterns

- **Navigation Menu**: Header with product categories
- **Product Tiles**: `kind: "link"`, contains product name
- **Shop Links**: Links with "Shop" or "Buy" text
- **Category Cards**: Large clickable cards with product images

## MCP Tools Used

- `mcp__athena-browser-mcp-local__navigate`
- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__capture_snapshot`

## Notes

- Apple Store pages may have dynamic loading - wait for content
- Some products have dedicated landing pages vs. configurator pages
- Regional pricing and availability varies
- Use breadcrumbs to track navigation hierarchy
