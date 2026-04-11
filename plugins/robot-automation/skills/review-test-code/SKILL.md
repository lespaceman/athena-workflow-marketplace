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
  after write-robot-code — catches wrong Browser-library dialect, brittle locators,
  post-action response waits, `force=True` misuse, `Sleep`, utility-class selectors,
  exact numeric assertions, missing teardown, parallel-unsafe mutations, hardcoded data,
  missing assertions, test coupling, and convention divergence. Review-only — does NOT
  rewrite tests, does NOT run tests. Use fix-flaky-tests for fixing, write-robot-code for rewriting.
allowed-tools: Read Glob Grep Task
---

# Review Test Code

Review Robot Framework test code for stability, correctness, and adherence to project conventions before final execution signoff.

## Input

Parse the test file path or directory from: $ARGUMENTS

If no argument is provided, search for recently modified `*.robot` files and review those.

## Workflow

### Step 1: Load Context
1. Read the `.robot` file or files under review
2. Read project conventions for comparison:
   - `robot.toml` or `pyproject.toml`
   - 2-3 existing `.robot` files not under review
   - `e2e-plan/conventions.yaml` if it exists, validating it against `plugins/robot-automation/schemas/conventions.schema.json`
3. Read the corresponding `test-cases/<feature>.md` file if it exists
4. Note the project's locator strategy, resource pattern, auth approach, tags, and runtime expectations

### Step 2: Run the Review Checklist

Track findings by severity:
- BLOCKER: will cause failures, false passes, or major convention breakage
- WARNING: likely to cause flakiness or maintenance burden
- SUGGESTION: useful improvement, not required for correctness

#### 2a. Locator Quality
| Check | What to Look For |
|-------|-----------------|
| Canonical Browser dialect | `Get Element By Role` / `Get Element By Label` / `Get Element By Placeholder` / `Get Element By Test Id`, or justified `css=` / `xpath=` / `text=` / `id=` |
| No fake selector engines | `role=`, `label=`, `placeholder=`, `alt=`, `title=`, `testid=` string prefixes are BLOCKERS unless hidden behind a deliberate custom keyword |
| No fragile positional selectors | `>> nth=0`, `>> nth=N` without documented justification |
| No dynamic IDs or classes | Generated hashes, UUID-like values, volatile classes |
| No utility framework classes | Tailwind, Bootstrap, or similar utility classes used as locators |
| Scoped where needed | Parent scoping or `>>` chaining used when ambiguity is possible |
| No exact long text matches | Prefer regex or shorter stable phrases |

When a locator appears suspicious, delegate a live-site spot-check to a subagent with browser access.

#### 2b. Waiting and Timing
| Check | What to Look For |
|-------|-----------------|
| No `Sleep` | Arbitrary delays masking timing issues |
| Proper action-response waits | `Promise To    Wait For Response` attached before the triggering action |
| Auto-retrying assertions used | Browser-library retrying assertions instead of one-shot snapshots where timing matters |
| Reasonable explicit timeouts | Custom timeouts justified by the flow |
| No custom network-idle logic | Prefer specific waits over vague “all network done” patterns |

#### 2c. Assertions
| Check | What to Look For |
|-------|-----------------|
| Every test has assertions | No action-only tests |
| Assertions test user outcomes | Visible text, URL, element states, expected errors |
| Assertions are specific | Concrete expected outcome, not just “visible” when richer verification is available |
| Error paths have assertions | Error tests verify the error UI |
| No exact server-computed values | Use patterns, ranges, or seeded data |
| No swallowed assertions | `Run Keyword And Ignore Error` around assertions is a BLOCKER |

#### 2d. Isolation and Structure
| Check | What to Look For |
|-------|-----------------|
| No shared mutable state | Tests do not depend on order |
| Proper setup and teardown | Shared setup in `Suite Setup` / `Test Setup`, not duplicated everywhere |
| Clear flow | Arrange, Act, Assert structure |
| No test coupling | Test B does not rely on Test A |
| Auth handled correctly | Reused state or shared auth keyword, not UI login in every test |
| Unique data | Unique IDs or seeded API data |
| Parallel-safe | `pabot` tests assert on the specific created entity, not global counts |
| Cleanup present | Persistent test data gets cleaned up |

#### 2e. Convention Adherence
| Check | What to Look For |
|-------|-----------------|
| TC-ID in test name | `TC-<FEATURE>-<NNN> <description>` |
| File naming matches project | Same suite naming convention |
| Resource imports match project | Reuse project resources |
| `${BASE_URL}` used | No hardcoded domains |
| Resource pattern followed | Interactions in resources, outcomes in tests |
| Locator strategy matches project | Aligns with existing files and `conventions.yaml` |

#### 2f. TC-ID Traceability
If a spec exists:
- Verify every spec TC-ID implemented here is present
- Flag missing implementations
- Flag orphaned tests not present in the spec

#### 2g. Anti-Pattern Detection
Flag any instances of:
1. Fake selector prefixes such as `role=` or `label=`
2. Raw CSS or XPath where semantic Browser locators would work
3. `Sleep`
4. `>> nth=N` without justification
5. Exact long text matches
6. Login via UI in every test
7. UI clicks to set up test data
8. No error path tests in the suite
9. Hardcoded test data
10. Tests depending on execution order
11. `Run Keyword And Ignore Error` wrapping assertions
12. Missing assertions after actions
13. `force=True` without documented justification
14. Post-action `Wait For Response` without `Promise To`
15. Custom network-idle helpers
16. Utility-class selectors
17. Exact server-computed value assertions without seeded data

### Step 3: Produce the Review Report

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
- <How this code differs from established patterns or `conventions.yaml`>

## TC-ID Traceability
- **Implemented:** <count> / <total in spec>
- **Missing from implementation:** <list>
- **Orphaned:** <list>

## Summary
<2-3 sentences>
```

### Step 4: Verdict Rules
- PASS: no blockers, 2 or fewer warnings
- PASS WITH WARNINGS: no blockers, 3 or more warnings
- NEEDS REVISION: 1 or more blockers

## Principles
- Review-only
- Evidence over opinion
- Convention-first
- Spot-check suspicious locators against the live site
- Keep output bounded and actionable
