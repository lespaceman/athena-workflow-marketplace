---
name: review-test-code
description: >
  Quality review of Playwright test code before final execution signoff. This skill should be used when implementation review of executable Playwright tests is needed, not for diagnosis of runtime flakiness. Triggers: "review test code", "review Playwright tests", "check test quality", "audit test implementation", "review my tests before merging", "check test code for issues", "review e2e tests", "code review Playwright", "are my tests stable", "check for brittle selectors", "review before running tests". Quality gate after write-test-code — catches brittle selectors, force:true misuse, networkidle overuse, Tailwind utility class selectors, exact numeric assertions, missing teardown, parallel-unsafe mutations, hardcoded data, missing assertions, test coupling, and convention divergence. Review-only — does NOT rewrite tests, does NOT run tests. Use fix-flaky-tests for fixing, write-test-code for rewriting.
allowed-tools: Read Glob Grep Task
---

# Review Test Code

Review Playwright test code for stability, correctness, and adherence to project conventions before final execution signoff. This is a quality gate — catch structural issues in code before running tests, not after flaky failures.

**Execution context:** this review must run in a fresh subagent, not the agent that authored the code. The orchestrator enforces this via the Task tool; the skill documents the contract so a drifting caller can see they're breaking it. Self-review reliably misses the gaps the author anchored on — passing only the file path (not the authoring transcript) into a new Task call is the cheapest way to get an independent read.

## Input

Parse the test file path or directory from: $ARGUMENTS

If no argument provided, search for recently modified `*.spec.ts` or `*.test.ts` files and review those.

## Workflow

### Step 1: Load Context

1. Read the test file(s) to review
2. Read project conventions for comparison:
   - `playwright.config.ts` or `playwright.config.js` — extract `baseURL`, `testDir`, projects, timeouts, `fullyParallel`, `workers`
   - 2-3 existing test files (not the ones under review) to establish the project's conventions
   - `e2e-plan/conventions.md` if it exists
3. Read the corresponding test case spec (`test-cases/<feature>.md`) if it exists — needed for traceability check
4. Note the project's locator strategy, fixture patterns, auth approach, and naming conventions

### Step 2: Run the Review Checklist

Evaluate the test code against each criterion. Track findings by severity:

- **BLOCKER** — will cause test failures or false passes (missing assertions, wrong selectors, broken isolation)
- **WARNING** — will cause flakiness or maintenance burden (brittle selectors, arbitrary waits, poor structure)
- **SUGGESTION** — style or convention improvement (naming, organization, minor readability)

Treat evidence-sensitive workarounds separately from ordinary style issues:
- **BLOCKER** when `{ force: true }`, JavaScript-dispatched clicks, guessed coordinate clicks, page-wide text oracles, or broad CSS fallbacks are used without fresh browser evidence at the execution conditions or without explicit reviewer/operator acceptance.
- **WARNING** only when one of those patterns is present and the file or linked exploration artifact documents fresh evidence or explicit acceptance with rationale.
- If the real issue is uncertain DOM/viewport evidence rather than code quality, say so directly and recommend re-exploration instead of calling it generic flakiness.

#### 2a. Locator Quality

| Check | What to Look For |
|-------|-----------------|
| Semantic locators preferred | `getByRole`, `getByLabel`, `getByPlaceholder` over CSS selectors |
| No fragile positional selectors | `.first()`, `.nth()`, `.last()` without documented justification |
| No dynamic IDs or classes | Selectors containing generated hashes, UUIDs, or auto-incremented values |
| No utility framework classes | Selectors must not contain Tailwind (`rounded-lg`, `flex`, `bg-*`), Bootstrap (`btn-primary`, `col-md-*`), or similar utility classes — these are styling, not identity |
| Scoped to containers | Locators narrowed to `main`, `nav`, `[role="dialog"]` where needed |
| No exact long text matches | Use regex with key words instead of full marketing copy |

When a locator appears suspicious, delegate verification to a subagent (Task tool): instruct it to open the target URL, locate the element using the browser MCP tools (`find`, `get_element`), and report back whether the element exists and is unique.

Mandatory re-exploration triggers:
- execution viewport/layout is materially different from the explored viewport and the interaction is coordinate- or layout-sensitive
- selector uniqueness observed during exploration no longer holds
- visible labels or control text are absent, duplicated, or rendered outside the explored container
- the implementation resorts to `{ force: true }`, JavaScript clicks, coordinate clicks, page-wide text oracles, or broad CSS selectors because semantic selection failed

In those cases, report an evidence gap and require fresh browser evidence before signoff.

#### 2b. Waiting and Timing

| Check | What to Look For |
|-------|-----------------|
| No `waitForTimeout()` | Arbitrary sleeps mask real timing issues |
| Proper action-response waits | `waitForResponse` before asserting API-dependent UI |
| Auto-retrying assertions used | `await expect(el).toBeVisible()` not `expect(await el.isVisible()).toBe(true)` |
| Reasonable explicit timeouts | Custom timeouts (`{ timeout: 10000 }`) have a comment explaining why |
| No `networkidle` overuse | `networkidle` is fragile; prefer specific response waits |

#### 2c. Assertions

| Check | What to Look For |
|-------|-----------------|
| Every test has assertions | No test blocks without `expect()` calls |
| Assertions test user outcomes | Visible text, URL changes, element states — not internal state or CSS classes |
| Assertions are specific | `toHaveText('Welcome, John')` not just `toBeVisible()` |
| Error paths have assertions | Error scenario tests verify the error message, not just that "something happened" |
| No exact server-computed values | Dashboard counters, totals, and aggregates must not assert exact numbers — use patterns, ranges, or seed data first |
| No `toBeTruthy()` on locators | Use Playwright-specific matchers (`toBeVisible`, `toBeEnabled`, `toHaveText`) |
| **Action-vs-assertion balance** | For each TC that claims to verify behavior, verify the test actually triggers the action (click, type, navigate, submit) AND asserts the resulting state. A test that only asserts `toBeVisible()` on an element the test never clicked or interacted with is visibility coverage masquerading as functional coverage — **BLOCKER**. Example pattern to flag: `await expect(page.getByRole('button', { name: /save/i })).toBeVisible()` with no preceding `click()` or `fill()` in the same test. |

#### 2d. Test Isolation and Structure

| Check | What to Look For |
|-------|-----------------|
| No shared mutable state | Tests do not depend on execution order or modify shared variables |
| Proper setup/teardown | `beforeEach`/`afterEach` for shared setup, not duplicated in each test |
| AAA structure | Clear Arrange → Act → Assert sections (comments optional but structure required) |
| No test coupling | Test B does not depend on side effects from Test A |
| Auth handled correctly | `storageState` or fixture, not UI login in every test (unless testing login itself) |
| Test data is unique | Uses `Date.now()`, factories, or unique IDs — not hardcoded shared data |
| Parallel-safe (if `fullyParallel: true` or `workers` > 1 found in config) | Tests that create data must not assert on unscoped lists or counts — filter assertions to the specific data created. If parallelism is disabled, note as SUGGESTION rather than WARNING |
| Data cleanup present | Tests that create persistent records (API POST/PUT) must have corresponding teardown (`afterEach`, fixture cleanup, or `globalTeardown`) |

#### 2e. Convention Adherence

| Check | What to Look For |
|-------|-----------------|
| TC-ID in test title | Every test has `TC-<FEATURE>-<NNN>: Description` format |
| File naming matches project | Follows existing `*.spec.ts` or `*.test.ts` convention |
| Import style matches project | Imports from project fixtures file if one exists, not raw `@playwright/test` |
| baseURL used | `page.goto('/')` not `page.goto('https://example.com/')` |
| POM pattern followed (if used) | Page objects for interactions, tests for assertions |
| Consistent locator strategy | Same locator approach as existing tests |

#### 2f. TC-ID Traceability

If a test case spec file exists for this feature:
- Verify every TC-ID from the spec has a corresponding test
- Flag TC-IDs in the spec with no implementation
- Flag tests with TC-IDs not present in the spec (orphaned tests)
- Note: not every spec TC-ID must be implemented — but missing ones should be acknowledged

#### 2g. Anti-Pattern Detection

Flag any instances of these known anti-patterns:
1. Raw CSS selectors where semantic locators would work
2. `waitForTimeout()` used as a fix
3. `.first()` / `.nth()` without justification
4. Exact long text matches (fragile to copy changes)
5. Login via UI in every test (should use storageState)
6. UI clicks to set up test data (should use API)
7. No error path tests in the suite
8. Hardcoded test data
9. Tests depending on execution order
10. `expect(await el.isVisible()).toBe(true)` instead of `await expect(el).toBeVisible()`
11. Missing `await` on Playwright calls (easy to miss, causes silent failures)
12. `{ force: true }` on interactions without documented justification (masks actionability issues — overlapping elements, disabled state, not scrolled into view)
13. `waitForLoadState('networkidle')` as default wait strategy — breaks on long-polling, WebSockets, analytics beacons; use specific `waitForResponse` or UI assertions instead
14. CSS utility class selectors (Tailwind `rounded-lg`, `flex`, Bootstrap `btn-primary`, `col-md-*`) — styling classes are volatile, never use as selectors
15. Asserting exact server-computed values (`toHaveText('12450')`) — use pattern matchers, ranges, or seed data to control expected values
16. **Visibility masquerading as functional coverage** — `toBeVisible()` or `toHaveCount()` on elements the test never interacted with. A render check is not a behavior check. Either add the action (click, type, submit) that the test claims to verify, or recategorize the test honestly as a smoke/render check and cap its count.
17. JavaScript-dispatched click used to bypass Playwright actionability instead of fixing the UI state or locator
18. Coordinate click based on guessed geometry or an unexplained bounding-box offset
19. Page-wide text-presence/count oracle used as proof of a specific control state
20. Broad CSS selector substituted for a failed semantic locator without fresh browser evidence showing it is unique and stable

### Step 3: Produce the Review Report

Output a structured review with this format:

```markdown
# Test Code Review: <file or feature>

**Files reviewed:** <list>
**Total tests:** <count>
**Review date:** <date>

## Verdict: PASS | PASS WITH WARNINGS | NEEDS REVISION

## Blockers (<count>)
- **<file>:<line>** `<test name>`: <issue description>

## Warnings (<count>)
- **<file>:<line>** `<test name>`: <issue description>

## Suggestions (<count>)
- **<file>:<line>**: <issue description>

## Convention Divergences
- <How this code differs from the project's established patterns>

## TC-ID Traceability
- **Implemented:** <count> / <total in spec>
- **Missing from implementation:** <list of TC-IDs>
- **Orphaned (no spec):** <list of TC-IDs>

## Summary
<2-3 sentences on overall code quality and what to address before test execution>
```

### Step 4: Verdict Rules

- **PASS** — no blockers, 2 or fewer warnings. Proceed to test execution.
- **PASS WITH WARNINGS** — no blockers, 3+ warnings. Can proceed but should address warnings for long-term stability.
- **NEEDS REVISION** — 1+ blockers. Do not run tests expecting stable results until blockers are resolved.

## Principles

- **Fresh context** — this review itself runs in a subagent that did not author the code. If the caller is the same agent that wrote the tests, they're using the skill wrong — the orchestrator should dispatch this via the Task tool with only the test-file path and the spec path.
- **Review-only** — never modify test files; report findings for the author to act on
- **Evidence over opinion** — cite specific file paths, line numbers, and code snippets when flagging issues
- **Live-site selector spot-check** — when specific locators look suspicious, delegate a bounded check to a *second* subagent with browser access. This is sub-delegation for evidence; it does not replace the fresh-subagent-reviewer itself.
- **Convention-first** — compare against the project's existing test patterns, not an abstract ideal
- **Evidence-sensitive workarounds** — `{ force: true }`, JS clicks, guessed coordinate clicks, page-wide text/count oracles, and broad CSS fallbacks are blockers unless backed by fresh browser evidence, a documented platform limitation, or explicit acceptance
- **Bounded output** — the review should be actionable and finite, not a full rewrite specification
- **Severity matters** — a missing `await` is a blocker; a naming style preference is a suggestion

## Example Usage

```
/review-test-code tests/e2e/login.spec.ts

/review-test-code tests/e2e/
```
