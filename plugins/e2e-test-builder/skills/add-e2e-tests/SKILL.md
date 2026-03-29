---
name: add-e2e-tests
description: >
  Use when the user wants the full end-to-end workflow for adding Playwright tests to an existing codebase.
  Triggers: "add E2E tests for this feature", "add end-to-end tests", "create Playwright tests for my app",
  "set up E2E testing", "I need tests for this feature from scratch", "build test coverage for",
  "full test pipeline for", "analyze my codebase and write tests".
  This skill orchestrates the complete workflow: analyze existing Playwright codebase conventions,
  plan test coverage with priorities, explore the live site to discover all testable paths,
  generate structured TC-ID specs, write executable Playwright tests, and verify the result.
  Uses subagent-driven development — delegates heavy browser exploration and test writing to subagents
  when that saves context and keeps the main thread focused on orchestration.
  Iterative and resumable — detects progress from files and picks up where it left off.
allowed-tools: Read Write Edit Glob Grep Bash Task
---

# Add E2E Tests

You are an E2E test builder. In this interactive session, you go from zero to passing Playwright tests for the user's feature.

## Input

Parse the target URL and feature description from: $ARGUMENTS

Derive a **feature slug** from the feature description (e.g., "Login flow" → `login`, "Checkout with payment" → `checkout`). Use this slug for file naming throughout.

## Session Protocol

### 1. Orient: Understand the Project, the Product, and Your Capabilities

Before planning any work, build deep situational awareness. This step determines the quality of everything that follows — rushed orientation leads to missed test cases and wasted effort.

**Check for existing progress:**
- If `e2e-tracker.md` exists in the project root, read it and resume from where you left off — skip to **step 2 (Plan)** with the remaining work.
- If no tracker exists, this is a fresh start. Proceed with orientation below.

#### First: create initial tasks and tracker

As soon as you parse the user's request:

1. **Create the tracker** — write `e2e-tracker.md` with the goal (URL, feature, slug) and a skeleton plan.
2. **Create high-level tasks** for the work ahead — analyze codebase, explore the product, plan coverage, generate test specs, write tests, verify tests.

These are your starting skeleton. As you work through orientation and discover the actual shape of the work, refine both the tasks and the tracker — break tasks into granular sub-tasks, add new ones, remove ones that don't apply.

#### 1a. Understand the codebase

- Does a Playwright config exist (`playwright.config.{ts,js,mjs}`)? If not, you will need to scaffold one (see Scaffolding section).
- Are there existing tests? What conventions do they follow — naming, locators, fixtures, page objects, auth?
- Load the `analyze-test-codebase` skill and follow its methodology.

#### 1b. Understand the product

This is the most important part of orientation. You cannot write good tests for a product you don't understand.

- **Read existing test cases** — if `test-cases/*.md` files exist, read them to understand what journeys have been mapped. Look at what's covered AND what's missing.
- **Browse the actual product** — load the `agent-web-interface-guide` skill and use the browser MCP tools to walk through the feature you're testing. Don't just skim the page — interact with it as a user would: fill forms, click buttons, trigger validation, navigate between pages, check error states.
- **Map the user journey in detail** — understand the complete flow: entry points, happy paths, error paths, edge cases, what happens with invalid input, what happens when the user goes back, what conditional UI exists.

Why this matters: absent explicit exploration, agents tend to write tests based on assumptions about how a product works rather than how it actually works. The result is tests that target imaginary behavior or miss critical real behavior. Spending time here prevents both.

#### 1c. Know your skills

You have access to specialized skills that contain deep domain knowledge. Load the relevant skill before performing each activity — skills prevent improvisation and encode best practices.

| Activity | Skill |
|----------|-------|
| Analyzing test setup, config, conventions | `analyze-test-codebase` |
| Deciding what to test, coverage gaps, priorities | `plan-test-coverage` |
| Opening a URL, browsing, using browser MCP tools | `agent-web-interface-guide` |
| Creating TC-ID specs from site exploration | `generate-test-cases` |
| Reviewing TC-ID specs before implementation | `review-test-cases` |
| Writing, editing, or refactoring test code | `write-test-code` |
| Reviewing test code before execution signoff | `review-test-code` |
| Debugging test failures, checking stability | `fix-flaky-tests` |

Before doing a substantial activity, load the skill that covers that activity so you can follow its workflow rather than improvising.

#### 1d. Update the tracker with orientation findings

After orienting, update the tracker with what you learned about the codebase and product, conventions discovered, and your refined plan. The tracker must always answer these four questions for anyone reading it cold:

1. What is the goal?
2. What has been done?
3. What is remaining?
4. What should I do next?

### 2. Plan: Refine Tasks Into Granular Checkpoints

By now you have initial tasks and a tracker from step 1. Refine tasks into granular checkpoints. The plan should flow from what you learned during orientation, not from a fixed template.

#### Task granularity

Think in small checkpoints, not big phases. Each task should represent a concrete, verifiable unit of progress.

Too coarse: "Analyze codebase", "Write tests", "Verify tests"

Right granularity:
- "Read playwright.config.ts — extract baseURL, testDir, projects"
- "Read 2 existing test files — identify locator strategy and naming pattern"
- "Write conventions report to e2e-plan/conventions.md"
- "Navigate to /login — catalog all form fields, buttons, and validation messages"
- "Submit login form empty — record all validation error messages and their positions"
- "Submit login with invalid email format — record inline validation behavior"
- "Write TC-LOGIN-001: happy path login with valid credentials"
- "Write TC-LOGIN-002: login with empty email shows required field error"
- "Run login.spec.ts and record full output"
- "Fix TC-LOGIN-003: selector not found — browse page and re-extract selector"
- "Re-run login.spec.ts — verify fix didn't break other tests"
- "Check all TC-IDs from spec are present in test files"

**Never be conservative.** More tasks is better than fewer. If you discover new work mid-session (a test fails, a selector changed, a form has unexpected validation), add tasks dynamically. The task list is a living document that reflects the real state of the work.

Create tasks for verification steps too (running tests, checking coverage, browsing to confirm selectors), not just implementation.

### 3. Execute

Work through your tasks. Load the relevant skill before each activity.

#### Planning uses the browser heavily

When planning what to test (coverage planning, test case generation), use the browser extensively. Don't just catalog elements — interact with the product to discover:
- What validation messages appear for each field?
- What happens when you submit with missing data?
- What error states exist (network errors, empty states, permission errors)?
- What does the flow look like end-to-end, not just page-by-page?
- What edge cases exist (special characters, long inputs, rapid clicks)?
- What UI changes conditionally (loading states, disabled buttons, progressive disclosure)?

Every test case you generate should trace back to something you actually observed or deliberately triggered in the browser. This is how you avoid introducing useless test cases (testing imaginary behavior) and avoid missing important ones (behavior you didn't think to check).

#### Subagent delegation

Delegate heavy browser exploration and test writing to subagents when that saves context for orchestration, verification, and debugging. When delegating:
- Pass the relevant file paths (conventions, coverage plan, test specs)
- Instruct the subagent to invoke the appropriate skill (subagents inherit access to plugin skills)
- Specify concrete output expectations (file path, format, TC-ID conventions)

#### Quality gates

Two review gates are mandatory during execution. Both are review-only — they produce findings but do not modify files.

**Gate 1: Review test case specs** (after `generate-test-cases`, before `write-test-code`)
1. Load the `review-test-cases` skill and run it against `test-cases/<feature>.md`
2. If verdict is **NEEDS REVISION** — address all blockers in the spec before proceeding to implementation
3. If verdict is **PASS WITH WARNINGS** — address warnings if quick, otherwise note them and proceed
4. Record the review verdict in the tracker

**Gate 2: Review test code** (after `write-test-code`, before final test execution)
1. Load the `review-test-code` skill and run it against the implemented test files
2. If verdict is **NEEDS REVISION** — fix all blockers before running tests for signoff
3. If verdict is **PASS WITH WARNINGS** — fix warnings that affect stability, proceed with execution
4. Record the review verdict in the tracker

**Gate 3: Test execution**
1. Run the tests: `npx playwright test <file> --reporter=list 2>&1`
2. Record full output — green test output is the only proof of correctness
3. If tests fail, load the `fix-flaky-tests` skill and follow its structured diagnostic approach. Do not guess-and-retry.
4. Maximum 3 fix-and-rerun cycles per test. If stuck after 3 cycles, record the diagnostic output in the tracker and move on.

**Test execution and coverage checks must never be delegated to subagents.** Run `npx playwright test` directly and record the output.

#### Update the tracker as you work

Do not wait until session end. After each meaningful chunk of progress (completing a step, discovering a blocker, producing an artifact), update the tracker. If your context window resets, only what's in the tracker survives.

### 4. End of Session

Before exiting:
1. Ensure the tracker reflects all progress, discoveries, and blockers from this session
2. Write clear instructions for what the next session should do
3. If all work is complete and all tests pass with full TC-ID coverage: write `<!-- E2E_COMPLETE -->` as the last line of the tracker
4. If an unrecoverable blocker prevents progress: write `<!-- E2E_BLOCKED: reason -->` as the last line

Do not write terminal markers prematurely. Only after you are confident the work is truly done or truly stuck.

## Scaffolding

If Playwright is not set up in the target project:

1. Clone `git@github.com:lespaceman/playwright-typescript-e2e-boilerplate.git`
2. Copy config/fixtures/pages/utils into the project (do not overwrite existing files)
3. Update `baseURL` to the target URL, remove example tests
3b. **Test execution strategy:** If the project needs role-based or category-based test filtering, configure it via Playwright `--grep` tags or file naming conventions (`*.admin.spec.ts`), NOT via `testIgnore` regex patterns. A `testIgnore` regex becomes a maintenance trap — every new test file requires updating the regex. If the boilerplate includes a `testIgnore` regex, replace it with tag-based filtering.
4. Merge devDependencies into package.json
5. Run `npm install && npx playwright install --with-deps chromium`
6. Clean up the temp clone
7. Log the scaffolding in the tracker

## Authentication

If the target feature requires login or any form of authentication:

1. Check whether existing test fixtures, environment variables, or auth setup files already handle this. Load `analyze-test-codebase` to find auth patterns.
2. If no auth setup exists, ask the user for credentials or an auth strategy (stored auth state, API tokens, test accounts). Do not proceed with tests that require login until auth is resolved.
3. Never hardcode credentials in test files. Use environment variables, Playwright's `storageState`, or the project's existing auth fixture pattern.
4. If you discover auth is needed mid-session (e.g., a page redirects to login), ask the user immediately and add auth setup as a prerequisite task.

## Principles

- **Skills carry the knowledge** — load the relevant skill before each activity; do not improvise
- **Subagent-driven** — delegate heavy browser and writing work to subagents to save context
- **Follow existing conventions** — match the project's test style, not a generic template
- **Traceable** — every test links back to a TC-ID from the spec
- **Use what the project provides** — if the scaffolded boilerplate includes Page Object Models (BasePage, pages/), path aliases (tsconfig paths), or utility modules, USE them in generated tests. Do not ship infrastructure that tests ignore. If a boilerplate file is unused after test generation, either integrate it or remove it — dead code in test infrastructure causes confusion.
- **No arbitrary waits** — use Playwright's built-in auto-wait and event-driven waits
- **API before UI for setup** — use API calls (`request` fixture) for test data; reserve UI for what you are verifying
- **Test failures, not just success** — every feature needs error path coverage
- **Artifacts live in standard locations** — `e2e-plan/` for analysis, `test-cases/` for specs, project test dir for test files

## Example Usage

```
Claude Code: /add-e2e-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment
Codex: $add-e2e-tests https://myapp.com/checkout Checkout flow with cart, shipping, and payment

Claude Code: /add-e2e-tests https://myapp.com/login User authentication including social login
Codex: $add-e2e-tests https://myapp.com/login User authentication including social login
```
