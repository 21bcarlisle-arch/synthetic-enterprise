#!/usr/bin/env python3
"""UserPromptSubmit hook -- stamp genuine HUMAN keystroke activity so the
injection gate can tell "the director is here" from "the machine is talking to
itself" (2026-07-14, director: "presence must AUTO-EXPIRE after N minutes
without human keystrokes ... a hold that needs my absence but can't detect
absence is a machine I switch off by looking at it").

On every prompt submission this writes docs/observability/.human_last_input with
the current epoch -- UNLESS the prompt is a daemon-INJECTED turn (supervisor
grant, NTFY relay, resume instruction), which must NOT count as human presence
(otherwise the machine's own injected turns would keep refreshing "presence" and
latch the hold forever -- the same self-refreshing-signal disease as the
fail-silent deadman). tmux_relay._director_present() reads the stamp and treats
presence as TRUE only within a short TTL of the last real keystroke, so it
self-expires when the human goes quiet and self-refreshes when they type. No
manual arm/release, ever.

Never blocks or errors into the session: any failure is swallowed and the prompt
proceeds untouched (exit 0, no output)."""
import json
import sys
import time
from pathlib import Path

# Prefixes that identify a MACHINE-injected turn (must NOT count as human
# presence). NOTE: an NTFY relay is deliberately NOT here -- it is a genuine
# human message from the director's phone (the daemon only carries it), so it
# SHOULD refresh presence; and its marker sits at the END of the prompt anyway
# (message first), so a startswith check would never catch it regardless.
_DAEMON_PROMPT_MARKERS = (
    "[SUPERVISOR:",
    "Session resuming after crash or usage-limit reset",
    "[AUTONOMOUS",
)

_STAMP = Path(__file__).resolve().parent.parent.parent / "docs" / "observability" / ".human_last_input"


def main() -> None:
    try:
        raw = sys.stdin.read()
        prompt = ""
        if raw.strip():
            try:
                prompt = (json.loads(raw).get("prompt") or "").lstrip()
            except (json.JSONDecodeError, AttributeError):
                prompt = raw.lstrip()
        # A machine-injected turn is NOT human presence -- do not stamp.
        if any(prompt.startswith(m) for m in _DAEMON_PROMPT_MARKERS):
            return
        _STAMP.parent.mkdir(parents=True, exist_ok=True)
        _STAMP.write_text(str(int(time.time())), encoding="utf-8")
    except Exception:
        pass  # never disrupt the session


if __name__ == "__main__":
    main()
    sys.exit(0)
