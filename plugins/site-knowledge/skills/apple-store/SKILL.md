---
name: apple-store
description: >
  Use when automating apple.com, configuring iPhones or other Apple products, navigating the Apple Store, adding items to bag, or writing tests for Apple Store flows. Covers site structure, purchase flows, bag behavior, and Apple-specific interaction patterns. Load live selectors from the browser; use the bundled reference only for site heuristics and flow guidance.
allowed-tools: 
---

# Apple Store Automation Skill

This skill is a thin router. Use it together with `agent-web-interface-guide` for live browser work.

## Workflow

1. Load `agent-web-interface-guide` before using browser MCP tools.
2. Read [references/apple-store.md](references/apple-store.md) for Apple Store navigation, flow order, and bag heuristics.
3. Treat selectors in the reference as patterns, not guarantees. Derive the current `eid` and best live selector from the page with `find`, `get_form`, and `get_element`.
4. Re-check the page after each configuration step because Apple often enables downstream options only after prerequisites are selected.
5. Before any checkout or order placement step, confirm the final configuration and total with the user.
