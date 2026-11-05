---
name: review
description: Two-axis review of a diff, branch or PR. The spec axis asks whether it does what was asked. The standards axis asks whether it follows the repo's standards and the principles. The built-in /code-review handles correctness bugs. Findings get severity labels and a why. Use before merging, when the user asks to review a branch, PR or changes, or invokes /dev:review.
disable-model-invocation: true
argument-hint: "[PR number, branch, or 'since <ref>']"
---

# Review

Review from a fixed point, so the diff is exactly what's being proposed. Coach mode applies: every finding says *why* it matters (see the `principles` skill).

## 1. Fix the scope

Work out the diff: `git diff <base>...HEAD`, `gh pr diff <n>`, or what the user named. Collect the intent: the PR body, linked issue, `SPEC.md`, `PLAN.md`. Collect the standards: `CODING_STANDARDS.md`, `CLAUDE.md`/`AGENTS.md`, linter configs, and the `principles` skill.

## 2. Run the axes separately

Keep the axes apart so one doesn't color the other. For diffs over about 300 lines, run each axis as a parallel subagent with fresh context. Give each the diff and only that axis's inputs. For small diffs, run them one after the other here.

**Spec axis: does it do what was asked?**
- Every requirement or "Done when" is met, and there's evidence of it.
- Nothing is missing, and nothing extra slipped in (scope creep).
- Public interfaces, env vars and outputs match the spec. Docs and spec were updated if a decision changed.

**Standards axis: is it built the way we build things?**
- The repo's written standards and linters come first. A documented repo rule overrides the defaults below.
- Principles: verified on the real system? Idempotent? Stateful changes done as expand/contract? Validated at the edges? Delete before add? Tagged debug lines gone?
- Security: no secrets, least privilege, no wildcard IAM, inputs validated, errors don't leak internals.
- Infrastructure: blast radius stated, door type correct, rollback possible, `terraform plan` reviewed, pinned versions and image tags (no `latest`).
- Design smells: duplicated logic, one-caller wrappers, a change that forces edits in many unrelated places, speculative generality.

**Correctness axis:** run the built-in `code-review` skill on the same target for logic bugs. Don't duplicate its work.

## 3. Report

Keep each axis's findings separate; don't merge or re-rank them across axes. Label each finding:

- **Critical**: breaks things, loses data or opens a security hole. Blocks the merge.
- **Required**: must be fixed before merge.
- **Optional**: a real improvement, at the author's call.
- **Nit**: style only.

Format: `file:line`, what's wrong, **Why:** in one line, and a suggested fix.

End with a verdict: **APPROVE**, **APPROVE WITH NITS** or **CHANGES REQUIRED**, plus the single most important thing to fix. Post comments to a PR only if the user asks; when you do, start them with `**Review by Claude**`.
