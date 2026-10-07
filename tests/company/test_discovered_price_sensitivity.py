"""B8: the company learns its own customers' price response from its own renewals.

Five ways it can go wrong, one control each:
  1. it moves the belief on no evidence (a correction from nothing reads as a finding);
  2. it learns the wrong DIRECTION (departures rising with the price move must steepen it);
  3. a departure is booked against the wrong renewal (the move must be the account's own);
  4. a renewal the company cannot place is booked anyway;
  5. it reaches a policy that did not ask for it (the control and level arms must not move).
"""
from __future__ import annotations

from company.crm.competitive_pressure import CompetitivePressureLedger, pressure_ledger_scope
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.policy.decision_policy import (
    CURRENT_POLICY,
    VALUE_ARM_LEARNED_POLICY,
    VALUE_ARM_POLICY,
    policy_scope,
)
from company.pricing import discovered_price_sensitivity as dps


def _book(ledger, year, moves_and_left, method="direct_debit", believed=0.2):
    for i, (move, left) in enumerate(moves_and_left):
        account = f"A{year}-{i}"
        ledger.observe_price_response(year, method, "electricity", account, move, believed)
        if left:
            ledger.observe_competitive_loss(year, payment_method=method, account_id=account)


def test_no_evidence_moves_nothing():
    r = dps.slope_reading({}, "direct_debit", "electricity")
    assert r.delta == 0.0 and r.weight == 0.0 and not r.moved_from_prior
    flat = {"n": 10, "sx": 1.0, "sxx": 0.1, "sp": 2.0, "spx": 0.2, "losses": 3, "loss_x": 0.3}
    assert dps.slope_reading(flat, "direct_debit", "electricity").delta == 0.0  # no spread in move


def test_departures_that_rise_with_the_move_teach_a_steeper_response():
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    # Accounts priced well above the default left; those priced at or below it stayed.
    _book(ledger, 2019, [(0.4, True)] * 6 + [(0.3, True)] * 4 + [(-0.1, False)] * 10)
    sums = ledger.closed_slope_sums("direct_debit", "electricity", 2020)
    reading = dps.slope_reading(sums, "direct_debit", "electricity")
    assert reading.raw_delta > 0 and 0 < reading.weight < 1 and 0 < reading.delta < reading.raw_delta
    # Not yet closed: the same year's evidence cannot price that year (no look-ahead).
    assert ledger.closed_slope_sums("direct_debit", "electricity", 2019)["n"] == 0


def test_a_departure_is_booked_against_its_own_renewals_move():
    ledger = CompetitivePressureLedger()
    ledger.observe_price_response(2019, "direct_debit", "electricity", "X", 0.37, 0.2)
    ledger.observe_price_response(2019, "direct_debit", "electricity", "Y", -0.05, 0.2)
    ledger.observe_competitive_loss(2019, payment_method="direct_debit", account_id="X")
    sums = ledger.slope_sums[("direct_debit", "electricity", 2019)]
    assert sums["losses"] == 1 and abs(sums["loss_x"] - 0.37) < 1e-12


def test_a_renewal_the_company_cannot_place_books_nothing():
    ledger = CompetitivePressureLedger()
    ledger.observe_price_response(2019, "direct_debit", "electricity", None, 0.2, 0.2)
    ledger.observe_price_response(2019, "direct_debit", "electricity", "A", None, 0.2)
    assert ledger.slope_sums == {}


def test_only_the_learned_policy_prices_with_what_was_learned():
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    _book(ledger, 2019, [(0.4, True)] * 6 + [(0.3, True)] * 4 + [(-0.1, False)] * 10)
    args = dict(old_rate_gbp_per_mwh=250.0, new_rate_gbp_per_mwh=300.0, tenure_years=3.0,
                annual_consumption_kwh=2700.0, renewal_year=2020, payment_method="direct_debit",
                published_default_rate_gbp_per_mwh=260.0)
    with pressure_ledger_scope(ledger):
        with policy_scope(CURRENT_POLICY):
            control = enriched_churn_estimate(**args)
        with policy_scope(VALUE_ARM_POLICY):
            value = enriched_churn_estimate(**args)
        with policy_scope(VALUE_ARM_LEARNED_POLICY):
            learned = enriched_churn_estimate(**args)
    assert control == value, "a policy that did not ask for the learned response moved"
    assert learned > value, "the learned, steeper response did not raise P(leave) above the default"


# ---- step 2: one definition of the company's own move, at both ends (2026-10-03) ----------

def test_a_household_with_a_published_default_is_measured_against_it():
    assert dps.own_move(300.0, 250.0, "electricity", 2020, segment="resi",
                        published_default_rate_gbp_per_mwh=260.0) == (300.0 - 260.0) / 260.0


def test_a_business_account_never_uses_the_domestic_default_even_when_handed_one():
    """The desk used to measure every account against the domestic cap, while pricing measured a
    business account by the fallback: the learner was taught on one quantity and priced on another."""
    from company.crm.market_conditions import market_rate_move_pct
    expected = (300.0 - 250.0) / 250.0 - market_rate_move_pct(2020, fuel="electricity")
    got = dps.own_move(300.0, 250.0, "electricity", 2020, segment="SME",
                       published_default_rate_gbp_per_mwh=260.0, on_date="2020-04-01")
    assert got == expected


def test_a_renewal_before_the_cap_is_booked_so_learning_can_start_in_2017():
    from company.crm.churn_desk import RenewalObservation, estimate_renewal_churn
    ledger = CompetitivePressureLedger()
    obs = RenewalObservation(
        old_rate_gbp_per_mwh=120.0, new_rate_gbp_per_mwh=132.0, tenure_years=1.0,
        renewal_year=2017, payment_method="direct_debit", account_id="PRE", term_start="2017-03-01",
        fuel="electricity", segment="resi")
    with pressure_ledger_scope(ledger):
        estimate_renewal_churn(obs)
    sums = ledger.slope_sums.get(("direct_debit", "electricity", 2017))
    assert sums is not None and sums["n"] == 1, "a pre-cap renewal taught the company nothing"


# --- the offer's effect from the company's own holdout ----------------------------------------

def _holdout(treated_stayed, treated_n, held_stayed, held_n):
    return ([{"arm": "treated", "stayed": i < treated_stayed} for i in range(treated_n)]
            + [{"arm": "holdout", "stayed": i < held_stayed} for i in range(held_n)])


def test_the_offer_effect_interval_is_newcombes_published_one():
    """DEFECT: a home-made interval that reads plausibly and is wrong. Newcombe (1998), method 10,
    worked example 56/70 against 48/80: difference 0.2000, interval 0.0524 to 0.3339."""
    est = dps.estimate_offer_effect(_holdout(56, 70, 48, 80))
    assert round(est.effect, 4) == 0.2000
    assert (round(est.low, 4), round(est.high, 4)) == (0.0524, 0.3339)


def test_every_verdict_is_reachable_and_each_is_the_intervals():
    """DEFECT: a verdict read off the point estimate, or one branch that can never be taken. All
    four verdicts must be reachable, and a point above zero with an interval spanning it is
    undecided."""
    verdicts = {
        dps.estimate_offer_effect(_holdout(600, 1000, 500, 1000)).verdict,
        dps.estimate_offer_effect(_holdout(500, 1000, 600, 1000)).verdict,
        dps.estimate_offer_effect(_holdout(52, 100, 50, 100)).verdict,
        dps.estimate_offer_effect(_holdout(5, 10, 0, 0)).verdict,
    }
    assert verdicts == {"raises_staying", "lowers_staying", "undecided", "refused"}
    small = dps.estimate_offer_effect(_holdout(52, 100, 50, 100))
    assert small.effect > 0 and small.verdict == "undecided"


def test_an_empty_arm_is_refused_by_name_never_estimated():
    """DEFECT (fail-open): a difference against an empty arm returned as an effect."""
    est = dps.estimate_offer_effect(_holdout(0, 0, 40, 100))
    assert est.effect is None and est.low is None and est.verdict == "refused"
    assert "treated" in est.reason
