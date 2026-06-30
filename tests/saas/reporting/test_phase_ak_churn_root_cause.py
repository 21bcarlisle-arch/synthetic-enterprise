"""Phase AK: Churn Root Cause Attribution section tests."""
import pytest
from saas.reporting.annual_report import _section_churn_root_cause


def _ce(cid, event_date, event_type="churned"):
    return {
        "customer_id": cid,
        "event_date": event_date,
        "commodity": "electricity",
        "event_type": event_type,
        "churn_probability": 0.32,
        "win_probability": 0.55,
        "effective_retention_probability": 0.87,
        "random_roll": 0.5,
        "home_move_won": False,
        "company_churn_estimate": 0.04,
        "churn_estimate_error_pct": -0.88,
        "retention_offered": False,
        "is_active_renewal": False,
        "unit_rate_gbp_per_mwh": 250.0,
    }


def _dpl(cid, term_start, rate_before, rate_after, commodity="electricity"):
    return {
        "customer_id": cid,
        "commodity": commodity,
        "term_start": term_start,
        "recent_margin_rates": [0.1],
        "mean_recent_margin_rate": 0.1,
        "portfolio_premium_pct": 0.0,
        "unit_rate_before": rate_before,
        "unit_rate_after": rate_after,
    }


def _cbr(cid, term_start, sim_p, co_est, rate_vs_svt=0.0):
    return {
        "customer_id": cid,
        "term_start": term_start,
        "sim_churn_probability": sim_p,
        "company_churn_estimate": co_est,
        "churn_estimate_error_pct": co_est - sim_p,
        "is_active_renewal": False,
        "unit_rate_gbp_per_mwh": 250.0,
        "svt_rate_gbp_per_mwh": 248.6,
        "rate_vs_svt_pct": rate_vs_svt,
    }


def _pcl(cid, segment="resi", net_margin=3000.0, acq_date="2018-01-01"):
    return {
        "segment": segment,
        "acquisition_date": acq_date,
        "net_margin_after_cost_to_serve_gbp": net_margin,
    }


def _data(ce_entries, dpl_entries=None, cbr_entries=None, pcl_dict=None):
    return {
        "customer_events": ce_entries,
        "dynamic_pricing_log": dpl_entries or [],
        "churn_basis_risk": cbr_entries or [],
        "per_customer_lifetime": pcl_dict or {},
    }


# ── 1. No churned events returns empty string ─────────────────────────────────

def test_no_churned_returns_empty():
    assert _section_churn_root_cause({}) == ""
    assert _section_churn_root_cause({"customer_events": [_ce("C1", "2022-01-01", "renewed")]}) == ""


# ── 2. Header present when churns exist ──────────────────────────────────────

def test_header_present():
    data = _data([_ce("C1", "2022-01-01")])
    result = _section_churn_root_cause(data)
    assert "## Churn Root Cause Attribution" in result


# ── 3. Churned account appears in table ──────────────────────────────────────

def test_churned_account_in_table():
    data = _data([_ce("C5", "2021-12-30")])
    result = _section_churn_root_cause(data)
    assert "C5" in result
    assert "2021-12-30" in result


# ── 4. Rate shock computed and shown ─────────────────────────────────────────

def test_rate_shock_shown():
    data = _data(
        [_ce("C2", "2022-03-31")],
        dpl_entries=[_dpl("C2", "2022-03-31", 300.0, 345.0)],
    )
    result = _section_churn_root_cause(data)
    # 45/300 = +15.0%
    assert "+15.0%" in result


# ── 5. Rate shock: decrease shown as negative ────────────────────────────────

def test_rate_shock_decrease():
    data = _data(
        [_ce("C3", "2020-06-30")],
        dpl_entries=[_dpl("C3", "2020-06-30", 113.4, 108.6)],
    )
    result = _section_churn_root_cause(data)
    assert "-4.2%" in result


# ── 6. Rate vs SVT shown in table ────────────────────────────────────────────

def test_rate_vs_svt_shown():
    data = _data(
        [_ce("C5", "2021-12-30")],
        cbr_entries=[_cbr("C5", "2021-12-30", 0.35, 0.83, rate_vs_svt=63.9)],
    )
    result = _section_churn_root_cause(data)
    assert "63.9" in result


# ── 7. Tenure computed from acquisition date ──────────────────────────────────

def test_tenure_computed():
    data = _data(
        [_ce("C1", "2022-01-01")],
        pcl_dict={"C1": _pcl("C1", acq_date="2016-01-01")},
    )
    result = _section_churn_root_cause(data)
    assert "6.0yr" in result


# ── 8. Lifetime margin shown ──────────────────────────────────────────────────

def test_lifetime_margin_shown():
    data = _data(
        [_ce("C5", "2021-12-30")],
        pcl_dict={"C5": _pcl("C5", net_margin=8498.0)},
    )
    result = _section_churn_root_cause(data)
    assert "8,498" in result


# ── 9. Total margin lost computed ─────────────────────────────────────────────

def test_total_margin_lost():
    data = _data(
        [_ce("C1", "2021-01-01"), _ce("C2", "2022-01-01")],
        pcl_dict={
            "C1": _pcl("C1", net_margin=2000.0),
            "C2": _pcl("C2", net_margin=3000.0),
        },
    )
    result = _section_churn_root_cause(data)
    assert "5,000" in result


# ── 10. Blind miss detected (sim >=30%, co <10%) ──────────────────────────────

def test_blind_miss_detected():
    data = _data(
        [_ce("C4", "2024-09-29")],
        cbr_entries=[_cbr("C4", "2024-09-29", 0.32, 0.00)],
    )
    result = _section_churn_root_cause(data)
    assert "blind miss" in result.lower()
    assert "C4" in result


# ── 11. Company-warned churn detected (co >=20%) ────────────────────────────

def test_company_warned_churn():
    data = _data(
        [_ce("C5", "2021-12-30")],
        cbr_entries=[_cbr("C5", "2021-12-30", 0.35, 0.83)],
    )
    result = _section_churn_root_cause(data)
    assert "warned" in result.lower()


# ── 12. Crisis-era churns flagged (2021-22) ────────────────────────────────

def test_crisis_era_churns_flagged():
    data = _data([
        _ce("C1", "2021-12-30"),
        _ce("C2", "2022-03-31"),
    ])
    result = _section_churn_root_cause(data)
    assert "2021-22" in result or "Crisis" in result or "crisis" in result


# ── 13. Overpriced at departure flagged ──────────────────────────────────────

def test_overpriced_at_departure():
    data = _data(
        [_ce("C5", "2021-12-30")],
        cbr_entries=[_cbr("C5", "2021-12-30", 0.35, 0.83, rate_vs_svt=63.9)],
    )
    result = _section_churn_root_cause(data)
    assert "overpriced" in result.lower() or "SVT" in result


# ── 14. Only renewed events (no churns) returns empty ────────────────────────

def test_only_renewed_events_returns_empty():
    ce = [_ce("C1", "2020-01-01", "renewed"), _ce("C2", "2021-01-01", "renewed")]
    data = _data(ce)
    assert _section_churn_root_cause(data) == ""
