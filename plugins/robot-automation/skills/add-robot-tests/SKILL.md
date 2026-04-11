---
name: add-robot-tests
description: >
  THE DEFAULT ENTRY POINT for all Robot Framework / Browser library E2E test work. This skill
  should be used FIRST whenever the user wants to add, create, or set up end-to-end tests
  written in Robot Framework for any feature, page, or application. Runs the full pipeline:
  analyze the .robot codebase, explore the live site, plan coverage, generate TC-ID specs,
  run quality-gate reviews, write production-grade .robot test suites, and execute.
  Delegates to sub-skills (analyze-test-codebase, plan-test-coverage, generate-test-cases,
  review-test-cases, write-robot-code, review-test-code, fix-flaky-tests) internally — do NOT
  skip to sub-skills directly unless the user explicitly requests a narrow activity.
  Uses subagent delegation to save context.
allowed-tools: Read Write Edit Glob Grep Bash Task
---

# Add Robot Framework Tests

Go from zero to passing Robot Framework tests (Browser library) for the target feature in one interactive session.

## Input

Parse the target URL and feature description from: $ARGUMENTS

Derive a **feature slug** from the feature description (e.g., "Login flow" → `login`, "Checkout with payment" → `checkout`). Use this slug for file naming throughout (`tests/<slug>.robot`, `resources/<slug>.resource`).

## 1. Orient: Understand the Project, the Product, and Your Capabilities

Before planning any work, build deep situational awareness. This step determines the quality of everything that follows — rushed orientation leads to missed test cases and wasted effort.

### Understand the codebase

- Does a Robot Framework setup exist? Look for `robot.toml`, `pyproject.toml` with `robotframework` in dependencies, `__init__.robot` suite init files, `tests/*.robot`, `resources/*.resource`, a `requirements.txt` listing `robotframework` and `robotframework-browser`. If the `Browser` library is not yet initialized, `rfbrowser init` must run before any test can execute (see Scaffolding section).
- Are there existing suites? What conventions do they follow — suite naming, keyword style, resource file layout, tags, variables, `Suite Setup` / `Test Setup` patterns, data-driven templates, authentication reuse?
- Load the `analyze-test-codebase` skill and follow its methodology.

### Understand the product

This is the most important part of orientation. You cannot write good tests for a product you don't understand.

- **Read existing test cases** — if `test-cases/*.md` files exist, read them to understand what journeys have been mapped. Look at what's covered AND what's missing.
- **Browse the actual product** — load the `agent-web-interface-guide` skill and use the browser MCP tools to walk through the feature you're testing. Don't just skim the page — interact with it as a user would: fill forms, click buttons, trigger validation, navigate between pages, check error states.
- **Map the user journey in detail** — understand the complete flow: entry points, happy paths, error paths, edge cases, what happens with invalid input, what happens when the user goes back, what conditional UI exists.

Why this matters: absent explicit exploration, agents tend to write tests based on assumptions about how a product works rather than how it actually works. The result is tests that target imaginary behavior or miss critical real behavior. Spending time here prevents both.

### Know your skills

You have access to specialized skills that contain deep domain knowledge. Load the relevant skill before performing each activity — skills prevent improvisation and encode best practices.

| Activity | Skill |
|----------|-------|
| Analyzing Robot setup, config, conventions | `analyze-test-codebase` |
| Deciding what to test, coverage gaps, priorities | `plan-test-coverage` |
| Opening a URL, browsing, using browser MCP tools | `agent-web-interface-guide` |
| Creating TC-ID specs from site exploration | `generate-test-cases` |
| Reviewing TC-ID specs before implementation | `review-test-cases` |
| Writing, editing, or refactoring `.robot` test code | `write-robot-code` |
| Reviewing `.robot` code before execution signoff | `review-test-code` |
| Debugging test failures, checking stability | `fix-flaky-tests` |

Before doing a substantial activity, load the skill that covers that activity so you can follow its workflow rather than improvising.

## 2. Plan: Refine Tasks Into Granular Checkpoints

Refine the work into granular checkpoints based on what orientation revealed. The plan should flow from what you learned, not from a fixed template.

### Task granularity

Think in small checkpoints, not big phases. Each task should represent a concrete, verifiable unit of progress.

Too coarse: "Analyze codebase", "Write tests", "Verify tests"

Right granularity:
- "Read robot.toml — extract outputdir, default tags, listeners"
- "Read 2 existing suites — identify locator style, Suite Setup pattern, resource imports"
- "Write conventions report to e2e-plan/conventions.md"
- "Navigate to /login — catalog all form fields, buttons, and validation messages"
- "Submit login form empty — record all validation error messages and their positions"
- "Submit login with invalid email format — record inline validation behavior"
- "Write TC-LOGIN-001: happy path login with valid credentials"
- "Write TC-LOGIN-002: login with empty email shows required field error"
- "Run `robot -d results tests/login.robot` and record full output"
- "Fix TC-LOGIN-003: locator not found — browse page and re-extract selector"
- "Re-run login suite — verify fix didn't break other tests"
- "Check all TC-IDs from spec are present in test suite"

**Never be conservative.** More tasks is better than fewer. If you discover new work mid-session (a test fails, a locator changed, a form has unexpected validation), add tasks dynamically. The task list is a living document that reflects the real state of the work.

Create tasks for verification steps too (running tests, checking coverage, browsing to confirm selectors), not just implementation.

Update task status as each checkpoint completes. A good pattern is: finish exploration and mark it complete, finish coverage/spec work and mark it complete, finish implementation and mark it complete, then finish review/execution and mark it complete. Do not keep all milestones open until session end.

## 3. Execute

Work through your tasks. Load the relevant skill before each activity.

### Planning uses the browser heavily

When planning what to test (coverage planning, test case generation), use the browser extensively. Don't just catalog elements — interact with the product to discover:
- What validation messages appear for each field?
- What happens when you submit with missing data?
- What error states exist (network errors, empty states, permission errors)?
- What does the flow look like end-to-end, not just page-by-page?
- What edge cases exist (special characters, long inputs, rapid clicks)?
- What UI changes conditionally (loading states, disabled buttons, progressive disclosure)?

Every test case you generate should trace back to something you actually observed or deliberately triggered in the browser. This is how you avoid introducing useless test cases (testing imaginary behavior) and avoid missing important ones (behavior you didn't think to check).

### Subagent delegation

Delegate heavy browser exploration and test writing to subagents when that saves context for orchestration, verification, and debugging. When delegating:
- Pass the relevant file paths (conventions, coverage plan, test specs)
- Instruct the subagent to invoke the appropriate skill (subagents inherit access to plugin skills)
- Specify concrete output expectations (file path, format, TC-ID conventions)

### Quality gates

Two review gates and a test execution checkpoint are mandatory during execution. The review gates are review-only — they produce findings but do not modify files.

**Gate 1: Review test case specs** (after `generate-test-cases`, before `write-robot-code`)
1. Load the `review-test-cases` skill and run it against `test-cases/<feature>.md`
2. If verdict is **NEEDS REVISION** — address all blockers in the spec before proceeding to implementation
3. If verdict is **PASS WITH WARNINGS** — address warnings if quick, otherwise note them and proceed

**Gate 2: Review test code** (after `write-robot-code`, before final test execution)
1. Load the `review-test-code` skill and run it against the implemented `.robot` files
2. If verdict is **NEEDS REVISION** — fix all blockers before running tests for signoff
3. If verdict is **PASS WITH WARNINGS** — fix warnings that affect stability, proceed with execution

**Checkpoint: Test execution**
1. Run the suite: `robot -d results tests/<feature>.robot 2>&1`
2. Inspect the full output — green test output AND the generated `results/log.html` / `results/report.html` are the only proof of correctness
3. If tests fail, load the `fix-flaky-tests` skill and follow its structured diagnostic approach. Do not guess-and-retry.
4. Maximum 3 fix-and-rerun cycles per test. If stuck after 3 cycles, move on with the diagnostic output.

**Test execution and coverage checks must never be delegated to subagents.** Run `robot` directly.

### Error recovery

If infrastructure failures occur (browser MCP unavailable, `rfbrowser init` failures, `pip install` errors), see [references/error-recovery.md](references/error-recovery.md) for diagnostic steps. General pattern: diagnose, attempt one known fix, if still stuck ask the user.

## Scaffolding

If Robot Framework + Browser library is not set up in the target project, follow the procedure in [references/scaffolding.md](references/scaffolding.md) to install dependencies, run `rfbrowser init`, and produce a minimal suite layout.

## Authentication

If the target feature requires login, follow [references/authentication.md](references/authentication.md). Key rule: never hardcode credentials — use variables passed via `--variable` / `.env` / `storageState` JSON, or the project's existing auth keyword.

## Principles

- **Skills carry the knowledge** — load the relevant skill before each activity; do not improvise
- **Subagent-driven** — delegate heavy browser and writing work to subagents to save context
- **Follow existing conventions** — match the project's test style, keyword naming, resource layout, not a generic template
- **Traceable** — every test case links back to a TC-ID from the spec
- **Use what the project provides** — if existing resources include a `CommonKeywords.resource`, a base `pages/*.resource`, environment variables in `variables.py`, or project-local listeners, USE them in generated tests. Do not ship infrastructure that tests ignore.
- **No arbitrary waits** — use Browser library auto-waits and `Wait For Elements State` / `Wait For Response`, never `Sleep`
- **API before UI for setup** — use `RequestsLibrary` for test data; reserve UI for what you are verifying
- **Test failures, not just success** — every feature needs error path coverage
- **Artifacts live in standard locations** — `e2e-plan/` for analysis, `test-cases/` for specs, project `tests/` and `resources/` for executables

## Example Usage

```
Claude Code: /add-robot-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
Codex: $add-robot-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment

Claude Code: /add-robot-tests https://myapp.com/login User authentication including social login
Codex: $add-robot-tests https://myapp.com/login User authentication including social login
```
