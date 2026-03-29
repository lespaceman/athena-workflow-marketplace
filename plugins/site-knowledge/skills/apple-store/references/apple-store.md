# Apple Store Reference

Use this file for Apple Store heuristics after loading `agent-web-interface-guide`. Do not assume exact selectors remain stable across sessions; resolve live elements from the page before acting.

## URL Patterns

- Store home: `/store`
- Product listing: `/shop/buy-{product}`
- Product configurator: `/shop/buy-{product}/{model}`
- Bag: `/shop/bag`
- Checkout: `/shop/checkout`

## Common Flow Shape

Apple purchase flows are usually sequential. Later choices often remain disabled until earlier choices are selected.

Typical order:

1. Select model or base configuration
2. Select color
3. Select storage or memory
4. Select carrier or connectivity options when applicable
5. Select trade-in or no trade-in
6. Select AppleCare option or no coverage
7. Add to bag
8. Review optional accessories page
9. Open bag and verify contents

## Page Heuristics

- Store landing pages often expose direct `Buy` links for each product family.
- Product grids usually show a product heading, a price text node like `From $...`, and a `Buy` link.
- Configurator choices usually surface as radio groups.
- Bag controls may render as links, buttons, or comboboxes depending on the page and experiment bucket. Derive them live.

## What To Verify At Each Step

- The newly selected option is marked selected or checked.
- The next section becomes enabled after the prerequisite selection.
- The configured price updates when storage, memory, or purchase option changes.
- The add-to-bag control becomes enabled before clicking.

## Common Optional Gates

- Trade-in prompts: choose explicit no-trade-in when the user did not ask for trade-in.
- AppleCare prompts: choose explicit no-coverage when the user did not ask for coverage.
- Accessory upsells: Apple often inserts a post-add accessory page with a `Review Bag` button.

## Bag Verification

Confirm:

- Product name
- Full configuration
- Quantity
- Unit price
- Bag total

Do not infer quantity from total alone when multiple items may already be in the bag. Read the quantity control directly if present.

## Common Failure Modes

- Add-to-bag disabled because a required radio group remains unanswered
- Option unavailable or incompatible with a previous choice
- Price lagging behind selection because the page has not re-rendered yet
- Existing bag contents making totals misleading
- Accessory interstitial mistaken for final confirmation
