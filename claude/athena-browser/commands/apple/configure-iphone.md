---
name: configure-iphone
description: Configure iPhone model, color, storage, and carrier options in the Apple Store.
---

# Configure iPhone

Select iPhone model, color, storage capacity, and carrier options.

## Usage

```
/athena-browser:apple/configure-iphone --model <model> [--color <color>] [--storage <storage>] [--carrier <carrier>]
```

## Options

- `--model <model>`: iPhone model (e.g., "iPhone 16 Pro Max", "iPhone 16", "iPhone SE")
- `--color <color>`: Color option (e.g., "Black Titanium", "White", "Blue")
- `--storage <storage>`: Storage capacity (e.g., "128GB", "256GB", "512GB", "1TB")
- `--carrier <carrier>`: Carrier option (e.g., "AT&T", "Verizon", "T-Mobile", "Unlocked")

## Prerequisites

- Browser must be launched (`/athena-browser:common/launch`)

## Workflow Steps

1. **Navigate to iPhone Selection**
   - Go to `https://www.apple.com/shop/buy-iphone`
   - Or use `/athena-browser:apple/navigate-store --section iphone`

2. **Select iPhone Model**
   - Find model tiles/cards
   - Look for: `kind: "link"`, label contains model name
   - Click the desired model
   - Wait for configurator page

3. **Select Color**
   - Find color swatches: `kind: "radio"` in color section
   - Look for color name labels
   - Click the desired color
   - Wait for image update

4. **Select Storage**
   - Find storage options: `kind: "radio"` in storage section
   - Options typically: 128GB, 256GB, 512GB, 1TB
   - Click the desired storage
   - Note price change

5. **Select Carrier/SIM Option**
   - Find carrier options
   - Options: Major carriers or "Connect to any carrier later" (unlocked)
   - Click the desired option

6. **Review Configuration**
   - Capture snapshot
   - Extract:
     - Selected configuration
     - Total price
     - Availability/shipping estimate

## Configuration Flow

```
Model Selection → Color → Storage → Carrier/SIM → Trade-in (optional) → AppleCare (optional)
```

## Element Patterns

- **Model Cards**: `kind: "link"`, contains "iPhone" and model name
- **Color Swatches**: `kind: "radio"`, grouped as color options
- **Storage Options**: `kind: "radio"`, text includes "GB" or "TB"
- **Carrier Selection**: `kind: "radio"`, carrier names
- **Price Display**: Updated dynamically with configuration

## MCP Tools Used

- `mcp__athena-browser-mcp-local__navigate`
- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__capture_snapshot`
- `mcp__athena-browser-mcp-local__scroll_element_into_view`

## Available Options (Example - iPhone 16 Pro Max)

### Colors
- Black Titanium
- White Titanium
- Natural Titanium
- Desert Titanium

### Storage
- 256GB
- 512GB
- 1TB

### Carriers
- AT&T
- Verizon
- T-Mobile
- Unlocked (Connect to any carrier later)

## Notes

- Prices update dynamically as options change
- Some color/storage combinations may have different availability
- Carrier selection affects pricing (subsidized vs. full price)
- Configuration state preserved during navigation
- Use scroll_element_into_view if options are below fold
