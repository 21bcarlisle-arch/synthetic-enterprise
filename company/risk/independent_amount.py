"""What a counterparty demands ABOVE the mark once it stops trusting the balance sheet.

Roadmap R6 of WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE
(2026-08-28). The CMA records the mechanism in one sentence: growing fast means acquisition costs
paid up front, which

    "weakened a firm's balance sheet ... increasing the perceived riskiness of the supplier and,
     therefore, the quantity of collateral that trading counterparties required."

This project has had a growth campaign and a collateral book for months, and nothing joined them.
Acquisition spend left the treasury and no counterparty noticed.

WHY "THE QUANTITY OF COLLATERAL REQUIRED" CANNOT RISE IN THE MODEL AS IT STANDS. Today the only
collateral is variation margin, `max(0, -netted_mtm)` -- the amount by which the company is
out-of-the-money. That is 100% of the OTM exposure already, and no assessment of the supplier can
make it more. What a real counterparty adds when it grows uneasy is an INDEPENDENT AMOUNT: collateral
posted over and above the mark, against the exposure that could accrue while the position is closed
out. `company/trading/initial_margin_register.py` describes exactly this and is
`initial_margin_gbp=0.0` on every call the live run makes (B6 FRAME §1.9). This module is what makes
that number non-zero, and the thing that moves it is the company's own balance sheet.

TWO CONSEQUENCES BEYOND THE ONE R6 ASKED FOR:

 1. **It is direction-agnostic.** B6 §1.9 records that the model can only kill on a price FALL,
    because a long hedge book goes in-the-money on a spike and posts no variation margin at all. An
    independent amount is demanded whichever way the price went -- it is about the supplier's credit,
    not the position's sign -- so the spike-direction drain becomes possible for the first time.
 2. **It is the growth/solvency loop closing.** Spend weakens equity; weaker equity is demanded
    collateral; demanded collateral is cash that cannot fund growth. Nothing in the arithmetic below
    aims at that -- it falls out of two sourced quantities and a trigger.

THERE IS NO INVENTED RATE HERE, and getting that right is why this took the shape it did. The first
design set the independent amount as a percentage of notional per credit band, which is how real
CSAs are written and would have meant inventing the band table -- the precise defect R1 existed to
remove. Instead:

  * WHEN it is demanded: when the supplier's FREE EQUITY -- net assets less the capital the
    regulator already obliges it to hold against its customer book -- no longer covers the gross
    exposure it is running. That is a bright line, not a tuned threshold: below it, the counterparty
    is looking at a name whose own balance sheet cannot absorb its own position.
  * HOW MUCH: the exposure that could accrue over a stressed close-out. The horizon is the market's,
    not ours -- `initial_margin_register.py:11` states the standard, "sized to cover a defined
    stressed holding period (typically 5 days)" -- and the move over that horizon is MEASURED from
    the observable price history the desk already holds, not assumed.

The MCR leg is sourced too: £130 of net assets per domestic account, Ofgem's decision of 26 July
2023, already load-bearing at `company/finance/treasury.MCR_PER_ACCOUNT` and
`saas/capital/solvency.MCR_FLOOR_GBP_PER_CUSTOMER`.

WHAT THIS IS NOT, said plainly because the evidence says to say it. This is NOT a model of how GB
domestic suppliers failed in 2021-22. Ofgem's own Financial Resilience Transparency Report, citing
the Oxera review, gives the dominant root cause as the opposite: suppliers that "had not purchased
energy in advance to 'hedge' their risk and could not afford to buy energy at elevated prices" --
naked exposure, not collateral calls on a hedged book. The collateral-drain mechanism is strongly
evidenced one level up the chain (Uniper/Fortum, 2022) and is real; it was not the UK retail cause.
R6 is the CMA's GROWTH channel, which is a different claim about a different decade, and conflating
the two would be inventing history to make a mechanism look important.

Epistemic position: every input is the company's own or public. Its net assets and account count are
its own books; the MCR is published; the close-out move is measured from the public spot history the
credit desk already marks against. The company does not compute its own riskiness for a counterparty
-- it computes what it will be ASKED for, which is what a treasurer actually forecasts.
"""
from __future__ import annotations

from math import isfinite

#: The stressed close-out horizon a counterparty sizes an independent amount over, in days. The
#: market's number, not ours: `company/trading/initial_margin_register.py:11` states the convention
#: ("sized to cover a defined stressed holding period (typically 5 days)"), and CCP margin models are
#: built on exactly this shape. Kept here as a named constant rather than a literal so the one place
#: it could be tuned is visible.
STRESSED_CLOSE_OUT_DAYS: int = 5

#: Ofgem's minimum capital requirement per domestic account, £. Decision of 26 July 2023, and the
#: same figure `company/finance/treasury.MCR_PER_ACCOUNT` and
#: `saas/capital/solvency.MCR_FLOOR_GBP_PER_CUSTOMER` already carry. Restated rather than imported:
#: importing `company.finance.treasury` from the risk layer would add a dependency for one scalar,
#: and `test_the_mcr_figure_agrees_with_every_other_copy` fails if the three ever disagree.
MCR_GBP_PER_ACCOUNT: float = 130.0


def free_equity_gbp(net_assets_gbp: float, accounts_held: int) -> float | None:
    """Net assets a counterparty could actually look to, after the regulator's prior claim.

    A supplier's equity is not all available to absorb a trading loss: Ofgem obliges it to hold
    £130 per domestic account against the customer book, and a counterparty assessing it knows
    that capital is spoken for. What is left is what backs the trading position.

    Returns `None` -- not zero -- on an unreadable balance sheet. The two are different claims and
    the caller must not confuse them: zero free equity is a supplier with nothing spare, which is a
    finding; `None` is a balance sheet nobody could read, which is a failure of the input. Both lead
    to a demanded independent amount here, but only one of them is a fact about the company.
    """
    if not isfinite(net_assets_gbp) or accounts_held < 0:
        return None
    return max(0.0, net_assets_gbp - accounts_held * MCR_GBP_PER_ACCOUNT)


def independent_amount_gbp(
    gross_exposure_gbp: float,
    net_assets_gbp: float,
    accounts_held: int,
    close_out_move_fraction: float,
) -> dict:
    """What the counterparty asks for above the mark, and the reason it asked.

    `close_out_move_fraction` is the proportional price move the position could suffer over
    `STRESSED_CLOSE_OUT_DAYS`, MEASURED from observable spot history by the caller (see
    `close_out_move_fraction_from_history`). Passing an assumed number here is legal and is exactly
    what this module exists to avoid, so the measurement lives beside it and the run uses it.

    Returns a dict rather than a float because the AMOUNT alone is unreadable -- a zero could mean
    a strong balance sheet, a flat book, or an input nobody could parse, and those are three
    different states of the world::

        {"independent_amount_gbp": float,
         "demanded": bool,
         "reason": "free_equity_covers_exposure" | "free_equity_below_exposure"
                   | "balance_sheet_unreadable" | "no_exposure",
         "free_equity_gbp": float | None,
         "gross_exposure_gbp": float}

    FAILS CLOSED, and in the direction that costs the company rather than flatters it: an
    unreadable balance sheet or a non-finite move produces a DEMAND, not a waiver. A counterparty
    that cannot read your accounts does not extend you unsecured credit. The opposite default --
    silently waiving on a NaN -- is the fail-open shape B6's FRAME §1.10 found three of in the
    existing margin chain, where a single non-finite mark returns "survived".
    """
    exposure = gross_exposure_gbp if isfinite(gross_exposure_gbp) else float("nan")
    if isfinite(exposure) and exposure <= 0.0:
        return {
            "independent_amount_gbp": 0.0, "demanded": False, "reason": "no_exposure",
            "free_equity_gbp": free_equity_gbp(net_assets_gbp, accounts_held),
            "gross_exposure_gbp": 0.0,
        }

    free = free_equity_gbp(net_assets_gbp, accounts_held)
    if free is None or not isfinite(exposure) or not isfinite(close_out_move_fraction):
        return {
            "independent_amount_gbp": 0.0, "demanded": True,
            "reason": "balance_sheet_unreadable",
            "free_equity_gbp": free, "gross_exposure_gbp": exposure,
        }

    if free >= exposure:
        # The name can absorb its own position out of unpledged equity. No independent amount --
        # this is the state a well-capitalised supplier is in, and it is why the mechanism is a
        # LOOP rather than a constant drain: spending the equity is what starts it.
        return {
            "independent_amount_gbp": 0.0, "demanded": False,
            "reason": "free_equity_covers_exposure",
            "free_equity_gbp": round(free, 2), "gross_exposure_gbp": round(exposure, 2),
        }

    amount = exposure * abs(close_out_move_fraction)
    return {
        "independent_amount_gbp": round(amount, 2), "demanded": True,
        "reason": "free_equity_below_exposure",
        "free_equity_gbp": round(free, 2), "gross_exposure_gbp": round(exposure, 2),
    }


def close_out_move_fraction_from_history(
    price_records: list,
    as_of: str,
    price_key: str = "systemSellPrice",
    date_key: str = "settlementDate",
    days: int = STRESSED_CLOSE_OUT_DAYS,
) -> float | None:
    """The worst `days`-day proportional move in the OBSERVABLE record up to `as_of`.

    THE DEFAULT KEYS ARE THE COMPANY'S OWN PRICING ENGINE'S, and that is load-bearing rather than
    convenient. `company/pricing/tariff_engine.py:116-118` reads exactly `settlementDate` and
    `systemSellPrice` and averages them to DAILY means before doing anything with them. This
    function reads the same feed the same way, so the close-out move and the forward mark it is
    applied to come from one reading of one series rather than two readings that agree by luck.

    THIS WAS WRONG ON ITS FIRST DRAFT AND THE FAILURE IS WORTH KEEPING. It defaulted to
    `settlement_date`/`price_gbp_per_mwh` -- plausible names, and the shape of a small internal
    feed elsewhere in the repo. Against the real 165,386-row Elexon record it parsed ZERO rows and
    returned `None` for every date in the decade, which the live call site turns into NaN, which
    demands an independent amount from every counterparty. A control keyed to a structure that
    does not exist, failing loudly in the wrong direction and inflating every published margin
    figure. Printing the numbers at real inputs found it in one run; no amount of reading would
    have.

    HALF-HOURLY IS AGGREGATED TO DAILY, AND THEN SMOOTHED THE WAY THE MARK IS. A "five-day move"
    across raw settlement periods is a five-period move -- two and a half hours -- and imbalance
    prices at that resolution are noise. But daily means are not enough either, and the second
    draft of this function stopped there: measured on the real record it reported worst five-day
    moves of 310% in 2017 rising to 681% by 2025, which as a collateral demand would be nearly
    seven times the position. Those are real moves in the BALANCING market, and the position is
    not marked there.

    A close-out is against the price the position is actually marked at, and
    `company/pricing/tariff_engine.py` marks it at an EWMA of the daily means. So this walks the
    same EWMA -- taking `EWMA_HALF_LIFE_DAYS` from the engine rather than restating it, so the two
    cannot drift -- and measures the worst five-day move of THAT. The move in the mark, which is
    the quantity a close-out actually exposes.

    Point-in-time by construction: nothing dated on or after `as_of` is read, so this is what a
    counterparty could have computed on the day it asked, not what the decade turned out to hold.
    A close-out sized on the whole history would price 2022 into 2017's margin.

    The WORST observed move rather than a volatility estimate, deliberately: a stressed close-out
    is a tail question, and a normal-distribution sigma on a market containing 2021-22 understates
    the tail it exists to cover. The empirical worst is honest about being bounded by what has
    actually happened.

    Returns `None` when the history is too short to contain one `days`-length window -- a refusal,
    not a zero, because a zero would waive the demand on the exact input it could not evaluate.

    RAISES `ValueError` when given records it could not parse a single row from. That is a
    different failure from "not enough history": it means the feed's shape is not what this
    function was told to expect, which is OUR bug and must not be absorbed into a data-shaped
    answer. Loud is the correct blast radius for a key mismatch -- silence is what made the first
    draft's defect survive.
    """
    by_day: dict[str, list[float]] = {}
    parsed = 0
    for record in price_records or []:
        try:
            when = str(record[date_key])[:10]
            price = float(record[price_key])
        except (KeyError, TypeError, ValueError):
            continue
        parsed += 1
        if when >= as_of or not isfinite(price) or price <= 0.0:
            continue
        by_day.setdefault(when, []).append(price)

    if price_records and parsed == 0:
        raise ValueError(
            f"close_out_move_fraction_from_history parsed 0 of {len(price_records)} records: "
            f"no row carried both {date_key!r} and a numeric {price_key!r}. This is a feed-shape "
            "mismatch, not a short history -- fix the keys rather than treating the result as "
            "'unmeasurable', which would demand collateral from every counterparty."
        )

    rows = sorted((day, sum(v) / len(v)) for day, v in by_day.items())
    if len(rows) <= days:
        return None

    # The engine's own smoothing, imported rather than restated so a change there follows here.
    from company.pricing.tariff_engine import EWMA_HALF_LIFE_DAYS

    alpha = 1.0 - 0.5 ** (1.0 / EWMA_HALF_LIFE_DAYS)
    marks: list[float] = []
    ewma = rows[0][1]
    marks.append(ewma)
    for _day, value in rows[1:]:
        ewma = alpha * value + (1.0 - alpha) * ewma
        marks.append(ewma)

    worst = 0.0
    for i in range(days, len(marks)):
        start = marks[i - days]
        if start <= 0.0:
            continue
        move = abs(marks[i] - start) / start
        if move > worst:
            worst = move
    return worst if worst > 0.0 else None
