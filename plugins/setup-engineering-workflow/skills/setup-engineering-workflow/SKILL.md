---
name: setup-engineering-workflow
description: Sets up the engineering workflow's per-repo context — an `## Agent skills` block in AGENTS.md/CLAUDE.md plus `docs/agents/` — capturing this repo's issue tracker (GitHub, GitLab, Linear, ClickUp, or local markdown), triage label vocabulary, domain doc layout, and delivery mode (merge / pr / local), and recording the workflow skill map derived from the installed plugins. Interactive by default; has an unattended mode that writes detected defaults marked as unconfirmed. Run before first use of the engineering workflow or its skills (`to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, `improve-codebase-architecture`, `zoom-out`), when the engineering workflow's Delivery phase needs a delivery mode, or if those skills appear to be missing context about the issue tracker, triage labels, or domain docs.
---

# Set Up Engineering Workflow

Scaffold the per-repo configuration the engineering workflow's skills assume, and record the workflow's skill map:

- **Issue tracker** — where issues live (GitHub, GitLab, Linear, ClickUp, or local markdown, all supported out of the box)
- **Triage labels** — the strings used for the five canonical triage roles
- **Domain docs** — where `CONTEXT.md` and ADRs live, and the consumer rules for reading them
- **Delivery mode** — how a finished working branch is resolved: `merge` to the default branch, `pr`, or `local` only
- **Workflow skill map** — an inventory of every skill the engineering workflow can load, derived from the installed plugins (recorded, not an interactive decision)

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write. When no user is available, see **Unattended mode** at the end.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config` — is this a GitHub or GitLab repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root — does either exist? Is there already an `## Agent skills` section in either?
- `CONTEXT.md` and `CONTEXT-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories
- `docs/agents/` — does this skill's prior output already exist?
- `.scratch/` — sign that a local-markdown issue tracker convention is already in use
- Repo-local evidence of a hosted tracker: `linear.app` or `app.clickup.com` links in the README, PR/issue templates, commit trailers, or an existing `docs/agents/issue-tracker.md`. Do **not** treat a configured `linear`/`clickup` MCP server as evidence — the engineering workflow pins both on every run regardless of the target repo. Bare issue keys (`ABC-123`) are ambiguous between Linear, ClickUp custom IDs, and Jira; they count only alongside a matching URL host.
- Branch protection and merge policy on the default branch. GitHub: `gh api repos/{owner}/{repo}/branches/<default>/protection` (HTTP 404 = none) **and** `gh api repos/{owner}/{repo}/rules/branches/<default>` (`[]` = no rulesets; merge queues and most newer protection live here), plus `CODEOWNERS` and required status checks. GitLab: `glab api projects/:id/protected_branches`. Any other host, or an API failure that is not a clean 404 / empty list, means protection is *unknown*.
- Contributor count: `git shortlog -sn`, ignoring bot authors

### 2. Present findings and ask

Summarise what's present and what's missing. Then walk the user through the four decisions **one at a time** — present a section, get the user's answer, then move to the next. Don't dump all four at once.

Assume the user does not know what these terms mean. Each section starts with a short explainer (what it is, why these skills need it, what changes if they pick differently). Then show the choices and the default.

**Section A — Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-issues`, `triage`, and `to-prd` read from and write to it — they need to know whether to call `gh issue create`, call the Linear or ClickUp MCP, write a markdown file under `.scratch/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

Default posture: if the `git remote` points at GitHub, propose GitHub; at GitLab (`gitlab.com` or a self-hosted host), propose GitLab. Repo-local Linear or ClickUp evidence (see step 1) overrides the remote. Otherwise (or if the user prefers), offer:

- **GitHub** — issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab** — issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Linear** — issues live in a Linear team; the `linear` skill owns pickup and status transitions (ask for the team key and default project)
- **ClickUp** — tasks live in a ClickUp list; the `clickup` skill owns pickup and status transitions (ask for the workspace, space, optional folder, and list)
- **Local markdown** — issues live as files under `.scratch/<feature>/` in this repo (good for solo projects or repos without a remote)
- **Other** (Jira, etc.) — ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose

**Section B — Triage label vocabulary.**

> Explainer: When the `triage` skill processes an incoming issue, it moves it through a state machine — needs evaluation, waiting on reporter, ready for an AFK agent to pick up, ready for a human, or won't fix. To do that, it needs to apply labels (or the equivalent in your issue tracker) that match strings *you've actually configured*. If your repo already uses different label names (e.g. `bug:triage` instead of `needs-triage`), map them here so the skill applies the right ones instead of creating duplicates.

The five canonical roles:

- `needs-triage` — maintainer needs to evaluate
- `needs-info` — waiting on reporter
- `ready-for-agent` — fully specified, AFK-ready (an agent can pick it up with no human context)
- `ready-for-human` — needs human implementation
- `wontfix` — will not be actioned

Default: each role's string equals its name. Ask the user if they want to override any. If their issue tracker has no existing labels, the defaults are fine.

**Section C — Domain docs.**

> Explainer: Some skills (`improve-codebase-architecture`, `diagnose`, `tdd`) read a `CONTEXT.md` file to learn the project's domain language, and `docs/adr/` for past architectural decisions. They need to know whether the repo has one global context or multiple (e.g. a monorepo with separate frontend/backend contexts) so they look in the right place.

Confirm the layout:

- **Single-context** — one `CONTEXT.md` + `docs/adr/` at the repo root. Most repos are this.
- **Multi-context** — `CONTEXT-MAP.md` at the root pointing to per-context `CONTEXT.md` files (typically a monorepo).

**Section D — Delivery mode.**

> Explainer: When the engineering workflow finishes a change on a working branch, its Delivery phase has to resolve that branch. (Skip this section when setting up for a workflow that has no delivery phase, such as `product-discovery`.) In a solo repo with no branch protection, merging straight to the default branch is fastest. In a team repo with required reviews or a merge queue, the agent must open a pull request and never self-merge. This choice decides which of those the workflow does without asking.

The three modes:

- **`merge`** — merge locally to the default branch after the Verification and Review gates pass, push, remove the worktree once the run has closed; no PR, no prompt
- **`pr`** — push the branch and open a pull request with the delivery summary; never self-merge; leave the tracker issue In Review
- **`local`** — commit locally only; no push or merge (read-only clones, forks without write access)

Default: `merge` only when the exploration found **no** protection (no branch protection, no rulesets, no required checks, no `CODEOWNERS`, no merge queue) **and** a single human contributor; `pr` in every other case, including when protection is unknown. Present the evidence and let the user override.

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4 for selection rules)
- The contents of `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/domain.md`, `docs/agents/delivery.md`

Let them edit before writing.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create — don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa) — always edit the one that's already there.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout — "single-context" or "multi-context"]. See `docs/agents/domain.md`.

### Delivery mode

[`merge` | `pr` | `local`] — [one-line reason]. See `docs/agents/delivery.md`.

### Workflow skills

Engineering-workflow skills, loaded by trigger on the agent's own judgment (model-invocable). Availability depends on the plugins being installed, not on this block:

[grouped inventory — see below]
```

**Derive the `### Workflow skills` inventory from what is actually installed**, not from memory. It is not one of the interactive decisions, but it must be true for this machine:

1. Find the engineering workflow's pins: `~/.config/athena/workflows/fullstack-engineering/workflow.json` (Athena) or the installed plugin list (Claude Code / Codex).
2. For each pinned plugin, list `skills/*/SKILL.md` under its installed package and read each `name:`. Athena unpacks packages under `~/.config/athena/plugin-packages/<owner>/<marketplace>/<plugin>/<version>/`; on Claude Code and Codex use the runtime's loaded-skill list (the skills named in the system prompt or the skill listing tool) filtered to those plugins.
3. Group them under these headings, dropping any heading with no installed skill: **Setup**, **Alignment & planning**, **Tracker & triage**, **Production errors**, **Code & diagnosis**, **UI**, **Live browser**, **Exploration**, **Test design**, **Test automation**, **Release scope**, **Handoff**.
4. List skills that are installed with a pinned plugin but are *not* routed by the workflow under a final line **Installed, not part of the workflow (load only on explicit request):** — the workflow's own `## Plugins` section names them.

If neither source is resolvable, fall back to this reference inventory (current as of `fullstack-engineering` 0.1.16) and say so in the block:

- **Setup:** `setup-engineering-workflow`
- **Alignment & planning:** `grill-with-docs`, `prototype`, `to-prd`, `to-issues`
- **Tracker & triage:** `linear`, `clickup`, `triage`
- **Production errors:** `sentry`
- **Code & diagnosis:** `tdd`, `diagnose`, `zoom-out`, `improve-codebase-architecture`
- **UI:** `frontend-design`, `shadcn-ui`
- **Live browser:** `agent-web-interface-guide`
- **Exploration:** `map-feature-scope`, `capture-feature-evidence`
- **Test design:** `plan-test-coverage`, `generate-test-cases`, `review-test-cases`, `exploratory-test-writer`
- **Test automation:** `analyze-test-codebase`, `add-playwright-tests`, `write-test-code`, `review-test-code`, `fix-flaky-tests`
- **Release scope:** `define-smoke-scope`, `define-regression-scope`
- **Handoff:** `workflow-handoff`, `handoff`
- **Installed, not part of the workflow (load only on explicit request):** `caveman`, `git-guardrails-claude-code`, `setup-pre-commit`, `write-a-skill`

Then write the four docs files using the seed templates in this skill folder as a starting point:

- [issue-tracker-github.md](./issue-tracker-github.md) — GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md) — GitLab issue tracker
- [issue-tracker-linear.md](./issue-tracker-linear.md) — Linear issue tracker (fill in the team key and default project)
- [issue-tracker-clickup.md](./issue-tracker-clickup.md) — ClickUp task tracker (fill in the workspace, space, optional folder, and list)
- [issue-tracker-local.md](./issue-tracker-local.md) — local-markdown issue tracker
- [triage-labels.md](./triage-labels.md) — label mapping
- [domain.md](./domain.md) — domain doc consumer rules + layout
- [delivery.md](./delivery.md) — delivery mode (fill in the chosen mode and reason)

For "other" issue trackers, write `docs/agents/issue-tracker.md` from scratch using the user's description.

### 5. Done

Tell the user the setup is complete and which engineering skills will now read from these files. Mention they can edit `docs/agents/*.md` directly later — re-running this skill is only necessary if they want to switch issue trackers, change the delivery mode, or restart from scratch.

## Unattended mode

Use this only when an AFK workflow run needs the config and no user is present to answer. Never use it when an `## Agent skills` block already exists — unattended mode creates, it does not overwrite. One exception: a block that predates delivery modes (no `### Delivery mode` line) may have that single section and `docs/agents/delivery.md` added unattended, with the same unconfirmed header.

1. Run step 1 (Explore) in full.
2. Choose each section's detected default without asking: the tracker per Section A's default posture (GitHub remote → GitHub; GitLab remote → GitLab; repo-local Linear/ClickUp evidence overrides the remote); the canonical label strings; single-context unless `CONTEXT-MAP.md` exists; the delivery mode per Section D's default (`merge` only with no protection of any kind and a single human contributor, else `pr`).
3. If the tracker cannot be detected (no remote and no repo-local tracker evidence, or evidence that is ambiguous such as a bare issue key), stop and report that instead of guessing — local markdown is an interactive choice, never an unattended default — and the workflow will hand off the config-dependent action.
4. Write the block and the four docs files exactly as in step 4, and put this line at the top of the block and of each generated file: `<!-- Auto-detected in unattended mode on <YYYY-MM-DD>; not yet confirmed by a maintainer. Edit or re-run setup-engineering-workflow to confirm. -->`
5. Commit the result as its own change (`chore: bootstrap engineering workflow config (unattended)`) before any product code changes, and record the detected choices in the workflow's session note.
