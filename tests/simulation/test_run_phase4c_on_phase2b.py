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


@pytest.fixture
def force_actual_reads(monkeypatch):
    """Pin every meter read to 'actual' so the bill-shock / seasonal-diagnostic
    LOGIC tests observe billed totals that track their constructed consumption
    exactly.

    D3 step 1 (estimated billing, wired into `build_monthly_bills`) otherwise
    perturbs billed amounts month-to-month, which is orthogonal to what these
    yoy/aftermath tests assert about the diagnostic's LOGIC. The interaction it
    exposes -- an estimated bill can itself trip the bill-shock-seasonal
    detector because its billed total diverges from the true seasonal pattern
    -- is a real, separately-registered follow-up (the detector has no notion
    of billing_basis yet), not what these pre-D3 logic tests were written to
    cover.
    """
    import simulation.meter_reads as mr

    monkeypatch.setattr(mr, "TRADITIONAL_ACTUAL_READ_PROBABILITY", 1.0)
    monkeypatch.setattr(mr, "SMART_METER_NOT_COMMUNICATING_RATE", 0.0)
    monkeypatch.setattr(mr, "READ_CUTOFF_DAYS_AFTER_PERIOD_END", 10**9)


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


def test_build_monthly_bills_carries_previous_bill_total_for_shock(force_actual_reads):
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


def test_bill_shock_yoy_pct_none_when_no_year_ago_data(force_actual_reads):
    records = consecutive_monthly_records("C1", 2020, [10] * 6)
    bills = bills_by_month(build_monthly_bills(records), "C1")
    assert bills["2020-06"]["bill_shock_yoy_pct"] is None
    assert bills["2020-06"]["bill_shock_likely_seasonal"] is False


def test_bill_shock_yoy_pct_computed_when_year_ago_exists(force_actual_reads):
    kwh = [10] * 12 + [10] * 5 + [30]  # flat, then June Y2 jumps to 30
    records = consecutive_monthly_records("C1", 2019, kwh)
    bills = bills_by_month(build_monthly_bills(records), "C1")
    june_y2 = bills["2020-06"]
    # YoY vs June Y1 (kwh=10): a real, non-None percentage
    assert june_y2["bill_shock_yoy_pct"] is not None
    assert june_y2["bill_shock_yoy_pct"] > 0.20


def test_bill_shock_likely_seasonal_true_for_genuine_repeating_pattern(force_actual_reads):
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


def test_bill_shock_likely_seasonal_false_for_genuine_one_off_anomaly(force_actual_reads):
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


def test_bill_shock_likely_seasonal_false_for_shock_aftermath_month(force_actual_reads):
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


# --- D3 step 1: estimated billing wired into the billed amount --------------
# (docs/design/maturity_map.yaml "Estimated billing & catch-up rebilling
# cycle", step 1. Step 2 -- actual-read catch-up rebilling -- is out of scope.)

import calendar
import random

from saas.bill_generator import generate_bill
from saas.customers import get_customer
from simulation.run_phase4c_on_phase2b import _estimated_settlement_records


def _sc_month_records(cid, year, month, kwh, unit_rate, sc_per_day=0.50):
    """One record per real day of `month`, carrying a settlement-derived
    standing-charge field so the real generate_bill() sc path is exercised."""
    days = calendar.monthrange(year, month)[1]
    recs = []
    for d in range(1, days + 1):
        recs.append({
            "customer_id": cid,
            "settlement_date": f"{year}-{month:02d}-{d:02d}",
            "settlement_period": 1,
            "consumption_kwh": kwh / days,
            "unit_rate_gbp_per_mwh": unit_rate,
            "revenue_gbp": (kwh / days / 1000) * unit_rate + sc_per_day,
            "standing_charge_gbp": sc_per_day,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        })
    return recs


def _realistic_36_month_records(cid="C1"):
    """Deterministic 36 consecutive months for a real traditional-meter
    customer: winter-heavy seasonal consumption, rates rising year-on-year.
    The fixed RNG seed makes the actual/estimated mix reproducible."""
    rng = random.Random(42)
    seasonal = [1.4, 1.35, 1.15, 0.95, 0.8, 0.7, 0.68, 0.72, 0.85, 1.05, 1.25, 1.4]
    records = []
    for i in range(36):
        year = 2019 + i // 12
        month = i % 12 + 1
        base = 300.0 * seasonal[month - 1] * (1 + rng.uniform(-0.05, 0.05))
        rate = 180.0 + (year - 2019) * 15.0
        records.extend(_sc_month_records(cid, year, month, base, rate))
    return records


def test_every_bill_carries_billing_basis():
    bills = build_monthly_bills(_realistic_36_month_records())
    assert bills, "expected bills"
    assert all(b["billing_basis"] in ("actual", "estimated") for b in bills)


def test_actual_read_bills_are_byte_identical_to_pre_d3(force_actual_reads):
    """The whole point of the additive-first design: with every read forced
    to 'actual', build_monthly_bills' output must match the pre-D3 behaviour
    (generate_bill straight over the true settlement records) on every
    pre-existing field. Only the additive `billing_basis`/yoy annotations may
    differ."""
    records = _realistic_36_month_records()
    new_bills = build_monthly_bills(records)
    assert all(b["billing_basis"] == "actual" for b in new_bills), (
        "force_actual_reads must pin every read to actual"
    )

    # Reconstruct the exact pre-D3 behaviour inline: generate_bill per month,
    # previous-total chain on the true bill, nothing else.
    by_month = {}
    for r in records:
        by_month.setdefault(r["settlement_date"][:7], []).append(r)
    cd = get_customer("C1")
    old_bills, prev = [], None
    for m in sorted(by_month):
        ob = generate_bill(
            "C1", by_month[m], cd.get("contract_type", "fixed_1yr"),
            prev, cd.get("segment", "resi"), cd.get("commodity", "electricity"),
        )
        old_bills.append(ob)
        prev = ob["total_amount_gbp"]

    added_keys = {"billing_basis", "bill_shock_yoy_pct", "bill_shock_likely_seasonal"}
    assert len(new_bills) == len(old_bills)
    for nb, ob in zip(new_bills, old_bills):
        nb_core = {k: v for k, v in nb.items() if k not in added_keys}
        ob_core = {k: v for k, v in ob.items() if k not in added_keys}
        assert nb_core == ob_core, f"actual-path field changed at {nb['period_end']}"


def test_estimated_settlement_records_preserve_rate_and_standing_charge():
    """The rescaling helper prices the estimate at the REAL unit rate and
    leaves the fixed standing charge untouched -- only the quantity moves."""
    records = _sc_month_records("C1", 2022, 6, kwh=500.0, unit_rate=200.0)
    true_bill = generate_bill("C1", records, "fixed_1yr", None, "resi", "electricity")

    scaled = _estimated_settlement_records(records, ratio=0.6, commodity="electricity")
    est_bill = generate_bill("C1", scaled, "fixed_1yr", None, "resi", "electricity")

    assert est_bill["total_consumption_kwh"] == pytest.approx(0.6 * 500.0)
    # real unit rate preserved exactly
    assert est_bill["average_unit_rate_gbp_per_mwh"] == pytest.approx(
        true_bill["average_unit_rate_gbp_per_mwh"]
    )
    # commodity == estimate(MWh) x real rate
    assert est_bill["commodity_amount_gbp"] == pytest.approx(
        (0.6 * 500.0 / 1000) * true_bill["average_unit_rate_gbp_per_mwh"]
    )
    # standing charge is a fixed daily charge -- unchanged by the estimate
    assert est_bill["standing_charge_gbp"] == pytest.approx(true_bill["standing_charge_gbp"])


def test_estimated_bills_priced_at_real_rate_with_quantity_divergence():
    """Integration: over a realistic mixed run, every estimated bill is
    consumption == its own estimate, priced at the customer's REAL unit rate
    (zero unit-rate divergence), and at least one estimated bill genuinely
    diverges in QUANTITY from the true consumption (and hence in £ total) --
    the honest estimate error that step 2 (catch-up rebilling) reconciles."""
    bills = build_monthly_bills(_realistic_36_month_records())
    estimated = [b for b in bills if b["billing_basis"] == "estimated"]
    assert estimated, "the realistic fixture must produce at least one estimated bill"

    saw_quantity_divergence = False
    for b in estimated:
        # billed consumption is the estimate
        assert b["total_consumption_kwh"] == pytest.approx(b["estimated_consumption_kwh"])
        # billed at the REAL unit rate (from the true settlement records)
        true_rate = b["true_commodity_amount_gbp"] / (b["true_consumption_kwh"] / 1000)
        assert b["average_unit_rate_gbp_per_mwh"] == pytest.approx(true_rate)
        # true-vs-billed provenance present for step-2 reconciliation
        assert "true_consumption_kwh" in b and "true_total_amount_gbp" in b
        if abs(b["estimated_consumption_kwh"] - b["true_consumption_kwh"]) > 1.0:
            saw_quantity_divergence = True
            # a real quantity gap must move the £ total away from the true bill
            assert b["total_amount_gbp"] != pytest.approx(b["true_total_amount_gbp"])
    assert saw_quantity_divergence, "expected at least one real estimate-vs-true quantity gap"


# --- D3 step 2: catch-up rebilling -- direct _resolve_catchup coverage,
# Expert-Hour finding (2026-07-12): the cap/proration/materiality math had
# only ever been exercised indirectly (via full-run integration and by-eye
# instance checks), never with a constructed scenario asserting the actual
# numbers. ------------------------------------------------------------------

from simulation.run_phase4c_on_phase2b import _resolve_catchup


def test_resolve_catchup_returns_none_for_empty_run():
    assert _resolve_catchup("C1", "resi", [], "2020-01-31") is None


def test_resolve_catchup_undercharge_no_cap_recent_period():
    pending = [{
        "period_start": "2020-01-01", "period_end": "2020-01-31",
        "true_total_amount_gbp": 150.0, "total_amount_gbp": 100.0,
    }]
    result = _resolve_catchup("C1", "resi", pending, "2020-02-29")
    assert result["direction"] == "undercharge"
    assert result["raw_delta_gbp"] == pytest.approx(50.0)
    assert result["chargeable_gbp"] == pytest.approx(50.0)
    assert result["written_off_gbp"] == 0.0
    assert result["back_billing_cap_applied"] is False
    assert result["is_material"] is True


def test_resolve_catchup_undercharge_capped_when_period_predates_12_months():
    """Ofgem SLC 31A: the oldest sliver of a long-unresolved estimated run
    falls outside the 12-month protected window as of the billing date --
    that portion must be written off, not recovered."""
    pending = [{
        "period_start": "2018-06-01", "period_end": "2019-05-31",
        "true_total_amount_gbp": 600.0, "total_amount_gbp": 0.0,
    }]
    result = _resolve_catchup("C1", "resi", pending, "2019-12-31")
    assert result["direction"] == "undercharge"
    assert result["raw_delta_gbp"] == pytest.approx(600.0)
    assert result["back_billing_cap_applied"] is True
    assert result["written_off_gbp"] > 0
    assert result["chargeable_gbp"] < 600.0
    assert result["chargeable_gbp"] + result["written_off_gbp"] == pytest.approx(600.0, abs=0.02)


def test_resolve_catchup_capped_undercharge_produces_write_off_adjustment():
    """ADVISOR_STEER_BACKBILLING_GATE.md item 1: the unrecoverable tranche
    must be a real write-off record, not just a bill-metadata number --
    reuses company/billing/account_adjustment_register.py's
    AdjustmentType.BACK_BILLING_CREDIT (built, tested, never wired before
    this steer), auto-applied since SLC 21BA makes it a legal requirement
    rather than a discretionary spend needing approval."""
    pending = [{
        "period_start": "2018-06-01", "period_end": "2019-05-31",
        "true_total_amount_gbp": 600.0, "total_amount_gbp": 0.0,
    }]
    result = _resolve_catchup("C1", "resi", pending, "2019-12-31")
    assert result["write_off_adjustment_id"] == "ADJ-BB-C1-2019-05-31"
    assert result["write_off_adjustment_status"] == "applied"
    assert "SLC 21BA" in result["write_off_adjustment_reason"]


def test_resolve_catchup_no_write_off_adjustment_when_cap_does_not_apply():
    pending = [{
        "period_start": "2020-01-01", "period_end": "2020-01-31",
        "true_total_amount_gbp": 150.0, "total_amount_gbp": 100.0,
    }]
    result = _resolve_catchup("C1", "resi", pending, "2020-02-29")
    assert "write_off_adjustment_id" not in result


def test_resolve_catchup_overcharge_never_capped_even_when_old():
    """A credit owed to the customer is never subject to the back-billing
    cap, however old -- the cap protects consumers from late demands, it
    does not let a supplier withhold a refund."""
    pending = [{
        "period_start": "2015-01-01", "period_end": "2015-12-31",
        "true_total_amount_gbp": 0.0, "total_amount_gbp": 500.0,
    }]
    result = _resolve_catchup("C1", "resi", pending, "2019-12-31")
    assert result["direction"] == "overcharge"
    assert result["raw_delta_gbp"] == pytest.approx(-500.0)
    assert result["chargeable_gbp"] == pytest.approx(-500.0)
    assert result["written_off_gbp"] == 0.0
    assert result["back_billing_cap_applied"] is False


def test_resolve_catchup_materiality_flag():
    small = [{
        "period_start": "2020-01-01", "period_end": "2020-01-31",
        "true_total_amount_gbp": 100.0, "total_amount_gbp": 99.0,
    }]
    assert _resolve_catchup("C1", "resi", small, "2020-02-28")["is_material"] is False

    large = [{
        "period_start": "2020-01-01", "period_end": "2020-01-31",
        "true_total_amount_gbp": 200.0, "total_amount_gbp": 100.0,
    }]
    assert _resolve_catchup("C1", "resi", large, "2020-02-28")["is_material"] is True


def test_resolve_catchup_negative_zero_normalized():
    """Expert-Hour finding: a near-exact-zero sum must not surface as the
    customer-facing '-0.0' rendering artifact."""
    pending = [{
        "period_start": "2020-01-01", "period_end": "2020-01-31",
        "true_total_amount_gbp": 100.0, "total_amount_gbp": 100.0 + 1e-13,
    }]
    result = _resolve_catchup("C1", "resi", pending, "2020-02-28")
    assert result["raw_delta_gbp"] == 0.0
    assert str(result["raw_delta_gbp"]) != "-0.0"
    assert str(result["chargeable_gbp"]) != "-0.0"


def test_build_monthly_bills_suppresses_immaterial_catchup(force_actual_reads, monkeypatch):
    """An immaterial correction (< CATCHUP_MATERIALITY_THRESHOLD_GBP) must
    not be stamped onto the bill at all -- a real supplier wouldn't bother
    (Expert-Hour finding: this threshold was computed but never consulted).
    Controls the scenario directly (rather than hunting for a real run that
    happens to produce a sub-threshold divergence) by monkeypatching
    _resolve_catchup itself to return a fixed immaterial result."""
    import simulation.run_phase4c_on_phase2b as mod

    immaterial = {
        "period_start": "2022-01-01", "period_end": "2022-01-31",
        "periods_covered": 1, "direction": "undercharge",
        "raw_delta_gbp": 1.0, "chargeable_gbp": 1.0, "written_off_gbp": 0.0,
        "back_billing_cap_applied": False, "is_material": False,
    }
    monkeypatch.setattr(mod, "_resolve_catchup", lambda *a, **k: immaterial)

    records = _sc_month_records("C1", 2022, 1, kwh=500.0, unit_rate=200.0)
    records += _sc_month_records("C1", 2022, 2, kwh=500.0, unit_rate=200.0)
    bills = build_monthly_bills(records)
    assert bills, "expected bills"
    assert all(not b.get("catchup_applied") for b in bills)


# --- D3 step 2: churn/account-closure forces a final-read resolution
# (Expert-Hour finding, 2026-07-12) --------------------------------------

@pytest.fixture
def force_estimated_reads(monkeypatch):
    """Pin every meter read to 'estimated' (opposite of force_actual_reads)
    so a customer's billing history can genuinely end on an unresolved run
    without waiting on random draws."""
    import simulation.meter_reads as mr

    monkeypatch.setattr(mr, "TRADITIONAL_ACTUAL_READ_PROBABILITY", 0.0)
    monkeypatch.setattr(mr, "SMART_METER_NOT_COMMUNICATING_RATE", 1.0)


def _short_run_records(cid="C1", n_months=10, start_year=2022, start_month=1):
    rng = random.Random(7)
    records = []
    for i in range(n_months):
        year = start_year + (start_month - 1 + i) // 12
        month = (start_month - 1 + i) % 12 + 1
        kwh = 300.0 * (1 + rng.uniform(-0.05, 0.05))
        records.extend(_sc_month_records(cid, year, month, kwh, unit_rate=200.0))
    return records


def test_churned_account_forces_final_read_resolution(force_estimated_reads):
    """Without churned_ids, a run of estimated bills with no natural
    forced-catch-up (fewer than MAX_CONSECUTIVE_ESTIMATED_PERIODS months)
    stays estimated forever -- the true-vs-billed delta is never recovered.
    A churning/succeeding account must instead force its own LAST bill to
    resolve on a final read (Ofgem SLC 21B), same real mechanism
    company/billing/account_closure.py's receive_final_read() models."""
    records = _short_run_records(n_months=10)

    bills_open = build_monthly_bills(records)
    assert len(bills_open) == 10
    assert bills_open[-1]["billing_basis"] == "estimated", (
        "sanity: 10 months must be too few to trip the natural 12-month forced catch-up"
    )

    bills_closed = build_monthly_bills(records, churned_ids={"C1"})
    assert len(bills_closed) == 10
    assert bills_closed[-1]["billing_basis"] == "actual"
    # only the FINAL bill is force-resolved -- earlier estimated bills for
    # the same (still-mid-run) customer are untouched.
    for b in bills_closed[:-1]:
        assert b["billing_basis"] == "estimated"


def test_non_churned_customer_unaffected_by_other_customers_churning(force_estimated_reads):
    """churned_ids scoping is per-customer -- a customer NOT in the set is
    unaffected even when other real customers in the same run are."""
    records = _short_run_records(cid="C1", n_months=10)
    bills = build_monthly_bills(records, churned_ids={"SOME_OTHER_CUSTOMER"})
    assert bills[-1]["billing_basis"] == "estimated"


# --- BILL_TO_LEDGER_LINKAGE.md (2026-07-12): held bills must not become
# recognised revenue. This tests the exact integration pattern main() now
# uses (validate_bills() -> build_ledger() -> derive_pnl()) -- main() itself
# runs the full ~100-minute pipeline and isn't unit-testable directly, so
# this proves the composition rather than invoking main(). ---

def test_held_bill_revenue_excluded_from_ledger_pnl():
    from company.billing.pre_bill_validation import validate_bills
    from company.compliance.domain_invariants import check_billed_clock_reconciles
    from saas.ledger import build_ledger, derive_pnl

    good_bill = {
        "customer_id": "C1", "period_start": "2024-01-01", "period_end": "2024-01-31",
        "segment": "resi", "commodity": "electricity", "total_consumption_kwh": 300.0,
        "commodity_amount_gbp": 44.55, "non_commodity_amount_gbp": 16.65,
        "standing_charge_gbp": 9.30, "vat_gbp": 3.53, "total_amount_gbp": 74.03,
    }
    # 20% VAT on a resi bill -- the R10 C6 defect class, guaranteed HELD.
    held_bill = {
        "customer_id": "C2", "period_start": "2024-01-01", "period_end": "2024-01-31",
        "segment": "resi", "commodity": "electricity", "total_consumption_kwh": 300.0,
        "commodity_amount_gbp": 44.55, "non_commodity_amount_gbp": 16.65,
        "standing_charge_gbp": 9.30, "vat_gbp": 14.10, "total_amount_gbp": 84.60,
    }
    bills = [good_bill, held_bill]
    issued_bills, exceptions = validate_bills(bills)
    assert len(issued_bills) == 1 and issued_bills[0]["customer_id"] == "C1"
    assert len(exceptions) == 1 and exceptions[0].customer_id == "C2"

    ledger_events = build_ledger([], issued_bills)
    ledger_pnl = derive_pnl(ledger_events)

    # The held bill's £84.60 must NOT appear in recognised revenue.
    assert ledger_pnl["total_billed_gbp"] == pytest.approx(74.03)
    assert check_billed_clock_reconciles(ledger_pnl["total_billed_gbp"], issued_bills) is True

    # Sanity: feeding the UNFILTERED bill list (the pre-fix behaviour)
    # would have wrongly recognised the held bill's revenue too, and the
    # invariant would correctly catch that as a real divergence.
    unfiltered_events = build_ledger([], bills)
    unfiltered_pnl = derive_pnl(unfiltered_events)
    assert unfiltered_pnl["total_billed_gbp"] == pytest.approx(74.03 + 84.60)
    assert check_billed_clock_reconciles(unfiltered_pnl["total_billed_gbp"], issued_bills) is False


class TestSerializeDdCollectionBook:
    """W5_1_banking_payment_rails L2->L3 (2026-07-12): the DD collection
    book's serialisation for the run-output/report surface -- the wiring
    that closed this atom's decisive 'zero live pipeline callers' gap."""

    def test_serializes_summary_mandates_and_attempts(self):
        from company.billing.direct_debit import DirectDebitBook, DDPaymentAttempt
        from simulation.run_phase4c_on_phase2b import _serialize_dd_collection_book

        book = DirectDebitBook()
        book.create_mandate("C1", "00-00-**", "0000", 80.0, "2020-01-15")
        book.record_attempt(DDPaymentAttempt("DD-C1-20200115-2020-01-31", "C1", "2020-01-31", 80.0, "collected"))

        result = _serialize_dd_collection_book(book)

        assert result["summary"]["total"] == 1
        assert len(result["mandates"]) == 1
        assert result["mandates"][0]["customer_id"] == "C1"
        assert len(result["attempts"]) == 1
        assert result["attempts"][0]["outcome"] == "collected"

    def test_serializes_empty_book(self):
        from company.billing.direct_debit import DirectDebitBook
        from simulation.run_phase4c_on_phase2b import _serialize_dd_collection_book

        result = _serialize_dd_collection_book(DirectDebitBook())
        assert result == {"summary": {"total": 0, "active": 0, "suspended": 0, "cancelled": 0, "total_monthly_gbp": 0.0}, "mandates": [], "attempts": []}

    def test_result_is_json_serializable(self):
        import json
        from company.billing.direct_debit import DirectDebitBook, DDPaymentAttempt
        from simulation.run_phase4c_on_phase2b import _serialize_dd_collection_book

        book = DirectDebitBook()
        book.create_mandate("C1", "00-00-**", "0000", 80.0, "2020-01-15",
                             setup_rails_reference="MANDATE-C1-2020-01-15",
                             setup_confirmed_date="2020-01-17")
        book.record_attempt(DDPaymentAttempt("REF", "C1", "2020-01-31", 80.0, "failed", failure_reason="Refer to Payer"))
        result = _serialize_dd_collection_book(book)
        json.dumps(result)  # must not raise
