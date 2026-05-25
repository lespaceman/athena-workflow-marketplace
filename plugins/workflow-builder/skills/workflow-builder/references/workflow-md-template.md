# workflow.md Template

Use this as the default shape for Athena workflow orchestration docs. Replace bracketed placeholders.

```md
# [Workflow Display Name] Workflow

[One short paragraph describing what the workflow carries from input to outcome.]

## Operating Principle

[One to three hard rules. Example: Build only from evidence. Do not jump phases. A phase is complete only when its artifact exists and its gate passes.]

## Capability Contract

Treat this document and the visible runtime context as the complete contract.
Use only Skills, Plugins, tools, and handoff rules visible in the current context or explicitly named here.

If a required capability is not visible, stop and name exactly what is missing.
Do not infer hidden pins, versions, permissions, or tools.

## Skill Routing

Load the owning Skill before doing the activity.

| Activity | Skill or visible capability |
|----------|-----------------------------|
| [Activity] | `[skill-name]` |

If the named Skill is not visible, follow this workflow's generic phase instructions or stop when specialist behavior is required for safety.

## Task Tracker Discipline

At session start:

- Read visible tracker, issue, execution notes, or handoff.
- Reconcile done, pending, blocked, and unknown work.
- Record current phase before changing files.

If no durable tracker exists, keep a session execution note with:

- Current phase
- Completed artifacts
- Open blockers
- Last verification result
- Next action

Do not write tracker files into the repo unless the repo already has that convention or the user approves it.

## State Graph

Default path:

**[Phase 1] -> [Phase 2] -> [Phase 3] -> [Success Terminal]**

Alternate terminal state:

**Handoff / Blocked**

Shortcut rule: if a skipped phase owns evidence required by a later gate, the shortcut is invalid.

## Phase 1: [Name]

Goal: [What this phase decides or produces.]

Enter with:

- [Required input]

Evidence required:

- [Evidence]

Action:

- [Action]

Artifact:

- [Artifact]

Gate:

- Continue only when [condition].

Loop if:

- [Local fix or retry condition.]

Stop if:

- [Missing evidence or unsafe condition.]

Anti-pattern:

- Do not [common failure mode].

## Reset Rules

Return to an earlier phase when evidence invalidates the current path:

- [Invalidating event] -> [Phase]

## Completion Gate

The workflow is complete only when:

- [Outcome evidence exists]
- [Verification or review passed]
- [Residual risk is documented]

## Handoff Rules

Stop and hand off when:

- Required evidence cannot be gathered.
- Environment or credentials are missing.
- User decision is required.
- Work cannot finish in the current session.

The handoff must name current phase, completed artifacts, blocker, last verification result, and next action.

## Guardrails

- Do not guess when evidence can be gathered.
- Do not claim unavailable capability.
- Do not call work done without the completion gate.
- Do not hide failed commands.
- Do not put low-level implementation procedure in this workflow. Load or write the owning Skill.
```
