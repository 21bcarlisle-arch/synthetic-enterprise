"""H30 — the diagnostic payload of a failed child process.

WHY THIS EXISTS
---------------
`background/sim_runner.py::run_simulation` launched the whole simulation with
`subprocess.run(...)` and no `capture_output`, so the child inherited fds 1/2.
When the runner is started by a daemon those fds point at a socket, not a
terminal — every traceback the child wrote went somewhere nobody reads. On
2026-08-08 eight consecutive runs failed on a plain `NameError` and each one
logged `rc=1` and nothing else; the fault was only ever identified by
re-running the child by hand. The director had to spend attention flagging a
loop that, by construction, could not be diagnosed from its own alert.

R5 says an alert fires on a transition AND CARRIES ITS DIAGNOSTIC PAYLOAD. A
failure report built from a return code alone cannot satisfy that: `rc=1` is
the same string for a missing import, a full disk and a killed process.

WHAT THIS MODULE IS
-------------------
Two small functions, deliberately not a subprocess wrapper. The launch sites
differ (timeouts, cwd, which stream matters, whether stdout must keep
streaming), and a wrapper that tried to own all of that would be the
adapters-for-future-adapters shape the SIMPLICITY GUARD forbids. What they
genuinely share is: turn whatever came back on stderr into something safe to
put in a log line and an NTFY body.

Both are total — bytes, str, None, or a test double's MagicMock all resolve to
a string, never an exception. A diagnostic helper that can itself raise turns a
child's failure into the parent's failure, which is how a monitoring path takes
down the thing it monitors.
"""
from __future__ import annotations

#: Lines of the child's stderr kept for the log. A Python traceback is
#: typically 5-20 lines; 40 holds one comfortably plus whatever the child
#: printed just before dying, without pasting a whole test-suite run into
#: the observability log.
STDERR_TAIL_LINES = 40

#: NTFY bodies are read on a phone. The last stderr line is nearly always the
#: exception type and message — the part that identifies the fault.
NTFY_STDERR_CHARS = 240


def stderr_tail(raw: object, limit: int = STDERR_TAIL_LINES) -> str:
    """Last `limit` non-blank lines of a child's stderr, as text.

    Accepts `bytes` (undecodable sequences are replaced, never raised on),
    `str`, `None`, or anything else — anything that is not text resolves to
    "" so a caller can always interpolate the result. Returns "" when there
    is nothing to show, which callers must render as an explicit "no stderr
    captured" rather than an empty gap: a silent blank reads exactly like the
    defect this module exists to remove.
    """
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="replace")
    elif isinstance(raw, str):
        text = raw
    else:
        # None, a MagicMock from a test double, an int from a caller that
        # passed the wrong thing. None of those are a diagnostic payload.
        return ""
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    return "\n".join(lines[-limit:])


def failure_detail(raw: object, chars: int = NTFY_STDERR_CHARS) -> str:
    """One-line summary of a child's stderr, sized for an NTFY body.

    Takes the LAST line (for a traceback, the exception line) and truncates.
    Returns an explicit marker when nothing was captured, so a reader can tell
    "the child said nothing" apart from "nobody looked" — the second is a
    defect in this code and must not be able to masquerade as the first.
    """
    tail = stderr_tail(raw, limit=1)
    if not tail:
        return "no stderr captured"
    if len(tail) > chars:
        return tail[: chars - 1] + "…"
    return tail
