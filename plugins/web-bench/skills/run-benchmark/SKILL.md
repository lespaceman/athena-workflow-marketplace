---
name: run-benchmark
description: >
  Run the WebBench browser agent benchmark — main entry point and orchestrator. Triggers: "run benchmark", "run WebBench", "start benchmark", "benchmark browser agent", "web bench", "execute WebBench", "run web-bench". Parses user configuration (category filter, sample size, resume), delegates to load-dataset, execute-task, evaluate-task, and generate-report skills. This is the user-invocable orchestrator that ties the full benchmark pipeline together.
allowed-tools: Read Write Edit Glob Grep Bash Task
---

# Run WebBench Benchmark

Main entry point for running the WebBench browser agent benchmark. This skill is used in interactive (single-session) mode. For multi-session workflow execution, see the system prompt.

## Input

Parse configuration from: `$ARGUMENTS`

Supported flags:

| Flag | Description | Default |
|------|-------------|---------|
| `--category <CAT>` | Filter tasks by category (READ, CREATE, UPDATE, DELETE, FILE_MANIPULATION) | All categories |
| `--sample <N>` | Random sample of N tasks (deterministic seed=42) | Full dataset |
| `--resume` | Resume from existing web-bench-results.jsonl, skip completed task IDs | Fresh run |
| `--report-only` | Skip execution, just generate report from existing results | Full run |

Examples:
- `run-benchmark --category READ --sample 50` — 50 random READ tasks
- `run-benchmark --resume` — continue from where last run stopped
- `run-benchmark --report-only` — just aggregate existing results

## Interactive Execution Protocol

When run interactively (not via the workflow loop), this skill executes the full pipeline in a single session:

### 1. Setup

1. Parse arguments
2. Check for existing state (`web-bench-tasks.jsonl`, `web-bench-results.jsonl`)
3. If `--resume` and results exist: determine completed task IDs, skip them
4. If not resuming: load the `load-dataset` skill to download and prepare the dataset
5. Report configuration and task count

### 2. Execute Tasks

For each task in `web-bench-tasks.jsonl` (skipping completed if resuming):

1. Read the task line
2. Record start time: `date +%s%3N`
3. Load `execute-task` methodology and have the browser-capable calling context perform the browser automation
4. Load `evaluate-task` methodology and score the result
5. Record end time: `date +%s%3N`, compute duration
6. Append result to `web-bench-results.jsonl`:
   ```json
   {"id": 42, "url": "...", "category": "READ", "task": "...", "score": 1.0, "verdict": "PASS", "reasoning": "...", "error": null, "duration_ms": 34200, "tokens_used": {"input": 12450, "output": 3200}, "timestamp": "2026-03-19T14:30:00Z"}
   ```
7. Print progress: `[42/2454] PASS (1.0) — acehardware.com — READ — 34.2s`

### 3. Generate Report

After all tasks are processed (or if `--report-only`):

1. Load `generate-report` methodology
2. Aggregate `web-bench-results.jsonl` into `web-bench-report.md`
3. Print summary statistics to console

## Token Tracking

Token usage should be tracked per task. The agent should estimate tokens consumed during task execution by recording:

- **Input tokens:** Approximate from the size of prompts, page snapshots, and tool responses received during execution
- **Output tokens:** Approximate from the size of responses and tool calls generated

If exact token counts are available from the session metadata, prefer those over estimates.

## Progress Display

After each task, print a status line:

```
[1/50] PASS  (1.0)  acehardware.com          READ    34.2s   15,650 tokens
[2/50] FAIL  (0.0)  airbnb.com               CREATE  12.1s    8,200 tokens  [auth_required]
[3/50] PARTIAL(0.5) amazon.com               READ    45.8s   22,100 tokens
```

## Guardrails

- **Always append, never overwrite** results. The JSONL file is append-only.
- **Respect the dataset.** Do not modify task descriptions or skip tasks without recording a FAIL.
