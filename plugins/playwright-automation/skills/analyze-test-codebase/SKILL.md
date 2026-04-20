---
name: analyze-test-codebase
description: >
  Scans and reports on an existing Playwright test codebase. This skill should be used to inspect the current Playwright setup before writing, reviewing, or fixing tests, and should be loaded early when working in a new project to understand existing patterns. Covers: Playwright config, page objects, fixtures, helpers, auth/globalSetup patterns, test conventions, and directory structure. Triggers: "understand", "check", "show me", "inspect", or "analyze" the current test setup, config, infrastructure, patterns, or conventions. In the full add-tests workflow, this skill serves as an early read-only analysis sub-step before planning detailed coverage or writing code. This skill examines existing files and outputs a structured report. It does NOT write or fix tests, install Playwright, or explore live websites — for live-site exploration, use `capture-feature-evidence` so evidence is captured in `e2e-plan/exploration-report.md`.
allowed-tools: Read Glob Grep Bash
---

# Analyze Test Codebase

Scan and analyze an existing Playwright test codebase to understand its conventions, configuration, and patterns before writing new tests.

## Workflow

1. **Locate Playwright configuration** — search for `playwright.config.ts`, `playwright.config.js`, or `playwright.config.mjs` in the project root and common subdirectories.

2. **Extract configuration details**:
   - `baseURL` — the target application URL
   - `testDir` — where tests live
   - `projects` — browser/device configurations
   - `use` — default options (viewport, headless, trace, screenshot)
   - `webServer` — if Playwright starts the app
   - `globalSetup` / `globalTeardown` — auth or data seeding scripts
   - `reporter` — configured reporters

3. **Scan test directory structure**:
   ```
   Glob for **/*.spec.ts, **/*.test.ts, **/*.spec.js, **/*.test.js
   ```
   - Count total test files
   - Identify naming conventions (`.spec.ts` vs `.test.ts`)
   - Map directory organization (by feature? by page? flat?)

4. **Detect patterns in existing tests** — read 2-3 representative test files and identify:
   - **Locator strategy**: `getByRole`, `getByTestId`, CSS selectors, XPath
   - **Wait strategy**: auto-waits, explicit `waitFor*`, any `waitForTimeout` (flag these)
   - **Test structure**: AAA pattern, describe/test nesting, use of `test.step`
   - **Data management**: fixtures, test data files, factory functions
   - **Page Objects**: POM pattern usage, fixture-based injection
   - **Auth handling**: `storageState`, global setup, per-test login
   - **Custom fixtures**: extended `test` with custom fixtures
   - **Helper utilities**: shared functions, custom assertions
   - **Network mocking**: `page.route()` usage, HAR recording (`routeFromHAR`), API interceptors
   - **Visual regression**: `toHaveScreenshot()`, `toMatchSnapshot()`, snapshot directories
   - **Accessibility testing**: `@axe-core/playwright` usage, custom a11y assertions
   - **Cross-browser config**: multiple projects in playwright.config (chromium, firefox, webkit)
   - **Retry configuration**: `retries` count, trace settings (`on-first-retry`)
   - **Parallelism**: `fullyParallel`, `workers` count, test isolation strategy

5. **Check for supporting infrastructure**:
   - `fixtures/` or `helpers/` directories
   - `pages/` or `pom/` (Page Object Model)
   - `.env` or `.env.test` files (test-specific environment configuration)
   - CI configuration (`.github/workflows/`, `Jenkinsfile`, etc.)
   - `package.json` scripts for running tests
   - `*.har` files or HAR directories (recorded API responses for mocking)
   - Snapshot directories (`__snapshots__`, `screenshots/`) for visual regression baselines
   - Docker or `docker-compose` for test environment setup
   - Global setup/teardown scripts — what they do (auth, seeding, cleanup)

6. **Generate report** — output a structured summary:

```markdown
## Test Codebase Analysis

### Framework
- **Playwright** version X.Y.Z
- Config: `playwright.config.ts`
- Test directory: `tests/`

### Conventions
- File naming: `*.spec.ts`
- Locator preference: getByRole > getByTestId
- Structure: describe blocks by feature
- Page Objects: Yes, in `tests/pages/`
- Custom fixtures: Yes, in `tests/fixtures/`

### Auth
- Method: storageState via global setup
- Auth file: `tests/.auth/user.json`

### Existing Coverage
- Total test files: N
- Feature areas covered: [list]
- Test count: ~N tests

### Network Mocking
- Method: page.route() / HAR / none
- Patterns: [list any existing mocking patterns]

### Visual Testing
- Enabled: Yes/No
- Tool: toHaveScreenshot() / third-party / none
- Baseline directory: [path if exists]

### Accessibility Testing
- Enabled: Yes/No
- Tool: @axe-core/playwright / custom assertions / none

### Cross-Browser & CI
- Browser projects: [list from config]
- Retries: N (CI) / N (local)
- Workers: N / fullyParallel: Yes/No
- CI platform: GitHub Actions / Jenkins / none detected
- Trace: [setting from config]

### Recommendations for New Tests
- Follow existing `*.spec.ts` naming
- Use page objects from `tests/pages/`
- Import test data from `tests/fixtures/testData.ts`
- Use `baseURL` for navigation (relative paths)
- Auth: reuse existing storageState setup
```

## Out of Scope

This skill only reads and reports on the codebase. For related tasks, use the appropriate skill:

| Task | Skill |
|------|-------|
| Shared live-site exploration and evidence capture | `capture-feature-evidence` |
| Deciding what to test, coverage gaps, priorities | `plan-test-coverage` |
| Writing or modifying executable test code | `write-test-code` |
| Diagnosing flaky or failing tests | `fix-flaky-tests` |

## Example Usage

```
/analyze-test-codebase

/analyze-test-codebase ./my-app
```
