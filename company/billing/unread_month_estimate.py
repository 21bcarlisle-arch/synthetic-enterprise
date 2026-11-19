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
    "BSC_BLEND_PROFILE_CLASSES",
    "ECONOMY_7_REGISTERS",
    "MONTHLY_SHARE_OF_ANNUAL_USE",
    "PC2_MONTHLY_REGISTER_SHARE",
    "annualised_advance_kwh",
    "annualised_register_advance_kwh",
    "blend_advances_into_eac",
    "bsc_blended_eac_kwh",
    "estimate_unread_kwh",
    "estimate_unread_register_kwh",
    "opening_estimate_kwh",
    "opening_register_estimate_kwh",
    "profile_weight",
    "refuse_spar_outside_the_range",
    "register_profile_weight",
    "SPAR_WEIGHT_RATE_STATED_RANGE",
    "split_on_register_shape",
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


ECONOMY_7_REGISTERS = ("day", "night")

# A Profile Class 2 ("Domestic Economy 7") meter's year, per calendar month and per register, January
# first; the 24 shares sum to 1. UKERC's verbatim `ProfileClass2.csv` (Electricity Association via
# Elexon, the 1997 Group Average Demand table; SHA-256 08457653...e60b, docs/data-sources/profile-class-2.md),
# run through the BSC season calendar for every day of 2016-2025, split at the Night register's
# 00:30-07:30 and averaged over the ten calendars (each month within 0.33 points of the mean). The
# same published table the industry settles a PC2 meter on, copied as knowledge, not read from the
# world. Night is the seasonal register: January 4.1 times August, against PC1's 1.4. Table and GAPs:
# docs/market_research/a_storage_heated_homes_default_tariff_is_two_rate.md.
PC2_MONTHLY_REGISTER_SHARE: dict[str, tuple[float, ...]] = dict(zip(ECONOMY_7_REGISTERS, (
    _normalised(
        (5.564, 5.077, 5.395, 4.172, 3.943, 3.603, 3.693, 3.627, 4.143, 4.508, 5.381, 5.566)
        + (5.930, 5.413, 5.637, 3.557, 2.631, 1.910, 1.798, 1.438, 2.373, 2.974, 5.738, 5.929)
    )[i * 12:(i + 1) * 12] for i in range(2))))


def _weight(shares: tuple[float, ...], start: date, end: date) -> float:
    total, day = 0.0, start
    while day <= end:
        total += shares[day.month - 1] / calendar.monthrange(day.year, day.month)[1]
        day += timedelta(days=1)
    return total


def profile_weight(fuel: str, start: date, end: date) -> float:
    """The share of a year's use the days `start`..`end` (both included) carry."""
    return _weight(MONTHLY_SHARE_OF_ANNUAL_USE[fuel], start, end)


def register_profile_weight(register: str, start: date, end: date) -> float:
    """The share of a PC2 meter's year that `register` records over `start`..`end` (both included)."""
    return _weight(PC2_MONTHLY_REGISTER_SHARE[register], start, end)


def split_on_register_shape(annual_kwh: float, start: date, end: date) -> dict[str, float]:
    """An annual figure for a PC2 meter's total, spread over `start`..`end` per register on PC2's shape.

    For the figures the company holds only as a total: the registration EAC (page GAP G7) and an
    annualised advance off the total register log (G8).
    """
    return {r: annual_kwh * register_profile_weight(r, start, end) for r in ECONOMY_7_REGISTERS}


def estimate_unread_kwh(
    fuel: str, window: list[tuple[date, date, float]], start: date, end: date
) -> float | None:
    """kWh to bill for `start`..`end` from the actual-read `window` of (start, end, kWh) periods.

    None when the window is empty, the fuel has no published shape, or the window's reads advanced
    by nothing: the caller then falls back to the registry figure, and the reason is the absence,
    not a number standing in for one. A zero advance is a missing measurement, as a zero registry
    EAC is (`estimate_annual_consumption`), never a household that uses nothing: an occupier's 0 kWh
    move-in month estimated every month after it at 0 kWh (10 of the 11 runs breaching
    INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER on the 1a02c46116 book).
    """
    if fuel not in MONTHLY_SHARE_OF_ANNUAL_USE:
        return None
    weight = sum(profile_weight(fuel, s, e) for s, e, _ in window)
    used = sum(kwh for _, _, kwh in window)
    if weight <= 0 or used <= 0:  # no read yet, or reads that measured nothing
        return None
    return used / weight * profile_weight(fuel, start, end)


def estimate_unread_register_kwh(
    window: list[tuple[date, date, dict[str, float]]], start: date, end: date
) -> dict[str, float] | None:
    """kWh per register to bill a PC2 meter for `start`..`end` from its actual-read `window`.

    `estimate_unread_kwh` applied to each register on its own PC2 share: each register's advance over
    its own weight, times this period's weight. A storage home's Night register carries its winter
    heat, and PC2 gives a summer night a quarter of a winter one, so winter night use is no longer
    spread into a summer month at the total's shape (the E2 (a) over-estimates).

    None when the meter's total advanced by nothing, the same missing measurement as there. A
    register that advanced by nothing while the other moved was read, so it estimates 0.
    """
    if sum(kwh for _, _, by_register in window for kwh in by_register.values()) <= 0:
        return None
    estimate = {}
    for register in ECONOMY_7_REGISTERS:
        weight = sum(register_profile_weight(register, s, e) for s, e, _ in window)
        used = sum(by_register.get(register, 0.0) for _, _, by_register in window)
        estimate[register] = used / weight * register_profile_weight(register, start, end)
    return estimate


def annualised_register_advance_kwh(
    window: list[tuple[date, date, dict[str, float]]], opening_day: date, closing_day: date,
    start: date, end: date,
) -> dict[str, float] | None:
    """An annualised advance on a PC2 meter, per register: each register's own advance from
    `opening_day` to `closing_day` (the span `annualised_advance_kwh` chose) over its own PC2 weight,
    times this period's weight. Settlement gives each register of a two-rate meter its own EAC
    (a_storage_heated_homes_default_tariff_is_two_rate.md, G7/G8).

    Spreading the annualised TOTAL on PC2's register shares instead billed a storage home's summer
    at PC2's 45% Night when its reads said 95%: PROS-2017-0336's June 2018 Day at 1,375 kWh against
    about 210 read, 18 INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS breaches on the 65bbdc6787 book.

    None unless the read periods in `window` tile the span exactly: then the company holds the total
    only, and the caller keeps `split_on_register_shape`.
    """
    span = sorted((s, e, by) for s, e, by in window if s > opening_day and e <= closing_day)
    day = opening_day + timedelta(days=1)
    for s, e, _ in span:
        if s != day:
            return None
        day = e + timedelta(days=1)
    if not span or day != closing_day + timedelta(days=1):
        return None
    return estimate_unread_register_kwh(span, start, end)


#: The shortest advance annualised. Elexon's EAC calculation (BSCP504) and Xoserve's AQ review both
#: work from a meter advance between two actual reads; an advance under half a year leans on the
#: profile for most of the year it claims to describe, which is the weakness the three-read window
#: above was measured to have (6.3% / 7.5% median error,
#: docs/staging/SEAT_FINDING_THE_COMPANY_HOLDS_SIX_CONSUMPTION_FORECASTS_AND_THE_WORLD_IS_TOO_STEADY_TO_RANK_THEM_2026-10-11.md).
#: UNSOURCED as a HOLD on the bill estimate. The six months is DESNZ's line for an AA, and the settlement
#: EAC has no hold: it blends every advance by min(1, FYC*SPAR) (BSC Annex S-2 4.3.7). The one supplier
#: found bills from that EAC. It stays because the alternative needs SPAR, which is Market Domain Data
#: under licence and is published nowhere (searched 2026-11-19). At SPAR -> 0 the blend is this hold;
#: at SPAR -> infinity it re-opens E1's short-first-month breaches. The hold over-bills new accounts
#: (D48: billed/true 1.15), which errs against our own thesis. The search and the route to removing it:
#: docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md section 8.
MIN_ADVANCE_DAYS = 182
#: ...and the longest: two years, so a hard-to-read household still has an advance to annualise.
MAX_ADVANCE_DAYS = 731
#: Gas's own floor, nine months: Xoserve's AQ is "based on the consumption between two meter readings
#: [9-36 months apart]" (Xoserve, *Annual Quantity (AQ)* help page; unbilled_energy_and_revenue_assurance.md
#: K2, design choice 1). Read only where the bill run's switch asks for it; `MIN_ADVANCE_DAYS` otherwise.
GAS_AQ_MIN_ADVANCE_DAYS = 273


def annualised_advance_kwh(
    fuel: str, register_reads: list[tuple[date, float]], min_advance_days: int = MIN_ADVANCE_DAYS,
) -> tuple[float, date, date] | None:
    """The annual rate the company's own actual reads imply: (kWh a year, from, to).

    `register_reads` are (read date, register kWh) for reads that ARRIVED, the register counting
    use through the end of that day. The latest read closes the advance; it opens on the earlier
    read whose span is nearest a year within `min_advance_days`..`MAX_ADVANCE_DAYS`. The advance is
    divided by the profile weight of the days it covers -- the industry's EAC/AQ-from-an-advance.

    None when no pair of reads spans long enough, or the fuel has no published shape: the caller
    then holds the registry figure, and the absence is the reason.
    """
    if fuel not in MONTHLY_SHARE_OF_ANNUAL_USE or len(register_reads) < 2:
        return None
    reads = sorted(register_reads)
    closing_day, closing_kwh = reads[-1]
    spans = [(abs((closing_day - d).days - 365), d, kwh) for d, kwh in reads[:-1]
             if min_advance_days <= (closing_day - d).days <= MAX_ADVANCE_DAYS]
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
    annual = _registration_annual_kwh(fuel, registration, start)
    return None if annual is None else annual * profile_weight(fuel, start, end)


def opening_register_estimate_kwh(
    registration: dict | None, start: date, end: date
) -> dict[str, float] | None:
    """`opening_estimate_kwh` for a PC2 meter: the same annual figure, spread per register on PC2's
    shape. Registration hands over one EAC, not one per register (page GAP G7)."""
    annual = _registration_annual_kwh("electricity", registration, start)
    return None if annual is None else split_on_register_shape(annual, start, end)


#: SPAR, the BSC smoothing parameter, carried as the stated range [low, high] and never as a point.
#: Its value is Market Domain Data under licence and is published nowhere (Elexon EAC/AA URS v13.0
#: s6.2.6; searched 2026-11-19). The range is what the evidence supports: on the 6af7fd0bfd book the
#: electricity gap falls at every SPAR from 0.5 to 4, and E1's breach and flag sets are those of the
#: hold at each one. E1 re-opens between 4 and 6. Table and predictions:
#: docs/staging/records/SEAT_PREREG_D48_E1_BREACHES_AT_EACH_SPAR_2026-11-19.md. Why a range:
#: docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md section 8.
SPAR_WEIGHT_RATE_STATED_RANGE = (0.5, 3.0)
#: The blend moves only these profile classes: single-register NHH meters (BSC PC1 domestic, PC3
#: non-domestic). PC2 is estimated per register, a separate question (D48 route prereg).
BSC_BLEND_PROFILE_CLASSES = (1, 3)


def refuse_spar_outside_the_range(spar: float) -> None:
    """Raise, naming the reason, unless `spar` lies in `SPAR_WEIGHT_RATE_STATED_RANGE`."""
    low, high = SPAR_WEIGHT_RATE_STATED_RANGE
    if not low <= spar <= high:
        raise ValueError(
            f"SPAR {spar} is outside the stated range [{low}, {high}]: SPAR's value is a GAP, and the "
            "range is the span over which E1's guard was shown unchanged (D48 E1 prereg)")


def bsc_blended_eac_kwh(
    fuel: str, registration: dict | None,
    advances: list[tuple[date, date, float]], spar: float, as_of: date,
) -> float | None:
    """The EAC the data collector would send on the D0019: the registration EAC with each of the
    company's own read `advances` (from, to, kWh) blended in by BSC Annex S-2 s4.3.7,
    `EAC <- w*advance/FYC + (1-w)*EAC`, `w = min(1, FYC*SPAR)`, oldest first.

    `spar` must lie in `SPAR_WEIGHT_RATE_STATED_RANGE`. A value outside it is refused, because
    the range is the only part of SPAR the evidence supports. A zero advance does not move the EAC:
    it is a missing measurement (`estimate_unread_kwh`). `as_of` dates the registration figure,
    as `opening_estimate_kwh` does.

    None when the fuel is not electricity (the gas AQ is not smoothed this way) or no
    registration figure is established. The caller then keeps the hold.
    """
    refuse_spar_outside_the_range(spar)
    if fuel != "electricity":
        return None
    eac = _registration_annual_kwh(fuel, registration, as_of)
    return None if eac is None else blend_advances_into_eac(fuel, eac, advances, spar)


def blend_advances_into_eac(
    fuel: str, eac: float, advances: list[tuple[date, date, float]], spar: float,
) -> float:
    """BSC Annex S-2 s4.3.7 applied to each advance in turn, from `eac`: the step alone, with no
    range check. The D48 harness sweeps SPAR past the range through this same step."""
    for start, end, kwh in advances:
        fyc = profile_weight(fuel, start, end)
        if kwh <= 0 or fyc <= 0:
            continue
        w = min(1.0, fyc * spar)
        eac = w * kwh / fyc + (1 - w) * eac
    return eac


def _registration_annual_kwh(fuel: str, registration: dict | None, as_of: date) -> float | None:
    registration = registration or {}
    registry = registration.get("eac_kwh" if fuel == "electricity" else "aq_kwh")
    return estimate_annual_consumption(
        as_of=as_of, commodity=fuel,
        registry_eac_kwh=float(registry) if registry else None,
        band=None if registry else "MEDIUM",
    ).kwh
