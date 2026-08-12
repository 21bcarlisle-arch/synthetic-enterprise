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

BETWEEN_RUN_PAUSE_SECONDS = 60  # brief pause between back-to-back runs

sys.path.insert(0, str(PROJECT_DIR))
from background.notify import notify  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.agent_protocol import AgentMessage  # noqa: E402
from background.child_diagnostics import (  # noqa: E402
    STDERR_TAIL_LINES, failure_detail, stderr_tail,
)

# The publisher's no-publish exit codes, mirrored as LITERALS for the same reason
# background_worker mirrors them: this module must not take an import-time dependency on the
# publish stack. A mirror without a drift pin is what wedged publishing for 4772 min on
# 2026-08-12 -- a sibling test held the number 0 as a proxy for "a duplicate is not an error"
# and nobody updated it when the duplicate path was given its own code. The number is not the
# property; `test_the_runner_mirror_constants_cannot_drift` is what keeps this copy honest.
EXIT_LOCK_SKIPPED = 75        # process_run_complete.EXIT_LOCK_SKIPPED
EXIT_NOTHING_PUBLISHED = 76   # process_run_complete.EXIT_NOTHING_PUBLISHED


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry, flush=True)


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
        return False

    size_kb = out_json.stat().st_size / 1024
    log(f"Run complete — {elapsed:.0f}s, {size_kb:.0f} KB ({out_json.name})")
    update_agent_status("sim-runner", status="idle", last_action=f"Run complete in {elapsed:.0f}s — {size_kb:.0f} KB ({out_json.name})")
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
        elif rc == 0:
            log('Auto-processed run complete marker')
        else:
            tail = stderr_tail(getattr(proc_result, 'stderr', None))
            log('Auto-process failed (rc={}) -- marker left for background_worker{}'.format(
                rc,
                '\n  publisher stderr (last {} lines):\n{}'.format(STDERR_TAIL_LINES, tail)
                if tail else '\n  publisher stderr: EMPTY'))
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
        tail = stderr_tail(exc.stderr)
        log('Auto-process timed out after {}s -- the publisher outran the deadline this loop '
            'puts on it. NOT a test failure: the gate it was running never returned a verdict. '
            'Marker left for background_worker{}'.format(
                _publisher_deadline_seconds(),
                '\n  publisher stderr before the kill:\n{}'.format(tail) if tail
                else '\n  publisher stderr: nothing captured before the kill'))
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
    budget, never a number of ours.

    Imported lazily and at CALL time (not bound at import) for the same reason the outcome
    router below is lazy: this module must not acquire an import-time dependency on the
    publish pipeline, and a constant snapshotted at import would go stale against a reloaded
    module in exactly the tests that check this coupling.

    FAIL-LONG, not fail-short. If the publisher is unimportable the subprocess is going to
    fail immediately anyway, so the only thing a fallback can do is re-create the bug by
    being too small. Deliberately larger than any bound the publisher currently declares;
    `tests/background/test_publisher_deadline_exceeds_its_gate.py` pins the real coupling for
    EVERY caller that spawns the publisher, this one included."""
    try:
        from background import process_run_complete as prc
        return prc.PUBLISH_PATH_TIMEOUT_SECONDS
    except Exception as exc:
        log('publisher deadline falling back (publisher module unreadable: {})'.format(exc))
        return 60 * 60


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
