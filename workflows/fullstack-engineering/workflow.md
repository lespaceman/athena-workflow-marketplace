# Full-Stack Engineering Workflow

A state machine with evidence gates that carries a change from user intent to verified delivery. You, the agent, do the implementation; the Skills it names are instructions for how to handle a given task or phase.

## Operating Principle

Build only from evidence.
Missing evidence -> gather it; ungatherable -> stop and name what is missing.
A phase completes only when its artifact exists and its gate passes.
Record artifacts durably - tracker, handoff artifact, committed change, or file - never only in your head or the conversation.
This is a dependency graph, not a script. Skip a phase only when either (a) its artifact already exists and is **current** - current = no Reset Rule trigger has fired since it was produced - or (b) the chosen path does not require it per the State Graph shortcuts. Never skip a phase when a later gate needs evidence only that phase owns.

## Delegation

Delegation = a subagent (Task tool) runs work in its own context and returns only its conclusion; file dumps and intermediate reasoning never enter the main thread.

Must delegate to a subagent: heavy reading, codebase exploration, and analysis - the file-dump-heavy work that would otherwise flood main context. Orientation's system inspection runs in subagents; so do the exploration parts of Problem Definition (`capture-feature-evidence`) and Build (reading a module to change it).

Must NOT delegate - run in the main agent: test execution and build/verification commands (`npx playwright test`, etc.). The raw pass/fail output is the proof and must stay in the main thread.

## Skill Discipline

Each phase below names its Skills.
When a phase's trigger holds, load that Skill **before** the next action.
Every Skill here is model-invocable.
A phase action that needed a Skill but ran without it is a workflow failure.
Playwright is the automation execution layer.

- Announce each load in one line: `Loading <skill> - trigger: <what you observed>.`
- Record loaded Skills in the phase artifact.
- Do not start a Skill-owned action until that Skill is loaded for the current turn or delegated subtask. A Skill loaded in a previous session does not count.
- Do not substitute memory, old summaries, or generic reasoning for a missing Skill. If a required Skill or Plugin is unavailable, or you cannot tell which Skill owns the activity, stop and report it.

Not phase-bound - load whenever their trigger fires, in any phase:

- `zoom-out` - about to read or change a module not yet mapped this session.
- `diagnose` - something is broken, failing, throwing, or slower than expected.
- `linear` - tracker state in Linear must be read or written.
- `triage` - an incoming bug/feature/issue must be classified or prepared.
- `handoff` - work is blocked, deferred, or being transferred to another agent/session. Unlike the others above, this is not an inline load-and-continue skill; it is the Stop -> handoff route into Phase 10, and current work cannot continue in this session after it fires.

## Task Tracker Discipline

At session start: read tracker/issue/handoff/prior notes, reconcile done/pending/blocked/unknown work, and record the current phase before changing files.

If Linear is source of truth, load `linear` first - it owns the issue-pickup procedure. Workflow constraint: drive status only through the gates (In Review when code-complete, Done only per Mandatory Gates), commenting at each transition with justifying evidence.

Prefer a visible tracker, active task tool, or handoff artifact - the session note must live in one.
A conversation-only note does not survive compaction: re-persist it to a durable artifact before any compaction or handoff.
The note must carry: current phase, goal, loaded Skills, completed artifacts, pending artifacts, blocker (or `None`), next action, last verification result (or `Not run`).

## Source Control Discipline

Keep the remote working branch current so a lost worktree, crash, or context reset never loses committed work.

- Never work on `main`. Establish the working branch (or `git worktree`) at the start of the run, before the first artifact is committed; Build still re-confirms the green baseline on it before the first code change.
- Commit **and push** whenever a unit of work lands: each phase artifact that is a repo file, and each completed vertical slice. A local-only commit is not enough - the push is what makes the work recoverable.
- Pushing your own working branch is a routine safety checkpoint and needs no user approval. It is distinct from PR / publish / merge to `main`, which is outward delivery and stays authority-gated (Phase 9).
- Commit messages name the artifact or slice and its proof state. Never commit secrets; remove temporary instrumentation before the artifact commit.
- If the remote is unreachable or a push fails, keep committing locally, record the failure as a blocker in the session note, and route to Handoff (Phase 10) if the work cannot otherwise be preserved.

## State Graph

Default path:

**Intake -> Orientation -> Problem Definition -> Design -> Implementation Plan -> Build -> Verification -> Review -> Delivery -> Handoff / Postmortem**

Valid shortcuts (invalid if a skipped phase owns evidence a later gate needs):

- Read-only request: stop after the first phase that answers it.
- Tiny local edit: Intake -> Orientation -> Build -> Verification -> Review -> Delivery.
- Confirmed bug: Intake -> Orientation -> Problem Definition with `diagnose`, then rejoin the default path.
- User-visible UI: must pass Design with `frontend-design` and Verification with browser evidence.
- Broad product testing: must pass product evidence -> coverage plan -> TC specs -> spec review before automation.
- Production-sensitive work: no shortcuts.

## Phases

Each phase produces its artifact and clears its gate before the next begins.

Every `Stop` below is tagged with its channel so the response is unambiguous:

- **Stop -> ask user** - halt, put a specific question to the user; no guessing.
- **Stop -> resolve** - halt, fix it yourself (often loop or return to an earlier phase).
- **Stop -> handoff** - halt, route to Handoff (Phase 10) with full state; work cannot continue here.

**1. Intake** - Choose the workflow path.
State the outcome; classify the task as one of the types that maps to a path (bug, feature, UI, test, production-sensitive); identify constraints.
Skills: `triage` to classify an incoming issue, `linear` when tracker state is part of the task.
Artifact: goal statement, task type, constraints, current phase.
Gate: outcome is specific enough to verify.
Stop -> ask user if goals conflict, the target surface is unknown, or intent cannot be inferred safely.
Do not turn ambiguity into a private plan.

**2. Orientation** - Know the system before changing it.
Inspect structure, conventions, commands, relevant modules, tests, domain docs, ADRs.
Confirm the test suite runs and record its pass/fail state in the orientation note - Build re-confirms against this baseline.
Delegate heavy reading/exploration to subagents (see Delegation).
Skills: `setup-matt-pocock-skills` first when the repo lacks the agent-skills context (other engineering Skills depend on it); `zoom-out` before touching any unmapped module.
Artifact: orientation note (surfaces, commands, conventions, risks, open questions, baseline suite pass/fail state).
Gate: likely files, test surfaces, commands, and risks can be named, and the baseline suite state is recorded.
Stop -> handoff if required context is inaccessible or no safe first surface exists.
Do not implement from filename guesses.

**3. Problem Definition** - Convert intent into observable behavior.
Define current and desired behavior; identify affected users/roles/systems/callers; define acceptance criteria.
Skills: `grill-with-docs`/`grill-me` for alignment, `diagnose` for bugs, `map-feature-scope` + `capture-feature-evidence` when product behavior must be observed.
Artifact: acceptance criteria, reproduction loop or feature slice, evidence gaps.
Gate: success and failure are externally observable.
Stop -> ask user if a feature has no smallest useful vertical slice.
Stop -> handoff if a bug cannot be reproduced or required product evidence is unavailable.
Do not fix before reproducing or plan from imagined behavior.

**4. Design** - Choose the smallest coherent approach.
Select the approach; identify changed surfaces and risks.
Skills: `frontend-design` for UI, `shadcn-ui` for shadcn work, `prototype` only for a real design question, `improve-codebase-architecture` only for concrete architecture friction.
Artifact: design note, expected changed surfaces, risks and rollback/mitigation.
Gate: design fits project conventions or the exception is explicit.
Stop -> ask user if the design changes user intent, public contracts widen without reason, or production risk lacks mitigation.
Do not add architecture to make the task feel important or promote prototype code without review.

**5. Implementation Plan** - Split work into safe vertical steps.
Create vertical steps and name the proof for each.
Skills: `to-prd` for substantial/production-sensitive requirements, `to-issues` for multi-slice work, `exploratory-test-writer`/`plan-test-coverage`/`generate-test-cases`/`review-test-cases` when testing artifacts are required.
Artifact: stepwise plan, verification commands or evidence sources, plus PRD/issues/coverage plan/reviewed specs when required.
Gate: the first step is clear, small, and verifiable.
Stop -> resolve if the plan is horizontal or required specs are unreviewed; Stop -> handoff if coverage planning depends on missing evidence that cannot be gathered.
Do not split by layers or write executable tests from unreviewed specs.

**6. Build** - Implement one complete vertical slice.
Before the first slice, the green baseline must be current for the exact tree you will modify (on the working branch/worktree established per Source Control Discipline). If isolation created a fresh worktree, reinstalled dependencies, or otherwise changed the build context since Orientation, run the full suite on that isolated tree to re-confirm - never skip. If the working branch is the same tree Orientation recorded green and nothing has changed it since, that baseline stands; do not re-run.
If the baseline is red or the suite cannot run where the change will happen, stop and resolve or record why before any change.
Then set the slice's proof condition and build only the active slice; commit and push each completed slice (Source Control Discipline).
Skills: `tdd` for behavior changes (failing test first; code written before its test is deleted), `analyze-test-codebase` to understand an existing Playwright suite, `add-playwright-tests`/`write-test-code` for Playwright tests, `frontend-design`/`shadcn-ui`/`agent-web-interface-guide` for UI, `diagnose` for unexpected failures.
Artifact: isolated branch/worktree with a recorded green baseline, each completed slice committed and pushed, code changes, test changes, notes for intentional deviations.
Gate: the slice builds on a verified-green baseline or the failure is understood and recorded.
Loop if a failure has a clear local fix.
Stop -> ask user if scope expands beyond the accepted design or new production-sensitive risk appears; Stop -> handoff if required verification is impossible here.
Do not clean up unrelated code, leave debug output, or widen interfaces without a recorded reason.

**7. Verification** - Prove the change works.
Run narrow verification first, expand as blast radius requires, rerun bug reproduction loops, gather browser evidence for UI claims, run Playwright execution in the main agent.
Skills: `agent-web-interface-guide` for browser evidence, `fix-flaky-tests` for a flaky or timing-out test, `define-smoke-scope`/`define-regression-scope` for release confidence.
Artifact: commands run, browser/product evidence, pass/fail result, remaining unverified risk.
Gate: verification supports the acceptance criteria.
Loop if a failure is understood and the next fix is evidence-based.
Stop -> handoff if tests cannot run or the environment is missing; Stop -> resolve if results are ambiguous or product evidence contradicts the implementation (return to Problem Definition or Build as the Reset Rules direct).
Do not treat a flaky pass as confidence or hide failed commands.

**8. Review** - Inspect the change as if reviewing a PR.
Check acceptance criteria, regressions, brittle tests, coupling, cleanup, docs, migrations, config, generated artifacts, and security (see Mandatory Gates for the security checklist). Security findings block, not advise.
Skills: `review-test-cases` for spec review, `review-test-code` for Playwright code, `improve-codebase-architecture` when review finds architecture friction.
Artifact: review notes, resolved findings (including security), residual risks.
Gate: blocking findings - including security - are resolved or explicitly documented.
Loop if findings are local and fixable.
Stop -> resolve if review exposes a scope change or missing evidence from an earlier phase (return to the phase the Reset Rules name).
Do not bury blockers as follow-up suggestions.

**9. Delivery** - Package the work for handoff, PR, or merge.
Summarize changes, verification, files/artifacts, risks, follow-up.
Skills: `linear` for tracker updates - Done only per Mandatory Gates; otherwise leave it In Review with a comment naming the outstanding gate.
Default for local worktree work, after a final full-suite green run (and, for user-visible work, a whole-feature browser pass - golden path plus the edge cases named in the design), the worktree lifecycle resolves one of two ways:

- **Merge.** Auto-merge only on a clean fast-forward or clean merge to `main`, then remove the worktree. Stop -> ask user if the merge has conflicts, the base is not `main`, or the tree is dirty.
- **Abandon.** Work rejected -> remove the worktree and delete the branch **only after typed user confirmation**. Never auto-discard.

Pushing your own working branch is a routine safety checkpoint (Source Control Discipline) and needs no approval. PR / publish / merge to `main` or any shared branch is outward delivery - do it only when requested or workflow-owned, and via the worktree lifecycle above.
Artifact: delivery summary plus tracker update/commit/PR reference when applicable.
Gate: the user can understand what changed and how it was proven.
Stop -> ask user if external delivery lacks authority or production risk is unresolved.
Do not imply production readiness from local verification alone.

**10. Handoff / Postmortem** - Preserve state when work cannot finish or should teach the next run.
Record phase, completed work, blocker, next command, next decision, evidence links.
Skills: `handoff` to capture state, `to-issues`/`linear` for durable follow-up.
Artifact: handoff or postmortem note.
Gate: another agent can resume without rediscovery.
Stop -> ask user if sensitive information cannot be safely redacted.
Do not say "continue from here" without defining "here".

## Reset Rules

Return to an earlier phase when evidence invalidates the current path: new scope -> Problem Definition; new public contract -> Design; product behavior differs from assumption -> Problem Definition; test spec changes materially -> Implementation Plan; test code changes materially after review -> Review; verification reveals a different bug -> Problem Definition with `diagnose`; production risk appears -> Design and Verification become mandatory.

## Mandatory Gates

Phase 7 (verification) and Phase 8 (review) are hard gates - never skipped, deferred, or self-waived. Only the user waives, and only a specific named gate.

- **Phase 7 clears when:** required verification ran and supports the acceptance criteria; user-visible work has browser/product evidence or a recorded skip reason. A passing unit suite alone does not clear it for user-visible work.
- **Phase 8 security checklist** (canonical; referenced from Phase 8): no secrets committed; authz/authn paths reviewed for any changed endpoint; new dependencies vetted. Security findings block - resolve them, do not log as follow-ups.

No work reaches Delivery, and no Linear issue moves to Done, until both gates pass or the user waives. A "done" claim without both cleared or waived is a workflow failure.
Unattended with no user to waive a blocked gate: route to Handoff (Phase 10) with full state - never self-waive, never stall.

## Completion Gate

Beyond the Mandatory Gates, complete only when: acceptance criteria are satisfied, temporary instrumentation is removed, and the tracker + final summary state what changed, how it was verified, and remaining risk.

## Handoff Rules

Stop and hand off when required evidence cannot be gathered, a required Skill/Plugin is unavailable, environment or credentials are missing, a user decision is required, or work cannot finish this session. The note carries what Phase 10 specifies.

## Guardrails

Phase "Do not" lines and the State Graph order are binding; not repeated here. Beyond those, do not: overwrite user changes; convert uncertainty into confidence; invent Plugin behavior; or put low-level implementation procedure in this Workflow (load the owning Skill).
