---
name: airbnb
description: >
  Use when automating airbnb.com, searching for stays, browsing experiences, creating wishlists,
  completing bookings, or writing tests for Airbnb flows. Covers site structure, element patterns,
  search forms, modal handling, and common issues.
user-invocable: false
---

# Airbnb Automation Skill

This skill provides patterns and knowledge for automating interactions with airbnb.com.

## Site Structure

### Main Sections
- **Stays**: Default landing, property rentals
- **Experiences**: Tours, activities, local experiences
- **Online Experiences**: Virtual experiences
- **Wishlists**: Saved properties (requires login)

### URL Patterns
- Home: `https://www.airbnb.com`
- Search results: `https://www.airbnb.com/s/{location}/homes`
- Listing detail: `https://www.airbnb.com/rooms/{id}`
- Experiences: `https://www.airbnb.com/experiences`
- Wishlists: `https://www.airbnb.com/wishlists`

## Element Patterns

### Search Bar Components

| Element | Selector |
|---------|----------|
| Location input | kind: "textbox", label contains "Where" |
| Check-in button | kind: "button", label contains "Check in" |
| Check-out button | kind: "button", label contains "Check out" |
| Guest selector | kind: "button", label contains "guests" or "Who" |
| Search button | kind: "button", magnifying glass icon |

### Date Picker

| Element | Selector |
|---------|----------|
| Calendar container | Modal overlay with month grid |
| Month navigation | Arrow buttons for prev/next month |
| Date cells | Clickable day numbers |
| Selected range | Highlighted date range |

### Guest Selector

| Element | Selector |
|---------|----------|
| Adults counter | +/- buttons for adults (13+) |
| Children counter | +/- buttons for children (2-12) |
| Infants counter | +/- buttons for infants (under 2) |
| Close/Apply | Button to confirm selection |

### Search Results Page

| Element | Selector |
|---------|----------|
| Filter bar | Horizontal bar with filter buttons |
| Filters modal | Full filter panel |
| Listing cards | region: "main", cards with image, title, price |
| Map toggle | Switch between list and map view |
| Pagination | "Show more" or infinite scroll |

### Listing Card Elements

| Element | Selector |
|---------|----------|
| Image carousel | Swipeable property images |
| Property title | Link to detail page |
| Price | "$XXX night" pattern |
| Rating | Star icon with decimal (4.95) |
| Heart/Save icon | kind: "button", heart icon |

### Listing Detail Page

| Element | Selector |
|---------|----------|
| Image gallery | Large photo grid/carousel |
| Title | Main heading |
| Host info | Host name, photo section |
| Amenities | List of features |
| Reserve button | kind: "button", label: "Reserve" |
| Calendar | Availability calendar |

## Modal Handling

### Cookie Consent
- **Selector**: kind: "button", label: "Accept" or "Accept all"
- **Location**: Bottom of page or modal overlay
- **Action**: Click to dismiss

### Login Prompt
- **Trigger**: Attempting to save, book, or message
- **Selector**: Modal with login options
- **Options**: Email, Phone, Google, Facebook, Apple
- **Dismiss**: Click outside or X button

### Translation Popup
- **Trigger**: Non-English location
- **Selector**: kind: "button", label: "Close" or "X"
- **Action**: Dismiss to continue in English

## Form Patterns

### Search Form Workflow
1. Find location input: kind: "textbox", label contains "Where"
2. Type location text
3. Wait for suggestions dropdown
4. Click matching suggestion
5. Find date picker, select dates
6. Find guest selector, adjust counts
7. Click search button

### Login Form Workflow
1. Find login button in header
2. Click to open modal
3. Select "Continue with email"
4. Enter email in textbox
5. Click Continue
6. Enter password
7. Click Log in

## Filter Options

### Price Range
- Min price input
- Max price input
- Price histogram visualization

### Property Type
- Entire place
- Private room
- Shared room
- Hotel room

### Rooms and Beds
- Bedrooms (any, 1, 2, 3, 4+)
- Beds (any, 1, 2, 3, 4+)
- Bathrooms (any, 1, 2, 3, 4+)

### Amenities
- Wifi, Kitchen, Washer, Dryer
- Air conditioning, Heating
- Pool, Hot tub
- Free parking, EV charger

### Booking Options
- Instant Book
- Self check-in
- Free cancellation

## Data Extraction

### From Search Results
For each listing card extract:
- Title: Property name/description
- Price: "$XXX per night"
- Rating: Decimal (e.g., 4.92)
- Reviews: Count (e.g., "128 reviews")
- Type: Entire home, room, etc.
- Superhost: Boolean indicator

### From Listing Page
- Full title and description
- Complete amenity list
- House rules
- Cancellation policy
- Check-in/out times
- Host details
- Availability calendar
- Full price breakdown
- All reviews

## Best Practices

1. **Handle modals first**: Always dismiss cookie consent and login prompts before main interactions
2. **Wait for dynamic content**: Airbnb uses heavy JavaScript - use `snapshot` after actions
3. **Use scroll for results**: Search results use infinite scroll - use `scroll` to load more
4. **Verify selections**: After selecting dates/guests, verify the selection persisted
5. **Extract before navigate**: Get listing data before clicking away
6. **Handle rate limiting**: Add delays between rapid interactions

## Common Issues

| Issue | Solution |
|-------|----------|
| Element not found | May be in modal or below fold - scroll and retry |
| Stale elements | Page updated - capture new snapshot |
| Dates unavailable | Check calendar before booking flow |
| Price mismatch | Fees added at checkout - get full breakdown |
| Regional variations | Site varies by country - check location settings |
