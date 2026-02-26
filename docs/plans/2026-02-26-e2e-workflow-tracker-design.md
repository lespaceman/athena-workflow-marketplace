# E2E Workflow Tracker Design

**Date:** 2026-02-26
**Status:** Approved

## Problem

The e2e-test-builder plugin needs a resilient, stateless workflow that athena-cli can loop until completion. Each Claude session is fresh (`claude -p`), with no conversation history carried over. The workflow must persist state across sessions via a tracker file.

## Architecture

```
athena-cli loop:
  while tracker doesn't contain E2E_COMPLETE or E2E_BLOCKED:
    claude -p --append-system-prompt-file e2e-workflow-prompt.md "<user query>"
```

Each session: read tracker → find next step → execute → update tracker → exit.

## Tracker File

Lives at `e2e-tracker.md` in the project root. Lean status document with pointers to artifacts.

### Format

```markdown
# E2E Test Tracker

**Target:** <url>
**Feature:** <description>
**Feature Slug:** <slug>
**Created:** <ISO date>

## Steps

| # | Step | Status | Artifact |
|---|------|--------|----------|
| 1 | Analyze codebase | pending | e2e-plan/conventions.md |
| 2 | Plan test coverage | pending | e2e-plan/coverage-plan.md |
| 3 | Explore site & generate specs | pending | test-cases/<slug>.md |
| 4 | Write tests | pending | |
| 5 | Verify & fix | pending | |
| 6 | Coverage check | pending | |

## Log
```

### Status Values

- `pending` — not started
- `in-progress` — started but not complete (session ran out of budget or was interrupted)
- `done` — step complete, artifact written
- `blocked` — unrecoverable issue (with reason)

### Session Log

Append-only, one entry per session:

```markdown
### Session N — <ISO timestamp>
- Completed: <what was done>
- Found: <key discoveries>
- Blocker: <if any>
- Next: <what the next session should do>
```

### Completion Markers

- `<!-- E2E_COMPLETE -->` — all steps done, all TC-IDs covered and passing
- `<!-- E2E_BLOCKED: reason -->` — unrecoverable, athena-cli should stop and report

## Artifact Files

```
<project-root>/
├── e2e-tracker.md                    # Lean status tracker
├── e2e-plan/
│   ├── conventions.md                # Step 1: codebase analysis
│   └── coverage-plan.md             # Step 2: prioritized test plan
├── test-cases/
│   └── <slug>.md                     # Step 3: TC-ID specs
└── <test-dir>/                       # Step 4: test files
    └── <slug>.spec.ts                # Placed per project conventions
```

## The 6 Steps

| # | Step | Skill | Input | Output | Done When |
|---|------|-------|-------|--------|-----------|
| 1 | Analyze codebase | `/analyze-test-codebase` | playwright.config, existing tests | e2e-plan/conventions.md | Conventions documented |
| 2 | Plan test coverage | `/plan-test-coverage` | URL, conventions | e2e-plan/coverage-plan.md | P0/P1/P2 tests planned |
| 3 | Explore & generate specs | `/generate-test-cases` | URL, coverage plan | test-cases/<slug>.md | All TC-IDs written |
| 4 | Write tests | `/write-e2e-tests` | Specs, conventions | <slug>.spec.ts | Test files created |
| 5 | Verify & fix | *(custom)* | Test files | Updated test files | All tests pass (max 2 fix cycles/session) |
| 6 | Coverage check | *(custom)* | Specs + test files | E2E_COMPLETE marker | All TC-IDs found in passing tests |

### Step Execution Rules

- Each session executes one step (steps 1-2 may combine since they're lightweight)
- Steps 1-4 invoke existing skills; steps 5-6 have inline instructions
- If step 6 finds uncovered TC-IDs, it resets step 4 to `pending` with a note listing missing IDs

## System Prompt File

`e2e-workflow-prompt.md` — appended via `--append-system-prompt-file`.

### Structure

1. **Role & Mission** — You are an E2E test automation agent. Tracker file is your memory.
2. **Session Protocol** — Read tracker → bootstrap or continue → execute step → update tracker → stop
3. **Step Definitions** — Which skill to invoke, what to read, what to produce, success criteria
4. **Guardrails** — Always read conventions before writing tests, never skip tracker update, use subagents for heavy work

### Bootstrap (No Tracker)

1. Parse URL and feature from user query
2. Derive feature slug
3. Check Playwright config exists (write `E2E_BLOCKED` if not)
4. Create `e2e-tracker.md` with all steps as `pending`
5. Create `e2e-plan/` directory
6. Begin step 1

### Continue (Tracker Exists)

1. Read tracker, find first non-`done` step
2. Read relevant artifacts for context
3. Execute the step
4. Update tracker status + append session log
5. If all steps done: write `<!-- E2E_COMPLETE -->`

## Resilience

### Session Budget Exhaustion
- Update tracker to `in-progress` before heavy work
- Next session reads partial artifact and continues

### Playwright Not Found
- Step 1 writes `<!-- E2E_BLOCKED: No Playwright config found -->`
- Athena-cli detects and aborts

### Flaky Tests (Step 5)
- Max 2 fix-and-rerun cycles per session
- If still failing: log details, leave as `in-progress`, next session retries fresh

### Missing Skills
- System prompt includes fallback inline instructions for each step
- Skills preferred but not required

### Tracker Corruption Prevention
- Rigid format: exact table headers, exact status values
- System prompt includes exact template to follow
