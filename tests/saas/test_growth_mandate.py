"""Tests for saas.growth_mandate — Phase 8a."""

import pytest

from saas.growth_mandate import (
    acquisition_budget_gbp,
    ACQUISITION_WIN_RATE,
    COST_PER_ACQUISITION,
    FIXED_COST_MONTHLY,
    MANDATE,
    acquisition_budget_gbp,
    forecast_churns_next_year,
    roll_acquisition,
)


def test_mandate_constants_exist_with_correct_types():
    assert MANDATE in ("flat", "grow", "shrink")
    assert isinstance(COST_PER_ACQUISITION, dict)
    assert "resi" in COST_PER_ACQUISITION and "SME" in COST_PER_ACQUISITION
    assert isinstance(FIXED_COST_MONTHLY, float)
    assert FIXED_COST_MONTHLY > 0


def test_roll_acquisition_deterministic_by_seed():
    result_a = roll_acquisition("resi", "seed_abc")
    result_b = roll_acquisition("resi", "seed_abc")
    assert result_a == result_b


def test_roll_acquisition_returns_bool():
    assert isinstance(roll_acquisition("resi", "any"), bool)
    assert isinstance(roll_acquisition("SME", "any"), bool)


def test_roll_acquisition_respects_segment_rates():
    # With many seeds, win frequency should approach the configured rate.
    resi_wins = sum(roll_acquisition("resi", f"s{i}") for i in range(500))
    sme_wins = sum(roll_acquisition("SME", f"s{i}") for i in range(500))
    # Resi rate (0.20) should win more than SME rate (0.12)
    assert resi_wins > sme_wins


def test_forecast_churns_next_year_returns_accounts_in_window():
    churn_risk = {
        "C3": [{"event_date": "2020-06-01", "churn_probability": 0.45}],
        "C1": [{"event_date": "2021-01-01", "churn_probability": 0.30}],
    }
    result = forecast_churns_next_year(churn_risk, "2020-01-01")
    assert "C3" in result
    assert abs(result["C3"] - 0.45) < 1e-6


def test_forecast_churns_next_year_excludes_out_of_window():
    churn_risk = {
        "C3": [{"event_date": "2022-06-01", "churn_probability": 0.50}],
    }
    result = forecast_churns_next_year(churn_risk, "2020-01-01")
    assert "C3" not in result


def test_acquisition_budget_sums_probabilities():
    churn_forecast = {"C3": 0.50, "C5": 0.30}
    segment_by_account = {"C3": "resi", "C5": "SME"}
    budget = acquisition_budget_gbp(churn_forecast, segment_by_account)
    expected = 0.50 * COST_PER_ACQUISITION["resi"] + 0.30 * COST_PER_ACQUISITION["SME"]
    assert abs(budget - expected) < 0.01


def test_acquisition_budget_defaults_unknown_segment_to_resi():
    churn_forecast = {"C99": 1.0}
    segment_by_account = {}
    budget = acquisition_budget_gbp(churn_forecast, segment_by_account)
    assert abs(budget - COST_PER_ACQUISITION["resi"]) < 0.01


from saas.growth_mandate import (
    MANDATE,
    COST_PER_ACQUISITION,
    ACQUISITION_WIN_RATE,
    FIXED_COST_MONTHLY,
    should_attempt_acquisition,
)


def test_mandate_is_flat():
    assert MANDATE == "flat"


def test_resi_acquisition_cost():
    assert COST_PER_ACQUISITION["resi"] == pytest.approx(150.0)


def test_sme_acquisition_cost():
    assert COST_PER_ACQUISITION["SME"] == pytest.approx(400.0)


def test_resi_win_rate():
    assert ACQUISITION_WIN_RATE["resi"] == pytest.approx(0.20)


def test_sme_win_rate():
    assert ACQUISITION_WIN_RATE["SME"] == pytest.approx(0.12)


def test_fixed_cost_monthly():
    assert FIXED_COST_MONTHLY == pytest.approx(50.0)


def test_should_attempt_nonresi_always_proceeds():
    proceed, reason = should_attempt_acquisition("SME", "electricity", 999.0, "2022-01-01")
    assert proceed is True
    assert reason is None


def test_should_attempt_gas_always_proceeds():
    proceed, reason = should_attempt_acquisition("resi", "gas", 999.0, "2022-01-01")
    assert proceed is True
    assert reason is None


def test_acquisition_budget_empty():
    assert acquisition_budget_gbp({}, {}) == pytest.approx(0.0)


def test_acquisition_budget_single_resi():
    budget = acquisition_budget_gbp({"C1": 0.5}, {"C1": "resi"})
    assert budget == pytest.approx(0.5 * 150.0)


# ---------------------------------------------------------------------------
# The company's own win rate (2026-08-24, the director's question: can the
# company see its own win rate and act on it?). Before this, it could not --
# `expected_quotes_per_win` returned the founding assumption forever, so the
# belief was never tested against the company's own books and the campaign
# over-estimated its wins for the whole run. These are the company's OWN
# counts (quotes it issued, accounts it won), so nothing here crosses the wall.
# ---------------------------------------------------------------------------

def test_the_company_starts_on_its_founding_belief():
    """Year one has no book to learn from, and must plan on the prior -- unchanged behaviour."""
    from saas.growth_mandate import expected_quotes_per_win

    assert expected_quotes_per_win("resi") == pytest.approx(1.0 / ACQUISITION_WIN_RATE["resi"])
    assert expected_quotes_per_win("resi", quotes_issued=0, wins=0) == pytest.approx(
        1.0 / ACQUISITION_WIN_RATE["resi"]
    )


def test_one_bad_year_is_not_a_rate():
    """VACUITY/NOISE GUARD. Below the evidence threshold the sample is noise, and planning off
    it would swing the campaign harder than the evidence justifies."""
    from saas.growth_mandate import MIN_QUOTES_FOR_REALISED_RATE, expected_quotes_per_win

    just_under = MIN_QUOTES_FOR_REALISED_RATE - 1
    assert expected_quotes_per_win("resi", quotes_issued=just_under, wins=0) == pytest.approx(
        1.0 / ACQUISITION_WIN_RATE["resi"]
    ), "a sub-threshold sample must not displace the prior"


def test_the_company_acts_on_its_own_rate_once_it_has_one():
    """THE POINT. Enough quotes issued, and the company's OWN conversion replaces the founding
    assumption -- so a supplier whose real rate is half what it assumed plans twice the quotes."""
    from saas.growth_mandate import MIN_QUOTES_FOR_REALISED_RATE, expected_quotes_per_win

    quotes = MIN_QUOTES_FOR_REALISED_RATE * 10
    realised = ACQUISITION_WIN_RATE["resi"] / 2          # half the believed rate
    wins = int(quotes * realised)

    got = expected_quotes_per_win("resi", quotes_issued=quotes, wins=wins)
    assert got == pytest.approx(1.0 / realised, rel=0.02)
    assert got > 1.0 / ACQUISITION_WIN_RATE["resi"], "a worse realised rate must need MORE quotes"


def test_a_year_that_won_nothing_does_not_ask_for_infinite_quotes():
    """FAIL-OPEN GUARD (R15). Winning nothing is a real and important outcome, but 1/0 is not a
    plan: untreated the divisor explodes and the capital ceiling silently becomes the only thing
    bounding the campaign. The company concludes 'worse than anything I have seen', not 'free'."""
    from saas.growth_mandate import (
        MIN_CREDIBLE_WIN_RATE,
        MIN_QUOTES_FOR_REALISED_RATE,
        expected_quotes_per_win,
    )

    got = expected_quotes_per_win(
        "resi", quotes_issued=MIN_QUOTES_FOR_REALISED_RATE * 10, wins=0
    )
    assert got == pytest.approx(1.0 / MIN_CREDIBLE_WIN_RATE)
    import math
    assert math.isfinite(got)


def test_the_budget_reports_which_basis_it_planned_on():
    """THE GAP IS THE SCORE (COUPLED_TRIAD): both numbers are reported, so the growth curve reads
    as a belief being corrected rather than a number that moved."""
    from saas.growth_mandate import MIN_QUOTES_FOR_REALISED_RATE, growth_quote_budget

    naive = growth_quote_budget("grow", 250_000.0, 60)
    assert naive["planning_on"] == "belief"
    assert naive["realised_win_rate"] is None
    assert naive["believed_win_rate"] == pytest.approx(ACQUISITION_WIN_RATE["resi"])

    quotes = MIN_QUOTES_FOR_REALISED_RATE * 10
    learned = growth_quote_budget(
        "grow", 250_000.0, 60,
        quotes_issued_to_date=quotes, wins_to_date=int(quotes * 0.05),
    )
    assert learned["planning_on"] == "realised"
    assert learned["realised_win_rate"] == pytest.approx(0.05, rel=0.02)
    # The belief is still reported alongside it -- that is what makes the gap readable.
    assert learned["believed_win_rate"] == pytest.approx(ACQUISITION_WIN_RATE["resi"])


def test_a_worse_realised_rate_buys_fewer_wins_from_the_same_capital():
    """THE CONSEQUENCE, and the reason this is worth wiring at all: discovering the belief was
    optimistic must CHANGE the plan, not just annotate it. Same balance sheet, worse evidence,
    fewer wins it can afford -- because each win now costs more quotes."""
    from saas.growth_mandate import MIN_QUOTES_FOR_REALISED_RATE, growth_quote_budget

    quotes = MIN_QUOTES_FOR_REALISED_RATE * 10
    optimistic = growth_quote_budget("grow", 250_000.0, 60)
    pessimistic = growth_quote_budget(
        "grow", 250_000.0, 60,
        quotes_issued_to_date=quotes, wins_to_date=int(quotes * 0.05),
    )
    assert pessimistic["wins_capital_allows"] < optimistic["wins_capital_allows"]
