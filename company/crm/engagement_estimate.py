"""C29: how likely THIS household is to enter a choice at its renewal, from its own record.

REUSE: company/crm/engagement_estimate.py
CLASS: CUSTOM
INDEX: searched "engagement estimate", "beta binomial", "empirical bayes", "shrink". The nearest is
       `company/crm/competitive_pressure.payment_method_engagement_reading`, which is a belief about
       a CHANNEL -- every direct-debit account gets the same figure -- and is what this module
       treats as the baseline to beat, not what it extends. Nothing in `company/` or `saas/` forms
       an engagement figure from an account's own renewal history.

WHAT IS ESTIMATED. Engagement is P(this household enters a choice at a fixed-term renewal) -- the
first of PB4's two traits. It is NOT P(leave), which is engagement times how far price moves the
household once it looks. The retention tiers in `CURRENT_POLICY` read P(leave), and so cannot tell
"will not look" from "looks and will not move". `docs/design/C29_DECISIONS_STOP_BEING_LOOKUP_TABLES_
DISCOVER_FRAME.md` gives the reasoning.

WHAT THE SUPPLIER SEES, AND NOTHING ELSE. Two things: the payment method it set up
(`get_payment_method`), and its own tariff record at each anniversary. At an anniversary the account
either started a new fixed term or left (it CHOSE), or it was on the default tariff afterwards (it
ROLLED). Leaving counts as choosing because leaving is doing something. A real supplier holds both
in its billing system.

HOW. Empirical Bayes, beta-binomial. The prior mean for an account is its channel's pooled
choose-rate on the company's own book. The prior strength is fitted by method of moments to how much
more accounts differ than binomial noise alone would make them differ. When the book shows no excess
spread, the strength is infinite and every account sits at its channel rate. That is the honest
answer when the record cannot separate accounts, and it collapses the estimate onto the baseline
rather than inventing a spread. No constant here is picked: the only inputs are the book's own
counts.

ONE OPT-IN READER. It was graded against the world's trait first
(`tests/company/test_the_per_account_engagement_estimate_ranks_better_than_the_channel_alone.py`),
and again on the refitted world of 2026-10-05, where the world arm's lift fell from 0.74 to 0.51
and stayed above its shuffle null. `engagement_at` is what the retention guard reads, through
`company/interfaces/growth_desk.py`, when a policy sets `retention_weighs_engagement`; no standing policy does, so no run moves until an arm asks.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Mapping, Sequence

CHOSE = "chose"
ROLLED = "rolled"
OUTCOMES = (CHOSE, ROLLED)


@dataclass(frozen=True)
class EngagementEstimate:
    account_id: str
    channel: str
    chose: int
    anniversaries: int
    channel_rate: float
    estimate: float
    #: `None` = the book showed no spread beyond noise, so the estimate IS the channel rate.
    prior_strength: float | None


def renewal_outcomes_from_terms(
    terms: Sequence[Mapping],
    *,
    contract_length_days: int,
    left_at_renewal: bool = False,
) -> list[str]:
    """One outcome per anniversary the account reached, read from the supplier's own term record.

    `terms` are the account's terms (`term_start` ISO date, `tariff_type` 'fixed' or 'svt'), in
    any order. The first term is the acquisition, which is a choice the account made of US. It says
    nothing about how it behaves at a renewal, so it is not counted. After that, an anniversary
    falls `contract_length_days` after the previous one. The term that starts there decides the
    outcome: a fixed term means the account chose, and the default tariff means it rolled. A
    default stint is cut into cap periods, and only the period starting AT the anniversary is a
    decision. The rest are the same choice not being made again.

    `left_at_renewal` adds the final anniversary at which the account left. That leaves no term
    behind it, so the caller (who holds the departure record) has to say so.
    """
    ordered = sorted(terms, key=lambda t: t["term_start"])
    if not ordered:
        return [CHOSE] if left_at_renewal else []
    step = timedelta(days=contract_length_days)
    next_decision = date.fromisoformat(ordered[0]["term_start"]) + step
    out: list[str] = []
    for term in ordered[1:]:
        start = date.fromisoformat(term["term_start"])
        kind = term.get("tariff_type")
        if kind == "fixed" or start >= next_decision - timedelta(days=1):
            if kind == "fixed":
                out.append(CHOSE)
            elif kind == "svt":
                out.append(ROLLED)
            else:
                continue
            next_decision = start + step
    if left_at_renewal:
        out.append(CHOSE)
    return out


def _prior_strength(counts: Sequence[tuple[int, int, float]]) -> float | None:
    """Method-of-moments beta-binomial prior strength (alpha + beta), pooled over channels.

    `counts` holds (chose, anniversaries, channel_rate) for every account with at least one
    anniversary. Each account's observed rate is compared with its own channel's rate. Under pure
    binomial noise the expected squared deviation is r(1-r)/n. A beta prior of strength s inflates
    that by (n + s) / (n(1 + s)). Solving the pooled excess for rho = 1/(1+s) gives s. Returns
    `None` when there is no excess, which means no evidence that accounts differ within a channel.
    """
    num = 0.0
    den = 0.0
    for k, n, r in counts:
        if n < 2 or r <= 0.0 or r >= 1.0:
            # One anniversary carries no within-account spread a moment fit can use, and a channel
            # rate of exactly 0 or 1 leaves no binomial variance to compare against.
            continue
        v = r * (1.0 - r)
        num += (k / n - r) ** 2 - v / n
        den += v * (n - 1) / n
    if den <= 0.0 or num <= 0.0:
        return None
    rho = min(num / den, 1.0)
    if rho >= 1.0:
        return 0.0
    return (1.0 - rho) / rho


def estimate_engagement(
    outcomes_by_account: Mapping[str, Iterable[str]],
    channel_by_account: Mapping[str, str],
) -> dict[str, EngagementEstimate]:
    """Every account's engagement estimate, fitted on this book alone.

    Every account in `channel_by_account` gets an estimate. One that has reached no anniversary
    gets its channel's rate, and says so with `anniversaries == 0`.
    """
    tallies: dict[str, tuple[int, int]] = {}
    for acc in channel_by_account:
        seq = list(outcomes_by_account.get(acc, ()))
        bad = [o for o in seq if o not in OUTCOMES]
        if bad:
            raise ValueError(f"{acc}: unknown renewal outcome(s) {bad!r}; expected {OUTCOMES}")
        tallies[acc] = (seq.count(CHOSE), len(seq))

    pooled: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for acc, (k, n) in tallies.items():
        pooled[channel_by_account[acc]][0] += k
        pooled[channel_by_account[acc]][1] += n
    book_k = sum(k for k, _ in pooled.values())
    book_n = sum(n for _, n in pooled.values())
    if book_n == 0:
        raise ValueError("no account on this book has reached an anniversary; there is nothing to "
                         "estimate engagement from, and a channel rate would be invented")
    book_rate = book_k / book_n
    # A channel with no anniversaries of its own borrows the book's rate rather than a guess.
    rate = {c: (k / n if n else book_rate) for c, (k, n) in pooled.items()}

    strength = _prior_strength(
        [(k, n, rate[channel_by_account[a]]) for a, (k, n) in tallies.items() if n])

    out: dict[str, EngagementEstimate] = {}
    for acc, (k, n) in tallies.items():
        r = rate[channel_by_account[acc]]
        if strength is None or n == 0:
            est = r
        else:
            est = (strength * r + k) / (strength + n)
        if not (0.0 <= est <= 1.0) or math.isnan(est):
            raise ValueError(f"{acc}: estimate {est!r} is not a probability")
        out[acc] = EngagementEstimate(acc, channel_by_account[acc], k, n, r, est, strength)
    return out


def engagement_at(
    account_id: str,
    as_of: str,
    *,
    terms: Iterable[Mapping],
    departures: Iterable[Mapping],
    channel_by_account: Mapping[str, str],
    fuel: str,
    contract_length_days: int,
) -> EngagementEstimate | None:
    """This account's engagement estimate, fitted on the book as it stood the day before `as_of`.

    POINT IN TIME. `terms` are the supplier's own term rows (`customer_id`, `commodity`,
    `term_start`, `tariff_type`) and `departures` its own renewal departures (`customer_id`,
    `commodity`, `event_date`, `event_type`, `departure_occasion`). Only rows dated strictly before
    `as_of` are read, so the anniversary being decided -- whose term row may already be written --
    never informs its own estimate, and nor does any account's later history.

    The book is the accounts in `channel_by_account`: the ones whose payment method the supplier
    has been asked for. `None` when this account is not among them, or when no account on the book
    has yet reached an anniversary, because a channel rate fitted on nothing would be invented.
    """
    if account_id not in channel_by_account:
        return None
    by_account: dict[str, list[Mapping]] = defaultdict(list)
    for row in terms:
        if (row.get("commodity") == fuel and row["customer_id"] in channel_by_account
                and row["term_start"] < as_of):
            by_account[row["customer_id"]].append(row)
    left = {r["customer_id"] for r in departures
            if r.get("commodity") == fuel and r.get("event_type") == "churned"
            and r.get("departure_occasion") == "renewal" and r.get("event_date", as_of) < as_of}
    outcomes = {a: renewal_outcomes_from_terms(by_account.get(a, ()),
                                               contract_length_days=contract_length_days,
                                               left_at_renewal=a in left)
                for a in channel_by_account}
    try:
        return estimate_engagement(outcomes, channel_by_account)[account_id]
    except ValueError:
        return None


def value_protected(expected_margin: float, acq_cost_saved: float,
                    engagement: float | None) -> float:
    """What a retention offer protects: the margin and the replacement cost avoided, weighted by
    the chance this household looks at all. Unweighted when there is no estimate to weigh by."""
    value = expected_margin + acq_cost_saved
    return value if engagement is None else value * engagement
