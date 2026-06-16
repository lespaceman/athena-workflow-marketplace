# Product Discovery Workflow

Carry a product idea from raw intent to two delivery-ready artifacts: a grounded PRD and a throwaway prototype, published as a Linear project that the `fullstack-engineering` workflow can pick up. This Workflow is a state machine with evidence gates. It orchestrates specialist Skills; it does not teach their internal methods.

## Operating Principle

Discover before you specify. Every claim in the PRD must trace to evidence, an answered design question, or an explicit assumption.

Do not jump phases. A phase is complete only when its artifact exists and its gate passes.

The prototype is throwaway code that answers a question. Never promote it to production from this Workflow — hand it off.

This is a dependency graph, not a script. Skip a phase only when its artifact already exists and is current.

## Plugins

This Workflow requires the following Plugin surfaces. Treat this table as the agent-facing contract. If any required Plugin or Skill is unavailable at runtime, stop and report the missing surface instead of continuing from memory.

| Plugin | Skills |
|--------|--------|
| `setup-engineering-workflow` | `setup-engineering-workflow` |
| `matt-pocock-skills` | `triage`, `grill-me`, `grill-with-docs`, `zoom-out`, `prototype`, `to-prd`, `to-issues`, `handoff` |
| `app-exploration` | `map-feature-scope`, `capture-feature-evidence` |
| `agent-web-interface` | `agent-web-interface-guide` |
| `frontend-design` | `frontend-design` |
| `shadcn` | `shadcn-ui` |
| `linear` | `linear` |

## Skill Routing

Load the owning Skill before doing the activity.

Hard rule: a phase action that names a Skill may not start until that Skill has been loaded for the current turn or delegated subtask. If the Skill is unavailable, stop and report the missing surface. Do not substitute memory, old summaries, or generic reasoning for a missing Skill.

Record loaded Skills in the phase artifact when the phase delegates work to a Skill.

| Activity | Skill |
|----------|-------|
| Repo foundation (glossary, tracker, label vocabulary) | `setup-engineering-workflow` |
| Logging or moving an idea/issue on the tracker | `triage` |
| Linear project, issue, and document work | `linear` |
| Unknown code area mapping | `zoom-out` |
| Feature decomposition of an existing surface | `map-feature-scope` |
| Observing current product behavior | `capture-feature-evidence` |
| Browser interaction (evidence and viewing the prototype) | `agent-web-interface-guide` |
| Stress-testing the idea against the domain model and ADRs | `grill-with-docs` |
| Stress-testing the idea when no repo domain model applies | `grill-me` |
| Building a throwaway prototype to answer a design question | `prototype` |
| Designing prototype UI | `frontend-design` |
| shadcn component primitives in the prototype | `shadcn-ui` |
| Synthesizing the PRD | `to-prd` |
| Breaking the PRD into vertical issues | `to-issues` |
| Handoff to the next workflow | `handoff` |

If the named Skill is not visible, follow this Workflow's generic phase instructions or stop when specialist behavior is required for safety.

## Skill Loading Gate

Before any phase action:

- Identify each Skill required by the action.
- Load each required Skill.
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
- Do not skip Skill loading because the Workflow already lists the Skill.
- Do not treat a previous session's loaded Skill as loaded for the current action.

## Task Tracker Discipline

At every session start:

- Read tracker, Linear project, handoff, or prior execution notes.
- Reconcile done, pending, blocked, and unknown work.
- Record current phase before changing files.

If Linear is the source of truth, load `linear` before reading or writing tracker state.

Fallback rule:

- Prefer a visible tracker, active task tool, or handoff artifact.
- If none exists, maintain a session execution note in the conversation.
- Do not write repo files for tracking unless the user asks, the repo convention authorizes it, or an existing workflow artifact already owns that path.

Minimum execution note fields:

- Current phase.
- Discovery goal.
- Loaded Skills.
- Completed artifacts (evidence note, decisions, prototype location, PRD, Linear refs).
- Pending artifacts.
- Blocker, or `None`.
- Next action.
- Last verification result, or `Not run`.

## State Graph

Default path:

**Intake -> Evidence -> Alignment -> Prototype -> PRD -> Publish to Linear -> Handoff to Engineering**

Alternate terminal state:

**Handoff / Blocked**

Valid shortcuts:

- Greenfield idea with no existing product surface: Evidence may record a `No existing surface` skip reason and proceed on market/user context.
- Design question is purely about state or business logic, not UI: Prototype uses the `prototype` terminal-app branch and may skip `frontend-design`.
- Idea already validated by a current prototype and evidence: skip to PRD, but only if the prototype and decisions are current.

Shortcut rule: if a skipped phase owns evidence required by a later gate, the shortcut is invalid. The PRD gate requires answered design questions; the Publish gate requires a PRD; the Handoff gate requires both PRD and prototype references.

## Phase 1: Intake

Goal: frame the discovery and choose the path.

Enter with:

- A product idea, request, problem statement, or Linear item.

Evidence required:

- The target product surface is named, or the idea is explicitly greenfield.
- The prototype target repo is identified (default: `eximpe-design`).

Action:

- State the desired outcome in one sentence.
- Classify the discovery: new product, new feature, enhancement, or redesign.
- Identify users, constraints, and the design question the prototype must answer.
- Use `linear` to read or create the owning project/idea, or `triage` to log a raw idea, when tracker state is part of the task.
- Use `setup-engineering-workflow` if the repo glossary, tracker, or label vocabulary is missing.

Artifact:

- Discovery brief: outcome, discovery type, users, constraints, the prototype's design question, prototype target repo, current phase.

Gate:

- Continue only when the outcome is specific enough to prototype against and to write acceptance criteria for.

Stop if:

- Goals conflict.
- The target surface and greenfield status are both unknown.
- Intent cannot be inferred safely.

Anti-pattern:

- Do not turn a vague idea into a private plan.
- Do not start prototyping before naming the design question.

## Phase 2: Evidence

Goal: ground the idea in how the product behaves today.

Enter with:

- Discovery brief.

Evidence required:

- For an existing surface: current behavior is observable.
- For greenfield: market, user, or domain context is available, or a `No existing surface` skip reason is recorded.

Action:

- Use `map-feature-scope` to decompose the affected surface.
- Use `capture-feature-evidence` and `agent-web-interface-guide` to observe live behavior.
- Use `zoom-out` for unfamiliar code areas.
- Capture constraints, edge cases, and existing patterns in the project's domain vocabulary.

Artifact:

- Discovery evidence note: current behavior, constraints, gaps, open questions, source links.

Gate:

- Continue only when current behavior and constraints can be named, or the greenfield skip reason is explicit.

Stop if:

- Required product evidence is inaccessible and the idea depends on it.

Anti-pattern:

- Do not plan from imagined product behavior.
- Do not treat assumptions as observed evidence.

## Phase 3: Alignment

Goal: resolve the design decision tree and sharpen terminology before committing effort.

Enter with:

- Discovery evidence note.

Evidence required:

- The open design questions from Intake and Evidence are listed.

Action:

- Use `grill-with-docs` to stress-test the idea against the domain model and ADRs, updating `CONTEXT.md` / ADRs inline when decisions crystallize.
- Use `grill-me` when no repo domain model applies.
- Resolve dependencies between decisions one at a time; record a recommended answer for each.

Artifact:

- Resolved-decisions record: each design question, its decision or explicit deferral, and the rationale.
- Draft acceptance-shaped statements.

Gate:

- Continue only when every blocking design question is resolved or explicitly deferred with a reason.

Stop if:

- A decision needs a user choice that cannot be obtained.

Anti-pattern:

- Do not silently pick a branch the user must own.
- Do not carry unresolved blocking questions into the prototype.

## Phase 4: Prototype

Goal: build throwaway code that answers the design question.

Enter with:

- Resolved-decisions record.

Evidence required:

- The design question and which branch answers it: state/logic vs UI.

Action:

- Use `prototype` to pick the branch — a runnable terminal app for state/business-logic questions, or several radically different UI variations toggleable from one route.
- For UI work, use `frontend-design` to build the variations in the prototype target repo (default `eximpe-design`), and `shadcn-ui` for component primitives.
- Use `agent-web-interface-guide` to view and interact with the running prototype.
- Keep the prototype isolated and clearly throwaway.

Artifact:

- Runnable prototype in the target repo (location recorded).
- Design-decision capture: what the prototype proved, the chosen direction, rejected alternatives, screenshots or run notes.

Gate:

- Continue only when the prototype answers the design question and the chosen direction is recorded.

Loop if:

- A variation fails to answer the question and the next iteration is clear.

Stop if:

- The prototype cannot run.
- The design question changes scope beyond the discovery brief.

Anti-pattern:

- Do not promote prototype code to production.
- Do not polish a prototype past the point it answers its question.

## Phase 5: PRD

Goal: synthesize the PRD from accumulated context.

Enter with:

- Discovery evidence note, resolved-decisions record, prototype, and design-decision capture.

Evidence required:

- The design question is answered and the chosen direction is recorded.

Action:

- Use `to-prd` to synthesize the PRD from existing context. Do not re-interview the user.
- Use the project's domain glossary throughout and respect ADRs in the touched area.
- Reference the prototype location and the design-decision capture.
- Include problem, users, scope and non-goals, acceptance criteria, and risks.

Artifact:

- PRD published per `to-prd` (tracker or repo location recorded), referencing the prototype.

Gate:

- Continue only when the PRD states the problem, users, scope, acceptance criteria, and links the prototype.

Stop if:

- Acceptance criteria are not externally observable.
- The PRD depends on an unresolved design decision.

Anti-pattern:

- Do not invent requirements the discovery never grounded.
- Do not interview the user from scratch at PRD time.

## Phase 6: Publish to Linear

Goal: turn the PRD into a Linear project engineering can grab.

Enter with:

- PRD and prototype references.

Evidence required:

- The owning Linear team/project is identified or can be created.

Action:

- Use `linear` to create or refresh the project and attach or link the PRD and prototype.
- Use `to-issues` to break the PRD into independently-grabbable vertical-slice issues, then create them via `linear`.
- Link each issue to the PRD and prototype.

Artifact:

- Linear project containing the PRD reference, prototype reference, and vertical-slice issues.

Gate:

- Continue only when the project and issues exist and are linked to the PRD and prototype.

Stop if:

- Linear access or the target project cannot be obtained.

Anti-pattern:

- Do not split issues by layer instead of vertical slice.
- Do not create issues that omit the PRD or prototype link.

## Phase 7: Handoff to Engineering

Goal: package discovery so the `fullstack-engineering` workflow can start without rediscovery.

Enter with:

- PRD, prototype, and Linear project references.

Evidence required:

- All three artifacts exist and are linked.

Action:

- Use `handoff` to write the handoff document.
- Name the PRD location/URL, prototype repo and route, Linear project and issue keys, resolved decisions, open risks, and the recommended next workflow (`fullstack-engineering`).

Artifact:

- Handoff note (terminal success artifact).

Gate:

- Complete only when another agent can start `fullstack-engineering` from the handoff without rediscovery.

Stop if:

- Sensitive information cannot be safely redacted.

Anti-pattern:

- Do not say "continue from here" without defining "here".
- Do not duplicate PRD content in the handoff; reference it by path or URL.

## Reset Rules

Return to an earlier phase when evidence invalidates the current path:

- New product surface or audience -> Intake.
- Observed behavior contradicts an assumption -> Evidence.
- A blocking design question reopens -> Alignment.
- Prototype disproves the chosen direction -> Alignment, then Prototype.
- PRD review exposes an ungrounded requirement -> Evidence or Alignment.
- Issue breakdown reveals the PRD is not sliceable -> PRD.

## Completion Gate

The Workflow is complete only when:

- A PRD exists with problem, users, scope, and observable acceptance criteria.
- A runnable throwaway prototype exists and its chosen direction is recorded.
- A Linear project exists with vertical-slice issues linked to the PRD and prototype.
- The handoff note names every artifact and the recommended next workflow.
- Open risks and deferred decisions are documented.

## Handoff Rules

Stop and hand off when:

- Required evidence cannot be gathered.
- A required Skill or Plugin named in this document is unavailable.
- A design decision requires a user choice that cannot be obtained.
- Linear or the prototype repo is inaccessible.
- Work cannot finish in the current session.

The handoff must name current phase, completed artifacts, blocker, last verification result, and next action.

## Guardrails

- Do not specify before discovering.
- Do not prototype before naming the design question.
- Do not write the PRD before the design question is answered.
- Do not publish issues before the PRD exists.
- Do not promote prototype code to production.
- Do not invent requirements the discovery never grounded.
- Do not hide failed commands or unanswered questions.
- Do not invent Plugin behavior.
- Do not put low-level implementation procedure in this Workflow. Load the owning Skill.
