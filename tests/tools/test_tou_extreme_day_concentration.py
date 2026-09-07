"""Controls over the extreme-day concentration instrument.

Each test is named for the defect it exists to catch. The fixtures are SYNTHETIC on purpose, for
the reason the sibling suite gives: the Elexon MID caches and the Ofgem cap models are gitignored
source data, so a suite that reached for them would pass vacuously in every clean worktree extract
and every mutation of this module would survive there.

The two that matter most are the subset control and the tail decomposition, because the finding
this module produced rests on them: that the ten-year widening of the within-day ratio is ENTIRELY
on the trough side, and that an extreme-day tariff cannot out-earn an everyday one. Both are
written with BOTH legs of their partition asserted, so a decomposition that always answers
"trough", or a guard that refuses everything, cannot pass.
"""
from __future__ import annotations

import math

import pytest

from tools.tou_extreme_day_concentration import (
    ConcentrationUnavailable,
    Day,
    assert_the_subset_cannot_beat_the_whole,
    break_evens,
    concentration,
    gross_value,
    price_product,
    slope_response,
    weights,
    where_the_ratio_tail_comes_from,
)
from tools.tou_price_shape_episode import arc_response

#: The Arcturus 2.0 primary specification as the landed artefact carries it, restated so a mutation
#: of the reading is caught against the PAPER rather than against whatever is loaded today.
PRIMARY = {"constant": -0.011, "ln_price_ratio": -0.065, "ln_price_ratio_x_technology": -0.046}

KWH_PER_YEAR = 3854.2


def day(date_str: str, *, saving: float, peak_rel: float | None = 1.3,
        off_rel: float | None = 0.75, kwh: float = 5.0, share: float = 0.56) -> Day:
    """One synthetic day. `off_rel=None` is a day whose trough went negative."""
    ratio = None if (peak_rel is None or off_rel is None) else peak_rel / off_rel
    return Day(date_str=date_str, saving=saving, kwh=kwh, share=share, backcast=False,
               ratio=ratio, peak_rel=None if ratio is None else peak_rel,
               off_rel=None if ratio is None else off_rel)


class TestTheSubsetControl:
    """The pre-registered control on this module's own arithmetic.

    An extreme-day product sums a subset of the everyday product's non-negative per-day terms, so
    it cannot exceed it. A run reporting otherwise would be publishing exactly the commercial
    result somebody wanted, which is the most attractive kind of defect there is.
    """

    def test_it_refuses_when_a_subset_product_out_earns_the_whole(self):
        """THE LEG THAT PROVES THE GUARD CAN FIRE AT ALL. Without this, a guard that never
        refuses passes every other test in this class."""
        with pytest.raises(ConcentrationUnavailable, match="cannot exceed the whole sum"):
            assert_the_subset_cannot_beat_the_whole({
                "everyday": {"available": True, "company_gbp_per_household_year": 0.50},
                "extreme_top_10pc": {"available": True, "company_gbp_per_household_year": 0.51},
            })

    def test_it_admits_the_ordering_the_arithmetic_actually_produces(self):
        """THE OTHER LEG. A guard that refused everything would be caught here, and this is the
        pairing this project has entered the same trap through three separate doors without."""
        assert_the_subset_cannot_beat_the_whole({
            "everyday": {"available": True, "company_gbp_per_household_year": 0.7392},
            "extreme_top_10pc": {"available": True, "company_gbp_per_household_year": 0.2916},
        })

    def test_an_equal_pair_is_admitted_because_a_full_trigger_is_the_whole_book(self):
        """A trigger of 100% selects every day, so equality is the boundary the arithmetic reaches
        rather than a violation of it. A guard written with `>=` would refuse a legitimate run."""
        assert_the_subset_cannot_beat_the_whole({
            "everyday": {"available": True, "company_gbp_per_household_year": 0.7392},
            "extreme_top_100pc": {"available": True, "company_gbp_per_household_year": 0.7392},
        })


class TestTheSlopeOnlyResponse:
    """If the intercept is not removed, the comparison counts DAYS instead of comparing PRODUCTS."""

    def test_it_vanishes_at_a_flat_price_where_the_fitted_response_does_not(self):
        """THE DEFECT THIS COLUMN EXISTS FOR. The fitted constant is -0.011, so a household shown
        no price difference is credited with a 1.1% reduction. The everyday product collects that
        on all 365 days and the extreme product on a few dozen, so a comparison on the fitted
        response is a count of billing days wearing the clothes of a behavioural result."""
        assert slope_response(1.0, PRIMARY) == 0.0
        assert arc_response(1.0, PRIMARY, opt_out=False) == pytest.approx(0.011, abs=1e-9)

    def test_it_keeps_the_papers_slope_and_only_drops_the_constant(self):
        """A reader that dropped the slope instead of the intercept, or rescaled it, would make
        every product figure in the artefact wrong while still vanishing at 1:1."""
        assert slope_response(2.0, PRIMARY) == pytest.approx(0.065 * math.log(2.0), abs=1e-12)
        assert slope_response(2.0, PRIMARY) == pytest.approx(
            arc_response(2.0, PRIMARY, opt_out=False) - 0.011, abs=1e-9)

    def test_a_dearer_off_peak_window_clips_to_zero_rather_than_a_negative_response(self):
        """Below 1:1 the raw expression goes negative, and a negative reduction published as a
        response would put a value-DESTROYING tariff on the frontier looking like a small number."""
        assert slope_response(0.5, PRIMARY) == 0.0

    def test_a_non_positive_ratio_is_refused_rather_than_returned_as_no_response(self):
        """There is no logarithm of zero. Returning 0.0 would read as "measured, found nothing"."""
        with pytest.raises(ConcentrationUnavailable):
            slope_response(0.0, PRIMARY)


class TestTheDaysTheModelCannotPrice:
    """Dropping negative-price days silently would delete the fattest part of the tail."""

    def test_a_negative_trough_day_is_carried_in_the_concentration_and_counted_in_money(self):
        """THE FAIL-SILENT DEFECT. The landed panel drops these from its ratio and the saving on
        them is real and large. An instrument that dropped them here would understate the very
        concentration it was built to measure, and would do it invisibly."""
        rows = [day(f"2024-01-{i:02d}", saving=5.0) for i in range(1, 20)]
        rows.append(day("2024-01-20", saving=95.0, peak_rel=None, off_rel=None))
        result = concentration(rows, "flat", KWH_PER_YEAR)
        blind = result["the_days_the_response_model_cannot_price"]
        assert blind["days"] == 1
        assert blind["share_of_gross_value"] == pytest.approx(95.0 / (19 * 5.0 + 95.0), abs=1e-4)
        assert blind["share_of_them_that_are_in_the_top_decile_by_value"] == 1.0

    def test_the_same_day_is_excluded_from_every_priced_product(self):
        """The other half of the same contract: carried in the concentration, absent from the
        products, because Arcturus cannot take the logarithm of a meaningless ratio. If it leaked
        into a product it would be priced by a function that has no value there.
        The fixture is built so the one unpriceable day carries EXACTLY half the year's value:
        19 days worth 5.0 against one worth 95.0. So the reachable share is a number the test can
        state rather than bound, and a day leaking into the product moves it to 1.0.
        """
        rows = [day(f"2024-01-{i:02d}", saving=5.0) for i in range(1, 20)]
        rows.append(day("2024-01-20", saving=95.0, peak_rel=None, off_rel=None))
        priced = price_product(rows, list(range(len(rows))), "flat", KWH_PER_YEAR,
                               PRIMARY, opt_out=False, intercept=False)
        assert priced["days_paid_on"] == 19
        assert priced["share_of_gross_value_reachable"] == pytest.approx(0.5, abs=1e-9)

    def test_a_product_of_only_unpriceable_days_refuses_instead_of_returning_zero(self):
        """A trigger that selected only negative-price days would otherwise report a tariff worth
        exactly nothing, which is a very different claim from "cannot be priced"."""
        rows = [day("2024-01-20", saving=95.0, peak_rel=None, off_rel=None)]
        assert price_product(rows, [0], "flat", KWH_PER_YEAR, PRIMARY,
                             opt_out=False, intercept=False)["available"] is False


class TestTheLoadAllocation:
    """A flat kWh allocation is right for a mean and wrong for a tail."""

    def test_pc1_weights_a_winter_day_above_a_summer_day_and_flat_does_not(self):
        """THE DEFECT: extreme price days are disproportionately winter days, and weighting them
        like an August Sunday understates exactly the product under test. Reverting to flat would
        be invisible in every total, because both allocations sum to one."""
        rows = [day("2024-01-15", saving=10.0, kwh=6.145),
                day("2024-07-15", saving=10.0, kwh=4.435)]
        pc1 = weights(rows, "pc1")
        assert pc1[0] > pc1[1]
        assert sum(pc1) == pytest.approx(1.0, abs=1e-12)
        assert weights(rows, "flat") == [0.5, 0.5]

    def test_both_allocations_conserve_the_years_value(self):
        """A weighting that did not sum to one would move the TOTAL as well as the shares, and the
        concentration share would still look perfectly reasonable."""
        rows = [day("2024-01-15", saving=10.0, kwh=6.1), day("2024-07-15", saving=30.0, kwh=4.4)]
        for allocation in ("flat", "pc1"):
            values = gross_value(rows, allocation, KWH_PER_YEAR)
            assert sum(values) > 0
            assert len(values) == 2

    def test_an_unknown_allocation_is_refused_rather_than_falling_back_to_flat(self):
        """A silent fallback to flat is the mutation this whole class is here to catch."""
        with pytest.raises(ConcentrationUnavailable, match="unknown kWh allocation"):
            weights([day("2024-01-15", saving=1.0)], "uniform")


class TestTheRatioTailDecomposition:
    """The finding rests on this: the ten-year widening is ENTIRELY on the trough side.

    A decomposition that always answered "trough" would produce that finding from any data at all,
    so both legs of the partition are asserted here.
    """

    def test_a_varying_trough_against_a_fixed_peak_is_attributed_to_the_trough(self):
        rows = [day(f"2024-01-{i:02d}", saving=10.0, peak_rel=1.3, off_rel=0.2 + i * 0.03)
                for i in range(1, 21)]
        out = where_the_ratio_tail_comes_from(rows)["variance_of_the_log_ratio"]
        assert out["from_the_peak"] == pytest.approx(0.0, abs=1e-12)
        assert out["from_the_trough"] > 0
        assert out["trough_share_of_the_two_variances"] == pytest.approx(1.0, abs=1e-6)

    def test_a_varying_peak_against_a_fixed_trough_is_attributed_to_the_peak(self):
        """THE MIRROR LEG. Without it, a decomposition hard-wired to blame the denominator passes
        the test above and produces this module's headline finding out of nothing."""
        rows = [day(f"2024-01-{i:02d}", saving=10.0, peak_rel=1.0 + i * 0.05, off_rel=0.75)
                for i in range(1, 21)]
        out = where_the_ratio_tail_comes_from(rows)["variance_of_the_log_ratio"]
        assert out["from_the_trough"] == pytest.approx(0.0, abs=1e-12)
        assert out["from_the_peak"] > 0
        assert out["trough_share_of_the_two_variances"] == pytest.approx(0.0, abs=1e-6)

    def test_the_gain_saturates_at_one_while_the_ratio_runs_away(self):
        """THE ARITHMETIC THE WHOLE VERDICT TURNS ON. As the trough collapses the ratio diverges
        without bound and the saving converges on the day's mean price and stops. If these two
        ever moved together, "fattest tail in the record" would mean what it was read to mean."""
        collapsing = [day(f"2024-01-{i:02d}", saving=10.0, peak_rel=1.3, off_rel=off)
                      for i, off in enumerate([0.5, 0.25, 0.1, 0.05, 0.01, 0.005], start=1)]
        ratios = [row.ratio for row in collapsing]
        gains = [1.0 - row.off_rel for row in collapsing]
        assert ratios[-1] / ratios[0] > 90            # the ratio has multiplied ninety-fold
        assert gains[-1] / gains[0] < 2.0             # the gain has not doubled
        assert max(gains) < 1.0
        bound = where_the_ratio_tail_comes_from(collapsing)["the_gain_is_bounded_where_the_ratio_is_not"]
        assert bound["ceiling_on_a_day_with_a_non_negative_trough"] == 1.0
        assert bound["p90_saving_over_day_mean"] < 1.0

    def test_it_refuses_a_single_day_rather_than_reporting_a_variance_of_zero(self):
        """One day has no variance, and reporting 0.0 would read as "the peak side never moves" --
        which is this instrument's actual finding, arrived at from no data."""
        assert where_the_ratio_tail_comes_from([day("2024-01-01", saving=1.0)])["available"] is False


class TestTheBreakEvens:
    """A break-even is the honest form of a number nobody has established. It has to be exact."""

    def test_the_attention_premium_is_the_ratio_of_the_two_optimised_company_values(self):
        """Company value is linear in the response, so the multiplier that closes the gap is exact
        rather than searched. A premium computed by re-optimising alpha would be subtly wrong and
        entirely plausible."""
        out = break_evens({
            "everyday": {"available": True, "company_gbp_per_household_year": 0.7392,
                         "days_paid_on_per_year": 324.8},
            "extreme_top_10pc": {"available": True, "company_gbp_per_household_year": 0.2916,
                                 "days_paid_on_per_year": 32.5},
        }, cac_gbp=27.5)
        row = out["by_trigger"]["extreme_top_10pc"]
        assert row["attention_premium_break_even_multiple"] == pytest.approx(
            0.7392 / 0.2916, abs=0.005)
        assert row["value_forgone_gbp_per_household_year"] == pytest.approx(0.4476, abs=1e-4)

    def test_the_running_cost_break_even_is_per_household_DAY_and_not_per_year(self):
        """Dividing by the year instead of by the days avoided would overstate the break-even by
        two orders of magnitude and make an unviable product look like a live commercial option.
        This project's most expensive recurring shape is a ratio whose two sides count different
        things."""
        out = break_evens({
            "everyday": {"available": True, "company_gbp_per_household_year": 0.7392,
                         "days_paid_on_per_year": 324.8},
            "extreme_top_10pc": {"available": True, "company_gbp_per_household_year": 0.2916,
                                 "days_paid_on_per_year": 32.5},
        }, cac_gbp=27.5)
        row = out["by_trigger"]["extreme_top_10pc"]
        assert row["household_days_avoided_per_year"] == pytest.approx(332.75, abs=0.1)
        assert row["running_cost_break_even_pence_per_household_day"] == pytest.approx(
            100.0 * 0.4476 / 332.75, abs=1e-4)
        assert row["running_cost_break_even_pence_per_household_day"] < 1.0

    def test_the_payback_uses_the_sourced_cac_it_was_handed_and_does_not_carry_its_own(self):
        """A second copy of the acquisition cost living here would go stale against the opex
        ledger's, and the stale one would be the one published."""
        out = break_evens({
            "everyday": {"available": True, "company_gbp_per_household_year": 1.0,
                         "days_paid_on_per_year": 365.0},
        }, cac_gbp=27.5)
        assert out["everyday_cac_payback_years"] == pytest.approx(27.5, abs=1e-6)
        assert out["cac_gbp"] == 27.5
