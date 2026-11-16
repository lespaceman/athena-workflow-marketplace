# gg-v7 — ship a task end-to-end

"Good game" v7: from a pasted task to a raised PR, in an isolated worktree, with every stage committed as a revertible slice.

You are the conductor. This workflow does not reimplement grilling, TDD, issue tracking or auditing — it **chains existing Skills** in a fixed order, holds the user at exactly one checkpoint, and then runs to the PR on its own.

## Plugins

This workflow is authored against the plugins pinned in `workflow.json`, which is the source of truth for versions.

| Plugin | Skills used here |
|--------|------------------|
| `matt-pocock-skills` | `grill-with-docs`, `zoom-out`, `diagnose`, `tdd`, `handoff`, `workflow-handoff` |
| `clickup` | `clickup` |

## Project Context — placeholders

This workflow is project-agnostic. Every project-specific fact is a `{{PLACEHOLDER}}`. **Resolve every placeholder before Stage 4**, in this order:

1. The workflow input (the user's pasted task may state it).
2. The target repo's own instructions: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/agents/*.md`, `Makefile`, CI config, `package.json` scripts, `pyproject.toml`.
3. Otherwise, ask — folded into the Stage 2 grill batch, each with a recommended answer.

Never guess a placeholder. Record every resolved value in the run log's `## Project context` section; a value inferred from the repo (rather than stated by the user) also goes under "Assumptions made without asking". A placeholder that does not apply to this repo (no frontend, no test database) is recorded as `n/a`, and the steps that depend on it are skipped out loud.

| Placeholder | Meaning | Example |
|---|---|---|
| `{{BASE_BRANCHES}}` | Every long-lived branch a PR may target | `main`, `production` |
| `{{DEFAULT_BASE_BRANCH}}` | Base used when only one long-lived branch exists | `main` |
| `{{BASE_BRANCH}}` | The bare base branch confirmed for this run at Stage 0 | `main` |
| `{{ISSUE_TRACKER}}` | Where the task lives | ClickUp |
| `{{TRACKER_LIST_MAP}}` | Which list/project a new task goes to, by task nature | bug → Bugs; refactor/perf/debt → Tech Debts; else → Stories |
| `{{TRACKER_ID_PREFIX}}` | Prefix on task IDs in branches and commits | `CU` |
| `{{TRACKER_REVIEW_STATUS}}` | Status meaning "PR raised, ready for review" | `Review` |
| `{{TRACKER_WRITE_ROUTE}}` | How tracker writes are attributed to the user | MCP tools, or REST API with `{{TRACKER_API_KEY_ENV}}` |
| `{{TRACKER_API_KEY_ENV}}` | Env var holding the user's tracker API key, if the REST route is used | `CLICKUP_API_KEY` |
| `{{TRACKER_DEFAULT_ASSIGNEE}}` | Who new tasks are assigned to | the user |
| `{{BRANCH_NAME_FORMAT}}` | Mandatory branch name shape | `{{TRACKER_ID_PREFIX}}-<task-id>-<TYPE>-<description>` |
| `{{COMMIT_MESSAGE_FORMAT}}` | Mandatory commit subject shape | `{{TRACKER_ID_PREFIX}}-<task-id> <TYPE> Short imperative description` |
| `{{PR_TITLE_FORMAT}}` | Mandatory PR title shape | `[TYPE]:[<task-id>]: Title` |
| `{{PR_BODY_OPENER}}` | Required first words of the PR body | `This PR will` |
| `{{TYPE_PREFIXES}}` | Allowed change-type prefixes | FEAT / BUG / EN / UI / HOUSEKEEPING / REFACTOR / TEST / CONFIG |
| `{{SENSITIVE_DATA_EXAMPLES}}` | Concrete kinds of production data this domain holds | account numbers, mailboxes, customer IDs |
| `{{KNOWN_BASELINE_FAILURES}}` | Tests known to fail on a clean base branch | none |
| `{{KNOWN_FAILURE_DESELECTS}}` | pytest `--deselect` flags for those tests, derived from the line above | empty |
| `{{GATE_COMMANDS}}` | The repo's authoritative check list, if it defines one | `make check` |
| `{{STACK}}` | Stack(s) the change touches, selecting the gate below | Python/Django, TypeScript/Vite, Java |
| `{{PY_ENV_TOOL}}` | Python environment manager | poetry |
| `{{TEST_DB_CONTAINER}}` | Container hosting the shared local test database | `myapp-testdb` |
| `{{TEST_ENV_FLAGS}}` | Env vars the static checks and tests need to import settings offline | `PYTEST=1` |
| `{{REPOS_WITHOUT_NEW_TESTS}}` | Repos where Stage 4 authors no new tests | the frontend repo |
| `{{FRONTEND_TSCONFIGS}}` | TS project files to type-check explicitly | `tsconfig.app.json`, `tsconfig.node.json` |

## 0. Priority order

When rules conflict, resolve in this order. Never silently pick a lower tier.

```
Safety constraints  →  Failure protocol  →  Execution rules  →  Code rules  →  Style
```

## 1. Safety constraints (absolute — never override)

- **No production data** in code, tests, commits, PR bodies, the issue tracker, or any external system — even when the user supplies it. Substitute a placeholder and say so out loud. `{{SENSITIVE_DATA_EXAMPLES}}` are production data.
- **No code outside the explicit scope** of the task.
- **The user's requirements are final.** A sub-agent, reviewer or auditor may not overrule them. If a finding contradicts a stated requirement, surface it to the user — never quietly implement the reviewer's preference instead.
- **Irreversible actions stop for the user**, whatever the automation level. See the risk table in Stage 6.
- **No `Co-Authored-By`, no AI attribution** in any commit, PR body or comment.

## 2. Failure protocol

- If the work cannot be delivered to standard, **STOP**.
- State exactly what is missing and exactly what is needed to continue.
- Never ship a degraded result and call it done.
- **Five attempts at the same failing thing is the limit.** A failing check, a failing test, a non-reproducing measurement: on the fifth failure, stop, print the raw output, and ask the user. The audit loop has its own, narrower bound of **two** rounds (Stage 7) — the narrower bound always wins. Never re-run an identical failing call hoping for a different result — change approach, and count the attempt.

### Terminal markers

The run log (below) is the run tracker. The runtime ends a run only when the **last non-empty line** of the run tracker is a terminal marker:

- `<!-- WORKFLOW_COMPLETE -->` — written by Stage 8 alone, after the report.
- `<!-- WORKFLOW_BLOCKED: <reason> -->` — written by every stop that ends the session: a failure-protocol stop, a risk-table stop with no user present, a question unanswered for a full turn.

A stop with no marker keeps looping until `maxIterations`. Never quote a marker earlier in the file where it could become the last line by accident. When the runtime provides its own tracker file, use it as the run log; otherwise use `<scratchpad>/gg-run.md`.

## 3. Autonomy contract

**One stop, at the start.** Stage 2 grills the user until the requirements — and every unresolved placeholder — are unambiguous. After that, the run goes to the raised PR without asking for approval — no test-review gate, no pre-PR checkpoint — and reports once at the end. The exceptions are the safety constraints in §1 and the failure protocol in §2, which interrupt at any point.

**Visible but not interrupting.** Print the stage chart at every stage change so the user can see where the run is and interrupt if it goes wrong:

```
[0 isolate]→[1 task]→[2 grill]→[3 diagnose]→[4 tests]→[5 build]→[6 gate]→[7 audit]→[8 ship]
    ✓          ✓         ✓         skip         ✓       ▶ 3/5       ·        ·        ·
   4m         1m        18m                     12m     ▶ 41m
```

**Timestamp every stage.** At each stage change, take the time from `date '+%Y-%m-%d %H:%M:%S %Z'` (never estimate it) and append a row to the `## Timings` table in the run log:

```
| Stage | Start | End | Duration | Note |
|---|---|---|---|---|
| 0 isolate | 2026-01-05 09:02:11 UTC | 2026-01-05 09:06:40 UTC | 4m29s | baseline green |
```

Show each finished stage's duration under it in the chart. A stage re-entered (a gate re-run, a second audit round) gets its own row. Time spent waiting on the user in Stage 2 is noted as such, so it is not mistaken for work. The final report carries the whole table.

**Unattended runs.** If the runtime says no user is present, Stage 2 cannot run: write the questions you would have asked into the run log and end with `<!-- WORKFLOW_BLOCKED: requirements need the user -->`.

## 4. Execution principles

- **Isolate first, always.** Stage 0 is not optional. See Appendix A.
- **Commit in logical slices.** Never one giant commit at the end. Every commit is one idea, revertible alone. See Appendix B.
- **Parallelism is mandatory for independent work.** Decompose, write each sub-agent's scope down before spawning, launch them in one message, synthesize into one deduplicated result. Skipping it needs written justification — there is exactly one standing justification, in Appendix C, and it covers the implement stage only.
- **Never fabricate — verify against the repo.** Don't invent file paths, function names, APIs, config keys, migrations or commands. Confirm each against the codebase or official docs. "Unverified — check before use" beats a confident guess.
- **Use web search for anything current or unverified.** Unfamiliar library APIs, error-code semantics, CVEs, version changes. Treat training data as possibly stale. Cite the link when the fact is load-bearing.
- **Prove it, don't assert it.** When a claim can be tested in a scratchpad in under a minute, test it. A measured result outranks a plausible argument, and outranks a GitHub issue thread about an older version.
- **Ask with the tool.** When clarification is genuinely needed, use the runtime's question tool (`AskUserQuestion` on Claude Code) — batch related doubts into one call, recommend an option. Never assume, and never ask what the codebase can answer: fan out and read it.

## 5. The flow

```
0.  Isolate & Orient  → worktree + baseline suite state + scope map
1.  Task on record    → find or create the tracker task, silently
2.  Requirements      → grill until the ask is unambiguous      → ONLY STOP
3.  Diagnose          → [PERF ONLY] evidence-first root cause
4.  Tests first       → tests written and committed, no approval gate
5.  Implement         → atomic commits, pushed as they land
6.  Gate              → the stack's real check list              → HARD GATE
7.  Audit             → one combined independent lane            → HARD GATE
8.  Ship              → raise the PR, close the loop on the tracker, report once
```

Keep a visible todo list of these stages alongside the chart. Stages 6 and 7 are hard: they block on being green, not on the user.

---

## Stage 0 — Isolate & Orient

**Invoking this workflow *is* the instruction to work in a worktree.** Enter one before touching anything.

1. **Confirm the base branch.** If `{{BASE_BRANCHES}}` has more than one entry, ask which one this work belongs on — the wrong base means the PR targets the wrong lane and the diff is noise. This is a requirements question, so it belongs in the same batch as Stage 2. Otherwise use `{{DEFAULT_BASE_BRANCH}}`. Record the answer as `$BASE` (e.g. `origin/main`); Stage 6 and Stage 8 both need it.
2. **Create the worktree.** On Claude Code, `EnterWorktree` takes only a `name` or a `path` — it has **no base-ref parameter**, and branches from `origin/<default-branch>` by default. So:
   - base *is* the default → `EnterWorktree` with a name in `{{BRANCH_NAME_FORMAT}}`.
   - base is anything else, or the runtime has no worktree tool → create it first, then enter it by path. **The branch and the directory take the same name** (Appendix A treats that as an invariant):
     ```bash
     NAME="<name in BRANCH_NAME_FORMAT>"
     git worktree add -b "$NAME" ".claude/worktrees/$NAME" "origin/<base-branch>"
     ```
     then `EnterWorktree` with `path: .claude/worktrees/<NAME>` (or `cd` into it).
   Never ask the base-branch question and then ignore the answer. Record both the bare branch name and the `origin/`-prefixed ref in the run log: Stage 6's diff needs the prefixed form, `gh pr create --base` needs the bare one.
3. **Verify the toolchain, don't trust the wrapper.** Before the baseline, resolve the real interpreter — see Appendix A. A package-manager wrapper inside a worktree can silently resolve to a bare system interpreter.
4. **Record the baseline.** Run the suite (or its narrowest relevant slice) and note green/red *before* any change. Keep the raw output in the main thread. If the baseline is red beyond `{{KNOWN_BASELINE_FAILURES}}`, or the suite can't run, **stop under §2** — print the raw output and ask the user whether to continue. This is not negotiable under the autonomy contract: on a red tree Stage 6's "zero errors" is unreachable, the five-attempt budget burns on someone else's failure, and the run ends with a PR raised on top of it. A pre-existing failure must never be silently inherited or later blamed on this change.
5. **Map the scope in parallel.** Fan out `Explore` sub-agents (or load `zoom-out` for one unfamiliar module) over the likely modules, conventions and test surfaces, so file dumps stay out of the main thread. Aggregate their conclusions. The same fan-out resolves the Project Context placeholders from the repo's own docs.
6. **Check for other live runs.** `git worktree list` shows every worktree on the repo. Other runs may share one local database, one broker and one set of ports, so a concurrent run can fail this run's gate for reasons unrelated to the change — a fast connection-refused or database-dropped failure is a collision, not a regression. Note what is live in the run log, and when a gate failure matches that signature, say so and do **not** spend an attempt on it.
7. **Open the run log.** Create the run log (see §2 Terminal markers) and write the task, the worktree path, the base branch, the resolved Project Context and the baseline result into it. Every stage appends. Format in Appendix B.

## Stage 1 — Task on record

**Find it, don't ask for it. Create it if it doesn't exist. No prompts.**

1. **Search first** in `{{ISSUE_TRACKER}}` for an existing task matching the ask. If one exists, take its ID and link — they drive the branch name, commit messages and PR title.
2. **If none exists, create one**, choosing the list from `{{TRACKER_LIST_MAP}}` by the task's nature, assigned to `{{TRACKER_DEFAULT_ASSIGNEE}}`. For ClickUp, load `clickup` first — it owns the tool conventions. Skip interactive previews and confirmations — this stage is silent by design.
3. **Report the link** in the stage chart line, then move on.

A wrong title or list is editable afterwards; a stop is not recoverable. Ownership, attribution and formatting rules: Appendix D. If the tracker is unreachable or unauthorized on this machine, say so, record it as an assumption, and continue with a local task ID only if the user's conventions allow one — otherwise stop under §2 naming the server.

## Stage 2 — Requirements — THE ONLY STOP

Load `grill-with-docs` for its interview only — do not create or edit `CONTEXT.md` or ADRs unless the user asks, since those files would land in the PR outside the task's scope — and interrogate until the requirements are unambiguous — edge cases, inputs and outputs, what is explicitly out of scope. This is the one stage that holds the user, because it is the one input that cannot be derived. Everything after it runs autonomously, so a misread here is expensive: it freezes the tests against the wrong target and is not caught until the PR.

Push harder than feels comfortable. One question at a time, each with a recommended answer, and **anything answerable from the codebase gets answered by reading the codebase instead of asking** — fan out sub-agents to read while the conversation continues.

Fold the Stage 0 base-branch question and every still-unresolved placeholder into the same batch.

**Design note.** For anything beyond a tiny edit, once *what* is settled, record *how* in two sentences before writing tests: the chosen approach, the surfaces it touches, and how to roll it back. Commit it. This catches "right what, wrong mechanism" before the tests freeze the target.

**Record the requirements verbatim** in the run log. §1 makes them final; the audit in Stage 7 checks the delivered work against that record.

## Stage 3 — Diagnose (performance work only)

**Only when the task is a performance, latency or resource problem.** Skip entirely for features and bugs — say "skip" in the chart.

The rule: **never optimise from a hypothesis.** Produce an evidence-backed root-cause report first, using `diagnose` for the reproduce-and-measure loop. Present the ranked report, state which bottlenecks are in scope based on the Stage 2 requirements, and continue — no second stop. No optimisation code during this stage; measurement scripts live in the scratchpad, not the repo.

The eleven-step protocol and its discipline rules: Appendix E.

## Stage 4 — Tests first

Load `tdd` to write the tests that encode Stage 2. **Tests only — no implementation.** Commit them as their own slice, and say in the message that they are expected to fail.

There is **no approval gate here** — the autonomy contract removed it. The tests are still the contract: once committed, they are the definition of done, and Stage 5 does not get to change them to make the implementation pass. If the tests turn out to be wrong, that is a requirements failure — stop under §2 and say so.

**No-new-tests exception.** In `{{REPOS_WITHOUT_NEW_TESTS}}`, no new tests are authored and this stage is skipped. The existing suite still runs in Stage 6 as a regression check.

## Stage 5 — Implement (against frozen tests)

Implement fully — real code, no placeholders, edge cases handled — until the Stage 4 tests pass. Keep changes surgical: every changed line traces to the task.

**Code rules (non-negotiable):**

- **No comments. No docstrings.** Module, class and function docstrings all count. Not "for the module header", not "to explain the numbers", not "because the sibling file has one". Rationale goes in the commit message. **But never delete a pre-existing docstring or comment** unless the user asks — this rule governs what you add, not what is already there.
- **No leading-underscore prefixes** on function or method names.
- Clean, meaningful, descriptive variable names.
- SOLID and OOP where it earns its place. Small, single-purpose classes and functions.
- Prefer composition over inheritance. Depend on abstractions at boundaries — I/O, external services, persistence — not everywhere.
- No speculative abstractions, no single-implementation interfaces unless a test genuinely needs one, no factories or layers for show.
- Use a design pattern only when it solves a real problem here. **Name it** if you use one.
- After the code of each slice, give 2–3 lines on the key design choices.
- Match the repo's existing style **except** where it conflicts with these rules. These rules win for code you write; the sibling file is not a precedent. They are not a licence to strip what already exists — see the docstring rule above.

**Commit granularity is the deliverable here, not an afterthought.** Split into vertical slices, each independently verifiable. As each slice goes green: commit, push, append to the ledger in the run log. A local-only commit does not survive a dead session.

**One writer.** This stage does not fan out — see the standing justification in Appendix C.

## Stage 6 — Gate (stack-aware) — HARD GATE

Detect the stack (`{{STACK}}`) and run its full check list. **Zero errors before you proceed** — never push hoping CI catches it. Raw output stays in the main thread; it is the proof. Fix any failure and re-run the **full** list, counting attempts against the five-attempt limit in §2.

**If the repo defines its own gate (`{{GATE_COMMANDS}}` — a project `CLAUDE.md`, a Makefile target, a CI config), that gate is authoritative — run its exact command list.** Check for one first. The stack gates below apply only where the repo defines none. **Do not create one** — writing a gate file into the target repo is out of scope for every task unless the user asks.

### Python (`{{PY_ENV_TOOL}}`) — one script, all checks, zero errors

**Substitute every placeholder, write the result to `<scratchpad>/gate.sh`, and run `bash <scratchpad>/gate.sh`.** Do not split it across several Bash calls and do not paste it into an interactive shell. Shell state does not survive between tool calls, so `$VENV` and `$BASE` set in one call are empty in the next — and an empty `$BASE` makes `git diff "$BASE"...HEAD` resolve as `HEAD...HEAD`, which returns zero files, prints "no python changes" and exits 0 on a branch with dozens of changed files. That is the fake pass this whole section exists to prevent. `{{BASE_BRANCH}}` is the bare base branch confirmed at Stage 0; `{{TEST_ENV_FLAGS}}` becomes the empty string when the repo needs none. `{{KNOWN_FAILURE_DESELECTS}}` becomes one `--deselect <node-id>` per test in `{{KNOWN_BASELINE_FAILURES}}`, or the empty string — the only failures the gate may ignore are the ones the user accepted at Stage 0. Drop the database block when `{{TEST_DB_CONTAINER}}` is `n/a`; drop a check the repo does not use (no mypy, no pre-commit) and record that.

```bash
set -u
[ -f "$0" ] || { echo "GATE RED: run as a file, not piped"; exit 1; }
grep -q '{''{' "$0" && { echo "GATE RED: unsubstituted placeholder in $0"; exit 1; }

BASE_BRANCH="{{BASE_BRANCH}}"
BASE="origin/$BASE_BRANCH"
git rev-parse --verify "$BASE" >/dev/null 2>&1 || { echo "GATE RED: base $BASE does not exist"; exit 1; }

MAIN=$(git rev-parse --path-format=absolute --git-common-dir | sed 's|/\.git$||')
VENV=$(cd "$MAIN" && poetry env info --path)
[ -n "$VENV" ] && [ -x "$VENV/bin/pytest" ] || { echo "GATE RED: no project venv resolved"; exit 1; }
"$VENV/bin/python" --version
"$VENV/bin/pytest" --version
[ -f .env ] || { [ -f "$MAIN/.env" ] && cp "$MAIN/.env" .env; }

PG_CONTAINER="{{TEST_DB_CONTAINER}}"
export DB_HOST=localhost DB_PORT=5432 DB_USERNAME=postgres
export DB_PASSWORD=$(docker exec "$PG_CONTAINER" printenv POSTGRES_PASSWORD)
export DB_NAME="gg_$(basename "$PWD" | tr 'A-Z' 'a-z' | tr -c 'a-z0-9\n' '_' | cut -c1-40)"
case "$DB_NAME" in gg_|gg_postgres|gg_test*) echo "GATE RED: refusing DB_NAME=$DB_NAME"; exit 1;; esac
docker exec "$PG_CONTAINER" psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 \
  || docker exec "$PG_CONTAINER" psql -U postgres -c "CREATE DATABASE \"$DB_NAME\"" \
  || { echo "GATE RED: could not create $DB_NAME"; exit 1; }
echo "DB_NAME=$DB_NAME (workers use test_${DB_NAME}_gwN)"
LOCKS=$(docker exec "$PG_CONTAINER" psql -U postgres -tAc "SHOW max_locks_per_transaction")
[ "${LOCKS:-0}" -ge 512 ] || { echo "GATE RED: max_locks_per_transaction=$LOCKS, -n auto needs >= 512"; exit 1; }

TIMINGS=""
stage() {
  local name="$1"; shift
  local start=$(date +%s)
  echo "=== $name  start $(date '+%H:%M:%S')"
  "$@"; local rc=$?
  local secs=$(( $(date +%s) - start ))
  echo "=== $name  end $(date '+%H:%M:%S')  ${secs}s  exit=$rc"
  TIMINGS="${TIMINGS}$(printf '%-12s %6ss  exit=%s' "$name" "$secs" "$rc")\n"
  return $rc
}
summary() { printf '\n--- gate timings ---\n%b' "$TIMINGS"; }

CHANGED=$( { git diff --name-only --diff-filter=ACMR "$BASE"...HEAD -- '*.py'
             git diff --name-only --diff-filter=ACMR -- '*.py'
             git diff --cached --name-only --diff-filter=ACMR -- '*.py'; } | sort -u )
TOUCHED=$(git diff --name-only "$BASE"...HEAD | wc -l | tr -d ' ')

stage ruff "$VENV/bin/ruff" check . || { summary; echo "GATE RED: ruff"; exit 1; }

if [ -n "$CHANGED" ]; then
  stage pylint env {{TEST_ENV_FLAGS}} "$VENV/bin/pylint" --rcfile="$PWD/pyproject.toml" $CHANGED || {
    summary; echo "GATE RED: pylint findings"; exit 1; }
elif [ "$TOUCHED" -eq 0 ]; then
  echo "GATE RED: $BASE yields an empty diff — the base is wrong, not the branch clean"; exit 1
else
  echo "no python changes ($TOUCHED non-python files touched)"
fi

stage mypy env {{TEST_ENV_FLAGS}} PYTHONPATH="$PWD" "$VENV/bin/mypy" . --cache-dir="$PWD/.mypy_cache" \
  || { summary; echo "GATE RED: mypy"; exit 1; }
stage pre-commit "$VENV/bin/pre-commit" run --all-files || { summary; echo "GATE RED: pre-commit"; exit 1; }
stage pytest env {{TEST_ENV_FLAGS}} "$VENV/bin/pytest" -n auto -p no:cacheprovider {{KNOWN_FAILURE_DESELECTS}} \
  || { summary; echo "GATE RED: pytest"; exit 1; }

summary
echo "GATE GREEN"
```

The script assumes Poetry, ruff, pylint, mypy, pre-commit, pytest-xdist, a Dockerised Postgres, pylint config in `pyproject.toml`, and that the project's settings read the test database from `DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD` and `DB_NAME`. Confirm each against the repo at Stage 0; if settings read other names (`DATABASE_URL`, `POSTGRES_*`), export those instead — otherwise the per-run database guarantee silently stops holding and concurrent runs share one test database. For a different `{{PY_ENV_TOOL}}`, replace only the `VENV=` line with that tool's command for the project environment path, run from `$MAIN`. Verify each tool exists in `$VENV/bin` before relying on it.

Read the result from the **exit status and the `GATE GREEN` line**, not by eyeballing the output: a clean mypy prints `Success: no issues found in N source files` followed by a long tail of `note: ... [annotation-unchecked]` lines, which are not failures. Never pipe mypy through `grep " error: "` in an automated run — `grep` exits 1 on clean output and inverts the result of the whole gate.

Load-bearing details, each of which has been got wrong before:

- **The base is substituted, then verified.** A hardcoded `main` diffs a branch cut from another lane against the wrong ref; an *unset* base silently diffs nothing at all. Both end in pylint not running. `git rev-parse --verify` plus the `TOUCHED` check close both.
- **Never `cmd $CHANGED || echo "no python changes"`.** pylint exits non-zero on *any* finding, so the `||` branch fires and the one check whose purpose is to find problems reports "nothing to check" and returns success.
- **`mypy` repo-wide, with `PYTHONPATH` and a per-worktree cache dir.** Without them, plugin stubs (e.g. django-stubs) load the *main checkout's* modules from the venv `.pth`. `$PWD/.mypy_cache` is already per-worktree and normally gitignored — do not invent a new cache name, it will show up untracked and get committed by `git add -A`. Narrowing mypy to single files can internal-error on framework stubs, so keep it repo-wide.
- **Every binary comes from `$VENV`, `pre-commit` included.** Ambient `PATH` resolution can pick a system copy — the exact mechanism that fakes a pass.
- **One script, not several calls.** See the warning above.
- **Every run gets its own database, enforced.** `DB_NAME` is derived from the worktree folder, created in the shared Postgres if missing, and the gate refuses a default or empty name. Two runs on the same name drop each other's databases mid-run, which looks exactly like a code bug. With `-n auto`, pytest-django makes `test_<DB_NAME>_gw0..N`, one per worker, all scoped to this run.
- **Static checks first, pytest last.** Static checks fail in minutes; pytest is the long stage. pre-commit can rewrite files (formatters), so it also has to run before the tests see the code.
- **pytest runs `-n auto`** when the repo already supports xdist; check CI config first. Without xdist, drop `-n auto` and the lock check.
- **The test Postgres needs `max_locks_per_transaction >= 512` under xdist.** With migrations disabled, every worker creates all tables in one transaction, and several at once overflow the default 64 (`out of shared memory`). Raising it needs `ALTER SYSTEM SET max_locks_per_transaction = 512` and a container restart — which drops every open connection on the shared container, so check `pg_stat_activity` for other runs first and ask the user if any are live.
- **Every check is timed.** `stage` prints start, end and seconds per check and the gate ends with a timings table, green or red. Copy that table into the run log.
- **pylint must use the repo's own config.** `--disable=all --enable=<a few>` discards `[tool.pylint]` and is nearly blind. Scope to changed files so pre-existing findings in frozen files stay out of the way without hiding anything in code you touched.
- **Static checks may reach the network.** If importing settings fetches remote secrets, offline that is a connection error — which is what `{{TEST_ENV_FLAGS}}` exists to prevent on the mypy, pylint and pytest lines. If those flags also disable migrations, `makemigrations --check` is not trustworthy under them — read migration files off disk instead.

### TypeScript / Vite frontend

No new tests are authored where `{{REPOS_WITHOUT_NEW_TESTS}}` says so, but the existing suite is a regression check. Verify each script exists in `package.json` first:

```bash
npx eslint .                                   # read-only; NOT a lint script that runs --fix
npx tsc -p <each of FRONTEND_TSCONFIGS> --noEmit
npm run test
npm run build
git status --porcelain --untracked-files=no    # must be empty
```

- **`npx tsc --noEmit` alone can type-check nothing.** When `tsconfig.json` is a solution file — `"files": []` plus project `references` — tsc without `-p` or `-b` ignores the references, checks 0 files, and exits 0, so it reads as a pass. `vite build` is esbuild and does not type-check either. Run tsc against each of `{{FRONTEND_TSCONFIGS}}` explicitly.
- **`--untracked-files=no` is required.** A plain `git status --porcelain` reports `?? .claude/worktrees/` when `.gitignore` does not cover it, so the check would fail on an untouched tree. Restricting it to tracked files still catches the real hazard: a lint or build step that rewrote your source.
- **Lint read-only.** If the repo's lint script is `eslint --fix`, a verification gate that mutates source leaves edits outside the Stage 5 slice discipline and outside the Stage 7 diff. Fix findings as their own commit.

Repo-level `CLAUDE.md` and `.claude/rules/` are authoritative for conventions. Never skip git hooks with `--no-verify`.

### Spring / Java (`pom.xml`, `build.gradle`)

```bash
mvn -q clean verify          # or: ./gradlew clean build
```

If formatting and linting are separate goals rather than bound into the build, run them too (`mvn spotless:check checkstyle:check`, `./gradlew spotlessCheck check`).

### Anything else

Find the project's own commands (README, Makefile, `package.json` scripts, CI config) and run those. Never invent a command; verify it exists first.

### Draft the outputs before leaving this stage

The gate being green is not the end of Stage 6. Stage 7 audits the PR body and the tracker comment, so they have to exist first. Write into the run log:

- the PR title, in `{{PR_TITLE_FORMAT}}` form;
- the full PR body, starting `{{PR_BODY_OPENER}}`, **200 words maximum** — what it does, the root cause in a sentence or two, the measured result, the tracker link. No tables, no revert ledger, no method sections. Measured facts only, no projected or estimated figures. No AI attribution.
- the tracker comment text, plain-text safe and also within 200 words.

Stage 8 posts these verbatim. It does not compose anything.

### Risk table — these stop for the user regardless of autonomy

| Action | Risk | Behaviour |
|---|---|---|
| Migration, or anything writing the shared local DB | high | stop and confirm — a worktree shares the database with every other worktree |
| Force-push, history rewrite, branch deletion | high | stop and confirm |
| Anything with an external side effect already emitted (webhook, email, third-party API call) | high | roll forward, never revert; say so |
| Creating or moving the tracker task | low | silent, by design (Stage 1) |
| Raising the PR | low | silent, by design (Stage 8) |
| Reading, searching, measuring in a scratchpad | low | silent |

With no user present, a high-risk stop ends the run with `<!-- WORKFLOW_BLOCKED: <the action awaiting confirmation> -->`.

## Stage 7 — Audit — HARD GATE

**Only once Stage 6 is fully green.**

**One combined audit lane, in a fresh context.** The agent that wrote the code is the worst reviewer of it: it re-derives the same assumptions and confirms itself. Spawn the auditor fresh, hand it the diff, the Stage 2 requirements record, the resolved Project Context and the **drafted** outputs — the PR title and body, the tracker comment, any generated document — and tell it to look for reasons the change is *wrong*.

A single "review this" agent tends to find one class of problem and stop, so the prompt **must demand a per-category verdict**. Every category reports either a finding or an explicit "nothing found":

1. **Correctness** — acceptance criteria vs Stages 2 and 4, regressions, brittle tests, coupling, leftover debug output, docs/migration/config drift.
2. **Security** — no secrets committed; authn/authz enforced on every changed endpoint; new dependencies justified and from a trusted source; for payment or sensitive-data changes, input validation and no sensitive data in logs.
3. **Outputs** — the drafted PR title and body, the tracker description and the drafted comment, and any generated document: no production data, no AI attribution, no projected or estimated figures, PR body within 200 words and starting `{{PR_BODY_OPENER}}`, tracker comment within 200 words and plain-text safe, PR title matching `{{PR_TITLE_FORMAT}}`. If a draft is missing, the audit **fails** — it does not return "nothing found".
4. **Requirement fidelity** — does the delivered work match the Stage 2 record, verbatim? Flag anything added, dropped or reinterpreted.

**Verify before reporting.** Each candidate finding must survive an honest attempt to refute it. A finding that survives is worth the user's attention; one that doesn't is noise and is dropped.

**Resolve, don't defer.** Fix blocking findings, re-run the relevant Stage 6 checks, re-audit. **Bounded at 2 rounds** — narrower than §2's five, and the narrower bound wins. If round 2 is not clean, stop under §2 and report. A security finding blocks the PR and is never downgraded to a follow-up. Only the user may waive a specific named finding, out loud.

**A finding that contradicts a stated requirement is not implemented.** §1 makes the user's requirements final: surface the disagreement in the final report instead.

Each fix is its own commit — a finding and its fix revert as a pair.

## Stage 8 — Ship

Automatic. No checkpoint.

1. Push any remaining commits.
2. Open the PR with `gh`, posting the title and body audited in Stage 7 **verbatim**. Compose nothing here — if a draft is missing, that is a Stage 6 failure, so go back rather than writing one now.
   ```bash
   gh pr create --base "$BASE_BRANCH" --title "$PR_TITLE" --body-file "$PR_BODY_FILE"
   ```
   `--base` takes the **bare** branch name (`main`) — never `origin/main`, which is not a valid base and will fail. Attach screenshots if applicable; everything else was fixed at draft time.
3. **Close the loop on the tracker:** move the task to `{{TRACKER_REVIEW_STATUS}}` and comment with the PR link, plain text — see Appendix D. Only after the PR exists; the status change means "ready for review".
4. **Clean up what the run created.** Only after the PR exists, and only things this run made:
   - **Test databases.** Drop the gate's `DB_NAME` and every database derived from it (`test_<DB_NAME>`, `test_<DB_NAME>_gwN`). List them first and drop exactly that list; never drop by a pattern another run could match:
     ```bash
     docker exec {{TEST_DB_CONTAINER}} psql -U postgres -tAc \
       "SELECT datname FROM pg_database WHERE datname = '<DB_NAME>' OR datname ~ '^test_<DB_NAME>(_gw[0-9]+)?$'"
     ```
     with `<DB_NAME>` taken from the gate output's `DB_NAME=` line (shell variables from the gate do not survive), then `DROP DATABASE IF EXISTS "<name>" WITH (FORCE)` for each listed name. A later review-fix gate recreates them.
   - **Scratch and stray files.** Delete mocks, screenshots, browser-tool output folders, throwaway scripts and anything else the run wrote outside the commits, in the worktree and the scratchpad. Keep the run log and the gate output files; they are the run's record. Run `git status --short` afterwards and confirm nothing untracked is left in the worktree.
   - The worktree and branch stay (see "Running the flow").
5. **Report once.** The PR link, the worktree path, the gate result with its timings table, the audit result per category, the stage timings table, what was cleaned up, every assumption made without asking (including every placeholder inferred rather than stated), and anything left undone with the reason. **gg.**
6. Write `<!-- WORKFLOW_COMPLETE -->` as the last line of the run log.

---

## Running the flow

- **Merging and deploying are the user's call**, always. Raise the PR; don't merge it. If merging the PR *is* the deploy, say so out loud and wait.
- If the user says "skip the tracker task" or "I already grilled this", honor it and confirm the skip out loud so nothing is silently dropped. The §1 safety constraints and the Stage 7 security category are never skipped on a change touching endpoints, auth, secrets or dependencies.
- **Running out of context?** Load `workflow-handoff` (or `handoff` for a plain summary). The run log already holds the worktree path, branch, last-pushed commit, stage, ledger, Project Context and requirements — that file is the handoff. Because Stage 5 pushes each slice, the remote holds the work.
- If a stage's underlying Skill isn't available, say so and do that stage's work inline rather than failing the whole flow.
- When you finish, **leave the worktree in place** (`ExitWorktree` with `action: "keep"` on Claude Code). The PR branch lives there.

---

## Appendix A — Working in a worktree

All work happens in an isolated git worktree. The user's main checkout is never touched, never left dirty, and stays usable for other work while this task runs.

**Why this is non-negotiable.** A long task leaves the main checkout dirty for its whole duration; a failed or abandoned task leaves nothing to clean up; the user and other agents can keep working in their own worktrees on the same repo; and isolation is at the **filesystem** level, not just the branch level, so nothing can half-apply into the wrong tree.

**Entering.** Invoking this workflow is the explicit instruction to use a worktree; note it out loud once, then proceed. Confirm the base branch first (Stage 0). The worktree tool cannot act on a non-default base: its only parameters are `name` and `path`; the base ref comes from a runtime *setting*, which a workflow must not change. So base is the default → enter by `name`; base is anything else → `git worktree add -b "$NAME" ".claude/worktrees/$NAME" "origin/<base>"` first, then enter by `path`. Creating by `name` is barred once you are already inside a worktree; entering by `path` needs the path to appear in `git worktree list`, which `git worktree add` supplies.

**The worktree name is the branch name.** The worktree tool names the new branch after the worktree, so the name must already satisfy `{{BRANCH_NAME_FORMAT}}`, with the type from `{{TYPE_PREFIXES}}`. Match the format's case exactly; a mis-cased name produces a branch that does not match the convention and the PR title will not line up with it.

Do not prune or remove other worktrees. They belong to other tasks and sessions.

**Filesystem isolation is not runtime isolation.** Two worktrees of the same repo still share whatever the *environment* points at: the same local database and its migration state, the same broker and queues, the same ports, the same `.env`, cloud credentials and remote services. Migrations bite hardest: applying one in this worktree changes the database every other worktree is using — which is why a migration is high-risk in the Stage 6 table. Before mutating shared state: **check what is live and tell the user what you found**, then confirm. Say which worktrees exist, whether the main checkout is dirty, and exactly what you are about to touch.

**The toolchain trap — it fakes a pass.** A package-manager wrapper may not resolve the project environment inside a worktree. With Poetry, `poetry env info` run from a fresh worktree can report `Virtualenv Path: NA` and fall back to a bare system interpreter with none of the project's libraries — so `poetry run pytest` and `poetry run pylint` do not run the project's tools, and pylint can still report a passing score. **A fake pass on a hard gate is the worst failure this flow can have.** Derive the real environment from the main checkout instead:

```bash
MAIN=$(git rev-parse --path-format=absolute --git-common-dir | sed 's|/\.git$||')
VENV=$(cd "$MAIN" && poetry env info --path)
```

Verify it before trusting it — the tools in `$VENV/bin` must exist and must not be a bare system interpreter. If `$VENV` is empty, stop under §2. Gitignored env files are absent in a fresh worktree: copy `.env` from the main checkout rather than inventing values, and never commit it.

**Leaving.** Default: keep the worktree — the PR branch lives there; removing it while the PR is open is hostile. Remove only when the work is abandoned or the user asks; if removal refuses because of uncommitted changes or unmerged commits, **show the user what it listed and confirm** before discarding. Don't exit proactively at the end of a successful run — report the worktree path and the PR link. The run log records the worktree path alongside the branch and last-pushed SHA, so a fresh session doesn't start editing the main checkout and produce a split-brain task.

## Appendix B — Commit granularity and the run log

The goal: **any single decision in this task can be undone without unpicking the rest.** If one slice was wrong, `git revert <sha>` fixes it cleanly and leaves everything else standing.

**One commit = one logical change.** Not one file, not one day of work, not "the feature". One idea describable in a single sentence without "and". Sizing heuristics, most reliable first:

- **The sentence test.** If the message needs "and" to be honest, split it.
- **The revert test.** If reverting it would break something unrelated in the same commit, split.
- **1–5 files.** A smell test, not a law. A commit averaging 15+ files is almost never one idea.

**What never shares a commit:**

| Keep separate | Why |
|---|---|
| Tests and the implementation they test | Tests are the frozen contract from Stage 4. Reverting an implementation must not silently delete its test |
| Refactor and behaviour change | Move code *or* change what it does, never both |
| Config/infra and application code | Config often needs reverting alone, on a different schedule |
| Migrations and the code that uses them | Migrations may be irreversible in prod; the code around them usually isn't |
| Dependency bumps and feature work | A bad bump should revert without losing the feature |
| Formatting/lint-only churn | Otherwise it buries the real change |
| An audit finding's fix | Pair it with its finding so one thing can be verified |

**Order within a task** — the tree is coherent at every commit: (1) design note (Stage 2), (2) tests (Stage 4, expected to fail — say so), (3) implementation slices (Stage 5), each turning some tests green, (4) audit fixes (Stage 7), one per finding.

**Push as you go.** A local-only commit is not recoverable. Commit and push each slice as it goes green.

**Message format:** `{{COMMIT_MESSAGE_FORMAT}}`, type from `{{TYPE_PREFIXES}}`. Hard rules: no `Co-Authored-By` and no AI attribution of any kind; no secrets; no production data, even in a test fixture; remove temporary instrumentation before committing; the body carries the *why* (the code carries no comments); measured facts only.

**The run log.** The ledger lives in a file, not in context and not in the PR body — context is the first thing a long run loses, and a ledger table breaks the 200-word PR ceiling on its own. Create it at Stage 0, append at every stage:

```markdown
# gg run — <task>
worktree:  <path>          base branch: <bare> / <origin/-prefixed>
task:      <id> <link>     baseline: <green/red + raw summary>

## Project context
| Placeholder | Value | Source (input / repo file / user) |

## Requirements (Stage 2, verbatim — final per §1)

## Timings
| Stage | Start | End | Duration | Note |

## Revert ledger
| # | SHA | Stage | Slice | Safe to revert alone? |
|---|-----|-------|-------|----------------------|
| 1 | a1b2c3d | 2 | Design note | yes |
| 2 | e4f5g6h | 4 | Tests for refund idempotency (red) | yes — reverts the contract too |
| 3 | i7j8k9l | 5 | Idempotency key on refund request | yes |
| 4 | m0n1o2p | 5 | Migration: unique index on key | **no — run the down migration first** |
| 5 | q3r4s5t | 7 | Fix: authz check on refund endpoint | yes |

## Assumptions made without asking

## Drafts (Stage 6)
```

Flag every slice that is **not** independently revertible and say what has to happen first. Migrations, data backfills, and anything that has already emitted an external side effect belong in that category — those are **rolled forward, not reverted**, and the ledger says so. The final report summarises this file; it does not paste it. The terminal marker, when written, is the file's last line.

## Appendix C — Fanning out to sub-agents

Parallelism is mandatory for independent work. Sequential work that could have run concurrently is wasted wall-clock, and sub-agent context isolation keeps file dumps and dead ends out of the main thread.

**Procedure, before any multi-part stage:** (1) decompose into every independent workstream; (2) write each sub-agent's scope down in the run log, one line each; (3) launch them all in one message — one per turn does not run concurrently, the most common way parallelism is silently lost; (4) synthesize into one deduplicated result yourself. Three to five at a time; more and synthesis becomes the bottleneck.

**Delegate:** scope mapping and placeholder resolution (Stage 0); "where is X handled?" during the grill (Stage 2); independent measurement lanes (Stage 3); prior-art and convention hunting; the audit (Stage 7, must run in a context that did not author the code); docs/API lookups for an unfamiliar library.

**Never leaves the main thread:** gate output (it is the proof, not to be summarised second-hand by an agent with an incentive to report success); the commits; the one stop.

**The standing justification for not fanning out Stage 5:**

> A git index and working tree are a single shared resource. Two agents writing to one worktree corrupt each other's staged state rather than going faster, and an interleaved slice cannot be reverted alone — which defeats the revertibility the whole flow is built on. Giving each slice its own worktree moves the collision to a merge step and multiplies the shared-database hazard in Appendix A. Stage 5 therefore has one writer. Every other stage fans out.

**A good sub-agent prompt** states: the question, concretely ("which module owns refund idempotency, and what enforces uniqueness today?", not "look into refunds"); where to look, if known; what to return — a conclusion plus `file:line` citations, never a file dump, within a stated 1,000–2,000-token budget; the search breadth; and what has already been ruled out. Split by domain or feature boundary, never by "first half of the files". If two pieces depend on each other, that is a pipeline — run it in sequence.

**Monitoring.** Each background sub-agent's completion arrives as a notification and re-invokes the conductor; for an ordinary fan-out that is the whole story — do not spawn a monitor agent. For genuinely long work only (the full suite, a Stage 3 measurement fan-out, a background shell), have each worker append status lines to `<scratchpad>/status/<name>.log` (say so in its prompt — nothing forces it) and watch that directory with the runtime's monitor tool, re-arming on each deadline. Don't build a design that depends on delivering messages to a still-running sibling.

**The audit lane** is one combined auditor in a fresh context, per Stage 7, with a mandatory per-category verdict. A missing category is a failed audit, not a clean one. Refutation is part of the lane, not a separate agent.

## Appendix D — Issue tracker conventions

**Stage 1 is silent.** Search; if none exists, create through `{{TRACKER_LIST_MAP}}`; report the link and continue. Do not create tasks speculatively — only when the flow needs one, or the user asks.

**Ownership.** Every task, comment and assignment this flow makes is created, assigned and commented **as the user** via `{{TRACKER_WRITE_ROUTE}}` — never left unassigned, never attributed to anyone else. Some MCP connectors post as a shared integration user; if writes would be attributed to someone other than the user, use the REST API with `{{TRACKER_API_KEY_ENV}}` instead, and check the key is set before relying on it. Send REST payloads from a script file in the scratchpad, not an inline command line (guard hooks may block strings in command lines), and build JSON with `jq -n --arg`; never hand-escape.

**Wording the description.** Write so a non-engineer stakeholder can read it: plain language, the *what* and the *why*, not the *how*. Only where the ask is genuinely technical, append a short "Technical notes" line with the specifics a developer needs — endpoint, model, service, error, migration. No production data. No projected or estimated figures.

**Formatting — ClickUp descriptions and comments behave differently.** Task descriptions accept markdown via `markdown_description` on create/update. Comments do not: `comment_text` is plain text, so `## Heading` shows the hashes and `**bold**` shows the asterisks. For comments, use backticks for every file path, env var and symbol (they become code chips), numbered and dashed lists, and UPPERCASE plain-text section titles; avoid `#` headings, `**bold**`, `_italic_` and tables. Comments are capped at 200 words. **A 200 response is not proof it rendered** — read the comment back and check for literal `##` or `**` before reporting it done. For other trackers, verify their rendering rules the same way.

**Closing the loop.** After the PR is open — and only then — move the task to `{{TRACKER_REVIEW_STATUS}}` and add a comment linking the PR. The status change signals "ready for review", so it must not run before the gate and audit are green and the PR exists.

## Appendix E — Diagnose: the performance protocol

Applies only to performance, latency or resource tasks: a slow endpoint, an APM trace, a timeout, a memory or DB-load complaint. **Never optimise from a hypothesis.** No optimisation code during this stage — measurement scripts belong in the scratchpad. Work through all eleven steps and report a quantified finding for each; where a step can't be answered, say so explicitly. Steps 1–4 and 7–9 are mutually independent — fan them out and aggregate.

1. **Record count** — how many rows does the operation actually process for the reported filters?
2. **Total query count** — uncapped. Framework query logs can truncate (Django's `connection.queries` caps at 9,000); use an execution hook such as `connection.execute_wrapper` instead.
3. **Slowest queries + repeated shapes** — normalise literals, group by shape, report how many statements belong to a repeated shape. That's the N+1 signal.
4. **`EXPLAIN (ANALYZE, BUFFERS)`** on the primary query — disk-spilling sorts, unexpected aggregates, unindexed filters, row width.
5. **Phase timing** — construction / DB fetch / transform / output generation / response, each split into DB time vs application time.
6. **Code inspection** — find the loop and the lazy lookups inside it. Cite `file:line`. Prove exhaustiveness with a control run.
7. **Cache frequency** — measure it. Ruling a suspect *out* with a number is a real finding.
8. **CPU profile** — a sampling profiler if installed (e.g. `py-spy`), else the stdlib profiler. State which; profiler overhead inflates absolute numbers.
9. **Peak memory** — RSS deltas per phase plus allocation tracing. Answer explicitly: is the whole dataset resident at once?
10. **Ranked bottlenecks** — ordered, each with quantitative evidence.
11. **Control measurement** — re-run with the suspected cause neutralised in a throwaway scratchpad script, converting "I think it's the N+1" into a measured before/after.

**Discipline rules.** State the caveats: dev-DB vs prod divergence, filters you couldn't reproduce, instrumentation overhead. Separate measurement from estimate — and keep estimates in chat: an extrapolation is fine in the report you show the user, labelled with its derivation, but it **never** reaches a commit message, PR body, tracker task or comment. Report incidental findings (an unstable sort, a missing index) and recommend separate tickets rather than widening scope.

**Ending the stage.** Present the ranked report, state which bottlenecks are in scope against the Stage 2 requirements, and continue to the tests. There is no second stop — if the ranking contradicts the requirements, that is a §2 failure: stop and say so.
