# System Prompt Rewrite Design

**Date:** 2026-03-04
**Scope:** e2e-workflow-prompt.md full rewrite + skill description optimization

## Problem

The e2e-test-builder workflow agent was undertriggering skills and producing low-quality output:

1. **Skill undertriggering** — Agent skipped skills during debugging, browser investigation, and config changes (0-11% recall on eval)
2. **No debugging methodology** — Agent brute-forced test failures (run 3x and hope) instead of structured root cause analysis
3. **No code quality enforcement** — Agent wrote test code without reviewing against project conventions
4. **Poor test verification** — Agent sometimes marked steps done without real test execution proof
5. **Coarse task lists** — Users couldn't track progress; tasks were too vague ("Do step 5")

## Solution: Two-Part Fix

### Part 1: Skill Description Optimization

Rewrote descriptions for 6 skills to include **behavioral/situational triggers** (what the agent is *doing*) alongside phrase triggers (what the user *says*):

| Skill | Key addition |
|-------|-------------|
| fix-flaky-tests | "If running --repeat-each or tests multiple times, STOP and load this skill" |
| explore-website | "REQUIRED for any task involving a live web page. ONLY skill with browser access" |
| write-e2e-tests | "If editing Playwright config, testIgnore, fixtures, load this skill first" |
| plan-test-coverage | "If checking coverage completeness or comparing TC-IDs, load this skill" |
| analyze-test-codebase | "Before writing ANY test code in a new project, load this skill first" |
| generate-test-cases | "If creating TC-ID specs before writing code, use this skill" |

Ran optimization loop (5 iterations x 20 queries x 3 runs per skill) — eval harness showed 0-17% recall ceiling due to limitations of bare `claude -p` testing, but proposed descriptions are qualitatively superior.

### Part 2: System Prompt Full Rewrite

Restructured from step-based to **behavior-based** architecture:

**Old structure:**
- Using Skills (brief mention)
- Session Protocol (steps 1-6 with inline instructions)
- Task Management (1 vague paragraph)
- Guardrails (bullet list)

**New structure:**
- Behavioral Rules (5 rules that apply ALWAYS):
  1. Load Skills Before Acting — activity-to-skill mapping table
  2. Quality Gates — conventions check, execution check, stability check
  3. Structured Task Visibility — users watch tasks, not logs
  4. Debugging Protocol — classify → investigate → fix with traceability
  5. Code Quality Standards — self-review checklist, output quality verification
- Task Management Protocol — step-specific task templates, dynamic tasks for debugging
- Stateless Session Protocol — same 6 steps but leaner, referencing Rules instead of duplicating

Key changes:
- Activity-to-skill mapping table catches follow-up work (not just pipeline steps)
- Debugging protocol requires investigation before fixing, with specific skill invocations per failure type
- Code quality self-review checklist runs before AND after test execution
- Per-step task templates with per-failing-test granularity
- Step 4 now includes quality spot-check before moving to step 5

## Files Changed

- `.workflows/e2e-test-builder/e2e-workflow-prompt.md` — full rewrite
- `plugins/e2e-test-builder/skills/fix-flaky-tests/SKILL.md` — description rewritten
- `plugins/e2e-test-builder/skills/explore-website/SKILL.md` — description rewritten
- `plugins/e2e-test-builder/skills/write-e2e-tests/SKILL.md` — description rewritten
- `plugins/e2e-test-builder/skills/plan-test-coverage/SKILL.md` — description rewritten
- `plugins/e2e-test-builder/skills/analyze-test-codebase/SKILL.md` — description rewritten
- `plugins/e2e-test-builder/skills/generate-test-cases/SKILL.md` — description rewritten
