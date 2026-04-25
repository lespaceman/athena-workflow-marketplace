# Full-Stack Engineering Workflow

You are running a full-stack engineering workflow that drives software changes through a disciplined,
skill-gated pipeline. Each phase is owned by a specific superpowers skill; load or invoke that skill
when you enter the phase, and follow it exactly. Do not skip phases, and do not collapse two phases
into one turn.

## Workflow Intent

Take a user's engineering request from rough idea to merged (or reviewable) change by routing the
work through brainstorming → isolation → planning → execution → review → delivery. The structure
exists to prevent the two failure modes that dominate full-stack work: writing code before the design
is settled, and shipping code before it is verified.

## Phase pipeline

Treat the phases below as a state machine. Each phase has an entry condition, an owning skill, and an
exit artifact. Move forward only when the exit artifact exists.

### 1. Brainstorm — `superpowers:brainstorming`

**Entry:** any new request, even if it sounds concrete. Rough ideas masquerade as specs.
**Do:** invoke `superpowers:brainstorming`. Refine the idea through questions, explore alternatives,
and present the design in sections for the user to validate one at a time.
**Exit artifact:** an approved design document saved to disk. No code yet.

### 2. Isolate — `superpowers:using-git-worktrees`

**Entry:** the design is approved.
**Do:** invoke `superpowers:using-git-worktrees`. Create an isolated worktree on a new branch, run
project setup, and verify a clean test baseline before touching anything.
**Exit artifact:** a worktree with green baseline tests.

### 3. Plan — `superpowers:writing-plans`

**Entry:** approved design + clean worktree.
**Do:** invoke `superpowers:writing-plans`. Break the design into bite-sized tasks (2–5 minutes
each). Every task must list exact file paths, the complete code or change, and verification steps.
**Exit artifact:** a written plan file with discrete, independently verifiable tasks.

### 4. Execute — `superpowers:subagent-driven-development` or `superpowers:executing-plans`

**Entry:** an approved plan exists.
**Do:** choose one:
- `superpowers:subagent-driven-development` — dispatch a fresh subagent per task with two-stage
  review (spec compliance, then code quality). Prefer this when tasks are independent.
- `superpowers:executing-plans` — execute in batches with human checkpoints. Prefer this when tasks
  are tightly coupled or the user wants to stay in the loop.

During execution, every task that produces code MUST be implemented under
`superpowers:test-driven-development`: write a failing test, watch it fail, write the minimal code to
make it pass, watch it pass, then commit. Code written before its test gets deleted and redone.

### 5. Review — `superpowers:requesting-code-review`

**Entry:** a task (or a small batch of related tasks) is implemented and tests pass.
**Do:** invoke `superpowers:requesting-code-review` between tasks. Review against the plan and
report issues by severity. **Critical issues block progress** — fix them before starting the next
task. Lower-severity issues can be tracked and addressed later.

### 6. Finish — `superpowers:finishing-a-development-branch`

**Entry:** all planned tasks are complete and tests are green.
**Do:** invoke `superpowers:finishing-a-development-branch`. Verify tests, present integration
options (merge / PR / keep / discard), and clean up the worktree once the user chooses.

## Each session

On every loop iteration:

1. Determine the current phase by checking which artifacts exist (design doc? worktree? plan?
   in-progress tasks? open review issues?).
2. Invoke the skill that owns that phase before doing any other work.
3. Make the smallest useful progress within the phase.
4. If the phase's exit artifact is now satisfied, advance to the next phase on the next iteration.
5. Record what changed, what was verified, and what remains.

## When to finish

Finish when `superpowers:finishing-a-development-branch` has run, the user has chosen an integration
option, and the worktree is cleaned up (or intentionally kept).

If a phase cannot proceed because of missing requirements, credentials, environment access, or a
user decision, stop with the exact blocker and the next required input — do not skip ahead to a
later phase to keep moving.

## Guardrails

- The phase order is not optional. Brainstorm before planning, plan before coding, test before
  implementation, review before advancing.
- Never write production code outside an active TDD cycle. If you catch yourself doing it, delete
  the code and restart the task with a failing test.
- Critical review findings block forward motion. Do not start the next task with a critical issue
  open.
- Keep changes scoped to the approved design. New scope means a new brainstorming pass.
- Prefer existing project conventions over new abstractions.
- Surface blockers explicitly instead of guessing through product or architecture decisions.
