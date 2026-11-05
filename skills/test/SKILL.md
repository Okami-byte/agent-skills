---
name: test
description: Write and run tests that check behavior in any language, Python first. For bugs, write a failing test before the fix. For infrastructure, run idempotency checks. Use when the user asks to test code, write test cases, check that something works, add a regression test, or invokes /dev:test.
argument-hint: "[file, function, or behavior]"
---

# Test

A test earns its place only if it would fail when the behavior breaks and pass when only the internals change. Coach mode applies (see the `principles` skill).

## 1. Know what "correct" means

Read the code, plus `SPEC.md` and `PLAN.md` if they exist (their "Done when" lines are your acceptance tests). If what the code should do is unclear, ask the user one or two focused questions, such as "What should this return for an empty list?" Never guess and then test the guess.

## 2. Pick the strategies

Pick 1 to 3 strategies and say why in one line each:

| Strategy | Use when |
|---|---|
| **Unit** | Small functions with clear inputs and outputs |
| **Integration** | Several components work together (class + helpers, app + DB) |
| **Functional / end-to-end** | A whole feature or workflow, from the user's side |
| **Acceptance** | The spec or the user stated explicit requirements |
| **Exploratory / edge** | Always: empty, `None`, zero, one item, boundaries, huge, unicode, duplicates |
| **Idempotency** | Scripts, playbooks, migrations, IaC: run it twice; the second run must change nothing |

Most code needs Unit + Exploratory. Bugs always get a **Prove-it** test: write the test, watch it fail for the right reason, then fix the bug.

## 3. Write good tests

- **Test behavior, not implementation details.** Assert on outputs, return values, side effects and HTTP responses, not on private calls.
- **Mock only at system boundaries:** network, cloud APIs, clock, randomness. Inside the system, prefer the real thing. Over-mocked tests can't fail.
- **Name tests after the behavior,** for example `test_<unit>_<scenario>_<expected>`. Each test gets a docstring saying *what* it checks and *why* that case matters (coach mode in tests).
- **Readable over clever.** Some repetition between tests is fine when it keeps each test understandable on its own. One behavior per test.
- **Use at most 5 cases per strategy.** Order them: happy path, then edges, then errors, then boundaries.
- **Skip a test rather than write a bad one.** A test that always passes or checks a copy of the code is worse than no test.

Language specifics are in sibling files. Python: `PYTHON.md`. For infrastructure, use the test column of `../build/STACKS.md`.

## 4. Run the tests and report

Run them yourself and read the full output. Then report:

- **All passing:** "✓ N passed", with a short breakdown by strategy.
- **Failures:** for each one, the test name and assertion, **why** it failed (the root cause), and a concrete fix. Say whether the code is wrong or the test is. If you're not sure, ask; don't weaken the test just to make it pass.
- **Gaps:** behaviors you deliberately didn't test, and why.
