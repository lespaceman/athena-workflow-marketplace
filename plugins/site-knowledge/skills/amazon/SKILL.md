---
name: amazon
description: >
  Use when automating amazon.com, searching for products, adding items to cart, browsing deals, navigating product pages, or writing tests for Amazon shopping flows. Covers site structure, search/buying heuristics, and common Amazon interaction patterns. Load live selectors from the browser; use the bundled reference only for flow guidance and site-specific caveats.
allowed-tools: 
---

# Amazon Automation Skill

This skill is a thin router. Use it together with `agent-web-interface-guide` for live browser work.

## Workflow

1. Load `agent-web-interface-guide` before using browser MCP tools.
2. Read [references/amazon.md](references/amazon.md) for Amazon search, product, cart, and modal heuristics.
3. Treat all selectors in the reference as starting patterns only. Derive the current `eid` and live selector from the page with `find`, `get_form`, and `get_element`.
4. Expect Amazon to vary by seller, region, stock state, and experiment bucket. Re-evaluate the flow after every navigation or modal open.
5. Before checkout or sign-in, confirm the intended product, seller, quantity, and total with the user.
