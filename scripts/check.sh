#!/usr/bin/env bash
#
# check.sh - verify the dev plugin before committing or merging.
#
# Usage: scripts/check.sh   (from anywhere inside the repo)
#
# Runs the same checks locally (via /dev:ship) and in CI, so there's one
# source of truth. Exit code 0 means all checks passed; 1 means at least one
# failed. Checks that need a missing tool are skipped and reported, never
# silently passed.

cd "$(git rev-parse --show-toplevel)" || exit 1

failures=0

pass() { printf '  ✓ %s\n' "$1"; }
fail() { printf '  ✗ %s\n' "$1" >&2; failures=$((failures + 1)); }
skip() { printf '  - %s (skipped: %s)\n' "$1" "$2"; }

echo "dev plugin checks"

# 1. Guard hook tests.
if python3 -I hooks/test_guard.py > /dev/null; then
  pass "guard hook tests"
else
  fail "guard hook tests (run: python3 hooks/test_guard.py)"
fi

# 2. Nothing the plugin needs may be gitignored. A bare "build/" pattern once
#    silently dropped skills/build/ from the repo. Two cases:
#    - untracked files that are ignored (never reach the repo)
#    - tracked files that match an ignore rule (the next new file beside
#      them would be silently dropped)
paths=(.claude-plugin skills agents hooks scripts)
ignored=$(
  {
    git ls-files --others --ignored --exclude-standard -- "${paths[@]}"
    git ls-files --cached --ignored --exclude-standard -- "${paths[@]}"
  } | grep -vE '(__pycache__/|\.pyc$|\.DS_Store$)'
)
if [[ -z "$ignored" ]]; then
  pass "no plugin files are gitignored"
else
  fail "gitignored plugin files (check .gitignore):"
  while IFS= read -r path; do
    printf '      %s\n' "$path" >&2
  done <<< "$ignored"
fi

# 3. Every skill and agent has the frontmatter Claude Code needs to load it.
missing=()
for f in skills/*/SKILL.md agents/*.md; do
  [[ -e "$f" ]] || continue
  head -n 15 "$f" | grep -q '^name:' || missing+=("$f: name")
  head -n 15 "$f" | grep -q '^description:' || missing+=("$f: description")
done
if (( ${#missing[@]} == 0 )); then
  pass "skill and agent frontmatter"
else
  fail "missing frontmatter: ${missing[*]}"
fi

# 4. Claude Code's own plugin validator, when the CLI is installed (not in CI).
if command -v claude > /dev/null; then
  if claude plugin validate . > /dev/null 2>&1; then
    pass "claude plugin validate"
  else
    fail "claude plugin validate (run it to see why)"
  fi
else
  skip "claude plugin validate" "claude CLI not installed"
fi

if (( failures > 0 )); then
  echo "$failures check(s) failed" >&2
  exit 1
fi
echo "all checks passed"
