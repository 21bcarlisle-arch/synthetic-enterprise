"""D48 slices 3-4: the unread month is estimated by the company alone -- from its own reads, shaped by
the season, or before its first read from the registry EAC/AQ spread by the same shape."""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass

import pytest

from company.billing import unread_month_estimate as U
from company.billing.monthly_bill_assembly import build_monthly_bills

D = dt.date
AUTUMN = [(D(2023, 9, 1), D(2023, 9, 30), 230.0), (D(2023, 10, 1), D(2023, 10, 31), 260.0),
          (D(2023, 11, 1), D(2023, 11, 30), 290.0)]
SPRING = [(D(2024, 3, 1), D(2024, 3, 31), 290.0), (D(2024, 4, 1), D(2024, 4, 30), 260.0),
          (D(2024, 5, 1), D(2024, 5, 31), 230.0)]


def _flat(window, start, end):
    days = sum((e - s).days + 1 for s, e, _ in window)
    return sum(k for _, _, k in window) / days * ((end - start).days + 1)


def test_with_every_day_weighted_alike_the_estimate_is_the_old_pro_rata_by_day(monkeypatch):
    """Defect caught: a shaped estimator that also changes the level. With equal day weights it
    must reproduce the flat estimate it replaced, so the shape is the only thing it changed."""
    flat = tuple(calendar.monthrange(2023, m)[1] / 365 for m in range(1, 13))
    monkeypatch.setattr(U, "MONTHLY_SHARE_OF_ANNUAL_USE", {"electricity": flat})
    assert U.estimate_unread_kwh("electricity", AUTUMN, D(2023, 12, 1), D(2023, 12, 31)) == (
        pytest.approx(_flat(AUTUMN, D(2023, 12, 1), D(2023, 12, 31))))


def test_the_estimate_follows_the_season_both_ways_for_both_fuels():
    """Defect caught: a shape that only lifts (or only lowers). From autumn reads December is billed
    above the flat estimate; from spring reads June is billed below it."""
    dec, jun = (D(2023, 12, 1), D(2023, 12, 31)), (D(2024, 6, 1), D(2024, 6, 30))
    moves = {fuel: (U.estimate_unread_kwh(fuel, AUTUMN, *dec) / _flat(AUTUMN, *dec),
                    U.estimate_unread_kwh(fuel, SPRING, *jun) / _flat(SPRING, *jun))
             for fuel in ("electricity", "gas")}
    assert all(up > 1.05 and down < 0.95 for up, down in moves.values()), moves
    # Gas swings harder than electricity, as the published shapes do.
    assert moves["gas"][0] > moves["electricity"][0] and moves["gas"][1] < moves["electricity"][1]


def test_each_published_shape_is_a_whole_year_peaking_in_winter():
    for fuel, shares in U.MONTHLY_SHARE_OF_ANNUAL_USE.items():
        assert len(shares) == 12 and sum(shares) == pytest.approx(1.0), fuel
        assert min(shares[0], shares[11]) > max(shares[5], shares[6]), fuel


def test_with_no_read_or_no_shape_there_is_no_estimate_rather_than_a_guess():
    dec = (D(2023, 12, 1), D(2023, 12, 31))
    assert U.estimate_unread_kwh("electricity", [], *dec) is None
    assert U.estimate_unread_kwh("hydrogen", AUTUMN, *dec) is None


# --- wired into the company's billing run --------------------------------------------------------

# A figure no feed now sends (the world's feed reports status only). Scripted here so that billing
# it anywhere is visible: the company must never price a bill on a number it did not make.
FEED_ESTIMATE_KWH = 999.0


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    """Actual reads Sep-Nov 2023 for C1, estimates after; C2 is estimated from its opening month."""

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if customer_id == "C1" and period_end < "2023-12":
            return _Read("actual", None, 0)
        return _Read("estimated", FEED_ESTIMATE_KWH, consecutive + 1)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh):
        return _Read("actual", None, 0)


def _month(cid, year, month, kwh):
    days = calendar.monthrange(year, month)[1]
    return [{"customer_id": cid, "settlement_date": f"{year}-{month:02d}-{d:02d}",
             "settlement_period": 1, "consumption_kwh": kwh / days,
             "unit_rate_gbp_per_mwh": 200.0, "revenue_gbp": kwh / days / 1000 * 200.0 + 0.5,
             "standing_charge_gbp": 0.5, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0}
            for d in range(1, days + 1)]


def test_the_billing_run_bills_only_its_own_estimate_from_its_reads_and_before_them_from_registry():
    """Defect caught, both ways at once: an estimator built and never reached (December would bill
    the feed's figure), and an opening month billed on anything but the registration figure -- the
    feed's number, or the household's true use, which is what the world's feed used to send."""
    from company.interfaces.supply_book import registered_point

    records = (_month("C1", 2023, 9, 230.0) + _month("C1", 2023, 10, 260.0)
               + _month("C1", 2023, 11, 290.0) + _month("C1", 2023, 12, 400.0)
               + _month("C2", 2023, 12, 400.0))
    events: list = []
    bills = build_monthly_bills(records, _Feed(), read_events_out=events)
    by = {(b["customer_id"], b["period_end"][:7]): (b, e) for b, e in zip(bills, events)}
    c1_dec, c1_event = by[("C1", "2023-12")]
    c2_dec, c2_event = by[("C2", "2023-12")]
    dec = (D(2023, 12, 1), D(2023, 12, 31))
    shaped = U.estimate_unread_kwh("electricity", AUTUMN, *dec)
    opening = U.opening_estimate_kwh("electricity", registered_point("C2"), *dec)

    assert (c1_dec["billing_basis"] == c2_dec["billing_basis"] == "estimated"
            and c1_dec["total_consumption_kwh"] == pytest.approx(shaped, abs=0.01)
            and c2_dec["total_consumption_kwh"] == pytest.approx(opening, abs=0.01)
            and opening not in (pytest.approx(400.0, abs=1), FEED_ESTIMATE_KWH)), (c1_dec, c2_dec)
    # The published read log carries the estimate each bill was priced on, not the feed's.
    assert c1_event.estimated_consumption_kwh == round(shaped, 2)
    assert c2_event.estimated_consumption_kwh == round(opening, 2)


def test_the_opening_estimate_is_the_registry_figure_spread_by_the_shape_and_tdcv_without_one():
    """Defect caught: an opening estimate that reads the wrong registry field for the fuel, or that
    returns a guess (or nothing) where registration carried no figure."""
    year = (D(2023, 1, 1), D(2023, 12, 31))
    jan = (D(2023, 1, 1), D(2023, 1, 31))
    assert U.opening_estimate_kwh("electricity", {"eac_kwh": 2600.0}, *year) == pytest.approx(2600.0)
    assert U.opening_estimate_kwh("gas", {"eac_kwh": 1.0, "aq_kwh": 11000.0}, *year) == (
        pytest.approx(11000.0))
    # Ofgem's TDCV MEDIUM in force on the period start (2,900 kWh from 1 Apr 2020).
    assert U.opening_estimate_kwh("electricity", {}, *year) == pytest.approx(2900.0)
    assert U.opening_estimate_kwh("electricity", {"eac_kwh": 2600.0}, *jan) == pytest.approx(
        2600.0 * U.MONTHLY_SHARE_OF_ANNUAL_USE["electricity"][0])
    assert U.opening_estimate_kwh("hydrogen", {"eac_kwh": 2600.0}, *year) is None


def test_a_seven_day_stub_after_a_month_is_billed_a_week_not_a_month():
    """Defect caught (carried over from the world's retired estimator, 2026-09-27 run: 736 kWh
    billed on a 7-day stub that used 42): the estimate is spread by days, not per bill."""
    window = [(D(2024, 6, 1), D(2024, 6, 30), 300.0)]
    stub = U.estimate_unread_kwh("electricity", window, D(2024, 7, 1), D(2024, 7, 7))
    assert 60.0 < stub < 80.0, stub
