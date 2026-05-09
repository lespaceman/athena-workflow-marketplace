# Phase pipeline (reference detail)

Each phase has: **Entry** (input artifact required to enter), **Do** (the action — invoke the owning skill where one exists; otherwise follow the procedure here), and **Exit** (output artifact required to leave).

The inner-loop skills (`grill-with-docs`, `grill-me`, `to-prd`, `to-issues`, `tdd`, `diagnose`, `zoom-out`, `prototype`, `improve-codebase-architecture`, `write-a-skill`) come from Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills) and are used here under their original terms. Browser verification comes from this repo's own `agent-web-interface` plugin.

## 1. Brainstorm — `grill-with-docs` (code) or `grill-me` (non-code)

- **Entry:** any new request. Treat every request as rough unless an approved design doc / PRD exists on disk or an approved lightweight session plan already exists.
- **Do:** invoke `grill-with-docs` for code work — it interviews you against the project's domain language (`CONTEXT.md`) and decisions (`docs/adr/`), then updates those docs inline as decisions crystallise. Use `grill-me` for non-code or pure design alignment without doc updates.
- **Simple-task exit:** approved lightweight session plan stating goal, intended files, verification. No PRD required.
- **Full-task exit artifact:** approved design document / PRD on disk (often produced by following the grilling session with `to-prd`). Use for ambiguous, multi-step, architectural, user-visible, or risky work.
- **No code in this phase.**
- **You are NOT in this phase if:** an approved design doc / PRD or session plan already exists. Move to Phase 2.

## 2. Isolate — manual phase

There is no Pocock skill for git worktree setup. Run this directly:

- **Entry:** approved design doc / PRD, or approved lightweight session plan.
- **Do:**
  1. `git worktree add ../<repo>-<branch> -b <branch>` from the repo root.
  2. `cd` into the worktree and run project setup (install deps, env files).
  3. Run the full test suite once to confirm a clean **green baseline** before touching anything. If the baseline is red, stop and fix the baseline (or surface to the user) before proceeding.
- **Exit artifact:** worktree on a new branch with verified green baseline.
- **Skip rule:** never skip this even for "small" changes. Isolation is what makes the rest of the pipeline safe.

## 3. Plan — `to-prd` then `to-issues`

- **Entry:** approved design doc / brainstorming output + clean worktree. Simple tasks with a session plan can skip and execute from the session plan.
- **Do:**
  1. `to-prd` — synthesize the conversation context into a PRD on the project issue tracker. No fresh interview; it captures what was already discussed. Skip if a PRD already exists.
  2. `to-issues` — break the PRD into independently-grabbable issues using tracer-bullet vertical slices. Each issue should be a 2–5 minute task with exact file paths, the complete change, and verification steps.
- **Exit artifact:** issue list (or plan file) of discrete, independently verifiable tasks.
- **Skip rule:** "I'll just remember the steps" is not a plan. Write the issues / plan file.

## 4. Execute — manual loop, with `tdd` mandatory inside each task

- **Entry:** approved plan / issue list on disk, or approved lightweight session plan.
- **Do:** pick one task at a time. For each task:
  - **TDD via `tdd`:** failing test → watch it fail → minimal code → watch it pass → refactor → commit. Vertical slice per cycle, never horizontal (don't write all tests then all code). Code written before its test gets deleted.
  - **Browser pass via `agent-web-interface` for any user-visible behavior:** load `agent-web-interface:agent-web-interface-guide` first, then exercise against a running dev server. Capture a screenshot/snapshot. Code-level green tests do not substitute. If there is no UI surface yet, say so explicitly — do not silently skip.
  - **Bug surfaces mid-task → `diagnose`:** if something is broken, throwing, failing, or behaving inconsistently, switch into the disciplined diagnosis loop (reproduce → minimise → hypothesise → instrument → fix → regression-test). Do not patch by guessing.
  - **Unfamiliar code → `zoom-out`:** before editing code you do not yet understand, zoom out for the broader context.
- **Exit per task:** test green + browser-pass artifact (or explicit no-UI declaration) + review findings addressed.

## 5. Review — manual phase (between tasks, not a separate phase)

There is no Pocock skill for between-task code review. Default approach:

- After each task (or end of a small related batch), have the user — or a fresh subagent — read the diff against the task's stated verification.
- Critical findings block the next task. Lower-severity findings can be tracked and addressed later — but tracked, not forgotten.
- For codebase-wide drift after several tasks (modules getting tangled, names diverging from `CONTEXT.md`), run `improve-codebase-architecture` to find deepening opportunities and consolidate.

## 6. Finish — manual phase

There is no Pocock skill for finishing a development branch. Procedure:

- **Entry:** all planned tasks complete, tests green, no open critical review issues.
- **Do:**
  1. Run the full test suite one more time — must be green.
  2. Final `agent-web-interface` browser pass across the whole feature: golden path + every edge case named in the design.
  3. **Default action in this repo: merge locally to `main` and remove the worktree.** Skip the 4-option integration prompt. Only stop and ask the user if: tests fail, the merge has conflicts, the base branch isn't `main`, or the user has explicitly asked for a PR instead.
  4. Destructive fallbacks (discard) still require typed confirmation.
- **Exit:** branch merged to `main`, worktree cleaned up.

## Pinned skills and plugins

### Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills) — process discipline

These cover the inner loops the workflow leans on. Used under their original terms; credit to Matt Pocock.

- `grill-with-docs` — alignment + shared language; interview against `CONTEXT.md` and `docs/adr/` and update both inline. Phase 1 default for code work.
- `grill-me` — alignment without doc updates. Phase 1 fallback for non-code/simple sessions.
- `to-prd` — synthesize current conversation into a PRD on the issue tracker. Phase 3 step 1.
- `to-issues` — break a PRD/plan into vertical-slice issues. Phase 3 step 2.
- `tdd` — red-green-refactor; vertical slices only. Mandatory inside every Phase 4 task that produces code.
- `diagnose` — reproduce → minimise → hypothesise → instrument → fix → regression-test. Use whenever a bug surfaces mid-execution.
- `zoom-out` — broader/system-level context for unfamiliar code. Use before editing code you do not understand.
- `prototype` — throwaway terminal app or several radically different UI variations to flush out a design before committing. Optional Phase 1 aid.
- `improve-codebase-architecture` — find deepening opportunities; consolidate tangled modules. Run periodically between tasks; ideal between feature batches.
- `triage` — issue-tracker state machine when managing a backlog of incoming bugs / feature requests.
- `write-a-skill` — when authoring or editing a skill (including this one).

Skills with no Pocock equivalent (worktree setup, between-task code review, finishing) are run as manual procedures defined per phase above.

### `tanstack-start` — frontend/full-stack framework knowledge

Use whenever the task involves TanStack Start, TanStack Router, server functions, server routes, SSR, RSC, or migrating from Next.js. Core skill: `tanstack-start:tanstack-start-guide`. Domain-specific skills under `skills/upstream/@tanstack/...` cover routing, Start internals, the router plugin, virtual file routes, and React Server Components. Consult these before hand-rolling routing or data patterns.

### `frontend-design` — UI quality and product-facing design

Use whenever the task includes a user-visible screen, flow, layout, interaction pattern, or visual state. Load before making UI decisions so the implementation has deliberate hierarchy, responsive behavior, accessibility, and domain-appropriate visual polish instead of framework-default screens.

### `shadcn` — component library and design system

Use whenever UI work needs accessible primitives, form patterns, theming, or registry components. Skill: `shadcn:shadcn-ui`. Prefer installing from the shadcn registry over hand-writing button/input/dialog primitives.

### `agent-web-interface` — live browser interaction (mandatory test layer)

Required test layer for anything user-visible. Every Phase 4 task that builds or modifies UI, a route, a server function exposed to the browser, an API consumed by the UI, or any end-to-end flow MUST be exercised against a running dev server through `mcp__plugin_agent-web-interface_browser__*` tools before being considered done. Unit and integration tests do not substitute.

Skill: `agent-web-interface:agent-web-interface-guide`. **Load it BEFORE any `mcp__plugin_agent-web-interface_browser__*` tool call** so observations are structured and selectors are stable.

Use it to walk the golden path, exercise edge cases and error states named in the design, capture a screenshot/snapshot as the task's verification artifact, and spot regressions in adjacent flows the change could plausibly affect.

If the app cannot be exercised this way (no dev server, pure backend with no client yet), say so explicitly in the verification step — do not silently skip the browser pass.

## Attribution

The inner-loop process discipline in this skill is adapted from **Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills)**. The phase scaffolding (Brainstorm → Isolate → Plan → Execute → Review → Finish) and the mandatory browser-pass test layer (`agent-web-interface`) are this repo's own. All trademarks and links are property of their respective owners.
