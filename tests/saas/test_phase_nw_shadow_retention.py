"""Tests for saas/reporting/shadow_retention.py -- Phase NW."""

import pytest
from saas.reporting.shadow_retention import (
    build_shadow_retention_analysis,
    _SHADOW_OFFER_DISCOUNT_PCT,
    _SHADOW_ACCEPT_PROBABILITY_FACTOR,
)


def _entry(cid="C1", date="2022-06-30", margin=1000.0, estimate=0.20):
    return {
        "customer_id": cid,
        "event_date": date,
        "company_churn_estimate": estimate,
        "expected_term_margin_gbp": margin,
        "no_offer_reason": "below_threshold",
    }


def _run(entries):
    return {"no_offer_churn_log": entries}


class TestBuildEvents:
    def test_p_accept_correct(self):
        run = _run([_entry(estimate=0.20)])
        events, _ = build_shadow_retention_analysis(run)
        expected = (1.0 - 0.20) * _SHADOW_ACCEPT_PROBABILITY_FACTOR
        assert events[0].p_accept == pytest.approx(expected)

    def test_shadow_margin_uses_discount(self):
        run = _run([_entry(margin=1000.0, estimate=0.0)])
        events, _ = build_shadow_retention_analysis(run)
        expected_retained = 1000.0 * _SHADOW_ACCEPT_PROBABILITY_FACTOR * (1.0 - _SHADOW_OFFER_DISCOUNT_PCT)
        assert events[0].shadow_margin_retained_gbp == pytest.approx(expected_retained)

    def test_shadow_offer_cost_correct(self):
        run = _run([_entry(margin=1000.0, estimate=0.0)])
        events, _ = build_shadow_retention_analysis(run)
        expected_cost = 1000.0 * _SHADOW_ACCEPT_PROBABILITY_FACTOR * _SHADOW_OFFER_DISCOUNT_PCT
        assert events[0].shadow_offer_cost_gbp == pytest.approx(expected_cost)

    def test_shadow_net_gain_equals_retained_minus_cost(self):
        run = _run([_entry(margin=1000.0, estimate=0.10)])
        events, _ = build_shadow_retention_analysis(run)
        e = events[0]
        assert e.shadow_net_gain_gbp == pytest.approx(e.shadow_margin_retained_gbp - e.shadow_offer_cost_gbp)

    def test_year_extracted_from_event_date(self):
        run = _run([_entry(date="2019-12-31")])
        events, _ = build_shadow_retention_analysis(run)
        assert events[0].year == 2019

    def test_empty_log_returns_empty(self):
        events, summaries = build_shadow_retention_analysis({})
        assert events == []
        assert summaries == []

    def test_high_churn_estimate_reduces_p_accept(self):
        run_low = _run([_entry(estimate=0.10)])
        run_high = _run([_entry(estimate=0.80)])
        evs_low, _ = build_shadow_retention_analysis(run_low)
        evs_high, _ = build_shadow_retention_analysis(run_high)
        assert evs_low[0].p_accept > evs_high[0].p_accept


class TestBuildSummaries:
    def test_summary_aggregates_by_year(self):
        run = _run([
            _entry(cid="C1", date="2022-01-01", margin=1000.0, estimate=0.10),
            _entry(cid="C2", date="2022-06-30", margin=500.0, estimate=0.20),
        ])
        _, summaries = build_shadow_retention_analysis(run)
        assert len(summaries) == 1
        assert summaries[0].year == 2022
        assert summaries[0].no_offer_count == 2

    def test_summaries_separate_years(self):
        run = _run([
            _entry(cid="C1", date="2021-01-01"),
            _entry(cid="C2", date="2022-01-01"),
        ])
        _, summaries = build_shadow_retention_analysis(run)
        assert len(summaries) == 2
        assert summaries[0].year == 2021
        assert summaries[1].year == 2022

    def test_actual_margin_lost_sum(self):
        run = _run([
            _entry(cid="C1", date="2022-01-01", margin=1000.0, estimate=0.10),
            _entry(cid="C2", date="2022-06-30", margin=500.0, estimate=0.10),
        ])
        _, summaries = build_shadow_retention_analysis(run)
        assert summaries[0].actual_margin_lost_gbp == pytest.approx(1500.0)

    def test_shadow_net_gain_positive(self):
        run = _run([_entry(margin=1000.0, estimate=0.10)])
        _, summaries = build_shadow_retention_analysis(run)
        assert summaries[0].shadow_net_gain_gbp > 0
