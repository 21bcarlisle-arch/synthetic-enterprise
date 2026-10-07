"""B8: the coin-drawn decision set. One control per way it can mislead:

  1. the coin never takes one arm, so every comparison is against nothing;
  2. the stay is decided by a rule of ours rather than the world's own roll;
  3. the null arm carries an effect, or the real arm's cut moves nothing in the world;
  4. the world's truth crosses to the company;
  5. a field the lean history fakes reaches the departure probability;
  6. the set leaves its households on the book of the process that built it;
  7. an effect planted with a known size is not recovered.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.interfaces.sim_interface import (
    HOLDOUT_OBSERVABLE_FIELDS,
    holdout_decision_observations,
)
from company.pricing.discovered_price_sensitivity import estimate_offer_effect
from simulation import coin_drawn_decision_set as cds

SMALL = dict(start_year=2016, end_year=2020, acquisitions_per_year=30.0)
TRUTH_FIELDS = ("p_stay_holdout", "p_stay_treated", "roll")


@pytest.fixture(scope="module")
def real():
    return cds.build_decision_set(42, cut_gbp_per_mwh=7.5, **SMALL)


@pytest.fixture(scope="module")
def null():
    return cds.build_decision_set(42, cut_gbp_per_mwh=0.0, **SMALL)


def test_the_coin_takes_both_arms(real):
    arms = real.per_arm
    assert arms["treated"] > 50 and arms["holdout"] > 50, arms
    assert cds.coin_is_treated(1, "HLD-x", "2020-01-01") == cds.coin_is_treated(1, "HLD-x", "2020-01-01")


def test_the_world_decides_the_stay_and_its_rule_is_the_roll_below_p(real):
    """`stayed` on a holdout row is the world's own event_type. That it equals roll <= P(stay) is
    what licenses the planted arm to reuse the roll; both outcomes must occur."""
    held = [r for r in real.rows if r["arm"] == "holdout"]
    assert {r["stayed"] for r in held} == {True, False}
    disagree = [r for r in held if abs(r["roll"] - r["p_stay_holdout"]) > 1e-4
                and (r["roll"] <= r["p_stay_holdout"]) != r["stayed"]]
    assert not disagree, disagree[:3]


def test_the_null_arm_has_no_effect_and_the_real_cut_raises_staying_in_the_world(real, null):
    assert null.true_effect == 0.0
    assert real.true_effect > 0.0
    assert all(r["p_stay_treated"] >= r["p_stay_holdout"] for r in real.rows)


def test_the_company_view_carries_no_world_truth(real):
    seen = holdout_decision_observations(real.rows)
    assert len(seen) == len(real.rows)
    assert all(set(r) == set(HOLDOUT_OBSERVABLE_FIELDS) for r in seen)
    assert not set(TRUTH_FIELDS) & set(HOLDOUT_OBSERVABLE_FIELDS)
    with pytest.raises(KeyError, match="stayed"):
        holdout_decision_observations([{k: v for k, v in real.rows[0].items() if k != "stayed"}])


def test_the_wholesale_cost_the_lean_history_fakes_does_not_reach_departure():
    c = cds.draw_households(42, **SMALL)[0]
    joined = dt.date.fromisoformat(c.acquisition_date)
    decision = joined + dt.timedelta(days=365)
    rate = cds.default_offer_ex_vat(joined)
    records = cds.lean_day_records(c.customer_id, c.eac_kwh, joined, decision, rate)
    inflated = [{**r, "wholesale_cost_gbp": 1e6} for r in records]
    with cds.registered([c]):
        offer = cds.default_offer_ex_vat(decision) - 7.5
        assert (cds.world_renewal(c, decision, records, rate, offer)
                == cds.world_renewal(c, decision, inflated, rate, offer))


def test_the_set_takes_its_households_back_off_the_book():
    from company.interfaces.supply_book import drawn_supply_points

    before = [p["customer_id"] for p in drawn_supply_points()]
    s = cds.build_decision_set(3, cut_gbp_per_mwh=0.0, start_year=2016, end_year=2016,
                               acquisitions_per_year=5.0)
    assert s.rows
    assert [p["customer_id"] for p in drawn_supply_points()] == before


def test_a_planted_effect_is_recovered_by_the_company_from_the_holdout_alone():
    s = cds.build_decision_set(42, cut_gbp_per_mwh=0.0, planted_effect=0.20, **SMALL)
    est = estimate_offer_effect(holdout_decision_observations(s.rows))
    assert est.verdict == "raises_staying"
    assert est.low <= s.true_effect <= est.high
