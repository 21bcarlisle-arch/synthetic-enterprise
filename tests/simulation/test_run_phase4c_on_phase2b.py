import pytest

from simulation.run_phase4c_on_phase2b import build_monthly_bills, main


def make_record(customer_id, settlement_date, kwh, unit_rate=200.0):
    return {
        "customer_id": customer_id,
        "settlement_date": settlement_date,
        "settlement_period": 1,
        "consumption_kwh": kwh,
        "unit_rate_gbp_per_mwh": unit_rate,
        "revenue_gbp": (kwh / 1000) * unit_rate,
        "wholesale_cost_gbp": 0.0,
        "margin_gbp": 0.0,
    }


def consecutive_monthly_records(customer_id, start_year, kwh_by_month_index):
    """One record per CONSECUTIVE calendar month starting Jan of start_year,
    kwh_by_month_index[i] = consumption for month i (0-indexed from Jan
    start_year). Consecutive (no gaps) so bill_shock_pct's "previous bill"
    and _prior_calendar_month() always refer to the same real month --
    sparse test data would let an intermediate gap masquerade as a
    same-month comparison that never really happened."""
    records = []
    for i, kwh in enumerate(kwh_by_month_index):
        year = start_year + i // 12
        month = i % 12 + 1
        records.append(make_record(customer_id, f"{year}-{month:02d}-01", kwh))
    return records


def bills_by_month(bills, customer_id):
    return {b["period_end"][:7]: b for b in bills if b["customer_id"] == customer_id}


def test_build_monthly_bills_groups_by_customer_and_month():
    records = [
        make_record("C1", "2023-01-15", 10.0),
        make_record("C1", "2023-01-16", 10.0),
        make_record("C1", "2023-02-01", 10.0),
        make_record("C2", "2023-01-10", 5.0),
    ]
    bills = build_monthly_bills(records)

    c1_bills = [b for b in bills if b["customer_id"] == "C1"]
    c2_bills = [b for b in bills if b["customer_id"] == "C2"]
    assert [b["period_start"] for b in c1_bills] == ["2023-01-15", "2023-02-01"]
    assert len(c2_bills) == 1


def test_build_monthly_bills_carries_previous_bill_total_for_shock():
    records = [
        make_record("C1", "2023-01-01", 10.0),   # small bill
        make_record("C1", "2023-02-01", 100.0),  # 10× jump — big shock
    ]
    bills = build_monthly_bills(records)

    assert bills[0]["bill_shock_pct"] is None  # first bill, no prior total
    # bill_shock_pct = |feb_total - jan_total| / jan_total (both totals include non-commodity + VAT)
    jan_total = bills[0]["total_amount_gbp"]
    feb_total = bills[1]["total_amount_gbp"]
    assert bills[1]["bill_shock_pct"] == pytest.approx((feb_total - jan_total) / jan_total)
    assert bills[1]["clarity_score"] < bills[0]["clarity_score"]


def test_build_monthly_bills_uses_customer_contract_type():
    records = [make_record("C1", "2023-01-01", 10.0)]
    bills = build_monthly_bills(records)
    # C1 is fixed_1yr -> base clarity 1.0, single steady day -> clarity 1.0
    assert bills[0]["clarity_score"] == pytest.approx(1.0)


from simulation.run_phase4c_on_phase2b import _billing_month


def test_billing_month_standard():
    assert _billing_month("2022-01-15") == "2022-01"


def test_billing_month_december():
    assert _billing_month("2022-12-31") == "2022-12"


def test_build_monthly_bills_empty():
    assert build_monthly_bills([]) == []


def test_build_monthly_bills_bill_keys_present():
    records = [make_record("C1", "2023-01-01", 10.0)]
    bills = build_monthly_bills(records)
    bill = bills[0]
    for key in ("customer_id", "period_start", "total_amount_gbp", "clarity_score", "bill_shock_pct"):
        assert key in bill, f"missing key: {key}"


def test_build_monthly_bills_chronological_order():
    records = [
        make_record("C1", "2023-02-15", 10.0),
        make_record("C1", "2023-01-01", 10.0),
    ]
    bills = build_monthly_bills(records)
    c1_bills = [b for b in bills if b["customer_id"] == "C1"]
    starts = [b["period_start"] for b in c1_bills]
    assert starts == sorted(starts)


def test_build_monthly_bills_total_is_positive():
    records = [make_record("C1", "2023-01-01", 50.0, unit_rate=200.0)]
    bills = build_monthly_bills(records)
    assert bills[0]["total_amount_gbp"] > 0.0


def test_billing_month_february_leap():
    assert _billing_month("2020-02-29") == "2020-02"


def test_build_monthly_bills_clarity_score_in_range():
    records = [make_record("C1", "2023-06-01", 50.0)]
    bills = build_monthly_bills(records)
    score = bills[0]["clarity_score"]
    assert 0.0 <= score <= 1.0


def test_build_monthly_bills_multi_customer_total_revenue():
    records = [
        make_record("C1", "2023-01-01", 10.0, unit_rate=100.0),
        make_record("C2", "2023-01-01", 20.0, unit_rate=100.0),
        make_record("C1", "2023-01-02", 5.0, unit_rate=100.0),
    ]
    bills = build_monthly_bills(records)
    total = sum(b["total_amount_gbp"] for b in bills)
    # Revenue: (10+5)/1000*100 + 20/1000*100 = 1.5 + 2.0 = 3.5 (before VAT/SC)
    assert total > 0.0
    c1_bills = [b for b in bills if b["customer_id"] == "C1"]
    c2_bills = [b for b in bills if b["customer_id"] == "C2"]
    assert len(c1_bills) == 1  # both C1 dates same month
    assert len(c2_bills) == 1


def test_billing_month_new_year():
    assert _billing_month("2022-01-01") == "2022-01"


def test_build_monthly_bills_total_exceeds_raw_revenue():
    records = [make_record("C1", "2023-01-01", 10.0, unit_rate=200.0)]
    bills = build_monthly_bills(records)
    raw_revenue = (10.0 / 1000) * 200.0
    assert bills[0]["total_amount_gbp"] > raw_revenue


def test_build_monthly_bills_clarity_score_not_none():
    records = [make_record("C1", "2023-03-01", 25.0)]
    bills = build_monthly_bills(records)
    assert bills[0]["clarity_score"] is not None
    assert isinstance(bills[0]["clarity_score"], float)


def test_main_produces_meter_read_log_matching_bills():
    # Phase 3 (CORE_FIDELITY_PHASES.md item 1) wiring: every bill the full
    # pipeline produces must have a corresponding meter-read event, and the
    # events must carry real status/delay data (not a stub).
    result = main()
    assert len(result["meter_read_log"]) == len(result["bills"])
    statuses = {entry["status"] for entry in result["meter_read_log"]}
    assert statuses <= {"actual", "estimated"}
    assert all(entry["delay_days"] >= 0 for entry in result["meter_read_log"])


def test_main_produces_contact_centre_log():
    # Phase 3 item 4 wiring: every logged contact carries a resolved
    # channel + first-response latency.
    result = main()
    assert "contact_centre_log" in result
    for entry in result["contact_centre_log"]:
        assert entry["channel"] in ("phone", "email", "webchat")
        assert entry["first_response_hours"] >= 0
        assert isinstance(entry["breached_sla"], bool)


def test_main_produces_credit_refund_log():
    # Phase 3 item 2 wiring: credit_refund.py's SLA mechanic now has a real
    # caller -- every logged event must carry a resolved SLC 14 outcome.
    result = main()
    assert "credit_refund_log" in result
    for entry in result["credit_refund_log"]:
        assert entry["credit_amount_gbp"] > 0
        assert entry["working_days_to_pay"] is not None
        assert isinstance(entry["breached_slc14_deadline"], bool)


# -- bill_shock_yoy_pct / bill_shock_likely_seasonal (docs/design/
# BILL_SHOCK_DEFINITION_FINDING.md, added 2026-07-10, real tests added
# 2026-07-10 per phase-close-evaluator NEEDS_WORK finding -- the feature
# shipped with zero test coverage on the new fields themselves) --

from simulation.run_phase4c_on_phase2b import _prior_calendar_month, _year_ago_month


def test_prior_calendar_month_normal():
    assert _prior_calendar_month("2020-06") == "2020-05"


def test_prior_calendar_month_january_rolls_back_a_year():
    assert _prior_calendar_month("2020-01") == "2019-12"


def test_year_ago_month_normal():
    assert _year_ago_month("2020-06") == "2019-06"


def test_bill_shock_yoy_pct_none_when_no_year_ago_data():
    records = consecutive_monthly_records("C1", 2020, [10] * 6)
    bills = bills_by_month(build_monthly_bills(records), "C1")
    assert bills["2020-06"]["bill_shock_yoy_pct"] is None
    assert bills["2020-06"]["bill_shock_likely_seasonal"] is False


def test_bill_shock_yoy_pct_computed_when_year_ago_exists():
    kwh = [10] * 12 + [10] * 5 + [30]  # flat, then June Y2 jumps to 30
    records = consecutive_monthly_records("C1", 2019, kwh)
    bills = bills_by_month(build_monthly_bills(records), "C1")
    june_y2 = bills["2020-06"]
    # YoY vs June Y1 (kwh=10): a real, non-None percentage
    assert june_y2["bill_shock_yoy_pct"] is not None
    assert june_y2["bill_shock_yoy_pct"] > 0.20


def test_bill_shock_likely_seasonal_true_for_genuine_repeating_pattern():
    """July is a real, repeating seasonal peak both years -- large MoM
    (vs June), small YoY (vs last July), and June itself was never flagged
    -- this SHOULD be flagged likely_seasonal."""
    year1 = [10, 10, 10, 10, 10, 10, 50, 10, 10, 10, 10, 10]
    year2 = [10, 10, 10, 10, 10, 10, 50, 10, 10, 10, 10, 10]
    records = consecutive_monthly_records("C1", 2019, year1 + year2)
    bills = bills_by_month(build_monthly_bills(records), "C1")
    july_y2 = bills["2020-07"]
    assert july_y2["bill_shock_pct"] >= 0.20
    assert july_y2["bill_shock_yoy_pct"] < 0.20
    assert july_y2["bill_shock_likely_seasonal"] is True


def test_bill_shock_likely_seasonal_false_for_genuine_one_off_anomaly():
    """July Y2 spikes with no precedent in July Y1 -- large MoM AND large
    YoY -- a real shock, must NOT be labelled seasonal."""
    year1 = [10] * 12
    year2 = [10, 10, 10, 10, 10, 10, 50, 10, 10, 10, 10, 10]
    records = consecutive_monthly_records("C1", 2019, year1 + year2)
    bills = bills_by_month(build_monthly_bills(records), "C1")
    july_y2 = bills["2020-07"]
    assert july_y2["bill_shock_pct"] >= 0.20
    assert july_y2["bill_shock_yoy_pct"] >= 0.20
    assert july_y2["bill_shock_likely_seasonal"] is False


def test_bill_shock_likely_seasonal_false_for_shock_aftermath_month():
    """Regression for the phase-close-evaluator's live finding (2026-07-10):
    July Y2 has a genuine one-off spike (as above); August Y2 reverts back
    to baseline. August's own MoM change is large (dropping back down from
    July's spike) and its YoY is small (August is normal both years) --
    without the prior-month-shock exclusion, August would be WRONGLY
    labelled likely_seasonal, when the real cause is July's anomaly, not
    August's own seasonal pattern."""
    year1 = [10] * 12
    year2 = [10, 10, 10, 10, 10, 10, 50, 10, 10, 10, 10, 10]
    records = consecutive_monthly_records("C1", 2019, year1 + year2)
    bills = bills_by_month(build_monthly_bills(records), "C1")
    august_y2 = bills["2020-08"]
    assert august_y2["bill_shock_pct"] >= 0.20  # reverting from July's spike
    assert august_y2["bill_shock_yoy_pct"] < 0.20  # August is normal both years
    assert august_y2["bill_shock_likely_seasonal"] is False  # NOT seasonal -- shock aftermath
