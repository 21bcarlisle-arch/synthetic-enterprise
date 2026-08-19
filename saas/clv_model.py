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
(customer_id/t_churn/T), just without the unstable fit step.

That pooled Beta is the PORTFOLIO prior. Each account's own projection comes
from its own posterior — the prior updated by that account's renewal history
(`fit_theta_posterior_per_account`) — evaluated in the sBG closed form
(`expected_lifetime_periods`). Reading the per-account figure out of
`distribution_customer_churn_time` instead, as this module did until
2026-08-13, made it a function of the account's position in the sampled draw:
swapping two accounts' churn beliefs changed neither account's projected
lifetime.

This module is pure: it takes the plain-dict outputs of `churn_model` and
`cost_to_serve` and returns a plain dict. No imports from `sim/`.
"""

import arviz as az
import numpy as np
import pandas as pd
from pymc_marketing.clv import ShiftedBetaGeoModelIndividual

from saas.customer_reaction import _billing_account_id

DISCOUNT_RATE_ANNUAL = 0.10  # applied per renewal period (annual contracts)

# THE COST BASIS THE BOOK IS VALUED ON — one symbol, used BOTH to index
# `cost_to_serve["by_customer"]` below AND as the label every downstream
# artefact publishes (`enterprise_value.build_enterprise_value` ->
# `enterprise_value_margin_basis` -> the site's basis line). Declaring the
# basis and consuming it through the same name is what makes the published
# label unforgeable: a future edit that values the book on a different line
# MOVES the label with it, and the parentage gate in
# `tools/generate_dashboard_data.py` then fails on the mismatch.
#
# 2026-08-17, `WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_
# THREE_QUARTERS_OF_THE_COST_STACK`: this used to read `net_margin_gbp`, which
# in `saas/cost_to_serve.py`'s key space meant gross-minus-cost-to-serve. The
# levies, network charges, capital and bad debt that a UK supplier incurs
# per-customer, per-kWh — 75.969% of gross margin — were not in the number the
# customer book was valued on. C7 was published as a £7,771.10 asset on a
# believed £1,201.15/yr while the same run's P&L gave it -£40.13/yr.
CLV_MARGIN_BASIS = "net_of_all_costs_margin_gbp"
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
    the PORTFOLIO-level Beta(alpha, beta) installed directly (method of
    moments, see `fit_theta_prior_from_churn_probabilities`) rather than via
    `.fit()`.

    `n_draws` repeated draws of the same (alpha, beta) point estimate stand
    in for a posterior, so that PyMC-Marketing's `distribution_*` helpers
    (which sample `pm.sample_posterior_predictive` over `self.idata`) have a
    posterior to draw from.

    NOT on the CLV path any more, and deliberately kept. `build_clv` used to
    read each account's expected lifetime out of this model's churn-time
    posterior predictive, which made the per-account number a function of the
    account's position in the sampled draw rather than of what the company
    believed about that account (see
    `fit_theta_posterior_per_account`). This constructor remains the
    portfolio-level view of theta and the reference for the data-shaping
    convention; it must not be reintroduced as the source of a per-account
    figure.
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


def fit_theta_posterior_per_account(churn_risk: dict) -> dict[str, tuple[float, float]]:
    """Per-account Beta(alpha, beta) for theta: the portfolio prior updated by
    THIS account's own renewal history.

    `fit_theta_prior_from_churn_probabilities` pools every renewal in the book
    into one Beta and says what the company believes about a customer it knows
    nothing else about. That is the right PRIOR and the wrong POSTERIOR: while
    it was installed as the posterior for every account alike, swapping two
    accounts' churn beliefs left both their projected lifetimes unchanged to
    three decimal places
    (`docs/staging/done/WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES_2026-08-13.md`).

    Each of the account's renewal points is one Bernoulli trial on theta whose
    outcome the company knows only in expectation — it holds
    `churn_probability`, not a realised churn flag — so the conjugate update
    takes SOFT counts:

        alpha = alpha_prior + sum(p_i)
        beta  = beta_prior  + sum(1 - p_i)

    over that account's own renewal points. Standard Beta-Bernoulli conjugacy
    with expected sufficient statistics. Two consequences are the point of it:
    an account with a long high-churn history moves further from the portfolio
    mean than one with two quiet renewals (evidence, not noise, sets the
    distance), and an account with no history of its own falls back exactly to
    the portfolio prior rather than to a draw's accident.

    The prior is fitted over the WHOLE of `churn_risk`, including accounts the
    caller will go on to exclude from the valued book: a supplier learns most
    from the customers who left.

    Accounts with no renewal points are omitted — they have no history to
    condition on, and `build_clv` excludes them anyway.
    """
    alpha_prior, beta_prior = fit_theta_prior_from_churn_probabilities(churn_risk)

    posteriors = {}
    for account_id, renewals in churn_risk.items():
        if not renewals:
            continue
        observed_churn = sum(renewal["churn_probability"] for renewal in renewals)
        observed_survival = sum(1.0 - renewal["churn_probability"] for renewal in renewals)
        posteriors[account_id] = (
            alpha_prior + observed_churn,
            beta_prior + observed_survival,
        )
    return posteriors


def expected_lifetime_periods(
    theta_posterior_by_account: dict[str, tuple[float, float]],
    max_periods: int = MAX_PROJECTION_PERIODS,
) -> dict[str, float]:
    """Expected number of renewal periods until churn, per billing account,
    under that account's own Beta(alpha, beta) posterior for theta.

    This is the shifted-beta-geometric expected lifetime in closed form,
    truncated at `max_periods`. Lifetime T is geometric on {1, 2, ...} given
    theta, so

        E[min(T, M)] = sum over t in 0..M-1 of P(T > t)
                     = sum over t in 0..M-1 of E[(1 - theta)^t]

    and for theta ~ Beta(alpha, beta) the survival term is a ratio of Beta
    functions with a product form that needs no special functions:

        E[(1 - theta)^t] = B(alpha, beta + t) / B(alpha, beta)
                         = product over k in 0..t-1 of (beta + k)/(alpha + beta + k)

    Computed rather than sampled, for two reasons beyond speed. The truncated
    sum is bounded by construction, where the untruncated mean E[1/theta] =
    (alpha + beta - 1)/(alpha - 1) diverges as alpha approaches 1 and then gets
    clipped by a cap doing load-bearing work. And it is exact, so an account's
    projected lifetime no longer depends on the seed, on `n_draws`, or on where
    the account sits in the roster — the identifier-dependence the finding
    called a C-S2 RNG-substream defect as well as a valuation one.

    Monotone decreasing in the posterior mean of theta: believe a customer is
    likelier to leave and their projected lifetime falls.
    """
    lifetimes = {}
    for account_id, (alpha, beta) in theta_posterior_by_account.items():
        survival = 1.0  # P(T > 0) == 1: the account is alive now
        total = 0.0
        for t in range(max_periods):
            total += survival
            survival *= (beta + t) / (alpha + beta + t)
        lifetimes[account_id] = total
    return lifetimes


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
    excluded_accounts: set[str] | None = None,
) -> dict:
    """Project customer lifetime value (CLV) for every billing account with
    at least one renewal point.

    Combines:
      - `churn_risk` (`churn_model.build_churn_risk()`) for the per-account
        churn-probability history (and renewal-point count `T`).
      - `cost_to_serve` (`cost_to_serve.build_cost_to_serve()`'s
        `by_customer`) for `CLV_MARGIN_BASIS` — the margin left after EVERY
        cost attributable to that account's own consumption (wholesale,
        policy levies, network charges, capital, bad debt, cost-to-serve) —
        summed across the dual-fuel electricity/gas legs of each billing
        account (`saas.customer_reaction._billing_account_id`). Indexed
        directly, never `.get`: a cost_to_serve view that cannot supply the
        basis this valuation declares must raise, not value the book on
        whatever it does have (R15 fail-open).

    Returns `{billing_account_id: {alpha, beta, expected_lifetime_periods,
    avg_annual_net_margin_gbp, clv_gbp}}`. Accounts with no renewal points
    are excluded (nothing to project), as are any in `excluded_accounts` —
    the caller's judgement about which accounts are still supplied, which
    this module does not attempt to make for itself.

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
                net_margin_by_account.get(account_id, 0.0) + entry[CLV_MARGIN_BASIS]
            )
        _margin_is_avg = False

    # Only include accounts that have both renewal history and cost_to_serve data.
    # Per-year snapshots may have churn data for an account that churned before
    # accumulating any billed records in the truncated window.
    #
    # `excluded_accounts` removes accounts the CALLER has determined are no
    # longer supplied. It is applied HERE, to the valued population, and
    # deliberately not to `churn_risk` upstream: the model and its theta prior
    # below are still fitted over every account's renewal history, so a departed
    # customer keeps informing what the company believes about churn while
    # ceasing to contribute forward value. Projecting a future for a customer
    # who has gone was the published defect
    # (WORKER_FINDING_THE_BOOK_VALUE_COUNTS_CUSTOMERS_WHO_HAVE_ALREADY_LEFT);
    # forgetting they ever churned would be a second one.
    excluded = excluded_accounts or set()
    accounts = [
        account_id for account_id, renewals in churn_risk.items()
        if renewals and account_id in net_margin_by_account
        and account_id not in excluded
    ]
    if not accounts:
        return {}

    # Per-account posterior, not the pooled prior installed for everyone alike:
    # `alpha`/`beta` below now differ between accounts because the company's
    # belief about each account differs. Fitted over the WHOLE of `churn_risk`
    # (departed accounts included) and then subsetted, so which accounts the
    # caller excludes from the valued book cannot move a retained account's
    # projection.
    theta_posteriors = fit_theta_posterior_per_account(churn_risk)
    lifetimes = expected_lifetime_periods(theta_posteriors)

    result = {}
    for account_id in accounts:
        periods = len(churn_risk[account_id])
        if _margin_is_avg:
            avg_annual_net_margin = net_margin_by_account[account_id]
        else:
            avg_annual_net_margin = net_margin_by_account[account_id] / periods
        lifetime = lifetimes[account_id]
        alpha, beta = theta_posteriors[account_id]
        result[account_id] = {
            "alpha": alpha,
            "beta": beta,
            "expected_lifetime_periods": lifetime,
            "avg_annual_net_margin_gbp": avg_annual_net_margin,
            "clv_gbp": avg_annual_net_margin * _annuity_factor(lifetime, DISCOUNT_RATE_ANNUAL),
        }
    return result
