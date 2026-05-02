# `workflow.md` Rating Rubric

Reusable checklist for rating the `workflow.md` of any workflow in
`/.athena-workflow/marketplace.json`.

## Why this exists

`workflow.json` is the contract (RFC 0001 §"Workflow Definition Contract"). `workflow.md` is the
operational guidance the runtime appends to its workflow/system prompt. So `workflow.md` is rated
as a prompt — does it let an agent enter the workflow cold and behave deterministically across
sessions, harness boundaries, and `--continue` resumes?

Anchor every dimension on what RFC 0001 says workflows exist to provide:

- resumability across process restarts and context resets
- deterministic progression through named steps
- explicit completion and blocked semantics
- repeatable behavior across CLI tools

## How to use

1. Read the target `workflow.md` and `workflow.json` once.
2. Score each dimension below 0–3 using the rubric.
3. Drop low-relevance dimensions (e.g. dimension 5 "Quality floors" is N/A for a one-shot
   benchmarking workflow). Note them as N/A rather than 0.
4. Total the applicable dimensions and divide by the maximum possible to get a percentage.
5. Capture the top 2–3 portable upgrades — concrete, named — in the notes section.

A score of 0 means the dimension is missing. 1 means it's referenced. 2 means it's concrete and
actionable. 3 means it's concrete, actionable, and battle-tested (carries rationale tied to a known
failure mode).

## Dimensions

### 1. Plugin / skill surface

The agent can pick the right skill from a cold start.

- **0** — plugins not listed; no skill mapping
- **1** — plugins listed in prose
- **2** — plugin → skills table and activity → skill mapping
- **3** — both tables, with explicit "load this skill before X" guidance and trigger language that
  matches the skill descriptions

### 2. Entry point

One unambiguous "first action this session" rule.

- **0** — no entry point named
- **1** — entry skill named for fresh sessions
- **2** — entry rule named for fresh + `--continue`
- **3** — entry rule covers fresh, `--continue`, harness sub-session, and delegated subagent

### 3. Resumability discipline

RFC's headline goal: durable state across sessions.

- **0** — no recovery story
- **1** — phase/state can be inferred from on-disk artifacts
- **2** — explicit reconciliation procedure on session start; tracker or execution-notes contract
- **3** — reconciliation + decomposition cadence + update cadence + handoff rules across harnesses

### 4. Sequence and dependency graph

Either strict order or a DAG with prerequisites.

- **0** — no sequence given
- **1** — informal narrative order
- **2** — explicit sequence or state machine
- **3** — sequence presented as a DAG with a "before you can X, you must have Y" prerequisites
  table and named alternative paths (narrow / broad / brownfield / repair)

### 5. Quality floors

Concrete numeric targets — defends against shallow work.

- **0** — none
- **1** — qualitative criteria only ("tests green", "looks good")
- **2** — at least one concrete numeric floor or cap
- **3** — multiple floors covering breadth, depth, and ratio (e.g. ≥N items, ≥X% functional,
  ≤Y% deferred), each with a stated rationale

> N/A is acceptable for workflows whose output isn't gradable in numeric terms. Mark it explicitly.

### 6. Gates and reset rules

Defined gates with pass/fail criteria + what triggers re-running an earlier gate when scope shifts.

- **0** — no gates
- **1** — single review step
- **2** — multiple gates with named entry/exit
- **3** — multiple gates + explicit reset rule for spec/code/scope changes + a run ledger or
  equivalent audit trail

### 7. Delegation rules

What stays in the main agent vs. dispatched subagents. Tool-locality. Anti-self-review.

- **0** — not addressed
- **1** — subagent dispatch mentioned
- **2** — main-agent vs subagent split named for the major activities
- **3** — codified rules including: who never browses, who never self-reviews, what proof artifact
  must stay in the main agent, what each Task call must receive

### 8. Failure handling

Retry/stop policy, triage protocol, "blockers surface, not guess."

- **0** — not addressed
- **1** — generic "fix and retry"
- **2** — retry policy with stop conditions
- **3** — retry policy + structured triage producing a typed verdict (e.g. product-regression /
  drift / test-defect / environment) + escalation rules

### 9. Anti-patterns with rationale

Names known failure modes and explains why each rule exists.

- **0** — rules without reasons
- **1** — a few rationale strings
- **2** — most rules carry a "this exists because..." note
- **3** — dedicated red-flag / anti-pattern section + per-rule rationale tied to observed prior
  failures

### 10. Done definition and proof artifact

Maps cleanly onto RFC 0001's complete/blocked/exhausted semantics.

- **0** — "done" undefined
- **1** — single proof step (e.g. tests pass)
- **2** — proof step + named on-disk artifact
- **3** — typed verdict (e.g. GREEN / YELLOW / RED) backed by an audit artifact and rules for what
  invalidates a previous green

### 11. Scannability

Cold-start readability for a fresh session.

- **0** — wall of prose
- **1** — headings only
- **2** — tables and/or diagrams compress the rules
- **3** — tables/diagrams + a scannable top-of-doc summary; tone proportional to content (rules
  carry weight through structure, not shouting)

## Scoring template

```
Workflow: <workflow-name>
Date: <YYYY-MM-DD>
Reviewer: <name or agent>

| # | Dimension                          | Score | Notes |
|---|------------------------------------|-------|-------|
| 1 | Plugin / skill surface             |       |       |
| 2 | Entry point                        |       |       |
| 3 | Resumability discipline            |       |       |
| 4 | Sequence and dependency graph      |       |       |
| 5 | Quality floors                     |       |       |
| 6 | Gates and reset rules              |       |       |
| 7 | Delegation rules                   |       |       |
| 8 | Failure handling                   |       |       |
| 9 | Anti-patterns with rationale       |       |       |
| 10| Done definition and proof artifact |       |       |
| 11| Scannability                       |       |       |

Applicable max: __ / 33
Total:          __
Percentage:     __ %

Top portable upgrades:
1.
2.
3.
```

## Reference scores

Two workflows in this repo, scored on 2026-05-02 as calibration anchors:

| Workflow | Score | Notes |
|---|---|---|
| `playwright-automation` | 32 / 33 | Battle-tested gates, reset rule, run ledger, typed Gate 4 verdict, codified delegation rules. Loses 1 point on scannability (long; no top-of-doc TL;DR). |
| `fullstack-engineering` | 24 / 33 | Strong phase state machine, red-flag thoughts, decision-flow diagram. Thin on resumability, quality floors, gate-reset semantics, and a typed done verdict. Loud framing substitutes for structure in places. |

Use these as anchors when scoring future workflows: a workflow that hits the playwright bar across
all dimensions should approach 33; a workflow with phase discipline but no resumability or numeric
floors should land near 24.
