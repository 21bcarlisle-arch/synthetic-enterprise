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

    def fake_baseline(report_end=None):
        return {"generated_at": "2026-01-01T00:00:00Z", "delta_ev_gbp": 42.0}

    monkeypatch.setattr(rfb, "run_frozen_baseline", fake_baseline)
    result = rfb.generate(path=path, force=True)
    assert result["delta_ev_gbp"] == 42.0
    assert json.loads(path.read_text())["delta_ev_gbp"] == 42.0
