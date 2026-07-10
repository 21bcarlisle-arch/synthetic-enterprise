"""Tests for tools/generate_dashboard_data.py pure extraction helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from tools.generate_dashboard_data import (
    _fmt, extract_portfolio, extract_financial, count_run_history_total,
    extract_regulatory, _SLC_OBLIGATIONS, extract_reputation, extract_opex_ledger,
)
import json


def test_fmt_rounds_float():
    assert _fmt(3.14159) == 3.14


def test_fmt_none_returns_zero():
    assert _fmt(None) == 0.0


def test_fmt_integer():
    assert _fmt(100) == 100.0


def _portfolio_data(**overrides):
    base = {
        "_ledger_headline": {"net_margin_gbp": 500_000.0, "gross_margin_gbp": 600_000.0},
        "total_net_gbp": 480_000.0,
        "total_gross_gbp": 590_000.0,
        "enterprise_value_gbp": 1_000_000.0,
        "starting_treasury_gbp": 200_000.0,
        "final_treasury_gbp": 300_000.0,
        "bills_total": 1500,
        "committee_wake_ups_total": 5,
        "retention_log": [{"outcome": "retained"}, {"outcome": "churned"}],
        "churned_billing_accounts": ["C5", "C6"],
    }
    base.update(overrides)
    return base


def test_extract_portfolio_keys():
    r = extract_portfolio(_portfolio_data())
    for key in ("net_margin_gbp", "gross_margin_gbp", "enterprise_value_gbp",
                "treasury_start_gbp", "treasury_end_gbp", "bills_total",
                "committee_interventions_total", "retention_offers", "retention_retained",
                "churn_count"):
        assert key in r


def test_extract_portfolio_uses_total_net_over_ledger():
    r = extract_portfolio(_portfolio_data())
    assert r["net_margin_gbp"] == 480_000.0


def test_extract_portfolio_retention_retained():
    r = extract_portfolio(_portfolio_data())
    assert r["retention_retained"] == 1


def test_extract_portfolio_churn_count():
    r = extract_portfolio(_portfolio_data())
    assert r["churn_count"] == 2


def _financial_data():
    return {
        "years": {
            "2022": {
                "revenue_gbp": 1_000_000.0,
                "gross_gbp": 200_000.0,
                "capital_gbp": 50_000.0,
                "net_gbp": 150_000.0,
                "treasury_end_gbp": 300_000.0,
                "policy_cost_gbp": 30_000.0,
                "bad_debt_gbp": 5_000.0,
                "bills_count": 100,
                "avg_bill_shock_pct": 5.2,
                "commodity_split": {
                    "electricity": {"gross_gbp": 120_000.0, "net_gbp": 90_000.0},
                    "gas": {"gross_gbp": 80_000.0, "net_gbp": 60_000.0},
                },
                "segment_split": {},
            }
        },
        "ledger_pnl": {},
    }


def test_extract_financial_annual_length():
    r = extract_financial(_financial_data())
    assert len(r["annual"]) == 1


def test_extract_financial_year_value():
    r = extract_financial(_financial_data())
    assert r["annual"][0]["year"] == 2022


def test_extract_financial_annual_keys():
    r = extract_financial(_financial_data())
    row = r["annual"][0]
    for key in ("year", "revenue_gbp", "gross_gbp", "net_gbp", "treasury_end_gbp",
                "bills_count", "elec_gross_gbp", "gas_net_gbp"):
        assert key in row


def test_extract_financial_empty_years():
    r = extract_financial({"years": {}, "ledger_pnl": {}})
    assert r["annual"] == []


# --- total_revenue_gbp / net_margin_pct denominator fix (2026-07-10,
# MARGIN_REALISM.md Step 1 gauge fix: years[yr].revenue_gbp is
# commodity-only, inflating any margin % computed against it -- total
# revenue from management_accounts is the real denominator) ---

def _financial_data_with_mgmt_accounts():
    data = _financial_data()
    data["management_accounts"] = {
        "2022": {"income_statement": {"revenue_gbp": 1000.0}},
    }
    data["years"]["2022"]["net_gbp"] = 150.0
    return data


def test_extract_financial_annual_has_total_revenue_field():
    r = extract_financial(_financial_data_with_mgmt_accounts())
    assert r["annual"][0]["total_revenue_gbp"] == 1000.0


def test_extract_financial_net_margin_pct_uses_total_revenue():
    r = extract_financial(_financial_data_with_mgmt_accounts())
    assert r["annual"][0]["net_margin_pct"] == 15.0


def test_extract_financial_total_revenue_none_when_no_management_accounts():
    r = extract_financial(_financial_data())
    assert r["annual"][0]["total_revenue_gbp"] is None
    assert r["annual"][0]["net_margin_pct"] == 0.0


# --- segment_annual revenue + net_margin_pct (2026-07-10, PRIORITIES.md
# "Segmented financials" backlog item, director page comments x2) ---

def _financial_data_with_segments():
    data = _financial_data()
    data["years"]["2022"]["segment_split"] = {
        "resi electricity": {
            "revenue_gbp": 500_000.0, "gross_gbp": 120_000.0,
            "capital_gbp": 20_000.0, "net_gbp": 100_000.0,
        },
        "sme electricity": {
            "revenue_gbp": 0.0, "gross_gbp": 0.0,
            "capital_gbp": 0.0, "net_gbp": 0.0,
        },
    }
    return data


def test_extract_financial_segment_annual_has_revenue_field():
    r = extract_financial(_financial_data_with_segments())
    row = r["segment_annual"][0]
    assert row["resi_electricity"]["revenue_gbp"] == 500_000.0


def test_extract_financial_segment_annual_net_margin_pct():
    r = extract_financial(_financial_data_with_segments())
    row = r["segment_annual"][0]
    assert row["resi_electricity"]["net_margin_pct"] == 20.0


def test_extract_financial_segment_annual_zero_revenue_no_division_error():
    r = extract_financial(_financial_data_with_segments())
    row = r["segment_annual"][0]
    assert row["sme electricity".replace(" ", "_")]["net_margin_pct"] == 0.0


def test_extract_financial_segments_list_sorted():
    r = extract_financial(_financial_data_with_segments())
    assert r["segments"] == ["resi electricity", "sme electricity"]


def test_extract_financial_segments_list_empty_when_no_segments():
    r = extract_financial(_financial_data())
    assert r["segments"] == []


def test_fmt_negative_value():
    assert _fmt(-5.5) == -5.5


def test_extract_portfolio_returns_dict():
    r = extract_portfolio(_portfolio_data())
    assert isinstance(r, dict)


def test_extract_financial_annual_is_list():
    r = extract_financial(_financial_data())
    assert isinstance(r["annual"], list)


def test_count_run_history_total_missing_file_returns_zero(tmp_path):
    assert count_run_history_total(tmp_path / "nonexistent.json") == 0


def test_count_run_history_total_counts_full_history_not_truncated(tmp_path):
    """Regression (PROJECT_TAB_OVERHAUL.md): the Project tab's "Sim runs" KPI
    used to read len() of the already-truncated last-10-entries list, so it
    always displayed exactly 10 no matter how many runs had really happened
    -- a dead counter. count_run_history_total() must read the full file."""
    history_path = tmp_path / "run_history.json"
    history_path.write_text(json.dumps([{"git_hash": "abc%d" % i} for i in range(37)]))
    assert count_run_history_total(history_path) == 37


def test_count_run_history_total_invalid_json_returns_zero(tmp_path):
    history_path = tmp_path / "run_history.json"
    history_path.write_text("not valid json")
    assert count_run_history_total(history_path) == 0


def _regulatory_data(**year_overrides):
    year_2024 = {
        "revenue_gbp": 1_000_000.0,
        "bad_debt_gbp": 5_000.0,
        "avg_clarity": 0.85,
        "avg_complaint_probability": 0.005,
        "bsc_credit_required_gbp": 1_000.0,
        "treasury_end_gbp": 500_000.0,
    }
    year_2024.update(year_overrides)
    return {
        "years": {"2024": year_2024},
        "management_accounts": {"2024": {"balance_sheet": {"total_equity_gbp": 1.0}}},
        "fra_ratio_series": [{"year": 2024, "fra_ratio": 5.0}],
        "demand_estimation_log": [],
    }


def test_extract_regulatory_no_years_returns_all_green():
    r = extract_regulatory({"years": {}})
    assert r["latest_year"] is None
    assert r["overall_rag"] == "GREEN"
    assert all(o["status"] == "GREEN" for o in r["obligations"])


def test_extract_regulatory_obligation_count():
    r = extract_regulatory(_regulatory_data())
    assert len(r["obligations"]) == len(_SLC_OBLIGATIONS)


def test_extract_regulatory_latest_year():
    r = extract_regulatory(_regulatory_data())
    assert r["latest_year"] == "2024"


def test_extract_regulatory_billing_amber_on_low_clarity():
    r = extract_regulatory(_regulatory_data(avg_clarity=0.65))
    row = next(o for o in r["obligations"] if o["code"] == "SLC 14")
    assert row["status"] == "AMBER"


def test_extract_regulatory_complaints_red_flows_to_slc25c():
    r = extract_regulatory(_regulatory_data(avg_complaint_probability=0.10))
    row = next(o for o in r["obligations"] if o["code"] == "SLC 25C")
    assert row["status"] == "RED"
    assert r["overall_rag"] == "RED"


def test_extract_regulatory_every_domain_has_an_obligation():
    """Regression: SLC 25C was originally mapped to information_transparency,
    leaving the complaints domain with no obligation row to surface a real RED
    breach (found live: avg_complaint_probability 0.061 -> complaints RED, but
    no row in the table showed it). Every domain capable of going non-GREEN
    must be reachable from at least one obligation row. tariff_price_cap is
    excluded: populate_compliance_scorecard hardcodes it permanently GREEN
    ("I&C supply exempt from SVT cap") and none of the 23 tracked SLC
    obligations is a price-cap clause, so it can never surface a breach."""
    from company.regulatory.compliance_scorecard import ComplianceDomain
    mapped_domains = {domain for _, _, domain in _SLC_OBLIGATIONS}
    all_domains = {d.value for d in ComplianceDomain} - {"tariff_price_cap"}
    assert all_domains <= mapped_domains


def test_extract_risk_tiered_compliance_no_ledger_file_defaults_clean(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)  # no site/state/billing_ledger.json here
    report = gdd.extract_risk_tiered_compliance()
    assert report["held_bill_count"] == 0
    assert report["overall_rag"] == "GREEN"


def test_extract_risk_tiered_compliance_reads_live_held_count(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    ledger_dir = tmp_path / "site" / "state"
    ledger_dir.mkdir(parents=True)
    (ledger_dir / "billing_ledger.json").write_text(json.dumps({"meta": {"held_bill_count": 4}}))
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    report = gdd.extract_risk_tiered_compliance()
    assert report["held_bill_count"] == 4
    assert report["overall_rag"] == "RED"


def test_extract_risk_tiered_compliance_malformed_ledger_defaults_to_zero(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    ledger_dir = tmp_path / "site" / "state"
    ledger_dir.mkdir(parents=True)
    (ledger_dir / "billing_ledger.json").write_text("not valid json")
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    report = gdd.extract_risk_tiered_compliance()
    assert report["held_bill_count"] == 0


def test_load_frozen_baseline_missing_file_returns_empty(tmp_path):
    from tools.generate_dashboard_data import _load_frozen_baseline
    assert _load_frozen_baseline(tmp_path / "missing.json") == {}


def test_load_frozen_baseline_reads_real_file(tmp_path):
    from tools.generate_dashboard_data import _load_frozen_baseline
    path = tmp_path / "frozen_policy_baseline.json"
    path.write_text(json.dumps({"delta_ev_gbp": 1234.5}))
    result = _load_frozen_baseline(path)
    assert result["delta_ev_gbp"] == 1234.5


def test_load_frozen_baseline_invalid_json_returns_empty(tmp_path):
    from tools.generate_dashboard_data import _load_frozen_baseline
    path = tmp_path / "frozen_policy_baseline.json"
    path.write_text("not json")
    assert _load_frozen_baseline(path) == {}


def test_extract_reputation_no_data_returns_empty_shape():
    r = extract_reputation({})
    assert r["nps_annual"] == {}
    assert r["gri_trajectory"] == []
    assert r["latest_nps"] is None
    assert r["latest_gri"] is None
    assert r["total_reputation_events"] == 0


def test_extract_reputation_latest_gri_is_last_trajectory_entry():
    data = {
        "gri_trajectory": [
            {"year": 2016, "gri_score": 50.0, "band": "adequate"},
            {"year": 2017, "gri_score": 49.0, "band": "weak"},
        ],
    }
    r = extract_reputation(data)
    assert r["latest_gri"] == {"year": 2017, "gri_score": 49.0, "band": "weak"}


def test_extract_reputation_latest_nps_skips_years_with_no_responses():
    data = {
        "nps_annual_summaries": {
            "2016": {"year": 2016, "responses": 0, "nps": None},
            "2017": {"year": 2017, "responses": 3, "nps": 10.0},
        },
    }
    r = extract_reputation(data)
    assert r["latest_nps"]["year"] == 2017


def test_extract_reputation_counts_events():
    data = {
        "reputation_events_log": [
            {"customer_id": "C1", "date": "2020-01-01", "event_type": "complaint_resolved_on_time"},
            {"customer_id": "C2", "date": "2020-02-01", "event_type": "complaint_resolved_late"},
        ],
    }
    r = extract_reputation(data)
    assert r["total_reputation_events"] == 2


# -- extract_opex_ledger (MARGIN_REALISM Step 3 / B2) --

def test_extract_opex_ledger_computes_against_real_customers_master_list():
    """Independent of run_output.json's own content -- reads saas.customers.CUSTOMERS
    directly, matching this module's existing pattern for other CUSTOMERS-derived
    figures (extract_customers etc.)."""
    result = extract_opex_ledger({})
    assert result["true_opex_total_gbp"] >= 0.0
    assert result["benchmark_opex_total_gbp"] >= 0.0
    assert result["household_count"] > 0
    assert "note" in result


def test_extract_opex_ledger_investor_thesis_gap_is_positive():
    result = extract_opex_ledger({})
    assert result["investor_thesis_gap_gbp"] == pytest.approx(
        result["benchmark_opex_total_gbp"] - result["true_opex_total_gbp"]
    )
    assert result["investor_thesis_gap_gbp"] > 0


def test_extract_opex_ledger_ai_compute_not_yet_populated():
    """Real, unresolved open design questions -- must stay 0.0, never silently
    fabricated (R12)."""
    result = extract_opex_ledger({})
    assert result["true_ai_compute_cost_gbp"] == 0.0
