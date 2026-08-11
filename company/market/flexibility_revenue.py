"""The supplier's own flexibility revenue book: domestic DSR/CM and I&C CM/DFS.

KNIFE pass 3, `A_composition_lift` step 18, 2026-08-11, disposition register
§3m. Before this, `simulation/run_phase2b.py::main()` opened a
`FlexibilityRevenueBook` and an `ICFlexibilityRevenueBook` itself, drove both
year by year, and summed their two totals into one figure — two of that
module's wall crossings (`company.market.flexibility_revenue_book`,
`company.market.ic_flexibility_revenue`).

WHY THIS IS THE SUPPLIER'S AND NOT THE WORLD'S. Enrolling a portfolio in the
Capacity Market and NESO's Demand Flexibility Service, deciding which customers
are eligible, and booking what the aggregator leaves you is a supplier
commercialising its own book. The world's job is to have the assets exist and
the meters turn; deciding that a 200 MWh/yr I&C site is worth enrolling, that
10% of its peak is genuinely interruptible, and that an EV plus a battery is
worth so many kW of flex is the supplier's own commercial reading — and it is
allowed to be wrong about all three.

WHY IT IS A GROUP AND NOT TWO ITEMS. The two books feed ONE accumulator:
`total_flexibility_revenue` in the code this replaces is the domestic total plus
the I&C total, and it is that single figure the report carries. Cutting them
separately would have left the world holding the running sum and threading it
through two doors — a seam that publishes a pull, which is half a cut. They are
also the same process (enrol flexible capacity, book CM and DFS revenue against
it) at the same point in the report, differing only in how flex capacity is
estimated for a house versus a factory.

WHAT ARRIVES AND WHAT DOES NOT. Two plain-data inputs: a per-year-end snapshot
of which customers had which flexible assets, and the I&C electricity roster as
`(customer_id, eac_kwh)` pairs. Both are things a real supplier reads off its
own CRM and billing systems. This module imports nothing from `simulation/` or
`sim/`; in particular the world's `HouseholdDemandRegister` no longer crosses.

THAT REGISTER CROSSING IS THE POINT, and it is worth naming because the import
count alone does not show it. `FlexibilityRevenueBook.compute_year` takes a
`household_register` and calls `.dynamic_assets(cid, date)` on it — so before
this cut a company module held a live SIM object and PULLED from it whenever it
liked. Deleting the import while still passing the object would have moved the
edge, not cut it. What crosses now is a mapping that was resolved on the world's
side of the door, at dates the world chose, before the door opened.

THE ONE ALIGNMENT DEFECT THIS SHAPE COULD HAVE INTRODUCED IS CLOSED BY
CONSTRUCTION, not by a control. `FlexibilityRevenueBook` derives its own
year-end date (`YYYY-12-31`) from the year it is computing and asks the register
for that date. A snapshot keyed by anything else — a year int, a position in a
list — would let the world hand over 2020's assets while the book believed it
was pricing 2023, silently, with every test on the book still green. So the
snapshot is keyed by the SAME date string the book asks for, and the private
adapter below looks it up rather than ignoring the argument: a misaligned
snapshot raises `KeyError` at the first customer instead of quietly repricing
the portfolio. The residual — the world building the right key off the wrong
query — is closed on the world's side, where one variable serves as both.

WHAT THIS DOES NOT DO. `run_phase2b` keeps its other crossings: the trading
desk, the CRM builders, the pricing group and the `saas.*` set are separate
processes on separate inputs, and the two indirect edges are untouched. This
door carries the flexibility revenue book and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from company.market.flexibility_revenue_book import FlexibilityRevenueBook
from company.market.ic_flexibility_revenue import ICFlexibilityRevenueBook

__all__ = ["FlexibilityRevenue", "build_flexibility_revenue"]


@dataclass(frozen=True)
class FlexibilityRevenue:
    """The supplier's flexibility position for the whole reporting window."""

    domestic_summary: dict
    ic_summary: dict
    domestic_revenue_by_year: dict
    total_revenue_gbp: float


class _AssetSnapshotRegister:
    """Answers the book's register question off a snapshot the world handed over.

    The book asks `dynamic_assets(cid, "YYYY-12-31")`. This holds exactly those
    answers, keyed by the same date string, so an asset map built for the wrong
    year end cannot be served for the right one — the lookup raises instead.
    """

    def __init__(self, by_date: Mapping[str, Mapping[str, Mapping[str, bool]]]) -> None:
        self._by_date = by_date

    def dynamic_assets(self, customer_id: str, date_str: str) -> Mapping[str, bool]:
        return self._by_date[date_str][customer_id]


def build_flexibility_revenue(
    *,
    report_years: Sequence[str],
    domestic_assets_by_date: Mapping[str, Mapping[str, Mapping[str, bool]]] | None,
    ic_elec_roster: Sequence[tuple],
) -> FlexibilityRevenue:
    """Book domestic and I&C flexibility revenue for the reporting window.

    `report_years` are the four-digit year strings, in report order.
    `domestic_assets_by_date` maps each year-end date (`YYYY-12-31`) to
    customer-id -> asset flags, in the order the customers should be priced;
    `None` means the world had no household register and the domestic book is
    skipped, as it was before this cut. `ic_elec_roster` is the I&C electricity
    book as `(customer_id, eac_kwh)` pairs.
    """
    domestic_book = FlexibilityRevenueBook()
    domestic_revenue_by_year: dict = {}
    if domestic_assets_by_date is not None:
        register = _AssetSnapshotRegister(domestic_assets_by_date)
        for year_str in report_years:
            year_int = int(year_str)
            year_end = f"{year_int}-12-31"
            customer_ids = list(domestic_assets_by_date[year_end].keys())
            by_cid = domestic_book.compute_year(year_int, register, customer_ids)
            domestic_revenue_by_year[year_str] = by_cid

    total_revenue_gbp = domestic_book.total_revenue_all_years()

    ic_book = ICFlexibilityRevenueBook()
    for year_str in report_years:
        ic_book.compute_year(int(year_str), list(ic_elec_roster))
    total_revenue_gbp += ic_book.total_revenue_all_years()

    return FlexibilityRevenue(
        domestic_summary=domestic_book.flexibility_summary(),
        ic_summary=ic_book.flexibility_summary(),
        domestic_revenue_by_year=domestic_revenue_by_year,
        total_revenue_gbp=total_revenue_gbp,
    )
