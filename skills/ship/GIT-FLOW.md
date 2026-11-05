
# Git flow (ship, part B)

Take local changes all the way to main: add, commit, push, PR, review, merge.
This is the detailed procedure that `SKILL.md` points to.
Work is split across three model tiers. Spawn each with the Agent tool and the
`model` parameter.

| Tier | Model param | Role |
|------|-------------|------|
| Orchestrator | `opus` | Plans, reviews before push, reviews PRs before merge, writes final report |
| Executor | `sonnet` | The dev: stages, commits, pushes, opens PRs, applies fixes |
| Worker | `haiku` | Small jobs: commit messages, safety checks, status lookups |

The main conversation is only the relay: it spawns the agents, passes their
output along, tracks time, and talks to the user. It makes no git decisions itself.

## Hard rules

1. **Always attribute AI-made work.** The user wants to be able to tell at a glance
   whether they or Claude made a change. (This reverses an earlier "no attribution"
   rule, removed at the user's request on 2026-11-04.)
   - Commits: end the message with the `Co-Authored-By:` trailer given by the
     harness's attribution reminder. If none is given, use
     `Co-Authored-By: Claude <noreply@anthropic.com>`.
   - PR bodies: end with the PR attribution line from the harness reminder. If none
     is given, use `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
   - PR review comments and issue comments: start with a short marker such as
     `**Review by Claude**` so they are distinguishable from the user's own.
   - Subjects and titles stay plain and short; put the attribution in the trailer or
     footer, not the subject. No emoji in commit subjects.
2. **No push before an Opus review** of the diff and Haiku's safety report.
3. **No merge before an Opus review of the PR(s)**, and **no merge without the
   user's explicit go-ahead** at the final step.
4. **No destructive git.** No `--force` / `--force-with-lease` push, `reset --hard`,
   `clean -f`, `branch -D`, or `--no-verify` unless the user explicitly asks.
5. **Never commit directly to main/master.** Work on a branch.
6. **Every branch gets its own git worktree**, never a plain `git checkout -b`
   in the main working copy. The main checkout stays on its current branch,
   untouched, for the whole run. See "Worktrees" below.

## Procedure

### 0. Start the clock
Run `date +%s` and save it as the start time. Also note the current branch and
the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`).

### 1. Recon (Haiku)
Spawn a `haiku` agent to report, read-only: `git status --short`, `git diff --stat`,
current branch, upstream/remote state, ahead/behind vs the default branch,
recent `git log --oneline -10` (to learn the user's commit style), and whether
`gh` is authenticated. Return it compactly.

### 2. Plan (Opus)
Spawn an `opus` agent with the recon output and the user's request. It must
produce a plan that states:
- Branch name (create one if on main; short, kebab-case, descriptive) and its
  worktree path (see "Worktrees").
- How to group changes into commits, and which files go in each. Keep commits
  logically atomic.
- Whether to open one PR or several, and their order/dependencies.
- Which files must NOT be committed (secrets, `.env`, build output, large
  binaries, unrelated changes).
- The expected merge strategy per PR (see "Merge strategy").
- Risks to watch for.

Read `LESSONS.md` in this skill directory and pass its contents to Opus so past
corrections shape the plan. Also pass the change-gate notes from `SKILL.md`
(blast radius, door type, rollback plan) if the gate applied. Show the user a short version of the plan. Proceed
unless they object or the plan involves something risky or ambiguous.

### 3. Safety check (Haiku)
Before any commit, spawn a `haiku` agent to verify:
- Nothing on the "do not commit" list is staged or about to be.
- No secrets or credentials in the diff (keys, tokens, `.env`, private keys,
  passwords).
- No merge-conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
- The branch is not behind its remote in a way a push would overwrite
  (`git fetch` then compare); nothing here requires a force push.
- No unexpectedly large files.
Return PASS or a list of problems. Any problem goes back to Opus to decide.

### 4. Commit (Sonnet, with Haiku messages)
Spawn a `sonnet` agent to execute the plan: create the worktree for the branch
(see "Worktrees"), `cd` into it, stage the planned files by explicit path (no
`git add -A`), and commit group by group.

For each commit, a `haiku` agent writes the message from the staged diff:
- Match the style in the recon `git log` (casing, tense, prefix conventions).
- Short imperative subject, ~50 chars, no trailing period; a body only if the
  why is not obvious.
- Plain voice, no emoji. Haiku writes only the subject and body; the Sonnet
  executor appends the attribution trailer (rule 1).

Pass messages to git with `-m` and verify with `git log -1 --format=%B` that the
attribution trailer is present. If it is missing, amend it in (the commit is
still local) before moving on.

### 5. Pre-push review (Opus)
Spawn an `opus` agent to review the full branch diff against the default branch
plus the Haiku safety report and the commit messages. It checks correctness,
scope creep, leftover debug code, accidental deletions or overwrites, message
quality, and that every commit carries the attribution trailer. It returns APPROVE or a list of required
changes.

- APPROVE: continue.
- Changes needed: this uses the one fix loop (see "Fix loop").

### 6. Push and open PR (Sonnet)
Spawn a `sonnet` agent to `git push -u origin <branch>` (never force), then open
the PR with `gh pr create`. Haiku drafts the title, and the body using the PR template in `SKILL.md`
(Summary, Evidence, Merge danger, Rollback). The executor appends the PR
attribution footer (rule 1). Verify afterwards with `gh pr view --json title,body`
that the footer is present, and add it with `gh pr edit` if not.

### 7. PR review (Opus)
Spawn an `opus` agent to review each PR via `gh pr diff` and `gh pr view`
(and `gh pr checks` if CI exists). It returns APPROVE or required changes, plus
the recommended merge strategy and a one-line reason.

- Changes needed: fix loop.
- CI failing: treat it as required changes, never merge over red checks.

### 8. Ask the user, then merge
Present a short summary to the user: each PR (title, link, size), Opus's
verdict, CI status, and the recommended merge strategy. Then **stop and ask for
confirmation**. Only on a clear yes, spawn a `sonnet` agent to run
`gh pr merge <n> <strategy-flag>` and, if the user wants it, delete the branch
afterwards (`--delete-branch`). Either way, remove the local worktree now that
it's merged (see "Worktrees" cleanup). With several PRs, merge in the planned
order and let Haiku confirm main is healthy between merges (`git pull` in the
main checkout, `gh pr view` state).

### 9. Final report (Opus)
Run `date +%s` again for the elapsed time. Spawn an `opus` agent with the full
run history to write a quick rundown:
- **What was done**: branch, commits, PRs (with links), how merged.
- **Time taken**: total elapsed.
- **Issues / risks**: anything odd, anything skipped, anything worth watching
  on main, any fix loop that occurred.

Keep it to a short, scannable list. Relay it to the user as is.

## Worktrees

Every branch in this workflow lives in its own `git worktree`, never a
`checkout -b` inside the user's main working copy. The main checkout is left
exactly as the user had it, on whatever branch they were on, for the whole run.

- **Location**: sibling directory next to the repo, named
  `<repo-name>.worktrees/<branch-slug>` (branch slug = the branch name with
  `/` kept as-is in the path, e.g. `../dotfiles.worktrees/herdr/migrate-to-fullerzz-sesh`).
  Create the parent dir if missing.
- **Create**: from the main checkout, `git worktree add <path> -b <branch>`
  (branching off the default branch, fetched fresh first). If the branch
  already exists (resuming work), `git worktree add <path> <branch>` without
  `-b`.
- **Work there**: every `git add`/`commit`/`push`/`gh pr create` in steps 4-6
  runs with that worktree as cwd. Subagents get the worktree path explicitly,
  not the main repo path.
- **List/inspect**: `git worktree list` to confirm state; show the user the
  worktree path alongside the branch name when presenting the plan.
- **Cleanup**: once a PR is merged (step 8), remove the worktree —
  `git worktree remove <path>` from the main checkout (add `--force` only if
  the worktree has no uncommitted work left behind; never force-remove
  something with unpushed commits). Then prune: `git worktree prune`. This
  happens whether or not the user also wants the git branch deleted.
- Never run two worktrees for the same branch, and never point a worktree at
  the default branch itself.

## Merge strategy

Choose per PR, situationally. The user's usual preference is a **merge commit**,
so default to it unless the situation clearly fits another:

- **Merge commit** (`--merge`): default. Multi-commit PRs where the individual
  commits are meaningful and worth keeping in history.
- **Squash** (`--squash`): many noisy commits (WIP, "fix typo", review churn),
  or a tiny single-purpose change where one commit on main is cleaner.
- **Rebase** (`--rebase`): a few clean, already-linear commits and the repo
  prefers linear history.

Opus states the choice and why. If the repo restricts allowed methods, use what
it permits and say so.

## Fix loop

Allowed once per run. When an Opus review (step 5 or 7) requires changes:

1. **Stop and tell the user** what Opus found, in plain language. Do not
   silently fix.
2. Discuss with the user and agree on the approach.
3. Spawn a `sonnet` agent to apply the agreed fixes as new commits (never
   rewrite pushed history), with Haiku writing the messages and re-running the
   safety check.
4. Send it back to Opus for a re-review.
5. **Record the lesson**: append a short entry to `LESSONS.md` (below) stating
   what was wrong and the rule agreed, so future runs get it right without
   asking. Past lessons are passed to Opus (step 2) and Sonnet (step 4).

If the re-review still fails, stop and report to the user. No second loop.

## LESSONS.md

`LESSONS.md` in this skill's folder (`${CLAUDE_PLUGIN_ROOT}/skills/ship/LESSONS.md`). Create it if missing. One entry per
lesson:

```
- [YYYY-MM-DD] <what went wrong> -> <rule to follow next time>
```

Keep entries short and general (not tied to one repo's file names unless the
lesson is repo-specific; then prefix with the repo name).

## Notes

- Each subagent starts cold. Give it everything it needs: the worktree path
  (not the main repo path), branch, exact job, the hard rules above, and
  relevant lessons.
- Keep Haiku jobs small and mechanical. If a job needs judgment, route it to
  Sonnet or Opus.
- If `gh` is not authenticated or there is no remote, stop at the first point it
  matters and tell the user.
