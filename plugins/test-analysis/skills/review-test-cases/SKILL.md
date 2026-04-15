---
name: review-test-cases
description: >
  This skill should be used when a quality review of TC-ID test case specifications is needed
  before any framework-specific implementation begins. It reviews the spec artifact only; it does
  not implement or rewrite tests. Triggers: "review test cases", "check test specs",
  "review TC-IDs", "audit test coverage", "are my test cases good", "validate test specs",
  "review test-cases/*.md", "check for gaps in test cases", "review before writing tests", and
  "quality check test specs". Inserted as the shared quality gate between `generate-test-cases`
  and execution-layer authoring — catches gaps, duplication, weak assertions, missing error paths,
  and invented scenarios before they get encoded into framework-specific code.
allowed-tools: Read Glob Grep Task
---

# Review Test Cases

Review TC-ID test case specifications for completeness, accuracy, and quality before they are
implemented in any execution framework. This is a quality gate — catch problems in the spec, not in
the code.

## Input

Parse the spec file path from: $ARGUMENTS

If no argument provided, search for `test-cases/*.md` files and review the most recently modified one.

## Workflow

### Step 1: Load the Spec and Context

1. Read the test case spec file
2. Read any related files for context:
   - `e2e-plan/exploration-report.md` if it exists
   - `e2e-plan/coverage-plan.md` if it exists
3. Extract the target URL from the spec header

### Step 2: Run the Review Checklist

Evaluate every test case against each criterion. Track findings by severity:

- **BLOCKER** — must fix before writing tests (missing critical paths, invented behavior, wrong URL)
- **WARNING** — should fix, will cause problems in implementation (vague steps, weak assertions, duplication)
- **SUGGESTION** — optional improvement (priority adjustment, better categorization, additional edge case)

#### 2a. Coverage Completeness

| Check | What to Look For |
|-------|-----------------|
| Happy path present | At least one Critical-priority test covers the primary success flow end-to-end |
| Error paths covered (when applicable) | For features that depend on backend retrieval/submission, expect coverage for meaningful server/network failures. For collection/data-driven UIs, expect empty-state coverage. For auth-gated features, expect session/auth edge cases. Missing an applicable category is a BLOCKER; a clearly documented non-applicable category is acceptable |
| Boundary conditions | Min/max values, empty inputs, special characters, long strings |
| Authentication edge cases | Session expiry, unauthorized access, role-based differences (if applicable) |
| Navigation edge cases | Back/forward, direct URL access, refresh mid-flow |
| Missing critical user actions | Every user-critical action in scope should appear in at least one test case. Ancillary controls may be omitted if they are not material to the target journey |

#### 2b. Specification Quality

| Check | What to Look For |
|-------|-----------------|
| Steps are concrete | "Click the Submit button" not "submit the form"; "Enter 'test@example.com' in Email field" not "enter email" |
| Expected results are observable | Specific text, URL change, element state — not "page updates" or "works correctly" |
| Preconditions are explicit | Auth state, test data, feature flags, starting URL — nothing assumed |
| TC-IDs are sequential | No gaps, no duplicates, and use the canonical `TC-<FEATURE>-<NNN>` format |
| Priority is justified | Critical = blocks core journey; not everything is Critical |
| Categories are accurate | Happy Path vs Validation vs Edge Case — correctly classified |

#### 2c. Invented vs Observed

This is the most important check. Test cases should trace back to behavior that was actually observed or deliberately triggered during exploration, not assumed.

Red flags for invented scenarios:
- Specific error message text that wasn't observed (e.g., "Please enter a valid email" when the actual message might differ)
- Assumptions about validation rules without exploration evidence (e.g., "minimum 8 characters" without trying it)
- Test cases for UI elements that may not exist (e.g., "retry button" on error page without visiting the error page)
- Server-side behavior assumptions (e.g., "rate limit after 5 attempts" without evidence)

When suspicious: delegate a spot-check to a subagent with browser access (Task tool). Pass it the target URL, the specific TC-IDs under suspicion, and the claims to verify (element existence, error message text, validation behavior). The subagent should return structured evidence: what it found, what matched, what differed.

#### 2d. Duplication and Overlap

- Flag test cases that test the same behavior with trivially different inputs
- Flag test cases where the steps are identical but expected results differ only cosmetically
- Merging candidates: cases that could be combined into a single parameterized test without losing coverage

#### 2e. Implementability

- Flag steps that cannot be automated cleanly by downstream execution frameworks (for example,
  "verify email arrives" or "check database directly" without a stated automation path)
- Flag preconditions that require manual setup with no automation path
- Flag assertions that require visual comparison without specifying tolerance
- Flag test cases that depend on third-party services (payment processors, OAuth providers) without a mock strategy

### Step 3: Produce the Review Report

Output a structured review with this format:

```markdown
# Test Case Review: <feature>

**Spec file:** <path>
**Total test cases:** <count>
**Review date:** <date>

## Verdict: PASS | PASS WITH WARNINGS | NEEDS REVISION

## Blockers (<count>)
- **TC-<ID>**: <issue description>

## Warnings (<count>)
- **TC-<ID>**: <issue description>

## Suggestions (<count>)
- **TC-<ID>**: <issue description>

## Coverage Gaps
- <Missing scenario that should be added>

## Duplication
- **TC-<ID>** and **TC-<ID>**: <overlap description>

## Summary
<2-3 sentences on overall spec quality and what to address before implementation>
```

### Step 4: Verdict Rules

- **PASS** — no blockers, 2 or fewer warnings. Proceed to the execution-layer authoring skill.
- **PASS WITH WARNINGS** — no blockers, 3+ warnings. Can proceed but should address warnings.
- **NEEDS REVISION** — 1+ blockers. Do not proceed to framework-specific implementation until
  blockers are resolved.

Example: 0 blockers + 2 warnings = PASS. 0 blockers + 3 warnings = PASS WITH WARNINGS. 1+ blockers = NEEDS REVISION regardless of warning count.

## Principles

- **Review-only** — never modify the spec file; report findings for the author to act on
- **Evidence over opinion** — cite specific TC-IDs and quote specific steps/assertions when flagging issues
- **Spot-check against live site** — delegate to a subagent with browser access to verify 2-3 suspicious claims rather than trusting all text at face value
- **Bounded output** — the review report should be actionable and finite, not an exhaustive rewrite
- **Severity matters** — distinguish blockers from suggestions; not every imperfection is worth fixing before implementation

## Example Usage

```
Claude Code: /review-test-cases test-cases/login.md
Codex: $review-test-cases test-cases/login.md

Claude Code: /review-test-cases test-cases/checkout.md
Codex: $review-test-cases test-cases/checkout.md
```
