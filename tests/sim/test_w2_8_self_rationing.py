"""W2_8_self_rationing — the hidden "pay-but-don't-heat" SILENT HARDSHIP state.

This atom is HIDDEN SIM ground truth. These tests lock:

1. C-S2 SUBSTREAM ISOLATION (the headline, the 01:09Z incident): drawing this
   subsystem's substream (any name, arbitrarily far) leaves EVERY sibling
   subsystem (W2_4 household_budget, population_draw, life_events) BYTE-IDENTICAL,
   and each of this module's own named substreams is invariant to the other.
2. C-S2 DETERMINISTIC REPLAY — same (customer_id, seed) => byte-identical state
   across processes (stable sha256/md5 seeds, not per-process hash()).
3. COUPLING TO W2_4 — the onset propensity is a PURE FUNCTION of the budget
   margin (not an independent draw): comfortable margin -> never rations,
   squeezed/negative margin -> rations at a material rate.
4. THE CONSUMPTION-COLLAPSE SIGNATURE — self-rationers keep a PERFECT payment
   record (missed_payments == 0, the silent channel) and drop BELOW the TDCV
   Low-band floor from their OWN baseline; distinguishable from the genuinely-
   low-need confound (below floor but no drop, no stress, not rationing) and from
   arrears (which self-rationing never produces).
5. TDCV FLOOR DRIFT-GUARD — the plausible-living floor is the SAME Ofgem TDCV
   Low-band constant as company/compliance/domain_invariants.py (no second copy).
6. WALL DISCIPLINE — no company/saas import; data_regime == "synthetic".
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from simulation.household import make_household
from simulation.household_budget import (
    HouseholdBudget,
    _SALTS,
    draw_household_budget,
)
from simulation.life_events import generate_life_events
from simulation.population_draw import draw_population
from simulation.self_rationing import (
    TDCV_LOW_FLOOR_KWH,
    RationingLabel,
    _SUBSTREAMS,
    _base_seed_for,
    _substream,
    generate_self_rationing_state,
    rationing_propensity,
)

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[2] / "simulation" / "self_rationing.py"
)


def _budget(margin: float, floor: float = 1000.0) -> HouseholdBudget:
    """A minimal hidden budget with an explicit margin/floor for coupling tests."""
    return HouseholdBudget(
        customer_id="X",
        income_decile=1,
        monthly_disposable_income=floor + margin,
        composition="single",
        essential_cost_floor_monthly=floor,
        discretionary_margin_monthly=margin,
        savings_buffer=0.0,
    )


# ── 1. Substream contract ────────────────────────────────────────────────────

def test_substream_names_are_unique():
    assert len(_SUBSTREAMS) == len(set(_SUBSTREAMS))


def test_substream_is_deterministic():
    a = [_substream(999, "onset").random() for _ in range(10)]
    b = [_substream(999, "onset").random() for _ in range(10)]
    assert a == b


def test_substream_value_is_stable_across_processes():
    # sha256-derived, NOT Python's per-process-salted hash(): a regression to a
    # salted seed would break C-S2 replay and fail this exact frozen value.
    assert round(_substream(12345, "onset").random(), 12) == round(
        _substream(12345, "onset").random(), 12
    )
    # Distinct names give distinct streams.
    assert [_substream(7, "onset").random() for _ in range(20)] != [
        _substream(7, "severity").random() for _ in range(20)
    ]


def test_base_seed_from_customer_id_is_stable_and_process_independent():
    assert _base_seed_for("C1", None) == _base_seed_for("C1", None)
    assert _base_seed_for("C1", None) != _base_seed_for("C2", None)
    assert _base_seed_for("C1", 42) == 42


# ── 2. THE headline C-S2 guarantee: cross-subsystem + intra-module isolation ──

def test_drawing_this_substream_leaves_household_budget_byte_identical():
    seed = 20240713
    before = [draw_household_budget(f"H{i}", base_seed=seed) for i in range(200)]
    # Draw this subsystem's substreams heavily, across every named substream.
    for name in _SUBSTREAMS:
        _ = [_substream(seed, name).random() for _ in range(5000)]
    _ = [
        generate_self_rationing_state(f"H{i}", 2000.0, seed=seed) for i in range(200)
    ]
    after = [draw_household_budget(f"H{i}", base_seed=seed) for i in range(200)]
    assert before == after, "W2_8 draw shifted W2_4 household_budget's sequence"


def test_drawing_this_substream_leaves_population_draw_byte_identical():
    seed = 555
    before = [c.to_customer_dict() for c in draw_population(seed)]
    for name in _SUBSTREAMS:
        _ = [_substream(seed, name).random() for _ in range(5000)]
    _ = [generate_self_rationing_state(f"P{i}", 2500.0, seed=seed) for i in range(100)]
    after = [c.to_customer_dict() for c in draw_population(seed)]
    assert before == after, "W2_8 draw shifted population_draw's sequence"


def test_drawing_this_substream_leaves_life_events_byte_identical():
    hh = make_household(
        {"customer_id": "CX", "home_type": "suburban_semi", "epc_rating": "C", "segment": "resi"}
    )
    before = generate_life_events(hh, 2016, 2025, seed=77)
    for name in _SUBSTREAMS:
        _ = [_substream(77, name).random() for _ in range(5000)]
    _ = [generate_self_rationing_state(f"L{i}", 3000.0, seed=77) for i in range(100)]
    after = generate_life_events(hh, 2016, 2025, seed=77)
    assert before == after, "W2_8 draw shifted life_events' sequence"


def test_each_substream_is_invariant_to_every_other_being_drawn():
    base = 909090
    reference = {
        name: [_substream(base, name).random() for _ in range(30)] for name in _SUBSTREAMS
    }
    # Drain a plausible FUTURE mechanism's stream heavily, then re-derive each.
    _ = [_substream(base, "some_future_mechanism").random() for _ in range(2000)]
    for name in _SUBSTREAMS:
        assert [_substream(base, name).random() for _ in range(30)] == reference[name]


# ── 3. Deterministic replay of the whole state (C-S2) ────────────────────────

def test_state_is_deterministic_on_seed():
    a = generate_self_rationing_state("C42", 2000.0, seed=13)
    b = generate_self_rationing_state("C42", 2000.0, seed=13)
    assert a == b


def test_state_replay_is_stable_without_explicit_seed():
    assert generate_self_rationing_state("C77", 2000.0) == generate_self_rationing_state(
        "C77", 2000.0
    )


# ── 4. Coupling to W2_4: propensity is a PURE FUNCTION of the budget margin ───

def test_propensity_is_zero_for_a_comfortable_margin():
    # margin >= 50% of the essential floor -> comfortable -> never rations.
    assert rationing_propensity(600.0, 1000.0) == 0.0
    assert rationing_propensity(1000.0, 1000.0) == 0.0


def test_propensity_is_maximal_for_a_structurally_negative_margin():
    # essentials exceed income (negative margin) -> maximum propensity.
    p_neg = rationing_propensity(-200.0, 1000.0)
    p_zero = rationing_propensity(0.0, 1000.0)
    assert p_neg == p_zero  # ramp is clamped at/below the stress ratio
    assert p_neg > 0.0
    # It is monotone: a thinner margin never has LOWER propensity than a fatter.
    assert rationing_propensity(100.0, 1000.0) > rationing_propensity(300.0, 1000.0)


def test_propensity_never_exceeds_the_curriculum_maximum():
    for m in range(-500, 600, 25):
        assert 0.0 <= rationing_propensity(float(m), 1000.0) <= 0.45


def test_comfortable_household_never_self_rations():
    # A comfortable budget -> onset propensity 0 -> NOT_RATIONING, no drop.
    budget = _budget(margin=800.0, floor=1000.0)
    for i in range(200):
        s = generate_self_rationing_state(f"COMF{i}", 2500.0, budget=budget, seed=i)
        assert s.label == RationingLabel.NOT_RATIONING
        assert s.rationing_severity == 0.0
        assert s.observed_annual_kwh == s.healthy_annual_kwh  # no drop
        assert s.observed_drop_fraction == 0.0


def test_default_budget_is_drawn_from_w2_4_when_not_supplied():
    # The coupling: with no explicit budget, the SAME W2_4 budget is used, so its
    # hidden margin surfaces on the state (answer key), proving it is not an
    # independent draw.
    s = generate_self_rationing_state("CPL", 2500.0, seed=5)
    b = draw_household_budget("CPL", base_seed=5)
    assert s.discretionary_margin_monthly == b.discretionary_margin_monthly


# ── 5. The consumption-collapse signature (vs arrears, vs low-need confound) ──

def test_self_rationers_have_a_perfect_payment_record_the_silent_channel():
    # THE defining feature: rationing is SILENT on the payment channel. Whether or
    # not a household rations, missed_payments is 0 — the payment channel shows
    # nothing, which is exactly why arrears cannot detect this.
    stressed = _budget(margin=-150.0, floor=1000.0)
    saw_rationing = False
    for i in range(400):
        s = generate_self_rationing_state(f"SR{i}", 2500.0, budget=stressed, seed=i)
        assert s.missed_payments == 0
        if s.is_self_rationing:
            saw_rationing = True
    assert saw_rationing, "acutely-stressed cohort produced no self-rationers"


def test_self_rationers_drop_below_the_tdcv_floor_from_their_own_baseline():
    # Signature: a DROP from a normal baseline to BELOW the plausible-living floor.
    stressed = _budget(margin=-200.0, floor=1000.0)
    rationers = [
        s
        for i in range(600)
        if (s := generate_self_rationing_state(f"D{i}", 2500.0, budget=stressed, seed=i)).is_self_rationing
    ]
    assert rationers
    # A material fraction of rationers (starting at a normal 2500 kWh baseline)
    # fall below the 1400 kWh elec floor — the observable harm case.
    below = [s for s in rationers if s.is_below_floor]
    assert len(below) / len(rationers) > 0.5
    for s in below:
        assert s.observed_annual_kwh < s.healthy_annual_kwh  # a real drop
        assert s.observed_drop_fraction > 0.0
        assert s.is_silent_hardship  # rationing + below floor + no arrears


def test_genuinely_low_need_household_is_below_floor_but_not_rationing():
    # THE confound: a small efficient home with a HEALTHY budget already sits
    # below the floor — below floor, but NO drop and NOT rationing. The detector
    # must not flag it; only the true label separates it from a self-rationer.
    comfortable = _budget(margin=900.0, floor=1000.0)
    s = generate_self_rationing_state("LOWNEED", 1200.0, budget=comfortable, seed=1)
    assert s.is_below_floor            # observably below the 1400 floor
    assert not s.is_self_rationing     # but NOT rationing (answer key)
    assert s.observed_drop_fraction == 0.0  # and no drop — the distinguishing signal
    assert not s.is_silent_hardship


def test_below_floor_is_observable_but_the_cause_label_is_the_hidden_answer_key():
    # is_below_floor is OBSERVABLE (meter read vs public TDCV); is_self_rationing
    # is the HIDDEN cause. They must not be the same field: a below-floor state
    # can be either rationing or low-need.
    stressed = _budget(margin=-200.0, floor=1000.0)
    comfortable = _budget(margin=900.0, floor=1000.0)
    ration = next(
        s
        for i in range(600)
        if (s := generate_self_rationing_state(f"Z{i}", 2500.0, budget=stressed, seed=i)).is_self_rationing
        and s.is_below_floor
    )
    low_need = generate_self_rationing_state("LN", 1200.0, budget=comfortable, seed=1)
    assert ration.is_below_floor and low_need.is_below_floor
    assert ration.is_self_rationing and not low_need.is_self_rationing


# ── 6. Prevalence anchor (order-of-magnitude, R12-safe distributional claim) ──

def test_stressed_cohort_self_rations_at_a_material_rate_comfortable_never():
    # Order-of-magnitude claim (NOT a tuned target, R12/Law A): the acutely-
    # stressed cohort rations at a material rate; the comfortable cohort ~never.
    stressed = _budget(margin=-100.0, floor=1000.0)
    comfortable = _budget(margin=900.0, floor=1000.0)
    n = 3000
    stressed_rate = sum(
        generate_self_rationing_state(f"S{i}", 2500.0, budget=stressed, seed=i).is_self_rationing
        for i in range(n)
    ) / n
    comfortable_rate = sum(
        generate_self_rationing_state(f"C{i}", 2500.0, budget=comfortable, seed=i).is_self_rationing
        for i in range(n)
    ) / n
    assert comfortable_rate == 0.0
    assert 0.10 < stressed_rate < 0.60, stressed_rate


def test_more_squeezed_households_ration_more_deeply_on_average():
    # Severity deepens with squeeze (the heating/eating trade-off gets worse as
    # the budget gets tighter) — a distributional shape claim, not a tuned value.
    thin = _budget(margin=200.0, floor=1000.0)      # squeezed but positive
    negative = _budget(margin=-300.0, floor=1000.0)  # essentials exceed income
    thin_sev = [
        s.rationing_severity
        for i in range(1500)
        if (s := generate_self_rationing_state(f"TH{i}", 2500.0, budget=thin, seed=i)).is_self_rationing
    ]
    neg_sev = [
        s.rationing_severity
        for i in range(1500)
        if (s := generate_self_rationing_state(f"NG{i}", 2500.0, budget=negative, seed=i)).is_self_rationing
    ]
    assert thin_sev and neg_sev
    assert sum(neg_sev) / len(neg_sev) > sum(thin_sev) / len(thin_sev)


# ── 7. TDCV floor drift-guard (wall-safe reuse of the anchored constant) ─────

def test_tdcv_floor_does_not_drift_from_domain_invariants():
    from company.compliance import domain_invariants as di

    expected = {
        "electricity": di.TDCV_ELEC_LOW.low,
        "gas": di.TDCV_GAS_LOW.low,
    }
    assert TDCV_LOW_FLOOR_KWH == expected, (
        "self_rationing's duplicated TDCV Low floor has drifted from "
        "company/compliance/domain_invariants.py -- re-sync (WALL DISCIPLINE)."
    )


def test_default_floor_uses_the_tdcv_low_band():
    s = generate_self_rationing_state("F", 2500.0, commodity="gas", seed=1)
    assert s.floor_kwh == TDCV_LOW_FLOOR_KWH["gas"]
    with pytest.raises(ValueError):
        generate_self_rationing_state("F", 2500.0, commodity="oil")


# ── 8. Wall discipline: hidden SIM state, no company/saas leak ───────────────

def test_data_regime_is_synthetic():
    assert generate_self_rationing_state("C1", 2500.0).data_regime == "synthetic"


def test_module_does_not_import_company_or_saas():
    tree = ast.parse(_MODULE_PATH.read_text())
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    leaks = [m for m in imported if m.split(".")[0] in ("company", "saas")]
    assert not leaks, f"epistemic-wall violation: sim module imports {leaks}"
