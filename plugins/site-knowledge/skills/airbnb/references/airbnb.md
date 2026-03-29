# Airbnb Reference

Use this file for Airbnb-specific heuristics after loading `agent-web-interface-guide`. Do not rely on exact selectors; Airbnb frequently re-renders controls and varies by locale and experiment bucket.

## URL Patterns

- Home: `https://www.airbnb.com`
- Search results: `https://www.airbnb.com/s/<location>/homes`
- Listing detail: `https://www.airbnb.com/rooms/<id>`
- Experiences: `https://www.airbnb.com/experiences`

## Search Heuristics

Typical search flow:

1. Choose location
2. Choose check-in and check-out dates
3. Choose guests
4. Submit search

Airbnb may collapse the search UI into progressive steps, a modal, or a sticky header variant. Re-read the page after each step.

## Results Heuristics

- Results may be infinite-scroll or paginated with `Show more`.
- Filters often open as modals or drawers rather than inline controls.
- Listing cards usually expose title, price, rating, and save/heart actions.
- Map/list toggles can re-layout the page substantially.

## Listing Heuristics

Before any reserve action, verify:

- Listing identity
- Dates
- Guest count
- Nightly price
- Full price breakdown including fees
- Cancellation policy when relevant

## Modal And Prompt Heuristics

Common interruptions:

- Cookie consent
- Login or sign-up prompt
- Translation prompt
- Date or guest picker overlays

Dismiss or resolve them explicitly, then snapshot again before continuing.

## Common Failure Modes

- Search controls re-rendering and invalidating stale element IDs
- Date selection not persisting when the modal closes
- Guest counts resetting after filter changes
- Price mismatch between results card and final booking breakdown
- Hidden fees only appearing deeper in the booking flow
