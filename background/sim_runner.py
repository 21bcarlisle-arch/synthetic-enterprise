#!/usr/bin/env python3
"""Continuous simulation runner — keeps the GPU busy between Claude sessions.

Runs the full 9.5-year simulation in a loop, saving each result to a
timestamped JSON and report file. Writes a run_complete_*.md staging marker
so Claude picks up new results on its next autonomous or interactive turn.

Output files are timestamped so successive runs don't overwrite each other.
run_output_latest.json IS updated so Claude always has fresh data available.
ANNUAL_REPORT.md is NOT overwritten — Claude regenerates that explicitly
when it processes the run_complete marker (preserving manual fixes like
Phase 9a reconciliation).

Runs continuously 24/7 — token budget takes priority over electricity cost.
"""

import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "sim-runner-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
REPORTS_DIR = PROJECT_DIR / "docs" / "reports"
HOLD_FLAG = PROJECT_DIR / "docs" / "review_gates" / ".sim_runner_hold"
FORCE_REPUBLISH_FLAG = PROJECT_DIR / "docs" / "review_gates" / ".force_republish_once"

#: PRODUCER HEALTH, the state file behind supervisor RUNG 1d (2026-08-17).
#:
#: WHY IT EXISTS. On 2026-08-17 this runner failed NINE consecutive times over 70
#: minutes on one KeyError, and nothing drew the fix. Every response was narration:
#: a line in sim-runner-log.md, an ntfy per failure, and an `agent_status` anomaly
#: field that no draw rung reads. The publisher, whose outage has the SAME
#: consequence -- nothing new reaches the live site -- has had a priority-zero draw
#: rung since 2026-07-23, because the same 2h17m of alarm-into-silence happened to
#: IT twice and got mechanised. The producer had the alarm and not the mechanism.
#:
#: Worse, the three watchers that could have seen it each could not:
#:   * the publish-gate wedge detector keys on publish FAILURES, and nine failed
#:     runs produce ZERO publish attempts -- an empty failure list is
#:     indistinguishable from a healthy gate (fail-open on empty, R15);
#:   * the operational-layer signal keys on `pytest -m operational` -- daemon
#:     lifecycle and IaC reconcile -- and this daemon was alive the whole time. It
#:     read GREEN, consecutive_green=6, at 16:54Z with eight failures behind it,
#:     because it measures LIVENESS and the broken thing was the OUTPUT;
#:   * the content-freshness clocks key on commit/publish recency by ANY writer,
#:     and a concurrent SITE lane kept committing and publishing, so `published_
#:     age_seconds` read 1.9h against a real producer outage of 3.0h. That is
#:     `publish_freshness.py`'s own "content moving by luck is not a healthy
#:     pipeline" defect, one level up.
#:
#: CONTRACT (the ONE place the write rule is stated -- supervisor reads this file
#: and never writes it, per its module doctrine):
#:   * every terminal run outcome writes it: success CLEARS, failure/timeout/crash
#:     INCREMENTS. A run that never reaches a terminal outcome leaves it alone.
#:   * `consecutive_failures` counts terminal non-successes since the last success.
#:   * `first_failure_ts` is the START of the current failure streak and is NOT
#:     re-stamped by later failures -- the detector measures the outage from it.
#:   * a hold is NOT a failure: `_check_hold` skipping a run does not touch it.
#:   * the DIAGNOSED limb (>=3 failures sustained >30min) is the sharp instrument and is what
#:     catches an outage of the 2026-08-17 shape; the detector's artefact-age limb is a 3h
#:     backstop for a runner that writes no counter at all, sized off the measured gap
#:     distribution rather than a guess (see supervisor.PRODUCER_ARTEFACT_STALE_SECONDS).
#:   * writing is best-effort and NEVER fatal. A runner that dies because its own
#:     bookkeeping failed is a worse outcome than an unwritten counter, and the
#:     detector's artefact-age limb does not depend on this file at all.
PRODUCER_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".sim_producer_state.json"

#: THE PRODUCER MUST NOT OUTRUN THE CONSUMER (measured 2026-09-04, lane 0 throughput).
#:
#: A 60-second pause meant "run flat out", and it made the run_complete queue structurally
#: undrainable: markers arrived every 13.2 min (median) while a publish cycle that actually
#: published completed every 88.9 min, so ~3.9 markers accumulated per hour and `pending == 0`
#: was never observed. The episode that watches for a drained queue therefore could never close,
#: and the alarm on it read a working publisher as a five-hour outage.
#:
#: The two figures below are MEASURED, not chosen, and the pause is DERIVED from them rather
#: than picked -- so when either side moves, the derivation moves with it and the control below
#: is what notices.
#:
#: THE COST OF THE OLD CADENCE WAS ALREADY BEING PAID AND THROWN AWAY. Of 272 markers minted
#: since 2026-08-28, 152 (55.9%) were retired `## Superseded (not published)` -- overtaken
#: before the publisher could reach them; all-time it is 972/1504 (64.6%). Those runs cost full
#: simulation compute and reached no reader. Slowing the producer to the consumer's measured
#: rate does not cost the reader one published figure: it returns the compute that was being
#: discarded, on a machine where OOM kills have already destroyed a published bound.
#:
#: NOT a fix for a slow publisher. This closes the gap from the producer's side because the
#: consumer's cycle is floored by controls that must not be removed (a 616s scoped gate and a
#: ~110s commit hook are only 12 min of it). Shortening the gate -- the candidate this direction
#: named as "the only lever with headroom" -- was measured and REFUSED: it can return at most
#: ~5 min of a ~90-min cycle and cannot bridge 4.55/h arrivals against 0.66/h service.
#:
#: CORRECTION, recorded beside the claim it replaces. The first derivation here used the median
#: gap over 2026-09-04 alone (39 min) and produced a 1608s pause at exactly rho = 1.0 -- parity,
#: which is not drainage: a queue at rho = 1 random-walks and never reliably empties. That
#: median was skewed by a run of FAILING cycles, which abort early and cost ~27 min. Separating
#: by outcome over two days is what the number had to be: a cycle following a PASSING gate costs
#: 88.9 min (p50, n=22), so the real oversupply was 6.8x, not the 3x first stated.
#: Gap between publish-gate completions FOLLOWING A PASS -- the cycle a real publish actually
#: costs -- docs/observability/publish_gate_duration.jsonl, n=22 over 2026-09-03..04.
#: p90 rather than p50 DELIBERATELY: the distribution is tight (p50 88.9, p90 90.3 min), so p90
#: buys a real margin for ~1.5 min and makes nine cycles in ten finish strictly inside one
#: producer period. That margin is what leaves a window in which `pending == 0` is observable,
#: rather than a queue that merely stops growing.
PUBLISHER_CYCLE_P90_SECONDS = 5417
#: Median marker interarrival (13.2 min) less the 60s pause that produced it -- i.e. how long a
#: simulation run itself takes, from docs/staging/ marker stamps, 28 runs since 06:00Z.
SIM_RUN_DURATION_P50_SECONDS = 732
#: Derived: the pause that makes one producer period cover one consumer cycle. The `max` floor
#: keeps a degenerate measurement from producing a busy-loop; it is NOT what binds today (see
#: the reachability control in tests/background/test_sim_runner.py).
BETWEEN_RUN_PAUSE_SECONDS = max(60, PUBLISHER_CYCLE_P90_SECONDS - SIM_RUN_DURATION_P50_SECONDS)

sys.path.insert(0, str(PROJECT_DIR))
from background import publisher_budget  # noqa: E402
from background.agent_protocol import AgentMessage  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.child_diagnostics import (  # noqa: E402
    STDERR_TAIL_LINES,
    child_output_excerpt,
    failure_detail,
    stderr_tail,
)
from background.episode_monotonic import guard_episode, recorded_instant_seconds  # noqa: E402
from background.live_ledger_guard import guard_live_ledger_write  # noqa: E402
from background.notify import notify  # noqa: E402

#: The episode-scoped fields of PRODUCER_STATE_FILE, declared for `guard_episode`. A field added
#: here without being declared is exactly the "wired it in but it is a no-op" gap the guard's own
#: docstring warns about.
PRODUCER_SINCE_FIELDS = ("first_failure_ts",)     # LOW-water: an open episode's start only moves earlier
PRODUCER_STREAK_FIELDS = ("consecutive_failures",)  # HIGH-water: an open counter only goes up

# The publisher's no-publish exit codes, mirrored as LITERALS for the same reason
# background_worker mirrors them: this module must not take an import-time dependency on the
# publish stack. A mirror without a drift pin is what wedged publishing for 4772 min on
# 2026-08-12 -- a sibling test held the number 0 as a proxy for "a duplicate is not an error"
# and nobody updated it when the duplicate path was given its own code. The number is not the
# property; `test_the_runner_mirror_constants_cannot_drift` is what keeps this copy honest.
EXIT_LOCK_SKIPPED = 75          # process_run_complete.EXIT_LOCK_SKIPPED
EXIT_NOTHING_PUBLISHED = 76     # process_run_complete.EXIT_NOTHING_PUBLISHED
EXIT_PUBLISH_DID_NOT_LAND = 77  # process_run_complete.EXIT_PUBLISH_DID_NOT_LAND


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry, flush=True)


def record_run_outcome(
    ok: bool,
    *,
    detail: str | None = None,
    head: str | None = None,
    elapsed: float | None = None,
    state_path=None,
    now: float | None = None,
) -> dict | None:
    """Record one TERMINAL run outcome to PRODUCER_STATE_FILE. See its contract.

    Returns the written state (for tests), or None if the write failed -- which is
    logged and never raised, because the runner's job is to run the simulation and
    a failed counter must not stop it.
    """
    import json

    path = Path(state_path) if state_path is not None else PRODUCER_STATE_FILE
    stamp = time.time() if now is None else now
    try:
        previous = json.loads(path.read_text())
        if not isinstance(previous, dict):
            previous = {}
    except (OSError, ValueError):
        previous = {}

    if ok:
        state = {
            "last_result": "ok",
            "consecutive_failures": 0,
            "first_failure_ts": None,
            "last_failure_ts": previous.get("last_failure_ts"),
            "last_success_ts": stamp,
            "detail": None,
            "git": head,
            "elapsed_s": round(elapsed) if elapsed is not None else None,
        }
    else:
        try:
            streak = int(previous.get("consecutive_failures") or 0)
        except (TypeError, ValueError):
            streak = 0
        # The streak START is preserved across failures -- the detector measures the
        # outage from it, so re-stamping it every failure would keep the measured age
        # pinned near zero and the rung would never reach its threshold. That is the
        # fail-silent shape this whole mechanism exists to remove, so it is spelled out
        # here and pinned by `test_the_streak_start_is_not_restamped_by_later_failures`.
        # ...and the adoption test ASKS the carrier's own module rather than re-implementing it
        # (2026-09-04). `isinstance(first, (int, float))` waved through the two values that are not
        # start times: `0` (a truncated or half-written state file) and `True` (an int in Python).
        # Both were then adopted, persisted, and read by RUNG 1d's `outage` as an outage of 496,815
        # hours -- which clears the 30-minute bar on its own, so a producer that had failed three
        # times in two minutes paged as a PRIORITY ZERO starvation. Measured, before this line
        # changed. `recorded_instant_seconds` is the one definition; a fourth hand-roll here is how
        # four copies of one question came to give three different answers.
        first = previous.get("first_failure_ts") if streak else None
        state = {
            "last_result": "failed",
            "consecutive_failures": streak + 1,
            "first_failure_ts": first if recorded_instant_seconds(first) is not None else stamp,
            "last_failure_ts": stamp,
            "last_success_ts": previous.get("last_success_ts"),
            "detail": detail,
            "git": head,
            "elapsed_s": round(elapsed) if elapsed is not None else None,
        }

    # EPISODE GUARD (PW2 self-clearing-alarm census, 2026-08-17). This file carries BOTH shapes
    # the census calls `real`: an episode START (`first_failure_ts`) and an episode COUNTER
    # (`consecutive_failures`), and RUNG 1d reads both for severity. Unguarded, any failure write
    # that lost its prior -- a concurrent writer, a truncated read, a hand edit -- would reset the
    # streak to 1 and re-stamp the start at now, silently shortening the outage and dropping the
    # rung back below its 30-minute bar. That is the same shape as the 10h26m publish outage that
    # paged as a fresh 14 minutes on 2026-08-09, which is why the class has a register.
    #
    # THE CLOSE CONDITION IS NAMED AND INDEPENDENT (R15 anti-tautology): the episode ends when a
    # run reaches TERMINAL SUCCESS -- `ok`, which is set by `run_simulation` only after the child
    # exited 0 AND wrote its `run_output_*.json`. The evidence is the child's artefact, not this
    # file's own counter, so the guard cannot be satisfied by the thing it guards.
    state = guard_episode(
        previous or None, state,
        since_fields=PRODUCER_SINCE_FIELDS,
        streak_fields=PRODUCER_STREAK_FIELDS,
        episode_closed=ok,
    )

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        guard_live_ledger_write(path, writer="sim_runner.record_run_outcome")
        path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    except OSError as exc:
        log(f"producer-health state write failed (non-fatal): {exc}")
        return None
    return state


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(PROJECT_DIR), text=True, timeout=5,
        ).strip()
    except Exception:
        return "unknown"


def run_simulation() -> bool:
    """Run one full simulation. Returns True on success."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    head = _git_head()
    out_json = REPORTS_DIR / f"run_output_{head}_{ts}.json"
    out_md = REPORTS_DIR / f"ANNUAL_REPORT_{ts}.md"

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log(f"Starting run — git={head}, json={out_json.name}")
    update_agent_status(
        "sim-runner", status="running",
        last_action=f"Sim started — git={head}",
        role="Runs full 10-year simulation in a loop; writes run_complete markers",
        produces="docs/reports/run_output_*.json, docs/staging/run_complete_*.md",
    )

    t0 = time.monotonic()
    try:
        # H30 (2026-08-08): stderr is CAPTURED, not inherited. When this runner
        # is started by a daemon, fd 2 points at a socket nobody reads, so every
        # traceback the child wrote was discarded -- eight consecutive failures
        # reported `rc=1` and nothing else. stdout stays inherited on purpose:
        # it is the child's progress output, it is large, and it is not what
        # identifies a failure.
        result = subprocess.run(
            [
                # KNIFE pass 1 (2026-08-09): the RUN entry point moved out of
                # saas/ to the composition root above both layers. The report
                # module is render-only now and no longer imports simulation.
                sys.executable, "-m", "tools.run_annual_report",
                "--save-json", str(out_json),
                "--output", str(out_md),
            ],
            cwd=str(PROJECT_DIR),
            timeout=7200,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - t0
        # A timed-out child still wrote to stderr before it was killed, and
        # TimeoutExpired carries what was read so far. That partial output is
        # usually where it got stuck.
        tail = stderr_tail(exc.stderr)
        log(f"Run TIMED OUT after {elapsed:.0f}s — killing subprocess and retrying"
            + (f"\n  child stderr (last lines before kill):\n{tail}" if tail
               else "\n  child stderr: nothing captured before the kill"))
        notify(f"[SIM] Run timed out after {elapsed:.0f}s — {failure_detail(exc.stderr)} "
               f"(full tail in sim-runner-log.md)", kind="real_alarm")
        update_agent_status("sim-runner", status="error", last_action=f"Run timed out after {elapsed:.0f}s", anomaly=f"TimeoutExpired after {elapsed:.0f}s: {failure_detail(exc.stderr)}")
        # PRODUCER HEALTH (RUNG 1d): a timeout is a terminal non-success like any other.
        record_run_outcome(False, detail=f"timeout after {elapsed:.0f}s: {failure_detail(exc.stderr)}", head=head, elapsed=elapsed)
        return False
    elapsed = time.monotonic() - t0

    if result.returncode != 0 or not out_json.exists():
        tail = stderr_tail(getattr(result, "stderr", None))
        log(f"Run FAILED (rc={result.returncode}) after {elapsed:.0f}s"
            + (f"\n  child stderr (last {STDERR_TAIL_LINES} lines):\n{tail}" if tail
               else "\n  child stderr: EMPTY — the child died without writing a diagnostic"))
        notify(f"[SIM] Run FAILED after {elapsed:.0f}s — {failure_detail(getattr(result, 'stderr', None))} "
               f"(full tail in sim-runner-log.md)", kind="real_alarm")
        update_agent_status("sim-runner", status="error", last_action=f"Run FAILED (rc={result.returncode}) after {elapsed:.0f}s", anomaly=f"Exit code {result.returncode}: {failure_detail(getattr(result, 'stderr', None))}")
        # PRODUCER HEALTH (RUNG 1d): this is the write that turns a repeating alarm into
        # drawable work. The 2026-08-17 outage failed here nine times and left nothing the
        # draw ladder could read.
        record_run_outcome(False, detail=failure_detail(getattr(result, "stderr", None)), head=head, elapsed=elapsed)
        return False

    size_kb = out_json.stat().st_size / 1024
    log(f"Run complete — {elapsed:.0f}s, {size_kb:.0f} KB ({out_json.name})")
    update_agent_status("sim-runner", status="idle", last_action=f"Run complete in {elapsed:.0f}s — {size_kb:.0f} KB ({out_json.name})")
    # PRODUCER HEALTH (RUNG 1d): a success CLEARS the streak, so the rung stops drawing
    # without anyone editing state by hand.
    record_run_outcome(True, head=head, elapsed=elapsed)
    # Stage 4: emit structured AgentMessage for run_complete (first live usage of protocol)
    _msg = AgentMessage(
        sender="sim-runner",
        receiver="broadcast",
        intent="run_complete",
        payload={"elapsed_s": round(elapsed), "size_kb": round(size_kb), "json": out_json.name},
    )
    log(f"[protocol] run_complete message: {_msg.to_json()}")

    # Update latest pointer so Claude always has fresh data
    latest_json = REPORTS_DIR / "run_output_latest.json"
    latest_json.write_bytes(out_json.read_bytes())

    # Write staging marker — Claude processes this on its next turn
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    marker = STAGING_DIR / f"run_complete_{ts}.md"
    marker.write_text(
        f"# Simulation Run Complete\n\n"
        f"Finished: {datetime.now(timezone.utc).isoformat()}\n"
        f"Git: {head}\n"
        f"JSON: {out_json}\n"
        f"Draft report: {out_md}\n"
        f"Duration: {elapsed:.0f}s | Size: {size_kb:.0f} KB\n\n"
        f"## Action required\n\n"
        f"1. Regenerate docs/reports/ANNUAL_REPORT.md from this run's data:\n"
        f"   `python3 -m saas.reporting.annual_report`\n"
        f"2. Update docs/status/LATEST.md with key figures.\n"
        f"3. Run tests, commit (include report + LATEST.md), push.\n"
        f"4. NTFY Rich with headline net margin, gross margin, enterprise value.\n"
    )

    auto_process_marker(marker)

    return True


def auto_process_marker(marker):
    """Publish ONE just-written run-complete marker, and report the outcome to
    the publish-gate wedge detector.

    Extracted from run_simulation() (2026-08-03) so the wedge-detector wiring
    below sits on a seam a test can actually DRIVE. It previously lived inline
    in a function that shells out to the whole simulation, so the only
    reachable test was one that called the recorder directly -- which is a
    TAUTOLOGY (R15): it passes whether or not this path is wired up at all.
    Returns the return code seen (124 for a timeout), for callers and tests.

    UNDOCUMENTED COUPLING, now documented (2026-07-13, director-flagged):
    this call passes ONLY the marker just written by the caller -- the run loop
    never re-scans staging/ for a DIFFERENT, earlier marker this exact process
    may have skipped on a prior iteration. process_run_complete.py's own
    `main()` used to return 0 both when it genuinely processed a marker AND
    when its own lock was already held by a concurrent instance -- so rc==0
    did NOT distinguish "processed" from "someone else was already running,
    this marker was left untouched." Since 2026-07-29 a lock-skip returns
    EXIT_LOCK_SKIPPED (75) and is logged as such below, but that only makes
    the skip VISIBLE here: there is still no retry of a skipped marker
    anywhere in this file. The real safety net is entirely external:
    background/background_worker.py::process_leftover_run_markers()
    unconditionally re-globs every run_complete_*.md in staging/ at the
    top of its own loop, every cycle -- it, not this function, is what
    actually guarantees a lock-skipped marker still gets processed."""
    processor = Path(__file__).parent / 'process_run_complete.py'
    try:
        proc_result = subprocess.run(
            [sys.executable, str(processor), str(marker)],
            cwd=str(PROJECT_DIR),
            # NOT A NUMBER OF OUR OWN -- the SIBLING HALF of the wrapper-deadline defect
            # (2026-08-10, the wedge that outlived the fix aimed at it). `background_worker`'s
            # independent `timeout=900` was replaced that morning by a derivation from the
            # publisher's own budget, and `test_publisher_deadline_exceeds_its_gate.py` pinned
            # it -- for THAT caller. This one, the path that publishes in the STEADY STATE
            # every ~10 min, kept its own literal 1200s and a comment citing a 600s internal
            # test timeout that has since been re-derived 600 -> 1800 -> 2600s against the cold
            # HEAD-checkout subject. So the class was closed on one half and left open on the
            # half that runs most often, and the wedge continued for another 3 hours after the
            # "fix" landed.
            #
            # OBSERVED, not inferred (docs/observability/sim-runner-log.md, 2026-08-10 18:51Z):
            #   Auto-process timed out after 1200s -- marker left for background_worker
            # recorded against the wedge detector as rc=124 / `test_regression`, at a HEAD
            # whose gate was never allowed to return a verdict.
            #
            # AND IT DID NOT ONLY MISREPORT -- IT CORRUPTED THE NEXT CYCLE. The SIGKILL reaches
            # this direct child only; the gate's pytest grandchild keeps running inside
            # /tmp/publish-gate-head-reused while the dead parent's flock is released. The next
            # cycle then takes that lock and refreshes the directory under the live orphan,
            # which is the other half of what the log shows: `ModuleNotFoundError: No module
            # named 'tools.test_execution_metric'` at 18:25Z and `FileNotFoundError:
            # '/tmp/publish-gate-head-reused'` at 18:51Z -- two reds that say nothing about any
            # test. `process_run_complete._reused_checkout_is_in_use` closes that second half.
            timeout=_publisher_deadline_seconds(),
            # BOTH STREAMS (2026-08-21) -- and this is the SIBLING HALF again, in the
            # same file that already records losing three hours to closing this class on
            # `background_worker` and not on the path that publishes in the steady state.
            # The publisher refuses on STDOUT (`process_run_complete.log()`); stderr
            # carries only library warnings. The EXIT_PUBLISH_DID_NOT_LAND branch below
            # tells the reader "the refusing gate is named in the publisher log tail",
            # which was structurally false for as long as that tail was stderr-only.
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # H30: same defect as run_simulation's, same file
            text=True,
        )
        rc = proc_result.returncode
        if rc == EXIT_LOCK_SKIPPED:
            log('Auto-process lock-skipped the marker (another instance holds '
                'the run lock) -- marker untouched, left for background_worker')
        elif rc == EXIT_NOTHING_PUBLISHED:
            # Not a failure and not a publish. Before this code existed it fell into the else
            # branch below and this path logged "Auto-process failed (rc=76)" for a marker that
            # was already safely published by somebody else -- a false red in the first log a
            # reader opens when diagnosing a wedge.
            log('Auto-process found the marker already archived (duplicate) -- '
                'nothing published by this cycle')
        elif rc == EXIT_PUBLISH_DID_NOT_LAND:
            # NOT "marker left for background_worker", which is what the generic else branch
            # below would have said and would have been false: the publisher archived this
            # marker before attempting the commit, so no sweep will ever see it again. The
            # retry is the NEXT cycle's marker, and it happens because the publisher withheld
            # this cycle's fingerprint. Said plainly here because the wrong sentence sends a
            # reader looking for a pending marker that does not exist.
            log('Auto-process published NOTHING -- the commit did not land (refused, timed '
                'out, or never reached origin). Marker already archived; the live site keeps '
                'serving the older snapshot and the next cycle re-attempts. The refusing gate '
                'is named in the publisher log tail; recorded as a publish-gate FAILURE.')
        elif rc == 0:
            log('Auto-processed run complete marker')
        else:
            log('Auto-process failed (rc={}) -- marker left for background_worker. '
                "The publisher's own verdict is on STDOUT:\n{}".format(
                    rc, child_output_excerpt(getattr(proc_result, 'stdout', None),
                                             getattr(proc_result, 'stderr', None))))
        # H15 (2026-08-03): feed THIS path's outcome into the publish-gate wedge
        # detector too. This is the path that actually publishes in the steady
        # state, and it fed the detector NOTHING -- only
        # background_worker's leftover sweep did, and that sweep by
        # construction chews the STALE backlog. So a healthy pipeline
        # publishing cleanly every ~10 min could never clear a wedge streak the
        # sweep kept growing: the alarm stayed armed ~5960 min against a
        # working publisher (2026-07-30..08-03). The router itself is
        # defensive and treats rc=75 as evidence of nothing.
        _record_publish_gate_outcome(marker, rc)
        return rc
    except subprocess.TimeoutExpired as exc:
        log('Auto-process timed out after {}s -- the publisher outran the deadline this loop '
            'puts on it. NOT a test failure: the gate it was running never returned a verdict. '
            'Marker left for background_worker. What it had written before the kill:\n{}'.format(
                _publisher_deadline_seconds(),
                child_output_excerpt(getattr(exc, 'stdout', None),
                                     getattr(exc, 'stderr', None))))
        # A timeout IS a publish failure (the marker stays unpublished), and it is exactly how
        # the 4-day 2026-07-25 blackout presented -- so it must reach the detector rather than
        # being swallowed. But it is NOT evidence about the tests, and rc=124 WAS: the
        # classifier maps any rc>0 to `test_regression`, which is how a stopwatch became
        # 145 recorded test failures and sent the RUNG-1 draw after a gate that was never
        # judged. `kind="deadline_kill"` with no invented return code is the same contract
        # background_worker's sweep already states (test_publisher_deadline_exceeds_its_gate).
        _record_publish_gate_outcome(marker, None, kind='deadline_kill')
        return 124


def _publisher_deadline_seconds():
    """The deadline this loop puts on ONE publisher run -- the publisher's OWN declared
    budget, never a number of ours, and never one this process cached earlier.

    READ FROM DISK, NOT FROM `sys.modules` (2026-08-22, and this loop is where it was
    OBSERVED). The old body was a lazy `from background import process_run_complete` under a
    docstring claiming a call-time import kept the number current. A lazy import is still a
    one-time import. This daemon started at 16:45:22 on 2026-08-21, inside the 78 minutes
    when `GATE_SUITE_TIMEOUT_SECONDS` was transiently 300 (commit 8d6f4a2b4), and cached
    1200. The constant was corrected to 3400 at 17:28 and 3800 at 18:32; this loop went on
    killing every publish at 1200s for ten hours, four cycles in a row, each recorded as
    `deadline_kill` against a gate with `total_red: 0` and `blocking_tests: []`. The last of
    them was killed with a GREEN gate behind it, mid-`git commit`.

    FAIL-LONG, not fail-short. A too-long deadline delays one diagnosis; a too-short one
    decides the inner gate's verdict by stopwatch, which is the whole defect."""
    try:
        return publisher_budget.declared_publisher_budget_seconds()
    except Exception as exc:
        log('publisher deadline falling back (publisher would not declare it: {})'.format(exc))
        return publisher_budget.FALLBACK_SECONDS


def _record_publish_gate_outcome(marker, rc, *, kind=None):
    """Report this publisher's outcome to the shared publish-gate wedge
    detector (`process_run_complete.record_publish_gate_outcome`).

    Imported lazily, not at module scope, for the same reason
    background_worker.py does: importing the publish pipeline at sim_runner
    import time drags in the whole reporting stack. Swallows everything -- a
    monitoring failure must never break the run loop it monitors."""
    try:
        from background import process_run_complete as prc
        return prc.record_publish_gate_outcome(marker, rc, kind=kind)
    except Exception as exc:
        log('publish-gate outcome recording failed (non-fatal): {}'.format(exc))
        return None


def _check_hold(was_held: bool) -> tuple[bool, bool]:
    """Check HOLD_FLAG and update hold state; returns (new_was_held, should_skip_run).

    No-orphan-transitions fix (2026-07-10, CLAIM_EQUALS_PIXEL.md/
    END_TO_END_VERIFICATION.md): a hold release must itself trigger
    republication -- releasing this hold previously did nothing on its own
    if the fixed code's headline figures looked "identical" to the pre-fix
    run's fingerprint, leaving the live site stale for hours despite the
    gate being closed. On the held->cleared transition, this touches
    FORCE_REPUBLISH_FLAG, which forces background/process_run_complete.py's
    next _process() call through regardless of fingerprint match, consumed
    exactly once."""
    if HOLD_FLAG.exists():
        if not was_held:
            log("HELD: {} present -- skipping new runs until it is removed "
                "(director hold on publishing new results)".format(HOLD_FLAG.name))
        return True, True
    if was_held:
        log("Hold cleared -- resuming normal runs, forcing next publish through")
        FORCE_REPUBLISH_FLAG.parent.mkdir(parents=True, exist_ok=True)
        FORCE_REPUBLISH_FLAG.touch()
    return False, False


def main() -> None:
    log("Simulation runner started")
    was_held = False
    while True:
        was_held, should_skip = _check_hold(was_held)
        if should_skip:
            time.sleep(120)
            continue
        try:
            success = run_simulation()
        except Exception as exc:
            log(f"Unexpected error in run_simulation: {type(exc).__name__}: {exc}")
            notify(f"[SIM] Unexpected crash: {type(exc).__name__}: {exc}", kind="real_alarm")
            # PRODUCER HEALTH (RUNG 1d): a crash INSIDE run_simulation never reached the
            # terminal writes above, so it is recorded here -- otherwise the one failure
            # mode that skips the bookkeeping is the one that leaves no counter.
            record_run_outcome(False, detail=f"{type(exc).__name__}: {exc}")
            success = False
        wait = BETWEEN_RUN_PAUSE_SECONDS if success else 300
        log(f"Waiting {wait}s before next run...")
        time.sleep(wait)


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/sim_runner.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("sim_runner")
    main()
