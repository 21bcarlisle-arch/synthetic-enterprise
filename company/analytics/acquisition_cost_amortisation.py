"""Acquisition cost, seen the two ways it is actually seen — expensed, and amortised.

Roadmap R5 of WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE
(2026-08-28).

BOTH TREATMENTS ARE CORRECT AND THEY ARE NOT THE SAME QUESTION. The accounts expense customer
acquisition cost as it is incurred, because that is what GAAP and IFRS require of it — the CMA
records the same of the real suppliers it examined: acquisition costs "are expensed as they are
incurred rather than capitalised". Our P&L does this and this module does not touch it.

The CMA's own economic analysis does the other thing: it amortises that spend across the customer
lifespan the acquisition bought, because the question "was winning that customer worth it" is not
answerable inside the year you paid for them. It reports supplier-submitted lifespans of four to
ten years, concentrated around six, and works a base case of six with a sensitivity at eight.

WHY THE SINGLE VIEW MISLEADS, and it is not a subtlety here. A supplier growing quickly books all
of its acquisition spend now and none of the margin it bought, so a good year of growth reads as a
bad year of trading. Poesys is that supplier: its campaign is the largest single discretionary
line it has. Showing only the expensed view makes growth look like a mistake; showing only the
amortised view would hide that the CASH left the building on day one, which is the mechanism
behind every supplier failure in 2021. Neither number is the truth on its own.

WHAT IS AN ASSUMPTION HERE, said plainly: the LIFETIME. Six years is the CMA's base case for the
GB market of 2016, not a measurement of this book — Poesys's own realised lifespans are shorter
than its window can even observe. It is a stated input with a citation, not a discovered fact, and
`amortisation_schedule` takes it as an argument so a caller can vary it rather than inherit it.

Source: CMA, Energy market investigation, Appendix 9.10 (Retail profitability), paragraphs 64 and
74 — see `docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md`.
"""
from __future__ import annotations

from datetime import date

#: The CMA's base-case customer lifespan for GB domestic supply, in years, used as the
#: amortisation period. Reported lifespans ranged 4-10 and clustered near six; the investigation
#: worked six as its base case and eight as a sensitivity. See the module docstring for what this
#: is and is not — it is the market's number, not this book's.
CMA_BASE_CASE_CUSTOMER_LIFETIME_YEARS: int = 6

#: The CMA's own sensitivity, carried so a caller can run the pair rather than invent a second
#: number when someone asks "and if they stay longer?".
CMA_SENSITIVITY_CUSTOMER_LIFETIME_YEARS: int = 8


def amortisation_schedule(
    acquisition_spend_events: list,
    lifetime_years: int = CMA_BASE_CASE_CUSTOMER_LIFETIME_YEARS,
    through_year: int | None = None,
) -> dict:
    """Both treatments of the same spend, per calendar year.

    `acquisition_spend_events` are the ledger's own acquisition rows — dicts carrying an
    `event_date` (ISO) and an `amount_gbp`. Sign is normalised: the ledger books cost as a
    negative cash movement and this module reports positive cost, because a schedule whose
    entries are negative is read wrongly by every consumer at least once.

    `through_year` bounds the amortised view. Spend in the final years of the window has most of
    its life ahead of it, so an unbounded schedule would report charges in years the run does not
    cover and a reader would compare them against revenue that is not there. Defaults to the last
    year that carries spend.

    Returns::

        {
          "by_year": [{"year": int, "expensed_gbp": float, "amortised_gbp": float}, ...],
          "total_spend_gbp": float,
          "amortised_within_window_gbp": float,
          "unamortised_carried_beyond_window_gbp": float,
          "lifetime_years": int,
          "events_that_could_not_be_read": int,
        }

    `unamortised_carried_beyond_window_gbp` is the honest residual: cost this book has paid and
    whose matching benefit falls outside the reported world. It is stated rather than folded into
    the last year, which would make the final year look worse for a reason that is arithmetic.
    """
    if lifetime_years < 1:
        raise ValueError("a customer lifetime of less than one year cannot be amortised annually")

    expensed: dict[int, float] = {}
    charges: dict[int, float] = {}
    total = 0.0
    unreadable = 0

    for event in acquisition_spend_events or []:
        try:
            year = date.fromisoformat(str(event["event_date"])[:10]).year
            amount = abs(float(event["amount_gbp"]))
        except (KeyError, TypeError, ValueError):
            # Counted, never silently dropped and never charged to a guessed year. An event this
            # function cannot read is not an event that cost nothing.
            unreadable += 1
            continue
        expensed[year] = expensed.get(year, 0.0) + amount
        total += amount
        annual = amount / lifetime_years
        for offset in range(lifetime_years):
            charges[year + offset] = charges.get(year + offset, 0.0) + annual

    if not expensed:
        return {
            "by_year": [], "total_spend_gbp": 0.0, "amortised_within_window_gbp": 0.0,
            "unamortised_carried_beyond_window_gbp": 0.0, "lifetime_years": lifetime_years,
            "events_that_could_not_be_read": unreadable,
        }

    last = through_year if through_year is not None else max(expensed)
    years = range(min(expensed), last + 1)
    by_year = [
        {
            "year": y,
            "expensed_gbp": round(expensed.get(y, 0.0), 2),
            "amortised_gbp": round(charges.get(y, 0.0), 2),
        }
        for y in years
    ]
    within = sum(charges.get(y, 0.0) for y in years)

    return {
        "by_year": by_year,
        "total_spend_gbp": round(total, 2),
        "amortised_within_window_gbp": round(within, 2),
        "unamortised_carried_beyond_window_gbp": round(total - within, 2),
        "lifetime_years": lifetime_years,
        "events_that_could_not_be_read": unreadable,
    }


def growth_year_distortion_gbp(schedule: dict) -> list:
    """Per year, what the expensed view charges that the amortised view does not — and vice versa.

    This is the number the two treatments exist to expose: a positive figure is a year the P&L
    charged more acquisition cost than the customers acquired that year will ever be asked to
    carry in it. For a growing book it is positive early and negative later, and its running sum
    is zero once every cohort has lived its full life.

    Returns `[{"year": int, "expensed_minus_amortised_gbp": float}, ...]`.
    """
    return [
        {
            "year": row["year"],
            "expensed_minus_amortised_gbp": round(
                row["expensed_gbp"] - row["amortised_gbp"], 2),
        }
        for row in schedule.get("by_year", [])
    ]
