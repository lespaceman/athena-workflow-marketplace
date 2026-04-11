---
name: review-test-code
description: >
  Quality review of Robot Framework test code before final execution signoff. This skill
  should be used when implementation review of executable `.robot` files is needed, not for
  diagnosis of runtime flakiness.
  Triggers: "review test code", "review Robot tests", "check test quality",
  "audit test implementation", "review my Robot tests before merging", "check .robot for issues",
  "review e2e tests", "code review Robot Framework", "are my tests stable",
  "check for brittle locators", "review before running tests". Quality gate
  after write-robot-code — catches brittle locators, `force=True` misuse, `Sleep`, utility-class
  selectors, exact numeric assertions, missing teardown, parallel-unsafe mutations (pabot),
  hardcoded data, missing assertions, test coupling, and convention divergence. Review-only — does
  NOT rewrite tests, does NOT run tests. Use fix-flaky-tests for fixing, write-robot-code for
  rewriting.
allowed-tools: Read Glob Grep Task
---

# Review Test Code

Review Robot Framework test code (Browser library) for stability, correctness, and adherence to project conventions before final execution signoff. This is a quality gate — catch structural issues in code before running tests, not after flaky failures.

## Input

Parse the test file path or directory from: $ARGUMENTS

If no argument provided, search for recently modified `*.robot` files and review those.

## Workflow

### Step 1: Load Context

1. Read the `.robot` file(s) to review
2. Read project conventions for comparison:
   - `robot.toml` / `pyproject.toml` — extract `outputdir`, default tags, listeners
   - 2-3 existing `.robot` files (not the ones under review) to establish the project's conventions
   - `e2e-plan/conventions.md` if it exists
3. Read the corresponding test case spec (`test-cases/<feature>.md`) if it exists — needed for traceability check
4. Note the project's locator strategy, resource patterns, auth approach, and naming conventions

### Step 2: Run the Review Checklist

Evaluate the test code against each criterion. Track findings by severity:

- **BLOCKER** — will cause test failures or false passes (missing assertions, wrong locators, broken isolation, hidden `Run Keyword And Ignore Error`)
- **WARNING** — will cause flakiness or maintenance burden (brittle locators, `Sleep`, poor structure)
- **SUGGESTION** — style or convention improvement (naming, organization, minor readability)

#### 2a. Locator Quality

| Check | What to Look For |
|-------|-----------------|
| Semantic Browser locators preferred | `role=`, `label=`, `[data-testid=]` over `css=` / `xpath=` |
| No fragile positional selectors | `>> nth=0`, `>> nth=N` without documented justification |
| No dynamic IDs or classes | Selectors containing generated hashes, UUIDs, or auto-incremented values |
| No utility framework classes | Locators must not contain Tailwind (`rounded-lg`, `flex`, `bg-*`), Bootstrap (`btn-primary`, `col-md-*`), or similar utility classes — these are styling, not identity |
| Scoped to containers | Locators chained with `>>` to `main`, `nav`, `[role="dialog"]` where needed |
| No exact long text matches | Use `text=/regex/i` with key words instead of full marketing copy |

When a locator appears suspicious, delegate verification to a subagent (Task tool): instruct it to open the target URL, locate the element using the browser MCP tools (`find`, `get_element`), and report back whether the element exists and is unique.

#### 2b. Waiting and Timing

| Check | What to Look For |
|-------|-----------------|
| No `Sleep` | Arbitrary sleeps mask real timing issues |
| Proper action-response waits | `Wait For Response` before asserting API-dependent UI |
| Auto-retrying assertions used | `Get Text    <loc>    contains    <value>` not `Should Contain    ${text}    <value>` after a one-shot `Get Text` |
| Reasonable explicit timeouts | Custom timeouts (`timeout=10s`) have a comment explaining why |
| No `networkidle`-style waits | Browser library has no exact equivalent, but any custom keyword waiting on "all network done" is fragile — prefer specific `Wait For Response` |

#### 2c. Assertions

| Check | What to Look For |
|-------|-----------------|
| Every test has assertions | No test blocks without a `Get *` / `Should *` assertion |
| Assertions test user outcomes | Visible text, URL changes, element states — not internal state or CSS classes |
| Assertions are specific | `Get Text    role=heading    ==    Welcome, John` not just `visible` |
| Error paths have assertions | Error scenario tests verify the error message, not just that "something happened" |
| No exact server-computed values | Dashboard counters, totals, and aggregates must not assert exact numbers — use patterns, ranges, or seed data first |
| No `Run Keyword And Ignore Error` around assertions | This silently swallows failures and produces green runs that verify nothing — BLOCKER |

#### 2d. Test Isolation and Structure

| Check | What to Look For |
|-------|-----------------|
| No shared mutable state | Tests do not depend on execution order or modify shared `Set Global Variable` values |
| Proper setup/teardown | `Test Setup` / `Test Teardown` / `Suite Setup` for shared setup, not duplicated in each test |
| AAA structure | Clear Arrange → Act → Assert sections inside each test case |
| No test coupling | Test B does not depend on side effects from Test A |
| Auth handled correctly | Persisted context state or shared keyword, not UI login in every test (unless testing login itself) |
| Test data is unique | Uses `Get Time    epoch`, `Evaluate    time.time_ns()`, or unique IDs from API — not hardcoded shared data |
| Parallel-safe (if `pabot` is in use) | Tests that create data must not assert on unscoped lists or counts — filter assertions to the specific data created. If pabot is not used, note as SUGGESTION rather than WARNING |
| Data cleanup present | Tests that create persistent records (RequestsLibrary POST/PUT) must have corresponding teardown (`[Teardown]`, `Suite Teardown`, or listener cleanup) |

#### 2e. Convention Adherence

| Check | What to Look For |
|-------|-----------------|
| TC-ID in test name | Every test has `TC-<FEATURE>-<NNN> <description>` as the test case name |
| File naming matches project | Follows existing `*.robot` convention |
| Resource imports match project | Imports from project `resources/*.resource`, not inline keywords duplicating them |
| `${BASE_URL}` used | `Go To    ${BASE_URL}/` not `Go To    https://example.com/` |
| Resource pattern followed | Page-level interactions live in resources, tests contain assertions |
| Consistent locator strategy | Same locator approach as existing tests |

#### 2f. TC-ID Traceability

If a test case spec file exists for this feature:
- Verify every TC-ID from the spec has a corresponding test
- Flag TC-IDs in the spec with no implementation
- Flag tests with TC-IDs not present in the spec (orphaned tests)
- Note: not every spec TC-ID must be implemented — but missing ones should be acknowledged

#### 2g. Anti-Pattern Detection

Flag any instances of these known anti-patterns:
1. Raw CSS / XPath locators where semantic Browser locators would work
2. `Sleep` used as a fix
3. `>> nth=N` without justification
4. Exact long text matches (fragile to copy changes)
5. Login via UI in every test (should use persisted context state)
6. UI clicks to set up test data (should use RequestsLibrary)
7. No error path tests in the suite
8. Hardcoded test data
9. Tests depending on execution order
10. `Run Keyword And Ignore Error` wrapping assertions (silent failure)
11. Missing assertions after actions (action-only tests pass without verifying anything)
12. `force=True` on interactions without documented justification (masks actionability issues — overlapping elements, disabled state, not scrolled into view)
13. Custom "wait for network idle" keywords that break on long-polling, WebSockets, analytics beacons
14. Utility-class selectors (Tailwind `rounded-lg`, `flex`, Bootstrap `btn-primary`, `col-md-*`) — never use as locators
15. Asserting exact server-computed values (`Get Text    ...    ==    12450`) — use pattern matchers, ranges, or seed data

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

- **Review-only** — never modify test files; report findings for the author to act on
- **Evidence over opinion** — cite specific file paths, line numbers, and code snippets when flagging issues
- **Spot-check locators** — delegate to a subagent with browser access to verify 2-3 suspicious locators against the live site
- **Convention-first** — compare against the project's existing test patterns, not an abstract ideal
- **Bounded output** — the review should be actionable and finite, not a full rewrite specification
- **Severity matters** — a missing assertion or `Run Keyword And Ignore Error` swallowing failures is a blocker; a naming style preference is a suggestion

## Example Usage

```
Claude Code: /review-test-code tests/login.robot
Codex: $review-test-code tests/login.robot

Claude Code: /review-test-code tests/
Codex: $review-test-code tests/
```
