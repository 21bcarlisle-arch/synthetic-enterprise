"""Tests for saas/opex_ledger.py -- MARGIN_REALISM Step 3 opex mechanism (Maturity Map B2)."""
import pytest

from saas.opex_ledger import (
    DCC_COMMS_CHARGE_GBP_PER_YEAR,
    GOVERNANCE_COST_LINES,
    INFRASTRUCTURE_COST_LINES,
    OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL,
    acquisition_cost_gbp,
    ai_compute_and_oversight_cost_gbp_per_year,
    audit_fee_gbp,
    break_even_analysis,
    break_even_customer_count,
    broker_commission_gbp,
    build_opex_ledger,
    cost_lines_by_classification,
    fixed_cost_floor_gbp_per_year,
    governance_floor_gbp_per_year,
    infrastructure_floor_gbp_per_year,
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


# -- Category (4): infrastructure at commercial rates --

def test_infrastructure_floor_sums_all_four_lines():
    total = infrastructure_floor_gbp_per_year()
    assert total == pytest.approx(sum(l["annual_gbp"] for l in INFRASTRUCTURE_COST_LINES.values()))
    assert total > 0


def test_infrastructure_cost_lines_all_estimates_flagged():
    """None of the category (4) anchors were found as a clean citable figure --
    every line must honestly say so, per the research doc."""
    for name, line in INFRASTRUCTURE_COST_LINES.items():
        assert line["is_estimate"] is True, name


def test_infrastructure_cost_lines_have_classification():
    for line in INFRASTRUCTURE_COST_LINES.values():
        assert line["classification"] in {"fixed", "stepped", "variable"}


# -- Category (5): fixed governance & professional --

def test_governance_floor_excludes_golive_conditional_by_default():
    excl = governance_floor_gbp_per_year(golive=False)
    incl = governance_floor_gbp_per_year(golive=True)
    assert incl > excl


def test_governance_floor_golive_true_includes_ofgem_and_insurance():
    excl = governance_floor_gbp_per_year(golive=False)
    incl = governance_floor_gbp_per_year(golive=True)
    ofgem = GOVERNANCE_COST_LINES["ofgem_licence_fee"]["annual_gbp"]
    insurance = GOVERNANCE_COST_LINES["insurance_pi_cyber_dando"]["annual_gbp"]
    assert incl - excl == pytest.approx(ofgem + insurance)


def test_ofgem_licence_fee_is_real_not_estimate():
    assert GOVERNANCE_COST_LINES["ofgem_licence_fee"]["is_estimate"] is False


def test_audit_fee_flat_below_5m_turnover():
    assert audit_fee_gbp(1_000_000) == GOVERNANCE_COST_LINES["statutory_audit"]["annual_gbp"]


def test_audit_fee_scales_at_5m_to_10m_band():
    assert audit_fee_gbp(8_000_000) == pytest.approx(8_000_000 * 0.0025)


def test_audit_fee_scales_at_10m_plus_band():
    assert audit_fee_gbp(20_000_000) == pytest.approx(20_000_000 * 0.0019)


def test_fixed_cost_floor_combines_infra_and_governance():
    result = fixed_cost_floor_gbp_per_year(golive=False)
    assert result["total_floor_gbp"] == pytest.approx(
        result["infrastructure_gbp"] + result["governance_gbp"]
    )
    assert result["golive"] is False


def test_fixed_cost_floor_golive_true_is_larger():
    excl = fixed_cost_floor_gbp_per_year(golive=False)
    incl = fixed_cost_floor_gbp_per_year(golive=True)
    assert incl["total_floor_gbp"] > excl["total_floor_gbp"]


# -- Category (6): scale structure + CAC --

def test_cost_lines_by_classification_covers_all_lines():
    result = cost_lines_by_classification()
    total_classified = sum(len(v) for v in result.values())
    assert total_classified == len(INFRASTRUCTURE_COST_LINES) + len(GOVERNANCE_COST_LINES) + 3
    assert "dcc_comms_charge" in result["variable"]


def test_acquisition_cost_dual_fuel_pcs():
    assert acquisition_cost_gbp("pcs_aggregator", is_dual_fuel=True) == 55.0


def test_acquisition_cost_single_fuel_pcs():
    assert acquisition_cost_gbp("pcs_aggregator", is_dual_fuel=False) == 27.5


def test_acquisition_cost_unknown_channel_is_zero_not_invented():
    """Direct/brand marketing CAC was flagged too weak to build on (no
    energy-specific anchor) -- must return 0.0, never a fabricated number."""
    assert acquisition_cost_gbp("direct_brand_marketing") == 0.0


def test_broker_commission_scales_with_kwh():
    low = broker_commission_gbp(1000, "sme")
    high = broker_commission_gbp(2000, "sme")
    assert high == pytest.approx(low * 2)


def test_broker_commission_unknown_segment_is_zero():
    assert broker_commission_gbp(1000, "residential") == 0.0


def test_broker_commission_larger_ic_has_lower_rate_per_kwh():
    """Real sourced bands: rate per kWh decreases as I&C size band increases."""
    sme = broker_commission_gbp(100_000, "sme")
    mid = broker_commission_gbp(100_000, "ic_mid_market")
    hh = broker_commission_gbp(100_000, "ic_half_hourly")
    assert sme > mid > hh


# -- Break-even analysis --

def test_break_even_customer_count_none_when_margin_non_positive():
    assert break_even_customer_count(10000, 0.0) is None
    assert break_even_customer_count(10000, -5.0) is None


def test_break_even_customer_count_basic_division():
    assert break_even_customer_count(10000, 100.0) == 100.0


def test_break_even_analysis_at_current_mix():
    result = break_even_analysis(
        segment_avg_gross_margin_gbp={"resi": 50.0, "sme": 200.0},
        current_mix_counts={"resi": 8, "sme": 2},
        fixed_floor_gbp=1000.0,
    )
    expected_weighted = (50.0 * 8 + 200.0 * 2) / 10
    assert result["weighted_avg_gross_margin_gbp_per_customer"] == pytest.approx(expected_weighted)
    assert result["break_even_customers_at_current_mix"] == pytest.approx(1000.0 / expected_weighted, rel=0.01)


def test_break_even_analysis_per_segment_sensitivity():
    result = break_even_analysis(
        segment_avg_gross_margin_gbp={"resi": 50.0, "sme": 200.0},
        current_mix_counts={"resi": 8, "sme": 2},
        fixed_floor_gbp=1000.0,
    )
    assert result["break_even_customers_per_segment_if_pure"]["resi"] == 20.0
    assert result["break_even_customers_per_segment_if_pure"]["sme"] == 5.0


def test_break_even_analysis_empty_book():
    result = break_even_analysis({}, {}, 1000.0)
    assert result["current_book_size"] == 0
    assert result["weighted_avg_gross_margin_gbp_per_customer"] == 0.0
    assert result["covers_floor_at_current_mix"] is False
