"""Tests for simulation/market_switching_propensity.py (Phase NS).

Validates the savings-elasticity churn multiplier calibrated from
DESNZ/Ofgem data (see docs/market_research/churn_price_elasticity.md).
"""
import pytest

from simulation.market_switching_propensity import (
    MARKET_SAVINGS_BY_YEAR,
    _savings_to_rate,
    market_departure_rate_pct,
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
        """2016 is the peak challenger era and must sit above the 2024 reference.

        KEYED TO THE RECORD, NOT TO THE OLD CURVE'S ANSWER. This asserted `> 1.5` until
        2026-08-30, which was the savings curve's own value (2.17) and nothing else -- the
        published record puts 2016 at 17.0-17.6% against 2024's 12.5-16.1%, i.e. a ratio near
        1.21, so the old bar was a pin on a number that turned out to be 1.8x the record's. The
        property is the direction: more switching in 2016 than in the post-ban new normal.
        """
        m = market_switching_multiplier(2016)
        assert m > 1.0, f"Peak competition multiplier {m:.3f} should exceed the 2024 reference"

    def test_the_multiplier_follows_the_record_and_NOT_the_savings_ordering(self):
        """MUTATION: rebuild the multiplier off `_savings_to_rate` and this fires at 2021.

        THE FINDING THIS REPLACES A PIN WITH. The old test asserted the multiplier was monotone
        in `MARKET_SAVINGS_BY_YEAR`, which it was -- being a function of savings alone. The
        published record is NOT monotone in those savings, and that is precisely why a
        savings-only curve can never reproduce it:

            2021 carries 0 GBP of savings and a published 17.9-18.4%.
            2017 carries 200 GBP and a published 13.5-14.0%.

        So 2021 must come out ABOVE 2017 despite offering nothing to switch for -- the H2-2021
        collapse was suppliers withdrawing products, and the households who moved that year mostly
        did so through SoLR rather than by shopping. A multiplier that still ranked these two by
        savings would be reporting the curve, not the world.
        """
        assert market_switching_multiplier(2021) > market_switching_multiplier(2017)
        assert market_switching_multiplier(2020) > market_switching_multiplier(2016)
        # The crisis trough is still the bottom, and by more than the curve knew.
        assert market_switching_multiplier(2022) < market_switching_multiplier(2023) < 1.0

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
        """A high-switching year must amplify, and 2020 -- not 2016 -- is the record's peak.

        The old bar (`effective > 0.08` from a 0.05 base, i.e. a multiplier above 1.6) was the
        savings curve's 2016 value read back as a requirement. The record's high-water mark is
        2020 at 22.5-23.0%, a year the curve had at 8.0% because savings were low; the amplifying
        property survives, the year it belongs to does not.
        """
        base_churn = 0.05  # 5% base, no bill shocks
        peak = market_switching_multiplier(2020)
        assert base_churn * peak > base_churn, (
            f"the record's peak switching year must amplify churn (multiplier {peak:.3f})"
        )
        assert peak > market_switching_multiplier(2024) > market_switching_multiplier(2022)


class TestTheTwoQuantitiesStaySeparate:
    """The level and the ratio are different quantities and each has one job (2026-08-30).

    `market_switching_multiplier` divided an absolute rate by its own 2024 value, so the level
    existed for one statement and was then cancelled -- nothing downstream could read it and no
    control could compare it with a publication. Splitting them is the correction; the trap is
    that the cheapest reading of "un-normalise it" pushes the ABSOLUTE rate through a company-side
    expression written for a ratio, and silently kills a signal that crosses the wall.
    """

    def test_the_level_carries_units_the_published_record_can_be_compared_against(self):
        """MUTATION: return the multiplier from `market_departure_rate_pct` and this fires.

        A per-cent-of-accounts-per-year rate is comparable with the commons; a ratio is not.
        Every year the record covers must come back as a percentage in the record's own range,
        not as a number near 1.
        """
        for year in range(2016, 2026):
            rate = market_departure_rate_pct(year)
            assert 2.0 < rate < 30.0, (
                f"{year}: {rate} is not a percentage of domestic electricity accounts per year "
                f"-- the level has been replaced by a ratio again"
            )

    def test_the_company_facing_observable_is_still_a_ratio_and_still_carries_pressure(self):
        """THE DEAD-WIRE LEG. MUTATION: make `market_switching_multiplier` return the absolute
        rate (0.036-0.228) and this fires.

        `company/pricing/renewal_desk.py:149` reads `pressure = max(0.0, multiplier - 1.0)` off
        this value and tightens its SVT-anchored ceiling by it. Pushed an absolute rate, that
        expression is identically zero for every year in the record -- the desk's competitive
        ceiling goes quiet forever and NOTHING SAYS SO, which is this project's most-repeated
        failure shape. So: the reference year is exactly 1.0, and the record's high-switching
        years must produce strictly positive pressure.
        """
        from company.pricing.renewal_desk import _competitive_ceiling_gbp_per_mwh

        assert market_switching_multiplier(2024) == pytest.approx(1.0, abs=1e-9)
        pressured = [y for y in range(2016, 2026) if market_switching_multiplier(y) > 1.0]
        assert len(pressured) >= 4, (
            f"only {len(pressured)} years produce any undercut pressure at the desk; a signal "
            f"that is zero almost everywhere is a dead wire that never complains"
        )
        # And it must reach the ceiling, not merely exist: the record's peak year has to buy a
        # strictly lower ceiling than the reference year does.
        baseline = _competitive_ceiling_gbp_per_mwh(200.0, market_switching_multiplier(2024))
        peak = _competitive_ceiling_gbp_per_mwh(200.0, market_switching_multiplier(2020))
        assert peak < baseline, (
            f"the record's peak switching year buys no undercut at the desk "
            f"({peak} vs {baseline}) -- the observable crosses the wall and does nothing"
        )
