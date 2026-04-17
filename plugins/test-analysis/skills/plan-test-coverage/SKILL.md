---
name: plan-test-coverage
description: >
  Use before writing specs or executable tests to decide what coverage is needed first. This shared planning skill consumes exploration evidence, existing tests, and related artifacts to produce `e2e-plan/coverage-plan.md` with prioritized P0/P1/P2 coverage and TC-IDs. When `e2e-plan/exploratory-charter.md` exists, use it as optional risk-framing context; do not require it and do not let it replace grounded exploration evidence. Use it for requests like "what tests do I need", "coverage gaps", or "what TC-IDs are missing". It plans; it does not perform the canonical exploration step and it does not write executable tests.
allowed-tools: Read Write Glob Grep Task
---

# Plan Test Coverage

Plan what to test by consuming shared exploration evidence and existing coverage.

This skill may consume `e2e-plan/exploratory-charter.md` when it exists, but that file is optional
context. `e2e-plan/exploration-report.md` remains the canonical grounded-evidence artifact whenever
real product behavior is required.

## Calibrating planning depth

Match the planning effort to the request:

- **"What tests do I need for X?"** — Light plan. Focus on the top 2-3 risk areas, produce 8-15
  TC-IDs across P0 and P1 only. Skip P2 and optional categories.
- **"Design test coverage for X"** — Standard plan. Cover all relevant risk areas, produce 20-40
  TC-IDs with full P0/P1/P2 prioritization. Include accessibility and visual sections only when
  the project has explicit requirements for them.
- **"Comprehensive coverage for X"** — Deep plan. Cover every applicable category, produce 40+
  TC-IDs with full prioritization, cross-feature coverage, and explicit gap analysis.

When in doubt, start standard and ask: "I've drafted a coverage plan — want me to go deeper on any
area, or is this level right?"

## Workflow

1. **Parse input** — extract the target URL and feature area from: $ARGUMENTS

2. **Load the evidence base**:
   - Read `e2e-plan/exploration-report.md` when real product evidence is required for the target
     feature
   - Read `e2e-plan/exploratory-charter.md` when it exists and the feature came through the
     exploratory workflow
   - Read existing `test-cases/*.md` specs for the same feature
   - Search for existing automated coverage related to the feature
   - Note any missing artifact that blocks confident planning

   Treat the evidence sources differently:
   - `exploration-report.md` supplies observed behavior, selectors, copy, and blockers
   - `exploratory-charter.md` supplies mission, risk framing, and investigation focus
   - if they conflict, observed evidence wins over inferred or interview-based framing

3. **Check existing test coverage**:
   - Search for existing test files related to the feature:
     ```
     Grep for feature keywords in **/*.spec.ts, **/*.test.ts
     ```
   - Identify what's already covered and what's missing
   - Note existing TC-IDs for the feature area to avoid conflicts
   - Use the canonical TC-ID format `TC-<FEATURE>-<NNN>` for every planned test, regardless of category. Category belongs in the plan metadata, not the ID.

4. **Block when required exploration evidence is missing**:
   - If the target flow depends on real product behavior, validation copy, selector shape, or
     conditional UI and `e2e-plan/exploration-report.md` is missing or clearly stale, stop and run
     `explore-app`
   - Do not treat `e2e-plan/exploratory-charter.md` as a substitute for missing exploration
     evidence
   - Do not replace missing exploration with lightweight pseudo-exploration
   - If you can still produce a partial plan from repo evidence alone, label the plan as partial and
     list the exact unknowns

5. **Identify test categories** — for the feature, determine tests needed across:
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

6. **Prioritize** — rank tests by:
   - **P0 (Must have)**: Core user journey, auth flows, data corruption prevention. Blocks revenue/signups if broken.
   - **P1 (Should have)**: Input validation, common error paths, accessibility basics (keyboard navigation, form labels)
   - **P2 (Nice to have)**: Edge cases, visual regression, performance scenarios, cross-browser specifics, rare error paths

   If an exploratory charter is available, use it to sharpen final prioritization and ordering:
   - pull candidate focus areas from the charter's risk hypotheses and investigation order
   - convert charter exploration gaps into explicit coverage gaps or blockers
   - keep the final test descriptions anchored in observed behavior from the exploration report

7. **Write `e2e-plan/coverage-plan.md`**:

```markdown
## Test Coverage Plan: <Feature>

**URL:** <url>
**Date:** <date>
**Evidence basis:** exploration-report | exploration-report + exploratory-charter | repo-only | mixed
**Existing coverage:** <N tests already exist / none>
**Status:** COMPLETE | PARTIAL | BLOCKED

### Already Covered
- TC-FEATURE-001: <description> (in `tests/feature.spec.ts`)
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

#### Cross-Browser Matrix (include if project runs tests across multiple browsers)
| Browser | Priority | Reason |
|---------|----------|--------|
| Chromium | P0 | Primary target |
| Firefox | P1 | Second largest desktop share |
| WebKit/Safari | P1 | Required for iOS users |

### Evidence Gaps / Blockers
- <missing exploration detail or blocker, or "None">

### Exploratory Inputs Applied (include only when `e2e-plan/exploratory-charter.md` was used)
- <risk hypothesis or mission statement that changed prioritization>
- <exploration gap that remains open and constrains planning>

### Recommended Order
1. Write P0 tests first (N tests)
2. Then P1 validation + accessibility basics (N tests)
3. P2 edge cases, visual regression, and performance as time allows

### Next Steps
- Invoke `generate-test-cases` with this plan and the exploration report
- Hand off the reviewed spec to the execution-layer plugin
```

## Quality bar

- Treat `exploratory-charter.md` as optional amplification, not a prerequisite.
- Keep observed evidence and inferred risk framing distinguishable in the plan.
- Own the final P0/P1/P2 prioritization here, even when the exploratory charter provided earlier
  investigation ordering.
- If a charter exists, let it improve priority ordering rather than duplicate the whole document.
- Do not silently promote interview-only or inferred concerns over contradictory observed evidence.

## Example Usage

```
/plan-test-coverage https://myapp.com/checkout Checkout flow

/plan-test-coverage https://myapp.com/login Authentication
```
