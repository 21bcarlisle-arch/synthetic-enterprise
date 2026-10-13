"""Tests for saas.growth_mandate — Phase 8a."""

import datetime as dt

import pytest

from saas.growth_mandate import (
    ACQUISITION_WIN_RATE,
    FIXED_COST_MONTHLY,
    MANDATE,
    acquisition_budget_gbp,
    cost_per_acquisition_gbp,
    forecast_churns_next_year,
    roll_acquisition,
)


def test_mandate_constants_exist_with_correct_types():
    assert MANDATE in ("flat", "grow", "shrink")
    # `COST_PER_ACQUISITION` (invented £150/£400) was deleted 2026-08-28 and replaced by a
    # function reading the sourced model in saas/opex_ledger.py -- see
    # tests/saas/test_sourced_acquisition_costs.py for why and for the control.
    assert cost_per_acquisition_gbp("resi") > 0
    assert cost_per_acquisition_gbp("SME") == 0.0  # structural: business pays a trail instead
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
    expected = (
        0.50 * cost_per_acquisition_gbp("resi") + 0.30 * cost_per_acquisition_gbp("SME")
    )
    assert abs(budget - expected) < 0.01


def test_acquisition_budget_defaults_unknown_segment_to_resi():
    churn_forecast = {"C99": 1.0}
    segment_by_account = {}
    budget = acquisition_budget_gbp(churn_forecast, segment_by_account)
    assert abs(budget - cost_per_acquisition_gbp("resi")) < 0.01


from saas.growth_mandate import (
    ACQUISITION_WIN_RATE,
    FIXED_COST_MONTHLY,
    MANDATE,
    cost_per_acquisition_gbp,
    should_attempt_acquisition,
)


def test_mandate_is_flat():
    assert MANDATE == "flat"


def test_resi_acquisition_cost_is_the_sourced_pcs_commission():
    """Was 150.0, an invented number. Now the £25-£30 single-fuel PCS commission midpoint --
    per BILLING ACCOUNT, so a dual-fuel household costs the sourced £55."""
    assert cost_per_acquisition_gbp("resi") == pytest.approx(27.5)


def test_sme_acquisition_has_no_one_off_cost():
    """Was 400.0, the exact shape the research says not to use. Business acquisition costs a
    broker trail per kWh at billing time instead (saas/opex_ledger.py), so the one-off is a
    structural zero -- and the pairing is asserted in tests/saas/test_sourced_acquisition_costs.py
    so it cannot become a free book."""
    assert cost_per_acquisition_gbp("SME") == 0.0


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


def test_should_attempt_gates_gas_like_electricity():
    # Was "gas always proceeds": the 2021-22 first terms the rule had to refuse were mostly gas.
    proceed, reason = should_attempt_acquisition("resi", "gas", 999.0, "2022-01-01")
    assert proceed is False
    assert reason.startswith("cap_constrained (gas ")


def test_acquisition_budget_empty():
    assert acquisition_budget_gbp({}, {}) == pytest.approx(0.0)


def test_acquisition_budget_single_resi():
    budget = acquisition_budget_gbp({"C1": 0.5}, {"C1": "resi"})
    assert budget == pytest.approx(0.5 * cost_per_acquisition_gbp("resi"))


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


def test_the_campaign_holds_the_decided_capital_target_not_the_consulted_one():
    """The run's quote budget holds £115 behind each account, Ofgem's 26 July 2023 decision.

    £130 was the April 2023 consultation figure and sat here until 2026-10-12. The figure is read
    through the production chain -- `growth_desk.plan_growth_campaign_year`, which passes no MCR of
    its own and so takes this module's default -- because a module default is only the production
    constant while the one caller declines to pass one. Headroom is `net_assets - accounts x target`,
    so the target is recovered exactly from two accounts counts on one balance sheet.

    Fires on: the target back at 130 (the consulted figure), anywhere on the chain -- the constant,
    either default, or the seam starting to pass its own.
    """
    from company.interfaces.growth_desk import plan_growth_campaign_year
    from saas.growth_mandate import CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT

    assert CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT == 115.0
    small = plan_growth_campaign_year(net_assets_gbp=250_000.0, accounts_held=100)
    large = plan_growth_campaign_year(net_assets_gbp=250_000.0, accounts_held=200)
    assert small.headroom_gbp - large.headroom_gbp == pytest.approx(100 * 115.0)
    assert small.headroom_gbp == pytest.approx(250_000.0 - 100 * 115.0)


def test_capital_target_dates_its_three_periods_C14():
    """C14 (`docs/design/DIRECTOR_CANON.md`, ruled 12 Oct, decision 13): "Before the July 2023
    decision there is none; between the decision and the binding date it is a plan-ahead target
    the company may choose to meet." Binding (31 March 2025) carries the SAME £ value as
    plan-ahead -- only the basis label changes; a value-keyed control cannot tell the two apart,
    so this checks the basis directly, one partition control over the whole axis."""
    from saas.growth_mandate import (
        CAPITAL_TARGET_BINDING_DATE,
        CAPITAL_TARGET_DECIDED_DATE,
        CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT,
        capital_target_basis,
        capital_target_gbp_per_account,
    )

    assert CAPITAL_TARGET_DECIDED_DATE == dt.date(2023, 7, 26)
    assert CAPITAL_TARGET_BINDING_DATE == dt.date(2025, 3, 31)

    before = CAPITAL_TARGET_DECIDED_DATE - dt.timedelta(days=1)
    plan_ahead_start = CAPITAL_TARGET_DECIDED_DATE
    plan_ahead_mid = CAPITAL_TARGET_BINDING_DATE - dt.timedelta(days=1)
    binding = CAPITAL_TARGET_BINDING_DATE

    assert capital_target_basis(before) == "none"
    assert capital_target_basis(plan_ahead_start) == "plan_ahead"
    assert capital_target_basis(plan_ahead_mid) == "plan_ahead"
    assert capital_target_basis(binding) == "binding"

    assert capital_target_gbp_per_account(before) == 0.0
    assert capital_target_gbp_per_account(plan_ahead_start) == CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT
    assert capital_target_gbp_per_account(binding) == CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT
    # Accepts the ISO string the seam actually carries, not just a date object.
    assert capital_target_gbp_per_account(binding.isoformat()) == CAPITAL_TARGET_GBP_PER_DUAL_FUEL_ACCOUNT


def test_capital_target_basis_over_the_shipped_campaign_years_2016_2025():
    """MEASURED (2026-10-12), not asserted blind, and not reconstructed independently either:
    this records the `as_of` values the real year loop
    (`simulation.net_new_acquisition.plan_growth_campaign`) actually PASSES, over the real
    `simulation.live_population.CAMPAIGN_YEARS`, rather than rebuilding a `dt.date(y, 1, 1)` range
    by hand -- a hand-built range cannot fail if the loop's own plan-date convention ever moves
    (e.g. to mid-year), because this test would have moved with it.

    Over the shipped years, "binding" never actually occurs -- 31 March 2025 is after every plan
    date the shipped run has reached so far -- so a control asserting all three bases occur over
    the SHIPPED years would be false. This is the honest partition instead: 8 "none" years
    (2016-2023) and 2 "plan_ahead" years (2024-2025), zero "binding" ones.
    """
    from saas.growth_mandate import capital_target_basis
    from simulation import net_new_acquisition as nna
    from simulation.live_population import CAMPAIGN_YEARS

    recorded_as_of = []

    def _recording_budget(net_assets_gbp, accounts_held, quotes_issued_to_date=0,
                           wins_to_date=0, as_of=None):
        recorded_as_of.append(as_of)
        return {"quotes": 0, "binding": "mandate", "headroom_gbp": net_assets_gbp}

    nna.plan_growth_campaign(
        years=list(CAMPAIGN_YEARS), base_seed=1, opening_net_assets_gbp=1.0,
        accounts_held_at_start=1, horizon_end=dt.date(2026, 1, 1), credit_bureau=None,
        cost_per_quote_gbp={"resi": 1.0, "SME": 1.0},
        run_funnel=lambda *a, **kw: None, quote_budget_fn=_recording_budget,
    )

    assert len(recorded_as_of) == len(list(CAMPAIGN_YEARS))
    assert all(as_of is not None for as_of in recorded_as_of)
    bases = [capital_target_basis(as_of) for as_of in recorded_as_of]
    assert bases.count("none") == 8
    assert bases.count("plan_ahead") == 2
    assert bases.count("binding") == 0
    assert bases == (["none"] * 8) + (["plan_ahead"] * 2)


def test_removing_the_pre_decision_capital_constraint_cannot_tighten_a_year_C14():
    """The fix's actual effect on the shipped book, by monotonicity rather than a fresh
    multi-year run: `capital_headroom_gbp` is non-decreasing as `mcr_per_account_gbp` falls, so
    `wins_capital_allows` only rises and capital can only become LESS likely to be the binding
    reason, never more. §3a of the SEAT_FINDING doc already measured, at the OLD £130 (the
    highest of the three figures in play), that capital bound only 2025 -- every other year was
    already tighter on `growth_rate`. So lowering pre-decision years to £0 (C14's "none" period)
    cannot move a single wins/quotes number in the shipped campaign: if growth_rate was the
    binding reason at £130, it is still the binding reason at £0.

    Point-check at the real 2016 parameters (£250,000 net assets, 403 accounts, the shipped
    opening position): binding is "growth_rate" and wins/quotes are IDENTICAL at £0, £115 and
    £130, even though `wins_capital_allows` differs (606 / 268 / 246) -- the gap the capital
    figure would make, each visible and each irrelevant because growth_rate is tighter.

    Fires on: `growth_quote_budget` or `capital_headroom_gbp` changing shape so the dated £0
    period starts to move the binding reason or the quote count at these parameters.
    """
    from saas.growth_mandate import growth_quote_budget

    results = {
        mcr: growth_quote_budget("grow", 250_000.0, 403, mcr_per_account_gbp=mcr)
        for mcr in (0.0, 115.0, 130.0)
    }
    assert {r["binding"] for r in results.values()} == {"growth_rate"}
    assert len({r["quotes"] for r in results.values()}) == 1
    assert len({r["wins_rate_allows"] for r in results.values()}) == 1
    # The capital-allowed figure DOES move with the target -- confirming the test exercises a
    # real difference in input, not a no-op mutation the control can't see.
    assert results[0.0]["wins_capital_allows"] > results[115.0]["wins_capital_allows"] > results[130.0]["wins_capital_allows"]


def test_the_seam_forwards_as_of_to_date_the_target_C14():
    """The dating is reachable through the production chain, not just the module function:
    `growth_desk.plan_growth_campaign_year` carries `as_of` straight to `growth_quote_budget`
    and the seam's own `GrowthCampaignPlan.capital_target_basis` reports which period it landed
    in -- the same two scalars (a balance sheet and a date) crossing the one seam, nothing
    regulatory leaking across it (`capital_target_basis` is a bare three-way label)."""
    from company.interfaces.growth_desk import plan_growth_campaign_year

    before = plan_growth_campaign_year(
        net_assets_gbp=250_000.0, accounts_held=403, as_of="2020-01-01",
    )
    after = plan_growth_campaign_year(
        net_assets_gbp=250_000.0, accounts_held=403, as_of="2024-01-01",
    )
    undated = plan_growth_campaign_year(net_assets_gbp=250_000.0, accounts_held=403)

    assert before.capital_target_basis == "none"
    assert after.capital_target_basis == "plan_ahead"
    assert undated.capital_target_basis is None
    # No target at all in 2020: headroom is the full balance sheet.
    assert before.headroom_gbp == pytest.approx(250_000.0)
    # 2024 and the undated (flat, pre-C14-dating) call agree: both are £115.
    assert after.headroom_gbp == pytest.approx(undated.headroom_gbp)
