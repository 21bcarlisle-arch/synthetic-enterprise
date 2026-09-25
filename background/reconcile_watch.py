"""Periodic reconcile watch — OPS1 sub-step 4, G-L2/G-R3 made LIVE (not boot-only).

PURPOSE
    The reconcile (process_manifest + schedule_manifest + gap-ledger declared-vs-actual) is a
    DRIFT CONTROL.
    A control with no live consumer is fail-silent theatre (R15): boot_announce runs the reconcile
    once at boot, so between boots drift is UNWATCHED — exactly why a live worker-seat declared
    `held` produced no HELD_VIOLATED (found 2026-07-17 at the worker-seat gate). This closes that
    gap: run the reconcile on a systemd timer and make drift LOUD the moment it appears.

GUARANTEES
    - LIVE + PERIODIC: fired by reconcile-watch.timer (committed IaC), every RECONCILE_INTERVAL.
    - TRANSITION-ONLY NTFY (R5): pages only when the drift set CHANGES (appears / changes / clears),
      carrying the full payload — never a heartbeat. A clean run is logged, not paged.
    - REPORT-ONLY ABOUT PROCESSES (G-R3): it starts/stops/enables/reaps NOTHING. It does now CLOSE
      THE FORK WITH ORIGIN — see `_reconcile_the_fork` for why that is not the same concession, and
      for the measurement that made a report-only watcher the wrong shape for this one subject.
    - Typed by source (G-N2): `rotating_light` when drift is present, `white_check_mark` when it
      clears back to clean.

WIRING
    reconcile-watch.service (Type=oneshot) + reconcile-watch.timer, declared in schedule_manifest,
    installed+armed by install_schedule.sh — so "watch for drift" is committed, reconstructable IaC.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import gap_ledger_reconciler as _gap  # noqa: E402
from background import process_reconciler as _proc  # noqa: E402
from background import schedule_reconciler as _sched  # noqa: E402
from background import seat_work_in_hand as _seat  # noqa: E402
from background.episode_prior import (  # noqa: E402
    ABSENT,
    load_episode_prior,
    preserve_unreadable,
    prior_unreadable,
    screen_list_value,
)
from background.live_ledger_guard import guard_live_ledger_write  # noqa: E402

# How many gap-drift lines the human summary spells out before counting the rest. The SIGNATURE
# always carries every item (so no transition can hide behind the cap) and the overflow is stated,
# never silently dropped.
_GAP_SUMMARY_CAP = 5

STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".reconcile_watch_state.json"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "reconcile-watch-log.md"


def drift_signature(proc_results: list[dict], sched_results: list[dict],
                    gap_results: list[dict] | None = None) -> list[str]:
    """A stable, order-independent signature of the CURRENT drift set — the thing whose CHANGE is
    the transition worth paging on (R5). Clean == []."""
    return sorted(
        [f"P:{r['session']}:{r['status']}" for r in _proc.drift(proc_results)]
        + [f"S:{r['item']}:{r['status']}" for r in _sched.drift(sched_results)]
        + [f"G:{r['item']}:{r['status']}" for r in _gap.drift(gap_results or [])]
    )


def build_report(proc_results: list[dict], sched_results: list[dict],
                 gap_results: list[dict] | None = None) -> tuple[list[str], str]:
    """(drift_signature, human_summary). Injectable results for tests; production reads live."""
    gap_results = gap_results or []
    sig = drift_signature(proc_results, sched_results, gap_results)
    if not sig:
        summary = ("[RECONCILE] clean — no drift "
                   f"({len(proc_results)} declared processes, {len(sched_results)} schedule entries, "
                   f"{len(gap_results)} gap-ledger entries all as declared).")
    else:
        lines = [f"[RECONCILE] DRIFT — {len(sig)} item(s) diverge from the manifests:"]
        for r in _proc.drift(proc_results):
            lines.append(f"    ✗ {r['session']}: {r['status']}")
        for r in _sched.drift(sched_results):
            lines.append(f"    ✗ [{r['kind']}] {r['item']}: {r['status']}")
        gap_drift = _gap.drift(gap_results)
        for r in gap_drift[:_GAP_SUMMARY_CAP]:
            lines.append(f"    ✗ [gap:{r['status']}] {r['item']}")
        if len(gap_drift) > _GAP_SUMMARY_CAP:
            lines.append(f"    … and {len(gap_drift) - _GAP_SUMMARY_CAP} further gap-ledger "
                         "entr(ies) — full set in the drift signature")
        summary = "\n".join(lines)
    return sig, summary


#: Said on the surface, not in a footnote. A page whose transition claim cannot be made must say so
#: in the page, or the director reads a bare all-clear as "it cleared" when what happened is "it is
#: clean now and we cannot tell you what it was".
_PRIOR_UNREADABLE_NOTE = (
    "[RECONCILE] THE LAST-SEEN DRIFT SIGNATURE WAS PRESENT AND UNREADABLE. This page states the "
    "CURRENT reconcile and makes no claim about whether it is a change. Paged rather than "
    "swallowed: read as a clean baseline, a lost memory beside a clean reconcile compares EQUAL, "
    "and the recovery page is the one that never goes out."
)


def _unreadable(reason: str) -> None:
    """Log the loss, keep the bytes, and answer None. The preserve is not optional housekeeping:
    `run()` calls `_save` on the page this loss forces, so the recovery is what destroys the
    evidence of what was lost."""
    kept = preserve_unreadable(STATE_FILE) or "(could not be preserved)"
    _log(f"last-seen drift signature UNREADABLE ({reason}); bytes kept at {kept}")
    return None


def _load_last() -> list[str] | None:
    """The last-seen drift signature, or `None` for PRESENT-AND-UNREADABLE, which is not one.

    THE TWO DIRECTIONS DIFFER, and until 2026-09-05 both answered `[]`.

    ABSENT -> `[]`, the clean baseline, unchanged. The original argument for it is sound and still
    holds: a FIRST clean run must not page, and `[]` is what makes it compare equal rather than
    read as a transition; a first run already in drift still pages, because drift != clean.

    UNREADABLE -> `None`. `[]` is a CLAIM -- "we were clean" -- and a corrupt file is not evidence
    for it. What that bought, concretely: with a corrupt state file and a currently-clean
    reconcile, `sig != last` was False, so the RECOVERY page was never sent. The director keeps
    holding the last alarm he received and nothing anywhere records that the all-clear was
    swallowed. `cleared = not sig and last` was False for the same reason, so even the tag would
    have been wrong. This is the ONLY quiet member of the partition -- every other unreadable shape
    here fails loud, to a duplicate drift page you can see and dismiss -- and a watcher whose whole
    purpose is that drift is LOUD must not let its own lost memory silence the all-clear.

    IT CANNOT STORM, which is what makes paging affordable: `run()` calls `_save(sig)` on every
    page, so a well-formed file replaces the corrupt one in the same pass. One page per corruption,
    not one every five minutes.

    A mapping that came off disk does NOT make its `drift` field a signature. A missing key,
    `"abc"` or `[1, 2]` are unreadable records, not clean ones -- and `"abc"` is the shape that
    answers `len()` with 3 and reads as three alarms downstream.
    """
    state, verdict = load_episode_prior(STATE_FILE)
    if prior_unreadable(verdict):
        return _unreadable("the file could not be read or did not parse to a mapping")
    if verdict == ABSENT:
        return []
    drift = screen_list_value(state.get("drift"))
    if drift is None:
        return _unreadable("it parsed, but its `drift` field is not a list of signature strings")
    return drift


def _save(sig: list[str]) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        guard_live_ledger_write(STATE_FILE, writer="reconcile_watch._save").write_text(json.dumps({"drift": sig,
                                          "at": datetime.now(timezone.utc).isoformat()}))
    except OSError:
        pass


def _log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"\n- [{ts}] {msg}")
    except OSError:
        pass


def _digest_class():
    """The G-N3 class this daemon's pages carry. Imported lazily so a test injecting `notify`
    never has to have the digest module wired, and so this file stays importable on its own."""
    from background import notification_digest
    return notification_digest.DIVERGENCE


#: How many CHANGED LOADED MODULES make a daemon meaningfully stale rather than merely behind
#: today's churn. SET FROM THE MEASURED DISTRIBUTION on 2026-08-21, not chosen: immediately after
#: a restart every daemon sat at 1-2 (this tree takes ~20 commits a day, so "anything changed
#: since you booted" is true within minutes and is NOT a fault); the genuinely stale ones sat at
#: 57, 63 and 65. Nothing lives between 2 and 57, so the threshold is a real gap in the data and
#: not a tuned parameter.
#:
#: A count of 1-2 must never report, or this becomes an always-red detector and gets ignored --
#: which is precisely how the drift went unseen for four days while a correct control computed it.
DRIFT_MODULE_THRESHOLD = 10


def _drift_report(evaluate=None) -> list[str]:
    """['session (N modules behind)'] for daemons past the threshold. REPORT ONLY -- it never
    restarts anything. Redeploying a daemon mid-work is a decision with its own blast radius,
    and a reconcile that silently restarted things would be the accretion OPS1 forbids."""
    if evaluate is None:
        from background.process_reconciler import evaluate_boot_sha_drift as evaluate
    verdict = evaluate() or {}
    detail = verdict.get("stale_detail") or {}
    lines = [f"{s} ({len(f)} modules behind)"
             for s, f in sorted(detail.items(), key=lambda kv: -len(kv[1]))
             if len(f) >= DRIFT_MODULE_THRESHOLD]
    # THE THIRD INSTRUMENT TO PUBLISH THIS NUMERATOR ALONE, found by asking what else read the
    # verdict after `graded` landed (e1736649a). An empty list above is what a clean fleet looks
    # like AND what a fleet nobody could grade looks like -- and this one is silent by design, so
    # the ungradable case produced no log line at all. Measured 2026-09-25 13:05: 10 of 11
    # daemons `stamp-predates-process`, and this reporter said nothing, correctly, about nothing.
    #
    # NOT ALWAYS-RED, which is the failure mode this whole function is shaped around: it fires
    # only when a daemon is genuinely ungradable, never on the 1-2 modules of ordinary churn the
    # threshold above exists for. On this box right now `graded == population` and it is silent.
    population, graded = verdict.get("population"), verdict.get("graded")
    if population is not None and graded is not None and len(graded) < len(population):
        lines.append(
            f"{len(population) - len(graded)} of {len(population)} daemon(s) UNGRADED "
            "-- the list above is a numerator, not a clean fleet")
    return lines


#: Statuses that mean the fork question was ASKED AND SETTLED — there is nothing left to close.
#: Everything else is a fork that is still open, whatever the reason, and gets logged as such.
#:
#: THIS IS DELIBERATELY NOT `origin_reconcile.main`'s EXIT-0 SET, and the difference is one status.
#: `main` returns 0 for `(LEVEL, RECONCILED, PUSHED)` and 1 for FAST_FORWARDED — but a
#: fast-forward is precisely the shared tree arriving at origin with nothing of ours to land, which
#: is the fork CLOSED. Grading it "still open" here would make the log read STILL OPEN on the one
#: outcome this whole leg was added to produce most often, and an always-red log line is an ignored
#: one. Whether `main`'s rc is itself wrong is a separate question and is NOT settled here; this
#: constant answers "is the fork closed", not "what did the CLI exit".
_FORK_SETTLED = ("LEVEL", "RECONCILED", "PUSHED", "FAST_FORWARDED")


def _reconcile_the_fork(state_fn=None, reconcile_fn=None, subject_fn=None) -> str | None:
    """Close the fork with origin when one is open. Returns a log line, or None when level.

    WHY THIS RIDES *THIS* TIMER AND WHY IT IS NOT A NEW CONCESSION (2026-09-24).

    `background/origin_reconcile` was built to be run on a cadence and had none. Nothing on this
    box was trying to merge. The measured cost: the publisher refused 51 times over 71.7h, a
    reader's figures went 74.1h stale, and this module's own log is the evidence — hours of
    `reconcile DRIFT (9 alarm(s)); unchanged -> log only`, every five minutes, while the shared
    tree sat 38 behind origin and 4 ahead. A watcher that reports a fork it is standing next to,
    forever, is not a control; it is a way of feeling watched.

    THE REPORT-ONLY GUARANTEE ABOVE IS ABOUT PROCESSES AND IT SURVIVES. G-R3 exists because
    redeploying a daemon mid-work has a blast radius that belongs to a decision. Nothing here
    starts, stops, enables or reaps anything. What it does instead is delegate to a module whose
    whole design is the objection this one would otherwise have to raise: the merge happens in a
    THROWAWAY WORKTREE with its own index, so the shared tree's index is never opened and no other
    lane's uncommitted work can be swept. That is `origin_reconcile`'s founding property, not a
    promise re-made here.

    AND THE JUDGEMENT STAYS WITH A HUMAN. `origin_reconcile` inherits `surgical_land --merge`'s
    refusal on CONFLICT, and a conflict is exactly the case where two lanes disagree about one
    file. So the cadence closes the mechanical fork and REFUSES the one that needs reading — which
    is the split that makes running this unattended affordable at all.

    NO NEW TIMER, deliberately, for the reason the seat-claim sweep gives above: a new timer is a
    new thing that can silently fail to be armed, and that is the failure class this whole file
    exists to catch.

    IT CANNOT STORM AND IT CANNOT TRAMPLE ITSELF. `MERGE_TIMEOUT_SECONDS` is 25 minutes and this
    tick is five, so ticks WILL overlap. `origin_reconcile._fresh_worktree` reads an owner marker
    and REFUSES rather than rebuilding a tree under a running merge, so the overlap costs a logged
    ERROR line and never a corrupted merge. The empty-merge loop that put 29 commits on origin in
    3.25h is likewise handled at the source: the `ahead == 0` leg advances instead of committing.

    WHY DELEGATE THE LEG CHOICE. This asks only "is there a fork at all" and hands the rest over.
    `origin_reconcile` already partitions behind-only (fast-forward), ahead-only (push) and
    diverged (isolated merge), and re-deciding that here would be a second copy of a partition
    this repo has already paid to get right once.
    """
    if reconcile_fn is None or state_fn is None or subject_fn is None:
        from background import origin_reconcile as _orc
        state_fn = state_fn or _orc.fork_state
        reconcile_fn = reconcile_fn or _orc.reconcile
        subject_fn = subject_fn or _orc.shared_tree

    # THE SUBJECT IS THE SHARED TREE, NOT `PROJECT_DIR`, AND THAT IS NOT A TIDY-UP.
    # `PROJECT_DIR` is `Path(__file__).parent.parent` -- whichever tree this module was IMPORTED
    # from. Today the unit sets WorkingDirectory to the shared tree so the two agree, which is
    # exactly what makes the bug latent rather than absent: this repo carries ten linked worktrees
    # and the seats run in them. `origin_reconcile.main` refuses to default for this reason and
    # names the measurement -- from a linked worktree its level check read 0 behind and returned
    # LEVEL while the shared tree was 2 behind with 30 consecutive publish failures. Re-deriving
    # the subject here from `__file__` would re-import that defect through the new caller, and it
    # would report SETTLED about a tree nothing publishes from.
    #
    # IT IS NOT ONLY THE LEVEL READ. `reconcile` threads `project` into `gate_is_running`, which
    # resolves the gate's lock file under that path -- so a wrong subject reads "no gate running"
    # while a real gate holds the real lock, and pushes underneath it.
    subject = subject_fn()
    if subject is None:
        return ("fork with origin NOT ATTEMPTED: the shared tree could not be established, so the "
                "subject is unknown -- refused rather than defaulted to this module's own tree")

    behind, ahead = state_fn(subject)
    if behind is None or ahead is None:
        return ("fork with origin UNREADABLE (behind={}, ahead={}); not acting on a state that "
                "was not observed".format(behind, ahead))
    if not behind and not ahead:
        return None                       # level: the common case, and it says nothing

    result = reconcile_fn(subject) or {}
    status = str(result.get("status", "UNREPORTED"))
    # THE STATUS IS THE RC. `origin_reconcile.main` turns exactly this set into exit 0 and
    # everything else into exit 1, so recording the status records the rc without shelling out to
    # get it -- and it records WHICH of the four settled shapes it was, which the rc throws away.
    settled = status in _FORK_SETTLED
    return "fork with origin ({} behind, {} ahead) -> {} [{}]: {}".format(
        behind, ahead, status, "settled" if settled else "STILL OPEN",
        str(result.get("detail", ""))[:400])


def run(proc_results: list[dict] | None = None,
        sched_results: list[dict] | None = None,
        notify=None,
        gap_results: list[dict] | None = None,
        reconcile_fork=None) -> bool:
    """Run one reconcile, log it, and NTFY only on a drift-set TRANSITION. Returns True if it
    paged. `notify` and results are injectable for tests; production reads live + uses send_ntfy."""
    if proc_results is None:
        proc_results = _proc.reconcile(_proc._live_unit_states(), _proc._seat_active(),
                                       _proc._live_tmux_running())
    if sched_results is None:
        sched_results = _sched.reconcile()
    if gap_results is None:
        gap_results = _gap.reconcile()

    # Claimed-but-not-moving work goes back to the draw. It rides THIS timer rather than one
    # of its own because it is the same question the rest of this module asks -- what was
    # declared, versus what is actually true -- applied to work in hand instead of to
    # processes and units. It is deliberately NOT part of the drift signature and never pages:
    # a stalled claim is not an emergency, and the correct outcome is that the work moves, not
    # that a phone buzzes. See background/seat_work_in_hand.py for the 4h23m stall that every
    # existing watcher, including this one, reported as clean.
    try:
        released = _seat.sweep()
        if released:
            _log(f"seat claims released back to the draw: {', '.join(released)}")
    except Exception as exc:                                   # noqa: BLE001
        # A failure here must never stop the reconcile that this module exists to run.
        _log(f"seat-claim sweep failed (reconcile continues): {exc!r}")

    # SEAT CONTINUITY (2026-08-24, director: "nothing notices it has stopped ... I shouldn't
    # be the mechanism that spots a stall"). The sweep above releases work the seat CLAIMED
    # and then stopped moving; this one handles the case where the seat itself is gone —
    # killed mid-edit by an API error, holding uncommitted work nobody has a record of.
    #
    # HERE rather than in a timer of its own, for the same reason the claim sweep is here:
    # this module already runs every five minutes and already asks "what was declared versus
    # what is actually true". A new timer would be a new thing that can silently fail to be
    # armed, which is the failure class this whole file exists to catch.
    try:
        from background import seat_continuity

        filed = seat_continuity.sweep()
        if filed:
            _log(f"interactive seat stopped mid-work; handoff filed: {filed}")
    except Exception as exc:                                   # noqa: BLE001
        _log(f"seat-continuity sweep failed (reconcile continues): {exc!r}")

    # DAEMONS RUNNING CODE THAT IS NO LONGER HEAD. R2 -- "committed != running" -- is one of
    # this repo's permanent rules, and on 2026-08-21 three daemons were 57, 63 and 65 changed
    # loaded modules behind, four days stale. The supervisor was making draw decisions on
    # four-day-old logic and a publishing-down alarm fixed that morning was inert in the process
    # that runs it.
    #
    # THE CONTROL WAS NOT MISSING. `process_reconciler.evaluate_boot_sha_drift()` computes this
    # precisely, and `health_check.py` phrases the fault well ("daemon(s) running an OLD copy of
    # a module they import (restart to deploy)"). Its only caller is `start_worker.sh`, at stack
    # startup -- so it ran at the single moment drift CANNOT exist and never during the four days
    # it accumulated. `health-check-log.md`'s last entry is 2026-07-29. Same shape as the seam
    # ratchet that wedged publishing for 27 hours the same day: a control that only fires when it
    # cannot.
    #
    # It rides this timer for the same reason the seat-claim sweep does -- declared-versus-actual
    # is the question this module already asks, and a fix's WORTH is exactly its deployment.
    try:
        drift = _drift_report()
        if drift:
            _log("boot-sha drift: " + "; ".join(drift))
    except Exception as exc:                                   # noqa: BLE001
        _log(f"boot-sha drift check failed (reconcile continues): {exc!r}")

    sig, summary = build_report(proc_results, sched_results, gap_results)
    last = _load_last()
    # UNREADABLE IS NOT `[]`. See `_load_last` for the direction and why it is this one: a lost
    # memory compared against a clean reconcile is EQUAL, and the page it silences is the recovery.
    unreadable = last is None
    changed = unreadable or sig != last
    if unreadable:
        summary = f"{_PRIOR_UNREADABLE_NOTE}\n{summary}"

    disposition = ("prior UNREADABLE -> paging the current state, transition unknown" if unreadable
                   else "transition -> paging" if changed else "unchanged -> log only")
    _log(f"reconcile {'DRIFT' if sig else 'clean'} ({len(sig)} alarm(s)); {disposition}")

    if changed:
        if notify is None:
            # THE CONTRACT, not the raw POST (2026-08-13). This called `send_ntfy` directly, so it
            # sat OUTSIDE `background.notify` and therefore outside G-N3 routing entirely -- which
            # is why a drift report the director cannot act on within the hour reached his phone
            # roughly twelve times on 2026-08-13, most of them the same five gap-ledger rows. Its
            # own name is the classification: manifest DIVERGENCE is the first category he listed
            # for batching.
            from background.notify import notify as notify
        # An unreadable prior beside a clean reconcile IS the all-clear the old code swallowed, so
        # it carries the recovery tag -- with the note above saying we cannot prove it was a
        # change. Tagging it `rotating_light` would page an alarm for a state with no drift in it.
        cleared = not sig and (unreadable or bool(last))
        notify(summary, headers={
            "X-Tags": "white_check_mark" if cleared else "rotating_light",
            "X-Priority": "default" if cleared else "high",
        }, kind="real_alarm", topic_class=_digest_class())
        _save(sig)

    # CLOSING THE FORK GOES LAST, AND THE ORDER IS THE POINT. The merge leg can run for up to
    # MERGE_TIMEOUT_SECONDS (25 min) against a five-minute tick, so anything sequenced after it is
    # a drift page that arrives late. Paging is this module's first duty and the fork is its
    # second; putting the slow, acting step behind the fast, reporting one means a wedged merge
    # costs a delayed reconcile and never a delayed alarm.
    try:
        line = (reconcile_fork or _reconcile_the_fork)()
        if line:
            _log(line)
    except Exception as exc:                                   # noqa: BLE001
        # Same fail-safe as every other rider on this timer: the reconcile is the thing that must
        # not stop. This one is last, so by here the page has already gone out regardless.
        _log(f"fork reconcile failed (reconcile continues): {exc!r}")
    return changed


def main(argv: list[str]) -> int:
    run()
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/reconcile_watch.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("reconcile_watch")
    raise SystemExit(main(sys.argv))
