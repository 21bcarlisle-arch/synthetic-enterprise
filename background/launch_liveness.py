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

#: Where a finished job's named artefact stands relative to git -- see `landing_verdict()`.
LANDED = "landed"
STAGED = "staged"
UNTRACKED = "untracked"
#: Not gradeable, and each for a different reason: the job wrote nothing, or wrote outside the
#: repository, or is still writing, or git is under standing orders not to hold it. None of these
#: is a defect and none of them is a pass.
ABSENT = "absent"
OUTSIDE = "outside"
IGNORED = "ignored"


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


def git_membership(rel: str, repo: Path) -> dict | None:
    """Where `rel` stands in git: `{"head": bool, "index": bool}`, or None if git could not be RUN.

    The two questions are asked separately on purpose. `git ls-files` reads the INDEX, and a path
    that is only in the index has not reached any commit -- a `reset --mixed` loses it and no
    clone has ever seen it. A control that asked only `ls-files` would have called such a path
    tracked, which is the exact reading that has already made one control here green while the
    thing it guarded was absent from every commit.

    None is reserved for a broken probe. It is NOT "the path is missing": `cat-file -e` exits
    non-zero for an absent path and for an unreadable repository alike, so health is established
    first and only then is the answer trusted.
    """
    try:
        healthy = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "HEAD"],
            capture_output=True, timeout=20)
        if healthy.returncode != 0:
            return None
        head = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"HEAD:{rel}"],
            capture_output=True, timeout=20)
        index = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", rel],
            capture_output=True, timeout=20)
        # The third question, and the first draft of this check did not ask it. `.gitignore` holds
        # `docs/observability/*.log`, so the very first path this control called stranded was a
        # 247MB run log git is under standing orders never to hold. "Not in git" and "must not be
        # in git" look identical from the index and mean opposite things.
        ignored = subprocess.run(
            ["git", "-C", str(repo), "check-ignore", "-q", "--", rel],
            capture_output=True, timeout=20)
    except Exception:
        return None
    return {"head": head.returncode == 0, "index": index.returncode == 0,
            "ignored": ignored.returncode == 0}


#: The fields of a record that name a file the job produced. `artefact` is the result and the other
#: two are the evidence it ran; all three are graded, because the hazard is identical and the first
#: real instance this check caught was a `log` -- the only surviving local trace of a run of
#: machine-hours, which an artefact-only reading called clean while it sat in no commit.
_PRODUCED_FIELDS = ("artefact", "log", "rc_path")


def named_paths(entry: dict) -> list:
    """The `(field, path)` pairs this record claims the job wrote. Empty fields are not pairs."""
    return [(f, entry[f]) for f in _PRODUCED_FIELDS if entry.get(f)]


def landing_verdict(entry: dict, field: str = "artefact", *, repo: Path | None = None,
                    membership=git_membership, probe=systemd_probe) -> dict:
    """Did the file this record NAMES in `field` reach git, or is it stranded on one machine's disk?

    THE DEFECT THIS EXISTS FOR. A long job's whole output is one file whose path the launch record
    already holds. Twice in three days a run of machine-hours finished, wrote that file, and the
    file sat untracked in this tree while the register recorded the job as `finished` and every
    reader took that to mean the work had landed. Nothing could notice, because `finished` is a
    claim about a PROCESS and the reader's question is about a FILE. This is the one leg that
    closes the gap, over the register that already names both.

    IT DOES NOT GRADE A JOB THAT IS STILL WRITING. `reask` is asked first and a RUNNING unit is
    skipped, because refusing there would tell the reader to land a half-written artefact -- worse
    than the defect. The skip is keyed to the probe's answer and not to the record's `claim`: a
    record whose unit was collected sits at `live` forever, and keying to the claim would let
    exactly the stranded case escape by never being settled. An UNREADABLE probe is not RUNNING,
    so a machine with no working systemd still grades every record.
    """
    repo = (repo or _REPO).resolve()
    artefact = entry.get(field)
    if not artefact:
        return {"verdict": ABSENT,
                "why": f"the record names no `{field}`, so there is nothing to ask"}
    path = Path(artefact)
    path = path if path.is_absolute() else (repo / path)
    try:
        # An artefact is written as a repo-relative path by some launches and an absolute one by
        # others -- `/home/rich/synthetic-enterprise/docs/...` and `docs/...` are the same file and
        # a check that read either literally would be blind to half its own subjects.
        rel = path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return {"verdict": OUTSIDE, "why": (
            f"`{artefact}` is not under {repo}, so git cannot hold it and its absence from git is "
            "not a finding. A job whose only output lives in /var/tmp has no landable evidence at "
            "all, which is a different problem and not this one")}
    if not path.exists():
        return {"verdict": ABSENT, "why": (
            f"there is no file at `{artefact}`, so this is a question for the liveness re-ask and "
            "not for git")}

    if reask(entry, probe=probe)["verdict"] == RUNNING:
        return {"verdict": RUNNING, "why": (
            f"`{entry.get('unit')}` is still going, so `{rel}` is a file being written and not a "
            "result being withheld")}

    where = membership(rel, repo)
    if where is None:
        return {"verdict": UNREADABLE, "why": (
            f"git could not be asked about `{rel}` at all, so this check has no answer. It refuses "
            "rather than passing: a control that reads a broken probe as a clean bill is the "
            "failure mode that makes it worse than no control")}
    if where["head"]:
        return {"verdict": LANDED, "why": f"`{rel}` is in HEAD"}
    if where.get("ignored"):
        return {"verdict": IGNORED, "why": (
            f"`{rel}` matches a `.gitignore` rule, so its absence from git is a standing decision "
            "and not a stranding. Named rather than refused -- but a job whose ONLY surviving "
            "evidence is an ignored file has no landable record of having run, which is a real "
            "hazard and a different one")}
    if where["index"]:
        return {"verdict": STAGED, "why": (
            f"`{rel}` is staged in the shared index and in no commit. Named, not refused: a lane "
            "mid-landing looks exactly like this, and refusing here would wedge every other lane "
            "for the duration of somebody else's commit. It is also not done -- `reset --mixed` "
            "loses it and no clone has seen it")}
    return {"verdict": UNTRACKED, "why": (
        f"the job finished and wrote `{rel}` (its `{field}`), and that file is in no commit and "
        "not even staged. The register says this work is done; git says it does not exist. Land "
        "it, or say on the record why it is not landable")}


def landed_check(path: Path | None = None, *, repo: Path | None = None,
                 membership=git_membership, probe=systemd_probe) -> tuple[int, list]:
    """Grade every file every record names against git. Returns `(refusals, lines)`.

    Only UNTRACKED and UNREADABLE refuse. Every other verdict still prints, because a run whose
    output lives outside the repository is invisible to this check by construction and a reader
    who cannot see that in the output would take silence for coverage.
    """
    lines, refusals = [], 0
    for entry in load(path):
        for field, _named in named_paths(entry):
            answer = landing_verdict(entry, field, repo=repo, membership=membership, probe=probe)
            verdict = answer["verdict"]
            if verdict in (ABSENT, OUTSIDE, IGNORED) and field != "artefact":
                # The result is reported whatever became of it; a log or an rc file that was never
                # written, or went to /var/tmp, is the ordinary case and printing all three for
                # every record would bury the one line that matters.
                continue
            lines.append(f"{entry.get('job')} [{field}]: {verdict.upper()} -- {answer['why']}")
            if verdict in (UNTRACKED, UNREADABLE):
                refusals += 1
    return refusals, lines


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="re-ask every live claim and settle the ones that are stale")
    parser.add_argument("--landed", action="store_true",
                        help="ask git whether each record's named artefact ever reached a commit")
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

    if args.landed:
        refusals, lines = landed_check()
        for line in lines:
            print(line)
        if refusals:
            print(f"landed: FAIL ({refusals} file(s) a finished job wrote into this repo and no "
                  "commit holds)")
            return 1
        print("landed: PASS (every in-repo file the register names is in HEAD)")
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
