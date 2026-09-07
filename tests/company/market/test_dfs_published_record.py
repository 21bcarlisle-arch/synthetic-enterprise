"""Controls on the published NESO DFS record.

Each test is named for the defect it exists to catch. The defect that motivated the module is a real
one that lived in the tree: `_DFS_RATE_GBP_PER_MWH = 4.5`, in two files, commented "NESO DFS average
2022-24", against a realised GBP3,316/MWh (2022/23) and GBP241/MWh (2024/25).

It survived because the test that asserted it recomputed the production formula from the same
constants -- `expected_dfs = _EV_FLEX_KW / 1000 * _DISPATCH_DURATION_HRS * _DFS_RATE_GBP_PER_MWH *
_DISPATCH_EVENTS_PER_YR`. That is a tautology: it cannot fail for any value of the constant. So the
controls here are keyed to the PUBLISHED RECORD and to structural properties, never to the formula.
"""
from __future__ import annotations

import inspect

import pytest

from company.market import dfs_published_record as record
from company.market import flexibility_potential, ic_flexibility_revenue


def test_both_legs_of_the_established_partition_are_reachable():
    """A guard that refuses EVERYTHING passes every single-leg test.

    The whole point of the 2023/24 row is that `established` has two values in the real record. If a
    later edit made every winter unestablished (or every winter established), each individual
    assertion below would still pass while the distinction the module exists to carry was gone.
    """
    established = [y for y in (2022, 2023, 2024) if record.winter(y).established]
    unestablished = [y for y in (2022, 2023, 2024) if not record.winter(y).established]
    assert established and unestablished, (
        f"the partition has collapsed: established={established} unestablished={unestablished}")


def test_an_unestablished_winter_returns_none_and_never_zero():
    """Fail-open: 0.0 would assert DFS paid nothing in 2023/24. It ran, and it paid.

    Zero and "we cannot say" lead to opposite decisions, so they must not share a representation.
    """
    assert record.realised_rate_gbp_per_mwh(2023) is None
    assert record.revenue_gbp_per_participant_winter(2023) is None
    assert record.revenue_gbp_for_flex_kw(7.4, 2023) is None
    assert "NOT ESTABLISHED" in record.winter(2023).source


def test_an_unestablished_winter_names_a_reason_rather_than_just_refusing():
    """A refusal that does not say why is how a wrong refusal survives."""
    source = record.winter(2023).source
    assert len(source) > 40 and "reconcile" in source, source


def test_the_dfs_rate_is_not_one_number_across_winters():
    """Collapsing the record to a scalar is the original defect's shape, not just its value.

    DFS was a contingency scheme with a GBP3,000/MWh guaranteed acceptance price in 2022/23 and a
    merit-based tool clearing an order of magnitude lower by 2024/25. Any single constant is wrong
    for at least one of them.
    """
    first = record.realised_rate_gbp_per_mwh(2022)
    latest = record.realised_rate_gbp_per_mwh(2024)
    assert first > 10 * latest, (
        f"the crisis winter and the competitive winter have converged: {first} vs {latest}")


def test_the_rate_is_not_the_four_point_five_that_was_wrong_by_three_orders_of_magnitude():
    """Regression on the actual defect, keyed to the published magnitude, not to today's figure."""
    for year in (2022, 2024):
        rate = record.realised_rate_gbp_per_mwh(year)
        assert rate > 100.0, f"{year}: {rate} GBP/MWh is back in the units the defect was in"


def test_neither_revenue_module_carries_its_own_copy_of_the_rate():
    """One fact, several implementations, is the shape that let a corrected copy diverge unnoticed.

    Source-level, because an import-level check passes happily while a module ALSO defines a private
    constant of its own and uses that instead.
    """
    for module in (flexibility_potential, ic_flexibility_revenue):
        src = inspect.getsource(module)
        assert "_DFS_RATE_GBP_PER_MWH =" not in src, f"{module.__name__} has re-minted the rate"
        assert "dfs_published_record" in src, f"{module.__name__} does not read the record"


def test_the_reference_participant_is_published_delivery_size_and_not_rated_asset_power():
    """Caught by a poison round: the reconciliation test below CANNOT catch this one.

    It feeds `REFERENCE_PARTICIPANT_FLEX_KW` into a function that divides by
    `REFERENCE_PARTICIPANT_FLEX_KW`, so it reads `base x 1` whatever the constant is -- the same
    self-referential shape as the tautology this whole file exists to replace. Setting the reference
    to 7.4 (rated charger power, the original defect) survived it. So the constant is checked here
    against the published bins by an independent route.

    NESO: "91% of delivery was below 1kW, and 9% between 1kW and 10kW", bin midpoints 0.5 and 5.5.
    """
    from_published_bins = 0.91 * 0.5 + 0.09 * 5.5
    assert record.REFERENCE_PARTICIPANT_FLEX_KW == pytest.approx(from_published_bins, abs=0.01)
    # and it must stay far under the rated power of one home charger, which is the defect's shape
    assert record.REFERENCE_PARTICIPANT_FLEX_KW < 0.25 * 7.4, (
        "the reference has drifted back toward rated asset power")


def test_a_book_of_average_participants_reproduces_the_published_total():
    """The anchor. If this drifts, the model has stopped agreeing with what DFS actually settled.

    Catches a wrong REFERENCE_PARTICIPANT_FLEX_KW, a wrong per-participant base, and any reversion to
    pricing off rated asset power -- which produced GBP461/yr for one EV household against a service
    that paid GBP6.94 per participant that winter.
    """
    for year in (2022, 2024):
        row = record.winter(year)
        per_average = record.revenue_gbp_for_flex_kw(record.REFERENCE_PARTICIPANT_FLEX_KW, year)
        modelled = per_average * row.registered_participants
        assert modelled == pytest.approx(row.paid_gbp, rel=0.02), (
            f"{year}: book total {modelled:,.0f} vs published {row.paid_gbp:,.0f}")


def test_events_counts_events_and_not_the_test_calendar():
    """`_DISPATCH_EVENTS_PER_YR = 20` matched the 2022/23 TEST count, not the event count.

    20 of the 22 were scheduled by calendar; only 2 were called by system conditions. A model keyed
    to the test calendar is measuring NESO's readiness programme, not GB system stress.
    """
    row = record.winter(2022)
    assert row.events == 22
    assert row.events_called_by_system_conditions == 2
    assert row.events_called_by_system_conditions < row.events, (
        "the founding winter's calendar-driven tests have been merged into the system-called count")


def test_participation_is_a_minority_of_registrants_and_never_the_whole_book():
    """The replaced model credited 100% of enrolled customers at 100% of rated power.

    NESO's best-attended event of 2024/25 drew 443,224 of 1.98m registered MPANs.
    """
    opt_in = record.winter(2024).opt_in_fraction
    assert 0.0 < opt_in < 0.35, f"opt-in of {opt_in} is outside anything the record supports"
    haircut = record.participation_haircut(2024)
    assert haircut < opt_in, "the delivery shortfall has stopped being applied on top of opt-in"


def test_the_called_day_premium_does_not_clear_the_published_break_even():
    """The finding, keyed to the PROPERTY rather than to today's number.

    A control pinned to 1.20 would go red when the measurement got better and stay green if the
    break-even moved. What must hold is the relation: the premium the real product achieved is below
    the multiple the extreme-day tariff needs, on the generous upper bound as well as the point
    estimate. If that ever reverses, the MERELY RARER verdict is refuted and must be corrected beside
    its claim -- which is a red worth having.
    """
    break_even = 2.53  # tools/tou_extreme_day_concentration.py, 2024-2025 episode, top decile
    assert record.CALLED_DAY_RESPONSE_PREMIUM < break_even
    assert record.CALLED_DAY_RESPONSE_PREMIUM_UPPER_BOUND < break_even
    assert record.CALLED_DAY_RESPONSE_PREMIUM < record.CALLED_DAY_RESPONSE_PREMIUM_UPPER_BOUND


def test_the_default_winter_is_the_latest_established_and_not_the_most_flattering():
    """Defaulting to the crisis winter would inflate every downstream figure by ~14x."""
    assert record.LATEST_ESTABLISHED_WINTER == 2024
    assert record.winter(record.LATEST_ESTABLISHED_WINTER).established
    assert (record.realised_rate_gbp_per_mwh(record.LATEST_ESTABLISHED_WINTER)
            < record.realised_rate_gbp_per_mwh(2022))


def test_an_unestablished_winter_books_zero_revenue_but_flags_that_it_did_so():
    """Both consumers must keep "paid nothing" and "we cannot say" distinguishable at the record."""
    estimate = flexibility_potential.FlexibilityPotentialBook().assess(
        "C1", has_ev=True, winter_start_year=2023)
    assert estimate.dfs_revenue_gbp_pa == 0.0 and estimate.dfs_established is False

    book = ic_flexibility_revenue.ICFlexibilityRevenueBook()
    book.compute_year(2023, [("C_IC1", 1_998_631)])
    assert book.records_for_year(2023)[0].dfs_established is False

    # and the established leg, so a module that flagged everything unestablished cannot pass
    book_ok = ic_flexibility_revenue.ICFlexibilityRevenueBook()
    book_ok.compute_year(2024, [("C_IC1", 1_998_631)])
    rec = book_ok.records_for_year(2024)[0]
    assert rec.dfs_established is True and rec.gross_dfs_revenue_gbp > 0.0


def test_a_pre_launch_year_is_zero_and_established_not_a_refusal():
    """Before Oct 2022 the service did not exist -- that is knowledge, not a gap."""
    book = ic_flexibility_revenue.ICFlexibilityRevenueBook()
    book.compute_year(2021, [("C_IC1", 1_998_631)])
    rec = book.records_for_year(2021)[0]
    assert rec.gross_dfs_revenue_gbp == 0.0 and rec.dfs_established is True
