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

#: Rendered when a stream was never piped at all, as opposed to piped and empty.
#: The two are different defects — "nobody looked" is a bug in the LAUNCH SITE,
#: "the child said nothing" is a fact about the child — and a reader who cannot
#: tell them apart re-diagnoses the wrong one. `None` reaches here for both, so
#: the launch site says which by passing `piped=`.
NOT_PIPED = "not captured by the launch site (stream was not piped)"
SAID_NOTHING = "empty (the child wrote nothing to it)"


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


def child_output_excerpt(stdout: object, stderr: object, *,
                         stdout_piped: bool = True, stderr_piped: bool = True,
                         limit: int = STDERR_TAIL_LINES) -> str:
    """BOTH streams of a failed child, labelled — the excerpt a wedge diagnosis starts from.

    WHY THIS EXISTS, AND WHY `stderr_tail` WAS NOT ENOUGH (2026-08-21, a 32-hour
    publishing outage that logged zero diagnostic characters per cycle).
    `background_worker.process_leftover_run_markers` launches the publisher with
    `stderr=subprocess.PIPE` and NOTHING for stdout, under a comment that says
    "Capture what the publisher actually said." It does not: the publisher's
    `log()` writes its narrative — including *every* refusal it can issue — to
    **stdout**. So the one line the worker log offers a reader is

        Failed to process run_complete_….md (rc=1) — will retry next cycle
          publisher stderr (last 40 lines):
          WARNING (pytensor.configdefaults): g++ not detected! …
          … SyntaxWarning: "\\_" is an invalid escape sequence …

    — four lines of library noise, identical on all 46 refusals across 2026-08-20/21,
    while the sentence that actually names the cause ("Fast test suite timed out
    (>300s)", "Scoped publish-path gate FAILED") went to an fd the daemon's parent
    points at a socket. `sim_runner`'s auto-process branch is the same shape and goes
    further: it tells the reader "the refusing gate is named in the publisher log
    tail" — of a tail that structurally cannot name it.

    THE POSITIONAL TAIL IS THE SECOND HALF OF THE DEFECT. Even given the right
    stream, `lines[-limit:]` selects by POSITION, and the last lines of a noisy
    stream are whatever the runtime happened to warn about last. Selecting by
    position is only safe on a stream that IS the child's log — which stdout is
    here and stderr is not. So this renders both and lets the reader see which is
    which, rather than picking one and being silently wrong about it.

    BOTH, NEVER ONE. Preferring stdout would fail-open the other way: a child that
    dies on an uncaught traceback says nothing on stdout and everything on stderr.
    A helper that guessed would be right most of the time, which is the property
    that makes a diagnostic untrustworthy exactly when it is needed. Cost of showing
    both is a few log lines; cost of guessing wrong is another 32-hour outage
    diagnosed by hand.

    Total, like the rest of this module: bytes/str/None/MagicMock all render, and
    a stream that was never piped is reported as such rather than as silence (R15 —
    an unavailable check is a FAILED check, and an unavailable *diagnostic* must not
    read as a clean one).
    """
    parts = []
    for name, raw, piped in (("stdout", stdout, stdout_piped),
                             ("stderr", stderr, stderr_piped)):
        if not piped:
            parts.append("  child {}: {}".format(name, NOT_PIPED))
            continue
        tail = stderr_tail(raw, limit=limit)
        if tail:
            parts.append("  child {} (last {} lines):\n{}".format(name, limit, tail))
        else:
            parts.append("  child {}: {}".format(name, SAID_NOTHING))
    return "\n".join(parts)


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
