# ship lessons (carried over from git-workflow)

Corrections agreed with the user after a fix loop. Format:
`- [YYYY-MM-DD] <what went wrong> -> <rule to follow next time>`

- [2026-10-22] Opus pre-push review flagged a user-authored debug/tooling file in the diff as "stray debug code" to remove -> don't recommend removing a user's own authored file (dated, lives in its own subdir, not obviously scratch/temp) unless it's clearly machine-generated or leftover from this run's own work; ask the user before suggesting removal.
- [2026-10-29] Plan assumed `git pull --ff-only` would fast-forward over dirty files whose content already matched the incoming commit; git refused anyway -> when changes were moved from the main checkout to a worktree via patch, plan for the post-merge sync up front: verify `git diff origin/main` is empty, then (with user OK) stash, pull --ff-only, confirm the stash matches HEAD, drop.
