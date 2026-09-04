"""The ONE torn-import-tolerant route from a publisher to the publish-gate wedge detector.

WHAT BROKE (2026-09-04 15:48Z, live, in `sim_runner` -- the path that actually publishes in the
steady state). Both publishers report their outcome to
`process_run_complete.record_publish_gate_outcome` through a LAZY import inside a bare `try`, so
that a monitoring failure can never break the run loop it monitors. That is right and stays. What
it hid is that the import runs against a tree three lanes write concurrently, and it caught
`background/episode_monotonic.py` mid-write:

    publish-gate outcome recording failed (non-fatal): cannot import name
    'recorded_instant_seconds' from 'background.episode_monotonic'

The name was present at line 145 in HEAD and in the shared tree, and the file's mtime was 15:48Z.
Not a broken landing: **a torn read of a source file under a live daemon.**

WHY THAT IS WORSE THAN NON-FATAL. The outcome being routed is usually a FAILURE, and a failure
that never reaches the detector makes the episode read one failure SHORT of what happened. That is
exactly the under-reporting `episode_monotonic` exists to prevent -- an episode that reads shorter
than it was -- arriving by the one route the guard cannot see, because the guard is downstream of
the import that failed. The log line said "non-fatal", which is true of the loop and false of the
measurement.

SO A TORN IMPORT IS RETRIED, ONCE. It is transient by construction -- another writer was mid-write
when Python opened the file, and a moment later the file is whole -- and one more look is the
entire cost. Everything else still degrades to a log line and a `False`.

WHY THIS IS ITS OWN MODULE AND NOT A LOOP IN EACH CALLER. There were already two identical
wrappers, in `background_worker` and `sim_runner`, and a repair written into one of them is the
shape CLAUDE.md names as this project's most expensive: one requirement, several implementations,
fixed in one of them and still live in the other. I wrote it into `background_worker` first and
found the observed instance was in `sim_runner`. It lives here once instead.

It is deliberately a LEAF: `time` and nothing else at module scope. The import chain a caller opens
to reach this file cannot itself be torn by a write to the reporting stack, because it does not
touch the reporting stack -- and the caller's own `try` remains the last resort for the vanishing
case where this file is the one being written.
"""
from __future__ import annotations

import time

#: How long to wait before re-reading a module whose first read was torn by a concurrent writer.
#: A second: long enough to be past another lane's write, short enough to be free inside a sweep
#: whose cycle is measured in minutes.
IMPORT_RETRY_SECONDS = 1.0

#: Two attempts, not more. The window is one other lane's write; if the second read is still torn
#: the cause is not a tear, and a retry loop inside a monitoring path is a wedge of its own.
ATTEMPTS = 2


def route(marker, rc, *, kind=None, log=None, sleep=None):
    """Route one publisher's outcome to the wedge detector. Returns True iff it was recorded.

    `marker` is passed through untouched -- this module never parses it; the detector does.
    `log` is the caller's own logger so the line lands in the caller's log, which is where a
    reader diagnosing that daemon is already looking.

    NEVER RAISES, and the return value is the honest answer: `False` means the detector did not
    see this cycle, and the caller may not read that as a skip.
    """
    def _say(msg):
        if log is not None:
            log(msg)

    _sleep = sleep if sleep is not None else time.sleep
    last = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            from background import process_run_complete as prc
            prc.record_publish_gate_outcome(marker, rc, kind=kind)
            if attempt > 1:
                _say("publish-gate outcome recorded on attempt {} -- the first read of the "
                     "import chain was torn ({})".format(attempt, last))
            return True
        except (ImportError, SyntaxError) as exc:
            # THE TWO SHAPES A HALF-WRITTEN MODULE TAKES: Python either parses a truncated file
            # (SyntaxError) or parses it fine and finds a name that is not there yet
            # (ImportError). Both are transient; nothing else here is.
            last = exc
            if attempt < ATTEMPTS:
                _sleep(IMPORT_RETRY_SECONDS)
        except Exception as exc:  # noqa: BLE001 -- a monitoring failure may never break the loop
            # NOT RETRIED, DELIBERATELY. A detector that raises on real state will raise again a
            # second later, and re-running its side effects is how one bad cycle becomes two.
            last = exc
            break
    # "LOST", not "skipped" and not "non-fatal". Both of those read benign, and what happened is
    # that the wedge detector never saw a cycle it should have.
    _say("publish-gate outcome LOST: {} -- the wedge detector never saw this cycle, so the "
         "episode reads one outcome short of what happened. This is not a skip.".format(last))
    return False
