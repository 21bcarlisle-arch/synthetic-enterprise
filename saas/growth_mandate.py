"""Phase 8a — Growth Mandate & Acquisition Model.

Configuration, budget calculation, and deterministic acquisition rolls.
No simulation imports — pure business-rule module.
"""

import random

# "flat": replace each churn with an acquisition attempt.
# "grow": attempt additional proactive acquisitions (Phase 8b).
# "shrink": no acquisition attempts (wind down portfolio).
MANDATE: str = "flat"

# Cost to attempt a fresh market acquisition (spent whether won or not).
COST_PER_ACQUISITION: dict[str, float] = {
    "resi": 150.0,
    "SME": 400.0,
}

# Fixed operating overhead deducted monthly regardless of portfolio size.
# Covers: metering admin, licensing fees, basic IT/ops.
# Note: calibrated for a micro-supplier with <15 accounts.
FIXED_COST_MONTHLY: float = 50.0  # £50/month — calibrate to match overhead ratio

# Base probability of winning a cold fresh-market acquisition.
# Lower than home-move rates (55%/35%) because we're competing blind.
ACQUISITION_WIN_RATE: dict[str, float] = {
    "resi": 0.20,
    "SME": 0.12,
}


def forecast_churns_next_year(
    churn_risk: dict,
    from_period: str,
) -> dict[str, float]:
    """Return {billing_account_id: forecast_churn_probability} for accounts
    whose most recent churn entry falls within 12 months of `from_period`.

    Point-in-Time safe: uses only churn_risk already computed from
    records up to from_period. Expects churn_risk[cid] to be a list of
    dicts with 'event_date' and 'churn_probability' keys.
    """
    from datetime import date, timedelta

    try:
        window_start = date.fromisoformat(from_period[:10])
    except ValueError:
        return {}
    window_end = window_start + timedelta(days=365)

    result: dict[str, float] = {}
    for cid, entries in churn_risk.items():
        if not entries:
            continue
        relevant = [
            e for e in entries
            if window_start <= date.fromisoformat(e["event_date"][:10]) <= window_end
        ]
        if relevant:
            result[cid] = max(e["churn_probability"] for e in relevant)
    return result


def acquisition_budget_gbp(
    churn_forecast: dict[str, float],
    segment_by_account: dict[str, str],
) -> float:
    """Expected acquisition spend = sum(churn_probability * cost_per_acquisition).

    This is a budget estimate — actual spend may differ if fewer churns fire.
    Accounts not in segment_by_account default to 'resi' cost.
    """
    total = 0.0
    for cid, prob in churn_forecast.items():
        segment = segment_by_account.get(cid, "resi")
        cost = COST_PER_ACQUISITION.get(segment, COST_PER_ACQUISITION["resi"])
        total += prob * cost
    return total


def should_attempt_acquisition(
    segment: str,
    commodity: str,
    company_fwd_gbp_per_mwh: float,
    date_str: str,
) -> tuple[bool, str | None]:
    """Return (should_attempt, gate_reason).

    Gate fires for resi electricity when the Ofgem domestic price cap falls
    below the company's forward cost — meaning any fixed-term deal would be
    sold below wholesale cost. Non-resi and gas always proceed.

    gate_reason is None when the attempt should proceed.
    """
    if segment != "resi" or commodity != "electricity":
        return True, None

    from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh

    year = int(date_str[:4])
    cap = get_cap_unit_rate_gbp_per_mwh("electricity", year)
    if cap is None:
        return True, None

    if cap < company_fwd_gbp_per_mwh:
        reason = (
            f"cap_constrained (cap={cap:.0f} < fwd={company_fwd_gbp_per_mwh:.0f} GBP/MWh)"
        )
        return False, reason

    return True, None


def roll_acquisition(segment: str, rng_seed: str) -> bool:
    """Deterministic acquisition win roll.

    Uses ACQUISITION_WIN_RATE[segment] and a seeded random.Random.
    Same seed always produces the same result (deterministic run guarantee).
    """
    win_rate = ACQUISITION_WIN_RATE.get(segment, ACQUISITION_WIN_RATE["resi"])
    return random.Random(rng_seed).random() <= win_rate


# ═══════════════════════════════════════════════════════════════════════════
# THE GROWTH PLAN — atom PB3_book_growth_as_earned_outcome
#
# The `"grow"` mandate declared at the top of this module has been a comment
# since Phase 8a ("attempt additional proactive acquisitions (Phase 8b)").
# Phase 8b never happened, so `roll_acquisition` and the funnel have only ever
# been reachable from inside the CHURN branch of `run_phase2b`: every fresh
# market win is a successor to an account that just left, named
# `f"{billing_account}_{suffix}"`. Wins are therefore identically bounded by
# losses and the book cannot grow, only be replaced.
#
# WHAT DECIDES HOW BIG THE CAMPAIGN IS, and why it is capital rather than a
# chosen number. Ofgem's Minimum Capital Requirement makes a supplier hold net
# assets per domestic account -- £130, already load-bearing in this repo at
# `saas/capital/solvency.py::MCR_FLOOR_GBP_PER_CUSTOMER` and
# `company/finance/treasury.py::MCR_PER_ACCOUNT`, and anchored to the 26 July
# 2023 decision in `docs/market_research/ofgem_licence_readiness.md` §2. So
# winning a customer costs a supplier twice: the cash to run the funnel, and
# the capital it must then hold behind that account for as long as it keeps it.
# A small supplier's growth ceiling is the second one, and that is the whole
# reason the growth curve this produces bends over instead of running away.
#
# THE PLAN IS EX ANTE AND THE OUTCOME IS NOT. This function decides a BUDGET,
# which is what a real supplier sets in advance and what its board actually
# controls. It does not decide, and cannot see, how many of those quotes are
# won -- that is the funnel's business, resolved per quote, and a year in which
# every quote fails is a legal outcome of this plan. "A growth curve that
# cannot be lost is not a growth curve" (director, 2026-08-11) is a statement
# about the second half; this is only the first.
#
# NO FORECAST CONTRIBUTION, stated as a limitation rather than papered over.
# The plan spends DOWN from the capital the company actually holds and does not
# credit itself with margin it expects the new accounts to earn. That makes the
# modelled ceiling CONSERVATIVE -- a real supplier retains earnings and can
# capitalise more accounts next year. Adding a forecast contribution means
# inventing a £/account-year number, and an invented number driving the
# headline book size is worse than a bound that is honestly too tight. The
# repair, when the company has enough realised history to estimate its own
# contribution per account-year, is to pass that measurement in here.
# ═══════════════════════════════════════════════════════════════════════════

#: THE RATE THE BOOK MAY GROW IN ONE YEAR, and the honest account of where it comes from.
#:
#: NOT A COMMERCIAL JUDGEMENT, and saying so is the point. Measured on the shipped funnel over
#: 4,000 quotes, `run_acquisition_funnel` converts at 18.7% -- so this company, holding
#: £2.47m of net assets against fourteen accounts, could quote 4,665 homes in 2016 and win
#: roughly 870 of them. Capital does not bind it. The funnel does not bind it. What binds it
#: is `simulation/net_new_acquisition.py::SETTLEMENT_CUSTOMER_YEAR_BUDGET` -- the half-hourly
#: settlement this machine can build before the stage that died at 465 customer-years in
#: AO12's scale probe. 20% is simply the largest annual rate whose ten-year book fits inside
#: that budget, and it was found by measuring rather than argued: at the fixed seed 12%
#: spends 103.6 of the 279 customer-years and 20% spends 201.8, while 25% overflows and the
#: engine starts refusing wins the company paid for. Above 25% the published book gets
#: SMALLER as the rate rises (66 accounts at 25%, 56 at 30%, 53 at 40%) because the refused
#: wins are still billed -- which is the clearest possible statement that the ceiling is ours.
#:
#: WHY IT IS EXPRESSED AS A RATE RATHER THAN A CAP ON THE BOOK. A hard cap produces a step:
#: the company wins everything it can in 2016, hits the ceiling, and reports flat for nine
#: years, which is a picture of our RAM wearing a supplier's clothes. A rate produces the
#: compounding curve a growing supplier actually has, and it leaves every year's outcome
#: contingent on that year's funnel -- a bad year still wins less. What is OURS is the slope;
#: what is the company's is whether it achieves it.
#:
#: THE REAL FINDING UNDERNEATH, which belongs to PB2 and is not fixed here: a supplier holding
#: £2.47m against fourteen accounts is over-capitalised by roughly two orders of magnitude.
#: PB2_OPENING_BOOK_DISCOVER.md derives the opening book that balance sheet actually implies
#: -- 3,217 accounts. The published company is small because it is a fixture, not because it
#: is poor, and no growth rate applied to the wrong opening book fixes that.
MAX_BOOK_GROWTH_RATE_PER_YEAR: float = 0.20

#: Share of AVAILABLE capital headroom the company is willing to commit to growth in any one
#: year. A DIAL (R12), not a target: it exists so a single campaign cannot spend the whole
#: solvency buffer and leave the supplier one bad winter from breaching its MCR. A third is
#: the judgement -- it keeps two thirds of the headroom as buffer -- and nothing is scored
#: against it.
GROWTH_CAPITAL_SHARE_PER_YEAR: float = 1.0 / 3.0

#: Quotes per win, used to turn a capital ceiling into a quote budget. NOT a constant of the
#: world: it is the company's own ESTIMATE, and the estimate it starts with is its own
#: published flat win rate. `run_acquisition_funnel` is what actually decides, and its
#: realised rate is lower (five stages of leakage compounding, plus the credit bureau), so a
#: company planning off this number systematically over-estimates its wins. That is correct
#: and is the point: a supplier's acquisition plan is built on its believed conversion, and
#: discovering that the belief was optimistic is a thing this simulation should be able to
#: show rather than assume away.
def expected_quotes_per_win(segment: str = "resi") -> float:
    rate = ACQUISITION_WIN_RATE.get(segment, ACQUISITION_WIN_RATE["resi"])
    return 1.0 / rate


def capital_headroom_gbp(
    net_assets_gbp: float,
    accounts_held: int,
    mcr_per_account_gbp: float = 130.0,
) -> float:
    """Net assets above the MCR the CURRENT book already obliges. Never negative.

    A supplier below its own MCR is not a supplier with a small growth budget; it is a
    supplier in breach, and the honest answer to "how much can it spend winning customers"
    is nothing. Clamping at zero rather than returning a negative keeps a breached balance
    sheet from reading as a spending instruction downstream.
    """
    return max(0.0, net_assets_gbp - accounts_held * mcr_per_account_gbp)


def growth_quote_budget(
    mandate: str,
    net_assets_gbp: float,
    accounts_held: int,
    segment: str = "resi",
    mcr_per_account_gbp: float = 130.0,
    capital_share: float = GROWTH_CAPITAL_SHARE_PER_YEAR,
    max_growth_rate: float = MAX_BOOK_GROWTH_RATE_PER_YEAR,
) -> dict:
    """How many quotes the company issues this year, and the binding reason.

    Returns a dict with `quotes`, `budget_gbp`, `wins_capital_allows`, `binding` and
    `headroom_gbp`. `binding` is one of "mandate", "capital" or "cash" and it is returned
    rather than inferred because the three produce the same number for different reasons and
    a reader of the published growth curve is entitled to know which one flattened it.

    THE ARITHMETIC. Each won account costs `cost_per_win` in funnel spend (which is spent on
    the losers too) plus `mcr_per_account_gbp` in capital that must then be held. So the
    all-in price of one won account is the sum of the two, and the number of wins the
    committed capital supports is `committed / (cost_per_win + mcr)`. Quotes follow from
    wins through the company's own believed conversion.
    """
    if mandate != "grow":
        return {"quotes": 0, "budget_gbp": 0.0, "wins_capital_allows": 0,
                "binding": "mandate", "headroom_gbp": 0.0}

    headroom = capital_headroom_gbp(net_assets_gbp, accounts_held, mcr_per_account_gbp)
    committed = headroom * capital_share
    cost_per_quote = COST_PER_ACQUISITION.get(segment, COST_PER_ACQUISITION["resi"])
    quotes_per_win = expected_quotes_per_win(segment)
    cost_per_win = cost_per_quote * quotes_per_win
    all_in_per_win = cost_per_win + mcr_per_account_gbp
    if all_in_per_win <= 0:  # pragma: no cover - both terms are positive constants
        raise ValueError("an account cannot cost nothing to win and hold")

    wins_capital_allows = int(committed // all_in_per_win)

    # THE RATE CAP, applied AFTER the capital calculation and never instead of it, so
    # `wins_capital_allows` still reports what the balance sheet would have supported. The two
    # numbers being far apart is the finding, and collapsing them into one would hide it.
    wins_rate_allows = max(1, int(accounts_held * max_growth_rate))
    if wins_rate_allows < wins_capital_allows:
        wins, binding = wins_rate_allows, "growth_rate"
    else:
        wins, binding = wins_capital_allows, "capital"

    quotes = int(round(wins * quotes_per_win))
    return {
        "quotes": quotes,
        "budget_gbp": round(quotes * cost_per_quote, 2),
        "wins_capital_allows": wins_capital_allows,
        "wins_rate_allows": wins_rate_allows,
        "binding": binding,
        "headroom_gbp": round(headroom, 2),
    }
