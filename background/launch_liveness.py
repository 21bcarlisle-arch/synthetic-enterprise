"""A launch record that can be RE-ASKED, so "the run is in flight" is a claim with an expiry.

THE DEFECT THIS EXISTS FOR, and it has now cost four launches of one job.
`SEAT_PREREGISTRATION_WHAT_THE_CURRENT_BOOK_RETAKE_OF_THE_LEVEL_SELECTION_SPLIT_CAN_AND_CANNOT_SETTLE_2026-09-07.md`
opens "The run is in flight." Its subject was a corpse within minutes and the sentence stood
unchallenged for six hours, then was corrected by hand, then the correction's own relaunch died and
*it* asserted liveness for another two. Every one of those claims was true when typed. Nothing in
the architecture could notice any of them going false, because a launch-time claim is written once
and read forever, and the only thing that ever caught one was a person going and looking at a pid.

SO THE SUBJECT HERE IS THE CLAIM, NOT THE JOB. `tools/wait_for.py` already answers "is it alive
right now" better than anything written here could -- with a deadline, a named subject and no
self-match. What it cannot do is be asked again tomorrow by whoever reads the document. This module
holds a record that a later reader re-asks, and the answer comes from OUTSIDE the job.

WHY OUTSIDE IS THE WHOLE POINT (`SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME…_2026-09-08.md`). The
09-07 relaunch wrote an rc file precisely so "gone" could be told from "gone with rc=137". It could
not: a SIGKILL to the tick's cgroup takes the wrapper too, so the rc file is absent in exactly the
case it was built to describe. **An exit-status file written by the process being killed cannot
report its own kill.** The transient user unit that finally carried the job to completion is also
what makes the verdict askable, because systemd holds an exit record the job had no part in
writing. `reask()` asks systemd FIRST and treats the rc file as corroboration only.

AND IT FAILS CLOSED ON A BROKEN PROBE. If `systemctl` cannot be run at all we return UNREADABLE and
say so, rather than reading "no unit" as "it died" -- reporting a death because we could not look is
the failure mode that would make this module worse than the hand-check it replaces.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
RECORDS_PATH = _REPO / "docs" / "observability" / ".launch_records.json"

#: The claim a record carries. `live` is what a launch writes; the other three are what a re-ask
#: settles it to. A record NEVER moves back to `live` -- see `check()`.
LIVE = "live"
FINISHED = "finished"
DIED = "died"
UNKNOWN = "unknown"
#: Not a state a record settles to: it is what a re-ask returns when the probe itself is broken.
UNREADABLE = "unreadable"
RUNNING = "running"

#: The ActiveStates systemd reports for a unit that has not finished. `deactivating` is included
#: deliberately: a job in its own teardown has not yet produced an exit record, and calling that
#: dead is the same guess this module exists to refuse.
_STILL_GOING = ("active", "activating", "reloading", "deactivating")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def systemd_probe(unit: str) -> dict | None:
    """What the user manager holds about `unit`, or None if the probe could not be RUN.

    None means "we could not look" and is not the same as an empty answer, which means "systemd
    looked and has no such unit". The caller must keep them apart; conflating them is how a
    control reports a death it never observed.
    """
    try:
        out = subprocess.check_output(
            ["systemctl", "--user", "show", unit,
             "-p", "ActiveState", "-p", "Result", "-p", "ExecMainStatus", "-p", "LoadState"],
            text=True, timeout=15, stderr=subprocess.DEVNULL)
    except Exception:
        return None
    fields = {}
    for line in out.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            fields[key.strip()] = value.strip()
    return fields


def reask(entry: dict, probe=systemd_probe) -> dict:
    """Ask, now, what became of the job this record was written for.

    THE ORDER IS THE ARGUMENT. systemd is asked before the artefact and long before the rc file,
    because a unit that is still active outranks an artefact that has not appeared yet, and a
    non-success `Result` outranks an absent rc file that a group kill would have prevented being
    written. The rc file only ever corroborates.
    """
    unit = entry.get("unit")
    fields = probe(unit) if unit else {}
    if fields is None:
        return {"verdict": UNREADABLE, "why": (
            f"`systemctl --user show {unit}` could not be run, so nothing here knows whether the "
            "job is alive. This is NOT a death: it is the absence of a probe, and the two are "
            "different states.")}

    state = (fields or {}).get("ActiveState") or ""
    if state in _STILL_GOING:
        return {"verdict": RUNNING, "why": (
            f"the user manager reports `{unit}` ActiveState={state}, which is a verdict from "
            "outside the job's own cgroup and therefore survives the kill it would report")}

    artefact = entry.get("artefact")
    on_disk = bool(artefact) and Path(artefact).exists()
    rc = _read_rc(entry.get("rc_path"))
    result = (fields or {}).get("Result") or ""
    status = (fields or {}).get("ExecMainStatus") or ""

    if on_disk and rc in (0, None) and result in ("success", ""):
        return {"verdict": FINISHED, "why": (
            f"the artefact `{artefact}` exists, the unit's Result={result or 'unrecorded'} and "
            f"ExecMainStatus={status or 'unrecorded'}, and the job's own rc file says "
            f"{'nothing' if rc is None else rc}")}

    if result and result != "success":
        return {"verdict": DIED, "why": (
            f"the user manager reports `{unit}` Result={result} "
            f"(ExecMainStatus={status or 'unrecorded'}) and no artefact at `{artefact}`. THIS IS "
            "THE VERDICT THE RC FILE COULD NOT GIVE: a group kill takes the wrapper that would "
            "have written it, so its absence is the signature and not the diagnosis.")}
    if status and status not in ("0", ""):
        return {"verdict": DIED, "why": (
            f"the user manager reports `{unit}` ExecMainStatus={status} and no artefact at "
            f"`{artefact}`")}

    return {"verdict": UNKNOWN, "why": (
        f"the user manager holds no exit record for `{unit}` (LoadState="
        f"{(fields or {}).get('LoadState') or 'unrecorded'}) and there is no artefact at "
        f"`{artefact}`. We cannot tell whether it ran -- most likely the unit was collected, "
        "which is why `--collect` must not be passed to a job whose death anyone will ask about.")}


def _read_rc(rc_path) -> int | None:
    if not rc_path:
        return None
    try:
        return int(Path(rc_path).read_text(encoding="utf-8").strip())
    except Exception:
        return None


def load(path: Path | None = None) -> list:
    try:
        data = json.loads((path or RECORDS_PATH).read_text(encoding="utf-8"))
    except Exception:
        return []
    return data if isinstance(data, list) else []


def save(records: list, path: Path | None = None) -> None:
    target = path or RECORDS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


def record(job: str, unit: str, artefact: str, *, log: str | None = None,
           rc_path: str | None = None, asserted_live_by: list | None = None,
           launched_at: str | None = None, path: Path | None = None) -> dict:
    """Write (or replace) the launch record for `job`. Always writes the claim `live`.

    `asserted_live_by` names the documents that state this run is in flight. It is what turns a
    contradiction into an address: the check does not just say a claim went stale, it says which
    pages are now wrong.
    """
    entry = {
        "job": job,
        "unit": unit,
        "artefact": artefact,
        "log": log,
        "rc_path": rc_path,
        "launched_at": launched_at or _now(),
        "asserted_live_by": list(asserted_live_by or []),
        "claim": LIVE,
        "settled_at": None,
        "evidence": None,
    }
    records = [r for r in load(path) if r.get("job") != job]
    records.append(entry)
    save(records, path)
    return entry


def check(path: Path | None = None, probe=systemd_probe) -> tuple[int, list, list]:
    """Re-ask every record still claiming `live`; settle the ones that are not, and say so.

    RETURNS `(stale, lines, settled)`. `settled` carries the records this call moved, each with the
    verdict that moved it, because A DEATH AND A COMPLETION ARE NOT THE SAME EVENT and only the
    caller can know what to do about that. Both contradict a document that says "in flight", which
    is why both count as stale; but one is an incident and the other is the good news the run was
    launched for. Handing back only a COUNT forced the caller to choose one severity for both, and
    the first version of the deadman wiring duly paged a `real_alarm` for a job that had succeeded
    -- crying wolf on the director's own channel, which is how this project has buried its signal
    before. The split has to exist here, at the point where the verdict is known.

    THE CONTRADICTION IS THE OUTPUT, and the writeback is what stops it being a nag. A record that
    the re-ask settles keeps the verdict and the evidence, so the next reader of the documents in
    `asserted_live_by` is contradicted by a file rather than by a person who thought to check a
    pid. Exit 1 the ONE time a stale claim is caught; green afterwards is correct, because the
    claim is no longer stale.

    A RECORD NEVER RETURNS TO `live`. Settling is one-way and only ever on evidence held outside
    the job: an UNREADABLE probe settles nothing, and neither does UNKNOWN, because "we could not
    tell" is not permission to overwrite what the launch said.
    """
    records, lines, settled = load(path), [], []
    for entry in records:
        if entry.get("claim") != LIVE:
            continue
        answer = reask(entry, probe=probe)
        verdict = answer["verdict"]
        lines.append(f"{entry.get('job')}: {verdict.upper()} -- {answer['why']}")
        if verdict == RUNNING:
            continue
        if verdict in (UNREADABLE, UNKNOWN):
            lines.append(
                f"  (claim left at `live`: {verdict} is not evidence the job ended)")
            continue
        entry["claim"] = FINISHED if verdict == FINISHED else DIED
        entry["settled_at"] = _now()
        entry["evidence"] = answer["why"]
        settled.append(entry)
        for doc in entry.get("asserted_live_by") or []:
            lines.append(f"  CONTRADICTS {doc} -- it says this run is in flight; it is not")
    if settled:
        save(records, path)
    return len(settled), lines, settled


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="re-ask every live claim and settle the ones that are stale")
    parser.add_argument("--record", metavar="JOB", help="write a launch record for JOB")
    parser.add_argument("--unit", help="the transient user unit the job runs in")
    parser.add_argument("--artefact", help="the path the job writes on success")
    parser.add_argument("--log")
    parser.add_argument("--rc-path")
    parser.add_argument("--asserted-live-by", action="append", default=[],
                        help="a document that states this run is in flight (repeatable)")
    # A job is often recorded LONG after it was launched -- the first real use of this module was
    # a floor leg recorded three hours in, because the module was written after the launch. Without
    # this flag `launched_at` silently becomes the moment someone got round to recording, which is
    # the one field a later reader uses to judge how long the claim has stood. Defaulting to now is
    # right for a fresh launch and wrong for every retrofit, so the retrofit has to be able to say.
    parser.add_argument("--launched-at", metavar="ISO8601",
                        help="when the job ACTUALLY started, if that is not now")
    args = parser.parse_args(argv)

    if args.record:
        if not args.unit or not args.artefact:
            print("--record needs --unit and --artefact: a record with neither cannot be re-asked")
            return 2
        entry = record(args.record, args.unit, args.artefact, log=args.log,
                       rc_path=args.rc_path, asserted_live_by=args.asserted_live_by,
                       launched_at=args.launched_at)
        print(f"recorded {entry['job']} -> unit {entry['unit']}, claim {entry['claim']}")
        return 0

    stale, lines, _ = check()
    for line in lines:
        print(line)
    if stale:
        print(f"check: FAIL ({stale} launch record(s) claimed live and are not)")
        return 1
    print("check: PASS (no stale liveness claim)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
