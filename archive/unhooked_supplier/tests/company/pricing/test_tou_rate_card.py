"""Tests for Phase Y: ToU Rate Card Optimiser.

Covers: ToURateCandidate, RateCardEvaluation, ToURateCardOptimiser.
"""
from __future__ import annotations

import pytest

from company.pricing.tou_rate_card import (
    RateCardEvaluation,
    ToURateCandidate,
    ToURateCardOptimiser,
)
from company.pricing.tou_tariff_assessor import WholesaleBandRates


class TestToURateCandidate:
    def test_octopus_go_style_rates(self):
        c = ToURateCandidate.octopus_go_style()
        assert c.overnight_p_per_kwh == 7.5
        assert c.standard_p_per_kwh == 28.5
        assert c.peak_p_per_kwh == 45.0

    def test_aggressive_ev_rates(self):
        c = ToURateCandidate.aggressive_ev()
        assert c.overnight_p_per_kwh < c.standard_p_per_kwh < c.peak_p_per_kwh

    def test_conservative_ev_rates(self):
        c = ToURateCandidate.conservative_ev()
        assert c.overnight_p_per_kwh == 10.0

    def test_invalid_rates_out_of_order_raises(self):
        with pytest.raises(ValueError):
            ToURateCandidate(overnight_p_per_kwh=30.0, standard_p_per_kwh=20.0, peak_p_per_kwh=40.0)

    def test_zero_rate_raises(self):
        with pytest.raises(ValueError):
            ToURateCandidate(overnight_p_per_kwh=0.0, standard_p_per_kwh=10.0, peak_p_per_kwh=20.0)

    def test_to_tou_rate_structure_converts(self):
        c = ToURateCandidate.octopus_go_style()
        s = c.to_tou_rate_structure()
        assert s.overnight_p_per_kwh == 7.5

    def test_candidate_is_frozen(self):
        c = ToURateCandidate.octopus_go_style()
        with pytest.raises((AttributeError, TypeError)):
            c.overnight_p_per_kwh = 99.0


class TestRateCardEvaluation:
    def _make(self, tou_margin=600.0, flat_margin=800.0, saving=200.0,
              loss_pct=25.0, viable=True) -> RateCardEvaluation:
        return RateCardEvaluation(
            candidate=ToURateCandidate.octopus_go_style(),
            flat_rate_p_per_kwh=28.5,
            annual_kwh=8000.0,
            year=2024,
            supplier_margin_tou_gbp=tou_margin,
            supplier_margin_flat_gbp=flat_margin,
            customer_saving_gbp=saving,
            margin_loss_pct=loss_pct,
            is_viable=viable,
        )

    def test_margin_delta_gbp(self):
        e = self._make(tou_margin=600.0, flat_margin=800.0)
        assert abs(e.margin_delta_gbp - (-200.0)) < 0.01

    def test_is_margin_positive_true(self):
        assert self._make(tou_margin=100.0).is_margin_positive is True

    def test_is_margin_positive_false(self):
        assert self._make(tou_margin=-50.0).is_margin_positive is False

    def test_is_customer_positive_true(self):
        assert self._make(saving=200.0).is_customer_positive is True

    def test_is_customer_positive_false(self):
        assert self._make(saving=-10.0).is_customer_positive is False

    def test_viability_reason_viable(self):
        assert self._make(viable=True, saving=200.0, tou_margin=500.0).viability_reason == "viable"

    def test_viability_reason_no_saving(self):
        assert self._make(saving=-10.0, viable=False).viability_reason == "no_customer_saving"

    def test_viability_reason_margin_loss(self):
        e = self._make(saving=200.0, tou_margin=500.0, viable=False, loss_pct=75.0)
        assert e.viability_reason == "margin_loss_exceeds_threshold"

    def test_evaluation_is_frozen(self):
        e = self._make()
        with pytest.raises((AttributeError, TypeError)):
            e.year = 9999


class TestToURateCardOptimiser:
    def _optimiser_with_go(self, threshold_pct=80.0) -> ToURateCardOptimiser:
        optimiser = ToURateCardOptimiser()
        optimiser.evaluate(
            candidate=ToURateCandidate.octopus_go_style(),
            flat_rate_p_per_kwh=28.5,
            annual_kwh=8000.0,
            year=2024,
            wholesale_band_rates=WholesaleBandRates.normal(),
            max_margin_loss_pct=threshold_pct,
        )
        return optimiser

    def test_evaluate_stores_result(self):
        o = self._optimiser_with_go()
        assert len(o.all_evaluations) == 1

    def test_octopus_go_customer_saves(self):
        o = self._optimiser_with_go()
        e = o.all_evaluations[0]
        assert e.customer_saving_gbp > 0

    def test_octopus_go_supplier_margin_positive(self):
        o = self._optimiser_with_go()
        e = o.all_evaluations[0]
        assert e.supplier_margin_tou_gbp > 0

    def test_octopus_go_not_viable_at_strict_threshold(self):
        o = self._optimiser_with_go(threshold_pct=20.0)
        assert o.viable_rates() == []

    def test_octopus_go_viable_at_loose_threshold(self):
        o = self._optimiser_with_go(threshold_pct=80.0)
        assert len(o.viable_rates()) == 1

    def test_optimal_rate_none_when_no_viable(self):
        o = self._optimiser_with_go(threshold_pct=20.0)
        assert o.optimal_rate() is None

    def test_optimal_rate_returns_highest_margin(self):
        optimiser = ToURateCardOptimiser()
        for c in [ToURateCandidate.octopus_go_style(),
                  ToURateCandidate.aggressive_ev(),
                  ToURateCandidate.conservative_ev()]:
            optimiser.evaluate(
                candidate=c,
                flat_rate_p_per_kwh=28.5,
                annual_kwh=8000.0,
                year=2024,
                wholesale_band_rates=WholesaleBandRates.normal(),
                max_margin_loss_pct=80.0,
            )
        optimal = optimiser.optimal_rate()
        assert optimal is not None
        for e in optimiser.viable_rates():
            assert optimal.supplier_margin_tou_gbp >= e.supplier_margin_tou_gbp

    def test_best_customer_rate_returns_highest_saving(self):
        optimiser = ToURateCardOptimiser()
        for c in [ToURateCandidate.octopus_go_style(), ToURateCandidate.conservative_ev()]:
            optimiser.evaluate(
                candidate=c,
                flat_rate_p_per_kwh=28.5,
                annual_kwh=8000.0,
                year=2024,
                wholesale_band_rates=WholesaleBandRates.normal(),
                max_margin_loss_pct=80.0,
            )
        best = optimiser.best_customer_rate()
        assert best is not None
        for e in optimiser.viable_rates():
            assert best.customer_saving_gbp >= e.customer_saving_gbp

    def test_conservative_margin_higher_than_go(self):
        optimiser = ToURateCardOptimiser()
        for c in [ToURateCandidate.octopus_go_style(), ToURateCandidate.conservative_ev()]:
            optimiser.evaluate(
                candidate=c,
                flat_rate_p_per_kwh=28.5,
                annual_kwh=8000.0,
                year=2024,
                wholesale_band_rates=WholesaleBandRates.normal(),
                max_margin_loss_pct=80.0,
            )
        evals = {e.candidate.overnight_p_per_kwh: e for e in optimiser.all_evaluations}
        assert evals[10.0].supplier_margin_tou_gbp > evals[7.5].supplier_margin_tou_gbp

    def test_aggressive_customer_saving_highest(self):
        optimiser = ToURateCardOptimiser()
        for c in [ToURateCandidate.octopus_go_style(), ToURateCandidate.aggressive_ev()]:
            optimiser.evaluate(
                candidate=c,
                flat_rate_p_per_kwh=28.5,
                annual_kwh=8000.0,
                year=2024,
                wholesale_band_rates=WholesaleBandRates.normal(),
                max_margin_loss_pct=80.0,
            )
        evals = {e.candidate.overnight_p_per_kwh: e for e in optimiser.all_evaluations}
        assert evals[5.0].customer_saving_gbp > evals[7.5].customer_saving_gbp

    def test_crisis_year_wholesale_reduces_margin(self):
        optimiser_normal = ToURateCardOptimiser()
        optimiser_crisis = ToURateCardOptimiser()
        c = ToURateCandidate.octopus_go_style()
        for o, rates in [(optimiser_normal, WholesaleBandRates.normal()),
                         (optimiser_crisis, WholesaleBandRates.crisis())]:
            o.evaluate(c, 28.5, 8000.0, 2022, rates, max_margin_loss_pct=80.0)
        normal_margin = optimiser_normal.all_evaluations[0].supplier_margin_tou_gbp
        crisis_margin = optimiser_crisis.all_evaluations[0].supplier_margin_tou_gbp
        assert crisis_margin < normal_margin

    def test_optimiser_summary_keys(self):
        o = self._optimiser_with_go(threshold_pct=80.0)
        s = o.optimiser_summary()
        assert "candidates_evaluated" in s
        assert "viable_count" in s
        assert "optimal_overnight_p" in s
        assert "optimal_margin_gbp" in s

    def test_empty_optimiser_summary(self):
        o = ToURateCardOptimiser()
        s = o.optimiser_summary()
        assert s["candidates_evaluated"] == 0
        assert s["optimal_overnight_p"] is None
