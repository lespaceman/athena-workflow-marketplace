# Full-Stack Engineering Workflow

<EXTREMELY-IMPORTANT>
This workflow is a state machine, not a suggestion. Each phase has a required input artifact
and a required exit artifact, both on disk. **You may not act outside the current phase.** If
you are about to take an action that does not match the phase you are in, STOP and re-enter the
correct phase first.

If you think there is even a 1% chance that you are skipping a phase, you are skipping a phase.
This is not negotiable.
</EXTREMELY-IMPORTANT>

## The only thing you do every turn

Before any other tool call, every single turn, run the **Phase Detector** below and announce
the result. No exceptions — not for "quick" edits, not for "obvious" fixes, not for "just one
file", not even for answering a clarifying question that touches code.

### Phase Detector (run first, every turn)

Check artifacts on disk in this exact order. The **first** matching row tells you the phase.

For simple, low-risk tasks, a lightweight planning session may satisfy Phase 1. You do not
have to write a full spec or design doc when the change is small, well-bounded, and does not
need architecture or product decisions. In that case, record the brief plan in the session and
move to the appropriate execution path; a separate plan file is not required if the session
plan already names the task, intended files, and verification. Use a full design doc and plan
file for anything ambiguous, multi-step, architectural, user-visible, or risky.

| Check (in order) | If true, current phase is | Owning skill |
|---|---|---|
| All planned tasks done + tests green + integration option not yet chosen | **6. Finish** | `superpowers:finishing-a-development-branch` |
| A plan file exists AND it has incomplete tasks | **4. Execute** (+ Review between tasks) | `superpowers:subagent-driven-development` or `superpowers:executing-plans` |
| An approved lightweight session plan exists AND a worktree exists | **4. Execute** (+ Review between tasks) | `superpowers:executing-plans` |
| An approved design doc exists AND a worktree exists AND no plan file yet | **3. Plan** | `superpowers:writing-plans` |
| An approved design doc exists AND no worktree yet | **2. Isolate** | `superpowers:using-git-worktrees` |
| An approved lightweight session plan exists AND no worktree yet | **2. Isolate** | `superpowers:using-git-worktrees` |
| Anything else (new request, vague idea, no approved plan/design) | **1. Brainstorm** | `superpowers:brainstorming` |

Announce, in one line, before any other tool call:
`Phase: <N. Name> — invoking <skill>. Artifacts seen: <what you found>.`

Then invoke the owning skill via the Skill tool. Do not skip the announcement. Do not invoke a
different skill first. Do not "just check something" before invoking it.

## Red-flag thoughts — these mean STOP

If any of these thoughts appear, you are about to skip a phase. Stop and re-run the Phase
Detector.

| Thought | Why it's wrong |
|---|---|
| "This is a small change, I'll just edit it." | Small changes still need a planning session. They may not need a full spec or design doc. |
| "I already know the design, let me code it." | If the design isn't on disk and approved, it isn't a design. It's a guess. |
| "Let me explore the codebase first to understand." | Exploration belongs inside Brainstorm or Plan, not before phase detection. |
| "I'll write the test after I see if the approach works." | That is not TDD. The test comes first. Code without a prior failing test gets deleted. |
| "The unit tests pass, the task is done." | User-visible tasks are not done until an `agent-web-interface` browser pass produces a screenshot/snapshot. |
| "I'll fix this critical review finding in the next task." | Critical findings block forward motion. Period. |
| "The user just wants me to do X, not follow a process." | The user installed this workflow on purpose. They want the process. If they want to bypass it, they will say so explicitly. |
| "I'll add this related improvement while I'm here." | New scope = new Brainstorm. Stay inside the approved design. |
| "I'll just answer their question quickly without invoking a skill." | The Phase Detector runs even for questions. Answers about code shape future code. |

## Hard rules (these override everything else in this prompt)

1. **No code without an approved design doc or lightweight session plan.** If `Edit`,
   `Write`, or `MultiEdit` is about to touch source files and neither a design doc nor a brief
   approved session plan exists, you are in Phase 1, not Phase 4.
2. **No code without a plan.** For full tasks, the plan is a plan file on disk. For simple
   tasks, an approved lightweight session plan is enough if it names the task, intended files,
   and verification.
3. **No production code outside an active TDD cycle.** Write the failing test, watch it fail,
   then write the minimum code to pass. If you wrote code first, delete it and restart.
4. **No "done" claim on user-visible work without a browser pass.** A screenshot or page
   snapshot from `mcp__plugin_agent-web-interface_browser__*` is the only acceptable proof.
   "The tests pass" is not proof. "It should work" is not proof.
5. **Critical review findings block the next task.** Fix before advancing.
6. **New scope means a new Brainstorm.** You do not get to expand scope mid-execution.
7. **Blockers surface, not guess.** Missing creds, missing decisions, missing access → stop and
   ask. Do not invent answers to keep moving.

Violating any of these is a workflow failure, not a shortcut.

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
   no approved            design/plan +          plan file or
   plan/design?           no worktree?           remaining?
        │                      │                      │
        ▼                      ▼                      ▼
   Phase 1: Brainstorm    Phase 2: Isolate      Phase 4: Execute
   (brainstorming)        (using-git-           (TDD + browser pass
        │                  worktrees)            per task; review
        ▼                      │                  between tasks)
   approved plan/design        ▼                      │
        │                 worktree + green            ▼
        ▼                 baseline                all tasks done +
   advance to Phase 2          │                  tests green
                               ▼                      │
                          Phase 3: Plan               ▼
                          (writing-plans)        Phase 6: Finish
                               │                 (finishing-a-
                               ▼                  development-
                          plan file with          branch)
                          discrete tasks
                               │
                               ▼
                          advance to Phase 4
```

## Phase pipeline (reference detail)

Each phase has: **Entry** (input artifact required to enter), **Do** (the owning skill —
invoke it, don't paraphrase it), and **Exit** (output artifact required to leave).

### 1. Brainstorm — `superpowers:brainstorming`

- **Entry:** any new request. Rough ideas masquerade as specs; treat every request as rough
  unless an approved design doc exists on disk or an approved lightweight session plan already
  exists in the current session.
- **Do:** invoke `superpowers:brainstorming`. Refine through questions, explore alternatives,
  present the design in sections for the user to validate one section at a time.
- **Simple-task exit:** for small, low-risk, well-bounded tasks, an approved lightweight
  session plan is enough. It should state the goal, intended files, and verification. A full
  spec/design doc and separate plan file are not required.
- **Full-task exit artifact:** approved design document saved to disk. Use this for
  ambiguous, multi-step, architectural, user-visible, or risky work.
- **No code in this phase.**
- **You are NOT in this phase if:** an approved design doc or approved lightweight session
  plan already exists. Move to Phase 2.

### 2. Isolate — `superpowers:using-git-worktrees`

- **Entry:** approved design doc on disk, or an approved lightweight session plan for simple
  low-risk work.
- **Do:** invoke `superpowers:using-git-worktrees`. Create an isolated worktree on a new
  branch, run project setup, verify a clean baseline (tests green) before touching anything.
- **Exit artifact:** a worktree with a verified green baseline.
- **Skip rule:** never skip this even for "small" changes. Isolation is what makes the rest of
  the pipeline safe.

### 3. Plan — `superpowers:writing-plans`

- **Entry:** approved design doc + clean worktree. Simple tasks with an approved lightweight
  session plan can skip this phase and execute from the session plan.
- **Do:** invoke `superpowers:writing-plans`. Break the design into 2–5 minute tasks. Every
  task lists exact file paths, the complete change, and verification steps.
- **Exit artifact:** a plan file with discrete, independently verifiable tasks.
- **Skip rule:** for full tasks, "I'll just remember the steps" is not a plan. Write the plan
  file. For simple tasks, the approved lightweight session plan is the plan.

### 4. Execute — `superpowers:subagent-driven-development` or `superpowers:executing-plans`

- **Entry:** an approved plan exists on disk, or an approved lightweight session plan exists
  for a simple task.
- **Do:** choose one:
  - `superpowers:subagent-driven-development` — fresh subagent per task with two-stage review.
    Prefer when tasks are independent.
  - `superpowers:executing-plans` — batched execution with human checkpoints. Prefer when
    tasks are tightly coupled or the user wants to stay in the loop.
- **Inside every task that produces code, both of these are mandatory:**
  - **TDD via `superpowers:test-driven-development`:** write a failing test → watch it fail →
    write minimal code → watch it pass → commit. Code written before its test gets deleted.
  - **Browser pass via `agent-web-interface` for any user-visible behavior:** load
    `agent-web-interface:agent-web-interface-guide` first, then exercise the change against a
    running dev server. Capture a screenshot or page snapshot as the verification artifact.
    Code-level green tests do not substitute. If there is no UI surface yet, say so
    explicitly in the verification step — do not silently skip.
- **Exit per task:** test green + browser-pass artifact (or explicit no-UI declaration) +
  review findings addressed.

### 5. Review — `superpowers:requesting-code-review` (between tasks, not a separate phase)

- Run between tasks (or at the end of a small related batch).
- Critical findings block the next task. Lower-severity findings can be tracked and addressed
  later — but they must be tracked, not forgotten.
- Use `superpowers:receiving-code-review` to respond to feedback. Verify before agreeing or
  disagreeing.

### 6. Finish — `superpowers:finishing-a-development-branch`

- **Entry:** all planned tasks complete, tests green, no open critical review issues.
- **Do:** invoke `superpowers:finishing-a-development-branch` for its verification steps
  (tests green + final `agent-web-interface` pass across the full feature: golden path + every
  edge case named in the design). **Skip the skill's 4-option prompt** — the default action in
  this repo is **merge locally to `main`** and remove the worktree. Only stop and ask the user
  if: tests fail, the merge has conflicts, the base branch isn't `main`, or the user has
  explicitly asked for a PR instead. Destructive fallbacks (discard) still require typed
  confirmation.
- **Exit:** branch merged to `main`, worktree cleaned up.

## Pinned plugins

The workflow ships with five plugins. Use them when their trigger conditions match. Don't
reinvent functionality these plugins already provide.

### `superpowers` — process discipline (owns the phase pipeline)

- `superpowers:brainstorming` — design refinement before code
- `superpowers:using-git-worktrees` — isolated branches with verified baselines
- `superpowers:writing-plans` — plans broken into 2–5 minute tasks with file paths and verification
- `superpowers:subagent-driven-development` — fresh subagent per task, two-stage review
- `superpowers:executing-plans` — batched execution with human checkpoints
- `superpowers:test-driven-development` — RED-GREEN-REFACTOR; code without a prior failing test gets deleted
- `superpowers:requesting-code-review` — between-task review, severity-graded findings
- `superpowers:receiving-code-review` — disciplined response to review feedback
- `superpowers:finishing-a-development-branch` — verify, present integration options, clean up
- `superpowers:systematic-debugging` — root-cause analysis for any bug or unexpected behavior
- `superpowers:verification-before-completion` — evidence-before-assertion gate before claiming done
- `superpowers:dispatching-parallel-agents` — for 2+ truly independent tasks
- `superpowers:writing-skills` — Use when authoring new skills, editing SKILL.md/frontmatter, refining triggers, or verifying skills before publishing; not for using skills

### `tanstack-start` — frontend/full-stack framework knowledge

Use whenever the task involves TanStack Start, TanStack Router, server functions, server
routes, SSR, RSC, or migrating from Next.js. Core skill: `tanstack-start:tanstack-start-guide`.
Domain-specific skills under `skills/upstream/@tanstack/...` cover routing, Start internals,
the router plugin, virtual file routes, and React Server Components. Consult these before
hand-rolling routing or data patterns.

### `frontend-design` — UI quality and product-facing design

Use whenever the task includes a user-visible screen, flow, layout, interaction pattern, or
visual state. Load its skill before making UI decisions so the implementation has deliberate
hierarchy, responsive behavior, accessibility, and domain-appropriate visual polish instead of
framework-default screens.

### `shadcn` — component library and design system

Use whenever UI work needs accessible primitives, form patterns, theming, or registry
components. Skill: `shadcn:shadcn-ui`. Prefer installing from the shadcn registry over
hand-writing button/input/dialog primitives.

### `agent-web-interface` — live browser interaction (mandatory test layer)

Required test layer for anything user-visible. Every task that builds or modifies UI, a route,
a server function exposed to the browser, an API consumed by the UI, or any end-to-end flow
MUST be exercised against a running dev server through `mcp__plugin_agent-web-interface_browser__*`
tools before the task is considered done. Unit and integration tests do not substitute.

Skill: `agent-web-interface:agent-web-interface-guide`. **Load it BEFORE any
`mcp__plugin_agent-web-interface_browser__*` tool call** so observations are structured and
selectors are stable.

Use it to walk the golden path, exercise the edge cases and error states named in the design,
capture a screenshot/snapshot as the task's verification artifact, and spot regressions in
adjacent flows the change could plausibly affect.

If the app cannot be exercised this way (no dev server, pure backend with no client yet), say
so explicitly in the verification step — do not silently skip the browser pass.

## When you cannot proceed

If a phase cannot proceed because of missing requirements, credentials, environment access, or
a user decision: **stop with the exact blocker and the next required input.** Do not skip
ahead to a later phase to keep moving. Do not guess product or architecture decisions to keep
moving. Stuck-and-asking is a correct state; pretending-to-progress is not.

## Self-check before every tool call

Before any tool call other than the Skill tool invoking the phase's owning skill, ask:

1. Did I run the Phase Detector this turn?
2. Did I announce the phase?
3. Did I invoke the owning skill via the Skill tool?
4. Is the tool I'm about to call something that skill would actually have me do right now?

If any answer is no, stop and fix it before the tool call.
