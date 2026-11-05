---
name: grill
description: Interview the user one question at a time, each with a recommended answer, until a plan or design is clear. Use for code, infrastructure, homelab, or non-technical decisions.
disable-model-invocation: true
argument-hint: "[what to decide]"
---

# Grill

Get the design right before anything gets built. The user owns the decisions. You do the fact-finding.

## 1. Learn the facts yourself first

Read the repo, config, existing infrastructure and docs before you ask anything. Never ask the user something you could find out yourself. If a fact needs a lot of digging, send it to a subagent with fresh context and use only its summary.

## 2. Map the decisions

List the open decisions as a tree: each decision and the decisions that depend on it. The **frontier** is the set of decisions whose prerequisites are already settled. Ask only about the frontier.

## 3. Ask one round at a time

- Use the AskUserQuestion tool when it is available, with 1 to 4 questions per round, all from the frontier.
- Every question gets a **recommended answer**. Put it first and mark it "(Recommended)". Word it so that saying yes accepts it.
- Coach mode: add a short **Why:** to each recommendation, giving the senior reasoning in one line. See the `principles` skill.
- Mark one-way-door decisions clearly. Those deserve the user's full attention.
- After each answer, update the tree. New facts can open new questions or close old ones.

## 4. Know when to stop

Stop when the frontier is empty, or when the remaining questions don't change what gets built. Don't grill on details the user won't care about. Pick sensible defaults and list them as assumptions.

## 5. Hand back

Give a short summary:

- **Decisions**: each one, with a one-line reason.
- **Assumptions**: the defaults you chose without asking.
- **Out of scope**: what was explicitly left out.
- **Open questions**: anything that is still fuzzy.

Then offer the next step, such as writing a spec (`/dev:spec` once it exists) or starting the work. Save the summary to a file only if the user asks.
