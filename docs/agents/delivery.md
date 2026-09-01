# Delivery mode: merge

How the engineering workflow resolves a finished working branch in this repo.

**Mode: `merge`** — `main` is unprotected (no branch protection, no rulesets) and the repo has a single maintainer. After the Verification and Review gates pass and the full suite is green on the merged result, merge the working branch into `main` locally (fast-forward or clean merge), push `main`, and remove the worktree once the run has closed. No pull request and no confirmation prompt.

Ask the user before acting only when:

- the merge has conflicts,
- the base branch is not `main`,
- the working tree is dirty,
- the full suite fails on the merged result.

Abandoning a branch (deleting it without merging) always needs typed user confirmation.

Other modes the workflow understands: `pr` (open a pull request to the default branch and never self-merge) and `local` (commit locally only; no push or merge, for read-only remotes). Re-run `setup-engineering-workflow` to change the mode.
