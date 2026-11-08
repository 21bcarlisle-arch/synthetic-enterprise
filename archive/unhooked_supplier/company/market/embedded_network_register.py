"""Embedded Network Supply Register (Phase DO).

An embedded network is a private electricity network behind a single grid
connection (parent meter). Common in blocks of flats, business parks,
commercial buildings. The network operator (usually the developer/landlord)
is an Embedded Network Operator (ENO).

From 2024, Ofgem has strengthened protections:
- Residents have the right to switch to any public supplier (not just ENO's
  appointed supplier)
- MPAN allocation: each unit gets its own MPAN (sub-metered)
- ENO must allow access for meter reading / data retrieval

Key Ofgem references:
- The Electricity (Class Exemptions from Requirement for Licence) Order 2001
- Ofgem embedded network consultation (2021-2024)
- Smart Meter Exemption Regulations

Epistemic: the company sees embedded networks as ordinary supply points but
must track them for compliance (rate limits, switching rights).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class EmbeddedNetworkType(str, Enum):
    RESIDENTIAL_BLOCK = "residential_block"   # flats / apartments
    COMMERCIAL_PARK = "commercial_park"       # business park
    MIXED_USE = "mixed_use"
    STUDENT_ACCOMMODATION = "student_accommodation"
    MARINA = "marina"                         # marina berths
    CARAVAN_PARK = "caravan_park"


class ENOStatus(str, Enum):
    ACTIVE = "active"
    TERMINATED = "terminated"
    DISPUTED = "disputed"         # switching rights dispute
    EXEMPT = "exempt"             # licence exemption applies


_MAX_EMBEDDED_RATE_PCT_ABOVE_DNO = 20.0   # Ofgem: EN rates cannot exceed DNO+20%
_MIN_SWITCHING_NOTICE_DAYS = 28            # 28-day exit from EN supply


@dataclass(frozen=True)
class EmbeddedNetworkRecord:
    network_id: str
    network_type: EmbeddedNetworkType
    eno_name: str                            # operator name
    parent_mpan: str                         # the single grid connection MPAN
    unit_count: int
    registered_at: dt.date
    status: ENOStatus
    rate_pence_per_kwh: float               # ENO-charged rate
    dno_rate_pence_per_kwh: float           # reference DNO/public supplier rate
    end_date: Optional[dt.date] = None

    @property
    def is_active(self) -> bool:
        return self.status == ENOStatus.ACTIVE

    @property
    def rate_premium_pct(self) -> float:
        if self.dno_rate_pence_per_kwh <= 0:
            return 0.0
        return (self.rate_pence_per_kwh - self.dno_rate_pence_per_kwh) / self.dno_rate_pence_per_kwh * 100

    @property
    def is_rate_compliant(self) -> bool:
        return self.rate_premium_pct <= _MAX_EMBEDDED_RATE_PCT_ABOVE_DNO

    @property
    def rate_excess_pct(self) -> float:
        return max(0.0, self.rate_premium_pct - _MAX_EMBEDDED_RATE_PCT_ABOVE_DNO)


class EmbeddedNetworkRegister:
    """Tracks embedded networks and monitors ENO rate compliance."""

    def __init__(self) -> None:
        self._records: Dict[str, EmbeddedNetworkRecord] = {}

    def register(
        self,
        network_type: EmbeddedNetworkType,
        eno_name: str,
        parent_mpan: str,
        unit_count: int,
        registered_at: dt.date,
        rate_pence_per_kwh: float,
        dno_rate_pence_per_kwh: float,
        status: ENOStatus = ENOStatus.ACTIVE,
        end_date: Optional[dt.date] = None,
    ) -> EmbeddedNetworkRecord:
        seq = len(self._records) + 1
        network_id = f"EN-{seq:04d}"
        rec = EmbeddedNetworkRecord(
            network_id=network_id,
            network_type=network_type,
            eno_name=eno_name,
            parent_mpan=parent_mpan,
            unit_count=unit_count,
            registered_at=registered_at,
            status=status,
            rate_pence_per_kwh=rate_pence_per_kwh,
            dno_rate_pence_per_kwh=dno_rate_pence_per_kwh,
            end_date=end_date,
        )
        self._records[network_id] = rec
        return rec

    def terminate(self, network_id: str, end_date: dt.date) -> EmbeddedNetworkRecord:
        rec = self._records[network_id]
        updated = EmbeddedNetworkRecord(
            network_id=rec.network_id,
            network_type=rec.network_type,
            eno_name=rec.eno_name,
            parent_mpan=rec.parent_mpan,
            unit_count=rec.unit_count,
            registered_at=rec.registered_at,
            status=ENOStatus.TERMINATED,
            rate_pence_per_kwh=rec.rate_pence_per_kwh,
            dno_rate_pence_per_kwh=rec.dno_rate_pence_per_kwh,
            end_date=end_date,
        )
        self._records[network_id] = updated
        return updated

    def active_networks(self) -> List[EmbeddedNetworkRecord]:
        return [r for r in self._records.values() if r.is_active]

    def non_compliant_rates(self) -> List[EmbeddedNetworkRecord]:
        return [r for r in self.active_networks() if not r.is_rate_compliant]

    def total_units(self) -> int:
        return sum(r.unit_count for r in self.active_networks())

    def by_type(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self.active_networks():
            out[r.network_type.value] = out.get(r.network_type.value, 0) + r.unit_count
        return out

    def terminated_networks(self) -> List[EmbeddedNetworkRecord]:
        return [r for r in self._records.values() if r.status == ENOStatus.TERMINATED]

    def get(self, network_id: str) -> Optional[EmbeddedNetworkRecord]:
        return self._records.get(network_id)

    def embedded_network_summary(self) -> str:
        n_active = len(self.active_networks())
        n_units = self.total_units()
        n_non_compliant = len(self.non_compliant_rates())
        return (
            f"Embedded Network Register: {n_active} active EN(s), {n_units} units. "
            f"Non-compliant rates (>{_MAX_EMBEDDED_RATE_PCT_ABOVE_DNO}% DNO+): "
            f"{n_non_compliant}. Min switch notice: {_MIN_SWITCHING_NOTICE_DAYS}d (Ofgem 2024)."
        )
