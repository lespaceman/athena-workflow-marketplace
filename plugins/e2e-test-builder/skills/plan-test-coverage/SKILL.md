---
name: plan-test-coverage
description: >
  Use when the user wants to decide what E2E tests to write before exploring a site or writing code.
  Triggers: "plan test coverage", "what should I test", "create a test plan", "prioritize tests",
  "identify test gaps", "plan E2E tests for", "what tests are missing", "where are the coverage gaps",
  "which features need tests", "test priority for this feature", "what's not covered yet".
  This skill checks existing test files for coverage gaps, does a quick browser inspection of the target page,
  then produces a prioritized test plan with proposed TC-IDs organized by P0/P1/P2 priority.
  It does NOT write test specs or code — use generate-test-cases or write-e2e-tests for those.
user-invocable: true
argument-hint: <url> <feature or area to test>
allowed-tools:
  - Read
  - Glob
  - Grep
  - mcp__plugin_e2e-test-builder_agent-web-interface__ping
  - mcp__plugin_e2e-test-builder_agent-web-interface__navigate
  - mcp__plugin_e2e-test-builder_agent-web-interface__find_elements
  - mcp__plugin_e2e-test-builder_agent-web-interface__scroll_page
  - mcp__plugin_e2e-test-builder_agent-web-interface__close_session
---

# Plan Test Coverage

Plan what E2E tests to write for a feature by analyzing existing test coverage and doing a quick site inspection.

## Workflow

1. **Parse input** — extract the target URL and feature area from: $ARGUMENTS

2. **Check existing test coverage**:
   - Search for existing test files related to the feature:
     ```
     Grep for feature keywords in **/*.spec.ts, **/*.test.ts
     ```
   - Identify what's already covered and what's missing
   - Note existing TC-IDs for the feature area to avoid conflicts

3. **Quick site inspection** (lightweight, not full exploration):
   - Navigate to the URL
   - Use `find_elements` to catalog the main interactive elements
   - Identify the key user flows visible on the page
   - Close the browser session when done

4. **Identify test categories** — for the feature, determine tests needed across:
   - **Critical path** — core happy path that must never break
   - **Input validation** — form fields, required fields, format constraints
   - **Error states** — network errors, server errors, empty states
   - **Edge cases** — boundary values, special characters, concurrent actions
   - **Cross-feature** — interactions with other features (e.g., auth + checkout)

5. **Prioritize** — rank tests by:
   - **P0 (Must have)**: Core user journey, blocks revenue/signups if broken
   - **P1 (Should have)**: Important validation, common error paths
   - **P2 (Nice to have)**: Edge cases, accessibility, rare scenarios

6. **Output test plan**:

```markdown
## Test Coverage Plan: <Feature>

**URL:** <url>
**Date:** <date>
**Existing coverage:** <N tests already exist / none>

### Already Covered
- TC-FEATURE-001: <description> (in `tests/feature.spec.ts`)
- ...

### Proposed New Tests

#### P0 — Critical Path
| TC-ID | Description | Why Critical |
|-------|-------------|-------------|
| TC-FEATURE-010 | Happy path: user completes full flow | Core revenue path |

#### P1 — Validation & Errors
| TC-ID | Description | Why Important |
|-------|-------------|--------------|
| TC-FEATURE-020 | Submit with empty required fields | Common user error |

#### P2 — Edge Cases
| TC-ID | Description | Notes |
|-------|-------------|-------|
| TC-FEATURE-030 | Special characters in search input | Unicode handling |

### Recommended Order
1. Write P0 tests first (N tests)
2. Then P1 validation tests (N tests)
3. P2 edge cases as time allows

### Next Steps
- Run `/generate-test-cases <url> <journey>` for detailed test specs
- Run `/write-e2e-tests` to implement the tests
```

## Example Usage

```
/plan-test-coverage https://myapp.com/checkout Checkout flow
/plan-test-coverage https://myapp.com/login Authentication
```
