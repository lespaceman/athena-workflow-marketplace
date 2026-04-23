---
name: fix-flaky-tests
description: >
  This skill should be used when a Playwright test is failing, flaky, timing out, or behaving inconsistently. It provides structured root cause analysis for: stabilizing intermittent tests, debugging timeouts ("Test timeout of 30000ms exceeded"), fixing race conditions, investigating local-vs-CI divergence, running repeated stability checks (--repeat-each). IMPORTANT: If running tests with --repeat-each, --retries, or multiple times to check stability, STOP and load this skill first — it has structured root cause analysis that prevents brute-force approaches. Triggers: "stabilize", "intermittent", "flaky", "keeps failing", "fails in CI", "timeout on", "race condition", "run N times to check stability", "verify tests are stable". NOT for writing new tests (use write-test-code) or analyzing setup (use analyze-test-codebase).
allowed-tools: Read Write Edit Bash Glob Grep Task
---

# Fix Flaky Tests

Systematically diagnose and fix intermittent Playwright test failures using root cause analysis. A flaky test is worse than no test — it trains teams to ignore failures.

## Input

Parse the test file path or test name from: $ARGUMENTS

If no argument provided, ask: "Which test file or test name is flaky?"

## Workflow

### Step 1: Reproduce and Classify

1. **Read the test file** to understand what it tests and how
2. **Run the test multiple times** to observe the failure pattern:
   ```bash
   npx playwright test <file> --repeat-each=5 --reporter=list 2>&1
   ```
3. **Run in isolation** if it passed above — it may only fail with other tests:
   ```bash
   npx playwright test --reporter=list 2>&1
   ```
4. **Classify the failure** into one of these root cause categories:

| Category | Symptoms |
|----------|----------|
| **Timing** | Timeout errors, "element not found", "not visible yet" |
| **State leakage** | Passes alone, fails when run with other tests |
| **Data dependency** | Fails when expected data doesn't exist or has changed |
| **Race condition** | Action fires before page is ready (hydration, animation) |
| **Selector fragility** | Element found but wrong one, or `.first()` picks different element |
| **Environment** | Passes locally, fails in CI (viewport, speed, resources) |
| **Evidence gap** | Current DOM, viewport, or label behavior no longer matches exploration, so the next fix would be guesswork |

### Step 2: Root Cause Analysis

Investigate based on the classification:

**Timing issues:**
- Look for assertions immediately after actions with no wait for the resulting state change
- Check if the test asserts before an API response arrives — search for missing `waitForResponse`
- Look for animations/transitions that affect element state (CSS transitions, skeleton screens)
- Check for `waitForTimeout` being used as a "fix" — this is a symptom, not a cure
- Check whether the test needs a more specific readiness signal: targeted `waitForResponse`, a URL/assertion change, a loading indicator disappearing, or a hydration marker becoming ready

**State leakage:**
- Run the failing test alone: `npx playwright test --grep "<test name>"`
- Check if tests share mutable state: global variables, database rows, cookies, localStorage
- Look for missing cleanup in `afterEach`/`afterAll`
- Check if `storageState` bleeds between tests or test files
- Check for test data created by one test that another test depends on

**Race conditions:**
- Identify the race: what two things are happening concurrently?
- Check for click handlers that fire before JavaScript hydration completes
- Look for optimistic UI updates that revert on API response
- Check for actions during navigation transitions (click during page load)
- Look for double-clicks or rapid interactions that trigger duplicate actions

**Selector fragility:**
- Navigate to the page in the browser and verify the selector currently matches the intended element
- Check if the selector matches multiple elements — `.first()` or `.nth()` is a smell
- Look for dynamically generated IDs, classes, or attributes
- Check for conditional rendering that changes element order or presence
- Verify locators against current DOM structure using `find` and `get_element`

**Environment issues:**
- Compare CI viewport size vs local — element may be off-screen in CI
- Check for timezone-dependent assertions (dates, timestamps)
- Check for locale-dependent formatting (numbers, currency)
- Check if CI has slower network/CPU affecting timing
- Look for third-party scripts (analytics, chat widgets) that load differently in CI

**Evidence gaps:**
- Treat this as missing evidence, not ordinary flakiness
- Re-explore before changing code when the execution viewport differs materially from exploration and the interaction is coordinate- or layout-sensitive
- Re-explore when selector uniqueness no longer holds, labels move outside the explored container, or semantic locators stop matching the observed DOM
- Re-explore before adopting `{ force: true }`, JavaScript-dispatched clicks, coordinate clicks, page-wide text oracles, or broad CSS fallbacks because semantic selection failed
- If browser confirmation at the actual execution state is missing, stop rerunning and refresh evidence first

### Step 3: Apply the Correct Fix

Use the right fix pattern for the diagnosed root cause. **Never apply a fix without understanding the cause.** See [references/fix-patterns.md](references/fix-patterns.md) for full code examples.

| Category | Principle |
|----------|-----------|
| **Timing** | Replace sleeps with event-driven waits (`waitForResponse`, auto-retrying assertions) |
| **State isolation** | Unique data per test, API-based reset in `beforeEach`, no shared mutable state |
| **Race condition** | Use `Promise.all` for action + expected response; wait for hydration before interaction |
| **Selector** | Scope locators to containers with unique content; avoid `.first()` and position-dependent selectors |
| **Environment** | Explicit viewport, timezone-agnostic assertions, block interfering third-party scripts |
| **Evidence gap** | Refresh exploration/browser evidence first; do not guess with workaround-heavy code changes |

Evidence-sensitive workarounds are not normal fixes. Treat these as last-resort options that require fresh browser evidence or explicit reviewer/operator acceptance:
- `{ force: true }`
- JavaScript-dispatched clicks
- coordinate clicks from guessed bounding boxes
- page-wide text-count or text-presence oracles used as functional proof
- broad CSS selectors adopted only because semantic locators failed

### Step 4: Verify the Fix

1. **Run the test 5+ times** to confirm stability:
   ```bash
   npx playwright test <file> --repeat-each=5 --reporter=list 2>&1
   ```
2. **Run with the full test suite** to verify no state leakage:
   ```bash
   npx playwright test --reporter=list 2>&1
   ```
3. If still flaky → return to Step 2 with the new failure output. The initial classification may have been wrong.
4. **Use judgment, not a fixed cap.** Continue only while each cycle adds something real: a new hypothesis, a concrete fix, or materially different failure evidence. Stop when the failure is not moving, the next rerun would repeat the same experiment, or the blocker is outside the test code and must be surfaced explicitly.

### Step 5: Summarize

Report:
1. **Root cause** — what made the test flaky and why
2. **Fix applied** — what changed and why this fix addresses the root cause
3. **Verification** — how many consecutive runs passed
4. **Prevention** — what pattern to follow in future tests to avoid this class of flakiness

## Flakiness Checklist (Less Obvious Causes)

When the standard categories don't fit, check these:

- [ ] **Viewport size** — element off-screen in CI (smaller viewport)
- [ ] **Font rendering** — text matching fails due to font differences across OS
- [ ] **Timezone** — date/time assertions fail in different timezones
- [ ] **Locale** — number/currency formatting differs (1,000 vs 1.000)
- [ ] **Third-party scripts** — analytics/chat widgets change DOM or block clicks
- [ ] **Cookie consent banners** — overlay blocks click targets
- [ ] **Feature flags** — different features enabled in different environments
- [ ] **Database state** — shared test database with stale or conflicting data
- [ ] **Parallel execution** — tests interfere when run in parallel workers
- [ ] **Browser caching** — cached responses differ from fresh ones
- [ ] **Service workers** — intercepting requests differently than expected
- [ ] **Lazy loading** — elements not yet in DOM when test tries to interact

## Anti-Patterns: What is NOT a Fix

These mask the problem. Never apply them without a real fix:

| "Fix" | Why It's Wrong | Real Fix |
|-------|---------------|----------|
| `waitForTimeout(3000)` | Hides timing race, will break under load | Wait for the specific event |
| `.first()` added | Hides selector ambiguity | Narrow the selector |
| Increased timeout to 30s | Hides missing wait or slow setup | Find what you're actually waiting for |
| `test.skip()` | Ignoring the problem | Diagnose and fix |
| `retries: 3` without fix | Masks real failures, wastes CI time | Fix the root cause, then keep retries as safety net |
| `{ force: true }` | Bypasses actionability checks, hides overlapping elements or disabled state | Find and fix the actionability issue: wait for overlay to disappear, scroll element into view, or wait for enabled state |
| `locator.evaluate(() => el.click())` / JS click | Bypasses the browser's real interaction model and can hide overlay, timing, or disabled-state issues | Re-explore the live DOM and restore a real user interaction path |
| Coordinate click from a guessed box | Couples the test to one viewport and guessed geometry | Re-explore at the execution viewport and find a stable selector or justified coordinate contract |
| Page-wide text oracle | Confuses incidental render text with the intended control state | Scope the assertion to the control/container proved by fresh evidence |
| `try/catch` swallowing errors | Test passes but doesn't verify anything | Fix the assertion |

## Multiple Flaky Tests

When a suite has several flaky tests:

1. **Triage first.** Run the full suite once and group failures by root cause category (timing, state leakage, etc.). Shared root causes (broken fixture, leaking state) should be fixed once, not per-test.
2. **Fix shared infrastructure issues first.** A bad `beforeEach`, a leaking `storageState`, or a missing cleanup can cause many tests to fail. One fix resolves many failures.
3. **Split independent fixes across subagents** when the fix scopes do not overlap (different test files, no shared fixtures). Pass each subagent the test file path, this diagnostic workflow, and the root cause classification table.
4. Judge progress **per test**. One stubborn failure should not block unrelated fixes, but do not keep rerunning the same test unless the next attempt exercises a genuinely new hypothesis.
