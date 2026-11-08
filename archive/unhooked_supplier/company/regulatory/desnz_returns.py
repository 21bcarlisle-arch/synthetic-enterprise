"""DESNZ supplier data returns and exception reporting.

UK energy suppliers submit mandatory data returns to the Department for
Energy Security and Net Zero (DESNZ, formerly BEIS):

1. Supplier Data Return (SDR): monthly submission of customer numbers
   by fuel type, meter type, and tariff type. Used for market monitoring.

2. Fuel Poverty Declaration: annual estimate of customers in fuel poverty.
   Fuel poverty threshold: household spends >10% of income on energy
   (England Low Income Low Energy Efficiency / LILEE definition from 2023).

3. Carbon Intensity Data: annual CO₂ per kWh for electricity supplied
   (required for Fuel Mix Disclosure under Electricity (Fuel Mix Disclosure)
   Regulations 2005).

Data returns are prepared from company-observable data — meter counts,
billing data, and the published fuel mix (Phase 111). They are
cross-validated before submission to avoid regulatory penalties.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


_FUEL_POVERTY_INCOME_THRESHOLD = 0.10   # >10% of income on energy = fuel poor
_FUEL_POVERTY_TYPICAL_INCOME_GBP = 25_000  # ONS median household income
_FUEL_POVERTY_ANNUAL_BILL_THRESHOLD = _FUEL_POVERTY_INCOME_THRESHOLD * _FUEL_POVERTY_TYPICAL_INCOME_GBP


@dataclass
class SupplierDataReturn:
    """Monthly Supplier Data Return (SDR) to DESNZ."""
    reference_month: str           # YYYY-MM
    electricity_customers: int
    gas_customers: int
    dual_fuel_customers: int
    smart_meter_customers: int
    prepayment_meter_customers: int
    fixed_tariff_customers: int
    variable_tariff_customers: int
    submitted: bool = False
    submission_date: str = ""

    @property
    def total_customers(self) -> int:
        return self.electricity_customers + self.gas_customers - self.dual_fuel_customers

    @property
    def smart_meter_pct(self) -> float:
        total = self.total_customers
        return round(100.0 * self.smart_meter_customers / total, 1) if total > 0 else 0.0


@dataclass
class FuelPovertyDeclaration:
    """Annual fuel poverty data declaration."""
    declaration_year: int
    total_customers: int
    fuel_poor_customers: int       # estimated customers meeting fuel poverty definition
    methodology: str = "LILEE"    # Low Income Low Energy Efficiency (England 2023+)
    submitted: bool = False

    @property
    def fuel_poverty_rate_pct(self) -> float:
        return round(100.0 * self.fuel_poor_customers / self.total_customers, 1) if self.total_customers > 0 else 0.0

    @property
    def estimated_from_annual_bill(cls) -> float:
        return _FUEL_POVERTY_ANNUAL_BILL_THRESHOLD


def estimate_fuel_poor_customers(total_customers: int, annual_bill_gbp: float) -> int:
    """Estimate customers in fuel poverty based on typical annual bill."""
    if annual_bill_gbp <= _FUEL_POVERTY_ANNUAL_BILL_THRESHOLD:
        return 0
    # Linear scaling: higher bills → more customers above threshold
    # Simplified: 15% baseline + proportional increase for high bills
    base_rate = 0.15
    bill_uplift = min(0.20, (annual_bill_gbp - _FUEL_POVERTY_ANNUAL_BILL_THRESHOLD) / 5000.0 * 0.10)
    return round(total_customers * (base_rate + bill_uplift))


@dataclass
class CarbonIntensityReturn:
    """Annual carbon intensity data for Fuel Mix Disclosure."""
    declaration_year: int
    total_kwh_supplied: float
    renewable_kwh: float
    nuclear_kwh: float
    gas_kwh: float
    coal_kwh: float
    other_kwh: float
    # g CO₂/kWh factors (IPCC lifecycle estimates)
    _CO2_FACTORS = {"renewable": 15, "nuclear": 12, "gas": 490, "coal": 820, "other": 300}

    @property
    def co2_intensity_g_per_kwh(self) -> float:
        if self.total_kwh_supplied == 0:
            return 0.0
        total_co2 = (
            self.renewable_kwh * self._CO2_FACTORS["renewable"]
            + self.nuclear_kwh * self._CO2_FACTORS["nuclear"]
            + self.gas_kwh * self._CO2_FACTORS["gas"]
            + self.coal_kwh * self._CO2_FACTORS["coal"]
            + self.other_kwh * self._CO2_FACTORS["other"]
        )
        return round(total_co2 / self.total_kwh_supplied, 1)

    @property
    def renewable_pct(self) -> float:
        if self.total_kwh_supplied == 0:
            return 0.0
        return round(100.0 * self.renewable_kwh / self.total_kwh_supplied, 1)
