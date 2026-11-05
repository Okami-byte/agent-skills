---
name: handoff
description: Package the current session into a handoff document so a fresh agent (or the user tomorrow) can continue without re-explaining. Covers the goal, current state, decisions, next steps and gotchas, and references files instead of copying them. Use when the context is getting long, before a break, before switching machines, or when the user invokes /dev:handoff.
disable-model-invocation: true
argument-hint: "[focus or next task]"
---

# Handoff

Write the shortest document a fresh agent needs to keep going as if it had been here the whole time. Coach mode applies (see the `principles` skill).

## 1. Make the state safe

If there's uncommitted work worth keeping, ask whether to commit it as a `wip:` commit on its branch, so the next agent can find it. Never push it without asking. Note any running processes, open worktrees or temporary infrastructure, and say whether they should stay up.

## 2. Write the document

Write it to `$TMPDIR/handoff-<topic>-<YYYY-MM-DD>.md`, or wherever the user asks. Point to artifacts (paths, commit SHAs, PR and issue URLs) instead of pasting them. **Redact secrets.**

```markdown
# Handoff: <topic> (<date>)
## Goal            What we're ultimately trying to achieve, and why.
## Current state   What's done (with SHAs/paths/links), what's in progress, what's verified vs. assumed.
## Decisions       Key choices made and the one-line reason for each (so they aren't re-litigated).
## Next steps      Ordered, concrete; the very next action first.
## Gotchas         Things that wasted time or will bite: env quirks, failed approaches and why they failed.
## Open questions  What still needs the user's call.
## Suggested skills Which /dev: commands fit the next steps.
```

Focus on the user's stated focus, if they gave one. Leave out anything the next agent can rediscover cheaply from the repo.

## 3. Hand back

Reply with the file path and a two-line summary. Also give the one-line prompt to start the next session: `Read <path> and continue from "Next steps".`
