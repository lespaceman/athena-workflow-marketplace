# Full-Stack Engineering Workflow

Ship non-trivial engineering work without guessing. Every phase has an artifact. If the artifact is missing, you are not in the next phase.

## Skills

Use only the ten Matt Pocock engineering skills bundled in `matt-pocock-skills`:

- `setup-matt-pocock-skills` - repo foundation.
- `triage` - incoming work state machine.
- `grill-with-docs` - alignment against `CONTEXT.md` and ADRs.
- `prototype` - disposable design probe.
- `to-prd` - PRD from current context.
- `to-issues` - vertical-slice task breakdown.
- `zoom-out` - map unfamiliar code.
- `tdd` - red-green-refactor.
- `diagnose` - reproduce, minimise, hypothesise, instrument, fix, regression-test.
- `improve-codebase-architecture` - deepen architecture when drift appears.

Use marketplace support skills when the domain demands them:

- UI: `frontend-design:frontend-design`
- UI primitives: `shadcn:shadcn-ui`
- TanStack apps: `tanstack-start:tanstack-start-guide`
- Browser verification: `agent-web-interface:agent-web-interface-guide`
- Manual QA: `app-exploration:map-feature-scope`, `app-exploration:capture-feature-evidence`

## Scale

Classify once in the alignment artifact.

- `light` - one bounded change. Needs foundation, alignment, prepare, execution, review, delivery. PRD/issues/manual QA can be skipped with reasons.
- `standard` - normal feature, bug fix, or refactor. Default. PRD/issues/manual QA may be skipped only when the artifact says why.
- `full` - risky, architectural, cross-module, multi-route, role-sensitive, auth/payment/security, or broad user-visible work. Requires PRD/issues and manual QA.

If unsure, choose the larger scale.

## Artifacts

Use one slug for the run: `agent/<slug>` for branch names and `.scratch/<slug>/` for local artifacts.

Required artifacts:

- Alignment: `.scratch/<slug>/alignment.md` or issue comment.
- PRD, when needed: `.scratch/<slug>/prd.md` or issue.
- Tasks, when needed: `.scratch/<slug>/tasks.md` or issues.
- Baseline: `.scratch/<slug>/baseline.md`.
- Review: `.scratch/<slug>/review.md`.
- QA, when needed: `e2e-plan/feature-map.md`, `e2e-plan/exploration-report.md`, or scoped files under `e2e-plan/exploration/`.

If the repo has no issue tracker, use local files. Do not block on missing GitHub/GitLab unless the user explicitly required issue creation.

## Entry

Run the foundation check first:

```bash
test -f CONTEXT.md && test -d docs/adr && test -s docs/agents/triage-labels.md
```

If it fails, enter Phase 0. If the repo intentionally uses different paths, document those paths in the alignment artifact before treating foundation as present.

Then choose the first matching phase:

| State | Phase |
|---|---|
| Foundation missing or stale | 0. Foundation |
| Untriaged issue/backlog/report | 1. Triage |
| New or unclear work | 2. Align |
| Alignment exists, plan missing | 3. Plan |
| Plan exists, baseline missing | 4. Prepare |
| Tasks remain | 5. Execute |
| Tasks done, review missing | 6. Review |
| Review done, QA required | 7. QA |
| Everything done | 8. Deliver |

Examples:

- Expired-card checkout bug: Align, then `diagnose` once reproduced.
- Settings page with API persistence: Align with `frontend-design`; add `shadcn-ui` and `tanstack-start-guide` if relevant.

## Phase 0. Foundation

Run `setup-matt-pocock-skills` when `CONTEXT.md`, `docs/adr`, issue tracker conventions, or triage labels are missing/stale.

Exit: foundation files exist, or alternate repo paths are documented.

## Phase 1. Triage

Run `triage` only for incoming, unevaluated work.

Exit: the issue/task is ready for agent, ready for human, blocked on info, duplicate, out of scope, or rejected.

## Phase 2. Align

Run `grill-with-docs`. Use `prototype` only when seeing a design run would answer a real question.

Load support skills during alignment, not after:

- UI output -> `frontend-design`
- component primitives/theming -> `shadcn-ui`
- TanStack routing/server work -> `tanstack-start-guide`

Alignment artifact must contain:

1. Scale: `light`, `standard`, or `full`.
2. Goal.
3. Scope: exact files/routes/modules expected to change.
4. Non-goals.
5. Verification: tests, browser paths, edge cases.
6. QA mode: `full`, `focused`, or `skip`.
7. Domain updates: `CONTEXT.md` / ADR paths changed, or explicitly unchanged.

QA modes:

- `full` - broad or risky user-visible work. Run Phase 7.
- `focused` - bounded user-visible work. Browser-check changed path plus one adjacent path.
- `skip` - docs-only, test-only, internal refactor with no runtime behavior change, or tiny non-shared copy/style change. Say why.

Exit: alignment artifact exists. No production code in this phase.

## Phase 3. Plan

Run `to-prd` for substantial work. Skip only when the alignment artifact is enough.

Run `to-issues` when there is more than one independently verifiable slice.

Each task must name:

- files,
- behavior,
- first test,
- browser verification,
- done criteria.

Exit: PRD/tasks exist, or skip reason is written in alignment.

## Phase 4. Prepare

Create a clean surface before code.

- Existing repo convention wins.
- `light` + clean worktree: stay put, create branch `agent/<slug>`.
- `standard` / `full`: create sibling worktree `../<repo>-<slug>` on branch `agent/<slug>`.

Run the baseline command named in alignment/tasks. Record command and result in `.scratch/<slug>/baseline.md`.

If baseline is red before your changes, stop. Diagnose baseline or report blocker. Do not mix baseline repair with feature work unless alignment changes.

Exit: branch/worktree exists, dependencies known, baseline recorded.

## Phase 5. Execute

One vertical slice at a time.

- Unknown area -> `zoom-out`.
- Behavior change -> `tdd`.
- Bug/flaking/perf surprise -> `diagnose`.
- UI/browser-observable change -> load `agent-web-interface:agent-web-interface-guide`, exercise the path, record evidence.

TDD rule: one failing behavior test, minimal code, passing test, refactor while green. No horizontal "all tests then all code" work.

For generated config, migrations, or hard-to-test refactors: write a characterization test when possible. If no meaningful test seam exists, record why in the task artifact and compensate with stronger review/browser/manual verification.

Exit per slice: tests green, evidence recorded or explicitly not applicable, no critical finding open.

## Phase 6. Review

Review before the next slice, or before QA if all slices are done.

Mechanism:

- `light`: self-review.
- `standard`: self-review recorded in `.scratch/<slug>/review.md`.
- `full`: fresh subagent diff review when available; otherwise record that no fresh reviewer was available.

Review template:

```md
## Review
- Scope:
- Tests:
- Domain language:
- Browser/QA evidence:
- Risks:
- Findings: critical / major / minor / none
```

Critical findings block forward motion.

Run `improve-codebase-architecture` when naming drifts, modules tangle, the branch crosses boundaries, the diff is no longer small, or review finds architecture risk.

Exit: review recorded; critical findings closed.

## Phase 7. QA

Run only for `QA mode: full` or `focused`.

- `full`: use `map-feature-scope` when the surface spans routes, roles, overlays, tabs, or shared state; then run `capture-feature-evidence`.
- `focused`: run `capture-feature-evidence` on the changed path plus one adjacent path. Use mapping only if the boundary is unclear.
- `skip`: no Phase 7, but the alignment artifact must say why.

Capture golden path, named edge cases, error/empty states, role variation, adjacent regressions, and blockers.

Exit: QA evidence exists, or skip reason exists.

## Phase 8. Deliver

Before final response, confirm:

- relevant tests ran,
- tasks complete,
- browser/QA evidence exists or is explicitly skipped,
- critical findings are closed,
- changed files and verification are summarized.

Delivery policy:

- User asked for PR: commit intentionally, push, open/update PR.
- User asked for local-only: do not PR; report files and verification.
- User asked to finish end-to-end and repo has local-merge convention: merge only after tests and QA pass.
- No delivery preference: stop after verification and ask before push, publish, or merge.

Commit policy:

- Commit only coherent completed slices.
- Message format: `<area>: <behavior change>`.
- Commit body names tests/QA evidence for non-trivial work.

Stop on failed tests, conflicts, missing credentials, unrelated user changes, or destructive fallback.

## Hard Rules

- No production code without alignment.
- No behavior change outside the TDD/characterization loop.
- No user-visible done claim without browser evidence or written QA skip.
- No new scope without returning to alignment.
- No architecture drift without review; use `improve-codebase-architecture` when needed.
- No invented plugin behavior. If a skill is unavailable, stop and report the missing plugin or pin.
