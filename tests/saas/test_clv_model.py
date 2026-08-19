import pytest
from saas.clv_model import (
    _annuity_factor,
    DISCOUNT_RATE_ANNUAL,
    FALLBACK_PRIOR_PSEUDO_COUNT,
    MAX_PROJECTION_PERIODS,
    build_clv,
    build_shifted_beta_geo_data,
    expected_lifetime_periods,
    fit_theta_posterior_per_account,
    fit_theta_prior_from_churn_probabilities,
)

CHURN_RISK = {
    "C1": [
        {"renewal_period": "2017-01", "bill_shock_count": 1, "churn_probability": 0.08},
        {"renewal_period": "2018-01", "bill_shock_count": 0, "churn_probability": 0.05},
        {"renewal_period": "2019-01", "bill_shock_count": 2, "churn_probability": 0.11},
    ],
    "C2": [
        {"renewal_period": "2017-01", "bill_shock_count": 0, "churn_probability": 0.05},
        {"renewal_period": "2018-01", "bill_shock_count": 0, "churn_probability": 0.05},
    ],
    "C3": [],
}

# Both cost bases, deliberately far apart (2026-08-17 margin-basis finding).
# `contribution_margin_gbp` is gross-minus-cost-to-serve; the line the book is
# valued on, `net_of_all_costs_margin_gbp`, is additionally net of policy
# levies, network charges, capital and bad debt. Equal values here would make
# every assertion below blind to which line `build_clv` read.
COST_TO_SERVE = {
    "by_customer": {
        "C1": {
            "cost_to_serve_gbp": 100.0, "margin_gbp": 500.0,
            "contribution_margin_gbp": 400.0, "net_of_all_costs_margin_gbp": 20.0,
        },
        "C1g": {
            "cost_to_serve_gbp": 50.0, "margin_gbp": 200.0,
            "contribution_margin_gbp": 150.0, "net_of_all_costs_margin_gbp": 10.0,
        },
        "C2": {
            "cost_to_serve_gbp": 80.0, "margin_gbp": 300.0,
            "contribution_margin_gbp": 220.0, "net_of_all_costs_margin_gbp": 16.0,
        },
    }
}


def test_build_shifted_beta_geo_data_excludes_accounts_with_no_renewals():
    data = build_shifted_beta_geo_data(CHURN_RISK)
    ids = set(data["customer_id"])
    assert ids == {"C1", "C2"}


def test_build_shifted_beta_geo_data_is_all_censored():
    data = build_shifted_beta_geo_data(CHURN_RISK)
    row = data[data["customer_id"] == "C1"].iloc[0]
    assert row["t_churn"] == row["T"] == 3


def test_fit_theta_prior_method_of_moments():
    alpha, beta = fit_theta_prior_from_churn_probabilities(CHURN_RISK)
    assert alpha > 0
    assert beta > 0
    # mean of Beta(alpha, beta) should match the mean churn probability
    thetas = [0.08, 0.05, 0.11, 0.05, 0.05]
    expected_mean = sum(thetas) / len(thetas)
    assert abs(alpha / (alpha + beta) - expected_mean) < 1e-9


def test_fit_theta_prior_falls_back_when_variance_is_degenerate():
    uniform_risk = {
        "C1": [{"renewal_period": "2017-01", "bill_shock_count": 0, "churn_probability": 0.05}],
    }
    alpha, beta = fit_theta_prior_from_churn_probabilities(uniform_risk)
    assert alpha + beta == FALLBACK_PRIOR_PSEUDO_COUNT
    assert abs(alpha / (alpha + beta) - 0.05) < 1e-9


def test_build_clv_excludes_accounts_with_no_renewals():
    result = build_clv(CHURN_RISK, COST_TO_SERVE, n_draws=50)
    assert set(result.keys()) == {"C1", "C2"}


def test_build_clv_combines_dual_fuel_net_margin():
    result = build_clv(CHURN_RISK, COST_TO_SERVE, n_draws=50)
    # C1's net margin combines C1 (400.0) and C1g (150.0) over 3 renewal periods
    assert abs(result["C1"]["avg_annual_net_margin_gbp"] - (20.0 + 10.0) / 3) < 1e-9


def test_build_clv_positive_lifetime_and_value():
    result = build_clv(CHURN_RISK, COST_TO_SERVE, n_draws=50)
    for account_id, entry in result.items():
        assert entry["expected_lifetime_periods"] > 0
        assert entry["clv_gbp"] > 0
        # CLV should be less than an undiscounted perpetuity proxy: avg margin
        # times expected lifetime (the annuity factor discounts future periods)
        assert entry["clv_gbp"] < entry["avg_annual_net_margin_gbp"] * entry["expected_lifetime_periods"]


def test_build_clv_empty_churn_risk_returns_empty():
    assert build_clv({"C1": []}, COST_TO_SERVE, n_draws=50) == {}


def test_discount_rate_is_positive():
    assert 0 < DISCOUNT_RATE_ANNUAL < 1


def test_annuity_factor_zero_periods():
    assert _annuity_factor(0, 0.10) == pytest.approx(0.0)


def test_annuity_factor_one_period():
    assert _annuity_factor(1, 0.10) == pytest.approx(1 / 1.1)


def test_annuity_factor_two_periods():
    expected = 1 / 1.1 + 1 / 1.21
    assert _annuity_factor(2, 0.10) == pytest.approx(expected)


def test_annuity_factor_fractional():
    expected = 0.5 / 1.1
    assert _annuity_factor(0.5, 0.10) == pytest.approx(expected)


def test_annuity_factor_one_and_half():
    expected = 1 / 1.1 + 0.5 / 1.21
    assert _annuity_factor(1.5, 0.10) == pytest.approx(expected)


def test_annuity_factor_zero_rate_equals_periods():
    assert _annuity_factor(3, 0.0) == pytest.approx(3.0)


def test_clv_constants():
    assert DISCOUNT_RATE_ANNUAL == pytest.approx(0.10)
    assert MAX_PROJECTION_PERIODS == 50  # noqa: E501


# ---------------------------------------------------------------------------
# The estimate must follow the BELIEF, not the draw.
#
# WORKER_FINDING_THE_LIFETIME_ESTIMATE_DOES_NOT_MOVE_WHEN_THE_BELIEF_DOES
# (2026-08-13, BLOCKING): `build_clv` published a per-account
# `expected_lifetime_periods` that was a function of the account's position in
# the posterior-predictive draw. Swapping two accounts' churn beliefs left both
# estimates identical to three decimal places, and on the live book the
# correlation between believed churn and projected lifetime was +0.093 -- near
# zero and backwards.
#
# The finding names its own control and its own way of going wrong: "It cannot
# be written as an equality assertion on a fixed seed -- that greens on exactly
# the defect it must catch." So these compare the estimator against ITSELF under
# a mutation of the input, never against a recorded number.
# ---------------------------------------------------------------------------

def _belief(account_churn_probabilities: dict) -> dict:
    """A churn_risk whose only per-account signal is the believed churn
    probability: identical tenure everywhere, so nothing but the belief can
    explain a difference in the output."""
    return {
        account_id: [
            {"renewal_period": f"201{i}-01", "bill_shock_count": 0, "churn_probability": p}
            for i in range(3)
        ]
        for account_id, p in account_churn_probabilities.items()
    }


_EQUAL_MARGIN = {
    "by_customer": {
        "SAFE": {
            "cost_to_serve_gbp": 0.0, "margin_gbp": 900.0,
            "contribution_margin_gbp": 900.0, "net_of_all_costs_margin_gbp": 216.0,
        },
        "RISKY": {
            "cost_to_serve_gbp": 0.0, "margin_gbp": 900.0,
            "contribution_margin_gbp": 900.0, "net_of_all_costs_margin_gbp": 216.0,
        },
    }
}


def test_mutation_swapping_two_accounts_churn_beliefs_swaps_their_lifetimes():
    """THE killer the finding named. Two accounts, identical tenure and identical
    margin, opposite churn beliefs. Swap the beliefs between them and each
    account's projection must follow the belief to the other account.

    Under the defect both runs returned SAFE=50.000 RISKY=23.926 -- the estimate
    stayed with the NAME. This asserts the exchange, not any particular value."""
    straight = build_clv(_belief({"SAFE": 0.05, "RISKY": 0.45}), _EQUAL_MARGIN, n_draws=50)
    swapped = build_clv(_belief({"SAFE": 0.45, "RISKY": 0.05}), _EQUAL_MARGIN, n_draws=50)

    # Anti-vacuity: the two accounts must be distinguishable at all, or the
    # "swap" below is comparing a number to itself.
    assert straight["SAFE"]["expected_lifetime_periods"] != pytest.approx(
        straight["RISKY"]["expected_lifetime_periods"]
    ), "the estimator gives two oppositely-believed accounts the same lifetime"

    assert swapped["SAFE"]["expected_lifetime_periods"] == pytest.approx(
        straight["RISKY"]["expected_lifetime_periods"]
    )
    assert swapped["RISKY"]["expected_lifetime_periods"] == pytest.approx(
        straight["SAFE"]["expected_lifetime_periods"]
    )
    # And the money that hangs off it moves too -- the published figure is clv_gbp.
    assert swapped["SAFE"]["clv_gbp"] == pytest.approx(straight["RISKY"]["clv_gbp"])


def test_a_more_likely_to_churn_account_gets_a_shorter_projected_lifetime():
    """Direction, not just movement. On the live book the defect's correlation
    between believed churn and projected lifetime was POSITIVE (+0.093): the
    joint-highest-churn account carried the longest projected life on the book."""
    result = build_clv(_belief({"SAFE": 0.05, "RISKY": 0.45}), _EQUAL_MARGIN, n_draws=50)
    assert (
        result["RISKY"]["expected_lifetime_periods"]
        < result["SAFE"]["expected_lifetime_periods"]
    )
    assert result["RISKY"]["clv_gbp"] < result["SAFE"]["clv_gbp"]


def test_the_per_account_posterior_is_not_the_pooled_prior_reinstalled():
    """The defect in its exact mechanism: one pooled Beta(alpha, beta) installed
    as the posterior for every account alike. The stored per-account alpha/beta
    fields existed throughout and were identical for every account."""
    posteriors = fit_theta_posterior_per_account(_belief({"SAFE": 0.05, "RISKY": 0.45}))
    assert posteriors["SAFE"] != posteriors["RISKY"]

    prior = fit_theta_prior_from_churn_probabilities(_belief({"SAFE": 0.05, "RISKY": 0.45}))
    safe_mean = posteriors["SAFE"][0] / sum(posteriors["SAFE"])
    risky_mean = posteriors["RISKY"][0] / sum(posteriors["RISKY"])
    prior_mean = prior[0] / sum(prior)
    # Each account's posterior sits on its own side of the portfolio mean.
    assert safe_mean < prior_mean < risky_mean


def test_an_accounts_projection_does_not_depend_on_the_seed_or_the_draw_count():
    """C-S2. The finding noted the estimate depended on the account's position in
    the draw, so renaming an account or reordering the roster changed its value.
    The closed form removes the sampler from the per-account path entirely."""
    churn_risk = _belief({"SAFE": 0.05, "RISKY": 0.45})
    a = build_clv(churn_risk, _EQUAL_MARGIN, n_draws=50, random_seed=1)
    b = build_clv(churn_risk, _EQUAL_MARGIN, n_draws=997, random_seed=12345)
    assert a == b


def test_an_account_with_more_history_moves_further_from_the_portfolio_prior():
    """Shrinkage, and the reason the update takes soft counts: distance from the
    portfolio mean must be bought with EVIDENCE. Two accounts believed equally
    risky, one with three renewals of it and one with nine."""
    churn_risk = {
        "SHORT": [
            {"renewal_period": f"201{i}-01", "bill_shock_count": 0, "churn_probability": 0.45}
            for i in range(3)
        ],
        "LONG": [
            {"renewal_period": f"20{10 + i}-01", "bill_shock_count": 0, "churn_probability": 0.45}
            for i in range(9)
        ],
        "ANCHOR": [
            {"renewal_period": f"201{i}-01", "bill_shock_count": 0, "churn_probability": 0.05}
            for i in range(6)
        ],
    }
    posteriors = fit_theta_posterior_per_account(churn_risk)
    prior_mean = (lambda a, b: a / (a + b))(*fit_theta_prior_from_churn_probabilities(churn_risk))
    short_mean = posteriors["SHORT"][0] / sum(posteriors["SHORT"])
    long_mean = posteriors["LONG"][0] / sum(posteriors["LONG"])
    assert abs(long_mean - prior_mean) > abs(short_mean - prior_mean)


def test_an_account_with_no_renewal_history_gets_no_posterior_of_its_own():
    """Nothing to condition on means no per-account estimate invented for it --
    the fail-open shape would be handing it a confident number anyway."""
    churn_risk = _belief({"SAFE": 0.05, "RISKY": 0.45})
    churn_risk["NEW"] = []
    assert "NEW" not in fit_theta_posterior_per_account(churn_risk)


def test_expected_lifetime_matches_a_direct_simulation_of_the_model():
    """Independence (R15 tautology guard): the closed form is checked against a
    Monte-Carlo simulation of the shifted-beta-geometric it claims to evaluate --
    draw theta from Beta(alpha, beta), draw a geometric lifetime, take the mean --
    written from the model definition rather than from the implementation."""
    import numpy as np

    alpha, beta = 2.5, 7.5
    rng = np.random.default_rng(0)
    thetas = rng.beta(alpha, beta, size=200_000)
    simulated = np.minimum(rng.geometric(thetas), MAX_PROJECTION_PERIODS).mean()

    closed_form = expected_lifetime_periods({"X": (alpha, beta)})["X"]
    assert closed_form == pytest.approx(simulated, rel=0.02)


def test_expected_lifetime_is_bounded_by_the_projection_cap():
    """A near-immortal belief (theta -> 0) must saturate at the cap rather than
    diverge: the untruncated mean (alpha + beta - 1)/(alpha - 1) blows up as
    alpha approaches 1."""
    lifetime = expected_lifetime_periods({"X": (1.0001, 10_000.0)})["X"]
    assert 0 < lifetime <= MAX_PROJECTION_PERIODS


def test_the_published_lifetime_is_the_per_account_one():
    """Wiring, not just the helper: `build_clv`'s output must be what
    `fit_theta_posterior_per_account` + `expected_lifetime_periods` produce. The
    defect was precisely a correct-looking helper the publish path did not use."""
    churn_risk = _belief({"SAFE": 0.05, "RISKY": 0.45})
    result = build_clv(churn_risk, _EQUAL_MARGIN, n_draws=50)
    expected = expected_lifetime_periods(fit_theta_posterior_per_account(churn_risk))
    for account_id, entry in result.items():
        assert entry["expected_lifetime_periods"] == pytest.approx(expected[account_id])
        assert (entry["alpha"], entry["beta"]) == fit_theta_posterior_per_account(churn_risk)[account_id]
