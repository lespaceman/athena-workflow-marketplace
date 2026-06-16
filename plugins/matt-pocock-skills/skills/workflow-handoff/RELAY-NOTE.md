# Relay note template

Copy this into the saved temp file and fill every field. Leave no field blank — an empty field is the next agent's first blocker. Keep it short: link to durable artifacts, don't paste them.

```markdown
# Relay: <task / goal in one line>

Reason for handoff: <boundary | context-rot> — <one sentence>
Workflow: fullstack-engineering · Relayed: <date>

## Turn Protocol (current state)
PHASE: <current phase name + number>
GOAL: <one-line outcome>
LAST GATE CLEARED: <phase + PASS, or "none yet">
NEXT ACTION: <the single next step — a command where possible>
BLOCKER: <None | description + Stop channel (ask user / resolve / handoff)>
LAST VERIFICATION: <command + result, or "Not run">

## Source control (resume here)
Working branch: <branch>            Worktree: <path or "main checkout">
Last pushed commit: <sha — "all work above is pushed"?>
Unpushed/uncommitted: <None | what is dirty and why>

## Gates cleared (with evidence)
- <Phase N>: PASS — evidence: <command output location / committed file / browser proof / tracker entry>
- ...

## Durable artifacts (references, not copies)
- Design note: <path/URL>          - Plan / issues: <path/URL or tracker key>
- PRD: <path/URL>                   - Coverage plan / TC specs: <path>
- Browser/product evidence: <path> - Key commits: <sha … sha>
- Tracker / Linear issue: <key/URL>

## Open work (in order)
1. <next concrete step>
2. ...

## Suggested skills on resume
- Re-enter <Phase N> with `<skill>`; <`diagnose`/`linear`/… and why>

## Trust ledger  (context-rot handoffs only)
- Re-verify from scratch: <what the rotting agent is unsure of>
- Trust as proven: <what is backed by durable evidence above>
- Known uncertainty / suspected mistakes: <...>

## Blockers needing a human
- <decision / credential / access required, and who>  (or "None")
```
