"""Tests for simulation/market_switching_propensity.py (Phase NS).

Validates the savings-elasticity churn multiplier calibrated from
DESNZ/Ofgem data (see docs/market_research/churn_price_elasticity.md).
"""
import pytest
from simulation.market_switching_propensity import (
    MARKET_SAVINGS_BY_YEAR,
    _savings_to_rate,
    market_switching_multiplier,
)


class TestSavingsToRate:
    def test_crisis_floor_when_savings_negative(self):
        assert _savings_to_rate(-200.0) == pytest.approx(0.03)

    def test_crisis_floor_when_savings_exactly_negative(self):
        assert _savings_to_rate(-1.0) == pytest.approx(0.03)

    def test_zero_savings_gives_five_pct(self):
        assert _savings_to_rate(0.0) == pytest.approx(0.05)

    def test_fifty_savings_interpolates(self):
        # 0<=S<100: 5% + 2%*(50/100) = 5% + 1% = 6%
        assert _savings_to_rate(50.0) == pytest.approx(0.06)

    def test_100_savings_boundary(self):
        # 100<=S<250: 7% + 6%*0 = 7%
        assert _savings_to_rate(100.0) == pytest.approx(0.07)

    def test_150_savings(self):
        # 100<=S<250: 7% + 6%*(50/150) = 7% + 2% = 9%
        assert _savings_to_rate(150.0) == pytest.approx(0.09)

    def test_250_savings_boundary(self):
        # 250<=S<400: 13% + 5%*0 = 13%
        assert _savings_to_rate(250.0) == pytest.approx(0.13)

    def test_saturation_above_400(self):
        assert _savings_to_rate(400.0) == pytest.approx(0.22)
        assert _savings_to_rate(9999.0) == pytest.approx(0.22)


class TestMarketSwitchingMultiplier:
    def test_calibration_year_is_1_0(self):
        # 2024 is the calibration year; multiplier must be exactly 1.0
        assert market_switching_multiplier(2024) == pytest.approx(1.0, abs=1e-9)

    def test_crisis_year_2022_below_one(self):
        # 2022: savings = -200 GBP; multiplier should be well below 1.0
        m = market_switching_multiplier(2022)
        assert m < 0.6, f"Crisis multiplier {m:.3f} should be < 0.6"
        assert m > 0.0

    def test_high_competition_2016_above_one(self):
        # 2016: savings = 300 GBP; multiplier should be substantially above 1.0
        m = market_switching_multiplier(2016)
        assert m > 1.5, f"Peak competition multiplier {m:.3f} should be > 1.5"

    def test_monotone_savings_relationship(self):
        # Higher savings years should produce higher multipliers
        # (years without post-ban factor to keep comparison clean)
        m_2016 = market_switching_multiplier(2016)   # 300 GBP
        m_2017 = market_switching_multiplier(2017)   # 200 GBP
        m_2021 = market_switching_multiplier(2021)   # 0 GBP
        m_2022 = market_switching_multiplier(2022)   # -200 GBP
        assert m_2016 > m_2017 > m_2021 > m_2022

    def test_post_ban_suppression_2023_vs_pre_ban(self):
        # 2023 savings == 100 GBP but post-ban factor 0.85 suppresses vs
        # a pre-ban year with same savings
        m_2023 = market_switching_multiplier(2023)
        # 2019 savings = 175 GBP (higher AND no post-ban suppression)
        m_2019 = market_switching_multiplier(2019)
        assert m_2019 > m_2023

    def test_unknown_year_defaults_sensibly(self):
        # Year beyond data should default to new-normal (150 GBP savings, no post-ban)
        m_future = market_switching_multiplier(2030)
        # Should be > 1 (no post-ban factor defaults to 1.0, savings default to 150)
        assert m_future > 1.0

    def test_never_returns_zero(self):
        for year in range(2015, 2030):
            m = market_switching_multiplier(year)
            assert m > 0.0, f"Year {year} returned zero multiplier"

    def test_market_savings_by_year_has_crisis_negative(self):
        # Crisis year 2022 must have negative savings to trigger floor behaviour
        assert MARKET_SAVINGS_BY_YEAR[2022] < 0

    def test_market_savings_by_year_2024_is_calibration(self):
        assert MARKET_SAVINGS_BY_YEAR[2024] == pytest.approx(150.0)


class TestMultiplierAppliedToChurn:
    """Integration-style: verify multiplier compresses crisis churn correctly."""

    def test_crisis_compresses_high_churn_probability(self):
        base_churn = 0.15  # e.g. customer with several bill shocks
        mult_2022 = market_switching_multiplier(2022)
        effective_crisis = base_churn * mult_2022
        assert effective_crisis < 0.08, (
            f"Crisis churn {effective_crisis:.3f} should be well below 8% "
            f"(multiplier {mult_2022:.3f})"
        )

    def test_high_competition_amplifies_low_churn(self):
        base_churn = 0.05  # 5% base, no bill shocks
        mult_2016 = market_switching_multiplier(2016)
        effective = base_churn * mult_2016
        assert effective > 0.08, (
            f"High-competition effective churn {effective:.3f} should exceed 8% "
            f"(multiplier {mult_2016:.3f})"
        )
