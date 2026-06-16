---
name: workflow-handoff
description: Package an in-flight fullstack-engineering task into a resumable relay note so the next agent continues at the exact phase and gate. Use at a clean slice/phase/gate boundary, or mid-task when the current agent is out of usable context (token window exhausted, context rot, "compact and continue"). Captures the Turn Protocol block, cleared gates, working branch + last pushed commit, durable-artifact pointers, the exact next action, and open blockers; saves to the OS temp dir like `handoff`. Triggers - "workflow handoff", "hand off this task", "relay to the next agent", "pass the baton", "continue in a fresh session", "running low on context", "context rot", "approaching the token limit", "I finished phase N, hand off", "resume from here", or any stop-and-handoff route into Phase 10. Unlike `handoff` (a generic conversation summary), this preserves binding workflow state for mid-flight resumption. It does NOT advance phases, waive gates, or duplicate the tracker/design/plan/commits - it references them.
---

# Workflow Handoff

Produce a **relay note**: a small, resumable capsule of *workflow state* that lets the next agent re-enter the [fullstack-engineering workflow](../../../../workflows/fullstack-engineering/workflow.md) at the exact phase and gate — without re-discovering anything. This is not a conversation summary (`handoff` does that); it is the running Turn Protocol block plus pointers to durable proof.

## When to relay

- **Boundary handoff** — a vertical slice, phase, or gate is cleanly complete and the next unit is better done by a fresh agent.
- **Context-rot handoff** — you are mid-task and out of *usable* context: token window exhausted, summary churn, you no longer trust your own recall of earlier turns. Relaying now beats pushing on degraded.

If a gate is blocked and only the user can clear it, that is a `Stop -> handoff` into **Phase 10** — relay, then stop. Work cannot continue in this session after this fires.

## Before you write the note — make state durable

The temp note is a **pointer**, not the system of record. So first ensure the truth survives you:

1. **Push the working branch.** Every completed slice and every repo-file artifact must be committed AND pushed — a local-only commit is not recoverable by the next agent. Record the last pushed commit SHA.
2. **Re-persist the session note** to its durable home (tracker / Linear issue / committed file). A conversation-only Turn Protocol block does not survive compaction.
3. **Reconcile the Turn Protocol block with reality** — it must match the branch, commits, and tracker, not what you intended. If they disagree, fix the durable artifact first.

Never relay a state you have not made recoverable. If you cannot push (read-only clone) or cannot reach the tracker, say so in the note as a blocker.

## Write the relay note

Save to the OS temp dir (not the workspace), filename naming the branch — e.g. `<tmp>/relay-<branch>.md`. Fill the template in [RELAY-NOTE.md](RELAY-NOTE.md). Rules:

- **Reference, do not duplicate.** Design note, plan, PRD, issues, coverage plan, browser evidence, commits already live in durable artifacts — link them by path/URL/SHA, don't paste them.
- **The next action must be a single concrete step**, ideally a command. "Continue from here" without defining "here" is a failure.
- **Cleared gates carry their evidence pointer** (command output location, committed file, browser proof, tracker entry) — never "I believe it passed".
- **Context-rot mode adds a Trust ledger:** what the next agent should re-verify from scratch vs. trust as proven, and anything you are now unsure you got right.
- **Suggested skills on resume** — name the phase's owning skills the next agent loads first (e.g. re-enter Phase 6 with `tdd`; `diagnose` if the open bug resurfaces; `linear` to read tracker state).
- **Redact secrets** — API keys, tokens, passwords, PII.

## Hand-back

End your turn pointing the user (or orchestrator) at the saved note path and the one-line next action. Do not start the next phase yourself — relaying means this session is done with the task.
