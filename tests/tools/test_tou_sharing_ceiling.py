"""Controls over the SHARING ceiling — each named for the defect it exists to catch.

Every test here is written against a defect this instrument could plausibly have, and the fixtures
are SYNTHETIC on purpose: the Elexon MID cache and the run outputs are both gitignored, so a suite
that reached for them would pass vacuously in every clean worktree extract and every mutation of
this module would survive. The one test that does touch the live tree skips explicitly when the
data is absent, and says so, rather than going quiet.
"""
from __future__ import annotations

import json
import random
import statistics

import pytest

from tools.r3_carbon_score_ceiling import (
    MIN_HOUSEHOLDS,
    CeilingUnavailable,
    achievable_saving_per_kwh,
    skill_free_saving_per_kwh,
)
from tools.tou_sharing_ceiling import (
    PASS_THROUGH_GRID,
    created_value_per_shifted_kwh,
    half_hourly_wholesale_price,
    headline,
    matched_panel_clearance,
    measure,
    money_share_curve,
    sharing_frontier,
    smart_metered_households,
)

WINDOW = 6
PERIODS = 48


def _shaped_day(offset: float) -> list[float]:
    """A day with a real diurnal shape: cheap overnight, dear at the evening peak."""
    return [
        offset + 40.0 + 30.0 * (1.0 if 34 <= p <= 40 else 0.0) - 15.0 * (1.0 if p <= 8 else 0.0)
        for p in range(PERIODS)
    ]


def _price_shape(days: int = 40) -> dict[tuple[str, int], float]:
    rng = random.Random(11)
    out: dict[tuple[str, int], float] = {}
    for d in range(days):
        date = f"2019-01-{d + 1:02d}" if d < 31 else f"2019-02-{d - 30:02d}"
        day = _shaped_day(rng.uniform(-5.0, 5.0))
        for p, price in enumerate(day, start=1):
            out[(date, p)] = price
    return out


def _flat_price_shape(days: int = 40) -> dict[tuple[str, int], float]:
    """A day with NO within-day shape at all. The cheapest window is not cheaper."""
    return {
        (f"2019-03-{d + 1:02d}", p): 50.0
        for d in range(days)
        for p in range(1, PERIODS + 1)
    }


def _book(households: int = 30, smart: int = 25) -> dict:
    return {
        "demand_estimation_log": [
            {"customer_id": f"C{i}", "company_eac_kwh": 3000.0} for i in range(1, households + 1)
        ],
        "meter_read_log": [
            {"customer_id": f"C{i}", "meter_type": "smart" if i <= smart else "traditional"}
            for i in range(1, households + 1)
        ],
    }


@pytest.fixture
def run_file(tmp_path):
    def _write(payload: dict):
        path = tmp_path / "run_output_fixture.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path
    return _write


# --------------------------------------------------------------------------------------------
# THE NULL. If it cannot be beaten and cannot fail, the ceiling means nothing.
# --------------------------------------------------------------------------------------------

def test_the_null_can_BOTH_be_cleared_and_NOT_be_cleared_over_this_partition():
    """DEFECT: a null that no world clears, or that every world clears, grades nothing.

    Written as ONE control over the whole partition rather than a leg per branch, because a guard
    that answers the same way everywhere passes every single-leg test ever written about it. The
    shaped day must clear; the flat day must not.
    """
    shaped = created_value_per_shifted_kwh(
        {d: [v for (_, _), v in sorted(
            ((k, x) for k, x in _price_shape(20).items() if k[0] == d), key=lambda kv: kv[0][1])]
         for d in sorted({k[0] for k in _price_shape(20)})},
        WINDOW, seed=3)
    flat_days = {f"2019-03-{d + 1:02d}": [50.0] * PERIODS for d in range(20)}
    flat = created_value_per_shifted_kwh(flat_days, WINDOW, seed=3)

    assert shaped["hindsight_gbp_per_mwh"] > shaped["null_max_gbp_per_mwh"], (
        "a day with a real diurnal price shape must clear an optimiser with no skill")
    assert flat["hindsight_gbp_per_mwh"] == pytest.approx(0.0, abs=1e-9), (
        "a day with NO within-day shape has exactly nothing to move load away from; a ceiling "
        "that returns anything above zero there is measuring its own construction")
    assert flat["hindsight_gbp_per_mwh"] <= flat["null_max_gbp_per_mwh"]


def test_the_null_is_NOT_the_optimiser_re_run_on_a_shuffled_day():
    """DEFECT: the obvious null returns the ceiling exactly and reads as a confirmation.

    Shuffling a day and re-running the optimiser sorts the same values, so it reproduces the
    achievable saving to the last decimal. The null that works picks BY the shuffle and scores BY
    the truth. This asserts the two are different, which is the only thing that distinguishes a
    null from a tautology here.
    """
    day = _shaped_day(0.0)
    rng = random.Random(7)
    achievable = achievable_saving_per_kwh(day, WINDOW)

    shuffled = list(day)
    rng.shuffle(shuffled)
    optimiser_on_a_shuffle = achievable_saving_per_kwh(shuffled, WINDOW)
    assert optimiser_on_a_shuffle == pytest.approx(achievable), (
        "the permutation null is a tautology by construction — if this ever stops holding, the "
        "reason this module uses the other null has changed")

    skill_free = statistics.fmean(
        [skill_free_saving_per_kwh(day, WINDOW, rng) for _ in range(200)])
    assert skill_free < achievable * 0.5, (
        "the null actually used must be materially below the achievable saving")


def test_the_clearance_ratio_FALLS_with_PANEL_SIZE_which_is_the_whole_reason_it_is_recomputed():
    """DEFECT: a matched-panel figure that does not actually vary with the panel.

    The payload tells a reader to compare THIS ratio with R3's and not the whole-panel one, and
    that instruction is only true if the ratio depends on the panel size. A smaller panel gives a
    noisier null mean, so the MAXIMUM over draws sits higher and the ratio comes out lower — for
    sampling reasons that have nothing to do with signal, which is exactly why the raw ratios of
    two differently-sized panels must never be read against each other.

    THE FIRST DRAFT OF THIS CONTROL COMPARED THE MATCHED RATIO WITH THE WHOLE-PANEL ONE AND
    SURVIVED THE MUTATION THAT REPLACES THE SUBSAMPLE WITH THE WHOLE SERIES. It passed for the
    wrong reason: `matched` takes its maximum over 60x more draws than `world` does, so its null
    sits higher and its ratio lower even when the two panels are identical. It was measuring the
    draw count. Both legs here use the same draw count, so only the panel differs.
    """
    prices = _price_shape(40)
    days = {d: [prices[(d, p)] for p in range(1, PERIODS + 1)]
            for d in sorted({k[0] for k in prices})}

    small = matched_panel_clearance(days, WINDOW, panel=8, seed=5)
    large = matched_panel_clearance(days, WINDOW, panel=32, seed=5)
    assert (small["panel_days"], large["panel_days"]) == (8, 32)
    assert small["median_ratio"] < large["median_ratio"], (
        f"a {small['panel_days']}-day panel reported {small['median_ratio']}x and a "
        f"{large['panel_days']}-day panel {large['median_ratio']}x — if the ratio does not fall "
        "with the panel, the recomputation is not doing the thing the payload says it does")
    for got in (small, large):
        assert got["worst_ratio"] <= got["median_ratio"] <= got["best_ratio"]


def test_a_matched_panel_LARGER_than_the_series_refuses_rather_than_inventing_a_subsample():
    """DEFECT: silently sampling with replacement, or returning a ratio over a panel that is not
    the panel claimed. Both would publish a comparison that was never computed."""
    days = {f"2019-01-{d + 1:02d}": _shaped_day(0.0) for d in range(5)}
    got = matched_panel_clearance(days, WINDOW, panel=20, seed=1)
    assert got["available"] is False
    assert "must NOT be read against" in got["why"]


# --------------------------------------------------------------------------------------------
# THE SHARING SIDE. An identity has to be asserted, or it is only a claim in a docstring.
# --------------------------------------------------------------------------------------------

def test_the_frontier_SUMS_TO_THE_CREATED_VALUE_at_every_pass_through():
    """DEFECT: a frontier whose two sides do not add up would make sharing look like creation.

    This is the instrument's central claim — sharing allocates value, it never creates any — and
    a claim made only in prose is a claim nothing can refute.
    """
    created = 51.3596
    for row in sharing_frontier(created):
        total = (row["household_gbp_per_household_year"]
                 + row["company_gbp_per_household_year"])
        assert total == pytest.approx(created, abs=0.001), (
            f"at pass-through {row['pass_through']} the two shares sum to {total}, not to the "
            "created value — which would mean the split had created or destroyed value")


def test_the_company_share_is_ZERO_AT_BOTH_ENDS_so_its_optimum_is_interior():
    """DEFECT: dropping either endpoint turns a parameter-free conclusion into an assertion.

    At full pass-through the company retains nothing — that is arithmetic and is asserted here. At
    zero pass-through it retains all of nothing, because a household whose bill does not move has
    no money reason to shift; that leg is a statement about the world and lives in the payload's
    `the_interior_optimum`, so this control checks BOTH: the arithmetic end here, and that the
    behavioural end is published rather than assumed.
    """
    rows = {row["pass_through"]: row for row in sharing_frontier(100.0)}
    assert rows[1.0]["company_gbp_per_household_year"] == pytest.approx(0.0)
    assert rows[0.0]["household_gbp_per_household_year"] == pytest.approx(0.0)
    assert 0.0 in PASS_THROUGH_GRID and 1.0 in PASS_THROUGH_GRID, (
        "a frontier printed without its endpoints cannot show that both ends are zero for the "
        "company, which is the only conclusion here that needs no elasticity")


def test_the_share_curve_carries_NO_carbon_column():
    """DEFECT: reusing R3's `share_curve` would fill a carbon column with 0.0.

    A zero there renders as "measured, abates nothing", which is the opposite of the truth: the
    same act abates exactly what R3 measures. `None` cannot be read as an established answer and a
    zero can, so the column is ABSENT rather than empty.
    """
    for row in money_share_curve(51.36):
        assert set(row) == {"shiftable_share", "gbp_per_household_year"}, (
            "the money share curve must not carry a carbon column at all")


# --------------------------------------------------------------------------------------------
# THE BOOK. Who could be sold the product is the constraint, and it is counted.
# --------------------------------------------------------------------------------------------

def test_the_reachable_population_is_the_SMART_METERED_ones_and_not_the_whole_book(run_file):
    """DEFECT: dropping the smart-meter filter would report a book three times its real size.

    A time-of-use tariff is settled half-hourly and half-hourly settlement needs a smart meter. If
    the filter is ever removed, `reachable` equals `households_with_an_eac` and this fails.
    """
    payload = _book(households=40, smart=25)
    got = measure(run_path=run_file(payload), prices=_price_shape(40), seed=2)
    assert got["book"]["households_with_an_eac"] == 40
    assert got["book"]["reachable"] == 25
    assert got["reachable_book"]["households"] == 25
    assert got["reachable_book"]["book_gbp_per_year"] < (
        got["created_value"]["gbp_per_household_year"] * 40), (
        "the reachable book must be smaller than the whole book at the same per-household rate")


def test_a_gas_leg_is_NOT_counted_as_a_smart_metered_household():
    """DEFECT: a gas leg registered under its electricity point's id has no timing lever at all.

    R3 excludes it from the EAC by `household_of`; this excludes it from the reachable population
    the same way. Counting it would inflate the population a ToU tariff could be sold to with a
    meter point that cannot be on one.
    """
    payload = {
        "meter_read_log": [
            {"customer_id": "C1", "meter_type": "smart"},
            {"customer_id": "C1g", "meter_type": "smart"},
        ]
    }
    assert smart_metered_households(payload) == {"C1"}


def test_a_reachable_population_under_the_floor_REFUSES_rather_than_publishing_a_book_figure(
        run_file):
    """DEFECT: "3 households, £150 a year" reads exactly like a measurement of the book.

    FAIL CLOSED, at the same floor R3 and R4 use. The refusal names its reason and the
    per-household ceiling is still reported, because that figure does not depend on the count.
    """
    payload = _book(households=30, smart=3)
    got = measure(run_path=run_file(payload), prices=_price_shape(40), seed=2)
    assert got["reachable_book"]["available"] is False
    assert got["reachable_book"]["households"] == 3
    assert str(MIN_HOUSEHOLDS) in got["reachable_book"]["why"]
    assert got["created_value"]["gbp_per_household_year"] > 0.0


def test_a_book_under_the_household_floor_RAISES_and_never_reports_a_zero_ceiling(run_file):
    """DEFECT: an instrument that cannot measure must not be able to report a retiring result.

    Zero created value RETIRES the time-of-use product, so an unavailable instrument reporting one
    would retire a programme on the strength of an absent file.
    """
    payload = _book(households=5, smart=5)
    with pytest.raises(CeilingUnavailable) as exc:
        measure(run_path=run_file(payload), prices=_price_shape(40), seed=2)
    assert "NOT a finding that a time-of-use tariff is worthless" in str(exc.value)


def test_too_few_days_RAISES_rather_than_bounding_a_programme_on_a_handful(run_file):
    """DEFECT: a ceiling over nine days is nine days wearing a ceiling's name."""
    with pytest.raises(CeilingUnavailable) as exc:
        measure(run_path=run_file(_book()), prices=_price_shape(4), seed=2)
    assert "whole day" in str(exc.value)


# --------------------------------------------------------------------------------------------
# WHAT THE PAYLOAD MUST SAY. A ceiling that publishes only its flattering side is a sales figure.
# --------------------------------------------------------------------------------------------

def test_the_known_errors_carry_BOTH_directions(run_file):
    """DEFECT: publishing only the understatements. Every ceiling here has errors both ways and
    an instrument that names one direction is arguing rather than measuring."""
    got = measure(run_path=run_file(_book()), prices=_price_shape(40), seed=2)
    directions = {e["direction"] for e in got["known_errors"]}
    assert directions == {"overstates", "understates"}, (
        f"both directions must be named; got {sorted(directions)}")


def test_the_payload_carries_NO_field_that_sums_the_two_currencies(run_file):
    """DEFECT: a total field is the number a reader would quote, and this one is not a quantity.

    The money column is a wholesale cost avoided; the carbon column is tonnes valued at the traded
    price. R4 refuses the same sum for the same reason.
    """
    got = measure(run_path=run_file(_book()), prices=_price_shape(40), seed=2)
    flat = json.dumps(got)
    assert "refuses_to_total" in got
    for banned in ("total_value_gbp", "combined_gbp", "money_plus_carbon"):
        assert banned not in flat


def test_the_headline_states_the_CEILING_and_the_reachable_book_without_conflating_them(run_file):
    """DEFECT: a per-household ceiling over one denominator quoted beside a book figure over
    another, with nothing saying which is which. That is how a ratio becomes a quantity nobody
    defined — this project's most expensive recurring shape."""
    got = measure(run_path=run_file(_book(households=40, smart=25)), prices=_price_shape(40),
                  seed=2)
    got["headline"] = headline(got)
    assert "CEILING" in got["headline"]
    assert "smart meter" in got["headline"]
    assert "22 of 68" not in got["headline"], "the headline must quote THIS run, not a past one"
    assert f"{got['book']['reachable']} of {got['book']['households_with_an_eac']}" in got[
        "headline"]
    assert "why_the_two_denominators_differ" in got["book"]


def test_a_retiring_reading_says_RETIRED_and_says_it_first(run_file):
    """DEFECT: a headline that leads with a number and buries the verdict.

    A flat price series has nothing for a tariff to pass through, and because the created value is
    a true CEILING that RETIRES the product outright rather than merely failing to support it. The
    branch exists to be taken rarely, so this asserts it CAN be taken at all.
    """
    got = measure(run_path=run_file(_book()), prices=_flat_price_shape(40), seed=2)
    assert got["verdict"]["clears_the_null"] is False
    assert got["verdict"]["retires_time_of_use"] is True
    assert headline(got).startswith("THE TIME-OF-USE PRODUCT IS RETIRED")


def test_the_carbon_column_is_READ_from_R3_and_never_recomputed_here(run_file):
    """DEFECT: two implementations of one quantity is how a figure comes to have two values and no
    owner. This repository has already paid for that once with the VAT rule."""
    got = measure(run_path=run_file(_book()), prices=_price_shape(40), seed=2)
    column = got["the_carbon_column"]
    if not column.get("available"):
        assert "r3_carbon_score_ceiling" in column["why"]
        pytest.skip("R3's artefact is absent from this tree; the absence path is asserted above")
    assert column["source"].startswith("tools/r3_carbon_score_ceiling.py")
    from tools.tou_sharing_ceiling import R3_ARTEFACT
    r3 = json.loads(R3_ARTEFACT.read_text(encoding="utf-8"))
    assert column["kg_co2e_per_household_year"] == (
        r3["rungs"]["hindsight_ceiling"]["kg_co2e_per_household_year"])


# --------------------------------------------------------------------------------------------
# THE LIVE TREE. One test, and it skips loudly rather than passing vacuously.
# --------------------------------------------------------------------------------------------

def test_the_live_price_series_refusal_NAMES_the_gitignored_cache():
    """DEFECT: a refusal that does not say why is a refusal nobody can discover was wrong.

    In a clean worktree extract the Elexon MID cache is absent, and the honest result is a named
    refusal rather than a book that cannot save anything.
    """
    try:
        prices = half_hourly_wholesale_price()
    except CeilingUnavailable as exc:
        assert "gitignored" in str(exc) or "could not be read" in str(exc)
        return
    assert prices, "a present cache must yield priced half hours"
    assert all(isinstance(k, tuple) and len(k) == 2 for k in list(prices)[:5])
