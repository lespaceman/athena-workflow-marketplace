---
name: review-robot-best-practices
description: >
  Use when reviewing Robot Framework and Python test automation code for best practices, maintainability, reliability, style, architecture, anti-patterns, or caveats. Trigger for `.robot`, `.resource`, Python custom libraries, Robot variable files, Browser/Selenium/API test suites, "Robot Framework best practices", "review automation quality", "what should be avoided", "common Robot issues", and "Python Robot library review". Review-only; does not rewrite tests or diagnose a specific flaky failure.
allowed-tools: Read Glob Grep
---

# Review Robot Best Practices

Review Robot Framework test automation as a quality gate for long-term maintainability, accurate behavior coverage, deterministic execution, and idiomatic Robot/Python design. Prefer project conventions when they are explicit; otherwise use the checklist below and the source notes in `references/robot-review-sources.md`.

## Workflow

1. Identify the review scope: `.robot` suites, `.resource` keyword files, variable files, Python libraries, CI config, and dependency files.
2. Read local conventions first: `robot.toml`, `pyproject.toml`, `requirements*.txt`, `robocop.toml`, `ruff.toml`, `pytest.ini`, `e2e-plan/conventions.yaml`, and 2-3 nearby suites/resources.
3. Review findings by severity:
   - BLOCKER: likely false pass/fail, hidden assertion failure, nondeterminism, unsafe secret handling, or code that cannot run.
   - WARNING: likely flake, maintenance burden, poor abstraction, unclear ownership, or convention drift.
   - SUGGESTION: style or readability improvement with limited behavioral risk.
4. Cite file paths and line numbers for every finding. Explain impact, not only preference.
5. Do not rewrite code unless explicitly asked. Do not run tests unless explicitly asked; this skill is for static quality review.

## Robot Suite Review

Check these areas first:

| Area | Best Practice | Avoid / Flag |
| --- | --- | --- |
| Test intent | Test names, `[Documentation]`, and tags describe user-visible behavior or API contract. | Action-only tests, vague names, duplicated coverage, tests that verify implementation details only. |
| Assertions | Every test has meaningful outcome assertions after the action. | `Run Keyword And Ignore Error` around assertions, "visible" as the only oracle for functional behavior, swallowed failures. |
| Setup/teardown | Shared setup/teardown is explicit and local to the required scope. Persistent data is cleaned up. | Order-dependent tests, shared mutable state, UI setup for data that should be seeded by API/fixture. |
| Keywords | User keywords express domain actions and remain small, composable, and readable. | Large procedural keywords, deep nesting, keywords that mix setup, action, assertion, and cleanup. |
| Resources | Shared keywords live in `.resource` files and suite files remain focused on tests. | Duplicated helper keywords across suites, resource names that conflict, ambiguous keyword imports. |
| Variables | Scope and casing make ownership clear; environment-specific values come from variables/env/config. | Hardcoded domains, credentials, generated IDs, or case/space variants of the same variable name. |
| Waiting | Use library-specific waits, retrying assertions, and event-driven waits. | `Sleep`, blanket network-idle waits, arbitrary retries, force-clicks hiding readiness problems. |
| Data | Use unique, deterministic test data and assert on the entity created by the test. | Global counts, list positions, shared usernames, tests that only pass in a pre-seeded environment. |
| Parallelism | Tests are safe under randomized order and `pabot` unless explicitly marked otherwise. | Global state mutation, shared browser/session state across independent tests, cleanup racing with other tests. |
| Style | Follow project formatter/linter settings; otherwise use 4-space cell separation, section order, concise lines, and consistent naming. | Inconsistent spacing, overlong lines, mixed old/new Robot syntax, redundant comments. |

## Python Library Review

For custom Python libraries imported by Robot:

- Prefer explicit keyword exposure with `@library` and `@keyword`, or `ROBOT_AUTO_KEYWORDS = False` plus decorated functions. Flag accidental helper exposure.
- Keep library scope intentional. Use `TEST`/`SUITE` scope for stateful libraries unless global state is proven safe.
- Raise clear exceptions for keyword failures. Do not return booleans that callers forget to assert.
- Use Python logging/Robot logger or returned values deliberately; avoid noisy `print` except where Robot logging semantics are intended.
- Keep keyword arguments typed and simple. Validate inputs close to the keyword boundary and make defaults explicit.
- Do not call Robot internal APIs unless the public API cannot solve the problem.
- Avoid broad `except Exception`, sleeps, hidden retries, module-level mutable state, hardcoded paths, network calls without timeouts, and leaking secrets into logs.
- For async or background work, make completion and timeout behavior explicit; do not leave background tasks/processes unmanaged.
- Apply normal Python quality gates to libraries: `ruff`/`flake8`, type checks where configured, unit tests for library logic, and deterministic filesystem/network behavior.

## Web/API Automation Caveats

- Browser tests should prefer accessibility-aligned locators, labels, stable test IDs, scoped locators, and user-observable assertions. CSS/XPath is acceptable only when justified and stable.
- API setup/teardown is preferable when UI behavior is not the subject under test.
- Error-path tests should verify the user-facing error state and relevant backend interaction when available.
- Network interception/mocking must not mask the behavior the test claims to cover.
- Do not use UI login in every test unless the login flow itself is under review; prefer authenticated state or API setup consistent with the project.

## Output Format

```markdown
# Robot Best Practices Review: <scope>

## Verdict: PASS | PASS WITH WARNINGS | NEEDS REVISION

## Blockers
- `<file>:<line>`: <issue, impact, and concrete recommendation>

## Warnings
- `<file>:<line>`: <issue, impact, and concrete recommendation>

## Suggestions
- `<file>:<line>`: <improvement>

## Conventions Checked
- <configs and examples read>

## Residual Risk
- <what was not reviewed or could not be verified statically>
```

## Review Boundaries

- Prefer precise, evidence-backed findings over broad style advice.
- Do not require a pattern only because it is personally preferred; tie it to Robot docs, project conventions, reliability, readability, or maintainability.
- If code is valid but non-idiomatic, classify by risk. Not every style issue is a blocker.
- If a finding depends on runtime DOM or service behavior, label it as an evidence gap and recommend targeted exploration or execution.
