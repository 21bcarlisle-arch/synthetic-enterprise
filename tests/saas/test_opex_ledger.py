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

def test_ai_compute_cost_always_zero_pending_representative_usage_data():
    """The oversight-rate/costing-basis questions this was originally blocked on are
    now RESOLVED (2026-07-11 NTFY, folded into GOVERNANCE_COST_LINES["director_
    oversight_expertise"] instead) -- but the per-customer METERED sub-component still
    must never be silently defaulted to a fabricated number (R12): the underlying
    representative-usage-data gap (token-usage-log.jsonl, 5 non-representative days)
    remains open."""
    assert ai_compute_and_oversight_cost_gbp_per_year(_cust("C1")) == 0.0
    assert ai_compute_and_oversight_cost_gbp_per_year({}) == 0.0


def test_director_oversight_expertise_governance_line_real_and_decided():
    """2026-07-11 NTFY resolution: 'Assume £500k pa of expertise needed.' Real,
    decided, not an estimate -- the director's own figure, not the agent's to invent."""
    line = GOVERNANCE_COST_LINES["director_oversight_expertise"]
    assert line["annual_gbp"] == 500_000.0
    assert line["is_estimate"] is False
    assert line["classification"] == "fixed"
    assert line["golive_conditional"] is False


def test_governance_floor_includes_director_oversight_expertise():
    floor_without_golive = governance_floor_gbp_per_year(golive=False)
    other_lines_total = sum(
        line["annual_gbp"] for name, line in GOVERNANCE_COST_LINES.items()
        if name != "director_oversight_expertise" and not line["golive_conditional"]
    )
    assert floor_without_golive == pytest.approx(other_lines_total + 500_000.0)


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
    """The unresolved branch, exercised with a channel that is genuinely not a channel.

    This used `"prepayment"` as its stand-in for "not in OFGEM_BUNDLED_ALLOWANCE" -- true
    when written, and false from 2026-09-05, when prepayment became a real channel with a
    real published allowance. A test that reaches a branch via a value the world later
    starts producing legitimately stops testing the branch and starts asserting the defect.

    `build_opex_ledger` takes plain strings, not the enum, so this branch stays reachable
    from a caller passing a stale or mistyped channel -- but it is no longer reachable from
    any PaymentChannel member, which is exactly what
    `test_a_payment_channel_the_world_can_produce_has_a_benchmark_allowance` now enforces.
    """
    from simulation.household_segments import PaymentChannel

    not_a_channel = "cheque_by_post"
    assert not_a_channel not in {c.value for c in PaymentChannel}
    assert not_a_channel not in OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL

    customers = [_cust("C9", "electricity", True)]
    ledger = build_opex_ledger(customers, {"C9": not_a_channel})
    assert ledger["true_third_party_cost_gbp"] == pytest.approx(19.01)  # true side unaffected
    assert ledger["benchmark_labour_cost_gbp"] == 0.0
    assert ledger["household_count"] == 0
    assert ledger["unresolved_household_count"] == 1


def test_a_prepayment_household_now_counts_in_the_benchmark_population():
    """The defect this pair of commits fixes, stated as its own control.

    A prepayment household used to land in `unresolved_household_count` and leave the
    benchmark population entirely -- so `household_count` under-reported the book and every
    per-household figure divided by the wrong denominator.
    """
    customers = [_cust("C9", "electricity", True)]
    ledger = build_opex_ledger(customers, {"C9": "prepayment"})

    assert ledger["household_count"] == 1
    assert ledger["unresolved_household_count"] == 0
    assert ledger["benchmark_labour_cost_gbp"] > 0.0


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


# -- per-household figures (ADVISOR_STEER_THESIS_CHART.md defect 2: the *_total_gbp
# fields are book SUMS accumulated across households, previously mislabelled as
# per-household on the Front Door) --

def test_build_opex_ledger_per_household_is_total_over_count():
    customers = [
        _cust("C1", "electricity", True),
        _cust("C2", "electricity", False),
    ]
    ledger = build_opex_ledger(customers, {"C1": "direct_debit", "C2": "standard_credit"})
    assert ledger["household_count"] == 2
    assert ledger["benchmark_opex_per_household_gbp"] == pytest.approx(
        ledger["benchmark_opex_total_gbp"] / 2, abs=0.01
    )
    assert ledger["true_opex_per_household_gbp"] == pytest.approx(
        ledger["true_opex_total_gbp"] / 2, abs=0.01
    )


def test_build_opex_ledger_per_household_zero_when_no_households():
    """Divide-by-zero guard: an empty/fully-unresolved book yields 0.0, not a crash."""
    ledger = build_opex_ledger([], {})
    assert ledger["benchmark_opex_per_household_gbp"] == 0.0
    assert ledger["true_opex_per_household_gbp"] == 0.0


def test_build_opex_ledger_per_household_single_household_equals_total():
    customers = [_cust("C1", "electricity", True)]
    ledger = build_opex_ledger(customers, {"C1": "direct_debit"})
    assert ledger["benchmark_opex_per_household_gbp"] == pytest.approx(
        ledger["benchmark_opex_total_gbp"]
    )
    assert ledger["true_opex_per_household_gbp"] == pytest.approx(
        ledger["true_opex_total_gbp"]
    )


def test_a_payment_channel_the_world_can_produce_has_a_benchmark_allowance():
    """Every PaymentChannel member must have an allowance, or its households vanish.

    THIS TEST REPLACES `test_ofgem_allowance_has_no_prepayment_key`, which asserted
    `"prepayment" not in OFGEM_BUNDLED_ALLOWANCE_...` and called it "the module's own
    documented scoping choice, not an oversight". That was keyed to the answer of the day
    rather than to a property, and it did exactly what such a control does: on 2026-09-05
    PB4 separated PREPAYMENT out of STANDARD_CREDIT, the world started producing a channel
    the allowance table did not carry, and the control that should have caught it was
    instead GREEN -- it was pinned to the very state that had become wrong. It went red
    only when the code became MORE honest, which is backwards.

    The property is the one that matters to the reader of the number: a household whose
    channel has no allowance is not an error, it is silently dropped from the benchmark
    population by `.get`, so the book shrinks and the per-household figures published on
    the Front Door thesis chart divide by a smaller denominator.

    Keyed to the enum rather than to a literal list, so the next channel added reds here
    on the commit that adds it, naming the file to change.
    """
    from simulation.household_segments import PaymentChannel

    missing = [
        channel.value
        for channel in PaymentChannel
        if channel.value not in OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL
    ]
    assert not missing, (
        f"PaymentChannel member(s) {missing} have no Ofgem benchmark allowance. Their "
        "households will be dropped from the benchmark population silently. Add the "
        "published Ofgem allowance to OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL in "
        "saas/opex_ledger.py -- and if no figure is published for it, say so there "
        "explicitly rather than leaving the key absent."
    )


def test_the_prepayment_allowance_is_the_published_ofgem_figure():
    """Sourced, not chosen: Ofgem cap Jul-Sep 2026 Annex 3, 17% of the £1,812 PPM
    dual-fuel cap. Recorded in ASSUMPTIONS.md at H confidence since 2026-07-10, and
    quoted in this module's own comment for two months before it had a population."""
    assert OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL["prepayment"] == 308.04
    assert 1812 * 0.17 == pytest.approx(308.04, abs=0.05)


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
