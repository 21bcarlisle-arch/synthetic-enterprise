"""EV Charging Demand Forecaster (Phase FS).

As EV penetration grows in the portfolio, the company needs to forecast:
1. Additional electricity demand (MWh) attributable to EV charging
2. Shape of that demand (overnight = smart charging; peak = unmanaged)
3. Impact on procurement: more baseload/overnight volume needed
4. ToU product opportunity: convert peak EV load to overnight (Phase T/X/Y)

From the company's observable perspective:
- Smart meter data shows higher overnight consumption for EV households
- EV registration data is public (DVLA) at regional level
- EPC/meter point data shows homes with smart charge points (new build regs)
- Company's own customer surveys / registration data

Calibration (public data):
- Average UK EV: 3,500-4,000 kWh/yr home charging
- Smart charging (12:00-07:00): ~85% of EV energy (UK Smart Charge Regs 2021)
- Unmanaged charging (any time): flat profile
- Regional penetration varies: EV-heavy in South/London vs North England

This module models portfolio-level EV demand based on what the company
can observe (customer-declared EV ownership, smart meter patterns).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ChargingPattern(str, Enum):
    SMART = "smart"           # overnight off-peak (Smart Charge Regs 2021)
    UNMANAGED = "unmanaged"   # any time, mostly after work (peak risk)
    MIXED = "mixed"           # some smart, some unmanaged


_SMART_KWH_PER_EV_PER_YEAR = 3_700.0      # UK average home charging
_UNMANAGED_KWH_PER_EV_PER_YEAR = 3_700.0  # same energy, different shape
_SMART_FRACTION_OF_SMART = 0.85            # 85% overnight (Regs 2021)
_PEAK_PERIODS_PER_DAY = 24                 # SP25-36 = 12:00-18:00 = 6hr = 12 HH


@dataclass(frozen=True)
class EVDemandForecast:
    forecast_year: int
    ev_count: int
    charging_pattern: ChargingPattern
    is_smart_charged: bool

    @property
    def annual_ev_kwh(self) -> float:
        base = _SMART_KWH_PER_EV_PER_YEAR if self.is_smart_charged else _UNMANAGED_KWH_PER_EV_PER_YEAR
        return self.ev_count * base

    @property
    def overnight_kwh(self) -> float:
        if self.charging_pattern == ChargingPattern.SMART:
            return self.annual_ev_kwh * _SMART_FRACTION_OF_SMART
        if self.charging_pattern == ChargingPattern.UNMANAGED:
            return self.annual_ev_kwh / 2   # rough day/night split
        return self.annual_ev_kwh * 0.65    # mixed

    @property
    def peak_risk_kwh(self) -> float:
        return self.annual_ev_kwh - self.overnight_kwh

    @property
    def triad_risk_mw(self) -> float:
        if self.charging_pattern == ChargingPattern.SMART:
            return 0.0
        peak_daily_kwh = self.peak_risk_kwh / 365
        return peak_daily_kwh / _PEAK_PERIODS_PER_DAY / 0.5  # MWh per 30min -> MW

    def forecast_summary(self) -> str:
        return (
            "EVForecast " + str(self.forecast_year) + ": "
            + str(self.ev_count) + " EVs "
            "[" + self.charging_pattern.value + "] "
            "annual=" + str(round(self.annual_ev_kwh / 1000, 1)) + "GWh "
            "overnight=" + str(round(self.overnight_kwh / 1000, 1)) + "GWh"
        )


class EVDemandForecaster:

    def __init__(self) -> None:
        self._forecasts: List[EVDemandForecast] = []

    def add_forecast(self, forecast: EVDemandForecast) -> EVDemandForecast:
        self._forecasts.append(forecast)
        return forecast

    def forecast_for_year(self, year: int) -> Optional[EVDemandForecast]:
        matching = [f for f in self._forecasts if f.forecast_year == year]
        return matching[0] if matching else None

    def total_annual_ev_kwh(self, year: Optional[int] = None) -> float:
        forecasts = self._forecasts
        if year is not None:
            f = self.forecast_for_year(year)
            return f.annual_ev_kwh if f else 0.0
        return sum(f.annual_ev_kwh for f in forecasts)

    def total_triad_risk_mw(self, year: Optional[int] = None) -> float:
        if year is not None:
            f = self.forecast_for_year(year)
            return f.triad_risk_mw if f else 0.0
        return sum(f.triad_risk_mw for f in self._forecasts)

    def smart_charging_adoption_pct(self) -> float:
        if not self._forecasts:
            return 0.0
        smart = sum(f.ev_count for f in self._forecasts
                    if f.charging_pattern == ChargingPattern.SMART)
        total = sum(f.ev_count for f in self._forecasts)
        return 100.0 * smart / total if total else 0.0

    def ev_demand_summary(self) -> str:
        n_years = len(self._forecasts)
        total_kwh = self.total_annual_ev_kwh()
        triad_risk = self.total_triad_risk_mw()
        smart_pct = self.smart_charging_adoption_pct()
        return (
            "EV Demand Forecaster: " + str(n_years) + " forecasts. "
            "Total annual EV demand: " + str(round(total_kwh / 1000, 1)) + "GWh. "
            "Triad risk: " + str(round(triad_risk, 1)) + "MW. "
            "Smart charging: " + str(round(smart_pct, 1)) + "%."
        )
