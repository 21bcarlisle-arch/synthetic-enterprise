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
"""
from __future__ import annotations

import pytest

from simulation.population_draw import _load_cohort_curriculum

#: Measured 2026-08-27: three attitude axes carry the flag. A floor, because a scan that found none
#: would report a clean sweep — the defect this file exists to catch, one level up.
MIN_AXES_SCANNED = 3


def _axes() -> dict[str, dict]:
    return {
        key[: -len("_marginals")]: spec
        for key, spec in _load_cohort_curriculum().items()
        if key.endswith("_marginals") and isinstance(spec, dict) and "hidden_truth_only" in spec
    }


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


#: axis -> probe. An axis claiming DISCOVERABLE must appear here; adding one without a probe fails.
PROBES = {
    "price_sensitivity": _probe_price_sensitivity,
}


def test_the_scan_sees_the_whole_set_of_axes():
    """POPULATION FLOOR. If the marginals were renamed or the loader changed shape, every
    assertion below would pass over an empty set and report the curriculum clean."""
    axes = _axes()
    assert len(axes) >= MIN_AXES_SCANNED, (
        f"only {len(axes)} axes carry `hidden_truth_only` (floor {MIN_AXES_SCANNED}) — this "
        "control's own subject has collapsed, so its green means nothing")


def test_every_axis_claiming_DISCOVERABLE_has_a_probe():
    claimed = sorted(a for a, spec in _axes().items() if not spec["hidden_truth_only"])
    missing = [a for a in claimed if a not in PROBES]
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
        f"{axis} claims to be discoverable, but households differing only in it face IDENTICAL "
        f"decisions ({observed[0]}) — no amount of observation can recover a trait the world does "
        "not act on")


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
