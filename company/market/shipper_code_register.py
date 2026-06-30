"""Xoserve Shipper Code Register.

UK gas suppliers must be registered as shippers in the Xoserve UK Link
system. Xoserve maintains the Shippers Database, which holds:
- Shipper codes (2-character identifier)
- LDZ (Local Distribution Zone) authorisations
- Transportation agreements with relevant transporters

Shipper registration is a prerequisite for:
- Gas nomination (UNC Transportation Principal Document)
- Access to the gas network (UNC Uniform Network Code)
- UNC Balancing Mechanism participation

A shipper must hold authorisation for each LDZ in which they supply.
There are 13 LDZs in GB, managed by the Distribution Network Operators.

Xoserve UK Link also manages Meter Point Reference Numbers (MPRNs) —
the gas equivalent of MPANs.

This register models the company's shipper status and LDZ coverage.
Epistemic: shipper registration is a public fact the company knows.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class LDZ(str, Enum):
    EA = "EA"   # East of England
    EM = "EM"   # East Midlands
    NE = "NE"   # North East
    NO = "NO"   # Northern
    NT = "NT"   # North Thames
    NW = "NW"   # North West
    SC = "SC"   # Scotland
    SE = "SE"   # South East
    SO = "SO"   # Southern
    SW = "SW"   # South West
    WM = "WM"   # West Midlands
    WN = "WN"   # Wales North
    WS = "WS"   # Wales South


class ShipperStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass(frozen=True)
class LDZAuthorisation:
    ldz: LDZ
    effective_date: date
    is_active: bool = True


@dataclass
class ShipperRecord:
    shipper_code: str           # 2-char Xoserve code
    company_name: str
    registration_date: date
    status: ShipperStatus = ShipperStatus.ACTIVE
    _ldz_authorisations: list[LDZAuthorisation] = field(default_factory=list)

    @property
    def active_ldz_codes(self) -> list[LDZ]:
        return [a.ldz for a in self._ldz_authorisations if a.is_active]

    @property
    def ldz_coverage_count(self) -> int:
        return len(self.active_ldz_codes)

    @property
    def is_national(self) -> bool:
        return self.ldz_coverage_count == len(LDZ)

    def add_ldz(self, ldz: LDZ, effective_date: date) -> None:
        if ldz not in self.active_ldz_codes:
            self._ldz_authorisations.append(LDZAuthorisation(ldz=ldz, effective_date=effective_date))

    def revoke_ldz(self, ldz: LDZ) -> None:
        self._ldz_authorisations = [
            LDZAuthorisation(ldz=a.ldz, effective_date=a.effective_date, is_active=False) if a.ldz == ldz else a
            for a in self._ldz_authorisations
        ]

    def can_supply_in(self, ldz: LDZ) -> bool:
        return self.status == ShipperStatus.ACTIVE and ldz in self.active_ldz_codes


class ShipperCodeRegister:
    """Xoserve Shipper Database — company's gas shipper registration."""

    def __init__(self) -> None:
        self._shippers: dict[str, ShipperRecord] = {}

    def register(self, shipper_code: str, company_name: str, registration_date: date) -> ShipperRecord:
        record = ShipperRecord(
            shipper_code=shipper_code,
            company_name=company_name,
            registration_date=registration_date,
        )
        self._shippers[shipper_code] = record
        return record

    def get(self, shipper_code: str) -> ShipperRecord | None:
        return self._shippers.get(shipper_code)

    def suspend(self, shipper_code: str) -> None:
        if shipper_code in self._shippers:
            r = self._shippers[shipper_code]
            self._shippers[shipper_code] = ShipperRecord(
                shipper_code=r.shipper_code,
                company_name=r.company_name,
                registration_date=r.registration_date,
                status=ShipperStatus.SUSPENDED,
                _ldz_authorisations=r._ldz_authorisations,
            )

    @property
    def active_shippers(self) -> list[ShipperRecord]:
        return [r for r in self._shippers.values() if r.status == ShipperStatus.ACTIVE]

    @property
    def suspended_shippers(self) -> list[ShipperRecord]:
        return [r for r in self._shippers.values() if r.status == ShipperStatus.SUSPENDED]

    def shipper_summary(self) -> str:
        n = len(self._shippers)
        n_active = len(self.active_shippers)
        n_susp = len(self.suspended_shippers)
        lines = [
            "Shipper Code Register (Xoserve UK Link)",
            "Registered: {:d} | Active: {:d} | Suspended: {:d}".format(n, n_active, n_susp),
        ]
        for r in self.active_shippers:
            lines.append("  [{}] {} — {:d}/{:d} LDZs{}".format(
                r.shipper_code, r.company_name, r.ldz_coverage_count, len(LDZ),
                " (national)" if r.is_national else ""
            ))
        return "\n".join(lines)
