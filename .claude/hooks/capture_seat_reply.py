#!/usr/bin/env python3
"""Stop hook: write the seat's reply beside the director turn it answers.

Director, 2026-09-07: *"it records what I send and not what you reply, and the stretch log only
lands when a stretch closes — so between the two there's a window where my advisor can see the
instruction and not the answer."*

WHY A STOP HOOK. The reply does not exist until the turn ends, so there is no earlier moment to
catch it. `UserPromptSubmit` captures his side; this captures the seat's, and the pair is complete
the instant the turn finishes rather than whenever a stretch closes.

THE SESSION ID IS THE HANDLE, NOT A TRANSCRIPT PATH. The one field verified against a real dumped
Stop payload in this repo is `session_id` (see `.claude/hooks/pull_next_work.py`), and the harness
names a transcript `<transcript folder>/<session_id>.jsonl`. `transcript_path` is used when the
payload happens to carry it and is never depended on -- an unverified field that silently goes
missing would put this back exactly where the console capture was for six days.

WHAT IT WRITES. The LAST assistant message of the turn, verbatim, redacted on the same terms as a
director turn. Not a summary: a summary is a judgement, and the whole point of a record is that the
reader can see what was actually said rather than what the machine thought worth repeating.

NEVER BLOCKS. Always exits 0, never writes to stdout -- a Stop hook that writes stdout is read as a
decision about whether the turn may end. A failure here is caught by
`console_instruction_record.check()`, which raises a finding when a day carries director turns and
no replies, so this may fail quietly BECAUSE something else is watching.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _seat import is_resident_seat  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


def assistant_turns(transcript: Path) -> list[tuple[str, str]]:
    """[(timestamp, text)] for every assistant message that said something, in order.

    Tool calls and thinking blocks are skipped: a `text` block is what was said to the director,
    and a record of what the machine said must not quote its own tool traffic back at him.

    THE TRANSCRIPT'S OWN TIMESTAMP, never the wall clock, so a reply sorts against the turn it
    answers. A hook firing late would otherwise file an answer after an instruction it preceded.
    """
    out: list[tuple[str, str]] = []
    with transcript.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                record = json.loads(line)
            except Exception:  # noqa: BLE001 - one bad line is not a blind transcript
                continue
            if record.get("type") != "assistant":
                continue
            content = (record.get("message") or {}).get("content")
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = "\n".join(b.get("text", "") for b in content
                                 if isinstance(b, dict) and b.get("type") == "text")
            else:
                continue
            if text.strip():
                out.append((str(record.get("timestamp") or ""), text))
    return out


def last_assistant_text(transcript: Path) -> tuple[str, str]:
    """The final assistant message, as (timestamp, text), or ("", "") if there is none."""
    turns = assistant_turns(transcript)
    return turns[-1] if turns else ("", "")


def main() -> int:
    if not is_resident_seat():
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0

    try:
        sys.path.insert(0, str(PROJECT_DIR))
        from datetime import datetime, timezone

        from tools import console_instruction_record as record

        transcript = None
        given = payload.get("transcript_path")
        if isinstance(given, str) and Path(given).is_file():
            transcript = Path(given)
        else:
            session = payload.get("session_id")
            if isinstance(session, str) and session:
                for folder in record.transcript_dirs():
                    candidate = folder / f"{session}.jsonl"
                    if candidate.is_file():
                        transcript = candidate
                        break
        if transcript is None:
            return 0

        stamp, text = last_assistant_text(transcript)
        if not text.strip():
            return 0
        if not stamp:
            now = datetime.now(timezone.utc)
            stamp = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
        record.append_reply(stamp, text)
    except Exception:  # noqa: BLE001 - see the module docstring: never block, the check watches
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
