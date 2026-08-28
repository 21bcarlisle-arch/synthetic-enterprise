"""Acquisition cost expensed and amortised — roadmap R5, 2026-08-28.

The module under test does not change the P&L and must not: expensing as incurred is what GAAP
and IFRS require, and the accounts are right. What it adds is the CMA's own view of the same
spend, so a growing supplier's year is not read as a trading loss when it is an investment.
"""
import pytest

from company.analytics.acquisition_cost_amortisation import (
    CMA_BASE_CASE_CUSTOMER_LIFETIME_YEARS,
    CMA_SENSITIVITY_CUSTOMER_LIFETIME_YEARS,
    amortisation_schedule,
    growth_year_distortion_gbp,
)


def _spend(year, amount):
    return {"event_date": f"{year}-06-01", "amount_gbp": amount}


class TestTheCitedInputs:
    def test_the_base_case_is_the_cmas_six_years(self):
        assert CMA_BASE_CASE_CUSTOMER_LIFETIME_YEARS == 6

    def test_the_sensitivity_is_the_cmas_eight(self):
        assert CMA_SENSITIVITY_CUSTOMER_LIFETIME_YEARS == 8


class TestTheArithmetic:
    def test_one_year_of_spend_spreads_evenly_over_the_lifetime(self):
        s = amortisation_schedule([_spend(2020, 600.0)], lifetime_years=6,
                                  through_year=2025)
        assert [r["amortised_gbp"] for r in s["by_year"]] == [100.0] * 6
        assert s["by_year"][0]["expensed_gbp"] == 600.0
        assert [r["expensed_gbp"] for r in s["by_year"][1:]] == [0.0] * 5

    def test_nothing_is_lost_when_the_window_covers_the_whole_life(self):
        s = amortisation_schedule([_spend(2020, 600.0)], lifetime_years=6, through_year=2025)
        assert s["amortised_within_window_gbp"] == pytest.approx(s["total_spend_gbp"])
        assert s["unamortised_carried_beyond_window_gbp"] == pytest.approx(0.0)

    def test_spend_at_the_edge_of_the_window_is_mostly_carried(self):
        """The number the report exists to state: cost paid whose benefit is outside the period.

        £600 spent in the last reported year has one sixth of its life inside it.
        """
        s = amortisation_schedule([_spend(2025, 600.0)], lifetime_years=6, through_year=2025)
        assert s["amortised_within_window_gbp"] == pytest.approx(100.0)
        assert s["unamortised_carried_beyond_window_gbp"] == pytest.approx(500.0)

    def test_a_longer_assumed_lifetime_charges_less_per_year(self):
        base = amortisation_schedule([_spend(2020, 600.0)],
                                     lifetime_years=CMA_BASE_CASE_CUSTOMER_LIFETIME_YEARS,
                                     through_year=2030)
        longer = amortisation_schedule([_spend(2020, 600.0)],
                                       lifetime_years=CMA_SENSITIVITY_CUSTOMER_LIFETIME_YEARS,
                                       through_year=2030)
        assert longer["by_year"][0]["amortised_gbp"] < base["by_year"][0]["amortised_gbp"]
        assert longer["total_spend_gbp"] == base["total_spend_gbp"]

    def test_the_ledgers_negative_sign_is_normalised(self):
        """Acquisition rows are booked as negative cash movements. A schedule of negative
        numbers is read wrongly by every consumer at least once."""
        s = amortisation_schedule([{"event_date": "2020-06-01", "amount_gbp": -600.0}],
                                  lifetime_years=6, through_year=2025)
        assert s["total_spend_gbp"] == 600.0
        assert all(r["amortised_gbp"] >= 0 for r in s["by_year"])


class TestTheDistortion:
    def test_a_growing_book_is_charged_more_than_it_carries(self):
        """The whole point. Spend rising every year means the expensed view is above the
        amortised one in every year of the growth, which is what makes growth read as loss."""
        events = [_spend(y, 100.0 * (y - 2019)) for y in range(2020, 2026)]
        d = growth_year_distortion_gbp(
            amortisation_schedule(events, lifetime_years=6, through_year=2025))
        assert all(x["expensed_minus_amortised_gbp"] > 0 for x in d)

    def test_it_nets_to_zero_once_every_cohort_has_lived_its_life(self):
        """MUTATION guard on the claim above: the gap is TIMING, not a different total. If the
        two columns did not converge, one of them would be measuring a different quantity."""
        events = [_spend(y, 600.0) for y in range(2020, 2023)]
        d = growth_year_distortion_gbp(
            amortisation_schedule(events, lifetime_years=6, through_year=2040))
        assert sum(x["expensed_minus_amortised_gbp"] for x in d) == pytest.approx(0.0, abs=0.02)

    def test_a_flat_book_still_distorts_while_it_is_young(self):
        """Even with constant spend the early years are under-charged in the amortised view,
        because there are no prior cohorts yet carrying their share."""
        events = [_spend(y, 600.0) for y in range(2020, 2026)]
        d = growth_year_distortion_gbp(
            amortisation_schedule(events, lifetime_years=6, through_year=2025))
        assert d[0]["expensed_minus_amortised_gbp"] > 0


class TestItFailsClosed:
    def test_an_unreadable_event_is_counted_not_dropped(self):
        s = amortisation_schedule(
            [_spend(2020, 600.0), {"event_date": "not-a-date", "amount_gbp": 100.0}],
            lifetime_years=6, through_year=2025)
        assert s["total_spend_gbp"] == 600.0
        assert s["events_that_could_not_be_read"] == 1

    @pytest.mark.parametrize("bad", [
        {"amount_gbp": 100.0},
        {"event_date": "2020-06-01"},
        {"event_date": "2020-06-01", "amount_gbp": None},
        {"event_date": None, "amount_gbp": 100.0},
        "not a dict at all",
    ])
    def test_malformed_shapes_are_counted(self, bad):
        s = amortisation_schedule([bad])
        assert s["events_that_could_not_be_read"] == 1
        assert s["total_spend_gbp"] == 0.0

    def test_no_spend_returns_an_empty_schedule_not_a_zero_row(self):
        """A year row of £0 reads as a supplier that spent nothing that year. Absent is not the
        same claim as zero, and the report renders nothing rather than an empty table."""
        s = amortisation_schedule([])
        assert s["by_year"] == []
        assert s["total_spend_gbp"] == 0.0

    def test_a_lifetime_under_a_year_is_refused_rather_than_clamped(self):
        with pytest.raises(ValueError, match="less than one year"):
            amortisation_schedule([_spend(2020, 600.0)], lifetime_years=0)


class TestItReachesTheReport:
    """R5 is only done if the view is rendered. An analytics module nobody calls is exactly the
    defect this whole roadmap exists to close -- see
    `tests/architecture/test_a_cited_constant_has_a_caller.py`."""

    def test_the_report_section_renders_both_columns(self):
        from saas.reporting.annual_report import _acquisition_amortisation_lines

        data = {"years": {2020: {"acquisition_spend_gbp": 600.0},
                          2021: {"acquisition_spend_gbp": 1200.0}}}
        text = "\n".join(_acquisition_amortisation_lines(data))
        assert "Expensed" in text and "Amortised" in text
        assert "£1,800" in text          # the total, unchanged by the treatment
        assert "6 years" in text         # the assumption is stated on the page, not implied

    def test_the_report_section_renders_nothing_when_no_spend(self):
        from saas.reporting.annual_report import _acquisition_amortisation_lines

        assert _acquisition_amortisation_lines({"years": {2020: {}}}) == []
        assert _acquisition_amortisation_lines({}) == []
