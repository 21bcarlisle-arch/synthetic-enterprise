"""Home move win-rate model — Phase 4b-4 (customer value layer).

`saas/churn_model.py` (4b-2) estimates the probability that an account
*doesn't* renew at each annual renewal point — i.e. the occupant moves out
("churns"). That event isn't the end of the story for the property: a new
occupant moves in, and the property's supply contract either stays with us
(a "win") or goes to a competitor (a "loss"). This module estimates that
win probability, and combines it with `churn_model`'s churn probability to
produce an *effective retention probability* per renewal point — the
likelihood the property remains on supply with us, whether through a normal
renewal or through winning the post-move-in occupant.

Two factors drive the win probability, both seed estimates (see
"Open Questions" in `docs/observability/PHASE_4b_SUMMARY.md`):

  1. Segment baseline — UK "deemed contract" inertia means many residential
     movers simply continue with whatever supplier already serves the
     property, giving resi properties a relatively high baseline win rate.
     SME premises are more often re-tendered by a facilities agent at
     move-in, giving a lower baseline.
  2. Price competitiveness, scaled by EPC rating — Key Domain Insight
     (CLAUDE.md): customer reaction to bills is non-rational and driven by
     absolute £ impact, not %. A poorly-insulated (low EPC) property has
     higher absolute consumption, so the same percentage price gap versus
     the market translates into a larger £ difference — making new
     occupants of low-EPC properties more price-sensitive at the point of
     moving in, and more likely to shop around rather than accept the
     incumbent.

This module is pure: it takes the plain-dict output of
`churn_model.build_churn_risk()` plus the CUSTOMERS roster (for segment and
epc_rating) and returns a plain dict. No imports from `sim/`.
"""

# Baseline win probability when our price is exactly at the market average
# (price_differential_pct == 0), by segment.
BASE_WIN_PROBABILITY = {
    "resi": 0.55,
    "SME": 0.35,
}

# Percentage-point reduction in win probability per 1 percentage point that
# our price sits above the market average (price_differential_pct == 0.01),
# scaled by the property's EPC rating. A negative price_differential_pct
# (we're cheaper than market) increases the win probability by the same
# scaling.
PRICE_SENSITIVITY_BY_EPC = {
    "A": 0.5,
    "B": 0.5,
    "C": 1.0,
    "D": 1.5,
    "E": 2.0,
    "F": 2.5,
    "G": 3.0,
}

MIN_WIN_PROBABILITY = 0.05
MAX_WIN_PROBABILITY = 0.95


def home_move_win_probability(segment: str, epc_rating: str, price_differential_pct: float) -> float:
    """Return the probability that we win/retain a property's supply
    contract when its occupant moves out and a new occupant moves in.

    segment: "resi" or "SME" — looked up in BASE_WIN_PROBABILITY, defaulting
        to the "resi" baseline for any other value.
    epc_rating: "A" through "G" — looked up in PRICE_SENSITIVITY_BY_EPC,
        defaulting to a sensitivity of 1.0 for any other value.
    price_differential_pct: our price relative to the market average, as a
        fraction (e.g. 0.05 == we are 5% above market average; -0.05 == 5%
        below). Positive values reduce the win probability, negative values
        increase it.

    Result is clamped to [MIN_WIN_PROBABILITY, MAX_WIN_PROBABILITY].
    """
    base = BASE_WIN_PROBABILITY.get(segment, BASE_WIN_PROBABILITY["resi"])
    sensitivity = PRICE_SENSITIVITY_BY_EPC.get(epc_rating, 1.0)
    win_probability = base - price_differential_pct * sensitivity
    return max(MIN_WIN_PROBABILITY, min(MAX_WIN_PROBABILITY, win_probability))


def build_home_move_win_rates(churn_risk: dict, customers: list[dict], price_differential_pct: float) -> dict:
    """For every renewal point in `churn_risk` (see
    `churn_model.build_churn_risk()`), add the home-move win probability and
    an effective retention probability.

    Returns a dict keyed by billing-account id (same keys as `churn_risk`),
    each value a list of:
      {renewal_period, churn_probability, win_probability, effective_retention_probability}

    `win_probability` is constant across an account's renewal points (it
    depends only on that property's segment and EPC rating, plus the
    portfolio-wide `price_differential_pct`), but is repeated per renewal
    point for convenience.

    `effective_retention_probability` is the probability the property
    remains on supply with us at this renewal point, whether through a
    normal renewal (probability `1 - churn_probability`) or by winning the
    post-move-in occupant after a churn (probability
    `churn_probability * win_probability`):

      effective_retention_probability
          = (1 - churn_probability) + churn_probability * win_probability

    Accounts with no renewal points (`churn_risk[account] == []`) map to an
    empty list.

    Raises KeyError if a billing account in `churn_risk` has no matching
    entry in `customers` (looked up by `customer_id`).
    """
    profile_by_account = {c["customer_id"]: c for c in customers}

    win_rates: dict[str, list[dict]] = {}
    for account_id, renewals in churn_risk.items():
        profile = profile_by_account[account_id]
        win_probability = home_move_win_probability(
            profile["segment"], profile["epc_rating"], price_differential_pct
        )

        account_win_rates = []
        for renewal in renewals:
            churn_probability = renewal["churn_probability"]
            account_win_rates.append({
                "renewal_period": renewal["renewal_period"],
                "churn_probability": churn_probability,
                "win_probability": win_probability,
                "effective_retention_probability": (
                    (1 - churn_probability) + churn_probability * win_probability
                ),
            })

        win_rates[account_id] = account_win_rates

    return win_rates
