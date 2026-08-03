#!/usr/bin/env python3
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
DONE_DIR = STAGING_DIR / "done"
LATEST_MD = PROJECT_DIR / "docs" / "status" / "LATEST.md"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "sim-runner-log.md"
LAST_TESTED_HASH_FILE = PROJECT_DIR / "docs" / "observability" / ".last_tested_hash"
LAST_PUSH_FILE = PROJECT_DIR / "docs" / "observability" / ".last_push_time.json"
RUN_LOCK_FILE = PROJECT_DIR / "docs" / "observability" / ".process_run_complete.lock"
# EX_TEMPFAIL. A lock-skip ("another instance already holds the run lock") is
# NEITHER a success NOR a processing failure -- the marker was left untouched.
# It used to return 0, indistinguishable from a real publish, which meant
# background_worker's sweep recorded a publish-gate SUCCESS for a marker it had
# not published -- clearing the H15 wedge streak and auto-resolving the open
# [ACTION NEEDED] item while the pipeline was still wedged (observed
# 2026-07-29 16:53Z: two markers logged "Processed", both untouched, one minute
# before the lock holder itself failed the gate). See _record_publish_gate_outcome.
EXIT_LOCK_SKIPPED = 75
RUN_INSIGHTS_PATH = PROJECT_DIR / "docs" / "observability" / "run_insights.json"
RUN_HISTORY_PATH = PROJECT_DIR / "docs" / "observability" / "run_history.json"
# H11_naive_organ (L2): the deliberately-amnesiac question organ's log + the
# LATEST.md digest block it feeds. The organ FIRES from run_naive_organ_step()
# below, wired into the live publish cycle.
NAIVE_ORGAN_LOG = PROJECT_DIR / "docs" / "observability" / "naive_organ_log.jsonl"
ORGAN_BLOCK_START = "<!-- NAIVE_ORGAN_ASKS -->"
ORGAN_BLOCK_END = "<!-- /NAIVE_ORGAN_ASKS -->"
# G5_effort_sizing_discipline (L2): remaining-effort / estimate-vs-actual /
# XL-decompose-signal digest block, same block-managed-in-LATEST.md pattern
# as the naive-organ block above. Rendering lives in
# background/effort_digest.py; the numbers come from tools/effort_calibration.py.
EFFORT_BLOCK_START = "<!-- EFFORT_SIZING_DIGEST -->"
EFFORT_BLOCK_END = "<!-- /EFFORT_SIZING_DIGEST -->"
# Change-detection gate (DIRECTOR_SEQUENCE_AND_TOKEN_ECONOMY.md, 2026-07-08):
# the sim is deterministic over frozen historical data, so every ~10-min cycle
# produced a byte-identical £1,535,308 result and yet still regenerated every
# report/site artifact, ran the test suite, and committed -- dozens of identical
# commits per day, pure token/CI burn. This file stores a fingerprint of the
# last FULLY-processed run; a new run whose fingerprint matches is skipped
# (one log line, marker archived, no regen/test/commit). The fingerprint
# deliberately does NOT key on the marker's git_hash -- that advances every
# cycle from the auto-commit itself, so it could never dedup -- and DOES include
# the UTC date so the once-per-day legitimate advances (rolling Elexon SSP
# fetch, live-decision days_to_renewal / market_data_stale_days) still produce
# exactly one processed commit per day.
LAST_FINGERPRINT_FILE = PROJECT_DIR / "docs" / "observability" / ".last_processed_fingerprint.json"
# No-orphan-transitions fix (2026-07-10, CLAIM_EQUALS_PIXEL.md/END_TO_END_
# VERIFICATION.md, director-flagged incident): the change-detection gate
# above is correct in general, but it has no concept of "the CODE changed
# even though headline figures barely moved" -- releasing a publish hold
# (docs/review_gates/.sim_runner_hold) after a fix whose real-world P&L
# impact happens to be small silently produced a fingerprint match against
# the pre-fix run, so the hold-release triggered nothing and the live site
# stayed on stale, pre-fix figures for hours. background/sim_runner.py now
# touches this flag the moment it detects a hold was just cleared; the next
# _process() call consumes it (bypassing the fingerprint-skip check exactly
# once, regardless of whether the figures look identical) and deletes it, so
# a hold-release always forces a real regen/test/commit/deploy.
FORCE_REPUBLISH_FLAG = PROJECT_DIR / "docs" / "review_gates" / ".force_republish_once"
# DEPLOY_CONTENTION_BATCH_COMMITS.md (2026-07-04): sim_runner cycles every
# ~10 min and each cycle committed+pushed unconditionally (LATEST.md's
# timestamp always differs), giving ~6 pushes/hour -- enough to contend with
# GitHub Pages' build throttling (58 failed "Deploy to GitHub Pages" runs,
# each superseded by the next push before it finished) and to burn through
# Cloudflare Pages' free-tier build quota. Commits still happen every cycle
# (free, local, no deploy trigger) but the push itself -- the thing that
# actually fires a Pages/Cloudflare build -- is throttled to at most once
# per PUSH_THROTTLE_SECONDS; the next successful push carries every commit
# accumulated since the last one.
PUSH_THROTTLE_SECONDS = 30 * 60
# The publish commit runs the FULL pre-commit hook chain (tools/git-hooks/pre-commit:
# status-honesty, pre_commit_test_gate, level_promotion_gate, site_lane_gate,
# moap_coherence_gate, ruling_archive_question_gate). Because a publish stages
# site/data/**, site_lane_gate takes its BROAD branch and runs the whole site suite --
# 27.3s measured on its own, 2026-08-03, against the 30s cap this call used to carry.
# The old cap was chosen when the hooks were trivial; it silently became a function of
# how many tests exist rather than of whether the commit is healthy, and a timeout there
# was UNCAUGHT (see git_commit_push) so it took the whole publish down as rc=1.
# Sized to BOTH constraints: ~10x the measured hook-chain cost (so growth in the suite
# does not silently re-create the wedge), while still fitting inside the 900s cap
# background_worker.py::process_leftover_run_markers puts on this whole process -- the
# fast-test gate already spends ~420s of that. A cap larger than the caller's budget
# would just move the kill one level up and lose the log line that explains it.
GIT_COMMIT_HOOK_TIMEOUT_SECONDS = 5 * 60
# H15_publish_gate_failure_alert (2026-07-14): the publish gate (fast-test
# suite + the processor's return code) can fail SILENTLY and repeatedly. The
# real worked example was pytest OOM-killed (rc=-9 -> "Tests FAILED - not
# committing") every ~10-min cycle for ~45min while run_complete markers piled
# up unpublished with NO alert -- a silent pipeline wedge. This state file
# tracks recent consecutive publish-gate FAILURES: N within a window fires ONE
# [ACTION NEEDED] alert (re-armed by a cooldown so a persistently-wedged
# pipeline can't spam), and a clean publish CLEARS it. R15: the mechanism is
# mutation-tested to FIRE on N consecutive failures, to NOT fire on a single
# transient failure or after recovery, and to FAIL-CLOSED (fire on the first
# failure) when its own gate-state file is unreadable rather than silently
# resetting the counter -- an unavailable check is a failed check.
PUBLISH_GATE_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".publish_gate_state.json"
PUBLISH_GATE_FAILURE_THRESHOLD = 3          # N consecutive failures inside the window
PUBLISH_GATE_WINDOW_SECONDS = 60 * 60       # 1h: a wedge fails every ~10min, so 3/hour is the signal
PUBLISH_GATE_COOLDOWN_SECONDS = 60 * 60     # re-arm: at most one alert NTFY per hour while it stays wedged
PUBLISH_GATE_ITEM_ID = "publish_gate_wedged"

# ── Publish-gate BLOCKING SCOPE (R10 class closure, 2026-07-18) ───────────────
# The overnight wedge (2026-07-16, TONIGHT_FIXES.md Item 4 + follow-up L166-171)
# had a STRUCTURAL root, not just the watchdog import bug that triggered it: the
# publish gate ran the ENTIRE ~18k-test suite with `-x`, so ONE red test ANYWHERE
# -- including the operational layer that validates the DAEMONS, never the
# published CONTENT -- wedged the live-site publish for hours (a daemon-lifecycle
# watchdog test raised AttributeError and blocked publishing ~21x overnight while
# the site went stale). The gate's remit is "do not ship a broken SURFACE";
# daemon/session lifecycle health is a SEPARATE concern already covered by
# health_check monitoring and the H22 3.7 red-gate-test sweep.
#
# The partition is keyed on WHAT A TEST VALIDATES, not its directory -- because
# tests/background MIXES daemon-lifecycle tests (which must not wedge publishing)
# with a handful of CONTENT-validating ones (test_effort_digest renders the
# EFFORT SIZING block into LATEST.md; test_atom_status_merge folds published atom
# level_current; test_status_honesty is the LATEST.md honesty gate). A directory
# ignore would fail-OPEN on those -- worse than the wedge. So the unit is an
# EXPLICIT, greppable `@pytest.mark.operational` marker on each daemon-lifecycle
# test module; the gate runs `-m "not operational"`. Content-, surface-generating,
# and safety-WALL tests stay UNMARKED and therefore keep BLOCKING.
#   * HEAVY ignores  -- excluded for SPEED (full-sim integration tests, 150-480s each).
#   * operational marker -- excluded for SCOPE (this class closure).
# The legitimate gate is UNCHANGED: any red publish-SURFACE test still blocks the
# publish (do not ship broken/wrong content), alarms transition-only (R5), and
# clears on the next clean publish (R11 release path).
PUBLISH_GATE_HEAVY_IGNORES = [
    "tests/simulation/test_run_phase2b.py",
    "tests/simulation/test_run_phase2b_event_log.py",
    "tests/simulation/test_run_phase4c_on_phase2b.py",
    "tests/simulation/test_phase40b_gas_pass_through.py",
    "tests/simulation/test_phase24a_ic_customer.py",
    "tests/simulation/test_phase40a_pass_through.py",
    "tests/simulation/test_phase40c_deemed_rate.py",
    "tests/simulation/test_phase41a_flex.py",
]
# Deselect the daemon-lifecycle layer by MARKER (see @pytest.mark.operational,
# registered in tests/conftest.py). Keyed on what a test validates, not its path.
PUBLISH_GATE_MARKER_EXPR = "not operational"


def publish_gate_pytest_argv(test_root="tests/"):
    """The exact pytest argv the publish gate runs. Factored out so the
    blocking SCOPE is a single testable surface (R15: a control's scope must be
    inspectable). A test marked @pytest.mark.operational is DESELECTED and can
    never reach the gate's return code; any UNMARKED test (publish-surface,
    surface-generating, or safety-wall) still does."""
    argv = [sys.executable, "-m", "pytest", test_root, "-x", "-q", "--tb=short",
            "-m", PUBLISH_GATE_MARKER_EXPR]
    for ignore in PUBLISH_GATE_HEAVY_IGNORES:
        argv.append("--ignore=" + ignore)
    return argv


# ── H23_publish_gate_scope_marker (L3): independent-cadence green signal for
# the DESELECTED operational layer ────────────────────────────────────────────
# The partition above is correct SCOPE (a red daemon-lifecycle test must never
# wedge the live-site publish) but leaves an R11 orphan on its own: deselected
# from the content gate must not mean uncovered by ANY gate. This gives the
# operational layer (`pytest -m operational`) its own, independent-cadence
# green signal, wired onto the existing deadman's-switch timer
# (background/deadmans_switch.py::run_cycle -> _check_operational_layer_signal),
# NOT onto every 5-min deadman cycle or every content-publish cycle -- the
# suite is slow, so it self-throttles to at most once per
# OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS via a last-run timestamp in its own
# state file (the same throttle shape as _push_due()/LAST_PUSH_FILE above).
#
# R5 transition-only + persistent-red paging: a SINGLE red result is logged
# and recorded to state but never pages -- a lone flake must not page. Only a
# PERSISTENT red (>= OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD consecutive
# checks) fires a real_alarm through the one notify() contract, keyed so an
# unchanged RED never re-pages faster than OPERATIONAL_LAYER_RE_ESCALATE_
# SECONDS. Recovery (red -> green) after a persistent-red page is itself a
# transition and pages once.
#
# DECOUPLING (by construction, not just convention): this signal owns its own
# state file (OPERATIONAL_LAYER_STATE_FILE, distinct from PUBLISH_GATE_STATE_
# FILE), its own pytest argv (the marker-expression COMPLEMENT of the content
# gate's), and is never called from anywhere in the commit/push/report/site
# regeneration path above -- it cannot block, skip, or alter what the content
# gate publishes, and a red result here can never touch content_gate_pytest_
# argv's own -m expression or PUBLISH_GATE_STATE_FILE. Purely observational.
OPERATIONAL_LAYER_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".operational_layer_signal.json"
OPERATIONAL_LAYER_MARKER_EXPR = "operational"
OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS = 60 * 60   # hourly -- suite is slow; deadman cycles every 5min
OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD = 2       # consecutive red checks before paging (no single-flake page)
OPERATIONAL_LAYER_RE_ESCALATE_SECONDS = 60 * 60      # re-page hourly while red persists (matches deadman cadence)
OPERATIONAL_LAYER_TRANSITION_KEY = "operational_layer_signal"


def operational_layer_pytest_argv(test_root="tests/"):
    """The exact pytest argv the independent operational-layer signal runs --
    the COMPLEMENT of publish_gate_pytest_argv's deselection above. Factored
    out for the same reason (R15: a control's scope must be inspectable)."""
    return [sys.executable, "-m", "pytest", test_root, "-q", "--tb=short",
            "-m", OPERATIONAL_LAYER_MARKER_EXPR]


def _read_operational_layer_state():
    """FAIL-CLOSED read (R15 fail-silent doctrine, same shape as
    _read_publish_gate_state above): an unreadable/corrupt state file resets
    the streak counters to zero rather than assuming a prior green, and
    reports state_unavailable=True so a caller can choose to treat it as due
    immediately rather than silently skip."""
    if not OPERATIONAL_LAYER_STATE_FILE.exists():
        return {"last_run_ts": None, "last_result": None, "consecutive_red": 0,
                "consecutive_green": 0, "state_unavailable": False}
    try:
        st = json.loads(OPERATIONAL_LAYER_STATE_FILE.read_text())
        if not isinstance(st, dict):
            raise ValueError("operational-layer state is not an object")
        st.setdefault("last_run_ts", None)
        st.setdefault("last_result", None)
        st.setdefault("consecutive_red", 0)
        st.setdefault("consecutive_green", 0)
        st["state_unavailable"] = False
        return st
    except (json.JSONDecodeError, OSError, ValueError):
        return {"last_run_ts": None, "last_result": None, "consecutive_red": 0,
                "consecutive_green": 0, "state_unavailable": True}


def _write_operational_layer_state(state):
    out = {
        "last_run_ts": state.get("last_run_ts"),
        "last_result": state.get("last_result"),
        "consecutive_red": state.get("consecutive_red", 0),
        "consecutive_green": state.get("consecutive_green", 0),
    }
    OPERATIONAL_LAYER_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    OPERATIONAL_LAYER_STATE_FILE.write_text(json.dumps(out, sort_keys=True))


def _operational_layer_check_due(now, state):
    """True if the throttle interval has elapsed (or no run is on record, or
    the state file itself was unreadable -- fail toward running the check
    rather than silently skipping it forever)."""
    if state.get("state_unavailable"):
        return True
    last_run = state.get("last_run_ts")
    if last_run is None:
        return True
    try:
        return (float(now) - float(last_run)) >= OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS
    except (TypeError, ValueError):
        return True


def run_operational_layer_signal(*, now=None, runner=None, notify_fn=None, log_fn=None, force=False):
    """Independent-cadence green signal for the DESELECTED operational layer
    (H23 L3). Runs `pytest -m operational`, records green/red to its OWN state
    file, and pages the director ONLY on a PERSISTENT red (>= N consecutive
    checks) -- a single red logs but never pages (R5: no flake pages).
    Recovery (red -> green) following a persistent-red page is itself a
    transition and pages once.

    Deliberately DECOUPLED from the content publish gate: this never runs
    publish_gate_pytest_argv(), never reads/writes PUBLISH_GATE_STATE_FILE,
    and its result cannot reach commit_and_push_if_changed or the report/site
    regeneration path -- nothing in this module calls it from there. Purely
    observational.

    `runner` -- injectable callable(argv) -> object with a `.returncode`
    attribute, defaulting to a real `subprocess.run` of
    operational_layer_pytest_argv(). Tests stub this so the real (slow) suite
    never runs in the unit test. Fully defensive: any internal error is
    logged and swallowed -- a monitoring check must never raise into its
    caller (matches every other check in deadmans_switch.py)."""
    log_fn = log_fn or log
    if notify_fn is None:
        from background.notify import notify as _notify
        notify_fn = _notify
    now = float(now) if now is not None else time.time()
    try:
        state = _read_operational_layer_state()
        if not force and not _operational_layer_check_due(now, state):
            return {"ran": False, "reason": "throttled"}

        if runner is None:
            def runner(argv):
                return subprocess.run(argv, cwd=str(PROJECT_DIR), timeout=1800)
        result = runner(operational_layer_pytest_argv())
        rc = getattr(result, "returncode", None)
        is_green = (rc == 0)

        consecutive_red = int(state.get("consecutive_red") or 0)
        consecutive_green = int(state.get("consecutive_green") or 0)
        paged = False

        if is_green:
            was_persistent_red = consecutive_red >= OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD
            consecutive_red = 0
            consecutive_green += 1
            if was_persistent_red:
                notify_fn(
                    "[OPERATIONAL LAYER RECOVERED] The independent-cadence operational-layer "
                    "signal (`pytest -m operational`, deselected from the content publish gate) "
                    "is GREEN again after a persistent red. Daemon-lifecycle tests recovered; "
                    "the live site/report was never affected by the prior red.",
                    kind="real_alarm", transition_key=OPERATIONAL_LAYER_TRANSITION_KEY, state="GREEN",
                )
                paged = True
                log_fn("Operational-layer signal: RECOVERED (green after persistent red) -- paged")
            else:
                log_fn("Operational-layer signal: green (consecutive_green={})".format(consecutive_green))
        else:
            consecutive_green = 0
            consecutive_red += 1
            if consecutive_red >= OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD:
                notify_fn(
                    "[OPERATIONAL LAYER RED] The independent-cadence operational-layer signal "
                    "(`pytest -m operational`, deselected from the content publish gate so it can "
                    "never wedge the live site) has been RED for {} consecutive check(s) (rc={}). "
                    "This does NOT affect the published site/report -- it is a daemon-lifecycle "
                    "test regression. Check tests/ for @pytest.mark.operational failures directly."
                    .format(consecutive_red, rc),
                    kind="real_alarm", transition_key=OPERATIONAL_LAYER_TRANSITION_KEY, state="RED",
                    re_escalate_after=OPERATIONAL_LAYER_RE_ESCALATE_SECONDS,
                )
                paged = True
                log_fn("Operational-layer signal: RED, persistent ({} consecutive) -- paged".format(
                    consecutive_red))
            else:
                log_fn(
                    "Operational-layer signal: red (consecutive_red={}, below persistent threshold "
                    "{}) -- logged, not paged (single flake)".format(
                        consecutive_red, OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD))

        _write_operational_layer_state({
            "last_run_ts": now,
            "last_result": "green" if is_green else "red",
            "consecutive_red": consecutive_red,
            "consecutive_green": consecutive_green,
        })
        return {"ran": True, "green": is_green, "rc": rc, "consecutive_red": consecutive_red,
                "consecutive_green": consecutive_green, "paged": paged}
    except Exception as exc:
        log_fn("Operational-layer signal check error (swallowed): {}".format(exc))
        return {"ran": False, "reason": "error", "error": str(exc)}


sys.path.insert(0, str(PROJECT_DIR))

from background.tree_lock import tree_lock  # noqa: E402


@contextmanager
def _run_lock():
    """Non-blocking exclusive lock so at most one process_run_complete.py
    instance does the heavy pipeline (report regen, dashboard/site build,
    full test suite -- ~5-10 min) at a time.

    sim_runner.py invokes this script synchronously right after writing a
    run_complete marker. background_worker.py separately sweeps staging/
    every 30 min for "leftover" markers still sitting in the root (the
    marker only moves to done/ at the very end of a successful run) and
    re-invokes this script on any it finds -- with no way to tell a marker
    that is genuinely abandoned (prior invocation crashed/timed out) apart
    from one that is simply still being processed by a live sim_runner
    invocation. Observed directly 2026-07-06: two instances running the
    full pipeline concurrently on the same marker. Losing this lock is not
    an error -- it just means another instance already has the marker in
    hand, so this invocation exits immediately and leaves the marker for
    that instance to archive."""
    RUN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = open(RUN_LOCK_FILE, "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fh.close()
        yield False
        return
    try:
        yield True
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def _run_fingerprint(data):
    """Stable content fingerprint of a run's meaningful outputs + the UTC date.

    Excludes volatile fields (timestamps, marker git_hash). Two runs with the
    same fingerprint would regenerate byte-identical business surfaces, so the
    second is pure burn. Includes the UTC date so a new calendar day always
    processes at least once (carrying that day's live-decision / rolling-fetch
    advance), even if the sim result itself is unchanged."""
    ret_log = data.get("retention_log", [])
    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_net_gbp": round(data.get("total_net_gbp", 0), 2),
        "total_gross_gbp": round(data.get("total_gross_gbp", 0), 2),
        "enterprise_value_gbp": round(data.get("enterprise_value_gbp", 0), 2),
        "final_treasury_gbp": round(data.get("final_treasury_gbp", 0), 2),
        "starting_treasury_gbp": round(data.get("starting_treasury_gbp", 0), 2),
        "total_capital_gbp": round(data.get("total_capital_gbp", 0), 2),
        "net_margin_after_cost_to_serve_gbp": round(data.get("net_margin_after_cost_to_serve_gbp", 0), 2),
        "committee_wake_ups_total": data.get("committee_wake_ups_total", 0),
        "bills_total": data.get("bills_total", 0),
        "offers": len(ret_log),
        "retained": sum(1 for r in ret_log if r.get("outcome") == "retained"),
        "no_offer_churns": len(data.get("no_offer_churn_log", [])),
        "churned_accounts": len(data.get("churned_billing_accounts", [])),
        "administration_event": bool(data.get("administration_event")),
    }


def _read_last_fingerprint():
    if not LAST_FINGERPRINT_FILE.exists():
        return None
    try:
        return json.loads(LAST_FINGERPRINT_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _write_last_fingerprint(fp):
    LAST_FINGERPRINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_FINGERPRINT_FILE.write_text(json.dumps(fp, sort_keys=True))


def _archive_marker(marker):
    """Move a processed/skipped marker into done/ so markers don't accumulate."""
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        marker.rename(DONE_DIR / marker.name)
        return True
    except FileNotFoundError:
        return (DONE_DIR / marker.name).exists()
    except OSError:
        # Cross-device or similar — fall back to copy + unlink.
        import shutil
        shutil.copy2(str(marker), str(DONE_DIR / marker.name))
        marker.unlink(missing_ok=True)
        return True


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = "- [{}] [process_run] {}".format(ts, msg)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write("\n" + entry)
    print(entry, flush=True)


def parse_marker(marker_path):
    text = marker_path.read_text()
    result = {}
    for line in text.splitlines():
        if line.startswith("JSON: "):
            result["json_path"] = Path(line[6:].strip())
        elif line.startswith("Git: "):
            result["git_hash"] = line[5:].strip()
        elif line.startswith("Duration: "):
            m = re.search(r"Duration:\s*([\d.]+)s", line)
            result["elapsed_s"] = float(m.group(1)) if m else 0.0
        elif line.startswith("Finished: "):
            result["finished"] = line[10:].strip()
    return result


def regenerate_report(json_path):
    result = subprocess.run(
        [sys.executable, "-m", "saas.reporting.annual_report", "--from-json", str(json_path)],
        cwd=str(PROJECT_DIR),
        timeout=120,
    )
    return result.returncode == 0


def update_latest_md(data, elapsed_s, git_hash="unknown"):
    text = LATEST_MD.read_text()
    ts_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = re.sub(r"Last updated: \S+", "Last updated: {}".format(ts_now), text)

    ledger = data.get("_ledger_headline", {})
    net = data.get("total_net_gbp", ledger.get("net_margin_gbp", 0))  # total_net_gbp includes bad debt + hedging costs
    gross = ledger.get("gross_margin_gbp", data.get("total_gross_gbp", 0))
    capital = data.get("total_capital_gbp", 0)
    t_start = data.get("starting_treasury_gbp", 0)
    t_end = data.get("final_treasury_gbp", 0)
    committee = data.get("committee_wake_ups_total", 0)
    bills = data.get("bills_total", 0)
    ev = data.get("enterprise_value_gbp", 0)
    net_cts = data.get("net_margin_after_cost_to_serve_gbp", 0)
    ret_log = data.get("retention_log", [])
    no_offer = data.get("no_offer_churn_log", [])
    churned = data.get("churned_billing_accounts", [])
    mins = elapsed_s / 60

    offers = len(ret_log)
    retained = sum(1 for r in ret_log if r.get("outcome") == "retained")
    no_offer_churns = len(no_offer)
    churn_count = len(churned)

    parts = [
        "**Latest simulation results (2016–2025)** — auto-processed ({:.0f}s / {:.0f} min):".format(elapsed_s, mins),
        "- Net margin: \xa3{:,.2f} | Gross: \xa3{:,.2f} | Capital: \xa3{:,.0f}".format(net, gross, capital),
        "- Treasury: \xa3{:,.0f} → \xa3{:,.0f} | {} committee interventions | {} bills issued".format(t_start, t_end, committee, bills),
        "- Enterprise value: \xa3{:,.2f} | Net after CTS: \xa3{:,.0f}".format(ev, net_cts),
        "- Retention: {} offers, {}/{} retained | {} no-offer churns | {} total churned accounts".format(
            offers, retained, offers, no_offer_churns, churn_count),
    ]
    new_block = "\n".join(parts)

    start_marker = "**Latest simulation results"
    try:
        start_idx = text.index(start_marker)
        end_idx = text.find("\n\n", start_idx)
        if end_idx == -1:
            end_idx = len(text)
        text = text[:start_idx] + new_block + text[end_idx:]
    except ValueError:
        # Block not yet present — append to end on first auto-process
        text = text.rstrip() + "\n\n" + new_block + "\n"
        log("Created 'Latest simulation results' block in LATEST.md")
    # Update "Net position:" summary line in Last Run section
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    text = re.sub(
        r"Net position: .*",
        "Net position: \xa3{:,.0f} (git {}, {})".format(net, git_hash, date_str),
        text,
    )
    LATEST_MD.write_text(text)


def _update_latest_md_organ_section():
    """Maintain the 'NAIVE ORGAN asks:' block in LATEST.md (the digest sink,
    design §3.2). Managed between HTML-comment markers, same shape as the
    'Latest simulation results' block — replaced in place, appended on first
    run."""
    from background import naive_organ
    section = naive_organ.render_digest_section()
    body = section if section else "_No open naive-organ questions._"
    block = "{}\n{}\n{}".format(ORGAN_BLOCK_START, body, ORGAN_BLOCK_END)
    text = LATEST_MD.read_text()
    if ORGAN_BLOCK_START in text and ORGAN_BLOCK_END in text:
        s = text.index(ORGAN_BLOCK_START)
        e = text.index(ORGAN_BLOCK_END) + len(ORGAN_BLOCK_END)
        text = text[:s] + block + text[e:]
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    LATEST_MD.write_text(text)


def _update_latest_md_effort_section():
    """Maintain the 'EFFORT SIZING' block in LATEST.md (G5_effort_sizing_
    discipline L2 digest sink) -- managed between HTML-comment markers, same
    shape as the naive-organ block above. Replaced in place, appended on
    first run."""
    from background import effort_digest
    section = effort_digest.render_digest_section()
    body = section if section else "_Effort sizing data unavailable this run._"
    block = "{}\n{}\n{}".format(EFFORT_BLOCK_START, body, EFFORT_BLOCK_END)
    text = LATEST_MD.read_text()
    if EFFORT_BLOCK_START in text and EFFORT_BLOCK_END in text:
        s = text.index(EFFORT_BLOCK_START)
        e = text.index(EFFORT_BLOCK_END) + len(EFFORT_BLOCK_END)
        text = text[:s] + block + text[e:]
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    LATEST_MD.write_text(text)


def run_effort_digest_step():
    """G5_effort_sizing_discipline L2 live hook: refresh the 'EFFORT SIZING'
    LATEST.md block every publish cycle. Fully defensive (matches
    run_naive_organ_step()'s own discipline): sizing is a DIAL, and this
    digest section must NEVER be able to break publishing -- any failure is
    logged and swallowed, never raised."""
    try:
        _update_latest_md_effort_section()
    except Exception as exc:
        log("Effort-sizing digest section skipped: {}".format(exc))


def run_naive_organ_step():
    """H11_naive_organ LIVE HOOK (L2 = habitual firing). Run the 7 SYSTEM
    detectors over the live observable state (map + run_history + logs) and ask
    the amnesiac Opus organ once per NEW fired contradiction (debounced). Output
    is QUESTIONS to naive_organ_log.jsonl + the 'NAIVE ORGAN asks:' block in
    LATEST.md — NEVER actions (safe by construction, SELF_INTERRUPT_DISCIPLINE
    QUEUE), so this cannot change what the pipeline does, only surface doubt.

    Fully defensive: any failure is logged and swallowed — the organ NEVER
    breaks publishing. Skipped under pytest (PYTEST_CURRENT_TEST) so the test
    suite never spawns a real `claude -p` Opus subprocess, and via
    NAIVE_ORGAN_DISABLE=1 as a kill switch."""
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("NAIVE_ORGAN_DISABLE") == "1":
        return
    try:
        from background import naive_organ
        written = naive_organ.run_organ_cycle(max_new=3)
        log("Naive organ: {} new question(s) asked (open: {})".format(
            len(written), naive_organ.hit_rate()["open"]))
    except Exception as exc:
        log("Naive organ cycle skipped: {}".format(exc))
    try:
        _update_latest_md_organ_section()
    except Exception as exc:
        log("Naive organ digest section skipped: {}".format(exc))


def run_fast_tests(git_hash: str):
    """Returns (passed: bool, timed_out: bool). Skips if git_hash already tested."""
    if LAST_TESTED_HASH_FILE.exists():
        if LAST_TESTED_HASH_FILE.read_text().strip() == git_hash:
            log("Tests skipped — already passed for git={}".format(git_hash))
            return True, False

    full_env = dict(os.environ)
    full_env["SIM_FAST_MODE"] = "1"
    try:
        # Blocking scope = publish-SURFACE tests only (see publish_gate_pytest_argv:
        # heavy ignores for speed, operational ignores for R10 class closure).
        #
        # R5/R9 (2026-07-29, a ~67-min publish wedge whose ONLY record was the
        # string "Tests FAILED - not committing"): the gate's own output was
        # discarded, so the blocking test was unknowable from the log and the
        # failure could not be diagnosed after the fact -- the site data has
        # since been regenerated, so the red is not reproducible later. An
        # alarm must carry its diagnostic payload, so capture the run and log
        # the failing node IDs. Capture is bounded (tail only) so a pathological
        # suite can never balloon the log.
        result = subprocess.run(
            publish_gate_pytest_argv("tests/"),
            cwd=str(PROJECT_DIR),
            env=full_env,
            timeout=600,
            capture_output=True,
            text=True,
            errors="replace",
        )
        if result.returncode == 0:
            LAST_TESTED_HASH_FILE.write_text(git_hash)
        else:
            _log_gate_failure_payload(result)
        return result.returncode == 0, False
    except subprocess.TimeoutExpired:
        # Timeout is a resource constraint, not a test failure — warn but don't block commit
        log("Fast test suite timed out (>600s) — committing anyway with warning")
        return True, True


# Bound on how much of a red gate's output reaches the log (chars).
GATE_FAILURE_TAIL_CHARS = 4000


def _log_gate_failure_payload(result):
    """Log WHICH tests blocked the publish, not just THAT they did.

    Called only on a red gate. Emits the failing node IDs (pytest's own
    ``FAILED <nodeid>`` / ``ERROR <nodeid>`` short-summary lines) plus a bounded
    tail of the combined output, so a wedge is diagnosable from the log alone
    after the underlying site data has been regenerated away."""
    out = "{}\n{}".format(result.stdout or "", result.stderr or "")
    node_ids = [ln.strip() for ln in out.splitlines()
                if ln.startswith(("FAILED ", "ERROR "))]
    if node_ids:
        log("Publish gate RED -- blocking test(s): {}".format("; ".join(node_ids[:20])))
    else:
        log("Publish gate RED (rc={}) -- no FAILED/ERROR summary line found".format(
            result.returncode))
    tail = out.strip()[-GATE_FAILURE_TAIL_CHARS:]
    if tail:
        log("Publish gate RED output tail:\n{}".format(tail))


def _run_weather_data(git_hash="unknown"):
    from tools.fetch_weather_data import generate_weather_data
    generate_weather_data(git_hash=git_hash)


def _fmt_gbp(v):
    """Format a GBP value with sign and £ prefix, e.g. £+225,920 or £-3,766."""
    sign = "+" if v >= 0 else ""
    return "\xa3{}{:,.0f}".format(sign, v)


def _cohort_coverage_gate_permits_publish():
    """Coverage-report PUBLISH GATE — director condition #3 of the generator
    population activation (POPULATION_ACTIVATION_AND_RUN_LEDGER 2026-07-25 §1.3;
    POOL_VS_BOOK_LAMBDA_STANDS 2026-07-27): when the R13 draw is ACTIVE
    (``SE_DRAW_POPULATION=1``) no derived figure may reach a surface until the
    realised-cohort coverage report is emitted and passes the redundancy floor —
    "a thin draw stops the number reaching a surface" (ruling §3). Thin cells are
    reported (in the written artifact + this log), never smoothed (R12).

    Returns True (publish may proceed) / False (block, caller NTFYs on gate fail).

    INERT WHEN OFF: reads the activation env var DIRECTLY (same signal
    ``live_population.draw_population_enabled`` uses) and returns True with ZERO
    new import/exception surface, so today's static-book publish path stays
    byte-identical and this gate can never jam it (the control-false-positive
    failure mode). FAIL-CLOSED WHEN ON: any exception building the report is a
    FAILED gate (R15 fail-silent doctrine — an unavailable check is a failed
    check), so it blocks rather than falling through to publication."""
    import os
    if os.environ.get("SE_DRAW_POPULATION", "") != "1":
        return True  # R13 draw inactive -> static-book path, inert & byte-identical
    try:
        from tools.generate_cohort_coverage import build_artifact, write_artifact
        artifact = build_artifact()
        write_artifact(artifact)
        gate_ok = bool(artifact.get("gate_ok"))
    except Exception as exc:  # noqa: BLE001 - unavailable coverage build == FAILED gate
        log("Coverage gate: realised-coverage report FAILED to build ({}); "
            "blocking publish (fail-closed, R15)".format(exc))
        return False
    if not gate_ok:
        cov = artifact.get("coverage", {}) or {}
        log("Coverage gate BLOCKED publish: realised draw fails the redundancy "
            "floor; thin cells NAMED = {}".format(cov.get("thin_cells", [])))
        return False
    log("Coverage gate PASSED: realised-cohort coverage meets floor; report written.")
    return True


def _trigger_frozen_baseline_refresh_out_of_band(git_hash="unknown"):
    """Spawn the weekly frozen-policy baseline refresh as a DETACHED background
    process when (and only when) it is stale -- never block the publish path.

    The refresh itself (tools.run_frozen_baseline.generate) holds a non-blocking
    single-writer lock, so spawning it every cycle a stale baseline is seen
    cannot stack overlapping multi-minute decade replays: the second and later
    spawns take the lock's absence and exit at once. Detached via
    start_new_session so it outlives this publish process; its output is
    discarded (it writes site/state/frozen_policy_baseline.json directly)."""
    sys.path.insert(0, str(PROJECT_DIR))
    from tools.run_frozen_baseline import should_refresh_baseline
    if not should_refresh_baseline():
        return
    proc = subprocess.Popen(
        [sys.executable, "-m", "tools.run_frozen_baseline", "--if-stale"],
        cwd=str(PROJECT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    log("Frozen-policy baseline stale -> refresh spawned OUT OF BAND (PID {}); "
        "publishing continues with the existing baseline (never blocks).".format(proc.pid))


def generate_dashboard_json(json_path, git_hash="unknown"):
    """Generate site/data/dashboard.json and every downstream site/state artifact.

    Returns False if the cross-surface consistency gate failed (Part C of the
    website-integrity fix: a mismatch must be surfaced loudly, never shipped
    silently) so the caller can NTFY immediately. The gate result is captured
    but must NOT short-circuit the rest of this function -- every generator
    below (shadow HTML, PROJECT_STATE.txt, billing ledger, population
    anchoring, customers.json, supplier.json, live decisions, scenario
    analysis, GitHub Pages mirror) has to run every cycle regardless of the
    gate outcome. (QG_REOPENED_R2.md, 2026-07-04: an early `return ok` here
    made all of the below dead code since Phase QF -- none of it had run on
    any auto-processed cycle since.)"""
    ok = True
    # Coverage-report publish gate (director condition #3). MUST run before any
    # derived-figure generator below so a thin R13 draw cannot reach a surface.
    # Inert while SE_DRAW_POPULATION is off (byte-identical); fail-closed when on.
    if not _cohort_coverage_gate_permits_publish():
        return False
    try:
        # Frozen-policy baseline (weekly, expensive): a full-decade replay x2
        # under CURRENT_POLICY vs NAIVE_POLICY, each invoking the real risk
        # committee (localhost Ollama LLM calls) -- MINUTES of wall-clock,
        # longer than a whole publish cycle. It MUST NOT run synchronously here.
        # PURPOSE/GUARANTEE (2026-07-29 wedge retro): the publish path is bounded
        # and never blocks on this OPTIONAL weekly artifact. Running it inline
        # wedged publishing -- 22 run_complete markers backed up, background_worker's
        # 900s per-marker timeout killing the processor and re-attempting forever,
        # the baseline 15 days stale so should_refresh_baseline() fired every cycle.
        # When stale we spawn the refresh OUT OF BAND (detached, single-writer
        # lock in run_frozen_baseline.generate) and continue immediately with the
        # existing baseline; the fresh result is picked up next cycle.
        # generate_dashboard_data below reads whatever frozen_policy_baseline.json
        # is on disk, so a deferred refresh never blanks the surface.
        _trigger_frozen_baseline_refresh_out_of_band(git_hash)
    except Exception as exc:
        log("Frozen-policy baseline out-of-band trigger failed (non-fatal): {}".format(exc))
    try:
        # D2_three_clocks (2026-07-12, ADVISOR_STEER_TWIN_READONLY.md real
        # finding): the settlement<->billed reconciliation bridge existed
        # only as a standalone script, never wired into the run pipeline --
        # "a first-class, always-on mechanism" per this atom's own
        # registration text. Must run before generate_dashboard_data, which
        # now reads its output (_check_bridge_reconciles).
        from tools.generate_margin_bridge import generate as gen_bridge
        bridge = gen_bridge(json_path)
        log("Generated site/data/margin_bridge.json (gap={:,.2f}, unexplained={:,.2f})".format(
            bridge.get("total_gap_gbp", 0.0), bridge.get("unexplained_remainder_gbp", 0.0)))
    except Exception as exc:
        log("Margin bridge generation failed: {}".format(exc))
    try:
        from tools.generate_dashboard_data import generate
        ok = generate(json_path)
        if ok:
            log("Generated site/data/dashboard.json")
        else:
            log("CONSISTENCY GATE FAILED — dashboard/exec-summary surfaces disagree (see stderr above)")
    except Exception as exc:
        log("Dashboard data generation failed: {}".format(exc))
        ok = True  # generation exception is not a consistency-gate failure; don't false-alarm
    try:
        from tools.generate_customer_data import generate as gen_cust
        gen_cust(json_path)
        log("Generated site/data/customers/ JSON")
    except Exception as exc:
        log("Customer data generation failed: {}".format(exc))
    try:
        # Must run before generate_invoice_data: real per-invoice bill-equation
        # data (usage, rate, standing charge) is wired from this ledger into the
        # customer JSON here; also must run before generate_shadow_html which reads
        # it independently.
        from tools.generate_billing_ledger import generate as gen_ledger
        gen_ledger(json_path)
        log("Generated site/state/billing_ledger.json")
    except Exception as exc:
        log("Billing ledger generation failed: {}".format(exc))
    try:
        from tools.generate_invoice_data import generate as gen_inv
        gen_inv(json_path)
        log("Generated customer invoice JSON")
    except Exception as exc:
        log("Invoice data generation failed: {}".format(exc))
    try:
        # Must run after generate_billing_ledger (real payments/arrears_history
        # source) and generate_invoice_data (patches the same customer JSON
        # files, this generator only adds a new "ledger" key alongside them).
        # BILLING_AND_PAYMENTS_LEDGER.md: Statement/Cashflow views.
        from tools.generate_payment_ledger_data import generate as gen_pay_ledger
        gen_pay_ledger()
        log("Generated per-account payment ledger JSON (BILLING_AND_PAYMENTS_LEDGER.md Statement/Cashflow)")
    except Exception as exc:
        log("Payment ledger generation failed: {}".format(exc))
    try:
        from tools.generate_customer_consumption import generate as gen_consumption
        gen_consumption(json_path)
        log("Generated customer consumption JSON (USAGE panel)")
    except Exception as exc:
        log("Customer consumption generation failed: {}".format(exc))
    try:
        # Must run after generate_customer_data/generate_invoice_data/
        # generate_customer_consumption: patches real timeline "effect"
        # annotations (item 3) and the reaction_chain (item 4) onto the
        # per-customer JSON those steps already produced.
        from tools.generate_customer_reaction_chain import generate as gen_reaction
        gen_reaction(json_path)
        log("Generated customer timeline effects + reaction_chain (CUSTOMER_360_REDESIGN.md v4 items 3-4)")
    except Exception as exc:
        log("Customer reaction-chain generation failed: {}".format(exc))
    try:
        # Must run after generate_dashboard_data (dashboard.json must exist)
        # and generate_billing_ledger (arrears-opened events need it).
        # SUPPLIER_TAB_OVERHAUL.md THE SPINE: portfolio event stream.
        from tools.generate_portfolio_event_stream import generate as gen_pes
        gen_pes(json_path)
        log("Generated portfolio event stream onto dashboard.json (SUPPLIER_TAB_OVERHAUL.md spine)")
    except Exception as exc:
        log("Portfolio event stream generation failed: {}".format(exc))
    try:
        from tools.generate_sim_data import generate as gen_sim
        gen_sim(git_hash)
        log("Generated site/data/sim_data.json")
    except Exception as exc:
        log("Sim data generation failed: {}".format(exc))
    try:
        from tools.generate_customer_sample import generate as gen_sample
        gen_sample(json_path)
        log("Generated site/data/customer_sample.json")
    except Exception as exc:
        log("Customer sample generation failed: {}".format(exc))
    # R11 no-orphan-transition fix (2026-07-14, surfaced by SITE1 Director-door
    # cold-eyes): these two generators were NOT wired into the pipeline, so
    # site/data/director_twin.json + provisional_plan.json froze/drifted after
    # every run. Wire them so the director-facing surfaces stay current.
    try:
        from tools.generate_director_twin_data import main as gen_twin
        gen_twin()
        log("Generated site/data/director_twin.json")
    except Exception as exc:
        log("Director twin data generation failed: {}".format(exc))
    try:
        from tools.generate_provisional_plan_data import main as gen_plan
        gen_plan()
        log("Generated site/data/provisional_plan.json")
    except Exception as exc:
        log("Provisional plan data generation failed: {}".format(exc))
    # Same no-orphan-transition rule, applied at the point the defect would be created
    # rather than after it froze (SITE_director_window_delta_view, 2026-08-03). The
    # delta feed is derived from the OTHER director feeds, so leaving it unwired would
    # freeze it against feeds that keep moving -- the exact 2026-07-14 failure above,
    # one layer up. Note this regenerates the DELTA only; the last-look STAMP is
    # deliberately never advanced here (it moves only on an explicit --mark-seen), or
    # the baseline would re-base every run and the panel would read "nothing changed"
    # forever.
    try:
        # Import generate(), NOT main(): main() is the CLI entry point and parses
        # sys.argv, so an in-process call inherited THIS process's arguments and
        # argparse exited with SystemExit(2) -- a BaseException the `except Exception`
        # below does not catch, i.e. it would abort the whole publish mid-way rather
        # than degrade to a logged failure. Caught by
        # test_website_integrity_fix.py::test_generate_dashboard_json_returns_gate_status.
        from tools.generate_director_data import generate as gen_director_delta
        gen_director_delta()
        log("Generated site/data/director_delta.json")
    except Exception as exc:
        log("Director delta data generation failed: {}".format(exc))
    try:
        # Must run after generate_customer_reaction_chain (timeline/reaction_chain
        # patched) and generate_customer_sample (churn_accuracy_by_renewal source).
        # WEBSITE_AS_SHOWCASE.md tab 4: case-study recommender.
        from tools.generate_case_study_recommender import generate as gen_case_studies
        gen_case_studies()
        log("Generated site/data/case_studies.json (WEBSITE_AS_SHOWCASE.md tab 4 case-study recommender)")
    except Exception as exc:
        log("Case-study recommender generation failed: {}".format(exc))
    try:
        from tools.generate_shadow_html import generate as gen_shadow
        gen_shadow()
        log("Generated site/shadow/ static HTML mirror")
    except Exception as exc:
        log("Shadow HTML generation failed: {}".format(exc))
    try:
        from tools.generate_project_state import generate as gen_state
        gen_state()
        log("Generated site/state/PROJECT_STATE.txt")
    except Exception as exc:
        log("PROJECT_STATE generation failed: {}".format(exc))
    try:
        from tools.generate_phases_json import generate as gen_phases
        gen_phases()
        log("Generated site/data/phases.json")
    except Exception as exc:
        log("phases.json generation failed: {}".format(exc))
    try:
        # Director page comments 2026-07-12 (/project/): "so what... velocity
        # and depth?" / "show the mix of tests... scope of what we are
        # testing" -- real pytest-collected counts per test-suite area, not
        # an estimate. ~30-40s (20 pytest --collect-only subprocess calls)
        # within an ~8-9min cycle; test-suite composition changes far less
        # often than the financial data driving the rest of this pipeline,
        # but re-running it every cycle is simpler than a staleness check
        # for a <10% time addition (BUDGET_UNCONSTRAINED.md).
        from tools.generate_test_mix_data import generate as gen_test_mix
        gen_test_mix()
        log("Generated site/data/test_mix.json")
    except Exception as exc:
        log("test_mix.json generation failed: {}".format(exc))
    try:
        from tools.generate_capabilities_json import generate as gen_capabilities
        gen_capabilities()
        log("Generated site/data/capabilities.json")
    except Exception as exc:
        log("capabilities.json generation failed: {}".format(exc))
    try:
        from tools.generate_maturity_map_data import generate as gen_maturity_map
        gen_maturity_map()
        log("Generated site/data/maturity_map.json")
    except Exception as exc:
        log("maturity_map.json generation failed: {}".format(exc))
    try:
        from tools.generate_simplified_data import generate as gen_simplified
        gen_simplified()
        log("Generated site/data/simplified.json")
    except Exception as exc:
        log("simplified.json generation failed: {}".format(exc))
    try:
        # PRODUCTION_READINESS_EVIDENCE_PASS.md's Part A found company/data/*.db
        # (the company's own operational financial/customer state) had NO
        # off-machine copy at all -- matches the "unrecoverable canonical data"
        # immediate-action carve-out. Rides along on the existing run-complete
        # cycle rather than a new standalone schedule; safe to run every cycle
        # (byte-identical DBs produce a clean no-op commit).
        from background.backup_company_data import backup_once
        backed_up = backup_once()
        log("Backed up company/data/*.db to ops repo: {}".format(backed_up))
    except Exception as exc:
        log("company/data backup failed: {}".format(exc))
    try:
        from tools.generate_saas_coverage_data import generate as gen_saas_coverage
        gen_saas_coverage()
        log("Generated site/data/saas_coverage.json")
    except Exception as exc:
        log("saas_coverage.json generation failed: {}".format(exc))
    try:
        from tools.generate_system_status import generate as gen_system_status
        gen_system_status()
        log("Generated site/data/system_status.json")
    except Exception as exc:
        log("system_status.json generation failed: {}".format(exc))
    try:
        from tools.population_anchor import generate as gen_anchor
        gen_anchor(json_path)
        log("Generated site/state/population_anchoring.json")
    except Exception as exc:
        log("Population anchoring failed: {}".format(exc))
    try:
        from tools.generate_customers_json import generate as gen_customers
        gen_customers(json_path)
        log("Generated site/data/customers.json")
    except Exception as exc:
        log("customers.json generation failed: {}".format(exc))
    try:
        from tools.generate_supplier_json import generate as gen_supplier
        gen_supplier(json_path)
        log("Generated site/data/supplier.json")
    except Exception as exc:
        log("supplier.json generation failed: {}".format(exc))
    try:
        from tools.project_portfolio_to_2026 import generate as gen_portfolio
        gen_portfolio(json_path)
        log("Generated site/state/live_portfolio.json")
    except Exception as exc:
        log("Live portfolio generation failed: {}".format(exc))
    try:
        # S1 Option A: extend the real Elexon SSP cache forward past 2025-06-07 on a
        # rolling basis BEFORE the live decision reads market state, so market_as_of_date
        # advances as real settlement data is published. Fully defensive (never raises,
        # never corrupts the frozen historical cache) -- a network-less/failed run is a
        # no-op and the decision falls back to the last known real price, honestly labelled.
        from background.refresh_elexon_ssp_rolling import refresh as refresh_ssp
        st = refresh_ssp()
        log("Rolling Elexon SSP refresh: {} ({} new records)".format(
            st.get("status"), st.get("fetched_records", 0)))
    except Exception as exc:
        log("Rolling Elexon SSP refresh failed (non-fatal): {}".format(exc))
    try:
        from tools.run_live_decisions import run_decisions
        run_decisions()
        log("Generated site/state/live_decisions_latest.json")
    except Exception as exc:
        log("Live decisions generation failed: {}".format(exc))
    try:
        from tools.run_live_decisions import run_scenario_analysis
        run_scenario_analysis()
        log("Generated site/state/scenario_analysis_latest.json")
    except Exception as exc:
        log("Scenario analysis generation failed: {}".format(exc))
    try:
        # Must run after run_live_decisions (reads live_decisions_log.jsonl it appends
        # to) and before generate_method_data (folds the scorecard onto the public
        # Method page -- S1 Decision 2: public from day one, misses included).
        from tools.generate_track_record_scorecard import generate as gen_scorecard
        gen_scorecard()
        log("Generated site/state/track_record_scorecard.json (Phase RX / S1 Option B)")
    except Exception as exc:
        log("Track record scorecard generation failed: {}".format(exc))
    try:
        from tools.generate_method_data import generate as gen_method
        gen_method()
        log("Generated site/data/method.json")
    except Exception as exc:
        log("method.json generation failed: {}".format(exc))
    try:
        # G11 activity-cost + utilisation (Method-door section): a reporting layer
        # over git history + the token log + the escalation register. Wired here
        # for the SAME R11 no-orphan-transition reason as the doors below -- a
        # generated surface must ride the regen cycle or it silently freezes
        # against its live sources. Its data file is ALSO in git_commit_push's
        # commit-list (both halves wired). DIAGNOSTIC never a target (R12).
        from tools.generate_activity_cost_data import generate as gen_activity_cost
        gen_activity_cost()
        log("Generated site/data/activity_cost.json (G11 activity-cost + utilisation)")
    except Exception as exc:
        log("activity_cost.json generation failed: {}".format(exc))
    try:
        # Door 4 THE PROOF + Door 3 THE COMPANY: their generators were built with
        # the pages but NOT wired here, so the pages froze against their own live
        # sources (Door-4 cold-eyes caught it: proof.json showed 60 atoms vs a live
        # 61). Run AFTER the maturity-map/scorecard/dashboard regen above (their
        # inputs) and BEFORE the GitHub-pages mirror below (so the mirror ships the
        # fresh copies). R11 no-orphan-transition: a generated surface must ride the
        # regen cycle or it silently decays.
        from tools.generate_proof_data import generate as gen_proof
        gen_proof()
        log("Generated site/data/proof.json (Door 4 THE PROOF)")
    except Exception as exc:
        log("proof.json generation failed: {}".format(exc))
    try:
        from tools.generate_company_data import generate as gen_company
        gen_company()
        log("Generated site/data/company.json (Door 3 THE COMPANY)")
    except Exception as exc:
        log("company.json generation failed: {}".format(exc))
    try:
        # Door 5 THE WORLD operational window -- the intra-day wholesale market feed
        # (site/data/market.json). Reads docs/market_data/price_feed.json and derives
        # the movement (latest / trajectory / session range / last change) so the
        # World panel can show what the market is DOING, not its annual mean
        # (director, 2026-07-20). Wired here for the SAME R11 no-orphan-transition
        # reason as the doors below -- a generated surface must ride the regen cycle
        # or it silently freezes against its live source. Its output file is picked
        # up by the site/data/*.json commit glob further down (no explicit path append
        # needed -- that is the durable class-fix for the orphaned-at-commit gap).
        from tools.generate_market_data import generate as gen_market
        gen_market()
        log("Generated site/data/market.json (Door 5 intra-day market feed)")
    except Exception as exc:
        log("market.json generation failed: {}".format(exc))
    try:
        # Door 5 THE WORLD: the two-sided epistemic-wall page (SIM ground truth vs
        # COMPANY observation + divergence) + the anchors register. Wired here for
        # the SAME R11 no-orphan-transition reason as Door 3/4 above -- a generated
        # surface must ride the regen cycle or it silently freezes against its live
        # sources (the exact orphaned-generator defect Door 4's cold-eyes caught).
        # Runs AFTER the dashboard/sim_data/anchoring regen it reads from.
        from tools.generate_world_data import generate as gen_world
        gen_world()
        log("Generated site/data/world.json (Door 5 THE WORLD)")
    except Exception as exc:
        log("world.json generation failed: {}".format(exc))
    try:
        # Door 5 demand-arrow evidence: the WORDS->DIAGRAM->EVIDENCE campaign
        # requires the weather->demand arrow of the World causal spine to carry its
        # belief-vs-truth chart. A rendering of the already-measured W1_5 coupled-gap
        # result -- wired here for the same R11 no-orphan-transition reason as world.json
        # (a generated surface must ride the regen cycle or it silently freezes).
        from tools.generate_premise_demand_data import generate as gen_premise_demand
        gen_premise_demand()
        log("Generated site/data/premise_demand.json (Door 5 demand-arrow evidence)")
    except Exception as exc:
        log("premise_demand.json generation failed: {}".format(exc))
    # (2026-07-20 v4 site rebuild) The combined "Method + Simplified" casebook surface
    # (site/method-casebook/) was RETIRED -- redundant with the separate canonical Method
    # (roles/rules/loop/retro/track-record) and Simplified (register) doors, which cover its
    # content. Its generator + commit-list entries removed with it.
    try:
        from tools.mirror_github_pages import mirror as mirror_gh_pages
        mirrored = mirror_gh_pages()
        log("Mirrored {} file(s) to docs/shadow + docs/state for GitHub Pages".format(len(mirrored)))
    except Exception as exc:
        log("GitHub Pages mirror failed: {}".format(exc))
    return ok


def generate_site(data, elapsed_s, git_hash, finished_ts):
    """No-op: site/index.html is a static SPA that reads site/data/dashboard.json."""
    pass


def git_commit_push(git_hash, net_margin):
    report = PROJECT_DIR / "docs" / "reports" / "ANNUAL_REPORT.md"
    site_index = PROJECT_DIR / "site" / "index.html"
    site_data = PROJECT_DIR / "site" / "data" / "dashboard.json"
    site_customers = PROJECT_DIR / "site" / "data" / "customers"
    site_sample = PROJECT_DIR / "site" / "data" / "customer_sample.json"
    site_shadow = PROJECT_DIR / "site" / "shadow"
    files = [str(report), str(LATEST_MD)]
    # H11_naive_organ: commit the organ's question log alongside the run whose
    # publish cycle produced it (LATEST.md's digest block is already tracked).
    if NAIVE_ORGAN_LOG.exists():
        files.append(str(NAIVE_ORGAN_LOG))
    if site_index.exists():
        files.append(str(site_index))
    if site_data.exists():
        files.append(str(site_data))
    if site_customers.exists():
        files.append(str(site_customers))
    if site_sample.exists():
        files.append(str(site_sample))
    if site_shadow.exists():
        files.append(str(site_shadow))
    site_state_sample = PROJECT_DIR / "site" / "state" / "customer_sample.json"
    if site_state_sample.exists():
        files.append(str(site_state_sample))
    site_state_project = PROJECT_DIR / "site" / "state" / "PROJECT_STATE.txt"
    if site_state_project.exists():
        files.append(str(site_state_project))
    docs_status_project = PROJECT_DIR / "docs" / "status" / "PROJECT_STATE.txt"
    if docs_status_project.exists():
        files.append(str(docs_status_project))
    site_state_billing = PROJECT_DIR / "site" / "state" / "billing_ledger.json"
    if site_state_billing.exists():
        files.append(str(site_state_billing))
    site_state_anchor = PROJECT_DIR / "site" / "state" / "population_anchoring.json"
    if site_state_anchor.exists():
        files.append(str(site_state_anchor))
    site_data_customers = PROJECT_DIR / "site" / "data" / "customers.json"
    if site_data_customers.exists():
        files.append(str(site_data_customers))
    site_data_supplier = PROJECT_DIR / "site" / "data" / "supplier.json"
    if site_data_supplier.exists():
        files.append(str(site_data_supplier))
    site_state_scenario = PROJECT_DIR / "site" / "state" / "scenario_analysis_latest.json"
    if site_state_scenario.exists():
        files.append(str(site_state_scenario))
    site_state_decision_log = PROJECT_DIR / "site" / "state" / "live_decisions_log.jsonl"
    if site_state_decision_log.exists():
        files.append(str(site_state_decision_log))
    # Phase RO (NAV_STORY_PLATFORM_METHOD.md): site/index.html moved from the
    # Supplier dashboard to the new Home/Story landing; the dashboard itself
    # now lives at site/supplier/, and the new Platform section needs both its
    # static page and its generated data file tracked here or they never get
    # picked up by the auto-commit pipeline.
    site_supplier_html = PROJECT_DIR / "site" / "supplier" / "index.html"
    if site_supplier_html.exists():
        files.append(str(site_supplier_html))
    site_saas_coverage_json = PROJECT_DIR / "site" / "data" / "saas_coverage.json"
    if site_saas_coverage_json.exists():
        files.append(str(site_saas_coverage_json))
    site_method_html = PROJECT_DIR / "site" / "method" / "index.html"
    if site_method_html.exists():
        files.append(str(site_method_html))
    site_method_json = PROJECT_DIR / "site" / "data" / "method.json"
    if site_method_json.exists():
        files.append(str(site_method_json))
    # G11 activity-cost + utilisation section rides the Method door -- its data
    # file must be tracked here or the regenerated-but-uncommitted file stays
    # frozen on the live site (same orphan-transition reasoning as the blocks above).
    site_activity_cost_json = PROJECT_DIR / "site" / "data" / "activity_cost.json"
    if site_activity_cost_json.exists():
        files.append(str(site_activity_cost_json))
    site_case_studies_json = PROJECT_DIR / "site" / "data" / "case_studies.json"
    if site_case_studies_json.exists():
        files.append(str(site_case_studies_json))
    site_track_record_json = PROJECT_DIR / "site" / "state" / "track_record_scorecard.json"
    if site_track_record_json.exists():
        files.append(str(site_track_record_json))
    # Door 5 THE WORLD (two-sided epistemic-wall page + anchors register): the
    # page and its generated data file must be tracked here or the auto-commit
    # pipeline never picks up the freshly-regenerated world.json (same reasoning
    # as the Platform/Method blocks above -- a regenerated-but-uncommitted file
    # stays frozen on the live site).
    site_world_html = PROJECT_DIR / "site" / "world" / "index.html"
    if site_world_html.exists():
        files.append(str(site_world_html))
    site_world_json = PROJECT_DIR / "site" / "data" / "world.json"
    if site_world_json.exists():
        files.append(str(site_world_json))
    # Door 5 operational window: the intra-day market feed derived from
    # price_feed.json. Tracked explicitly here (matching world/company/proof
    # above) AND covered by the site/data/*.json glob below -- belt-and-braces so
    # a regenerated-but-uncommitted market.json can never freeze on the live site.
    site_market_json = PROJECT_DIR / "site" / "data" / "market.json"
    if site_market_json.exists():
        files.append(str(site_market_json))
    # Door 4 THE PROOF + Door 3 THE COMPANY: their generators were wired into the
    # regen block above, but their data/page files were NOT added to this commit-
    # list -- so they regenerated every run yet the fresh copy was never committed,
    # leaving the deployed pages frozen (the same orphaned-at-commit gap Door 5
    # closed for world.json; caught by Door 5's cold-eyes). Track them here too.
    # Doors 3/4 (The Company, The Proof): page + generated data file tracked here or the
    # regenerated JSON stays frozen on the live site (the orphaned-at-commit gap Door 5
    # closed for world.json). (method-casebook retired 2026-07-20 -- entries removed.)
    for _door_file in (
        PROJECT_DIR / "site" / "proof" / "index.html",
        PROJECT_DIR / "site" / "data" / "proof.json",
        PROJECT_DIR / "site" / "company" / "index.html",
        PROJECT_DIR / "site" / "data" / "company.json",
    ):
        if _door_file.exists():
            files.append(str(_door_file))
    # R10 CLASS-CLOSURE for the orphaned-at-commit gap (SITE1 Expert-Hour,
    # 2026-07-16): the block above and the explicit method.json/world.json/etc.
    # appends fixed this gap ONE FILE AT A TIME, so three MORE generated data
    # files silently recurred it -- simplified.json (live showed 168/48 vs a real
    # 291/93, hiding ~42% of the "nothing filtered" register), provisional_plan.json
    # (2 days stale on the director page), system_status.json (6 days stale, the
    # action-needed queue). generate_*_data() writes every one of these under
    # site/data/ each cycle, so the durable fix is to commit the WHOLE generated
    # data surface, not to add another explicit path line each time a door is
    # built. Any future site/data/*.json is now tracked automatically.
    site_data_dir = PROJECT_DIR / "site" / "data"
    if site_data_dir.is_dir():
        for _gen_json in sorted(site_data_dir.glob("*.json")):
            files.append(str(_gen_json))
    # GitHub Pages mirror (docs/staging/ADVISOR_GITHUBIO_MIRROR.md): the advisor's
    # fetch path to poesys.net proved persistently stale independent of any CD
    # incident, so shadow pages + state JSONs also ship from docs/ (GitHub Pages),
    # same as docs/status/PROJECT_STATE.txt already does.
    docs_shadow = PROJECT_DIR / "docs" / "shadow"
    if docs_shadow.exists():
        files.append(str(docs_shadow))
    docs_state = PROJECT_DIR / "docs" / "state"
    if docs_state.exists():
        files.append(str(docs_state))
    if DONE_DIR.exists():
        files.append(str(DONE_DIR))
    msg = "Auto-process run complete: report + LATEST.md + site/ (git={}, net=\xa3{:,.0f})".format(
        git_hash, net_margin
    )
    # Serialize against other git writers (interactive session, autonomous_runner
    # turns, a concurrent process_run_complete.py invocation) -- see
    # background/tree_lock.py. Without this, a `git add` from another writer
    # staged between this one's add and commit gets swept into this commit
    # (observed directly: a manually-staged code change landed inside an
    # unrelated auto-process commit message).
    with tree_lock():
        try:
            subprocess.run(["git", "add"] + files, cwd=str(PROJECT_DIR), timeout=120)
            # Publish the pre-gate inbox fold too (maturity_map.yaml change + the deleted
            # atom_status inboxes) so a reconciled map lands WITH the run it belongs to,
            # never dangling uncommitted. -A stages the inbox DELETIONS. No-op if nothing
            # was folded this cycle.
            subprocess.run(["git", "add", "-A", "docs/design/maturity_map.yaml",
                            "docs/design/atom_status"], cwd=str(PROJECT_DIR), timeout=120)
            # COMMIT TIMEOUT (2026-08-03): this is NOT a bare `git commit` -- it runs
            # the whole pre-commit hook chain (tools/git-hooks/pre-commit: status-honesty,
            # pre_commit_test_gate, level_promotion_gate, site_lane_gate,
            # moap_coherence_gate, ruling_archive_question_gate). A publish commit stages
            # site/data/**, which fires site_lane_gate's BROAD trigger -- the WHOLE site
            # suite, measured at 27.3s on its own, against the 30s cap this used to carry.
            # The cap was set when the hooks were trivial and quietly became a
            # publish-blocker as the suite grew: the deadline is now a property of how many
            # tests exist, not of whether the commit is healthy.
            result = subprocess.run(["git", "commit", "-m", msg], cwd=str(PROJECT_DIR),
                                    timeout=GIT_COMMIT_HOOK_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as exc:
            # UNCAUGHT, THIS CRASHED THE PUBLISH (CLAUDE.md's own standing learning:
            # "sim_runner TimeoutExpired must be caught -- uncaught exception kills the
            # loop"). It propagated out of _process(), so process_run_complete exited
            # rc=1 having logged NEITHER "Nothing to commit or commit failed" NOR "Done"
            # -- the wedge detector recorded it as a test_regression, which it was not,
            # and the diagnosis pointed at the test suite for hours. A slow hook chain
            # must degrade to "retry next cycle", never take the pipeline down, and must
            # say SO in the log.
            log("Commit TIMED OUT after {}s ({}) -- the pre-commit hook chain outran its "
                "deadline. Nothing committed; retrying next cycle. If this repeats, the "
                "hook chain (not the run) is the cause.".format(
                    GIT_COMMIT_HOOK_TIMEOUT_SECONDS, exc.__class__.__name__))
            return False
        if result.returncode != 0:
            log("Nothing to commit or commit failed")
            return False

        if not _push_due():
            log("Committed locally, push deferred (throttled to every {}min)".format(
                PUSH_THROTTLE_SECONDS // 60
            ))
            return True

        # SELF-VERIFYING PUSH (2026-07-24, 3.5h origin-freeze incident): a bare
        # `git push` that returns rc=0 WITHOUT advancing origin (a phantom
        # "Everything up-to-date" against a stale remote-tracking ref) must NOT
        # reset the throttle -- that is exactly what froze origin for 3.5h: every
        # cycle recorded a "successful" push that never reached origin, so _push_due
        # stayed False and 15 real commits piled up locally, unseen by the advisor
        # bridge (which depends on this pipeline). Explicit refspec (never rely on
        # bare-push upstream resolution) + ground-truth verification via ls-remote
        # (the real remote, not the local tracking ref). _record_push_time fires
        # ONLY on a VERIFIED advance; a phantom logs LOUD and leaves the throttle
        # untouched so the NEXT cycle retries immediately instead of deferring.
        push = subprocess.run(["git", "push", "origin", "HEAD:main"],
                              cwd=str(PROJECT_DIR), timeout=60)
        local_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_DIR),
                                    capture_output=True, text=True, timeout=15).stdout.strip()
        remote_head = ""
        try:
            ls = subprocess.run(["git", "ls-remote", "origin", "refs/heads/main"],
                                cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=30)
            remote_head = ls.stdout.split()[0] if ls.stdout.strip() else ""
        except Exception as exc:
            log("Push verify: ls-remote failed ({}) -- cannot confirm origin advanced".format(exc))
        if _push_reached_origin(push.returncode, remote_head, local_head):
            _record_push_time()
            return True
        from background.notify import notify
        notify(
            "[SIM] PUSH DID NOT REACH ORIGIN (rc={}, origin={}, head={}) -- publish pipeline "
            "commits are stacking LOCALLY and the advisor bridge is blind. NOT recording a push "
            "time; next cycle retries. If this repeats, the remote-tracking ref or auth is the "
            "cause.".format(push.returncode, (remote_head or "?")[:9], (local_head or "?")[:9]),
            kind="real_alarm",
        )
        log("PUSH did NOT advance origin (rc={}, origin={}, head={}) -- throttle left untouched, "
            "will retry next cycle".format(push.returncode, (remote_head or "?")[:9], (local_head or "?")[:9]))
        return False


def _push_reached_origin(push_rc: int, remote_head: str, local_head: str) -> bool:
    """A push counts as SUCCESS only if it advanced origin to the local HEAD.

    The 3.5h origin-freeze (2026-07-24): a bare `git push` returned rc=0 while
    origin did NOT advance (phantom "Everything up-to-date"), and the caller
    recorded a push time anyway -- so _push_due() stayed False and every real
    push was deferred behind a success that never happened. This makes the
    success condition GROUND-TRUTH: rc==0 AND the real remote head (from
    ls-remote, not the local tracking ref) equals local HEAD. A phantom rc=0
    with a stale/behind remote head returns False -> no throttle reset -> retry.
    """
    return push_rc == 0 and bool(remote_head) and remote_head == local_head


def _push_due() -> bool:
    """True if PUSH_THROTTLE_SECONDS have elapsed since the last recorded
    successful push (or none has ever been recorded)."""
    if not LAST_PUSH_FILE.exists():
        return True
    try:
        last = json.loads(LAST_PUSH_FILE.read_text())["ts"]
    except (json.JSONDecodeError, KeyError, TypeError, OSError):
        return True
    return (datetime.now(timezone.utc).timestamp() - last) >= PUSH_THROTTLE_SECONDS


def _record_push_time() -> None:
    LAST_PUSH_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_PUSH_FILE.write_text(json.dumps({"ts": datetime.now(timezone.utc).timestamp()}))


# ── Fault #1 (2026-07-25 overnight publish-freeze): liveness publication must NOT
# be coupled to business-output-change ──────────────────────────────────────────
LIVENESS_SURFACE_FILES = (
    "site/data/tick_heartbeat.json",
    "docs/observability/agent_status.json",
)


def _refresh_published_liveness_on_skip(git_hash: str) -> bool:
    """Publish ONLY the liveness surface on a change-detection SKIP. Returns True
    iff a fresh liveness commit reached origin this call.

    ROOT CAUSE (director-flagged, 2026-07-25): the worker-tick heartbeat
    (site/data/tick_heartbeat.json) is rewritten on disk every 60s, but it only
    reaches origin as a SIDE-EFFECT of a CONTENT publish (commit_and_push_if_
    changed of site/). When the sim output is byte-identical across runs -- the
    common at-rest case, net=£1,521,070 for hours -- the change-detection gate
    SKIPs every cycle, so no content publish happens and the PUBLISHED heartbeat
    freezes for hours while every daemon is healthy. Overnight this froze the live
    site's liveness signal for ~4h though nothing had died. A liveness signal whose
    freshness depends on the business OUTPUT changing is the defect -- fail-silent:
    a heartbeat frozen because healthy-and-unchanged is indistinguishable on origin
    from one frozen because dead.

    Fix: on a SKIP, when a push is DUE (the SAME 30-min throttle as content, so no
    per-cycle commit spam -- the very thing the change-detection gate exists to
    prevent), commit+push ONLY the liveness files via the SAME self-verifying push
    (ground-truth ls-remote, records the throttle only on a verified advance). This
    bounds published-heartbeat staleness to <= PUSH_THROTTLE_SECONDS instead of
    unbounded, with no regen/report/site/test. Commits ONLY the explicit paths
    (never the whole index) so a concurrent writer's staged work is never swept in.
    """
    if not _push_due():
        return False
    files = [str(PROJECT_DIR / rel) for rel in LIVENESS_SURFACE_FILES
             if (PROJECT_DIR / rel).exists()]
    if not files:
        return False
    msg = ("chore(liveness): publish heartbeat while sim output unchanged (git={}) -- "
           "decouples published liveness from content-change (Fault#1 2026-07-25)".format(git_hash))
    with tree_lock():
        subprocess.run(["git", "add"] + files, cwd=str(PROJECT_DIR), timeout=30)
        # Commit ONLY these paths (never the whole index): a concurrent publisher's
        # staged files must not be swept into a liveness commit.
        result = subprocess.run(["git", "commit", "-m", msg, "--"] + files,
                                cwd=str(PROJECT_DIR), timeout=30)
        if result.returncode != 0:
            # Heartbeat byte-identical to the committed copy -> nothing to commit. Fine.
            return False
        push = subprocess.run(["git", "push", "origin", "HEAD:main"],
                              cwd=str(PROJECT_DIR), timeout=60)
        local_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_DIR),
                                    capture_output=True, text=True, timeout=15).stdout.strip()
        remote_head = ""
        try:
            ls = subprocess.run(["git", "ls-remote", "origin", "refs/heads/main"],
                                cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=30)
            remote_head = ls.stdout.split()[0] if ls.stdout.strip() else ""
        except Exception as exc:
            log("Liveness push verify: ls-remote failed ({})".format(exc))
        if _push_reached_origin(push.returncode, remote_head, local_head):
            _record_push_time()
            log("Liveness heartbeat published to origin (sim output unchanged, "
                "published-liveness decoupled from content-change).")
            return True
        log("Liveness heartbeat push did NOT advance origin (rc={}, origin={}, head={}) -- "
            "throttle untouched, retry next cycle.".format(
                push.returncode, (remote_head or '?')[:9], (local_head or '?')[:9]))
        return False


def _run_history_max_net():
    hp = PROJECT_DIR / "docs" / "observability" / "run_history.json"
    if not hp.exists():
        return 0.0
    try:
        import json as _j
        history = _j.loads(hp.read_text())
        return max((h.get("net_margin_gbp", 0) for h in history), default=0.0)
    except Exception:
        return 0.0


# ── H15: publish-gate failure alerting (silent-wedge detector) ───────────────

def _classify_gate_failure(rc):
    """Cheap OOM-vs-regression classification from a processor return code.

    A negative code == the child was killed by signal -rc (subprocess
    convention); -9 = SIGKILL, overwhelmingly the OOM-killer / a resource
    limit rather than a code regression. A positive non-zero code is a real
    processing/test failure ('Tests FAILED', report regen failed, ...)."""
    if rc is None:
        return "unknown"
    try:
        rc = int(rc)
    except (TypeError, ValueError):
        return "unknown"
    if rc < 0:
        return "resource_kill" if rc == -9 else "signal_kill"
    if rc == 0:
        return "pass"
    return "test_regression"


def _gate_failure_label(kind):
    return {
        "resource_kill": "resource kill (SIGKILL/OOM -- almost certainly memory, NOT a code regression)",
        "signal_kill": "killed by a signal (a resource/environment problem, not a normal test failure)",
        "test_regression": "test failure or processing error (rc>0 -- a real regression is possible)",
        "unknown": "unknown cause (return code unavailable)",
    }.get(kind, kind)


def _read_publish_gate_state():
    """Load the wedge-state file. FAIL-CLOSED (R15 fail-silent doctrine): an
    unreadable/corrupt state is itself a failed check -- signalled via
    state_unavailable=True so the current failure escalates immediately rather
    than being lost to a silent reset that would suppress the alarm."""
    if not PUBLISH_GATE_STATE_FILE.exists():
        return {"failures": [], "alerted_at": None, "state_unavailable": False}
    try:
        st = json.loads(PUBLISH_GATE_STATE_FILE.read_text())
        if not isinstance(st, dict):
            raise ValueError("gate state is not an object")
        st.setdefault("failures", [])
        st.setdefault("alerted_at", None)
        # wedge_since (2026-07-24, WEDGE3_AND_RUNG1_MECHANISE): the PERSISTENT start-of-streak
        # timestamp -- NOT trimmed to the 1h window like `failures`, so it is the only field that
        # can measure a wedge older than the window. Set on the first failure of a streak, preserved
        # across every later failure, cleared to None on the next clean publish. The supervisor's
        # RUNG-1 unwedge draw (background/supervisor.py::_publish_gate_wedge_active) reads it to
        # decide ">60 min". Without it the ">60 min" rule was un-mechanisable (window trimming caps
        # the oldest surviving `failures`/`alerted_at` timestamp below 60 min for a live wedge) --
        # the exact reason the prose rule was consumed-not-absorbed twice.
        st.setdefault("wedge_since", None)
        st["state_unavailable"] = False
        return st
    except (json.JSONDecodeError, OSError, ValueError):
        return {"failures": [], "alerted_at": None, "wedge_since": None, "state_unavailable": True}


def _write_publish_gate_state(state):
    out = {"failures": state.get("failures", []), "alerted_at": state.get("alerted_at"),
           "wedge_since": state.get("wedge_since")}
    PUBLISH_GATE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUBLISH_GATE_STATE_FILE.write_text(json.dumps(out, sort_keys=True))


def _fire_publish_gate_alert(recent, kind, rc, git_hash, unavailable, send_ntfy_fn):
    window_min = PUBLISH_GATE_WINDOW_SECONDS // 60
    n = len(recent)
    detail = _gate_failure_label(kind)
    count_phrase = "an unknown number of" if unavailable else str(n)
    what = ("The run-complete PUBLISH GATE has failed {} time(s) in a row within the "
            "last {} min -- the site/report pipeline is WEDGED and run_complete markers "
            "are piling up unpublished. Latest cause: {} (rc={}, git={}).").format(
                count_phrase, window_min, detail, rc, git_hash)
    if unavailable:
        what += (" NOTE: the gate-state file was unreadable, so this alert fired "
                 "fail-closed on the first failure rather than risk staying silent.")
    how = ("Check docs/observability/sim-runner-log.md for the 'Tests FAILED' / failure "
           "lines. rc=-9 is almost certainly OOM (free memory or cut test parallelism), "
           "NOT a code bug; rc>0 means run the fast suite locally to find the regression. "
           "The alarm clears automatically on the next clean publish.")
    why = ("A silently-wedged publish gate stops the live site and report updating with "
           "NO other signal -- this is the exact ~45-min silent stall of 2026-07-14 (H15).")
    msg = "[ACTION NEEDED] {}\nWhat: {}\nHow: {}\nWhy: {}".format(PUBLISH_GATE_ITEM_ID, what, how, why)
    if send_ntfy_fn is None:
        from background.notify import notify
        send_ntfy_fn = lambda m: notify(m, kind="real_alarm")
    sent_id = send_ntfy_fn(msg)
    # Durable register + daily re-ping while it stays wedged (best-effort -- a
    # register failure must never suppress the NTFY that already went out).
    # CLASS FIX (2026-07-18): register_item() never advances the send-clock any
    # more -- only a CONFIRMED successful send (a truthy id) does, via
    # mark_sent(). A failed send here leaves the item due, so the deadman's
    # daily due_for_reping() sweep retries instead of the item silently
    # looking "recently pinged" on a page that never reached the phone.
    try:
        from background import action_needed
        action_needed.register_item(PUBLISH_GATE_ITEM_ID, what=what, how=how, why=why)
        if sent_id:
            action_needed.mark_sent(PUBLISH_GATE_ITEM_ID)
    except Exception as exc:
        log("Publish-gate action_needed register skipped: {}".format(exc))
    return msg


def record_publish_gate_failure(reason, rc=None, git_hash="unknown", *, now=None, send_ntfy_fn=None):
    """Record ONE publish-gate failure and fire a single [ACTION NEEDED] alert
    once N failures accumulate within the window (re-armed by a cooldown so a
    persistently-wedged pipeline can't spam). Returns a small result dict for
    callers/tests. Fully defensive -- never raises into the caller (a
    monitoring failure must not break the pipeline it monitors)."""
    try:
        now = float(now) if now is not None else time.time()
        state = _read_publish_gate_state()
        unavailable = bool(state.get("state_unavailable"))
        kind = _classify_gate_failure(rc)
        failures = [f for f in state.get("failures", [])
                    if isinstance(f, dict) and now - float(f.get("ts", 0)) <= PUBLISH_GATE_WINDOW_SECONDS]
        failures.append({"ts": now, "reason": str(reason), "rc": rc, "kind": kind, "git_hash": git_hash})
        count = len(failures)
        # PERSISTENT wedge-start (2026-07-24): preserve the existing streak start; only stamp `now`
        # when the streak is starting (no prior wedge_since). Survives the 1h window trim above so a
        # long wedge's true age stays measurable. Cleared to None by record_publish_gate_success.
        prev_wedge_since = state.get("wedge_since")
        wedge_since = prev_wedge_since if isinstance(prev_wedge_since, (int, float)) else now
        threshold_met = unavailable or count >= PUBLISH_GATE_FAILURE_THRESHOLD
        last_alert = state.get("alerted_at")
        armed = last_alert is None or (now - float(last_alert)) >= PUBLISH_GATE_COOLDOWN_SECONDS
        fired = False
        alerted_at = last_alert
        if threshold_met and armed:
            _fire_publish_gate_alert(failures, kind, rc, git_hash, unavailable, send_ntfy_fn)
            alerted_at = now
            fired = True
        _write_publish_gate_state({"failures": failures, "alerted_at": alerted_at, "wedge_since": wedge_since})
        log("Publish-gate failure #{} ({}, rc={}) -- alert {}".format(
            count, kind, rc, "FIRED" if fired else ("armed/cooldown" if threshold_met else "below threshold")))
        return {"count": count, "kind": kind, "threshold_met": threshold_met, "fired": fired}
    except Exception as exc:
        log("record_publish_gate_failure error (swallowed): {}".format(exc))
        return {"count": 0, "kind": "error", "threshold_met": False, "fired": False}


def record_publish_gate_success(*, now=None):
    """A clean publish (or a clean skip) CLEARS the wedge state: resets the
    consecutive-failure streak, re-arms the alarm, and resolves the durable
    action_needed item if one was open. Idempotent; never raises."""
    try:
        had_state = False
        if PUBLISH_GATE_STATE_FILE.exists():
            prev = _read_publish_gate_state()
            had_state = bool(prev.get("failures")) or prev.get("alerted_at") is not None
        _write_publish_gate_state({"failures": [], "alerted_at": None, "wedge_since": None})
        if had_state:
            log("Publish gate recovered -- cleared wedge state, re-armed alarm.")
            try:
                from background import action_needed
                reg = action_needed.load_register()
                if PUBLISH_GATE_ITEM_ID in reg and not reg[PUBLISH_GATE_ITEM_ID].get("resolved"):
                    ts = datetime.now(timezone.utc).isoformat()
                    action_needed.resolve_item(
                        PUBLISH_GATE_ITEM_ID,
                        answer="Auto-resolved: the publish gate recovered and a run published cleanly at {}.".format(ts))
            except Exception as exc:
                log("Publish-gate action_needed resolve skipped: {}".format(exc))
        return had_state
    except Exception as exc:
        log("record_publish_gate_success error (swallowed): {}".format(exc))
        return False


def record_publish_gate_outcome(marker, rc):
    """Route ONE run-complete processing return code into the publish-gate wedge
    detector. THE shared router for every caller that publishes a marker.

    WHY IT LIVES HERE (2026-08-03, this exact defect): this routing used to
    exist ONLY as `background_worker._record_publish_gate_outcome`, wired into
    `process_leftover_run_markers()`'s sweep. But that sweep is NOT the path
    that actually publishes in the steady state -- `background/sim_runner.py`
    publishes the marker it just wrote, every cycle, and fed its return code to
    NOBODY. The detector was therefore blind to the ONLY healthy publisher and
    saw only the sweep, which by construction chews the STALE backlog. Result
    (observed 2026-07-30..08-03): sim_runner published cleanly every ~10 min --
    04:02Z "Committed locally... Done" -- while the sweep failed on 4-day-old
    markers, so the wedge streak only ever grew. The alarm stayed armed for
    ~5960 min against a pipeline that was working, firing a PRIORITY-ZERO
    doorbell each tick for a wedge that no longer existed.

    R10 (class, not instance): the fix is not "also call it from sim_runner" as
    a second copy -- it is ONE router that every publish path must feed, so a
    THIRD publisher added later cannot reintroduce a half-blind detector by
    forgetting to duplicate the logic.

    THREE outcomes, not two (fail-open closed 2026-07-29, preserved here): a
    lock-skip (EXIT_LOCK_SKIPPED) means the caller did NOT publish the marker
    -- evidence of NOTHING about the gate's health -- so it records NEITHER a
    success NOR a failure and leaves the streak exactly as it found it.
    Recording it as a success actively DISARMED the detector.

    Defensive by construction: a monitoring failure must never break the
    pipeline it monitors. Returns "success" / "failure" / "skipped" / None
    (None == the router itself errored) so callers and tests can assert which
    branch ran.
    """
    try:
        if rc == EXIT_LOCK_SKIPPED:
            return "skipped"
        if rc == 0:
            record_publish_gate_success()
            return "success"
        git_hash = "unknown"
        try:
            git_hash = parse_marker(Path(marker)).get("git_hash", "unknown")
        except Exception:
            pass
        record_publish_gate_failure(
            "process_run_complete rc={} on {}".format(rc, Path(marker).name),
            rc=rc, git_hash=git_hash,
        )
        return "failure"
    except Exception as exc:
        log("record_publish_gate_outcome error (swallowed): {}".format(exc))
        return None


def maybe_ntfy(data, net_margin, insights=None):
    """Send NTFY for notable exceptions. Returns log message if sent, else None."""
    admin = data.get("administration_event")
    from background.notify import notify
    if admin:
        date_str = admin.get("date", "unknown date") if isinstance(admin, dict) else str(admin)
        notify(
            "[SIM] ADMINISTRATION EVENT on {} - net margin £{:,.0f}. Check annual report.".format(
                date_str, net_margin
            ),
            kind="real_alarm",
        )
        return "NTFY sent: administration event on {}".format(date_str)
    prev_best = _run_history_max_net()
    is_new_high = net_margin > prev_best * 1.01 and prev_best > 0
    is_new_low = net_margin < prev_best * 0.5 and prev_best > 1_000_000
    if not (is_new_high or is_new_low):
        return None
    tag = "[NEW HIGH]" if is_new_high else "[NEW LOW]"
    summary = getattr(insights, "executive_summary", "") if insights else ""
    acts = list(getattr(insights, "recommended_actions", ()) if insights else [])
    msg = "[SIM] {} Net margin £{:,.0f}".format(tag, net_margin)
    if summary:
        msg += " -- " + str(summary)[:120]
    if acts:
        msg += " | Action: " + str(acts[0])[:80]
    notify(msg, kind="real_alarm")
    return "NTFY sent: {} net margin £{:,.0f}".format(tag, net_margin)



def main(marker_path_str):
    """COUPLING (2026-07-13, director-flagged; the exit-code half FIXED
    2026-07-29): a lock-skip below returns EXIT_LOCK_SKIPPED (75), a THIRD
    outcome distinct from both "ran to completion" (0) and "a real processing
    error" (1, inside `_process()`). It used to return 0, so no caller could
    tell a skip from a real publish -- and `background_worker`'s sweep
    therefore fed rc==0 into `record_publish_gate_success()`, wiping the H15
    wedge streak for a marker it had never published (fail-open: the detector
    disarmed by its own input). Callers must now treat 75 as "still pending,
    nobody published it": no success, no failure. `background/sim_runner.py`
    only
    ever calls this with the ONE marker it just created THIS cycle -- it
    never re-scans staging/ for a marker it was told (by this exact log
    line) would be "picked up next cycle if still present." That promise
    is not kept by this function or by sim_runner.py; it is kept ENTIRELY
    by `background/background_worker.py::process_leftover_run_markers()`,
    which unconditionally re-globs every `run_complete_*.md` in staging/ at
    the top of its own loop, every cycle, regardless of peak hours or queue
    state -- see that function's own docstring for the other half of this
    coupling. A marker skipped here WILL still be processed, just not by
    sim_runner.py's own retry (there is none) -- by background_worker.py's
    sweep instead."""
    with _run_lock() as acquired:
        if not acquired:
            log("Another process_run_complete instance is already running -- "
                "skipping {} (will be picked up by background_worker.py's "
                "process_leftover_run_markers() sweep, not by sim_runner.py "
                "itself retrying)".format(
                    Path(marker_path_str).name))
            return EXIT_LOCK_SKIPPED
        return _process(marker_path_str)


def _process(marker_path_str):
    marker = Path(marker_path_str).resolve()
    if not marker.exists():
        if (DONE_DIR / Path(marker_path_str).name).exists():
            log("Already in done/ (duplicate run): {}".format(Path(marker_path_str).name))
            return 0
        log("Marker not found: {}".format(marker))
        return 1

    log("Processing {}".format(marker.name))
    fields = parse_marker(marker)
    json_path = fields.get("json_path")
    git_hash = fields.get("git_hash", "unknown")
    elapsed_s = fields.get("elapsed_s", 0.0)

    if not json_path or not json_path.exists():
        log("JSON not found: {}".format(json_path))
        return 1

    data = json.loads(json_path.read_text())
    net_margin = data.get("total_net_gbp", 0)

    # Change-detection gate: if this run's meaningful outputs are identical to
    # the last fully-processed run (same headline figures, same UTC date), the
    # entire regen/test/commit pipeline below would reproduce byte-identical
    # surfaces -- skip it, log one line, archive the marker. An administration
    # event always processes (never skipped) so the NTFY exception path fires.
    # A pending FORCE_REPUBLISH_FLAG (a hold was just released) also forces
    # processing through regardless of fingerprint match -- see its own
    # comment above for why: a code fix can change correctness without
    # moving headline figures enough to break the fingerprint match.
    fingerprint = _run_fingerprint(data)
    # R3 two-strike redesign (2026-07-12, director page comment "/project/
    # data looks stale"): a real, code-only change (a new UI feature, a new
    # billing mechanism with no material P&L impact) previously left every
    # tracked headline figure unchanged, so the gate silently skipped
    # publishing for ~5 hours straight across 7+ real commits -- the exact
    # same class of incident FORCE_REPUBLISH_FLAG was built for (the
    # hold-release case), recurring on a different trigger (an ordinary
    # commit, not a hold release). Folding the producing commit's hash into
    # the compared fingerprint closes the class generally: ANY new commit
    # since the last published run now breaks the equality check and forces
    # a republish, regardless of whether financial headline figures moved --
    # while a genuinely unchanged commit across consecutive cycles (the
    # common case) still skips exactly as before.
    fingerprint["source_git_hash"] = git_hash
    last_fp = _read_last_fingerprint()
    forced = FORCE_REPUBLISH_FLAG.exists()
    if last_fp == fingerprint and not fingerprint["administration_event"] and not forced:
        _archive_marker(marker)
        log("SKIP (change-detection gate): identical to last processed run "
            "[net=\xa3{:,.0f}, date={}] -- no regen/test/commit. Archived {}.".format(
                net_margin, fingerprint["date"], marker.name))
        # Fault #1 (2026-07-25): even on a content SKIP, keep the PUBLISHED liveness
        # surface fresh on origin (throttled) -- the on-disk heartbeat updates every
        # 60s but only reached origin via a content publish, so an unchanged-output
        # night froze the live-site heartbeat ~4h though the machine was healthy.
        try:
            _refresh_published_liveness_on_skip(git_hash)
        except Exception as exc:  # never let liveness publishing break the SKIP path
            log("Liveness refresh on SKIP raised (non-fatal): {}".format(exc))
        return 0
    if forced:
        log("FORCED processing (a hold was just released) -- bypassing change-detection gate "
            "regardless of fingerprint match [net=\xa3{:,.0f}, date={}].".format(
                net_margin, fingerprint["date"]))
        FORCE_REPUBLISH_FLAG.unlink()

    log("Regenerating ANNUAL_REPORT.md from {}".format(json_path.name))
    if not regenerate_report(json_path):
        log("Report regeneration failed")
        return 1

    log("Updating LATEST.md")
    update_latest_md(data, elapsed_s, git_hash)

    # Run insights (so-what layer) MUST be regenerated before the dashboard/
    # site build below: generate_dashboard_data.py reads run_insights.json
    # straight off disk for the exec-summary section, separately from the
    # run_output.json it loads for the totals section. Building the dashboard
    # first would bake in the PREVIOUS run's exec summary next to this run's
    # totals -- exactly the contradiction the website-integrity fix closed.
    log("Generating run insights (so-what layer)")
    run_insights = None
    try:
        from tools.generate_insights import generate_insights, save_insights, append_run_history
        run_insights = generate_insights(data, git_hash)
        save_insights(run_insights, RUN_INSIGHTS_PATH)
        append_run_history(run_insights, RUN_HISTORY_PATH)
        log("Run insights saved: {}".format(run_insights.executive_summary[:80]))
    except Exception as exc:
        log("Run insights generation skipped: {}".format(exc))

    # H11_naive_organ live hook: run AFTER run_history.json is appended above so
    # the flat-metric detectors (T1/T5) see this run's figure. Questions only.
    run_naive_organ_step()

    # G5_effort_sizing_discipline L2 live hook: refresh the 'EFFORT SIZING'
    # digest block (remaining-effort / estimate-vs-actual / XL-decompose
    # signal). Reads maturity_map.yaml directly; independent of run_history.
    run_effort_digest_step()

    log("Generating site/data/dashboard.json")
    consistency_ok = generate_dashboard_json(json_path, git_hash)
    if not consistency_ok:
        from background.notify import notify
        notify(
            "[SIM] CONSISTENCY GATE FAILED (git={}) — dashboard totals and exec-summary "
            "insights disagree on a headline number. Site figures may be untrustworthy "
            "until this is fixed. See docs/observability/sim-runner-log.md for detail.".format(git_hash),
            kind="real_alarm",
        )
        log("NTFY sent: consistency gate failure")
    generate_site(data, elapsed_s, git_hash, fields.get("finished"))

    try:
        from tools.revenue_sanity_check import run_check
        _ok, sanity_report = run_check(data)
        status = "PASS" if _ok else "ANOMALIES"
        log("Revenue sanity: {} — see annual report".format(status))
    except Exception as exc:
        log("Revenue sanity check skipped: {}".format(exc))

    log("Publishing market price feed")
    try:
        from simulation.publish_market_feed import publish as _publish_feed
        _publish_feed()
        log("Price feed published to docs/market_data/price_feed.json")
    except Exception as exc:
        log("Price feed publication skipped: {}".format(exc))

    log("Publishing HH consumption data feed")
    try:
        from simulation.publish_consumption_data import publish_consumption
        publish_consumption()
        log("Consumption feed published to docs/market_data/consumption_feed.json")
    except Exception as exc:
        log("Consumption feed publication skipped: {}".format(exc))

    log("Fetching weather data (Open-Meteo)")
    try:
        _run_weather_data(git_hash)
        log("Weather data written to site/data/weather.json")
    except Exception as exc:
        log("Weather data fetch skipped: {}".format(exc))

    # PRE-GATE RECONCILIATION (2026-07-16, class fix for the stale-live-state test
    # wedge): fold any atom_status inbox a fork wrote (F1, in its own commit) into the
    # working-tree map BEFORE the gate, so the map-reconciliation CONTROL tests a
    # RECONCILED map, not a fork/fold-race transient. An unfolded W1_8 inbox intermittently
    # failed test_no_unfolded_atom_status_inbox_at_rest and wedged the publish gate. This
    # closes the whole reconciliation-race CLASS (any pending fork report), not one atom.
    # Working-tree fold is enough for the gate; git_commit_push includes the map so the
    # fold is published, not left dangling. tree_lock serialises against the daemon's own
    # fold. Non-fatal: a fold error must never crash the publish.
    try:
        from background.tree_lock import tree_lock as _tree_lock
        from tools import merge_atom_status as _mas
        with _tree_lock():
            # suppression-lint: not-a-suppression _folded -- functional reduce (atom_status inbox reconciliation), not a page/alarm suppression
            _folded = _mas.merge()
        if _folded:
            log("Pre-gate fold: reconciled {} pending atom_status inbox(es) into the map: {}".format(
                len(_folded), _folded))
    except Exception as _exc:
        log("Pre-gate inbox fold skipped (non-fatal): {}".format(_exc))

    log("Running fast test suite (SIM_FAST_MODE=1)")
    tests_ok, timed_out = run_fast_tests(git_hash)
    if not tests_ok:
        log("Tests FAILED - not committing")
        return 1
    if timed_out:
        log("WARNING: tests timed out — results unverified but committing")

    # Move the marker to done/ BEFORE committing so the archive itself lands in
    # the same commit as the run it documents, instead of sitting untracked
    # forever (observed: 7+ done/ markers never made it into any commit).
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        marker.rename(DONE_DIR / marker.name)
        log("Moved {} to done/".format(marker.name))
    except FileNotFoundError:
        if (DONE_DIR / marker.name).exists():
            log("{} already in done/ (processed concurrently)".format(marker.name))
        else:
            log("WARNING: {} vanished from staging and not in done/".format(marker.name))

    log("Committing and pushing (net=\xa3{:,.0f})".format(net_margin))
    if not git_commit_push(git_hash, net_margin):
        log("Commit/push failed (possibly nothing changed)")

    # Record this run's fingerprint AFTER a full process so the next identical
    # cycle is skipped by the change-detection gate above. Written even if the
    # commit was a no-op (nothing changed) -- that is exactly the state we want
    # future identical cycles to short-circuit on.
    _write_last_fingerprint(fingerprint)

    # Keep agent_status.json financial metrics current (phase/tests preserved by phase-close)
    try:
        import json as _json
        from background.agent_status import update_sim_metrics, STATUS_FILE
        _existing = _json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {}
        update_sim_metrics(
            phase=_existing.get("phase", 0),
            tests_passing=_existing.get("tests_passing", 0),
            treasury_gbp=data.get("final_treasury_gbp", 0),
            net_margin_gbp=data.get("total_net_gbp", 0),
            enterprise_value_gbp=data.get("enterprise_value_gbp", 0),
        )
    except Exception as exc:
        log("agent_status metrics update skipped: {}".format(exc))

    ntfy_msg = maybe_ntfy(data, net_margin, run_insights)
    if ntfy_msg:
        log(ntfy_msg)
    log("Done")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <path/to/run_complete_TIMESTAMP.md>".format(sys.argv[0]))
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
