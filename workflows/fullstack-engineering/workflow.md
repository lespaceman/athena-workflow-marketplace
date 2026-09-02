# Full-Stack Engineering Workflow

A state machine with evidence gates that carries a change from user intent to verified delivery. You, the agent, do the implementation; the Skills it names are instructions for how to handle a given task or phase.

**This workflow is binding, not advisory.** Every phase has an artifact and a gate. You may not act outside the Turn Protocol below, and you may not enter a phase before emitting the prior phase's gate-pass. Skipping a phase, self-waiving a gate, or claiming "done" without the required proof is a workflow failure — not a shortcut.

## Plugins

This workflow is authored against the plugins pinned in `workflow.json`, which is the source of truth for versions.

<!-- maintainers: scripts/marketplace-cli validate checks that every skill named in this file belongs to a pinned plugin and that every pinned plugin is used. -->

| Plugin | Skills used here |
|--------|------------------|
| `setup-engineering-workflow` | `setup-engineering-workflow` |
| `matt-pocock-skills` | `triage`, `zoom-out`, `diagnose`, `grill-with-docs`, `prototype`, `improve-codebase-architecture`, `to-prd`, `to-issues`, `tdd`, `handoff`, `workflow-handoff` |
| `linear` | `linear` |
| `clickup` | `clickup` |
| `sentry` | `sentry` |
| `agent-web-interface` | `agent-web-interface-guide` |
| `app-exploration` | `map-feature-scope`, `capture-feature-evidence` |
| `frontend-design` | `frontend-design` |
| `shadcn` | `shadcn-ui` |
| `exploratory-testing` | `exploratory-test-writer` |
| `test-analysis` | `plan-test-coverage`, `generate-test-cases`, `review-test-cases` |
| `playwright-automation` | `analyze-test-codebase`, `add-playwright-tests`, `write-test-code`, `review-test-code`, `fix-flaky-tests` |
| `smoke-testing` | `define-smoke-scope` |
| `regression-testing` | `define-regression-scope` |

Installed with `matt-pocock-skills` but **not part of this workflow** — never load them on the workflow's own initiative, only when the user asks for them by name: `caveman` (compresses output; conflicts with the Turn Protocol), `git-guardrails-claude-code` (installs hooks that block `git push`; conflicts with Source Control Discipline), `setup-pre-commit`, `write-a-skill`.

## Skill Routing

| Activity | Skill |
|----------|-------|
| Seed per-repo tracker, label, domain-doc, and delivery-mode config | `setup-engineering-workflow` |
| Classify an incoming bug, feature, or issue | `triage` |
| Read or write issue-tracker state | `linear` or `clickup`, whichever `docs/agents/issue-tracker.md` names (GitHub, GitLab, local markdown: no Skill — follow that file's `gh`/`glab`/file conventions) |
| Map an unfamiliar module before touching it | `zoom-out` |
| Reproduce and diagnose a bug or regression | `diagnose` |
| Pull production error context: issues, events, stack traces, release impact | `sentry` |
| Stress-test intent against the domain model and ADRs | `grill-with-docs` |
| Observe live product behavior | `map-feature-scope`, `capture-feature-evidence` |
| Drive a browser for evidence | `agent-web-interface-guide` |
| Design or reshape UI | `frontend-design`, `shadcn-ui` |
| Answer a real design question with throwaway code | `prototype` |
| Resolve concrete architecture friction | `improve-codebase-architecture` |
| Write a PRD; split work into vertical issues | `to-prd`, `to-issues` |
| Plan and specify test coverage | `exploratory-test-writer`, `plan-test-coverage`, `generate-test-cases`, `review-test-cases` |
| Understand, write, review, or stabilize Playwright tests | `analyze-test-codebase`, `add-playwright-tests`, `write-test-code`, `review-test-code`, `fix-flaky-tests` |
| Scope release checks | `define-smoke-scope`, `define-regression-scope` |
| Implement a behavior change test-first | `tdd` |
| Relay resumable workflow state; summarize a conversation | `workflow-handoff`; `handoff` |

Inside this workflow, `add-playwright-tests` is a Build-phase sub-step for the Playwright execution layer, not an entry point: this workflow's phases and gates stay in force while it is loaded.

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
- **Persist it; printing it is not enough.** The chat does not survive compaction. Every turn, write the current block into the **run tracker**'s `## Status` section (overwrite in place) — current truth and next intent only, revised in place, never appended.
- **Gate lines are the run's journal, not its state**, so they follow the run tracker's own shedding rules rather than the Status section's overwrite-in-place rule. Append every gate line to a `## Gates` ledger in the run tracker as you emit it. On most single-unit runs this is the whole of it: the run tracker's Dossier never grows past the run tracker itself, and the `## Gates` ledger simply lives there unless the tracker crosses the size threshold. If the run tracker's Dossier sheds a unit — a phase or slice closing while another stays open, or the run tracker crossing the runtime's size threshold — that unit's gate lines move with the rest of its cold detail into its **unit record** (`units/<slug>.md`, beside the run tracker in the same Dossier directory), and the run tracker keeps only a pointer row plus the still-open unit's live gate lines in its own `## Gates` ledger. On a runtime with no Dossier/unit-record mechanism, every gate line simply stays in the run tracker's `## Gates` ledger, unshed, as before — never drop a gate line to keep the file small.
- The run tracker is the runtime's tracker file, whose last line the runtime reads for terminal markers; it is distinct from the **issue tracker** (Linear, ClickUp, GitHub). When the runtime provides no run tracker, keep a session note file with the same two sections and treat it as the run tracker everywhere below.
- Nothing in the harness checks this for you. Fill the block by reading the run tracker's `## Status` and reconciling it against `git status` / `git log` — that read-only inspection is part of emitting the block, not an action gated by it. Then write the corrected block back before any other action. A stale `## Status` is exactly the workflow failure this rule exists to make visible.

## Phase Transition Rule — the hard forcing function

You may NOT begin phase N+1 until you have, in the conversation, emitted:

```
GATE <phase N>: PASS — artifact: <where it lives durably> — evidence: <what proves the gate>
```

- One gate line per phase, before the next phase's first action, emitted in the chat AND appended to the run tracker's `## Gates` ledger — or, once that phase's unit has been shed to its unit record (`units/<slug>.md`), to that record's gate evidence instead. No line -> no transition.
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
- `sentry` — the bug or regression was reported from production, a Sentry issue or stack trace is referenced, or you need to know whether a change fixed or introduced production errors. Load before any `mcp__plugin_sentry_sentry__` call.
- `linear` — tracker state in Linear must be read or written.
- `clickup` — tracker state in ClickUp must be read or written.
- `triage` — an incoming bug/feature/issue must be classified or prepared.
- `workflow-handoff` — an in-flight task must be relayed to the next agent: a slice/phase/gate boundary is cleanly done, or you are mid-task and out of usable context (token window exhausted, context rot). It captures resumable workflow state (Turn Protocol block, cleared gates, branch + last pushed commit, durable-artifact pointers, exact next action) so the next agent re-enters at the right phase. Use `handoff` instead for a generic conversation summary with no live workflow state to preserve. Like the route below, this is not inline load-and-continue — it is the Stop -> handoff into Phase 10, and current work cannot continue in this session after it fires.

## First-Run Setup

`setup-engineering-workflow` seeds per-repo config — issue tracker, triage labels, domain-doc layout, delivery mode — that the tracker/triage/domain-aware Skills and Phase 9 read: `to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, `improve-codebase-architecture`, `zoom-out`. It is **mandatory once per repo** when the repo has no `## Agent skills` block (in `CLAUDE.md`/`AGENTS.md`) or `docs/agents/`. It does not gate Skills that ignore it — `frontend-design`, `shadcn-ui`, `linear`/`clickup`, `agent-web-interface-guide`, and the app/test/Playwright Skills load regardless, so a missing block never means zero Skills.

It is interactive by default (asks the user to choose the tracker, confirm labels, domain layout, delivery mode, and which doc file to create) and has an unattended mode that writes detected defaults marked as unconfirmed. Treat it as a precondition only for work that actually reads that config; a missing block never blocks the config-free Skills and never applies to a read-only request.

When the block is missing AND the next required action needs tracker/triage/domain/delivery config:

- **User available:** run it now (commit it as its own setup change, separate from the change's diff), then proceed.
- **No user (AFK):** run it in unattended mode; it writes detected defaults under its "unconfirmed" header (the detection rules live in the Skill, not here). Commit that as its own setup change, record it in the run tracker, and proceed. If the Skill reports that it cannot detect the tracker, proceed with everything that does not need the config and Stop -> handoff (Phase 10) only for the specific config-dependent action, naming it. Never stall over config-free work; never overwrite an existing block unattended. A block that predates delivery modes (no `### Delivery mode` line) counts as missing for Phase 9 only: unattended mode may add that one section.

## Task Tracker Discipline

At session start: read the run tracker, issue, handoff, and prior notes, reconcile done/pending/blocked/unknown work, and record the current phase before changing files.

- `docs/agents/issue-tracker.md` names the source of truth. If it is Linear, load `linear` first; if ClickUp, load `clickup` first — the matching Skill owns the issue-pickup procedure. If the tracker's MCP server is not authorized on this machine (its OAuth consent was never completed), that is a Stop -> handoff naming the server; consent cannot be granted from inside the run. Drive status only through the gates (In Review when code-complete; Done only per Mandatory Gates), commenting at each transition with justifying evidence.
- The session note is the run tracker's `## Status` section (Turn Protocol). It carries current phase, goal, loaded Skills, completed artifacts, pending artifacts, blocker (or `None`), next action, and last verification result (or `Not run`). A conversation-only note does not survive compaction: re-persist it before any compaction or handoff.

## Source Control Discipline

Keep the remote working branch current so a lost worktree, crash, or context reset never loses committed work.

- **Never work on `main`.** Establish the working branch (or `git worktree`) at the start of the run, before the first artifact is committed; Build still re-confirms the green baseline on it before the first code change.
- **Commit AND push** whenever a unit of work lands: each phase artifact that is a repo file, and each completed vertical slice. A local-only commit is not enough — the push is what makes the work recoverable.
- Pushing your own working branch is a routine safety checkpoint and needs no user approval. PR / publish / merge to a shared branch is outward delivery and stays authority-gated; the delivery mode grants that authority at Phase 9 — a clean merge to `main` in `merge` mode, opening a PR in `pr` mode (see Delivery).
- Commit messages name the artifact or slice and its proof state. Never commit secrets; remove temporary instrumentation before the artifact commit.
- If Orientation found no push rights (read-only clone, fork without write), local-commit-only is the sanctioned mode: keep committing locally and note it once, not per-artifact. If the remote was expected writable but a push fails or is unreachable, record it as a blocker in the session note and route to Handoff (Phase 10) if the work cannot otherwise be preserved.

## State Graph

Default path:

**1 Intake -> 2 Orientation -> 3 Problem Definition -> 4 Design -> 5 Implementation Plan -> 6 Build -> 7 Verification -> 8 Review -> 9 Delivery -> 10 Handoff / Postmortem**

Valid shortcuts (invalid if a skipped phase owns evidence a later gate needs — and each skip still needs its gate line citing the existing artifact):

- Read-only request: Stop -> resolve after the first phase that answers it — record the answer in the run tracker, emit `GATE 7` and `GATE 8: PASS — N/A, read-only path, no repo file changed`, and close through the Completion Gate (its branch and instrumentation criteria are vacuous on this path).
- Tiny local edit: 1 -> 2 -> 6 -> 7 -> 8 -> 9.
- Confirmed bug: 1 -> 2 -> 3 with `diagnose`, then rejoin the default path.
- User-visible UI: MUST pass Design with `frontend-design` and Verification with browser evidence.
- Broad product testing: MUST pass product evidence -> coverage plan -> TC specs -> spec review before automation.
- Production-sensitive work: no shortcuts.

## Phases

Each phase produces its artifact and emits its gate-pass line before the next begins. Every `Stop` is tagged with its channel so the response is unambiguous:

| Channel | Attended (a user can answer) | Unattended (AFK loop, no user) | Run tracker terminal marker |
|---------|------------------------------|--------------------------------|-------------------------|
| **Stop -> ask user** | Halt and put one specific question to the user; no guessing. | Route to Handoff (Phase 10) with the exact question and the options you weighed as the blocker, then end the run. | `<!-- WORKFLOW_BLOCKED: <the question> -->` |
| **Stop -> resolve** | Halt and fix it yourself, usually by looping or returning to the phase the Reset Rules name. | Same. Not terminal. | none |
| **Stop -> handoff** | Halt and route to Handoff (Phase 10) with full state; work cannot continue here. | Same; the Phase 10 note is the last thing written before the marker. | `<!-- WORKFLOW_BLOCKED: <blocker> -->` |

The runtime ends a run only when the **last non-empty line** of the run tracker is a terminal marker. `<!-- WORKFLOW_COMPLETE -->` is written by the Completion Gate alone — never by a phase, never before the Completion Gate's criteria hold. A run that stops without a marker keeps looping until `maxIterations`, so every unattended Stop that ends the session must leave a `WORKFLOW_BLOCKED` marker with its reason. Never quote a marker earlier in the run tracker where it could become the last line by accident. "Unattended" means the runtime told you no user is present, or a question has gone unanswered for a full turn.

---

**1. Intake** — Choose the workflow path.
- MUST: state the outcome; classify the task as one path type (bug, feature, UI, test, production-sensitive); identify constraints.
- Skills: `triage` to classify an incoming issue; `linear`/`clickup` (per `docs/agents/issue-tracker.md`) when issue-tracker state is part of the task.
- Artifact: goal statement, task type, constraints, current phase.
- Gate: outcome is specific enough to verify.
- Stop -> ask user if goals conflict, the target surface is unknown, or intent cannot be inferred safely.
- Do NOT turn ambiguity into a private plan.

**2. Orientation** — Know the system before changing it.
- MUST: inspect structure, conventions, commands, relevant modules, tests, domain docs, ADRs. Confirm the test suite runs and record its pass/fail state (Build re-confirms against this baseline). Confirm whether the remote is writable and record it. Probe each pinned MCP server the task will need (tracker, Sentry, browser) once and record whether it is authorized. Read `docs/agents/delivery.md` if present and record the delivery mode; if absent, record `pr` as the mode in force until `setup-engineering-workflow` has written one (see First-Run Setup). Delegate heavy reading/exploration to subagents.
- Skills: `zoom-out` before touching any unmapped module.
- Artifact: orientation note (surfaces, commands, conventions, risks, open questions, baseline suite pass/fail, push capability, MCP availability, delivery mode).
- Gate: likely files, test surfaces, commands, and risks can be named, AND the baseline suite state is recorded.
- Stop -> handoff if required context is inaccessible, an MCP server the task needs is unauthorized (name the server; consent must be granted outside the run), or no safe first surface exists.
- Do NOT implement from filename guesses.

**3. Problem Definition** — Convert intent into observable behavior.
- MUST: define current and desired behavior; identify affected users/roles/systems/callers; define acceptance criteria.
- Skills: `grill-with-docs` for alignment; `diagnose` for bugs, with `sentry` loaded first when the bug comes from production or a Sentry issue / stack trace exists; `map-feature-scope` + `capture-feature-evidence` when product behavior must be observed.
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
- If the baseline is red or the suite cannot run where the change will happen, Stop -> resolve (or record why) before any change.
- MUST: set the slice's proof condition, build only the active slice, then commit and push the completed slice.
- Skills: `tdd` for behavior changes (failing test first; code written before its test is deleted); `analyze-test-codebase` to understand an existing Playwright suite; `add-playwright-tests`/`write-test-code` for Playwright tests; `frontend-design`/`shadcn-ui`/`agent-web-interface-guide` for UI; `diagnose` for unexpected failures.
- Artifact: isolated branch/worktree with a recorded green baseline; each completed slice committed and pushed; code changes; test changes; notes for intentional deviations.
- Gate: the slice builds on a verified-green baseline or the failure is understood and recorded.
- Loop if a failure has a clear local fix.
- Stop -> ask user if scope expands beyond the accepted design or new production-sensitive risk appears; Stop -> handoff if required verification is impossible here.
- Do NOT clean up unrelated code, leave debug output, or widen interfaces without a recorded reason.

**7. Verification** — Prove the change works. **MANDATORY GATE — never skipped, deferred, or self-waived.**
- MUST: run narrow verification first, expand as blast radius requires, rerun bug reproduction loops, gather browser evidence for UI claims, run Playwright execution in the main agent.
- Skills: `agent-web-interface-guide` for browser evidence; `fix-flaky-tests` for a flaky or timing-out test; `define-smoke-scope`/`define-regression-scope` for release confidence; `sentry` to check whether a production error still recurs after the fix, or to record that this cannot be confirmed before release.
- Artifact: commands run, browser/product evidence, pass/fail result, remaining unverified risk.
- Gate: required verification ran and supports the acceptance criteria; user-visible work has browser/product evidence. A passing unit suite alone does NOT clear it for user-visible work. Browser evidence may be recorded as N/A only when the diff touches no web-rendered surface (a CLI, terminal renderer, API, or library change), and the N/A note must name the surface that changed and the product evidence used instead (a rendered-output assertion, an API response). Any other missing browser evidence is a Stop -> handoff, not a skip.
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
- Skills: `linear`/`clickup` (per `docs/agents/issue-tracker.md`) for issue-tracker updates — Done only per Mandatory Gates; otherwise leave it In Review with a comment naming the outstanding gate.
- Delivery mode comes from `docs/agents/delivery.md` (seeded by `setup-engineering-workflow`; Orientation recorded it). When the file is missing the mode is `pr`. After a final full-suite green run (and, for user-visible work, a whole-feature browser pass — golden path plus the edge cases named in the design), resolve the working branch per the mode:
  - **`merge`.** A clean merge to `main` after both Mandatory Gates pass is workflow-owned — no separate user request needed. Auto-merge only on a clean fast-forward or clean merge to `main`. Remove the worktree only after the Completion Gate has written its marker, and never while the run tracker lives inside it. Stop -> ask user if the merge has conflicts, the base is not `main`, or the tree is dirty.
  - **`pr`.** Push the branch, open a pull request with the delivery summary as its body, and leave the tracker issue In Review with the PR link. Never self-merge, even with both gates passed.
  - **`local`.** Do not merge or open a PR; the committed (and, where the remote is writable, pushed) branch is the deliverable. Note the mode once.
  - **Abandon.** Work rejected -> remove the worktree and delete the branch **only after typed user confirmation**, in every mode. Never auto-discard.
- Pushing your own working branch needs no approval. Publishing or merging to `main` or any shared branch is outward delivery — do it only when the delivery mode owns it or the user requests it.
- Artifact: delivery summary plus tracker update/commit/PR reference when applicable.
- Gate: the user can understand what changed and how it was proven.
- Stop -> ask user if external delivery lacks authority or production risk is unresolved.
- Do NOT imply production readiness from local verification alone.

**10. Handoff / Postmortem** — Preserve state when work cannot finish or should teach the next run.
- MUST record: phase, completed work, blocker, next command, next decision, evidence links. When the run ends here, the run tracker's last line is `<!-- WORKFLOW_BLOCKED: <blocker> -->`; a handoff never writes `WORKFLOW_COMPLETE`.
- Skills: `workflow-handoff` to relay resumable workflow state (phase, cleared gates, branch + last pushed commit, next action) so the next agent resumes mid-flight; `handoff` for a generic conversation summary; `to-issues` plus `linear`/`clickup` (per `docs/agents/issue-tracker.md`) for durable follow-up.
- Artifact: handoff or postmortem note.
- Gate: another agent can resume without rediscovery.
- Stop -> ask user if sensitive information cannot be safely redacted.
- Do NOT say "continue from here" without defining "here".

## Reset Rules

Return to an earlier phase when evidence invalidates the current path: new scope -> Problem Definition; new public contract -> Design; product behavior differs from assumption -> Problem Definition; test spec changes materially -> Implementation Plan; test code changes materially after review -> Review; verification reveals a different bug -> Problem Definition with `diagnose`; production risk appears -> Design and Verification become mandatory.

On a shortcut path, a Reset that names a skipped phase is a promotion to the full path: enter that phase now (a join, not a return) and continue the default path from there — e.g. scope expansion during a tiny local edit promotes to Problem Definition. Re-emit the Turn Protocol block on every reset.

## Mandatory Gates

Phase 7 (Verification) and Phase 8 (Review) are hard gates whenever a repo file changed — never skipped, deferred, or self-waived. On a read-only path that changed nothing they pass as N/A with the gate line saying so. Only the user waives, and only a specific named gate. Their PASS lines require the proof named in those phases (Phase 7: verification evidence incl. browser proof for user-visible work; Phase 8: resolved findings incl. the security checklist).

No work reaches Delivery, and no issue-tracker item moves to Done, until both gates pass or the user waives. A "done" claim without both cleared or waived is a workflow failure.
Unattended with no user to waive a blocked gate: route to Handoff (Phase 10) with full state and end with the `WORKFLOW_BLOCKED` marker — never self-waive, never stall.

## Completion Gate

Beyond the Mandatory Gates, complete only when: acceptance criteria are satisfied, temporary instrumentation is removed, Delivery has resolved the branch per the delivery mode (or the path changed no repo files), and the run tracker + final summary state what changed, how it was verified, and remaining risk. Only then write `<!-- WORKFLOW_COMPLETE -->` as the run tracker's last line.

## Handoff Rules

Stop and hand off when required evidence cannot be gathered, a required Skill/Plugin is unavailable, an MCP server the task needs is unauthorized or unreachable (name it), environment or credentials are missing, a user decision is required and no user is present, or work cannot finish this session. The note carries what Phase 10 specifies, and the run ends with `<!-- WORKFLOW_BLOCKED: <reason> -->`.

## Guardrails

Phase "Do NOT" lines, the Turn Protocol, the Phase Transition Rule, and the State Graph order are binding. Beyond those, do not: overwrite user changes; convert uncertainty into confidence; invent Plugin behavior; or put low-level implementation procedure in this Workflow (load the owning Skill).
