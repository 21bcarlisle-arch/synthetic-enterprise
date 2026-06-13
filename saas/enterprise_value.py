"""Enterprise value function — Phase 4b-5 (customer value layer, final
sub-phase).

The final step of the customer value layer combines all four prior
sub-phases into a single portfolio-level figure:

  - 4b-1 (`cost_to_serve`) — net margin per account, the basis of value.
  - 4b-2 (`churn_model`) — per-renewal-point churn probability.
  - 4b-3 (`clv_model`) — projects churn probability into an expected
    lifetime and a discounted CLV per account.
  - 4b-4 (`home_move_win_rate`) — for a churned account, the probability we
    retain the property by winning the new occupant.

4b-3's CLV is computed directly from churn probability: an account that
"churns" is treated as gone for good. But 4b-4 established that isn't quite
right — when an account churns (occupant moves out), the property doesn't
necessarily leave the portfolio; a new occupant may move in and stay with
us. This module closes that loop: it derives an *effective* churn
probability — the probability the property is actually lost, i.e. the
occupant moves out AND we fail to win the new occupant — and re-runs 4b-3's
CLV projection on that adjusted figure. The portfolio-wide sum of the
resulting per-account CLVs is the **enterprise value**: the total
discounted future net margin of the customer book, accounting for both
renewal risk and home-move win-back potential.

This module is pure at the seam level: it takes the plain-dict outputs of
`churn_model`, `cost_to_serve`, and the CUSTOMERS roster, and returns a
plain dict. It imports `clv_model` and `home_move_win_rate` (both
themselves pure/seam-safe) — no imports from `sim/`.
"""

from saas.clv_model import build_clv
from saas.home_move_win_rate import build_home_move_win_rates


def effective_churn_probability(churn_probability: float, win_probability: float) -> float:
    """Probability that a property is actually lost from the portfolio at
    this renewal point.

    This requires both that the occupant moves out (probability
    `churn_probability`, from `churn_model`) AND that we fail to win the
    new occupant's custom (probability `1 - win_probability`, from
    `home_move_win_rate`):

        effective_churn_probability = churn_probability * (1 - win_probability)

    This is the complement of `home_move_win_rate.build_home_move_win_rates`'s
    `effective_retention_probability` (which is `1 -
    effective_churn_probability`, restated here as its own function so
    `clv_model.fit_theta_prior_from_churn_probabilities` can consume it
    directly in place of raw `churn_probability`).
    """
    return churn_probability * (1 - win_probability)


def adjust_churn_risk_for_home_move(churn_risk: dict, home_move_win_rates: dict) -> dict:
    """Return a copy of `churn_risk` (see `churn_model.build_churn_risk()`)
    with each renewal point's `churn_probability` replaced by its
    `effective_churn_probability`, using the matching `win_probability` from
    `home_move_win_rates` (see `home_move_win_rate.build_home_move_win_rates()`)
    for the same account and renewal period.

    Other fields (`renewal_period`, `bill_shock_count`) are preserved
    unchanged. Accounts with no renewal points map to an empty list.
    """
    adjusted: dict[str, list[dict]] = {}
    for account_id, renewals in churn_risk.items():
        win_probability_by_period = {
            entry["renewal_period"]: entry["win_probability"]
            for entry in home_move_win_rates.get(account_id, [])
        }
        adjusted[account_id] = [
            {
                **renewal,
                "churn_probability": effective_churn_probability(
                    renewal["churn_probability"], win_probability_by_period[renewal["renewal_period"]]
                ),
            }
            for renewal in renewals
        ]
    return adjusted


def build_enterprise_value(
    churn_risk: dict,
    cost_to_serve: dict,
    customers: list[dict],
    price_differential_pct: float,
    n_draws: int = 500,
    random_seed: int = 42,
) -> dict:
    """Project the enterprise value of the customer book: the portfolio-wide
    sum of per-account CLV, computed using home-move-adjusted (effective)
    churn probabilities rather than raw churn probabilities.

    Returns:
      {
        "by_customer": {billing_account_id: {...same shape as
            `clv_model.build_clv()`'s per-account output, plus
            "effective_churn_probability" entries are folded into the CLV
            projection but not separately reported}},
        "portfolio": {"enterprise_value_gbp": <sum of clv_gbp>,
                       "account_count": <number of accounts included>},
      }

    Accounts with no renewal points are excluded from both `by_customer` and
    the portfolio total, matching `clv_model.build_clv()`.
    """
    home_move_win_rates = build_home_move_win_rates(churn_risk, customers, price_differential_pct)
    adjusted_churn_risk = adjust_churn_risk_for_home_move(churn_risk, home_move_win_rates)

    by_customer = build_clv(adjusted_churn_risk, cost_to_serve, n_draws=n_draws, random_seed=random_seed)

    return {
        "by_customer": by_customer,
        "portfolio": {
            "enterprise_value_gbp": sum(entry["clv_gbp"] for entry in by_customer.values()),
            "account_count": len(by_customer),
        },
    }
