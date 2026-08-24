"""The OOM door: did the kernel kill this unit's runs, or did they never happen?

PURPOSE. `supervisor._producer_starved_active` (RUNG 1d) decides the producer is down from
two inputs, and on 2026-08-24 both were blind to the same door for four hours:

  * `.sim_producer_state.json` -- written by `sim_runner` itself. An OOM kill takes the child
    down without a Python-level exception, so the producer records only the last run that
    failed *with a return code*. On the day this module was written that was a seven-second-old
    code error, reported as the standing condition while the actual condition was a
    forty-seven-minute run being killed at 13.2G.
  * the age of the newest `run_output_*.json` -- true, and consistent with BOTH "the runner is
    dead" and "the runner is running flat out and losing every time".

Neither input can tell those apart, so LIMB 2's message asserted the wrong one outright ("this
is not a run failing, it is runs NOT HAPPENING") and prescribed the wrong repair (restart it).
By the time it was read, systemd's restart counter stood at 13. A fourteenth restart is not a
repair, and the thirteen before it are the evidence.

WHAT THIS GUARANTEES. A third input, independent of both: systemd's own verdict on the unit,
which outlives the child, is written by neither the producer nor this repository, and is the
only record an OOM kill can leave. When it says the unit was OOM-killed, the doorbell names the
kill -- count, window, latest peak, restart counter -- instead of claiming the runs never ran.

WHY THIS IS NOT A NEW MECHANISM (OPS1). Nothing here schedules, holds, restarts or notifies. It
is a missing *reading* handed to a detector that already exists and already owns this decision.
The repair for the kills themselves is a memory decision and is not taken here.

NOT `measure_publish_gate_subject_cost._scope_oom_killed`, which is the nearest analogue (R4).
That asks the KERNEL log whether one named cgroup scope hit its OWN ceiling during one timed
phase, and answers True/False. This asks the USER journal how many times a long-lived unit has
been killed over a window, and needs the peak and the restart counter -- fields the kernel line
does not carry. Same doctrine, different source, different question.

FAIL-SILENT IS A FAILED CHECK (R15). An unreadable journal returns None, never an empty list.
None is NOT "no OOM happened": callers must say the door could not be read rather than fall
back to asserting the runs never ran, which is precisely the sentence this module exists to
stop being printed on no evidence.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass

#: The unit RUNG 1d is about. Named here because the supervisor asks about the producer, not
#: about a unit -- the mapping is this module's business.
PRODUCER_UNIT = "sim-runner.service"

#: How far back to ask. Wide enough that a chronic intermittent pattern (22 kills over five
#: days when this was written, clustered on three of them) reads as chronic rather than as a
#: single event, and narrow enough that a journal read stays a couple of seconds.
DEFAULT_SINCE = "-6h"

# systemd's own three lines, in the order it emits them. The unit name is required in each so
# that a caller supplying a wider journal cannot have another unit's kill counted as this one's
# -- `-u` already scopes the real reader, and this survives a reader that does not.
_RESULT_OOM = re.compile(r"^(?P<ts>\S+)\s.*?(?P<unit>\S+\.service): Failed with result 'oom-kill'\.")
_CONSUMED = re.compile(r"(?P<unit>\S+\.service): Consumed .*?(?P<peak>[\d.]+[KMGT]) memory peak")
_RESTART_COUNTER = re.compile(r"(?P<unit>\S+\.service): Scheduled restart job, restart counter is at (?P<n>\d+)")


#: systemd writes IEC suffixes. A bare number is bytes.
_SIZE_UNITS_MB = {"K": 1 / 1024, "M": 1.0, "G": 1024.0, "T": 1024.0 * 1024.0}


def parse_memory_size_mb(text: str) -> float | None:
    """`"13.5G"` -> 13824.0 MB. None when it does not parse -- never 0.0.

    Zero is a real peak (a unit that allocated nothing), so an unparseable size MUST NOT
    collapse to it: a caller comparing a declared weight against 0.0 would read every drift
    as clean, which is the FAIL-OPEN shape R15 names.
    """
    match = re.fullmatch(r"(?P<n>[\d.]+)(?P<unit>[KMGT]?)", (text or "").strip())
    if match is None:
        return None
    try:
        value = float(match.group("n"))
    except ValueError:
        return None
    unit = match.group("unit")
    return value * _SIZE_UNITS_MB[unit] if unit else value / (1024.0 * 1024.0)


def read_unit_memory_peaks_mb(
    unit: str = PRODUCER_UNIT,
    since: str = DEFAULT_SINCE,
    journal_reader=None,
) -> list[float] | None:
    """Every memory peak systemd recorded for `unit` in the window, in MB. None if unreadable.

    DIFFERENT QUESTION TO `read_oom_kills`, and deliberately not folded into it. That function
    attributes a peak to the kill it followed, so it can only ever see the peaks of runs that
    DIED. This one takes every peak systemd logged -- systemd emits `Consumed ... memory peak`
    on every stop, not only on a kill -- because the number that matters for sizing a job is
    what the job actually takes when it SURVIVES. Asking only the corpses biases the estimate
    low by exactly the runs that fitted.

    FAIL-SILENT IS A FAILED CHECK (R15). An unreadable journal returns None, never []. An
    empty list means "the journal answered and recorded no peak"; None means nobody knows.
    """
    reader = journal_reader or _run_journalctl
    try:
        text = reader(unit, since)
    except Exception:  # a reader that raises is a reader that did not answer
        return None
    if text is None:
        return None

    peaks: list[float] = []
    for line in text.splitlines():
        consumed = _CONSUMED.search(line)
        if consumed and consumed.group("unit") == unit:
            parsed = parse_memory_size_mb(consumed.group("peak"))
            if parsed is not None:
                peaks.append(parsed)
    return peaks


@dataclass(frozen=True)
class OomKill:
    """One kill, as systemd recorded it."""

    at: str
    peak: str | None = None
    restart_counter: int | None = None


def _run_journalctl(unit: str, since: str) -> str | None:
    """The journal text, or None if the question could not be put.

    `--grep` is server-side on purpose: this unit's own stdout is in the same journal and ran
    to 700k lines over six hours on the machine this was written for. Filtering here is the
    difference between a two-second read and a rung that times out.
    """
    if shutil.which("journalctl") is None:
        return None
    argv = [
        "journalctl", "--user", "-u", unit, "--since", since,
        "-o", "short-iso", "--no-pager",
        "--grep", "oom-kill|memory peak|restart counter is at",
    ]
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, errors="replace", timeout=60
        )
    except (OSError, subprocess.SubprocessError):
        return None
    # rc=1 is journalctl's "no entries matched", which is a real, clean answer -- not a failure
    # to read. Anything else is the journal declining to answer.
    if result.returncode not in (0, 1):
        return None
    return result.stdout


def read_oom_kills(
    unit: str = PRODUCER_UNIT,
    since: str = DEFAULT_SINCE,
    journal_reader=None,
) -> list[OomKill] | None:
    """Kills systemd recorded for `unit` in the window, newest last. None if unreadable.

    `journal_reader` takes (unit, since) and returns journal text; injected so the parse can be
    mutation-tested against a synthetic record without a systemd on the box (R15).
    """
    reader = journal_reader or _run_journalctl
    try:
        text = reader(unit, since)
    except Exception:  # a reader that raises is a reader that did not answer
        return None
    if text is None:
        return None

    kills: list[OomKill] = []
    for line in text.splitlines():
        match = _RESULT_OOM.match(line)
        if match and match.group("unit") == unit:
            kills.append(OomKill(at=match.group("ts")))
            continue
        if not kills:
            # A peak or a counter with no kill ahead of it belongs to a kill outside the
            # window, or to an ordinary restart. Neither is ours to attribute.
            continue
        consumed = _CONSUMED.search(line)
        if consumed and consumed.group("unit") == unit and kills[-1].peak is None:
            kills[-1] = OomKill(
                at=kills[-1].at,
                peak=consumed.group("peak"),
                restart_counter=kills[-1].restart_counter,
            )
            continue
        counter = _RESTART_COUNTER.search(line)
        if counter and counter.group("unit") == unit and kills[-1].restart_counter is None:
            kills[-1] = OomKill(
                at=kills[-1].at,
                peak=kills[-1].peak,
                restart_counter=int(counter.group("n")),
            )
    return kills


def producer_oom_clause(
    unit: str = PRODUCER_UNIT,
    since: str = DEFAULT_SINCE,
    journal_reader=None,
) -> str | None:
    """The sentence RUNG 1d should print instead of guessing, or None when there is nothing.

    Three outcomes, and the middle one is the whole point:

      * kills found -> a clause naming them and refusing the restart prescription;
      * journal unreadable -> a clause SAYING it is unreadable, so the doorbell never asserts
        "runs are NOT HAPPENING" on evidence it failed to obtain (R15 fail-silent);
      * journal clean -> None, and the caller's existing wording stands.
    """
    kills = read_oom_kills(unit=unit, since=since, journal_reader=journal_reader)
    if kills is None:
        return (
            f"THE OOM DOOR COULD NOT BE READ (`journalctl --user -u {unit}`), so whether the "
            f"runs are absent or merely being killed is UNKNOWN here -- an unavailable check is "
            f"a failed check (R15), not a clean one. Establish it before accepting any account "
            f"of this outage that rests on the runs never having started."
        )
    if not kills:
        return None

    latest = kills[-1]
    peak = latest.peak or "peak not recorded"
    counter = (
        f", and systemd's restart counter stands at {latest.restart_counter}"
        if latest.restart_counter is not None
        else ""
    )
    return (
        f"THE RUNS ARE HAPPENING AND THE KERNEL IS KILLING THEM: systemd recorded "
        f"{len(kills)} OOM kill(s) of {unit} since {since}, the latest at {latest.at} at "
        f"{peak}{counter}. So this is NOT a dead producer and NOT a restart problem -- a "
        f"restart is what has already happened once per kill. The producer's own state file "
        f"cannot show this (an OOM kill leaves no Python-level exception to record), which is "
        f"why it may name some older, unrelated, already-fixed error as the standing condition. "
        f"The repair is a MEMORY decision -- the guest's allocation or the run's own footprint "
        f"-- and the host-allocation half is the director's. Diagnose against "
        f"`docs/staging/done/WORKER_FINDING_THE_PRODUCER_IS_NOT_DEAD_IT_IS_OOM_KILLED_TWELVE_"
        f"TIMES_TODAY_2026-08-24.md` before opening anything new: this door is already surveyed."
    )
