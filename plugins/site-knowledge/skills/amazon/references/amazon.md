# Amazon Reference

Use this file for Amazon-specific heuristics after loading `agent-web-interface-guide`. Do not rely on exact selectors; Amazon frequently changes labels, placement, and region-specific chrome.

## URL Patterns

- Home: `https://www.amazon.com`
- Search results: `https://www.amazon.com/s?k=<query>`
- Product detail: `https://www.amazon.com/<slug>/dp/<asin>`
- Cart: `https://www.amazon.com/gp/cart/view.html`

## Search Heuristics

- Prefer precise product queries over broad ones.
- Sponsored results often appear above the best organic match.
- Related-search links can narrow ambiguous results faster than refining the query manually.
- Autocomplete suggestions may not be directly targetable; pressing Enter is often more reliable.

## Product Page Heuristics

- Some products expose a direct `Add to Cart`.
- Others route through `See All Buying Options`, especially when multiple sellers compete or stock is constrained.
- Seller, condition, shipping speed, and region can change what controls are visible.
- The first prominent purchase control is not always the cheapest or intended seller option.

## Buying Options Heuristics

When `Add to Cart` is absent:

1. Open the buying options surface
2. Compare seller, condition, and price
3. Pick the intended seller explicitly
4. Re-check the resulting cart page for the actual seller and item configuration

## Cart Verification

Confirm:

- Product title
- Seller when relevant
- Quantity
- Price per item
- Subtotal

Do not trust search-result price text as final cart price. Amazon often changes price or seller between results and checkout surfaces.

## Common Modals And Interruptions

- Region or locale prompt
- Sign-in prompt
- Protection plan or add-on upsell
- Buying options drawer or modal

Dismiss or resolve these explicitly before continuing.

## Common Failure Modes

- Search results polluted by accessories or competing products
- Sponsored result chosen accidentally
- Wrong seller added through buying options
- Region-specific currency or shipping state confusing comparisons
- Cart page showing bundle, protection plan, or add-on that was added during the flow
