"""The only legal way to wait for something. Named subject, mandatory deadline, cannot
wait for itself.

THE DIRECTOR, three times in one week, most recently 2026-08-27: *"you still have a
background shell polling for a pytest process that ended eleven hours ago -- third time this
week. A waiter whose subject has gone looks exactly like work in progress, so the shell
indicator now tells neither of us anything. Give waiters a deadline and make them say what
they're waiting for."*

WHAT THE THIRD ONE ACTUALLY WAS, and it is not carelessness. The shell was::

    until ! pgrep -f "pytest tests/simulation/test_live_population" >/dev/null;
    do sleep 15; done

`pgrep -f` matches against the FULL command line, and a background shell is spawned as
`bash -c '<the whole loop>'` -- so the pattern is sitting in the waiter's own cmdline. The
loop was matching ITSELF. Its exit condition was unreachable from the first second, and the
pytest it named had already finished. Twelve hours of a shell indicator that meant nothing,
and no deadline to end it.

That makes this a CLASS defect (R10), not an instance: *every* inline `pgrep -f` waiter
written through the Bash tool self-matches, by construction. Adding a deadline to that
particular loop would have capped the damage and left the mechanism intact. So the fix is a
waiter that cannot be written the broken way:

  * **A deadline is REQUIRED.** No default, no "0 means forever", and a hard ceiling. A
    waiter that can outlive the thing it waits for is the whole complaint.
  * **Self-exclusion is structural.** This process and every one of its ancestors are
    struck out of the match set before anything is counted, so a pattern that appears in
    the waiter's own command line matches nothing rather than matching forever.
  * **An absent subject REFUSES rather than waits.** If nothing matches when we start (and
    nothing appears inside `--start-grace`), the exit is non-zero and immediate. The orphan
    case -- waiting for something that already ended -- becomes a ten-second failure
    instead of a twelve-hour impression of work.
  * **The output says what it is waiting for.** A heartbeat line carrying subject, elapsed
    and deadline, so the output file is self-describing to whoever finds it, including me.

`--pid` is strictly better than `--pattern` where a PID is available: a PID cannot
self-match and cannot be ambiguous. Prefer it.

FAIL-CLOSED, WITH THE DISTINCTION THAT MATTERS (see the standing lesson about controls that
refuse on input they could not READ): if `pgrep` itself cannot be run, that is a broken
probe, not an absent subject, and we exit UNREADABLE rather than reporting the subject gone.
Reporting "finished" because we could not look is the failure mode that would let this tool
tell a caller a run had completed when it had not.

EXIT CODES -- distinct because the caller's next move differs for each:
  0  FINISHED      the subject was there and is now gone; this is the success we wait for
  1  DEADLINE      still running when the deadline expired
  2  NEVER_STARTED nothing ever matched; probably already over before we looked
  3  UNREADABLE    the probe could not be run; we do not know and refuse to guess

THERE IS DELIBERATELY NO "SELF_MATCH" VERDICT, and the reason is worth keeping. The first
draft had one, and writing its test showed it would fire on every honest answer: a pattern
passed as `--pattern X` is on THIS process's own argv by definition, so "the only matches
were us" is the normal state whenever the subject is not running. A verdict that cannot
distinguish the bug from the ordinary case is not a diagnosis. The exclusion set is the cure;
the self-match count rides along in the detail string as information, so a caller whose
pattern matched nothing but the waiter can see exactly that without it being mistaken for a
different outcome.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

# A waiter that could be handed a week is the defect wearing an argument. Six hours is
# longer than the slowest thing in this repo (a full decade sim run) by a wide margin, and
# anything genuinely longer wants a marker file and a cold start, not a live shell.
MAX_DEADLINE_SECONDS = 6 * 3600

DEFAULT_POLL_SECONDS = 15.0
DEFAULT_HEARTBEAT_SECONDS = 300.0

FINISHED = "FINISHED"
DEADLINE = "DEADLINE"
NEVER_STARTED = "NEVER_STARTED"
UNREADABLE = "UNREADABLE"

EXIT_CODES = {FINISHED: 0, DEADLINE: 1, NEVER_STARTED: 2, UNREADABLE: 3}


class ProbeUnreadable(Exception):
    """The probe could not be run. Distinct from "the subject is not there" -- conflating
    the two is what makes a fail-closed control refuse on input it never read.

    `verdict` is what `wait()` reports for this failure. It lives on the exception rather
    than in a chain of `isinstance` checks inside `wait()` so that a new probe failure can
    name its own verdict without the wait loop learning about it."""

    verdict = UNREADABLE


# ---------------------------------------------------------------------------
# self-exclusion
# ---------------------------------------------------------------------------

def _ppid_of(pid: int) -> int | None:
    """The parent of `pid` from /proc, or None if it cannot be read."""
    try:
        with open("/proc/{}/status".format(pid), "r") as fh:
            for line in fh:
                if line.startswith("PPid:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return None


def self_and_ancestors(pid: int | None = None, ppid_of=_ppid_of, limit: int = 64) -> set[int]:
    """This process and every process above it, up to init.

    THE ANCESTORS ARE THE POINT, not belt-and-braces. A background shell runs as
    `bash -c '<command>'` and Python is its child, so the pattern the caller passed us lives
    on the PARENT's command line, not ours. Excluding only `os.getpid()` would have caught
    nothing at all on 2026-08-27.

    `limit` bounds the walk: /proc can be read mid-reparent and a cycle here would hang the
    tool inside the function meant to stop hangs.
    """
    pid = os.getpid() if pid is None else pid
    seen: set[int] = set()
    current = pid
    for _ in range(limit):
        if current is None or current <= 0 or current in seen:
            break
        seen.add(current)
        current = ppid_of(current)
    return seen


def _is_probe_noise(cmdline: str) -> bool:
    """True for lines that are the act of looking rather than the thing looked for.

    A `pgrep`/`grep` carrying the pattern is not a running subject, and neither is an
    editor with the file open. Kept narrow deliberately: over-filtering here would make a
    LIVE subject invisible, which is the more dangerous direction -- we would report
    FINISHED for something still running.
    """
    head = cmdline.split()[0].rsplit("/", 1)[-1] if cmdline.split() else ""
    return head in ("pgrep", "grep", "egrep", "fgrep")


def matching_pids(pattern: str, exclude: set[int], runner=None) -> tuple[list[int], int]:
    """PIDs whose full command line contains `pattern`, minus ourselves.

    Returns `(kept, raw_count)`. The raw count is what separates SELF_ONLY from
    NEVER_STARTED: if the pattern matched three processes and all three were us, the caller
    wrote the 2026-08-27 bug and deserves to be told that, not told the subject was absent.

    Raises `ProbeUnreadable` if pgrep could not be run at all. Note that pgrep exits 1 for
    "no matches", which is an ANSWER and not a failure -- only a non-{0,1} exit or an OSError
    means we could not look.
    """
    runner = runner or _run_pgrep
    try:
        rc, out = runner(pattern)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProbeUnreadable("pgrep could not be run: {}".format(exc)) from exc
    if rc not in (0, 1):
        raise ProbeUnreadable("pgrep exited {} for pattern {!r}".format(rc, pattern))

    raw = 0
    kept: list[int] = []
    for line in out.splitlines():
        pid_text, _, cmdline = line.strip().partition(" ")
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if _is_probe_noise(cmdline):
            continue
        raw += 1
        if pid not in exclude:
            kept.append(pid)
    return kept, raw


def _run_pgrep(pattern: str) -> tuple[int, str]:
    r = subprocess.run(["pgrep", "-af", pattern], capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout


def pid_is_alive(pid: int) -> bool:
    """Whether `pid` exists. `/proc` rather than `os.kill(pid, 0)` because the latter
    raises PermissionError for a live process owned by someone else, and a live process we
    may not signal is still very much not finished."""
    return os.path.exists("/proc/{}".format(pid))


# ---------------------------------------------------------------------------
# the wait
# ---------------------------------------------------------------------------

def wait(subject: str, deadline_s: float, probe, start_grace_s: float = 0.0,
         poll_s: float = DEFAULT_POLL_SECONDS,
         heartbeat_s: float = DEFAULT_HEARTBEAT_SECONDS,
         clock=time.monotonic, sleep=time.sleep, emit=print) -> dict:
    """Wait until `probe()` reports the subject gone, or the deadline.

    `probe` returns `(present: bool, detail: str)` and may raise `ProbeUnreadable`.

    THE SHAPE THAT MATTERS is that "never present" and "present then gone" are different
    verdicts. A waiter that treats an absent subject as a finished one reports success for
    a run that never happened -- and reports it in the same second, which reads as a very
    fast pass rather than a mistake.

    `clock` is monotonic: a wall clock going backwards (NTP, DST) could otherwise extend a
    deadline indefinitely, which is the failure this tool exists to prevent.
    """
    if deadline_s <= 0:
        raise ValueError("a waiter needs a positive deadline; got {}".format(deadline_s))
    if deadline_s > MAX_DEADLINE_SECONDS:
        raise ValueError(
            "deadline {}s exceeds the {}s ceiling -- something this long wants a marker "
            "file and a cold start, not a live shell".format(deadline_s, MAX_DEADLINE_SECONDS))

    started = clock()
    ever_present = False
    last_heartbeat = started
    detail = ""

    emit("WAITING for {} -- deadline {:.0f}s".format(subject, deadline_s))

    while True:
        try:
            present, detail = probe()
        except ProbeUnreadable as exc:
            return _outcome(exc.verdict, subject, clock() - started, deadline_s, str(exc),
                            ever_present, emit)

        if present:
            ever_present = True
        elif ever_present:
            return _outcome(FINISHED, subject, clock() - started, deadline_s, detail,
                            ever_present, emit)
        elif (clock() - started) >= start_grace_s:
            return _outcome(NEVER_STARTED, subject, clock() - started, deadline_s, detail,
                            ever_present, emit)

        elapsed = clock() - started
        if elapsed >= deadline_s:
            return _outcome(DEADLINE, subject, elapsed, deadline_s, detail, ever_present, emit)

        if heartbeat_s and (clock() - last_heartbeat) >= heartbeat_s:
            last_heartbeat = clock()
            emit("still waiting for {} -- {:.0f}s of {:.0f}s; {}".format(
                subject, elapsed, deadline_s, detail))

        sleep(min(poll_s, max(0.0, deadline_s - elapsed)))


def _outcome(verdict: str, subject: str, waited: float, deadline_s: float, detail: str,
             ever_present: bool, emit) -> dict:
    emit("{} after {:.0f}s waiting for {} (deadline {:.0f}s){}".format(
        verdict, waited, subject, deadline_s, " -- " + detail if detail else ""))
    return {"verdict": verdict, "subject": subject, "waited_seconds": round(waited, 1),
            "deadline_seconds": deadline_s, "detail": detail, "ever_present": ever_present,
            "exit_code": EXIT_CODES[verdict]}


def pattern_probe(pattern: str, exclude: set[int] | None = None, matcher=matching_pids):
    """A `probe` for `wait()` that looks for processes matching `pattern`.

    Closes over the exclusion set ONCE, at construction. Recomputing the ancestry on every
    poll would be correct but slower, and worse: if this process were reparented to init
    mid-wait, a later recomputation would drop the real ancestor and the waiter could start
    matching a sibling shell that merely carries the same words.
    """
    exclude = self_and_ancestors() if exclude is None else exclude

    def probe() -> tuple[bool, str]:
        pids, raw = matcher(pattern, exclude)
        if pids:
            return True, "pid " + ", ".join(str(p) for p in pids)
        # `raw` counts matches BEFORE exclusion. When the subject is absent it is almost
        # always >= 1, because the pattern is on our own argv -- saying so is what stops a
        # reader concluding the probe is broken when it is working exactly as intended.
        return False, ("no process matches {!r}{}".format(
            pattern,
            " ({} match{} excluded as this waiter or its ancestors)".format(
                raw, "" if raw == 1 else "es") if raw else ""))

    return probe


def pid_probe(pid: int, alive=pid_is_alive):
    def probe() -> tuple[bool, str]:
        return alive(pid), "pid {}".format(pid)
    return probe


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wait_for",
        description="Wait for a named subject to finish, with a deadline it cannot outlive.")
    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--pid", type=int,
                        help="wait for this PID to exit. PREFER THIS: a PID cannot match "
                             "the waiter's own command line.")
    target.add_argument("--pattern",
                        help="wait for processes whose full cmdline contains this. This "
                             "process and its ancestors are excluded from the match.")
    # required=True is the load-bearing word in this file.
    p.add_argument("--deadline", type=float, required=True,
                   help="seconds to wait before giving up. REQUIRED -- max {}.".format(
                       MAX_DEADLINE_SECONDS))
    p.add_argument("--subject", required=True,
                   help="what you are waiting for, in words, for whoever finds the output.")
    p.add_argument("--start-grace", type=float, default=0.0,
                   help="seconds to allow the subject to APPEAR before declaring it never "
                        "started. Default 0: if it is not there when we look, say so now.")
    p.add_argument("--poll", type=float, default=DEFAULT_POLL_SECONDS)
    p.add_argument("--heartbeat", type=float, default=DEFAULT_HEARTBEAT_SECONDS)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = pid_probe(args.pid) if args.pid else pattern_probe(args.pattern)
    try:
        outcome = wait(args.subject, args.deadline, probe,
                       start_grace_s=args.start_grace, poll_s=args.poll,
                       heartbeat_s=args.heartbeat)
    except ValueError as exc:
        print("REFUSED: {}".format(exc))
        return EXIT_CODES[UNREADABLE]
    return outcome["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
