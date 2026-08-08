"""Phase QD -- tests for simulation.arrears_engine.

Verifies the shared payment-outcome/arrears engine, and -- the draft phase's
explicit acceptance criterion -- that the emergent bad debt fed into
run_output records (via apply_emergent_bad_debt) is provably the same
figure the per-customer billing ledger reports as WRITTEN_OFF, because both
draw from the same deterministic engine over the same bills.
"""
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from simulation.arrears_engine import (
    FUEL_POVERTY_DD_FAIL_MULTIPLIER,
    FUEL_POVERTY_ON_TIME_MULTIPLIER,
    _fuel_poor_for_bill,
    _tone_for_bill,
    apply_debt_recovery,
    apply_emergent_bad_debt,
    arrears_stages,
    bill_substream,
    compute_debt_recovery,
    compute_emergent_bad_debt,
    debt_archetype,
    ic_arrears_stages,
    opening_arrears_stage,
    payment_method,
    payment_outcome,
    stress_for_year,
)
from tools.generate_billing_ledger import generate as generate_ledger

REPO_ROOT = Path(__file__).resolve().parents[2]


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
    resolved = arrears_stages(100.0, date(2022, 1, 1), True, method='direct_debit')
    written_off = arrears_stages(100.0, date(2022, 1, 1), False, method='direct_debit')
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
    written_off = arrears_stages(100.0, date(2022, 1, 1), False, archetype='OVERWHELMED', method='direct_debit')
    stage_names = [s['stage'] for s in written_off]
    assert stage_names == ['DD_FAILED', 'FIRST_NOTICE', 'SECOND_NOTICE', 'WRITTEN_OFF',
                           'PLACED_WITH_DCA', 'RECOVERED']
    wo = next(s for s in written_off if s['stage'] == 'WRITTEN_OFF')
    assert wo['date'] == (date(2022, 1, 1) + timedelta(days=90)).isoformat()
    recovered = written_off[-1]
    assert 'GBP' in recovered['note']


def test_arrears_stages_written_off_unchanged_then_recovered_for_neutral():
    written_off = arrears_stages(100.0, date(2022, 1, 1), False, archetype='NEUTRAL', method='direct_debit')
    stage_names = [s['stage'] for s in written_off]
    assert stage_names[-1] == 'RECOVERED'
    wo = next(s for s in written_off if s['stage'] == 'WRITTEN_OFF')
    assert wo['date'] == (date(2022, 1, 1) + timedelta(days=90)).isoformat()


def test_arrears_stages_written_off_unchanged_then_sold_for_avoidant():
    written_off = arrears_stages(100.0, date(2022, 1, 1), False, archetype='AVOIDANT', method='direct_debit')
    stage_names = [s['stage'] for s in written_off]
    assert stage_names == ['DD_FAILED', 'FIRST_NOTICE', 'SECOND_NOTICE', 'WRITTEN_OFF',
                           'PLACED_WITH_DCA', 'SOLD']
    wo = next(s for s in written_off if s['stage'] == 'WRITTEN_OFF')
    assert wo['date'] == (date(2022, 1, 1) + timedelta(days=90)).isoformat()
    sold = written_off[-1]
    assert 'GBP' in sold['note']


def test_arrears_stages_default_archetype_is_neutral():
    default = arrears_stages(100.0, date(2022, 1, 1), False, method='direct_debit')
    explicit_neutral = arrears_stages(100.0, date(2022, 1, 1), False, archetype='NEUTRAL', method='direct_debit')
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


# --- NUDGE_PHYSICS.md remaining mechanism: debt-collection letter tone (2026-07-10) ---

def test_tone_for_bill_none_when_no_customer_id():
    assert _tone_for_bill("direct_debit", None, "2020-01-31") is None


def test_tone_for_bill_none_for_corp_methods():
    assert _tone_for_bill("bacs", "C1", "2020-01-31") is None
    assert _tone_for_bill("chaps", "C1", "2020-01-31") is None


def test_tone_for_bill_returns_a_real_tone_for_resi():
    tone = _tone_for_bill("direct_debit", "C1", "2020-01-31")
    assert tone in ("empathetic_toned", "firm_toned")


def test_tone_for_bill_deterministic():
    a = _tone_for_bill("direct_debit", "C1", "2020-01-31")
    b = _tone_for_bill("direct_debit", "C1", "2020-01-31")
    assert a == b


def test_payment_outcome_default_matches_no_tone_or_customer_id():
    """Backward compatibility: tone/customer_id default to None, must
    reproduce the exact original probability behaviour bit-for-bit."""
    import random
    rng_a = random.Random(42)
    rng_b = random.Random(42)
    for _ in range(200):
        a = payment_outcome("direct_debit", "MODERATE", rng_a, segment="resi")
        b = payment_outcome("direct_debit", "MODERATE", rng_b, segment="resi", tone=None, customer_id=None)
        assert a == b


def test_payment_outcome_tone_without_customer_id_is_a_noop():
    """tone alone (no customer_id) must not change behaviour -- there is
    nothing to resolve a multiplier against."""
    import random
    rng_a = random.Random(7)
    rng_b = random.Random(7)
    for _ in range(200):
        a = payment_outcome("direct_debit", "MODERATE", rng_a, segment="resi")
        b = payment_outcome("direct_debit", "MODERATE", rng_b, segment="resi", tone="firm_toned")
        assert a == b


def test_payment_outcome_matched_tone_increases_on_time_rate():
    """A large sample at fixed stress, across many customers, must show a
    higher on-time-or-better rate when a MATCHED tone is applied to
    susceptible customers than with no tone at all."""
    import random

    from simulation.nudge_physics import ToneSusceptibility, tone_susceptibility_for

    n = 2000
    successes_no_tone = 0
    successes_with_tone = 0
    for i in range(n):
        cid = f"TONE_{i}"
        susc = tone_susceptibility_for(cid)
        if susc == ToneSusceptibility.FIRM_RESPONSIVE:
            matched_tone = "firm_toned"
        elif susc == ToneSusceptibility.EMPATHETIC_RESPONSIVE:
            matched_tone = "empathetic_toned"
        else:
            continue
        rng1 = random.Random(f"seed_{cid}")
        outcome_no_tone, _ = payment_outcome("direct_debit", "MODERATE", rng1, segment="resi", customer_id=cid)
        rng2 = random.Random(f"seed_{cid}")
        outcome_with_tone, _ = payment_outcome(
            "direct_debit", "MODERATE", rng2, segment="resi", tone=matched_tone, customer_id=cid
        )
        successes_no_tone += outcome_no_tone == "success"
        successes_with_tone += outcome_with_tone == "success"
    assert successes_with_tone >= successes_no_tone


# --- Method-aware arrears opening stage (atom
# W2_payment_channel_dd_consistency_invariant) ---
#
# These sit on the GENERATOR, deliberately. The population test in
# tests/company/compliance/test_payment_channel_dd_consistency.py judges the
# billing ledger, which is a build ARTEFACT -- a source mutation here does not
# move it until it is regenerated, so the artefact test alone would let a
# regression sit green until the next publish. These fire on the source.

def test_a_direct_debit_arrears_case_still_opens_with_dd_failed():
    """Direction (b): the legitimate case is untouched."""
    stages = arrears_stages(100.0, date(2022, 1, 1), True, method='direct_debit')
    assert stages[0]['stage'] == 'DD_FAILED'
    assert stages[0]['note'] == 'Direct debit returned'


def test_a_standard_credit_arrears_case_does_not_open_with_a_dd_failure():
    """Direction (a): the named defect. A customer with no Direct Debit
    Instruction has nothing that could be returned."""
    stages = arrears_stages(100.0, date(2022, 1, 1), True, method='standard_credit')
    assert stages[0]['stage'] == 'PAYMENT_MISSED'
    assert 'direct debit' not in stages[0]['note'].lower()


def test_every_non_dd_method_gets_a_method_appropriate_opening_stage():
    """R10 -- the closure is the CLASS. Every non-DD label the two generators
    can emit, not just the standard_credit instance that was reported."""
    for method in ('standard_credit', 'standing_order', 'card', 'prepayment',
                   'bacs', 'chaps'):
        opening = opening_arrears_stage(method, date(2022, 1, 1))
        assert opening['stage'] == 'PAYMENT_MISSED', method
        assert 'direct debit' not in opening['note'].lower(), method


def test_an_unknown_method_does_not_fall_back_to_a_direct_debit_failure():
    """Fail-closed: a method nobody anticipated must not inherit the DD
    vocabulary by default."""
    opening = opening_arrears_stage('carrier_pigeon', date(2022, 1, 1))
    assert opening['stage'] == 'PAYMENT_MISSED'
    assert 'direct debit' not in opening['note'].lower()


def test_method_is_a_required_argument_so_an_unupdated_caller_fails_loudly():
    """A default of 'direct_debit' would have preserved the exact defect the
    parameter exists to remove -- every un-migrated caller would keep stamping
    'Direct debit returned' onto non-DD customers while the build read as done.
    This is the guard that keeps the argument required."""
    with pytest.raises(TypeError):
        arrears_stages(100.0, date(2022, 1, 1), True)


def test_the_collections_cascade_after_the_opening_stage_is_method_independent():
    """Only the FIRST stage is method-specific: once the money is late the
    collections process is the same. Asserting this stops a future change from
    quietly forking the whole cascade per method."""
    dd = arrears_stages(100.0, date(2022, 1, 1), False, method='direct_debit')
    sc = arrears_stages(100.0, date(2022, 1, 1), False, method='standard_credit')
    assert [s['stage'] for s in dd[1:]] == [s['stage'] for s in sc[1:]]
    assert [s['date'] for s in dd] == [s['date'] for s in sc]


# ---------------------------------------------------------------------------
# W2_16 -- C-S2 RNG substream isolation for the per-bill payment outcome.
#
# Before this atom every consumer advanced ONE shared random.Random(seed) over
# the bills in sorted order, so a bill's outcome depended on how many draws
# every alphabetically-earlier bill consumed. These tests pin the property that
# replaced it: a bill's outcome is a pure function of its own identity.
# ---------------------------------------------------------------------------

def _credit_bill(cid, period_end):
    """A REAL credit invoice's shape (modelled on C1g 2021-07-31 in
    docs/reports/run_output_latest.json): every line item positive, the total
    driven negative by an overcharge catch-up adjustment. That shape matters --
    it passes the pre-bill validation gate, so it reaches the ledger, where
    `generate()` skips the payment-outcome draw for it. Under the old shared
    stream that skip is exactly what offset the ledger from the P&L.
    """
    ps = (date.fromisoformat(period_end) - timedelta(days=30)).isoformat()
    return {
        "customer_id": cid, "period_start": ps, "period_end": period_end,
        "total_consumption_kwh": 382.19, "commodity_amount_gbp": 10.72,
        "non_commodity_amount_gbp": 4.59, "standing_charge_gbp": 8.06,
        "vat_gbp": 1.17, "total_amount_gbp": -21.95,
        "average_unit_rate_gbp_per_mwh": 28.05, "clarity_score": 0.5,
        "bill_shock_pct": None, "segment": "resi", "commodity": "gas",
        "days_in_period": 30, "standing_charge_gbp_per_day": 0.26,
        "billing_basis": "actual", "catchup_applied": True,
        "catchup_adjustment_gbp": -46.49, "catchup_direction": "overcharge",
    }


def _outcome_for(bill, behavioral, seed=42):
    """Resolve one bill exactly as the engine's consumers do."""
    cid, period_end = bill["customer_id"], bill["period_end"]
    segment = bill.get("segment", "resi")
    method = payment_method(segment, bill["total_amount_gbp"], cid, bill.get("commodity", "electricity"))
    stress = stress_for_year(behavioral.get(cid) or {}, int(period_end[:4]))
    return payment_outcome(
        method, stress, bill_substream(seed, cid, period_end, bill.get("commodity", "electricity")),
        segment, _fuel_poor_for_bill(method, cid), _tone_for_bill(method, cid, period_end), cid,
    )


def _stress_beh(cid, years, level="high"):
    return {cid: {"income_stress_trajectory": [{"year": y, "stress": level} for y in years]}}


def test_bill_outcome_does_not_depend_on_iteration_order():
    """The property the shared stream could not offer: resolving the bills in a
    different order must not change a single outcome."""
    bills = [_bill(f"C{c}", f"2022-{m:02d}-28", 200.0) for c in range(1, 8) for m in range(1, 13)]
    beh = _stress_beh("C1", [2022])
    forward = {(b["customer_id"], b["period_end"]): _outcome_for(b, beh) for b in bills}
    backward = {(b["customer_id"], b["period_end"]): _outcome_for(b, beh) for b in reversed(bills)}
    assert forward == backward


def test_improving_one_segments_model_cannot_rewrite_another_customers_history():
    """THE defect W2_16 names, in miniature. Removing C2/C3's bills entirely --
    the crudest possible stand-in for "their model changed how many draws they
    consume" -- must leave every OTHER customer's outcome untouched.

    Measured instance this pins: the W2_sme_segment_case_normalisation fix moved
    resi C7's longest undischarged credit from 1224 days to 32, purely because
    SME customers sort earlier and changed their draw count.
    """
    bills = [_bill(f"C{c}", f"2022-{m:02d}-28", 200.0) for c in range(1, 8) for m in range(1, 13)]
    beh = _stress_beh("C1", [2022])
    full = {(b["customer_id"], b["period_end"]): _outcome_for(b, beh) for b in bills}

    survivors = [b for b in bills if b["customer_id"] not in ("C2", "C3")]
    reduced = {(b["customer_id"], b["period_end"]): _outcome_for(b, beh) for b in survivors}

    assert reduced, "vacuity guard: the reduced set must still contain bills"
    assert len(reduced) < len(full), "vacuity guard: bills must actually have been removed"
    assert all(reduced[k] == full[k] for k in reduced)


def test_ledger_and_pl_agree_on_written_off_cases_when_a_credit_invoice_is_present(tmp_path):
    """The regression that the pre-W2_16 acceptance test could not catch.

    `test_emergent_bad_debt_matches_billing_ledger_written_off` above passed
    throughout the defect's life only because its fixture contains no credit
    invoice -- with no skipped draw the two streams never drifted apart, so a
    green result there was fail-open evidence. Adding ONE real-shaped credit
    invoice EARLY in sorted order is what desynchronised the real run (24 such
    bills, first at sorted index 138 of 1557, 42 failed/dispute decisions
    disagreeing between the ledger and the P&L).
    """
    bills = [_credit_bill("C0", "2022-01-31")]
    bills += [_bill("C1", f"202{2 + i // 12}-{(i % 12) + 1:02d}-28", 200.0, "resi") for i in range(24)]
    bills += [_bill("C_IC1", f"202{2 + i // 12}-{(i % 12) + 1:02d}-28", 9000.0, "I&C") for i in range(24)]
    beh = _stress_beh("C1", [2022, 2023])
    churned = {"C1", "C_IC1"}

    emergent = compute_emergent_bad_debt(bills, beh, churned)
    assert emergent, "vacuity guard: the fixture must actually produce written-off cases"

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
                key = (cid, int(stages["WRITTEN_OFF"][:4]))
                ledger_writeoffs_by_year[key] = ledger_writeoffs_by_year.get(key, 0.0) + case["arrears_gbp"]

    assert ledger_writeoffs_by_year == emergent


def test_bill_substream_is_stable_across_processes():
    """C-S2 replay: the seed must come from sha256, never Python's
    per-process-salted hash(). Pinning a literal value is what makes a switch
    to hash()-derived seeding fail here rather than silently break replay
    between processes."""
    drawn = bill_substream(42, "C1", "2022-01-28", "electricity").random()
    expected = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '.');"
         "from simulation.arrears_engine import bill_substream;"
         "print(repr(bill_substream(42, 'C1', '2022-01-28', 'electricity').random()))"],
        capture_output=True, text=True, cwd=REPO_ROOT, check=True,
    ).stdout.strip()
    assert repr(drawn) == expected


def test_each_bill_gets_a_distinct_substream():
    """Two bills sharing a stream would reintroduce the coupling by the back
    door -- one bill's draws would shift the other's."""
    seen = {
        (cid, pe, fuel): bill_substream(42, cid, pe, fuel).random()
        for cid in ("C1", "C2", "C10")
        for pe in ("2022-01-28", "2022-02-28", "2022-01-29")
        for fuel in ("electricity", "gas")
    }
    assert len(set(seen.values())) == len(seen)


def test_substream_key_components_cannot_be_confused():
    """The (customer_id, period_end) pair is joined with a separator, so no
    two different pairs can collide into one key by concatenation."""
    assert (bill_substream(42, "C1", "2022-01-28", "electricity").random()
            != bill_substream(42, "C12", "022-01-28", "electricity").random())
    assert (bill_substream(42, "C1", "2022-01-28", "electricity").random()
            != bill_substream(43, "C1", "2022-01-28", "electricity").random())
    # The dual-fuel collision `commodity` exists to prevent: one account, one
    # period, two meters must never share a payment-outcome stream.
    assert (bill_substream(42, "C1", "2022-01-28", "electricity").random()
            != bill_substream(42, "C1", "2022-01-28", "gas").random())


def test_commodity_is_a_required_substream_key_component():
    """Same reasoning as `method` on arrears_stages: a default would let an
    un-migrated caller silently collapse an account's gas and electricity bills
    for one period onto a single stream, tying their outcomes together -- the
    exact silent coupling this atom removes. It must fail loudly instead."""
    with pytest.raises(TypeError):
        bill_substream(42, "C1", "2022-01-28")
