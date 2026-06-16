# Full-Stack Engineering Workflow

A state machine with evidence gates that carries a change from user intent to verified delivery. You, the agent, do the implementation; the Skills it names are instructions for how to handle a given task or phase.

**This workflow is binding, not advisory.** Every phase has an artifact and a gate. You may not act outside the Turn Protocol below, and you may not enter a phase before emitting the prior phase's gate-pass. Skipping a phase, self-waiving a gate, or claiming "done" without the required proof is a workflow failure — not a shortcut.

## Turn Protocol — run EVERY turn, no exceptions

Before taking any action in a turn, emit this status block. If you cannot fill a field, that is the work to do next — do not act past it.

```
PHASE: <current phase name + number>
GOAL: <one-line outcome>
LAST GATE CLEARED: <phase + PASS, or "none yet">
SKILLS LOADED THIS TURN: <names, or "none needed">
NEXT ACTION: <the single next step>
BLOCKER: <None | description + Stop channel>
LAST VERIFICATION: <command + result, or "Not run">
```

Rules:
- No status block emitted -> you are not allowed to edit files, run commands, or call Skills this turn.
- The block is cheap and mandatory. Re-emit it after every phase transition and after every Stop.
- It must match a durable artifact (tracker/handoff/commit/file), never live only in the chat.

## Phase Transition Rule — the hard forcing function

You may NOT begin phase N+1 until you have, in the conversation, emitted:

```
GATE <phase N>: PASS — artifact: <where it lives durably> — evidence: <what proves the gate>
```

- One gate line per phase, before the next phase's first action. No line -> no transition.
- "Evidence" is observable: a command's output, a committed file, a tracker entry, browser proof. Never "I believe" / "it should".
- A gate you cannot honestly mark PASS is a Stop, not a downgrade. Route it per the phase's Stop channel.
- Mandatory Gates (Phase 7, Phase 8) are never marked PASS without the proof named there, and never self-waived.

## Operating Principle

Build only from evidence.
Missing evidence -> gather it; ungatherable -> Stop and name what is missing.
A phase completes only when its artifact exists AND its gate-pass line is emitted.
Record artifacts durably — tracker, handoff artifact, committed change, or file — never only in your head or the conversation.
This is a dependency graph, not a script. Skip a phase ONLY when either (a) its artifact already exists and is **current** — current = no Reset Rule trigger has fired since it was produced — or (b) the chosen path does not require it per the State Graph shortcuts. A skip still requires the gate line, citing the existing artifact. Never skip a phase when a later gate needs evidence only that phase owns.

## Delegation

Delegation = a subagent (Task tool) runs work in its own context and returns only its conclusion; file dumps and intermediate reasoning never enter the main thread.

- **MUST delegate to a subagent:** heavy reading, codebase exploration, and analysis — the file-dump-heavy work that would otherwise flood main context. Orientation's system inspection, the exploration parts of Problem Definition (`capture-feature-evidence`), and Build's read-a-module-to-change-it all run in subagents.
- **MUST NOT delegate — run in the main agent:** test execution and build/verification commands (`npx playwright test`, etc.). The raw pass/fail output is the proof and must stay in the main thread.

## Skill Discipline

Each phase names its Skills. When a phase's trigger holds, load that Skill **before** the next action. Every Skill here is model-invocable.

- **Announce each load on its own line, before the action:** `Loading <skill> — trigger: <what you observed>.` Record loaded Skills in the Turn Protocol block and the phase artifact.
- Do not start a Skill-owned action until that Skill is loaded for the current turn or delegated subtask. A Skill loaded in a previous session does not count.
- A phase action that needed a Skill but ran without it is a workflow failure — Stop, load it, redo the action.
- Do not substitute memory, old summaries, or generic reasoning for a named phase Skill you skipped. If a phase-named Skill or its Plugin is genuinely not installed, Stop and report it. An activity with no owning Skill is not a blocker — proceed with normal agent work.
- Skill availability comes from installed plugins, never from repo files: a missing `## Agent skills` block or un-run First-Run Setup never blocks loading a Skill. The block only configures tracker/triage/domain details for a few Skills.
- When test automation is needed, Playwright is the execution layer.

Not phase-bound — load whenever their trigger fires, in any phase:

- `zoom-out` — about to read or change a module not yet mapped this session.
- `diagnose` — something is broken, failing, throwing, or slower than expected.
- `linear` — tracker state in Linear must be read or written.
- `clickup` — tracker state in ClickUp must be read or written.
- `triage` — an incoming bug/feature/issue must be classified or prepared.
- `workflow-handoff` — an in-flight task must be relayed to the next agent: a slice/phase/gate boundary is cleanly done, or you are mid-task and out of usable context (token window exhausted, context rot). It captures resumable workflow state (Turn Protocol block, cleared gates, branch + last pushed commit, durable-artifact pointers, exact next action) so the next agent re-enters at the right phase. Use `handoff` instead for a generic conversation summary with no live workflow state to preserve. Like the route below, this is not inline load-and-continue — it is the Stop -> handoff into Phase 10, and current work cannot continue in this session after it fires.

## First-Run Setup

`setup-engineering-workflow` seeds per-repo config — issue tracker, triage labels, domain-doc layout — that the tracker/triage/domain-aware Skills read: `to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, `improve-codebase-architecture`, `zoom-out`. It is **mandatory once per repo** when the repo has no `## Agent skills` block (in `CLAUDE.md`/`AGENTS.md`) or `docs/agents/`. It does not gate Skills that ignore it — `frontend-design`, `shadcn-ui`, `linear`, `agent-web-interface-guide`, and the app/test/Playwright Skills load regardless, so a missing block never means zero Skills.

It is interactive (asks the user to choose tracker, confirm labels and domain layout, and which doc file to create) so it cannot be completed unattended. Treat it as a precondition only for work that actually reads that config; a missing block never blocks the config-free Skills and never applies to a read-only request.

When the block is missing AND the next required action needs tracker/triage/domain config:

- **User available:** run it now (commit it as its own setup change, separate from the change's diff), then proceed.
- **No user (AFK):** proceed with everything that does not need the config; Stop -> handoff (Phase 10) only for the specific config-dependent action, naming it. Never silently bootstrap repo docs; never stall over config-free work.

## Task Tracker Discipline

At session start: read tracker/issue/handoff/prior notes, reconcile done/pending/blocked/unknown work, and record the current phase before changing files.

- If Linear is source of truth, load `linear` first; if ClickUp is source of truth, load `clickup` first — the matching Skill owns the issue-pickup procedure. Drive status only through the gates (In Review when code-complete; Done only per Mandatory Gates), commenting at each transition with justifying evidence.
- The session note must live in a visible tracker, active task tool, or handoff artifact. A conversation-only note does not survive compaction: re-persist it to a durable artifact before any compaction or handoff.
- The note carries: current phase, goal, loaded Skills, completed artifacts, pending artifacts, blocker (or `None`), next action, last verification result (or `Not run`) — i.e. the Turn Protocol block, persisted.

## Source Control Discipline

Keep the remote working branch current so a lost worktree, crash, or context reset never loses committed work.

- **Never work on `main`.** Establish the working branch (or `git worktree`) at the start of the run, before the first artifact is committed; Build still re-confirms the green baseline on it before the first code change.
- **Commit AND push** whenever a unit of work lands: each phase artifact that is a repo file, and each completed vertical slice. A local-only commit is not enough — the push is what makes the work recoverable.
- Pushing your own working branch is a routine safety checkpoint and needs no user approval. PR / publish / merge to a shared branch is outward delivery and stays authority-gated; a clean merge to `main` after both Mandatory Gates pass is itself workflow-owned authority at Phase 9 (see Delivery).
- Commit messages name the artifact or slice and its proof state. Never commit secrets; remove temporary instrumentation before the artifact commit.
- If Orientation found no push rights (read-only clone, fork without write), local-commit-only is the sanctioned mode: keep committing locally and note it once, not per-artifact. If the remote was expected writable but a push fails or is unreachable, record it as a blocker in the session note and route to Handoff (Phase 10) if the work cannot otherwise be preserved.

## State Graph

Default path:

**1 Intake -> 2 Orientation -> 3 Problem Definition -> 4 Design -> 5 Implementation Plan -> 6 Build -> 7 Verification -> 8 Review -> 9 Delivery -> 10 Handoff / Postmortem**

Valid shortcuts (invalid if a skipped phase owns evidence a later gate needs — and each skip still needs its gate line citing the existing artifact):

- Read-only request: Stop after the first phase that answers it.
- Tiny local edit: 1 -> 2 -> 6 -> 7 -> 8 -> 9.
- Confirmed bug: 1 -> 2 -> 3 with `diagnose`, then rejoin the default path.
- User-visible UI: MUST pass Design with `frontend-design` and Verification with browser evidence.
- Broad product testing: MUST pass product evidence -> coverage plan -> TC specs -> spec review before automation.
- Production-sensitive work: no shortcuts.

## Phases

Each phase produces its artifact and emits its gate-pass line before the next begins. Every `Stop` is tagged with its channel so the response is unambiguous:

- **Stop -> ask user** — halt, put a specific question to the user; no guessing.
- **Stop -> resolve** — halt, fix it yourself (often loop or return to an earlier phase).
- **Stop -> handoff** — halt, route to Handoff (Phase 10) with full state; work cannot continue here.

---

**1. Intake** — Choose the workflow path.
- MUST: state the outcome; classify the task as one path type (bug, feature, UI, test, production-sensitive); identify constraints.
- Skills: `triage` to classify an incoming issue; `linear` when tracker state is part of the task.
- Artifact: goal statement, task type, constraints, current phase.
- Gate: outcome is specific enough to verify.
- Stop -> ask user if goals conflict, the target surface is unknown, or intent cannot be inferred safely.
- Do NOT turn ambiguity into a private plan.

**2. Orientation** — Know the system before changing it.
- MUST: inspect structure, conventions, commands, relevant modules, tests, domain docs, ADRs. Confirm the test suite runs and record its pass/fail state (Build re-confirms against this baseline). Confirm whether the remote is writable and record it. Delegate heavy reading/exploration to subagents.
- Skills: `zoom-out` before touching any unmapped module.
- Artifact: orientation note (surfaces, commands, conventions, risks, open questions, baseline suite pass/fail, push capability).
- Gate: likely files, test surfaces, commands, and risks can be named, AND the baseline suite state is recorded.
- Stop -> handoff if required context is inaccessible or no safe first surface exists.
- Do NOT implement from filename guesses.

**3. Problem Definition** — Convert intent into observable behavior.
- MUST: define current and desired behavior; identify affected users/roles/systems/callers; define acceptance criteria.
- Skills: `grill-with-docs`/`grill-me` for alignment; `diagnose` for bugs; `map-feature-scope` + `capture-feature-evidence` when product behavior must be observed.
- Artifact: acceptance criteria, reproduction loop or feature slice, evidence gaps.
- Gate: success and failure are externally observable.
- Stop -> ask user if a feature has no smallest useful vertical slice.
- Stop -> handoff if a bug cannot be reproduced or required product evidence is unavailable.
- Do NOT fix before reproducing or plan from imagined behavior.

**4. Design** — Choose the smallest coherent approach.
- MUST: select the approach; identify changed surfaces and risks.
- Skills: `frontend-design` for UI; `shadcn-ui` for shadcn work; `prototype` only for a real design question; `improve-codebase-architecture` only for concrete architecture friction.
- Artifact: design note, expected changed surfaces, risks and rollback/mitigation.
- Gate: design fits project conventions or the exception is explicit.
- Stop -> ask user if the design changes user intent, public contracts widen without reason, or production risk lacks mitigation.
- Do NOT add architecture to make the task feel important or promote prototype code without review.

**5. Implementation Plan** — Split work into safe vertical steps.
- MUST: create vertical steps and name the proof for each.
- Skills: `to-prd` for substantial/production-sensitive requirements; `to-issues` for multi-slice work; `exploratory-test-writer`/`plan-test-coverage`/`generate-test-cases`/`review-test-cases` when testing artifacts are required.
- Artifact: stepwise plan, verification commands or evidence sources, plus PRD/issues/coverage plan/reviewed specs when required.
- Gate: the first step is clear, small, and verifiable.
- Stop -> resolve if the plan is horizontal or required specs are unreviewed; Stop -> handoff if coverage planning depends on missing evidence that cannot be gathered.
- Do NOT split by layers or write executable tests from unreviewed specs.

**6. Build** — Implement one complete vertical slice.
- MUST, before the first slice: confirm the green baseline is current for the exact tree you will modify (on the working branch/worktree). If isolation created a fresh worktree, reinstalled deps, or otherwise changed the build context since Orientation, re-run the full suite on that isolated tree — never skip. If it is the same tree Orientation recorded green and nothing changed it, that baseline stands; do not re-run.
- If the baseline is red or the suite cannot run where the change will happen, Stop and resolve or record why before any change.
- MUST: set the slice's proof condition, build only the active slice, then commit and push the completed slice.
- Skills: `tdd` for behavior changes (failing test first; code written before its test is deleted); `analyze-test-codebase` to understand an existing Playwright suite; `add-playwright-tests`/`write-test-code` for Playwright tests; `frontend-design`/`shadcn-ui`/`agent-web-interface-guide` for UI; `diagnose` for unexpected failures.
- Artifact: isolated branch/worktree with a recorded green baseline; each completed slice committed and pushed; code changes; test changes; notes for intentional deviations.
- Gate: the slice builds on a verified-green baseline or the failure is understood and recorded.
- Loop if a failure has a clear local fix.
- Stop -> ask user if scope expands beyond the accepted design or new production-sensitive risk appears; Stop -> handoff if required verification is impossible here.
- Do NOT clean up unrelated code, leave debug output, or widen interfaces without a recorded reason.

**7. Verification** — Prove the change works. **MANDATORY GATE — never skipped, deferred, or self-waived.**
- MUST: run narrow verification first, expand as blast radius requires, rerun bug reproduction loops, gather browser evidence for UI claims, run Playwright execution in the main agent.
- Skills: `agent-web-interface-guide` for browser evidence; `fix-flaky-tests` for a flaky or timing-out test; `define-smoke-scope`/`define-regression-scope` for release confidence.
- Artifact: commands run, browser/product evidence, pass/fail result, remaining unverified risk.
- Gate: required verification ran and supports the acceptance criteria; user-visible work has browser/product evidence or a recorded skip reason. A passing unit suite alone does NOT clear it for user-visible work.
- Loop if a failure is understood and the next fix is evidence-based.
- Stop -> handoff if tests cannot run or the environment is missing; Stop -> resolve if results are ambiguous or product evidence contradicts the implementation (return to Problem Definition or Build as the Reset Rules direct).
- Do NOT treat a flaky pass as confidence or hide failed commands.

**8. Review** — Inspect the change as if reviewing a PR. **MANDATORY GATE — never skipped, deferred, or self-waived.**
- MUST check: acceptance criteria, regressions, brittle tests, coupling, cleanup, docs, migrations, config, generated artifacts, and security. Security findings block, not advise.
- **Security checklist (canonical):** no secrets committed; authz/authn paths reviewed for any changed endpoint; new dependencies vetted. Resolve findings — do not log as follow-ups.
- Skills: `review-test-cases` for spec review; `review-test-code` for Playwright code; `improve-codebase-architecture` when review finds architecture friction.
- Artifact: review notes, resolved findings (including security), residual risks.
- Gate: blocking findings — including security — are resolved or explicitly documented.
- Loop if findings are local and fixable.
- Stop -> resolve if review exposes a scope change or missing evidence from an earlier phase (return to the phase the Reset Rules name).
- Do NOT bury blockers as follow-up suggestions.

**9. Delivery** — Package the work for handoff, PR, or merge.
- MUST: summarize changes, verification, files/artifacts, risks, follow-up. No work reaches here until Phases 7 and 8 are PASS or user-waived.
- Skills: `linear` for tracker updates — Done only per Mandatory Gates; otherwise leave it In Review with a comment naming the outstanding gate.
- Default for local worktree work, after a final full-suite green run (and, for user-visible work, a whole-feature browser pass — golden path plus the edge cases named in the design), resolve the worktree one of two ways:
  - **Merge.** A clean merge to `main` after both Mandatory Gates pass is workflow-owned — no separate user request needed. Auto-merge only on a clean fast-forward or clean merge to `main`, then remove the worktree. Stop -> ask user if the merge has conflicts, the base is not `main`, or the tree is dirty.
  - **Abandon.** Work rejected -> remove the worktree and delete the branch **only after typed user confirmation**. Never auto-discard.
- Pushing your own working branch needs no approval. PR / publish / merge to `main` or any shared branch is outward delivery — do it only when requested or workflow-owned, via the lifecycle above.
- Artifact: delivery summary plus tracker update/commit/PR reference when applicable.
- Gate: the user can understand what changed and how it was proven.
- Stop -> ask user if external delivery lacks authority or production risk is unresolved.
- Do NOT imply production readiness from local verification alone.

**10. Handoff / Postmortem** — Preserve state when work cannot finish or should teach the next run.
- MUST record: phase, completed work, blocker, next command, next decision, evidence links.
- Skills: `workflow-handoff` to relay resumable workflow state (phase, cleared gates, branch + last pushed commit, next action) so the next agent resumes mid-flight; `handoff` for a generic conversation summary; `to-issues`/`linear` for durable follow-up.
- Artifact: handoff or postmortem note.
- Gate: another agent can resume without rediscovery.
- Stop -> ask user if sensitive information cannot be safely redacted.
- Do NOT say "continue from here" without defining "here".

## Reset Rules

Return to an earlier phase when evidence invalidates the current path: new scope -> Problem Definition; new public contract -> Design; product behavior differs from assumption -> Problem Definition; test spec changes materially -> Implementation Plan; test code changes materially after review -> Review; verification reveals a different bug -> Problem Definition with `diagnose`; production risk appears -> Design and Verification become mandatory.

On a shortcut path, a Reset that names a skipped phase is a promotion to the full path: enter that phase now (a join, not a return) and continue the default path from there — e.g. scope expansion during a tiny local edit promotes to Problem Definition. Re-emit the Turn Protocol block on every reset.

## Mandatory Gates

Phase 7 (Verification) and Phase 8 (Review) are hard gates — never skipped, deferred, or self-waived. Only the user waives, and only a specific named gate. Their PASS lines require the proof named in those phases (Phase 7: verification evidence incl. browser proof for user-visible work; Phase 8: resolved findings incl. the security checklist).

No work reaches Delivery, and no Linear issue moves to Done, until both gates pass or the user waives. A "done" claim without both cleared or waived is a workflow failure.
Unattended with no user to waive a blocked gate: route to Handoff (Phase 10) with full state — never self-waive, never stall.

## Completion Gate

Beyond the Mandatory Gates, complete only when: acceptance criteria are satisfied, temporary instrumentation is removed, and the tracker + final summary state what changed, how it was verified, and remaining risk.

## Handoff Rules

Stop and hand off when required evidence cannot be gathered, a required Skill/Plugin is unavailable, environment or credentials are missing, a user decision is required, or work cannot finish this session. The note carries what Phase 10 specifies.

## Guardrails

Phase "Do NOT" lines, the Turn Protocol, the Phase Transition Rule, and the State Graph order are binding. Beyond those, do not: overwrite user changes; convert uncertainty into confidence; invent Plugin behavior; or put low-level implementation procedure in this Workflow (load the owning Skill).
