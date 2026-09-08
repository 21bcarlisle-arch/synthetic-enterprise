"""What is still in a bounded unit's cgroup at the moment it returns — and is therefore about to die.

THE HALF THE CENSUS CANNOT SEE. `tools/launch_shape_census.py` (9af8c855e) censuses committed launch
shapes over `git ls-files`, and it closes the committed half. Every one of the four deaths that
motivated the one-launcher work was a `/var/tmp/*.sh` that was never committed, so the census would
have caught NONE of them at the time. That limit is on the surface of the census's own finding
rather than in a footnote, deliberately. This module closes the other half, and it can only do so
by observing the RUNTIME: a file-reading control is blind to a file that is never in the tree.

WHY THE DISCRIMINATOR IS FREE HERE, AND NOWHERE ELSE. Both bounded units are `Type=oneshot` with
the default `KillMode=control-group`: when `ExecStart` returns, systemd SIGKILLs everything left in
the cgroup. Both of them also BLOCK on the child they legitimately spawned —
`worker_tick.run_tick()` on `proc.wait()`, `seat_executor.run_once()` on its own bounded turn — so
at the instant the `finally` runs, everything that was supposed to be here has already gone. The
rule is therefore the whole rule:

    anything in my cgroup, when I am about to return, that is not me, is about to be SIGKILLed

No allowlist, no age cutoff, no per-caller declaration of what busy means. That is the entire
reason this is wired into the exit path and not run as a periodic sweep over the same cgroups: a
sweep samples a bounded unit MID-WORK, where the legitimate child is present and indistinguishable
from a stray without exactly the tuned number this shape does not need.
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_A_TEARDOWN_CHECK_SEES_IN_A_LIVE_BOUNDED_CGROUP_2026-09-08.md`
recorded that prediction before the reading was taken, so the sweep was refused by a measurement
and not by a preference.

THIS REPORTS, IT DOES NOT RESCUE, AND THAT IS THE POINT. By the time the `finally` runs the job
cannot be saved — the kill is milliseconds away and nothing here can adopt a process out of a
doomed cgroup. What it buys is the thing whose absence actually cost the four launches: the
launcher's own docstring says "invisible is the state that cost four launches", and every one of
those deaths was found hours later by a person going to look. A named line at the instant of death,
carrying the doomed process's own command line, turns a silent disappearance into an event. That is
a smaller claim than a refusal and it is the honest one.

WHY A DOUBLE SAMPLE AND NOT A SINGLE READ. A child that has just exited can sit un-reaped for a
moment, and a check that reported it would fire on the ordinary path and be silenced within a day.
`_SETTLE_SECONDS` is not a tuned property of any job: it only has to exceed the gap between a
child's `exit()` and its reaping, and a LONG job — the only kind this exists for — survives any
window at all. Reporting the INTERSECTION of two samples means the failure mode is missing a
process that vanished on its own, which is precisely the case that was never a loss.

NOT A CONTROL THAT WATCHES A CONTROL. CLAUDE.md warns that a control guarding only your own
controls is usually not worth having, and that warning is why this was an open question rather than
a foregone yes. It does not apply: this watches the RUNTIME, the census watches the TREE, and the
population that killed us four times is visible only to the first. The two do not overlap in a
single process — a hand-rolled launch in a committed module is the census's, an uncommitted one is
this module's, and neither can see the other's.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

CGROUP_ROOT = Path("/sys/fs/cgroup")

#: Long enough to outlast the gap between a child's exit and its reaping; short enough to add
#: nothing meaningful to a tick that has already run for minutes. NOT a property of any job being
#: watched -- see the module docstring: a long job survives any settle window, so this number
#: cannot be wrong in the direction that matters.
_SETTLE_SECONDS = 0.5


def own_cgroup_procs_path(proc_root: Path | str = "/proc",
                          cgroup_root: Path | str = CGROUP_ROOT) -> Path | None:
    """The `cgroup.procs` of the cgroup this process is in, or None if it cannot be read.

    cgroup v2 gives one unified line, `0::<path>`. A v1 hierarchy or an unreadable `/proc` returns
    None, which every caller treats as "we did not look" and never as "nothing was there".
    """
    try:
        text = (Path(proc_root) / "self" / "cgroup").read_text()
    except Exception:  # noqa: BLE001 -- unreadable is not evidence of empty
        return None
    for line in text.splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3 and parts[0] == "0":
            return Path(cgroup_root) / parts[2].lstrip("/") / "cgroup.procs"
    return None


def _read_pids(procs_path: Path) -> set[int] | None:
    try:
        text = procs_path.read_text()
    except Exception:  # noqa: BLE001
        return None
    out = set()
    for line in text.splitlines():
        line = line.strip()
        if line.isdigit():
            out.add(int(line))
    return out


def _is_zombie(pid: int, proc_root: Path | str = "/proc") -> bool:
    """A process already dead and awaiting its reaping. Killing it takes nothing from anybody.

    Unreadable means the process has gone between the two reads, which is the same answer for our
    purposes: there is nothing here to lose.
    """
    try:
        for line in (Path(proc_root) / str(pid) / "status").read_text().splitlines():
            if line.startswith("State:"):
                return line.split()[1] == "Z"
    except Exception:  # noqa: BLE001
        return True
    return True


def describe(pid: int, proc_root: Path | str = "/proc") -> str:
    """The doomed process's own command line, so the report names WHAT died and not just a number.

    A pid alone is useless in a log read an hour later -- the process it named is gone by
    definition. `/proc/<pid>/cmdline` is NUL-separated; a kernel thread has an empty one, so fall
    back to `comm`.
    """
    base = Path(proc_root) / str(pid)
    try:
        raw = (base / "cmdline").read_bytes()
    except Exception:  # noqa: BLE001
        raw = b""
    argv = [p for p in raw.decode("utf-8", "replace").split("\0") if p]
    if argv:
        return " ".join(argv)[:400]
    try:
        return "[{}]".format((base / "comm").read_text().strip())
    except Exception:  # noqa: BLE001
        return "<gone>"


def doomed(*, me: int | None = None,
           proc_root: Path | str = "/proc",
           cgroup_root: Path | str = CGROUP_ROOT,
           settle_s: float = _SETTLE_SECONDS,
           sleep=time.sleep) -> tuple[list[dict], str | None]:
    """`(doomed, unreadable_reason)` — what will be SIGKILLed when this process returns.

    A non-empty list means a long job was launched from inside this bounded unit's cgroup and is
    about to die with it. `unreadable_reason` is set instead when we could not look; the two are
    never both meaningful, and an empty list with a reason set is NOT a clean verdict.
    """
    me = os.getpid() if me is None else me
    procs_path = own_cgroup_procs_path(proc_root, cgroup_root)
    if procs_path is None:
        return [], "this process's cgroup path could not be read, so nothing was checked"
    first = _read_pids(procs_path)
    if first is None:
        return [], "{} is unreadable, so nothing was checked".format(procs_path)
    candidates = {p for p in first if p != me}
    if not candidates:
        return [], None
    # Only now is the settle worth paying for: the ordinary tick reaches the line above and stops.
    sleep(settle_s)
    second = _read_pids(procs_path)
    if second is None:
        return [], "{} became unreadable mid-check, so nothing was concluded".format(procs_path)
    still = sorted(p for p in (candidates & second) if not _is_zombie(p, proc_root))
    return [{"pid": p, "cmdline": describe(p, proc_root)} for p in still], None


def report_line(found: list[dict], reason: str | None) -> str | None:
    """The one line a caller logs, or None when there is nothing to say.

    A reason is reported too: "we did not look" is a result and belongs on the surface, not in a
    footnote. It is phrased so it can never be read as a clean bill of health.
    """
    if reason:
        return "DOOMED-AT-TEARDOWN: NOT CHECKED -- " + reason
    if not found:
        return None
    return "DOOMED-AT-TEARDOWN: {} process(es) in this bounded unit's cgroup will be SIGKILLed " \
           "when it returns -- launch long jobs via background/launch_long_job.py: {}".format(
               len(found), "; ".join("{} ({})".format(f["pid"], f["cmdline"]) for f in found))


def check_and_log(log=None) -> str | None:
    """Wired into the `finally` of every bounded oneshot. NEVER raises, NEVER changes the outcome.

    A diagnostic that can fail its own caller is a worse defect than the one it reports: this runs
    on the exit path of the two processes that do all the unattended work here, including the path
    taken when they are already failing.
    """
    try:
        found, reason = doomed()
        line = report_line(found, reason)
    except Exception as e:  # noqa: BLE001 -- see docstring
        line = "DOOMED-AT-TEARDOWN: NOT CHECKED -- {!r}".format(e)
    if line and log is not None:
        try:
            log(line)
        except Exception:  # noqa: BLE001
            pass
    return line


def main(argv: list | None = None) -> int:  # pragma: no cover - operator surface
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable")
    args = ap.parse_args(argv)
    found, reason = doomed()
    if args.json:
        print(json.dumps({"doomed": found, "not_checked": reason}, indent=1))
    else:
        print(report_line(found, reason) or "nothing else in this cgroup")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
