#!/usr/bin/env python3
"""PreToolUse guard: ask the user before an agent runs a destructive shell command.

Reads the hook event JSON from stdin. If the Bash command matches a dangerous
pattern, prints a permissionDecision of "ask" so Claude Code shows a prompt.
Otherwise prints nothing and exits 0, which leaves the normal permission flow
in charge. Never blocks on its own errors (fails open to the normal prompt flow).
"""

from __future__ import annotations

import json
import re
import sys

# (reason, regex). Matched case-insensitively against the whole command string.
RULES: list[tuple[str, str]] = [
    # Filesystem
    ("recursive delete of a broad path",
     r"\brm\s+(-[a-z]*r[a-z]*|--recursive)\b[^;&|]*\s(/|~|\$home|\.|\.\.|\*|/[^/\s]+/?)(\s|$|;|&|\|)"),
    ("raw disk write or format", r"\b(dd\s+[^;&|]*of=/dev/|mkfs(\.\w+)?\s|wipefs\s)"),
    ("recursive permission change on a system path", r"\bch(mod|own)\s+-[a-z]*r[a-z]*\s+\S+\s+(/|~)(\s|$)"),
    # Git
    ("force push", r"\bgit\s+push\b[^;&|]*(\s-f\b|--force|\s\+\S+)"),
    ("discarding local work", r"\bgit\s+(reset\s+--hard|clean\s+-[a-z]*f|checkout\s+--\s+\.|restore\s+\.)"),
    ("deleting an unmerged branch", r"\bgit\s+branch\s+-D\b"),
    ("skipping git hooks", r"\bgit\s+(commit|push|merge)\b[^;&|]*--no-verify"),
    # Infrastructure as code
    ("terraform/tofu destroy or unreviewed apply",
     r"\b(terraform|tofu)\s+(destroy|apply\b[^;&|]*-auto-approve|state\s+(rm|mv|push)|force-unlock)"),
    # Containers / orchestration
    ("docker prune or volume removal",
     r"\bdocker\s+(system\s+prune|volume\s+(rm|prune)|image\s+prune\s+-a)|\bdocker[- ]compose\b[^;&|]*\bdown\b[^;&|]*(-v\b|--volumes)"),
    ("kubernetes bulk or namespace delete", r"\bkubectl\s+delete\s+(ns|namespace)\b|\bkubectl\s+delete\b[^;&|]*--all\b"),
    ("helm uninstall", r"\bhelm\s+(uninstall|delete)\b"),
    # Hypervisor / storage (Proxmox, ZFS)
    ("destroying a VM, container or dataset", r"\b(qm|pct)\s+destroy\b|\bzfs\s+destroy\b|\bzpool\s+destroy\b"),
    # Databases
    ("dropping or truncating data", r"\b(drop\s+(database|table|schema)|truncate\s+table)\b"),
    # Remote code
    ("piping a download into a shell", r"\b(curl|wget)\b[^;&]*\|\s*(sudo\s+)?(ba|z)?sh\b"),
]

COMPILED = [(reason, re.compile(rx, re.IGNORECASE)) for reason, rx in RULES]


def check(command: str) -> list[str]:
    """Return the reasons a command is dangerous (empty list if it looks fine)."""
    return [reason for reason, rx in COMPILED if rx.search(command)]


def main() -> int:
    try:
        event = json.load(sys.stdin)
        command = event.get("tool_input", {}).get("command", "") or ""
    except (json.JSONDecodeError, AttributeError):
        return 0
    reasons = check(command)
    if not reasons:
        return 0
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "dev guard: " + "; ".join(reasons) + ". Confirm this is intended.",
        }
    }, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
