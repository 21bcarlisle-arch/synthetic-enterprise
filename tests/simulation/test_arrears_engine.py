"""Phase QD -- tests for simulation.arrears_engine.

Verifies the shared payment-outcome/arrears engine, and -- the draft phase's
explicit acceptance criterion -- that the emergent bad debt fed into
run_output records (via apply_emergent_bad_debt) is provably the same
figure the per-customer billing ledger reports as WRITTEN_OFF, because both
draw from the same deterministic engine over the same bills.
"""
from datetime import date, timedelta

from simulation.arrears_engine import (
    FUEL_POVERTY_DD_FAIL_MULTIPLIER,
    FUEL_POVERTY_ON_TIME_MULTIPLIER,
    _fuel_poor_for_bill,
    apply_debt_recovery,
    apply_emergent_bad_debt,
    arrears_stages,
    compute_debt_recovery,
    compute_emergent_bad_debt,
    debt_archetype,
    ic_arrears_stages,
    payment_method,
    payment_outcome,
    stress_for_year,
)
from tools.generate_billing_ledger import generate as generate_ledger


def _bill(cid, period_end, amount, segment="resi"):
    ps = (date.fromisoformat(period_end) - timedelta(days=90)).isoformat()
    # VAT derived from the subtotal (not a flat weight of `amount`) at the
    # correct rate per segment, so this fixture passes the Phase 3 pre-bill
    # validation gate now wired into generate_billing_ledger.generate() --
    # other components reweighted proportionally so they still sum to `amount`.
    vat_rate = 0.05 if segment == "resi" else 0.20
    subtotal = amount / (1 + vat_rate)
    vat_gbp = amount - subtotal
    return {
        "customer_id": cid, "period_start": ps, "period_end": period_end,
        "total_consumption_kwh": 1000.0, "commodity_amount_gbp": subtotal * (0.8 / 0.95),
        "non_commodity_amount_gbp": subtotal * (0.1 / 0.95), "standing_charge_gbp": subtotal * (0.05 / 0.95),
        "vat_gbp": vat_gbp, "total_amount_gbp": amount,
        "average_unit_rate_gbp_per_mwh": amount, "clarity_score": 0.75,
        "bill_shock_pct": None, "segment": segment, "commodity": "electricity",
    }


def test_stress_for_year_default_low():
    assert stress_for_year({}, 2020) == "LOW"


def test_payment_method_ic_chaps_threshold():
    assert payment_method("I&C", 15000) == "chaps"
    assert payment_method("I&C", 5000) == "bacs"


def test_payment_method_resi_defaults_to_direct_debit_when_no_customer_id():
    """Backward compatibility: customer_id/fuel are optional -- omitting them
    must reproduce the exact original flat behaviour (every resi customer on
    direct debit), so pre-existing callers that never pass customer_id are
    unaffected."""
    assert payment_method("resi", 100.0) == "direct_debit"


def test_payment_method_resi_archetype_aware_with_customer_id():
    """With a customer_id, resi payment method must be archetype-aware
    (2026-07-09 fix) -- a large sample must produce both direct_debit and
    standard_credit, not a flat single value."""
    methods = {payment_method("resi", 100.0, f"PM_C{i}", "electricity") for i in range(200)}
    assert methods == {"direct_debit", "standard_credit"}


def test_payment_method_resi_archetype_is_deterministic():
    a = payment_method("resi", 100.0, "C1", "electricity")
    b = payment_method("resi", 100.0, "C1", "electricity")
    assert a == b


def test_payment_method_sme_ignores_customer_id():
    """SME/I&C payment method is amount/segment-driven only -- customer_id
    must not perturb it."""
    assert payment_method("sme", 100.0, "C1", "electricity") == "bacs"
    assert payment_method("I&C", 15000, "C1", "electricity") == "chaps"


def test_payment_outcome_bacs_ic_can_dispute():
    rng_outcomes = set()
    import random
    rng = random.Random(7)
    for _ in range(2000):
        outcome, _ = payment_outcome("bacs", "LOW", rng, segment="I&C")
        rng_outcomes.add(outcome)
    assert "dispute" in rng_outcomes
    assert "success" in rng_outcomes


def test_arrears_stages_written_off_vs_resolved():
    resolved = arrears_stages(100.0, date(2022, 1, 1), True)
    written_off = arrears_stages(100.0, date(2022, 1, 1), False)
    assert "RESOLVED" in [s["stage"] for s in resolved]
    assert "WRITTEN_OFF" in [s["stage"] for s in written_off]


def test_ic_arrears_stages_written_off_vs_resolved():
    resolved = ic_arrears_stages(100.0, date(2022, 1, 1), True)
    written_off = ic_arrears_stages(100.0, date(2022, 1, 1), False)
    assert "PAYMENT_PLAN_AGREED" in [s["stage"] for s in resolved]
    assert "WRITTEN_OFF" in [s["stage"] for s in written_off]


def test_compute_emergent_bad_debt_only_counts_churned():
    # High-stress resi customer who does NOT churn -- any failed payment
    # should resolve, not write off, so no emergent bad debt.
    bills = [_bill("C1", "2022-01-31", 200.0, "resi")] * 12
    beh = {"C1": {"income_stress_trajectory": [{"year": 2022, "stress": "high"}]}}
    result = compute_emergent_bad_debt(bills, beh, churned_ids=set())
    assert result == {}


def test_compute_emergent_bad_debt_finds_writeoffs_for_churned():
    # 24 months of high-stress bills for a customer who does churn --
    # with a 35% DD failure rate this should produce at least one write-off.
    bills = [_bill("C1", f"202{2 + i // 12}-{(i % 12) + 1:02d}-28", 200.0, "resi") for i in range(24)]
    beh = {"C1": {"income_stress_trajectory": [{"year": 2022, "stress": "high"}, {"year": 2023, "stress": "high"}]}}
    result = compute_emergent_bad_debt(bills, beh, churned_ids={"C1"})
    assert sum(result.values()) > 0


def test_apply_emergent_bad_debt_adjusts_last_record_and_treasury():
    records = [
        {"customer_id": "C1", "settlement_date": "2022-01-01", "bad_debt_gbp": 5.0,
         "net_margin_gbp": 100.0, "treasury_cash_balance_gbp": 1000.0},
        {"customer_id": "C1", "settlement_date": "2022-06-01", "bad_debt_gbp": 5.0,
         "net_margin_gbp": 50.0, "treasury_cash_balance_gbp": 1050.0},
    ]
    # Old bad debt for (C1, 2022) = 10.0. New emergent figure = 40.0 -> delta +30.
    apply_emergent_bad_debt(records, {("C1", 2022): 40.0})
    assert records[0]["net_margin_gbp"] == 100.0  # untouched
    assert records[1]["bad_debt_gbp"] == 35.0     # 5.0 + 30 delta
    assert records[1]["net_margin_gbp"] == 20.0   # 50.0 - 30 delta
    assert records[0]["treasury_cash_balance_gbp"] == 1000.0  # untouched -- correction lands from here on
    assert records[1]["treasury_cash_balance_gbp"] == 1020.0  # 1050 - 30 delta


def test_apply_emergent_bad_debt_noop_when_unchanged():
    records = [
        {"customer_id": "C1", "settlement_date": "2022-01-01", "bad_debt_gbp": 5.0,
         "net_margin_gbp": 100.0, "treasury_cash_balance_gbp": 1000.0},
    ]
    apply_emergent_bad_debt(records, {("C1", 2022): 5.0})
    assert records[0]["net_margin_gbp"] == 100.0
    assert records[0]["bad_debt_gbp"] == 5.0


def test_emergent_bad_debt_matches_billing_ledger_written_off(tmp_path):
    """Phase QD acceptance test: sum(WRITTEN_OFF arrears_gbp per year) from the
    billing ledger == emergent bad_debt applied to run_output records, for the
    same bills/behavioral/churned inputs -- the ledger and the P&L are
    provably the same source of truth.
    """
    bills = [_bill("C1", f"202{2 + i // 12}-{(i % 12) + 1:02d}-28", 200.0, "resi") for i in range(24)]
    bills += [_bill("C_IC1", f"202{2 + i // 12}-{(i % 12) + 1:02d}-28", 9000.0, "I&C") for i in range(24)]
    beh = {
        "C1": {"income_stress_trajectory": [{"year": 2022, "stress": "high"}, {"year": 2023, "stress": "high"}]},
    }
    churned = {"C1", "C_IC1"}

    emergent = compute_emergent_bad_debt(bills, beh, churned)

    run_json = tmp_path / "run.json"
    run_json.write_text(__import__("json").dumps({
        "bills": bills, "per_customer_behavioral": beh,
        "churned_billing_accounts": sorted(churned),
    }))
    ledger = generate_ledger(run_json, tmp_path / "ledger.json")

    ledger_writeoffs_by_year: dict[tuple, float] = {}
    for cid, cust in ledger["customers"].items():
        for case in cust["arrears_history"]:
            stages = {s["stage"]: s["date"] for s in case["stages"]}
            if "WRITTEN_OFF" in stages:
                year = int(stages["WRITTEN_OFF"][:4])
                key = (cid, year)
                ledger_writeoffs_by_year[key] = ledger_writeoffs_by_year.get(key, 0.0) + case["arrears_gbp"]

    assert ledger_writeoffs_by_year == emergent


def test_debt_archetype_overwhelmed_recent_onset():
    trajectory = [{'year': 2019, 'stress': 'low'}, {'year': 2020, 'stress': 'high'}]
    assert debt_archetype(trajectory, 2020) == 'OVERWHELMED'


def test_debt_archetype_overwhelmed_moderate_also_counts():
    trajectory = [{'year': 2019, 'stress': 'low'}, {'year': 2020, 'stress': 'moderate'}]
    assert debt_archetype(trajectory, 2020) == 'OVERWHELMED'


def test_debt_archetype_avoidant_two_consecutive_high_years():
    trajectory = [{'year': 2019, 'stress': 'high'}, {'year': 2020, 'stress': 'high'}]
    assert debt_archetype(trajectory, 2020) == 'AVOIDANT'


def test_debt_archetype_avoidant_three_consecutive_high_years():
    trajectory = [
        {'year': 2018, 'stress': 'high'}, {'year': 2019, 'stress': 'high'},
        {'year': 2020, 'stress': 'high'},
    ]
    assert debt_archetype(trajectory, 2020) == 'AVOIDANT'


def test_debt_archetype_neutral_no_trajectory():
    assert debt_archetype([], 2020) == 'NEUTRAL'


def test_debt_archetype_neutral_flat_low():
    trajectory = [{'year': 2019, 'stress': 'low'}, {'year': 2020, 'stress': 'low'}]
    assert debt_archetype(trajectory, 2020) == 'NEUTRAL'


def test_debt_archetype_single_high_year_reads_overwhelmed():
    trajectory = [{'year': 2020, 'stress': 'high'}]
    assert debt_archetype(trajectory, 2020) == 'OVERWHELMED'


def test_arrears_stages_written_off_unchanged_then_recovered_for_overwhelmed():
    written_off = arrears_stages(100.0, date(2022, 1, 1), False, archetype='OVERWHELMED')
    stage_names = [s['stage'] for s in written_off]
    assert stage_names == ['DD_FAILED', 'FIRST_NOTICE', 'SECOND_NOTICE', 'WRITTEN_OFF',
                           'PLACED_WITH_DCA', 'RECOVERED']
    wo = next(s for s in written_off if s['stage'] == 'WRITTEN_OFF')
    assert wo['date'] == (date(2022, 1, 1) + timedelta(days=90)).isoformat()
    recovered = written_off[-1]
    assert 'GBP' in recovered['note']


def test_arrears_stages_written_off_unchanged_then_recovered_for_neutral():
    written_off = arrears_stages(100.0, date(2022, 1, 1), False, archetype='NEUTRAL')
    stage_names = [s['stage'] for s in written_off]
    assert stage_names[-1] == 'RECOVERED'
    wo = next(s for s in written_off if s['stage'] == 'WRITTEN_OFF')
    assert wo['date'] == (date(2022, 1, 1) + timedelta(days=90)).isoformat()


def test_arrears_stages_written_off_unchanged_then_sold_for_avoidant():
    written_off = arrears_stages(100.0, date(2022, 1, 1), False, archetype='AVOIDANT')
    stage_names = [s['stage'] for s in written_off]
    assert stage_names == ['DD_FAILED', 'FIRST_NOTICE', 'SECOND_NOTICE', 'WRITTEN_OFF',
                           'PLACED_WITH_DCA', 'SOLD']
    wo = next(s for s in written_off if s['stage'] == 'WRITTEN_OFF')
    assert wo['date'] == (date(2022, 1, 1) + timedelta(days=90)).isoformat()
    sold = written_off[-1]
    assert 'GBP' in sold['note']


def test_arrears_stages_default_archetype_is_neutral():
    default = arrears_stages(100.0, date(2022, 1, 1), False)
    explicit_neutral = arrears_stages(100.0, date(2022, 1, 1), False, archetype='NEUTRAL')
    assert default == explicit_neutral


def test_ic_arrears_stages_written_off_unchanged_then_recovered():
    written_off = ic_arrears_stages(100.0, date(2022, 1, 1), False, archetype='NEUTRAL')
    stage_names = [s['stage'] for s in written_off]
    assert stage_names == ['INVOICE_DISPUTED', 'DISPUTE_NOTICE', 'WRITTEN_OFF',
                           'PLACED_WITH_DCA', 'RECOVERED']
    wo = next(s for s in written_off if s['stage'] == 'WRITTEN_OFF')
    assert wo['date'] == (date(2022, 1, 1) + timedelta(days=60)).isoformat()


def test_ic_arrears_stages_written_off_unchanged_then_sold_for_avoidant():
    written_off = ic_arrears_stages(100.0, date(2022, 1, 1), False, archetype='AVOIDANT')
    stage_names = [s['stage'] for s in written_off]
    assert stage_names == ['INVOICE_DISPUTED', 'DISPUTE_NOTICE', 'WRITTEN_OFF',
                           'PLACED_WITH_DCA', 'SOLD']
    wo = next(s for s in written_off if s['stage'] == 'WRITTEN_OFF')
    assert wo['date'] == (date(2022, 1, 1) + timedelta(days=60)).isoformat()


def test_compute_debt_recovery_deterministic():
    bills = [_bill('C1', f'202{2 + i // 12}-{(i % 12) + 1:02d}-28', 200.0, 'resi') for i in range(24)]
    beh = {'C1': {'income_stress_trajectory': [{'year': 2022, 'stress': 'high'}, {'year': 2023, 'stress': 'high'}]}}
    r1 = compute_debt_recovery(bills, beh, churned_ids={'C1'})
    r2 = compute_debt_recovery(bills, beh, churned_ids={'C1'})
    assert r1 == r2
    assert sum(r1.values()) > 0


def test_compute_debt_recovery_only_counts_written_off_cases():
    bills = [_bill('C1', f'202{2 + i // 12}-{(i % 12) + 1:02d}-28', 200.0, 'resi') for i in range(24)]
    beh = {'C1': {'income_stress_trajectory': [{'year': 2022, 'stress': 'high'}, {'year': 2023, 'stress': 'high'}]}}
    result = compute_debt_recovery(bills, beh, churned_ids=set())
    assert result == {}


def test_apply_debt_recovery_reduces_bad_debt_and_increases_margin():
    records = [
        {'customer_id': 'C1', 'settlement_date': '2022-01-01', 'bad_debt_gbp': 40.0,
         'net_margin_gbp': 100.0, 'treasury_cash_balance_gbp': 1000.0},
        {'customer_id': 'C1', 'settlement_date': '2022-06-01', 'bad_debt_gbp': 0.0,
         'net_margin_gbp': 50.0, 'treasury_cash_balance_gbp': 1050.0},
    ]
    apply_debt_recovery(records, {('C1', 2022): 30.0})
    assert records[0]['net_margin_gbp'] == 100.0
    assert records[0]['bad_debt_gbp'] == 40.0
    assert records[1]['bad_debt_gbp'] == -30.0
    assert records[1]['net_margin_gbp'] == 80.0
    assert records[0]['treasury_cash_balance_gbp'] == 1000.0
    assert records[1]['treasury_cash_balance_gbp'] == 1080.0


def test_apply_debt_recovery_noop_when_zero():
    records = [
        {'customer_id': 'C1', 'settlement_date': '2022-01-01', 'bad_debt_gbp': 5.0,
         'net_margin_gbp': 100.0, 'treasury_cash_balance_gbp': 1000.0},
    ]
    apply_debt_recovery(records, {('C1', 2022): 0.0})
    assert records[0]['net_margin_gbp'] == 100.0
    assert records[0]['bad_debt_gbp'] == 5.0
    assert records[0]['treasury_cash_balance_gbp'] == 1000.0


# --- Layer 2 dimension 2: fuel poverty modifier on payment_outcome() (2026-07-09) ---


def test_fuel_poor_for_bill_false_when_no_customer_id():
    assert _fuel_poor_for_bill("direct_debit", None) is False


def test_fuel_poor_for_bill_false_for_corp_methods():
    assert _fuel_poor_for_bill("bacs", "C1") is False
    assert _fuel_poor_for_bill("chaps", "C1") is False


def test_fuel_poor_for_bill_deterministic():
    a = _fuel_poor_for_bill("direct_debit", "C1")
    b = _fuel_poor_for_bill("direct_debit", "C1")
    assert a == b


def test_payment_outcome_default_matches_no_fuel_poor_flag():
    """Backward compatibility: fuel_poor defaults to False, must reproduce
    the exact original probability behaviour bit-for-bit against the same
    RNG seed."""
    import random
    rng_a = random.Random(42)
    rng_b = random.Random(42)
    for _ in range(200):
        a = payment_outcome("direct_debit", "MODERATE", rng_a, segment="resi")
        b = payment_outcome("direct_debit", "MODERATE", rng_b, segment="resi", fuel_poor=False)
        assert a == b


def test_payment_outcome_fuel_poor_increases_failure_rate():
    """A large sample at fixed stress must show a higher failure rate when
    fuel_poor=True than when False, matching the multiplier direction."""
    import random
    n = 3000
    rng1 = random.Random(7)
    fails_normal = sum(
        payment_outcome("direct_debit", "MODERATE", rng1, segment="resi", fuel_poor=False)[0] == "failed"
        for _ in range(n)
    )
    rng2 = random.Random(7)
    fails_poor = sum(
        payment_outcome("direct_debit", "MODERATE", rng2, segment="resi", fuel_poor=True)[0] == "failed"
        for _ in range(n)
    )
    assert fails_poor > fails_normal


def test_fuel_poverty_multipliers_are_bounded():
    assert FUEL_POVERTY_DD_FAIL_MULTIPLIER >= 1.0
    assert 0.0 < FUEL_POVERTY_ON_TIME_MULTIPLIER <= 1.0
