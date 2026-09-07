"""Capacity Market (CM) obligation management -- the SUPPLIER side.

UK suppliers pay a Capacity Market charge, recovered from all electricity demand customers as a
pass-through on the bill. This module models the company's own CM obligation and charge from
company-observable settlement data.

THIS MODULE APPLIES NO DE-RATING FACTOR, AND IT NEVER SHOULD HAVE. Asked deliberately on
2026-09-07, once `capacity_market_published_record.derating_factor()` began serving real published
numbers and the two remaining CM consumers needed a decision each. The answer here is not "no
factor is available" -- it is that **the concept does not apply**. De-rating is a haircut on a
capacity PROVIDER's connection capacity, reflecting how much of it can be relied on at a stress
event. A supplier's obligation is a payment scaled by the electricity it SUPPLIED, and demand is
not de-rated. There is no published factor for it because there is nothing to publish.

WHAT WAS HERE INSTEAD, and it is the more instructive half. `_DERATING_FACTOR = 0.92  # Assumed
average de-rated supply margin %` -- invented, named for a concept that does not apply to the
quantity it multiplied, and load-bearing in every figure this module produced. Alongside it,
`_CM_OBLIGATION_RATE_BY_YEAR` was a FOURTH home for the CM clearing price (after
`flexibility_potential`, `capacity_market` and `ic_flexibility_revenue`), keyed by year with no
statement of which year, ending in `.get(year, _RATE[2025])` so that every unrecognised year
silently priced at a real-looking number.

AND THE CLEARING PRICE WAS NEVER THIS QUANTITY. A supplier levy is not an auction result: it is
the total cost of all capacity agreements recovered across all suppliers in proportion to their
peak-period demand, and no publication states it as a rate you can derive from a clearing price.
Measured against Ofgem Annex 9 at 5 TWh, the route this replaced read 8.51x at 2016, 0.21x at 2020,
0.03x at 2021, 4.21x at 2022 and 1.69x at 2024 -- it tracked the published series in neither level
nor sign of error. 2022 is the clearest: the T-1 cleared at the GBP75/kW CAP and the real levy
FELL, because the volume behind that price was small. A clearing-price model gets that year
backwards, and no re-parameterisation fixes a quantity that is not the one being asked for.

REMOVING THE 0.92 MADE THE OLD ANSWER WORSE (2024: 12.29 -> 13.36 GBP/MWh against a published
7.27), which is the most expensive thing an invented constant can do: it was pulling an overstated
figure toward plausibility and so made a wrong route look roughly calibrated. That is why this is a
re-founding rather than a deletion.

The charge now comes from the regulation commons -- the published Annex 9 series, one home, read
rather than derived. Reading the commons is not a wall crossing (see `ro_commons`, same doctrine):
the law and the published cost breakdown are readable by every lane, and what stays owned here is
the READING.

THE DELIVERY LEGS ARE NOW GONE, and this is the record of why they were deleted rather than moved
(2026-09-07, a52, answering the question a51 named and left open). `delivery_status`, `shortfall_kw`,
`penalty_gbp` and a `firm_capacity_kw` argument modelled a capacity PROVIDER's obligation to deliver
at a System Stress Event and its penalty for failing to. A supplier holds no such obligation: its CM
obligation is a payment, and it discharges it by paying.

NOTHING WAS MOVED, because there was no receiving home for it. Three separate things were wrong and
only the last of them is the sort a re-founding could fix:

  * THE DIFFERENCE WAS NOT A SHORTFALL. `shortfall_kw = obligation_kw - firm_capacity_kw` subtracted
    a contracted capacity from this module's estimate of the supplier's own PEAK-PERIOD DEMAND. A
    provider's shortfall is its agreed de-rated capacity less what it actually delivered at a stress
    event; neither term of that is a demand estimate, so the subtraction names a quantity nobody
    holds.
  * THE PENALTY WAS NOT MONEY. `(shortfall_kw / 1000) * (levy / 8)` is MW x GBP/MWh, which is GBP
    PER HOUR -- a rate, in a field called `penalty_gbp`. The `/ 8` had no source and no unit. At 5
    TWh of demand it produced GBP933.65 for 2024 beside a GBP36.35m charge: five orders of magnitude
    apart, which is the size an invented divisor reaches when nothing constrains it.
  * AND THE STATUS WAS CONSTANT. `firm_capacity_kw` defaulted to None -> 0, so `delivery_status` read
    FAILED for every year at every input a real supplier could present. DELIVERED and PARTIAL were
    reachable only by handing the function a firm capacity a supplier does not have, which its own
    tests duly did.

The provider side already exists and is correct: `company/market/capacity_market.py` holds `CMUnit`,
`CMObligation.penalties_gbp` and `apply_penalty`, hung off a de-rated capacity and a delivery year.
Moving these fields there would have been a second and worse home for a mechanism that is already
built -- the same fourth-home failure this module was just re-founded to undo.

WHAT REPLACES THEM IS NOTHING, deliberately. A supplier that wants to reduce this charge does it by
reducing customer demand in the winter peak periods the levy is assessed on. That is a real and
modellable lever, it is not a delivery obligation, and inventing it here to fill the hole the
deletion leaves would be the same move that produced the 0.92.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

_COMMONS = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory"
    / "capacity_market_supplier_levy.json"
)


def _load_levy() -> Dict[int, float]:
    """`{obligation_year: GBP/MWh}` from the regulation commons.

    NO FAIL-OPEN PATH (R15). A missing, empty or malformed artefact RAISES at import rather than
    degrading to the literals this replaced or to a plausible default. An unavailable publication
    is not a licence to invent one -- which is exactly how a fourth home for the clearing price
    and an invented 0.92 came to be load-bearing here in the first place.
    """
    if not _COMMONS.exists():
        raise FileNotFoundError(
            f"Capacity Market supplier levy commons missing: {_COMMONS}. The published series is "
            "required; there is no invented default."
        )
    rows = json.loads(_COMMONS.read_text()).get("levy_gbp_per_mwh")
    if not rows:
        raise ValueError(f"CM supplier levy commons carries no series: {_COMMONS}")
    return {row["obligation_year"]: float(row["gbp_per_mwh"]) for row in rows}


_LEVY_GBP_PER_MWH: Dict[int, float] = _load_levy()

#: Peak-to-average demand ratio used to size the peak-period demand the CM charge is levied on.
#: Origin: assumption -- NOT a published figure, and it is only reachable through
#: `compute_cm_obligation`'s `obligation_kw`, which is a diagnostic. It does NOT reach
#: `annual_charge_gbp` or `cm_charge_per_mwh`, both of which are now the published levy times
#: volume. Kept explicit and named so its status is visible; it used to be multiplied by an
#: invented de-rating factor and a mis-keyed clearing price to produce the headline number.
_PEAK_TO_AVERAGE_RATIO = 1.8


def cm_levy_gbp_per_mwh(obligation_year: int) -> Optional[float]:
    """The published CM supplier levy for an Apr-Mar obligation year, or `None`.

    `None` means the year is outside Ofgem's published record -- NOT zero, and NOT the last known
    rate. There is deliberately no carry-forward: the lookup this replaced ended
    `.get(year, _RATE[2025])`, so a caller asking about an unpublished year got a real-looking
    number with nothing behind it and no way to tell.
    """
    return _LEVY_GBP_PER_MWH.get(obligation_year)


@dataclass
class CMObligationResult:
    year: int
    total_demand_mwh: float
    obligation_kw: float          # peak-period demand estimate; a diagnostic, see the docstring
    levy_gbp_per_mwh: float
    """The PUBLISHED supplier levy, GBP per MWh supplied. This field used to be called
    `clearing_price_gbp_per_kw` and held an auction result -- a different quantity, in different
    units, belonging to a different party. Renamed rather than re-sourced, because a caller
    reading `clearing_price` off a supplier obligation was being told something false by the
    field name alone."""
    annual_charge_gbp: float


def compute_cm_obligation(year: int, total_demand_mwh: float) -> CMObligationResult:
    """Compute the company's Capacity Market charge for an Apr-Mar obligation year.

    Args:
        year: obligation year (the calendar year the Apr-Mar year opens in)
        total_demand_mwh: supplier's total annual metered demand

    THERE IS NO `firm_capacity_kw` AND NO DELIVERY RESULT. See the module docstring: a supplier's
    CM obligation is a payment, so it has no delivery status to report and no shortfall to be
    penalised for. The argument was never optional-with-a-default so much as unanswerable.

    THE CHARGE IS THE PUBLISHED LEVY TIMES VOLUME, and nothing else feeds it. It is no longer
    peak demand times a de-rating factor times a clearing price, which was three invented or
    mis-keyed inputs producing a figure that missed Ofgem's published series by up to 33x in one
    direction and 8.5x in the other.

    `obligation_kw` survives as a DIAGNOSTIC -- the peak-period demand the charge is levied on,
    sized by `_PEAK_TO_AVERAGE_RATIO`, which is an assumption and says so. It no longer reaches
    the money.

    Raises `ValueError` for a year outside the published record. There is no carry-forward: the
    lookup this replaced defaulted to its last known rate, so an unpublished year was
    indistinguishable from a published one at the call site.
    """
    levy = cm_levy_gbp_per_mwh(year)
    if levy is None:
        raise ValueError(
            f"no published Capacity Market supplier levy for obligation year {year}: the record "
            f"covers {min(_LEVY_GBP_PER_MWH)}-{max(_LEVY_GBP_PER_MWH)}. There is no default, "
            "because the default this replaced was the last known rate and it made an "
            "unpublished year look established."
        )

    peak_mw = (total_demand_mwh / 8760.0) * _PEAK_TO_AVERAGE_RATIO
    obligation_kw = round(peak_mw * 1000, 1)

    return CMObligationResult(
        year=year,
        total_demand_mwh=total_demand_mwh,
        obligation_kw=obligation_kw,
        levy_gbp_per_mwh=levy,
        annual_charge_gbp=round(total_demand_mwh * levy, 2),
    )


def cm_charge_per_mwh(year: int, total_demand_mwh: float) -> float:
    """The CM pass-through charge in GBP/MWh -- which is the published levy itself.

    Kept as a named function because callers ask for it by this name, and because the identity is
    the point: a per-MWh charge derived from a per-MWh publication cannot drift from it. The form
    this replaced routed the same question through a peak estimate, a de-rating factor and a
    clearing price, and arrived somewhere else entirely.
    """
    if total_demand_mwh <= 0:
        return 0.0
    return round(compute_cm_obligation(year, total_demand_mwh).annual_charge_gbp
                 / total_demand_mwh, 4)
