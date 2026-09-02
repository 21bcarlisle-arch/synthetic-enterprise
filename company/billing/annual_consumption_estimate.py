"""The estimated annual consumption a direct debit is sized from — atom
``D_opening_dd_seasonal_sizing``.

WHY THIS MODULE EXISTS
----------------------
Until now nothing in the direct-debit path estimated anything.
``dd_review_runner`` and ``dd_balance_book`` both opened a customer's standing
DD at ``seq[0][1]`` — **the first issued bill's amount** — which makes the
monthly payment an accident of which month the account happened to start in.
A first bill falling in January over-sizes the DD for the year; one falling in
July under-sizes it. Neither is an annualised plan.

The director's correction, 2026-09-01, verbatim:

    "There's no such thing as a half-month direct debit — an annualised plan
    divides estimated annual cost by twelve whatever the start date. The real
    defect is that the DD is only as good as the estimated annual consumption
    behind it: when that estimate is wrong the account drifts into credit or
    debit, and the correction arrives later as a change the customer didn't
    expect."

So the DD's quality is the *estimate's* quality, and the estimate needs a
source, a precedence and an honest absence. That is this module.

THE DUTY IT IMPLEMENTS
----------------------
**SLC 27.15** (electricity and gas supply licences; strengthened 21 Oct 2022):
the fixed direct debit "must be based on the best and most current information
available (or which reasonably ought to be available) to the licensee."

That sentence is an *ordering* instruction, not a formula, and ``BASIS_ORDER``
below is that ordering made executable. The full establishment — including what
the published record does NOT settle — is
``docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md``.

THE EPISTEMIC WALL
------------------
Every input here is something a real supplier holds:

  * ``metered_annual_kwh`` — the supplier's OWN meter reads. It billed them.
  * ``registry_eac_kwh`` — the EAC (electricity, D0019 flow from the Data
    Collector) or AQ (gas, Xoserve) handed over ON REGISTRATION. This is an
    estimate carrying error, forecast from the last D0010 read — it is NOT the
    household's realised annual usage, and the error it carries is precisely
    the thing that causes the drift the director described.
  * ``declared_annual_kwh`` — what the customer said at sign-up.
  * TDCV — Ofgem's published typical values, the explicit published fallback.

**The household's ground-truth annual consumption is not a parameter of any
function in this module and must never become one.** If a caller finds itself
with true usage and no estimate, the answer is ``None`` with a reason, not the
truth wearing an estimate's name.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
No buffer, no smoothing, no seasonal weighting of the first winter. Real
suppliers do all three; the published record establishes no figure for any of
them, so applying one would be a number picked because a number was needed.
Registered as a gap in the research page, §4.2.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Mapping, Optional


class ConsumptionBasis(str, Enum):
    """Where an annual-consumption estimate came from. Ordered best to worst by
    SLC 27.15's "best and most current information available"."""

    METERED_HISTORY = "metered_history"      # our own reads over a completed period
    REGISTRY_EAC = "registry_eac"            # EAC/AQ handed over at registration
    CUSTOMER_DECLARED = "customer_declared"  # what the customer told us
    TDCV_TYPICAL = "tdcv_typical"            # Ofgem's published fallback
    UNAVAILABLE = "unavailable"              # nothing reachable -- an honest None


#: The SLC 27.15 precedence, executable. Best first.
BASIS_ORDER: tuple[ConsumptionBasis, ...] = (
    ConsumptionBasis.METERED_HISTORY,
    ConsumptionBasis.REGISTRY_EAC,
    ConsumptionBasis.CUSTOMER_DECLARED,
    ConsumptionBasis.TDCV_TYPICAL,
)


# ---------------------------------------------------------------------------
# Ofgem Typical Domestic Consumption Values, keyed by the date they came into
# force. ORIGIN: Ofgem TDCV decision letters, read directly -- 3 Aug 2017
# (effective 1 Oct 2017), 6 Jan 2020 (effective 1 Apr 2020), 25 May 2023
# (effective 1 Oct 2023), 27 May 2026 (effective 1 Jul 2026). The pre-2017 row
# is the "Current TDCVs" column of the 2017 decision. Tabulated with sources in
# docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md §3.
#
# WHY DATE-KEYED AND NOT A SINGLE CONSTANT: this company runs 2016-2025. The
# TDCV in force moved four times across that window, and the value a supplier
# could have used in 2018 is not the one published in 2026. A single "current"
# TDCV would be the company knowing a number that did not exist yet -- an
# epistemic-wall breach wearing a constant's clothes.
#
# NOT the same numbers as population_draw.TDCV_BANDS_KWH and deliberately so:
# that table draws a synthetic POPULATION (a world-building decision inside the
# baseline/curriculum split) and carries only today's bands. Drawing a
# population is not estimating a customer's consumption.
# ---------------------------------------------------------------------------

#: (in_force_from, {commodity: {band: kWh/year}}). Ascending by date.
TDCV_BY_DATE: tuple[tuple[date, Mapping[str, Mapping[str, float]]], ...] = (
    (
        date(2016, 1, 1),  # the series as it stood before the 1 Oct 2017 revision
        {
            "gas": {"LOW": 8000.0, "MEDIUM": 12500.0, "HIGH": 18000.0},
            "electricity": {"LOW": 2000.0, "MEDIUM": 3100.0, "HIGH": 4600.0},
            "electricity_pc2": {"LOW": 2500.0, "MEDIUM": 4300.0, "HIGH": 7200.0},
        },
    ),
    (
        date(2017, 10, 1),
        {
            "gas": {"LOW": 8000.0, "MEDIUM": 12000.0, "HIGH": 17000.0},
            "electricity": {"LOW": 1900.0, "MEDIUM": 3100.0, "HIGH": 4600.0},
            "electricity_pc2": {"LOW": 2500.0, "MEDIUM": 4200.0, "HIGH": 7100.0},
        },
    ),
    (
        date(2020, 4, 1),
        {
            "gas": {"LOW": 8000.0, "MEDIUM": 12000.0, "HIGH": 17000.0},
            "electricity": {"LOW": 1800.0, "MEDIUM": 2900.0, "HIGH": 4300.0},
            "electricity_pc2": {"LOW": 2400.0, "MEDIUM": 4200.0, "HIGH": 7100.0},
        },
    ),
    (
        date(2023, 10, 1),
        {
            "gas": {"LOW": 7500.0, "MEDIUM": 11500.0, "HIGH": 17000.0},
            "electricity": {"LOW": 1800.0, "MEDIUM": 2700.0, "HIGH": 4100.0},
            "electricity_pc2": {"LOW": 2200.0, "MEDIUM": 3900.0, "HIGH": 6700.0},
        },
    ),
    (
        date(2026, 7, 1),
        {
            "gas": {"LOW": 6000.0, "MEDIUM": 9500.0, "HIGH": 14000.0},
            "electricity": {"LOW": 1600.0, "MEDIUM": 2500.0, "HIGH": 3800.0},
            # PC2 for 2026 is NOT established from the decision letter read.
            # Absent rather than carried forward: a stale PC2 silently reused
            # under a new date would read as published and cannot be checked.
        },
    ),
)


@dataclass(frozen=True)
class AnnualConsumptionEstimate:
    """One customer's estimated annual consumption, with where it came from.

    ``kwh is None`` is a RESULT, not a failure: it means nothing a supplier
    holds established a figure, and ``reason`` says which. A caller may not
    substitute a number for it -- that is the whole point of the type.
    """

    kwh: Optional[float]
    basis: ConsumptionBasis
    reason: Optional[str] = None

    @property
    def is_established(self) -> bool:
        return self.kwh is not None


def tdcv_kwh(
    commodity: str,
    band: str,
    as_of: date,
) -> Optional[float]:
    """Ofgem's published typical annual consumption for ``commodity``/``band``
    as it stood on ``as_of``.

    Returns ``None`` -- never a guess and never the nearest neighbour -- when
    the commodity, band or date is outside the published series. A date before
    the series starts is genuinely unanswerable: we do not hold what Ofgem
    published in 2014.

    ``band`` is LOW / MEDIUM / HIGH. These are the lower quartile, median and
    upper quartile of household consumption (2023 decision §1.2), so HALF of
    all households fall outside LOW-HIGH. Any bound built on this inherits that
    and must say so.
    """
    table: Optional[Mapping[str, Mapping[str, float]]] = None
    for in_force_from, values in TDCV_BY_DATE:
        if as_of >= in_force_from:
            table = values
        else:
            break
    if table is None:
        return None
    by_band = table.get(commodity.strip().lower())
    if by_band is None:
        return None
    return by_band.get(band.strip().upper())


def estimate_annual_consumption(
    *,
    as_of: date,
    commodity: str,
    metered_annual_kwh: Optional[float] = None,
    registry_eac_kwh: Optional[float] = None,
    declared_annual_kwh: Optional[float] = None,
    band: Optional[str] = None,
) -> AnnualConsumptionEstimate:
    """The best annual-consumption estimate a supplier can make on ``as_of``.

    Walks ``BASIS_ORDER`` -- SLC 27.15's "best and most current information
    available (or which reasonably ought to be available)" -- and returns the
    first source that establishes a figure, saying which one it was.

    Every argument is something a real supplier holds. The household's true
    annual usage is NOT among them and must not be passed as any of them.

    A non-positive figure is treated as NOT establishing anything rather than
    as a valid zero: a zero EAC on a registration flow is a missing field, not
    a household that consumes nothing, and letting it through would publish a
    measured zero for an unobservable cause.
    """

    def _usable(v: Optional[float]) -> bool:
        return v is not None and v > 0.0

    if _usable(metered_annual_kwh):
        return AnnualConsumptionEstimate(
            kwh=float(metered_annual_kwh),  # type: ignore[arg-type]
            basis=ConsumptionBasis.METERED_HISTORY,
        )
    if _usable(registry_eac_kwh):
        return AnnualConsumptionEstimate(
            kwh=float(registry_eac_kwh),  # type: ignore[arg-type]
            basis=ConsumptionBasis.REGISTRY_EAC,
        )
    if _usable(declared_annual_kwh):
        return AnnualConsumptionEstimate(
            kwh=float(declared_annual_kwh),  # type: ignore[arg-type]
            basis=ConsumptionBasis.CUSTOMER_DECLARED,
        )
    if band is not None:
        typical = tdcv_kwh(commodity, band, as_of)
        if typical is not None:
            return AnnualConsumptionEstimate(
                kwh=typical, basis=ConsumptionBasis.TDCV_TYPICAL
            )
        return AnnualConsumptionEstimate(
            kwh=None,
            basis=ConsumptionBasis.UNAVAILABLE,
            reason=(
                f"no metered history, registry EAC or declaration, and Ofgem "
                f"publishes no TDCV for commodity={commodity!r} band={band!r} "
                f"as at {as_of.isoformat()}"
            ),
        )
    return AnnualConsumptionEstimate(
        kwh=None,
        basis=ConsumptionBasis.UNAVAILABLE,
        reason=(
            "no metered history, no registry EAC, no customer declaration, and "
            "no consumption band from which to reach a published TDCV"
        ),
    )


def opening_monthly_dd_gbp(
    estimate: AnnualConsumptionEstimate,
    *,
    unit_rate_p_kwh: float,
    standing_charge_p_day: float,
) -> Optional[float]:
    """The monthly direct debit an annualised plan opens at — ``None`` when the
    estimate did not establish a consumption.

    ``estimated annual cost / 12``, **whatever the start date**. That divisor is
    the director's practitioner statement of 2026-09-01, cited as exactly that:
    no SLC, decision letter or Ofgem guidance found publishes a formula
    converting an annual estimate into a monthly amount (research page §4.1).
    It is not dressed as regulation.

    The annual cost is NOT recomputed here. It delegates to
    ``company/pricing/tariff_comparison.annual_cost_gbp`` -- the function the
    tariff desk already uses to price a year for a given EAC -- so the quote a
    customer is shown and the direct debit that collects it cannot drift apart.
    A third private copy of ``energy + standing_charge * 365`` is exactly how
    this repository ended up with one VAT rule in five implementations.

    No buffer and no seasonal weighting: the published record establishes no
    figure for either, and one invented here would be load-bearing within a
    week (research page §4.2).

    Returned unrounded. Rounding a DD to the pound is the supplier's
    presentation convention and lives with the review, not with the estimate.
    """
    if estimate.kwh is None:
        return None
    from company.pricing.tariff_comparison import annual_cost_gbp

    return (
        annual_cost_gbp(
            unit_rate_p=unit_rate_p_kwh,
            standing_charge_p=standing_charge_p_day,
            eac_kwh=estimate.kwh,
        )
        / 12.0
    )
