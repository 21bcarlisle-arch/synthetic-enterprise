"""Tests for Phase 10b segment portfolio annual report generator."""

import pytest

from saas.reporting.segment_report import (
    _headcount_table,
    _per_segment_pnl_table,
    extract_segment_data,
    generate_segment_report,
)


def _rec(sid, commodity, date_str, period, margin, capital, net, treasury, revenue=None):
    return {
        "customer_id": sid,
        "settlement_date": date_str,
        "settlement_period": period,
        "commodity": commodity,
        "margin_gbp": margin,
        "capital_cost_gbp": capital,
        "net_margin_gbp": net,
        "treasury_cash_balance_gbp": treasury,
        "revenue_gbp": revenue if revenue is not None else margin + 80.0,
        "unit_rate_gbp_per_mwh": 50.0,
        "data_regime": "historical",
        "segment_headcount": 150,
    }


def _run_output():
    """Minimal run_segments output fixture covering 2016–2017."""
    all_records = [
        _rec("resi_standard", "electricity", "2016-01-01", 1, 100.0, 15.0, 85.0, 508_385.0),
        _rec("resi_standard", "electricity", "2016-06-01", 2, 120.0, 18.0, 102.0, 508_487.0),
        _rec("resi_smart", "electricity", "2016-02-01", 1, 20.0, 3.0, 17.0, 508_504.0),
        _rec("sme_standard", "electricity", "2016-03-01", 1, 200.0, 30.0, 170.0, 508_674.0),
        _rec("sme_smart", "electricity", "2016-04-01", 1, 30.0, 5.0, 25.0, 508_699.0),
        _rec("gas_resi", "gas", "2016-05-01", 1, 50.0, 8.0, 42.0, 508_741.0),
        # 2017 records
        _rec("resi_standard", "electricity", "2017-01-01", 1, 90.0, 14.0, 76.0, 508_817.0),
        _rec("gas_resi", "gas", "2017-03-01", 1, 45.0, 7.0, 38.0, 508_855.0),
    ]

    return {
        "all_records": all_records,
        "administration_event": None,
        "committee_wake_ups": [
            {
                "settlement_date": "2016-08-13",
                "treasury_gbp": 508_700.0,
                "portfolio_var_current_gbp": 5000.0,
                "portfolio_var_stressed_gbp": 8000.0,
                "adjustments": {"resi_standard": 0.95},
            }
        ],
        "hedge_evolution": {
            "resi_standard": [
                {"term_start": "2016-01-01", "term_end": "2017-01-01",
                 "commodity": "electricity", "hf_used": 0.85,
                 "actual_net": 102.0, "naked_net": 88.0, "next_hf": 0.87, "headcount": 150},
            ],
            "resi_smart": [
                {"term_start": "2016-01-01", "term_end": "2017-01-01",
                 "commodity": "electricity", "hf_used": 0.85,
                 "actual_net": 17.0, "naked_net": 14.0, "next_hf": 0.87, "headcount": 20},
            ],
        },
        "headcount_history": [
            {"year": "2016", "headcounts": {
                "resi_standard": 150, "resi_smart": 20, "sme_standard": 40,
                "sme_smart": 5, "gas_resi": 80,
            }},
            {"year": "2017", "headcounts": {
                "resi_standard": 145, "resi_smart": 25, "sme_standard": 39,
                "sme_smart": 6, "gas_resi": 78,
            }},
        ],
        "final_headcounts": {
            "resi_standard": 145, "resi_smart": 25, "sme_standard": 39,
            "sme_smart": 6, "gas_resi": 78,
        },
        "fixed_cost_events": [
            {"timestamp": "2016-01", "amount_gbp": -50.0},
            {"timestamp": "2016-02", "amount_gbp": -50.0},
            {"timestamp": "2017-01", "amount_gbp": -50.0},
        ],
        "starting_treasury": 508_300.0,
        "final_treasury": 508_855.0,
        "total_gross": 655.0,
        "total_capital": 100.0,
        "total_net": 555.0,
        "growth_mandate": "flat",
        "customer_events": [],
        "churned_billing_accounts": [],
        "won_successor_activations": {},
        "acquired_customers": [],
        "acquisition_spend_events": [],
    }


# ---- extract_segment_data ----

def test_extract_returns_years():
    data = extract_segment_data(_run_output())
    assert "2016" in data["years"]
    assert "2017" in data["years"]


def test_extract_yearly_gross():
    data = extract_segment_data(_run_output())
    gross_2016 = data["years"]["2016"]["gross_gbp"]
    assert gross_2016 == pytest.approx(100.0 + 120.0 + 20.0 + 200.0 + 30.0 + 50.0)


def test_extract_per_segment_headcount():
    data = extract_segment_data(_run_output())
    hc = data["years"]["2016"]["per_segment"]["resi_standard"]["headcount"]
    assert hc == 150


def test_extract_per_segment_net():
    data = extract_segment_data(_run_output())
    net = data["years"]["2016"]["per_segment"]["resi_standard"]["net_gbp"]
    assert net == pytest.approx(85.0 + 102.0)


def test_extract_net_per_customer():
    data = extract_segment_data(_run_output())
    npc = data["years"]["2016"]["per_segment"]["resi_standard"]["net_per_customer_gbp"]
    assert npc == pytest.approx((85.0 + 102.0) / 150)


def test_extract_treasury_end():
    data = extract_segment_data(_run_output())
    # Last record in 2016 sorted by date is 2016-06-01 (resi_standard), treasury=508_487.0
    assert data["years"]["2016"]["treasury_end_gbp"] == pytest.approx(508_487.0)


def test_extract_committee_wake_ups():
    data = extract_segment_data(_run_output())
    assert len(data["years"]["2016"]["committee_wake_ups"]) == 1
    assert len(data["years"]["2017"]["committee_wake_ups"]) == 0


def test_extract_hedge_effectiveness():
    data = extract_segment_data(_run_output())
    heff = data["years"]["2016"]["hedge_effectiveness"]
    assert heff["actual_net_gbp"] == pytest.approx(102.0 + 17.0)
    assert heff["naked_net_gbp"] == pytest.approx(88.0 + 14.0)
    assert heff["hedging_value_add_gbp"] == pytest.approx((102.0 - 88.0) + (17.0 - 14.0))


def test_extract_total_gross():
    data = extract_segment_data(_run_output())
    assert data["total_gross_gbp"] == pytest.approx(655.0)


def test_extract_total_fixed_cost():
    data = extract_segment_data(_run_output())
    assert data["total_fixed_cost_gbp"] == pytest.approx(150.0)


def test_extract_initial_headcounts():
    data = extract_segment_data(_run_output())
    assert data["initial_headcounts"]["resi_standard"] == 150
    assert data["initial_headcounts"]["gas_resi"] == 80


def test_extract_final_headcounts():
    data = extract_segment_data(_run_output())
    assert data["final_headcounts"]["resi_standard"] == 145
    assert data["final_headcounts"]["resi_smart"] == 25


def test_extract_per_segment_lifetime_gross():
    data = extract_segment_data(_run_output())
    psl = data["per_segment_lifetime"]["resi_standard"]
    assert psl["gross_gbp"] == pytest.approx(100.0 + 120.0 + 90.0)


def test_extract_per_segment_lifetime_headcounts():
    data = extract_segment_data(_run_output())
    psl = data["per_segment_lifetime"]["resi_standard"]
    assert psl["initial_headcount"] == 150
    assert psl["final_headcount"] == 145


def test_extract_total_headcount_per_year():
    data = extract_segment_data(_run_output())
    # 2016: 150+20+40+5+80=295, 2017: 145+25+39+6+78=293
    assert data["years"]["2016"]["total_headcount"] == 295
    assert data["years"]["2017"]["total_headcount"] == 293


def test_extract_no_administration():
    data = extract_segment_data(_run_output())
    assert data["administration_event"] is None


def test_extract_administration_propagated():
    ro = _run_output()
    ro["administration_event"] = {"date": "2022-06-01", "segment_id": "resi_standard",
                                  "treasury_balance_gbp": -100.0, "commodity": "electricity"}
    data = extract_segment_data(ro)
    assert data["administration_event"] is not None
    assert data["administration_event"]["date"] == "2022-06-01"


# ---- generate_segment_report ----

def test_generate_report_is_string():
    data = extract_segment_data(_run_output())
    report = generate_segment_report(data)
    assert isinstance(report, str)
    assert len(report) > 200


def test_generate_report_has_executive_summary():
    data = extract_segment_data(_run_output())
    report = generate_segment_report(data)
    assert "Executive Summary" in report


def test_generate_report_has_headcount_table():
    data = extract_segment_data(_run_output())
    report = generate_segment_report(data)
    assert "Headcount Trajectory" in report
    assert "2016" in report


def test_generate_report_has_year_sections():
    data = extract_segment_data(_run_output())
    report = generate_segment_report(data)
    assert "### 2016" in report
    assert "### 2017" in report


def test_generate_report_end_year_truncation():
    data = extract_segment_data(_run_output())
    report = generate_segment_report(data, end_year="2016")
    assert "### 2016" in report
    assert "### 2017" not in report


def test_generate_report_crisis_year_flag():
    ro = _run_output()
    ro["all_records"].append(
        _rec("resi_standard", "electricity", "2021-06-01", 1, 80.0, 12.0, 68.0, 509_000.0)
    )
    ro["headcount_history"].append({"year": "2021", "headcounts": {
        "resi_standard": 140, "resi_smart": 28, "sme_standard": 38,
        "sme_smart": 7, "gas_resi": 75,
    }})
    data = extract_segment_data(ro)
    report = generate_segment_report(data)
    assert "crisis year" in report


def test_generate_report_administration_noted():
    ro = _run_output()
    ro["administration_event"] = {"date": "2022-06-01", "segment_id": "resi_standard",
                                  "treasury_balance_gbp": -100.0, "commodity": "electricity"}
    data = extract_segment_data(ro)
    report = generate_segment_report(data)
    assert "ADMINISTRATION" in report


# ---- table helpers ----

def test_headcount_table_has_all_segments():
    data = extract_segment_data(_run_output())
    table = _headcount_table(data)
    assert "Resi Standard" in table
    assert "Resi Gas" in table
    assert "Portfolio" in table


def test_per_segment_pnl_table_has_net():
    data = extract_segment_data(_run_output())
    table = _per_segment_pnl_table(data)
    assert "Net £" in table
    assert "resi_standard" not in table  # should use label, not raw id
    assert "Resi Standard" in table
