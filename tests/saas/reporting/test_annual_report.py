from saas.reporting.annual_report import (
    NOT_AVAILABLE,
    _mandate_comparison_section,
    extract_report_data,
    generate_annual_report,
)


def _record(cid, commodity, settlement_date, period, margin, capital, net, rate, treasury):
    return {
        "customer_id": cid,
        "settlement_date": settlement_date,
        "settlement_period": period,
        "consumption_kwh": 10.0,
        "unit_rate_gbp_per_mwh": rate,
        "revenue_gbp": margin + 100.0,
        "wholesale_cost_gbp": 100.0,
        "margin_gbp": margin,
        "capital_cost_gbp": capital,
        "net_margin_gbp": net,
        "commodity": commodity,
        "data_regime": "historical",
        "treasury_cash_balance_gbp": treasury,
    }


def _run_output():
    all_records = [
        _record("C1", "electricity", "2016-01-01", 1, 10.0, 2.0, 8.0, 50.0, 1008.0),
        _record("C1", "electricity", "2016-06-01", 1, 12.0, 3.0, 9.0, 52.0, 1017.0),
        _record("C1g", "gas", "2016-03-01", 1, 5.0, 1.0, 4.0, 30.0, 1021.0),
        _record("C1", "electricity", "2017-01-01", 1, -5.0, 1.0, -6.0, 60.0, 1015.0),
    ]

    phase2b = {
        "all_records": all_records,
        "administration_event": None,
        "committee_wake_ups": [
            {"settlement_date": "2017-01-01", "treasury_gbp": 1015.0, "adjustments": {"C1": 0.8}},
        ],
        "hedge_evolution": {
            "C1": [
                {
                    "term_index": 0,
                    "term_start": "2016-01-01",
                    "commodity": "electricity",
                    "hf_used": 0.5,
                    "actual_net": 8.0,
                    "naked_net": 6.0,
                    "next_hf": 0.6,
                },
                {
                    "term_index": 1,
                    "term_start": "2016-06-01",
                    "commodity": "electricity",
                    "hf_used": 0.6,
                    "actual_net": 9.0,
                    "naked_net": 7.0,
                    "next_hf": 0.7,
                },
            ],
        },
        "total_gross": 22.0,
        "total_capital": 7.0,
        "total_net": 15.0,
        "final_treasury": 1015.0,
        "starting_treasury": 1000.0,
    }

    bills = [
        {
            "customer_id": "C1",
            "period_start": "2016-01-01",
            "period_end": "2016-06-30",
            "total_consumption_kwh": 10.0,
            "total_amount_gbp": 110.0,
            "average_unit_rate_gbp_per_mwh": 51.0,
            "clarity_score": 0.8,
            "bill_shock_pct": None,
        },
        {
            "customer_id": "C1",
            "period_start": "2016-07-01",
            "period_end": "2017-01-31",
            "total_consumption_kwh": 10.0,
            "total_amount_gbp": 160.0,
            "average_unit_rate_gbp_per_mwh": 60.0,
            "clarity_score": 0.6,
            "bill_shock_pct": 0.25,
        },
    ]

    payment_behaviour = {
        "C1": [
            {
                "customer_id": "C1",
                "period_end": "2016-06-30",
                "total_amount_gbp": 110.0,
                "credit_risk": "low",
                "bad_debt_provision_gbp": 1.0,
                "expected_payment_date": "2016-07-15",
                "is_vulnerable": False,
            },
            {
                "customer_id": "C1",
                "period_end": "2017-01-31",
                "total_amount_gbp": 160.0,
                "credit_risk": "medium",
                "bad_debt_provision_gbp": 4.0,
                "expected_payment_date": "2017-02-15",
                "is_vulnerable": False,
            },
        ],
    }

    contact_model = {
        "by_customer": {
            "C1": [
                {
                    "customer_id": "C1",
                    "period_end": "2016-06-30",
                    "contact_probability": 0.1,
                    "complaint_probability": 0.05,
                },
                {
                    "customer_id": "C1",
                    "period_end": "2017-01-31",
                    "contact_probability": 0.3,
                    "complaint_probability": 0.2,
                },
            ],
        },
        "portfolio": {"avg_complaint_probability": 0.125, "service_quality_score": 0.95},
    }

    return {
        "phase2b": phase2b,
        "bills": bills,
        "payment_behaviour": payment_behaviour,
        "contact_model": contact_model,
    }


def test_extract_report_data_splits_by_year():
    data = extract_report_data(_run_output())

    assert set(data["years"]) == {"2016", "2017"}

    y2016 = data["years"]["2016"]
    assert y2016["gross_gbp"] == 27.0
    assert y2016["net_gbp"] == 21.0
    assert y2016["commodity_split"]["electricity"]["net_gbp"] == 17.0
    assert y2016["commodity_split"]["gas"]["net_gbp"] == 4.0
    # Picked from the chronologically latest record (2016-06-01), not list order
    assert y2016["treasury_end_gbp"] == 1017.0
    # All 10 real customers have a 2016 acquisition_date
    assert y2016["acquisitions"] == ["C1", "C1g", "C2", "C2g", "C3", "C3g", "C4", "C4g", "C5", "C6"]
    assert y2016["hedge_fractions"]["C1"]["start_hf"] == 0.5
    assert y2016["hedge_fractions"]["C1"]["avg_hf"] == 0.55
    assert y2016["committee_wake_ups"] == []
    assert y2016["bill_shock_events"] == []

    y2017 = data["years"]["2017"]
    assert y2017["net_gbp"] == -6.0
    assert y2017["worst_period"]["customer_id"] == "C1"
    assert y2017["worst_period"]["net_margin_gbp"] == -6.0
    assert len(y2017["committee_wake_ups"]) == 1
    assert y2017["committee_wake_ups"][0]["adjustments"] == {"C1": 0.8}
    assert len(y2017["bill_shock_events"]) == 1
    assert y2017["bill_shock_events"][0]["customer_id"] == "C1"
    assert y2017["bad_debt_gbp"] == 4.0

    assert data["total_net_gbp"] == 15.0
    assert data["per_customer_lifetime"]["C1"]["net_gbp"] == 11.0


def test_generate_annual_report_produces_year_sections():
    data = extract_report_data(_run_output())
    report = generate_annual_report(data)

    assert "# Annual Report" in report
    assert "## Executive Summary" in report
    assert "## 2016" in report
    assert "## 2017" in report
    assert "Not available in current run output" in report
    # Net-negative customer flagged in pricing section
    assert "net-negative" in report
    # Phase 5c hedging mandate before/after comparison
    assert "## Hedging Mandate — Before/After Phase 5c" in report


def test_mandate_comparison_section_reports_not_available_without_old_data():
    data = extract_report_data(_run_output())
    section = _mandate_comparison_section(data, None)

    assert "## Hedging Mandate — Before/After Phase 5c" in section
    assert NOT_AVAILABLE in section


def test_mandate_comparison_section_compares_capital_ratio_and_2021_margin():
    data = extract_report_data(_run_output())
    old_data = extract_report_data(_run_output())
    # Simulate the old reactive model having a higher capital cost ratio
    old_data["total_capital_gbp"] = old_data["total_gross_gbp"] * 0.5

    section = _mandate_comparison_section(data, old_data)

    assert "Capital cost as % of gross margin" in section
    assert "2021 net margin" in section
    assert "Whole-run net margin, three ways" in section
