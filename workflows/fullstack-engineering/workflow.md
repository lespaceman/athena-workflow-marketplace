# Full-Stack Engineering Workflow

A composable workflow for shipping real engineering work — features, bug fixes, refactors. Built around Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills) (used under their original terms) plus this repo's `agent-web-interface` and `app-exploration` plugins for live verification. The workflow is a default ordering of small skills, not a framework that owns your process. Skip steps deliberately when the situation does not need them; never skip by default.

## Prerequisites

Every skill named below resolves through a Plugin pinned in `workflow.json`. The runtime installs them automatically; there is no external setup step.

- **`agent-web-interface`** — MCP browser server + the agent-web-interface guide skill.
- **`app-exploration`** — `map-feature-scope`, `capture-feature-evidence`.
- **`frontend-design`** — UI design skills.
- **`matt-pocock-skills`** — bundled subset of Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills): `setup-matt-pocock-skills`, `triage`, `grill-with-docs`, `grill-me`, `to-prd`, `to-issues`, `tdd`, `diagnose`, `zoom-out`, `prototype`, `improve-codebase-architecture`. Original work © Matt Pocock; see the plugin's `NOTICE.md`.
- **`shadcn`** — accessible primitives, registry components.
- **`tanstack-start`** — TanStack Start, Router, server functions, SSR/RSC guidance.

If any step below names a skill that does not resolve, the runtime is mis-configured — stop and ask the user to verify the Plugin Pins, do not improvise the step's behavior inline.

## Four failure modes this prevents

1. **Misalignment** — agent builds the wrong thing fast.
2. **Verbosity and naming drift** — agent uses different language than the codebase.
3. **Broken code** — agent ships without real feedback loops.
4. **Ball-of-mud entropy** — AI accelerates complexity faster than you can fix it.

Every step below exists to block one of these. If a step does not map to one of these four, question whether it should exist.

## Foundation: shared language (precondition)

Before any other skill in this workflow runs effectively, the repo needs:

- `CONTEXT.md` at the root — the project's domain language.
- `docs/adr/` — architectural decisions on disk.

These are read by `grill-with-docs`, `improve-codebase-architecture`, `diagnose`, and `tdd` to keep naming consistent and avoid relearning the codebase every session. Without them, every step that follows is degraded — verbose, inconsistent, and tokens spent re-deriving project jargon.

If either is missing, run `setup-matt-pocock-skills` first to scaffold them. This is the highest-leverage move in the workflow.

## Default ordering

For non-trivial work, follow this sequence. Each step names the skill that owns it. State on disk is what carries between steps — if your context resets, you should be able to `ls` and know exactly where you are.

### −1. Foundation check — first action of every workflow run

**Before Step 0, every run, the very first action is to verify the foundation exists on disk:**

```
test -f CONTEXT.md && test -d docs/adr/
```

- If both exist → proceed to Step 0.
- If either is missing → invoke `setup-matt-pocock-skills` immediately and do nothing else until it completes. The Pocock skills will not work correctly without these files, and re-running this step later means the work done before it was degraded.

This is not informational. It is the first command of the workflow.

### 0. Triage — `triage` (only when entering from a backlog)

Skip when the user has handed you a defined task. Run when the work originates as an unevaluated incoming bug, feature request, or issue queue. `triage` walks the issue through the canonical state machine (`needs-triage` → `needs-info` → `ready-for-agent` / `ready-for-human` / `wontfix`) so the rest of the workflow only ever picks up issues that are actually ready to work on.

**Output on disk:** an issue with the right label and enough detail that Step 1 can run without re-interviewing the reporter.

### 1. Align — `grill-with-docs` (code) or `grill-me` (non-code)

Refines the request through targeted questions. `grill-with-docs` additionally challenges the plan against `CONTEXT.md` and `docs/adr/`, sharpening domain terms and capturing new decisions inline. Use `grill-me` only for non-code work (process, comms, content) where there is no domain model to update.

**No production code in this step.**

Throwaway exploration when discussion is not enough — `prototype` aid:

- If alignment cannot decide between approaches without seeing them run (state machine choice, data model trade-off, two radically different UI directions), invoke **`prototype`**: either a runnable terminal app for state / business-logic questions, or several toggleable UI variations from one route.
- The prototype output is meant to be deleted. Only the design decision survives, captured in the ADR.

**Alignment artifact — schema and location.** This is the on-disk contract Steps 3, 5, 7, and 8 read from. It must contain, in this order:

1. **Goal** — one sentence stating user-visible outcome.
2. **Files** — every path expected to be created or modified.
3. **Verification** — golden-path scenario plus every named edge case.
4. **QA mode** — exactly one of:
   - `qa: full` — Step 7 manual-QA pass is mandatory (default for any user-visible change).
   - `qa: skip — <reason>` — Step 7 may be skipped. Only allowed for tiny, well-isolated, no-blast-radius changes (copy fix, single-component prop tweak with no shared state, doc-only change). The reason must name *why* there is no blast radius.
5. **Domain updates** — new or changed terms added to `CONTEXT.md`, new ADRs created. List the paths.

**Where it lives:**

- If the run entered through Step 0 (backlog) → as a comment on the issue, plus any `CONTEXT.md` / ADR edits committed to the worktree.
- If the run came from a direct user request with no issue → a single file at `.scratch/<branch>/alignment.md` with the same schema, plus the doc edits.

**Reduced form (skip-condition):** for genuinely small, well-bounded tasks (one file, no architectural choice, no user-visible surface), the alignment artifact may be a four-line session note (Goal / Files / Verification / `qa: skip — <reason>`) instead of full doc updates. Anything ambiguous, multi-step, or user-visible runs the full grilling and writes the full artifact.

### 2. Isolate — manual

```
git worktree add ../<repo>-<branch> -b <branch>
cd ../<repo>-<branch>
<install deps>
<run full test suite — must be green>
```

If the baseline is red, stop and fix the baseline (or surface to the user) before proceeding. **Output:** a worktree on a new branch with a verified green baseline. Never skip this — isolation is what makes the rest of the loop safe.

### 3. Plan — `to-prd` then `to-issues`

- `to-prd` synthesizes the alignment session into a PRD on the issue tracker.
- `to-issues` breaks the PRD into independently-grabbable issues using tracer-bullet vertical slices. Each issue lists exact file paths, the complete change, and verification steps.

**Skip rule:** if alignment already produced a 2–5 minute task list naming files and verification, that is the plan; do not write a second one. For anything larger, write the issues.

### 4. Execute — one task at a time

For each task, three Pocock skills plus the per-task browser-pass procedure:

- **`tdd` — mandatory inside every task that produces code.** Failing test → watch it fail → minimum code → watch it pass → refactor → commit. **One vertical slice per cycle.** Never bulk-write tests then bulk-implement: that produces tests that describe imagined behavior and pass when real behavior breaks. Code written before its test gets deleted.
- **`diagnose` when a bug surfaces mid-task** — reproduce → minimise → hypothesise → instrument → fix → regression-test. Do not patch by guessing.
- **`zoom-out` when entering unfamiliar code** — get system-level context before editing.
- **Browser pass via `agent-web-interface` — mandatory for any user-visible behavior** (procedure, not a Pocock skill). Load `agent-web-interface:agent-web-interface-guide` *before* any `mcp__plugin_agent-web-interface_browser__*` call so observations are structured and selectors stable. Capture a screenshot or page snapshot as the verification artifact. Code-level green tests do not substitute. If the task genuinely has no UI surface, say so explicitly — do not silently skip.

**Output per task:** test green + browser-pass artifact (or explicit no-UI declaration) + review findings addressed.

### 5. Review between tasks — fresh-subagent diff review

After each task — or the end of a small tightly-coupled batch — spawn a **fresh subagent** with no prior context and hand it the diff plus the task's stated verification criteria. Fresh context matters: the executing agent has rationalized its choices and will not catch its own drift.

The reviewer reads against four checks, in order:

1. **Scope** — does the diff change anything outside the files named in the alignment artifact / issue? Out-of-scope changes are an automatic critical finding.
2. **Tests** — is there a failing-then-passing test for every behavior change? Tests written after the code, tests asserting on implementation rather than behavior, and bulk-written tests are critical.
3. **Domain language** — do new identifiers (functions, files, types) use terms from `CONTEXT.md`? Naming drift is at minimum a major finding; left unfixed it compounds across tasks.
4. **Verification artifact** — is the per-task browser-pass screenshot/snapshot present (or an explicit no-UI declaration)? Missing is critical.

**Severity rubric:**

- **Critical** — scope leak, test missing/inverted, verification artifact missing, security/data-loss risk. Blocks the next task. Fix before advancing.
- **Major** — naming drift from `CONTEXT.md`, dead code, unhandled error paths the design called out. Track in the issue and fix before Step 7.
- **Minor** — style, comment quality, micro-refactor opportunities. Track for later; never block on these.

Findings get appended to the issue / alignment artifact, not just spoken in chat.

### 6. Periodic deepening — `improve-codebase-architecture`

AI accelerates entropy. This is the maintenance loop that keeps the codebase from becoming a ball of mud — not optional on long-running work.

**Trigger (run when *any* of these is true):**

- ≥ 5 tasks have completed since the last deepening pass on this branch.
- The branch's cumulative diff against `main` exceeds 500 changed lines or touches ≥ 5 distinct top-level modules.
- About to enter Step 7 on a branch that has not had a deepening pass yet.
- Step 5 review surfaced a *major* finding tagged "naming drift" or "tangled module" — even if the other thresholds have not been hit.

If none of the above are true, skip this step and continue. Run the skill against `CONTEXT.md` and `docs/adr/`; record findings as ADR updates or as new issues in the tracker — do not silently refactor inside the current branch unless an ADR sanctions it.

### 7. Manual QA — `app-exploration:map-feature-scope` then `app-exploration:capture-feature-evidence`

Before merge, do a structured exploratory pass against the running app — not just the changes you made, but the surrounding flows the change could plausibly affect. The per-task browser passes in Step 4 prove that each change worked in isolation; this step proves the whole feature still hangs together end-to-end and catches regressions in adjacent flows that no test named.

Use the layered shape:

1. **`app-exploration:map-feature-scope`** — for any feature that spans multiple routes, tabs, overlays, or roles, decompose it into concrete bounded sub-features and shared state. Output: `e2e-plan/feature-map.md`.
2. **`app-exploration:capture-feature-evidence`** — for each scoped sub-feature (or the single feature if mapping is unnecessary), exercise it deeply against the live app via `agent-web-interface` and capture grounded evidence: golden path, every edge case named in the alignment artifact, error states, role variations, and any blockers discovered. Output: `e2e-plan/exploration-report.md` or scoped files under `e2e-plan/exploration/`.

**Skip rule:** for a tiny, well-isolated change with no plausible blast radius (e.g. a copy fix, a single-component prop tweak with no shared state), the per-task browser pass in Step 4 is sufficient and this step can be declared explicitly skipped in the alignment artifact. Anything user-facing with a real surface area runs this step.

**Output on disk:** `e2e-plan/feature-map.md` (when mapping was needed) plus exploration report(s). These are the manual-QA artifacts; their absence on a non-trivial user-visible change is a missing step.

### 8. Finish — manual

- Full test suite green.
- Step 7 manual-QA artifacts present (or explicit skip declared in the alignment artifact for trivial changes).
- **Default in this repo: merge locally to `main` and remove the worktree.** Stop and ask the user only on test failure, merge conflict, non-`main` base branch, or explicit PR request. Destructive fallbacks (discard) require typed confirmation.

**After merge, decide the loop exit:**

- If the run started from Step 0 (backlog entry) and the issue tracker still has issues labelled `ready-for-agent`, return to Step 0 and pick the next one.
- Otherwise — direct user request, or no remaining `ready-for-agent` issues — **stop and report**. Do not invent new work to keep the loop alive. Idle is a correct state.

## Non-negotiable rules

Each is falsifiable in one line. Violation is a workflow failure, not a shortcut.

1. **No code without an alignment artifact on disk** — PRD, issue, or session note naming goal, files, verification.
2. **No production code outside an active TDD cycle.** Failing test first; vertical slices only.
3. **No "done" claim on user-visible work without a browser-pass artifact** (per-task, Step 4) **and an `app-exploration` evidence artifact** (Step 7) — unless the alignment artifact declares `qa: skip — <reason>` per Step 1's schema. Tests passing is not proof.
4. **Critical review findings block the next task.** Fix before advancing.
5. **New scope = new alignment session.** Mid-execution scope expansion requires re-running `grill-with-docs` and rewriting the alignment artifact (or appending a new section with its own Goal / Files / Verification / `qa:` / Domain updates fields). Slipping in a "while I'm here" change without that update violates this rule.
6. **Surface blockers; do not guess.** Stuck-and-asking is a correct state.

## Red-flag thoughts — these mean stop

If you catch yourself thinking any of these, a step is about to be skipped:

| Thought | What it actually means |
|---|---|
| "Small change, I'll just edit it." | Small still needs an alignment artifact. |
| "I already know the design." | If it's not on disk, it's a guess. Run `grill-with-docs` (or `grill-me` for non-code work). |
| "I'll write the test after I see the code works." | Not TDD. Test first; vertical slice. |
| "Unit tests pass, task is done." | User-visible work needs a browser pass. |
| "I'll add this related improvement while I'm here." | New scope = new alignment. |
| "I'll fix this critical finding next task." | Critical findings block forward motion. |
| "User just wants me to do X, not follow process." | They installed this workflow on purpose. If they want to bypass it, they will say so explicitly. |

## When you cannot proceed

Missing credentials, environment access, product decision, or design call → **stop and surface the exact blocker plus the next required input.** Do not skip ahead to keep moving. Do not guess product or architecture decisions.

## Skills used by this workflow

From Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills) (Engineering set), used under their original terms. Each maps to a step above:

- `setup-matt-pocock-skills` — Foundation. Scaffolds `CONTEXT.md`, ADRs, issue tracker, triage labels. Run once per repo.
- `triage` — Step 0. Issue-tracker state machine for unevaluated incoming work.
- `grill-with-docs` — Step 1. Alignment for code work; updates `CONTEXT.md` and ADRs inline.
- `grill-me` — Step 1. Alignment for non-code work (process, comms, content) where there is no domain model to update.
- `prototype` — Step 1 aid. Throwaway runnable exploration when discussion alone cannot decide a design.
- `to-prd` — Step 3. Synthesize alignment into a PRD on the issue tracker.
- `to-issues` — Step 3. Break the PRD into vertical-slice issues.
- `tdd` — Step 4. Red-green-refactor; one vertical slice per cycle.
- `diagnose` — Step 4. Disciplined bug loop when something breaks mid-execution.
- `zoom-out` — Step 4. System-level context before editing unfamiliar code.
- `improve-codebase-architecture` — Step 6. Periodic deepening to fight entropy.

From this repo:

- `agent-web-interface:agent-web-interface-guide` — Step 4. Mandatory per-task test layer for user-visible work. Browser tools live only in this plugin; load the guide before any `mcp__plugin_agent-web-interface_browser__*` call.
- `app-exploration:map-feature-scope` — Step 7. Decompose a broad feature into bounded sub-features before deep exploration. Owns `e2e-plan/feature-map.md`.
- `app-exploration:capture-feature-evidence` — Step 7. Deeply explore the live app and capture grounded evidence for the manual-QA pass. Owns `e2e-plan/exploration-report.md` and scoped files under `e2e-plan/exploration/`. Delegates browser work to `agent-web-interface` under the hood.

Domain framework skills (load when the task domain matches):

- `tanstack-start:tanstack-start-guide` — TanStack Start, Router, server functions/routes, SSR, RSC, Next.js migration.
- `frontend-design` — load before any UI decision so the implementation has deliberate hierarchy, responsive behavior, accessibility, and visual polish.
- `shadcn:shadcn-ui` — accessible primitives, form patterns, theming. Prefer the registry over hand-written button/input/dialog.
