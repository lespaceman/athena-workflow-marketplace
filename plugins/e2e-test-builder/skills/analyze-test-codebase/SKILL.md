---
name: analyze-test-codebase
description: >
  Use when the user wants to understand an existing Playwright test codebase before writing new tests.
  Triggers: "analyze test setup", "check test codebase", "detect test framework", "scan test configuration",
  "understand test structure", "what test framework does this project use", "how are tests organized",
  "what conventions do existing tests follow", "show me the test setup", "what Playwright config is used",
  "analyze existing tests", "check test patterns".
  This skill scans the project for playwright.config, test directories, existing test files, page objects,
  fixtures, auth setup, and naming conventions. Outputs a structured report of conventions to follow
  when writing new tests. Does NOT write tests or explore websites — it only reads and analyzes local files.
user-invocable: true
argument-hint: "[optional: path to project root]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
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

5. **Check for supporting infrastructure**:
   - `fixtures/` or `helpers/` directories
   - `pages/` or `pom/` (Page Object Model)
   - `.env` or `.env.test` files
   - CI configuration (`.github/workflows/`, `Jenkinsfile`, etc.)
   - `package.json` scripts for running tests

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

### Recommendations for New Tests
- Follow existing `*.spec.ts` naming
- Use page objects from `tests/pages/`
- Import test data from `tests/fixtures/testData.ts`
- Use `baseURL` for navigation (relative paths)
- Auth: reuse existing storageState setup
```

## When to Use

Run this **before** writing any new tests to ensure new code follows existing conventions. The output informs the playwright-test-writer agent about project-specific patterns.

## Example Usage

```
/analyze-test-codebase
/analyze-test-codebase ./my-app
```
