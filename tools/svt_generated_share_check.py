"""The generated fixed/SVT split, printed beside the published one — a CHECK, never an input.

C1b. `simulation/svt_product.py` names this as the third thing owed before assignment, and is
explicit about which direction it must run in: *"the published year-by-year fixed/SVT split
printed beside the result as a CHECK. Never an input: if the split has to be set to land in
range, the behaviour is wrong and setting it hides that."*

So this tool reads. It builds the electricity schedules the world would build, counts
ACCOUNT-DAYS on each product in each calendar year, and prints the generated domestic fixed share
against the published rows in
`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` §(b). Nothing here is fed back
into `simulation/`, and there is no dial in this file to make a year land.

WHY ACCOUNT-DAYS AND NOT ACCOUNTS. The published statistic is a point-in-time stock — the share of
domestic accounts sitting on a fixed deal on a given day. Counting SCHEDULES instead would count a
household once per product it held that year and read as a flow, and an SVT stint and a fixed term
would weigh the same however long each lasted. Before dividing: the numerator is domestic
electricity account-days on a `fixed` term in the year, the denominator is domestic electricity
account-days settled at all in that year, and both count the same entity.

The schedules are built without running settlement, which is what makes this cheap enough to run
beside a change rather than only after a full decade run.

REUSE
-----
REUSE: tools/svt_generated_share_check.py
CLASS: CUSTOM
INDEX: searched "svt", "share", "split", "fixed", "tariff mix", "check", "population anchor".
       `tools/population_anchor.py` reconciles the world's CHURN rate against the published
       switching record and is the nearest shape — same "generated versus published, printed as
       an interval" discipline — but its subject is departures per year, read off the customer
       event log after a run. This subject is the product MIX, readable off the schedules with no
       run at all, and folding it in would have made one tool that needs a decade run to answer
       either question.
       `tests/simulation/test_drawn_book_tariff_type_fidelity.py` asserts the distribution is not
       a blanket label; it is a control with a pass/fail, not a report, and a control that printed
       a table would be read as evidence for whichever number was in it.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, timedelta

from simulation.run_phase2b import REPORT_END, REPORT_START
from tools.published_tariff_mix import fixed_share

#: The published fixed-deal band now comes from `tools/published_tariff_mix.py`, which is the one
#: home for this series. THIS FILE USED TO CARRY ITS OWN COPY and that copy was wrong in a way
#: worth recording rather than quietly deleting: it rendered Ofgem's 2017 and 2019 readings as the
#: DOMESTIC fixed share when both are published over a population with **prepayment removed**, and
#: more than 90% of prepayment customers are on a default tariff. The old table also carried a 2020
#: band copied from 2019 with no source of its own. See that module's docstring for the correction
#: and `docs/market_research/gb_domestic_default_tariff_share_2016_2025.md` for the sourcing.
#:
#: The basis is named at every call site rather than defaulted, because this world models no
#: prepayment meter and so matches NEITHER published population exactly — see `--basis`.
PUBLISHED_BASES = ("all_domestic", "as_published")


def generated_fixed_share_by_year(report_end: str = REPORT_END) -> dict[int, dict]:
    """Domestic electricity account-days by product, per calendar year, off the built schedules."""
    from sim.cache_store import get_cached_prices
    from simulation.renewals import build_renewal_schedule
    from simulation.run_phase2b import (
        EARLIEST_SSP_DATE,
        EFFECTIVE_EAC_KWH,
        ELEC_CUSTOMERS,
    )
    from simulation.svt_product import SVT_TARIFF_TYPE

    start = date.fromisoformat(REPORT_START)
    end = date.fromisoformat(report_end)
    fetch_start = max(
        (min(date.fromisoformat(c["acquisition_date"]) for c in ELEC_CUSTOMERS)
         - timedelta(days=365)).isoformat(),
        EARLIEST_SSP_DATE,
    )
    price_records = get_cached_prices(fetch_start, report_end)
    if price_records is None:
        raise SystemExit(
            "no cached SSP records for the window; this tool deliberately does not fetch -- run "
            "the sim once to warm the cache, or narrow --report-end"
        )

    days: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for c in ELEC_CUSTOMERS:
        if c.get("segment", "resi") != "resi":
            continue
        schedule = build_renewal_schedule(
            c["customer_id"], c["acquisition_date"], report_end,
            price_records, EFFECTIVE_EAC_KWH[c["customer_id"]],
            segment=c.get("segment", "resi"),
            tariff_type=c.get("tariff_type") or "fixed",
            deemed_gap_days=c.get("deemed_gap_days", 0),
        )
        for term in schedule:
            t_start = max(date.fromisoformat(term["acquisition_date"]), start)
            t_end = min(date.fromisoformat(term["term_end"]), end + timedelta(days=1))
            product = term.get("tariff_type") or "unlabelled"
            day = t_start
            while day < t_end:
                # Year boundaries split a term, so the stock is counted in the year it was held.
                year_end = min(date(day.year + 1, 1, 1), t_end)
                days[day.year][product] += (year_end - day).days
                day = year_end

    out: dict[int, dict] = {}
    for year in sorted(days):
        by_product = dict(days[year])
        total = sum(by_product.values())
        out[year] = {
            "account_days": by_product,
            "total_account_days": total,
            "fixed_share": (by_product.get("fixed", 0) / total) if total else None,
            "svt_share": (by_product.get(SVT_TARIFF_TYPE, 0) / total) if total else None,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report-end", default=REPORT_END)
    ap.add_argument(
        "--basis", default="all_domestic", choices=PUBLISHED_BASES,
        help="which published population to judge against. 'as_published' is Ofgem's own figure, "
             "which for 2017-2019 EXCLUDES prepayment; 'all_domestic' restores prepayment at the "
             "published PPM share and default-tariff rate. This world models no prepayment meter, "
             "so neither is an exact comparator and the two disagree by ~6pp on the pre-crisis "
             "years -- which is enough to flip the 2018 and 2019 verdicts.",
    )
    args = ap.parse_args()

    rows = generated_fixed_share_by_year(args.report_end)
    print(f"published fixed-deal band on basis: {args.basis}")
    print(f"{'year':>6} {'acct-days':>10} {'fixed':>8} {'svt':>8} {'other':>8}  published fixed")
    for year, row in rows.items():
        other = 1.0 - (row["fixed_share"] or 0.0) - (row["svt_share"] or 0.0)
        band = fixed_share(year, args.basis)
        if band is None:
            verdict = "(no established figure)"
        else:
            lo, hi = band
            inside = lo <= (row["fixed_share"] or 0.0) <= hi
            verdict = f"{lo:.0%}-{hi:.0%}  {'IN' if inside else 'OUT'}"
        print(
            f"{year:>6} {row['total_account_days']:>10,} "
            f"{row['fixed_share']:>8.1%} {row['svt_share']:>8.1%} {other:>8.1%}  {verdict}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
