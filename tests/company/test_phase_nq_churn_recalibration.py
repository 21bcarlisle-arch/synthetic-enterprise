"""Phase NQ: Churn Model Recalibration -- extended reference window.

Part A (floor): INDUSTRY_BASE_CHURN_RATE floor on enriched_churn_estimate was REMOVED
        per advisor redirect (2026-07-03). Floor shifted estimates uniformly without
        improving discrimination. PASSIVE_BASE_CHURN_RATE still applies to passive renewers only.
Part B (keep): yoy_extended comparison mode averages prior 2 years, surfacing crisis-period
        shocks that YoY misses when the reference year itself was elevated.
"""
import inspect
import pytest
from company.crm.enriched_churn_estimate import enriched_churn_estimate, INDUSTRY_BASE_CHURN_RATE
from company.crm.churn_model import (
    estimate_passive_churn_probability,
    PASSIVE_BASE_CHURN_RATE,
    PASSIVE_CHURN_CAP,
)
from company.crm.payment_behaviour_analytics import BehaviourScore
from saas.customer_reaction import score_experience_signals
from saas.churn_model import build_churn_risk


def test_industry_base_churn_rate_constant_still_defined():
    # Constant kept for documentation; no longer used as a floor in enriched_churn_estimate.
    assert INDUSTRY_BASE_CHURN_RATE == 0.05


def test_enriched_estimate_no_floor_stable_rates_long_tenure():
    # Without floor: stable rates + excellent behaviour + long tenure -> estimate below 5%.
    p = enriched_churn_estimate(80.0, 80.0, 6.0, behaviour_score=BehaviourScore.EXCELLENT)
    # Should still be positive but may be well below the old 5% floor.
    assert 0.0 < p < 0.10


def test_enriched_estimate_no_floor_when_rate_falls():
    # Rate falls (customer benefits) -> very low estimate; no artificial floor.
    p = enriched_churn_estimate(100.0, 80.0, 4.0)
    assert 0.0 < p <= 0.10


def test_enriched_estimate_normal_case_high_rate_rise():
    p = enriched_churn_estimate(80.0, 120.0, 1.0)
    assert p > 0.30


def test_passive_estimate_never_below_passive_base_rate():
    # Passive model retains its own floor -- appropriate for inert SVT-rollers.
    p = estimate_passive_churn_probability(80.0, 78.0, 6.0)
    assert p >= PASSIVE_BASE_CHURN_RATE


def test_passive_estimate_cap_still_respected():
    p_stable = estimate_passive_churn_probability(80.0, 80.0, 1.0)
    p_rising = estimate_passive_churn_probability(80.0, 160.0, 1.0)
    assert p_stable <= PASSIVE_CHURN_CAP
    assert p_rising <= PASSIVE_CHURN_CAP


_CRISIS_RECORDS = [
    {
        "customer_id": "C1",
        "settlement_date": ds,
        "settlement_period": 1,
        "revenue_gbp": bill,
        "wholesale_cost_gbp": bill * 0.8,
    }
    for ds, bill in [("2019-12-01", 100.0), ("2020-12-01", 120.0), ("2021-12-01", 200.0)]
]


def test_yoy_extended_mode_accepted():
    result = score_experience_signals(_CRISIS_RECORDS, comparison_mode="yoy_extended")
    assert "C1" in result


def test_yoy_extended_uses_2year_average_as_reference():
    ext = score_experience_signals(_CRISIS_RECORDS, comparison_mode="yoy_extended")
    dec_2021 = ext["C1"][2]
    assert abs(dec_2021["yoy_ref_gbp"] - 110.0) < 0.01


def test_yoy_extended_shows_larger_shock_than_yoy():
    yoy = score_experience_signals(_CRISIS_RECORDS, comparison_mode="yoy")
    ext = score_experience_signals(_CRISIS_RECORDS, comparison_mode="yoy_extended")
    assert ext["C1"][2]["bill_shock_score"] > yoy["C1"][2]["bill_shock_score"]


def test_yoy_extended_falls_back_when_only_one_prior_year():
    recs = _CRISIS_RECORDS[1:]
    ext = score_experience_signals(recs, comparison_mode="yoy_extended")
    yoy = score_experience_signals(recs, comparison_mode="yoy")
    assert ext["C1"][1]["yoy_ref_gbp"] == yoy["C1"][1]["yoy_ref_gbp"]


def test_build_churn_risk_accepts_yoy_extended():
    customers = [{"customer_id": "C1", "acquisition_date": "2018-01-01"}]
    recs = [
        {"customer_id": "C1", "settlement_date": ds, "settlement_period": 1,
         "revenue_gbp": bill, "wholesale_cost_gbp": bill * 0.8}
        for ds, bill in [
            ("2018-12-01", 90.0), ("2019-12-01", 100.0),
            ("2020-12-01", 120.0), ("2021-12-01", 200.0),
        ]
    ]
    result = build_churn_risk(recs, customers, comparison_mode="yoy_extended")
    assert "C1" in result


def test_build_churn_risk_default_is_yoy():
    sig = inspect.signature(build_churn_risk)
    assert sig.parameters["comparison_mode"].default == "yoy"


def test_yoy_mode_backward_compatible_after_nq():
    yoy = score_experience_signals(_CRISIS_RECORDS, comparison_mode="yoy")
    assert abs(yoy["C1"][2]["yoy_ref_gbp"] - 120.0) < 0.01
