# Scaffolding Robot Framework + Browser Library

If Robot Framework + Browser library is not set up in the target project, follow this procedure. Unlike Playwright projects, there is no canonical Robot Framework boilerplate repo to clone — scaffold directly in the target project.

## 1. Install Python dependencies

Detect the project's Python dependency manager before installing:

- `pyproject.toml` with Poetry → `poetry add --group dev robotframework robotframework-browser robotframework-requests`
- `pyproject.toml` with `uv`/`pdm` → use that tool's add/install command
- `requirements.txt` / plain venv → `python3 -m pip install robotframework robotframework-browser robotframework-requests` and append to `requirements-dev.txt`

Do not install globally without asking the user.

## 2. Initialize the Browser library

```
rfbrowser init
```

This downloads the Playwright browsers Browser library wraps. If it fails, see `error-recovery.md`.

## 3. Create a minimal suite layout

```
tests/
  <feature>.robot        # test suites
resources/
  common.resource        # shared keywords (navigation, auth)
  <feature>.resource     # feature-specific page keywords
variables.py             # optional, for dynamic variables (e.g., BASE_URL from env)
robot.toml               # optional, Robot Framework 7+ runtime config
```

Populate `resources/common.resource` with library imports and shared Suite Setup / Suite Teardown keywords:

```robotframework
*** Settings ***
Library    Browser    auto_closing_level=SUITE
Library    RequestsLibrary

*** Keywords ***
Open Browser To Base URL
    [Arguments]    ${url}=${BASE_URL}
    New Browser    chromium    headless=${HEADLESS}
    New Context    viewport={'width': 1280, 'height': 720}
    New Page    ${url}
```

## 4. Wire up `robot.toml` (or `__init__.robot`) for defaults

- Set `outputdir = "results"` so artifacts go to a predictable place.
- Prefer tag-based selection (`-i smoke`, `-e slow`) over regex exclusions.
- Do NOT create a `testIgnore`-style regex that must be updated for every new suite — tag tests instead.

## 5. Verify the install

Run the example Browser library smoke test or a trivial suite to confirm `robot` executes and `rfbrowser init` succeeded before attempting real test generation:

```
robot -d results tests/smoke.robot
```

Preserve the important scaffolding decisions in your working notes.
