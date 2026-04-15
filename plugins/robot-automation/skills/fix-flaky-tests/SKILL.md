---
name: fix-flaky-tests
description: >
  This skill should be used when a Robot Framework test (Browser library) is failing, flaky, timing out, or behaving inconsistently. It provides structured root cause analysis for: stabilizing intermittent tests, debugging timeouts, fixing race conditions, investigating local-vs-CI divergence, config drift, strict-mode ambiguity, and running repeated stability checks. IMPORTANT: If running tests with repeated runs, retries, or pabot loops to check stability, STOP and load this skill first — it has structured root cause analysis that prevents brute-force approaches. Triggers: "stabilize", "intermittent", "flaky", "keeps failing", "fails in CI", "timeout on", "race condition", "run N times to check stability", "verify Robot tests are stable". NOT for writing new tests (use write-robot-code) or analyzing setup (use analyze-test-codebase).
allowed-tools: Read Write Edit Bash Glob Grep Task
---

# Fix Flaky Tests

Systematically diagnose and fix intermittent Robot Framework test failures.

## Input

Parse the test file path or test name from: $ARGUMENTS

## Workflow

### Step 1: Reproduce and Classify
1. Read the failing test file
2. Read `e2e-plan/conventions.yaml` if it exists so you know the intended locator style and runtime baseline
3. Run the test multiple times to observe the pattern
4. Run it in isolation if needed
5. Classify the root cause

| Category | Symptoms |
|----------|----------|
| Timing | Timeout errors, element not ready |
| State leakage | Passes alone, fails with others |
| Data dependency | Missing or conflicting data |
| Race condition | Action and response timing mismatch |
| Locator fragility | Wrong or ambiguous element selected |
| Environment | Local vs CI divergence |
| Config drift | Missing resilience primitives, runtime no longer matches conventions |
| Strict ambiguity | Strict mode fails because a locator now matches multiple elements |

### Step 2: Root Cause Analysis

Investigate based on the category:

- Timing: missing waits, delayed rendering, hidden loading indicators
- State leakage: shared mutable state, missing cleanup, leaking storage state
- Race condition: actions triggered before hydration or before a response wait is attached
- Locator fragility: dynamic DOM, positional selectors, weak scoping
- Environment: viewport, locale, timezone, resource constraints, third-party scripts
- Config drift: missing `run_on_failure`, missing `RetryFailed`, wrong `PABOTQUEUEINDEX`, missing viewport or tracing pins, divergence from `conventions.yaml`
- Strict ambiguity: more than one match, need tighter scoping with `parent=` or `>>`

### Step 3: Apply the Correct Fix

| Category | Principle |
|----------|-----------|
| Timing | Replace `Sleep` with event-driven waits and retrying assertions |
| State isolation | Unique data per test, cleanup, no shared mutable state |
| Race condition | Use `Promise To` + action + `Wait For` |
| Locator | Scope with `parent=` or `>>`, avoid positional selectors |
| Environment | Pin viewport, locale, timezone, and block interfering third-party scripts |
| Config drift | Add missing brownfield resilience primitives in place and rewrite `e2e-plan/conventions.yaml` |
| Strict ambiguity | Keep strict mode on and narrow the locator |

### Step 4: Verify the Fix
1. Run the test 5 or more times
2. Run with the full suite if state leakage is possible
3. If still flaky, reclassify based on new evidence
4. Stop after 3 fix-and-rerun cycles and report the findings if it still flakes

### Step 5: Summarize
Report:
1. Root cause
2. Fix applied
3. Verification evidence
4. Prevention guidance

## Less Obvious Causes
- Viewport size
- Font rendering
- Timezone
- Locale
- Third-party scripts
- Cookie banners
- Feature flags
- Shared database state
- Parallel execution under `pabot`
- Browser caching
- Service workers
- Lazy loading

## Anti-Patterns
- `Sleep`
- `>> nth=0`
- Bigger timeout with no diagnosis
- `skip` instead of fixing
- `--rerunfailed` without a root-cause fix
- `force=True` to hide actionability issues
- `Run Keyword And Ignore Error` around assertions
