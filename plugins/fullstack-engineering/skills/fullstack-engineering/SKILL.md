---
name: fullstack-engineering
description: End-to-end engineering workflow as a state machine - Brainstorm → Isolate → Plan → Execute (TDD + browser pass) → Review → Finish. Each phase has a required input and exit artifact on disk. Use when starting any non-trivial feature, bug fix, or refactor; when the user wants disciplined process with phase gates, design docs, plan files, worktrees, TDD, and browser verification; when they say "fullstack engineering", "follow the workflow", "do this properly end to end", or coordinate brainstorming + planning + execution together. Not for one-line edits, doc tweaks, or read-only investigation.
---

# Full-Stack Engineering

A state machine, not a suggestion. Each phase has a required input artifact and exit artifact, both on disk. **You may not act outside the current phase.** If you are about to take an action that does not match your current phase, STOP and re-enter the correct phase first.

If you think there is even a 1% chance you are skipping a phase, you are skipping a phase.

The skill leans on Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills) for the inner loops (alignment, planning, TDD, diagnosis). See [PHASES.md](PHASES.md) for full attribution.

## The only thing you do every turn

Before any other tool call, every single turn, run the **Phase Detector** and announce the result. No exceptions — not for "quick" edits, not for "obvious" fixes, not for "just one file", not even for clarifying questions that touch code.

### Phase Detector (run first, every turn)

Check artifacts on disk in this exact order. The **first** matching row tells you the phase.

For simple, low-risk tasks, a lightweight planning session may satisfy Phase 1 — record the brief plan in the session naming the task, intended files, and verification. Use a full design doc and plan file for anything ambiguous, multi-step, architectural, user-visible, or risky.

| Check (in order) | Phase | Owning skill |
|---|---|---|
| All planned tasks done + tests green + integration option not chosen yet | **6. Finish** | (no skill — see PHASES.md) |
| Plan file / issue list exists with incomplete tasks | **4. Execute** (+ Review between tasks) | `tdd` per task; `diagnose` if a bug surfaces |
| Approved lightweight session plan + worktree exists | **4. Execute** | `tdd` per task |
| Approved design doc / PRD + worktree + no plan file | **3. Plan** | `to-prd` then `to-issues` |
| Approved design doc + no worktree | **2. Isolate** | (no skill — see PHASES.md) |
| Approved lightweight session plan + no worktree | **2. Isolate** | (no skill — see PHASES.md) |
| Anything else (new request, vague idea, no approved plan/design) | **1. Brainstorm** | `grill-with-docs` |

Announce, in one line, before any other tool call:
`Phase: <N. Name> — invoking <skill or "manual phase">. Artifacts seen: <what you found>.`

When a phase has an owning skill, invoke it via the Skill tool before doing anything else. When a phase has no owning skill (Isolate, Finish), follow the procedure in [PHASES.md](PHASES.md) directly.

**Load skills on your own judgment.** Every skill named here is model-invocable — when its trigger holds, load it yourself, before the action, without waiting to be asked. Two triggers are easy to miss:

- **First-run setup:** before Brainstorm in a repo with no `## Agent skills` block in `CLAUDE.md`/`AGENTS.md` or no `docs/agents/`, load `setup-matt-pocock-skills` first — the other engineering skills depend on the tracker, triage, and domain context it writes.
- **Unfamiliar code:** before reading or changing a module you have not mapped this session, load `zoom-out` for the map instead of orienting by ad-hoc file reads.

## Hard rules (override everything else)

1. **No code without an approved design doc / PRD or lightweight session plan.** If `Edit`/`Write`/`MultiEdit` is about to touch source files and neither exists, you are in Phase 1, not Phase 4.
2. **No code without a plan.** Full tasks → plan file or issue list on disk. Simple tasks → approved session plan naming task, files, verification.
3. **No production code outside an active TDD cycle.** Failing test first, watch it fail, then minimum code to pass. Code written before its test gets deleted. (Use `tdd`.)
4. **No "done" claim on user-visible work without a browser pass.** A screenshot or page snapshot from `mcp__plugin_agent-web-interface_browser__*` is the only acceptable proof. "Tests pass" is not proof.
5. **Critical review findings block the next task.** Fix before advancing.
6. **New scope means a new Brainstorm.** No expanding scope mid-execution. (Re-enter `grill-with-docs`.)
7. **Surface blockers, do not guess.** Missing creds, decisions, or access → stop and ask.

Violating any of these is a workflow failure, not a shortcut.

## Red-flag thoughts — these mean STOP

If any of these appear, you are about to skip a phase.

| Thought | Why it's wrong |
|---|---|
| "Small change, I'll just edit it." | Small changes still need a planning session. |
| "I already know the design." | If it's not on disk and approved, it's a guess. Run `grill-with-docs`. |
| "Let me explore the codebase first." | Exploration belongs inside Brainstorm or Plan. Use `zoom-out` for unfamiliar code. |
| "I already understand this repo's setup." | If the `## Agent skills` block / `docs/agents/` aren't present, the engineering skills lack tracker, triage, and domain context. Load `setup-matt-pocock-skills`. |
| "That skill is the user's to invoke, not mine." | Every skill here is model-invocable. If its trigger holds, you load it — don't wait to be asked. |
| "I'll write the test after I see if it works." | Not TDD. Test first. Code without a prior test gets deleted. |
| "Unit tests pass, task is done." | User-visible tasks need a browser-pass artifact. |
| "I'll fix this critical finding next task." | Critical findings block forward motion. |
| "User just wants me to do X, not follow process." | They installed this workflow on purpose. |
| "I'll add this related improvement while I'm here." | New scope = new Brainstorm. |
| "I'll answer their question quickly without a skill." | Phase Detector runs even for questions. |

## Phase decision flow

```
            ┌─────────────────────────────┐
            │  New turn — run Phase       │
            │  Detector (artifacts on     │
            │  disk decide the phase)     │
            └──────────────┬──────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
no approved          design/plan +          plan file or
plan/design?         no worktree?           tasks remaining?
    │                      │                      │
    ▼                      ▼                      ▼
Phase 1: Brainstorm    Phase 2: Isolate      Phase 4: Execute
(grill-with-docs)      (manual: worktree     (tdd per task;
                        + green baseline)     diagnose on bugs;
                                              browser pass via
                                              agent-web-interface)
                                                  │
                                                  ▼
                                              all done +
                                              tests green
                                                  │
                                                  ▼
                                              Phase 6: Finish
                                              (manual: merge to
                                               main + cleanup)
```

## When you cannot proceed

If a phase is blocked by missing requirements, credentials, environment access, or a user decision: **stop with the exact blocker and the next required input.** Do not skip ahead. Do not guess. Stuck-and-asking is a correct state; pretending-to-progress is not.

## Self-check before every tool call

Before any tool call other than the Skill tool invoking the phase's owning skill (or, for skill-less phases, the first action of that phase):

1. Did I run the Phase Detector this turn?
2. Did I announce the phase?
3. Did I invoke the owning skill (or follow PHASES.md for skill-less phases)?
4. Is the tool I'm about to call something that phase would actually have me do right now?

If any answer is no, stop and fix it.
