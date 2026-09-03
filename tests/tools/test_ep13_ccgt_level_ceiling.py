"""R15 for `tools/ep13_ccgt_level_ceiling.py` — every test names the defect it exists to catch.

THE DANGER THIS INSTRUMENT HAS is the one its whole reason for existing is about. §15's `ccgt_level`
rung reported +0.116 and could not be quoted, because it moved the daily gas total without
re-deciding the residual and part of what it reported was that disturbance. **An instrument built to
repair that defect, which itself fails to conserve, would report the identical unattributable number
under a name that claims otherwise** — and it would look like progress.
`test_the_balanced_rung_CONSERVES_the_energy_the_shipped_stack_SERVED` and its complement
`test_the_unbalanced_rung_DOES_NOT_conserve_and_that_is_why_it_is_kept` are the load-bearing pair:
one shows the repair works, the other shows there was something to repair. Either alone is half a
claim.

THE SECOND DANGER IS THE ANCHOR ITSELF, and the first draft of the module had it wrong.
`test_the_anchor_is_what_the_stack_SERVED_and_NOT_the_thermal_residual` pins the correction: the
shipped model does NOT satisfy `gas + coal + peaker == thermal_mw`, so a control keyed to that would
have gone red for the world rather than for the instrument, in every high-demand half hour.

THE THIRD IS SHARED WITH EVERY EP13 BOUND: this file re-implements a shipped function, so a copy
that has drifted would silently measure a second model and attribute the difference to the
substitution.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sim import grid_carbon_intensity as gci
from tools import ep13_ccgt_level_ceiling as lvl

PROJECT_DIR = Path(__file__).resolve().parents[2]


# --- the inputs the shipped dispatch is exercised over -----------------------------------------
# A GRID ACROSS THE REAL RANGE rather than one comfortable half hour, because two plausible and
# wrong drafts of a formula in this project were caught by printing a table across the range and
# neither would have been caught by a single point. The high-demand/low-renewable corner is
# deliberately included: it is the one where the shipped stack cannot meet its own residual, and it
# is what refuted this module's first conservation anchor.
DISPATCHES = [
    dict(demand_mw=d, renewable_generation_mw=r, year=y, import_mw=i, import_rate_t_per_mwh=0.2,
         coal_capacity_mw=c, thermal_floor_mw=3000.0, zero_carbon_must_run_mw=z,
         biomass_capacity_mw=2600.0, biomass_floor_mw=900.0)
    for d in (18000.0, 30000.0, 45000.0, 55000.0)
    for r in (500.0, 12000.0, 26000.0)
    for y in (2019, 2022, 2024)
    for i in (0.0, 4000.0)
    for c in (0.0, 6000.0)
    for z in (None, 5200.0, 7000.0)
]


def _row(
    *,
    balanced: float = 0.12,
    unbalanced: float = 0.20,
    identity: float = 0.0,
    shuffled: float = -0.20,
    balance_balanced: float = 0.0,
    balance_unbalanced: float = 900.0,
    distance: float = 700.0,
    bound_share: float = 0.02,
) -> dict:
    """A published row with every control passing, so a test can move ONE field and read the effect.

    Built here rather than from the artefact on purpose: a fixture read off the real run would make
    every control below a restatement of today's answer, which is the shape this project keeps
    catching (a control keyed to the current state goes red when the code becomes more honest).
    """
    return {
        "gain_over_baseline": {
            "level_balanced": balanced,
            "level_unbalanced": unbalanced,
            "level_identity": identity,
            "level_shuffled": shuffled,
        },
        "control_max_abs_balance_mw": {
            "baseline": 0.0,
            "level_balanced": balance_balanced,
            "level_unbalanced": balance_unbalanced,
        },
        "control_substitution_distance_mw": distance,
        "control_bound_share": bound_share,
    }


def test_the_reimplementation_reproduces_the_shipped_dispatch_EXACTLY() -> None:
    """DEFECT: the copy of `emissions_rate_t_per_mwh` drifts from the original.

    Then every rung in the artefact is a second model scored against NESO, and the gain attributed
    to substituting the gas level is partly the drift. Bit-equality rather than a tolerance: it is
    the same arithmetic on the same inputs, so anything but zero is a difference in the code.

    BOTH MODES ARE CHECKED. With no override the balanced and unbalanced paths must be the same
    function, or the comparison between the two rungs would carry a baseline difference.
    """
    for kwargs in DISPATCHES:
        theirs = gci.emissions_rate_t_per_mwh(**kwargs)
        for balanced in (True, False):
            mine, _implied, balance, caps = lvl.dispatch_rate(**kwargs, balanced=balanced)
            assert mine == theirs, (kwargs, balanced)
            assert balance == 0.0, "no override was passed, so nothing can move the energy served"
            assert not caps["clamped_low"] and not caps["clamped_high"]
            assert not caps["capped_to_served"]


def test_the_balanced_rung_CONSERVES_the_energy_the_shipped_stack_SERVED() -> None:
    """DEFECT: the repair does not repair — the balanced rung moves the daily gas total and the
    energy still vanishes, so it reports §15's unattributable number under a name that says
    otherwise.

    This is the whole point of the pass. Substituting a gas level DOWNWARD must leave
    `gas + coal + peaker` exactly where the shipped stack left it, with the difference taken up by
    the next units in the shipped merit order. An identity, not a tolerance.
    """
    moved = 0
    for kwargs in DISPATCHES:
        _rate, implied, _b, _c = lvl.dispatch_rate(**kwargs)
        for factor in (0.80, 0.94, 0.99):
            override = implied * factor
            _r, _i, balance, caps = lvl.dispatch_rate(
                **kwargs, ccgt_mw_override=override, balanced=True
            )
            # A CAP BINDING IS A DECLARED LIMIT, NOT A PASS. Either the rung conserved, or it said
            # plainly that it could not -- and there is no third branch where it quietly did
            # neither. `unservable` is what a 20% cut reaches when coal capacity plus the peaker
            # headroom runs out; on the real population it never fires, which is why the fixture
            # has to go this far to exercise it.
            if caps["capped_to_served"] or caps["unservable"]:
                continue
            assert abs(balance) <= lvl.MAX_BALANCE_RESIDUAL_MW, (kwargs, factor, balance)
            if implied > 0.0:
                moved += 1
    assert moved > 0, "the fixture never actually moved the gas level, so nothing was tested"


def test_a_cut_the_stack_CANNOT_ABSORB_is_declared_and_not_quietly_reported() -> None:
    """DEFECT: the balanced rung silently fails to conserve when the peakers run out.

    Pushing gas down far enough exhausts coal capacity plus the 7,000 MW peaker headroom, and the
    shortfall is then unservable — so the rung does NOT conserve in that half hour. A caller that
    could not see it would read a genuine imbalance as a clean measurement, which is precisely the
    defect this whole pass exists to remove, reappearing one layer down.

    THE FLAG AND THE IMBALANCE MUST AGREE. A flag that fires without an imbalance, or an imbalance
    without a flag, are both fail-open.
    """
    kwargs = dict(demand_mw=45000.0, renewable_generation_mw=500.0, year=2019, coal_capacity_mw=0.0)
    _rate, implied, _b, _c = lvl.dispatch_rate(**kwargs)

    _r, _i, balance, caps = lvl.dispatch_rate(
        **kwargs, ccgt_mw_override=implied * 0.5, balanced=True
    )
    assert caps["unservable"], "a cut the stack cannot absorb must be DECLARED"
    assert balance < -lvl.MAX_BALANCE_RESIDUAL_MW, "the flag must correspond to a real imbalance"

    _r, _i, small, small_caps = lvl.dispatch_rate(
        **kwargs, ccgt_mw_override=implied - 500.0, balanced=True
    )
    assert not small_caps["unservable"], "a cut well inside the headroom must NOT be flagged"
    assert abs(small) <= lvl.MAX_BALANCE_RESIDUAL_MW


def test_the_unbalanced_rung_DOES_NOT_conserve_and_that_is_why_it_is_kept() -> None:
    """DEFECT: §15's arithmetic conserved energy all along, the +0.116 was a bound, and this whole
    pass repaired nothing.

    That is a real possible world and it is refused HERE, on the arithmetic, rather than asserted in
    a docstring. The unbalanced rung leaves coal and the peakers decided from the fleet CAPACITY, so
    they do not move when gas does and the imbalance is exactly the gas the override added or
    removed. If this test ever passes trivially, the two rungs are the same rung and every
    `disturbance` figure in the artefact is zero by construction.
    """
    witnessed = 0
    for kwargs in DISPATCHES:
        _rate, implied, _b, _c = lvl.dispatch_rate(**kwargs)
        if implied <= 0.0:
            continue
        override = implied * 0.90
        _r, _i, balance, _caps = lvl.dispatch_rate(
            **kwargs, ccgt_mw_override=override, balanced=False
        )
        assert balance == pytest.approx(override - implied), kwargs
        assert abs(balance) > lvl.MAX_BALANCE_RESIDUAL_MW
        witnessed += 1
    assert witnessed > 0, "no fixture dispatched any gas, so the defect was never exercised"


def test_the_anchor_is_what_the_stack_SERVED_and_NOT_the_thermal_residual() -> None:
    """DEFECT: conservation is keyed to `thermal_mw`, which the SHIPPED model already violates.

    THE FIRST DRAFT OF THIS MODULE DID EXACTLY THAT and a smoke test at real inputs refuted it
    before a single rung was scored. Whenever the residual exceeds the CCGT fleet plus the peaker
    headroom the shipped stack truncates and serves LESS than it demanded — so a control keyed to
    `thermal_mw` would report the shipped model's truncation as this substitution's imbalance, in
    every high-demand half hour, and go red for the world rather than for the instrument.

    The corner is pinned with a concrete case, and both halves are asserted: the truncation is real
    and non-zero, AND the balanced rung still conserves against the right anchor.
    """
    kwargs = dict(demand_mw=55000.0, renewable_generation_mw=500.0, year=2024, coal_capacity_mw=0.0)
    _rate, implied, balance, caps = lvl.dispatch_rate(**kwargs)

    assert caps["baseline_unserved_mw"] > 0.0, (
        "the fixture no longer reaches the corner where the shipped stack truncates its own "
        "residual, so this test has stopped testing the thing it names"
    )
    assert balance == 0.0, "the baseline conserves against what it SERVED, by construction"

    assert caps["baseline_unserved_mw"] > 1000.0, (
        "the corner must be a LARGE truncation, or this test would pass on rounding and the "
        "wrong-anchor defect could hide inside the tolerance"
    )

    # AND THE TWO PROPERTIES ARE LINKED, WHICH IS WORTH PINNING RATHER THAN REDISCOVERING. The
    # shipped stack truncates only when the peakers are already at their cap -- so in exactly the
    # corner where the wrong anchor would have manufactured a 9,300 MW imbalance, the balanced rung
    # has no headroom in EITHER direction and says so. Declared, not silently reported.
    _r, _i, cut_balance, cut_caps = lvl.dispatch_rate(
        **kwargs, ccgt_mw_override=implied - 500.0, balanced=True
    )
    assert cut_caps["unservable"], (
        "where the shipped model truncates, the peakers are maxed and ANY cut is unservable -- the "
        "instrument must declare that rather than report a clean balance"
    )
    assert cut_caps["baseline_unserved_mw"] == pytest.approx(caps["baseline_unserved_mw"]), (
        "the shipped truncation is a property of the baseline and must not move with the override"
    )


def test_substituting_the_models_OWN_level_changes_NOTHING() -> None:
    """DEFECT: the override path does something extra on the way through.

    Then every gain in the artefact is partly the machinery rather than the information, and the
    instrument would report headroom when handed the model's own answer. Bit-equality: the same
    number through the same arithmetic.
    """
    for kwargs in DISPATCHES:
        baseline, implied, _b, _c = lvl.dispatch_rate(**kwargs)
        swapped, _i, balance, caps = lvl.dispatch_rate(**kwargs, ccgt_mw_override=implied)
        assert swapped == baseline, kwargs
        assert balance == 0.0
        assert not caps["capped_to_served"]


def test_raising_gas_above_what_the_stack_SERVED_is_capped_and_COUNTED() -> None:
    """DEFECT: the instrument manufactures energy when truth's gas level is above the model's.

    The ceiling is ASYMMETRIC and a reader must be able to see it: gas can only be raised as far as
    coal and the peakers were actually running, so where the residual sits below the CCGT fleet the
    upward headroom is zero. Silently letting gas exceed the served total would invent generation
    and flatter every year where the model runs LOW on gas — which §15 measured as 13% in 2019.

    THE CAP MUST BE COUNTED, NOT JUST APPLIED. A cap that binds without being reported is a rung
    partly measuring the cap while reading as a clean measurement.
    """
    kwargs = dict(demand_mw=26000.0, renewable_generation_mw=6000.0, year=2024, coal_capacity_mw=0.0)
    baseline, implied, _b, _c = lvl.dispatch_rate(**kwargs)
    assert implied > 0.0

    rate, _i, balance, caps = lvl.dispatch_rate(
        **kwargs, ccgt_mw_override=implied * 1.5, balanced=True
    )
    assert caps["capped_to_served"], "gas above the served total must be capped and flagged"
    assert abs(balance) <= lvl.MAX_BALANCE_RESIDUAL_MW, "the cap must restore the balance, not break it"
    assert rate == baseline, "capped to the served total IS the baseline dispatch"


def test_a_half_hour_with_NO_GAS_READING_is_refused_and_not_dispatched_as_zero() -> None:
    """DEFECT: an absent override falls back to the model's own gas.

    §14's fail-open shape, one layer over. A half hour with no CCGT row is not a half hour with no
    gas; it is no reading. Falling back would mix baseline half hours into a swap rung and dilute
    the very gain being measured, and the dilution would look like a modest honest result.
    """
    demand = {("2024-01-02", 1): 30000.0, ("2024-01-02", 2): 31000.0}
    wind = {("2024-01-02", 1): 5000.0, ("2024-01-02", 2): 5000.0}

    rates, implied, _balance, _caps, _bound = lvl.build_rates(demand, wind)
    assert set(rates) == set(demand), "with no override every half hour is dispatched"

    partial = {("2024-01-02", 1): float(implied[("2024-01-02", 1)])}
    rates, _i, _b, _c, _bd = lvl.build_rates(demand, wind, ccgt_override_by_period=partial)
    assert set(rates) == {("2024-01-02", 1)}, (
        "the half hour with no override must be REFUSED, not dispatched with the model's own gas"
    )


def test_the_null_deals_DAY_LEVELS_to_other_days_and_keeps_every_value() -> None:
    """DEFECT: the null destroys something other than the day a level belongs to.

    A null that also changes the values, or the coverage, is not a null — it would collapse for a
    reason that has nothing to do with the information being tested, and the discrimination control
    would then pass on that irrelevance.
    """
    implied = {
        (f"2024-01-{d:02d}", p): 8000.0 + 100.0 * p for d in (2, 4, 6, 8) for p in range(1, 5)
    }
    truth = {
        (f"2024-01-{d:02d}", p): 5000.0 + 900.0 * d + 10.0 * p
        for d in (2, 4, 6, 8)
        for p in range(1, 5)
    }
    shuffled = lvl.shuffled_day_levels(implied, truth)
    straight = lvl.level_swap(implied, truth)

    assert set(shuffled) == set(straight), "the null must cover exactly the same half hours"
    assert sorted(round(v, 9) for v in shuffled.values()) == sorted(
        round(v, 9) for v in straight.values()
    ), "the null must be a re-dealing of the same values, not different values"
    assert shuffled != straight, "the fixture's day levels are all equal, so nothing was scrambled"


def test_the_null_control_does_not_refuse_the_instrument_for_WORKING() -> None:
    """DEFECT: the null is keyed to a guessed answer rather than to what a null owes.

    §15's FIRST DRAFT DID THIS and went RED against a sound instrument. It asked for
    `abs(gain) < 0.01` — "the null collapses to nothing" — but scrambled input is not absent input:
    it replaces the model's own level with a WRONG level and MUST hurt. Measured on the timing axis
    it cost 0.22 to 0.31, and requiring that to be small refuses the instrument for behaving
    correctly. What a null owes is that it does not FLATTER.

    Carried forward here rather than re-learned, and pinned so a later pass cannot "tidy" it back.
    """
    hurting = lvl.verdicts(_row(shuffled=-0.28))
    assert hurting["the_null_does_not_gain"], (
        "a null that HURTS is a null doing its job and must not be read as a failure"
    )
    assert hurting["correct_levels_beat_scrambled_levels"]

    flattering = lvl.verdicts(_row(shuffled=+0.05))
    assert not flattering["the_null_does_not_gain"], (
        "a null that GAINS means the machinery is talking, and must be refused"
    )


def test_the_discrimination_control_fires_when_SCRAMBLED_LEVELS_SCORE_THE_SAME() -> None:
    """DEFECT: an instrument that reports one constant whatever it is handed passes the null.

    "Did not gain" alone is satisfied by a rung that cannot move. Correct day levels must clear
    scrambled ones by a material margin, or these rungs are not measuring the level at all.
    """
    # BOTH NUMBERS SIT BELOW THE MATERIAL BAR ON PURPOSE, so the null leg genuinely PASSES and the
    # discrimination leg is the only thing left to catch this. A fixture whose null gain cleared the
    # bar would be refused by the null leg first, and this test would pass without ever exercising
    # the leg it names.
    dead = _row(balanced=0.009, shuffled=0.005)
    verdict = lvl.verdicts(dead)
    assert verdict["the_null_does_not_gain"], "the null still does not FLATTER, which is the trap"
    assert not verdict["correct_levels_beat_scrambled_levels"], (
        "correct and scrambled levels scoring the same must be refused by the discrimination leg"
    )


def test_the_identity_control_FIRES_when_the_machinery_itself_gains() -> None:
    """DEFECT: the soundness check is decorative and passes whatever the identity rung reports.

    The identity rung is algebraically the model's own series. If it gains, the artefact's every
    number is void — so this control has to be able to say so.
    """
    assert lvl.verdicts(_row(identity=0.0))["substituting_the_models_own_level_changes_nothing"]
    assert not lvl.verdicts(_row(identity=0.04))[
        "substituting_the_models_own_level_changes_nothing"
    ]
    assert not lvl.verdicts(_row(identity=-0.04))[
        "substituting_the_models_own_level_changes_nothing"
    ], "a NEGATIVE identity gain is just as much a broken machine as a positive one"


def test_the_conservation_controls_FIRE_on_both_limbs() -> None:
    """DEFECT: the conservation verdict is a restatement rather than a test.

    Both limbs must be able to fail, and they fail for opposite reasons. If the balanced rung stops
    conserving, the repair did not work. If the unbalanced rung starts conserving, there was nothing
    to repair and this pass has no subject — which would mean §15's +0.116 was quotable all along.
    """
    good = lvl.verdicts(_row())
    assert good["the_balanced_rung_conserves_energy"]
    assert good["the_unbalanced_rung_does_NOT_conserve_energy"]

    assert not lvl.verdicts(_row(balance_balanced=250.0))["the_balanced_rung_conserves_energy"]
    assert not lvl.verdicts(_row(balance_unbalanced=0.0))[
        "the_unbalanced_rung_does_NOT_conserve_energy"
    ]


def test_the_bound_share_COUNTS_the_cap_that_actually_binds() -> None:
    """DEFECT: the cap-share control does not count `capped_to_served`, the dominant cap.

    THE FIRST DRAFT OF THIS MODULE HAD EXACTLY THIS and it was fail-open in the worst possible
    place. It counted only the fleet clamps and a non-zero balance, read **0.000-0.050**, and passed
    every year — while `capped_to_served` was binding on **117,510** half hours run-wide against the
    clamps' 1,293. Corrected, the share is 0.531-0.852 and the control is RED in all six years.

    A control that exists to refuse a rung its caps are carrying, and that does not count the cap
    carrying it, reports a clean measurement of a rung pinned to its own baseline. This test walks
    the real dispatch rather than a fixture, because the defect was in which caps reached the share.
    """
    demand = {("2024-01-02", p): 26000.0 for p in range(1, 5)}
    wind = {("2024-01-02", p): 6000.0 for p in range(1, 5)}
    _r, implied, _b, _c, _bd = lvl.build_rates(demand, wind)

    # Every half hour asks for MORE gas than the shipped stack served -- so `capped_to_served` binds
    # everywhere, and no fleet clamp does: the values sit well inside [0, CCGT_CAPACITY_MW].
    override = {k: v * 1.2 for k, v in implied.items()}
    _r, _i, balance, caps, bound = lvl.build_rates(
        demand, wind, ccgt_override_by_period=override, balanced=True
    )
    assert caps["capped_to_served"] == len(demand), "the fixture must actually trip that cap"
    assert caps["clamped_low"] == 0 and caps["clamped_high"] == 0, (
        "no fleet clamp may fire here, or this test would pass through the cap it is not about"
    )
    assert all(abs(v) <= lvl.MAX_BALANCE_RESIDUAL_MW for v in balance.values()), (
        "the cap restores the balance, which is exactly why a balance-only share cannot see it"
    )
    assert all(bound.values()), (
        "every half hour is cap-bound and the per-key view must say so -- a share computed from "
        "the fleet clamps and the balance alone would report 0.0 here"
    )


def test_the_cap_control_fires_when_THE_CAPS_ARE_CARRYING_THE_RUNG() -> None:
    """DEFECT: a year whose caps bind constantly is published as a measurement of the gas level.

    The ceiling is asymmetric — gas can only be raised as far as dirtier plant was running — so a
    year where the model runs LOW on gas caps almost everywhere and the rung is then measuring the
    cap. Past `MAX_BOUND_SHARE` its reading is REFUSED rather than footnoted.
    """
    assert lvl.verdicts(_row(bound_share=0.10))["the_caps_are_not_carrying_the_rung"]
    assert not lvl.verdicts(_row(bound_share=lvl.MAX_BOUND_SHARE + 0.01))[
        "the_caps_are_not_carrying_the_rung"
    ]


def test_the_substitution_distance_control_fires_when_NOTHING_WAS_SUBSTITUTED() -> None:
    """DEFECT: a zero gain is published as "the level is worth nothing".

    If truth's day levels were near-identical to the model's own, a zero gain would be equally
    consistent with "the level carries nothing" and with "the substitution was a no-op" — a control
    whose PASS branch is unreachable. This is the one a reader should check before any gain.
    """
    assert lvl.verdicts(_row(distance=700.0))["the_substituted_levels_are_not_the_models_own"]
    assert not lvl.verdicts(_row(distance=lvl.MIN_SUBSTITUTION_DISTANCE_MW - 1.0))[
        "the_substituted_levels_are_not_the_models_own"
    ]


def test_the_metered_gas_series_CANNOT_REACH_the_published_feed() -> None:
    """DEFECT: the half-hourly metered gas series leaks into what the site publishes.

    Then the reconstruction is NESO's arithmetic with a different cache, the coupled-triad gap
    measures nothing while still producing a number, and the epistemic wall is crossed by an import.
    An AST WALK rather than a substring search, for §15's reason: a doc comment that MENTIONS this
    module without importing it is exactly what a later pass writes next to the feed, and a
    substring search would call that a leak and get the pointer deleted.
    """
    assert lvl.ceiling_is_unreachable_from(lvl._published_feed_source()), (
        "the published feed imports this module — the metered gas series now reaches the site"
    )
    assert lvl.ceiling_is_unreachable_from(
        "# see tools.ep13_ccgt_level_ceiling for the bound\n"
        "'ep13_ccgt_level_ceiling'\n"
    ), "a MENTION is not an import, and treating it as one would delete a pointer a reader needs"
    assert not lvl.ceiling_is_unreachable_from("from tools import ep13_ccgt_level_ceiling")
    assert not lvl.ceiling_is_unreachable_from("import tools.ep13_ccgt_level_ceiling")


@pytest.mark.skipif(
    not (PROJECT_DIR / "docs" / "observability" / "ep13_ccgt_level_ceiling.json").exists(),
    reason="the artefact has not been generated in this tree",
)
def test_the_published_artefact_carries_its_controls_and_its_reimplementation_verdict() -> None:
    """DEFECT: the artefact publishes gains with no way for a reader to see what they rest on.

    A verdict that lives only in another process is one a reader has to take on trust. THE KEY IS
    ASSERTED AND THE VALUE IS ONLY SKIPPED ON, deliberately: a `skip` keyed to the value would
    swallow the exact mutation this control exists to catch.
    """
    artefact = json.loads(
        (PROJECT_DIR / "docs" / "observability" / "ep13_ccgt_level_ceiling.json").read_text(
            encoding="utf-8"
        )
    )
    assert "reimplementation_reproduces_the_shipped_shape" in artefact
    assert "conservation_anchor" in artefact
    assert artefact["ceiling_reaches_the_published_feed"] is False
    assert artefact["years"], "an artefact with no years scored is not a measurement"

    for year, row in artefact["years"].items():
        controls = row["controls"]
        for name in (
            "the_balanced_rung_conserves_energy",
            "the_unbalanced_rung_does_NOT_conserve_energy",
            "substituting_the_models_own_level_changes_nothing",
            "the_null_does_not_gain",
            "the_caps_are_not_carrying_the_rung",
        ):
            assert name in controls, f"{year} is missing control {name}"
        assert "level_balanced" in row["gain_over_baseline"], year
        assert "level_unbalanced" in row["gain_over_baseline"], year
