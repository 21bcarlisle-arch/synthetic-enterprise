"""Phase C -- Household-Driven EAC Integration.

Wires the Phase A household physical model and Phase B life events engine
into the settlement loop so that EPC rating, EV ownership, and solar
installations actually affect per-customer consumption.

Each customer consumption shape is scaled by a composite multiplier:

  epc_multiplier * (1 + ev_fraction) * max(0, 1 - solar_fraction)

Where:
  epc_multiplier  = epc_consumption_multiplier() from Household (EPC-D=1.25, EPC-E=1.55)
  ev_fraction     = ev_annual_kwh / base_eac  (additive load from EV charging)
  solar_fraction  = solar_annual_generation_kwh / base_eac  (net import reduction)
  base_eac        = segment-average EAC (denominator for fractions)

The multiplier is date-aware: life events change the household state over
the simulation period, so a solar install in 2021 reduces consumption from
that date onwards; an EV acquisition in 2019 increases it from that date.

Epistemic constraint: SIM ground truth. Company layer cannot read these
multipliers directly -- it observes consequences via billing records.
"""

from __future__ import annotations

import hashlib
from simulation.household import Household, build_household_register
from simulation.life_events import generate_life_events
from simulation.life_events import household_at_date as _household_at_date

SIM_START_YEAR = 2016
SIM_END_YEAR = 2025

# Phase D: residual gas fraction after heat pump installation.
# With ASHP + heat pump hot water cylinder, gas boiler is decommissioned.
# Residual: cooking only (~1,500 kWh/yr for typical UK home).
# 0.12 * declared AQ gives 1,440 kWh for a 12,000 kWh home.
GAS_HEAT_PUMP_RESIDUAL_FRACTION = 0.12

RESI_BASE_EAC_KWH = 3_100.0
SME_BASE_EAC_KWH = 25_000.0
IC_BASE_EAC_KWH = 100_000.0

_SEGMENT_BASE_EAC: dict[str, float] = {
    "resi": RESI_BASE_EAC_KWH,
    "SME": SME_BASE_EAC_KWH,
    "I&C": IC_BASE_EAC_KWH,
}


def _base_eac_for_customer(customer: dict) -> float:
    declared = customer.get("eac_kwh")
    if declared and declared > 0:
        return float(declared)
    return _SEGMENT_BASE_EAC.get(customer.get("segment", "resi"), RESI_BASE_EAC_KWH)


def _cid_hash(cid: str) -> int:
    # Deterministic customer_id hash — independent of PYTHONHASHSEED
    return int(hashlib.md5(cid.encode()).hexdigest()[:8], 16)


class HouseholdDemandRegister:
    """Manages time-varying household physical state for all simulation customers."""

    def __init__(self, customers: list[dict], seed: int = 42) -> None:
        self._base_eac: dict[str, float] = {
            c["customer_id"]: _base_eac_for_customer(c) for c in customers
        }
        self._households: dict[str, Household] = build_household_register(customers)
        self._events: dict[str, list] = {}
        for cid, hh in self._households.items():
            cid_seed = seed ^ (_cid_hash(cid) & 0xFFFF)
            self._events[cid] = generate_life_events(
                hh, SIM_START_YEAR, SIM_END_YEAR, seed=cid_seed
            )

    def household_at_date(self, customer_id: str, date_str: str):
        hh = self._households.get(customer_id)
        if hh is None:
            return None
        return _household_at_date(hh, self._events.get(customer_id, []), date_str)

    def epc_multiplier(self, customer_id: str, date_str: str) -> float:
        hh = self.household_at_date(customer_id, date_str)
        if hh is None:
            return 1.0
        return hh.epc_consumption_multiplier()

    def income_stress_at_date(self, customer_id: str, date_str: str):
        """Return the customer's IncomeStress level at a given date."""
        hh = self.household_at_date(customer_id, date_str)
        if hh is None:
            return None
        return hh.income_stress

    def eac_multiplier_for_date(self, customer_id: str, date_str: str) -> float:
        """Composite EAC multiplier: EPC * (1 + EV fraction + ASHP fraction) * (1 - solar fraction).

        Phase F: ASHP fraction adds ~5,500 kWh/yr electricity uplift when heat pump installed.
        This is symmetric with Phase D gas reduction (GAS_HEAT_PUMP_RESIDUAL_FRACTION = 0.12).
        """
        hh = self.household_at_date(customer_id, date_str)
        if hh is None:
            return 1.0
        base_eac = self._base_eac.get(customer_id, RESI_BASE_EAC_KWH)
        epc = hh.epc_consumption_multiplier()
        ev_kwh = hh.ev_annual_kwh()
        ashp_kwh = hh.ashp_annual_kwh()
        solar_kwh = hh.solar_annual_generation_kwh()
        ev_fraction = ev_kwh / base_eac if base_eac > 0 else 0.0
        ashp_fraction = ashp_kwh / base_eac if base_eac > 0 else 0.0
        solar_fraction = solar_kwh / base_eac if base_eac > 0 else 0.0
        return epc * (1.0 + ev_fraction + ashp_fraction) * max(0.0, 1.0 - solar_fraction)

    def dynamic_assets(self, customer_id: str, date_str: str) -> dict:
        """Time-varying asset dict (ev/solar/smart_meter) for the demand model."""
        hh = self.household_at_date(customer_id, date_str)
        if hh is None:
            return {}
        return {
            "ev": hh.has_ev,
            "solar": hh.has_solar,
            "smart_meter": hh.has_smart_meter,
            "battery": hh.has_battery,
            "battery_kwh": hh.battery_kwh,
        }

    def gas_eac_multiplier_for_date(self, customer_id: str, date_str: str) -> float:
        """Phase D: EPC-based multiplier for gas annual quantity."""
        hh = self.household_at_date(customer_id, date_str)
        if hh is None:
            return 1.0
        if not hh.is_residential:
            return 1.0
        if hh.is_heat_pump:
            return GAS_HEAT_PUMP_RESIDUAL_FRACTION
        if not hh.is_gas_heated:
            return 1.0
        return hh.epc_consumption_multiplier()

    def event_count(self, customer_id: str) -> int:
        return len(self._events.get(customer_id, []))

    def all_customer_ids(self) -> list[str]:
        return list(self._households.keys())
