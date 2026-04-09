# WebBench Benchmark Runner

You execute real-world browser tasks from the Halluminate/WebBench dataset and score them, **exactly one task per session**.

## Skills

Load the relevant skill before each activity.

| Activity | Skill |
|----------|-------|
| Download and prepare dataset | `load-dataset` |
| Execute a browser task | `execute-task` |
| Judge task completion | `evaluate-task` |
| Aggregate results into report | `generate-report` |
| Full interactive run (not used in workflow mode) | `run-benchmark` |

## Persistent State

Two files persist across sessions:

| File | Purpose | Format |
|------|---------|--------|
| `web-bench-results.jsonl` | Append-only results log — one JSON line per completed task | JSONL |

The results file records what was done.

### Results Line Schema

Each line in `web-bench-results.jsonl` must contain:

```json
{
  "id": 42,
  "url": "https://acehardware.com",
  "category": "READ",
  "task": "Navigate to the news section and...",
  "score": 1.0,
  "verdict": "PASS",
  "reasoning": "Successfully navigated to news section and extracted all requested data",
  "error": null,
  "duration_ms": 34200,
  "tokens_used": {"input": 12450, "output": 3200},
  "timestamp": "2026-03-19T14:30:00Z"
}
```

**Required fields:**
- `id` (int): Task ID from the dataset
- `url` (string): Starting URL
- `category` (string): READ, CREATE, UPDATE, DELETE, or FILE_MANIPULATION
- `task` (string): Original task description
- `score` (float): 1.0 (PASS), 0.5 (PARTIAL), or 0.0 (FAIL)
- `verdict` (string): PASS, PARTIAL, or FAIL
- `reasoning` (string): Explanation of why this verdict was given
- `error` (string|null): Blocker type if applicable (e.g., "auth_required", "captcha", "site_down")
- `duration_ms` (int): Wall-clock time from task start to evaluation end
- `tokens_used` (object): `{"input": N, "output": N}` — token counts for this task's execution and evaluation
- `timestamp` (string): ISO 8601 timestamp of completion

## Orientation Steps

### Prepare the dataset

First check if `web-bench-tasks.jsonl` already exists in the working directory. If it exists and is non-empty, skip the download — reuse the existing file.

If the file does not exist, load the `load-dataset` skill to:

1. Download the WebBench CSV from HuggingFace
2. Convert to `web-bench-tasks.jsonl`
3. Apply filters (category, sample size) per the user's configuration
4. Verify the output

**Session 1 ends after setup.** Do not execute any tasks in the setup session.

## Workflow Sequence

### Execute one task

1. Determine the next task to execute. If all tasks are complete, skip to report generation.
2. Fetch the task line from `web-bench-tasks.jsonl`.
3. Record start time.
4. Load the `execute-task` skill. Navigate to the starting URL, perform browser actions, capture final state.
5. **Action limit:** If the task requires more than 25 browser actions, consider it stuck. Record what you have and move to evaluation.
6. Load the `evaluate-task` skill. Check requirements against the execution trace. Determine verdict: PASS (1.0), PARTIAL (0.5), or FAIL (0.0).
7. Record end time and compute `duration_ms`.
8. Record token usage — use exact session token counts from the runtime if available, otherwise estimate from content received (input) and generated (output).
9. Append a single JSON line to `web-bench-results.jsonl`. **Always append, never overwrite.**
**One task per session.** After executing and evaluating a single task, stop. This ensures clean browser state, bounded context usage, and granular progress tracking.

### Generate report (final session)

When all tasks are complete:

1. Load the `generate-report` skill
2. Aggregate `web-bench-results.jsonl`
3. Write `web-bench-report.md`
## Guardrails

- **One task per session.** Execute one task, record the result, stop.
- **Always append results** — never overwrite `web-bench-results.jsonl`.
- **Close the browser** after each task.
- **Do not skip tasks.** If a task fails or is blocked, record FAIL and move on. Every task must have a result line.

## Error Recovery

If previously recorded output and the current session state disagree about what has already been completed, trust `web-bench-results.jsonl` as the source of truth for completed tasks because it is append-only and harder to corrupt.
