import json
from datetime import datetime, timedelta, timezone

import pytest

from tools import run_frozen_baseline as rfb


def _fake_phase4c_result(ev_gbp, net_gbp, offers, retained, treasury=1000.0, churned=0):
    return {
        "phase2b": {
            "retention_log": [
                {"outcome": "retained" if i < retained else "churned_despite_offer"}
                for i in range(offers)
            ],
            # amount_gbp is stored negated (cash-out convention, saas/ledger.py)
            "retention_cost_events": [{"amount_gbp": -10.0} for _ in range(offers)],
            "total_net": net_gbp,
            "final_treasury": treasury,
            "churned_billing_accounts": ["C{}".format(i) for i in range(churned)],
        },
        "enterprise_value": {
            "portfolio": {"enterprise_value_gbp": ev_gbp, "account_count": 5},
        },
    }


def test_portfolio_metrics_extracts_headline_fields():
    result = _fake_phase4c_result(ev_gbp=1000.0, net_gbp=500.0, offers=3, retained=2, churned=1)
    metrics = rfb._portfolio_metrics(result)
    assert metrics["enterprise_value_gbp"] == 1000.0
    assert metrics["total_net_gbp"] == 500.0
    assert metrics["retention_offers_made"] == 3
    assert metrics["retention_offers_retained"] == 2
    assert metrics["retention_cost_gbp"] == 30.0
    assert metrics["churned_accounts"] == 1


def test_run_frozen_baseline_computes_delta_ev(monkeypatch):
    calls = []

    def fake_run_phase4c(report_end=None, policy=None):
        calls.append(policy.name)
        if policy.name == "current":
            return _fake_phase4c_result(ev_gbp=1200.0, net_gbp=600.0, offers=4, retained=3)
        return _fake_phase4c_result(ev_gbp=1000.0, net_gbp=550.0, offers=2, retained=1)

    monkeypatch.setattr(rfb, "run_phase4c", fake_run_phase4c)
    baseline = rfb.run_frozen_baseline(report_end="2020-01-01")

    assert calls == ["current", "naive"]
    assert baseline["delta_ev_gbp"] == pytest.approx(200.0)
    assert baseline["delta_net_margin_gbp"] == pytest.approx(50.0)
    assert baseline["current_policy"]["retention_offers_made"] == 4
    assert baseline["naive_policy"]["retention_offers_made"] == 2
    assert "£200" in baseline["narrative"]


def test_should_refresh_baseline_true_when_missing(tmp_path):
    assert rfb.should_refresh_baseline(tmp_path / "missing.json") is True


def test_should_refresh_baseline_false_when_fresh(tmp_path):
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }))
    assert rfb.should_refresh_baseline(path) is False


def test_should_refresh_baseline_true_when_stale(tmp_path):
    path = tmp_path / "baseline.json"
    stale = datetime.now(timezone.utc) - timedelta(days=30)
    path.write_text(json.dumps({"generated_at": stale.strftime("%Y-%m-%dT%H:%M:%SZ")}))
    assert rfb.should_refresh_baseline(path) is True


def test_should_refresh_baseline_true_when_corrupt(tmp_path):
    path = tmp_path / "baseline.json"
    path.write_text("not json")
    assert rfb.should_refresh_baseline(path) is True


def test_generate_skips_when_fresh(tmp_path, monkeypatch):
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }))

    def should_not_be_called(report_end=None):
        raise AssertionError("run_frozen_baseline should not be called when fresh")

    monkeypatch.setattr(rfb, "run_frozen_baseline", should_not_be_called)
    result = rfb.generate(path=path)
    assert result is None


def test_generate_writes_when_forced(tmp_path, monkeypatch):
    path = tmp_path / "baseline.json"
    monkeypatch.setattr(rfb, "REFRESH_LOCK_PATH", tmp_path / ".refresh.lock")

    def fake_baseline(report_end=None):
        return {"generated_at": "2026-01-01T00:00:00Z", "delta_ev_gbp": 42.0}

    monkeypatch.setattr(rfb, "run_frozen_baseline", fake_baseline)
    result = rfb.generate(path=path, force=True)
    assert result["delta_ev_gbp"] == 42.0
    assert json.loads(path.read_text())["delta_ev_gbp"] == 42.0


def test_generate_skips_when_refresh_lock_already_held(tmp_path, monkeypatch):
    """A second refresh must NOT stack a second multi-minute decade replay
    behind an in-flight one -- it takes the held lock as 'already running' and
    returns None without calling run_frozen_baseline. This is the single-writer
    guarantee the out-of-band publish trigger relies on (2026-07-29 wedge)."""
    import fcntl

    lock_path = tmp_path / ".refresh.lock"
    monkeypatch.setattr(rfb, "REFRESH_LOCK_PATH", lock_path)
    path = tmp_path / "baseline.json"

    def should_not_run(report_end=None):
        raise AssertionError("run_frozen_baseline ran while the lock was held")

    monkeypatch.setattr(rfb, "run_frozen_baseline", should_not_run)

    # Hold the lock from an independent fd, exactly as an in-flight refresh would.
    held = open(lock_path, "w")
    fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        assert rfb.generate(path=path, force=True) is None
        assert not path.exists()  # nothing written by the blocked second caller
    finally:
        fcntl.flock(held, fcntl.LOCK_UN)
        held.close()

    # Mutation check: with the lock released, the same call now runs and writes.
    monkeypatch.setattr(rfb, "run_frozen_baseline",
                        lambda report_end=None: {"generated_at": "2026-01-01T00:00:00Z",
                                                 "delta_ev_gbp": 7.0})
    assert rfb.generate(path=path, force=True)["delta_ev_gbp"] == 7.0


# ── Importing this module must not BUILD THE BOOK (2026-08-31 publish wedge) ──────────
# Nine consecutive publish-gate failures, ~6h wedged. `tools/run_frozen_baseline.py` carried
# `from simulation.run_phase4c_on_phase2b import main` at module scope; that import chain
# reaches `simulation/run_phase2b.py`'s module body, which runs `CUSTOMERS = live_population()`,
# which writes `docs/observability/book_growth_campaign.json`. On 2026-08-31 that directory
# became a whole PROTECTED_SURFACE in tests/production_surface_guard.py, so every test that
# merely IMPORTED this module raised ProductionWriteRefused -- and before that commit the write
# had simply been landing on the live evidence base unnoticed.
#
# R15: this is keyed to the PROPERTY (an import has no simulation side effects), not to today's
# error. Restoring the module-level import makes it red whether or not the guard covers the path,
# and it would also have been red for the months when the guard did not.


def test_importing_the_module_does_not_import_the_simulation():
    """A subprocess, because in a full suite run `simulation.run_phase2b` is already in
    `sys.modules` from some other test and an in-process check would pass vacuously."""
    import subprocess
    import sys

    probe = (
        "import sys; import tools.run_frozen_baseline; "
        "print(','.join(sorted(m for m in sys.modules "
        "if m.startswith('simulation.'))))"
    )
    proc = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(rfb.PROJECT_DIR), capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, "the probe itself failed:\n{}".format(proc.stderr)
    leaked = [m for m in proc.stdout.strip().split(",") if m]
    assert leaked == [], (
        "importing tools.run_frozen_baseline pulled in {} -- the replay must be imported "
        "at CALL time, inside run_phase4c(), not at module scope".format(leaked)
    )


def test_the_replay_is_still_reachable_through_the_module_level_seam(monkeypatch):
    """The other half: a lazy import that nothing can reach, or that the arms can no longer be
    faked at, would make the test above pass for the wrong reason."""
    import sys
    import types

    seen = []
    # A STUB MODULE, not `monkeypatch.setattr("simulation.run_phase4c_on_phase2b.main", ...)`:
    # that string form imports the real module to patch it, which is the very import this
    # module was just stopped from doing -- the test would rebuild the book to prove the book
    # is not rebuilt.
    fake = types.ModuleType("simulation.run_phase4c_on_phase2b")
    fake.main = lambda report_end=None, policy=None: (
        seen.append((report_end, policy)) or {"ok": True}
    )
    monkeypatch.setitem(sys.modules, "simulation.run_phase4c_on_phase2b", fake)

    assert rfb.run_phase4c(report_end="2020-01-01", policy=None) == {"ok": True}
    assert seen == [("2020-01-01", None)]
