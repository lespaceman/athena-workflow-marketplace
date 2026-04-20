---
name: analyze-test-codebase
description: >
  Use to inspect an existing Robot Framework + Browser library codebase before writing, reviewing, or fixing tests. Covers robot.toml or pyproject config, resource files, keyword libraries, listeners, auth keywords, suite init (`__init__.robot`), tag conventions, directory structure, and emits the typed `e2e-plan/conventions.yaml` contract used by downstream skills. Triggers: "understand", "check", "show me", "inspect", or "analyze" the current Robot Framework test setup, config, infrastructure, patterns, or conventions. Does NOT write or fix tests, install Robot Framework, or explore live websites.
allowed-tools: Read Glob Grep Bash
---

# Analyze Robot Framework Test Codebase

Scan and analyze an existing Robot Framework test codebase to understand its conventions, configuration, and patterns before writing new tests.

## Workflow

1. **Locate Robot Framework configuration** — search for `robot.toml`, `pyproject.toml` (look for `[tool.robotframework]`, `robotframework`, `robotframework-browser` dependencies), `requirements*.txt`, and any `__init__.robot` suite-init files.

2. **Extract configuration details**:
   - `outputdir` — where run artifacts go
   - Default `tags` (include/exclude)
   - Configured `listeners` — custom observers for setup, teardown, reporting
   - `variables.py` or `.env` loading — source of environment-derived variables
   - `Library    Browser` import options (`auto_closing_level`, `jsextension`, etc.)
   - `pabot` configuration if parallel execution is used
   - CI scripts in `package.json`, `Makefile`, `tox.ini`, or shell wrappers

3. **Scan suite directory structure**:
   ```
   Glob for tests/**/*.robot, **/__init__.robot, resources/**/*.resource
   ```
   - Count total suite files
   - Identify naming conventions (`*.robot` vs `suite_*.robot`)
   - Map directory organization (by feature? by role? flat?)

4. **Detect patterns in existing suites** — read 2-3 representative `.robot` files and identify:
   - **Locator style**: `Get Element By Role` / `Get Element By Label` / `Get Element By Test Id`, explicit `css=` / `xpath=` / `text=` / `id=`, or legacy mixed forms (flag raw XPath as a risk)
   - **Wait strategy**: auto-waits, `Wait For Elements State`, `Wait For Response`, any `Sleep` (flag these)
   - **Suite structure**: `*** Settings ***` / `*** Variables ***` / `*** Keywords ***` / `*** Test Cases ***` order, suite-level Documentation
   - **Data management**: `Variables    variables.py`, external YAML/CSV, fixtures loaded via listeners
   - **Resource files**: keyword layering, `Resource` imports, any `BasePage`-style shared resource
   - **Auth handling**: persisted `storageState`, `Suite Setup    Log In`, per-test login, hard-coded credentials
   - **Custom libraries**: Python libraries under `libraries/` or `lib/`, custom keyword decorators
   - **Listeners**: `--listener` arguments in `robot.toml` / scripts, custom reporting or cleanup hooks
   - **Network mocking**: `Route URL`, `Intercept Requests`, custom proxy wrappers
   - **Visual regression**: `Take Screenshot`, image-diff keywords, external visual tools
   - **Accessibility testing**: `robotframework-aiolib`, axe integrations, custom a11y keywords
   - **Cross-browser config**: multiple `New Browser` types / headless flags driven by `--variable BROWSER:...`
   - **Retry configuration**: `--rerunfailed`, test-level `[Tags]    retry`, listener-based retries
   - **Parallelism**: `pabot` scripts, suite-level vs test-level parallelism

5. **Check for supporting infrastructure**:
   - `resources/` or `keywords/` directories
   - `libraries/` or `lib/` with Python keyword modules
   - `.env` or `.env.test` files (test-specific environment configuration)
   - `variables.py` or `variables/**/*.yaml`
   - CI configuration (`.github/workflows/`, `Jenkinsfile`, `gitlab-ci.yml`)
   - Auth state files (`auth/*.json`) produced by `Save Storage State`
   - Snapshot directories (`screenshots/`, `baselines/`) for visual regression
   - Docker or `docker-compose` for test environment setup
   - Suite setup/teardown scripts — what they do (auth, seeding, cleanup)

6. **Generate report** — output a structured summary:

```markdown
## Test Codebase Analysis

### Framework
- **Robot Framework** version X.Y.Z
- **Browser library** version X.Y.Z (`rfbrowser init` has/has not been run)
- Config: `robot.toml` / `pyproject.toml`
- Suite directory: `tests/`

### Conventions
- File naming: `*.robot`
- Locator preference: `Get Element By Role` > `Get Element By Label` > `Get Element By Test Id`
- Structure: one suite per feature under `tests/<feature>.robot`
- Shared keywords: `resources/common.resource`, `resources/<feature>.resource`
- Custom libraries: Python modules under `libraries/`

### Auth
- Method: persisted browser state (`auth/user.json`)
- Login keyword: `Log In As Default User` in `resources/auth.resource`

### Existing Coverage
- Total suite files: N
- Feature areas covered: [list]
- Total test cases: ~N

### Network Mocking
- Method: `Route URL` / custom proxy / none
- Patterns: [list any existing mocking keywords]

### Visual Testing
- Enabled: Yes/No
- Tool: Browser `Take Screenshot` + baselines / third-party / none
- Baseline directory: [path if exists]

### Accessibility Testing
- Enabled: Yes/No
- Tool: axe / custom keywords / none

### Cross-Browser & CI
- Browser variants: [list from launch config]
- Retries: [strategy — `--rerunfailed`, listener, none]
- Parallelism: `pabot` / sequential
- CI platform: GitHub Actions / Jenkins / none detected
- Trace: [trace/screenshot settings from `New Context`]

### Recommendations for New Tests
- Follow existing `*.robot` naming
- Reuse keywords from `resources/common.resource`
- Import variables from `variables.py`
- Use `${BASE_URL}` for navigation (no hardcoded domains)
- Auth: reuse existing persisted state setup
```

7. **Emit `e2e-plan/conventions.yaml`** — in addition to the human-readable report, produce a strict, versioned conventions artifact for downstream skills to read. Validate it against `plugins/robot-automation/schemas/conventions.schema.json`. If no Robot project is present, stop and note that analysis could not infer conventions from history; only suggest the optional external scaffold repository if a greenfield bootstrap is requested.

## Out of Scope

This skill only reads and reports on the codebase. For related tasks, use the appropriate skill:

| Task | Skill |
|------|-------|
| Shared live-site exploration and evidence capture | `capture-feature-evidence` |
| Deciding what to test, coverage gaps, priorities | `plan-test-coverage` |
| Writing or modifying executable `.robot` code | `write-robot-code` |
| Diagnosing flaky or failing tests | `fix-flaky-tests` |

## Example Usage

```
/analyze-test-codebase

/analyze-test-codebase ./my-app
```
