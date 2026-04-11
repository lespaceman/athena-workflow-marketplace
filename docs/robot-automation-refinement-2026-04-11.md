# Robot Automation Plugin — Senior-Engineer Refinement

**Date:** 2026-04-11
**Author:** Claude (brainstorming + research pass)
**Status:** Approved — proceeding to implementation plan
**Scope:** `plugins/robot-automation/` + `workflows/robot-automation/`

## Summary

The `robot-automation` plugin is factually incorrect in its locator dialect, under-specifies proactive resilience, duplicates content between its workflow doc and its entry skill, and does not dogfood against any real Robot Framework project. This design corrects all four.

Scaffolding is optional and external to this marketplace repo. The shipped skills remain responsible for Robot-specific conventions, brownfield adaptation, locator dialect, waiting strategy, and review gates. An external scaffold/bootstrap project is only used when no Robot project exists and the user wants an all-at-once `git clone` starting point.

The refinement is grounded in primary sources: the Browser library keyword documentation, the `robotframework-browser` README, DeepWiki's Finding Elements synthesis, the `pabot` README, Robot Framework forum threads (including maintainer comments from Mikko Korpela), and the `robotframework-retryfailed` listener.

## Goals

1. **Correctness.** Stop teaching Playwright-JS selector syntax as Robot Browser library syntax. Use the library's own `Get Element By Role` / `Get Element By Label` / `Get Element By Test Id` keywords and only `css=` / `xpath=` / `text=` / `id=` as prefixed engines.
2. **Resilience.** Bake the Browser library's built-in resilience primitives (`run_on_failure`, strict mode, `Promise To`, tracing on failure, viewport/locale/timezone pinning, third-party script blocking, RetryFailed listener) into every scaffolded project by default.
3. **Adaptation.** Introduce a typed `conventions.yaml` contract that `analyze-test-codebase` always produces for existing Robot projects, and that an optional external scaffold project can also produce for greenfield starts. Every downstream skill reads the same contract. Stop each skill re-deriving conventions independently.
4. **Professionalism.** Add smoke-first discipline, mandatory selector spot-checks, re-run-for-stability in Gate 3, and end-to-end dogfooding via a dry-run target inside the marketplace repo.

## Non-goals

- Rewriting the 8-skill structure from scratch.
- Abandoning the existing TC-ID / quality-gate / review-only gate discipline — those are the plugin's strongest parts and stay untouched.
- Shipping a local scaffold skill inside this marketplace repo. Bootstrap stays external and optional; the marketplace ships the expertise needed for direct brownfield work.
- Supporting non-Browser Robot Framework libraries (SeleniumLibrary, AppiumLibrary). The plugin stays Browser-library-specific.

## Research grounding

All factual claims in this design are cited to primary sources:

- [Browser library keyword documentation](https://marketsquare.github.io/robotframework-browser/Browser.html) — confirms only `css=`, `xpath=`, `text=`, `id=` are documented selector engine prefixes; strict mode on by default; `auto_closing_level` semantics
- [DeepWiki: Finding Elements](https://deepwiki.com/MarketSquare/robotframework-browser/4.1-finding-elements) — confirms the `Get Element By *` keyword family (Role, Label, Placeholder, Alt Text, Test Id, Text, Title); `>>` same-frame chaining; `>>>` iframe piercing
- [robotframework-browser README](https://github.com/MarketSquare/robotframework-browser) — pabot integration, `ROBOT_FRAMEWORK_BROWSER_NODE_PORT`, BrowserBatteries install path, `--testlevelsplit` discouraged for small tests
- [pabot README](https://github.com/mkorpela/pabot) — `PABOTQUEUEINDEX` (not `PABOT_QUEUE_INDEX`), `--pabotlib`, `Acquire Value Set`, `--resourcefile`, value sets for credential distribution
- [Robot Framework forum: properly using Wait for Response](https://forum.robotframework.org/t/properly-using-wait-for-response/4507) — maintainer Mikko Korpela: "There is a possibility that the click-related request response happens before you attach the wait if wait is done after"
- [Robot Framework forum: pabot test data setup](https://forum.robotframework.org/t/how-do-you-setup-test-data-when-running-parallel-tests-using-pabot/7049) — `Acquire Value Set` + `--resourcefile` is the idiomatic pattern
- [robotframework-retryfailed listener](https://github.com/MarketSquare/robotframework-retryfailed) — `--listener RetryFailed:1:True`, `[Tags] test:retry(2)` tag format
- [RoboCon 2026 Mastering Browser library workshop](https://pretalx.com/robocon-2026/talk/8WNP37/) — Tatu Aalto lead developer, current workshop coverage

## What the current plugin gets wrong

### Locator dialect (factually incorrect)

`write-robot-code/SKILL.md` teaches this hierarchy:

> Priority 1: `role=button[name="Submit"]`
> Priority 2: `label=Email`
> Priority 3: `placeholder=Search…`

None of `role=`, `label=`, `placeholder=`, `alt=`, `title=`, `testid=` are documented selector engines in the Browser library. Only `css=`, `xpath=`, `text=`, `id=` are. The documented way to access role/label/placeholder/alt/title/testid locators is via the dedicated `Get Element By Role` / `Get Element By Label` / `Get Element By Placeholder` / `Get Element By Alt Text` / `Get Element By Title` / `Get Element By Test Id` keywords, which return Locator references.

Tests written with `role=button[name="…"]` string selectors may fall back to a looser match or silently not match the intended element. The plugin currently references `Get Element By Role` zero times across all 8 skills.

### `Promise To` race condition

Maintainer Mikko Korpela on the Robot Framework forum:

> "There is a possibility that the click-related request response happens before you attach the wait if wait is done after."

The plugin mentions `Promise To` once in `references/network-interception.md` but then teaches the naive "click then Wait For Response" pattern in multiple other places — the exact pattern the maintainer warns against.

### `PABOTQUEUEINDEX` typo

`references/auth-patterns.md` uses `PABOT_QUEUE_INDEX`. The pabot README documents the variable as `PABOTQUEUEINDEX` (no underscores). The plugin's example Strategy 2 code will not work as written.

### Missing built-in resilience primitives

The Browser library has a `run_on_failure` library-import parameter that provides auto-screenshot-on-failure in one line. The plugin references it zero times. Similarly missing: `tracing=retain-on-failure` context argument, strict mode (on by default), the `robotframework-retryfailed` listener, `New Context` viewport/locale/timezoneId pinning, third-party script blocking.

### No machine-readable adaptation contract

`analyze-test-codebase` produces a human-readable report. Every downstream skill independently re-derives conventions from the `.robot` files, which causes silent drift between what the writer assumes and what the reviewer checks. There is no contract that says "these are the conventions you must respect." `e2e-plan/conventions.md` is mentioned in `review-test-code/SKILL.md` but never defined or produced.

### Workflow duplication

`workflow.md` and `add-robot-tests/SKILL.md` duplicate orientation, quality-gate rules, and delegation constraints. They've already drifted slightly in wording. Operational guidance should have one source of truth.

### Never dogfooded

No Robot Framework project exists anywhere under the marketplace repo. The plugin has never executed end-to-end against its own target framework. The locator dialect error would have surfaced on the first real test run.

## Architecture after refinement

```
                                   ┌──────────────────────────┐
  workflow.md (thin orchestration) │   add-robot-tests        │
  ─────────────────────────────── │   (operational guide)     │
                                   └─────────┬────────────────┘
                                             │
                ┌────────────────────────────┼───────────────────────────────┐
                ▼                            ▼                               ▼
      ┌─────────────────┐         ┌──────────────────────┐         ┌──────────────────┐
      │ analyze-test-   │────────▶│ conventions.yaml     │◀────────│ scaffold-robot-  │
      │ codebase        │  writes │ (typed contract)     │  writes │ project (NEW)    │
      └─────────────────┘         └──────────┬───────────┘         └──────────────────┘
                                             │ reads
                 ┌───────────────────────────┼─────────────────────────────┐
                 ▼                           ▼                             ▼
      ┌──────────────────┐        ┌──────────────────┐         ┌──────────────────┐
      │ plan-test-       │───▶    │ generate-test-   │───▶     │ review-test-     │
      │ coverage         │        │ cases            │         │ cases (Gate 1)   │
      └──────────────────┘        └──────────────────┘         └─────────┬────────┘
                                                                         │
                 ┌───────────────────────────────────────────────────────┘
                 ▼
      ┌──────────────────┐        ┌──────────────────┐         ┌──────────────────┐
      │ write-robot-     │───▶    │ review-test-     │───▶     │ Gate 3: execute  │
      │ code             │        │ code (Gate 2)    │         │ + 3× re-run      │
      └──────────────────┘        └──────────────────┘         └─────────┬────────┘
                                                                         │
                                                                         ▼
                                                          ┌──────────────────┐
                                                          │ fix-flaky-tests  │
                                                          └──────────────────┘
```

**Skill count stays at 8** (one new, one dropped-to-reference: nothing — scaffolding is promoted, the reference file moves into the new skill's body).

## Component changes

### `add-robot-tests` — operational source of truth

- Absorbs all substantive content from `workflow.md` (quality-gate rules, delegation constraints, orientation guidance, guardrails)
- Adds smoke-first discipline as a mandatory step
- Adds `conventions.yaml` read requirement
- Re-anchors the skill table around the new 8-skill set

### `analyze-test-codebase` — emit `conventions.yaml`

- Adds detection for: strict mode, `run_on_failure`, listeners (including `RetryFailed`), `robot.toml` vs `__init__.robot`, pabot config + `--resourcefile`, BrowserBatteries vs classic Node install path, auto_closing_level
- Existing human-readable report stays; new typed output is added alongside
- Handles missing fields gracefully — the output is a best-effort snapshot of what was detected, fields that could not be inferred are marked `null`

### External scaffold project — optional bootstrap path

The scaffold/bootstrap project is not a shipped skill in this marketplace repo.

**Greenfield only (no Robot Framework project exists):**
- The agent may clone an external scaffold/bootstrap repository when the user explicitly wants an all-at-once starting point
- That external project can provide templates, dependency install guidance, CI skeletons, and a smoke suite
- It should emit the same `conventions.yaml` contract so downstream marketplace skills can continue from the same handoff

**Brownfield stays inside the shipped skills:**
- `analyze-test-codebase` emits `conventions.yaml`
- `write-robot-code`, `review-test-code`, and `fix-flaky-tests` carry the Browser-library-specific best practices directly
- Missing resilience primitives in an existing Robot project are handled as additive, in-place improvements guided by the shipped skills rather than by cloning a scaffold

### `plan-test-coverage` — light touches

- Reads `conventions.yaml` to respect existing tag vocabulary, priorities, and locator style
- No other changes

### `generate-test-cases` — locator dialect in observations

- "Selectors observed" section of spec format updated: emits actual `Get Element By Role    button    name=Submit` calls, not `role=button[name="Submit"]` strings
- Browser exploration output format accepts either form but records in the new canonical form

### `review-test-cases` — checklist dialect update

- Invented-vs-observed check unchanged
- Locator syntax check updated to match the new dialect
- Still review-only

### `write-robot-code` — major rewrite

The biggest content change in this refinement:

- **New locator hierarchy** (see Locator Dialect section below) replaces the current Playwright-JS-flavored one
- **Smoke-first discipline** as a mandatory Step 4: write ONE happy-path test, run it, get it green, THEN expand
- **Mandatory locator spot-check** as Step 3 (currently optional)
- **`Promise To` + `Wait For Response` pattern** promoted to first-class in the Waiting Strategy section with a direct quote from maintainer Mikko Korpela
- **Strict mode awareness** — tests must not silently disable it
- **`conventions.yaml` read** required in Step 2
- Anti-patterns list updated for new dialect
- Test template updated to use `Get Element By Role` + `Promise To` pattern

### `review-test-code` — major rewrite

- **BLOCKER** for any use of `role=` / `label=` / `placeholder=` / `alt=` / `title=` / `testid=` as string selector prefixes
- **BLOCKER** for `Set Strict Mode False` without a `# WHY:` comment
- **BLOCKER** for `force=True` without a root-cause comment
- **WARNING** for any Click/Fill followed by a bare `Wait For Response` (should be `Promise To ... Click ... Wait For`)
- **WARNING** for `>> nth=N` without justification
- Locator quality checklist rebuilt around the new dialect
- `conventions.yaml` adherence check added

### `fix-flaky-tests` — diagnostic tree additions

- Check strict mode status when locator ambiguity is suspected
- Check for `Promise To` race condition when network-driven tests flake
- Check `run_on_failure` config when screenshots on failure are missing
- Check pabot `PABOTQUEUEINDEX` typos
- Check viewport / locale / timezone pinning on flakiness that varies CI-vs-local

## `conventions.yaml` schema

```yaml
version: 1
framework:
  robot_framework: "7.2.1"            # null if greenfield
  robotframework_browser: "19.12.5"
  python: "3.11"
  node: "22"                          # null if BrowserBatteries path
  rfbrowser_initialized: true
layout:
  tests_dir: "tests/"
  resources_dir: "resources/"
  variables_file: "variables.py"      # null if absent
  output_dir: "results/"
runtime:
  runner_config: "robot.toml"         # or "__init__.robot"
  strict_mode: true
  auto_closing_level: "SUITE"
  run_on_failure: "Take Screenshot failure-{index} fullPage=True"
  listeners:
    - "RetryFailed:1:True"
  default_timeout: "10s"
conventions:
  locator_style: "get_element_by_role_first"  # or "css_first" for legacy
  resource_pattern: "common+feature"           # or "monolithic", "none"
  auth_strategy: "persisted_storage_state"     # or "per_test", "api_token", "none"
  test_data_strategy: "requests_library_api"   # or "ui_setup", "fixtures", "none"
  tag_vocabulary: ["smoke", "critical", "TC-*"]
parallel:
  enabled: true
  mode: "suite"                       # or "test", "disabled"
  pabotlib: true
  resource_file: null                 # path to users.dat or null
base_url:
  source: "variables.py::BASE_URL"    # or "hardcoded", "env"
  value_example: "https://example.com"
observations:
  generated_at: "2026-04-11T00:00:00Z"
  generated_by: "analyze-test-codebase"
  notes: []
```

**Contract rules:**

- `analyze-test-codebase` is the default writer for existing Robot projects. An optional external scaffold/bootstrap project may also write the artifact for greenfield starts.
- Every downstream skill reads it in its "understand context" step and fails loudly if it's missing (or runs `analyze-test-codebase` first if appropriate).
- Unknown fields are an error — no silent schema drift. When the schema evolves, `version` bumps.
- Enumerated fields (locator_style, auth_strategy, test_data_strategy, etc.) must use documented values. Freeform values are not allowed.
- `notes` is the only freeform field, reserved for caveats that don't fit the schema.

## Locator dialect (new canonical)

**New priority order** — enforced by `write-robot-code` and `review-test-code`:

| Priority | Pattern | When to use |
|---|---|---|
| 1 | `Get Element By Role    button    name=Submit` (keyword call) | Semantic elements: buttons, links, headings, form controls |
| 2 | `Get Element By Label    Email` | Form inputs with visible labels |
| 3 | `Get Element By Placeholder    Search…` | Inputs identified by placeholder |
| 4 | `Get Element By Test Id    submit-button` | When the dev team provides `data-testid` |
| 5 | `text="Welcome"` or `text=/welcome/i` | Short, stable text (JavaScript regex syntax) |
| 6 | `id=login_btn` | Stable static IDs |
| 7 | `css=main >> .card:not(.hidden)` with `>>` scoping | Last-resort CSS, scoped to a container |
| 8 | `xpath=//button[@data-qa='x']` | Absolute last resort, requires a `# WHY:` comment |

**Banned:**

- `role=…` / `label=…` / `placeholder=…` / `alt=…` / `title=…` / `testid=…` as string selector prefixes (BLOCKER)
- `>> nth=N` without a documented reason (WARNING)
- `Set Strict Mode False` without a `# WHY:` comment (BLOCKER)
- Utility-class selectors (Tailwind `.btn-primary`, Bootstrap `.col-md-6`, etc.) (BLOCKER)
- `force=True` on interactions without a `# WHY:` comment (WARNING)

**Scoping pattern** — use `parent=` on `Get Element By *` calls:

```robotframework
${dialog}=     Get Element By Role    dialog    name=Confirm delete
${confirm}=    Get Element By Role    button    name=Delete    parent=${dialog}
Click          ${confirm}
```

**iframe piercing** — `>>>` (three angles), not `>>`:

```robotframework
${button}=    Set Variable    id=payment-iframe >>> role=button[name="Pay"]
```

**Strict mode ON by default.** Tests that genuinely need to disable it must do so scoped and commented:

```robotframework
# WHY: vendor widget renders identical role=listitem entries, intentional duplication
Set Strict Mode    False    scope=Suite
```

## `Promise To` pattern as default

Any action that triggers a network call uses this pattern:

```robotframework
${promise}=    Promise To    Wait For Response    matcher=**/api/session    timeout=10s
Click          role=button[name="Sign in"]
${response}=   Wait For    ${promise}
```

Cited in `write-robot-code/SKILL.md` body with a direct quote from maintainer Mikko Korpela.

**Matcher gotcha documented:**
- URL glob form (`**/api/session`) is preferred for simple cases
- Regex form uses JavaScript regex syntax, not Python
- Predicate function form (`async (response) => response.status() === 200`) is JavaScript

## Proactive resilience toolkit

These defaults are the standard the shipped skills teach and enforce. An optional external scaffold/bootstrap project should emit them automatically for greenfield starts:

**`resources/common.resource`:**
```robotframework
*** Settings ***
Library    Browser
...    auto_closing_level=SUITE
...    run_on_failure=Take Screenshot failure-{index} fullPage=True
...    strict=True
Library    RequestsLibrary
Variables  ../variables.py

*** Keywords ***
Open Browser To Base URL
    [Arguments]    ${url}=${BASE_URL}
    New Browser    chromium    headless=${HEADLESS}
    New Context
    ...    viewport={'width': 1280, 'height': 720}
    ...    locale=en-US
    ...    timezoneId=UTC
    ...    tracing=retain-on-failure
    Block Noise
    New Page    ${url}

Block Noise
    # Third-party scripts commonly cause flakiness
    # Populate with Route URL ... Abort calls for analytics/chat/hotjar after exploration
    Log    Noise blocking placeholder — populate after browser exploration    level=DEBUG
```

**`robot.toml`** (RF 7+):
```toml
output-dir = "results"
listener = ["RetryFailed:1:True"]
variablefile = ["variables.py"]

[tags]
default = ["smoke"]
```

**`variables.py`:**
```python
import os

BASE_URL = os.getenv("BASE_URL", "https://example.com")
HEADLESS = os.getenv("HEADLESS", "True") == "True"
```

**`tests/smoke.robot`:**
```robotframework
*** Settings ***
Documentation    Scaffold smoke test — proves the installation works.
Resource         ../resources/common.resource
Suite Setup      Open Browser To Base URL
Suite Teardown   Close Browser
Test Tags        smoke

*** Test Cases ***
TC-SMOKE-001 Base URL loads and has a title
    [Documentation]    Smoke check — the page loads, a title exists.
    [Tags]    TC-SMOKE-001    critical
    ${title}=    Get Title
    Should Not Be Empty    ${title}
```

**`.github/workflows/robot.yml`:** one job, caches pip, runs install + `rfbrowser init`, runs `robot -d results tests/smoke.robot`, uploads `results/` on failure. Comments explain how to extend.

**`.gitignore` additions:** `results/`, `auth/*.json`, `node_modules/`, `traces/`, `.env`

## Workflow changes

### `workflow.md` — thin orchestration doc

~30 lines, strictly the state machine for Athena CLI sessions:
- orient → analyze OR scaffold → plan → generate → review specs → write → review code → execute + re-run → stabilize
- Session boundaries and loop limits
- Delegation constraints (browser exploration + writing → subagents, execution → main agent only)
- Everything else lives in `add-robot-tests/SKILL.md`

### Gate 3 — re-run for stability

After the first green run, run the suite 2 more times (3 total) before claiming signoff. Any flakiness across those three runs triggers `fix-flaky-tests`. Maximum 3 fix-and-rerun cycles per suite per session — unchanged from current.

### Smoke-first discipline

`write-robot-code` Step 4 is mandatory:

> Write ONE happy-path test end-to-end. Run it. Get it green. THEN expand to the rest of the spec.

Rationale: writing 20 tests before running any of them is the #1 cause of cascading failures in Robot projects. A single passing test validates the resource imports, the locator dialect, the auth state, the teardown, the reporting — in one pass.

### Mandatory locator spot-check

`write-robot-code` Step 3 is mandatory:

> Before writing any locator into a test, verify it via `agent-web-interface-guide` browser tools. Record the verified locator and its source element. No exceptions.

Currently this is phrased as "spot-check 2-3 critical selectors" — it becomes mandatory for every locator.

## Dry-run target

`_dryrun/robot-sample/` — a throwaway Robot Framework project in the marketplace repo used to dogfood the refined plugin end-to-end. Not shipped to users.

- **Target site:** `https://practicetestautomation.com/practice-test-login/` — stable, public, purpose-built for automation
- **Scope:** 1 suite (`tests/login.robot`), 3 tests (happy path, wrong username, locked account)
- **Purpose:** end-to-end validation. Start from either an existing Robot target or an optionally scaffolded greenfield target, then run `/add-robot-tests` against the target, observe Gate 1 / Gate 2 / Gate 3 firing, re-run 3x for stability
- **Gitignore:** `_dryrun/**/results/`, `_dryrun/**/auth/`, `_dryrun/**/node_modules/` are ignored; the source files are kept in the repo so future refinements can re-validate
- **Cleanup:** anything in `_dryrun/` that mirrors the optional external scaffold/bootstrap repo should live there rather than being duplicated in this marketplace repo

## Delivery sequencing

This design doc is the foundation. The implementation plan (produced via `writing-plans`) will break it into phases. Approximate shape:

1. **Schema + conventions contract** — write `docs/robot-automation-conventions-schema.md` with the full schema and enum definitions
2. **`analyze-test-codebase` update** — emit `conventions.yaml` alongside the existing human report
3. **Optional external scaffold/bootstrap alignment** — greenfield template emits the same resilience toolkit and `conventions.yaml` contract without becoming a shipped skill here
4. **`write-robot-code` rewrite** — new locator hierarchy, `Promise To` pattern, smoke-first, mandatory spot-check
5. **`review-test-code` rewrite** — blocker/warning rules for the new dialect
6. **`plan-test-coverage`, `generate-test-cases`, `review-test-cases` touches** — dialect updates and `conventions.yaml` read
7. **`fix-flaky-tests` additions** — strict mode, Promise To race, run_on_failure, pabot env var, viewport/locale/TZ
8. **`add-robot-tests` + `workflow.md` dedupe** — single source of truth for operational guidance
9. **Dry-run target + end-to-end validation** — `_dryrun/robot-sample/` and one complete pipeline run
10. **Plugin metadata bump + marketplace.json update** — version bump from `0.1.0` to `0.2.0`

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| New locator dialect breaks users who have already written tests against the old plugin | Migration note in the plugin's README explaining the dialect change. The plugin is at `0.1.0` — no stable contract yet. |
| `conventions.yaml` schema evolves and breaks cross-skill contract | `version: 1` field on the artifact; schema changes bump the version. Skills check `version` on read. |
| Dry-run target becomes stale (target site changes, dependencies drift) | The target site is `practicetestautomation.com` — purpose-built for automation, stable by design. Dry-run is opt-in during development, not part of CI. |
| Optional bootstrap path encourages unnecessary re-scaffolding | Entry-point docs say scaffold is greenfield-only. Existing Robot projects stay in-place and are adapted via the shipped skills. |
| RetryFailed listener masks real flakiness | The recommended baseline sets `RetryFailed:1:True` — one retry max. The plugin's anti-patterns list already flags `--rerunfailed` without a root-cause fix as wrong. |

## Success criteria

1. Running `/add-robot-tests https://practicetestautomation.com/practice-test-login/ login` end-to-end produces a green `tests/login.robot` suite with 3+ tests that pass 3 consecutive runs.
2. `review-test-code` blocks any test file containing `role=` / `label=` / `placeholder=` as string selector prefixes.
3. `conventions.yaml` is read by every downstream skill and the read is testable (broken `version` fails loudly).
4. `workflow.md` and `add-robot-tests/SKILL.md` contain no duplicated substantive content.
5. The plugin's README migration note points to this design doc by file path.

## Out of scope for this refinement

- Visual regression testing integration
- Cross-browser matrix execution (WebKit/Firefox) — defaults to Chromium, users configure their own matrix
- Accessibility testing skill — exists abstractly in `plan-test-coverage` categories but no dedicated skill
- Performance testing via Browser library's `Browser.library.Get Performance Metrics`
- Visual regression via `Take Screenshot` baselines
- A separate `configure-robot-runtime` skill (runtime config folded into scaffold + analyze)

These are all valid future refinements but expand scope beyond what correcting correctness + adding resilience + adapting to existing codebases requires.
