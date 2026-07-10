"""Tests for saas/opex_ledger.py -- MARGIN_REALISM Step 3 opex mechanism (Maturity Map B2)."""
import pytest

from saas.opex_ledger import (
    DCC_COMMS_CHARGE_GBP_PER_YEAR,
    OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL,
    ai_compute_and_oversight_cost_gbp_per_year,
    build_opex_ledger,
    true_opex_cost_gbp_per_year,
    true_third_party_cost_gbp_per_year,
)


def _cust(customer_id, commodity="electricity", smart_meter=True):
    return {"customer_id": customer_id, "segment": "resi", "commodity": commodity, "smart_meter": smart_meter}


# -- Part (a): true third-party cost --

def test_true_third_party_cost_zero_when_not_smart_metered():
    assert true_third_party_cost_gbp_per_year(_cust("C1", smart_meter=False)) == 0.0


def test_true_third_party_cost_zero_when_smart_meter_unknown():
    c = _cust("C1")
    c["smart_meter"] = None
    assert true_third_party_cost_gbp_per_year(c) == 0.0


def test_true_third_party_cost_electricity_smart_meter():
    result = true_third_party_cost_gbp_per_year(_cust("C1", commodity="electricity", smart_meter=True))
    assert result == pytest.approx(DCC_COMMS_CHARGE_GBP_PER_YEAR["electricity"])
    assert result == pytest.approx(19.01)


def test_true_third_party_cost_gas_smart_meter():
    result = true_third_party_cost_gbp_per_year(_cust("C1g", commodity="gas", smart_meter=True))
    assert result == pytest.approx(DCC_COMMS_CHARGE_GBP_PER_YEAR["gas"])
    assert result == pytest.approx(14.32)


def test_true_third_party_cost_unknown_commodity_is_zero():
    result = true_third_party_cost_gbp_per_year(_cust("C1", commodity="hydrogen", smart_meter=True))
    assert result == 0.0


# -- Part (b): AI-compute + oversight, explicitly not yet populated --

def test_ai_compute_cost_always_zero_pending_open_design_questions():
    """Real, unresolved: token-usage-log representativeness + costing-basis choice +
    director's own oversight rate -- must never be silently defaulted to a fabricated
    number (R12)."""
    assert ai_compute_and_oversight_cost_gbp_per_year(_cust("C1")) == 0.0
    assert ai_compute_and_oversight_cost_gbp_per_year({}) == 0.0


def test_true_opex_cost_is_just_third_party_cost_today():
    c = _cust("C1", commodity="electricity", smart_meter=True)
    assert true_opex_cost_gbp_per_year(c) == pytest.approx(true_third_party_cost_gbp_per_year(c))


# -- Part (c): dual ledger + household netting --

def test_build_opex_ledger_single_electricity_only_household():
    customers = [_cust("C1", "electricity", True)]
    ledger = build_opex_ledger(customers, {"C1": "direct_debit"})
    assert ledger["true_third_party_cost_gbp"] == pytest.approx(19.01)
    assert ledger["true_ai_compute_cost_gbp"] == 0.0
    assert ledger["true_opex_total_gbp"] == pytest.approx(19.01)
    # benchmark = Ofgem DD allowance (297.92) netted of this household's own £19.01
    assert ledger["benchmark_labour_cost_gbp"] == pytest.approx(297.92 - 19.01)
    assert ledger["household_count"] == 1
    assert ledger["unresolved_household_count"] == 0


def test_build_opex_ledger_dual_fuel_household_nets_both_legs_once():
    """C1 (elec) + C1g (gas) are the SAME household -- the Ofgem dual-fuel allowance
    must be counted once, netted of BOTH legs' DCC cost combined, not once per account."""
    customers = [_cust("C1", "electricity", True), _cust("C1g", "gas", True)]
    ledger = build_opex_ledger(customers, {"C1": "direct_debit"})
    total_dcc = 19.01 + 14.32
    assert ledger["true_third_party_cost_gbp"] == pytest.approx(total_dcc)
    assert ledger["household_count"] == 1  # one household, not two
    assert ledger["benchmark_labour_cost_gbp"] == pytest.approx(297.92 - total_dcc)


def test_build_opex_ledger_standard_credit_uses_higher_allowance():
    customers = [_cust("C2", "electricity", False)]
    ledger = build_opex_ledger(customers, {"C2": "standard_credit"})
    assert ledger["benchmark_labour_cost_gbp"] == pytest.approx(441.10)  # no DCC cost to net (not smart)


def test_build_opex_ledger_investor_thesis_gap_is_benchmark_minus_true():
    customers = [_cust("C1", "electricity", True)]
    ledger = build_opex_ledger(customers, {"C1": "direct_debit"})
    assert ledger["investor_thesis_gap_gbp"] == pytest.approx(
        ledger["benchmark_opex_total_gbp"] - ledger["true_opex_total_gbp"]
    )
    assert ledger["investor_thesis_gap_gbp"] > 0  # true cost is far below the benchmark proxy


def test_build_opex_ledger_unresolved_payment_channel_excluded_from_benchmark_only():
    customers = [_cust("C9", "electricity", True)]
    ledger = build_opex_ledger(customers, {"C9": "prepayment"})  # not in OFGEM_BUNDLED_ALLOWANCE
    assert ledger["true_third_party_cost_gbp"] == pytest.approx(19.01)  # true side unaffected
    assert ledger["benchmark_labour_cost_gbp"] == 0.0
    assert ledger["household_count"] == 0
    assert ledger["unresolved_household_count"] == 1


def test_build_opex_ledger_benchmark_never_goes_negative():
    """A household's own true third-party cost can never exceed the Ofgem allowance in
    practice at today's DCC rates, but the netting is clamped at 0.0 defensively rather
    than producing a negative 'benchmark' cost."""
    customers = [_cust("C1", "electricity", True)]
    ledger = build_opex_ledger(customers, {"C1": "direct_debit"})
    assert ledger["benchmark_labour_cost_gbp"] >= 0.0


def test_build_opex_ledger_empty_portfolio():
    ledger = build_opex_ledger([], {})
    assert ledger["true_opex_total_gbp"] == 0.0
    assert ledger["benchmark_opex_total_gbp"] == 0.0
    assert ledger["investor_thesis_gap_gbp"] == 0.0
    assert ledger["household_count"] == 0


def test_ofgem_allowance_has_no_prepayment_key():
    """This codebase's PaymentChannel enum has no Prepayment variant -- confirms the
    module's own documented scoping choice, not an oversight."""
    assert "prepayment" not in OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL
