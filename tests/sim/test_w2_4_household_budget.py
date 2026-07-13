"""W2_4_household_budget — hidden budget state: RNG isolation, replay, L3 shape.

This atom is HIDDEN SIM ground truth. These tests lock four things:

1. C-S2 SUBSTREAM ISOLATION — the headline requirement (the 01:09Z incident):
   drawing this subsystem's substream (any salt, arbitrarily far) leaves EVERY
   sibling subsystem (population_draw, life_events) BYTE-IDENTICAL, and each of
   this module's own named salts is invariant to every other being drawn.
2. C-S2 DETERMINISTIC REPLAY — same (customer_id, seed) => byte-identical budget
   across processes (stable sha256/md5 seeds, not per-process hash()).
3. THE L3 SHAPE CLAIMS from docs/design/CHARTER_W2_AFFORDABILITY.md §W2_4(b) —
   negative-margin bottom decile as an ARITHMETIC consequence (not a coded
   probability), FCA-anchored savings shape, priority-before-non-priority debt
   servicing. These are R12-safe distributional assertions, NOT tuned targets.
4. WALL DISCIPLINE — no company/saas import; data_regime == "synthetic".
"""

import ast
import collections
import pathlib

import pytest

from simulation.household import make_household
from simulation.household_budget import (
    DEFAULT_DEBT_PRIORITY_ORDER,
    MONTHLY_DISPOSABLE_INCOME_BY_DECILE,
    NON_PRIORITY_DEBTS,
    PRIORITY_DEBTS,
    _SALTS,
    _base_seed_for,
    _substream,
    allocate_debt_payments,
    draw_household_budget,
)
from simulation.life_events import generate_life_events
from simulation.population_draw import draw_population

_MODULE_PATH = pathlib.Path(__file__).resolve().parents[2] / "simulation" / "household_budget.py"


# ── 1. Substream contract ────────────────────────────────────────────────────

def test_salts_are_unique():
    assert len(_SALTS) == len(set(_SALTS))


def test_substream_is_deterministic():
    a = [_substream(999, "income").random() for _ in range(10)]
    b = [_substream(999, "income").random() for _ in range(10)]
    assert a == b


def test_substream_value_is_stable_across_processes():
    # sha256-derived, NOT Python's per-process-salted hash(): a regression to a
    # salted seed would break C-S2 replay and fail this exact frozen value.
    assert round(_substream(12345, "income").random(), 12) == 0.343784623476


def test_distinct_salts_produce_different_sequences():
    inc = [_substream(555, "income").random() for _ in range(20)]
    sav = [_substream(555, "savings").random() for _ in range(20)]
    assert inc != sav


def test_base_seed_from_customer_id_is_stable():
    # md5-derived => process-independent (regression guard vs builtin hash()).
    assert _base_seed_for("C1", None) == _base_seed_for("C1", None)
    assert _base_seed_for("C1", None) != _base_seed_for("C2", None)


def test_base_seed_passthrough_when_explicit():
    assert _base_seed_for("C1", 42) == 42


# ── 2. THE headline C-S2 guarantee: cross-subsystem + intra-module isolation ──

def test_drawing_this_substream_leaves_population_draw_byte_identical():
    seed = 20240713
    before = [c.to_customer_dict() for c in draw_population(seed)]
    # Draw this subsystem's substreams heavily, across every named salt.
    for salt in _SALTS:
        _ = [_substream(seed, salt).random() for _ in range(5000)]
    _ = [draw_household_budget(f"C{i}", base_seed=seed) for i in range(200)]
    after = [c.to_customer_dict() for c in draw_population(seed)]
    assert before == after, "W2_4 draw shifted population_draw's sequence"


def test_drawing_this_substream_leaves_life_events_byte_identical():
    hh = make_household(
        {"customer_id": "CX", "home_type": "suburban_semi", "epc_rating": "C", "segment": "resi"}
    )
    before = generate_life_events(hh, 2016, 2025, seed=77)
    for salt in _SALTS:
        _ = [_substream(77, salt).random() for _ in range(5000)]
    _ = [draw_household_budget(f"H{i}", base_seed=77) for i in range(200)]
    after = generate_life_events(hh, 2016, 2025, seed=77)
    assert before == after, "W2_4 draw shifted life_events' sequence"


def test_each_salt_is_invariant_to_every_other_being_drawn():
    base = 909090
    reference = {
        salt: [_substream(base, salt).random() for _ in range(30)] for salt in _SALTS
    }
    # Drain a plausible FUTURE attribute's stream heavily, then re-derive each.
    _ = [_substream(base, "some_future_attribute").random() for _ in range(2000)]
    for salt in _SALTS:
        assert [_substream(base, salt).random() for _ in range(30)] == reference[salt]


# ── 3. Deterministic replay of the whole draw (C-S2) ─────────────────────────

def test_draw_is_deterministic_on_seed():
    a = draw_household_budget("C42", base_seed=13)
    b = draw_household_budget("C42", base_seed=13)
    assert a == b


def test_draw_replay_is_stable_without_explicit_seed():
    assert draw_household_budget("C77") == draw_household_budget("C77")


def test_different_customers_get_different_budgets():
    budgets = {draw_household_budget(f"C{i}") for i in range(50)}
    # A degenerate generator would collapse; require real variation.
    assert len({b.monthly_disposable_income for b in budgets}) > 20


# ── 4. L3 shape claim #1: bottom decile CAN be negative, top decile rarely ───
# Charter §W2_4(b).1: negative margin must be the ARITHMETIC consequence of
# income minus the floor, not a coded probability. We assert the SHAPE is
# capable of it at a materially higher rate in the bottom band than the top —
# NOT a tuned magnitude (R12/Law A safe).

def test_bottom_decile_has_material_negative_margin_incidence():
    pop = [draw_household_budget(f"HH{i}") for i in range(4000)]
    bottom = [b for b in pop if b.income_decile <= 2]
    top = [b for b in pop if b.income_decile >= 9]
    assert bottom and top
    frac_bottom_neg = sum(b.is_structurally_negative for b in bottom) / len(bottom)
    frac_top_neg = sum(b.is_structurally_negative for b in top) / len(top)
    # Bottom band must be able to go negative pre-shock; top band essentially never.
    assert frac_bottom_neg > 0.15, frac_bottom_neg
    assert frac_bottom_neg > frac_top_neg
    assert frac_top_neg < 0.02, frac_top_neg


def test_negative_margin_is_pure_arithmetic_of_income_minus_floor():
    # No hidden probability: margin is exactly income - floor, always.
    for i in range(500):
        b = draw_household_budget(f"A{i}")
        assert b.discretionary_margin_monthly == round(
            b.monthly_disposable_income - b.essential_cost_floor_monthly, 2
        )
        assert b.is_structurally_negative == (b.discretionary_margin_monthly < 0.0)


def test_median_income_anchor_holds():
    # The cited anchor: ~£3,225/mo median disposable income at the D5/D6 boundary.
    d5, d6 = MONTHLY_DISPOSABLE_INCOME_BY_DECILE[5], MONTHLY_DISPOSABLE_INCOME_BY_DECILE[6]
    assert (d5 + d6) / 2 == pytest.approx(3225, abs=50)


# ── 5. L3 shape claim #3: FCA-anchored savings buffer distribution ───────────

def test_savings_buffer_reproduces_fca_shape():
    pop = [draw_household_budget(f"S{i}") for i in range(5000)]
    frac_zero = sum(b.savings_buffer == 0.0 for b in pop) / len(pop)
    frac_under_1k = sum(b.savings_buffer < 1000.0 for b in pop) / len(pop)
    # FCA population-wide: ~1 in 10 zero, ~a third under £1k (zero incl.). These are
    # order-of-magnitude distributional assertions, not tuned equalities.
    assert 0.04 < frac_zero < 0.20, frac_zero
    assert 0.20 < frac_under_1k < 0.45, frac_under_1k


def test_low_income_band_has_thinner_savings_than_high_band():
    pop = [draw_household_budget(f"T{i}") for i in range(5000)]
    low = [b for b in pop if b.annual_disposable_income < 15000]
    high = [b for b in pop if b.annual_disposable_income >= 50000]
    assert low and high
    low_zero = sum(b.savings_buffer == 0.0 for b in low) / len(low)
    high_zero = sum(b.savings_buffer == 0.0 for b in high) / len(high)
    # FCA: low band far more likely to have zero savings than high band.
    assert low_zero > high_zero
    assert low_zero > 0.12, low_zero


# ── 6. L3 shape claim #4: priority-before-non-priority debt servicing ────────

def test_priority_debts_serviced_before_any_non_priority():
    # Household with a binding budget below total debts due.
    debts = {
        "rent_mortgage_arrears": 500.0,
        "energy_arrears": 300.0,
        "council_tax_arrears": 200.0,
        "credit_card": 400.0,
        "personal_loan": 350.0,
    }
    total_priority = 500 + 300 + 200
    # Give exactly enough to cover all priority debts and nothing more.
    paid = allocate_debt_payments(total_priority, debts)
    assert paid["rent_mortgage_arrears"] == 500.0
    assert paid["energy_arrears"] == 300.0
    assert paid["council_tax_arrears"] == 200.0
    # Non-priority debts got NOTHING.
    assert paid["credit_card"] == 0.0
    assert paid["personal_loan"] == 0.0


def test_partial_budget_never_starts_non_priority_before_priority_fully_paid():
    debts = {"energy_arrears": 300.0, "credit_card": 300.0}
    # Only enough for half the priority debt.
    paid = allocate_debt_payments(150.0, debts)
    assert paid["energy_arrears"] == 150.0
    assert paid["credit_card"] == 0.0


def test_surplus_budget_reaches_non_priority_debts():
    debts = {"energy_arrears": 100.0, "credit_card": 100.0}
    paid = allocate_debt_payments(1000.0, debts)
    assert paid["energy_arrears"] == 100.0
    assert paid["credit_card"] == 100.0


def test_energy_is_a_priority_debt_not_below_rent_and_council_tax():
    # The charter's correction to the atom's original text: energy sits INSIDE
    # the priority tier (disconnection risk), not beneath rent/council-tax/food.
    assert "energy_arrears" in PRIORITY_DEBTS
    assert "energy_arrears" not in NON_PRIORITY_DEBTS
    # And "food" is NOT a debt-stack entry at all (essential spend, no creditor).
    assert not any("food" in d for d in DEFAULT_DEBT_PRIORITY_ORDER)


def test_all_priority_debts_precede_all_non_priority_in_default_order():
    order = DEFAULT_DEBT_PRIORITY_ORDER
    last_priority = max(order.index(d) for d in PRIORITY_DEBTS)
    first_non_priority = min(order.index(d) for d in NON_PRIORITY_DEBTS)
    assert last_priority < first_non_priority


# ── 7. Wall discipline: hidden SIM state, no company/saas leak ───────────────

def test_data_regime_is_synthetic():
    assert draw_household_budget("C1").data_regime == "synthetic"


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
