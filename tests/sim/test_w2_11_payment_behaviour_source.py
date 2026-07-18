"""W2_11_payment_behaviour_source -- payment-behaviour generator (sim-source,
world side, coupled-triad W of the D5 decomposition).

Covers:
  * RNG SUBSTREAM ISOLATION (C-S2, the 01:09Z incident) -- per-customer AND
    per-period substreams; advancing this subsystem leaves every named
    sibling (population_draw, life_events, household_budget, sme_distress,
    dd_attribution) BYTE-IDENTICAL, and never touches the global `random`
    module. This is the load-bearing test class per the build brief.
  * DETERMINISTIC REPLAY (C-S2) on (customer_id, seed), across processes.
  * The four FRAME behaviour dimensions: payment TIMING, DD success/failure
    WITH REASON, arrears/late-payment AGEING, payment-METHOD mix.
  * Anchored plausibility (DESNZ/Ofgem DD share) -- diagnostic bands, R12/R13.
  * Epistemic wall: pure sim, no company/saas import.
"""
from __future__ import annotations

import hashlib
import random
from datetime import date
from pathlib import Path

import pytest

from simulation import payment_behaviour_source as pbs

REPO_ROOT = Path(__file__).resolve().parents[2]


def _due_dates(n=12, start_year=2024):
    return [(date(start_year + (i // 12), (i % 12) + 1, 15), 100.0) for i in range(n)]


# -- 1. Substream contract ----------------------------------------------------

def test_substream_names_are_unique():
    assert len(pbs._SUBSTREAMS) == len(set(pbs._SUBSTREAMS))


def test_substream_is_deterministic():
    a = [pbs._substream(999, "payment_method").random() for _ in range(10)]
    b = [pbs._substream(999, "payment_method").random() for _ in range(10)]
    assert a == b


def test_substream_value_is_stable_across_processes():
    # sha256-derived, NOT Python's per-process-salted hash(): a regression to a
    # salted seed would break C-S2 deterministic replay and fail this exact value.
    key = "W2_11_payment_behaviour_source::payment_method::12345".encode("utf-8")
    expected_seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    assert pbs._substream(12345, "payment_method").random() == \
        random.Random(expected_seed).random()


def test_distinct_substreams_produce_different_sequences():
    a = [pbs._substream(555, "payment_method").random() for _ in range(20)]
    b = [pbs._substream(555, "payment_method_submethod").random() for _ in range(20)]
    assert a != b


def test_base_seed_from_customer_id_is_stable_and_process_independent():
    expected = int(hashlib.md5(b"C7").hexdigest()[:8], 16)
    assert pbs._base_seed_for("C7", None) == expected
    assert pbs._base_seed_for("C7", 42) == 42  # explicit seed passes through


def test_period_substream_isolates_by_period_index():
    """Different period indices under the SAME base_seed/base_name must never
    produce the same draw sequence -- the per-period isolation this module
    adds on top of the per-customer substream pattern."""
    a = [pbs._period_substream(42, "payment_event", 0).random() for _ in range(20)]
    b = [pbs._period_substream(42, "payment_event", 1).random() for _ in range(20)]
    assert a != b


def test_period_substream_is_deterministic():
    a = [pbs._period_substream(42, "payment_event", 3).random() for _ in range(10)]
    b = [pbs._period_substream(42, "payment_event", 3).random() for _ in range(10)]
    assert a == b


# -- 2. THE headline C-S2 guarantee: this substream can't shift a sibling -----

def test_new_substream_does_not_shift_existing_substream():
    base = 424242
    before = [pbs._substream(base, "payment_method").random() for _ in range(50)]
    _ = [pbs._substream(base, "some_future_mechanism").random() for _ in range(500)]
    after = [pbs._substream(base, "payment_method").random() for _ in range(50)]
    assert before == after


def test_draining_one_period_never_shifts_another_period():
    base = 7788
    reference = {
        i: [pbs._period_substream(base, "payment_event", i).random() for _ in range(30)]
        for i in range(10)
    }
    _ = [pbs._period_substream(base, "payment_event", 999).random() for _ in range(1000)]
    for i in range(10):
        assert [pbs._period_substream(base, "payment_event", i).random() for _ in range(30)] == reference[i]


def test_advancing_pbs_does_not_perturb_global_random():
    random.seed(12345)
    before = [random.random() for _ in range(20)]
    random.seed(12345)
    _ = [pbs.generate_customer_payment_history(f"G{i}", _due_dates(6), seed=i) for i in range(50)]
    after = [random.random() for _ in range(20)]
    assert before == after


def test_advancing_pbs_leaves_population_draw_byte_identical():
    from simulation import population_draw as pdraw
    baseline = pdraw.draw_population(base_seed=808)
    _ = [pbs.generate_customer_payment_history(f"P{i}", _due_dates(6), seed=i) for i in range(80)]
    assert pdraw.draw_population(base_seed=808) == baseline


def test_advancing_pbs_leaves_life_events_byte_identical():
    from simulation.household import make_household
    from simulation.life_events import generate_life_events
    hh = make_household(
        {"customer_id": "C1", "home_type": "suburban_semi",
         "epc_rating": "C", "segment": "resi"}
    )
    baseline = generate_life_events(hh, 2016, 2025)
    _ = [pbs.generate_customer_payment_history(f"L{i}", _due_dates(6), seed=i) for i in range(80)]
    assert generate_life_events(hh, 2016, 2025) == baseline


def test_advancing_pbs_leaves_household_budget_byte_identical():
    from simulation.household_budget import draw_household_budget
    baseline = draw_household_budget("BUDGET_CUST_42")
    _ = [pbs.generate_customer_payment_history(f"B{i}", _due_dates(6), seed=i) for i in range(80)]
    assert draw_household_budget("BUDGET_CUST_42") == baseline


def test_advancing_pbs_leaves_sme_distress_byte_identical():
    from simulation.sme_distress import generate_business_distress
    baseline = generate_business_distress("BIZ9", "SME", 2016, 2025, seed=9)
    _ = [pbs.generate_customer_payment_history(f"D{i}", _due_dates(6), seed=i) for i in range(80)]
    assert generate_business_distress("BIZ9", "SME", 2016, 2025, seed=9) == baseline


def test_advancing_pbs_leaves_dd_attribution_byte_identical():
    from simulation.dd_attribution import generate_dd_attribution
    baseline = generate_dd_attribution("DDCUST1", seed=1)
    _ = [pbs.generate_customer_payment_history(f"A{i}", _due_dates(6), seed=i) for i in range(80)]
    assert generate_dd_attribution("DDCUST1", seed=1) == baseline


def test_advancing_arrears_engine_batch_does_not_shift_pbs():
    """The reverse direction: calling the shared arrears_engine batch machinery
    (which THIS module wraps, on a fresh global RNG of its own) must not shift
    this module's own substreams either -- proves the wrapper's isolation is
    not accidentally one-directional."""
    from simulation import arrears_engine as ae
    baseline = pbs.generate_customer_payment_history("ISO1", _due_dates(6), seed=1)
    bills = [{"customer_id": "X", "period_end": "2024-01-31",
              "total_amount_gbp": 100.0, "segment": "resi", "commodity": "electricity"}]
    _ = ae.compute_emergent_bad_debt(bills, {}, set(), seed=42)
    assert pbs.generate_customer_payment_history("ISO1", _due_dates(6), seed=1) == baseline


# -- 3. Deterministic replay (C-S2) -------------------------------------------

def test_deterministic_replay_identical_profile_same_seed():
    a = pbs.generate_customer_payment_history("C42", _due_dates(6), seed=13)
    b = pbs.generate_customer_payment_history("C42", _due_dates(6), seed=13)
    assert a == b  # frozen dataclasses compare by value


def test_deterministic_replay_survives_intervening_global_rng_use():
    a = pbs.generate_customer_payment_history("C77", _due_dates(6))
    random.seed()
    _ = [random.random() for _ in range(1000)]
    b = pbs.generate_customer_payment_history("C77", _due_dates(6))
    assert a == b


def test_different_customers_generally_differ():
    profiles = [pbs.generate_customer_payment_history(f"CUST{i}", _due_dates(6), seed=i) for i in range(40)]
    shapes = {(p.payment_method, p.pattern, tuple(e.result for e in p.events)) for p in profiles}
    assert len(shapes) > 1


# -- 4. Payment TIMING (early/on-time/late) -----------------------------------

def test_low_stress_mostly_on_time_high_stress_mostly_late_or_failed():
    """Structural sanity on the reused arrears_engine anchors: LOW-stress
    customers should look much healthier than HIGH-stress ones."""
    low_events, high_events = [], []
    for i in range(300):
        low_events += list(pbs.generate_customer_payment_history(
            f"LOW{i}", _due_dates(3), stress_trajectory=[{"year": 2024, "stress": "low"}], seed=i
        ).events)
        high_events += list(pbs.generate_customer_payment_history(
            f"HIGH{i}", _due_dates(3), stress_trajectory=[{"year": 2024, "stress": "high"}], seed=i
        ).events)
    low_problem_rate = sum(e.is_late or e.is_unresolved for e in low_events) / len(low_events)
    high_problem_rate = sum(e.is_late or e.is_unresolved for e in high_events) / len(high_events)
    assert low_problem_rate < high_problem_rate


def test_on_time_event_has_payment_date_equal_to_due_date():
    ev = None
    for i in range(200):
        e = pbs.generate_payment_event(f"T{i}", 0, date(2024, 1, 15), 100.0, "LOW", pbs.DIRECT_DEBIT, seed=i)
        if e.result == "success" and e.days_late == 0:
            ev = e
            break
    assert ev is not None, "expected at least one on-time draw in 200 tries"
    assert ev.payment_date == ev.due_date


# -- 5. DD SUCCESS/FAILURE with REASON ----------------------------------------

def test_failed_payment_carries_a_reason_success_does_not():
    for i in range(200):
        ev = pbs.generate_payment_event(f"R{i}", 0, date(2024, 1, 15), 100.0, "HIGH", pbs.DIRECT_DEBIT, seed=i)
        if ev.result == "failed":
            assert ev.dd_failure_reason in (pbs.INSUFFICIENT_FUNDS, pbs.CANCELLED_OTHER)
            assert ev.payment_date is None
        else:
            assert ev.dd_failure_reason is None


def test_dd_failure_reason_split_direction_insufficient_funds_dominant():
    """Direction anchored to bacs_rails.py's ARUDD-dominant-code citation
    (Refer to Payer / insufficient funds is the real-world dominant DD-failure
    cause) -- diagnostic band, not a tuned target (R12)."""
    reasons = []
    for i in range(2000):
        ev = pbs.generate_payment_event(f"REASON{i}", 0, date(2024, 1, 15), 100.0, "HIGH", pbs.DIRECT_DEBIT, seed=i)
        if ev.dd_failure_reason is not None:
            reasons.append(ev.dd_failure_reason)
    assert reasons, "expected some DD failures at HIGH stress across 2000 draws"
    share_insufficient = reasons.count(pbs.INSUFFICIENT_FUNDS) / len(reasons)
    assert 0.65 < share_insufficient < 0.98


# -- 6. Arrears / late-payment AGEING -----------------------------------------

def test_arrears_age_days_zero_when_paid_before_as_of():
    assert pbs.arrears_age_days("2024-01-15", "2024-03-01", "2024-01-20") == 0


def test_arrears_age_days_positive_when_unpaid():
    assert pbs.arrears_age_days("2024-01-15", "2024-03-01", None) == 46


def test_arrears_age_days_never_negative():
    assert pbs.arrears_age_days("2024-03-01", "2024-01-15", None) == 0


@pytest.mark.parametrize("age,expected", [
    (0, "current"), (-5, "current"), (15, "0-30"), (30, "0-30"),
    (31, "31-60"), (60, "31-60"), (61, "61-90"), (90, "61-90"), (91, "90+"),
])
def test_ageing_bucket_boundaries(age, expected):
    assert pbs.ageing_bucket(age) == expected


def test_ageing_as_of_reflects_unresolved_events():
    profile = pbs.generate_customer_payment_history(
        "AGE1", _due_dates(3), stress_trajectory=[{"year": 2024, "stress": "high"}], seed=1
    )
    ageing = profile.ageing_as_of("2025-01-01")
    assert set(ageing) == {0, 1, 2}
    for idx, (age_days, bucket) in ageing.items():
        assert age_days >= 0
        assert bucket in pbs.AGEING_BUCKETS


# -- 7. Payment-METHOD mix -----------------------------------------------------

def test_payment_method_is_one_of_the_four_taxonomy_values():
    for i in range(200):
        m = pbs.generate_payment_method(f"M{i}", seed=i)
        assert m in (pbs.DIRECT_DEBIT, pbs.STANDING_ORDER, pbs.CARD, pbs.PREPAYMENT)


def test_payment_method_is_persistent_per_customer():
    a = pbs.generate_payment_method("STABLE1", seed=5)
    b = pbs.generate_payment_method("STABLE1", seed=5)
    assert a == b


def test_dd_share_tracks_the_desnz_anchor():
    """DESNZ June 2026: DD ~72% of electricity customers. Diagnostic band (R12)."""
    methods = [pbs.generate_payment_method(f"SHARE{i}", seed=i) for i in range(4000)]
    dd_share = sum(m == pbs.DIRECT_DEBIT for m in methods) / len(methods)
    assert 0.62 < dd_share < 0.82, f"DD share {dd_share:.3f} off the DESNZ anchor"


def test_gas_dd_share_is_higher_than_electricity_per_desnz_anchor():
    elec = [pbs.generate_payment_method(f"FUEL{i}", fuel="electricity", seed=i) for i in range(3000)]
    gas = [pbs.generate_payment_method(f"FUEL{i}", fuel="gas", seed=i) for i in range(3000)]
    elec_share = sum(m == pbs.DIRECT_DEBIT for m in elec) / len(elec)
    gas_share = sum(m == pbs.DIRECT_DEBIT for m in gas) / len(gas)
    assert gas_share > elec_share


# -- 8. Payment PATTERN classification (chronic / transient) ------------------

def test_classify_payment_pattern_empty_is_consistent_on_time():
    assert pbs.classify_payment_pattern([]) == "CONSISTENT_ON_TIME"


def test_classify_payment_pattern_chronic_high_stress_more_often_chronic():
    low_patterns = [
        pbs.generate_customer_payment_history(
            f"PATL{i}", _due_dates(8), stress_trajectory=[{"year": y, "stress": "low"} for y in range(2024, 2026)], seed=i
        ).pattern for i in range(150)
    ]
    high_patterns = [
        pbs.generate_customer_payment_history(
            f"PATH{i}", _due_dates(8), stress_trajectory=[{"year": y, "stress": "high"} for y in range(2024, 2026)], seed=i
        ).pattern for i in range(150)
    ]
    assert low_patterns.count("CHRONIC") < high_patterns.count("CHRONIC")


# -- 9. Epistemic wall + data_regime -------------------------------------------

def test_module_does_not_import_company_or_saas():
    src = (REPO_ROOT / "simulation" / "payment_behaviour_source.py").read_text()
    for banned in ("import company", "from company", "import saas", "from saas"):
        assert banned not in src, f"epistemic-wall violation: '{banned}' in payment_behaviour_source.py"


def test_data_regime_is_synthetic():
    ev = pbs.generate_payment_event("REG1", 0, date(2024, 1, 15), 100.0, "LOW", pbs.DIRECT_DEBIT, seed=1)
    assert ev.data_regime == "synthetic"
    profile = pbs.generate_customer_payment_history("REG2", _due_dates(3), seed=1)
    assert profile.data_regime == "synthetic"
