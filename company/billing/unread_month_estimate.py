"""The estimate a supplier bills for a month no read arrived for, shaped by the season.

D48 slice 3. The estimate used to be flat across the year: the last three actual reads' kWh over
their days, times this period's days. Graded against the reads that later closed each run
(`company/billing/billing_accuracy.estimated_billing_outstanding_grade`, slice 2), a run open at a
December month end had been estimated from autumn use and under-billed: +10% of billed kWh for
electricity and +24% for gas, pooled over the decade's year ends. At June it over-billed gas by 26%.
The bias was the estimator's, and it sat in every period-end position and in what the customer paid.

THE METHOD IS THE INDUSTRY'S, NOT OURS. Settlement turns a meter advance into an annual rate by
dividing it by the profile weight of the days it covers (Elexon's EAC from an advance and the
profile coefficients; Xoserve's AQ against the end-user category's annual load profile), and
spreads that rate back over any other days by their weight. A bill estimate done the same way is a
trailing window's actual kWh over the window's summed weight, times this period's summed weight.
With every month weighted equally it is exactly the old pro-rata-by-day estimate, which is the
control that the shape is the only thing that changed.

WHAT THE COMPANY KNOWS. Its own confirmed actual reads and their periods, and a published shape.
Nothing here reads the household's consumption for the month being estimated. The shape is
seasonal normal: the published method weather-corrects settlement, not the customer's estimate,
and the company holds no weather feed for billing.

Sources and the gaps they leave: `docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md`.
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta

from company.billing.annual_consumption_estimate import estimate_annual_consumption

__all__ = [
    "MONTHLY_SHARE_OF_ANNUAL_USE",
    "annualised_advance_kwh",
    "estimate_unread_kwh",
    "opening_estimate_kwh",
    "profile_weight",
]


def _normalised(percentages: tuple[float, ...]) -> tuple[float, ...]:
    total = sum(percentages)
    return tuple(p / total for p in percentages)


# Share of a year's domestic use falling in each calendar month, January first, each summing to 1.
# DESNZ Energy Trends 5.5 ("Domestic sales") and 4.2 ("Domestic"), 2023-2025 averaged: the
# published stand-ins for Elexon's Profile Class 1 and Xoserve's EUC01B load profile, which are
# gated to settlement parties. Two differences are carried, not hidden: they are actual weather,
# not seasonal normal, and they are later than most of the run. Every supplier held the industry
# profile throughout 2016-2025, so the shape is knowledge in kind; these numbers are its proxy.
MONTHLY_SHARE_OF_ANNUAL_USE: dict[str, tuple[float, ...]] = {
    "electricity": _normalised(
        (10.81, 8.87, 9.12, 8.14, 7.25, 6.73, 6.78, 6.96, 7.30, 8.18, 9.65, 10.22)),
    "gas": _normalised(
        (17.05, 13.42, 12.30, 7.87, 4.10, 2.61, 2.33, 2.29, 3.43, 7.13, 12.24, 15.22)),
}


def _day_weight(fuel: str, day: date) -> float:
    share = MONTHLY_SHARE_OF_ANNUAL_USE[fuel][day.month - 1]
    return share / calendar.monthrange(day.year, day.month)[1]


def profile_weight(fuel: str, start: date, end: date) -> float:
    """The share of a year's use the days `start`..`end` (both included) carry."""
    total, day = 0.0, start
    while day <= end:
        total += _day_weight(fuel, day)
        day += timedelta(days=1)
    return total


def estimate_unread_kwh(
    fuel: str, window: list[tuple[date, date, float]], start: date, end: date
) -> float | None:
    """kWh to bill for `start`..`end` from the actual-read `window` of (start, end, kWh) periods.

    None when the window is empty or the fuel has no published shape: the caller then keeps the
    estimate it already had, and the reason is the absence, not a number standing in for one.
    """
    if fuel not in MONTHLY_SHARE_OF_ANNUAL_USE:
        return None
    weight = sum(profile_weight(fuel, s, e) for s, e, _ in window)
    if weight <= 0:  # no read yet
        return None
    return sum(kwh for _, _, kwh in window) / weight * profile_weight(fuel, start, end)


#: The shortest advance annualised. Elexon's EAC calculation (BSCP504) and Xoserve's AQ review both
#: work from a meter advance between two actual reads; an advance under half a year leans on the
#: profile for most of the year it claims to describe, which is the weakness the three-read window
#: above was measured to have (6.3% / 7.5% median error,
#: docs/staging/SEAT_FINDING_THE_COMPANY_HOLDS_SIX_CONSUMPTION_FORECASTS_AND_THE_WORLD_IS_TOO_STEADY_TO_RANK_THEM_2026-10-11.md).
MIN_ADVANCE_DAYS = 182
#: ...and the longest: two years, so a hard-to-read household still has an advance to annualise.
MAX_ADVANCE_DAYS = 731


def annualised_advance_kwh(
    fuel: str, register_reads: list[tuple[date, float]]
) -> tuple[float, date, date] | None:
    """The annual rate the company's own actual reads imply: (kWh a year, from, to).

    `register_reads` are (read date, register kWh) for reads that ARRIVED, the register counting
    use through the end of that day. The latest read closes the advance; it opens on the earlier
    read whose span is nearest a year within `MIN_ADVANCE_DAYS`..`MAX_ADVANCE_DAYS`. The advance is
    divided by the profile weight of the days it covers -- the industry's EAC/AQ-from-an-advance.

    None when no pair of reads spans long enough, or the fuel has no published shape: the caller
    then holds the registry figure, and the absence is the reason.
    """
    if fuel not in MONTHLY_SHARE_OF_ANNUAL_USE or len(register_reads) < 2:
        return None
    reads = sorted(register_reads)
    closing_day, closing_kwh = reads[-1]
    spans = [(abs((closing_day - d).days - 365), d, kwh) for d, kwh in reads[:-1]
             if MIN_ADVANCE_DAYS <= (closing_day - d).days <= MAX_ADVANCE_DAYS]
    if not spans:
        return None
    _, opening_day, opening_kwh = min(spans)
    weight = profile_weight(fuel, opening_day + timedelta(days=1), closing_day)
    if weight <= 0:
        return None
    return (closing_kwh - opening_kwh) / weight, opening_day, closing_day


def opening_estimate_kwh(
    fuel: str, registration: dict | None, start: date, end: date
) -> float | None:
    """kWh to bill for `start`..`end` before the account's first actual read (D48 slice 4).

    The company holds no read of its own yet, so it bills the annual figure it was handed on
    registration (EAC for electricity, AQ for gas) spread over the year by the published shape:
    the same EAC/AQ-against-a-profile step `estimate_unread_kwh` takes from its own reads. Where
    registration carried no figure, Ofgem's TDCV MEDIUM band in force on `start` stands in, as it
    does for the opening direct debit (`simulation/run_phase4c_on_phase2b._opening_dd_by_customer`).

    None when the fuel has no published shape or no annual figure is established.
    """
    if fuel not in MONTHLY_SHARE_OF_ANNUAL_USE:
        return None
    registration = registration or {}
    registry = registration.get("eac_kwh" if fuel == "electricity" else "aq_kwh")
    annual = estimate_annual_consumption(
        as_of=start, commodity=fuel,
        registry_eac_kwh=float(registry) if registry else None,
        band=None if registry else "MEDIUM",
    )
    if annual.kwh is None:
        return None
    return annual.kwh * profile_weight(fuel, start, end)
