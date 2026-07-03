"""SIM-side market switching propensity: savings-elasticity churn model (Phase NS).

Encodes the empirical relationship between annual savings available from switching
and the market-level switching propensity multiplier.

Key empirical finding (Ofgem/DESNZ data; see docs/market_research/churn_price_elasticity.md):
- PRIMARY driver of switching: SAVINGS AVAILABLE from switching to a competitor.
- Absolute price level does NOT independently increase switching (2022 disconfirms it:
  bills hit 3,549 GBP/yr yet switching collapsed to 3-4% because competitor fixed deals
  were 1,000+ GBP more expensive than SVT -- the "nowhere cheaper to go" effect).
- Post-2023 fairer-pricing rule permanently removed new-customer-exclusive discounts;
  structural switching equilibrium reduced ~25-30% from pre-2021 levels.

Piecewise elasticity (calibrated from DESNZ switching series 2015-2025):
    savings < 0:         3%   (crisis floor: home movers / SoLR only)
    0 <= S < 100:        5% + 2% * (S / 100)
    100 <= S < 250:      7% + 6% * ((S - 100) / 150)
    250 <= S < 400:      13% + 5% * ((S - 250) / 150)
    S >= 400:            22% (saturation -- maximum engaged segment)

Market multiplier: normalised so that 2024 new-normal (150 GBP savings, post-ban) = 1.0.
Applied in simulation/customer_events.py before income_stress and satisfaction modifiers.
"""
from __future__ import annotations

# Annual savings (GBP/yr, dual-fuel) available to a typical household by switching to
# the best available competitor deal. Midpoints from DESNZ/Ofgem engagement survey series.
# Negative values (crisis period) indicate fixed alternatives were MORE expensive than SVT.
MARKET_SAVINGS_BY_YEAR: dict[int, float] = {
    2016: 300.0,   # Peak challenger era; cheapest fix ~18% below SVT
    2017: 200.0,   # Some consolidation; still competitive
    2018: 200.0,   # Pre-cap surge; median saving ~160-240 GBP
    2019: 175.0,   # Default Tariff Cap (Jan 2019) compressed new-customer offers
    2020: 125.0,   # COVID + fewer products; cap falls; peak switching volumes despite lower savings
    2021: 0.0,     # H2 collapse: suppliers withdrew fixed products; averaged over year
    2022: -200.0,  # Crisis: no competitive alternative below SVT; fixed deals 1,000+ GBP more expensive
    2023: 100.0,   # Recovery; acquisition tariff ban + fairer-pricing rule moderating savings
    2024: 150.0,   # New normal (calibration year)
    2025: 175.0,   # Gradual normalisation continues
}

# Post-2023 "fairer for existing customers" rule eliminates new-customer-exclusive discounts.
# Permanently reduces the savings differential vs. the pre-2022 era.
_POST_BAN_STRUCTURAL_FACTOR: dict[int, float] = {
    2023: 0.85,
    2024: 0.75,
    2025: 0.75,
}

# Calibration reference: 2024 new-normal
_CALIBRATION_SAVINGS = MARKET_SAVINGS_BY_YEAR[2024]   # 150 GBP
_CALIBRATION_POST_BAN = _POST_BAN_STRUCTURAL_FACTOR[2024]   # 0.75

_CRISIS_FLOOR_RATE = 0.03   # 3% -- structural minimum (home movers, SoLR regardless of savings)
_MAX_RATE = 0.22             # 22% -- saturation (maximum engaged segment)


def _savings_to_rate(savings_gbp: float) -> float:
    """Piecewise linear annual switching rate from savings available (GBP/yr dual-fuel).

    Calibrated from DESNZ electricity switching series 2015-2025 cross-referenced
    with Ofgem engagement surveys and savings-available estimates.
    """
    if savings_gbp < 0:
        return _CRISIS_FLOOR_RATE
    if savings_gbp < 100:
        return 0.05 + 0.02 * (savings_gbp / 100.0)
    if savings_gbp < 250:
        return 0.07 + 0.06 * ((savings_gbp - 100.0) / 150.0)
    if savings_gbp < 400:
        return 0.13 + 0.05 * ((savings_gbp - 250.0) / 150.0)
    return _MAX_RATE


def _calibration_rate() -> float:
    """Rate at the calibration year (2024) -- multiplier denominator."""
    return _savings_to_rate(_CALIBRATION_SAVINGS) * _CALIBRATION_POST_BAN


def market_switching_multiplier(renewal_year: int) -> float:
    """Return the market-conditions switching propensity multiplier for a given year.

    Normalised: 2024 new-normal = 1.0.
    Below 1.0 suppresses churn relative to model baseline; above 1.0 amplifies it.

    Typical values:
      2016 (peak competition):  ~2.2
      2020 (pre-crisis normal): ~1.0
      2021 (crisis emerging):   ~0.7
      2022 (crisis peak):       ~0.4
      2023 (recovery):          ~0.85
      2024 (new normal):        1.00
      2025 (continuing):        ~1.1

    Applied to SIM ground-truth churn probability BEFORE income_stress and satisfaction
    modifiers -- it sets the market opportunity ceiling, not the customer-level probability.
    """
    savings = MARKET_SAVINGS_BY_YEAR.get(renewal_year, 150.0)
    structural = _POST_BAN_STRUCTURAL_FACTOR.get(renewal_year, 1.0)
    adjusted_rate = _savings_to_rate(savings) * structural
    cal = _calibration_rate()
    return max(adjusted_rate / cal, _CRISIS_FLOOR_RATE / cal)
