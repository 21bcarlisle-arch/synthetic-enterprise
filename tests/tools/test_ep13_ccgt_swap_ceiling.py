"""R15 for `tools/ep13_ccgt_swap_ceiling.py` — every test names the defect it exists to catch.

THE DANGER THIS INSTRUMENT HAS, and it is the same one `ep13_per_fuel_oracle_bound` named: it
reports a POSITIVE, so the failure mode is an instrument that says "there is headroom" whatever it
is handed. `test_the_instrument_reports_NO_gain_when_THE_MODEL_ALREADY_HAS_THE_TIMING` is the
load-bearing one and it is the inverse of the four negative bounds' load-bearing tests.

THE SECOND DANGER IS PECULIAR TO THIS FILE: it re-implements a shipped function, so a copy that has
drifted would silently measure a second model and attribute the difference to the substitution.
`test_the_reimplementation_reproduces_the_shipped_dispatch_EXACTLY` is what stands between the
artefact and that, and it is checked on the real dispatch rather than on a fixture.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sim import grid_carbon_intensity as gci
from tools import ep13_ccgt_swap_ceiling as swap

PROJECT_DIR = Path(__file__).resolve().parents[2]


# --- the inputs the shipped dispatch is exercised over -----------------------------------------
# A GRID ACROSS THE REAL RANGE rather than one comfortable half hour, because two plausible and
# wrong drafts of a formula in this project were caught by printing a table across the range and
# neither would have been caught by a single point.
DISPATCHES = [
    dict(demand_mw=d, renewable_generation_mw=r, year=y, import_mw=i, import_rate_t_per_mwh=0.2,
         coal_capacity_mw=c, thermal_floor_mw=3000.0, zero_carbon_must_run_mw=z,
         biomass_capacity_mw=2600.0, biomass_floor_mw=900.0)
    for d in (18000.0, 30000.0, 45000.0)
    for r in (500.0, 12000.0, 26000.0)
    for y in (2019, 2022, 2024)
    for i in (0.0, 4000.0)
    for c in (0.0, 6000.0)
    for z in (None, 5200.0, 7000.0)
]


def test_the_reimplementation_reproduces_the_shipped_dispatch_EXACTLY() -> None:
    """DEFECT: the copy of `emissions_rate_t_per_mwh` drifts from the original.

    Then every rung in the artefact is a second model scored against NESO, and the gain attributed
    to substituting gas is partly the drift. Bit-equality rather than a tolerance: it is the same
    arithmetic on the same inputs, so anything but zero is a difference in the code.
    """
    for kwargs in DISPATCHES:
        mine, _implied, low, high = swap.dispatch_rate(**kwargs)
        theirs = gci.emissions_rate_t_per_mwh(**kwargs)
        assert mine == theirs, kwargs
        assert not low and not high, "no override was passed, so nothing can clamp"


def test_substituting_the_models_OWN_gas_changes_NOTHING() -> None:
    """DEFECT: the override path does something extra on the way through.

    A rung is a difference between two runs of this function, so an override path that perturbs
    anything beyond the gas term puts that perturbation into every gain. Handing back the model's
    own answer is the identity, and it must be exactly the identity.
    """
    for kwargs in DISPATCHES:
        baseline, implied, _, _ = swap.dispatch_rate(**kwargs)
        echoed, _, low, high = swap.dispatch_rate(**kwargs, ccgt_mw_override=implied)
        assert echoed == baseline, kwargs
        assert not low and not high


def test_the_override_moves_the_GAS_TERM_AND_NOTHING_ELSE() -> None:
    """DEFECT: the substitution re-decides the merit order around the new gas figure.

    Then it is two variables again -- gas AND the coal/peaker split -- which is the exact defect
    this whole instrument exists to repair one layer up. Checked where it would show: a dispatch
    deep enough to put plant above the CCGT band, so coal and the peakers are both carrying MW.
    """
    kwargs = dict(demand_mw=45000.0, renewable_generation_mw=500.0, year=2019, import_mw=0.0,
                  import_rate_t_per_mwh=0.0, coal_capacity_mw=6000.0, thermal_floor_mw=3000.0,
                  zero_carbon_must_run_mw=5200.0, biomass_capacity_mw=2600.0,
                  biomass_floor_mw=900.0)
    base, implied, _, _ = swap.dispatch_rate(**kwargs)
    assert implied == gci.CCGT_CAPACITY_MW, "the fixture must load the CCGT band to its top"

    lowered, _, _, _ = swap.dispatch_rate(**kwargs, ccgt_mw_override=implied - 5000.0)
    worst, best = gci._ccgt_efficiency_band(2019)

    def gas_tonnes(mw: float) -> float:
        fraction = mw / gci.CCGT_CAPACITY_MW
        return mw * (gci.EF_GAS_TCO2_PER_MWH_TH / (best - (best - worst) * fraction / 2.0))

    expected = (gas_tonnes(implied - 5000.0) - gas_tonnes(implied)) / kwargs["demand_mw"]
    assert lowered - base == pytest.approx(expected, rel=1e-12)


def test_a_half_hour_with_NO_GAS_READING_is_refused_and_not_dispatched_as_zero() -> None:
    """DEFECT: an absent override falls back to the model's own gas, or to zero.

    Falling back to the model's own gas silently mixes baseline half hours into a swap rung and
    dilutes the very gain being measured. Falling back to ZERO is worse and is §14's own first
    draft: no CCGT row is not no gas, it is no reading, and dispatching it as zero deletes the
    largest carbon term on the system and reports a clean grid.
    """
    demand = {("2024-01-02", p): 30000.0 for p in range(1, 9)}
    wind = {k: 8000.0 for k in demand}
    override = {k: 6000.0 for k in list(demand)[:4]}  # the other four have no reading

    rates, _implied, _clamps = swap.build_rates(demand, wind, ccgt_override_by_period=override)
    assert set(rates) == set(override), "a half hour with no gas reading must not be scored"

    baseline, _, _ = swap.build_rates(demand, wind)
    assert set(baseline) == set(demand), "with no override map at all, nothing is refused"


def test_the_timing_swap_preserves_the_models_own_DAY_MEAN() -> None:
    """DEFECT: the primary rung leaks the level it was built to hold constant.

    `ccgt_timing` is the only rung read as a CEILING, and it earns that by being day-total
    preserving -- the half hour is still met by the same energy. A multiplicative rescale, or an
    additive one taken against the wrong day, moves the level too and the rung becomes `ccgt_full`
    wearing the ceiling's name.
    """
    keys = [("2024-01-02", p) for p in range(1, 49)] + [("2024-01-04", p) for p in range(1, 49)]
    implied = {k: 9000.0 + 40.0 * k[1] for k in keys}
    truth = {k: 5000.0 + 300.0 * ((k[1] * 7) % 11) for k in keys}

    swapped = swap.timing_swap(implied, truth)
    for day in ("2024-01-02", "2024-01-04"):
        mine = [swapped[k] for k in swapped if k[0] == day]
        theirs = [implied[k] for k in implied if k[0] == day]
        assert sum(mine) / len(mine) == pytest.approx(sum(theirs) / len(theirs), rel=1e-12)

    # ...and it carries TRUTH's within-day deviations, or it has preserved the level by preserving
    # the whole series and substituted nothing at all.
    truth_day = swap.day_mean(truth)
    implied_day = swap.day_mean(implied)
    for key in swapped:
        assert swapped[key] - implied_day[key] == pytest.approx(truth[key] - truth_day[key])


def test_the_level_swap_is_the_EXACT_COMPLEMENT_of_the_timing_swap() -> None:
    """DEFECT: the two decomposition rungs overlap, so their numbers double-count.

    The pair is what lets the artefact say "the level is worth 2.4x the timing" rather than "the
    timing is worth this and the rest is a residual". If `ccgt_level` kept any of truth's within-day
    shape, that sentence would be counting the same information twice.
    """
    keys = [("2024-03-02", p) for p in range(1, 49)]
    implied = {k: 9000.0 + 40.0 * k[1] for k in keys}
    truth = {k: 5000.0 + 300.0 * ((k[1] * 7) % 11) for k in keys}

    level = swap.level_swap(implied, truth)
    implied_day, truth_day = swap.day_mean(implied), swap.day_mean(truth)
    for key in level:
        assert level[key] - truth_day[key] == pytest.approx(implied[key] - implied_day[key])
    mine = list(level.values())
    assert sum(mine) / len(mine) == pytest.approx(
        sum(truth.values()) / len(truth), rel=1e-12
    )


def test_the_null_deals_profiles_to_OTHER_days_and_keeps_every_value() -> None:
    """DEFECT: the null is built by drawing new numbers rather than by re-dealing the real ones.

    A null made of fresh values tests the scale of the numbers; this axis needs a null that tests
    the TIMING, so the multiset of within-day deviations must survive the shuffle exactly and only
    the day each profile belongs to may change.
    """
    # THE DAY MUST ENTER THE PROFILE, not only its level, and the first draft of this fixture got
    # that wrong: with `300 * ((p * 7) % 11)` every day carries an IDENTICAL within-day profile, so
    # re-dealing the profiles is the identity and the leg below fails against correct code. A
    # mutation that does not fire is either a missing test or an equivalence -- that one was an
    # equivalence manufactured by the fixture.
    keys = [(f"2024-05-{d:02d}", p) for d in range(2, 20) for p in range(1, 49)]
    implied = {k: 9000.0 for k in keys}
    truth = {
        k: 5000.0 + 100.0 * int(k[0][-2:]) + 300.0 * ((k[1] * 7 + int(k[0][-2:])) % 11)
        for k in keys
    }

    truth_day = swap.day_mean(truth)
    original = sorted(round(truth[k] - truth_day[k], 9) for k in keys)
    nulled = swap.shuffled_days(implied, truth)
    dealt = sorted(round(nulled[k] - 9000.0, 9) for k in nulled)
    assert dealt == original, "the null must preserve every deviation, and move only its day"
    assert nulled != swap.timing_swap(implied, truth), "a shuffle that changes nothing is no null"


def test_the_instrument_reports_NO_gain_when_THE_MODEL_ALREADY_HAS_THE_TIMING() -> None:
    """DEFECT: the instrument reports headroom whatever it is handed. THE LOAD-BEARING TEST.

    This is the inverse of the four EP13 bounds that reported negatives, whose danger was an
    instrument that can only say "no headroom". This one reports a POSITIVE, so its danger is one
    that says "big headroom" against a model that already has the answer. Handed a truth series
    IDENTICAL to the model's own gas, the timing rung must gain nothing AND the distinctness
    control must go red -- a zero gain from an identical series is uninterpretable on its own.
    """
    keys = [(f"2024-07-{d:02d}", p) for d in range(2, 20) for p in range(1, 49)]
    implied = {k: 9000.0 + 250.0 * ((k[1] * 5) % 13) for k in keys}
    swapped = swap.timing_swap(implied, implied)
    assert all(swapped[k] == pytest.approx(implied[k]) for k in swapped)

    verdict = swap.verdicts(
        {
            "gain_over_baseline": {
                "ccgt_timing": 0.0,
                "ccgt_level": 0.0,
                "ccgt_timing_shuffled": 0.0,
            },
            "control_substitution_distance_mw": 0.0,
            "control_clamped_low_share": 0.0,
            "control_clamped_high_share": 0.0,
        }
    )
    assert verdict["the_substituted_series_is_not_the_models_own"] is False
    assert verdict["correct_timing_beats_scrambled_timing"] is False
    assert verdict["timing_clears_the_baseline"] is False


def test_the_null_control_does_not_refuse_the_instrument_for_WORKING() -> None:
    """DEFECT: the null control is keyed to a guessed answer instead of to the property.

    THE FIRST DRAFT HAD IT AND THE REAL RUN CAUGHT IT. It asked for `abs(shuffled gain) < 0.01` --
    "the null collapses to nothing" -- and scrambled timing does not sit at nothing: it replaces
    the model's own gas timing with wrong timing and MUST hurt, measured at -0.22 to -0.31. That
    control went red against a sound instrument, which is a control keyed to today's answer going
    red because the world behaved correctly. What a null owes is that it does not FLATTER.
    """
    strongly_negative = swap.verdicts(
        {
            "gain_over_baseline": {
                "ccgt_timing": 0.0485,
                "ccgt_level": 0.1162,
                "ccgt_timing_shuffled": -0.2192,
            },
            "control_substitution_distance_mw": 2903.0,
            "control_clamped_low_share": 0.008,
            "control_clamped_high_share": 0.0,
        }
    )
    assert strongly_negative["the_null_does_not_gain"] is True
    assert strongly_negative["correct_timing_beats_scrambled_timing"] is True

    flattering = swap.verdicts(
        {
            "gain_over_baseline": {
                "ccgt_timing": 0.05,
                "ccgt_level": 0.0,
                "ccgt_timing_shuffled": 0.04,
            },
            "control_substitution_distance_mw": 2903.0,
            "control_clamped_low_share": 0.0,
            "control_clamped_high_share": 0.0,
        }
    )
    assert flattering["the_null_does_not_gain"] is False, "a null that GAINS must refuse the run"


def test_the_discrimination_control_fires_when_SCRAMBLED_TIMING_SCORES_THE_SAME() -> None:
    """DEFECT: a null that cannot gain is satisfied by an instrument that reports one constant.

    "The null did not gain" is met by an instrument insensitive to everything, so it must be paired
    with a requirement that CORRECT timing beats scrambled timing by a margin. Without this leg the
    pair of controls has an unreachable failure branch.
    """
    identical = swap.verdicts(
        {
            "gain_over_baseline": {
                "ccgt_timing": -0.30,
                "ccgt_level": 0.0,
                "ccgt_timing_shuffled": -0.30,
            },
            "control_substitution_distance_mw": 2903.0,
            "control_clamped_low_share": 0.0,
            "control_clamped_high_share": 0.0,
        }
    )
    assert identical["the_null_does_not_gain"] is True, "it did not gain -- and it means nothing"
    assert identical["correct_timing_beats_scrambled_timing"] is False


def test_the_clamp_control_fires_when_THE_CLAMP_IS_CARRYING_THE_RUNG() -> None:
    """DEFECT: a rung whose substituted series is mostly pinned at a bound reads as a measurement.

    Truth's deviations added to a small modelled day mean go negative, and gas cannot be negative.
    Past a share of clamped half hours the rung is reporting the clamp, and the honest answer is a
    refusal rather than a footnote under a number.
    """
    row = {
        "gain_over_baseline": {"ccgt_timing": 0.05, "ccgt_level": 0.0, "ccgt_timing_shuffled": -0.2},
        "control_substitution_distance_mw": 2903.0,
        "control_clamped_low_share": 0.30,
        "control_clamped_high_share": 0.0,
    }
    assert swap.verdicts(row)["the_clamp_is_not_carrying_the_rung"] is False
    row["control_clamped_low_share"] = 0.008
    assert swap.verdicts(row)["the_clamp_is_not_carrying_the_rung"] is True


def test_the_metered_gas_series_CANNOT_REACH_the_published_feed() -> None:
    """DEFECT: the half-hourly metered gas series leaks into the series this world publishes.

    That is the line `sim/elexon_fuel_outturn.py` was written to draw -- a reconstruction that reads
    the metered mix is not a second route to NESO's number, it is NESO's arithmetic with a different
    cache. Checked by AST walk over the real feed, and the walk is checked against a source that
    DOES import this module so its pass branch is reachable.
    """
    assert swap.ceiling_is_unreachable_from(swap._published_feed_source()) is True
    assert swap.ceiling_is_unreachable_from("import tools.ep13_ccgt_swap_ceiling\n") is False
    assert swap.ceiling_is_unreachable_from(
        "from tools.ep13_ccgt_swap_ceiling import measure\n"
    ) is False
    assert swap.ceiling_is_unreachable_from("from tools import ep13_ccgt_swap_ceiling\n") is False

    # THE LEG THAT MAKES THIS A TEST OF THE WALK RATHER THAN OF THE NAME, added because the
    # mutation to a plain substring search SURVIVED every assertion above -- they are all real
    # imports, and a substring search agrees with the walk on all four. What separates them is a
    # source that MENTIONS this module without importing it, which is every doc comment that will
    # eventually be written next to the feed pointing at this instrument. A substring search calls
    # that a leak, the feed goes red for a sentence, and the cheapest repair is deleting the
    # sentence -- so the guard would end up suppressing the very pointer a reader needs.
    assert swap.ceiling_is_unreachable_from(
        "# the ceiling in tools/ep13_ccgt_swap_ceiling.py must never reach this feed\n"
        "import json\n"
    ) is True


def test_the_published_artefact_carries_its_controls_and_its_reimplementation_verdict() -> None:
    """DEFECT: the verdicts live only in this test process, so a reader has to take them on trust.

    Skipped rather than failed when the artefact has not been produced in this tree: this file is a
    control on the instrument, and turning it into a control on whether an 8-minute job has been run
    would make every unrelated lane's commit wait for it.
    """
    if not swap.OUT_PATH.exists():
        pytest.skip("artefact not produced in this tree; run `python3 -m tools.ep13_ccgt_swap_ceiling`")
    data = json.loads(swap.OUT_PATH.read_text(encoding="utf-8"))
    assert data["ceiling_reaches_the_published_feed"] is False
    assert data["reimplementation_reproduces_the_shipped_shape"] is True
    for year, row in data["years"].items():
        controls = row["controls"]
        assert controls["the_substituted_series_is_not_the_models_own"] is True, year
        assert controls["the_null_does_not_gain"] is True, year
        assert controls["correct_timing_beats_scrambled_timing"] is True, year
        assert controls["the_clamp_is_not_carrying_the_rung"] is True, year
        assert set(row["gain_over_baseline"]) == {
            "ccgt_timing",
            "ccgt_level",
            "ccgt_full",
            "ccgt_day_mean",
            "ccgt_timing_shuffled",
        }, year
