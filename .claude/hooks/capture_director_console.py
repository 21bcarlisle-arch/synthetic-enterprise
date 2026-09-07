#!/usr/bin/env python3
"""UserPromptSubmit hook: write the director's console turn where the machine reads it.

WHY THIS IS A HOOK AND NOT A SCAN, which is the whole lesson of 2026-09-07.

`tools/console_instruction_record.py` captured by scanning session transcripts, on a path
hardcoded to `~/.claude/projects/-`. On 2026-09-03 the seat moved under systemd, its launch
directory changed, and every transcript after that landed in a differently-named folder. The old
folder still existed and still held sixteen real transcripts, so the module's fail-closed guard --
which refuses when there is NO transcript -- never fired. Six days of console input went
uncaptured and nothing anywhere noticed, because a folder that has gone cold reads exactly like a
director who has said nothing.

Fixing the path alone would not have been enough, and this is the part worth keeping. Scanning
transcripts cannot tell the director from a daemon: measured that day, an interactive seat, an
autonomous worker tick and a delivery-seat dispatch all record `userType: "external"` with
identical cwd and version. There is no structural discriminator after the fact -- only the text,
and matching text is the enumeration that module already warns about. At prompt-submit the answer
is simply known, so the classification problem does not arise.

The scan stays as a backstop for a session this hook missed. It is no longer the mechanism.

NEVER BLOCKS. Always exits 0, writes nothing to stdout, and swallows every failure: capturing the
director's words must not become a new way for his session to get stuck. A failure here is caught
by `console_instruction_record.check()`, which compares this record against the presence stamp and
raises a finding -- so the hook may fail silently precisely BECAUSE something else is watching.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _seat import is_resident_seat  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    # Seat guard FIRST, before any read or write: `.claude/hooks/` is committed, so every session
    # on this repo runs it, and a foreign session must not write the resident seat's record.
    if not is_resident_seat():
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001 - a malformed payload must never interrupt the prompt
        return 0

    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return 0

    try:
        sys.path.insert(0, str(PROJECT_DIR))
        from datetime import datetime, timezone

        from tools import console_instruction_record as record

        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
            f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
        record.append_turn(stamp, prompt)
    except Exception:  # noqa: BLE001 - see the module docstring: never block, the check watches
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
