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
from datetime import datetime, timezone
from pathlib import Path

# (reason, regex). Matched case-insensitively against the whole command string.
RULES: list[tuple[str, str]] = [
    # Filesystem
    (
        "recursive delete of a broad path",
        r"\brm\s+(-[a-z]*r[a-z]*|--recursive)\b[^;&|]*\s(/|~|\$home|\.|\.\.|\*|/[^/\s]+/?)(\s|$|;|&|\|)",
    ),
    ("raw disk write or format", r"\b(dd\s+[^;&|]*of=/dev/|mkfs(\.\w+)?\s|wipefs\s)"),
    (
        "recursive permission change on a system path",
        r"\bch(mod|own)\s+-[a-z]*r[a-z]*\s+\S+\s+(/|~)(\s|$)",
    ),
    # Git
    ("force push", r"\bgit\s+push\b[^;&|]*(\s-f\b|--force|\s\+\S+)"),
    (
        "discarding local work",
        r"\bgit\s+(reset\s+--hard|clean\s+-[a-z]*f|checkout\s+--\s+\.|restore\s+\.)",
    ),
    ("deleting an unmerged branch", r"\bgit\s+branch\s+-D\b"),
    ("skipping git hooks", r"\bgit\s+(commit|push|merge)\b[^;&|]*--no-verify"),
    # Infrastructure as code
    (
        "terraform/tofu destroy or unreviewed apply",
        r"\b(terraform|tofu)\s+(destroy|apply\b[^;&|]*-auto-approve|state\s+(rm|mv|push)|force-unlock)",
    ),
    # Containers / orchestration
    (
        "docker prune or volume removal",
        r"\bdocker\s+(system\s+prune|volume\s+(rm|prune)|image\s+prune\s+-a)|\bdocker[- ]compose\b[^;&|]*\bdown\b[^;&|]*(-v\b|--volumes)",
    ),
    (
        "kubernetes bulk or namespace delete",
        r"\bkubectl\s+delete\s+(ns|namespace)\b|\bkubectl\s+delete\b[^;&|]*--all\b",
    ),
    ("helm uninstall", r"\bhelm\s+(uninstall|delete)\b"),
    # Hypervisor / storage (Proxmox, ZFS)
    (
        "destroying a VM, container or dataset",
        r"\b(qm|pct)\s+destroy\b|\bzfs\s+destroy\b|\bzpool\s+destroy\b",
    ),
    # Databases
    (
        "dropping or truncating data",
        r"\b(drop\s+(database|table|schema)|truncate\s+table)\b",
    ),
    # Remote code
    (
        "piping a download into a shell",
        r"\b(curl|wget)\b[^;&]*\|\s*(sudo\s+)?(ba|z)?sh\b",
    ),
]

COMPILED = [(reason, re.compile(rx, re.IGNORECASE)) for reason, rx in RULES]


def check(command: str) -> list[str]:
    """Return the reasons a command is dangerous (empty list if it looks fine)."""
    return [reason for reason, rx in COMPILED if rx.search(command)]


# Modes where nobody is reliably watching each command. A dangerous command is
# denied outright here, so a human always has to run it themselves.
UNATTENDED_MODES = {"auto", "bypassPermissions", "dontAsk"}


def decide(mode: str, reasons: list[str]) -> tuple[str, str]:
    """Return (permissionDecision, reason message) for a flagged command."""
    why = "; ".join(reasons)
    if mode in UNATTENDED_MODES:
        return (
            "deny",
            f"dev guard: {why}. Blocked in {mode} mode. Do not retry or work "
            "around this. Show the user the exact command and why it is "
            "needed, and let them run it themselves with `! <command>`.",
        )
    return ("ask", f"dev guard: {why}. Confirm this is intended.")


AUDIT_LOG = Path.home() / ".claude" / "logs" / "dev-guard.tsv"


def audit(event: dict, command: str, reasons: list[str]) -> None:
    """Append one TSV row per flagged command: time, mode, cwd, reasons, command.

    Gives a record of every dangerous command an agent attempted. Tabs and
    newlines are flattened so one event is always one row. Never raises.
    """

    def clean(s: str) -> str:
        return " ".join(str(s).split())

    row = [
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
        clean(event.get("permission_mode", "")),
        clean(event.get("cwd", "")),
        clean("; ".join(reasons)),
        clean(command)[:500],
    ]
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write("\t".join(row) + "\n")
    except OSError:
        pass


def main() -> int:
    try:
        event = json.load(sys.stdin)
        command = event.get("tool_input", {}).get("command", "") or ""
    except (json.JSONDecodeError, AttributeError):
        return 0
    reasons = check(command)
    if not reasons:
        return 0
    mode = event.get("permission_mode", "")
    decision, message = decide(mode, reasons)
    audit(event, command, reasons + [f"decision={decision}"])
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": message,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
