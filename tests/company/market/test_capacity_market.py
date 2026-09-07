import datetime as dt

import pytest

from company.market.capacity_market import (
    AuctionType,
    CapacityMarketBook,
    CMObligation,
    CMUnit,
    CMUnitType,
    get_cm_price,
)


def test_the_two_auctions_for_one_delivery_year_are_not_one_price():
    """DY 2022/23 priced 6.44 in the T-4 slot and 75.00 in the T-1 -- 11.6x apart, both real.

    THE DEFECT THIS EXISTS FOR (2026-09-07). `test_cm_price_2022` asserted `get_cm_price(2022) ==
    75.00` against a table keyed by AUCTION year under a parameter named `delivery_year`. 75.00 is
    the T-1 clearing price for delivery year 2022/23, which cleared at the price CAP; the same
    delivery year's T-4 was suspended and its replacement T-3 cleared at 6.44, the lowest of the
    record. So the old assertion was right about the number, wrong about the year, and wrong about
    the auction -- and a single-price lookup could not have expressed the difference.

    MUTATION: make `get_cm_price` ignore its `auction` argument and this fires on the equality.
    """
    t4 = get_cm_price(2022, AuctionType.T4)
    t1 = get_cm_price(2022, AuctionType.T1)
    assert t4 == pytest.approx(6.44)
    assert t1 == pytest.approx(75.00)
    assert t1 / t4 == pytest.approx(11.65, abs=0.01)


def test_a_delivery_year_with_no_t4_refuses_rather_than_pricing():
    """2016/17 had no T-4 delivery at all -- only transitional DSR auctions ran.

    The deleted table asserted 18.00 for this year, which is the T-4 clearing price for delivery
    year 2019/20: the four-year offset between auction year and delivery year, visible in one
    value. `None` here is the published record refusing, not a lookup miss.
    """
    assert get_cm_price(2016, AuctionType.T4) is None
    assert get_cm_price(2017, AuctionType.T4) is None
    # and the refusal is NOT blanket -- the very next delivery year prices, so a `get_cm_price`
    # that returned None for everything would fail this leg.
    assert get_cm_price(2018, AuctionType.T4) == pytest.approx(19.40)


def test_annual_revenue():
    unit = CMUnit('BATT-001', CMUnitType.BATTERY, 10_000.0, dt.date(2022, 1, 1))
    o = CMObligation(unit, 2022, AuctionType.T4, 75.0)
    assert o.annual_revenue_gbp == pytest.approx(10_000.0 * 75.0)


def test_penalty_reduces_net():
    unit = CMUnit('BATT-001', CMUnitType.BATTERY, 10_000.0, dt.date(2022, 1, 1))
    o = CMObligation(unit, 2022, AuctionType.T4, 75.0)
    o.apply_penalty(50_000.0)
    assert o.net_revenue_gbp == pytest.approx(10_000.0 * 75.0 - 50_000.0)


def test_book_register_and_obligation():
    book = CapacityMarketBook()
    unit = book.register_unit('DR-001', CMUnitType.DEMAND_RESPONSE, 5000.0, dt.date(2022, 1, 1))
    ob = book.add_obligation(unit, 2022, AuctionType.T4)
    assert ob.clearing_price_gbp_per_kw == pytest.approx(6.44)


def test_an_obligation_is_priced_at_the_auction_it_is_actually_in():
    """A T-1 obligation prices at the T-1, not at the T-4 for the same delivery year.

    `add_obligation` took an `auction_type` and then ignored it when defaulting the price, so
    every obligation priced off one table. For DY 2022/23 that is GBP6.44 against a real GBP75.00
    -- an 11.6x understatement of a T-1 unit's revenue, from an argument the caller had already
    supplied.

    MUTATION: drop the `auction_type` argument in `add_obligation`'s `get_cm_price` call and this
    fires.
    """
    book = CapacityMarketBook()
    unit = book.register_unit('DR-9', CMUnitType.DEMAND_RESPONSE, 1000.0, dt.date(2022, 1, 1))
    t4_ob = book.add_obligation(unit, 2022, AuctionType.T4)
    t1_ob = book.add_obligation(unit, 2022, AuctionType.T1)
    assert t4_ob.clearing_price_gbp_per_kw == pytest.approx(6.44)
    assert t1_ob.clearing_price_gbp_per_kw == pytest.approx(75.00)


def test_an_obligation_in_a_year_with_no_published_price_refuses_by_name():
    """Rather than pricing at an invented default, which is what GBP50/kW was."""
    book = CapacityMarketBook()
    unit = book.register_unit('U0', CMUnitType.CCGT, 1000.0, dt.date(2016, 1, 1))
    with pytest.raises(ValueError, match="no published T4 clearing price"):
        book.add_obligation(unit, 2016, AuctionType.T4)
    # ...and an explicitly supplied price still works, so the refusal is about the DEFAULT and
    # does not wall off a caller that knows the price from elsewhere.
    ob = book.add_obligation(unit, 2016, AuctionType.T4, clearing_price=27.50)
    assert ob.clearing_price_gbp_per_kw == pytest.approx(27.50)


def test_total_revenue():
    book = CapacityMarketBook()
    unit = book.register_unit('CCGT-001', CMUnitType.CCGT, 100_000.0, dt.date(2022, 1, 1))
    book.add_obligation(unit, 2022, AuctionType.T4)
    assert book.total_revenue_gbp(2022) == pytest.approx(100_000.0 * 6.44)


def test_the_capped_t1_beats_every_t4_in_the_record():
    """The property, not today's answer: DY 2022/23's T-1 cleared above every published T-4.

    Keyed to the shape of the record rather than to a pair of years, so it stays true when a year
    is added and goes red if a T-4 is ever entered above the cap -- which would mean somebody had
    put a T-1 in a T-4 field, the exact defect this file's repair was about.
    """
    t4s = [
        p for y in range(2016, 2029)
        if (p := get_cm_price(y, AuctionType.T4)) is not None
    ]
    assert len(t4s) >= 8, "too few established T-4 prices for this control to mean anything"
    assert get_cm_price(2022, AuctionType.T1) > max(t4s)


def test_total_derated_kw():
    book = CapacityMarketBook()
    u1 = book.register_unit('U1', CMUnitType.BATTERY, 3000.0, dt.date(2022, 1, 1))
    u2 = book.register_unit('U2', CMUnitType.DEMAND_RESPONSE, 2000.0, dt.date(2022, 1, 1))
    book.add_obligation(u1, 2022, AuctionType.T4)
    book.add_obligation(u2, 2022, AuctionType.T1)
    assert book.total_derated_kw(2022) == pytest.approx(5000.0)


def test_cm_summary():
    book = CapacityMarketBook()
    unit = book.register_unit('U1', CMUnitType.OCGT, 50_000.0, dt.date(2022, 1, 1))
    book.add_obligation(unit, 2022, AuctionType.T4)
    s = book.cm_summary(2022)
    assert s['obligations'] == 1
    assert s['total_derated_kw'] == pytest.approx(50_000.0)


# --- Phase JX depth tests ---

def test_an_unknown_year_has_no_invented_default():
    """This asserted `== 50.0` until 2026-09-07, pinning an invented fallback as a contract.

    No GB capacity auction ever cleared at GBP50/kW. The old lookup ended `.get(year, 50.0)`, so
    every delivery year outside its ten keys priced there silently -- and a test asserting the
    fallback made removing it look like a breaking change instead of a repair.
    """
    assert get_cm_price(9999, AuctionType.T4) is None
    assert get_cm_price(1066, AuctionType.T4) is None


def test_the_cheapest_t4_in_the_record_is_a_price_and_not_a_zero():
    """This asserted `get_cm_price(2021) == 0.0` on a comment reading "No T4 cleared in some years".

    The T-4 for delivery year 2021/22 cleared at GBP8.40/kW -- the cheapest of the whole record,
    against post-buildout excess capacity, but a real auction with a real price. The comment
    described the opposite of what happened, and the zero it justified would have deleted a
    revenue line rather than refused it. A zero and a `None` are different claims and this is the
    year that separates them.
    """
    assert get_cm_price(2021, AuctionType.T4) == pytest.approx(8.40)


def test_penalty_accumulates_multiple_calls():
    unit = CMUnit('BATT-002', CMUnitType.BATTERY, 5000.0, dt.date(2022, 1, 1))
    o = CMObligation(unit, 2022, AuctionType.T4, 75.0)
    o.apply_penalty(10_000.0)
    o.apply_penalty(5_000.0)
    assert o.penalties_gbp == pytest.approx(15_000.0)


def test_total_revenue_empty_year():
    book = CapacityMarketBook()
    unit = book.register_unit('U1', CMUnitType.CCGT, 10_000.0, dt.date(2022, 1, 1))
    book.add_obligation(unit, 2022, AuctionType.T4)
    assert book.total_revenue_gbp(2023) == pytest.approx(0.0)


def test_obligations_for_year_filters_correctly():
    book = CapacityMarketBook()
    u1 = book.register_unit('U1', CMUnitType.BATTERY, 1000.0, dt.date(2022, 1, 1))
    u2 = book.register_unit('U2', CMUnitType.DEMAND_RESPONSE, 2000.0, dt.date(2022, 1, 1))
    book.add_obligation(u1, 2022, AuctionType.T4)
    # DY 2023/24's T-1 is CONTESTED in the published record (Ofgem's annex says GBP60, Montel says
    # GBP45), so it refuses -- the price is supplied here because this test is about year
    # filtering, not about pricing.
    book.add_obligation(u2, 2023, AuctionType.T1, clearing_price=45.00)
    assert len(book.obligations_for_year(2022)) == 1
    assert len(book.obligations_for_year(2023)) == 1


# --- Phase MO depth tests ---

def test_unit_id_stored():
    unit = CMUnit("DR-001", CMUnitType.DEMAND_RESPONSE, 5000.0, dt.date(2022, 1, 1))
    assert unit.unit_id == "DR-001"


def test_unit_type_stored():
    unit = CMUnit("DR-001", CMUnitType.DEMAND_RESPONSE, 5000.0, dt.date(2022, 1, 1))
    assert unit.unit_type == CMUnitType.DEMAND_RESPONSE


def test_unit_derated_capacity_stored():
    unit = CMUnit("DR-001", CMUnitType.DEMAND_RESPONSE, 5000.0, dt.date(2022, 1, 1))
    assert unit.derated_capacity_kw == pytest.approx(5000.0)


def test_unit_registered_date_stored():
    d = dt.date(2022, 3, 15)
    unit = CMUnit("DR-001", CMUnitType.DEMAND_RESPONSE, 5000.0, d)
    assert unit.registered_date == d


def test_obligation_is_prequalified_default_true():
    unit = CMUnit("BATT-001", CMUnitType.BATTERY, 10000.0, dt.date(2022, 1, 1))
    o = CMObligation(unit, 2022, AuctionType.T4, 75.0)
    assert o.is_prequalified is True


def test_obligation_auction_type_stored():
    unit = CMUnit("BATT-001", CMUnitType.BATTERY, 10000.0, dt.date(2022, 1, 1))
    o = CMObligation(unit, 2022, AuctionType.T1, 75.0)
    assert o.auction_type == AuctionType.T1


def test_cm_unit_type_has_6_members():
    assert len(list(CMUnitType)) == 6


def test_auction_type_has_2_members():
    assert len(list(AuctionType)) == 2


def test_register_unit_returns_cm_unit():
    book = CapacityMarketBook()
    result = book.register_unit("U1", CMUnitType.CCGT, 50000.0, dt.date(2022, 1, 1))
    assert isinstance(result, CMUnit)


def test_cm_summary_has_clearing_price_key():
    book = CapacityMarketBook()
    unit = book.register_unit("U1", CMUnitType.OCGT, 50000.0, dt.date(2022, 1, 1))
    book.add_obligation(unit, 2022, AuctionType.T4)
    s = book.cm_summary(2022)
    # BOTH auctions are named on the summary. The single `clearing_price_gbp_per_kw` key this
    # replaced was already choosing between two prices 11.6x apart, and printing the choice as
    # though the delivery year had one price.
    assert s["clearing_price_gbp_per_kw_t4"] == pytest.approx(6.44)
    assert s["clearing_price_gbp_per_kw_t1"] == pytest.approx(75.0)
    assert "clearing_price_gbp_per_kw" not in s, (
        "the un-suffixed key is the conflation this repair removed; a caller reading it would "
        "silently get one auction's price for a delivery year that had two"
    )
