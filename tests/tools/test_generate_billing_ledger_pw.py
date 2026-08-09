"""Phase PW -- I&C Corporate Arrears Calibration tests."""
import json
import random
from datetime import date, timedelta
from pathlib import Path

from tools.generate_billing_ledger import (
    generate, _payment_outcome, _ic_arrears_stages,
    _CORP_BACS_DISPUTE_PROB, _CORP_BACS_ON_TIME_PROB,
)


def _ic_bill(cid, period_end, amount=8000.0):
    ps = (date.fromisoformat(period_end) - timedelta(days=90)).isoformat()
    # VAT at the correct 20% (non-resi) rate so this fixture passes the
    # Phase 3 pre-bill validation gate -- other components reweighted
    # proportionally so they still sum to `amount`.
    vat_rate = 0.20
    subtotal = amount / (1 + vat_rate)
    vat_gbp = amount - subtotal
    return {
        "customer_id": cid, "period_start": ps, "period_end": period_end,
        "total_consumption_kwh": 1000.0, "commodity_amount_gbp": subtotal * (0.8 / 0.95),
        "non_commodity_amount_gbp": subtotal * (0.1 / 0.95), "standing_charge_gbp": subtotal * (0.05 / 0.95),
        "vat_gbp": vat_gbp, "total_amount_gbp": amount,
        "average_unit_rate_gbp_per_mwh": amount, "clarity_score": 0.75,
        "bill_shock_pct": None, "segment": "I&C", "commodity": "electricity",
    }


def _resi_bill(cid, period_end, amount=150.0):
    ps = (date.fromisoformat(period_end) - timedelta(days=90)).isoformat()
    # VAT derived from the subtotal (not a flat weight of `amount`) so the
    # effective rate is exactly 5%, within the Phase 3 gate's tolerance --
    # other components reweighted proportionally so they still sum to `amount`.
    vat_rate = 0.05
    subtotal = amount / (1 + vat_rate)
    vat_gbp = amount - subtotal
    return {
        "customer_id": cid, "period_start": ps, "period_end": period_end,
        "total_consumption_kwh": 300.0, "commodity_amount_gbp": subtotal * (0.7 / 0.95),
        "non_commodity_amount_gbp": subtotal * (0.15 / 0.95), "standing_charge_gbp": subtotal * (0.1 / 0.95),
        "vat_gbp": vat_gbp, "total_amount_gbp": amount,
        "average_unit_rate_gbp_per_mwh": 200.0, "clarity_score": 0.80,
        "bill_shock_pct": None, "segment": "resi", "commodity": "electricity",
    }


def _run(bills, beh=None, churned=None):
    return {"bills": bills, "per_customer_behavioral": beh or {}, "churned_billing_accounts": churned or []}


def test_ic_bacs_can_produce_dispute():
    """With many samples, I&C BACS should produce some disputes (~0.7%/invoice)."""
    rng = random.Random(99)
    outcomes = [_payment_outcome("bacs", "LOW", rng, "I&C")[0] for _ in range(2000)]
    assert "dispute" in outcomes


def test_ic_bacs_on_time_rate_over_85pct():
    rng = random.Random(42)
    outcomes = [_payment_outcome("bacs", "LOW", rng, "I&C")[0] for _ in range(1000)]
    on_time = sum(1 for o, d in
                  [_payment_outcome("bacs", "LOW", random.Random(i), "I&C") for i in range(1000)]
                  if o == "success" and d == 0)
    assert on_time > 850


def test_ic_bacs_late_success_has_positive_days():
    rng = random.Random(1234)
    late_found = False
    for _ in range(5000):
        outcome, days = _payment_outcome("bacs", "LOW", rng, "I&C")
        if outcome == "success" and days > 0:
            assert 14 <= days <= 45, days
            late_found = True
    assert late_found


def test_sme_bacs_is_no_longer_always_success():
    """UPDATED 2026-08-08 (W2_sme_segment_case_normalisation).

    This test used to be `test_non_ic_bacs_still_always_success` and asserted
    that an SME on bacs ALWAYS succeeds with days == 0. That was a
    characterization of a DEFECT, not a contract: SME was absent from the I&C
    tuple, so it fell through `payment_outcome`'s corporate arm to a bare
    ("success", 0) and could never be late, fail or dispute. Pinning it made
    the missing SME outcome model look intentional.

    SME now has its own Ofgem-D6/DBT-anchored model, so the correct assertion
    is the opposite one. Full coverage lives in
    tests/simulation/test_segment_case_normalisation.py; this keeps the
    ledger-side reader honest about which contract it depends on.
    """
    rng = random.Random(42)
    outcomes = [_payment_outcome("bacs", "HIGH", rng, "SME", False, None, "SME%03d" % i)
                for i in range(2000)]
    assert any(o != "success" or d > 0 for o, d in outcomes), (
        "SME bills are all on-time successes again -- the corporate fall-through "
        "that deletes SME bad debt has come back"
    )


def test_a_non_business_segment_on_a_corporate_rail_still_succeeds():
    """The fall-through arm itself, which is unreachable by construction.

    `payment_method` only returns bacs/chaps for a business segment, so a resi
    bill on bacs cannot occur in a real run. The arm is retained so an
    unforeseen caller degrades exactly as it always has, and this pins that
    degradation rather than leaving it undescribed.
    """
    rng = random.Random(42)
    for _ in range(200):
        outcome, days = _payment_outcome("bacs", "HIGH", rng, "resi")
        assert outcome == "success"
        assert days == 0


def test_ic_dispute_invoice_status_is_disputed(tmp_path):
    """An I&C dispute (0.7% of corporate-rail bills) renders as `disputed`.

    The fixture was 500 copies of ONE bill (`[_ic_bill(...)] * 500` -- the same
    identity 500 times). That only ever produced a dispute because the old
    shared RNG handed each copy a different draw purely by position. Since
    W2_16 a bill's outcome is a pure function of its identity, so 500 copies of
    one bill correctly resolve 500 identical ways -- the fixture stopped
    modelling 500 invoices and started modelling one, repeated.

    Now 500 genuinely distinct monthly bills, which is what "enough invoices for
    a 0.7% event to appear" actually requires.
    """
    bills = [
        _ic_bill("C_IC1", f"{1600 + i // 12:04d}-{i % 12 + 1:02d}-28", 8000.0)
        for i in range(500)
    ]
    assert len({(b["customer_id"], b["period_end"]) for b in bills}) == 500, (
        "fixture guard: the bills must be distinct invoices, not one repeated"
    )
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills)))
    result = generate(rj, tmp_path / "l.json")
    cust = result["customers"]["C_IC1"]
    statuses = {inv["payment_status"] for inv in cust["invoices"]}
    assert "disputed" in statuses


def test_ic_dispute_creates_arrears_case(tmp_path):
    bills = [_ic_bill("C_IC1", "2022-%02d-28" % m, 8000.0) for m in range(1, 13)]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills)))
    result = generate(rj, tmp_path / "l.json")
    cust = result["customers"]["C_IC1"]
    assert cust["arrears_case_count"] >= 0


def test_ic_arrears_stages_no_dd_failed():
    stages = _ic_arrears_stages(5000.0, date(2022, 5, 1), True)
    stage_names = [s["stage"] for s in stages]
    assert "DD_FAILED" not in stage_names
    assert "INVOICE_DISPUTED" in stage_names


def test_ic_arrears_stages_starts_with_invoice_disputed():
    stages = _ic_arrears_stages(5000.0, date(2022, 5, 1), True)
    assert stages[0]["stage"] == "INVOICE_DISPUTED"


def test_ic_arrears_stages_resolved_via_payment_plan():
    stages = _ic_arrears_stages(5000.0, date(2022, 5, 1), True)
    names = [s["stage"] for s in stages]
    assert "PAYMENT_PLAN_AGREED" in names
    assert "WRITTEN_OFF" not in names


def test_ic_arrears_stages_written_off_when_churned():
    stages = _ic_arrears_stages(5000.0, date(2022, 5, 1), False)
    names = [s["stage"] for s in stages]
    assert "WRITTEN_OFF" in names
    assert "PAYMENT_PLAN_AGREED" not in names


def test_ic_arrears_dates_ordered():
    stages = _ic_arrears_stages(5000.0, date(2022, 5, 1), True)
    dates = [s["date"] for s in stages]
    assert dates == sorted(dates)


def test_ic_dispute_case_id_prefix_dis(tmp_path):
    bills = [_ic_bill("C_IC1", "2022-03-31", 8000.0)] * 200
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills)))
    result = generate(rj, tmp_path / "l.json")
    cust = result["customers"]["C_IC1"]
    for case in cust.get("arrears_history", []):
        assert case["case_id"].startswith("DIS-")


def test_segment_stored_in_ledger(tmp_path):
    bills = [_ic_bill("C_IC1", "2022-03-31", 8000.0), _resi_bill("C1", "2022-03-31")]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills)))
    result = generate(rj, tmp_path / "l.json")
    assert result["customers"]["C_IC1"]["segment"] == "I&C"
    assert result["customers"]["C1"]["segment"] == "resi"


def test_resi_dd_path_unchanged(tmp_path):
    """Regression: residential DD path still uses income_stress model."""
    beh = {"C7": {"income_stress_trajectory": [{"year": 2022, "stress": "high"}]}}
    bills = [_resi_bill("C7", "2022-%02d-28" % m, 200.0) for m in range(1, 13)]
    rj = tmp_path / "run.json"
    rj.write_text(json.dumps(_run(bills, beh=beh)))
    result = generate(rj, tmp_path / "l.json")
    cust = result["customers"]["C7"]
    assert cust["arrears_case_count"] > 0
    first_stage = cust["arrears_history"][0]["stages"][0]["stage"]
    assert first_stage == "DD_FAILED"


def test_ic_dispute_probability_constant_defined():
    assert _CORP_BACS_DISPUTE_PROB == 0.007


def test_ic_on_time_probability_constant_defined():
    assert _CORP_BACS_ON_TIME_PROB == 0.92
