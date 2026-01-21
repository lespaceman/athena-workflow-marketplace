---
description: Discover and browse Airbnb Experiences - tours, activities, and local guides.
---

# Browse Airbnb Experiences

Discover and browse local experiences, tours, and activities on Airbnb.

## Usage

```
/athena-browser:airbnb/browse-experiences --location <location> [--date <date>] [--category <category>]
```

## Options

- `--location <location>`: Location to search for experiences - REQUIRED
- `--date <date>`: Date for the experience (YYYY-MM-DD format)
- `--category <category>`: Category filter (e.g., "food", "tours", "art", "sports")

## Prerequisites

- Browser must be launched (`/athena-browser:common/launch`)

## Workflow Steps

1. **Navigate to Experiences**
   - Use `navigate` to go to `https://www.airbnb.com/experiences`
   - Handle cookie consent if present

2. **Enter Location**
   - Find location search bar
   - Type the destination
   - Select from suggestions

3. **Set Date** (if provided)
   - Find date picker
   - Navigate to correct month
   - Select the target date

4. **Apply Category Filter** (if provided)
   - Find category tabs/buttons
   - Click the appropriate category

5. **Browse Results**
   - Capture snapshot
   - Extract experience cards
   - Get: title, host, price, rating, duration

6. **Get Experience Details**
   - Click on an experience card
   - Extract full details:
     - Description
     - Itinerary
     - What's included
     - Host information
     - Reviews
     - Availability

## Element Patterns

- **Location Search**: `kind: "textbox"` in header area
- **Category Tabs**: Horizontal navigation buttons
- **Experience Cards**: Cards with image, title, price
- **Date Picker**: Calendar component
- **Price Display**: Look for "$" followed by number

## MCP Tools Used

- `mcp__athena-browser-mcp-local__navigate`
- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__type`
- `mcp__athena-browser-mcp-local__scroll_page`
- `mcp__athena-browser-mcp-local__capture_snapshot`
- `mcp__athena-browser-mcp-local__get_node_details`

## Experience Categories

- **Food & Drink**: Cooking classes, food tours, wine tasting
- **Tours**: Walking tours, sightseeing, historical
- **Art & Culture**: Museums, crafts, local traditions
- **Sports**: Surfing, hiking, yoga, outdoor activities
- **Entertainment**: Shows, nightlife, unique activities
- **Nature**: Wildlife, gardens, scenic experiences

## Data Extraction

For each experience, extract:
- Title
- Host name
- Price per person
- Duration
- Rating and review count
- Key highlights

## Notes

- Experiences have limited availability - check dates
- Some experiences require minimum participants
- Online experiences also available (filter option)
- Prices shown per person unless noted
