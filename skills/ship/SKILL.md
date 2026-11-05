---
name: ship
description: Take changes from the working tree to main and, when asked, out to a running system. Covers the change gate (blast radius, one-way vs two-way door, rollback plan), commit, push, PR, review, merge, deploy and checking the result. Use when the user asks to commit, push, open/create/review/merge a PR, "ship this", "get this into main", deploy or roll out a change, or invokes /dev:ship.
argument-hint: "[what to ship]"
---

# Ship

Coach mode applies: add a **Why:** line at each key decision (see the `principles` skill).

## Part A. The change gate

Run the gate before committing anything that touches infrastructure, deploys, data, secrets, networking, CI/CD or shared config. For docs-only or purely local changes, skip it and say in one line that you skipped it.

1. **Blast radius.** List what could break: services, hosts, users, data, other repos and pipelines.
2. **Door type.** Is this a **two-way door** (a config value, a feature flag, a new resource) or a **one-way door** (deleting a volume, DB or zone, a state move, a destroy-and-recreate, a schema drop)? For a one-way door, stop and get the user's explicit OK, and take a backup or snapshot first.
3. **The one fact.** Name the single fact that makes the change safe, then prove it by running something. Evidence ranks from weakest to strongest: "I said so", "I pointed at the line", "I walked through the failure", "I ran it", "I reproduced it on the real system". Aim for "I ran it" or better.
   - Terraform: run `terraform plan`, read every `destroy` and `-/+` replace, and paste the summary line.
   - Docker: build the image and run it locally, and check its health.
   - Python: run the tests and type checks.
4. **Stateful changes use expand → migrate → contract.** If the change renames or removes something that holds state, split it so the destructive step ships last and on its own. For Terraform renames, use a `moved` block.
5. **Rollback plan.** Write down the exact undo steps and roughly how long they take, for example: "`git revert <sha>` then `terraform apply`, about 3 min" or "restore the Proxmox snapshot `pre-x`, about 5 min". If you can't write a rollback plan, the change is a one-way door. Treat it that way.

Keep the gate output short. It goes into the PR body.

## Part B. Git: commit → PR → merge

Follow `GIT-FLOW.md` in this folder: three model tiers, worktrees, a safety check, an Opus review before push and before merge, attribution on everything Claude made, merge only after the user says yes, and lessons recorded in `LESSONS.md`. Every rule in it still applies.

### PR body template

```
## Summary
What changed and why, using the smallest clear visual: a file tree, call flow, diff excerpt or diagram.

## Evidence
Proof it works: test output, the `terraform plan` summary, health checks, before/after.

## Merge danger
Door: one-way | two-way. Blast radius: <what could break>. The one fact: <fact + how it was proven>.

## Rollback
<exact steps> (~<time>)
```

## Part C. Deploy and verify (only when asked to deploy or roll out)

1. Deploy to the smallest target first: one container, one VM, a staging workspace or a canary.
2. **Verify the real thing.** Hit the endpoint, check the container's health, check the service status, or re-run `terraform plan`, which should now show no changes. A green CI run is not proof.
3. Watch it for a short window and state what you watched. Signs of trouble: error rate, restarts, latency, failing health checks. If any of them go bad, run the rollback plan. Don't debug on top of a broken deploy.
4. Widen the rollout only after the check passes.

## Final report

Report the branch, commits, PR links and merge method. Include gate results such as door type and rollback plan, deploy verification evidence if you deployed, total time, and anything to keep an eye on.
