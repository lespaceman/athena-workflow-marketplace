# Delivery mode: <merge | pr | local>

How the engineering workflow resolves a finished working branch in this repo. The Delivery phase of the `fullstack-engineering` workflow reads this file; until it exists the workflow uses `pr`.

## Modes

- **`merge`** — after the Verification and Review gates pass and the full suite is green on the merged result, merge the working branch into the default branch locally (fast-forward or clean merge), push, and remove the worktree once the run has closed. No pull request and no confirmation prompt. Right for solo repos with no branch protection.
- **`pr`** — push the working branch and open a pull request to the default branch with the delivery summary as the body. Never self-merge; leave the tracker issue In Review with the PR link. Right for repos with branch protection, required reviews, or a merge queue.
- **`local`** — commit locally only; no push, no merge. Right for read-only clones and forks without write access. Note it once in the session note, not per commit.

## Chosen mode

**`<mode>`** because `<reason: e.g. "no branch protection, single contributor" / "main is protected, reviews required">`.

## Always ask the user first when

- the merge has conflicts,
- the base branch is not the default branch,
- the working tree is dirty,
- the full suite fails on the merged result.

Abandoning a branch (deleting it without merging) always needs typed user confirmation, in every mode.
