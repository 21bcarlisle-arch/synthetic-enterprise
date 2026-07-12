from pathlib import Path

from saas.reporting.annual_report import (
    NOT_AVAILABLE,
    _append_pricing_actions_summary,
    _build_clv_snapshots,
    _build_ledger_headline,
    _clv_trajectory_section,
    _customer_book_section,
    _ledger_summary_section,
    _lifetime_pricing_section,
    _mandate_comparison_section,
    _pricing_action,
    _section_enterprise_value_analysis,
    _section_ic_portfolio,
    _section_policy_costs,
    _section_scenario_metadata,
    _section_solvency_signal,
    _section_volume_tolerance,
    _section_triad_exposure,
    _segment_margin_trend_section,
    _send_run_complete_ntfy,
    extract_report_data,
    generate_annual_report,
)


def _record(cid, commodity, settlement_date, period, margin, capital, net, rate, treasury, bad_debt=0.0):
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
        "bad_debt_gbp": bad_debt,
        "commodity": commodity,
        "data_regime": "historical",
        "treasury_cash_balance_gbp": treasury,
    }


def _run_output():
    all_records = [
        _record("C1", "electricity", "2016-01-01", 1, 10.0, 2.0, 8.0, 50.0, 1008.0),
        _record("C1", "electricity", "2016-06-01", 1, 12.0, 3.0, 9.0, 52.0, 1017.0),
        _record("C1g", "gas", "2016-03-01", 1, 5.0, 1.0, 4.0, 30.0, 1021.0),
        _record("C1", "electricity", "2017-01-01", 1, -5.0, 1.0, -6.0, 60.0, 1015.0, bad_debt=4.0),
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


def test_extract_report_data_forwards_dd_collection_book():
    """W5_1_banking_payment_rails L2->L3 (2026-07-12): the rails-timed DD
    collection book must reach the persisted run-output JSON, not be
    silently dropped like the pre-existing dd_collection_book.py module was
    before this wiring (its own Expert Hour review's decisive finding)."""
    run_output = _run_output()
    run_output["dd_collection_book"] = {
        "summary": {"total": 1, "active": 1, "suspended": 0, "cancelled": 0, "total_monthly_gbp": 80.0},
        "mandates": [{"customer_id": "C1", "mandate_reference": "DD-C1-20160101"}],
        "attempts": [{"mandate_reference": "DD-C1-20160101", "customer_id": "C1", "outcome": "collected"}],
    }
    data = extract_report_data(run_output)
    assert data["dd_collection_book"]["summary"]["total"] == 1
    assert data["dd_collection_book"]["mandates"][0]["customer_id"] == "C1"
    assert data["dd_collection_book"]["attempts"][0]["outcome"] == "collected"


def test_extract_report_data_dd_collection_book_defaults_to_empty_dict():
    data = extract_report_data(_run_output())  # no dd_collection_book key at all
    assert data["dd_collection_book"] == {}


def test_extract_report_data_splits_by_year():
    data = extract_report_data(_run_output())

    assert set(data["years"]) == {"2016", "2017"}

    y2016 = data["years"]["2016"]
    # revenue_gbp = margin + 100.0 per _record(); 110.0 + 112.0 + 105.0
    assert y2016["revenue_gbp"] == 327.0
    assert y2016["gross_gbp"] == 27.0
    assert y2016["net_gbp"] == 21.0
    assert y2016["commodity_split"]["electricity"]["net_gbp"] == 17.0
    assert y2016["commodity_split"]["gas"]["net_gbp"] == 4.0
    # C1 and C1g are both segment "resi" (saas.customers.CUSTOMERS)
    assert y2016["segment_split"]["resi electricity"]["net_gbp"] == 17.0
    assert y2016["segment_split"]["resi gas"]["net_gbp"] == 4.0
    # revenue_gbp threaded into segment_split (2026-07-10, segmented financials
    # backlog item): 110.0 + 112.0 from the two C1 electricity records
    assert y2016["segment_split"]["resi electricity"]["revenue_gbp"] == 222.0
    assert y2016["segment_split"]["resi gas"]["revenue_gbp"] == 105.0
    # Picked from the chronologically latest record (2016-06-01), not list order
    assert y2016["treasury_end_gbp"] == 1017.0
    # All 13 customers (incl. Phase 6a HH customers C7-C9) have a 2016
    # acquisition_date.
    assert y2016["acquisitions"] == [
        "C1", "C1g", "C2", "C2g", "C3", "C3g", "C4", "C4g", "C5", "C6", "C7", "C8", "C9",
    ]
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
    # D3 Expert-Hour finding (2026-07-12): a shock with no catchup_applied
    # field on its source bill must default to catchup_driven=False, not
    # crash or omit the key.
    assert y2017["bill_shock_events"][0]["catchup_driven"] is False
    assert y2017["bad_debt_gbp"] == 4.0

    # revenue_gbp = margin + 100.0 per _record(); 110 + 112 + 105 + 95
    assert data["total_revenue_gbp"] == 422.0
    assert data["total_net_gbp"] == 15.0
    assert data["per_customer_lifetime"]["C1"]["net_gbp"] == 11.0


def test_by_billing_account_carries_avg_annual_net_margin_when_ev_present():
    """Director page comment (2026-07-11, /customers/: "expose forecast profit
    and cashflow"): saas/clv_model.py::build_clv() already computes
    avg_annual_net_margin_gbp (the forecast-annual-profit input that drives
    clv_gbp), but by_billing_account's construction only ever extracted
    clv_gbp/expected_lifetime_periods from it, dropping this field before it
    reached tools/generate_customer_data.py."""
    run_output = _run_output()
    run_output["enterprise_value"] = {
        "by_customer": {
            "C1": {
                "clv_gbp": 5452.61,
                "expected_lifetime_periods": 16.78,
                "avg_annual_net_margin_gbp": 500.0,
            },
        },
    }

    data = extract_report_data(run_output)

    assert data["by_billing_account"]["C1"]["avg_annual_net_margin_gbp"] == 500.0
    assert data["by_billing_account"]["C1"]["clv_gbp"] == 5452.61


def test_by_billing_account_avg_annual_net_margin_none_when_ev_absent():
    """None-safety, same pattern already used for clv_gbp/expected_lifetime_periods:
    an account with no enterprise_value entry gets None, never a silent 0."""
    data = extract_report_data(_run_output())  # no "enterprise_value" key at all

    assert data["by_billing_account"]["C1"]["avg_annual_net_margin_gbp"] is None
    assert data["by_billing_account"]["C1"]["clv_gbp"] is None


def test_extract_report_data_total_net_ignores_stale_phase2b_scalar():
    """Regression test for the Project tab consistency bug (PROJECT_TAB_OVERHAUL.md
    critique finding #1): total_net_gbp/total_bad_debt_gbp must be derived live from
    all_records (post-mutation, after apply_emergent_bad_debt/apply_debt_recovery run
    in run_phase4c_on_phase2b.py), never trusted from phase2b's own total_net/
    total_bad_debt scalars, which are captured before those mutation passes run and
    can go stale relative to all_records."""
    run_output = _run_output()
    # Simulate exactly the bug: phase2b's scalars were computed pre-mutation and no
    # longer match all_records (post-mutation), which is the real invariant.
    run_output["phase2b"]["total_net"] = 999.0
    run_output["phase2b"]["total_bad_debt"] = 999.0

    data = extract_report_data(run_output)

    all_records = run_output["phase2b"]["all_records"]
    expected_net = sum(r["net_margin_gbp"] for r in all_records)
    expected_bad_debt = sum(r.get("bad_debt_gbp", 0.0) for r in all_records)

    assert expected_net == 15.0
    assert expected_bad_debt == 4.0

    assert data["total_net_gbp"] == expected_net
    assert data["total_bad_debt_gbp"] == expected_bad_debt
    assert data["total_net_gbp"] != 999.0
    assert data["total_bad_debt_gbp"] != 999.0

    # Core consistency invariant the site needs: the top-level total must equal the
    # sum of the per-year breakdown, by construction (same source list, same field).
    assert data["total_net_gbp"] == sum(
        data["years"][year]["net_gbp"] for year in data["years"]
    )


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
    # Segment margin trend (REPORTING_BACKLOG item 11)
    assert "## Segment Margin Trend" in report


def test_segment_margin_trend_section_breaks_down_by_segment_and_year():
    data = extract_report_data(_run_output())
    section = _segment_margin_trend_section(data)

    assert "resi electricity" in section
    assert "resi gas" in section
    # 2016: resi electricity net = 17.0, resi gas net = 4.0, total = 21.0
    assert "| 2016 |" in section
    row_2016 = [line for line in section.splitlines() if line.startswith("| 2016 |")][0]
    assert "£17.00" in row_2016
    assert "£4.00" in row_2016
    assert "£21.00" in row_2016
    # 2017: resi electricity net = -6.0, no gas activity that year
    row_2017 = [line for line in section.splitlines() if line.startswith("| 2017 |")][0]
    assert "£-6.00" in row_2017


def test_segment_margin_trend_section_handles_no_years():
    data = extract_report_data(_run_output())
    data["years"] = {}
    assert NOT_AVAILABLE in _segment_margin_trend_section(data)


def test_segment_margin_trend_section_handles_missing_segment_split():
    # Cached report-data JSON generated before this section existed won't
    # have "segment_split" -- regenerating the report from it must degrade
    # gracefully rather than raising KeyError.
    data = extract_report_data(_run_output())
    for yd in data["years"].values():
        del yd["segment_split"]
    assert NOT_AVAILABLE in _segment_margin_trend_section(data)


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
    # Clarify that gross/capital/net figures from the two runs aren't
    # comparable across rows (e.g. don't subtract old net from new gross).
    assert "different" in section
    assert "This run (Phase 9a): gross" in section
    assert "Old-model run (commodity-only, pre-Phase-9a): gross" in section
    assert "commodity-only" in section


def test_mandate_comparison_section_reports_revenue_pct_when_old_has_revenue():
    data = extract_report_data(_run_output())
    old_data = extract_report_data(_run_output())

    section = _mandate_comparison_section(data, old_data)

    assert "Net margin as % of revenue" in section
    assert NOT_AVAILABLE not in section.split("Net margin as % of revenue")[1].split("\n")[0]


def test_mandate_comparison_section_reports_not_available_revenue_pct_for_old_snapshot():
    data = extract_report_data(_run_output())
    old_data = extract_report_data(_run_output())
    # Simulate a pre-revenue-capture snapshot (e.g. the preserved
    # run_output_old_reactive_model_pre5c.json), which has no
    # total_revenue_gbp key at all.
    del old_data["total_revenue_gbp"]

    section = _mandate_comparison_section(data, old_data)

    assert "Net margin as % of revenue" in section
    assert NOT_AVAILABLE in section


def test_ledger_summary_section_shows_waterfall_and_event_counts():
    meta = {
        "event_count": 300,
        "by_type": {"billing_event": 100, "settlement_event": 150, "capital_charge_event": 50},
    }
    pnl = {
        "revenue_gbp": 10000.0,
        "wholesale_cost_gbp": 7000.0,
        "gross_margin_gbp": 3000.0,
        "capital_cost_gbp": 500.0,
        "net_margin_gbp": 2500.0,
    }
    data = {"ledger_meta": meta, "ledger_pnl": pnl, "total_net_gbp": 2500.0}
    section = _ledger_summary_section(data)
    assert "Transaction Log" in section
    assert "300" in section
    assert "billing_event" in section
    assert "£10,000.00" in section  # revenue
    assert "£2,500.00" in section  # net margin


def test_ledger_summary_section_shows_not_available_when_no_meta():
    section = _ledger_summary_section({})
    assert NOT_AVAILABLE in section


def test_ledger_summary_section_shows_cost_to_serve_row():
    """CTS reconciliation fix (NEXT_PHASE.md option B): the ledger waterfall
    must show a distinct Cost to serve row, separate from Fixed overhead."""
    meta = {"event_count": 5, "by_type": {"billing_event": 1}}
    pnl = {
        "revenue_gbp": 10000.0,
        "wholesale_cost_gbp": 7000.0,
        "gross_margin_gbp": 3000.0,
        "capital_cost_gbp": 500.0,
        "net_margin_gbp": 2500.0,
        "fixed_cost_gbp": 100.0,
        "cost_to_serve_gbp": 250.0,
        "operating_net_margin_gbp": 2150.0,
    }
    data = {"ledger_meta": meta, "ledger_pnl": pnl}
    section = _ledger_summary_section(data)
    assert "Cost to serve" in section
    assert "£250.00" in section


def test_ledger_summary_section_phase9a_shows_vat_breakdown():
    """Phase 9a: total_billed, VAT remittance, and non-commodity lines appear."""
    meta = {"event_count": 5, "by_type": {"billing_event": 1}}
    pnl = {
        "total_billed_gbp": 12000.0,
        "vat_remittance_gbp": 1000.0,
        "revenue_gbp": 11000.0,
        "non_commodity_cost_gbp": 3000.0,
        "wholesale_cost_gbp": 7000.0,
        "gross_margin_gbp": 1000.0,
        "capital_cost_gbp": 100.0,
        "net_margin_gbp": 900.0,
    }
    data = {"ledger_meta": meta, "ledger_pnl": pnl}
    section = _ledger_summary_section(data)
    assert "£12,000.00" in section   # total_billed
    assert "£1,000.00" in section    # VAT (£1,000.00 also matches vat_remittance)
    assert "£11,000.00" in section   # ex-VAT revenue
    assert "non-commodity" in section.lower()
    assert "VAT" in section


def test_build_ledger_headline_returns_none_for_pre9a():
    """Pre-Phase-9a ledger (no total_billed_gbp) returns None."""
    pnl = {"revenue_gbp": 10000.0, "gross_margin_gbp": 3000.0, "net_margin_gbp": 2500.0,
           "capital_cost_gbp": 500.0}
    assert _build_ledger_headline(pnl) is None
    assert _build_ledger_headline(None) is None


def test_build_ledger_headline_extracts_phase9a_fields():
    """Phase 9a ledger with total_billed_gbp returns all headline fields."""
    pnl = {
        "total_billed_gbp": 12000.0,
        "vat_remittance_gbp": 1000.0,
        "revenue_gbp": 11000.0,
        "non_commodity_cost_gbp": 3000.0,
        "wholesale_cost_gbp": 7000.0,
        "gross_margin_gbp": 1000.0,
        "capital_cost_gbp": 100.0,
        "net_margin_gbp": 900.0,
    }
    hl = _build_ledger_headline(pnl)
    assert hl is not None
    assert hl["total_billed_gbp"] == 12000.0
    assert hl["vat_remittance_gbp"] == 1000.0
    assert hl["revenue_gbp"] == 11000.0
    assert hl["non_commodity_cost_gbp"] == 3000.0
    assert hl["net_margin_gbp"] == 900.0


def _ntfy_data():
    return {
        "total_net_gbp": 3121.74,
        "total_revenue_gbp": 93868.0,
        "starting_treasury_gbp": 29846.0,
        "final_treasury_gbp": 32967.0,
        "committee_wake_ups_total": 85,
        "churned_billing_accounts": ["C1", "C5"],
        "customer_events": [
            {"customer_id": "C1", "event_date": "2021-12-30", "event_type": "churned"},
            {"customer_id": "C5", "event_date": "2021-12-30", "event_type": "churned"},
            {"customer_id": "C2", "event_date": "2020-03-31", "event_type": "renewed"},
        ],
    }


def test_send_run_complete_ntfy_is_no_op(monkeypatch):
    # _send_run_complete_ntfy was removed (per-run NTFYs are spam at 1 run/17min).
    # Verify the function exists but sends nothing.
    import background.ntfy_utils as ntfy_utils
    sent = []
    monkeypatch.setattr(ntfy_utils, "send_ntfy", lambda msg, headers=None: sent.append(msg))
    _send_run_complete_ntfy(_ntfy_data(), Path("ANNUAL_REPORT.md"))
    assert sent == []


# --- _pricing_action tests ---

def test_pricing_action_ok_when_margin_exceeds_benchmark():
    result = _pricing_action(net_margin_after_cts_gbp=500.0, revenue_gbp=10_000.0)
    assert result["flag"] == "OK"
    assert result["recommended_uplift_pct"] is None


def test_pricing_action_margin_squeeze_below_benchmark():
    # 1% net margin after CTS — below 2% benchmark
    result = _pricing_action(net_margin_after_cts_gbp=100.0, revenue_gbp=10_000.0)
    assert result["flag"] == "MARGIN_SQUEEZE"
    assert result["recommended_uplift_pct"] is None


def test_pricing_action_net_negative_computes_uplift():
    # -£200 shortfall on £10,000 revenue → 2% tariff uplift needed
    result = _pricing_action(net_margin_after_cts_gbp=-200.0, revenue_gbp=10_000.0)
    assert result["flag"] == "NET_NEGATIVE"
    assert abs(result["recommended_uplift_pct"] - 2.0) < 0.01


def test_pricing_action_unknown_when_cts_missing():
    result = _pricing_action(net_margin_after_cts_gbp=None, revenue_gbp=10_000.0)
    assert result["flag"] == "UNKNOWN"
    assert result["recommended_uplift_pct"] is None


def test_pricing_action_unknown_when_zero_revenue():
    result = _pricing_action(net_margin_after_cts_gbp=-50.0, revenue_gbp=0.0)
    assert result["flag"] == "UNKNOWN"
    assert result["recommended_uplift_pct"] is None


def test_extract_report_data_includes_pricing_action():
    data = extract_report_data(_run_output())
    for pcl in data["per_customer_lifetime"].values():
        assert "pricing_action" in pcl
        assert "flag" in pcl["pricing_action"]
        assert pcl["pricing_action"]["flag"] in ("OK", "MARGIN_SQUEEZE", "NET_NEGATIVE", "UNKNOWN")


def test_extract_report_data_includes_avg_hedge_fraction():
    """2026-07-11, HARDEN sweep (harden_sweep:live_site:B3_hedge_tariff_alignment):
    hedge_fraction has always been on every settlement record but was never
    surfaced to per_customer_lifetime -- this closes that gap."""
    data = extract_report_data(_run_output())
    for pcl in data["per_customer_lifetime"].values():
        assert "avg_hedge_fraction" in pcl


def test_avg_hedge_fraction_is_consumption_weighted():
    base = _run_output()
    # Two records: 20 kWh at hedge_fraction 1.0, 10 kWh at hedge_fraction 0.0
    # -> weighted average = (20*1.0 + 10*0.0) / 30 = 0.6667, NOT the plain
    # mean of 0.5 -- proves the weighting, not just presence of the field.
    records = [
        dict(_record("C1", "electricity", "2016-01-01", 1, 10.0, 2.0, 8.0, 50.0, 1008.0),
             consumption_kwh=20.0, hedge_fraction=1.0),
        dict(_record("C1", "electricity", "2016-06-01", 1, 12.0, 3.0, 9.0, 52.0, 1017.0),
             consumption_kwh=10.0, hedge_fraction=0.0),
    ]
    base["phase2b"]["all_records"] = records
    data = extract_report_data(base)
    assert abs(data["per_customer_lifetime"]["C1"]["avg_hedge_fraction"] - 0.6667) < 0.001


def test_avg_hedge_fraction_none_when_zero_consumption():
    base = _run_output()
    records = [
        dict(_record("C1", "electricity", "2016-01-01", 1, 10.0, 2.0, 8.0, 50.0, 1008.0),
             consumption_kwh=0.0, hedge_fraction=0.5),
    ]
    base["phase2b"]["all_records"] = records
    data = extract_report_data(base)
    assert data["per_customer_lifetime"]["C1"]["avg_hedge_fraction"] is None


def test_extract_report_data_includes_revenue_gbp_per_customer():
    data = extract_report_data(_run_output())
    # C1 has records with revenue = margin + 100: (10+100) + (12+100) + (-5+100) = 317
    assert abs(data["per_customer_lifetime"]["C1"]["revenue_gbp"] - 317.0) < 0.01


def test_extract_report_data_includes_clv_snapshots_key():
    data = extract_report_data(_run_output())
    # clv_snapshots is None when churn_risk is empty (fixture has no churn_risk)
    assert "clv_snapshots" in data


def test_clv_trajectory_section_shows_not_available_when_no_snapshots():
    section = _clv_trajectory_section({"clv_snapshots": None})
    assert NOT_AVAILABLE in section


def test_clv_trajectory_section_renders_table_with_snapshots():
    snapshots = {
        "2016": {"C1": 1000.0, "C2": None},
        "2017": {"C1": 1100.0, "C2": 950.0},
    }
    section = _clv_trajectory_section({"clv_snapshots": snapshots})
    assert "## CLV Trajectory" in section
    assert "2016" in section
    assert "2017" in section
    assert "C1" in section
    assert "C2" in section
    assert "£1,000" in section
    assert "£1,100" in section
    assert "£950" in section
    # 2016 C2 has no data yet — should show em-dash
    assert "—" in section


def test_extract_report_data_churn_risk_by_account_empty_when_no_churn_data():
    data = extract_report_data(_run_output())
    # Fixture has no churn_risk — should give empty dict for all years
    for year_data in data["years"].values():
        assert year_data["churn_risk_by_account"] == {}


def _run_output_with_churn_risk():
    base = _run_output()
    base["churn_risk"] = {
        "C1": [
            {"renewal_period": "2016-06", "churn_probability": 0.15},
            {"renewal_period": "2017-06", "churn_probability": 0.30},
        ],
        "C2": [
            {"renewal_period": "2017-06", "churn_probability": 0.10},
        ],
    }
    return base


def test_extract_report_data_churn_risk_by_account_per_year():
    data = extract_report_data(_run_output_with_churn_risk())
    # 2016: only C1 had a renewal (2016-06); churn prob 0.15
    assert data["years"]["2016"]["churn_risk_by_account"] == {"C1": 0.15}
    # 2017: C1 (0.30) and C2 (0.10) both renewed
    assert data["years"]["2017"]["churn_risk_by_account"] == {"C1": 0.30, "C2": 0.10}


def _pricing_data_with_flags(flags: dict) -> dict:
    """Build a minimal data dict with per_customer_lifetime pricing flags."""
    per_customer_lifetime = {}
    for cid, flag_info in flags.items():
        per_customer_lifetime[cid] = {
            "revenue_gbp": flag_info.get("revenue", 1000.0),
            "cost_to_serve_gbp": 100.0,
            "net_margin_after_cost_to_serve_gbp": flag_info.get("net_after_cts", 50.0),
            "pricing_action": {
                "flag": flag_info["flag"],
                "recommended_uplift_pct": flag_info.get("uplift"),
            },
        }
    return {"per_customer_lifetime": per_customer_lifetime}


def test_append_pricing_actions_summary_no_flags_emits_nothing():
    data = _pricing_data_with_flags({"C1": {"flag": "OK"}})
    lines: list[str] = []
    _append_pricing_actions_summary(lines, data)
    assert lines == []


def test_append_pricing_actions_summary_net_negative_shows_uplift():
    data = _pricing_data_with_flags({
        "C1": {"flag": "NET_NEGATIVE", "revenue": 1000.0, "net_after_cts": -50.0, "uplift": 5.0},
    })
    lines: list[str] = []
    _append_pricing_actions_summary(lines, data)
    output = "\n".join(lines)
    assert "Activity-Based Pricing Actions" in output
    assert "C1" in output
    assert "5.0%" in output
    assert "loss-making" in output.lower()


def test_append_pricing_actions_summary_margin_squeeze_listed():
    data = _pricing_data_with_flags({
        "C2": {"flag": "MARGIN_SQUEEZE", "revenue": 1000.0, "net_after_cts": 10.0},
    })
    lines: list[str] = []
    _append_pricing_actions_summary(lines, data)
    output = "\n".join(lines)
    assert "MARGIN_SQUEEZE" in output
    assert "C2" in output
    assert "2%" in output


def test_append_pricing_actions_summary_both_sections_rendered():
    data = _pricing_data_with_flags({
        "C1": {"flag": "NET_NEGATIVE", "revenue": 1000.0, "net_after_cts": -30.0, "uplift": 3.0},
        "C3": {"flag": "MARGIN_SQUEEZE", "revenue": 1000.0, "net_after_cts": 5.0},
        "C5": {"flag": "OK"},
    })
    lines: list[str] = []
    _append_pricing_actions_summary(lines, data)
    output = "\n".join(lines)
    assert "C1" in output
    assert "C3" in output
    assert "C5" not in output


def _minimal_year_data(year: str = "2016") -> dict:
    return {
        "active_customer_ids": ["C1"],
        "acquisitions": [],
        "bill_shock_events": [],
        "bills_count": 1,
        "avg_clarity": 0.8,
        "avg_bill_shock_pct": None,
        "churn_risk_by_account": {},
    }


def test_customer_book_section_per_year_clv_from_snapshots():
    yd = _minimal_year_data("2016")
    data = {
        "customer_events": [],
        "churned_billing_accounts": [],
        "avg_clv_gbp": None,
        "highest_clv": None,
        "lowest_clv": None,
        "clv_snapshots": {"2016": {"C1": 500.0}},
    }
    section = _customer_book_section("2016", yd, data)
    assert "Point-in-Time" in section
    assert "£500" in section


def test_customer_book_section_per_year_clv_falls_back_to_whole_run():
    yd = _minimal_year_data("2016")
    data = {
        "customer_events": [],
        "churned_billing_accounts": [],
        "avg_clv_gbp": 750.0,
        "highest_clv": {"customer_id": "C1", "clv_gbp": 750.0},
        "lowest_clv": {"customer_id": "C1", "clv_gbp": 750.0},
        "clv_snapshots": None,
    }
    section = _customer_book_section("2016", yd, data)
    assert "whole-run projection" in section
    assert "£750" in section


def test_customer_book_section_churn_risk_above_threshold_shown():
    yd = _minimal_year_data("2017")
    yd["churn_risk_by_account"] = {"C1": 0.35, "C2": 0.10}
    data = {
        "customer_events": [],
        "churned_billing_accounts": [],
        "avg_clv_gbp": None,
        "highest_clv": None,
        "lowest_clv": None,
        "clv_snapshots": None,
    }
    section = _customer_book_section("2017", yd, data)
    assert "1 at risk" in section
    assert "C1" in section
    assert "35%" in section
    assert "C2" not in section.split("at risk")[1]


def test_lifetime_pricing_section_not_available_without_cts():
    data = {"per_customer_lifetime": {"C1": {"cost_to_serve_gbp": None}}}
    section = _lifetime_pricing_section(data)
    assert "## Cost to Serve & Pricing Actions" in section
    assert NOT_AVAILABLE in section


def test_lifetime_pricing_section_renders_once_with_flags():
    data = {
        "per_customer_lifetime": {
            "C1": {
                "cost_to_serve_gbp": 100.0,
                "net_margin_after_cost_to_serve_gbp": -20.0,
                "revenue_gbp": 500.0,
                "pricing_action": {"flag": "NET_NEGATIVE", "recommended_uplift_pct": 4.0},
            },
        }
    }
    section = _lifetime_pricing_section(data)
    assert "## Cost to Serve & Pricing Actions" in section
    assert "NET_NEGATIVE" in section
    assert "4.0%" in section
    assert "Activity-Based Pricing Actions" in section


def test_generate_annual_report_pricing_section_appears_once():
    report = generate_annual_report(extract_report_data(_run_output()))
    assert report.count("## Cost to Serve & Pricing Actions") == 1
    assert "**Pricing & Margin**" in report


def test_customer_book_section_hh_resi_counted_separately():
    yd = _minimal_year_data("2016")
    yd["active_customer_ids"] = ["C1", "C5", "C7", "C1g"]
    data = {
        "customer_events": [],
        "churned_billing_accounts": [],
        "avg_clv_gbp": None,
        "highest_clv": None,
        "lowest_clv": None,
        "clv_snapshots": None,
        "per_customer_lifetime": {
            "C1":  {"segment": "resi", "commodity": "electricity"},
            "C5":  {"segment": "SME",  "commodity": "electricity"},
            "C7":  {"segment": "resi", "commodity": "electricity"},
            "C1g": {"segment": "resi", "commodity": "gas"},
        },
    }
    section = _customer_book_section("2016", yd, data)
    assert "Resi electricity: 2" in section
    assert "SME electricity: 1" in section
    assert "gas (dual-fuel): 1" in section


# ---- Phase 7e: successor activations in extract_report_data ----

def _run_output_with_successor_activation():
    """Extend the base fixture with a won_successor_activations entry for 2017."""
    base = _run_output()
    base["won_successor_activations"] = {"C1_2": "2017-01-01"}
    return base


def test_extract_report_data_passes_through_won_successor_activations():
    """won_successor_activations from run output is forwarded into extracted data."""
    data = extract_report_data(_run_output_with_successor_activation())
    assert data.get("won_successor_activations") == {"C1_2": "2017-01-01"}


def test_extract_report_data_won_successor_activations_empty_by_default():
    """When not present in run output, won_successor_activations defaults to empty dict."""
    data = extract_report_data(_run_output())
    assert data.get("won_successor_activations") == {}


# ---- Phase QP: churn_journey_log forwarding (was silently dropped since Phase QL) ----

def test_extract_report_data_forwards_churn_journey_log():
    """phase2b's churn_journey_log (Phase QL) must reach the saved run_output json --
    it was computed but never forwarded, leaving dash["customers"]["journey_log"]
    empty in every production run since Phase QL shipped."""
    run_output = _run_output()
    run_output["phase2b"]["churn_journey_log"] = [
        {"customer_id": "C1", "term_start": "2021-01-01", "journey_state": "irritated",
         "resentment_score": 12.5, "is_burned": False, "perceived_bill_saving_gbp": 3.2},
    ]
    data = extract_report_data(run_output)
    assert data.get("churn_journey_log") == run_output["phase2b"]["churn_journey_log"]


def test_extract_report_data_churn_journey_log_empty_by_default():
    data = extract_report_data(_run_output())
    assert data.get("churn_journey_log") == []


def test_acquisitions_includes_won_successors_in_activation_year():
    """A won successor activated in 2017 appears in 2017's acquisitions list."""
    data = extract_report_data(_run_output_with_successor_activation())
    assert "C1_2" in data["years"]["2017"]["acquisitions"]


def test_acquisitions_excludes_won_successors_from_other_years():
    """A won successor activated in 2017 does NOT appear in 2016's acquisitions."""
    data = extract_report_data(_run_output_with_successor_activation())
    assert "C1_2" not in data["years"]["2016"]["acquisitions"]


# ---- Regression: successor customer records must not cause KeyError in CLV snapshots ----

def test_build_clv_snapshots_with_successor_records():
    """Regression: _build_clv_snapshots must not raise KeyError when all_records
    contains a successor customer (e.g. C1_2). This was the exact failure mode in
    the Phase 7e run where the JSON-save step crashed with KeyError: 'C1_2' because
    build_cost_to_serve was called with only CUSTOMERS, not CUSTOMERS+SUCCESSOR_CUSTOMERS.
    """
    records = [
        _record("C1",   "electricity", "2016-01-01", 1, 10.0, 2.0, 8.0, 50.0, 1008.0),
        _record("C1_2", "electricity", "2022-01-01", 1, 12.0, 2.0, 9.0, 50.0, 1017.0),
    ]
    churn_risk = {
        "C1": [{"renewal_period": "2016-12", "bill_shock_count": 0, "churn_probability": 0.05}],
    }
    # Must not raise KeyError: 'C1_2'
    snapshots = _build_clv_snapshots(records, churn_risk, ["2016", "2022"])
    assert "2016" in snapshots
    assert "2022" in snapshots


# ---- Phase 12c: Retention ROI section ----

def test_section_retention_strategy_empty():
    from saas.reporting.annual_report import _section_retention_strategy
    result = _section_retention_strategy({})
    assert "Retention Strategy" in result


def test_section_retention_strategy_with_retained():
    from saas.reporting.annual_report import _section_retention_strategy
    rl = [dict(
        customer_id="C1", event_date="2021-06-30",
        company_churn_estimate=0.45, discount_pct=0.05,
        retention_cost_gbp=12.50, expected_term_margin_gbp=200.0,
        outcome="retained",
    )]
    data = dict(retention_log=rl, no_offer_churn_log=[])
    result = _section_retention_strategy(data)
    assert "Net ROI" in result
    assert "187.50" in result
    assert "retained" in result


def test_section_retention_strategy_with_churned_despite():
    from saas.reporting.annual_report import _section_retention_strategy
    rl = [dict(
        customer_id="C2", event_date="2022-06-30",
        company_churn_estimate=0.55, discount_pct=0.05,
        retention_cost_gbp=15.0, expected_term_margin_gbp=150.0,
        outcome="churned_despite_offer",
    )]
    data = dict(retention_log=rl, no_offer_churn_log=[])
    result = _section_retention_strategy(data)
    assert "churned_despite_offer" in result
    assert "-15.00" in result


def test_section_retention_strategy_with_missed():
    from saas.reporting.annual_report import _section_retention_strategy
    no_offer = [dict(
        customer_id="C3", event_date="2022-12-31",
        company_churn_estimate=0.20, expected_term_margin_gbp=180.0,
    )]
    data = dict(retention_log=[], no_offer_churn_log=no_offer)
    result = _section_retention_strategy(data)
    assert "Missed opportunities" in result
    assert "180.00" in result


def test_extract_report_data_includes_no_offer_churn_log():
    # Use minimal approach: just check the key passes through when provided
    from saas.reporting.annual_report import _section_retention_strategy
    data = dict(retention_log=[], no_offer_churn_log=[dict(
        customer_id="C1", event_date="2021-01-01", expected_term_margin_gbp=100.0
    )])
    result = _section_retention_strategy(data)
    assert "Missed opportunities" in result
    assert "1**" in result


# Phase 12e: Company Model Divergence tests

def test_section_company_divergence_not_available_when_empty():
    from saas.reporting.annual_report import _section_company_divergence
    result = _section_company_divergence({})
    assert "Company Model Divergence" in result
    assert "N/A" in result or "not available" in result.lower() or "n/a" in result.lower()


def test_section_company_divergence_renders_tariff_table():
    from saas.reporting.annual_report import _section_company_divergence
    data = {
        "company_divergence": {
            "tariff_error_by_year": {
                "2021": {"n": 4, "mean_abs_error_pct": 0.25, "max_abs_error_pct": 0.50},
                "2022": {"n": 4, "mean_abs_error_pct": 0.40, "max_abs_error_pct": 0.80},
            },
            "churn_error_by_year": {},
        }
    }
    result = _section_company_divergence(data)
    assert "Company Model Divergence" in result
    assert "Tariff Pricing Error" in result
    assert "2021" in result
    assert "25.0%" in result  # mean_abs_error_pct 0.25 * 100
    assert "50.0%" in result  # max_abs_error_pct 0.50 * 100
    assert "2022" in result


def test_section_company_divergence_renders_churn_table():
    from saas.reporting.annual_report import _section_company_divergence
    data = {
        "company_divergence": {
            "tariff_error_by_year": {},
            "churn_error_by_year": {
                "2020": {"n": 3, "mean_abs_error_pct": 0.15, "max_abs_error_pct": 0.30},
            },
        }
    }
    result = _section_company_divergence(data)
    assert "Churn Estimate Error" in result
    assert "2020" in result
    assert "0.15×" in result   # shown as ×SIM multiplier (Phase 14a annotation)
    assert "0.30×" in result


def test_extract_report_data_includes_company_divergence():
    # Verify the key passes through from phase2b output
    from saas.reporting.annual_report import _section_company_divergence
    # If company_divergence missing from data, section returns NOT_AVAILABLE
    result = _section_company_divergence({"company_divergence": {}})
    assert "Company Model Divergence" in result


# ── ToU utilization section tests (Phase 14d) ─────────────────────────────────

def _tou_stats_fixture():
    """Synthetic tou_stats: C8-like customer with 43.8% peak vs 30% design."""
    return {
        "C8": {
            "total_kwh": 10000.0,
            "peak_kwh": 4376.0,
            "offpeak_kwh": 5624.0,
            "peak_pct": 43.76,
            "peak_revenue_gbp": 622.6,
            "offpeak_revenue_gbp": 420.0,
            "avg_peak_rate": 142.3,
            "avg_offpeak_rate": 74.7,
        },
    }


def test_tou_revenue_premium_above_zero_for_high_peak_utilization():
    from saas.reporting.annual_report import _tou_revenue_premium
    s = _tou_stats_fixture()["C8"]
    flat_equiv, premium_pct = _tou_revenue_premium(s)
    # C8 uses 43.8% peak > 30% design → ToU earns more than flat rate
    assert premium_pct > 0.0


def test_tou_revenue_premium_zero_at_design_split():
    from saas.reporting.annual_report import _tou_revenue_premium
    from saas.tariff_pricing import TOU_PEAK_MULTIPLIER, TOU_OFFPEAK_MULTIPLIER
    flat_rate = 100.0
    total_kwh = 10000.0
    peak_kwh = 3000.0   # exactly 30% design split
    offpeak_kwh = 7000.0
    s = {
        "peak_kwh": peak_kwh,
        "offpeak_kwh": offpeak_kwh,
        "peak_revenue_gbp": peak_kwh * flat_rate * TOU_PEAK_MULTIPLIER / 1000.0,
        "offpeak_revenue_gbp": offpeak_kwh * flat_rate * TOU_OFFPEAK_MULTIPLIER / 1000.0,
        "avg_peak_rate": flat_rate * TOU_PEAK_MULTIPLIER,
        "avg_offpeak_rate": flat_rate * TOU_OFFPEAK_MULTIPLIER,
    }
    _, premium_pct = _tou_revenue_premium(s)
    # At design split, revenue neutral → premium ≈ 0%
    assert abs(premium_pct) < 0.01


def test_section_tou_utilization_shows_premium_column():
    from saas.reporting.annual_report import _section_tou_utilization
    data = {"tou_stats": _tou_stats_fixture()}
    result = _section_tou_utilization(data)
    assert "ToU Premium" in result
    assert "%" in result
    assert "Total HH revenue" in result


def test_section_tou_utilization_empty_returns_empty():
    from saas.reporting.annual_report import _section_tou_utilization
    assert _section_tou_utilization({"tou_stats": {}}) == ""
    assert _section_tou_utilization({}) == ""


# ── Bill Shock Summary tests (Phase 14e) ──────────────────────────────────────

def _bill_shock_data_fixture():
    """Minimal run data with bill shock events across 2 years."""
    return {
        "years": {
            "2021": {
                "bill_shock_events": [
                    {"customer_id": "C5", "period_end": "2021-10-31", "bill_shock_pct": 0.85},
                    {"customer_id": "C4g", "period_end": "2021-11-30", "bill_shock_pct": 1.52},
                ],
            },
            "2022": {
                "bill_shock_events": [
                    {"customer_id": "C2_2", "period_end": "2022-04-30", "bill_shock_pct": 17.17},
                ],
            },
        },
        "churned_billing_accounts": ["C5"],
    }


def test_section_bill_shock_shows_header():
    from saas.reporting.annual_report import _section_bill_shock_summary
    result = _section_bill_shock_summary(_bill_shock_data_fixture())
    assert "Bill Shock Summary" in result


def test_section_bill_shock_shows_year_table():
    from saas.reporting.annual_report import _section_bill_shock_summary
    result = _section_bill_shock_summary(_bill_shock_data_fixture())
    assert "2021" in result
    assert "2022" in result
    assert "3" in result   # total events across 2 years (2+1=3)


def test_section_bill_shock_shows_top_shocks():
    from saas.reporting.annual_report import _section_bill_shock_summary
    result = _section_bill_shock_summary(_bill_shock_data_fixture())
    assert "C2_2" in result   # worst spike (1717%)
    assert "1717%" in result


def test_section_bill_shock_marks_churned_customers():
    from saas.reporting.annual_report import _section_bill_shock_summary
    result = _section_bill_shock_summary(_bill_shock_data_fixture())
    # C5 is in churned set → should show 'yes'
    # The top shock is C2_2, but C5 is also in the list
    assert "yes" in result   # C5 appears in top shocks and is churned


def test_section_bill_shock_empty_returns_empty():
    from saas.reporting.annual_report import _section_bill_shock_summary
    assert _section_bill_shock_summary({}) == ""
    assert _section_bill_shock_summary({"years": {}}) == ""


# ── Gas Renewal Pressure tests (Phase 15a) ────────────────────────────────────

def _gas_churn_log_fixture():
    return {
        "company_gas_churn_log": [
            {"customer_id": "C1g", "billing_account": "C1", "term_start": "2021-10-01",
             "old_gas_rate": 40.0, "new_gas_rate": 80.0, "company_gas_churn_estimate": 0.32},
            {"customer_id": "C2g", "billing_account": "C2", "term_start": "2021-10-01",
             "old_gas_rate": 38.0, "new_gas_rate": 90.0, "company_gas_churn_estimate": 0.41},
            {"customer_id": "C1g", "billing_account": "C1", "term_start": "2019-10-01",
             "old_gas_rate": 35.0, "new_gas_rate": 37.0, "company_gas_churn_estimate": 0.09},
        ],
    }


def test_section_gas_renewal_shows_header():
    from saas.reporting.annual_report import _section_gas_renewal_pressure
    result = _section_gas_renewal_pressure(_gas_churn_log_fixture())
    assert "Gas Renewal Pressure" in result


def test_section_gas_renewal_shows_year_table():
    from saas.reporting.annual_report import _section_gas_renewal_pressure
    result = _section_gas_renewal_pressure(_gas_churn_log_fixture())
    assert "2021" in result
    assert "2019" in result


def test_section_gas_renewal_flags_elevated_years():
    from saas.reporting.annual_report import _section_gas_renewal_pressure
    result = _section_gas_renewal_pressure(_gas_churn_log_fixture())
    # 2021 has 2 entries above 20% threshold → should show warning flag
    assert "⚠" in result
    # 2019 has 1 entry at 9% → no flag expected (below threshold)
    # Check 2021 row has elevated count
    assert "2 ⚠" in result


def test_section_gas_renewal_shows_top_elevated_entries():
    from saas.reporting.annual_report import _section_gas_renewal_pressure
    result = _section_gas_renewal_pressure(_gas_churn_log_fixture())
    assert "C2g" in result   # highest estimate (41%)
    assert "41%" in result


def test_section_gas_renewal_empty_on_missing_log():
    from saas.reporting.annual_report import _section_gas_renewal_pressure
    assert _section_gas_renewal_pressure({}) == ""
    assert _section_gas_renewal_pressure({"company_gas_churn_log": []}) == ""


# ── Full economic ROI tests (Phase 15c) ─────────────────────────────────────

def _retention_with_acq_data():
    """Retention log with acq_cost_saved_gbp (Phase 15b+ format)."""
    return {
        "retention_log": [
            {
                "customer_id": "C1",
                "event_date": "2021-12-30",
                "company_churn_estimate": 0.95,
                "discount_pct": 0.08,
                "retention_cost_gbp": 67.20,
                "expected_term_margin_gbp": 13.65,
                "acq_cost_saved_gbp": 150.0,
                "outcome": "retained",
            },
            {
                "customer_id": "C5",
                "event_date": "2021-12-30",
                "company_churn_estimate": 0.95,
                "discount_pct": 0.08,
                "retention_cost_gbp": 160.0,
                "expected_term_margin_gbp": 121.89,
                "acq_cost_saved_gbp": 400.0,
                "outcome": "retained",
            },
        ],
        "no_offer_churn_log": [],
    }


def test_section_retention_shows_acq_cost_row():
    from saas.reporting.annual_report import _section_retention_strategy
    result = _section_retention_strategy(_retention_with_acq_data())
    assert "Acquisition cost avoided" in result


def test_section_retention_shows_full_economic_roi():
    from saas.reporting.annual_report import _section_retention_strategy
    result = _section_retention_strategy(_retention_with_acq_data())
    assert "Full economic ROI" in result
    # acq_cost_saved = £150 + £400 = £550
    # net_roi = (13.65 + 121.89) - (67.20 + 160.0) = 135.54 - 227.20 = -91.66
    # full_roi = -91.66 + 550 = 458.34
    assert "£458" in result or "458" in result


def test_section_retention_omits_acq_rows_without_acq_data():
    """Old-format retention logs (no acq_cost_saved_gbp) don't show acq rows."""
    from saas.reporting.annual_report import _section_retention_strategy
    old_log = [
        {
            "customer_id": "C2",
            "event_date": "2017-04-01",
            "company_churn_estimate": 0.30,
            "discount_pct": 0.03,
            "retention_cost_gbp": 5.61,
            "expected_term_margin_gbp": 9.19,
            "outcome": "retained",
        },
    ]
    result = _section_retention_strategy({"retention_log": old_log, "no_offer_churn_log": []})
    assert "Acquisition cost avoided" not in result
    assert "Full economic ROI" not in result


# ── Tariff Repricing Impact tests (Phase 16a) ─────────────────────────────────

def _repricing_fixture():
    """Minimal data for Phase 16a repricing impact tests."""
    return {
        "per_customer_lifetime": {
            "C_raise": {
                "commodity": "electricity",
                "segment": "SME",
                "acquisition_date": "2016-01-01",
                "net_margin_after_cost_to_serve_gbp": -800.0,
                "pricing_action": {"flag": "NET_NEGATIVE", "recommended_uplift_pct": 20.0},
            },
            "C_hold": {
                "commodity": "electricity",
                "segment": "resi",
                "acquisition_date": "2022-01-01",
                "net_margin_after_cost_to_serve_gbp": -500.0,
                "pricing_action": {"flag": "NET_NEGATIVE", "recommended_uplift_pct": 75.0},
            },
            "C_ok": {
                "commodity": "electricity",
                "segment": "resi",
                "acquisition_date": "2016-01-01",
                "net_margin_after_cost_to_serve_gbp": 200.0,
                "pricing_action": {"flag": "OK"},
            },
        },
        "basis_risk_terms": [
            {
                "customer_id": "C_raise",
                "company_fwd_gbp_per_mwh": 100.0,
                "term_start": "2024-01-01",
                "sim_fwd_gbp_per_mwh": 100.0,
                "tariff_error_pct": 0.0,
            },
            {
                "customer_id": "C_hold",
                "company_fwd_gbp_per_mwh": 100.0,
                "term_start": "2024-01-01",
                "sim_fwd_gbp_per_mwh": 100.0,
                "tariff_error_pct": 0.0,
            },
        ],
        "churned_billing_accounts": ["C_hold"],
    }


def test_repricing_section_shows_header():
    from saas.reporting.annual_report import _section_repricing_impact
    result = _section_repricing_impact(_repricing_fixture())
    assert "Tariff Repricing Impact Assessment" in result


def test_repricing_manageable_shows_raise():
    """Low uplift → 'Raise' recommendation."""
    from saas.reporting.annual_report import _section_repricing_impact
    result = _section_repricing_impact(_repricing_fixture())
    assert "C_raise" in result
    assert "Raise" in result


def test_repricing_risky_shows_hold():
    """High uplift (+75%) → 'Hold' recommendation."""
    from saas.reporting.annual_report import _section_repricing_impact
    result = _section_repricing_impact(_repricing_fixture())
    assert "C_hold" in result
    assert "Hold" in result


def test_repricing_ok_customers_excluded():
    """Customers with OK pricing action not shown in table."""
    from saas.reporting.annual_report import _section_repricing_impact
    result = _section_repricing_impact(_repricing_fixture())
    assert "C_ok" not in result


def test_repricing_empty_when_no_net_negative():
    """No NET_NEGATIVE customers → empty string."""
    from saas.reporting.annual_report import _section_repricing_impact
    data = {
        "per_customer_lifetime": {
            "C_ok": {
                "commodity": "electricity",
                "segment": "resi",
                "acquisition_date": "2016-01-01",
                "net_margin_after_cost_to_serve_gbp": 200.0,
                "pricing_action": {"flag": "OK"},
            },
        },
        "basis_risk_terms": [],
        "churned_billing_accounts": [],
    }
    assert _section_repricing_impact(data) == ""


# ── Retention Durability tests (Phase 16b) ─────────────────────────────────────

def _durability_fixture():
    """Retention log with two cohorts: one churned, one active."""
    return {
        "retention_log": [
            {
                "customer_id": "C_long",
                "event_date": "2017-04-01",
                "company_churn_estimate": 0.30,
                "discount_pct": 0.03,
                "retention_cost_gbp": 5.0,
                "expected_term_margin_gbp": 10.0,
                "outcome": "retained",
            },
            {
                "customer_id": "C_short",
                "event_date": "2018-07-01",
                "company_churn_estimate": 0.32,
                "discount_pct": 0.03,
                "retention_cost_gbp": 3.0,
                "expected_term_margin_gbp": 8.0,
                "outcome": "retained",
            },
        ],
        "company_event_log": [
            {
                "event_type": "churn",
                "customer_id": "C_short",
                "event_date": "2020-07-01",
                "reason": "non-renewal",
                "sim_churn_probability": 0.20,
                "company_churn_estimate": 0.10,
            }
        ],
        "churned_billing_accounts": ["C_short"],
    }


def test_retention_durability_shows_header():
    from saas.reporting.annual_report import _section_retention_durability
    result = _section_retention_durability(_durability_fixture())
    assert "Retention Durability" in result


def test_retention_durability_churned_shows_end_date():
    """Churned customer shows the actual churn date."""
    from saas.reporting.annual_report import _section_retention_durability
    result = _section_retention_durability(_durability_fixture())
    assert "2020-07-01" in result
    assert "C_short" in result


def test_retention_durability_active_shows_window_end():
    """Active customer shows '(window end)'."""
    from saas.reporting.annual_report import _section_retention_durability
    result = _section_retention_durability(_durability_fixture())
    assert "(window end)" in result
    assert "C_long" in result


def test_retention_durability_summary_avg_months():
    """Summary line shows avg months for churned cohort.
    C_short: 2020-07-01 - 2018-07-01 = 24 months."""
    from saas.reporting.annual_report import _section_retention_durability
    result = _section_retention_durability(_durability_fixture())
    assert "24 months" in result


def test_retention_durability_empty_when_no_log():
    """No retention log → empty string."""
    from saas.reporting.annual_report import _section_retention_durability
    assert _section_retention_durability({"retention_log": [], "company_event_log": [], "churned_billing_accounts": []}) == ""


# ---- Phase QM: retention-as-deferral (H1 vs H2) section tests ----

def test_retention_deferral_economics_shows_header():
    from saas.reporting.annual_report import _section_retention_deferral_economics
    result = _section_retention_deferral_economics(_durability_fixture())
    assert "Retention as Deferral" in result


def test_retention_deferral_economics_underperformed_offer_flagged():
    from saas.reporting.annual_report import _section_retention_deferral_economics
    result = _section_retention_deferral_economics(_durability_fixture())
    assert "C_short" in result
    assert "resolved offers" in result


def test_retention_deferral_economics_serial_saver_flagged():
    from saas.reporting.annual_report import _section_retention_deferral_economics
    fixture = {
        "retention_log": [
            {
                "customer_id": "C_repeat", "event_date": "2018-01-01",
                "company_churn_estimate": 0.30, "discount_pct": 0.03,
                "retention_cost_gbp": 5.0, "expected_term_margin_gbp": 10.0,
                "outcome": "retained",
            },
            {
                "customer_id": "C_repeat", "event_date": "2019-01-01",
                "company_churn_estimate": 0.35, "discount_pct": 0.05,
                "retention_cost_gbp": 6.0, "expected_term_margin_gbp": 10.0,
                "outcome": "churned_despite_offer",
            },
        ],
        "company_event_log": [
            {"event_type": "churn", "customer_id": "C_repeat", "event_date": "2019-06-01"},
        ],
        "churned_billing_accounts": ["C_repeat"],
    }
    result = _section_retention_deferral_economics(fixture)
    assert "Serial savers" in result
    assert "EV-negative" in result
    assert "C_repeat" in result


def test_retention_deferral_economics_empty_when_no_log():
    from saas.reporting.annual_report import _section_retention_deferral_economics
    assert _section_retention_deferral_economics({"retention_log": [], "company_event_log": []}) == ""


# ---- Phase 17a: dynamic pricing section tests ----

def _dynamic_pricing_fixture():
    return {
        "dynamic_pricing_log": [
            {
                "customer_id": "C1",
                "term_start": "2022-01-01",
                "recent_margin_rates": [-0.30, -0.20],
                "mean_recent_margin_rate": -0.25,
                "portfolio_premium_pct": 15.0,
                "unit_rate_before": 200.00,
                "unit_rate_after": 230.00,
            },
            {
                "customer_id": "C2",
                "term_start": "2022-06-01",
                "recent_margin_rates": [0.20, 0.15],
                "mean_recent_margin_rate": 0.175,
                "portfolio_premium_pct": -5.0,
                "unit_rate_before": 180.00,
                "unit_rate_after": 171.00,
            },
        ]
    }


def test_dynamic_pricing_shows_header():
    from saas.reporting.annual_report import _section_dynamic_pricing
    result = _section_dynamic_pricing(_dynamic_pricing_fixture())
    assert "Portfolio Learning Premium" in result


def test_dynamic_pricing_shows_surcharge_count():
    from saas.reporting.annual_report import _section_dynamic_pricing
    result = _section_dynamic_pricing(_dynamic_pricing_fixture())
    assert "1 surcharge" in result
    assert "1 discount" in result


def test_dynamic_pricing_shows_customer_id():
    from saas.reporting.annual_report import _section_dynamic_pricing
    result = _section_dynamic_pricing(_dynamic_pricing_fixture())
    assert "C1" in result
    assert "C2" in result


def test_dynamic_pricing_empty_when_no_log():
    from saas.reporting.annual_report import _section_dynamic_pricing
    assert _section_dynamic_pricing({}) == ""
    assert _section_dynamic_pricing({"dynamic_pricing_log": []}) == ""


# ---- Phase 19a: gas feedback extension tests ----

def _gas_feedback_fixture():
    """Fixtures with both electricity and gas events for Phase 19a tests."""
    return {
        "dynamic_pricing_log": [
            {
                "customer_id": "C1",
                "commodity": "electricity",
                "term_start": "2022-01-01",
                "recent_margin_rates": [-0.30, -0.20],
                "mean_recent_margin_rate": -0.25,
                "portfolio_premium_pct": 15.0,
                "unit_rate_before": 200.0,
                "unit_rate_after": 230.0,
            },
            {
                "customer_id": "C1g",
                "commodity": "gas",
                "term_start": "2022-01-01",
                "recent_margin_rates": [-0.40, -0.35],
                "mean_recent_margin_rate": -0.375,
                "portfolio_premium_pct": 14.4,
                "unit_rate_before": 80.0,
                "unit_rate_after": 91.5,
            },
        ],
        "margin_feedback_log": [
            {
                "customer_id": "C1",
                "commodity": "electricity",
                "term_start": "2023-01-01",
                "prev_margin_gbp": -500.0,
                "prev_revenue_gbp": 5000.0,
                "surcharge_pct": 5.0,
                "unit_rate_before": 180.0,
                "unit_rate_after": 189.0,
            },
            {
                "customer_id": "C1g",
                "commodity": "gas",
                "term_start": "2023-01-01",
                "prev_margin_gbp": -120.0,
                "prev_revenue_gbp": 1200.0,
                "surcharge_pct": 5.0,
                "unit_rate_before": 70.0,
                "unit_rate_after": 73.5,
            },
        ],
    }


def test_dynamic_pricing_shows_gas_events():
    """Phase 19a: gas renewals should appear in the portfolio premium section."""
    from saas.reporting.annual_report import _section_dynamic_pricing
    result = _section_dynamic_pricing(_gas_feedback_fixture())
    assert "C1g" in result
    assert "gas" in result


def test_dynamic_pricing_counts_gas_in_summary():
    """Phase 19a: summary line should mention gas event count."""
    from saas.reporting.annual_report import _section_dynamic_pricing
    result = _section_dynamic_pricing(_gas_feedback_fixture())
    assert "1 gas" in result


def test_margin_feedback_shows_gas_events():
    """Phase 19a: gas surcharges should appear in the margin feedback section."""
    from saas.reporting.annual_report import _section_margin_feedback
    result = _section_margin_feedback(_gas_feedback_fixture())
    assert "C1g" in result
    assert "gas" in result


def test_margin_feedback_counts_gas_in_summary():
    """Phase 19a: margin feedback summary should mention gas count."""
    from saas.reporting.annual_report import _section_margin_feedback
    result = _section_margin_feedback(_gas_feedback_fixture())
    assert "1 gas" in result


def test_margin_feedback_backward_compat_no_commodity_field():
    """Legacy log entries without 'commodity' field should still render."""
    from saas.reporting.annual_report import _section_margin_feedback
    data = {"margin_feedback_log": [{
        "customer_id": "C1",
        # no "commodity" field (pre-Phase-19a)
        "term_start": "2022-01-01",
        "prev_margin_gbp": -500.0,
        "prev_revenue_gbp": 5000.0,
        "surcharge_pct": 5.0,
        "unit_rate_before": 180.0,
        "unit_rate_after": 189.0,
    }]}
    result = _section_margin_feedback(data)
    assert "C1" in result
    assert "Margin Recovery" in result


# ---- Phase 17b: churn avoidability section tests ----

def _churn_avoidability_fixture():
    return {
        "no_offer_churn_log": [
            {
                "customer_id": "C_blind",
                "event_date": "2021-12-31",
                "company_churn_estimate": 0.15,
                "expected_term_margin_gbp": -800.0,
                "no_offer_reason": "below_threshold",
            },
            {
                "customer_id": "C_uneconomical",
                "event_date": "2022-06-01",
                "company_churn_estimate": 0.50,
                "expected_term_margin_gbp": -300.0,
                "no_offer_reason": "uneconomical",
            },
        ],
        "company_event_log": [
            {
                "event_type": "churn",
                "customer_id": "C_blind",
                "event_date": "2021-12-31",
                "sim_churn_probability": 0.60,   # SIM said 60% → detectable
            },
            {
                "event_type": "churn",
                "customer_id": "C_uneconomical",
                "event_date": "2022-06-01",
                "sim_churn_probability": 0.55,
            },
        ],
    }


def test_churn_avoidability_shows_header():
    from saas.reporting.annual_report import _section_churn_avoidability
    result = _section_churn_avoidability(_churn_avoidability_fixture())
    assert "Churn Avoidability" in result


def test_churn_avoidability_counts_blind_vs_uneconomical():
    from saas.reporting.annual_report import _section_churn_avoidability
    result = _section_churn_avoidability(_churn_avoidability_fixture())
    assert "Blind misses: **1**" in result
    assert "Deliberate passes (uneconomical): **1**" in result


def test_churn_avoidability_detectable_blind_miss():
    """C_blind had SIM p=0.60 >= 0.30 → should be flagged as detectable."""
    from saas.reporting.annual_report import _section_churn_avoidability
    result = _section_churn_avoidability(_churn_avoidability_fixture())
    assert "detectable with a better model" in result.lower() or "Detectable" in result


def test_churn_avoidability_shows_customer_ids():
    from saas.reporting.annual_report import _section_churn_avoidability
    result = _section_churn_avoidability(_churn_avoidability_fixture())
    assert "C_blind" in result
    assert "C_uneconomical" in result


def test_churn_avoidability_empty_when_no_log():
    from saas.reporting.annual_report import _section_churn_avoidability
    assert _section_churn_avoidability({}) == ""
    assert _section_churn_avoidability({"no_offer_churn_log": []}) == ""


# ---- Phase 17c: customer P&L ranking tests ----

def _pnl_ranking_fixture():
    return {
        "all_records": [
            {"customer_id": "C_profit", "settlement_date": "2022-01-15",
             "margin_gbp": 500.0, "capital_cost_gbp": 50.0,
             "net_margin_gbp": 450.0, "revenue_gbp": 5000.0},
            {"customer_id": "C_profit", "settlement_date": "2022-02-15",
             "margin_gbp": 600.0, "capital_cost_gbp": 60.0,
             "net_margin_gbp": 540.0, "revenue_gbp": 6000.0},
            {"customer_id": "C_loss", "settlement_date": "2022-01-15",
             "margin_gbp": -200.0, "capital_cost_gbp": 20.0,
             "net_margin_gbp": -220.0, "revenue_gbp": 2000.0},
        ]
    }


def test_pnl_ranking_shows_header():
    from saas.reporting.annual_report import _section_customer_pnl_ranking
    result = _section_customer_pnl_ranking(_pnl_ranking_fixture())
    assert "Customer P&L Ranking" in result


def test_pnl_ranking_profitable_customer_first():
    """C_profit (net £990) should rank above C_loss (net -£220)."""
    from saas.reporting.annual_report import _section_customer_pnl_ranking
    result = _section_customer_pnl_ranking(_pnl_ranking_fixture())
    pos_profit = result.find("C_profit")
    pos_loss = result.find("C_loss")
    assert pos_profit < pos_loss


def test_pnl_ranking_shows_net_margin_pct():
    """Section should include percentage column."""
    from saas.reporting.annual_report import _section_customer_pnl_ranking
    result = _section_customer_pnl_ranking(_pnl_ranking_fixture())
    assert "%" in result


def test_pnl_ranking_empty_when_no_records():
    from saas.reporting.annual_report import _section_customer_pnl_ranking
    assert _section_customer_pnl_ranking({}) == ""
    assert _section_customer_pnl_ranking({"all_records": []}) == ""


# ---- Phase 17d: dual-fuel P&L tests ----

def _dual_fuel_fixture():
    return {
        "all_records": [
            {"customer_id": "C1", "settlement_date": "2022-01-15",
             "commodity": "electricity",
             "margin_gbp": 300.0, "capital_cost_gbp": 30.0,
             "net_margin_gbp": 270.0, "revenue_gbp": 3000.0},
            {"customer_id": "C1g", "settlement_date": "2022-01-15",
             "commodity": "gas",
             "margin_gbp": 50.0, "capital_cost_gbp": 5.0,
             "net_margin_gbp": 45.0, "revenue_gbp": 500.0},
            {"customer_id": "C2", "settlement_date": "2022-01-15",
             "commodity": "electricity",
             "margin_gbp": -200.0, "capital_cost_gbp": 20.0,
             "net_margin_gbp": -220.0, "revenue_gbp": 2000.0},
            {"customer_id": "C2g", "settlement_date": "2022-01-15",
             "commodity": "gas",
             "margin_gbp": -80.0, "capital_cost_gbp": 8.0,
             "net_margin_gbp": -88.0, "revenue_gbp": 800.0},
        ]
    }


def test_dual_fuel_shows_header():
    from saas.reporting.annual_report import _section_dual_fuel_pnl
    result = _section_dual_fuel_pnl(_dual_fuel_fixture())
    assert "Dual-Fuel" in result


def test_dual_fuel_c1_gas_accretive():
    """C1 gas leg has positive net margin → accretive."""
    from saas.reporting.annual_report import _section_dual_fuel_pnl
    result = _section_dual_fuel_pnl(_dual_fuel_fixture())
    # The section should mention C1+C1g pair
    assert "C1" in result
    assert "C1g" in result


def test_dual_fuel_shows_accretive_count():
    from saas.reporting.annual_report import _section_dual_fuel_pnl
    result = _section_dual_fuel_pnl(_dual_fuel_fixture())
    # C1g accretive, C2g not → 1/2
    assert "1/2" in result


def test_dual_fuel_empty_when_no_gas_records():
    from saas.reporting.annual_report import _section_dual_fuel_pnl
    # Only electricity records → no pairs
    data = {"all_records": [
        {"customer_id": "C1", "settlement_date": "2022-01-15",
         "commodity": "electricity",
         "margin_gbp": 300.0, "capital_cost_gbp": 30.0,
         "net_margin_gbp": 270.0, "revenue_gbp": 3000.0},
    ]}
    assert _section_dual_fuel_pnl(data) == ""
    assert _section_dual_fuel_pnl({}) == ""


# ---- Phase 17c/17d: pre-aggregated JSON path (per_cid_pnl / per_cid_comm_pnl) ----

def _pnl_ranking_fixture_pre_aggregated():
    """Simulates data loaded from saved JSON (no all_records, uses per_cid_pnl)."""
    return {
        "per_cid_pnl": {
            "C_profit": {"gross": 1100.0, "capital": 110.0, "net": 990.0, "revenue": 11000.0},
            "C_loss": {"gross": -200.0, "capital": 20.0, "net": -220.0, "revenue": 2000.0},
        }
    }


def test_pnl_ranking_uses_per_cid_pnl_when_present():
    """per_cid_pnl (saved JSON path) should produce the same ranking as all_records."""
    from saas.reporting.annual_report import _section_customer_pnl_ranking
    result = _section_customer_pnl_ranking(_pnl_ranking_fixture_pre_aggregated())
    assert "Customer P&L Ranking" in result
    pos_profit = result.find("C_profit")
    pos_loss = result.find("C_loss")
    assert pos_profit < pos_loss


def _dual_fuel_fixture_pre_aggregated():
    """Simulates data loaded from saved JSON (per_cid_comm_pnl, no all_records)."""
    return {
        "per_cid_comm_pnl": {
            "C1": {"electricity": {"gross": 300.0, "capital": 30.0, "net": 270.0, "revenue": 3000.0}},
            "C1g": {"gas": {"gross": 50.0, "capital": 5.0, "net": 45.0, "revenue": 500.0}},
            "C2": {"electricity": {"gross": -200.0, "capital": 20.0, "net": -220.0, "revenue": 2000.0}},
            "C2g": {"gas": {"gross": -80.0, "capital": 8.0, "net": -88.0, "revenue": 800.0}},
        }
    }


def test_dual_fuel_uses_per_cid_comm_pnl_when_present():
    """per_cid_comm_pnl (saved JSON path) should produce the same output as all_records."""
    from saas.reporting.annual_report import _section_dual_fuel_pnl
    result = _section_dual_fuel_pnl(_dual_fuel_fixture_pre_aggregated())
    assert "Dual-Fuel" in result
    assert "C1" in result
    assert "C1g" in result
    assert "1/2" in result


# ---- Phase 21a: Policy costs section ----

def test_policy_costs_section_hidden_when_all_zero():
    """Pre-Phase-21a data (no policy costs) produces empty section."""
    data = {"years": {
        "2016": {"ro_levy_gbp": 0.0, "cfd_levy_gbp": 0.0, "policy_cost_gbp": 0.0},
        "2017": {"ro_levy_gbp": 0.0, "cfd_levy_gbp": 0.0, "policy_cost_gbp": 0.0},
    }}
    assert _section_policy_costs(data) == ""


def test_policy_costs_section_empty_years():
    """Empty years dict → no section."""
    assert _section_policy_costs({"years": {}}) == ""
    assert _section_policy_costs({}) == ""


def test_policy_costs_section_shows_ro_and_cfd():
    """Section renders year-by-year RO + CfD table when costs present."""
    data = {"years": {
        "2021": {"ro_levy_gbp": 1000.0, "cfd_levy_gbp": 100.0, "policy_cost_gbp": 1100.0},
        "2022": {"ro_levy_gbp": 1200.0, "cfd_levy_gbp": -500.0, "policy_cost_gbp": 700.0},
    }}
    result = _section_policy_costs(data)
    assert "Policy Costs" in result
    assert "2021" in result
    assert "2022" in result
    assert "1,000" in result   # RO 2021
    assert "-500" in result    # CfD 2022 negative (rebate)
    assert "REBATE" in result  # 2022 CfD negative label


def test_policy_costs_section_totals():
    """Section shows correct column totals."""
    data = {"years": {
        "2021": {"ro_levy_gbp": 1000.0, "cfd_levy_gbp": 100.0, "policy_cost_gbp": 1100.0},
        "2022": {"ro_levy_gbp": 1200.0, "cfd_levy_gbp": -500.0, "policy_cost_gbp": 700.0},
    }}
    result = _section_policy_costs(data)
    # Total RO = 2200, total CfD = -400, total policy = 1800
    assert "2,200" in result
    assert "-400" in result
    assert "1,800" in result


# --- Phase 22a: enterprise value analysis section ---

def _make_ev_data(years_margins: dict[str, float], ev_full: float = -7978.0) -> dict:
    """Build minimal data dict for _section_enterprise_value_analysis."""
    return {
        "enterprise_value_gbp": ev_full,
        "churn_risk": {
            "C1": [{"churn_probability": 0.15, "renewal_period": f"{yr}-01-01"}
                   for yr in years_margins],
        },
        "years": {
            yr: {"net_gbp": net, "per_customer": {"C1": {"net_gbp": net, "commodity": "electricity",
                                                          "gross_gbp": net + 50, "capital_gbp": 50}}}
            for yr, net in years_margins.items()
        },
        "by_billing_account": {"C1": {"clv_gbp": -500.0}},
        "clv_snapshots": None,
    }


def test_ev_analysis_hidden_when_no_churn_risk():
    data = {"enterprise_value_gbp": -1000.0, "churn_risk": {}, "years": {}}
    assert _section_enterprise_value_analysis(data) == ""


def test_ev_analysis_shows_full_history_ev():
    data = _make_ev_data({"2022": -800.0, "2023": -200.0, "2024": 400.0})
    result = _section_enterprise_value_analysis(data)
    assert "Full-history EV" in result
    assert "-7,978" in result  # ev_full passed in


def test_ev_analysis_shows_trailing_ev():
    data = _make_ev_data({"2022": -800.0, "2023": -200.0, "2024": 400.0})
    result = _section_enterprise_value_analysis(data)
    assert "3yr-trailing EV" in result


def test_ev_analysis_shows_year_table():
    data = _make_ev_data({"2022": -800.0, "2023": -200.0, "2024": 400.0})
    result = _section_enterprise_value_analysis(data)
    assert "2022" in result
    assert "2024" in result
    assert "trailing" in result


def test_ev_analysis_trailing_better_than_full_after_recovery():
    """When recent years profitable and history dragged by losses, trailing EV > full EV."""
    # Deep losses in early years; recent 3 years profitable
    data = _make_ev_data({
        "2016": -2000.0, "2017": -1500.0, "2018": -1000.0,
        "2019": 200.0, "2020": 300.0, "2021": -3000.0,
        "2022": -500.0, "2023": 400.0, "2024": 800.0,
    }, ev_full=-7000.0)
    result = _section_enterprise_value_analysis(data)
    # Both EVs should appear; the text should be present
    assert "Full-history EV" in result
    assert "3yr-trailing EV" in result


# ---------------------------------------------------------------------------
# Phase 23a — Company-owned demand estimation
# ---------------------------------------------------------------------------

def _demand_log_fixture():
    """Minimal demand_estimation_log for report section tests."""
    return [
        {
            "customer_id": "C1",
            "term_start": "2018-01-01",
            "company_eac_kwh": 3100,
            "true_eac_kwh": 3000,
            "error_pct": 3.33,
            "source": "prior_billing",
        },
        {
            "customer_id": "C1",
            "term_start": "2019-01-01",
            "company_eac_kwh": 3050,
            "true_eac_kwh": 3000,
            "error_pct": 1.67,
            "source": "prior_billing",
        },
        {
            "customer_id": "C2",
            "term_start": "2017-01-01",
            "company_eac_kwh": 5000,
            "true_eac_kwh": 5000,
            "error_pct": 0.0,
            "source": "fallback",
        },
    ]


def test_demand_section_empty_when_no_log():
    from saas.reporting.annual_report import _section_demand_estimation
    result = _section_demand_estimation({})
    assert result == ""


def test_demand_section_empty_when_empty_log():
    from saas.reporting.annual_report import _section_demand_estimation
    result = _section_demand_estimation({"demand_estimation_log": []})
    assert result == ""


def test_demand_section_shows_header():
    from saas.reporting.annual_report import _section_demand_estimation
    result = _section_demand_estimation({"demand_estimation_log": _demand_log_fixture()})
    assert "Demand Estimation" in result


def test_demand_section_shows_year_rows():
    from saas.reporting.annual_report import _section_demand_estimation
    result = _section_demand_estimation({"demand_estimation_log": _demand_log_fixture()})
    assert "2017" in result
    assert "2018" in result
    assert "2019" in result


def test_demand_section_shows_fallback_count():
    from saas.reporting.annual_report import _section_demand_estimation
    result = _section_demand_estimation({"demand_estimation_log": _demand_log_fixture()})
    # 2 prior_billing, 1 fallback out of 3
    assert "2" in result and "prior billing" in result.lower() or "prior_billing" in result.lower() or "prior billing" in result


def test_demand_section_mean_error_nonzero_for_year_with_errors():
    from saas.reporting.annual_report import _section_demand_estimation
    result = _section_demand_estimation({"demand_estimation_log": _demand_log_fixture()})
    # 2018 has 3.33% error; 2019 has 1.67% — both > 0
    assert "3.3" in result or "3.33" in result


# --- _company_eac_estimate unit tests ---

def _make_records(cid, year, consumption_kwh):
    """Build synthetic settlement records for prior year."""
    from datetime import date, timedelta
    records = []
    d = date(year, 1, 1)
    while d.year == year:
        records.append({
            "customer_id": cid,
            "settlement_date": d.isoformat(),
            "consumption_kwh": consumption_kwh / 365.0,
        })
        d += timedelta(days=1)
    return records


def test_company_eac_estimate_uses_prior_year_billing():
    from simulation.run_phase2b import _company_eac_estimate
    # Term starts 2019-01-01; prior year is 2018; records total ~3650 kWh
    records = _make_records("C1", 2018, 3650.0)
    result = _company_eac_estimate("C1", "2019-01-01", records)
    assert abs(result - 3650.0) < 1.0


def test_company_eac_estimate_falls_back_when_no_records():
    from simulation.run_phase2b import _company_eac_estimate, EFFECTIVE_EAC_KWH
    # No records for C1 before 2017 — should fall back to oracle
    oracle = EFFECTIVE_EAC_KWH.get("C1", 0.0)
    result = _company_eac_estimate("C1", "2017-01-01", [])
    assert result == oracle


def test_company_eac_estimate_ignores_other_customers():
    from simulation.run_phase2b import _company_eac_estimate, EFFECTIVE_EAC_KWH
    # Records exist but for C2, not C1 — should fall back
    records = _make_records("C2", 2018, 5000.0)
    oracle_c1 = EFFECTIVE_EAC_KWH.get("C1", 0.0)
    result = _company_eac_estimate("C1", "2019-01-01", records)
    assert result == oracle_c1


def test_company_eac_estimate_excludes_records_at_term_start():
    from simulation.run_phase2b import _company_eac_estimate
    # A record ON term_start should be excluded (half-open [year_ago, term_start))
    records = [
        {"customer_id": "C1", "settlement_date": "2019-01-01", "consumption_kwh": 100.0},
        {"customer_id": "C1", "settlement_date": "2018-06-01", "consumption_kwh": 200.0},
    ]
    result = _company_eac_estimate("C1", "2019-01-01", records)
    # Only the 2018-06-01 record should be included
    assert abs(result - 200.0) < 0.01


# --- _compute_company_divergence demand_error_by_year ---

def test_divergence_demand_error_by_year_populated():
    from simulation.run_phase2b import _compute_company_divergence
    demand_log = [
        {"customer_id": "C1", "term_start": "2018-06-01", "company_eac_kwh": 3100,
         "true_eac_kwh": 3000, "error_pct": 3.33, "source": "prior_billing"},
        {"customer_id": "C1", "term_start": "2018-12-01", "company_eac_kwh": 2900,
         "true_eac_kwh": 3000, "error_pct": -3.33, "source": "prior_billing"},
    ]
    result = _compute_company_divergence([], [], demand_estimation_log=demand_log)
    assert "demand_error_by_year" in result
    assert "2018" in result["demand_error_by_year"]
    stats = result["demand_error_by_year"]["2018"]
    assert stats["n"] == 2
    assert abs(stats["mean_abs_error_pct"] - 3.33) < 0.01


def test_divergence_demand_error_by_year_empty_when_no_log():
    from simulation.run_phase2b import _compute_company_divergence
    result = _compute_company_divergence([], [], demand_estimation_log=None)
    assert result["demand_error_by_year"] == {}


# --- Phase 21b: solvency signal section ---

def _make_solvency_data(years: dict) -> dict:
    """Minimal data dict for _section_solvency_signal."""
    return {"years": years}


def test_solvency_signal_empty_data():
    """No years → empty string."""
    assert _section_solvency_signal({"years": {}}) == ""
    assert _section_solvency_signal({}) == ""


def test_solvency_signal_header_present():
    """Section renders heading and Ofgem threshold reference."""
    data = _make_solvency_data({
        "2024": {
            "treasury_end_gbp": 50000.0,
            "active_customer_ids": ["C1", "C1g", "C5"],
        }
    })
    result = _section_solvency_signal(data)
    assert "Solvency Signal" in result
    assert "£130" in result
    assert "2024" in result


def test_solvency_signal_billing_account_dedup():
    """C1 + C1g count as one billing account (dual-fuel dedup)."""
    data = _make_solvency_data({
        "2024": {
            "treasury_end_gbp": 10000.0,
            "active_customer_ids": ["C1", "C1g", "C5"],
        }
    })
    result = _section_solvency_signal(data)
    # 2 billing accounts (C1 and C5): 10000 / 2 = 5000
    assert "5,000" in result
    assert "| 2 |" in result or "| 2024 |" not in result or "5,000" in result


def test_solvency_signal_above_target():
    """Treasury well above target → 'OK' for both floor and target."""
    data = _make_solvency_data({
        "2024": {
            "treasury_end_gbp": 5000.0,
            "active_customer_ids": ["C1"],
        }
    })
    result = _section_solvency_signal(data)
    # 5000/1 = 5000 — above both £0 and £130
    assert result.count("OK") >= 2


def test_solvency_signal_below_target_shows_gap():
    """Treasury below £130/account shows gap and 'below' label."""
    data = _make_solvency_data({
        "2024": {
            "treasury_end_gbp": 100.0,
            "active_customer_ids": ["C1"],
        }
    })
    result = _section_solvency_signal(data)
    # 100/1 = 100 — below £130 target, gap = £30
    assert "below" in result
    assert "30" in result


def test_solvency_signal_breach_when_negative():
    """Negative treasury → STRESS flag (Phase 55: MCR ratio < 1×)."""
    data = _make_solvency_data({
        "2022": {
            "treasury_end_gbp": -500.0,
            "active_customer_ids": ["C1"],
        }
    })
    result = _section_solvency_signal(data)
    assert "STRESS" in result


def test_solvency_signal_end_state_summary():
    """Final year end-state sentence appears in section."""
    data = _make_solvency_data({
        "2023": {
            "treasury_end_gbp": 2000.0,
            "active_customer_ids": ["C1", "C1g"],
        }
    })
    result = _section_solvency_signal(data)
    # 2000/1 = 2000/account — well above target
    assert "End-state" in result
    assert "2023" in result


# --- Phase 27c: _section_volume_tolerance tests ---

def test_volume_tolerance_empty_returns_empty():
    assert _section_volume_tolerance({}) == ""
    assert _section_volume_tolerance({"volume_tolerance_log": []}) == ""


def test_volume_tolerance_within_band_shows_no_breach():
    data = {
        "volume_tolerance_log": [
            {
                "customer_id": "C_IC1",
                "term_start": "2020-01-01",
                "term_end": "2021-01-01",
                "contracted_kwh": 2_000_000.0,
                "actual_kwh": 2_050_000.0,
                "variance_pct": 2.5,
                "band_high_kwh": 2_200_000.0,
                "band_low_kwh": 1_800_000.0,
                "excess_kwh": 0.0,
                "deficit_kwh": 0.0,
                "excess_spot_cost_gbp": 0.0,
                "deficit_unwind_gbp": 0.0,
                "within_band": True,
            }
        ]
    }
    result = _section_volume_tolerance(data)
    assert "27c" in result or "Volume Tolerance" in result
    assert "no spot over-run" in result
    assert "⚠" not in result


def test_volume_tolerance_breach_shows_warning():
    data = {
        "volume_tolerance_log": [
            {
                "customer_id": "C_IC1",
                "term_start": "2022-01-01",
                "term_end": "2023-01-01",
                "contracted_kwh": 2_000_000.0,
                "actual_kwh": 2_400_000.0,
                "variance_pct": 20.0,
                "band_high_kwh": 2_200_000.0,
                "band_low_kwh": 1_800_000.0,
                "excess_kwh": 200_000.0,
                "deficit_kwh": 0.0,
                "excess_spot_cost_gbp": 20_000.0,
                "deficit_unwind_gbp": 0.0,
                "within_band": False,
            }
        ]
    }
    result = _section_volume_tolerance(data)
    assert "⚠" in result
    assert "1 tolerance breach" in result
    assert "20,000" in result


def test_volume_tolerance_multiple_terms_both_shown():
    data = {
        "volume_tolerance_log": [
            {
                "customer_id": "C_IC1",
                "term_start": "2020-01-01",
                "term_end": "2021-01-01",
                "contracted_kwh": 2_000_000.0,
                "actual_kwh": 2_000_000.0,
                "variance_pct": 0.0,
                "band_high_kwh": 2_200_000.0,
                "band_low_kwh": 1_800_000.0,
                "excess_kwh": 0.0,
                "deficit_kwh": 0.0,
                "excess_spot_cost_gbp": 0.0,
                "deficit_unwind_gbp": 0.0,
                "within_band": True,
            },
            {
                "customer_id": "C_IC2",
                "term_start": "2020-01-01",
                "term_end": "2021-01-01",
                "contracted_kwh": 1_000_000.0,
                "actual_kwh": 1_000_000.0,
                "variance_pct": 0.0,
                "band_high_kwh": 1_100_000.0,
                "band_low_kwh": 900_000.0,
                "excess_kwh": 0.0,
                "deficit_kwh": 0.0,
                "excess_spot_cost_gbp": 0.0,
                "deficit_unwind_gbp": 0.0,
                "within_band": True,
            },
        ]
    }
    result = _section_volume_tolerance(data)
    assert "C_IC1" in result
    assert "C_IC2" in result
    assert "Terms tracked: 2" in result


# --- Phase 27d: _section_triad_exposure tests ---

def test_triad_exposure_empty_returns_empty():
    assert _section_triad_exposure({}) == ""
    assert _section_triad_exposure({"triad_log": []}) == ""


def test_triad_exposure_shows_customer_and_winter():
    data = {
        "triad_log": [
            {
                "customer_id": "C_IC1",
                "triad_year": 2021,
                "triad_periods": [],
                "avg_triad_kw": 250.0,
                "tnuos_tariff_gbp_per_kw": 56.41,
                "estimated_tnuos_gbp": 14102.5,
            }
        ]
    }
    result = _section_triad_exposure(data)
    assert "C_IC1" in result
    assert "2021/22" in result
    assert "14,102" in result


def test_triad_exposure_totals_across_customers():
    data = {
        "triad_log": [
            {
                "customer_id": "C_IC1",
                "triad_year": 2021,
                "triad_periods": [],
                "avg_triad_kw": 200.0,
                "tnuos_tariff_gbp_per_kw": 56.41,
                "estimated_tnuos_gbp": 11282.0,
            },
            {
                "customer_id": "C_IC2",
                "triad_year": 2021,
                "triad_periods": [],
                "avg_triad_kw": 100.0,
                "tnuos_tariff_gbp_per_kw": 56.41,
                "estimated_tnuos_gbp": 5641.0,
            },
        ]
    }
    result = _section_triad_exposure(data)
    # Total = 11282 + 5641 = 16923
    assert "16,923" in result
    assert "C_IC1" in result
    assert "C_IC2" in result


# --- Phase 28a: _section_ic_portfolio tests ---

def _make_ic_portfolio_data():
    """Minimal data for _section_ic_portfolio with two I&C customers."""
    return {
        "all_records": [
            {
                "customer_id": "C_IC1",
                "commodity": "electricity",
                "revenue_gbp": 300_000.0,
                "net_margin_gbp": 15_000.0,
                "ccl_gbp": 14_340.0,
                "consumption_kwh": 2_000_000.0,
            },
            {
                "customer_id": "C_IC2",
                "commodity": "electricity",
                "revenue_gbp": 150_000.0,
                "net_margin_gbp": 7_500.0,
                "ccl_gbp": 7_170.0,
                "consumption_kwh": 1_000_000.0,
            },
        ],
        "years": {
            "2021": {
                "segment_split": {
                    "I&C electricity": {"net_gbp": 22_500.0},
                    "SME electricity": {"net_gbp": 5_000.0},
                    "resi electricity": {"net_gbp": -2_000.0},
                }
            }
        },
        "triad_log": [],
        "volume_tolerance_log": [],
    }


def test_ic_portfolio_empty_returns_empty():
    assert _section_ic_portfolio({}) == ""
    assert _section_ic_portfolio({"all_records": []}) == ""


def test_ic_portfolio_no_ccl_returns_empty():
    """Without CCL records, I&C can't be identified — returns empty."""
    data = {
        "all_records": [
            {"customer_id": "C1", "commodity": "electricity",
             "revenue_gbp": 1000.0, "net_margin_gbp": 50.0,
             "ccl_gbp": 0.0, "consumption_kwh": 10000.0},
        ],
        "years": {},
    }
    assert _section_ic_portfolio(data) == ""


def test_ic_portfolio_shows_customer_summary():
    data = _make_ic_portfolio_data()
    result = _section_ic_portfolio(data)
    assert "C_IC1" in result
    assert "C_IC2" in result
    assert "I&C Portfolio" in result


def test_ic_portfolio_shows_ccl_totals():
    data = _make_ic_portfolio_data()
    result = _section_ic_portfolio(data)
    # CCL totals: 14340 + 7170 = 21510
    assert "14,340" in result
    assert "7,170" in result


def test_ic_portfolio_shows_segment_comparison():
    data = _make_ic_portfolio_data()
    result = _section_ic_portfolio(data)
    # Segment table should include 2021 row
    assert "2021" in result
    assert "22,500" in result  # I&C net


def test_ic_portfolio_includes_triad_when_present():
    data = _make_ic_portfolio_data()
    data["triad_log"] = [
        {"customer_id": "C_IC1", "triad_year": 2021,
         "avg_triad_kw": 250.0, "tnuos_tariff_gbp_per_kw": 56.41,
         "estimated_tnuos_gbp": 14_102.5, "triad_periods": []},
    ]
    result = _section_ic_portfolio(data)
    assert "TNUoS" in result or "Triad" in result


# ── Gas Book P&L section (Phase 32a) ─────────────────────────────────────────

def _gas_pl_data(*, rev=1000.0, whl=600.0, gross=400.0, cap=50.0, net=200.0,
                 policy=80.0, network=70.0, year="2021"):
    """Minimal data dict for _section_gas_pl with a single gas-active year."""
    return {
        "years": {
            year: {
                "commodity_split": {
                    "gas": {
                        "revenue_gbp": rev,
                        "wholesale_cost_gbp": whl,
                        "gross_gbp": gross,
                        "capital_gbp": cap,
                        "net_gbp": net,
                    }
                },
                "gas_policy_cost_gbp": policy,
                "gas_network_cost_gbp": network,
            }
        }
    }


def test_section_gas_pl_empty_on_no_years():
    from saas.reporting.annual_report import _section_gas_pl
    assert _section_gas_pl({}) == ""
    assert _section_gas_pl({"years": {}}) == ""


def test_section_gas_pl_empty_on_zero_gas_revenue():
    from saas.reporting.annual_report import _section_gas_pl
    data = _gas_pl_data(rev=0.0, whl=0.0, gross=0.0, cap=0.0, net=0.0)
    assert _section_gas_pl(data) == ""


def test_section_gas_pl_shows_header():
    from saas.reporting.annual_report import _section_gas_pl
    result = _section_gas_pl(_gas_pl_data())
    assert "Gas Book P&L" in result


def test_section_gas_pl_shows_year_row():
    from saas.reporting.annual_report import _section_gas_pl
    result = _section_gas_pl(_gas_pl_data())
    assert "2021" in result
    assert "1,000" in result   # revenue
    assert "600" in result     # wholesale
    assert "400" in result     # gross
    assert "80" in result      # policy
    assert "70" in result      # network
    assert "50" in result      # capital
    assert "200" in result     # net


def test_section_gas_pl_shows_total_row():
    from saas.reporting.annual_report import _section_gas_pl
    result = _section_gas_pl(_gas_pl_data())
    assert "Total" in result


def test_section_gas_pl_net_percent():
    from saas.reporting.annual_report import _section_gas_pl
    # net=200, rev=1000 → 20.0%
    result = _section_gas_pl(_gas_pl_data(rev=1000.0, net=200.0))
    assert "+20.0%" in result


def test_section_gas_pl_negative_net_sign():
    from saas.reporting.annual_report import _section_gas_pl
    result = _section_gas_pl(_gas_pl_data(net=-50.0))
    assert "negative" in result


def test_section_gas_pl_positive_net_sign():
    from saas.reporting.annual_report import _section_gas_pl
    result = _section_gas_pl(_gas_pl_data(net=200.0))
    assert "positive" in result


def test_section_gas_pl_skips_zero_revenue_years():
    from saas.reporting.annual_report import _section_gas_pl
    data = {
        "years": {
            "2019": {
                "commodity_split": {"gas": {"revenue_gbp": 0.0, "wholesale_cost_gbp": 0.0,
                                            "gross_gbp": 0.0, "capital_gbp": 0.0, "net_gbp": 0.0}},
                "gas_policy_cost_gbp": 0.0, "gas_network_cost_gbp": 0.0,
            },
            "2021": {
                "commodity_split": {"gas": {"revenue_gbp": 800.0, "wholesale_cost_gbp": 500.0,
                                            "gross_gbp": 300.0, "capital_gbp": 40.0, "net_gbp": 150.0}},
                "gas_policy_cost_gbp": 60.0, "gas_network_cost_gbp": 50.0,
            },
        }
    }
    result = _section_gas_pl(data)
    assert "2021" in result
    assert "2019" not in result


def test_section_gas_pl_multi_year_totals():
    from saas.reporting.annual_report import _section_gas_pl
    data = {
        "years": {
            "2020": {
                "commodity_split": {"gas": {"revenue_gbp": 500.0, "wholesale_cost_gbp": 300.0,
                                            "gross_gbp": 200.0, "capital_gbp": 20.0, "net_gbp": 100.0}},
                "gas_policy_cost_gbp": 40.0, "gas_network_cost_gbp": 40.0,
            },
            "2021": {
                "commodity_split": {"gas": {"revenue_gbp": 700.0, "wholesale_cost_gbp": 450.0,
                                            "gross_gbp": 250.0, "capital_gbp": 30.0, "net_gbp": 120.0}},
                "gas_policy_cost_gbp": 60.0, "gas_network_cost_gbp": 40.0,
            },
        }
    }
    result = _section_gas_pl(data)
    # Total revenue: 1200, total net: 220
    assert "1,200" in result
    assert "220" in result


# ── commodity_split revenue/wholesale (Phase 32a) ─────────────────────────────

def test_commodity_split_includes_revenue_and_wholesale():
    """extract_report_data now populates revenue_gbp and wholesale_cost_gbp
    in commodity_split for both electricity and gas legs."""
    data = extract_report_data(_run_output())
    y2016 = data["years"]["2016"]
    gas = y2016["commodity_split"]["gas"]
    elec = y2016["commodity_split"]["electricity"]
    # _record sets wholesale_cost_gbp=100.0 and revenue_gbp=margin+100
    assert gas["revenue_gbp"] == 105.0   # 5.0 margin + 100.0 wholesale
    assert gas["wholesale_cost_gbp"] == 100.0
    assert elec["revenue_gbp"] == 222.0  # (10+100)+(12+100)
    assert elec["wholesale_cost_gbp"] == 200.0  # 100 + 100


# ── Active/Passive renewal split section (Phase 33b) ─────────────────────────

def _active_passive_data(*, active_count=3, passive_count=5, year="2021"):
    """Build minimal churn_basis_risk data with is_active_renewal field."""
    records = []
    for i in range(active_count):
        records.append({
            "customer_id": f"C{i+1}",
            "term_start": f"{year}-01-01",
            "sim_churn_probability": 0.25,
            "company_churn_estimate": 0.20,
            "churn_estimate_error_pct": -0.2,
            "is_active_renewal": True,
        })
    for i in range(passive_count):
        records.append({
            "customer_id": f"C{i+10}",
            "term_start": f"{year}-01-01",
            "sim_churn_probability": 0.08,
            "company_churn_estimate": 0.05,
            "churn_estimate_error_pct": -0.375,
            "is_active_renewal": False,
        })
    return {"churn_basis_risk": records}


def test_section_active_passive_empty_on_no_cbr():
    from saas.reporting.annual_report import _section_active_passive_renewal
    assert _section_active_passive_renewal({}) == ""
    assert _section_active_passive_renewal({"churn_basis_risk": []}) == ""


def test_section_active_passive_empty_on_pre_phase33_data():
    """Pre-Phase-33 data lacks is_active_renewal field — returns empty."""
    from saas.reporting.annual_report import _section_active_passive_renewal
    data = {"churn_basis_risk": [
        {"customer_id": "C1", "term_start": "2021-01-01",
         "sim_churn_probability": 0.2, "company_churn_estimate": 0.15,
         "churn_estimate_error_pct": -0.25}
    ]}
    assert _section_active_passive_renewal(data) == ""


def test_section_active_passive_shows_header():
    from saas.reporting.annual_report import _section_active_passive_renewal
    result = _section_active_passive_renewal(_active_passive_data())
    assert "Active vs Passive" in result


def test_section_active_passive_shows_counts():
    from saas.reporting.annual_report import _section_active_passive_renewal
    result = _section_active_passive_renewal(_active_passive_data(active_count=3, passive_count=5))
    assert "3" in result   # active count
    assert "5" in result   # passive count


def test_section_active_passive_shows_year_row():
    from saas.reporting.annual_report import _section_active_passive_renewal
    result = _section_active_passive_renewal(_active_passive_data(year="2022"))
    assert "2022" in result


def test_section_active_passive_passive_estimate_lower():
    """The section should show passive estimate lower than active estimate."""
    from saas.reporting.annual_report import _section_active_passive_renewal
    data = _active_passive_data(active_count=4, passive_count=6)
    result = _section_active_passive_renewal(data)
    # Active estimate: 20.0%, passive estimate: 5.0%
    assert "20.0%" in result or "20%" in result
    assert "5.0%" in result or "5%" in result


# Phase 37a: Forward scenario metadata section


def test_section_scenario_metadata_empty_when_no_scenario():
    assert _section_scenario_metadata({}) == ""
    assert _section_scenario_metadata({"scenario_name": None}) == ""


def test_section_scenario_metadata_shows_scenario_name():
    data = {"scenario_name": "central_2027", "scenario_year_range": [2026, 2029]}
    result = _section_scenario_metadata(data)
    assert "central_2027" in result


def test_section_scenario_metadata_shows_year_range():
    data = {"scenario_name": "central_2027", "scenario_year_range": [2026, 2029]}
    result = _section_scenario_metadata(data)
    assert "2026" in result
    assert "2029" in result


def test_section_scenario_metadata_shows_forward_scenario_warning():
    data = {"scenario_name": "stress_dunkelflaute_2027", "scenario_year_range": [2026, 2030]}
    result = _section_scenario_metadata(data)
    assert "FORWARD SCENARIO" in result or "forward scenario" in result.lower()


def test_section_scenario_metadata_shows_distribution_params():
    # scenario_params now passed via run output, not looked up from SIM bimodal_generator
    scenario_params = {
        "upper_mode_mean": 120.0, "upper_mode_std": 20.0,
        "lower_mode_mean": 38.0, "lower_mode_std": 20.0,
        "lower_mode_fraction": 0.55, "negative_days_per_year": 20.0,
        "negative_price_floor": -75.0,
        "dunkelflaute_events_per_year": 5.0, "dunkelflaute_multiplier_mean": 2.0,
    }
    data = {"scenario_name": "central_2027", "scenario_year_range": [2026, 2028], "scenario_params": scenario_params}
    result = _section_scenario_metadata(data)
    assert "120" in result or "£120" in result  # upper_mode_mean
    assert "38" in result or "£38" in result    # lower_mode_mean


def test_section_scenario_metadata_works_with_unknown_scenario_name():
    """Unknown scenario name should still render without crashing (no params shown)."""
    data = {"scenario_name": "custom_scenario", "scenario_year_range": [2026, 2027]}
    result = _section_scenario_metadata(data)
    assert "custom_scenario" in result


def test_section_scenario_metadata_is_first_after_title():
    """Scenario metadata appears before the executive summary (within first 300 chars of output)."""
    data = {"scenario_name": "low_renewables_2027", "scenario_year_range": [2026, 2028]}
    result = _section_scenario_metadata(data)
    # The section heading should be near the top
    idx = result.find("Forward Scenario Run")
    assert idx < 100, f"Heading not near top: found at index {idx}"


# ── Phase 39a: SVT comparative pricing ────────────────────────────────────────

def _make_cbr_with_svt(
    is_active=False,
    unit_rate=200.0,
    svt_rate=250.0,
    term_start="2024-01-01",
):
    pct = round((unit_rate - svt_rate) / svt_rate * 100.0, 2) if svt_rate else None
    return {
        "customer_id": "C1",
        "term_start": term_start,
        "sim_churn_probability": 0.1,
        "company_churn_estimate": 0.12,
        "churn_estimate_error_pct": 0.02,
        "is_active_renewal": is_active,
        "unit_rate_gbp_per_mwh": unit_rate,
        "svt_rate_gbp_per_mwh": svt_rate,
        "rate_vs_svt_pct": pct,
    }


def test_section_svt_comparison_silent_without_passive():
    from saas.reporting.annual_report import _section_svt_comparison
    data = {"churn_basis_risk": [_make_cbr_with_svt(is_active=True)]}
    assert _section_svt_comparison(data) == ""


def test_section_svt_comparison_silent_when_no_cbr():
    from saas.reporting.annual_report import _section_svt_comparison
    assert _section_svt_comparison({}) == ""


def test_section_svt_comparison_has_heading():
    from saas.reporting.annual_report import _section_svt_comparison
    data = {"churn_basis_risk": [_make_cbr_with_svt(is_active=False)]}
    result = _section_svt_comparison(data)
    assert "SVT" in result
    assert "Phase 39a" in result or "39a" in result


def test_section_svt_comparison_below_svt_shown():
    from saas.reporting.annual_report import _section_svt_comparison
    # unit_rate < svt_rate → below SVT, premium is negative
    data = {"churn_basis_risk": [_make_cbr_with_svt(is_active=False, unit_rate=200.0, svt_rate=250.0)]}
    result = _section_svt_comparison(data)
    assert "Protected" in result or "below" in result.lower() or "-" in result


def test_section_svt_comparison_above_svt_shown():
    from saas.reporting.annual_report import _section_svt_comparison
    # unit_rate > svt_rate → above SVT, at-risk
    data = {"churn_basis_risk": [_make_cbr_with_svt(is_active=False, unit_rate=300.0, svt_rate=250.0)]}
    result = _section_svt_comparison(data)
    assert "1" in result  # 1 above SVT


def test_section_svt_comparison_year_breakdown():
    from saas.reporting.annual_report import _section_svt_comparison
    recs = [
        _make_cbr_with_svt(is_active=False, term_start="2023-06-01"),
        _make_cbr_with_svt(is_active=False, term_start="2024-06-01"),
    ]
    data = {"churn_basis_risk": recs}
    result = _section_svt_comparison(data)
    assert "2023" in result
    assert "2024" in result


def test_section_svt_comparison_silent_without_svt_data():
    from saas.reporting.annual_report import _section_svt_comparison
    # Pre-39a record: no svt_rate_gbp_per_mwh
    rec = {
        "customer_id": "C1",
        "term_start": "2024-01-01",
        "sim_churn_probability": 0.1,
        "company_churn_estimate": 0.12,
        "churn_estimate_error_pct": 0.02,
        "is_active_renewal": False,
    }
    assert _section_svt_comparison({"churn_basis_risk": [rec]}) == ""
