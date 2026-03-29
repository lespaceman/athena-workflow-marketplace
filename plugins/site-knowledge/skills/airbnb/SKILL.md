---
name: airbnb
description: >
  Use when automating airbnb.com, searching for stays, browsing experiences, creating wishlists,
  completing bookings, or writing tests for Airbnb flows. Covers site structure, search and booking
  heuristics, and common Airbnb interaction patterns. Load live selectors from the browser; use the
  bundled reference only for flow guidance and modal caveats.
---

# Airbnb Automation Skill

This skill is a thin router. Use it together with `agent-web-interface-guide` for live browser work.

## Workflow

1. Load `agent-web-interface-guide` before using browser MCP tools.
2. Read [references/airbnb.md](references/airbnb.md) for Airbnb search, listing, filter, and modal heuristics.
3. Treat all selectors in the reference as patterns, not guarantees. Derive the current `eid` and live selector from the page with `find`, `get_form`, and `get_element`.
4. Re-check page state after search, filter changes, or modal dismissal because Airbnb frequently re-renders key controls.
5. Before any booking or sign-in step, confirm dates, guest counts, listing identity, and total price with the user.
