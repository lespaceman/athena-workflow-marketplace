---
description: End-to-end Airbnb booking workflow - login, search, select property, and complete reservation.
---

# Complete Airbnb Booking

Full workflow to search, select, and book an Airbnb property.

## Usage

```
/athena-browser:airbnb/complete-booking --location <location> --checkin <date> --checkout <date> --guests <number> [--max-price <amount>]
```

## Options

- `--location <location>`: Destination - REQUIRED
- `--checkin <date>`: Check-in date (YYYY-MM-DD) - REQUIRED
- `--checkout <date>`: Check-out date (YYYY-MM-DD) - REQUIRED
- `--guests <number>`: Number of guests - REQUIRED
- `--max-price <amount>`: Maximum price per night (optional filter)

## Prerequisites

- Browser must be launched (`/athena-browser:common/launch`)
- User credentials available for login

## Workflow Steps

### Phase 1: Authentication

1. **Navigate to Airbnb**
   - Go to `https://www.airbnb.com`
   - Handle cookie consent

2. **Login**
   - Open login modal
   - Enter credentials
   - Complete authentication
   - Verify logged-in state

### Phase 2: Search

3. **Enter Search Criteria**
   - Fill location in search bar
   - Set check-in and check-out dates
   - Set guest count

4. **Execute Search**
   - Click search button
   - Wait for results

5. **Apply Filters** (if max-price specified)
   - Open filters
   - Set price range
   - Apply and refresh results

### Phase 3: Selection

6. **Browse Results**
   - Scroll through listings
   - Extract key info (price, rating, amenities)
   - Present options to user

7. **Select Property**
   - User chooses property (or auto-select based on criteria)
   - Click listing to open details

8. **Review Property Details**
   - Verify availability
   - Check amenities
   - Review house rules
   - Confirm price breakdown

### Phase 4: Booking

9. **Initiate Reservation**
   - Click "Reserve" button
   - Confirm dates and guests

10. **Review Booking Details**
    - Verify total price
    - Check cancellation policy
    - Review any special requirements

11. **Enter Payment** (if proceeding)
    - Fill payment information
    - Enter billing address
    - Review final total

12. **Confirm Booking**
    - Click "Confirm and pay"
    - Wait for confirmation
    - Capture confirmation details

### Phase 5: Confirmation

13. **Verify Booking**
    - Check for confirmation page
    - Extract confirmation number
    - Note check-in instructions
    - Report success to user

## Element Patterns

- **Reserve Button**: `kind: "button"`, `label: "Reserve"`
- **Price Breakdown**: Look for itemized costs section
- **Payment Form**: Credit card input fields
- **Confirm Button**: `kind: "button"`, `label: "Confirm and pay"`
- **Confirmation Number**: Displayed after successful booking

## MCP Tools Used

- `mcp__athena-browser-mcp-local__navigate`
- `mcp__athena-browser-mcp-local__find_elements`
- `mcp__athena-browser-mcp-local__click`
- `mcp__athena-browser-mcp-local__type`
- `mcp__athena-browser-mcp-local__press`
- `mcp__athena-browser-mcp-local__scroll_page`
- `mcp__athena-browser-mcp-local__capture_snapshot`

## User Interaction Points

The workflow pauses for user input at these points:
1. Login credentials (if not stored)
2. Property selection from search results
3. Payment information
4. Final booking confirmation

## Safety Notes

- Always show price breakdown before confirming
- Verify cancellation policy with user
- Never store payment credentials
- Confirm property details match user requirements
- Check for any additional fees (cleaning, service)

## Error Handling

- If property unavailable: Return to search results
- If payment fails: Prompt for alternative payment
- If dates blocked: Suggest alternative dates
- If login expires: Re-authenticate
