#!/usr/bin/env python3
"""PreToolUse hook: block any Bash command that invokes sudo.

HARNESS_BEST_PRACTICE_ADOPTION.md item 1(b). Reads the tool-call JSON Claude
Code passes on stdin; if tool_name is Bash and the command contains a sudo
invocation, exits 2 (blocks the call, stderr shown to the model).
"""
from __future__ import annotations

import json
import re
import sys

_SUDO_RE = re.compile(r"(^|[;&|]\s*)sudo\b")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    command = (payload.get("tool_input") or {}).get("command", "")
    if _SUDO_RE.search(command):
        sys.stderr.write(
            "BLOCKED by block_sudo.py: sudo is banned in this harness "
            "(HARNESS_BEST_PRACTICE_ADOPTION.md item 1b). "
            f"Command was: {command!r}\n"
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
