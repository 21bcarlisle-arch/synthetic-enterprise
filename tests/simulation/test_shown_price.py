"""The price a household is SHOWN is not the price it pays, and the decision keys on the first.

WHAT EACH TEST HERE NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_the_shown_bill_does_not_depend_on_the_households_own_volume` — THE ONE-LINE STATEMENT OF
    WHAT C3 DOES, and the defect is the world before it: the switching decision was scaled by the
    household's own settled trailing-year bill, a number only its supplier holds. Two households
    on the identical tariff and different consumption must now be shown the same annual figure,
    because that is what a comparison listing puts in front of them.
  * `test_the_shown_bill_keeps_the_households_own_RATE` — the opposite defect, and the one that
    would make C3 meaningless: showing everybody the same bill regardless of tariff. The volume is
    typical; the price is theirs. A dearer household must be shown a bigger number.
  * `test_an_unknown_volume_REFUSES_rather_than_inventing_a_typical_bill` — a household whose
    trailing window carries no volume has no shown price, and the caller's fallback is the
    market-average scale, which is the pre-C3 behaviour. Inventing one would put a fabricated
    number into a churn decision.
  * `test_an_unrecognised_fuel_REFUSES_rather_than_pricing_it_as_ABSENT` — the fail-open shape.
    Silently dropping a fuel with no published TDCV would show a dual-fuel household a
    single-fuel saving and understate what it is choosing over, which makes it stickier — a
    move in the company's favour arrived at by an omission.
  * `test_the_per_fuel_split_and_the_published_dual_fuel_total_cannot_diverge` — one name and two
    numbers, this repository's most-repeated published defect. The check is at IMPORT, so a split
    that stops summing to `competitor_reference.TDCV_DUAL_FUEL_MWH` cannot even be loaded.
  * `test_the_pounds_and_the_kwh_are_counted_over_the_SAME_records` — the ratio defect in its own
    right. `_annual_bill_and_volume` exists as one pass precisely so the numerator and denominator
    cannot come to count different populations; two walkers with independently-drifting filters
    would produce a ratio that is not a quantity.
  * `test_the_fuels_come_from_what_was_SETTLED_not_from_the_roster` — a roster saying dual-fuel
    while only the electricity leg billed would show the household a typical volume it never took.

R15 MUTATIONS, each applied in place and reverted, with the OBSERVED result recorded:
  * `shown_annual_bill_gbp` returns `billed_gbp` unchanged (i.e. C3 undone) -> **2 red**
    (`..._does_not_depend_on_the_households_own_volume`, `..._keeps_the_households_own_RATE`
    survives because the rate is still carried — recorded rather than assumed).
  * `typical_consumption_kwh` drops the `issubset` check, so an unknown fuel is priced as absent
    -> **1 red** (`..._REFUSES_rather_than_pricing_it_as_ABSENT`).
  * `shown_annual_bill_gbp` treats a zero volume as 1.0 instead of refusing -> **1 red**
    (`..._REFUSES_rather_than_inventing_a_typical_bill`).
  * `_annual_bill_and_volume` sums kWh over ALL of the household's records rather than the window
    -> **1 red** (`..._counted_over_the_SAME_records`).
  * `TDCV_KWH_BY_FUEL["gas"]` changed to 12000.0 -> **ImportError at collection**, which is the
    import guard doing its job; recorded as such rather than as a test failure.
"""
from __future__ import annotations

import pytest

from simulation.competitor_reference import TDCV_DUAL_FUEL_MWH
from simulation.customer_events import _annual_bill_and_volume, _annual_bill_gbp
from simulation.shown_price import (
    TDCV_KWH_BY_FUEL,
    shown_annual_bill_gbp,
    typical_consumption_kwh,
)


def _rec(cid, day, gbp, kwh):
    return {"customer_id": cid, "settlement_date": day,
            "revenue_gbp": gbp, "consumption_kwh": kwh}


def test_the_shown_bill_does_not_depend_on_the_households_own_volume():
    """Two households, identical tariff, very different consumption, one shown figure.

    The small flat pays £226 a year and the large house £1,130 on the same £127/MWh. Today the
    world scales their switching response by those two numbers. A comparison listing shows them
    both the same thing, and that is what they decide on.
    """
    rate_gbp_per_kwh = 226.0 / 1780.0
    small = shown_annual_bill_gbp(billed_gbp=226.0, billed_kwh=1780.0, fuels={"electricity"})
    large = shown_annual_bill_gbp(billed_gbp=1130.0, billed_kwh=8900.0, fuels={"electricity"})

    assert small == pytest.approx(large), (
        "two households on the same tariff are shown different annual figures, so the decision is "
        "still keyed to consumption only their supplier can see")
    assert small == pytest.approx(rate_gbp_per_kwh * TDCV_KWH_BY_FUEL["electricity"])


def test_the_shown_bill_keeps_the_households_own_RATE():
    """The volume is typical; the price is theirs. Flattening both would make C3 meaningless --
    every household shown one number responds identically and the price signal disappears."""
    cheap = shown_annual_bill_gbp(billed_gbp=200.0, billed_kwh=2000.0, fuels={"electricity"})
    dear = shown_annual_bill_gbp(billed_gbp=400.0, billed_kwh=2000.0, fuels={"electricity"})

    assert dear == pytest.approx(2 * cheap), (
        "a household paying twice the rate is not shown twice the annual figure, so the shown "
        "price has lost the only thing it is supposed to carry")


def test_a_dual_fuel_household_is_shown_the_dual_fuel_typical_volume():
    """The fuels a household took decide which published pair it is compared at. A dual-fuel home
    choosing on a single-fuel figure would be understating what is at stake by most of its bill."""
    assert typical_consumption_kwh({"electricity"}) == 2700.0
    assert typical_consumption_kwh({"gas"}) == 11500.0
    assert typical_consumption_kwh({"electricity", "gas"}) == 14200.0


@pytest.mark.parametrize("kwh", [0.0, None, -5.0])
def test_an_unknown_volume_REFUSES_rather_than_inventing_a_typical_bill(kwh):
    """`None`, and the caller falls back to the market-average scale -- the PRE-C3 behaviour,
    bounded, and wrong only in the way the world was already wrong."""
    assert shown_annual_bill_gbp(
        billed_gbp=500.0, billed_kwh=kwh, fuels={"electricity"}) is None


@pytest.mark.parametrize("fuels", [{"hydrogen"}, {"electricity", "heat"}, set(), None])
def test_an_unrecognised_fuel_REFUSES_rather_than_pricing_it_as_ABSENT(fuels):
    """The fail-open shape, and it moves in the company's favour.

    Dropping a fuel with no published TDCV would show a dual-fuel household a single-fuel saving.
    A smaller perceived saving is a stickier household, and a stickier book earns more -- an
    advantage arrived at by an omission is exactly what R13 exists to stop.
    """
    assert typical_consumption_kwh(fuels) is None
    assert shown_annual_bill_gbp(billed_gbp=500.0, billed_kwh=5000.0, fuels=fuels) is None


def test_the_per_fuel_split_and_the_published_dual_fuel_total_cannot_diverge():
    """One name, two numbers. Held at import so a divergent split cannot be loaded, not by a test
    that could be deleted and not by a comment that could go stale."""
    assert sum(TDCV_KWH_BY_FUEL.values()) == pytest.approx(TDCV_DUAL_FUEL_MWH * 1000.0)


def test_the_pounds_and_the_kwh_are_counted_over_the_SAME_records():
    """The ratio defect in its own right, and the reason this is one pass and not two walkers.

    The window opens twelve months before the term. A record outside it must be absent from BOTH
    the pounds and the kWh; a filter that drifted on one side alone would produce a shown bill
    built from a numerator and a denominator counting different populations.
    """
    records = [
        _rec("C1", "2019-06-01", 100.0, 1000.0),     # inside the window
        _rec("C1", "2020-01-01", 150.0, 1500.0),     # inside the window
        _rec("C1", "2018-01-01", 999.0, 9999.0),     # BEFORE the window -- must not appear
        _rec("C2", "2019-06-01", 500.0, 5000.0),     # a different household
    ]
    billed = _annual_bill_and_volume("C1", records, "2020-06-01")

    assert billed["gbp"] == pytest.approx(250.0)
    assert billed["kwh"] == pytest.approx(2500.0)
    # And the thin wrapper still answers exactly what it always answered, so nothing that reads
    # the trailing bill alone has changed meaning underneath it.
    assert _annual_bill_gbp("C1", records, "2020-06-01") == pytest.approx(250.0)


def test_the_fuels_come_from_what_was_SETTLED_not_from_the_roster():
    """A household whose gas leg billed in the window is dual-fuel for this purpose; one whose gas
    leg did not is not, whatever the roster says. The shown price is built on what was supplied."""
    dual = [_rec("C1", "2020-01-01", 100.0, 1000.0), _rec("C1g", "2020-01-01", 200.0, 8000.0)]
    elec_only = [_rec("C1", "2020-01-01", 100.0, 1000.0)]

    assert _annual_bill_and_volume("C1", dual, "2020-06-01")["fuels"] == {"electricity", "gas"}
    assert _annual_bill_and_volume("C1", elec_only, "2020-06-01")["fuels"] == {"electricity"}
    # The gas leg's pounds and kWh are summed in, which is the household and not the supply point.
    assert _annual_bill_and_volume("C1", dual, "2020-06-01")["kwh"] == pytest.approx(9000.0)


def test_an_empty_trailing_window_is_None_and_not_a_zero_bill():
    """A first renewal with no settled history has no bill to be felt. A zero would be a household
    shown that switching saves it nothing, which is a claim, not an absence."""
    assert _annual_bill_and_volume("C1", [], "2020-06-01") is None
    assert _annual_bill_gbp("C1", [], "2020-06-01") is None
