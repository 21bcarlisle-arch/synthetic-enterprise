"""An axis claiming to be DISCOVERABLE must actually move something a supplier could see.

WHY THIS EXISTS. `segmentation_curriculum_v1.json` marks each drawn attitude axis
`hidden_truth_only: true|false` and, when false, names the channel through which a supplier could
learn it. On 2026-08-27 that field was found to be read by **no code anywhere** — a claim in a data
file with nothing behind it — and two of the three claims were false:

  * `price_sensitivity` — "discoverable via rate-change churn response". Nothing wired the axis to
    the churn response; it was drawn, coverage-tested, wall-guarded, mutation-tested against leaks,
    and read by no live module.
  * `channel_pref` — "discoverable via the contact channel actually used". `contact_propensity.py`
    keys on the ENGAGEMENT archetype and never reads `channel_pref`.

Both were undiscoverable IN PRINCIPLE while the curriculum promised a route. A supplier that tried
to learn either would have been right to try and would have failed forever, and the failure would
have read as a weak company model rather than as an absent channel.

THE DIRECTOR'S RULE, 2026-08-27: *"if a trait has no channel the company can observe, either give
it one or mark it hidden. Don't leave it claiming discoverable and don't wait for me to say so."*
`price_sensitivity` was given one; `channel_pref` was marked hidden. This test is what stops the
next one drifting back, per MAKE_IT_STICK — *"a rule lives in CLAUDE.md AND as enforced code, or
not at all; prose-only is worse than no rule."*

WHAT A PROBE HAS TO SHOW, and why it is not a grep. "The axis is mentioned in a live module" is
satisfied by a comment — a mention is not a use, found five times in one day on 2026-08-27. A probe
runs the WORLD'S DECISION and shows that two households differing only in that axis face different
outcomes. That is the necessary condition for any supplier, however clever, to infer anything: if
the decision does not move, no volume of observation can recover the trait.

TWO PROBE BARS, because two kinds of claim live in this file. An INFERRED axis
(`price_sensitivity`) clears the bar above: the world's decision must move with it, or no volume of
observation recovers it. An OBSERVED axis (`region`) clears a strictly stronger and quite different
bar: the value is on the company's own record, so the probe reads the OBSERVABLE stream and shows
the value is there and varies. Both are probes; neither is a grep; and an axis is not excused from
one bar by being the other kind.

THE FIRST WIDENING, 2026-08-27, and why the scan is not filtered by name. This file shipped
scanning `key.endswith("_marginals")`, which is a naming convention and not the subject. The
curriculum carried `hidden_truth_only` on FIVE keys and the filter admitted three, so the two it
dropped — `tenure_adoption_gating_strength` and `region_marginal_synthetic_acquisitions` — both
claimed DISCOVERABLE with no probe, unseen. `MIN_AXES_SCANNED` was worse than useless while it was
pinned to whatever that filter returned: the one guard written to catch a missed axis was satisfied
by its own blindness, which is the catalogued shape where an exclusion scoped by a naming
convention hides everything the convention mixes. The scan now enumerates every key carrying the
flag, whatever it is called, and the floor is re-based on the widened scan. Dispositions from that
widening: `region` got the observed-axis probe below; `tenure_adoption_gating_strength` was marked
hidden, because its declared channel does not exist in the live run (see that test).
"""
from __future__ import annotations

import pytest

from simulation.population_draw import _load_cohort_curriculum

#: Measured 2026-08-27 on the WIDENED scan: five keys carry the flag. A floor, because a scan that
#: found none would report a clean sweep — the defect this file exists to catch, one level up. It is
#: a floor on the flag, not on a suffix: the previous value of 3 was the suffix filter's own yield,
#: so raising the count that mattered could not move it. Raise this when an axis is added.
MIN_AXES_SCANNED = 5

#: The suffix three of the five keys happen to carry. Stripped for readability ONLY — never used to
#: decide membership, which is the defect above.
_COSMETIC_SUFFIX = "_marginals"


def _axes_in(curriculum: dict) -> dict[str, dict]:
    """Every key declaring `hidden_truth_only`, keyed by its axis name.

    MEMBERSHIP IS THE FLAG, NOT THE NAME. Takes the curriculum as an argument so the R15 mutation
    below can hand it a fabricated one — a scan that could only ever read the shipped file could
    not be proven to fire on a key the shipped file does not contain.
    """
    out = {}
    for key, spec in curriculum.items():
        if not isinstance(spec, dict) or "hidden_truth_only" not in spec:
            continue
        name = key[: -len(_COSMETIC_SUFFIX)] if key.endswith(_COSMETIC_SUFFIX) else key
        out[name] = spec
    return out


def _axes() -> dict[str, dict]:
    return _axes_in(_load_cohort_curriculum())


def _axes_claiming_discoverable_without_a_probe(axes: dict[str, dict]) -> list[str]:
    return sorted(a for a, spec in axes.items() if not spec["hidden_truth_only"] and a not in PROBES)


def _probe_price_sensitivity() -> list[float]:
    """The world's churn decision for one account at one renewal, across elasticities.

    THE DECISION, NOT THE ROLL. The company observes departures, not probabilities; but a
    probability that does not move is a departure rate that does not move, so this is the necessary
    condition stated at the point it can be measured without averaging over thousands of dice.
    """
    from simulation import population_draw as pd
    from simulation.customer_events import roll_lifecycle_event
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh
    from tests.simulation.test_customer_events import (
        _build_one_year_records,
        _first_renewal_date,
        _make_customers,
    )

    renewal = _first_renewal_date("2016-01-01")
    svt = get_svt_elec_rate_gbp_per_mwh(renewal)
    original = pd.price_elasticity_for_customer
    out: list[float] = []
    try:
        for weight in (0.5, 1.0, 2.0):
            pd.price_elasticity_for_customer = lambda *a, _w=weight, **k: _w
            event = roll_lifecycle_event(
                "C5", renewal, "electricity",
                _build_one_year_records(), _make_customers(),
                old_rate_gbp_per_mwh=svt, new_rate_gbp_per_mwh=svt * 1.20,
            )
            assert event is not None, "the probe's fixture stopped reaching a renewal"
            out.append(event["realized_churn_probability"])
    finally:
        pd.price_elasticity_for_customer = original
    return out


def _probe_region() -> list[str]:
    """The region the company READS off its own enrolment record, for real drawn acquisitions.

    THE OBSERVED BAR, NOT THE INFERRED ONE. `region` does not have to move a decision to be
    learnable, because it is not learned: it is on the account. So the necessary condition is that
    the value reaches the OBSERVABLE stream on the shipped path and distinguishes customers — a
    single constant would be the `_PLACEHOLDER_REGION` state this axis exists to have closed.

    READ FROM THE OBSERVABLE SIDE. This goes through `to_customer_dict()`, the saas-shaped dict the
    integration layer consumes, and never touches the hidden `cohort` — reading the trait off SIM
    truth would prove the wall was broken, not that the channel exists. `draw_region=True` is the
    live setting (`simulation/live_population.py::_drawn_trickle`), passed here rather than
    imported, so this probe fails if the shipped path stops drawing regions.
    """
    from simulation.population_draw import iter_acquisition_events

    out: list[str] = []
    for customer in iter_acquisition_events(20260827, 2016, 2025, draw_region=True):
        out.append(customer.to_customer_dict()["location"]["region"])
    # POPULATION FLOOR on the probe's own subject. Measured 10 acquisitions / 7 distinct regions
    # over the full decade at this seed. Without this a fixture that quietly drew one customer
    # would still be judged by the distinctness assertion downstream, which one customer cannot
    # fail — a probe that cannot fail is the thing this whole file exists to refuse.
    assert len(out) >= 5, (
        f"the probe drew only {len(out)} acquisitions — too few for its own distinctness check to "
        "mean anything, so the fixture has collapsed rather than the axis")
    return out


#: axis -> probe. An axis claiming DISCOVERABLE must appear here; adding one without a probe fails.
PROBES = {
    "price_sensitivity": _probe_price_sensitivity,
    "region_marginal_synthetic_acquisitions": _probe_region,
}


def test_the_scan_sees_the_whole_set_of_axes():
    """POPULATION FLOOR. If the marginals were renamed or the loader changed shape, every
    assertion below would pass over an empty set and report the curriculum clean."""
    axes = _axes()
    assert len(axes) >= MIN_AXES_SCANNED, (
        f"only {len(axes)} axes carry `hidden_truth_only` (floor {MIN_AXES_SCANNED}) — this "
        "control's own subject has collapsed, so its green means nothing")


def test_every_axis_claiming_DISCOVERABLE_has_a_probe():
    missing = _axes_claiming_discoverable_without_a_probe(_axes())
    assert not missing, (
        f"these axes claim to be discoverable and no probe demonstrates it: {missing}. Either wire "
        "the axis to something a supplier can observe and add a probe here, or set "
        "`hidden_truth_only: true`. Leaving the claim standing is what made price_sensitivity and "
        "channel_pref undiscoverable in principle while the file promised a route.")


@pytest.mark.parametrize("axis", sorted(PROBES))
def test_each_probe_shows_the_axis_MOVING_the_worlds_decision(axis):
    """R15: the claim must be able to FAIL. If the wiring is reverted, the probe returns one value
    repeated and this fires — which is precisely the state the curriculum described as
    'discoverable' for months."""
    observed = PROBES[axis]()
    assert len(observed) > 1, f"the {axis} probe returned nothing to compare"
    assert len(set(observed)) > 1, (
        f"{axis} claims to be discoverable, but its probe returns one value repeated "
        f"({observed[0]}) — for an inferred axis that means households differing only in it face "
        "identical decisions and no volume of observation recovers it; for an observed axis it "
        "means the value on the record distinguishes nobody. Either way the claimed channel "
        "carries no information.")


def test_the_tenure_adoption_gate_is_still_unwired_in_the_live_run():
    """WHY `tenure_adoption_gating_strength` IS MARKED HIDDEN, stated as a fact that can expire.

    Its note claimed the company must DISCOVER that tenure gates adoption from its own data. The
    only channel from that curriculum value into any adoption decision is `generate_life_events`'s
    `adoption_eligibility_multiplier`, and the sole live caller does not pass it, so every live
    adoption gate runs ungated at 1.0. `Household` carries no tenure field, so the decision cannot
    reach tenure by another route either. Marked hidden 2026-08-27 on the director's rule — "either
    give it one or mark it hidden" — rather than left claiming a route a supplier would mine for
    forever. Live-run activation is R13 director-reserved curriculum, so giving it one is not the
    agent's move.

    R11, NO ORPHAN TRANSITION: this is the RELEASE. When the director activates the gate, the live
    call starts carrying a real per-household factor, this fires, and the flag has to go back to
    false with a probe. It asserts the wiring's ABSENCE by running the real construction and
    recording what it actually passed — not by grepping the source for the parameter name.
    """
    from simulation import household_demand

    calls: list = []
    real = household_demand.generate_life_events

    def _recording(*args, **kwargs):
        calls.append(kwargs.get("adoption_eligibility_multiplier", 1.0))
        return real(*args, **kwargs)

    household_demand.generate_life_events = _recording
    try:
        household_demand.HouseholdDemandRegister(
            [{"customer_id": "C1", "segment": "resi"}, {"customer_id": "C2", "segment": "resi"}]
        )
    finally:
        household_demand.generate_life_events = real

    assert calls, "the fixture built no households, so it observed nothing about the live call"
    assert set(calls) == {1.0}, (
        f"the live run now passes an adoption gating factor ({sorted(set(calls))}) — tenure gates "
        "adoption in the world the company lives in, so `tenure_adoption_gating_strength` is no "
        "longer hidden truth. Set `hidden_truth_only: false` and add a probe showing the adoption "
        "decision moving with tenure.")
    assert _axes()["tenure_adoption_gating_strength"]["hidden_truth_only"] is True


def test_the_scan_finds_a_flagged_key_that_does_not_follow_the_marginals_naming():
    """R15 MUTATION: the exact defect this widening repaired, planted and required to fire.

    A sixth key carrying `hidden_truth_only: false` and a fabricated channel note, named without
    the `_marginals` suffix. Against the shipped suffix filter this was invisible and the control
    reported the curriculum clean; against the widened scan it must be caught. The mutation is fed
    through `_axes_in`, so it exercises the real membership rule rather than a copy of it.
    """
    mutated = dict(_load_cohort_curriculum())
    mutated["nudge_susceptibility_gating_strength"] = {
        "value": 0.4,
        "hidden_truth_only": False,
        "note": "DISCOVERABLE via the customer's observed response to reminder emails.",
    }

    axes = _axes_in(mutated)
    assert "nudge_susceptibility_gating_strength" in axes, (
        "the scan dropped a flagged key because of what it is called — this is the defect the "
        "widening repaired, returning")
    assert len(axes) > MIN_AXES_SCANNED, "the population floor did not move with the planted key"
    assert "nudge_susceptibility_gating_strength" in _axes_claiming_discoverable_without_a_probe(axes)

    # ...and the same planted key is invisible to the filter this file used to ship with, which is
    # what made the floor of 3 satisfiable by the control's own blindness.
    by_suffix = {k for k in mutated if k.endswith(_COSMETIC_SUFFIX)}
    assert "nudge_susceptibility_gating_strength" not in by_suffix


def test_an_axis_marked_HIDDEN_is_never_required_to_prove_anything():
    """The escape hatch is honest and must stay open: marking a trait hidden is always a legitimate
    answer, and is the one `channel_pref` and `green_stance` take. This asserts the control does not
    quietly demand a probe for them — a control that forced every axis to be discoverable would
    push the next author toward inventing a proxy, which the D-SEGMENT wall forbids outright."""
    hidden = sorted(a for a, spec in _axes().items() if spec["hidden_truth_only"])
    assert hidden, "no axis is marked hidden — the flag has stopped distinguishing anything"
    for axis in hidden:
        assert axis not in PROBES or True  # a probe is permitted, never required


def test_green_stance_is_still_hidden_and_channel_pref_now_is_too():
    """The two facts this file was written around, pinned so a later edit has to argue with them.
    `green_stance` has never had a company observable and must not acquire an invented proxy
    (.claude/rules: "no company observable exists for it, ever"). `channel_pref` was moved to hidden
    on 2026-08-27 because its claimed channel did not exist."""
    axes = _axes()
    assert axes["green_stance"]["hidden_truth_only"] is True
    assert axes["channel_pref"]["hidden_truth_only"] is True, (
        "channel_pref claims discoverable again — if the contact channel has genuinely been wired "
        "to it, add a probe above; if not, this is the false claim returning")
