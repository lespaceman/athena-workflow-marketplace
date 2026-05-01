# athena-evals

Long-running, event-sourced reliability evaluation pipeline for community-built agent skills. See `docs/rfcs/0003-skill-evaluation-pipeline.md` for the contract.

## Quickstart

```bash
python3.12 -m venv evals/.venv
evals/.venv/bin/pip install -e 'evals[dev]'

export GITHUB_TOKEN=...
export ANTHROPIC_API_KEY=...

scripts/run-evals.sh discover
scripts/run-evals.sh extract
scripts/run-evals.sh eval --phase 1
scripts/run-evals.sh report --format rich
```

## Layout

```
evals/
  events/      Append-only event log + projections (SQLite)
  github/      Async httpx client with rate-limit handling
  extraction/  Discovery + SKILL.md fetch
  evaluators/  Phased evaluators (compliance, repo health, security, LLM judge, authenticity, ...)
  llm/         Anthropic client wrapper + versioned rubrics + cost tracker
  scoring/     Weights + composite reliability score + tier mapping
  reporter/    rich.Table + JSONL + Markdown
  workers/     Dispatcher + concurrency pool
  seeds/       Hand-curated registry seeds
  tests/       pytest suite
```

## Architecture

```
seeds (YAML) -> Discovery -> EventStore (append-only)
                                 |
                             Dispatcher -> Workers (per evaluator) -> EventStore
                                 |
                             Projector -> skills_current / evals_current
                                 |
                             Reporter -> rich.Table + JSONL + Markdown
```

Idempotency is enforced by `dedupe_key = sha256(skill_id | evaluator@version | inputs_hash)`.

## Standards

- Python 3.12, type hints everywhere, `mypy --strict`.
- Lint: `ruff check evals/`. Format: `black evals/`.
- Tests: `pytest evals/tests`. No real network in tests.
