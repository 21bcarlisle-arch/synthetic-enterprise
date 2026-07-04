"""CorrelatedGeneratorAdapter -- bivariate Ornstein-Uhlenbeck electricity + gas price generator.

Regime-switching model: 8% monthly probability of high-volatility (crisis) regime,
calibrated to the 2021-22 UK energy crisis. Satisfies MarketDataPort with zero
company-layer changes (Phase PV guarantee maintained).

All constants calibrated from 2016-2025 NBP + Elexon SSP published data.
"""
from __future__ import annotations
import datetime
import math
import random as _random
from typing import Optional

GAS_LONG_RUN_MEAN_GBP_PER_MWH = 54.0
ELEC_LONG_RUN_MEAN_GBP_PER_MWH = 85.0
GAS_MEAN_REVERSION_SPEED = 0.5
ELEC_MEAN_REVERSION_SPEED = 0.6
GAS_VOL_NORMAL = 0.35
GAS_VOL_CRISIS = 1.20
ELEC_VOL_NORMAL = 0.45
ELEC_VOL_CRISIS = 1.50
ELEC_GAS_CORR = 0.70
CRISIS_REGIME_PROB = 0.08
FORWARD_CONTANGO_ANNUAL = 0.02

_GAS_FLOOR = 2.0
_ELEC_FLOOR = 5.0
_GAS_CEILING = 300.0
_ELEC_CEILING = 1000.0
_DT = 1.0 / 12.0


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


class CorrelatedGeneratorAdapter:
    """Bivariate OU price generator implementing MarketDataPort.

    Calling get_market_summary() advances the process one monthly step.
    get_spot_elec/gas() return the current state without advancing.
    """

    def __init__(self, seed=None, regime="normal"):
        self._rng = _random.Random(seed)
        self._forced_crisis = (regime == "crisis")
        self._is_crisis = self._forced_crisis
        self._gas = GAS_LONG_RUN_MEAN_GBP_PER_MWH
        self._elec = ELEC_LONG_RUN_MEAN_GBP_PER_MWH

    def _draw_correlated(self):
        """Draw (z_gas, z_elec) ~ bivariate N(0,I) with correlation ELEC_GAS_CORR."""
        u1 = max(self._rng.random(), 1e-12)
        u2 = self._rng.random()
        z1 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        z2 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
        rho = ELEC_GAS_CORR
        z_gas = z1
        z_elec = rho * z1 + math.sqrt(1.0 - rho ** 2) * z2
        return z_gas, z_elec

    def _advance(self):
        """Advance one monthly OU step, optionally switching regime."""
        if not self._forced_crisis:
            self._is_crisis = self._rng.random() < CRISIS_REGIME_PROB
        gas_vol = GAS_VOL_CRISIS if self._is_crisis else GAS_VOL_NORMAL
        elec_vol = ELEC_VOL_CRISIS if self._is_crisis else ELEC_VOL_NORMAL
        z_gas, z_elec = self._draw_correlated()
        sqrt_dt = math.sqrt(_DT)
        self._gas = _clamp(
            self._gas
            + GAS_MEAN_REVERSION_SPEED * (GAS_LONG_RUN_MEAN_GBP_PER_MWH - self._gas) * _DT
            + gas_vol * sqrt_dt * z_gas,
            _GAS_FLOOR, _GAS_CEILING,
        )
        self._elec = _clamp(
            self._elec
            + ELEC_MEAN_REVERSION_SPEED * (ELEC_LONG_RUN_MEAN_GBP_PER_MWH - self._elec) * _DT
            + elec_vol * sqrt_dt * z_elec,
            _ELEC_FLOOR, _ELEC_CEILING,
        )

    def get_spot_elec_gbp_per_mwh(self, as_of=None):
        return round(self._elec, 2)

    def get_spot_gas_gbp_per_mwh(self, as_of=None):
        return round(self._gas, 2)

    def get_forward_price(self, as_of=None, delivery_date=None, commodity="electricity"):
        if delivery_date is not None and as_of is not None:
            T = max(0.0, (delivery_date - as_of).days / 365.0)
        else:
            T = 1.0
        spot = self._elec if commodity == "electricity" else self._gas
        return round(spot * (1.0 + FORWARD_CONTANGO_ANNUAL * T), 2)

    def get_market_summary(self, as_of=None):
        self._advance()
        return {
            "as_of_date": str(as_of) if as_of else None,
            "elec_spot_gbp_per_mwh": round(self._elec, 2),
            "gas_spot_gbp_per_mwh": round(self._gas, 2),
            "elec_12m_forward_gbp_per_mwh": round(self._elec * (1.0 + FORWARD_CONTANGO_ANNUAL), 2),
            "gas_12m_forward_gbp_per_mwh": round(self._gas * (1.0 + FORWARD_CONTANGO_ANNUAL), 2),
        }
