# ship lessons (carried over from git-workflow)

Corrections agreed with the user after a fix loop. Format:
`- [YYYY-MM-DD] <what went wrong> -> <rule to follow next time>`

- [2026-10-22] Opus pre-push review flagged a user-authored debug/tooling file in the diff as "stray debug code" to remove -> don't recommend removing a user's own authored file (dated, lives in its own subdir, not obviously scratch/temp) unless it's clearly machine-generated or leftover from this run's own work; ask the user before suggesting removal.
- [2026-10-29] Plan assumed `git pull --ff-only` would fast-forward over dirty files whose content already matched the incoming commit; git refused anyway -> when changes were moved from the main checkout to a worktree via patch, plan for the post-merge sync up front: verify `git diff origin/main` is empty, then (with user OK) stash, pull --ff-only, confirm the stash matches HEAD, drop.
- [2026-11-04] Default worktree location (`<repo>.worktrees/` next to the repo) would have landed inside `~/.claude/skills/`, where Claude Code auto-loads plugins, risking a duplicate plugin -> never create worktrees inside a folder Claude Code loads skills or plugins from; use `~/Developer/<repo-name>.worktrees/<branch>` instead.
- [2026-11-04] Push failed only after planning and committing: the remote was unreachable (SSH agent inside Herdr had no keys) and the GitHub repo was still empty -> in recon, run `git ls-remote origin` to prove the remote is reachable, and check the default branch exists on GitHub, before planning anything.
