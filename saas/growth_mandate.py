"""Phase 8a — Growth Mandate & Acquisition Model.

Configuration, budget calculation, and deterministic acquisition rolls.
No simulation imports — pure business-rule module.
"""

import random

# "flat": replace each churn with an acquisition attempt.
# "grow": attempt additional proactive acquisitions (Phase 8b).
# "shrink": no acquisition attempts (wind down portfolio).
MANDATE: str = "flat"

# WHAT REPLACED `COST_PER_ACQUISITION` (2026-08-28, WORKER_FINDING_THE_SOURCED_ACQUISITION_
# MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE.md, roadmap R1/R2).
#
# This module used to hold `COST_PER_ACQUISITION = {"resi": 150.0, "SME": 400.0}` — two
# invented numbers with no source behind them, and they were what the live campaign spent.
# The researched model already existed, in `saas/opex_ledger.py`, cited to
# `docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md` (CMA Energy market investigation
# Appendix 8.3 and broker rate cards), and reached no code. The table is DELETED rather than
# re-pointed, so a caller cannot reach an unsourced figure through this namespace at all.
#
# TWO CHOICES ARE MADE HERE AND BOTH ARE VISIBLE ON PURPOSE.
#
# 1. THE RESIDENTIAL RATE IS THE SINGLE-FUEL ONE, £27.50, NOT THE DUAL-FUEL £55. The
#    acquisition event in this model fires per BILLING ACCOUNT (one fuel — 'C1' and 'C1g' are
#    two accounts of one household), so charging the dual-fuel commission per account would
#    bill £110 for a household the source prices at £55. Charging the single-fuel rate per
#    account sums to exactly the sourced £55 for a dual-fuel household and to the sourced
#    £27.50 for a single-fuel one. The sourced figure is the household's; the per-account rate
#    is the arithmetic that lands it, not a second assumption.
#
# 2. BUSINESS ACQUISITION HAS NO ONE-OFF COST AT ALL — it returns 0.0 here because the cost
#    is real but a different SHAPE: an ongoing broker trail commission embedded in the unit
#    rate for the life of the contract, charged per kWh at billing time via
#    `saas.opex_ledger.build_broker_commission_ledger_events()`. The research says this in
#    terms ("recommend modelling as an ongoing per-kWh cost line (not a one-off acquisition
#    cost) ... rather than forcing it into the same 'one-off CAC per new customer' shape").
#    The 0.0 is therefore a STRUCTURAL zero, not a missing number, and it is not a discount to
#    the book: the trail is charged, to the same ledger account 6300, over the whole term.
def cost_per_acquisition_gbp(segment: str) -> float:
    """One-off acquisition cost for one billing account in `segment`, sourced.

    Unknown segments fall back to the residential rate, matching the old table's
    `.get(segment, COST_PER_ACQUISITION["resi"])` behaviour at every call site.
    """
    from saas.opex_ledger import acquisition_cost_gbp

    if segment in _BROKER_ACQUIRED_SEGMENTS:
        return 0.0
    return acquisition_cost_gbp("pcs_aggregator", is_dual_fuel=False)


# Segments whose acquisition cost is a broker trail, not a one-off. Named here (and read by
# `saas.opex_ledger`) so the two halves of the same decision cannot drift apart: a segment
# that stops paying a one-off here must start paying a trail there, and the control
# `tests/saas/test_sourced_acquisition_costs.py` asserts exactly that pairing.
_BROKER_ACQUIRED_SEGMENTS: frozenset[str] = frozenset({"SME", "sme", "I&C", "ic"})

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
        total += prob * cost_per_acquisition_gbp(segment)
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

#: THE RATE THE BOOK MAY GROW IN ONE YEAR, set from the director's target.
#:
#: 2026-08-24: "Grow residential toward 200, earned through the funnel as you've just built it."
#: The served book opens at 13 records, so reaching 200 across the ten-year window needs
#: (200/13)^(1/10) - 1 = 32.4% a year. 33% is that number rounded, and it is the ONLY thing in
#: this file that comes from a target rather than from a measurement.
#:
#: WHY A RATE AND NOT A BOOK CAP. A hard cap produces a step — everything won in the first year,
#: then flat — which is a picture of a constraint wearing a supplier's clothes. A rate produces
#: the compounding curve a growing supplier actually has and leaves every year's outcome
#: contingent on that year's funnel: a bad year still wins less, and 2017 won nothing.
#:
#: IT IS NOT WHAT WILL BIND, and until 2026-08-29 what did was our own settlement ceiling:
#: exhausted inside 2017, it booked ZERO in each of the eight years after, so the target was
#: unreachable for a reason that has nothing to do with this rate.
#:
#: THE TARGET IS NOW MET, AND THE PUBLISHED BOOK IS A SAMPLE OF IT. On the record of
#: 2026-08-29 the supplier holds 587 accounts — 82 founders and 505 the funnel won — so
#: "toward 200" was passed in 2018 and the binding reasons are commercial in all ten years
#: (growth_rate in nine, capital in 2025). What this machine can SETTLE is a uniform ~18%
#: SAMPLE of them -- read the rate off the run's own record rather than from this comment,
#: which is the mistake this module's neighbour made and paid for -- reported per year as
#: `wins`/`funnel_wins` and per campaign as `settlement_sample_rate`. The director asked for
#: the engine constraint SURFACED: it is a rate on every row rather than a cliff in the middle
#: of the decade. See `net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET` and
#: docs/design/SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md.
#:
#: WHAT BINDS NOW IS A DIFFERENT ENGINEERING CEILING, and it is stated here so the next reader
#: does not have to rediscover it: three of the ten years are MARKET-BOUND at
#: `net_new_acquisition.PROSPECTS_PER_YEAR` (400) — in 2024 the company could afford 861 quotes
#: and only 400 prospects exist to quote. That is our number, not the GB switching market's, and
#: it is the next artefact in this chain.
#:
#: THE FINDING UNDERNEATH, which belongs to PB2: a supplier holding this much capital against a
#: book this small is over-capitalised, and the published company is small because it is a
#: fixture rather than because it is poor.
MAX_BOOK_GROWTH_RATE_PER_YEAR: float = 0.33

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
#: The company's own quote book must be this large before its realised rate displaces the prior.
#: One bad year is not a rate. Below this the sample is noise and planning off it would swing the
#: campaign harder than the evidence justifies -- above it, the company has issued enough quotes
#: that its own conversion is the better estimate of its next one.
MIN_QUOTES_FOR_REALISED_RATE: int = 40

#: The floor a realised rate is clamped to before it becomes a divisor. A year that won NOTHING is
#: a real and important outcome, but 1/0 is not a plan -- untreated it asks for infinite quotes,
#: and the capital ceiling would then silently become the only thing bounding the campaign. The
#: company concludes "worse than anything I have seen", not "free".
MIN_CREDIBLE_WIN_RATE: float = 0.01


def realised_win_rate(quotes_issued: int, wins: int) -> float | None:
    """The company's OWN conversion, or None when it has not yet issued enough quotes to have one.

    This is the company's commercial record, not a read through the wall: a real supplier knows
    how many quotes it sent and how many became customers, because it sent them. Nothing here
    consults who won or why -- only the two counts the company itself booked.
    """
    if quotes_issued < MIN_QUOTES_FOR_REALISED_RATE:
        return None
    if quotes_issued <= 0:
        return None
    return max(MIN_CREDIBLE_WIN_RATE, wins / quotes_issued)


#: Quotes per win, used to turn a capital ceiling into a quote budget. NOT a constant of the
#: world: it is the company's own ESTIMATE, and the estimate it starts with is its own
#: published flat win rate. `run_acquisition_funnel` is what actually decides, and its
#: realised rate is lower (five stages of leakage compounding, plus the credit bureau), so a
#: company planning off this number systematically over-estimates its wins. That is correct
#: and is the point: a supplier's acquisition plan is built on its believed conversion, and
#: discovering that the belief was optimistic is a thing this simulation should be able to
#: show rather than assume away.
#:
#: WHAT CHANGED (2026-08-24, the director's question -- can the company see its own win rate and
#: act on it?). It could not: this returned the founding assumption forever, so the belief was
#: never tested against the company's own books and the over-estimate above compounded silently
#: for the whole campaign. Now, once the company has issued enough quotes to have a rate,
#: ITS OWN replaces the prior. The prior is still where every company starts, and still what it
#: uses in year one -- what it no longer does is keep believing it after the evidence arrives.
def expected_quotes_per_win(
    segment: str = "resi",
    quotes_issued: int = 0,
    wins: int = 0,
) -> float:
    rate = ACQUISITION_WIN_RATE.get(segment, ACQUISITION_WIN_RATE["resi"])
    own = realised_win_rate(quotes_issued, wins)
    if own is not None:
        rate = own
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
    max_growth_rate: float | None = None,
    quotes_issued_to_date: int = 0,
    wins_to_date: int = 0,
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
    # Read at CALL time -- see the note in net_new_acquisition.plan_growth_campaign. A default
    # argument freezes the constant at import and makes the dial unmovable from a test or a
    # measurement run.
    if max_growth_rate is None:
        max_growth_rate = MAX_BOOK_GROWTH_RATE_PER_YEAR
    if mandate != "grow":
        return {"quotes": 0, "budget_gbp": 0.0, "wins_capital_allows": 0,
                "binding": "mandate", "headroom_gbp": 0.0,
                "believed_win_rate": None, "realised_win_rate": None,
                "planning_on": "mandate"}

    headroom = capital_headroom_gbp(net_assets_gbp, accounts_held, mcr_per_account_gbp)
    committed = headroom * capital_share
    cost_per_quote = cost_per_acquisition_gbp(segment)
    quotes_per_win = expected_quotes_per_win(segment, quotes_issued_to_date, wins_to_date)
    own_rate = realised_win_rate(quotes_issued_to_date, wins_to_date)
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
        # THE GAP, reported rather than inferred (COUPLED_TRIAD: the gap is the score). Both
        # numbers are the company's own -- what it assumed when it started, and what its books
        # have since told it -- so a reader of the growth curve can see whether the campaign was
        # planned on a founding belief or on evidence, and how far apart the two were.
        "believed_win_rate": ACQUISITION_WIN_RATE.get(segment, ACQUISITION_WIN_RATE["resi"]),
        "realised_win_rate": own_rate,
        "planning_on": "realised" if own_rate is not None else "belief",
    }
