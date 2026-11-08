from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from company.crm.property_model import Property, EPCRating
from company.crm.household_profile import HouseholdBehaviourProfile, HouseholdType


@dataclass(frozen=True)
class CustomerEnergyProfile:
    customer_id: str
    as_of_date: date
    property: Property
    behaviour: HouseholdBehaviourProfile

    @property
    def estimated_annual_elec_kwh(self) -> float:
        return self.property.estimated_annual_elec_kwh

    @property
    def estimated_annual_gas_kwh(self) -> float:
        return self.property.estimated_annual_gas_kwh

    @property
    def is_fuel_poor(self) -> bool:
        return self.property.is_fuel_poor

    @property
    def eco4_eligible(self) -> bool:
        return self.property.eco4_eligible

    @property
    def tou_candidate(self) -> bool:
        return self.behaviour.tou_price_sensitivity in ('high', 'medium')

    @property
    def heat_pump_candidate(self) -> bool:
        return (
            self.behaviour.heat_pump_eligible
            and self.property.epc_rating.value in ('A', 'B', 'C', 'D')
        )

    @property
    def decarbonisation_priority_score(self) -> float:
        epc_score = {'A': 0.0, 'B': 0.2, 'C': 0.4, 'D': 0.6, 'E': 0.8, 'F': 1.0, 'G': 1.0}
        epc = epc_score.get(self.property.epc_rating.value, 0.5)
        hp_bonus = 0.2 if self.heat_pump_candidate else 0.0
        solar_bonus = 0.1 if not self.property.has_solar_pv else 0.0
        return round(min(1.0, epc + hp_bonus + solar_bonus), 2)

    def summary(self) -> dict:
        result = dict(
            customer_id=self.customer_id,
            as_of_date=str(self.as_of_date),
            uprn=self.property.uprn,
            epc_rating=self.property.epc_rating.value,
            tenure=self.property.tenure.value,
            household_type=self.behaviour.household_type.value,
            occupants=self.property.occupants,
            estimated_annual_elec_kwh=self.estimated_annual_elec_kwh,
            estimated_annual_gas_kwh=self.estimated_annual_gas_kwh,
            is_fuel_poor=self.is_fuel_poor,
            eco4_eligible=self.eco4_eligible,
            tou_candidate=self.tou_candidate,
            heat_pump_candidate=self.heat_pump_candidate,
            decarbonisation_priority_score=self.decarbonisation_priority_score,
        )
        return result
