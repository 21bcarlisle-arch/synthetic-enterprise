"""OPS1 sub-step 4: the drift control made LIVE — periodic reconcile, transition-only paging.

The load-bearing property is that this is the LIVE consumer the reconcile lacked (its absence let a
live worker-seat declared `held` produce no HELD_VIOLATED, 2026-07-17). R5: it pages only on a drift
TRANSITION, never a heartbeat; a clean run logs and stays silent."""
from __future__ import annotations

import pytest

from background import reconcile_watch as W


@pytest.fixture(autouse=True)
def _isolate_the_gap_ledger_source(monkeypatch):
    """The gap-ledger reconcile is the THIRD drift source and it reads real git + the real ledger.
    A new source that a test lets fall through to live disk silently flips every clean/drift
    assertion in this file the moment the live ledger goes stale — the same fixture-isolation
    class the F-lane draw rung hit. Default it to clean here; the tests that exercise it inject
    their own rows in the body, which runs after this fixture and therefore wins."""
    monkeypatch.setattr(W._gap, "reconcile", lambda *a, **k: [])


def _clean():
    proc = [{"session": "sim-runner", "status": "OK", "alarm": False},
            {"session": "supervisor", "status": "HELD", "alarm": False}]
    sched = [{"kind": "unit", "item": "file-api.service", "status": "OK", "alarm": False}]
    return proc, sched


def _drift():
    proc = [{"session": "supervisor", "status": "HELD_VIOLATED", "alarm": True},
            {"session": "sim-runner", "status": "OK", "alarm": False}]
    sched = [{"kind": "cron", "item": "0 * * * * evil", "status": "UNDECLARED_CRON", "alarm": True}]
    return proc, sched


def test_signature_is_order_independent_and_empty_when_clean():
    proc, sched = _clean()
    assert W.drift_signature(proc, sched) == []
    proc2, sched2 = _drift()
    sig = W.drift_signature(proc2, sched2)
    assert "P:supervisor:HELD_VIOLATED" in sig
    assert "S:0 * * * * evil:UNDECLARED_CRON" in sig


def test_clean_report_says_clean_and_lists_nothing():
    proc, sched = _clean()
    sig, summary = W.build_report(proc, sched)
    assert sig == [] and "clean" in summary


def test_drift_report_lists_each_alarm():
    proc, sched = _drift()
    sig, summary = W.build_report(proc, sched)
    assert "supervisor: HELD_VIOLATED" in summary
    assert "UNDECLARED_CRON" in summary


@pytest.fixture
def _wired(monkeypatch, tmp_path):
    pages = []
    monkeypatch.setattr(W, "STATE_FILE", tmp_path / ".reconcile_watch_state.json")
    monkeypatch.setattr(W, "LOG_FILE", tmp_path / "reconcile-watch-log.md")
    return pages


def test_clean_run_does_not_page(_wired):
    proc, sched = _clean()
    paged = W.run(proc, sched, notify=lambda *a, **k: _wired.append((a, k)))
    assert paged is False and _wired == []


def test_drift_appears_pages_once_then_stays_silent_until_change(_wired):
    proc, sched = _drift()
    notify = lambda *a, **k: _wired.append((a, k))
    assert W.run(proc, sched, notify=notify) is True          # transition clean->drift: page
    assert len(_wired) == 1
    assert W.run(proc, sched, notify=notify) is False         # same drift: no repeat (R5)
    assert len(_wired) == 1


def test_drift_clearing_pages_a_recovery(_wired):
    notify = lambda *a, **k: _wired.append((a, k))
    dp, ds = _drift()
    W.run(dp, ds, notify=notify)                              # drift -> page (rotating_light)
    cp, cs = _clean()
    assert W.run(cp, cs, notify=notify) is True               # cleared -> page (recovery)
    assert _wired[-1][1]["headers"]["X-Tags"] == "white_check_mark"


def test_drift_present_is_typed_high_priority(_wired):
    dp, ds = _drift()
    W.run(dp, ds, notify=lambda *a, **k: _wired.append((a, k)))
    assert _wired[0][1]["headers"]["X-Tags"] == "rotating_light"
    assert _wired[0][1]["headers"]["X-Priority"] == "high"

# --- the gap-ledger source, wired in 2026-08-09 ------------------------------------------------
# H_GAP's three-times-registered residual: eleven couple_*/gap tools, no production caller, so
# their published rows go stale unseen. This watch is the caller — the reconcile is report-only,
# so being SEEN on a transition is the whole mechanism.

def _gap_drift():
    return [{"item": "W1_11_fabric_physics_core", "kind": "row", "producers": [],
             "status": "stale", "detail": "producer moved"},
            {"item": "W2_7_willingness_classification", "kind": "row", "producers": [],
             "status": "current", "detail": "unchanged"}]


def test_a_stale_gap_row_reaches_the_drift_signature_under_its_own_prefix():
    proc, sched = _clean()
    sig = W.drift_signature(proc, sched, _gap_drift())
    assert sig == ["G:W1_11_fabric_physics_core:stale"]


def test_a_gap_row_measured_by_current_code_adds_nothing():
    proc, sched = _clean()
    current_only = [r for r in _gap_drift() if r["status"] == "current"]
    assert W.drift_signature(proc, sched, current_only) == []


def test_gap_drift_pages_on_its_own_even_when_processes_are_clean(_wired):
    """The property that matters: this source can page by itself. A third source folded in so
    that it can only ever ride along with process drift would be decorative."""
    proc, sched = _clean()
    notify = lambda *a, **k: _wired.append((a, k))  # noqa: E731
    assert W.run(proc, sched, notify=notify, gap_results=_gap_drift()) is True
    assert "gap:stale" in _wired[0][0][0]
    assert _wired[0][1]["headers"]["X-Tags"] == "rotating_light"


def test_the_summary_caps_the_gap_lines_and_SAYS_SO_while_the_signature_keeps_them_all():
    """No silent caps: an elided line must be counted out loud, and the transition signal must
    still see every item or a change inside the tail could not page."""
    many = [{"item": f"W9_{i}_x", "kind": "row", "producers": [], "status": "stale",
             "detail": "d"} for i in range(W._GAP_SUMMARY_CAP + 3)]
    proc, sched = _clean()
    sig, summary = W.build_report(proc, sched, many)
    assert len(sig) == len(many)
    assert summary.count("[gap:stale]") == W._GAP_SUMMARY_CAP
    assert "and 3 further gap-ledger" in summary


def test_run_falls_through_to_the_live_reconcile_when_no_rows_are_injected(monkeypatch):
    """Production must not need the caller to pass rows — otherwise the wiring is inert."""
    seen = []
    monkeypatch.setattr(W._gap, "reconcile", lambda *a, **k: seen.append(1) or [])
    proc, sched = _clean()
    W.run(proc, sched, notify=lambda *a, **k: None)
    assert seen == [1]


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational


# ── DAEMONS RUNNING CODE THAT IS NO LONGER HEAD (2026-08-21) ────────────────────────────────
# R2, "committed != running", is a permanent rule here and it was being broken at scale: three
# daemons 57, 63 and 65 changed loaded modules behind, four days stale. The supervisor was
# drawing work on four-day-old logic and a publishing-down alarm fixed that morning was inert in
# the process that runs it.
#
# The control was NOT missing. `evaluate_boot_sha_drift` computed it exactly and `health_check`
# phrased the fault well. Its only caller was `start_worker.sh` -- stack startup -- so it ran at
# the one moment drift cannot exist and never while it accumulated. health-check-log.md's last
# entry was 2026-07-29, twenty-three days earlier.

def test_a_daemon_far_behind_head_is_reported():
    """The observed incident."""
    out = W._drift_report(evaluate=lambda: {"stale_detail": {
        "supervisor": ["m"] * 57, "background-worker": ["m"] * 63}})
    assert any("supervisor (57 modules behind)" in line for line in out)
    assert any("background-worker (63 modules behind)" in line for line in out)


def test_ordinary_churn_is_not_reported():
    """ALWAYS-RED IS THE FAILURE MODE HERE, not under-reporting. This tree takes ~20 commits a
    day, so every daemon is 1-2 modules behind within minutes of restarting. A detector that
    fires on that gets ignored -- which is exactly how four days of real drift went unseen while
    a correct control computed it."""
    assert W._drift_report(evaluate=lambda: {"stale_detail": {
        "sim-runner": ["m"] * 2, "deadmans-switch": ["m"]}}) == []


def test_the_threshold_sits_in_the_gap_the_measurement_found():
    """1-2 is churn, 57+ is stale, and nothing was observed between. A threshold inside that gap
    is read from the data; one outside it would be a preference."""
    assert 2 < W.DRIFT_MODULE_THRESHOLD < 57


def test_the_drift_check_never_restarts_anything():
    """REPORT-ONLY (G-R3). Redeploying a daemon mid-work has its own blast radius and belongs to
    a decision, not to a reconcile pass -- a watcher that quietly restarted things is the
    accretion OPS1 forbids."""
    # The CODE, not the prose. First cut grepped the whole source and tripped on this
    # function's own docstring, which contains "restart" precisely because it promises not to --
    # a check reading text it should not have been reading, which is the day's recurring shape
    # in miniature.
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(W._drift_report).strip())
    fn = tree.body[0]
    if (fn.body and isinstance(fn.body[0], ast.Expr)
            and isinstance(fn.body[0].value, ast.Constant)):
        fn.body = fn.body[1:]                      # drop the docstring
    code = ast.unparse(ast.Module(body=fn.body, type_ignores=[])).lower()
    for verb in ("restart", "systemctl", "kill", "terminate"):
        assert verb not in code, f"the drift reporter must not {verb}"


def test_a_failing_drift_check_does_not_stop_the_reconcile(monkeypatch):
    """FAIL-SAFE: this rides the reconcile timer, and the reconcile is the thing that must not
    stop. An exception here is logged and swallowed."""
    def boom():
        raise RuntimeError("git unavailable")
    monkeypatch.setattr(W, "_drift_report", lambda *a, **k: boom())
    paged = W.run(proc_results=[], sched_results=[], gap_results=[], notify=lambda *a, **k: None)
    assert paged is False
