---
name: generate-report
description: >
  Aggregate WebBench benchmark results into a comprehensive evaluation report.
  Triggers: "generate report", "create benchmark report", "summarize results",
  "aggregate scores", "produce evaluation report".
  Reads web-bench-results.jsonl, computes statistics by category/website/failure mode,
  and writes web-bench-report.md with pass rates, timing, token usage, and analysis.
  Does NOT execute or evaluate tasks — only aggregates existing results.
user-invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Generate WebBench Benchmark Report

Aggregate all results from `web-bench-results.jsonl` into a comprehensive markdown report.

## Input

- **Results file:** `web-bench-results.jsonl` — one JSON line per completed task
- **Result line schema:**
  ```json
  {
    "id": 42,
    "url": "https://acehardware.com",
    "category": "READ",
    "task": "Navigate to...",
    "score": 1.0,
    "verdict": "PASS",
    "reasoning": "Successfully extracted all specs",
    "error": null,
    "duration_ms": 34200,
    "tokens_used": {"input": 12450, "output": 3200},
    "timestamp": "2026-03-19T14:30:00Z"
  }
  ```

## Report Generation

Use Node.js to compute all statistics:

```bash
node -e "
const fs = require('fs');
const results = fs.readFileSync('web-bench-results.jsonl','utf-8').trim().split('\n')
  .filter(l => l.trim()).map(JSON.parse);

const total = results.length;
const passed = results.filter(r => r.verdict === 'PASS').length;
const partial = results.filter(r => r.verdict === 'PARTIAL').length;
const failed = results.filter(r => r.verdict === 'FAIL').length;
const totalScore = results.reduce((s, r) => s + r.score, 0);

// Timing
const totalDurationMs = results.reduce((s, r) => s + (r.duration_ms || 0), 0);
const avgDurationMs = total ? totalDurationMs / total : 0;

// Tokens
const totalInputTokens = results.reduce((s, r) => s + ((r.tokens_used || {}).input || 0), 0);
const totalOutputTokens = results.reduce((s, r) => s + ((r.tokens_used || {}).output || 0), 0);
const totalTokens = totalInputTokens + totalOutputTokens;

// By category
const byCat = {};
for (const r of results) {
  if (!byCat[r.category]) byCat[r.category] = [];
  byCat[r.category].push(r);
}

// By website (top failures)
const bySite = {};
for (const r of results) {
  if (!bySite[r.url]) bySite[r.url] = [];
  bySite[r.url].push(r);
}

// Failure modes
const blockers = {};
for (const r of results) {
  if (r.error) blockers[r.error] = (blockers[r.error] || 0) + 1;
}

const catStats = {};
for (const [cat, rs] of Object.entries(byCat)) {
  catStats[cat] = {
    total: rs.length,
    passed: rs.filter(r => r.verdict === 'PASS').length,
    score: rs.reduce((s, r) => s + r.score, 0) / rs.length
  };
}

const siteFailures = Object.entries(bySite)
  .map(([site, rs]) => [site, rs.filter(r => r.verdict === 'FAIL').length])
  .sort((a, b) => b[1] - a[1]).slice(0, 20);

console.log(JSON.stringify({
  total, passed, partial, failed,
  totalScore, avgScore: total ? totalScore / total : 0,
  totalDurationMs, avgDurationMs,
  totalInputTokens, totalOutputTokens, totalTokens,
  byCategory: catStats,
  bySiteFailures: Object.fromEntries(siteFailures),
  blockers
}, null, 2));
"
```

## Report Template

Write `web-bench-report.md` with this structure:

```markdown
# WebBench Benchmark Report

**Date:** {timestamp}
**Agent:** {agent identifier}
**Dataset:** Halluminate/WebBench
**Tasks evaluated:** {total} / 2454

---

## Overall Results

| Metric | Value |
|--------|-------|
| **Pass Rate** | {passed}/{total} ({pass_pct}%) |
| **Partial Rate** | {partial}/{total} ({partial_pct}%) |
| **Fail Rate** | {failed}/{total} ({fail_pct}%) |
| **Average Score** | {avg_score:.2f} / 1.0 |
| **Total Duration** | {total_duration_formatted} |
| **Avg Duration/Task** | {avg_duration_formatted} |
| **Total Tokens** | {total_tokens:,} ({input_tokens:,} input + {output_tokens:,} output) |
| **Avg Tokens/Task** | {avg_tokens:,} |

## Results by Category

| Category | Total | Pass | Partial | Fail | Pass Rate | Avg Score |
|----------|-------|------|---------|------|-----------|-----------|
| READ | ... | ... | ... | ... | ...% | ... |
| CREATE | ... | ... | ... | ... | ...% | ... |
| UPDATE | ... | ... | ... | ... | ...% | ... |
| DELETE | ... | ... | ... | ... | ...% | ... |
| FILE_MANIPULATION | ... | ... | ... | ... | ...% | ... |

## Timing Breakdown

| Category | Avg Duration | Min | Max |
|----------|-------------|-----|-----|
| READ | ... | ... | ... |
| CREATE | ... | ... | ... |
| ... | | | |

## Token Usage Breakdown

| Category | Avg Input Tokens | Avg Output Tokens | Avg Total |
|----------|-----------------|-------------------|-----------|
| READ | ... | ... | ... |
| CREATE | ... | ... | ... |
| ... | | | |

## Top Failure Modes

| Failure Mode | Count | % of Failures |
|-------------|-------|---------------|
| Auth required | ... | ... |
| CAPTCHA | ... | ... |
| Site unavailable | ... | ... |
| Navigation failure | ... | ... |

## Worst Performing Websites (by failure count)

| Website | Tasks | Failures | Failure Rate |
|---------|-------|----------|-------------|
| ... | ... | ... | ... |

## Best Performing Websites (by pass rate, min 3 tasks)

| Website | Tasks | Pass Rate | Avg Score |
|---------|-------|-----------|-----------|
| ... | ... | ... | ... |

## Sample Failures

{Show 5-10 representative failures with task description, what went wrong, and verdict reasoning}

## Methodology

- **Execution:** One task per session via agent-web-interface browser automation
- **Evaluation:** LLM-as-judge with structured rubric (PASS=1.0, PARTIAL=0.5, FAIL=0.0)
- **Scoring dimensions:** Navigation, Comprehension, Completeness, Accuracy, Confirmation
- **Infrastructure blockers** (auth, CAPTCHA, site down) scored as FAIL but flagged separately
```

## Output

- **File:** `web-bench-report.md` in working directory
- Report should be self-contained and readable without the raw JSONL data

## Guardrails

- Use the JSONL file as the sole source of truth — do not fabricate statistics
- Format all durations as human-readable (e.g., "2h 34m 12s" not "9252000ms")
- Format token counts with thousands separators
- Round percentages to one decimal place
- If results file has fewer than the expected total tasks, note this prominently in the report header
