# Full-Stack Engineering Workflow

Ship engineering changes through alignment, implementation, validation, review, and delivery without letting the agent guess. Each phase consumes an artifact, produces an artifact, and has a gate before the next phase.

This Workflow is an orchestrator, not a replacement for the Skills it routes to. Keep the user in
control of ambiguous decisions, keep Skills small and composable, and move through the work by
observable state rather than confidence.

## Plugins

This workflow is authored against the Plugins pinned in `workflow.json`. The markdown lists the
Plugin surfaces, while `workflow.json` remains the source of truth for Plugin Pins and versions.

| Plugin | Skills Used Here |
|--------|------------------|
| `matt-pocock-skills` | `setup-matt-pocock-skills`, `triage`, `grill-with-docs`, `prototype`, `to-prd`, `to-issues`, `zoom-out`, `tdd`, `diagnose`, `improve-codebase-architecture` |
| `frontend-design` | `frontend-design` |
| `shadcn` | `shadcn-ui` |
| `tanstack-start` | `tanstack-start-guide` and focused TanStack routing/start skills when applicable |
| `agent-web-interface` | `agent-web-interface-guide` |
| `app-exploration` | `map-feature-scope`, `capture-feature-evidence` |

## Skills

Load the relevant Skill before each activity. Skills own the detailed method; this Workflow owns
routing, artifacts, gates, and handoffs.

| Activity | Skill |
|----------|-------|
| Repo foundation and local conventions | `setup-matt-pocock-skills` |
| Incoming issue or request triage | `triage` |
| Scope, constraints, domain language, and ADR alignment | `grill-with-docs` |
| Disposable design probe | `prototype` |
| PRD from aligned context | `to-prd` |
| Vertical-slice task breakdown | `to-issues` |
| Unfamiliar codebase area | `zoom-out` |
| Feature implementation or bug fix with behavior tests | `tdd` |
| Hard bug, flake, or performance regression | `diagnose` |
| Architecture drift or shallow module cluster | `improve-codebase-architecture` |
| User-visible UI design | `frontend-design` |
| shadcn/ui primitives, theming, or registry work | `shadcn-ui` |
| TanStack Start or Router work | `tanstack-start-guide` |
| Browser verification | `agent-web-interface-guide` |
| Broad manual QA or product evidence | `map-feature-scope`, `capture-feature-evidence` |

## Failure-Mode Routing

Use the Workflow to catch the common agent failure modes early:

| Failure Mode | Symptom | Route |
|--------------|---------|-------|
| Misalignment | The request is broad, underspecified, or likely to surprise the user | `grill-with-docs` before planning |
| Missing domain language | The agent uses vague words, local jargon is unclear, or names drift | `grill-with-docs`; update `CONTEXT.md` or ADRs inline |
| Weak feedback loop | The agent cannot prove behavior quickly | strengthen baseline, use `tdd`, browser evidence, or `diagnose` |
| Debugging by inspection | A bug is being "fixed" before it is reproduced | `diagnose` and build a reproducible loop first |
| Horizontal implementation | Many tests or files are changing before one slice is green | return to one tracer bullet via `tdd` |
| Architecture entropy | Understanding requires bouncing across shallow modules or tangled seams | `improve-codebase-architecture` |
| Product guessing | UI, route, selector, role, or behavior assumptions lack evidence | `agent-web-interface-guide` or `capture-feature-evidence` |

## Task Tracker Discipline

Progress must survive resumes, context resets, subagents, and missing task tools.

On every session start:

1. Read the current tracker or `.scratch/<slug>/` artifacts before acting.
2. Reconcile completed, in-flight, blocked, and next work.
3. If a task tool exists, update it. Otherwise write the same state into the active artifact.
4. Surface mismatches before choosing the next phase.

Use one slug for the run: `agent/<slug>` for branches and `.scratch/<slug>/` for local artifacts.

## Artifacts

| Artifact | Owner | Required When |
|----------|-------|---------------|
| `.scratch/<slug>/alignment.md` or issue comment | `grill-with-docs` | Always |
| `.scratch/<slug>/prd.md` or issue | `to-prd` | Substantial or risky work |
| `.scratch/<slug>/tasks.md` or issues | `to-issues` | More than one independently verifiable slice |
| `.scratch/<slug>/baseline.md` | Workflow | Always before code |
| `.scratch/<slug>/review.md` | Workflow or fresh reviewer | `standard` and `full`; optional for `light` |
| `e2e-plan/feature-map.md` | `map-feature-scope` | Broad user-visible QA |
| `e2e-plan/exploration-report.md` or `e2e-plan/exploration/*.md` | `capture-feature-evidence` | Required QA or browser evidence |

If the repo has no issue tracker, use local files. Do not block on missing GitHub or GitLab unless the user explicitly required issue creation.

## Orientation Steps

First, run the foundation check:

```bash
test -f CONTEXT.md && test -d docs/adr && test -s docs/agents/triage-labels.md
```

If it fails, enter Phase 0. If the repo intentionally uses different paths, document those paths in
the alignment artifact before treating foundation as present.

Classify scale once during alignment:

- `light` - one bounded change; PRD, issues, and QA may be skipped with reasons.
- `standard` - normal feature, bug fix, or refactor. Default when unsure.
- `full` - risky, architectural, cross-module, multi-route, role-sensitive, auth/payment/security, or broad user-visible work. Requires PRD/issues and QA.

## Workflow Sequence

Default progression:

**foundation → triage when needed → align → plan when needed → prepare → execute one slice → review → QA when needed → deliver**

Choose the first matching phase:

| State | Phase |
|---|---|
| Foundation missing or stale | 0. Foundation |
| Untriaged issue/backlog/report | 1. Triage |
| New or unclear work | 2. Align |
| Alignment exists, but needed PRD/tasks are missing | 3. Plan |
| Plan exists, but baseline is missing | 4. Prepare |
| Tasks remain | 5. Execute |
| Tasks done, but review missing | 6. Review |
| Review done, and QA is required | 7. QA |
| Gates passed | 8. Deliver |

Treat the sequence as a dependency graph, not a rigid script. Direct bug reports route from Align
into `diagnose`; unfamiliar areas route through `zoom-out`; UI work loads UI support Skills during
Align, not after implementation has already drifted.

Human checkpoints are required when the Workflow changes intent: after alignment questions expose a
scope decision, after hypotheses are ranked for a hard bug, before accepting an architecture
deepening path, and before push/publish/merge.

## Phase Gates

### 0. Foundation

Run `setup-matt-pocock-skills` when foundation files are missing or stale.

Gate: foundation files exist, or alternate repo paths are documented.

### 1. Triage

Run `triage` only for incoming, unevaluated work.

Gate: request is ready for agent, ready for human, blocked on info, duplicate, out of scope, or rejected.

### 2. Align

Run `grill-with-docs`. Use `prototype` only when a disposable design probe would answer a real decision.

Alignment artifact must state:

1. Scale: `light`, `standard`, or `full`.
2. Goal and non-goals.
3. Scope: expected files, routes, modules, or surfaces.
4. Verification: tests, browser paths, edge cases, and baseline command.
5. QA mode: `full`, `focused`, or `skip`, with reason.
6. Domain updates: `CONTEXT.md` / ADR paths changed, or explicitly unchanged.

Gate: alignment artifact exists. No production code in this phase.

### 3. Plan

Run `to-prd` for substantial work. Run `to-issues` when more than one independently verifiable slice is needed.

Each task must name files, behavior, first test, browser verification, and done criteria.

Tasks must be vertical tracer bullets: each slice should produce one observable behavior change that
can be tested, reviewed, and delivered independently. Do not create tasks that split "all tests",
"all implementation", and "all cleanup" into separate horizontal phases.

Gate: PRD/tasks exist, or the alignment artifact explains why they are skipped.

### 4. Prepare

Create a clean work surface according to repo convention.

- `light` with clean worktree: stay put; create branch `agent/<slug>` when useful.
- `standard` or `full`: prefer a sibling worktree `../<repo>-<slug>` on branch `agent/<slug>`.

Run the baseline command named in alignment/tasks and record command/result in `.scratch/<slug>/baseline.md`.

Gate: baseline is known. If baseline is red before your changes, stop, diagnose, or report blocker.

### 5. Execute

Work one vertical slice at a time.

- Unknown area -> `zoom-out`.
- Behavior change -> `tdd`.
- Bug, flake, or performance surprise -> `diagnose`.
- UI/browser-observable change -> `agent-web-interface-guide` with evidence recorded.
- Architecture friction -> pause slice and run `improve-codebase-architecture`.

Implementation rule: one failing behavior test, minimal code to pass, refactor while green. Do not
write all tests first and all code second. If a slice cannot get a meaningful test, write a
characterization harness or record the missing seam as a review finding before proceeding.

Gate per slice: relevant tests green, evidence recorded or explicitly not applicable, no critical finding open.

### 6. Review

Review before the next slice when risk is high, otherwise before QA/delivery.

- `light`: self-review is acceptable.
- `standard`: record self-review in `.scratch/<slug>/review.md`.
- `full`: use a fresh subagent diff review when available; otherwise record that no fresh reviewer was available.

Review must cover scope, tests, domain language, browser/QA evidence, risks, and findings.

Gate: review recorded; critical findings closed. Architecture findings route to `improve-codebase-architecture`.

### 7. QA

Run only for `QA mode: full` or `focused`.

- `full`: use `map-feature-scope` when the surface spans routes, roles, overlays, tabs, or shared state; then run `capture-feature-evidence`.
- `focused`: run `capture-feature-evidence` on the changed path plus one adjacent path. Use mapping only if the surface is unclear.
- `skip`: no QA, but the alignment artifact must say why.

Capture golden path, named edge cases, error/empty states, role variation, adjacent regressions, and blockers.

Gate: QA evidence exists, or skip reason exists.

### 8. Deliver

Before final response, confirm tests, completed tasks, review status, QA evidence or skip reason, and remaining risk.

Delivery policy:

- User asked for PR: commit intentionally, push, open/update PR.
- User asked for local-only: do not PR; report files and verification.
- User asked to finish end-to-end and repo has local-merge convention: merge only after tests and QA pass.
- No delivery preference: stop after verification and ask before push, publish, or merge.

## Handoff Rules

- If a required Skill or pinned Plugin is unavailable, stop and report the missing surface.
- If requirements change, return to Phase 2 before changing scope.
- If user intent is still ambiguous after alignment, ask the user rather than manufacturing a plan.
- If tests fail for unrelated baseline reasons, separate baseline instability from the requested work.
- If no meaningful test seam exists, record that as a finding and strengthen review/QA.
- If the work exposes architecture friction, hand off to `improve-codebase-architecture` with concrete files and symptoms.
- If browser/product evidence is required but unavailable, stop rather than planning or coding from assumptions.

## Guardrails

- No production code before alignment.
- No behavior change outside TDD, diagnosis, or characterization.
- No user-visible done claim without browser evidence or a written QA skip.
- No new scope without returning to alignment.
- No invented Plugin behavior; `workflow.json` pins define available Plugins.
- No direct publish, push, merge, or destructive git action unless explicitly requested or already covered by delivery policy.
