"""The supplier's own broker book: who introduced the I&C customer, and what it cost.

KNIFE pass 3, `A_composition_lift` step 22, disposition register §3q.

Before this, `simulation/run_phase2b.py::main()` built the supplier's TPI book
itself: it constructed `TPIBook`, registered the broker with a name, a tier, a
commission basis, a rate and a registration date, decided that a deal is one
customer-year, filtered out the zero-consumption ones, chose the rounding, chose
1 January as the deal date, and then read the book's PRIVATE `_deals` list to
publish a count.

None of that is world physics. Which brokers a supplier is accredited with, what
tier it puts them on, whether it pays them on volume or on revenue, and what it
pays per MWh are the commercial terms of the supplier's own channel. The world
owns two things and hands both over: the settled records (what physically flowed
and what was billed for it) and its own roster of which electricity accounts are
I&C. Everything else is behind this desk.

THE READ DIRECTION IS WHY THIS IS A CUT AND NOT A FILE MOVE, the same test §3f
applied to bill assembly and §3p to the customer-experience books: this module
imports nothing from `simulation/` or `sim/`.

ONE NAME, ONE NUMBER — the defect this cut removes on the way past. Before the
cut the commission rate appeared TWICE as a literal `1.5`: once in the
registration call and once, independently, in the published summary's
`commission_rate_gbp_per_mwh`. A reader checking the published rate against the
charged rate was comparing a number to a second typing of itself, and the two
could drift with nothing to notice. The published rate is now read off the
registered TPI, and `test_the_published_rate_is_the_charged_rate` mutation-proves
it by moving the registered rate and asserting the published one moves with it.

WHAT THIS DOOR DOES NOT CARRY. `company/market/tpi_commission_book.py` is a
separate, richer broker model that nothing in the run path uses; this door
composes `company/crm/tpi_book.py`, which is what the run actually ran, and does
not merge the two. Merging them would be a behaviour change smuggled in with an
import move, which is the thing B7 named.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping, Sequence

from company.crm.tpi_book import TPIBook, TPICommissionBasis, TPITier

# The supplier's own channel terms. These were literals inside the world's run
# loop until step 22; they are the commercial relationship, not the physics.
TPI_ID: str = "TPI-001"
TPI_NAME: str = "Standard Energy Broker"
TPI_TIER: TPITier = TPITier.PREFERRED
TPI_COMMISSION_BASIS: TPICommissionBasis = TPICommissionBasis.PCT_OF_ANNUAL_CONSUMPTION
# £/MWh (0.15 p/kWh — standard for large I&C). Published from HERE, not retyped.
TPI_COMMISSION_RATE_GBP_PER_MWH: float = 1.5
TPI_REGISTERED_DATE: date = date(2016, 1, 1)

# A deal is one broker-introduced customer for one supply year. The supplier
# books it on 1 January of that year because commission is settled against the
# year's consumption, not against a contract anniversary it does not hold here.
_DEAL_DAY = (1, 1)
_CONSUMPTION_DP = 3
_REVENUE_DP = 2


@dataclass(frozen=True)
class TPICommissionResult:
    """What the supplier publishes about its broker channel."""

    summary: dict
    total_commission_gbp: float
    deal_count: int


def build_tpi_commission(
    settled_records: Sequence[Mapping],
    ic_elec_customer_ids: Iterable[str],
    report_years: Sequence[str],
) -> TPICommissionResult:
    """Book the broker commission the supplier owes on its I&C book.

    `settled_records` and `ic_elec_customer_ids` are the world's; the broker,
    its terms, what counts as a deal and what gets published are the supplier's.
    """
    book = TPIBook()
    book.register(
        tpi_id=TPI_ID,
        name=TPI_NAME,
        tier=TPI_TIER,
        commission_basis=TPI_COMMISSION_BASIS,
        commission_rate=TPI_COMMISSION_RATE_GBP_PER_MWH,
        registered_date=TPI_REGISTERED_DATE,
    )

    brokered = set(ic_elec_customer_ids)
    yearly: dict[tuple[str, str], list[Mapping]] = defaultdict(list)
    for rec in settled_records:
        if rec.get("customer_id") in brokered:
            yearly[(rec["customer_id"], rec["settlement_date"][:4])].append(rec)

    deals = 0
    for (cid, year), recs in sorted(yearly.items()):
        annual_consumption_mwh = sum(r.get("consumption_kwh", 0.0) for r in recs) / 1000.0
        annual_revenue_gbp = sum(r.get("revenue_gbp", 0.0) for r in recs)
        if annual_consumption_mwh <= 0:
            continue
        book.record_deal(
            tpi_id=TPI_ID,
            customer_id=cid,
            annual_consumption_mwh=round(annual_consumption_mwh, _CONSUMPTION_DP),
            annual_revenue_gbp=round(annual_revenue_gbp, _REVENUE_DP),
            deal_date=date(int(year), *_DEAL_DAY),
        )
        deals += 1

    registered = book.active_tpis()
    summary = {
        "total_commission_gbp": book.total_commission_gbp(),
        "commission_rate_gbp_per_mwh": _published_rate(registered),
        "per_year": {yr: book.annual_summary(int(yr)) for yr in sorted(report_years)},
        "active_tpi_count": len(registered),
        "total_deals": deals,
    }
    return TPICommissionResult(
        summary=summary,
        total_commission_gbp=summary["total_commission_gbp"],
        deal_count=deals,
    )


def _published_rate(registered) -> float:
    """The rate the supplier PUBLISHES is the rate it actually charges itself.

    Read off the registered broker rather than retyped as a literal — see the
    ONE NAME, ONE NUMBER paragraph in this module's docstring. With more than one
    accredited broker on the same basis this would need a weighted answer; there
    is one, and a second would make the single-rate headline wrong regardless of
    where the number came from, so it raises rather than averaging silently.
    """
    on_volume = [
        t for t in registered
        if t.commission_basis == TPICommissionBasis.PCT_OF_ANNUAL_CONSUMPTION
    ]
    if len(on_volume) != 1:
        raise ValueError(
            "the published headline commission rate assumes exactly one "
            f"volume-based broker; found {len(on_volume)}"
        )
    return on_volume[0].commission_rate
