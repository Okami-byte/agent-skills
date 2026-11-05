---
name: simplify
description: Behavior-preserving cleanup of a file, module or diff. Pins current behavior first, runs the formatters and linters, then simplifies to the style standards for Python, Terraform, Bash, Docker Compose and Dockerfiles. Use when the user wants code cleaned up, simplified, refactored, made readable, or invokes /dev:simplify.
disable-model-invocation: true
argument-hint: "[file, folder, or 'diff']"
---

# Simplify

Make code smaller and clearer **without changing what it does**. Coach mode applies: say why each change is simpler (see the `principles` skill).

## 1. Pin the behavior first

- If tests cover the code, run them and record that they pass.
- If they don't, write a few quick characterization tests that capture what the code does *now* (see `/dev:test`). For IaC, save a `terraform plan` or the output of `docker compose config` as the baseline.
- Without a pinned baseline you can't prove nothing changed. If you can't pin it, say so and keep the changes cosmetic.

## 2. Let the tools do the mechanical part

Run the formatter and linter for each file type before making any judgment calls:

| Type | Format | Lint |
|---|---|---|
| Python | `ruff format` | `ruff check --fix`, `mypy` |
| Terraform | `terraform fmt -recursive` | `terraform validate`, `tflint` |
| Bash | `shfmt -i 2 -w` | `shellcheck` |
| Compose | — | `docker compose config -q` |
| Dockerfile | — | `hadolint` |

If a tool isn't installed, run it through `uvx`, `brew` or `docker`, or tell the user rather than skipping it silently.

## 3. Simplify by judgment

Work in small steps. After each step, re-run the baseline from step 1. If it's red, revert that step.

- **Delete before you add.** Remove dead code, unused variables and imports, one-caller wrappers and stale comments.
- **Flatten:** use guard clauses and early returns instead of nested conditionals.
- **Name for intent,** and split functions that do more than one thing.
- **Remove repetition** with locals, constants, loops, `for_each` or YAML anchors, but only when it makes the code easier to read.
- **Chesterton's fence:** if odd code might exist for a reason (performance, compatibility, a workaround), find the reason in git history (`git log -L`, `git blame`) before removing it. If you keep it, add a *why* comment.

Apply the standards for each language from `STYLE.md` in this folder.

## 4. Report

Show:

- the changes, grouped by kind (deleted, flattened, renamed, split, style)
- a **Why:** line for any change that isn't obvious
- proof that behavior is unchanged: the same tests passing, or the same plan or config output
- anything you flagged but deliberately left alone, and why
