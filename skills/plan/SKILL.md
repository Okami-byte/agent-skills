---
name: plan
description: Break a spec, issue or task into small vertical slices. Each slice gets acceptance criteria, a command that checks it, a size tag (small/medium/large) and a dependency order. The plan is written so /dev:build can work through it. Use when there is a spec or a clear task and it's time to decide the order of work.
disable-model-invocation: true
argument-hint: "[spec path, issue, or task]"
---

# Plan

Turn "what we're building" into an ordered list of small steps, each of which can be checked. Coach mode applies (see the `principles` skill).

## 0. Know what we're solving

Read `SPEC.md` (or the issue or task) if one exists. If nothing concrete exists, ask the user directly what we're solving, and wait for a concrete answer. If they don't know yet, suggest `/dev:grill` or `/dev:spec` first.

## 1. Plan on Opus

The planning should run on Opus. If this conversation is already on Opus, plan here; that saves a cold-start subagent. Otherwise, spawn a foreground `general-purpose` subagent with `model: "opus"`. Pass it the spec or issue word for word, plus any repo context. That subagent only plans; it doesn't execute anything.

## 2. Slice the work

- **Vertical slices.** Each slice delivers something that works end to end and can be checked, however thin. Never build "all the models, then all the routes"; build one route all the way through instead.
- **Build order for infrastructure:**
  1. config and version pinning
  2. variables
  3. data and storage
  4. security (IAM, policies)
  5. compute
  6. interface (API, load balancer, DNS)
  7. outputs and docs
- **Risky slices go first.** Whatever you're least sure of should be proven earliest.
- **Stateful changes** get split into expand → migrate → contract slices (principle 5).

## 3. Write each task like this

```
N. <imperative title>                          [small|medium|large] (depends on: M)
   Done when: <observable acceptance criteria>
   Check: <exact command that proves it — pytest …, curl …, terraform plan …>
```

Size tags drive delegation in `/dev:build`:
- **small**: a lookup, a one-line edit, or an existence check.
- **medium/large**: needs reasoning, touches several files, or the approach is unclear.

Add a **checkpoint** after every 3 to 5 tasks, where the whole system is verified, plus a short **Risks** list.

## 4. Save it and get approval

Write the plan to `PLAN.md` next to the spec, or to the issue if the work is tracked there. Also create one task-list entry per task, so progress survives if the session ends. Show the user the list, and start `/dev:build` only after they're happy with the order and the scope.
