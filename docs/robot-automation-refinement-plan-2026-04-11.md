# Robot Automation Plugin Refinement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the `robot-automation` plugin to teach the correct Browser library dialect, bake in proactive resilience primitives, adapt to existing codebases via a typed `conventions.yaml` contract, keep Robot-specific best practices inside the shipped skills, and treat scaffolding as an optional external bootstrap path for greenfield starts only.

**Architecture:** Keeps the shipped Robot workflow centered on the existing skills, corrects locator dialect (Playwright-JS → Robot Browser), introduces a machine-readable adaptation contract, dedupes workflow.md, and adds smoke-first + re-run-for-stability gates. Scaffolding is optional and external: the agent may clone a separate bootstrap project only when no Robot project exists and the user wants everything at once. Full design in `docs/robot-automation-refinement-2026-04-11.md`.

**Tech Stack:** Robot Framework 6.1+ / 7+, `robotframework-browser` (Browser library, Playwright-based), `pabot`, `robotframework-retryfailed`, Python 3.10+, Node 20/22/24 LTS (optional when using BrowserBatteries install path). Plugin artifacts are markdown skill files + JSON Schema + one Python validator.

**Validation strategy:** No unit test suite exists for plugin markdown content. Validation = (1) a JSON Schema validator for `conventions.yaml` with a pytest, (2) end-to-end execution of the refined plugin against an existing Robot target or a scaffolded dry-run target producing real `results/log.html`, re-run 3x for stability.

> **Implementation update:** references below to `scaffold-robot-project` should now be read as an optional external bootstrap repository, not a shipped marketplace skill. Brownfield adaptation and Robot-specific conventions remain in the marketplace skills.

---

## Phase 0 — Design artifacts and schema

### Task 0.1: Create conventions schema JSON

**Files:**
- Create: `plugins/robot-automation/schemas/conventions.schema.json`

- [ ] **Step 1: Create the schema file**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/lespaceman/athena-workflow-marketplace/plugins/robot-automation/schemas/conventions.schema.json",
  "title": "Robot Automation Conventions Contract",
  "description": "Typed contract between analyze-test-codebase / scaffold-robot-project (writers) and all downstream skills (readers). The artifact is written to e2e-plan/conventions.yaml at project root.",
  "type": "object",
  "required": ["version", "framework", "layout", "runtime", "conventions", "parallel", "base_url", "observations"],
  "additionalProperties": false,
  "properties": {
    "version": {
      "const": 1,
      "description": "Schema version. Readers fail loudly if this does not match their expected version."
    },
    "framework": {
      "type": "object",
      "required": ["robot_framework", "robotframework_browser", "python", "rfbrowser_initialized"],
      "additionalProperties": false,
      "properties": {
        "robot_framework": {"type": ["string", "null"]},
        "robotframework_browser": {"type": ["string", "null"]},
        "python": {"type": ["string", "null"]},
        "node": {"type": ["string", "null"], "description": "null when using BrowserBatteries install path"},
        "rfbrowser_initialized": {"type": "boolean"}
      }
    },
    "layout": {
      "type": "object",
      "required": ["tests_dir", "resources_dir", "output_dir"],
      "additionalProperties": false,
      "properties": {
        "tests_dir": {"type": "string"},
        "resources_dir": {"type": "string"},
        "variables_file": {"type": ["string", "null"]},
        "output_dir": {"type": "string"}
      }
    },
    "runtime": {
      "type": "object",
      "required": ["runner_config", "strict_mode", "auto_closing_level", "run_on_failure", "listeners", "default_timeout"],
      "additionalProperties": false,
      "properties": {
        "runner_config": {"enum": ["robot.toml", "__init__.robot", "none"]},
        "strict_mode": {"type": "boolean"},
        "auto_closing_level": {"enum": ["TEST", "SUITE", "MANUAL", "KEEP"]},
        "run_on_failure": {"type": ["string", "null"]},
        "listeners": {"type": "array", "items": {"type": "string"}},
        "default_timeout": {"type": "string"}
      }
    },
    "conventions": {
      "type": "object",
      "required": ["locator_style", "resource_pattern", "auth_strategy", "test_data_strategy", "tag_vocabulary"],
      "additionalProperties": false,
      "properties": {
        "locator_style": {"enum": ["get_element_by_role_first", "css_first", "legacy_mixed"]},
        "resource_pattern": {"enum": ["common+feature", "monolithic", "none"]},
        "auth_strategy": {"enum": ["persisted_storage_state", "per_test", "api_token", "none"]},
        "test_data_strategy": {"enum": ["requests_library_api", "ui_setup", "fixtures", "none"]},
        "tag_vocabulary": {"type": "array", "items": {"type": "string"}}
      }
    },
    "parallel": {
      "type": "object",
      "required": ["enabled", "mode"],
      "additionalProperties": false,
      "properties": {
        "enabled": {"type": "boolean"},
        "mode": {"enum": ["suite", "test", "disabled"]},
        "pabotlib": {"type": "boolean"},
        "resource_file": {"type": ["string", "null"]}
      }
    },
    "base_url": {
      "type": "object",
      "required": ["source"],
      "additionalProperties": false,
      "properties": {
        "source": {"enum": ["variables.py", "env", "hardcoded", "robot.toml"]},
        "value_example": {"type": "string"}
      }
    },
    "observations": {
      "type": "object",
      "required": ["generated_at", "generated_by", "notes"],
      "additionalProperties": false,
      "properties": {
        "generated_at": {"type": "string", "format": "date-time"},
        "generated_by": {"enum": ["analyze-test-codebase", "scaffold-robot-project"]},
        "notes": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/schemas/conventions.schema.json
git commit -m "feat(robot-automation): add conventions.yaml JSON Schema contract"
```

### Task 0.2: Create validator script + pytest

**Files:**
- Create: `plugins/robot-automation/schemas/validate_conventions.py`
- Create: `plugins/robot-automation/schemas/test_conventions.py`
- Create: `plugins/robot-automation/schemas/fixtures/valid-minimal.yaml`
- Create: `plugins/robot-automation/schemas/fixtures/valid-full.yaml`
- Create: `plugins/robot-automation/schemas/fixtures/invalid-version.yaml`
- Create: `plugins/robot-automation/schemas/fixtures/invalid-missing-field.yaml`

- [ ] **Step 1: Write failing tests first**

```python
# plugins/robot-automation/schemas/test_conventions.py
"""Tests for conventions.yaml schema validation.

Run from the marketplace repo root:
    python -m pytest plugins/robot-automation/schemas/test_conventions.py -v
"""
import pathlib

import pytest

from validate_conventions import ConventionsError, validate_file

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def test_valid_minimal_fixture_passes():
    validate_file(FIXTURES / "valid-minimal.yaml")


def test_valid_full_fixture_passes():
    validate_file(FIXTURES / "valid-full.yaml")


def test_wrong_version_is_rejected():
    with pytest.raises(ConventionsError, match="version"):
        validate_file(FIXTURES / "invalid-version.yaml")


def test_missing_required_field_is_rejected():
    with pytest.raises(ConventionsError, match="required"):
        validate_file(FIXTURES / "invalid-missing-field.yaml")


def test_unknown_field_is_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        (FIXTURES / "valid-minimal.yaml").read_text() + "\nunknown_field: 42\n"
    )
    with pytest.raises(ConventionsError, match="unknown_field|additionalProperties"):
        validate_file(bad)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest plugins/robot-automation/schemas/test_conventions.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'validate_conventions'`

- [ ] **Step 3: Write minimal validator implementation**

```python
# plugins/robot-automation/schemas/validate_conventions.py
"""Validator for conventions.yaml against conventions.schema.json.

Usage:
    python validate_conventions.py <path/to/conventions.yaml>
"""
from __future__ import annotations

import json
import pathlib
import sys

import jsonschema
import yaml

SCHEMA_PATH = pathlib.Path(__file__).parent / "conventions.schema.json"


class ConventionsError(RuntimeError):
    """Raised when conventions.yaml fails schema validation."""


def _load_schema() -> dict:
    with SCHEMA_PATH.open() as fh:
        return json.load(fh)


def validate_file(path: pathlib.Path | str) -> dict:
    """Load and validate a conventions.yaml file.

    Returns the parsed document on success. Raises ConventionsError with
    a human-readable message on failure.
    """
    path = pathlib.Path(path)
    with path.open() as fh:
        doc = yaml.safe_load(fh)
    try:
        jsonschema.validate(doc, _load_schema())
    except jsonschema.ValidationError as exc:
        raise ConventionsError(f"{path}: {exc.message}") from exc
    return doc


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_conventions.py <path>", file=sys.stderr)
        return 2
    try:
        validate_file(argv[1])
    except ConventionsError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Create valid-minimal fixture**

```yaml
# plugins/robot-automation/schemas/fixtures/valid-minimal.yaml
version: 1
framework:
  robot_framework: null
  robotframework_browser: null
  python: null
  node: null
  rfbrowser_initialized: false
layout:
  tests_dir: "tests/"
  resources_dir: "resources/"
  variables_file: null
  output_dir: "results/"
runtime:
  runner_config: "none"
  strict_mode: true
  auto_closing_level: "SUITE"
  run_on_failure: null
  listeners: []
  default_timeout: "10s"
conventions:
  locator_style: "get_element_by_role_first"
  resource_pattern: "none"
  auth_strategy: "none"
  test_data_strategy: "none"
  tag_vocabulary: []
parallel:
  enabled: false
  mode: "disabled"
base_url:
  source: "hardcoded"
observations:
  generated_at: "2026-04-11T00:00:00Z"
  generated_by: "scaffold-robot-project"
  notes: ["greenfield scaffold"]
```

- [ ] **Step 5: Create valid-full fixture**

```yaml
# plugins/robot-automation/schemas/fixtures/valid-full.yaml
version: 1
framework:
  robot_framework: "7.2.1"
  robotframework_browser: "19.12.5"
  python: "3.11"
  node: "22"
  rfbrowser_initialized: true
layout:
  tests_dir: "tests/"
  resources_dir: "resources/"
  variables_file: "variables.py"
  output_dir: "results/"
runtime:
  runner_config: "robot.toml"
  strict_mode: true
  auto_closing_level: "SUITE"
  run_on_failure: "Take Screenshot failure-{index} fullPage=True"
  listeners:
    - "RetryFailed:1:True"
  default_timeout: "10s"
conventions:
  locator_style: "get_element_by_role_first"
  resource_pattern: "common+feature"
  auth_strategy: "persisted_storage_state"
  test_data_strategy: "requests_library_api"
  tag_vocabulary:
    - "smoke"
    - "critical"
    - "TC-*"
parallel:
  enabled: true
  mode: "suite"
  pabotlib: true
  resource_file: "users.dat"
base_url:
  source: "variables.py"
  value_example: "https://staging.example.com"
observations:
  generated_at: "2026-04-11T12:00:00Z"
  generated_by: "analyze-test-codebase"
  notes: []
```

- [ ] **Step 6: Create invalid-version fixture**

```yaml
# plugins/robot-automation/schemas/fixtures/invalid-version.yaml
version: 99
framework:
  robot_framework: null
  robotframework_browser: null
  python: null
  node: null
  rfbrowser_initialized: false
layout:
  tests_dir: "tests/"
  resources_dir: "resources/"
  variables_file: null
  output_dir: "results/"
runtime:
  runner_config: "none"
  strict_mode: true
  auto_closing_level: "SUITE"
  run_on_failure: null
  listeners: []
  default_timeout: "10s"
conventions:
  locator_style: "get_element_by_role_first"
  resource_pattern: "none"
  auth_strategy: "none"
  test_data_strategy: "none"
  tag_vocabulary: []
parallel:
  enabled: false
  mode: "disabled"
base_url:
  source: "hardcoded"
observations:
  generated_at: "2026-04-11T00:00:00Z"
  generated_by: "scaffold-robot-project"
  notes: []
```

- [ ] **Step 7: Create invalid-missing-field fixture**

```yaml
# plugins/robot-automation/schemas/fixtures/invalid-missing-field.yaml
# Missing top-level "runtime" key
version: 1
framework:
  robot_framework: null
  robotframework_browser: null
  python: null
  node: null
  rfbrowser_initialized: false
layout:
  tests_dir: "tests/"
  resources_dir: "resources/"
  variables_file: null
  output_dir: "results/"
conventions:
  locator_style: "get_element_by_role_first"
  resource_pattern: "none"
  auth_strategy: "none"
  test_data_strategy: "none"
  tag_vocabulary: []
parallel:
  enabled: false
  mode: "disabled"
base_url:
  source: "hardcoded"
observations:
  generated_at: "2026-04-11T00:00:00Z"
  generated_by: "scaffold-robot-project"
  notes: []
```

- [ ] **Step 8: Install dependencies if needed and re-run tests**

Run:
```bash
python3 -m pip install --user jsonschema pyyaml pytest
cd plugins/robot-automation/schemas
python -m pytest test_conventions.py -v
```
Expected: 5 passed.

- [ ] **Step 9: Commit**

```bash
git add plugins/robot-automation/schemas/
git commit -m "feat(robot-automation): add conventions.yaml validator + tests"
```

---

## Phase 1 — Optional external scaffold integration

### Task 1.1: Update docs to treat scaffold as optional external bootstrap only

**Files:**
- Update: `docs/robot-automation-refinement-2026-04-11.md`
- Update: `workflows/robot-automation/workflow.md`
- Update: `plugins/robot-automation/skills/add-robot-tests/SKILL.md`

- [ ] **Step 1: Remove any implication that scaffold is a shipped skill**

Replace those references with: the scaffold is an external repository the agent may clone only when no Robot project exists and the user wants an all-at-once bootstrap.

- [ ] **Step 2: Keep best practices inside shipped skills**

Make sure the docs say Browser-library conventions, locator dialect, resilience primitives, brownfield adaptation, and review gates remain inside `analyze-test-codebase`, `write-robot-code`, `review-test-code`, and `fix-flaky-tests`.

- [ ] **Step 3: Commit**

```bash
git add docs/robot-automation-refinement-2026-04-11.md workflows/robot-automation/workflow.md plugins/robot-automation/skills/add-robot-tests/SKILL.md
git commit -m "refactor(robot-automation): make scaffold optional external bootstrap"
```

### Task 1.2: Keep `conventions.yaml` compatible with external scaffold output

**Files:**
- Update: `plugins/robot-automation/schemas/conventions.schema.json`
- Update: `plugins/robot-automation/schemas/fixtures/*.yaml`

- [ ] **Step 1: Preserve a writer identifier for greenfield bootstrap**

The schema may still allow a scaffold-oriented `generated_by` value, but the docs must treat it as output from an optional external bootstrap repository rather than a local marketplace skill.

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/schemas/
git commit -m "docs(robot-automation): clarify external scaffold conventions writer"
```

```bash
git add plugins/robot-automation/skills/scaffold-robot-project/references/brownfield-upgrade.md
git commit -m "feat(robot-automation): brownfield upgrade reference"
```

### Task 1.6: Delete the old scaffolding.md reference

**Files:**
- Delete: `plugins/robot-automation/skills/add-robot-tests/references/scaffolding.md`
- Modify: `plugins/robot-automation/skills/add-robot-tests/SKILL.md` (remove the reference link)

- [ ] **Step 1: Delete the file**

```bash
git rm plugins/robot-automation/skills/add-robot-tests/references/scaffolding.md
```

- [ ] **Step 2: Update add-robot-tests/SKILL.md to point at the new skill**

Find the Scaffolding section in `plugins/robot-automation/skills/add-robot-tests/SKILL.md` (currently around line 142):

Replace:
```markdown
## Scaffolding

If Robot Framework + Browser library is not set up in the target project, use the optional external scaffold/bootstrap repo only when the user wants a full greenfield bootstrap. Otherwise stay in the current repository and use the shipped skills directly.
```

With:
```markdown
## Scaffolding

If Robot Framework + Browser library is not set up in the target project, the agent may clone the optional external scaffold/bootstrap repo when the user wants a full greenfield bootstrap. If Robot is already present but missing resilience primitives (strict mode, `run_on_failure`, RetryFailed listener, viewport/locale/timezone pinning), handle that inside the shipped skills as an additive brownfield improvement. Do not treat scaffold as the brownfield path.
```

- [ ] **Step 3: Commit**

```bash
git add plugins/robot-automation/skills/add-robot-tests/
git commit -m "refactor(robot-automation): move scaffolding into scaffold-robot-project skill"
```

---

## Phase 2 — `analyze-test-codebase` emits `conventions.yaml`

### Task 2.1: Update analyze-test-codebase/SKILL.md to emit conventions.yaml

**Files:**
- Modify: `plugins/robot-automation/skills/analyze-test-codebase/SKILL.md`

- [ ] **Step 1: Add a new workflow step for conventions.yaml emission**

Read the current `plugins/robot-automation/skills/analyze-test-codebase/SKILL.md`. After the existing Step 6 (Generate report) section, add a new Step 7:

```markdown
## Step 7: Emit `conventions.yaml` (typed contract)

In addition to the human-readable report, produce a machine-readable `conventions.yaml` at project root for downstream skills to read. This is a strict, versioned contract validated against `plugins/robot-automation/schemas/conventions.schema.json`.

### Field sources

| Field | How to derive |
|---|---|
| `version` | Always `1` |
| `framework.robot_framework` | `python3 -m robot --version` output |
| `framework.robotframework_browser` | `python3 -m pip show robotframework-browser` — Version line |
| `framework.python` | `python3 --version` |
| `framework.node` | `node --version` if present; `null` otherwise (BrowserBatteries path) |
| `framework.rfbrowser_initialized` | Check for `~/.cache/rfbrowser` or the library's install marker |
| `layout.*` | Directory glob results |
| `runtime.runner_config` | Which of `robot.toml` / `__init__.robot` / `none` is present |
| `runtime.strict_mode` | Parse `Library Browser` import for `strict=False`; `Set Strict Mode False` scope |
| `runtime.auto_closing_level` | Parse `Library Browser` import |
| `runtime.run_on_failure` | Parse `Library Browser` import |
| `runtime.listeners` | Parse `robot.toml` `listener` array OR CLI scripts for `--listener` |
| `runtime.default_timeout` | Parse for `Set Browser Timeout` / `Browser timeout` import arg; default `10s` if absent |
| `conventions.locator_style` | Sample 3 `.robot` files; if majority use `Get Element By *` keywords → `get_element_by_role_first`; if majority use `css=` / `xpath=` → `css_first`; mixed → `legacy_mixed` |
| `conventions.resource_pattern` | `resources/common.resource` + `resources/<feature>.resource` layout → `common+feature`; everything in one file → `monolithic`; no resources dir → `none` |
| `conventions.auth_strategy` | Grep for `Save Storage State` / `storageState` → `persisted_storage_state`; `POST` to `/login` or `auth.*` API calls → `api_token`; every test calls a Log In keyword → `per_test`; no auth → `none` |
| `conventions.test_data_strategy` | Grep for `RequestsLibrary` usage → `requests_library_api`; fixtures dir → `fixtures`; UI form fills for setup → `ui_setup`; nothing → `none` |
| `conventions.tag_vocabulary` | Aggregate `[Tags]` values + `robot.toml` `[tags]` table |
| `parallel.*` | Grep CI scripts for `pabot`; detect `--resourcefile`; detect `--pabotlib` |
| `base_url.source` | Grep `variables.py` for `BASE_URL`; `robot.toml` `[variables]` table; hardcoded `https://…` in `.robot` files |
| `observations.generated_*` | Current ISO-8601 UTC; `analyze-test-codebase` |

### Validation

Before writing, validate the draft against the schema using the helper:

```bash
python3 plugins/robot-automation/schemas/validate_conventions.py e2e-plan/conventions.yaml
```

A schema validation failure is a blocker — do not write an invalid file. Report the validation error and stop.

### Write location

Write to `e2e-plan/conventions.yaml` at the target project root (not inside the plugin). The `e2e-plan/` directory is the canonical working-notes location for this workflow (already used for `e2e-plan/conventions.md` in historical review skills).

### Fallback for fields that cannot be inferred

When a field cannot be determined from the codebase (e.g. `framework.rfbrowser_initialized` in a sandbox with no filesystem access), set it to `null` or the explicit enum value `"none"` rather than guessing. Add a line to `observations.notes` explaining which fields were inferred conservatively.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/analyze-test-codebase/SKILL.md
git commit -m "feat(robot-automation): analyze-test-codebase emits conventions.yaml"
```

---

## Phase 3 — `write-robot-code` locator dialect rewrite

### Task 3.1: Rewrite the Locator Strategy section

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/SKILL.md`

- [ ] **Step 1: Replace the Locator Strategy table (currently lines ~86-98)**

Find the existing section headed `### Locator Strategy (Browser library)` in `plugins/robot-automation/skills/write-robot-code/SKILL.md`. Replace the entire table + the paragraphs that follow (up to and including the "Within-file consistency" paragraph) with:

```markdown
### Locator Strategy (Browser library)

The Browser library documents only four prefixed selector engines: `css=`, `xpath=`, `text=`, `id=`. **`role=`, `label=`, `placeholder=`, `alt=`, `title=`, `testid=` are NOT valid selector-string prefixes** — they are Playwright-JS syntax and do not work as string selectors in Robot Framework. The library exposes role/label/placeholder/alt/title/testid lookup via dedicated `Get Element By *` keywords that return Locator references.

**Priority order** (enforced by `review-test-code`):

| Priority | Pattern | When to use |
|---|---|---|
| 1 | `Get Element By Role    button    name=Submit` (keyword call, returns Locator) | Semantic elements: buttons, links, headings, form controls |
| 2 | `Get Element By Label    Email` | Form inputs with visible labels |
| 3 | `Get Element By Placeholder    Search…` | Inputs identified by placeholder |
| 4 | `Get Element By Test Id    submit-button` | When the dev team provides `data-testid` |
| 5 | `text="Welcome"` or `text=/welcome/i` | Short, stable text (JavaScript regex, not Python) |
| 6 | `id=login_btn` | Stable static IDs |
| 7 | `css=main >> .card:not(.hidden)` with `>>` scoping | Last-resort CSS, scoped to a container |
| 8 | `xpath=//button[@data-qa='x']` | Absolute last resort. Requires a `# WHY:` comment on the line above. |

**Scoping pattern** — use the `parent=` argument on `Get Element By *` calls to scope to a container without chaining string selectors:

```robotframework
${dialog}=     Get Element By Role    dialog    name=Confirm delete
${confirm}=    Get Element By Role    button    name=Delete    parent=${dialog}
Click          ${confirm}
```

**iframe piercing** uses `>>>` (three angles), not `>>`:

```robotframework
Click    id=payment-iframe >>> id=pay-button
```

**Strict mode is ON by default.** A selector that matches multiple elements raises an error — no silent first-match. Do not disable strict mode without a `# WHY:` comment and a scoped `Set Strict Mode    False    scope=Suite`. Scoped disables auto-reset at suite end.

**Banned:**
- `role=` / `label=` / `placeholder=` / `alt=` / `title=` / `testid=` as string selector prefixes — **BLOCKER** (not documented engines)
- `>> nth=N` without a documented reason — **WARNING** (strict mode catches ambiguity loudly; scope instead)
- Utility-class selectors (Tailwind `.btn-primary`, Bootstrap `.col-md-6`) — **BLOCKER** (styling, not identity)
- `force=True` on actions without a `# WHY:` comment — **WARNING** (masks overlap, disabled state, un-scrolled)

**Within-file consistency:** every `.robot` file MUST use one approach for equivalent elements. Do not mix `Get Element By Role` in one test with `css=button` in another within the same file. When adding tests to an existing file, match the existing style; if the existing style is `css_first` (per `conventions.yaml`), stay in that dialect unless the user asks for a migration.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/SKILL.md
git commit -m "feat(robot-automation): correct locator dialect in write-robot-code"
```

### Task 3.2: Rewrite the Waiting Strategy section with Promise To as default

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/SKILL.md`

- [ ] **Step 1: Replace the Waiting Strategy section**

Find the section headed `### Waiting Strategy` in `plugins/robot-automation/skills/write-robot-code/SKILL.md`. Replace with:

```markdown
### Waiting Strategy

**Auto-waits first.** Browser library's click / fill / assert keywords auto-wait for elements to become actionable. You rarely need explicit waits for presence.

**Explicit element state waits.** When you need a specific state transition (loading spinner gone, button enabled), use:

```robotframework
Wait For Elements State    role=progressbar    hidden     timeout=10s
Wait For Elements State    ${submit}            enabled    timeout=5s
```

**Network-driven actions use the `Promise To` + `Wait For` pattern.** This is the default for any click / fill that triggers a network call — not an advanced technique. Maintainer Mikko Korpela on the Robot Framework forum:

> "There is a possibility that the click-related request response happens before you attach the wait if wait is done after."

The wait must be attached **before** the action. Pattern:

```robotframework
${promise}=    Promise To    Wait For Response    matcher=**/api/session    timeout=10s
Click          role=button[name="Sign in"]
${response}=   Wait For    ${promise}
```

**Matcher gotcha.** `matcher=` uses:
- URL glob form: `**/api/session` — preferred for most cases
- JavaScript regex: `/\/api\/items/i` — NOT Python regex
- JS predicate function as a string: `async (response) => response.url().endsWith('/status') && response.status() === 200`

**Do not use `networkidle`-style waits.** Browser library has no exact equivalent, but any custom "wait for all network done" keyword is fragile — breaks on long-polling, WebSockets, analytics beacons. Wait on the specific response you care about.

**Assertion retries.** Browser library assertions with operators (`==`, `contains`, `*=`, `matches`) auto-retry until the keyword's `timeout` before failing. Use them instead of single-shot `Should Be Equal` on snapshot values:

```robotframework
# GOOD — auto-retries
Get Text    role=alert    contains    Invalid email    timeout=5s

# BAD — one-shot, fails on any timing drift
${text}=    Get Text    role=alert
Should Contain    ${text}    Invalid email
```

(NOTE: the examples above use short notation for readability. The priority-1 rewrite is `Get Element By Role alert` returning a locator — see the Locator Strategy section.)
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/SKILL.md
git commit -m "feat(robot-automation): promote Promise To pattern to first-class"
```

### Task 3.3: Add smoke-first discipline and mandatory spot-check

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/SKILL.md`

- [ ] **Step 1: Replace Step 3 (Verify Key Selectors) with a mandatory version**

Find the existing `### 3. Verify Key Selectors Against the Live Site` section. Replace with:

```markdown
### 3. Verify Every Locator Against the Live Site (MANDATORY)

Before writing any locator into a test, verify it against the live site using `agent-web-interface-guide` browser tools. This is not optional.

- If a test case spec file includes **Selectors observed**, use those as your starting point and spot-check 1 in 3 to confirm they still resolve
- If no spec or selectors are available, browse the target page, use `find` / `get_element` / `get_form` to capture the canonical locator, and record it in your working notes before writing any test code
- For every locator that ends up in the test suite, record the source element (role, accessible name, label, test-id, containing section) in a comment or in the `test-cases/<feature>.md` spec
- **Strict mode catches ambiguity loudly.** If `find` returns more than one match, scope the locator to a container via `parent=` or `>> ` chaining before proceeding
- Translate exploration locators into Browser library syntax following the Locator Strategy priority order (Get Element By Role, Get Element By Label, …, css= as last resort)

Writing tests with unverified locators is the single biggest cause of wasted rework. The time spent verifying is always less than the time spent debugging cascading failures downstream.
```

- [ ] **Step 2: Insert a new Step 4.5 for smoke-first discipline**

Find the existing `### 4. Implement Tests` section. After its bullet list ends and before `### 5. Stabilize`, insert:

```markdown
### 4.5. Smoke-First Gate (MANDATORY)

Before expanding to the full spec, write ONE happy-path test end-to-end and run it. Get it green. THEN write the rest.

Reason: writing 20 tests before running any of them is the #1 cause of cascading failures in Robot Framework projects. A single passing test validates the resource imports, the locator dialect, the auth state, the teardown, and the reporting — in one pass. If any of those are broken, you find out after 2 minutes of work instead of 20.

Concretely:

1. Write the resource file keywords the happy path needs (Page Object style) in `resources/<feature>.resource`
2. Write `TC-<FEATURE>-001` — the simplest happy path — in `tests/<feature>.robot`
3. Run `robot -d results -t "TC-<FEATURE>-001*" tests/<feature>.robot 2>&1`
4. Inspect `results/log.html` — confirm green
5. If red, diagnose and fix BEFORE writing TC-002. Do not pile more tests on a broken foundation.
6. Only after TC-001 is green: proceed to write TC-002, TC-003, etc.

This gate is not a suggestion. The review-test-code skill flags test suites containing more than one new test with no corresponding run evidence as a WARNING.
```

- [ ] **Step 3: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/SKILL.md
git commit -m "feat(robot-automation): mandatory locator spot-check + smoke-first gate"
```

### Task 3.4: Add conventions.yaml read to Step 2

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/SKILL.md`

- [ ] **Step 1: Update Step 2 to read conventions.yaml first**

Find the existing `### 2. Inspect Repo Conventions (CRITICAL — before writing any code)` section. Replace its first bullet with:

```markdown
- **Read `e2e-plan/conventions.yaml` first.** If it exists, validate it against `plugins/robot-automation/schemas/conventions.schema.json` and use it as the source of truth for locator style, resource pattern, auth strategy, test data strategy, tag vocabulary, and parallel mode. **If it does not exist, stop and run the `analyze-test-codebase` skill first** — writing code without knowing the conventions is how you get convention divergence blockers in review.
- Search for `robot.toml`, `pyproject.toml`, `requirements*.txt` — confirm `robotframework-browser` is installed and extract any `outputdir`, default tags, and listeners
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/SKILL.md
git commit -m "feat(robot-automation): write-robot-code reads conventions.yaml"
```

### Task 3.5: Update the Test Template

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/SKILL.md`

- [ ] **Step 1: Replace the Test Template**

Find the existing `## Test Template` section. Replace with:

```markdown
## Test Template

```robotframework
*** Settings ***
Documentation     Login feature E2E suite.
Resource          ../resources/common.resource
Resource          ../resources/login.resource
Suite Setup       Open Browser To Base URL
Suite Teardown    Close Browser
Test Tags         login    smoke

*** Variables ***
${VALID_EMAIL}       %{TEST_USER_EMAIL}
${VALID_PASSWORD}    %{TEST_USER_PASSWORD}

*** Test Cases ***
TC-LOGIN-001 User can log in with valid credentials
    [Documentation]    Happy path login redirects to dashboard.
    [Tags]    TC-LOGIN-001    critical
    Go To    ${BASE_URL}/login
    ${email}=       Get Element By Label       Email
    ${password}=    Get Element By Label       Password
    ${signin}=      Get Element By Role        button    name=Sign in
    Fill Text       ${email}       ${VALID_EMAIL}
    Fill Secret     ${password}    $VALID_PASSWORD
    ${promise}=     Promise To    Wait For Response    matcher=**/api/session    timeout=10s
    Click           ${signin}
    Wait For        ${promise}
    Get Url         contains    /dashboard    timeout=5s
    ${welcome}=     Get Element By Role    heading    name=/welcome/i
    Get Element States    ${welcome}    *=    visible
```

**Things this template demonstrates:**

1. `Get Element By Role` / `Get Element By Label` as priority 1 and 2 — returns Locator references bound to local variables
2. `Fill Secret` (not `Fill Text`) for sensitive fields — redacts the value in logs
3. `Promise To` + `Click` + `Wait For` pattern — race-free network-driven action
4. `Get Url contains /dashboard` — auto-retrying URL assertion
5. `Get Element States ${welcome} *= visible` — auto-retrying visibility assertion on a locator reference
6. `%{TEST_USER_EMAIL}` / `$VALID_PASSWORD` — env-var sourcing, never hardcoded
7. Tags include `TC-LOGIN-001` so `--include TC-LOGIN-001` filters cleanly
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/SKILL.md
git commit -m "feat(robot-automation): update test template to canonical dialect"
```

### Task 3.6: Update Anti-Patterns (quick reference) list

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/SKILL.md`

- [ ] **Step 1: Replace the Anti-Patterns quick-reference list**

Find the existing `## Anti-Patterns (Quick Reference)` section. Replace its numbered list with:

```markdown
1. `role=` / `label=` / `placeholder=` / `alt=` / `title=` / `testid=` as STRING selector prefixes — not documented Browser library engines. Use `Get Element By Role` / `Get Element By Label` / etc. keywords instead.
2. Raw CSS / XPath selectors where a `Get Element By Role` / `Get Element By Label` / `Get Element By Test Id` would work
3. `Sleep` — use `Wait For Elements State` / `Wait For Response` / `Promise To`
4. Fragile `>> nth=N` — scope with `parent=` or a container chain. Strict mode catches ambiguity; silencing it with `nth=0` hides real bugs.
5. Exact long text matches — use `text=/regex/i` with key words (JavaScript regex syntax)
6. Unscoped locators — use `parent=` on `Get Element By *` or scope CSS to a container via `>>`
7. Login via UI in every test — reuse persisted context state (`Save Storage State` / `New Context storageState=`)
8. UI clicks for test data setup — use `RequestsLibrary`
9. No error path tests — add failure scenarios via Browser library route mocking keywords
10. Hardcoded test data — use API setup + dynamic values from `Evaluate time.time_ns()` / `Generate Random String`
11. Tests depending on execution order
12. `Run Keyword And Ignore Error` wrapping assertions — silent failure, BLOCKER
13. `force=True` without a `# WHY:` comment — masks actionability issues
14. `Click` followed by a bare `Wait For Response` — race condition. Use `Promise To` + `Click` + `Wait For` instead.
15. `Sleep` after navigation instead of `Wait For Elements State` / `Wait For Response`
16. Utility-class selectors (Tailwind `.btn-primary`, Bootstrap `.col-md-6`) — styling, not identity. BLOCKER.
17. Asserting exact server-computed values — use patterns, ranges, or seed via API
18. `Set Strict Mode False` without a `# WHY:` comment — silences the library's built-in ambiguity check
19. `matcher=` written as Python regex — Browser library uses JavaScript regex semantics
20. `PABOT_QUEUE_INDEX` — typo. The env var is `PABOTQUEUEINDEX` (no underscores).

See [references/anti-patterns.md](references/anti-patterns.md) for detailed explanations and fix strategies.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/SKILL.md
git commit -m "feat(robot-automation): update write-robot-code anti-pattern list"
```

---

## Phase 4 — `write-robot-code` references updates

### Task 4.1: Rewrite anti-patterns.md items 1-5

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/references/anti-patterns.md`

- [ ] **Step 1: Replace items 1-5 with new dialect-aware content**

Open `plugins/robot-automation/skills/write-robot-code/references/anti-patterns.md`. Replace sections `## 1. Raw CSS / XPath selectors` through `## 5. Unscoped locators` (inclusive) with:

```markdown
## 1. `role=` / `label=` / `placeholder=` / `alt=` / `title=` / `testid=` as string selector prefixes

These are Playwright-JS selector engine prefixes that **do not work** as string selectors in Robot Framework's Browser library. The Browser library documents only four prefixed engines: `css=`, `xpath=`, `text=`, `id=`. Using `role=button[name="Submit"]` as a string selector will not target elements the way you expect — it may silently match something else or fail non-obviously.

**Fix:** use the dedicated `Get Element By *` keywords that return Locator references.

```robotframework
# BAD — role= is not a documented Browser library engine
Click    role=button[name="Submit"]

# GOOD — Get Element By Role returns a Locator reference
${submit}=    Get Element By Role    button    name=Submit
Click         ${submit}
```

Available keywords: `Get Element By Role`, `Get Element By Label`, `Get Element By Placeholder`, `Get Element By Test Id`, `Get Element By Alt Text`, `Get Element By Title`, `Get Element By Text`. Each accepts a `parent=` argument for scoping and optional `all_elements=True` for list returns.

## 2. Raw CSS / XPath selectors where a Get Element By keyword would work

Even after correcting the dialect, raw `css=.submit-btn` or `xpath=//button` is still wrong when `Get Element By Role button name=Submit` is possible. CSS breaks on class renames; XPath breaks on DOM restructures. Semantic locators survive both.

**Fix:** follow the priority order in `write-robot-code/SKILL.md`'s Locator Strategy section. Use `css=` and `xpath=` only as fallbacks #7 and #8, and scope them to a container with `>>`.

## 3. `Sleep`

Use event-driven waits. `Sleep 2s` that works locally may be too short in CI (slower machines) or too long (wasted time). It also hides the real question: "what am I actually waiting for?"

**Fix:**
- `Wait For Response matcher=**/api/data` for API-dependent UI
- `Wait For Elements State <locator> visible/hidden/enabled` for element state
- `Promise To Wait For Response` + `Click` + `Wait For` for race-free network-triggered actions
- Rely on Browser library auto-waits for the simple cases

## 4. Fragile `>> nth=N` / positional selectors

Browser library has strict mode ON by default — a selector matching multiple elements raises an error. `>> nth=0` silences that error without fixing the ambiguity, and will silently pick the wrong element when the DOM reorders.

**Fix:** scope with `parent=` on `Get Element By *`, or chain to a container in the underlying CSS:

```robotframework
# BAD — hides ambiguity
Click    role=listitem >> nth=0

# GOOD — use Get Element By Role on the list, then scope
${list}=    Get Element By Role    list    name=Cart items
${first}=   Get Element By Role    listitem    parent=${list}    name=/^Widget/

# GOOD (legacy dialect) — scoped CSS chain
Click    [data-testid="cart-list"] >> css=li:first-of-type
```

Only use `nth=N` when order genuinely is the semantics (ranking lists, chronological feeds), and add a `# WHY:` comment next to the call.

## 5. Unscoped locators

A page-wide `Get Element By Role button name=Submit` with strict mode ON will fail if the page has a header submit and a footer submit and a modal submit. Strict mode surfaces the ambiguity; your fix is to scope, not to silence.

**Fix:** use `parent=`:

```robotframework
${main}=       Get Element By Role    main
${submit}=     Get Element By Role    button    name=Submit    parent=${main}
Click          ${submit}
```

Or scope with CSS first when you need structural scoping:

```robotframework
${dialog}=     Get Element By Role    dialog    name=Confirm
${ok}=         Get Element By Role    button    name=OK    parent=${dialog}
Click          ${ok}
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/references/anti-patterns.md
git commit -m "feat(robot-automation): anti-patterns.md items 1-5 use correct dialect"
```

### Task 4.2: Rewrite mapping-tables.md

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/references/mapping-tables.md`

- [ ] **Step 1: Replace the Target Kind to Locator table**

Open `plugins/robot-automation/skills/write-robot-code/references/mapping-tables.md`. Replace the `## Target Kind to Locator` table with:

```markdown
## Target Kind to Locator

| Target Kind | Value Pattern | Robot Browser Library |
|-------------|--------------|------------------------|
| `role`  | `button name~Add to Bag` | `Get Element By Role    button    name=Add to Bag` |
| `role`  | `radio name~256GB`        | `Get Element By Role    radio    name=256GB` |
| `label` | `Email address`           | `Get Element By Label   Email address` |
| `placeholder` | `Search…`            | `Get Element By Placeholder    Search…` |
| `testid` | `checkout-button`        | `Get Element By Test Id    checkout-button` |
| `alt`   | `Company logo`            | `Get Element By Alt Text    Company logo` |
| `title` | `Close dialog`            | `Get Element By Title    Close dialog` |
| `text`  | `Welcome back`            | `Get Element By Text    Welcome back` (or `text="Welcome back"` / `text=/welcome/i` as a string selector) |
| `id`    | `login-btn`               | `id=login-btn` (string selector, stable only) |
| `css`   | scoped structural match   | `css=main >> .card:not(.hidden)` (last-resort fallback) |
```

- [ ] **Step 2: Replace the Low Confidence Handling example**

Find `## Low Confidence Handling` and replace its code block with:

```robotframework
# Primary locator returns a reference; fall back to a Get Element By Label call if needed
${storage_radio}=    Get Element By Role    radio    name=256GB
Click                ${storage_radio}
Get Checkbox State   ${storage_radio}    ==    checked    timeout=5s
```

- [ ] **Step 3: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/references/mapping-tables.md
git commit -m "feat(robot-automation): mapping tables use Get Element By * keywords"
```

### Task 4.3: Update network-interception.md

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/references/network-interception.md`

- [ ] **Step 1: Replace the "Assert backend was called" section**

Find the `**Assert backend was called:**` subsection. Replace its code block with:

```robotframework
Place Order And Verify API Call
    [Documentation]    Race-free: the wait must be attached BEFORE the click.
    ...    See Mikko Korpela's forum note on Promise To.
    ${place_order}=    Get Element By Role    button    name=Place order
    ${promise}=        Promise To    Wait For Response    matcher=**/api/order    timeout=10s
    Click              ${place_order}
    ${response}=       Wait For    ${promise}
    Should Be Equal As Integers    ${response}[status]    201
```

- [ ] **Step 2: Add a new subsection at the top of the file on matcher semantics**

After the `# Network Interception and Error Path Testing` header, before `## Network Interception`, add:

```markdown
## Matcher Semantics

`Wait For Response` takes a `matcher=` argument in one of three forms:

- **URL glob** — `matcher=**/api/session` — simplest and preferred when the endpoint is known
- **JavaScript regex** — `matcher=/\/api\/items/i` — JS regex syntax, NOT Python regex
- **JS predicate function** — `matcher=async (response) => response.status() === 200 && response.url().endsWith('/status')` — full programmatic matching

Common failure mode: writing a Python-style regex and wondering why the matcher never fires. Confirm the form before debugging.
```

- [ ] **Step 3: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/references/network-interception.md
git commit -m "feat(robot-automation): network-interception.md uses Promise To + matcher semantics"
```

### Task 4.4: Fix auth-patterns.md

**Files:**
- Modify: `plugins/robot-automation/skills/write-robot-code/references/auth-patterns.md`

- [ ] **Step 1: Fix the `PABOT_QUEUE_INDEX` typo and add value-set pattern**

Find Strategy 2. Replace the code block with the corrected env var and add a new Strategy 2b:

```robotframework
*** Keywords ***
Open Authenticated Page For Worker
    [Documentation]    pabot workers use PABOTQUEUEINDEX (no underscores).
    ...    Each worker reads its own per-worker storage state file.
    ${worker_id}=    Get Environment Variable    PABOTQUEUEINDEX    default=0
    New Browser      chromium    headless=${HEADLESS}
    New Context      storageState=${EXECDIR}/auth/worker-${worker_id}.json
    New Page         ${BASE_URL}
```

Then add a new section after Strategy 2:

```markdown
## Strategy 2b: Per-pabot-worker credentials via PabotLib value sets (recommended for parallel)

Saving separate storage state files per worker is error-prone — multiple workers racing to write `auth/worker-N.json` in a `Suite Setup` is a classic footgun. The idiomatic alternative is PabotLib's value sets.

**Resource file** (`users.dat`) at project root:

```
[user1]
tags=app-user
USERNAME=alice@example.com
PASSWORD=hunter2

[user2]
tags=app-user
USERNAME=bob@example.com
PASSWORD=swordfish
```

**Run:**

```
pabot --pabotlib --resourcefile users.dat --processes 2 tests/
```

**Keyword:**

```robotframework
*** Settings ***
Library    pabot.PabotLib

*** Keywords ***
Log In As Pooled User
    [Documentation]    Acquires exclusive access to one user from the pool.
    ...    Release in [Teardown] so other workers can re-use.
    ${set}=          Acquire Value Set    app-user
    ${username}=     Get Value From Set   USERNAME
    ${password}=     Get Value From Set   PASSWORD
    Go To            ${BASE_URL}/login
    ${email}=        Get Element By Label    Email
    ${pw}=           Get Element By Label    Password
    ${signin}=       Get Element By Role     button    name=Sign in
    Fill Text        ${email}    ${username}
    Fill Secret      ${pw}       $password
    ${promise}=      Promise To    Wait For Response    matcher=**/api/session    timeout=10s
    Click            ${signin}
    Wait For         ${promise}
    RETURN           ${set}

Release Pooled User
    [Arguments]    ${set_name}
    Release Value Set
```

**Why this beats per-worker storage state files:**

- No race on filesystem writes
- Works when you need more parallelism than you have pre-baked storage state files
- PabotLib enforces exclusive access via the locking server — guaranteed one worker per credential set at any time
- Requires `--pabotlib` flag; without it `Acquire Value Set` is a no-op
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/write-robot-code/references/auth-patterns.md
git commit -m "fix(robot-automation): PABOTQUEUEINDEX typo + add PabotLib value-set auth strategy"
```

---

## Phase 5 — `review-test-code` rewrite

### Task 5.1: Rewrite the Locator Quality checklist

**Files:**
- Modify: `plugins/robot-automation/skills/review-test-code/SKILL.md`

- [ ] **Step 1: Replace section 2a**

Find `#### 2a. Locator Quality` in `plugins/robot-automation/skills/review-test-code/SKILL.md`. Replace the entire table + the paragraph below it with:

```markdown
#### 2a. Locator Quality

| Check | What to Look For | Severity |
|-------|-----------------|----------|
| No Playwright-JS selector prefixes | `role=` / `label=` / `placeholder=` / `alt=` / `title=` / `testid=` used as STRING selectors (not in `Get Element By *` keyword arguments) | **BLOCKER** — not documented Browser library engines |
| Semantic locators preferred | `Get Element By Role` / `Get Element By Label` / `Get Element By Test Id` used for buttons, labeled inputs, and test-id elements | WARNING if `css=` / `xpath=` is used where a Get Element By would work |
| Strict mode not silenced without reason | `Set Strict Mode    False` or `strict=False` on `Library Browser` without a `# WHY:` comment | **BLOCKER** |
| No fragile positional selectors | `>> nth=N` without a documented reason | WARNING |
| No dynamic IDs or classes | Selectors containing generated hashes, UUIDs, or auto-incremented numeric IDs | WARNING |
| No utility framework classes | Tailwind (`rounded-lg`, `bg-primary`), Bootstrap (`btn-primary`, `col-md-*`) used as locators | **BLOCKER** — styling, not identity |
| Scoped to containers | `Get Element By *` uses `parent=` OR css locators scope with `>>` to `main` / `nav` / `dialog` | WARNING if top-level locators match multiple elements |
| No exact long text matches | `text="full sentence"` instead of `text=/keyword/i` | WARNING |
| iframe crossing uses `>>>` | Any iframe interaction uses the three-angle syntax, not `>>` | **BLOCKER** if wrong — tests will fail silently |
| Within-file consistency | Every `.robot` file uses ONE dialect: `get_element_by_role_first` OR `css_first`, not mixed | WARNING |
| Matches `conventions.yaml` locator_style | If `conventions.yaml` says `css_first`, the file uses css; if it says `get_element_by_role_first`, the file uses keyword-first | WARNING |

When a locator looks suspicious, delegate verification to a subagent (Task tool): instruct it to open the target URL, locate the element using `find` / `get_element`, and report back whether the element exists and is uniquely matched under strict mode.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/review-test-code/SKILL.md
git commit -m "feat(robot-automation): review-test-code BLOCKs wrong locator dialect"
```

### Task 5.2: Update the Waiting and Timing checklist

**Files:**
- Modify: `plugins/robot-automation/skills/review-test-code/SKILL.md`

- [ ] **Step 1: Replace section 2b**

Find `#### 2b. Waiting and Timing`. Replace with:

```markdown
#### 2b. Waiting and Timing

| Check | What to Look For | Severity |
|-------|-----------------|----------|
| No `Sleep` | Any literal `Sleep` call | WARNING unless tagged as a documented debug aid being removed |
| Proper action-response waits | `Click` / `Fill Text` that triggers a network call is followed by a bare `Wait For Response` | WARNING — use `Promise To` + `Click` + `Wait For` instead (race condition) |
| Auto-retrying assertions used | `Get Text <loc> contains <val>` not `Should Contain ${text} <val>` after a one-shot `Get Text` | WARNING |
| Reasonable explicit timeouts | Custom `timeout=` values have a `# WHY:` comment when above 10s | SUGGESTION |
| No `networkidle`-style waits | Custom keywords that wait on "all network done" | WARNING — prefer specific `Wait For Response` |
| `matcher=` uses correct form | URL glob, JavaScript regex, or JS predicate function — NOT Python regex | **BLOCKER** if it's Python regex syntax |
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/review-test-code/SKILL.md
git commit -m "feat(robot-automation): review-test-code Promise To race detection"
```

### Task 5.3: Add conventions.yaml read to Step 1

**Files:**
- Modify: `plugins/robot-automation/skills/review-test-code/SKILL.md`

- [ ] **Step 1: Update the Load Context step**

Find `### Step 1: Load Context`. Replace the numbered list with:

```markdown
1. Read the `.robot` file(s) to review
2. **Read `e2e-plan/conventions.yaml`** if it exists. Validate against `plugins/robot-automation/schemas/conventions.schema.json`. Use it as the source of truth for expected locator style, resource pattern, auth strategy, tag vocabulary. If the file does not exist, run `analyze-test-codebase` first (or note the absence as a review caveat).
3. Read 2-3 existing `.robot` files (not under review) to cross-check `conventions.yaml` against the actual codebase
4. Read the corresponding test case spec (`test-cases/<feature>.md`) if it exists — needed for traceability check
5. Note any divergence between `conventions.yaml` and the files under review — this feeds the Convention Adherence check
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/review-test-code/SKILL.md
git commit -m "feat(robot-automation): review-test-code reads conventions.yaml"
```

---

## Phase 6 — `fix-flaky-tests` diagnostic additions

### Task 6.1: Add new diagnostic branches

**Files:**
- Modify: `plugins/robot-automation/skills/fix-flaky-tests/SKILL.md`

- [ ] **Step 1: Add new classification rows**

Find the `| Category | Symptoms |` table in Step 1. Add three new rows at the bottom:

```markdown
| **Promise To race**   | Action appears to fire before a matching `Wait For Response` attaches; network-driven flow flakes on fast machines only |
| **Config drift**      | Passes locally with tuned env vars, fails in CI with default; screenshots missing on failure (no `run_on_failure`) |
| **Strict mode ambiguity** | New error: "strict mode violation"; selector that worked yesterday matches multiple elements today |
```

- [ ] **Step 2: Add matching Root Cause Analysis subsections**

Find `### Step 2: Root Cause Analysis`. Append after the `**Environment issues:**` block:

```markdown
**Promise To race:**
- Look for `Click` / `Fill` immediately followed by `Wait For Response` — the wait may attach after the response arrives
- Confirm by adding a temporary log to the click callsite: if the response is sometimes seen and sometimes not, it is a race
- **Fix:** move to the `Promise To` + `Click` + `Wait For` pattern. The promise attaches before the click, eliminating the race.

```robotframework
# BAD — wait attaches after click
Click             ${submit}
Wait For Response    matcher=**/api/session    timeout=10s

# GOOD — promise attached before click
${promise}=       Promise To    Wait For Response    matcher=**/api/session    timeout=10s
Click             ${submit}
Wait For          ${promise}
```

**Config drift:**
- Check `Library Browser` import for `run_on_failure=` — if missing, no screenshots on failure and you have no evidence trail
- Check `New Context` for `viewport=`, `locale=`, `timezoneId=` — missing pins cause CI-vs-local divergence
- Check for `PABOT_QUEUE_INDEX` (WRONG) vs `PABOTQUEUEINDEX` (RIGHT) in auth keywords
- Check `robot.toml` / CI scripts for the `RetryFailed` listener — its absence means one flake fails the whole suite
- **Fix:** apply additive brownfield improvements inside the shipped skills and validate the updated `conventions.yaml`

**Strict mode ambiguity:**
- Strict mode is ON by default. A new ambiguity means the DOM added another match — investigate which element is new
- Browse the page with `find` and count matches for the locator in question
- **Fix:** scope the locator with `parent=` (`Get Element By *` keywords) or `>>` chaining. Do NOT disable strict mode. Do NOT add `>> nth=0`.
```

- [ ] **Step 3: Add matching rows to the fix principle table**

Find the table headed `| Category | Principle |` in Step 3. Append:

```markdown
| **Promise To race**   | Attach the wait BEFORE the action via `Promise To` + `Click` + `Wait For`; cite Korpela's forum post in the fix commit message |
| **Config drift**      | Apply additive brownfield patches in-place; validate new conventions.yaml |
| **Strict mode ambiguity** | Scope locators with `parent=` or `>>`; never disable strict mode to silence ambiguity |
```

- [ ] **Step 4: Commit**

```bash
git add plugins/robot-automation/skills/fix-flaky-tests/SKILL.md
git commit -m "feat(robot-automation): fix-flaky-tests covers Promise To race + config drift + strict ambiguity"
```

### Task 6.2: Extend fix-patterns.md

**Files:**
- Modify: `plugins/robot-automation/skills/fix-flaky-tests/references/fix-patterns.md`

- [ ] **Step 1: Append new fix sections**

At the end of `plugins/robot-automation/skills/fix-flaky-tests/references/fix-patterns.md`, append:

```markdown
## Promise To Race Fixes

```robotframework
# BAD — race: the click's response may arrive before the wait attaches
Click    role=button[name="Sign in"]
${resp}=    Wait For Response    matcher=**/api/session    timeout=10s

# GOOD — race-free: promise attached first
${promise}=    Promise To    Wait For Response    matcher=**/api/session    timeout=10s
Click          role=button[name="Sign in"]
${resp}=       Wait For    ${promise}
```

Cite the maintainer quote in the fix commit message: `"There is a possibility that the click-related request response happens before you attach the wait if wait is done after." — Mikko Korpela`.

## Strict Mode Ambiguity Fixes

```robotframework
# BAD — disabling strict mode hides the bug
Set Strict Mode    False
Click    role=button[name="Delete"]

# BAD — nth=0 picks the wrong element silently
Click    role=button[name="Delete"] >> nth=0

# GOOD — scope with parent= on the Get Element By Role call
${row}=       Get Element By Role    row    name=Invoice 2026-04
${delete}=    Get Element By Role    button    name=Delete    parent=${row}
Click         ${delete}
```

## Config Drift Fixes

Apply additive brownfield improvements from the shipped skills. At minimum:

```robotframework
# Shared resource file header — add the run_on_failure + strict arguments
Library    Browser
...    auto_closing_level=SUITE
...    run_on_failure=Take Screenshot failure-{index} fullPage=True
...    strict=True

# New Context calls — pin the environment
New Context
...    viewport={'width': 1280, 'height': 720}
...    locale=en-US
...    timezoneId=UTC
...    tracing=retain-on-failure
```

Fix the pabot env var typo:

```
# WRONG
${worker}=    Get Environment Variable    PABOT_QUEUE_INDEX    default=0

# RIGHT
${worker}=    Get Environment Variable    PABOTQUEUEINDEX    default=0
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/fix-flaky-tests/references/fix-patterns.md
git commit -m "feat(robot-automation): fix-patterns for Promise To race, strict ambiguity, config drift"
```

---

## Phase 7 — Light touches on `plan-test-coverage`, `generate-test-cases`, `review-test-cases`

### Task 7.1: `plan-test-coverage` reads conventions.yaml

**Files:**
- Modify: `plugins/robot-automation/skills/plan-test-coverage/SKILL.md`

- [ ] **Step 1: Insert a new Step 1.5 after the existing Step 1**

Find `1. **Parse input**` in the Workflow section. After that bullet, insert:

```markdown
1.5. **Read `e2e-plan/conventions.yaml`** if it exists. Use its `tag_vocabulary` so the plan emits tags consistent with the existing project ("smoke", "critical", role-scoped tags, etc.) instead of inventing new tag names. Use its `locator_style` to know whether downstream tests will be written with `Get Element By *` keywords or `css_first`. If conventions.yaml is missing, run `analyze-test-codebase` first.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/plan-test-coverage/SKILL.md
git commit -m "feat(robot-automation): plan-test-coverage reads conventions.yaml"
```

### Task 7.2: `generate-test-cases` emits correct selector syntax in observed selectors

**Files:**
- Modify: `plugins/robot-automation/skills/generate-test-cases/SKILL.md`

- [ ] **Step 1: Replace the "Selectors observed" example in the test case format**

Find `**Selectors observed:**` in the Test Case Format. Replace its two bullets with:

```markdown
**Selectors observed:**
- <element>: `Get Element By Role    button    name=Submit` — returns a Locator reference
- <element>: `Get Element By Label    Email` — form field identified by visible label
- <element>: `Get Element By Test Id    cart-checkout` — when dev team provides data-testid
- (Use Robot Browser library's `Get Element By *` keyword form, not the Playwright-JS `role=button[name="…"]` string-selector syntax — the latter is not a documented Browser library engine. Only when no semantic keyword applies, fall back to `css=main >> .widget` or `xpath=//…` and explain why in a note.)
```

- [ ] **Step 2: Replace the Step 2 structured output example**

Find `Step: <what was done>` in Step 2. Replace its Elements block with:

```markdown
Step: <what was done>
URL: <current URL after action>
Elements found:
  - Submit button: Get Element By Role button name=Submit
  - Email field: Get Element By Label Email
  - Error alert: Get Element By Role alert
Observations: <what appeared, validation messages, state changes>
```

- [ ] **Step 3: Add conventions.yaml read to Step 1**

At the start of Step 1, add:

```markdown
Before exploring, read `e2e-plan/conventions.yaml` if it exists. Its `locator_style` field tells you whether the downstream writer expects `get_element_by_role_first` or `css_first` — record observed selectors in the matching dialect so `write-robot-code` doesn't have to translate.
```

- [ ] **Step 4: Commit**

```bash
git add plugins/robot-automation/skills/generate-test-cases/SKILL.md
git commit -m "feat(robot-automation): generate-test-cases emits Get Element By * syntax"
```

### Task 7.3: `review-test-cases` dialect update

**Files:**
- Modify: `plugins/robot-automation/skills/review-test-cases/SKILL.md`

- [ ] **Step 1: Update the Specification Quality check for locators**

Find `| Locators in Browser library syntax |` in the Specification Quality table. Replace its row with:

```markdown
| Locators in Robot Browser library syntax | `Get Element By Role button name=Submit` (keyword form) OR scoped `css=` / `text=` / `id=`. **NOT** `role=button[name="…"]`, `label=…`, `placeholder=…`, `alt=…`, `title=…`, `testid=…` as string selectors (those are Playwright-JS syntax, not Robot Browser library syntax) |
```

- [ ] **Step 2: Commit**

```bash
git add plugins/robot-automation/skills/review-test-cases/SKILL.md
git commit -m "feat(robot-automation): review-test-cases checks correct locator dialect"
```

---

## Phase 8 — `add-robot-tests` + `workflow.md` dedupe

### Task 8.1: Thin `workflow.md` to state-machine only

**Files:**
- Modify: `workflows/robot-automation/workflow.md`

- [ ] **Step 1: Replace workflow.md contents**

Replace the entire contents of `workflows/robot-automation/workflow.md` with:

```markdown
# Robot Framework E2E Workflow

Stateless orchestration for Athena CLI session loops. Substantive operational guidance lives in the `add-robot-tests` skill — this file only encodes the session-level state machine.

## Sequence

```
orient → (analyze OR scaffold) → plan → explore → generate specs → REVIEW specs (Gate 1)
       → write code → REVIEW code (Gate 2) → execute + re-run for stability (Gate 3)
       → stabilize on failure
```

## Session boundaries

- **Session 1:** load `add-robot-tests` as the top-level skill. Do not improvise — follow its workflow.
- Each subsequent session continues the plan produced in session 1.
- `loop.maxIterations = 15` is a safety cap; most feature additions complete within 3-6 sessions.

## Delegation rules

- **Browser exploration and test writing** can be delegated to subagents via the Task tool
- **Test execution** is NEVER delegated — the main agent runs `robot` directly so it can verify and interpret output
- Subagents inherit plugin skills and must load the matching skill before acting

## Quality gates (summary)

- **Gate 1** — `review-test-cases` passes before `write-robot-code`
- **Gate 2** — `review-test-code` passes before test execution
- **Gate 3** — `robot` suite passes green AND 2 additional re-runs pass green (3 total) before claiming signoff

## Orientation requirement

Before any writing, the agent must have:
1. Read `e2e-plan/conventions.yaml` (or run `analyze-test-codebase` to produce it; for greenfield only, an optional external scaffold/bootstrap repo may also emit it)
2. Browsed the target feature live (`agent-web-interface-guide`) and recorded observed selectors
3. Confirmed auth strategy and test data strategy for the target project

If any of those are blocked (browser MCP unavailable, no user for auth decisions), stop and ask the user rather than writing tests against assumptions.

## Full guidance

See `plugins/robot-automation/skills/add-robot-tests/SKILL.md` for the complete operational guide, skill table, quality-gate detail, smoke-first discipline, and error recovery.
```

- [ ] **Step 2: Commit**

```bash
git add workflows/robot-automation/workflow.md
git commit -m "refactor(robot-automation): thin workflow.md to state-machine shell"
```

### Task 8.2: Update `add-robot-tests/SKILL.md` for smoke-first + re-run-for-stability

**Files:**
- Modify: `plugins/robot-automation/skills/add-robot-tests/SKILL.md`

- [ ] **Step 1: Replace Gate 3 (test execution) section**

Find the `**Checkpoint: Test execution**` block in the Quality gates section. Replace with:

```markdown
**Gate 3: Test execution + re-run for stability**

1. Run the suite: `robot -d results tests/<feature>.robot 2>&1`
2. Inspect the full output — green test output AND `results/log.html` / `results/report.html` are the proof artifacts
3. If tests fail, load the `fix-flaky-tests` skill and follow its structured diagnostic approach. Do not guess-and-retry.
4. **Re-run for stability** — after the first green run, re-run the same suite 2 more times (3 total). Any flakiness across those three runs triggers `fix-flaky-tests` before claiming signoff. A single green run proves nothing about flakiness.
5. Maximum 3 fix-and-rerun cycles per suite per session. If stuck after 3 cycles, move on with the diagnostic output — the failure likely signals a deeper issue that another retry won't fix.

Test execution and coverage checks must never be delegated to subagents. Run `robot` directly from the main agent.
```

- [ ] **Step 2: Add a new section on smoke-first discipline**

Before the `### Error recovery` subsection, insert:

```markdown
### Smoke-first discipline (MANDATORY)

Never write more than one new test against newly scaffolded infrastructure. `write-robot-code` enforces this as its Step 4.5: write ONE happy-path test end-to-end, run it, get it green, THEN expand to the rest of the spec. If the smoke test fails, diagnose before piling more tests on a broken foundation.

Rationale: a single passing test validates the resource imports, the locator dialect, the auth state, the teardown, and the reporting in one pass. 20 tests written before any are run means you debug 20 failures at once with no idea which is a real bug and which is a scaffolding issue.
```

- [ ] **Step 3: Add conventions.yaml read to Step 1**

Find the `### Understand the codebase` subsection. Replace its first bullet with:

```markdown
- **Read `e2e-plan/conventions.yaml`** first. It is the typed contract produced by `analyze-test-codebase` and read by every downstream skill. For greenfield-only bootstraps, an optional external scaffold/bootstrap repo may emit the same contract. If absent and the project has Robot already, run `analyze-test-codebase`. If absent and no Robot exists, decide whether to bootstrap externally or create only the minimum needed in-place.
- Does a Robot Framework setup exist? Look for `robot.toml`, `pyproject.toml` with `robotframework` in dependencies, `__init__.robot` suite init files, `tests/*.robot`, `resources/*.resource`, a `requirements.txt` listing `robotframework` and `robotframework-browser`. If the Browser library is not yet initialized, `rfbrowser init` or `rfbrowser install` must run before any test can execute. Use the optional external scaffold/bootstrap repo only when the user wants a greenfield bootstrap; otherwise continue working directly in the repository.
```

- [ ] **Step 4: Remove duplicated orientation content**

Find the entire `### Understand the product` subsection. Delete its second paragraph starting with "Why this matters: absent explicit exploration…" and replace with:

```markdown
Why this matters: agents that skip live exploration write tests for imaginary behavior — locators that don't exist, flows that work differently than assumed, validation messages that say something else entirely. See the full rationale in `workflows/robot-automation/workflow.md` Orientation requirement section. No exceptions on this step.
```

- [ ] **Step 5: Commit**

```bash
git add plugins/robot-automation/skills/add-robot-tests/SKILL.md
git commit -m "feat(robot-automation): add-robot-tests smoke-first + re-run Gate 3 + conventions.yaml read"
```

---

## Phase 9 — Dry-run target and end-to-end validation

### Task 9.1: Create `_dryrun/robot-sample/` from scratch following the scaffold skill

**Files:**
- Create: `_dryrun/robot-sample/resources/common.resource`
- Create: `_dryrun/robot-sample/resources/login.resource`
- Create: `_dryrun/robot-sample/variables.py`
- Create: `_dryrun/robot-sample/robot.toml`
- Create: `_dryrun/robot-sample/tests/smoke.robot`
- Create: `_dryrun/robot-sample/tests/login.robot`
- Create: `_dryrun/robot-sample/requirements-dev.txt`
- Modify: `.gitignore`

- [ ] **Step 1: Update `.gitignore` for dryrun artifacts**

Append to `.gitignore` (create if absent):

```
# Robot Framework dry-run target (dogfooding)
_dryrun/**/results/
_dryrun/**/auth/
_dryrun/**/traces/
_dryrun/**/node_modules/
```

- [ ] **Step 2: Create `_dryrun/robot-sample/requirements-dev.txt`**

```
robotframework>=7.0
robotframework-browser>=19.12
robotframework-requests>=0.9
robotframework-retryfailed>=0.2
```

- [ ] **Step 3: Create `_dryrun/robot-sample/variables.py`**

```python
"""Dry-run target variables. BASE_URL is pinned to a stable public automation
test site: https://practicetestautomation.com/practice-test-login/
"""
import os

BASE_URL = os.getenv("BASE_URL", "https://practicetestautomation.com")
HEADLESS = os.getenv("HEADLESS", "True") == "True"
VALID_USERNAME = os.getenv("VALID_USERNAME", "student")
VALID_PASSWORD = os.getenv("VALID_PASSWORD", "Password123")
```

- [ ] **Step 4: Create `_dryrun/robot-sample/robot.toml`**

```toml
output-dir = "results"
listener = ["RetryFailed:1:True"]
variablefile = ["variables.py"]

[tags]
default = ["smoke"]
```

- [ ] **Step 5: Create `_dryrun/robot-sample/resources/common.resource`**

```robotframework
*** Settings ***
Documentation    Shared resource for dry-run target — mirrors the recommended greenfield baseline
...              produces for a real project.
Library    Browser
...    auto_closing_level=SUITE
...    run_on_failure=Take Screenshot failure-{index} fullPage=True
...    strict=True
Library    RequestsLibrary
Variables  ../variables.py

*** Keywords ***
Open Browser To Base URL
    [Documentation]    Standard suite-level browser open. Pins viewport, locale, timezone,
    ...    and enables tracing retained on failure.
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
    [Documentation]    Populate after exploration with Route URL calls for analytics,
    ...    chat widgets, hotjar, etc. Placeholder for now.
    Log    Noise blocking placeholder    level=DEBUG
```

- [ ] **Step 6: Create `_dryrun/robot-sample/resources/login.resource`**

```robotframework
*** Settings ***
Documentation    Login page keywords for practicetestautomation.com test target.
Resource         common.resource

*** Keywords ***
Go To Login Page
    Go To    ${BASE_URL}/practice-test-login/
    ${heading}=    Get Element By Role    heading    name=Test Login
    Get Element States    ${heading}    *=    visible

Fill Login Form
    [Arguments]    ${username}    ${password}
    ${username_field}=    Get Element By Label    Username
    ${password_field}=    Get Element By Label    Password
    Fill Text             ${username_field}    ${username}
    Fill Secret           ${password_field}    $password

Submit Login
    ${submit}=    Get Element By Role    button    name=Submit
    Click         ${submit}

Assert Logged In
    ${success}=    Get Element By Role    heading    name=Logged In Successfully
    Get Element States    ${success}    *=    visible
    Get Url        contains    /logged-in-successfully/

Assert Error Message
    [Arguments]    ${expected_pattern}
    ${error}=    Get Element By Test Id    error
    Get Text     ${error}    matches    ${expected_pattern}    timeout=5s
```

- [ ] **Step 7: Create `_dryrun/robot-sample/tests/smoke.robot`**

```robotframework
*** Settings ***
Documentation     Dry-run smoke test — proves the baseline setup runs.
Resource          ../resources/common.resource
Suite Setup       Open Browser To Base URL
Suite Teardown    Close Browser
Test Tags         smoke

*** Test Cases ***
TC-SMOKE-001 Base URL loads and has a title
    [Documentation]    Smoke check — the page loads, a title exists.
    [Tags]    TC-SMOKE-001    critical
    ${title}=    Get Title
    Should Not Be Empty    ${title}
```

- [ ] **Step 8: Create `_dryrun/robot-sample/tests/login.robot`**

```robotframework
*** Settings ***
Documentation     Dry-run login suite against practicetestautomation.com — 3 test cases
...               exercising happy path, wrong username, and locked account flows.
...               Used to dogfood the refined robot-automation plugin end-to-end.
Resource          ../resources/common.resource
Resource          ../resources/login.resource
Suite Setup       Open Browser To Base URL
Suite Teardown    Close Browser
Test Tags         login    critical

*** Test Cases ***
TC-LOGIN-001 User can log in with valid credentials
    [Documentation]    Happy path — valid username and password redirects to success page.
    [Tags]    TC-LOGIN-001    smoke
    Go To Login Page
    Fill Login Form    ${VALID_USERNAME}    ${VALID_PASSWORD}
    Submit Login
    Assert Logged In

TC-LOGIN-002 Invalid username shows error
    [Documentation]    Wrong username surfaces the "Your username is invalid!" error.
    [Tags]    TC-LOGIN-002
    Go To Login Page
    Fill Login Form    incorrectUser    ${VALID_PASSWORD}
    Submit Login
    Assert Error Message    Your username is invalid!

TC-LOGIN-003 Invalid password shows error
    [Documentation]    Correct username with wrong password surfaces the "Your password is invalid!" error.
    [Tags]    TC-LOGIN-003
    Go To Login Page
    Fill Login Form    ${VALID_USERNAME}    incorrectPassword
    Submit Login
    Assert Error Message    Your password is invalid!
```

- [ ] **Step 9: Commit the dry-run target source**

```bash
git add _dryrun/robot-sample/ .gitignore
git commit -m "feat(robot-automation): dry-run target _dryrun/robot-sample for dogfooding"
```

### Task 9.2: Run the dry-run end-to-end

- [ ] **Step 1: Install dependencies into a venv for the dry-run**

```bash
cd _dryrun/robot-sample
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements-dev.txt
rfbrowser init
```

Expected: `rfbrowser init` completes without errors. Chromium, Firefox, WebKit downloaded.

- [ ] **Step 2: Run the smoke test**

```bash
robot -d results tests/smoke.robot 2>&1
```

Expected: 1 test passes. `results/log.html` and `results/report.html` exist.

- [ ] **Step 3: Run the login suite**

```bash
robot -d results tests/login.robot 2>&1
```

Expected: 3 tests pass. Inspect `results/log.html` — the error-path tests (TC-LOGIN-002, TC-LOGIN-003) should show the error messages captured and matched.

- [ ] **Step 4: Re-run the login suite 2 more times for stability**

```bash
robot -d results/run-2 tests/login.robot 2>&1
robot -d results/run-3 tests/login.robot 2>&1
```

Expected: 3 passes on each run — Gate 3 satisfied.

- [ ] **Step 5: If any run fails, load fix-flaky-tests and diagnose**

The plan cannot proceed to commit claims of "tests pass" without three consecutive clean runs. Fix root causes, never extend timeouts or add Sleep.

- [ ] **Step 6: Record the dry-run outcome in the design doc**

Append a "Dry-run results (2026-04-11)" section to `docs/robot-automation-refinement-2026-04-11.md` with:
- Python / Node / Robot Framework versions observed
- Install path used (BrowserBatteries vs classic)
- 3 consecutive run results (pass/fail + elapsed)
- Any issues encountered and their fixes

- [ ] **Step 7: Commit the dry-run record**

```bash
git add docs/robot-automation-refinement-2026-04-11.md
git commit -m "docs(robot-automation): dry-run results 2026-04-11"
```

---

## Phase 10 — Plugin version bump + marketplace metadata

### Task 10.1: Bump plugin version to 0.2.0

**Files:**
- Modify: `plugins/robot-automation/package.json`
- Modify: `plugins/robot-automation/.claude-plugin/plugin.json`
- Modify: `plugins/robot-automation/.codex-plugin/plugin.json`
- Modify: `workflows/robot-automation/workflow.json`

- [ ] **Step 1: Check how other plugins handle version bumps**

Read `scripts/bump-versions.sh` to see the canonical way versions are propagated across manifests in this marketplace. If the script handles all three manifest files automatically, run it:

```bash
./scripts/bump-versions.sh robot-automation 0.2.0
```

If the script only handles some files, do the remaining edits by hand.

- [ ] **Step 2: Manually verify all three plugin manifests show 0.2.0**

```bash
grep -R '"version"' plugins/robot-automation/
```

Expected: all three files list `0.2.0`.

- [ ] **Step 3: Update the workflow.json pin**

In `workflows/robot-automation/workflow.json`, find the plugin reference:

```json
{
  "ref": "robot-automation@lespaceman/athena-workflow-marketplace",
  "version": "0.1.0"
}
```

Update to `"version": "0.2.0"`.

- [ ] **Step 4: Commit**

```bash
git add plugins/robot-automation/package.json plugins/robot-automation/.claude-plugin/plugin.json plugins/robot-automation/.codex-plugin/plugin.json workflows/robot-automation/workflow.json
git commit -m "chore(robot-automation): bump to 0.2.0"
```

### Task 10.2: Update marketplace.json files if needed

**Files:**
- Modify: `.claude-plugin/marketplace.json` (if version is pinned there)
- Modify: `.agents/plugins/marketplace.json` (if version is pinned there)
- Modify: `.athena-workflow/marketplace.json` (if version is pinned there)

- [ ] **Step 1: Check whether any marketplace file pins plugin versions**

```bash
grep -l '"version"' .claude-plugin/marketplace.json .agents/plugins/marketplace.json .athena-workflow/marketplace.json 2>/dev/null
```

- [ ] **Step 2: Update any file that pins the old 0.1.0 version**

For each file flagged above, update the pinned version to `0.2.0`. If none pin the version (marketplace files just reference by path), skip this step.

- [ ] **Step 3: Commit if any files were modified**

```bash
git add .claude-plugin/marketplace.json .agents/plugins/marketplace.json .athena-workflow/marketplace.json 2>/dev/null || true
git commit -m "chore(robot-automation): marketplace metadata for 0.2.0" || echo "nothing to commit"
```

---

## Phase 11 — README migration note

### Task 11.1: Add a migration note to the plugin README

**Files:**
- Create or modify: `plugins/robot-automation/README.md`

- [ ] **Step 1: Check whether README exists**

```bash
ls plugins/robot-automation/README.md 2>/dev/null
```

- [ ] **Step 2: If README does not exist, create it**

```markdown
# robot-automation plugin

Full-pipeline Robot Framework (Browser library) test generation — explores your live site via browser, detects existing `.robot` conventions, plans coverage gaps, produces reviewed TC-ID specs, writes production-grade `.robot` test suites with quality gates, and stabilizes flaky tests.

## Skills

| Skill | Purpose |
|---|---|
| `add-robot-tests` | Top-level pipeline orchestrator |
| `analyze-test-codebase` | Read-only analysis of existing Robot setup; emits `conventions.yaml` |
| External scaffold/bootstrap repo | Optional greenfield bootstrap only; emits the same resilience primitives and `conventions.yaml` contract |
| `plan-test-coverage` | Coverage gap analysis |
| `generate-test-cases` | Browser exploration → structured TC-ID specs |
| `review-test-cases` | Quality gate 1 — spec review |
| `write-robot-code` | Writes executable `.robot` suites following the canonical dialect |
| `review-test-code` | Quality gate 2 — code review |
| `fix-flaky-tests` | Diagnostic flow for intermittent failures |

## Changes in 0.2.0 (2026-04-11)

This release is a correctness + resilience overhaul. See the full design doc at `docs/robot-automation-refinement-2026-04-11.md`.

**Breaking changes in locator dialect:**

- `role=button[name="Submit"]` string selectors are NO LONGER taught — they are Playwright-JS syntax and do not work as prefixed engines in Robot Framework's Browser library. Priority 1 is now `Get Element By Role    button    name=Submit` (keyword form, returns Locator reference).
- Same applies to `label=`, `placeholder=`, `alt=`, `title=`, `testid=` as string prefixes — use the dedicated `Get Element By Label` / `Get Element By Placeholder` / `Get Element By Alt Text` / `Get Element By Title` / `Get Element By Test Id` keywords.
- `review-test-code` now flags the old dialect as a BLOCKER.

**New primitives baked into scaffolded projects:**

- `run_on_failure=Take Screenshot failure-{index} fullPage=True` on the library import
- Strict mode on by default (no silent first-match on ambiguous selectors)
- `tracing=retain-on-failure` on every New Context
- `viewport={…} locale=en-US timezoneId=UTC` pinned to prevent CI-vs-local divergence
- `RetryFailed:1:True` listener wired in `robot.toml`
- Third-party script noise-blocking scaffold in `common.resource`

**New `conventions.yaml` contract** between `analyze-test-codebase` and every downstream skill, with optional compatibility for output emitted by an external greenfield scaffold/bootstrap repo. Schema at `plugins/robot-automation/schemas/conventions.schema.json`.

**Optional external scaffold/bootstrap repo.** Greenfield-only convenience for users who want a one-shot bootstrap via clone/template. Brownfield expertise remains in the shipped skills.

**Workflow changes:**

- Gate 3 (execution) now requires 3 consecutive green runs for signoff, not 1
- `write-robot-code` enforces smoke-first: ONE passing test end-to-end before expansion
- Locator spot-check is mandatory in `write-robot-code`, not optional

**Bug fixes:**

- `PABOT_QUEUE_INDEX` typo corrected to `PABOTQUEUEINDEX` (the actual env var set by pabot)
- `Promise To` + `Wait For` pattern promoted to first-class for race-free network-driven actions (cites maintainer Mikko Korpela)
- `matcher=` gotcha documented — JavaScript regex, not Python
```

If the README already exists, prepend the "Changes in 0.2.0" section at the top.

- [ ] **Step 3: Commit**

```bash
git add plugins/robot-automation/README.md
git commit -m "docs(robot-automation): README migration note for 0.2.0"
```

---

## Self-review checklist

Run through this list with fresh eyes after writing the plan. Fix issues inline, no re-review.

1. **Spec coverage:**
   - [x] Correctness (locator dialect fix): Phase 3, 4, 5, 7
   - [x] Resilience toolkit baked into scaffold: Phase 1 (new skill + references)
   - [x] Adaptation via conventions.yaml: Phase 0 (schema + validator), Phase 2 (analyze emits), Phase 3/5/7 (downstream reads)
   - [x] Professionalism: smoke-first (Phase 3.3), mandatory spot-check (Phase 3.3), re-run-for-stability (Phase 8.2)
   - [x] Workflow dedupe: Phase 8
   - [x] Dogfooding: Phase 9
   - [x] Version metadata: Phase 10
   - [x] Migration note: Phase 11

2. **Placeholder scan:** no TBD / TODO / "implement later" / "fill in details" in the plan. Code blocks are complete.

3. **Type consistency:**
   - `conventions.yaml` schema fields used identically across Phase 0 (schema), Phase 2 (analyze emits), Phase 3/5/7 (reads) ✓
   - External scaffold/bootstrap path is consistently described as optional and greenfield-only ✓
   - `Get Element By Role    button    name=Submit` form used consistently everywhere it appears ✓
   - `PABOTQUEUEINDEX` (not `PABOT_QUEUE_INDEX`) used consistently ✓
   - `Promise To Wait For Response` → `Click` → `Wait For ${promise}` ordering consistent ✓

4. **Granularity:** edits to skill files are scoped to individual sections per task; commits happen after each logical unit; no single task carries more than ~200 lines of content change.

## Execution Handoff

Plan complete and saved to `docs/robot-automation-refinement-plan-2026-04-11.md`.

Given the user granted autonomy ("you choose the best option and proceed"), executing via **subagent-driven development** — fresh subagent per task, two-stage review between tasks. Starting with Phase 0 (schema + validator) because every later phase reads or writes the artifact it defines.
