---
name: amazon
description: >
  Use when automating amazon.com, searching for products, adding items to cart, browsing deals,
  navigating product pages, or writing tests for Amazon shopping flows. Covers site structure,
  element patterns, search workflows, buying options, and common issues.
user-invocable: false
---

# Amazon Automation Skill

This skill provides patterns and knowledge for automating interactions with amazon.com.

## Site Structure

### Main Sections
- **Home**: Landing page with deals, recommendations, carousels
- **Search Results**: Product grid with filters sidebar
- **Product Detail**: Full product page with buying options
- **Cart**: Shopping cart with checkout flow
- **Today's Deals**: Daily promotions and lightning deals
- **Account**: Orders, lists, settings (requires sign-in)

### URL Patterns
- Home: `https://www.amazon.com`
- Search results: `https://www.amazon.com/s?k=<query>`
- Product detail: `https://www.amazon.com/<product-slug>/dp/<ASIN>`
- Cart: `https://www.amazon.com/gp/cart/view.html`
- Deals: `https://www.amazon.com/gp/goldbox`
- Orders: `https://www.amazon.com/gp/css/order-history`

## Element Patterns

### Search Bar

| Element | Selector |
|---------|----------|
| Search input | kind: "textbox", label: "Search Amazon" |
| Department dropdown | kind: "combobox", label: "Search in" |
| Search button | kind: "button", label: "Go" |
| Autocomplete suggestions | Appear as rows after typing; not directly findable by kind — press Enter or click suggestion text |

### Navigation Header

| Element | Selector |
|---------|----------|
| Amazon logo | kind: "link", label: "Amazon" |
| Cart icon | kind: "link", label contains "Cart" |
| Account menu | kind: "link", label contains "Account & Lists" |
| Orders link | kind: "link", label contains "Returns & Orders" |
| Deliver to | kind: "button", label contains "Deliver to" |
| All menu | kind: "button", label contains "All Categories Menu" |

### Search Results Page

| Element | Selector |
|---------|----------|
| Result count | Text like "1-16 of over X results" in main region |
| Product links | kind: "link" in region: "main", text contains product title |
| Rating stars | kind: "button", label contains "out of 5 stars" |
| Review count | kind: "link", label contains "ratings" |
| Price | kind: "link", label contains price (e.g., "INR" or "$") |
| Sort dropdown | kind: "combobox", label: "Sort by:" in region: "form" |
| Pagination | kind: "button", label: "Go to page N" |
| Quick filters | kind: "link", label: "Apply ... filter" in region: "main" |
| Related searches | kind: "link" at bottom of results with alternative queries |
| Quick Add to Cart | kind: "button", label: "Add to cart" in region: "form" (only for some products) |

### Product Detail Page

| Element | Selector |
|---------|----------|
| Product title | Main heading on page |
| Price | Displayed prominently near title |
| Add to Cart | kind: "button", label: "Add to Cart" (may be absent — see Buying Options) |
| Buy Now | kind: "button", label: "Buy Now" |
| Quantity selector | kind: "combobox" near Add to Cart |
| Buying options | kind: "link", label: "See All Buying Options" in region: "form" |
| Add to List | kind: "link", label: "Add to List" in region: "form" |
| About this item | kind: "link", label: "About this item" in region: "nav" |
| Breadcrumbs | kind: "link" chain near top (e.g., "Video Games" > "PlayStation 5") |
| Seller info | kind: "link", seller name under buying options |

### Buying Options Panel (Third-Party Sellers)

When a product has no direct "Add to Cart" button (common for high-demand items), click "See All Buying Options" to open a modal:

| Element | Selector |
|---------|----------|
| Close button | kind: "button", label: "Close" (focused on open) |
| Filter button | kind: "button", label: "Filter" |
| Seller Add to Cart | kind: "button", label: "Add to Cart from seller <name> and price <amount>" in region: "form" |
| Seller name link | kind: "link", seller name text (opens seller profile) |
| Recommendations | kind: "link", related product suggestions below offers |

### Cart Page

| Element | Selector |
|---------|----------|
| Product link | kind: "link", product title in region: "main" |
| Proceed to checkout | kind: "button", label contains "Proceed to checkout" in region: "form" |
| Go to Cart | kind: "link", label: "Go to Cart" in region: "main" |
| Sign in prompt | kind: "link", label contains "sign in" in region: "main" |
| Suggested add-ons | kind: "button", label: "Add to cart" for gift cards and related items in region: "form" |

## Search Workflow

### Basic Product Search
1. Find search input: kind "textbox", label "Search Amazon"
2. Type product name (use `clear: true` to replace any existing text)
3. Autocomplete suggestions appear as rows — they are not directly findable by `find_elements`
4. Press Enter to submit search, or wait and try clicking a suggestion
5. Results page loads with product grid

### Refining Search
- Use related search links at bottom of results (e.g., "ps5 pro console" narrows from "PS5 Pro")
- Use filter links in sidebar (brand, rating, seller, price range)
- Use sort dropdown to reorder results
- Pagination buttons to browse more results

### Search Tips
- **Be specific**: "playstation 5 pro console 2tb" yields better results than "PS5 Pro"
- **Use related searches**: Amazon shows refined query links below results that narrow to the exact product
- **First result may not match**: Amazon often shows sponsored or competing products first (e.g., Xbox in PS5 results)
- **Check "Overall Pick"**: Amazon marks recommended products with an "Overall Pick" badge

## Add to Cart Workflow

### Standard Flow (Direct Add to Cart)
1. Navigate to product detail page
2. Find "Add to Cart" button (kind: "button")
3. Click Add to Cart
4. Redirected to cart page with confirmation

### Third-Party Seller Flow (No Direct Add to Cart)
1. Navigate to product detail page
2. No "Add to Cart" button visible — find "See All Buying Options" link in region: "form"
3. Click "See All Buying Options" — modal opens with seller list
4. Modal shows sellers sorted by price with individual "Add to Cart" buttons
5. Each button label includes seller name and price: `"Add to Cart from seller <name> and price <amount>"`
6. Click the desired seller's Add to Cart button
7. Redirected to cart page with product added

### Cart Confirmation
After adding to cart, Amazon redirects to a confirmation/cart page showing:
- Product name as a link in region: "main"
- "Proceed to checkout" button in region: "form"
- "Go to Cart" link for reviewing items
- Suggested add-ons (gift cards, accessories)
- Sign-in prompt if not authenticated

## Modal Handling

### Cookie/Region Prompt
- **Trigger**: First visit or location mismatch
- **Element**: Link like "Click here to go to amazon.in" or country selector
- **Action**: Ignore or dismiss — does not block interaction

### Sign-In Prompt
- **Trigger**: Attempting checkout, adding to list, or viewing order history
- **Element**: kind: "link", label contains "sign in" or "Sign in"
- **Action**: Click to authenticate, or continue as guest where possible

### Buying Options Modal
- **Trigger**: Clicking "See All Buying Options"
- **Element**: Overlay with Close button, seller list, and Add to Cart buttons
- **Action**: Select a seller and click their Add to Cart button
- **Close**: kind: "button", label: "Close" (auto-focused on open)

## Data Extraction

### From Search Results
For each product listing extract:
- Title: Product name/description (from link text)
- Price: Dollar or currency amount
- Rating: "X.X out of 5 stars" from button label
- Reviews: Count from link label (e.g., "1,719 ratings")
- Platform/Brand: e.g., "PlayStation 5", "Xbox"
- Badge: "Overall Pick", "Best Seller", "Climate Pledge Friendly"
- Offers: "(N used & new offers)" link

### From Product Detail Page
- Full title
- Price and price history
- Availability and shipping estimate
- Seller name and fulfillment method
- Rating and review count
- Feature bullets
- Product images
- Breadcrumb category path

### From Cart Page
- Product name and configuration
- Quantity
- Price per item
- Subtotal
- Suggested add-on products

## Best Practices

1. **Search specifically**: Use detailed product names to get relevant results faster
2. **Check for "See All Buying Options"**: High-demand products (consoles, GPUs) often lack a direct Add to Cart button — the buying options panel has multiple sellers
3. **Verify the correct product**: Amazon search results mix sponsored ads, competing products, and accessories — always verify the product title matches what you want
4. **Use related search links**: The links below search results (e.g., "ps5 pro console") narrow results significantly
5. **Handle region/currency**: Amazon may show prices in local currency (INR, EUR, etc.) based on detected location
6. **Scroll for results**: Some elements are below the fold — use `scroll_page` to find them
7. **Cart is guest-accessible**: Items can be added to cart without signing in, but checkout requires authentication
8. **Action tools return snapshots**: `navigate`, `click`, `type` already return fresh state — no need for `capture_snapshot` after interactions

## Common Issues

| Issue | Solution |
|-------|----------|
| No "Add to Cart" button | Product sold by third-party sellers only — click "See All Buying Options" |
| Search returns wrong products | Use more specific query or click related search links to narrow results |
| Autocomplete not clickable | Suggestions appear as rows but may not have findable eids — press Enter to submit search instead |
| Price shown in wrong currency | Amazon detects location — currency is cosmetic and doesn't affect cart |
| Sponsored results mixed in | Look for "Sponsored" label; skip to organic results below |
| Product out of stock | Buying options panel will show fewer or no sellers; check alternative listings |
| Cart requires sign-in for checkout | Items stay in guest cart; sign-in needed only at checkout |
| Page elements not found after search | Results page is dense — use `find_elements` with `region: "main"` and `kind: "link"` filters |
