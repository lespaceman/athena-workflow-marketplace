---
name: fix-flaky-tests
description: >
  This skill should be used when a Robot Framework test (Browser library) is failing, flaky,
  timing out, or behaving inconsistently. It provides structured root cause analysis for:
  stabilizing intermittent tests, debugging timeouts, fixing race conditions, investigating
  local-vs-CI divergence, and running repeated stability checks.
  IMPORTANT: If running tests with repeated runs, retries, or pabot loops to check stability,
  STOP and load this skill first — it has structured root cause analysis that prevents
  brute-force approaches. Triggers: "stabilize", "intermittent", "flaky", "keeps failing",
  "fails in CI", "timeout on", "race condition", "run N times to check stability",
  "verify Robot tests are stable".
  NOT for writing new tests (use write-robot-code) or analyzing setup (use analyze-test-codebase).
allowed-tools: Read Write Edit Bash Glob Grep Task
---

# Fix Flaky Tests

Systematically diagnose and fix intermittent Robot Framework test failures using root cause analysis. A flaky test is worse than no test — it trains teams to ignore failures.

## Input

Parse the test file path or test name from: $ARGUMENTS

If no argument provided, ask: "Which `.robot` file or test name is flaky?"

## Workflow

### Step 1: Reproduce and Classify

1. **Read the test file** to understand what it tests and how
2. **Run the test multiple times** to observe the failure pattern:
   ```bash
   for i in 1 2 3 4 5; do robot -d results/run-$i -t "<test name>" tests/<file>.robot; done
   ```
3. **Run in isolation** if it passed above — it may only fail with other tests:
   ```bash
   robot -d results tests/
   ```
4. **Classify the failure** into one of these root cause categories:

| Category | Symptoms |
|----------|----------|
| **Timing** | Timeout errors, "element not found", "not visible yet" |
| **State leakage** | Passes alone, fails when run with other tests |
| **Data dependency** | Fails when expected data doesn't exist or has changed |
| **Race condition** | Action fires before page is ready (hydration, animation) |
| **Locator fragility** | Element found but wrong one, or `>> nth=N` picks different element |
| **Environment** | Passes locally, fails in CI (viewport, speed, resources) |

### Step 2: Root Cause Analysis

Investigate based on the classification:

**Timing issues:**
- Look for assertions immediately after actions with no wait for the resulting state change
- Check if the test asserts before an API response arrives — search for missing `Wait For Response`
- Look for animations/transitions that affect element state (CSS transitions, skeleton screens)
- Check for `Sleep` being used as a "fix" — this is a symptom, not a cure
- Check whether the test needs a more specific readiness signal: targeted `Wait For Response`, a URL/state change, a loading indicator disappearing, a hydration marker becoming ready

**State leakage:**
- Run the failing test alone: `robot -d results -t "<test name>" tests/<file>.robot`
- Check if tests share mutable state: global variables, database rows, cookies, browser storage
- Look for missing cleanup in `[Teardown]` / `Suite Teardown`
- Check if persisted `storageState` bleeds between suites or contexts
- Check for test data created by one test that another test depends on

**Race conditions:**
- Identify the race: what two things are happening concurrently?
- Check for actions that fire before JavaScript hydration completes
- Look for optimistic UI updates that revert on API response
- Check for actions during navigation transitions (click during page load)
- Look for double-clicks or rapid interactions that trigger duplicate actions

**Locator fragility:**
- Navigate to the page in the browser and verify the locator currently matches the intended element
- Check if the locator matches multiple elements — `>> nth=N` is a smell
- Look for dynamically generated IDs, classes, or attributes
- Check for conditional rendering that changes element order or presence
- Verify locators against current DOM structure using `find` and `get_element`

**Environment issues:**
- Compare CI viewport size vs local — element may be off-screen in CI (check `New Context    viewport={...}`)
- Check for timezone-dependent assertions (dates, timestamps)
- Check for locale-dependent formatting (numbers, currency)
- Check if CI has slower network/CPU affecting timing
- Look for third-party scripts (analytics, chat widgets) that load differently in CI

### Step 3: Apply the Correct Fix

Use the right fix pattern for the diagnosed root cause. **Never apply a fix without understanding the cause.** See [references/fix-patterns.md](references/fix-patterns.md) for full code examples.

| Category | Principle |
|----------|-----------|
| **Timing** | Replace `Sleep` with event-driven waits (`Wait For Response`, `Wait For Elements State`, auto-retrying Browser assertions) |
| **State isolation** | Unique data per test, API-based reset in `Test Setup`, no shared mutable state |
| **Race condition** | Use `Promise To` + `Wait For` for action + expected response; wait for hydration markers before interaction |
| **Locator** | Scope locators to containers with `>>`; avoid `>> nth=` and position-dependent selectors |
| **Environment** | Explicit viewport via `New Context`, timezone-agnostic assertions, block interfering third-party scripts via `Route URL    ... Abort` |

### Step 4: Verify the Fix

1. **Run the test 5+ times** to confirm stability:
   ```bash
   for i in 1 2 3 4 5; do robot -d results/run-$i -t "<test name>" tests/<file>.robot || break; done
   ```
2. **Run with the full suite** to verify no state leakage:
   ```bash
   robot -d results tests/
   ```
3. If still flaky → return to Step 2 with the new failure output. The initial classification may have been wrong.
4. **Maximum 3 fix-and-rerun cycles.** If the test is still flaky after 3 attempts, stop and report the diagnostic findings (root cause hypothesis, fixes attempted, remaining failure output) so the user can decide next steps. Do not continue looping.

### Step 5: Summarize

Report:
1. **Root cause** — what made the test flaky and why
2. **Fix applied** — what changed and why this fix addresses the root cause
3. **Verification** — how many consecutive runs passed
4. **Prevention** — what pattern to follow in future tests to avoid this class of flakiness

## Flakiness Checklist (Less Obvious Causes)

When the standard categories don't fit, check these:

- [ ] **Viewport size** — element off-screen in CI (smaller viewport in `New Context`)
- [ ] **Font rendering** — text matching fails due to font differences across OS
- [ ] **Timezone** — date/time assertions fail in different timezones
- [ ] **Locale** — number/currency formatting differs (1,000 vs 1.000)
- [ ] **Third-party scripts** — analytics/chat widgets change DOM or block clicks
- [ ] **Cookie consent banners** — overlay blocks click targets
- [ ] **Feature flags** — different features enabled in different environments
- [ ] **Database state** — shared test database with stale or conflicting data
- [ ] **Parallel execution** — suites interfere when run under `pabot`
- [ ] **Browser caching** — cached responses differ from fresh ones
- [ ] **Service workers** — intercepting requests differently than expected
- [ ] **Lazy loading** — elements not yet in DOM when test tries to interact

## Anti-Patterns: What is NOT a Fix

These mask the problem. Never apply them without a real fix:

| "Fix" | Why It's Wrong | Real Fix |
|-------|---------------|----------|
| `Sleep    3s` | Hides timing race, will break under load | Wait for the specific event |
| `>> nth=0` added | Hides locator ambiguity | Narrow the locator |
| Increased timeout to 30s | Hides missing wait or slow setup | Find what you're actually waiting for |
| Tagging with `skip` | Ignoring the problem | Diagnose and fix |
| `--rerunfailed` without fix | Masks real failures, wastes CI time | Fix the root cause, then keep rerun as a safety net |
| `force=True` | Bypasses actionability checks, hides overlapping elements or disabled state | Find and fix the actionability issue: wait for overlay to disappear, scroll element into view, wait for enabled state |
| `Run Keyword And Ignore Error` around an assertion | Test passes but doesn't verify anything | Fix the assertion |

## Multiple Flaky Tests

When a suite has several flaky tests:

1. **Triage first.** Run the full suite once and group failures by root cause category (timing, state leakage, etc.). Shared root causes (broken `Suite Setup`, leaking state) should be fixed once, not per-test.
2. **Fix shared infrastructure issues first.** A bad `Test Setup`, a leaking persisted context, or a missing cleanup can cause many tests to fail. One fix resolves many failures.
3. **Split independent fixes across subagents** when the fix scopes do not overlap (different suite files, no shared resources). Pass each subagent the file path, this diagnostic workflow, and the root cause classification table.
4. The 3 fix-and-rerun cycle limit applies **per test**, not globally.
