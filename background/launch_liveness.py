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

THERE IS ONE BOOK AND IT LIVES ON THE SHARED TREE (2026-09-16). `RECORDS_PATH` is derived from
`__file__`, so this module imported out of a linked worktree -- which is where the seat executor
mandates delivery turns run -- bound the register to git's CHECKOUT of a TRACKED file. Measured in
`/var/tmp/se-seat-executor` against `/home/rich/synthetic-enterprise`, same commit, same code, two
trees: the worktree's copy held **4** records of which **2 still claimed `live`**
(`noise-floor-20260910`, `arms-rerun-20260910b`); the shared tree's held **12**, and both of those
two were `finished`, settled six days earlier. So `check()` re-asks claims the machine settled long
ago, `unregistered_live_units()` grades systemd's real units against a book missing eight of them,
and -- the direction that actually loses data -- `record()` from a worktree writes a launch nothing
else will ever read.

THE SUBJECT IS WHY THE ANSWER IS THE SHARED TREE AND NOT "WHICHEVER TREE ASKED". A record's subject
is a `systemctl --user` UNIT, and there is ONE user manager per machine. The register describes
machine state, not tree state, so two books is not a tolerable divergence -- it is two answers to a
question that has one. (Contrast `docs/observability/.seat_heartbeat.json`, the other
read-modify-write over a live record, where the opposite holds and the redirect was REFUSED: see
`background/seat_continuity.note_activity`. Same shape, different subject, different answer.)

AND THE READ SIDE COULD NOT BE DECIDED ALONE, which is why this was filed as owed rather than wired
with the other five readers in `e9ad946cd`. `record()` is `load()` then `save()`. Resolving the READ
without the WRITE makes a worktree read the shared book and write it into its own copy, where the
next read ignores it -- trading a stale read for a LOST write, which is strictly worse. Both sides
resolve here, and `load`/`save` are the only two functions in this module that touch the path, so
every caller is covered and no future one can resolve half of it. The resolution is a pure function
of the filesystem, so the two calls cannot disagree.

THE GUARD RUNS BEFORE THE REDIRECT, AND THE ORDER IS LOAD-BEARING (R15). `is_live_record_path` --
which is what `guard_live_ledger_write` refuses on -- derives its room from THIS tree's
`LIVE_RECORD_DIR`. A path already redirected to the shared tree is outside that room, so guarding
after resolving would turn the refusal into a silent no-op and hand a test process the real
register. Resolving the write is exactly what opens that hole, so the write-side doctrine is applied
first, to the path the caller actually named.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from background.episode_prior import (
    UNREADABLE as PRIOR_UNREADABLE,
)
from background.episode_prior import (
    load_list_prior,
    preserve_unreadable,
    prior_unreadable,
)
from background.live_ledger_guard import guard_live_ledger_write, shared_tree_live_record

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
RECORDS_PATH = _REPO / "docs" / "observability" / ".launch_records.json"

#: The claim a record carries. `live` is what a launch writes; the other three are what a re-ask
#: settles it to. A record NEVER moves back to `live` -- see `check()`.
LIVE = "live"
FINISHED = "finished"
DIED = "died"
UNKNOWN = "unknown"
#: Terminal, and NOT a verdict a re-ask can produce: what `record()` moves a still-`live` row to
#: when a relaunch takes its unit name. It says "this run was never settled and now never can be"
#: -- which is a worse answer than DIED and a strictly better one than the row's silent deletion.
#: It must be terminal precisely BECAUSE the name is reused: a row left at `live` would be re-asked
#: by `check()` against the NEW run's systemd state, and answer confidently about the wrong job.
SUPERSEDED = "superseded"
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
#: In a commit on THIS machine's branch and reachable from no published one. A refusal, and the
#: fourth question this check needed: `STAGED`'s own note says a staged path is "not done -- no
#: clone has seen it", and that is just as true of a commit on a branch 42 ahead of `origin`.
#: HEAD is whatever this checkout happens to point at; it is not durability.
LANDED_LOCAL_ONLY = "landed_local_only"
#: Not gradeable, and each for a different reason: the job wrote nothing, or wrote outside the
#: repository, or is still writing, or git is under standing orders not to hold it. None of these
#: is a defect and none of them is a pass.
ABSENT = "absent"
OUTSIDE = "outside"
IGNORED = "ignored"

#: The ref that decides whether anyone ELSE can obtain the bytes. Deliberately the published
#: branch and not `@{upstream}`: a detached worktree (every `se-*` lane here) has no upstream at
#: all, and reading "this checkout tracks nothing" as "nothing is stranded" is how the check under
#: it went quiet in the first place.
_PUBLISHED_REF = "origin/main"


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


class RegisterUnreadable(RuntimeError):
    """The register exists and cannot be read, so no claim it held can be re-asked.

    A DISTINCT EXCEPTION BECAUSE THE CALLERS NEED OPPOSITE THINGS FROM IT, and a bare
    `RuntimeError` would be swallowed by the blanket `except` every daemon caller already has --
    which is the silence this class exists to break. `deadmans_switch` must PAGE (every `live`
    claim just became un-re-askable, which is an incident); `launch_long_job` must LAUNCH ANYWAY
    (a launch that is not recorded is the state it kills a healthy job to avoid).
    """

    def __init__(self, path, preserved: str | None):
        self.path = str(path)
        #: Where the bytes went, or `None` when they could not be kept. Named rather than
        #: implied: "we lost it and could not even keep the evidence" is a worse state than
        #: "we lost it", and a reader who cannot tell them apart will assume the better one.
        self.preserved = preserved
        super().__init__(
            "the launch register at {} cannot be read, so no `live` claim in it can be "
            "re-asked and an empty board is NOT what this means. Prior bytes {}.".format(
                self.path,
                "preserved at `{}`".format(preserved) if preserved
                else "COULD NOT BE PRESERVED -- they may be gone"))


def _resolved_path(path: Path | None = None) -> Path:
    """The copy `load` reads and `save` writes. ONE function so the two can never disagree about
    which file they mean -- the module docstring's whole argument rests on that identity."""
    return Path(shared_tree_live_record(path or RECORDS_PATH))


def _resolved_path_or_named(path: Path | None = None) -> Path:
    """`_resolved_path`, falling back to the UNRESOLVED path when the resolver cannot answer.

    THIS IS A REPORTING PATH AND NEVER A WRITE TARGET. `load_register` already grades a raising
    resolver UNREADABLE, so the two callers below are on their way to a refusal -- and a refusal
    whose own construction raises the resolver's exception is caught by the blanket `except` every
    daemon caller has, which is the silence `RegisterUnreadable` exists to break. The caller named
    a path; saying which one, unresolved, is strictly better than losing the refusal to say it.
    """
    try:
        return _resolved_path(path)
    except Exception:          # noqa: BLE001 -- see docstring: never let the refusal itself raise
        return Path(path or RECORDS_PATH)


def load_register(path: Path | None = None) -> tuple[list, str]:
    """The launch register AND what we actually know about it: `(records, verdict)`.

    THE HONEST READER, and `load` below is the lossy one kept for the callers whose decision does
    not turn on the difference. Five distinct priors used to collapse into one answer and it was
    the flattering one every time -- ABSENT, a zero-byte file (the signature of an interrupted
    write), truncated JSON, a bare `null` (which PARSES, so no `except` ever saw it), and a
    non-list object all returned `[]`, indistinguishable from *no launches*.

    `episode_prior` is the partition and this module is its sixth carrier rather than a seventh
    hand-rolled loop; `item_type=dict` is what makes a PARTLY-right register (`[{...}, "x"]`)
    UNREADABLE instead of readable-with-junk, because a record we cannot fully account for cannot
    answer "what became of the run this document says is in flight".

    A RESOLVER THAT RAISES IS UNREADABLE, NOT ABSENT. If we cannot even establish which file we
    mean, we have not looked -- and "we did not look" must never be the empty board.

    THE VERDICT IS `episode_prior`'s AND NOT THIS MODULE'S. Both spell the word `unreadable` and
    they answer different questions: `launch_liveness.UNREADABLE` is what a re-ask returns when
    `systemctl` cannot be RUN, and `PRIOR_UNREADABLE` is what the REGISTER FILE is. The import is
    aliased so no future edit can make a probe verdict and a file verdict compare equal by
    accident, which they would, both being the string `"unreadable"`.
    """
    try:
        resolved = _resolved_path(path)
    except Exception:
        return [], PRIOR_UNREADABLE
    return load_list_prior(resolved, item_type=dict)


def load(path: Path | None = None) -> list:
    """The launch register. THE SHARED TREE'S copy when read from a linked worktree -- module
    docstring for the measurement, and for why this could not be wired without `save` below.

    LOSSY BY CONSTRUCTION: this returns `[]` for an ABSENT register and for an UNREADABLE one
    alike. That is correct for the callers that only ever FILTER what is there
    (`pending_notices`, `clear_notices`, `landed_check`, `unregistered_live_units`) -- none of
    them writes a rebuilt register, and `unregistered_live_units` is keyed to what systemd says
    is running rather than to what the file says, so an emptiness here makes it report MORE, not
    less. **Any caller whose decision differs between "nothing was launched" and "we cannot tell"
    must call `load_register` instead**, and the two that do are `record` and `check`.
    """
    return load_register(path)[0]


def save(records: list, path: Path | None = None) -> None:
    """Replace the launch register. Resolves to the SAME copy `load` reads -- see the module
    docstring: a read redirected without its write does not stale a read, it loses a write."""
    target = path or RECORDS_PATH
    # BEFORE the redirect, never after, and this is not bookkeeping. `guard_live_ledger_write`
    # refuses on THIS tree's live-record room; the redirect's whole job is to hand back a path
    # outside it, so guarding second would make the refusal unreachable for exactly the callers
    # the redirect applies to. The write-side doctrine is applied to the path the caller named.
    guard_live_ledger_write(target, writer="launch_liveness.save")
    target = Path(shared_tree_live_record(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


def record(job: str, unit: str, artefact: str, *, log: str | None = None,
           rc_path: str | None = None, asserted_live_by: list | None = None,
           launched_at: str | None = None, path: Path | None = None) -> dict:
    """Write the launch record for `job`. Always writes the claim `live`.

    `asserted_live_by` names the documents that state this run is in flight. It is what turns a
    contradiction into an address: the check does not just say a claim went stale, it says which
    pages are now wrong.

    THE IMMEDIATELY-PRECEDING RUN IS KEPT, AND THIS USED TO DELETE IT. The line was
    `[r for r in load(path) if r.get("job") != job]` -- a filter by job name that never looked at
    `claim`. Four launches of one job is four relaunches of ONE JOB NAME, so that filter ran on
    exactly the event this module was built for, and it ran in the window where the contradiction
    had not been written yet: a job dies, its row still reads `live` because `check()` runs on the
    deadman's cadence and not on the death, somebody relaunches, and the `live` row is dropped. The
    next deadman cycle finds nothing stale and clears; the `[LAUNCH DIED]` page never fires; every
    document in the deleted row's `asserted_live_by` is never contradicted. This is the module's
    own founding defect arriving through its own writer.

    So an unsettled row is SUPERSEDED rather than deleted -- terminal, dated, and carrying the
    reason it can never be settled -- and the run before that one is what gets dropped. ONE prior
    row per job, not a growing history: the reader this serves is someone holding a document that
    says the LAST run is in flight, and two runs ago was already contradicted by the run between.

    NOT A REFUSAL. Refusing to relaunch over an unsettled row would wedge the launcher outright
    whenever a death settles to UNKNOWN -- and `check()` by design never settles UNKNOWN, so the
    row would stay `live` forever and no relaunch of that job would ever be possible again. A guard
    that refuses a legitimate relaunch every time the probe was inconclusive is a guard that
    refuses the ordinary case, which is the shape this project ships worst.

    AN UNREADABLE PRIOR IS PRESERVED BEFORE IT IS REBUILT, AND THE RECORD SAYS SO. This is
    load -> supersede -> append -> save, and on an unreadable prior the load half used to return
    `[]` -- so the save half wrote a ONE-ELEMENT register over whatever was there. Measured on a
    truncated register holding a `live` row for `longjob-A`: `record('longjob-B')` left the file
    holding `['longjob-B']`, with A's bytes preserved nowhere. **A destroyed `live` record is a
    claim that can never be contradicted**, which is the single thing this module exists to
    abolish, arriving through its own writer -- exactly as the founding defect in the paragraph
    above did.

    ABSENT AND UNREADABLE TAKE THE SAME ACTION AND ARE DIFFERENT ANSWERS. The write still
    happens, because the alternative is an unrecorded launch. What changes is that the bytes go
    somewhere first and this record carries `prior_register` naming where -- a field no other row
    has, so a reader of the register can see that everything before it was lost and can go and
    read it. Preserving is best-effort by `episode_prior`'s own doctrine (a launcher that refuses
    to run because it could not archive a corrupt file has turned a lost record into an outage),
    so `preserved_as: null` is a REPORTABLE state and not an omission.
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
    records, verdict = load_register(path)
    if prior_unreadable(verdict):
        # BEFORE `save` below, which is the only ordering that keeps anything: `save` writes the
        # rebuilt list over the same resolved path, so a preserve afterwards would archive our own
        # output. `keep_original=False` -- the corrupt file is MOVED aside, so the rebuild lands on
        # a clean path and the next read is honestly ABSENT rather than perpetually unreadable.
        preserved = None
        try:
            preserved = preserve_unreadable(_resolved_path_or_named(path))
        except Exception:      # noqa: BLE001 -- the launch still has to be recorded; see docstring
            preserved = None
        entry["prior_register"] = {"verdict": verdict, "preserved_as": preserved}
        print("[launch-liveness] the register was UNREADABLE and has been rebuilt from this "
              "launch alone; every earlier record is gone from it. Prior bytes {}.".format(
                  "at `{}`".format(preserved) if preserved else "COULD NOT BE PRESERVED"),
              file=sys.stderr)
    prior = [r for r in records if r.get("job") == job]
    # Identity, not equality: two runs of one job can be equal dicts field for field, and `!=` on
    # the value would drop the row we mean to keep.
    stale = {id(r) for r in prior[:-1]}
    kept = [r for r in records if id(r) not in stale]
    if prior and prior[-1].get("claim") == LIVE:
        prior[-1]["claim"] = SUPERSEDED
        prior[-1]["settled_at"] = _now()
        prior[-1]["evidence"] = (
            f"a relaunch of `{job}` took the unit name `{prior[-1].get('unit')}` while this run's "
            "claim was still `live`, so nothing had asked what became of it and now nothing can: "
            "the only exit record that could answer belongs to whichever run holds the name. The "
            "row is kept rather than deleted so the documents it names are not left uncontradicted "
            f"-- re-ask them by hand. Superseded at {_now()} by a launch recorded after it.")
    kept.append(entry)
    save(kept, path)
    return entry


def check(path: Path | None = None, probe=systemd_probe, *,
          only: str | None = None, notice: bool = False) -> tuple[int, list, list]:
    """Re-ask every record still claiming `live`; settle the ones that are not, and say so.

    `only` narrows the re-ask to ONE job. It exists for `launch_long_job.launch()`, which must
    settle the run it is about to overwrite before `reset-failed` destroys the evidence -- and has
    no business probing units belonging to other jobs on its way to starting one.

    `notice` marks what it settles to DIED as owed to the director. The settling moved to the
    launcher, so the REPORTING has to be able to start from the record rather than from this call's
    return value: the deadman only ever sees rows still claiming `live`, and a row the launcher
    already settled is invisible to it. Left off by default, which is why the deaths already
    settled in the live register do not all page the first time this ships.

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

    AND AN UNREADABLE REGISTER RAISES, because the paragraph above was careful about the probe and
    the loader one frame below handed this function an emptiness it could not tell from an empty
    board. On a truncated register this returned `stale=0` -- not "we could not tell", but the
    CLEAN one -- and `deadmans_switch._check_launch_liveness` reads `if not stale: clear_transition`.
    So the register losing its own contents read, all the way to the alarm, as every launch
    accounted for. `(0, [...], [])` cannot carry that refusal: a count is the field the caller
    branches on and zero is the flattering value, so the refusal has to be a control-flow event the
    caller cannot spend by ignoring a field. `RegisterUnreadable` is that, and both callers have an
    explicit branch for it.

    IT PRESERVES WITHOUT MOVING (`keep_original=True`), which is the opposite of `record`'s choice
    and for a reason. This runs on the deadman's cadence: moving the file would make the next cycle
    read ABSENT and go quiet, turning a standing condition into a single page nobody was awake for.
    The condition stands until a `record()` rebuilds the register, and the alarm re-escalates while
    it stands. `preserve_unreadable` never overwrites an earlier copy, so repeating this every
    cycle keeps the FIRST loss -- the one that still held the real record -- and not the last.
    """
    records, register_verdict = load_register(path)
    if prior_unreadable(register_verdict):
        named = _resolved_path_or_named(path)
        try:
            preserved = preserve_unreadable(named, keep_original=True)
        except Exception:      # noqa: BLE001 -- best-effort; the refusal below is the real output
            preserved = None
        raise RegisterUnreadable(named, preserved)
    lines, settled = [], []
    for entry in records:
        if entry.get("claim") != LIVE:
            continue
        if only is not None and entry.get("job") != only:
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
        if notice and entry["claim"] == DIED:
            entry["pending_notice"] = True
        settled.append(entry)
        for doc in entry.get("asserted_live_by") or []:
            lines.append(f"  CONTRADICTS {doc} -- it says this run is in flight; it is not")
    if settled:
        save(records, path)
    return len(settled), lines, settled


def _identity(entry: dict) -> tuple:
    """What tells two runs of one job apart. Deliberately not `job` alone: the whole subject here
    is a job name carrying more than one run's record."""
    return (entry.get("job"), entry.get("unit"), entry.get("launched_at"))


def pending_notices(path: Path | None = None) -> list:
    """Deaths that were settled but never reported, so somebody can still be told.

    A DEATH SETTLED BY THE RELAUNCH IS INVISIBLE TO THE DEADMAN, and that is the whole reason this
    exists. `check()` re-asks rows claiming `live`; the launcher's own pre-`reset-failed` settle
    leaves the row DIED, so the next deadman cycle correctly finds nothing stale and correctly
    stays silent -- and the page is suppressed by the very repair that preserved the evidence.
    Separating "settled" from "reported" is what stops the fix re-creating the defect one move on.

    Absent `pending_notice` means "not owed", NOT "owed". Every row settled before this shipped
    lacks the field, so this returns nothing for them rather than paging the whole register at once
    the first time the deadman runs it.
    """
    return [r for r in load(path) if r.get("pending_notice")]


def clear_notices(entries, path: Path | None = None) -> int:
    """Mark these deaths reported. Called AFTER the notify, never before: a notice cleared ahead of
    a send that then throws is a death nobody is told about twice over."""
    wanted = {_identity(e) for e in entries}
    records = load(path)
    cleared = 0
    for r in records:
        if r.get("pending_notice") and _identity(r) in wanted:
            r.pop("pending_notice", None)
            cleared += 1
    if cleared:
        save(records, path)
    return cleared


def git_membership(rel: str, repo: Path) -> dict | None:
    """Where `rel` stands in git, or None if git could not be RUN.

    Returns `{"head", "index", "ignored", "published", "publishable"}`.

    The questions are asked separately on purpose. `git ls-files` reads the INDEX, and a path
    that is only in the index has not reached any commit -- a `reset --mixed` loses it and no
    clone has ever seen it. A control that asked only `ls-files` would have called such a path
    tracked, which is the exact reading that has already made one control here green while the
    thing it guarded was absent from every commit.

    AND THAT REASONING DID NOT STOP WHERE IT SHOULD HAVE. For 106 hours this check reported a real
    stranding, was corrected by a LOCAL commit, and went silent -- `head` said yes, on a `main` 42
    commits ahead of `origin` that no clone has ever seen either. The sentence above justifies the
    fourth question as exactly as it justifies the third, so `published` is now asked too. The
    silence was less true than the noise had been.

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
        # The FOURTH question, and this control shipped without it for long enough to go quiet on
        # a real stranding. `HEAD` is whatever branch this machine happens to be on: an artefact
        # committed onto a local `main` that is 42 ahead of `origin` answers "yes" here and is
        # obtainable by nobody -- no clone, no CI, no other worktree -- and a `reset --hard
        # origin/main` destroys it. That is the same hazard the `head`/`index` split above exists
        # to catch, one level up, and the docstring's own words for it ("no clone has ever seen
        # it") apply unchanged.
        published = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{_PUBLISHED_REF}:{rel}"],
            capture_output=True, timeout=20)
        # Distinguishing "not in origin/main" from "there is no origin/main to ask" -- without it a
        # clone with no remote reads every artefact as stranded, which is a wrong answer and not a
        # conservative one.
        has_ref = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", _PUBLISHED_REF],
            capture_output=True, timeout=20)
    except Exception:
        return None
    return {"head": head.returncode == 0, "index": index.returncode == 0,
            "ignored": ignored.returncode == 0,
            "published": published.returncode == 0,
            "publishable": has_ref.returncode == 0}


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
        if where.get("publishable") and not where.get("published"):
            return {"verdict": LANDED_LOCAL_ONLY, "why": (
                f"`{rel}` is in HEAD and is NOT reachable from `{_PUBLISHED_REF}`, so it is in a "
                "commit on this machine's branch and in no published one. Nobody else can obtain "
                "these bytes -- no clone, no CI, no other worktree -- and a `reset --hard "
                f"{_PUBLISHED_REF}` destroys them. A local commit is neither of the two things "
                "this check's own remedy asks for: it has not been landed, and it has not been "
                "recorded as unlandable. Push the branch, or say on the record why it cannot go")}
        return {"verdict": LANDED, "why": (
            f"`{rel}` is in HEAD and reachable from `{_PUBLISHED_REF}`"
            if where.get("published") else
            f"`{rel}` is in HEAD, and there is no `{_PUBLISHED_REF}` to ask about publication")}
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

    Only UNTRACKED, UNREADABLE and LANDED_LOCAL_ONLY refuse. Every other verdict still prints,
    because a run whose
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
            if verdict in (UNTRACKED, UNREADABLE, LANDED_LOCAL_ONLY):
                refusals += 1
    return refusals, lines


#: The namespace `launch_long_job.unit_name()` puts every job it starts into. A live unit outside
#: this prefix belongs to something else and is not this register's business.
_JOB_UNIT_PREFIX = "longjob-"

#: Not a state: what `unregistered_live_units` returns when systemd could not be asked at all.
UNREGISTERED_UNREADABLE = -1


def live_units(runner=subprocess.run, prefix: str = _JOB_UNIT_PREFIX) -> list | None:
    """Every `longjob-*` unit the user manager reports as ACTIVE right now.

    None means the probe could not be RUN, and is not an empty list. The two are opposite claims --
    "nothing is running" versus "we could not look" -- and the caller must fail closed on the
    second, which is why they are not both `[]`.
    """
    try:
        out = runner(
            ["systemctl", "--user", "list-units", "--type=service", "--all",
             "--no-legend", "--no-pager", f"{prefix}*"],
            capture_output=True, text=True, timeout=20)
    except Exception:  # noqa: BLE001 -- a broken probe is UNREADABLE, never "all clear"
        return None
    if getattr(out, "returncode", 1) != 0:
        return None
    names = []
    for line in (out.stdout or "").splitlines():
        fields = line.replace("●", " ").split()
        if len(fields) < 4 or not fields[0].startswith(prefix):
            continue
        # ACTIVE is the third column after UNIT/LOAD. `_STILL_GOING` is reused rather than
        # re-spelled so this leg and `reask()` cannot drift apart about what "not finished" means.
        if fields[2] in _STILL_GOING:
            names.append(fields[0])
    return names


def unregistered_live_units(path: Path | None = None, *, runner=subprocess.run,
                            units=None) -> tuple[int, list]:
    """Is every RUNNING job covered by a register entry that claims it is live?

    THE DEFECT THIS EXISTS FOR. `launch_long_job.launch()` will STOP a healthy long run rather than
    leave it unrecorded -- its own docstring calls "running and unrecorded" the state the module
    exists to abolish, and pays a killed job to abolish it. That guards the DOOR. Nothing guarded
    the wall beside it: a job started with `systemd-run` by hand gets a real transient unit, a real
    cgroup and a real log, looks in every way like a launch that went through the door, and is
    invisible to `check()` forever, because `check()` iterates the REGISTER and an absent job is
    not a `live` claim to re-ask.

    AND THE SILENCE IS WORSE THAN AN EMPTY ANSWER, which is the part that made this worth a
    control. `--check` does not go quiet on an unregistered job; it prints PASS. On 2026-09-10 that
    PASS was a true statement about `longjob-arms-rerun-20260910b` -- a different nine-seed floor,
    launched the same day, with a near-identical name -- while `longjob-noise-floor-20260910` ran
    unregistered beside it and a Lane 0 item instructed the next reader to take that PASS as
    evidence the floor was alive. A green about somebody else's job does not prompt the second
    question an empty answer would.

    Returns `(refusals, lines)`. `UNREGISTERED_UNREADABLE` refusals means systemd could not be
    asked -- fail closed, because reporting full coverage because we could not look is the failure
    that would make this worse than nothing.
    """
    names = live_units(runner=runner) if units is None else list(units)
    if names is None:
        return UNREGISTERED_UNREADABLE, [
            "unregistered: UNREADABLE -- `systemctl --user list-units` could not be run, so "
            "nothing here knows what is running. This is NOT a clean bill: it is the absence of a "
            "probe, and a control that reads one as the other is worse than no control."]
    by_unit = {}
    for entry in load(path):
        if entry.get("unit"):
            by_unit.setdefault(entry["unit"], []).append(entry)
    lines, refusals = [], 0
    for unit in sorted(names):
        # A unit is named with and without `.service` in different places; the register holds
        # whichever the launcher wrote, so both spellings are asked before calling a job absent.
        held = by_unit.get(unit) or by_unit.get(unit.removesuffix(".service")) or []
        if any(e.get("claim") == LIVE for e in held):
            lines.append(f"{unit}: COVERED -- a register record claims this job live")
            continue
        refusals += 1
        if held:
            claims = ", ".join(sorted({str(e.get("claim")) for e in held}))
            lines.append(
                f"{unit}: STALE RECORD -- the unit is running, but its only record(s) claim "
                f"`{claims}`. A settled record is never re-asked, so this job's death would be "
                "graded against an answer given before it started.")
        else:
            lines.append(
                f"{unit}: UNREGISTERED -- this job is RUNNING and the register has never heard of "
                "it, so `--check` cannot grade it, the deadman cannot page on its death, and any "
                "document saying it is in flight will never be contradicted. Record it: "
                f"`python3 -m background.launch_liveness --record <job> --unit {unit} "
                "--artefact <path> --launched-at <when it ACTUALLY started>`.")
    if not names:
        lines.append("unregistered: no `longjob-*` unit is running, so there is nothing to cover")
    return refusals, lines


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="re-ask every live claim and settle the ones that are stale")
    parser.add_argument("--landed", action="store_true",
                        help="ask git whether each record's named artefact ever reached a commit")
    parser.add_argument("--unregistered", action="store_true",
                        help="refuse if any RUNNING longjob-* unit has no record claiming it live")
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

    if args.unregistered:
        refusals, lines = unregistered_live_units()
        for line in lines:
            print(line)
        if refusals == UNREGISTERED_UNREADABLE:
            print("unregistered: UNREADABLE (systemd could not be asked -- refusing, not passing)")
            return 1
        if refusals:
            print(f"unregistered: FAIL ({refusals} running job(s) no register record covers)")
            return 1
        print("unregistered: PASS (every running longjob-* unit has a live record)")
        return 0

    try:
        stale, lines, _ = check()
    except RegisterUnreadable as e:
        # REFUSES, where the `--check` leg below deliberately does not. The comment under that leg
        # says why it reports rather than refuses -- it cannot grade a job that was never recorded
        # -- and this is the opposite case: the register itself is gone, so there is no reading of
        # its silence that could be a PASS.
        print(f"check: UNREADABLE -- {e}")
        return 1
    for line in lines:
        print(line)
    # THE PASS BELOW USED TO CLAIM MORE THAN IT KNEW. `check()` re-asks the REGISTER, so a job that
    # was never recorded contributes nothing to it and a bare PASS reads as "your run is fine" --
    # which on 2026-09-10 was a true sentence about a DIFFERENT job with a near-identical name.
    # Reported and not refused here on purpose: `deadmans_switch` calls `check()` directly and a new
    # refusal on this path would page for a state no lane can clear mid-run. `--unregistered` is
    # the leg that refuses.
    uncovered, ulines = unregistered_live_units()
    if uncovered == UNREGISTERED_UNREADABLE or uncovered:
        for line in ulines:
            print(f"  {line}")
    if stale:
        print(f"check: FAIL ({stale} launch record(s) claimed live and are not)")
        return 1
    if uncovered == UNREGISTERED_UNREADABLE:
        print("check: PASS on the records held -- but systemd could not be asked what is RUNNING, "
              "so this says nothing about coverage (`--unregistered`)")
        return 0
    if uncovered:
        print(f"check: PASS on the records held -- but {uncovered} RUNNING job(s) are covered by "
              "no record at all, so this PASS is not about them (`--unregistered` refuses)")
        return 0
    print("check: PASS (no stale liveness claim; every running longjob-* unit is covered)")
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/launch_liveness.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("launch_liveness")
    sys.exit(main())
