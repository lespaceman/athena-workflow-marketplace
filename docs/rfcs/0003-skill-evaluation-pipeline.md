# RFC 0003: Skill Evaluation Pipeline

- Status: Draft
- Author: Athena Workflow Marketplace Maintainers
- Created: 2026-05-01
- Audience: marketplace maintainers and skill authors

## Abstract

This RFC defines a reproducible, event-sourced pipeline for evaluating Agent
Skills published across community marketplaces. The pipeline produces a tiered
reliability report (S/A/B/C/D) from a layered scoring model that combines
deterministic repo and frontmatter checks with LLM-judged compliance and
adversarial provenance signals. The event log is the source of truth; all
projections, scores, and reports are derivable from it. This RFC complements
RFC 0001 (workflow contract) and RFC 0002 (cross-runtime packaging) by adding a
trust-signal layer that is independent of any one runtime.

## Problem Statement

Public skill registries are growing faster than maintainers can audit. Naive
trust signals such as GitHub star counts, follower numbers, and "trending"
listings are easy to inflate and do not measure whether a skill actually works.
A user picking a skill cannot tell at a glance whether it is well-maintained,
runtime-portable, secure, or backed by a real community. This RFC defines a
pipeline that produces a reliability report from observable, mostly cheap
signals, with explicit cost and reproducibility guarantees.

## Goals

- Reproducible: re-running the pipeline against the same inputs produces the
  same report.
- Idempotent: re-runs do not duplicate work; the dedupe key gates writes.
- Phased: cheap deterministic evaluators run first; expensive LLM judges run
  only when phase gates allow.
- Cost-bounded: a per-run cost cap MUST stop further LLM calls when reached.
- Runtime-agnostic: skills authored for any compatible runtime can be
  evaluated; the pipeline is not coupled to Claude or Codex.
- Machine-readable: every artifact (events, projections, reports) is JSON or
  JSONL so downstream tooling can ingest it.

## Non-Goals

- The pipeline is not a runtime; it does not execute skills against real
  workloads beyond a sandboxed live-validator clone step.
- It is not a security audit; security signals are advisory and probabilistic.
- It is not a marketplace gatekeeper; tier outputs are recommendations, not
  enforcement.

## Design Principles

1. Event-sourced
- The append-only event log is the source of truth.
- Projections (`skills_current`, `evals_current`) are derived state and can be
  rebuilt from events at any time.

2. Deterministic-first
- Phase 1 evaluators rely only on git/GitHub metadata and frontmatter parsing.
- LLM judges run only after deterministic phases gate them in.

3. LLM-judged with cache
- Judge prompts and rubrics are versioned. Identical `(skill, evaluator,
  evaluator_version, inputs_hash)` MUST hit cache rather than re-billing.

4. Layered scoring
- Evaluator scores roll up into four buckets (health, provenance, compliance,
  security) before being combined into the composite score and tier.

## Pipeline Phases

| Phase | Evaluators                                        | Inputs                            | Side Effects                               | Failure Mode                           |
|-------|---------------------------------------------------|-----------------------------------|--------------------------------------------|----------------------------------------|
| 1     | repo-health, release-cadence                      | GitHub repo metadata              | `eval.completed` per evaluator             | Evaluator is skipped; `eval.failed`    |
| 2     | follower-authenticity, contributor-authenticity   | GitHub user/org graph             | Bot-likelihood signals; `eval.completed`   | Bot signals downgrade provenance score |
| 3     | compliance-check, cross-runtime, report-quality   | SKILL.md frontmatter and overlays | LLM judge calls; `eval.completed`          | Cost cap may abort; `eval.failed`      |
| 4     | live-validator, security-scan                     | Sandboxed clone of skill repo    | Optional clone; `eval.completed`           | Sandbox failure marks evaluator failed |

Phases run in order. A higher phase MUST NOT execute for a skill until the
lower phase has settled (completed or failed) for that skill.

## Event Model

Eight event types compose the log. All share a base envelope with `event_id`,
`occurred_at`, `run_id`, `skill_id`, `schema_version`, and `dedupe_key`.

| Event Type           | Payload Fields                                                                 |
|----------------------|--------------------------------------------------------------------------------|
| `skill.discovered`   | `source_registry`, `repo_url`, `initial_metadata`                              |
| `skill.extracted`    | `skill_md_sha`, `frontmatter`, `overlays`, `content_hash`                      |
| `eval.requested`     | `evaluator`, `evaluator_version`, `phase`, `inputs_hash`                       |
| `eval.started`       | `evaluator`, `evaluator_version`, `worker_id`                                  |
| `eval.progress`      | `evaluator`, `pct`, `note`                                                     |
| `eval.completed`     | `evaluator`, `evaluator_version`, `score`, `sub_scores`, `findings`, `cost_usd`, `duration_ms` |
| `eval.failed`        | `evaluator`, `error_class`, `error_message`, `retriable`                       |
| `report.generated`   | `output_paths`, `skills_count`, `composite_summary`                            |

The dedupe key for evaluator events MUST be derived from
`(skill_id, evaluator@version, inputs_hash)` so identical work cannot
double-write.

## Storage

The store is SQLite by default. The migration creates the append-only `events`
table plus two projections (`skills_current`, `evals_current`) and a `runs`
header. The reporter reads only projections and the event log.

```text
discoverer/extractor/workers
        |
        v
   [events table]   <-- append-only, dedupe-keyed
        |
        v
   projections      <-- skills_current, evals_current (rebuildable)
        |
        v
   reporter         <-- rich.Table, JSONL, Markdown
```

## Composite Scoring

The composite score is the weighted average of four bucket scores. A bucket
score is the simple mean of its present evaluator scores; missing evaluators
contribute zero only if the entire bucket is empty.

Default weights:

| Bucket      | Weight | Evaluators                                                         |
|-------------|--------|--------------------------------------------------------------------|
| health      | 0.25   | repo-health, release-cadence                                       |
| provenance  | 0.25   | follower-authenticity, contributor-authenticity                    |
| compliance  | 0.30   | compliance-check, cross-runtime, live-validator, report-quality    |
| security    | 0.20   | security-scan                                                      |

```text
score = 0.25*health + 0.25*provenance + 0.30*compliance + 0.20*security
```

Tier mapping:

| Tier | Threshold |
|------|-----------|
| S    | >= 90.0   |
| A    | >= 80.0   |
| B    | >= 70.0   |
| C    | >= 60.0   |
| D    | <  60.0   |

## Adversarial Evaluators

Provenance evaluators look at the social graph around a skill's owner and top
contributors. The intent is to surface obviously inauthentic signal-boosting,
not to make a definitive judgment.

| Signal                       | Source                                  |
|------------------------------|-----------------------------------------|
| Follower-to-following ratio  | GitHub user graph                       |
| Account age vs. activity     | GitHub `created_at`, contributions      |
| Default avatar / empty bio   | GitHub user profile                     |
| Burst follow patterns        | Sampled follower timestamps             |
| Contributor overlap with bots| Known bot list / GitHub App accounts    |

These signals are probabilistic. The reporter MUST present provenance findings
as advisory text; the pipeline MUST NOT publish per-account "bot" labels.
Evaluator output is a numeric score plus prose findings, never a hard claim.

## CLI Contract

| Subcommand | Key Flags                                                                                                    | Purpose                                  |
|------------|---------------------------------------------------------------------------------------------------------------|------------------------------------------|
| `discover` | `--seeds <path>`                                                                                              | Emit `skill.discovered` from seeds       |
| `extract`  | `--skill <id>`                                                                                                | Fetch SKILL.md and overlays              |
| `eval`     | `--phase {1,2,3,4}`, `--evaluator <name>`, `--judge-model`, `--cost-cap-usd`, `--force`, `--strict`           | Run evaluators                           |
| `project`  | `--rebuild`                                                                                                   | Rebuild current-state projections        |
| `report`   | `--format {rich,jsonl,md}`, `--all`, `--sort-by`, `--filter-category`, `--min-tier`                            | Render the reliability report            |

All subcommands accept `--db <path>` and `--log-level`.

## Cost & Rate-Limit Governance

- A per-run cost cap (`--cost-cap-usd` or `EVALS_COST_CAP_USD`) MUST be
  enforced before any LLM call. Once the cap is exceeded, additional LLM-backed
  evaluators MUST be marked `eval.failed` with `error_class="cost_cap"`.
- GitHub calls SHOULD use a token. Workers SHOULD respect the response's
  `X-RateLimit-Remaining` header and back off rather than retry tightly.
- Cache hits do not consume the cost cap.

## Versioning

Each evaluator declares an `evaluator_version` that combines code version and
rubric version. The cache key is
`(skill_id, evaluator, evaluator_version, inputs_hash)`. Any change to the
rubric or the prompt MUST bump `evaluator_version`; this invalidates affected
cache entries without rewriting history.

`schema_version` on events covers payload shape only. Increasing it MUST be
backward-compatible for projections (old payloads still validate) or
accompanied by a projection rebuild.

## Forward Compatibility

- The event store is a `Protocol`; the SQLite implementation can be swapped
  for Postgres without changing call sites.
- New evaluators SHOULD register via Python entry points
  (`athena_evals.evaluators`) so external packages can extend the suite without
  forking the pipeline.
- The Markdown and JSONL renderers are structured to feed a future web UI;
  field names match the dataclass fields exactly.

## Security Considerations

- The live-validator clone step MUST run inside a sandbox with no host
  filesystem write access outside its scratch directory. Network access SHOULD
  be limited to the cloned repository.
- Secret scans MUST NOT log matched secret bytes. Findings SHOULD reference
  only the file path, line number, and a non-reversible fingerprint.
- Workers MUST treat skill content as untrusted input and never execute scripts
  or shell snippets read from a SKILL.md.
- LLM prompts MUST quote skill content rather than interpolate it as
  instructions.

## Open Questions

- Whether the GitHub token used by provenance evaluators should be an
  organization token (higher rate limits, but more identifying) or per-user.
- Behavior when a run is started already over the cost cap: refuse, warn, or
  run only deterministic phases.
- Whether bot-likelihood disclaimers should be a fixed footer in the report or
  emitted per finding.
- Compaction policy for the event log: when (if ever) to summarize old events
  into a single rebuilt projection snapshot.

## Appendix A: Sample Event JSON

`skill.discovered`:

```json
{
  "event_type": "skill.discovered",
  "event_id": "8b9a...",
  "occurred_at": "2026-05-01T12:00:00Z",
  "run_id": "f1e2...",
  "skill_id": "acme/example#skills/define-regression-scope",
  "schema_version": 1,
  "dedupe_key": "...",
  "source_registry": "seeds.yaml",
  "repo_url": "https://github.com/acme/example",
  "initial_metadata": {"category": "testing"}
}
```

`skill.extracted`:

```json
{
  "event_type": "skill.extracted",
  "skill_md_sha": "sha1:abc...",
  "frontmatter": {"name": "x", "description": "y"},
  "overlays": {"claude": null, "openai": null},
  "content_hash": "abc..."
}
```

`eval.requested`:

```json
{
  "event_type": "eval.requested",
  "evaluator": "compliance-check",
  "evaluator_version": "1.0.0",
  "phase": 3,
  "inputs_hash": "h1"
}
```

`eval.started`:

```json
{
  "event_type": "eval.started",
  "evaluator": "compliance-check",
  "evaluator_version": "1.0.0",
  "worker_id": "w-12"
}
```

`eval.progress`:

```json
{
  "event_type": "eval.progress",
  "evaluator": "live-validator",
  "pct": 0.42,
  "note": "cloning repo"
}
```

`eval.completed`:

```json
{
  "event_type": "eval.completed",
  "evaluator": "compliance-check",
  "evaluator_version": "1.0.0",
  "score": 87.5,
  "sub_scores": {"frontmatter_schema": 1.0, "portable_keys": 0.9, "overlays_present": 0.5, "description_quality": 1.0},
  "findings": ["overlays present: 1/2 (claude/openai)"],
  "cost_usd": 0.012,
  "duration_ms": 2300
}
```

`eval.failed`:

```json
{
  "event_type": "eval.failed",
  "evaluator": "live-validator",
  "error_class": "sandbox_error",
  "error_message": "clone timed out after 60s",
  "retriable": true
}
```

`report.generated`:

```json
{
  "event_type": "report.generated",
  "output_paths": ["evals/runs/<run-id>/report.jsonl",
                   "evals/runs/<run-id>/report.md"],
  "skills_count": 42,
  "composite_summary": {"S": 3, "A": 12, "B": 18, "C": 7, "D": 2}
}
```

## Appendix B: Sample Reliability Report Excerpt

Rich-rendered (text approximation):

```text
                   Skill Reliability Report
+--------------------------------+------+-------+--------+------------+------------+----------+
| Skill                          | Tier | Score | Health | Provenance | Compliance | Security |
+--------------------------------+------+-------+--------+------------+------------+----------+
| acme/example#skills/regression | S    |  93.2 |   95.0 |       91.0 |       94.0 |     90.0 |
| other/sample#skills/lint-tests | B    |  72.5 |   80.0 |       65.0 |       78.0 |     60.0 |
+--------------------------------+------+-------+--------+------------+------------+----------+
```

Markdown excerpt:

```markdown
# Skill Reliability Report

## Tier S

<details>
<summary><strong>acme/example#skills/regression</strong> &mdash; score 93.2</summary>

- Repo: https://github.com/acme/example
- Category: testing
- Bucket scores:
  - health: 95.0
  - provenance: 91.0
  - compliance: 94.0
  - security: 90.0
- Findings: none

</details>
```

The Markdown report MUST keep the `<details>` blocks collapsible by default;
maintainers can expand individual skills to see findings without scrolling
past clean ones.
