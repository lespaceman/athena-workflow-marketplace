---
name: evaluate-task
description: >
  Evaluate whether a WebBench task was successfully completed using LLM-as-judge scoring.
  Triggers: "evaluate task", "score task", "judge result", "grade benchmark task".
  Examines the execution trace, final page state, and extracted data against the original
  task description. Produces a structured verdict (PASS/PARTIAL/FAIL) with reasoning.
  Does NOT execute browser actions — use execute-task for that.
allowed-tools: Read Write Edit
---

# Evaluate WebBench Task

Judge whether a completed task execution meets the success criteria defined in the original task description. This is a post-hoc evaluation — no browser interaction, only analysis of the execution trace and captured state.

## Input

You receive:

1. **Original task:** `{"id": 42, "url": "...", "category": "READ", "task": "Navigate to the news section and summarize..."}`
2. **Execution trace:** Actions taken, final URL, extracted data, blockers encountered, screenshots

## Scoring Rubric

### Verdict Scale

| Verdict | Score | Criteria |
|---------|-------|----------|
| **PASS** | 1.0 | Task fully completed. All requested information extracted or all requested actions performed. |
| **PARTIAL** | 0.5 | Task partially completed. Some but not all requirements met. Meaningful progress was made. |
| **FAIL** | 0.0 | Task not completed. No meaningful progress, wrong information, or blocked before starting. |

### Category-Specific Evaluation

#### READ Tasks
- **PASS:** All requested data was extracted accurately and completely
- **PARTIAL:** Some data extracted but incomplete (e.g., found the page but missed some fields)
- **FAIL:** Wrong data, wrong page, or no data extracted

#### CREATE Tasks
- **PASS:** Item was created as specified, confirmation visible
- **PARTIAL:** Creation started but not confirmed (e.g., form filled but not submitted)
- **FAIL:** Could not reach the creation form, or creation failed

#### UPDATE Tasks
- **PASS:** Data was modified as specified, change confirmed
- **PARTIAL:** Found the item but could not complete the modification
- **FAIL:** Could not find the item or reach the edit interface

#### DELETE Tasks
- **PASS:** Item was deleted and removal confirmed
- **PARTIAL:** Found the item and initiated deletion but could not confirm
- **FAIL:** Could not find the item or reach the delete action

#### FILE_MANIPULATION Tasks
- **PASS:** File downloaded with correct name/content
- **PARTIAL:** Download initiated but not verified
- **FAIL:** Could not locate or download the file

### Blocker Handling

If the execution trace contains blockers, evaluate based on the blocker type:

| Blocker | Verdict | Reasoning |
|---------|---------|-----------|
| Login required (no credentials) | FAIL | Infrastructure limitation — task requires auth |
| CAPTCHA | FAIL | Infrastructure limitation — cannot solve programmatically |
| Site down / 404 | FAIL | External dependency — site unavailable |
| Geo-restricted | FAIL | Infrastructure limitation — content not accessible |
| Paywall | FAIL | Infrastructure limitation — paid content |
| Pop-up could not be dismissed | PARTIAL or FAIL | Depends on whether task could proceed |

### Evaluation Dimensions

Score each dimension and use them to determine the overall verdict:

1. **Navigation (required):** Did the agent reach the correct page/section?
   - Correct site? Correct section? Correct page?

2. **Comprehension (required):** Did the agent understand what was being asked?
   - Did it attempt the right type of action? Did it target the right elements?

3. **Completeness (required):** Did the agent fulfill ALL parts of the task?
   - Multi-part tasks: each part must be addressed
   - Quantitative tasks: all requested data points must be present

4. **Accuracy (for READ tasks):** Is the extracted information correct?
   - Does it match what's visible on the page?
   - Are numbers, names, and details accurate?

5. **Confirmation (for WRITE tasks):** Is there evidence the action was performed?
   - Success message visible? Item appears in list? State changed?

## Evaluation Process

### Step 1: Parse the Task Requirements

Break the task description into discrete, verifiable requirements:

```
Task: "Navigate to the news section and summarize the headline and key points from the latest science policy update."

Requirements:
1. Navigate to the news section
2. Find the latest science policy update
3. Extract the headline
4. Extract key points
```

### Step 2: Check Each Requirement Against the Trace

For each requirement, determine if the execution trace shows it was fulfilled:

```
1. Navigate to news section → DONE (action 2: clicked "News", URL changed to /news)
2. Find latest science policy update → DONE (action 3: found article "New Science Policy...")
3. Extract headline → DONE (extracted: "New Science Policy Framework Announced")
4. Extract key points → NOT DONE (only headline extracted, no key points)
```

### Step 3: Determine Verdict

- All requirements met → **PASS**
- Some requirements met → **PARTIAL**
- No requirements met or fundamentally wrong approach → **FAIL**

### Step 4: Write Reasoning

Provide clear, structured reasoning:

```
Verdict: PARTIAL (0.5)
Reasoning: Agent successfully navigated to the news section and identified the correct article.
The headline was extracted accurately. However, the task also requested "key points" from the
article, which were not extracted. 3 of 4 requirements met.
```

## Output Format

Return a structured evaluation result:

```json
{
  "task_id": 42,
  "verdict": "PARTIAL",
  "score": 0.5,
  "reasoning": "Agent navigated correctly and extracted the headline, but missed the key points requirement. 3/4 requirements fulfilled.",
  "requirements_met": 3,
  "requirements_total": 4,
  "blocker": null
}
```

If a blocker prevented execution:

```json
{
  "task_id": 43,
  "verdict": "FAIL",
  "score": 0.0,
  "reasoning": "Task requires account login. No credentials available — infrastructure limitation.",
  "requirements_met": 0,
  "requirements_total": 3,
  "blocker": "auth_required"
}
```

## Guardrails

- **Be strict but fair.** A task that asks for 5 data points and delivers 4 is PARTIAL, not PASS.
- **Do not hallucinate success.** If the trace doesn't show evidence of completion, it didn't happen.
- **Separate agent failure from infrastructure failure.** Auth requirements, CAPTCHAs, and site outages are not agent failures — but they are still FAIL verdicts for scoring purposes. Note the distinction in reasoning.
- **Evaluate what was asked, not what was attempted.** A well-executed wrong approach is still a FAIL.
