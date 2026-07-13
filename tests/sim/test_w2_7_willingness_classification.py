"""W2_7_willingness_classification -- hidden ABILITY x WILLINGNESS 2x2 answer key.

These tests lock the five things this WORLD-side atom must guarantee:

1. C-S2 SUBSTREAM ISOLATION -- the headline requirement (the 01:09Z incident):
   drawing this subsystem's willingness substream arbitrarily far leaves EVERY
   sibling subsystem (population_draw, life_events, household_budget, sme_distress)
   BYTE-IDENTICAL, and the willingness substream is invariant to any other being
   drawn.
2. C-S2 DETERMINISTIC REPLAY -- same (customer_id, seed) => byte-identical profile
   across processes (stable sha256/md5 seeds, not per-process hash()).
3. ABILITY COUPLES TO W2_4 -- genuine cannot-pay is derived ARITHMETICALLY from
   the coupled household budget's discretionary margin, byte-consistent with a
   standalone draw_household_budget for that customer; it is NOT an independent
   random ability draw.
4. WILLINGNESS is an INDEPENDENT MINORITY behavioural trait -- a director-set
   curriculum incidence (R13), deliberately a minority, matching the arithmetic of
   its own parameter; and the 2x2 / observable are correctly wired.
5. WALL DISCIPLINE -- no company/saas import; data_regime == "synthetic".
"""

import ast
import pathlib

import pytest

from simulation.household import make_household
from simulation.household_budget import HouseholdBudget, draw_household_budget
from simulation.life_events import generate_life_events
from simulation.population_draw import draw_population
from simulation.sme_distress import generate_business_distress
from simulation.willingness_classification import (
    _SUBSTREAMS,
    _WONT_PAY_INCIDENCE,
    Ability,
    Quadrant,
    Willingness,
    _base_seed_for,
    _substream,
    ability_from_budget,
    draw_willingness_profile,
    quadrant_of,
)

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "simulation"
    / "willingness_classification.py"
)


# ── 1. Substream contract ────────────────────────────────────────────────────

def test_substream_names_are_unique():
    assert len(_SUBSTREAMS) == len(set(_SUBSTREAMS))


def test_substream_is_deterministic():
    a = [_substream(999, "willingness").random() for _ in range(10)]
    b = [_substream(999, "willingness").random() for _ in range(10)]
    assert a == b


def test_substream_value_is_stable_across_processes():
    # sha256-derived, NOT Python's per-process-salted hash(): a regression to a
    # salted seed would break C-S2 replay and fail this exact frozen value.
    assert round(_substream(12345, "willingness").random(), 12) == 0.066306377532


def test_base_seed_from_customer_id_is_stable():
    # md5-derived => process-independent (regression guard vs builtin hash()).
    assert _base_seed_for("C1", None) == _base_seed_for("C1", None)
    assert _base_seed_for("C1", None) != _base_seed_for("C2", None)


def test_base_seed_passthrough_when_explicit():
    assert _base_seed_for("C1", 42) == 42


# ── 2. THE headline C-S2 guarantee: advancing willingness shifts NO sibling ──
# Named in the brief: advancing this substream must leave population_draw,
# life_events, household_budget AND sme_distress byte-identical.

def _drain_willingness(seed: int, n: int = 8000) -> None:
    _ = [_substream(seed, "willingness").random() for _ in range(n)]
    _ = [draw_willingness_profile(f"W{i}", base_seed=seed) for i in range(200)]


def test_drawing_this_substream_leaves_population_draw_byte_identical():
    seed = 20240713
    before = [c.to_customer_dict() for c in draw_population(seed)]
    _drain_willingness(seed)
    after = [c.to_customer_dict() for c in draw_population(seed)]
    assert before == after, "W2_7 draw shifted population_draw's sequence"


def test_drawing_this_substream_leaves_life_events_byte_identical():
    hh = make_household(
        {"customer_id": "CX", "home_type": "suburban_semi", "epc_rating": "C", "segment": "resi"}
    )
    before = generate_life_events(hh, 2016, 2025, seed=77)
    _drain_willingness(77)
    after = generate_life_events(hh, 2016, 2025, seed=77)
    assert before == after, "W2_7 draw shifted life_events' sequence"


def test_drawing_this_substream_leaves_household_budget_byte_identical():
    seed = 5150
    before = [draw_household_budget(f"H{i}", base_seed=seed) for i in range(300)]
    _drain_willingness(seed)
    after = [draw_household_budget(f"H{i}", base_seed=seed) for i in range(300)]
    assert before == after, "W2_7 draw shifted household_budget's sequence"


def test_drawing_this_substream_leaves_sme_distress_byte_identical():
    before = generate_business_distress("BIZ01", "SME", 2016, 2025, seed=909)
    _drain_willingness(909)
    after = generate_business_distress("BIZ01", "SME", 2016, 2025, seed=909)
    assert before == after, "W2_7 draw shifted sme_distress's sequence"


def test_willingness_substream_is_invariant_to_a_future_attribute_being_drawn():
    base = 424242
    before = [_substream(base, "willingness").random() for _ in range(50)]
    _ = [_substream(base, "some_future_attribute").random() for _ in range(2000)]
    after = [_substream(base, "willingness").random() for _ in range(50)]
    assert before == after, "a new named substream shifted the willingness stream"


# ── 3. Deterministic replay of the whole profile (C-S2) ──────────────────────

def test_profile_is_deterministic_on_seed():
    a = draw_willingness_profile("C42", base_seed=13)
    b = draw_willingness_profile("C42", base_seed=13)
    assert a == b


def test_profile_replay_is_stable_without_explicit_seed():
    assert draw_willingness_profile("C77") == draw_willingness_profile("C77")


# ── 4. ABILITY couples to W2_4 -- arithmetic, consistent, not an extra draw ───

def test_ability_matches_coupled_household_budget_byte_for_byte():
    # The budget used inside the profile is byte-consistent with a standalone
    # W2_4 draw for the same customer, and ability is the pure arithmetic of it.
    for i in range(400):
        cid = f"CPL{i}"
        prof = draw_willingness_profile(cid)
        budget = draw_household_budget(cid)
        assert prof.discretionary_margin_monthly == budget.discretionary_margin_monthly
        expected = (
            Ability.CANNOT_PAY if budget.discretionary_margin_monthly <= 0.0 else Ability.CAN_PAY
        )
        assert prof.ability == expected


def test_cannot_pay_is_exactly_structurally_negative_at_default_threshold():
    # Genuine cannot-pay derives from the hidden budget going negative, not a draw.
    for i in range(500):
        cid = f"NEG{i}"
        prof = draw_willingness_profile(cid)
        assert prof.is_genuine_cantpay == (prof.discretionary_margin_monthly <= 0.0)


def test_ability_from_budget_threshold_is_honoured():
    # A thin but positive margin is CAN_PAY at threshold 0.0, CANNOT_PAY once the
    # near-zero buffer is raised above it (the overridable R10 refinement).
    thin = HouseholdBudget(
        customer_id="T", income_decile=2, monthly_disposable_income=1500.0,
        composition="single", essential_cost_floor_monthly=1450.0,
        discretionary_margin_monthly=50.0, savings_buffer=0.0,
    )
    assert ability_from_budget(thin, 0.0) == Ability.CAN_PAY
    assert ability_from_budget(thin, 100.0) == Ability.CANNOT_PAY


def test_ability_is_not_an_independent_draw_of_willingness():
    # Changing the willingness incidence must NEVER change any ability outcome:
    # the two axes are orthogonal, ability off the budget, willingness off its
    # own substream.
    for i in range(300):
        cid = f"ORTH{i}"
        a = draw_willingness_profile(cid, wont_pay_incidence=0.0).ability
        b = draw_willingness_profile(cid, wont_pay_incidence=1.0).ability
        assert a == b


# ── 5. WILLINGNESS is an independent MINORITY behavioural trait (R13) ─────────

def test_wont_pay_incidence_is_a_deliberate_minority():
    # The director-set curriculum placeholder is a minority (can't-pay-dominant
    # framing), NOT a naive 50/50 or an inflated won't-pay rate.
    assert 0.0 < _WONT_PAY_INCIDENCE < 0.25


def test_realised_wont_pay_rate_matches_the_parameter():
    pop = [draw_willingness_profile(f"WP{i}") for i in range(6000)]
    frac = sum(p.willingness == Willingness.WONT_PAY for p in pop) / len(pop)
    # Order-of-magnitude distributional check (R12-safe), not a tuned equality.
    assert frac == pytest.approx(_WONT_PAY_INCIDENCE, abs=0.03)


def test_willingness_rate_tracks_an_overridden_incidence():
    pop = [draw_willingness_profile(f"OV{i}", wont_pay_incidence=0.4) for i in range(6000)]
    frac = sum(p.willingness == Willingness.WONT_PAY for p in pop) / len(pop)
    assert frac == pytest.approx(0.4, abs=0.03)


def test_extreme_incidences_are_degenerate_as_expected():
    assert draw_willingness_profile("Z", wont_pay_incidence=0.0).willingness == Willingness.WILL_PAY
    assert draw_willingness_profile("Z", wont_pay_incidence=1.0).willingness == Willingness.WONT_PAY


# ── 6. The 2x2 quadrant + single sanctioned observable are correctly wired ───

def test_quadrant_map_is_total_and_correct():
    assert quadrant_of(Ability.CAN_PAY, Willingness.WILL_PAY) == Quadrant.CAN_WILL
    assert quadrant_of(Ability.CAN_PAY, Willingness.WONT_PAY) == Quadrant.CAN_WONT
    assert quadrant_of(Ability.CANNOT_PAY, Willingness.WILL_PAY) == Quadrant.CANNOT_WILL
    assert quadrant_of(Ability.CANNOT_PAY, Willingness.WONT_PAY) == Quadrant.CANNOT_WONT


def test_all_four_quadrants_are_reachable_in_the_population():
    quads = {draw_willingness_profile(f"Q{i}").quadrant for i in range(8000)}
    assert quads == set(Quadrant), quads


def test_only_can_and_will_pays_the_other_three_cells_are_in_arrears():
    # THE confound: the single observable (is_in_arrears) is identical across the
    # three non-paying cells and differs only for CAN_WILL.
    for a in Ability:
        for w in Willingness:
            prof = _forced_profile(a, w)
            in_arrears = not (a == Ability.CAN_PAY and w == Willingness.WILL_PAY)
            assert prof.is_in_arrears() == in_arrears


def test_strategic_nonpayer_is_exactly_can_wont():
    assert _forced_profile(Ability.CAN_PAY, Willingness.WONT_PAY).is_strategic_nonpayer
    for a, w in [
        (Ability.CAN_PAY, Willingness.WILL_PAY),
        (Ability.CANNOT_PAY, Willingness.WILL_PAY),
        (Ability.CANNOT_PAY, Willingness.WONT_PAY),
    ]:
        assert not _forced_profile(a, w).is_strategic_nonpayer


def test_among_low_income_households_arrears_are_cantpay_dominated():
    # The can't-pay-crisis framing emerges from selection: within the low-income
    # (bottom-decile) cohort, genuine can't-pay dominates the arrears cells --
    # a property of WHERE arrears come from, not of the willingness parameter.
    profs = [draw_willingness_profile(f"LO{i}") for i in range(8000)]
    low = [p for p in profs if p.discretionary_margin_monthly <= 200.0 and p.is_in_arrears()]
    assert low
    cantpay = sum(p.is_genuine_cantpay for p in low) / len(low)
    assert cantpay > 0.6, cantpay


# ── 7. Wall discipline: hidden SIM state, no company/saas leak ────────────────

def test_data_regime_is_synthetic():
    assert draw_willingness_profile("C1").data_regime == "synthetic"


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


# ── helpers ──────────────────────────────────────────────────────────────────

def _forced_profile(ability: Ability, willingness: Willingness):
    from simulation.willingness_classification import WillingnessProfile
    margin = -100.0 if ability == Ability.CANNOT_PAY else 500.0
    return WillingnessProfile(
        customer_id="F", ability=ability, willingness=willingness,
        discretionary_margin_monthly=margin,
    )
