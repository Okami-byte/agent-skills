---
name: spec
description: Turn an idea or a grilling session into a short, approved spec before any code is written. The spec covers the goal, non-goals, architecture diagram, key decisions, security and how you'll prove it works. Use for new projects, new infrastructure, or any change big enough that getting the shape wrong would be expensive.
disable-model-invocation: true
argument-hint: "[what we're building]"
---

# Spec

Decide what "done" means and what shape the work takes before writing any code. Coach mode applies (see the `principles` skill).

## 1. Get clear on the requirements

- If the idea is still fuzzy, run `/dev:grill` first and work from its decisions.
- Otherwise, ask only what you can't find out yourself. Use AskUserQuestion with a recommended answer for each question. Typical gaps: platform or cloud, region, budget, language and versions, existing infrastructure to reuse, and how long it should live (lab or long-lived).

## 2. Draw the architecture

Draw a Mermaid diagram in the spec (or ASCII if Mermaid won't render) showing:

- every component and how they connect, with arrows labeled by data flow
- security boundaries: networks, IAM roles, what can reach what
- build order: what must exist before what

A component that can't be placed on the diagram isn't understood yet.

## 3. Write `SPEC.md`

Put it at the repo root, or follow the repo's existing docs convention if it has one. Keep it to one or two screens.

```markdown
# <name>
## Goal          One paragraph: the problem, and what "done" looks like from the outside.
## Non-goals     What we are explicitly not doing (scope protection).
## Architecture  The diagram + one line per component.
## Decisions     Each key choice: chosen option, alternative considered, why. Mark one-way doors.
## Interfaces    Endpoints, CLI commands, env vars, inputs/outputs others depend on.
## Security      Least-privilege access, where secrets live, encryption, input validation, what's exposed.
## Verification  How we'll prove it works on the real system: exact commands/checks (feeds /dev:plan).
## Lifecycle     Deploy, rollback, and teardown (for labs: how to destroy everything and confirm it's gone).
## Open questions
```

## 4. Get approval

Show a short summary: how many components, the file layout (one line per file), the 3 to 5 key decisions, and any one-way doors. **Wait for the user's OK before building.** Then offer `/dev:plan`.

Treat the spec as a living document. When a decision changes during the build, update `SPEC.md` in the same commit.
