"""MPAS supply point registry: MPAN/MPRN registration, gain/loss and objections."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class RegistrationStatus(str, Enum):
    REGISTERED = 'registered'
    IN_TRANSFER = 'in_transfer'
    OBJECTED = 'objected'
    WITHDRAWN = 'withdrawn'
    LOST = 'lost'


class Commodity(str, Enum):
    ELECTRICITY = 'electricity'
    GAS = 'gas'


_TRANSFER_BUSINESS_DAYS = 5


@dataclass
class SupplyPoint:
    supply_point_id: str
    commodity: Commodity
    customer_id: str
    registration_date: dt.date
    annual_consumption_kwh: float
    status: RegistrationStatus = RegistrationStatus.REGISTERED
    transfer_effective_date: Optional[dt.date] = None
    objection_raised: bool = False
    objection_reason: Optional[str] = None
    losing_supplier: Optional[str] = None

    @property
    def is_active(self) -> bool:
        return self.status == RegistrationStatus.REGISTERED

    @property
    def annual_mwh(self) -> float:
        return round(self.annual_consumption_kwh / 1000, 2)

    def raise_objection(self, reason: str) -> None:
        self.objection_raised = True
        self.objection_reason = reason
        self.status = RegistrationStatus.OBJECTED

    def resolve_objection(self, allow_transfer: bool) -> None:
        if allow_transfer:
            self.status = RegistrationStatus.IN_TRANSFER
            self.objection_raised = False
        else:
            self.status = RegistrationStatus.WITHDRAWN

    def complete_transfer(self, transfer_date: dt.date) -> None:
        self.status = RegistrationStatus.LOST
        self.transfer_effective_date = transfer_date


class MPASRegistry:
    def __init__(self) -> None:
        self._supply_points: Dict[str, SupplyPoint] = {}

    def register(self, supply_point_id: str, commodity: Commodity,
                   customer_id: str, registration_date: dt.date,
                   annual_kwh: float,
                   losing_supplier: Optional[str] = None) -> SupplyPoint:
        sp = SupplyPoint(
            supply_point_id=supply_point_id, commodity=commodity,
            customer_id=customer_id, registration_date=registration_date,
            annual_consumption_kwh=annual_kwh,
            losing_supplier=losing_supplier,
        )
        self._supply_points[supply_point_id] = sp
        return sp

    def get(self, supply_point_id: str) -> Optional[SupplyPoint]:
        return self._supply_points.get(supply_point_id)

    def active_supply_points(self, commodity: Optional[Commodity] = None) -> List[SupplyPoint]:
        return [
            sp for sp in self._supply_points.values()
            if sp.is_active and (commodity is None or sp.commodity == commodity)
        ]

    def total_registered_mwh(self, commodity: Optional[Commodity] = None) -> float:
        return round(sum(
            sp.annual_mwh for sp in self.active_supply_points(commodity)
        ), 2)

    def objected_points(self) -> List[SupplyPoint]:
        return [sp for sp in self._supply_points.values()
                 if sp.status == RegistrationStatus.OBJECTED]

    def registrations_in_period(self, from_date: dt.date,
                                   to_date: dt.date) -> List[SupplyPoint]:
        return [
            sp for sp in self._supply_points.values()
            if from_date <= sp.registration_date <= to_date
        ]

    def mpas_summary(self) -> dict:
        active = self.active_supply_points()
        elec = self.active_supply_points(Commodity.ELECTRICITY)
        gas = self.active_supply_points(Commodity.GAS)
        return {
            'total_registered': len(active),
            'electricity_points': len(elec),
            'gas_points': len(gas),
            'total_electricity_mwh': self.total_registered_mwh(Commodity.ELECTRICITY),
            'total_gas_mwh': self.total_registered_mwh(Commodity.GAS),
            'objected': len(self.objected_points()),
        }
