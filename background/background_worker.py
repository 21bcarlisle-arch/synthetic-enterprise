#!/usr/bin/env python3
"""
Synthetic Enterprise — Background Worker
Runs autonomously using local Qwen only (no frontier tokens).
Checks docs/instructions/background-tasks.md for queued tasks.
Respects UK peak electricity hours: pauses between 16:00-19:00 GMT daily.
Logs all activity to docs/observability/background-worker-log.md
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Stdlib-only helper (H30) -- safe at module scope, unlike the publish pipeline.
from background import publisher_budget  # noqa: E402
from background.child_diagnostics import child_output_excerpt  # noqa: E402
from background.episode_monotonic import guard_episode  # noqa: E402  (PW4)

PEAK_START = 16  # 4pm GMT
PEAK_END = 19    # 7pm GMT
CHECK_INTERVAL_MINUTES = 30
TASKS_FILE = Path("docs/instructions/background-tasks.md")
# Mirrors background.process_run_complete.EXIT_LOCK_SKIPPED. Duplicated as a
# literal (rather than imported at module scope) because importing the
# publish pipeline at worker import time drags in the whole reporting stack;
# tests/background/test_background_worker.py pins the two values equal so the
# mirror can never silently drift back into "a skip looks like a success".
EXIT_LOCK_SKIPPED = 75
# Same mirror, same pin, same reason (2026-08-12): a marker another publisher archived between
# this sweep's glob and the subprocess opening it was published by NOBODY here, so it must not
# reach the rc==0 branch below -- that branch logs "Processed" and calls
# _record_marker_published(), PW4's one evidenced close of the zero-progress episode.
EXIT_NOTHING_PUBLISHED = 76
NOT_PUBLISHED_BY_THIS_SWEEP = (EXIT_LOCK_SKIPPED, EXIT_NOTHING_PUBLISHED)
LOG_FILE = Path("docs/observability/background-worker-log.md")
OLLAMA_MODEL = "qwen3:14b"

def is_peak_hours():
    """Return True if current GMT time is between 16:00 and 19:00."""
    now_gmt = datetime.now(timezone.utc)
    return PEAK_START <= now_gmt.hour < PEAK_END

def log(message: str):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{timestamp}] {message}"
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)

def run_ollama_task(prompt: str, task_name: str) -> str:
    """Run a task via local Ollama. Returns the model output."""
    log(f"Starting task: {task_name}")
    result = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL, prompt],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        log(f"Task failed: {task_name} — {result.stderr[:200]}")
        return ""
    log(f"Task complete: {task_name}")
    return result.stdout

STAGING_DIR = Path("docs/staging")
DONE_DIR = STAGING_DIR / "done"
# Persistent sweep state (oldest-marker stall counter). Module-level so tests
# can redirect it -- a new real-disk flag that tests do NOT pin leaks into
# every unpinned loader and starts alarming off other tests' fixtures.
SWEEP_STATE_FILE = Path("docs/observability/.run_marker_sweep_state.json")
# Consecutive sweeps with the SAME oldest marker still sitting in staging/
# before the zero-progress alarm fires. The worker loop is 30 min, so this is
# ~1.5h of a retry loop that is provably not retrying.
STALL_ALARM_CYCLES = 3


def _marker_stamp(name: str) -> str | None:
    """`run_complete_20260803T064304Z.md` -> `20260803T064304Z`.

    Returns None for anything that does not parse. FAIL-SAFE DIRECTION (R15):
    an unparseable name is treated as PENDING by every caller, never as
    superseded -- the failure mode of a bad parse must be "we tried to publish
    something we didn't need to", never "we retired a marker nobody published".
    """
    stem = Path(name).stem
    if not stem.startswith("run_complete_"):
        return None
    stamp = stem[len("run_complete_"):]
    return stamp or None


def _newest_published_stamp(done_dir: Path) -> str | None:
    """The latest run stamp that actually REACHED the archive, i.e. the newest
    run whose publish pipeline ran to completion. This is the supersession
    frontier: any marker older than it describes a snapshot that has already
    been overtaken on every published surface.

    Reads the UNION of done/ and the exhaust tree (AO10 moved ~4,300 markers
    out of done/ into docs/staging/exhaust/<YYYY-MM>/). Globbing done/ alone
    would now return nothing, and a frontier of None classifies every leftover
    marker as PENDING -- republishing a stale snapshot over current figures,
    the exact fidelity regression classify_markers() exists to prevent."""
    from background import staging_archive_policy
    stamps = [
        s for s in (
            _marker_stamp(p.name)
            for p in staging_archive_policy.iter_marker_paths("run_complete_", done_dir=done_dir)
        ) if s
    ]
    return max(stamps) if stamps else None


def classify_markers(markers, newest_published):
    """Split leftover markers into (superseded, pending).

    SUPERSEDED == a strictly LATER run has already been published. Re-running
    the pipeline on such a marker does not "catch up" -- it regenerates
    ANNUAL_REPORT.md, LATEST.md and the whole site FROM A STALE SNAPSHOT,
    overwriting current figures with older ones. That is a fidelity
    regression (R11/R14: every published figure carries its clock; this would
    silently wind the clock backwards), so supersession is a TERMINAL state,
    not a retry state.

    Ordering is lexicographic on the fixed-width UTC stamp, which for this
    format is chronological. Unparseable names sort as pending (see
    _marker_stamp)."""
    superseded, pending = [], []
    for marker in markers:
        stamp = _marker_stamp(marker.name)
        if newest_published and stamp and stamp < newest_published:
            superseded.append(marker)
        else:
            pending.append(marker)
    return superseded, pending


def retire_superseded_marker(marker: Path, newest_published: str, done_dir: Path) -> bool:
    """Move a superseded marker to done/ with the reason RECORDED IN THE FILE.

    R10 forbids closing the backlog defect by DELETING the backlog. This does
    not delete: the marker keeps its content and gains an explicit
    superseded-by stamp, so an auditor reading done/ can see exactly why this
    run was never published and which run overtook it."""
    try:
        done_dir.mkdir(parents=True, exist_ok=True)
        note = (
            "\n\n## Superseded (not published)\n\n"
            f"Retired by background_worker.process_leftover_run_markers() at "
            f"{datetime.now(timezone.utc).isoformat()}.\n"
            f"A strictly later run ({newest_published}) had already completed its publish "
            f"pipeline, so this snapshot was overtaken on every published surface before "
            f"this marker could be processed. Re-running the pipeline here would have "
            f"republished stale figures over current ones. No publish was performed.\n"
        )
        with open(marker, "a") as fh:
            fh.write(note)
        marker.rename(done_dir / marker.name)
        return True
    except Exception as exc:
        log(f"Could not retire superseded marker {marker.name}: {exc}")
        return False


def _load_sweep_state() -> dict:
    try:
        return json.loads(SWEEP_STATE_FILE.read_text())
    except Exception:
        return {}


def _save_sweep_state(state: dict):
    try:
        SWEEP_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SWEEP_STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception as exc:
        log(f"Could not persist run-marker sweep state: {exc}")


def _remember_oldest_outcome(name: str, rc: int) -> None:
    """Persist the last publisher outcome for the OLDEST pending marker (EPISODE4 item 2).

    Kept deliberately small and defensive: this only feeds an alarm's wording, so a failure to
    record it must never disturb the sweep it is observing."""
    label = {0: "rc=0 (published)",
             EXIT_LOCK_SKIPPED: f"rc={EXIT_LOCK_SKIPPED} (lock-skipped, not attempted)",
             # Without its own entry a duplicate fell into the default below and was reported to
             # the alarm as "publisher ran and FAILED", which is the opposite of what happened.
             EXIT_NOTHING_PUBLISHED: f"rc={EXIT_NOTHING_PUBLISHED} (duplicate — already "
                                     "published by another process, nothing done here)",
             }.get(rc, f"rc={rc} (publisher ran and FAILED — a red publish gate "
                       "looks exactly like this)")
    try:
        state = _load_sweep_state()
        state["last_outcome"] = f"{label} at {datetime.now(timezone.utc):%H:%M}Z"
        state["last_outcome_marker"] = name
        _save_sweep_state(state)
    except Exception as exc:  # noqa: BLE001 -- an observer must never break the observed
        log(f"Could not record sweep outcome for {name}: {exc}")


SWEEP_STREAK_FIELDS = ("cycles",)   # PW4 -- the zero-progress episode counter


def _record_marker_published(name: str) -> None:
    """PW4 -- THE CLOSE CONDITION for the sweep's zero-progress episode: a marker was PUBLISHED.

    `cycles` counts consecutive zero-progress sweeps and `_check_zero_progress` writes the
    counter its own alarm reads, so the census flags it as self-clearing. Its close used to be
    implicit and wrong: "the oldest marker's NAME changed". A superseded marker is retired by a
    rename that needs no run lock and cannot be lock-skipped -- it drains the queue whether or
    not the publish path works -- so a retirement changed `oldest` and silently reset the count
    on a stall that was still running.

    THE CONDITION: a publisher invocation returned rc == 0. That is the return code of a
    subprocess, read at the one site that sees it, and is independent of
    `.run_marker_sweep_state.json` by construction (R15 anti-tautology).

    This is the ONLY close besides an empty queue. It is deliberately narrower than "the backlog
    shrank": the alarm's claim is that the PUBLISH PATH is not moving, and only a publish
    refutes it."""
    try:
        state = _load_sweep_state()
        if not state.get("cycles") and not state.get("stalled_on"):
            return                      # no open episode to close
        closed = guard_episode(state, dict(state, cycles=0, oldest=None, stalled_on=None),
                               streak_fields=SWEEP_STREAK_FIELDS, episode_closed=True)
        _save_sweep_state(closed)
        log(f"Run-marker sweep: zero-progress episode CLOSED — {name} published (rc=0)")
    except Exception as exc:  # noqa: BLE001 -- an observer must never break the observed
        log(f"Could not close the sweep zero-progress episode for {name}: {exc}")


def _check_zero_progress(pending):
    """A retry loop that has NEVER succeeded is an ALARM, not a log line.

    THE DEFECT THIS CLOSES (2026-08-03, atom OPS_run_marker_sweep_livelock):
    the sweep logged `Lock-skipped ... will retry next cycle` 404 times per
    cycle, for days. That is the vocabulary of a healthy transient queue, and
    it is indistinguishable in the log from progress -- so a permanent total
    failure read as a working retry. FAIL-SILENT, exactly the R15 pattern.

    The signal is the OLDEST pending marker: if the same marker is still the
    oldest N sweeps running, nothing is draining, whatever the per-marker log
    lines say. R5: fires ONCE on the transition into the stalled state and
    stays quiet until the oldest marker actually changes."""
    state = _load_sweep_state()
    oldest = pending[0].name if pending else None
    if oldest is None:
        if state.get("stalled_on"):
            log("Run-marker sweep: backlog cleared — zero-progress alarm reset")
        # PW4: an EMPTY queue is an evidenced close -- the same independent signal the publish
        # gate's own episode uses (pending_run_complete_markers() == 0). The thing the alarm
        # measures no longer exists, so there is no episode left to shorten.
        _save_sweep_state({})
        return False
    # PW4: the episode does NOT close because `oldest` changed. A superseded marker being
    # RETIRED (a rename to done/, which needs no run lock and so happens whether or not
    # publishing works at all) changes `oldest` without a single marker having been published --
    # and that reset the counter this alarm reads, so a persistent publish stall paged as a
    # first occurrence. The ONLY close is _record_marker_published(), written at the site that
    # sees rc == 0.
    cycles = int(state.get("cycles", 0)) + 1
    guarded = guard_episode(state, {"cycles": cycles}, streak_fields=SWEEP_STREAK_FIELDS,
                            episode_closed=False)
    cycles = guarded["cycles"]
    # R5 keyed on the EPISODE, not on the oldest marker's name: once alarmed, stay quiet until
    # the episode genuinely closes. Keying on `oldest` meant a retirement -- which does not close
    # the episode -- would re-fire the page on an unchanged status.
    already_alarmed = bool(state.get("stalled_on"))
    fire = cycles >= STALL_ALARM_CYCLES and not already_alarmed
    # PRESERVE the observed outcome across the save. This used to replace the whole state dict,
    # which silently dropped `last_outcome`/`last_outcome_marker` every cycle -- the alarm only
    # still read them because it holds the pre-save `state`. That fragility is a defect in its
    # own right (it made the retry property untestable), so the fields are carried explicitly.
    _save_sweep_state({
        "oldest": oldest, "cycles": cycles,
        "stalled_on": oldest if (fire or already_alarmed) else None,
        "last_outcome": state.get("last_outcome"),
        "last_outcome_marker": state.get("last_outcome_marker"),
    })
    if fire:
        # R9 APPLIED TO A CONTROL (EPISODE4 item 2, 2026-08-09). This alarm used to end
        # "The publish retry loop is not retrying — treat 'will retry next cycle' as FALSE."
        # That is an INFERENCE, and on 2026-08-09 it was measurably WRONG: the oldest marker
        # was attempted at 14:01 (rc=1) and again at 14:54 (rc=1), straddling this alarm's own
        # 14:48 firing. The loop retried exactly as promised; the retries FAILED, because the
        # publish gate was red on a stale derived artefact. Zero progress and "not retrying"
        # are different claims, and this detector can only observe the first.
        #
        # The cost of asserting the wrong one is not cosmetic: it sent the diagnosis at a
        # retry-loop bug that does not exist while the real cause sat one line above in the
        # same log, as `rc=1`. So the alarm now reports WHAT IT SAW (no progress, and the last
        # recorded publisher outcome, which it does have) and names the gate as where to look.
        # Same defect class as the ghost-pusher tripwire: a verdict that is an inference rather
        # than an observation.
        last = state.get("last_outcome") or _load_sweep_state().get("last_outcome")
        cause = (f" Last publisher outcome for it: {last}." if last
                 else " No publisher outcome recorded yet for it.")
        msg = (
            f"[ACTION NEEDED] Run-marker sweep has made ZERO progress for {cycles} "
            f"consecutive cycles: {oldest} is still the oldest of {len(pending)} pending "
            f"run_complete marker(s).{cause} The sweep IS re-attempting every pending marker "
            f"each cycle (unconditional glob) — so this is the publish path failing, not the "
            f"retry loop stopping. Look at the publish gate's blocking test in "
            f"docs/observability/sim-runner-log.md, not at the sweep."
        )
        log(msg)
        try:
            # Pages through the ONE contract (G-N2: an untyped page is forbidden).
            # No transition_key: this call site already owns its own transition
            # suppression via the `stalled_on`/`already_alarmed` sweep state above,
            # and keying it again would suppress the retry that block depends on.
            from background.notify import notify
            notify(msg, kind="real_alarm")
        except Exception as exc:
            # An unavailable checker is a FAILED check, not a passed one (R15
            # FAIL-SILENT). The alarm still lands in the worker log above, and
            # we do NOT record it as alarmed, so the next cycle retries the send.
            log(f"Zero-progress alarm NTFY failed (alarm stands, will re-send): {exc}")
            state = _load_sweep_state()
            state["stalled_on"] = None
            _save_sweep_state(state)
    return fire


def beat_liveness() -> bool:
    """Publish the liveness surface, whether or not any content published. Returns True iff a
    fresh liveness commit reached origin.

    LIVENESS IS NOW ITS OWN JOB, AND THIS LANDS BEFORE THE CADENCE SLOWS. Director, 2026-09-04:
    *"The publish path has been our best liveness signal — when the site stops we know something is
    wrong — so give that job to something else before you slow it down."* The site is moving to a
    WEEKLY content cadence, and the moment it does, "the site stopped" stops meaning anything: six
    days in seven it is correct.

    THE MECHANISM ALREADY EXISTED AND WAS WIRED TO THE WRONG THING. `process_run_complete.
    _refresh_published_liveness_on_skip` publishes ONLY `LIVENESS_SURFACE_FILES` — a heartbeat and
    the agent status, no figures — and was built for exactly this separation (Fault#1, 2026-07-25:
    "an unchanged-output night froze the live-site heartbeat ~4h though the machine was healthy").
    But it could only ever run INSIDE a publish cycle, so it inherited the cadence it exists to be
    independent of. Here it runs every worker cycle (~30 min) with no content publish required.

    Cheap by construction: two small files, its own narrow pathspec, and `_push_due()` throttles the
    push. Wrapped, because a liveness beat may never take the sweep down — it is a passenger.
    """
    try:
        from background import process_run_complete as _prc
        if _prc._refresh_published_liveness_on_skip(_prc._head_sha() or "unknown"):
            log("Liveness heartbeat published (content cadence is weekly; this is the signal that "
                "the machine is alive between publishes)")
            return True
    except Exception as exc:  # noqa: BLE001 -- a passenger, never a gate on the sweep
        log(f"Liveness heartbeat skipped (non-fatal): {exc}")
    return False


def process_leftover_run_markers():
    """Process any run_complete_*.md markers that process_run_complete.py left behind.

    UNDOCUMENTED COUPLING, now documented (2026-07-13, director-flagged): this
    function is the ENTIRE real safety net for a marker that
    `background/sim_runner.py` itself skipped -- sim_runner.py only ever
    passes process_run_complete.py the ONE marker it just wrote each
    iteration, and process_run_complete.py's own lock-skip path returns
    EXIT_LOCK_SKIPPED (75) without touching the marker, so a marker
    left behind because another instance was already running is NEVER
    retried by sim_runner.py itself. This function's own unconditional glob
    of every `run_complete_*.md` still in staging/ -- called at the TOP of
    background_worker.py's main loop, every cycle, "regardless of peak
    hours" per that call site's own comment -- is what actually keeps the
    promise the skip-path's own log line makes ("will be picked up... next
    cycle"). If this function is ever removed, disabled, or made
    conditional, a lock-skipped marker becomes permanently orphaned with no
    other mechanism to rescue it -- see tests/background/
    test_background_worker.py's own test asserting this glob is genuinely
    unconditional (not gated behind queue state, peak-hours, or any other
    check) for the regression guard on this exact property."""
    markers = sorted(STAGING_DIR.glob("run_complete_*.md"))
    if not markers:
        _check_zero_progress([])
        return

    # THE GLOB STAYS UNCONDITIONAL (see docstring above) -- every leftover
    # marker is still collected and still DISPOSED every cycle. What changed
    # (2026-08-03, OPS_run_marker_sweep_livelock) is that disposal now has a
    # terminal state other than "published": a marker a later published run
    # has already overtaken is RETIRED, not retried forever. Retiring is a
    # rename, not a pipeline run, so it needs no run lock and cannot be
    # lock-skipped -- which is what turned this sweep into a livelock.
    done_dir = STAGING_DIR / "done"
    newest_published = _newest_published_stamp(done_dir)
    superseded, pending = classify_markers(markers, newest_published)

    if superseded:
        retired = sum(
            1 for m in superseded
            if retire_superseded_marker(m, newest_published, done_dir)
        )
        log(f"Retired {retired}/{len(superseded)} superseded run_complete marker(s) "
            f"— overtaken by published run {newest_published}, not republished")

    _check_zero_progress(pending)

    if not pending:
        return
    # DRAIN-SUPERSESSION (OPS3, 2026-08-14). `pending` is ascending and this loop used to walk
    # it OLDEST-FIRST. That is the fidelity regression classify_markers() exists to prevent,
    # reached from the other side: supersession was only ever computed against what had ALREADY
    # published, never against the marker about to publish, so a marker that no completed run
    # had yet overtaken was "pending" however stale it was. With one publisher cycle costing up
    # to _publisher_deadline_seconds() against a sim_runner minting a marker every ~10 min, the
    # queue GROWS, and the snapshot the pipeline publishes is the one at the BACK of it —
    # measured 2026-08-14 19:22Z: 102 pending, publisher chewing 20260814T090117Z while
    # 20260814T183636Z sat unpublished, i.e. the figures about to be published were 9.5h stale.
    # Publishing that overwrites current figures with older ones — winding the clock backwards,
    # which classify_markers' own docstring calls a fidelity regression under R11/R14.
    #
    # The queue is a STACK, not a FIFO: every marker describes the SAME thing (the state of the
    # world after a run), so the newest strictly dominates and the older ones carry nothing it
    # lacks. Publish the newest; the rest are superseded BY IT, retired naming it.
    order = list(reversed(pending))
    log(f"Found {len(pending)} leftover run_complete marker(s) — processing newest-first "
        f"({order[0].name} first of {len(order)})")
    processor = Path(__file__).parent / "process_run_complete.py"
    for position, marker in enumerate(order):
        try:
            result = subprocess.run(
                [sys.executable, str(processor), str(marker)],
                cwd=str(Path(__file__).resolve().parent.parent),
                # NOT A NUMBER OF OUR OWN (2026-08-10). This was an independent `timeout=900`
                # and it drifted below the budget of the very process it wraps: the publisher's
                # gate alone may legitimately run to GATE_SUITE_TIMEOUT_SECONDS (2600s, derived
                # against the cold HEAD-checkout subject), so every cold cycle was killed here
                # at 900s before the gate could return a verdict. Observed 17:44Z on 2026-08-10:
                # 95 markers pending, 142 recorded "failures", and the blocking test they were
                # blamed on passing at HEAD. A wrapper bound below the work it wraps decides the
                # inner gate's verdict by stopwatch. Importing the publisher's own declared
                # budget is what stops the pair drifting again -- re-deriving the gate's bound
                # now moves this one with it, which no comment could guarantee.
                timeout=_publisher_deadline_seconds(),
                # H30 (2026-08-08): this sweep is the SAFETY NET for every skipped
                # marker, so "Failed to process (rc=N)" with no payload is the one
                # log line a backlog diagnosis starts from. Capture what the
                # publisher actually said.
                #
                # BOTH STREAMS (2026-08-21). This captured stderr ALONE for thirteen
                # days, and the publisher does not refuse on stderr: every verdict
                # `process_run_complete.log()` issues goes to **stdout**. So all 46
                # refusals across the 32-hour wedge of 2026-08-20/21 logged the same
                # four lines of pytensor/SyntaxWarning noise and never once named the
                # cause -- which was, in the end, one line the publisher had printed
                # every cycle ("Fast test suite timed out"). The comment above claimed
                # this capture existed; only half of it did.
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.TimeoutExpired as exc:
            # UNCAUGHT, THIS ABORTED THE WHOLE SWEEP -- the identical defect this project
            # already fixed one layer DOWN, for the same reason, in the same words
            # (process_run_complete.git_commit_push's own TimeoutExpired handler, and
            # CLAUDE.md's standing learning "sim_runner TimeoutExpired must be caught").
            # The exception propagated out of this loop to main()'s catch-all, so ONE slow
            # marker abandoned all 94 behind it, and -- worse -- skipped the three lines
            # below it: the oldest-outcome memory, the failure log, and the wedge detector.
            # A kill therefore reached the detector as NOTHING, while the detector's own
            # docstring claims it sees "OOM SIGKILL rc=-9". It sees return codes; a timeout
            # kill has none. Fail-silent (R15), and it is why a 27h wedge kept naming a test
            # that passes.
            log(f"TIMED OUT processing {marker.name} after {_publisher_deadline_seconds()}s "
                f"— the publisher outran the deadline this sweep puts on it. NOT a test "
                f"failure: the gate it was running never returned a verdict. Marker left "
                f"pending; continuing to the next one. What it had written before the kill:\n"
                + child_output_excerpt(getattr(exc, "stdout", None),
                                       getattr(exc, "stderr", None)))
            if position == 0:
                _remember_oldest_outcome(marker.name, None)
            # rc=None, kind stated: a deadline kill produces no return code, and inventing
            # one would launder a stopwatch into evidence about the tests.
            _record_publish_gate_outcome(marker, None, kind="deadline_kill")
            continue
        # EPISODE4 item 2: remember what actually happened to the OLDEST pending marker, so the
        # zero-progress alarm can report an observed cause instead of inferring one. Written
        # here (not in the alarm) because this is the only place that sees the return code.
        if position == 0:
            _remember_oldest_outcome(marker.name, result.returncode)
        if result.returncode == EXIT_LOCK_SKIPPED:
            # NOT processed -- another instance holds the run lock and the
            # marker is untouched. Saying "Processed" here was a false claim in
            # the worker log (it is what a reader sees first when diagnosing a
            # backlog) as well as a false success to the wedge detector.
            log(f"Lock-skipped {marker.name} (another instance holds the run "
                f"lock) — still pending, will retry next cycle")
        elif result.returncode == EXIT_NOTHING_PUBLISHED:
            # NOT published by this sweep -- a concurrent publisher had already archived it.
            # Visible in the log (a silent outcome would be its own defect) but NOT progress:
            # the marker leaving the backlog is somebody else's act, not evidence that this
            # sweep is moving, so it must not close the zero-progress episode.
            log(f"Duplicate {marker.name} (already archived by another publisher) — nothing "
                f"published by this sweep")
        elif result.returncode == 0:
            log(f"Processed {marker.name}")
            # PW4: the ONE evidenced close of the zero-progress episode (see
            # _record_marker_published) -- written here because this is the only place that sees
            # a publish actually succeed.
            _record_marker_published(marker.name)
            # DRAIN-SUPERSESSION (OPS3). This marker just completed its publish pipeline, so
            # every marker still queued behind it is -- by the ordering above -- STRICTLY OLDER
            # and now genuinely overtaken on every published surface. That is the same terminal
            # state classify_markers() assigns, on the same evidence (a later run published);
            # the only thing that was missing is that the frontier is read once at the TOP of
            # the sweep, so a run published by THIS sweep never retired anything until the next
            # one. Retiring them here is what makes the backlog drain in one cycle instead of
            # one-marker-per-cycle against an arrival rate that outruns it.
            #
            # NOT a bulk-archive (R10): each is retired through the same audited path, keeping
            # its content and gaining a note naming the run that superseded it.
            drained = [m for m in order[position + 1:] if m.exists()]
            if drained:
                stamp = _marker_stamp(marker.name)
                retired = sum(
                    1 for m in drained
                    if retire_superseded_marker(m, stamp, done_dir)
                )
                log(f"Drain-superseded {retired}/{len(drained)} older run_complete marker(s) "
                    f"— overtaken by {marker.name}, which published in this sweep")
            _record_publish_gate_outcome(marker, result.returncode)
            # Publishing an older snapshot AFTER a newer one has published is the clock-rewind
            # this ordering exists to stop, so the sweep ends here rather than walking on.
            return
        elif position == 0:
            # THE FRONTIER FAILED, AND THE SWEEP USED TO WALK BACKWARDS FROM HERE. Observed live
            # 2026-09-04 10:35: `run_complete_20260904T085811Z` refused (commit_refused), and the
            # next thing the sweep started was `...T084511Z` — an OLDER marker, at a full
            # expensive cycle, publishing a progressively older snapshot. That is precisely the
            # clock-rewind the success branch above ends the sweep to prevent, reached through
            # the failure branch, and it is why the queue grew (15 -> 17) while every individual
            # log line said "will retry next cycle".
            #
            # NOTHING IS RETIRED HERE, AND THE FIRST DRAFT OF THIS BRANCH GOT THAT WRONG. Retiring
            # the queue behind a FAILED frontier was caught by three controls that already exist —
            # `test_a_red_gate_retires_nothing_and_keeps_the_whole_backlog`,
            # `..._a_crashed_publisher_is_not_a_publish_and_retires_nothing`,
            # `..._a_lock_skipped_newest_does_not_retire_the_queue_behind_it` — and they are right:
            # retirement is justified by a marker having PUBLISHED, and a red gate that ate its own
            # queue would leave the wedge detector reading an empty backlog as health. The depth of
            # this queue IS the evidence that publishing is stuck, and it must survive.
            #
            # WHAT IS FIXED IS THE WALK, WHICH IS SEPARABLE FROM THE RETENTION. Every marker stays
            # pending, exactly as those controls require; the sweep simply stops instead of
            # attempting each older one in turn. The next sweep re-globs and starts from the newest
            # marker on disk, which at a marker every 13.3 minutes is newer than the one that just
            # failed. Walking on could only ever publish something staler than what already
            # refused, at a full expensive cycle each.
            _record_publish_gate_outcome(marker, result.returncode)
            # THROUGH `child_output_excerpt`, NOT A RAW TAIL (2026-09-04). This branch is new in
            # 3d369242c and it hand-rolled its own rendering, which silently undid three landed
            # repairs at once: the lowercase stream LABEL (2026-08-21 — a reader cannot tell the
            # publisher's verdict from whatever the runtime warned about last), BOTH streams rather
            # than stdout alone (2026-08-21 — a child that dies on an uncaught traceback says
            # nothing on stdout), and `verdict_excerpt` SELECTION rather than a positional tail
            # (2026-08-24 — a publish prints ~100 "Generated site/data/*.json" lines AFTER the
            # sentence naming its refusal, so the tail renders forty things that went right).
            # Only the label was under a control, so only the label went red; the sibling that
            # checks for the cause phrase passed on luck, because the raw tail happened to still
            # contain it. The excerpt helper is the one place all three live.
            log(f"Failed to process {marker.name} (rc={result.returncode}) — the sweep ends here "
                f"and the NEXT one retries from the newest marker on disk. The publisher's own "
                f"verdict is on STDOUT:\n"
                + child_output_excerpt(getattr(result, "stdout", None),
                                       getattr(result, "stderr", None)))
            return
        else:
            log(f"Failed to process {marker.name} (rc={result.returncode}) — will retry next "
                f"cycle. The publisher's own verdict is on STDOUT:\n"
                + child_output_excerpt(getattr(result, "stdout", None),
                                       getattr(result, "stderr", None)))
        # H15_publish_gate_failure_alert: feed every processing outcome into the
        # publish-gate wedge detector. This sweep is the recurring caller that
        # actually manifests a silent wedge -- process_run_complete returns
        # rc!=0 every cycle (test-fail / OOM SIGKILL rc=-9 / report-regen fail)
        # and leaves the marker in staging, so N consecutive failures here == a
        # stalled pipeline that must raise ONE [ACTION NEEDED] alert.
        _record_publish_gate_outcome(marker, result.returncode)


def _publisher_deadline_seconds():
    """The deadline this sweep puts on ONE publisher run — the publisher's OWN declared
    budget, never a number of ours, and never one this process cached earlier.

    READ FROM DISK, NOT FROM `sys.modules` (2026-08-22). This used to be a lazy
    `from background import process_run_complete`, with a docstring claiming that importing
    at CALL time kept the number current. It does not: a lazy import is still a one-time
    import, so the constant was whatever was on disk when THIS DAEMON first published. This
    sweep ran for ten hours on a 4300s deadline it had frozen at 17:28:59 on 2026-08-21
    while the publisher declared 4700 — and `sim_runner`, started inside a 78-minute window
    when the gate bound was transiently 300, froze 1200 and killed four consecutive publish
    cycles on a stopwatch. `background.publisher_budget` asks the file every time.

    FAIL-LONG, not fail-short. A too-long deadline delays one diagnosis; a too-short one
    decides the inner gate's verdict by stopwatch, which is the whole defect."""
    try:
        return publisher_budget.declared_publisher_budget_seconds()
    except Exception as exc:
        log(f"publisher deadline falling back (publisher would not declare it: {exc})")
        return publisher_budget.FALLBACK_SECONDS


def _record_publish_gate_outcome(marker, rc, *, kind=None):
    """H15: route a run-complete processing return code into the publish-gate
    failure detector (background/process_run_complete.py). Defensive by
    construction -- a monitoring failure must never break the marker sweep or
    the loop that calls it.

    THREE outcomes, not two (fail-open closed 2026-07-29). A lock-skip
    (EXIT_LOCK_SKIPPED) means this sweep did NOT publish the marker -- it is
    evidence of NOTHING about the gate's health, so it records NEITHER a
    success NOR a failure and leaves the streak exactly as it found it.
    Recording it as a success (the old behaviour, when the skip path returned
    0) actively DISARMED the detector: `record_publish_gate_success` clears the
    failure list, re-arms the alarm, and auto-resolves the open [ACTION NEEDED]
    item with "a run published cleanly" -- for a marker nobody published.
    Observed 2026-07-29 16:53Z: both backed-up markers recorded successes one
    minute before the lock holder itself failed the gate at 16:54Z, wiping the
    streak that was supposed to raise the alert.

    DELEGATES (2026-08-03): the three-outcome logic now lives ONCE in
    `process_run_complete.record_publish_gate_outcome` so that EVERY publish
    path feeds the same detector. This sweep was the only caller, which left
    the detector blind to sim_runner.py -- the path that actually publishes in
    the steady state -- for ~4 days. This wrapper stays because it is the name
    tests/background/test_background_worker.py pins.

    AND THE ROUTE ITSELF NOW LIVES ONCE TOO (2026-09-04). `sim_runner` carried a byte-for-byte
    twin of the body below, and the torn-import loss observed at 15:48Z happened in THAT one. A
    repair written here would have read as done and left the observed instance live -- the exact
    shape CLAUDE.md names as this project's most expensive. See
    `background/publish_outcome_route.py` for the incident and why the retry is bounded at two."""
    try:
        from background.publish_outcome_route import route
        route(marker, rc, kind=kind,
              log=lambda m: log(f"{m} (marker {marker.name})"))
    except Exception as exc:  # noqa: BLE001 -- a monitoring failure may never break the sweep
        # The last resort, for the vanishing case where the ROUTE is the file being written. It
        # is a leaf module importing only `time`, so this is much narrower than what it replaced.
        log(f"publish-gate outcome LOST for {marker.name} (the route could not be reached): {exc}")


def main():
    from background.agent_status import update_agent_status
    log("Background worker started")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    update_agent_status(
        "background-worker", status="idle",
        last_action="Worker started",
        role="Runs background automation tasks via local Qwen; respects 16-19 UTC peak hours",
        produces="docs/observability/background-worker-log.md",
    )

    while True:
        # RESOURCE HOUSEKEEPING, EVERY CYCLE, BEFORE ANY WORK (director ruling 2026-08-19:
        # "bounded lifetimes, alarms before exhaustion rather than after, and no reliance on
        # anyone noticing"). This is the WIRING, and the wiring is the whole point: the RAM
        # governor was built on 2026-08-10 after 64 oom-kills and had NEVER RUN -- no caller,
        # no unit, no state file -- so the machine ran out of memory once and out of disk once
        # with a governor for each sitting in the tree. Both are called here, in the one loop
        # that is actually a running daemon, ahead of the work so pressure is known before
        # anything allocates.
        #
        # Never fatal: a governor that can crash the worker is a worse outage than the one it
        # prevents. It logs and the cycle continues.
        # STATIC imports, not `__import__(name)`. The first draft used a dynamic import in a
        # loop, and the orphan ratchet refused the commit -- correctly: a module reached only
        # by a runtime string is invisible to static caller analysis, so it reads as having no
        # caller at all. That is precisely the blindness that let `resource_headroom` sit
        # unwired since 2026-08-10, and wiring it in a way no tool can see would have
        # reproduced the defect while looking like the fix.
        from background import disk_headroom, resource_headroom, staging_two_rooms_repair
        from tools import console_instruction_record, lane_formation

        # The formation measure is a DIAGNOSTIC (R12) and is wired here for one reason: the
        # orphan ratchet refused it as a module nothing runs, and it was right. A shape nobody
        # computes is a shape nobody sees, which is the state the 2026-08-19 ruling describes.
        # It reports and alarms on TRANSITION (R5). It does not weight the draw -- see the
        # module docstring for why a lane quota would be gamed by the thing it measures.
        # Two of these five LOSE something when they do not run, which is why they are here
        # rather than in a gate: a gate fires when someone commits, and nobody committing is
        # exactly when the director's words scroll out of the pane and a duplicate sits
        # refusing every commit in the tree.
        for _tag, _observer in (("disk-headroom", disk_headroom),
                                ("memory-headroom", resource_headroom),
                                ("lane-formation", lane_formation),
                                ("console-record", console_instruction_record),
                                ("two-rooms-repair", staging_two_rooms_repair)):
            try:
                _reading = _observer.observe()
                if _reading.get("alarm"):
                    log(f"[{_tag}] {_reading['alarm']}")
                if _reading.get("shadow_alarm"):
                    log(f"[{_tag}] {_reading['shadow_alarm']}")
                elif _reading.get("changed"):
                    # The two governors recover to a BAND; the formation measure recovers to a
                    # VERDICT. Naming the tag rather than assuming a shared vocabulary, because
                    # the first draft logged "[formation-headroom] recovered to ?" -- a message
                    # that is wrong twice over and would have been read as a broken governor.
                    _to = _reading.get("band") or _reading.get("verdict") or "?"
                    log(f"[{_tag}] recovered to {_to}")
            except Exception as exc:  # noqa: BLE001
                log(f"[{_tag}] failed to run: {exc}")

        # Always check for leftover run_complete markers first, regardless of peak hours
        try:
            process_leftover_run_markers()
        except Exception as exc:
            log(f"process_leftover_run_markers error: {exc}")

        beat_liveness()

        if is_peak_hours():
            now = datetime.now(timezone.utc)
            log(f"Peak hours (16:00-19:00 GMT) — pausing. Current time: {now.strftime('%H:%M UTC')}")
            update_agent_status("background-worker", status="idle", last_action=f"Peak hours pause — {now.strftime('%H:%M UTC')}", is_heartbeat=True)
            time.sleep(60 * 15)  # check every 15min during peak
            continue

        # Read task queue
        if not TASKS_FILE.exists():
            log("No background-tasks.md found — sleeping")
            update_agent_status("background-worker", status="idle", last_action="No task queue found — sleeping", is_heartbeat=True)
            time.sleep(60 * CHECK_INTERVAL_MINUTES)
            continue

        tasks_content = TASKS_FILE.read_text()
        if "## QUEUED" not in tasks_content:
            log("No queued tasks — sleeping")
            update_agent_status("background-worker", status="idle", last_action="No queued tasks — sleeping", is_heartbeat=True)
            time.sleep(60 * CHECK_INTERVAL_MINUTES)
            continue

        log("Found queued tasks — beginning execution")
        update_agent_status("background-worker", status="working", last_action="Executing queued tasks")
        # Tasks are executed by the individual task scripts (see below)
        # This worker just triggers them and logs completion
        exec(open("background/run_queued_tasks.py").read(), globals())
        update_agent_status("background-worker", status="idle", last_action="Task batch complete")
        time.sleep(60 * CHECK_INTERVAL_MINUTES)

if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/background_worker.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("background_worker")
    main()
