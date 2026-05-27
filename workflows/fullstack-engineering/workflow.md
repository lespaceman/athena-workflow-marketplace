# Full-Stack Engineering Workflow

Carry a change from user intent to verified delivery. This is a state machine with evidence gates that orchestrates specialist Skills; it does not teach their internal methods.

## Operating Principle

Build only from evidence. If evidence is missing, gather it; if it cannot be gathered, stop and name what is missing. A phase is complete only when its artifact exists and its gate passes. This is a dependency graph, not a script - skip a phase only when its artifact already exists and is current.

## Plugins

Required Plugin surfaces. If any is unavailable at runtime, stop and report it instead of continuing from memory.

| Plugin | Skills |
|--------|--------|
| `matt-pocock-skills` | `setup-matt-pocock-skills`, `triage`, `grill-with-docs`, `grill-me`, `prototype`, `to-prd`, `to-issues`, `zoom-out`, `tdd`, `diagnose`, `improve-codebase-architecture`, `handoff` |
| `linear` | `linear` |
| `frontend-design` | `frontend-design` |
| `shadcn` | `shadcn-ui` |
| `agent-web-interface` | `agent-web-interface-guide` |
| `app-exploration` | `map-feature-scope`, `capture-feature-evidence` |
| `exploratory-testing` | `exploratory-test-writer` |
| `test-analysis` | `plan-test-coverage`, `generate-test-cases`, `review-test-cases` |
| `playwright-automation` | `analyze-test-codebase`, `add-playwright-tests`, `write-test-code`, `review-test-code`, `fix-flaky-tests` |
| `smoke-testing` | `define-smoke-scope` |
| `regression-testing` | `define-regression-scope` |

## Skill Routing

When a trigger below holds, load that Skill **before** the next action - on your own judgment, without waiting to be asked. Every Skill here is model-invocable. A phase action that needed a Skill but ran without it is a workflow failure.

Rules:

- Announce each load in one line: `Loading <skill> - trigger: <what you observed>.`
- Record loaded Skills in the phase artifact.
- Do not start a Skill-owned action until that Skill is loaded for the current turn or delegated subtask. A Skill loaded in a previous session does not count.
- Do not substitute memory, old summaries, or generic reasoning for a missing Skill. If a required Skill or Plugin is unavailable, or you cannot tell which Skill owns the activity, stop and report it.

| Auto-load when | Skill |
|----------------|-------|
| First engineering action in a repo whose `CLAUDE.md`/`AGENTS.md` lacks an `## Agent skills` block or `docs/agents/` - load at Orientation before any other engineering Skill | `setup-matt-pocock-skills` |
| Tracker state in Linear must be read or written | `linear` |
| An incoming bug/feature/issue must be classified or prepared | `triage` |
| A plan must be checked against the repo's domain model or terminology | `grill-with-docs` |
| A plan needs stress-testing and there is no repo/domain doc to anchor it | `grill-me` |
| About to read or change code in a module not yet mapped this session | `zoom-out` |
| Something is broken, failing, throwing, or slower than expected | `diagnose` |
| A design question needs a throwaway prototype | `prototype` |
| Requirements are substantial or production-sensitive | `to-prd` |
| Work spans multiple independently-shippable slices | `to-issues` |
| Concrete architecture friction is blocking the change | `improve-codebase-architecture` |
| About to write or change production behavior | `tdd` |
| The output is user-visible UI | `frontend-design` |
| Building with shadcn primitives | `shadcn-ui` |
| A live page must be driven or observed | `agent-web-interface-guide` |
| A broad feature spans many surfaces and must be split | `map-feature-scope` |
| Live product behavior must be observed and captured | `capture-feature-evidence` |
| A risk-based exploratory charter is needed | `exploratory-test-writer` |
| Test coverage must be planned from evidence | `plan-test-coverage` |
| TC-ID test specs must be written | `generate-test-cases` |
| Specs must be reviewed before any test code | `review-test-cases` |
| An existing Playwright suite must be understood | `analyze-test-codebase` |
| Playwright tests must be written | `add-playwright-tests` or `write-test-code` |
| Playwright test code must be reviewed | `review-test-code` |
| A Playwright test is flaky, timing out, or inconsistent | `fix-flaky-tests` |
| Smoke-test scope must be defined | `define-smoke-scope` |
| Regression-test scope must be defined | `define-regression-scope` |
| Work is blocked, deferred, or handed to another agent | `handoff` |

If you catch yourself thinking any of these, you are skipping a Skill load - stop and load it: "I already understand this repo's setup" (load `setup-matt-pocock-skills` if the agent-skills context is absent); "I'll just read the files to get oriented" (load `zoom-out`); "I know the design, I can skip alignment" (load `grill-with-docs`/`grill-me`); "I'll write the code, then add a test" (load `tdd`, write the failing test first); "this Skill is for the user to invoke" (every Skill here is model-invocable); "tests pass, so it's done" (load `agent-web-interface-guide` for browser evidence on user-visible work); "I'll note the Skill in the summary instead of loading it" (naming is not loading).

## Task Tracker Discipline

At session start: read tracker/issue/handoff/prior notes, reconcile done/pending/blocked/unknown work, and record the current phase before changing files.

If Linear is source of truth, load `linear` first. On picking up any issue it requires you to: read the issue in full (description, comments, labels, state, relations) **and its parent project**; read **all attachments and documents on both** before planning; assign to yourself and move to In Progress before writing code; drive status only through the gates (In Review when code-complete, Done only after the Phase 7 and Phase 8 gates pass and the work is merged), commenting at each transition with justifying evidence.

Prefer a visible tracker, active task tool, or handoff artifact. If none exists, keep a session execution note in the conversation - not in repo files unless the user asks or a workflow artifact already owns that path. The note must carry: current phase, goal, loaded Skills, completed artifacts, pending artifacts, blocker (or `None`), next action, last verification result (or `Not run`).

## State Graph

Default path:

**Intake -> Orientation -> Problem Definition -> Design -> Implementation Plan -> Build -> Verification -> Review -> Delivery -> Handoff / Postmortem**

Valid shortcuts (invalid if a skipped phase owns evidence a later gate needs):

- Read-only request: stop after the first phase that answers it.
- Tiny local edit: Intake -> Orientation -> Build -> Verification -> Delivery.
- Confirmed bug: Intake -> Orientation -> Problem Definition with `diagnose`.
- User-visible UI: must pass Design with `frontend-design` and Verification with browser evidence.
- Broad product testing: must pass product evidence -> coverage plan -> TC specs -> spec review before automation.
- Production-sensitive work: no shortcuts.

## Phases

Each phase produces its artifact and clears its gate before the next begins. `Stop if` conditions mean halt and resolve or hand off.

**1. Intake** - Choose the workflow path. State the outcome; classify the task (bug, feature, refactor, UI, test, research, delivery, incident, production-sensitive); identify constraints; use `linear`/`triage` when tracker state is part of the task. Artifact: goal statement, task type, constraints, current phase. Gate: outcome is specific enough to verify. Stop if goals conflict, the target surface is unknown, or intent cannot be inferred safely. Do not turn ambiguity into a private plan.

**2. Orientation** - Know the system before changing it. Inspect structure, conventions, commands, relevant modules, tests, domain docs, ADRs. Load `setup-matt-pocock-skills` first when the repo lacks the agent-skills context (other engineering Skills depend on it). Load `zoom-out` before touching any module not yet mapped this session. Artifact: orientation note (surfaces, commands, conventions, risks, open questions). Gate: likely files, test surfaces, commands, and risks can be named. Stop if required context is inaccessible or no safe first surface exists. Do not implement from filename guesses.

**3. Problem Definition** - Convert intent into observable behavior. Define current and desired behavior; identify affected users/roles/systems/callers; define acceptance criteria. Use `grill-with-docs`/`grill-me` for alignment, `diagnose` for bugs, `map-feature-scope` + `capture-feature-evidence` when product behavior must be observed. Artifact: acceptance criteria, reproduction loop or feature slice, evidence gaps. Gate: success and failure are externally observable. Stop if a bug cannot be reproduced, a feature has no smallest useful vertical slice, or required product evidence is unavailable. Do not fix before reproducing or plan from imagined behavior.

**4. Design** - Choose the smallest coherent approach. Select the approach; identify changed surfaces and risks. Use `frontend-design` for UI, `shadcn-ui` for shadcn work, `prototype` only for a real design question, `improve-codebase-architecture` only for concrete architecture friction. Artifact: design note, expected changed surfaces, risks and rollback/mitigation. Gate: design fits project conventions or the exception is explicit. Stop if the design changes user intent, public contracts widen without reason, or production risk lacks mitigation. Do not add architecture to make the task feel important or promote prototype code without review.

**5. Implementation Plan** - Split work into safe vertical steps. Create vertical steps and name the proof for each. Use `to-prd` for substantial/production-sensitive requirements, `to-issues` for multi-slice work, and `exploratory-test-writer`/`plan-test-coverage`/`generate-test-cases`/`review-test-cases` when testing artifacts are required. Artifact: stepwise plan, verification commands or evidence sources, plus PRD/issues/coverage plan/reviewed specs when required. Gate: the first step is clear, small, and verifiable. Stop if the plan is horizontal, required specs are unreviewed, or coverage planning depends on missing evidence. Do not split by layers or write executable tests from unreviewed specs.

**6. Build** - Implement one complete vertical slice. Establish a baseline command (or record a skip reason) and the slice's proof condition. Build only the active slice. Use `tdd` for behavior changes, `diagnose` for unexpected failures, `frontend-design`/`shadcn-ui`/`agent-web-interface-guide` for UI, Playwright skills for Playwright automation. Artifact: code changes, test changes, notes for intentional deviations. Gate: the slice builds or the failure is understood and recorded. Loop if a failure has a clear local fix. Stop if scope expands beyond the accepted design, required verification is impossible, or new production-sensitive risk appears. Do not clean up unrelated code, leave debug output, or widen interfaces without a recorded reason.

**7. Verification** - Prove the change works. Run narrow verification first, expand as blast radius requires, rerun bug reproduction loops, gather browser evidence for UI claims, run Playwright execution in the main agent, and use `define-smoke-scope`/`define-regression-scope` for release confidence. Artifact: commands run, browser/product evidence, pass/fail result, remaining unverified risk. Gate: verification supports the acceptance criteria. Loop if a failure is understood and the next fix is evidence-based. Stop if tests cannot run, the environment is missing, results are ambiguous, or product evidence contradicts the implementation. Do not treat a flaky pass as confidence or hide failed commands.

**8. Review** - Inspect the change as if reviewing a PR. Check acceptance criteria, regressions, brittle tests, coupling, cleanup, docs, migrations, config, generated artifacts. Use `review-test-cases` for spec review, `review-test-code` for Playwright code, `improve-codebase-architecture` when review finds architecture friction. Artifact: review notes, resolved findings, residual risks. Gate: blocking findings are resolved or explicitly documented. Loop if findings are local and fixable. Stop if review exposes a scope change or missing evidence from an earlier phase. Do not bury blockers as follow-up suggestions.

**9. Delivery** - Package the work for handoff, PR, or merge. Summarize changes, verification, files/artifacts, risks, follow-up. Use `linear` for tracker updates - move the issue to Done **only after the Phase 7 and Phase 8 gates both pass and the work is merged**; otherwise leave it In Review with a comment naming the outstanding gate. Commit/push/open PR/publish/merge only when requested or explicitly workflow-owned. Artifact: delivery summary plus tracker update/commit/PR reference when applicable. Gate: the user can understand what changed and how it was proven. Stop if external delivery lacks authority or production risk is unresolved. Do not imply production readiness from local verification alone.

**10. Handoff / Postmortem** - Preserve state when work cannot finish or should teach the next run. Use `handoff`; record phase, completed work, blocker, next command, next decision, evidence links; use `to-issues`/`linear` for durable follow-up. Artifact: handoff or postmortem note. Gate: another agent can resume without rediscovery. Stop if sensitive information cannot be safely redacted. Do not say "continue from here" without defining "here".

## Reset Rules

Return to an earlier phase when evidence invalidates the current path: new scope -> Problem Definition; new public contract -> Design; product behavior differs from assumption -> Problem Definition; test spec changes materially -> Implementation Plan; test code changes materially after review -> Review; verification reveals a different bug -> Problem Definition with `diagnose`; production risk appears -> Design and Verification become mandatory.

## Mandatory Gates

The QA/verification gate (Phase 7) and code-review gate (Phase 8) are hard gates, not optional steps. They may not be skipped, deferred, or self-waived:

- **QA / verification (Phase 7):** required verification has run and supports the acceptance criteria; user-visible work has browser/product evidence or a recorded skip reason. A passing unit suite alone does not clear this gate for user-visible work.
- **Code review (Phase 8):** the diff has been reviewed against acceptance criteria, regressions, brittle tests, coupling, and cleanup. Critical findings block forward motion and must be resolved, not logged as follow-ups.

No work advances to Delivery, and no Linear issue moves to Done, until both gates pass or the user explicitly waives a specific gate. Only the user may waive a gate; the agent may not. A "done" claim without both gates cleared or explicitly waived is a workflow failure.

## Completion Gate

Complete only when: acceptance criteria are satisfied; both mandatory gates have passed (or a specific one was user-waived); relevant verification has run; review has no unresolved blockers; temporary instrumentation is removed; product evidence exists for user-visible claims (or a skip reason is recorded); test specs and code passed required review gates when used; the tracker reflects reality (Done only after gates pass and merge, with a closing comment of what changed, how it was verified, and remaining risk); and the final summary states what changed, how it was verified, and what risk remains.

## Handoff Rules

Stop and hand off when required evidence cannot be gathered, a required Skill/Plugin is unavailable, environment or credentials are missing, a user decision is required, or work cannot finish this session. The handoff must name current phase, completed artifacts, blocker, last verification result, and next action.

## Guardrails

Do not: guess when evidence can be gathered; implement before orientation; plan before problem definition; review before verification; deliver before review; call work done without verification; hide failed commands; overwrite user changes; convert uncertainty into confidence; invent Plugin behavior; or put low-level implementation procedure in this Workflow (load the owning Skill).
