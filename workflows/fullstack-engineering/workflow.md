# Full-Stack Engineering Workflow

Carry a change from user intent to verified delivery. This Workflow is a state machine with evidence gates. It orchestrates specialist Skills; it does not teach their internal methods.

## Operating Principle

Build only from evidence. If evidence is missing, gather it. If it cannot be gathered, stop and name the missing evidence.

Do not jump phases. A phase is complete only when its artifact exists and its gate passes.

This is a dependency graph, not a script. Skip a phase only when its artifact already exists and is current.

## Plugins

This Workflow requires the following Plugin surfaces. Treat this table as the agent-facing contract. If any required Plugin or Skill is unavailable at runtime, stop and report the missing surface instead of continuing from memory.

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

Loading the owning Skill is mandatory, not optional. The moment a trigger below holds, load that Skill **before** the next action — on your own judgment, without waiting for the user to ask. Auto-loading is the expected behavior: every one of these Skills is model-invocable, and a phase action that needed a Skill but ran without it is a workflow failure, not a shortcut.

Hard rule: a phase action that names a Skill may not start until that Skill has been loaded for the current turn or delegated subtask. If the Skill is unavailable, stop and report the missing surface. Do not substitute memory, old summaries, or generic reasoning for a missing Skill.

Announce the load in one line before you act: `Loading <skill> — trigger: <what you observed>.` Record loaded Skills in the phase artifact when the phase delegates work to a Skill.

The **Auto-load when** column is the trigger. Read it as: when this condition holds, you must load the Skill yourself, now, before doing the activity.

| Activity | Auto-load when | Skill |
|----------|----------------|-------|
| Repo foundation | First engineering action in a repo whose `CLAUDE.md`/`AGENTS.md` has no `## Agent skills` block or no `docs/agents/` — load at Orientation, before any other engineering Skill | `setup-matt-pocock-skills` |
| Linear tracker work | Tracker state in Linear must be read or written | `linear` |
| Issue triage | An incoming bug, feature, or issue must be classified or prepared | `triage` |
| Domain alignment | A plan or design must be checked against the repo's domain model or terminology | `grill-with-docs` |
| Non-repo alignment | A plan needs stress-testing and there is no repo/domain doc to anchor it | `grill-me` |
| Unknown code area | About to read or change code in a module you have not yet mapped this session | `zoom-out` |
| Bug or performance diagnosis | Something is broken, failing, throwing, or slower than expected | `diagnose` |
| Design probe | A design question needs a throwaway prototype to answer | `prototype` |
| PRD | Requirements are substantial or production-sensitive | `to-prd` |
| Vertical issue breakdown | Work spans multiple independently-shippable slices | `to-issues` |
| Architecture deepening | Concrete architecture friction is blocking the change | `improve-codebase-architecture` |
| Behavior implementation | About to write or change production behavior | `tdd` |
| UI design | The output is user-visible UI | `frontend-design` |
| shadcn component work | Building with shadcn primitives | `shadcn-ui` |
| Browser interaction | A live page must be driven or observed | `agent-web-interface-guide` |
| Feature decomposition | A broad feature spans many surfaces and must be split | `map-feature-scope` |
| Product evidence | Live product behavior must be observed and captured | `capture-feature-evidence` |
| Exploratory test charter | A risk-based exploratory charter is needed | `exploratory-test-writer` |
| Coverage plan | Test coverage must be planned from evidence | `plan-test-coverage` |
| TC-ID specs | TC-ID test specs must be written | `generate-test-cases` |
| TC-ID spec review | Specs must be reviewed before any test code | `review-test-cases` |
| Playwright analysis | An existing Playwright suite must be understood | `analyze-test-codebase` |
| Playwright authoring | Playwright tests must be written | `add-playwright-tests` or `write-test-code` |
| Playwright code review | Playwright test code must be reviewed | `review-test-code` |
| Playwright flake repair | A Playwright test is flaky, timing out, or inconsistent | `fix-flaky-tests` |
| Smoke scope | Smoke-test scope must be defined | `define-smoke-scope` |
| Regression scope | Regression-test scope must be defined | `define-regression-scope` |
| Handoff | Work is blocked, deferred, or being handed to another agent | `handoff` |

## Skill Loading Gate

Before any phase action:

- Check the routing triggers against what you observe right now.
- Load every Skill whose trigger holds — yourself, without waiting for the user to name it.
- Announce the load: `Loading <skill> — trigger: <what you observed>.`
- Confirm the loaded Skill matches the activity.
- Record the loaded Skill name in the phase artifact.

Gate:

- Continue only when every required Skill for the next action is loaded.

Stop if:

- A required Skill is unavailable.
- A required Plugin surface is unavailable.
- The agent cannot determine which Skill owns the activity.

Anti-pattern:

- Do not perform specialist work from memory.
- Do not skip Skill loading because the workflow already lists the Skill.
- Do not treat a previous session's loaded Skill as loaded for the current action.
- Do not wait to be told to load a Skill. If a trigger holds, loading it is your call to make now.

## Skip-rationalizations that mean STOP

If you catch yourself thinking any of these, a Skill load is being skipped. Stop and load it.

| Thought | Why it's wrong |
|---|---|
| "I already understand this repo's setup." | If the `## Agent skills` block and `docs/agents/` are not present, the engineering Skills have no tracker, triage, or domain context. Load `setup-matt-pocock-skills` first. |
| "I'll just read the files directly to get oriented." | Ad-hoc reading of an unfamiliar module is exactly what `zoom-out` replaces — load it to get the map and caller graph first. |
| "I know the design; I can skip alignment." | Unwritten alignment is a guess. Load `grill-with-docs` (or `grill-me` when there is no repo to anchor on). |
| "I'll write the code, then add a test." | Not TDD. Load `tdd` and write the failing test first; code written before its test gets deleted. |
| "This Skill is meant for the user to invoke, not me." | Every Skill in the routing table is model-invocable. If its trigger holds, you load it — do not wait to be asked. |
| "Tests pass, so it's done." | User-visible work needs browser evidence. Load `agent-web-interface-guide` and capture proof. |
| "I'll note the Skill in the summary instead of loading it." | Naming a Skill is not loading it. The activity may not start until the Skill is loaded. |

## Task Tracker Discipline

At every session start:

- Read tracker, issue, handoff, or prior execution notes.
- Reconcile done, pending, blocked, and unknown work.
- Record current phase before changing files.

If Linear is source of truth, load `linear` before reading or writing tracker state.

Fallback rule:

- Prefer a visible tracker, active task tool, or handoff artifact.
- If none exists, maintain a session execution note in the conversation.
- Do not write repo files for tracking unless the user asks, the repo convention authorizes it, or an existing workflow artifact already owns that path.

Minimum execution note fields:

- Current phase.
- Goal.
- Loaded Skills.
- Completed artifacts.
- Pending artifacts.
- Blocker, or `None`.
- Next action.
- Last verification result, or `Not run`.

## State Graph

Default path:

**Intake -> Orientation -> Problem Definition -> Design -> Implementation Plan -> Build -> Verification -> Review -> Delivery -> Handoff / Postmortem**

Valid shortcuts:

- Read-only request: stop after the first phase that answers it.
- Tiny local edit: Intake -> Orientation -> Build -> Verification -> Delivery.
- Confirmed bug: Intake -> Orientation -> Problem Definition with `diagnose`.
- User-visible UI: must pass Design with `frontend-design` and Verification with browser evidence.
- Broad product testing: must pass product evidence -> coverage plan -> TC specs -> spec review before automation.
- Production-sensitive work: no shortcuts.

Shortcut rule: if a skipped phase owns evidence required by a later gate, the shortcut is invalid.

## Phase 1: Intake

Goal: choose the workflow path.

Enter with:

- User request, issue, or handoff.

Evidence required:

- Target repo or product surface is known.

Action:

- State outcome.
- Classify task: bug, feature, refactor, UI, test, research, delivery, incident, production-sensitive.
- Identify constraints.
- Use `linear` or `triage` when tracker state is part of the task.

Artifact:

- Goal statement.
- Task type.
- Constraints.
- Current phase.

Gate:

- Continue only when the outcome is specific enough to verify.

Stop if:

- Goals conflict.
- Target surface is unknown.
- Intent cannot be inferred safely.

Anti-pattern:

- Do not turn ambiguity into a private plan.

## Phase 2: Orientation

Goal: know the system before changing it.

Enter with:

- Intake artifact.

Evidence required:

- Project instructions and relevant tracker context have been read when present.

Action:

- Inspect structure, conventions, commands, relevant modules, tests, domain docs, and ADRs.
- Load `setup-matt-pocock-skills` as the first action when the repo has no `## Agent skills` block in `CLAUDE.md`/`AGENTS.md` or no `docs/agents/`. The other engineering Skills depend on the tracker, triage, and domain context it writes, so this comes before them.
- Load `zoom-out` before reading or changing code in any module you have not yet mapped this session. Do not orient by ad-hoc file reads when the area is unfamiliar.

Artifact:

- Orientation note: relevant surfaces, commands, conventions, risks, open questions.

Gate:

- Continue only when likely files, test surfaces, commands, and risks can be named.

Stop if:

- Required context is inaccessible.
- No safe first surface can be identified.

Anti-pattern:

- Do not implement from filename guesses.

## Phase 3: Problem Definition

Goal: convert intent into observable behavior.

Enter with:

- Orientation artifact.

Evidence required:

- Current behavior, desired behavior, or investigation target is known.

Action:

- Define current behavior.
- Define desired behavior.
- Identify affected users, roles, systems, or callers.
- Define acceptance criteria.
- Use `grill-with-docs` or `grill-me` for alignment.
- Use `diagnose` for bugs.
- Use `map-feature-scope` and `capture-feature-evidence` when product behavior must be observed.

Artifact:

- Acceptance criteria.
- Reproduction loop or feature slice.
- Evidence gaps.

Gate:

- Continue only when success and failure are externally observable.

Stop if:

- Bug cannot be reproduced or characterized.
- Feature lacks a smallest useful vertical slice.
- Required product evidence is unavailable.

Anti-pattern:

- Do not fix before reproducing.
- Do not plan from imagined product behavior.

## Phase 4: Design

Goal: choose the smallest coherent approach.

Enter with:

- Problem Definition artifact.

Evidence required:

- Acceptance criteria.
- Relevant project patterns.

Action:

- Select the approach.
- Identify changed surfaces and risks.
- Use `frontend-design` for UI.
- Use `shadcn-ui` for shadcn work.
- Use `prototype` only to answer a real design question.
- Use `improve-codebase-architecture` only for concrete architecture friction.

Artifact:

- Design note.
- Expected changed surfaces.
- Risks and rollback or mitigation notes.

Gate:

- Continue only when the design fits project conventions or the exception is explicit.

Stop if:

- Design changes user intent.
- Public contracts widen without a reason.
- Production risk lacks mitigation.

Anti-pattern:

- Do not add architecture to make the task feel important.
- Do not promote prototype code without review.

## Phase 5: Implementation Plan

Goal: split work into safe vertical steps.

Enter with:

- Design artifact.

Evidence required:

- First behavior and verification strategy are known.

Action:

- Create vertical steps.
- Identify proof for each step.
- Use `to-prd` for substantial or production-sensitive requirements.
- Use `to-issues` for multi-slice work.
- Use `exploratory-test-writer`, `plan-test-coverage`, `generate-test-cases`, and `review-test-cases` when testing artifacts are required.

Artifact:

- Stepwise plan.
- Verification commands or evidence sources.
- PRD, issues, coverage plan, and reviewed test specs when required.

Gate:

- Continue only when the first step is clear, small, and verifiable.

Stop if:

- Plan is horizontal.
- Required test specs are unreviewed.
- Coverage planning depends on missing product evidence.

Anti-pattern:

- Do not split by layers.
- Do not write executable tests from unreviewed specs.

## Phase 6: Build

Goal: implement one complete vertical slice.

Enter with:

- Implementation Plan artifact.

Evidence required:

- Baseline command or baseline skip reason.
- Active slice proof condition.

Action:

- Build only the active slice.
- Use `tdd` for behavior changes.
- Use `diagnose` for unexpected failures.
- Use `frontend-design`, `shadcn-ui`, and `agent-web-interface-guide` for UI surfaces.
- Use Playwright skills for Playwright automation.

Artifact:

- Code changes.
- Test changes.
- Notes for intentional deviations.

Gate:

- Continue only when the slice builds or failure is understood and recorded.

Loop if:

- Failure has a clear local fix path.

Stop if:

- Scope expands beyond accepted design.
- Required verification is impossible.
- New production-sensitive risk appears.

Anti-pattern:

- Do not clean up unrelated code.
- Do not leave temporary debug output.
- Do not widen interfaces without a recorded reason.

## Phase 7: Verification

Goal: prove the change works.

Enter with:

- Build artifact.

Evidence required:

- Acceptance criteria.
- Verification plan.

Action:

- Run narrow verification first.
- Expand verification when blast radius requires it.
- Rerun bug reproduction loops.
- Gather browser evidence for UI claims.
- Run Playwright execution in the main agent.
- Use `define-smoke-scope` and `define-regression-scope` for release confidence.

Artifact:

- Commands run.
- Browser or product evidence.
- Pass/fail result.
- Remaining unverified risk.

Gate:

- Continue only when verification supports the acceptance criteria.

Loop if:

- Failure is understood and the next fix is evidence-based.

Stop if:

- Tests cannot run.
- Environment is missing.
- Results are ambiguous.
- Product evidence contradicts implementation.

Anti-pattern:

- Do not treat a flaky pass as confidence.
- Do not hide failed commands.

## Phase 8: Review

Goal: inspect the change as if reviewing a PR.

Enter with:

- Verification artifact.

Evidence required:

- Diff, tests, verification output, and known risks.

Action:

- Check acceptance criteria, regressions, brittle tests, coupling, cleanup, docs, migrations, config, and generated artifacts.
- Use `review-test-cases` for spec review.
- Use `review-test-code` for Playwright code review.
- Use `improve-codebase-architecture` when review finds architecture friction.

Artifact:

- Review notes.
- Resolved findings.
- Residual risks.

Gate:

- Continue only when blocking findings are resolved or explicitly documented.

Loop if:

- Findings are local and fixable.

Stop if:

- Review exposes a scope change.
- Review exposes missing evidence from an earlier phase.

Anti-pattern:

- Do not bury blockers as follow-up suggestions.

## Phase 9: Delivery

Goal: package the work for user handoff, PR, or merge.

Enter with:

- Review artifact.

Evidence required:

- Acceptance criteria satisfied or gaps explicit.
- Verification and review artifacts exist.

Action:

- Summarize changes, verification, files or artifacts, risks, and follow-up.
- Use `linear` for tracker updates.
- Commit, push, open PR, publish, or merge only when requested or explicitly workflow-owned.

Artifact:

- Delivery summary.
- Tracker update, commit, or PR reference when applicable.

Gate:

- Complete only when the user can understand what changed and how it was proven.

Stop if:

- External delivery lacks authority.
- Production risk is unresolved.

Anti-pattern:

- Do not imply production readiness from local verification alone.

## Phase 10: Handoff / Postmortem

Goal: preserve state when work cannot finish or should teach the next run.

Enter with:

- Blocked, deferred, interrupted, or materially risky work.

Evidence required:

- Current phase and last completed artifact.

Action:

- Use `handoff`.
- Record phase, completed work, blocker, next command, next decision, and evidence links.
- Use `to-issues` or `linear` for durable follow-up.

Artifact:

- Handoff or postmortem note.

Gate:

- Complete only when another agent can resume without rediscovery.

Stop if:

- Sensitive information cannot be safely redacted.

Anti-pattern:

- Do not say "continue from here" without defining "here".

## Reset Rules

Return to an earlier phase when evidence invalidates the current path:

- New scope -> Problem Definition.
- New public contract -> Design.
- Product behavior differs from assumption -> Problem Definition.
- Test spec changes materially -> Implementation Plan.
- Test code changes materially after review -> Review.
- Verification reveals a different bug -> Problem Definition with `diagnose`.
- Production risk appears -> Design and Verification become mandatory.

## Completion Gate

The Workflow is complete only when:

- Acceptance criteria are satisfied.
- Relevant verification has run.
- Review has no unresolved blockers.
- Temporary instrumentation is removed.
- Product evidence exists for user-visible claims, or skip reason is recorded.
- Test specs and test code passed required review gates when used.
- Final summary states what changed, how it was verified, and what risk remains.

## Handoff Rules

Stop and hand off when:

- Required evidence cannot be gathered.
- Required Skill or Plugin named in this document is unavailable.
- Environment or credentials are missing.
- User decision is required.
- Work cannot finish in the current session.

The handoff must name current phase, completed artifacts, blocker, last verification result, and next action.

## Guardrails

- Do not guess when evidence can be gathered.
- Do not implement before orientation.
- Do not plan before problem definition.
- Do not review before verification.
- Do not deliver before review.
- Do not call work done without verification.
- Do not hide failed commands.
- Do not overwrite user changes.
- Do not convert uncertainty into confidence.
- Do not invent Plugin behavior.
- Do not put low-level implementation procedure in this Workflow. Load the owning Skill.
