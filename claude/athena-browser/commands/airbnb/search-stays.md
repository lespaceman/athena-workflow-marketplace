---
name: search-stays
description: Search for Airbnb stays with location, dates, guests, and filters like price and amenities.
---

# Search Airbnb Stays

Search for accommodation on Airbnb with various criteria and filters.

## Usage

```
/athena-browser:airbnb/search-stays --location <location> [--checkin <date>] [--checkout <date>] [--guests <number>] [--min-price <amount>] [--max-price <amount>]
```

## Options

- `--location <location>`: Destination (city, address, or region) - REQUIRED
- `--checkin <date>`: Check-in date (YYYY-MM-DD format)
- `--checkout <date>`: Check-out date (YYYY-MM-DD format)
- `--guests <number>`: Number of guests
- `--min-price <amount>`: Minimum price per night
- `--max-price <amount>`: Maximum price per night

## Prerequisites

- Browser must be launched (`/athena-browser:common/launch`)

## Workflow Steps

1. **Navigate to Airbnb**
   - Use `navigate` to go to `https://www.airbnb.com`
   - Handle cookie consent if present

2. **Enter Location**
   - Find search bar: `kind: "textbox"`, label contains "Where"
   - Click to focus
   - Type the destination
   - Wait for suggestions dropdown
   - Click the matching suggestion or press Enter

3. **Set Check-in Date** (if provided)
   - Find check-in date picker: `kind: "button"`, label contains "Check in"
   - Click to open calendar
   - Navigate to correct month
   - Click the target date

4. **Set Check-out Date** (if provided)
   - Find check-out date picker (usually auto-focused after check-in)
   - Navigate to correct month if needed
   - Click the target date

5. **Set Guest Count** (if provided)
   - Find guest selector: `kind: "button"`, label contains "guests" or "Who"
   - Click to open dropdown
   - Use +/- buttons to adjust adult/child counts

6. **Execute Search**
   - Find and click the search button (magnifying glass icon)
   - Wait for results to load

7. **Apply Price Filters** (if provided)
   - Find "Filters" button
   - Click to open filters panel
   - Find price range inputs
   - Set min/max values
   - Apply filters

8. **Extract Results**
   - Capture snapshot of results page
   - Find listing cards in main region
   - Extract: property name, price, rating, key features

## Element Patterns

- **Search Bar**: `kind: "textbox"`, label contains "Where"
- **Date Picker**: Calendar modal with month navigation
- **Guest Selector**: Dropdown with +/- controls
- **Search Button**: `kind: "button"` with magnifying glass icon
- **Filter Button**: `kind: "button"`, `label: "Filters"`
- **Listing Cards**: Cards in `region: "main"` with price patterns

## MCP Tools Used

- `mcp__athena-browser-mcp-local__navigate`
- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__type`
- `mcp__athena-browser-mcp-local__press`
- `mcp__athena-browser-mcp-local__scroll_page`
- `mcp__athena-browser-mcp-local__capture_snapshot`

## Notes

- Location suggestions appear as you type - select the appropriate one
- Flexible dates option available if exact dates not provided
- Results can be sorted by relevance, price, or rating
- Use scroll_page to load more results (infinite scroll)
