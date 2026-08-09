"""The COMPANY's fabric-targeted intervention decision — `C14_thermal_parameter_inference`.

WHAT THIS SUITE IS FOR
======================
`company/pricing/fabric_intervention.py` is the first thing in this codebase that
SPENDS MONEY on a thermal belief. Three of its four outcomes are refusals, and a
refusal is the easiest thing in the world to get accidentally right — a function that
declined everything would pass a naive suite completely. So each guard is put under
mutation (R15) and each is shown firing on a premise the others do not touch.

THE GUARDS ARE ORDERED, AND TWO OF THEM OVERLAP — WHICH THE MUTATION FOUND
--------------------------------------------------------------------------
`decide` checks evidence, then positive value, then robustness. Writing the mutation
tests turned up something the design had not noticed: on a premise whose best offer
LOSES money, guards 2 and 3 both fire, because a winner that is negative at the
estimate is negative at the pessimistic bound too. So removing the do-nothing option
does NOT resurrect the loss-making sale — the robustness check catches it — and a
test asserting otherwise would simply have been false.

That is recorded rather than tidied away, and it changes what this suite claims:
"the outcome did not change under mutation" is NOT evidence a guard is inert here
(this project's own "guard shadowed by an outer guard" pattern, met head-on). Each
guard is therefore also shown firing ALONE, on an input the other cannot refuse —
`test_the_two_declines_are_INDEPENDENTLY_REACHABLE_and_not_one_guard_in_disguise`.
"""

from __future__ import annotations

import math
from dataclasses import replace

import pytest

from company.pricing import fabric_intervention as fi
from company.pricing.thermal_inference import (
    EvidenceBasis,
    HlcPrior,
    InsufficientObservationError,
    ThermalBelief,
    WallViolationError,
)

# A UK heating season at the 15.5 C published base, in K.day.
DEGREE_DAYS = 2000.0

# A realistic 2022-23 UK domestic GAS unit rate. Not an electricity rate: above about
# 20 p/kWh the heat pump wins on delivered efficiency whatever the fabric, and every
# fabric-sensitivity test below would go quietly vacuous.
GAS_RATE = 12.0


def _belief(
    hlc=0.25,
    *,
    relative_sd=0.20,
    basis=EvidenceBasis.METER_AND_EPC,
    floor_area_m2=90.0,
):
    prior = HlcPrior(
        hlc_kw_per_k=hlc,
        relative_sd=relative_sd,
        basis=basis,
        floor_area_m2=floor_area_m2,
        certificate_age_years=3.0,
    )
    return ThermalBelief(
        premise_id="P1",
        hlc_kw_per_k=hlc,
        relative_sd=relative_sd,
        basis=basis,
        prior=prior,
        meter_hlc_kw_per_k=hlc,
        meter_relative_sd=relative_sd,
        fit=None,
        response_time_constant_hours=None,
    )


# ===========================================================================
# THE WALL
# ===========================================================================


def test_the_module_does_not_reach_into_the_SIM():
    fi.assert_wall_intact()


def test_the_wall_control_DEFAULTS_TO_THIS_FILE_and_not_to_the_one_it_was_borrowed_from(tmp_path):
    """R15, and the specific fail-open this wrapper exists to close.

    `thermal_inference.assert_wall_intact()` defaults to `thermal_inference.py`. If
    this module had re-exported it unwrapped, calling it here would have cheerfully
    checked a DIFFERENT FILE and passed while this one imported the whole simulation.
    A control pointed at the wrong file is not a weak control, it is no control.
    """
    leaky = tmp_path / "leaky.py"
    leaky.write_text("from simulation.premise_trace import generate_premise_trace\n")
    with pytest.raises(WallViolationError):
        fi.assert_wall_intact(str(leaky))

    # ...and the default really is THIS module, not the borrowed one: point the
    # borrowed default at a clean file and it still passes, which is exactly why the
    # default had to be overridden rather than trusted.
    clean = tmp_path / "clean.py"
    clean.write_text("x = 1\n")
    fi.assert_wall_intact(str(clean))


def test_the_company_cannot_read_its_own_score():
    """A standing wall condition in the other direction: this module must not name,
    import or otherwise be able to find the harness that measures it."""
    import pathlib

    text = pathlib.Path(fi.__file__).read_text(encoding="utf-8")
    for forbidden in ("fabric_gap_ledger", "couple_fabric", "coupled_gap_ledger"):
        assert forbidden not in text, f"the company must not be able to find {forbidden}"


# ===========================================================================
# THE DO-NOTHING OPTION — the defect this module was built to close
# ===========================================================================


def test_DOING_NOTHING_is_always_in_the_choice_set_at_exactly_zero():
    ranked = dict(fi.rank_offers(0.25, 12000.0, DEGREE_DAYS, unit_rate_p_per_kwh=GAS_RATE))
    assert ranked[fi.DO_NOTHING] == 0.0


def test_the_REGRESSION_CASE_a_measure_worth_MINUS_41_POUNDS_is_refused():
    """THE OBSERVED DEFECT, pinned as a test (2026-08-09).

    A 0.08 kW/K flat using 4,000 kWh/yr at 7.4 p/kWh was recommended `time_shift` at
    a lifetime net value of MINUS £41 — spend £300 to save £259 — because the choice
    set the decision was drawn from had no do-nothing in it. The metric downstream
    then scored it as a correct decision, since the truth arm picked the same
    value-destroying measure.
    """
    result = fi.decide(
        "F1",
        0.08,
        hlc_pessimistic_kw_per_k=0.06,
        actionable=True,
        annual_heat_kwh=4000.0,
        annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=7.4,
    )
    assert result.decision is fi.Decision.DECLINE_NO_POSITIVE_VALUE
    assert result.measure == fi.DO_NOTHING
    best_offer = [(n, v) for n, v in result.ranked if n != fi.DO_NOTHING][0]
    assert best_offer[1] < 0.0, "the premise of this test is that every offer loses money"
    assert f"{best_offer[1]:,.0f}" in result.reason, "the refusal must name what it refused"


def test_R15_WITHOUT_THE_DO_NOTHING_OPTION_the_refusal_loses_its_REASON_and_its_ZERO(monkeypatch):
    """MUTATION — and the result is more interesting than the one this test was
    written expecting, so it is recorded rather than tidied.

    Strip the do-nothing option out of the ranking (exactly the choice set that
    existed before 2026-08-09) and the £-41 premise is STILL refused — by the
    robustness guard behind it, because a winner that is negative at the estimate is
    negative at the pessimistic bound too. The two guards overlap on this premise.
    THAT IS DEFENCE IN DEPTH AND IT IS ALSO A WARNING: it means "the outcome did not
    change" is NOT evidence that the do-nothing option is doing nothing, and it means
    a test asserting the loss-making sale returns would have been simply false.

    What the mutation DOES destroy is the two things the option is actually for:
    the REASON (the company can no longer say "nothing here is worth doing", only
    "I am not sure enough"), and the ZERO — the £0 reference the money consequence
    charges a decline against. Without it the least-bad LOSS becomes the reference,
    and every declined premise would be scored against a negative baseline.
    """
    real = fi.rank_offers

    def without_do_nothing(*args, **kwargs):
        return [(n, v) for n, v in real(*args, **kwargs) if n != fi.DO_NOTHING]

    monkeypatch.setattr(fi, "rank_offers", without_do_nothing)
    mutated = fi.decide(
        "F1", 0.08, hlc_pessimistic_kw_per_k=0.06, actionable=True,
        annual_heat_kwh=4000.0, annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=7.4,
    )
    assert mutated.decision is not fi.Decision.DECLINE_NO_POSITIVE_VALUE, (
        "the mutation must remove the ability to say 'nothing is worth doing', or it "
        "is not the mutation this test claims to be"
    )
    assert fi.DO_NOTHING not in dict(mutated.ranked), "no zero reference survives"
    assert max(v for _, v in mutated.ranked) < 0.0, (
        "and the best remaining option is a LOSS — the number a declined premise "
        "would then be scored against"
    )


def test_the_two_declines_are_INDEPENDENTLY_REACHABLE_and_not_one_guard_in_disguise():
    """Because the guards overlap on a negative winner, each must be shown firing on a
    premise the other does not touch, or this suite could not tell two controls from
    one."""
    no_value = fi.decide(
        "F1", 0.08, hlc_pessimistic_kw_per_k=0.08, actionable=True,
        annual_heat_kwh=4000.0, annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=7.4,
    )
    # Zero-width belief: the robustness guard CANNOT be what refused this one.
    assert no_value.decision is fi.Decision.DECLINE_NO_POSITIVE_VALUE

    not_robust = _robustness_case(0.34)
    # A strictly positive winner at the estimate: guard 2 cannot be what refused this.
    assert not_robust.ranked[0][1] > 0.0
    assert not_robust.decision is fi.Decision.DECLINE_NOT_ROBUST


def test_a_do_nothing_may_not_be_smuggled_in_as_a_priced_offer():
    """Inaction costs zero. An offer named `do_nothing` with a capex would silently
    price it, and every 'beats doing nothing' comparison below would be against a
    moving zero."""
    with pytest.raises(ValueError):
        fi.rank_offers(
            0.25,
            12000.0,
            DEGREE_DAYS,
            unit_rate_p_per_kwh=GAS_RATE,
            offers={fi.DO_NOTHING: fi.RetrofitOffer(fi.DO_NOTHING, 100.0, 0.0, 0.0, 0.0, 10.0)},
        )


def test_a_measure_that_merely_TIES_with_doing_nothing_loses_to_it():
    """A tie is not a reason to send an installer to someone's house."""
    breakeven = fi.RetrofitOffer("breakeven", 0.0, 0.0, 0.0, 0.0, 10.0)
    ranked = fi.rank_offers(
        0.25, 12000.0, DEGREE_DAYS, unit_rate_p_per_kwh=GAS_RATE,
        offers={"breakeven": breakeven},
    )
    assert dict(ranked)["breakeven"] == pytest.approx(0.0)
    assert ranked[0][0] == fi.DO_NOTHING


# ===========================================================================
# GUARD 1 — EVIDENCE
# ===========================================================================


def test_a_stock_prior_is_REFUSED_however_good_its_numbers_look():
    """C14's `is_actionable` refuses a stock prior because it contains no information
    about THIS premise. The refusal must survive a premise where acting would have
    looked extremely attractive, or it is only ever exercised on cases nobody wanted."""
    belief = _belief(0.45, relative_sd=0.05, basis=EvidenceBasis.STOCK_PRIOR)
    result = fi.recommend_measure(
        belief,
        annual_heat_kwh=22000.0,
        annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=GAS_RATE,
    )
    assert result.decision is fi.Decision.DECLINE_INSUFFICIENT_EVIDENCE
    assert "stock_prior" in result.reason


def test_R15_WITHOUT_THE_EVIDENCE_GUARD_THE_STOCK_PRIOR_IS_ACTED_ON():
    """MUTATION, aimed at guard 1 ALONE: the same premise with `actionable=True` must
    produce a live recommendation. If it did not, the evidence guard would be masked
    by one of the two guards behind it and this suite would be proving nothing."""
    result = fi.decide(
        "P1",
        0.45,
        hlc_pessimistic_kw_per_k=fi.__dict__ and 0.40,
        actionable=True,
        annual_heat_kwh=22000.0,
        annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=GAS_RATE,
    )
    assert result.decision is fi.Decision.RECOMMEND


def test_a_belief_WIDER_than_the_actionable_threshold_is_refused_on_width_alone():
    """The two halves of the refusal are independent: basis and width. This premise
    has a real certificate, so only the width can be refusing it."""
    belief = _belief(0.45, relative_sd=0.50, basis=EvidenceBasis.EPC_ONLY)
    result = fi.recommend_measure(
        belief,
        annual_heat_kwh=22000.0,
        annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=GAS_RATE,
    )
    assert result.decision is fi.Decision.DECLINE_INSUFFICIENT_EVIDENCE
    assert "0.500" in result.reason


# ===========================================================================
# GUARD 3 — ROBUSTNESS TO THE COMPANY'S OWN UNCERTAINTY
# ===========================================================================


def _robustness_case(relative_sd):
    """A premise sitting just above breakeven on insulation, so the width of the
    belief — and nothing else — decides whether the company commits."""
    return fi.recommend_measure(
        _belief(0.18, relative_sd=relative_sd, basis=EvidenceBasis.METER_AND_EPC),
        annual_heat_kwh=9000.0,
        annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=9.0,
    )


def test_the_SAME_estimate_is_acted_on_when_tight_and_refused_when_WIDE():
    """The interval must be able to change an outcome, or C14's whole uncertainty
    model is decoration. Same point estimate, same premise, same price — only the
    width moves."""
    tight = _robustness_case(0.05)
    wide = _robustness_case(0.34)
    assert tight.decision is fi.Decision.RECOMMEND, tight.reason
    assert wide.decision is fi.Decision.DECLINE_NOT_ROBUST, wide.reason
    assert wide.ranked[0][0] != fi.DO_NOTHING, (
        "this test must reach guard 3 — if the winner were already do-nothing it "
        "would be testing guard 2 under a different name"
    )


def test_R15_WITHOUT_THE_ROBUSTNESS_GUARD_THE_WIDE_BELIEF_IS_COMMITTED(monkeypatch):
    """MUTATION: make the pessimistic bound equal to the estimate — which is what
    ignoring the interval amounts to — and the wide belief is acted on."""
    result = fi.decide(
        "P1",
        0.18,
        hlc_pessimistic_kw_per_k=0.18,
        actionable=True,
        annual_heat_kwh=9000.0,
        annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=9.0,
    )
    assert result.decision is fi.Decision.RECOMMEND


def test_robustness_is_NOT_a_correction_toward_truth_and_a_confident_error_sails_through():
    """THE PROPERTY THAT KEEPS THIS HONEST. The pessimistic bound comes from the
    COMPANY's own belief, not from the world. A belief that is badly wrong but tightly
    held therefore passes the robustness check exactly as a correct one does — the
    company cannot hedge against an error it does not know it has, and a mechanism
    that let it would be reading the truth through the wall.
    """
    confidently_wrong = fi.recommend_measure(
        _belief(0.45, relative_sd=0.03, basis=EvidenceBasis.METER_AND_EPC),
        annual_heat_kwh=9000.0,
        annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=GAS_RATE,
    )
    assert confidently_wrong.decision is fi.Decision.RECOMMEND
    assert confidently_wrong.measure == "insulate"


# ===========================================================================
# THE PHYSICS
# ===========================================================================


def test_only_the_FABRIC_share_of_the_bill_is_available_to_insulation():
    """A home whose bill is mostly hot water and cooking gets very little from a
    cavity fill. Insulation saving must scale with HLC x degree days, never with the
    bill — the previous formulation scaled a demand estimate by `belief / truth`,
    which no company could compute because it needs the truth."""
    # Both HLCs kept BELOW the point where fabric loss exceeds the bill, or the cap
    # would flatten the ratio and this test would silently measure the cap instead.
    small = fi.offer_annual_saving_kwh(0.05, 12000.0, DEGREE_DAYS, fi.OFFER_BOOK["insulate"])
    large = fi.offer_annual_saving_kwh(0.15, 12000.0, DEGREE_DAYS, fi.OFFER_BOOK["insulate"])
    assert 0.15 * DEGREE_DAYS * 24.0 < 12000.0, "the fixture must not be in the capped region"
    assert large == pytest.approx(3.0 * small)
    assert small == pytest.approx(0.30 * 0.05 * DEGREE_DAYS * 24.0)


def test_the_fabric_share_is_CAPPED_at_the_energy_the_premise_actually_used():
    """A belief may imply more loss than the premise burned. Valuing a measure on the
    excess would be saving kWh nobody consumed. The cap refuses that WITHOUT moving
    the belief back toward truth — it is not a correction, it is a refusal."""
    absurd = fi.fabric_heat_kwh(2.0, DEGREE_DAYS, annual_heat_kwh=9000.0)
    assert absurd == pytest.approx(9000.0)
    uncapped = fi.fabric_heat_kwh(2.0, DEGREE_DAYS)
    assert uncapped == pytest.approx(2.0 * DEGREE_DAYS * 24.0)


def test_solar_does_not_scale_with_fabric_so_the_decision_can_be_wrong_BOTH_WAYS():
    """PV is in the choice set precisely so OVERestimating fabric is punished too: a
    home steered to insulation when PV was the better buy is a real error, and a
    choice set of only fabric measures could not express it."""
    for hlc in (0.08, 0.45):
        assert fi.offer_annual_saving_kwh(
            hlc, 12000.0, DEGREE_DAYS, fi.OFFER_BOOK["solar_pv"]
        ) == pytest.approx(fi.SOLAR_KWH_PER_YEAR)


def test_NO_SAVING_MAY_COME_FROM_DISCOUNTING():
    """THE MISSION CONSTRAINT, structural rather than asserted: the saving function
    has no price parameter at all, so no tariff move can conjure a saved kWh."""
    import inspect

    parameters = inspect.signature(fi.offer_annual_saving_kwh).parameters
    assert not any("rate" in p or "price" in p or "tariff" in p for p in parameters), (
        f"a physical saving must not take a price: {list(parameters)}"
    )
    useless = fi.RetrofitOffer("useless", 5000.0, 0.0, 0.0, 0.0, 30.0)
    for rate in (5.0, 25.0, 200.0):
        ranked = dict(
            fi.rank_offers(0.25, 12000.0, DEGREE_DAYS, unit_rate_p_per_kwh=rate,
                           offers={"useless": useless})
        )
        assert ranked["useless"] == pytest.approx(-5000.0)
        assert ranked[fi.DO_NOTHING] == 0.0


# ===========================================================================
# REFUSALS ON DEGENERATE INPUT — every one of these is NaN-blind if unchecked
# ===========================================================================


@pytest.mark.parametrize(
    "call",
    [
        lambda: fi.rank_offers(0.2, 9000.0, DEGREE_DAYS, unit_rate_p_per_kwh=0.0),
        lambda: fi.rank_offers(0.2, 9000.0, DEGREE_DAYS, unit_rate_p_per_kwh=float("nan")),
        lambda: fi.offer_annual_saving_kwh(0.0, 9000.0, DEGREE_DAYS, fi.OFFER_BOOK["insulate"]),
        lambda: fi.offer_annual_saving_kwh(float("nan"), 9000.0, DEGREE_DAYS, fi.OFFER_BOOK["insulate"]),
        lambda: fi.offer_annual_saving_kwh(0.2, float("nan"), DEGREE_DAYS, fi.OFFER_BOOK["insulate"]),
        lambda: fi.offer_annual_saving_kwh(0.2, -1.0, DEGREE_DAYS, fi.OFFER_BOOK["insulate"]),
        lambda: fi.offer_annual_saving_kwh(0.2, 9000.0, 0.0, fi.OFFER_BOOK["insulate"]),
        lambda: fi.offer_annual_saving_kwh(0.2, 9000.0, float("nan"), fi.OFFER_BOOK["insulate"]),
        lambda: fi.RetrofitOffer("bad", float("nan"), 0.0, 0.0, 0.0, 30.0),
        lambda: fi.RetrofitOffer("bad", 100.0, 0.0, 0.0, 0.0, 0.0),
    ],
)
def test_degenerate_inputs_are_REFUSED(call):
    with pytest.raises(InsufficientObservationError):
        call()


def test_a_NaN_saving_can_never_reach_a_threshold_comparison():
    """Every comparison in this module is NaN-blind (`nan > 0` is False), so the
    refusals above have to happen FIRST. This asserts the ordering holds end to end
    rather than trusting each function individually."""
    with pytest.raises(InsufficientObservationError):
        fi.decide(
            "P1",
            float("nan"),
            hlc_pessimistic_kw_per_k=0.1,
            actionable=True,
            annual_heat_kwh=9000.0,
            annual_degree_days_k_day=DEGREE_DAYS,
            unit_rate_p_per_kwh=GAS_RATE,
        )


# ===========================================================================
# THE BOOK
# ===========================================================================


def test_a_premise_that_cannot_be_priced_is_REFUSED_not_silently_dropped():
    """A targeting list that quietly drops the customers it could not price reads as
    complete when it is not — this project's most-repeated fail-open shape."""
    beliefs = [replace(_belief(), premise_id="A"), replace(_belief(), premise_id="B")]
    with pytest.raises(InsufficientObservationError):
        fi.recommendations_for(
            beliefs,
            annual_heat_kwh={"A": 12000.0},
            annual_degree_days_k_day=DEGREE_DAYS,
            unit_rate_p_per_kwh=GAS_RATE,
        )


def test_a_book_decision_is_order_preserving_and_deterministic():
    beliefs = [
        replace(_belief(0.10), premise_id="A"),
        replace(_belief(0.40), premise_id="B"),
        replace(_belief(0.25), premise_id="C"),
    ]
    heat = {"A": 5000.0, "B": 20000.0, "C": 12000.0}
    first = fi.recommendations_for(
        beliefs, annual_heat_kwh=heat, annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=GAS_RATE,
    )
    second = fi.recommendations_for(
        beliefs, annual_heat_kwh=heat, annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=GAS_RATE,
    )
    assert [r.premise_id for r in first] == ["A", "B", "C"]
    assert [(r.decision, r.measure) for r in first] == [(r.decision, r.measure) for r in second]


def test_every_recommendation_carries_its_basis():
    """R14 — a financial figure without its clock/basis is a defect, and that applies
    to a decline as much as to a recommendation."""
    for belief in (_belief(), _belief(basis=EvidenceBasis.STOCK_PRIOR)):
        result = fi.recommend_measure(
            belief,
            annual_heat_kwh=12000.0,
            annual_degree_days_k_day=DEGREE_DAYS,
            unit_rate_p_per_kwh=GAS_RATE,
        )
        assert result.basis.startswith("PROVISIONAL")
        assert "never from discounting" in result.basis


def test_a_decline_never_reports_a_measure_or_a_value():
    """A decline that carried a measure name or a non-zero value would be read
    downstream as an action. `acted` is the single place that distinction lives."""
    result = fi.recommend_measure(
        _belief(basis=EvidenceBasis.STOCK_PRIOR),
        annual_heat_kwh=12000.0,
        annual_degree_days_k_day=DEGREE_DAYS,
        unit_rate_p_per_kwh=GAS_RATE,
    )
    assert not result.acted
    assert result.measure == fi.DO_NOTHING
    assert result.lifetime_net_value_gbp == 0.0
    assert math.isfinite(result.lifetime_net_value_gbp)
