---
name: build
description: Work through a plan one slice at a time. Implement each slice, prove it with its check, commit it, then move on. Medium and large tasks go to the dev:issue-manager agent and small ones to dev:quick-task. Secure defaults and explanatory comments are included, and every endpoint is tested at the end. Use when a plan exists (PLAN.md, an issue or a task list) and it's time to execute.
disable-model-invocation: true
argument-hint: "[plan path or task number]"
---

# Build

Turn the plan into working, proven code one slice at a time. Coach mode applies (see the `principles` skill).

## 1. Hand off to the manager

Spawn the `dev:issue-manager` agent with one self-contained prompt. It has no memory of this conversation. Include:

- the plan word for word (each task with its size, Done when, Check and dependencies)
- file paths, repo context and constraints from the spec
- the standards in step 2 below

The manager sequences the work, does the medium and large tasks itself, and sends each small task to `dev:quick-task`. Run it in the foreground if the next step depends on it.

If there's no plan yet, stop and suggest `/dev:plan`. Building without a plan is how scope creeps.

## 2. Standards for every slice

- **Loop:** implement → run the task's **Check** → green → commit (via `/dev:ship` rules) → next task. Never start a slice while the previous one is red.
- **Stay in scope.** Do what the task says. Note anything else you notice for later instead of fixing it now.
- **Explanatory comments.** Explain *why* at non-obvious choices, security decisions and gotchas. Never comment on the obvious. This is coach mode in code.
- **Secure by default,** even when nobody asked:
  - least-privilege permissions with no wildcards
  - encryption at rest
  - input validation at the edges
  - no secrets in code (commit `.example` files only)
  - generic error responses that never leak stack traces
- **Keep derived values in one place:** `locals`, a constants module, or one config file.
- **If a task turns out bigger or different than planned,** stop and report it. Don't improvise past what the plan covered.

## 3. Verify the whole thing

At each checkpoint, and at the end, run the stack-specific checks in `STACKS.md`:

1. Static checks: lint, types, validate.
2. Deploy or start the system, if the spec says so. Use `/dev:ship` Part C for anything shared or long-lived.
3. Exercise **every** endpoint or interface: the happy path, error handling (missing, invalid, not found) and edge cases (empty, duplicate, already deleted).
4. Confirm logs and metrics are actually coming through.
5. Report a **pass/fail table**. A red row is not done.

## 4. Hand back

- Summarize what was built, what the manager did directly versus what it delegated, and any deviations from the plan.
- **For labs and temporary infrastructure:** pause so the user can inspect it, and tear down only after they confirm. Then check that the number of resources destroyed matches the number created, so nothing is left running up a bill.
- Offer `/dev:ship` to get it into main.
