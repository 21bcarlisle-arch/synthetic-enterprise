"""Customer Lifetime Value via Shifted Beta-Geometric — Phase 4b-3 (customer
value layer).

Builds on `saas/churn_model.py` (4b-2) and `saas/cost_to_serve.py` (4b-1) to
project each billing account's future net margin, using PyMC-Marketing's
`ShiftedBetaGeoModelIndividual` — the discrete-time contractual churn model
(Fader & Hardie 2007) referenced in CLAUDE.md's Scope Discipline.

Why not a direct MCMC `.fit()`: this portfolio has only 6 billing accounts,
each with ~9 annual renewal points and 0 observed churns (every account is
right-censored — still active at the end of the Phase 2b simulation window).
Fitting `ShiftedBetaGeoModelIndividual` on data this sparse and uniformly
censored is numerically unstable: MCMC produces divergences and theta
collapsing to ~0 (implying near-infinite expected lifetimes), and MAP with
informative priors produces degenerate alpha=0 estimates. See the 4b-3 "Open
Questions" in `docs/observability/PHASE_4b_SUMMARY.md` for the details.

Instead, this module derives the Beta(alpha, beta) hyperparameters for theta
(per-period churn probability) via method-of-moments directly from
`churn_model.build_churn_risk()`'s per-renewal `churn_probability` estimates
— which already encode the bill-shock-driven churn signal — and installs
those as a fixed "posterior" on the model. This still uses
`ShiftedBetaGeoModelIndividual`'s data-shaping convention
(customer_id/t_churn/T) and its `distribution_customer_churn_time` machinery
for projecting expected remaining lifetime, just without the unstable fit
step.

This module is pure: it takes the plain-dict outputs of `churn_model` and
`cost_to_serve` and returns a plain dict. No imports from `sim/`.
"""

import arviz as az
import numpy as np
import pandas as pd
from pymc_marketing.clv import ShiftedBetaGeoModelIndividual

from saas.customer_reaction import _billing_account_id

DISCOUNT_RATE_ANNUAL = 0.10  # applied per renewal period (annual contracts)
MAX_PROJECTION_PERIODS = 50  # cap on summed future renewal periods per account

# Fallback alpha+beta ("pseudo-count") when the spread of per-renewal churn
# probabilities is too small (or zero) to solve method-of-moments for a
# proper Beta distribution — keeps theta's prior weakly informative rather
# than degenerate.
FALLBACK_PRIOR_PSEUDO_COUNT = 10.0


def build_shifted_beta_geo_data(churn_risk: dict) -> pd.DataFrame:
    """Shape `churn_model.build_churn_risk()` output into the
    {customer_id, t_churn, T} convention required by
    `ShiftedBetaGeoModelIndividual`.

    Every billing account in this portfolio is right-censored — still active
    at its last observed renewal point — so `t_churn == T`, where `T` is the
    number of renewal points reached. Accounts with no renewal points
    (`churn_risk[account] == []`) are excluded — they have no contract-year
    history to project from.
    """
    rows = []
    for customer_id, renewals in churn_risk.items():
        t = len(renewals)
        if t == 0:
            continue
        rows.append({"customer_id": customer_id, "t_churn": t, "T": t})
    return pd.DataFrame(rows)


def fit_theta_prior_from_churn_probabilities(churn_risk: dict) -> tuple[float, float]:
    """Method-of-moments Beta(alpha, beta) hyperparameters for theta (the
    per-renewal churn probability), derived from every `churn_probability`
    value across `churn_risk` — NOT fit via MCMC on this portfolio's
    all-censored data (see module docstring).

    If the spread of churn probabilities is too small to solve for a proper
    Beta distribution (zero or near-zero variance — e.g. every account has
    identical bill-shock history), falls back to a Beta with mean equal to
    the observed churn probability and `FALLBACK_PRIOR_PSEUDO_COUNT` total
    pseudo-observations.
    """
    thetas = [
        renewal["churn_probability"]
        for renewals in churn_risk.values()
        for renewal in renewals
    ]
    mean = float(np.mean(thetas))
    variance = float(np.var(thetas))

    max_variance = mean * (1 - mean)
    if variance <= 0 or variance >= max_variance:
        nu = FALLBACK_PRIOR_PSEUDO_COUNT
    else:
        nu = max_variance / variance - 1

    alpha = mean * nu
    beta = (1 - mean) * nu
    return alpha, beta


def build_clv_model(
    churn_risk: dict, n_draws: int = 500, random_seed: int = 42
) -> ShiftedBetaGeoModelIndividual:
    """Construct a `ShiftedBetaGeoModelIndividual` for this portfolio, with
    an informative "posterior" for alpha/beta installed directly (method of
    moments, see `fit_theta_prior_from_churn_probabilities`) rather than via
    `.fit()`.

    `n_draws` repeated draws of the same (alpha, beta) point estimate stand
    in for a posterior, so that PyMC-Marketing's `distribution_*` helpers
    (which sample `pm.sample_posterior_predictive` over `self.idata`) have a
    posterior to draw from.
    """
    data = build_shifted_beta_geo_data(churn_risk)
    alpha, beta = fit_theta_prior_from_churn_probabilities(churn_risk)

    model = ShiftedBetaGeoModelIndividual()
    model.build_model(data=data)
    model.idata = az.from_dict(
        posterior={
            "alpha": np.full((1, n_draws), alpha),
            "beta": np.full((1, n_draws), beta),
        }
    )
    return model


def expected_lifetime_periods(
    model: ShiftedBetaGeoModelIndividual, customer_ids: list[str], random_seed: int = 42
) -> dict[str, float]:
    """Expected number of future renewal periods until churn, per billing
    account, from `model`'s churn-time posterior predictive — the mean of
    `distribution_customer_churn_time` over all draws, capped at
    `MAX_PROJECTION_PERIODS`.
    """
    draws = model.distribution_customer_churn_time(
        customer_id=customer_ids, random_seed=random_seed
    )
    means = draws.mean(dim=[d for d in draws.dims if d != "customer_id"])
    return {
        customer_id: min(float(means.sel(customer_id=customer_id)), MAX_PROJECTION_PERIODS)
        for customer_id in customer_ids
    }


def _annuity_factor(periods: float, rate: float) -> float:
    """Present value of £1 received at the end of each of the next `periods`
    periods (fractional `periods` pro-rates the final period), discounted at
    `rate` per period.
    """
    whole = int(periods)
    fraction = periods - whole
    factor = sum(1.0 / (1.0 + rate) ** k for k in range(1, whole + 1))
    if fraction > 0:
        factor += fraction / (1.0 + rate) ** (whole + 1)
    return factor


def build_clv(
    churn_risk: dict, cost_to_serve: dict, n_draws: int = 500, random_seed: int = 42,
    override_avg_margin_by_account: dict | None = None,
) -> dict:
    """Project customer lifetime value (CLV) for every billing account with
    at least one renewal point.

    Combines:
      - `churn_risk` (`churn_model.build_churn_risk()`) for the per-account
        churn-probability history (and renewal-point count `T`).
      - `cost_to_serve` (`cost_to_serve.build_cost_to_serve()`'s
        `by_customer`) for `net_margin_gbp`, summed across the dual-fuel
        electricity/gas legs of each billing account
        (`saas.customer_reaction._billing_account_id`).

    Returns `{billing_account_id: {alpha, beta, expected_lifetime_periods,
    avg_annual_net_margin_gbp, clv_gbp}}`. Accounts with no renewal points
    are excluded (nothing to project).

    `clv_gbp = avg_annual_net_margin_gbp * annuity_factor(expected_lifetime,
    DISCOUNT_RATE_ANNUAL)` — the present value of `expected_lifetime_periods`
    future years of net margin at this account's historical average,
    discounted at `DISCOUNT_RATE_ANNUAL` per year.
    """
    if override_avg_margin_by_account is not None:
        net_margin_by_account = override_avg_margin_by_account
        # override already contains avg-per-year margins; set periods=1 so the
        # division below is a no-op (we use the override directly as avg_annual).
        _margin_is_avg = True
    else:
        net_margin_by_account = {}
        for customer_id, entry in cost_to_serve["by_customer"].items():
            account_id = _billing_account_id(customer_id)
            net_margin_by_account[account_id] = (
                net_margin_by_account.get(account_id, 0.0) + entry["net_margin_gbp"]
            )
        _margin_is_avg = False

    # Only include accounts that have both renewal history and cost_to_serve data.
    # Per-year snapshots may have churn data for an account that churned before
    # accumulating any billed records in the truncated window.
    accounts = [
        account_id for account_id, renewals in churn_risk.items()
        if renewals and account_id in net_margin_by_account
    ]
    if not accounts:
        return {}

    alpha, beta = fit_theta_prior_from_churn_probabilities(churn_risk)
    model = build_clv_model(churn_risk, n_draws=n_draws, random_seed=random_seed)
    lifetimes = expected_lifetime_periods(model, accounts, random_seed=random_seed)

    result = {}
    for account_id in accounts:
        periods = len(churn_risk[account_id])
        if _margin_is_avg:
            avg_annual_net_margin = net_margin_by_account[account_id]
        else:
            avg_annual_net_margin = net_margin_by_account[account_id] / periods
        lifetime = lifetimes[account_id]
        result[account_id] = {
            "alpha": alpha,
            "beta": beta,
            "expected_lifetime_periods": lifetime,
            "avg_annual_net_margin_gbp": avg_annual_net_margin,
            "clv_gbp": avg_annual_net_margin * _annuity_factor(lifetime, DISCOUNT_RATE_ANNUAL),
        }
    return result
