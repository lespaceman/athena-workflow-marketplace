---
name: plan-test-coverage
description: >
  Use before writing specs or Robot Framework test code to decide what E2E coverage is needed
  first. It scans existing `.robot` suites, inspects the target flow, finds coverage gaps,
  and produces a prioritized P0/P1/P2 plan with TC-IDs. Use it for requests like
  "what Robot tests do I need", "coverage gaps", or "what TC-IDs are missing". It does not
  write detailed specs or executable tests.
allowed-tools: Read Glob Grep Task
---

# Plan Test Coverage

Plan what Robot Framework E2E tests to write for a feature by analyzing existing coverage and, when browser tooling is available in the current context, doing a quick site inspection.

## Workflow

1. **Parse input** — extract the target URL and feature area from: $ARGUMENTS

2. **Check existing test coverage**:
   - Read `e2e-plan/conventions.yaml` if it exists so the plan reflects the project locator style, tag vocabulary, and parallel mode instead of inventing defaults
   - Search for existing suites related to the feature:
     ```
     Grep for feature keywords in tests/**/*.robot, resources/**/*.resource
     ```
   - Identify what's already covered and what's missing
   - Note existing TC-IDs for the feature area to avoid conflicts
   - Use the canonical TC-ID format `TC-<FEATURE>-<NNN>` for every planned test, regardless of category. Category belongs in the plan metadata, not the ID.

3. **Quick site inspection** (lightweight, not full exploration, optional if browser tooling is unavailable):
   - If the current context has browser tools, follow the `agent-web-interface-guide` skill's browsing patterns (orient before acting, use `list_pages` for session awareness, close only pages you opened)
   - Navigate to the URL in a dedicated page
   - Use `find` to catalog the main interactive elements
   - Use `get_form` or `get_field` if the page has forms worth covering
   - Identify the key user flows visible on the page
   - Close only the page you opened when done; do not rely on a session-wide close
   - If browser tooling is unavailable, infer flows from the URL, existing tests, route names, component names, and user-provided context, and record that the plan was produced without live inspection

4. **Identify test categories** — for the feature, determine tests needed across:
   - **Critical path** — core happy path that must never break
   - **Input validation** — form fields, required fields, format constraints
   - **Error states** — network errors, server errors, empty states
   - **Edge cases** — boundary values, special characters, concurrent actions
   - **Cross-feature** — interactions with other features (e.g., auth + checkout)
   - **Accessibility** — keyboard navigation, screen reader support, focus management
   - **Visual regression** — layout consistency, responsive breakpoints (375px, 768px, 1280px)
   - **Performance** — loading states, lazy loading, large data sets
   - **Network errors** — server 500s, timeouts, offline behavior

   Not all categories apply to every project. Include Accessibility, Visual Regression, and Cross-Browser sections only when the project has explicit requirements, tooling, or configuration for them. Omit them from the output plan if not relevant — a focused plan is more useful than a padded one.

5. **Prioritize** — rank tests by:
   - **P0 (Must have)**: Core user journey, auth flows, data corruption prevention. Blocks revenue/signups if broken.
   - **P1 (Should have)**: Input validation, common error paths, accessibility basics (keyboard navigation, form labels)
   - **P2 (Nice to have)**: Edge cases, visual regression, performance scenarios, cross-browser specifics, rare error paths

6. **Output test plan**:

```markdown
## Test Coverage Plan: <Feature>

**URL:** <url>
**Date:** <date>
**Existing coverage:** <N tests already exist / none>

### Already Covered
- TC-FEATURE-001: <description> (in `tests/feature.robot`)
- ...

### Proposed New Tests

#### P0 — Critical Path
| TC-ID | Description | Why Critical |
|-------|-------------|-------------|
| TC-FEATURE-001 | Happy path: user completes full flow | Core revenue path |

#### P1 — Validation & Errors
| TC-ID | Description | Why Important |
|-------|-------------|--------------|
| TC-FEATURE-002 | Submit with empty required fields | Common user error |

#### P2 — Edge Cases
| TC-ID | Description | Notes |
|-------|-------------|-------|
| TC-FEATURE-003 | Special characters in search input | Unicode handling |

#### Accessibility (include if project has accessibility requirements or WCAG compliance goals)
| TC-ID | Description | WCAG Criterion |
|-------|-------------|----------------|
| TC-FEATURE-004 | Keyboard-only navigation through flow | 2.1.1 Keyboard |
| TC-FEATURE-005 | Form errors announced to screen readers | 1.3.1 Info and Relationships |

#### Visual Regression (if project has visual testing setup)
| TC-ID | Description | Viewport |
|-------|-------------|----------|
| TC-FEATURE-006 | Layout consistency at mobile width | 375x812 |

#### Cross-Browser Matrix (include if project runs Browser library tests across multiple browsers)
| Browser | Priority | Reason |
|---------|----------|--------|
| Chromium | P0 | Primary target |
| Firefox | P1 | Second largest desktop share |
| WebKit/Safari | P1 | Required for iOS users |

### Recommended Order
1. Write P0 tests first (N tests)
2. Then P1 validation + accessibility basics (N tests)
3. P2 edge cases, visual regression, and performance as time allows

### Next Steps
- Invoke the `generate-test-cases` skill with the target URL and journey for detailed test specs
- Invoke the `write-robot-code` skill to implement the tests
```

## Example Usage

```
Claude Code: /plan-test-coverage https://myapp.com/checkout Checkout flow
Codex: $plan-test-coverage https://myapp.com/checkout Checkout flow

Claude Code: /plan-test-coverage https://myapp.com/login Authentication
Codex: $plan-test-coverage https://myapp.com/login Authentication
```
