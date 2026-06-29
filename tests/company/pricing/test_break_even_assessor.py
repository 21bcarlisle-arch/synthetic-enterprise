"""Tests for company/pricing/break_even_assessor.py — Phase K.

Validates break-even unit rate calculation, price-cap constraint detection,
uncovered loss computation, and portfolio-level reporting.
"""
from __future__ import annotations

import pytest
from company.pricing.break_even_assessor import (
    BreakEvenAssessment,
    BreakEvenAssessorBook,
)


def _assessment(
    account_id="A1",
    year=2023,
    fuel="electricity",
    consumption_kwh=3100.0,
    total_cost_p_per_kwh=28.0,
    minimum_margin_p_per_kwh=0.5,
    cap_p_per_kwh=30.0,
) -> BreakEvenAssessment:
    return BreakEvenAssessment(
        account_id=account_id,
        year=year,
        fuel=fuel,
        consumption_kwh=consumption_kwh,
        total_cost_p_per_kwh=total_cost_p_per_kwh,
        minimum_margin_p_per_kwh=minimum_margin_p_per_kwh,
        cap_p_per_kwh=cap_p_per_kwh,
    )


class TestBreakEvenAssessment:
    def test_break_even_rate(self):
        a = _assessment(total_cost_p_per_kwh=28.0, minimum_margin_p_per_kwh=0.5)
        assert a.break_even_p_per_kwh == pytest.approx(28.5)

    def test_not_cap_constrained_when_cap_above_break_even(self):
        a = _assessment(total_cost_p_per_kwh=28.0, minimum_margin_p_per_kwh=0.5, cap_p_per_kwh=30.0)
        assert a.is_cap_constrained is False

    def test_cap_constrained_when_cap_below_break_even(self):
        a = _assessment(total_cost_p_per_kwh=30.0, minimum_margin_p_per_kwh=0.5, cap_p_per_kwh=29.0)
        assert a.is_cap_constrained is True

    def test_cap_unconstrained_when_cap_is_none(self):
        a = _assessment(cap_p_per_kwh=None)
        assert a.is_cap_constrained is False

    def test_headroom_positive_when_unconstrained(self):
        a = _assessment(total_cost_p_per_kwh=28.0, minimum_margin_p_per_kwh=0.5, cap_p_per_kwh=30.0)
        assert a.headroom_p_per_kwh == pytest.approx(1.5)

    def test_headroom_negative_when_constrained(self):
        a = _assessment(total_cost_p_per_kwh=30.0, minimum_margin_p_per_kwh=0.5, cap_p_per_kwh=29.0)
        assert a.headroom_p_per_kwh == pytest.approx(-1.5)

    def test_headroom_none_when_no_cap(self):
        a = _assessment(cap_p_per_kwh=None)
        assert a.headroom_p_per_kwh is None

    def test_uncovered_loss_zero_when_unconstrained(self):
        a = _assessment(total_cost_p_per_kwh=28.0, cap_p_per_kwh=30.0)
        assert a.uncovered_loss_gbp == 0.0

    def test_uncovered_loss_computed_when_constrained(self):
        # break_even = 30.5p; cap = 29.0p; shortfall = 1.5p; 3100 kWh -> £46.50
        a = _assessment(
            consumption_kwh=3100.0, total_cost_p_per_kwh=30.0,
            minimum_margin_p_per_kwh=0.5, cap_p_per_kwh=29.0,
        )
        assert a.uncovered_loss_gbp == pytest.approx(46.50)

    def test_minimum_viable_tariff_gbp_pa(self):
        # break_even 28.5p * 3100 kWh / 100 = £883.50
        a = _assessment(total_cost_p_per_kwh=28.0, minimum_margin_p_per_kwh=0.5,
                        consumption_kwh=3100.0)
        assert a.minimum_viable_tariff_gbp_pa == pytest.approx(883.50)

    def test_ashp_customer_high_consumption_constrained(self):
        """ASHP customer at 8,600 kWh: levy load pushes break-even above cap."""
        # Levies at 2022 peak: CM + CfD + RO + BSUoS ~6p/kWh; wholesale 20p; operating 1p
        a = _assessment(
            account_id="ASHP",
            consumption_kwh=8_600.0,
            total_cost_p_per_kwh=27.5,  # high levies at high volume
            minimum_margin_p_per_kwh=0.5,
            cap_p_per_kwh=27.0,  # 2022-Q4 cap tight
        )
        assert a.is_cap_constrained is True
        assert a.uncovered_loss_gbp > 0


class TestBreakEvenAssessorBook:
    def test_record_and_latest_for(self):
        book = BreakEvenAssessorBook()
        a = _assessment("A1")
        book.record(a)
        assert book.latest_for("A1") == a

    def test_latest_for_most_recent_year(self):
        book = BreakEvenAssessorBook()
        book.record(_assessment("A1", year=2022))
        book.record(_assessment("A1", year=2023))
        assert book.latest_for("A1").year == 2023

    def test_latest_for_fuel_filter(self):
        book = BreakEvenAssessorBook()
        book.record(_assessment("A1", fuel="electricity"))
        book.record(_assessment("A1", fuel="gas"))
        assert book.latest_for("A1", "gas").fuel == "gas"

    def test_cap_constrained_returns_list(self):
        book = BreakEvenAssessorBook()
        book.record(_assessment("A1", total_cost_p_per_kwh=29.0, cap_p_per_kwh=30.0))
        book.record(_assessment("A2", total_cost_p_per_kwh=31.0, cap_p_per_kwh=30.0))
        constrained = book.cap_constrained()
        assert len(constrained) == 1
        assert constrained[0].account_id == "A2"

    def test_total_uncovered_loss(self):
        book = BreakEvenAssessorBook()
        # A1: constrained by 1.5p; 3100 kWh -> £46.50
        book.record(_assessment("A1", consumption_kwh=3100.0,
                                 total_cost_p_per_kwh=30.0, minimum_margin_p_per_kwh=0.5,
                                 cap_p_per_kwh=29.0))
        # A2: not constrained
        book.record(_assessment("A2", total_cost_p_per_kwh=28.0, cap_p_per_kwh=30.0))
        assert book.total_uncovered_loss_gbp() == pytest.approx(46.50)

    def test_cap_constrained_rate_pct(self):
        book = BreakEvenAssessorBook()
        book.record(_assessment("A1", total_cost_p_per_kwh=29.0, cap_p_per_kwh=30.0))  # ok
        book.record(_assessment("A2", total_cost_p_per_kwh=31.0, cap_p_per_kwh=30.0))  # constrained
        assert book.cap_constrained_rate_pct() == pytest.approx(50.0)

    def test_assessor_summary(self):
        book = BreakEvenAssessorBook()
        book.record(_assessment("A1", total_cost_p_per_kwh=29.0, cap_p_per_kwh=30.0))
        book.record(_assessment("A2", total_cost_p_per_kwh=31.0, cap_p_per_kwh=30.0))
        s = book.assessor_summary()
        assert s["accounts_assessed"] == 2
        assert s["cap_constrained_count"] == 1
        assert s["cap_constrained_rate_pct"] == 50.0

    def test_assessor_summary_empty(self):
        book = BreakEvenAssessorBook()
        s = book.assessor_summary()
        assert s["accounts_assessed"] == 0

    def test_year_filter_in_summary(self):
        book = BreakEvenAssessorBook()
        book.record(_assessment("A1", year=2022, total_cost_p_per_kwh=31.0, cap_p_per_kwh=30.0))
        book.record(_assessment("A1", year=2023, total_cost_p_per_kwh=28.0, cap_p_per_kwh=30.0))
        s_2022 = book.assessor_summary(year=2022)
        s_2023 = book.assessor_summary(year=2023)
        assert s_2022["cap_constrained_count"] == 1
        assert s_2023["cap_constrained_count"] == 0

    def test_record_returns_same_object(self):
        book = BreakEvenAssessorBook()
        a = _assessment()
        assert book.record(a) is a
