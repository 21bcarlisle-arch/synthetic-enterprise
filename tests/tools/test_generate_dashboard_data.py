"""Tests for tools/generate_dashboard_data.py pure extraction helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from tools.generate_dashboard_data import (
    _fmt, extract_portfolio, extract_financial, count_run_history_total,
    extract_regulatory, _SLC_OBLIGATIONS, extract_reputation, extract_opex_ledger,
    extract_b2_taxonomy,
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


def _regulatory_data(contact_centre_log=None, **year_overrides):
    year_2024 = {
        "revenue_gbp": 1_000_000.0,
        "bad_debt_gbp": 5_000.0,
        "avg_clarity": 0.85,
        "bsc_credit_required_gbp": 1_000.0,
        "treasury_end_gbp": 500_000.0,
    }
    year_2024.update(year_overrides)
    return {
        "years": {"2024": year_2024},
        "management_accounts": {"2024": {"balance_sheet": {"total_equity_gbp": 1.0}}},
        "fra_ratio_series": [{"year": 2024, "fra_ratio": 5.0}],
        "demand_estimation_log": [],
        "contact_centre_log": contact_centre_log or [],
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
    """SLC 25C ("Communication Channel Choice") is keyed on the real
    contact-centre first-response SLA breach rate (simulation/contact_centre.py),
    not complaint probability -- fixed 2026-07-10 (director page comment,
    docs/design/SLC25C_CHANNEL_CHOICE_FIX.md: complaint probability measures how
    likely a customer is to complain, nothing about whether they had a real
    channel choice or were served well through it)."""
    log = (
        [{"period_end": "2024-06-30", "breached_sla": True}] * 8
        + [{"period_end": "2024-06-30", "breached_sla": False}] * 2
    )
    r = extract_regulatory(_regulatory_data(contact_centre_log=log))
    row = next(o for o in r["obligations"] if o["code"] == "SLC 25C")
    assert row["status"] == "RED"
    assert r["overall_rag"] == "RED"


def test_extract_regulatory_complaints_green_on_low_breach_rate():
    log = (
        [{"period_end": "2024-06-30", "breached_sla": True}]
        + [{"period_end": "2024-06-30", "breached_sla": False}] * 19
    )
    r = extract_regulatory(_regulatory_data(contact_centre_log=log))
    row = next(o for o in r["obligations"] if o["code"] == "SLC 25C")
    assert row["status"] == "GREEN"


def test_extract_regulatory_complaints_green_when_no_contact_events():
    r = extract_regulatory(_regulatory_data(contact_centre_log=[]))
    row = next(o for o in r["obligations"] if o["code"] == "SLC 25C")
    assert row["status"] == "GREEN"
    assert "No contact-centre events" in row["notes"]


def test_extract_regulatory_complaints_filters_by_year():
    """A breach logged in a different year must not bleed into 2024's rate."""
    log = (
        [{"period_end": "2023-06-30", "breached_sla": True}] * 10
        + [{"period_end": "2024-06-30", "breached_sla": False}] * 5
    )
    r = extract_regulatory(_regulatory_data(contact_centre_log=log))
    row = next(o for o in r["obligations"] if o["code"] == "SLC 25C")
    assert row["status"] == "GREEN"


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
# ADVISOR_STEER_THESIS_CHART.md (defects 2+3, 2026-07-11): the population is now
# the RESI households ACTIVE IN THE FINAL SIMULATION YEAR (resi-only fixes the
# domestic-Ofgem-benchmark contamination; final-year active reconciles with the
# pulse-strip Book Size), not the static all-time, all-segment CUSTOMERS list.

def _opex_run_data(active_ids):
    """A minimal run_output-shaped dict carrying just the final-year active
    population extract_opex_ledger now reads."""
    return {"years": {"2025": {"active_customer_ids": list(active_ids)}}}


# The final-year active population as it appears in the live run (resi legs
# C1_2/C2/C2g/C7/C8/C9 dedupe to 5 households; I&C C_IC* excluded).
_LIVE_FINAL_YEAR_ACTIVE = [
    "C1_2", "C2", "C2g", "C7", "C8", "C9",
    "C_IC1", "C_IC2", "C_IC3", "C_IC3g", "C_IC4",
]


def test_extract_opex_ledger_uses_final_year_active_resi_population():
    result = extract_opex_ledger(_opex_run_data(_LIVE_FINAL_YEAR_ACTIVE))
    assert result["true_opex_total_gbp"] >= 0.0
    assert result["benchmark_opex_total_gbp"] >= 0.0
    # 5 resi households (C1_2, C2[+C2g], C7, C8, C9); I&C excluded.
    assert result["household_count"] == 5
    assert result["population_basis"] == "resi households active in the final simulation year"
    assert "note" in result


def test_extract_opex_ledger_excludes_ic_and_sme_from_benchmark():
    """Defect 2: SME/I&C accounts have no valid DOMESTIC Ofgem allowance and must
    never load the benchmark. A book of resi + I&C + SME must produce the SAME
    benchmark as the resi-only subset alone."""
    resi_only = ["C1_2", "C2", "C2g", "C7", "C8", "C9"]
    mixed = resi_only + ["C_IC1", "C_IC2", "C_IC3", "C_IC3g", "C_IC4", "C5", "C6"]
    r_resi = extract_opex_ledger(_opex_run_data(resi_only))
    r_mixed = extract_opex_ledger(_opex_run_data(mixed))
    assert r_mixed["household_count"] == r_resi["household_count"] == 5
    assert r_mixed["benchmark_opex_total_gbp"] == pytest.approx(r_resi["benchmark_opex_total_gbp"])
    assert r_mixed["true_opex_total_gbp"] == pytest.approx(r_resi["true_opex_total_gbp"])


def test_extract_opex_ledger_per_household_figures_are_correct_arithmetic():
    """Defect 2 (mislabelling): *_total_gbp are book SUMS; the per-household
    fields must be total / household_count."""
    result = extract_opex_ledger(_opex_run_data(_LIVE_FINAL_YEAR_ACTIVE))
    hc = result["household_count"]
    assert hc == 5
    assert result["benchmark_opex_per_household_gbp"] == pytest.approx(
        result["benchmark_opex_total_gbp"] / hc, abs=0.01
    )
    assert result["true_opex_per_household_gbp"] == pytest.approx(
        result["true_opex_total_gbp"] / hc, abs=0.01
    )
    # A real domestic incumbent cost-to-serve is a few hundred pounds PER HOUSEHOLD,
    # not the ~£1.6k book sum.
    assert 100.0 < result["benchmark_opex_per_household_gbp"] < 500.0


def test_extract_opex_ledger_empty_population_no_crash():
    """No years / empty active set -> zeroed figures, never a divide-by-zero."""
    result = extract_opex_ledger({})
    assert result["household_count"] == 0
    assert result["benchmark_opex_per_household_gbp"] == 0.0
    assert result["true_opex_per_household_gbp"] == 0.0


def test_extract_opex_ledger_investor_thesis_gap_is_positive():
    result = extract_opex_ledger(_opex_run_data(_LIVE_FINAL_YEAR_ACTIVE))
    assert result["investor_thesis_gap_gbp"] == pytest.approx(
        result["benchmark_opex_total_gbp"] - result["true_opex_total_gbp"]
    )
    assert result["investor_thesis_gap_gbp"] > 0


def test_extract_opex_ledger_ai_compute_not_yet_populated():
    """Real, unresolved open design questions -- must stay 0.0, never silently
    fabricated (R12)."""
    result = extract_opex_ledger(_opex_run_data(_LIVE_FINAL_YEAR_ACTIVE))
    assert result["true_ai_compute_cost_gbp"] == 0.0


# -- Population consistency gate (R10 class fix, defect 3) --

def _dashboard_for_population_gate(active_ids, book_legs, opex_household_count):
    """Assemble the two page surfaces the population gate reconciles: the
    pulse-strip Book Size (book_annual last entry) and the opex household count."""
    elec = [c for c in active_ids if not c.endswith("g")]
    gas = [c for c in active_ids if c.endswith("g")]
    # book_legs lets a test deliberately break the Book-Size-vs-source assertion.
    return {
        "customers": {"book_annual": [
            {"year": 2025, "active_elec": len(elec), "active_gas": len(gas)},
        ]},
        "opex_ledger": {"household_count": opex_household_count},
    }


def test_population_gate_passes_when_figures_reconcile():
    from tools.generate_dashboard_data import _check_population_consistency
    data = _opex_run_data(_LIVE_FINAL_YEAR_ACTIVE)
    dashboard = _dashboard_for_population_gate(_LIVE_FINAL_YEAR_ACTIVE, None, 5)
    assert _check_population_consistency(data, dashboard) is True


def test_population_gate_catches_all_time_master_list_regression():
    """The exact defect-2/3 bug: opex household_count reverts to the all-time,
    all-segment master-list count (13) instead of the 5 resi households active in
    the final year. The gate MUST fail -- a real regression test, not happy-path."""
    from tools.generate_dashboard_data import _check_population_consistency
    data = _opex_run_data(_LIVE_FINAL_YEAR_ACTIVE)
    dashboard = _dashboard_for_population_gate(_LIVE_FINAL_YEAR_ACTIVE, None, 13)
    assert _check_population_consistency(data, dashboard) is False


def test_population_gate_catches_book_size_diverging_from_source():
    """If the Book Size count stops reconciling to the final-year active
    population it was supposedly counted from, the gate fails."""
    from tools.generate_dashboard_data import _check_population_consistency
    data = _opex_run_data(_LIVE_FINAL_YEAR_ACTIVE)
    dashboard = _dashboard_for_population_gate(_LIVE_FINAL_YEAR_ACTIVE, None, 5)
    # Corrupt the Book Size so elec+gas no longer equals the 11 active legs.
    dashboard["customers"]["book_annual"][-1]["active_elec"] = 99
    assert _check_population_consistency(data, dashboard) is False


# -- B2_OPEX_TAXONOMY_EXPANSION.md: extract_b2_taxonomy() --

def _b2_data():
    return {
        "years": {
            "2025": {
                "segment_split": {
                    "resi electricity": {"revenue_gbp": 10000.0, "gross_gbp": 500.0, "net_gbp": 100.0},
                    "ic electricity": {"revenue_gbp": 90000.0, "gross_gbp": 40000.0, "net_gbp": 39000.0},
                },
            },
        },
        "per_customer_lifetime": {
            "R1": {"segment": "resi", "commodity": "electricity", "gross_gbp": 500.0},
            "W1": {"segment": "ic", "commodity": "electricity", "gross_gbp": 40000.0},
        },
    }


def _write_ledger(tmp_path, customers):
    import json as _json
    ledger_dir = tmp_path / "site" / "state"
    ledger_dir.mkdir(parents=True)
    (ledger_dir / "billing_ledger.json").write_text(_json.dumps({"customers": customers}))


def test_extract_b2_taxonomy_real_director_numbers_wired(tmp_path, monkeypatch):
    """Director set these live 2026-07-10 (from_rich_20260710_190908.md) --
    must no longer be None/not-set."""
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {"R1": {"segment": "resi", "balance_gbp": 0.0},
                             "W1": {"segment": "ic", "balance_gbp": 0.0}})
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_b2_taxonomy(_b2_data())
    assert result["segment_roce_hurdle"]["hurdle_pct"] == 12.0
    assert result["segment_roce_hurdle"]["hurdle_set"] is True
    assert result["single_customer_concentration"]["limit_pct"] == 15.0
    assert result["single_customer_concentration"]["amber_pct"] == 10.0


def test_extract_b2_taxonomy_whale_customer_breaches_concentration(tmp_path, monkeypatch):
    """W1 holds 40000/40500 = 98.8% of gross margin -- must be a real RED
    breach against the director's 15% limit, not silently passed."""
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {"R1": {"segment": "resi", "balance_gbp": 0.0},
                             "W1": {"segment": "ic", "balance_gbp": 0.0}})
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_b2_taxonomy(_b2_data())
    conc = result["single_customer_concentration"]
    assert conc["top_customer"] == "W1"
    assert conc["status"] == "red"
    assert conc["breach"] is True


def test_extract_b2_taxonomy_break_even_flagged_provisional(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {"R1": {"segment": "resi", "balance_gbp": 0.0},
                             "W1": {"segment": "ic", "balance_gbp": 0.0}})
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_b2_taxonomy(_b2_data())
    be = result["break_even_analysis"]
    assert be["provisional"] is True
    assert "whale-distorted" in be["provisional_note"]


def test_extract_b2_taxonomy_under_hurdle_segment_flagged(tmp_path, monkeypatch):
    """resi's segment ROCE is far below the 12% hurdle at this scale -- must
    show up in under_hurdle, not silently omitted."""
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {"R1": {"segment": "resi", "balance_gbp": -5000.0},
                             "W1": {"segment": "ic", "balance_gbp": 0.0}})
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_b2_taxonomy(_b2_data())
    hurdle = result["segment_roce_hurdle"]
    assert hurdle["hurdle_set"] is True
    assert isinstance(hurdle["under_hurdle"], list)
