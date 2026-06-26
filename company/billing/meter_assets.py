"""Meter asset management.

UK suppliers are responsible for providing and maintaining the metering equipment
at customer premises. Each meter has an asset ID, installation date, and a
periodic certification/replacement schedule (usually 10-20 years depending on type).

Meter types:
- SMETS1: first-generation smart meters (non-interoperable pre-2018)
- SMETS2: second-generation smart meters (interoperable, Ofgem mandate)
- TRAD: traditional non-smart credit meter
- PPM: pre-payment meter (coin/token/key)
- AMR: Advanced Meter Reading (commercial HH, often leased from meter operator)

This module tracks meter assets at the company level.
Asset data comes from the company's meter asset register, not simulation internals.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


_CERT_PERIOD_YEARS: dict[str, int] = {
    "TRAD": 10,    # traditional credit meter certification (BS 5685)
    "PPM": 10,
    "SMETS1": 15,  # longer life in smart meters
    "SMETS2": 15,
    "AMR": 7,      # commercial AMR shorter certification cycle
}


@dataclass
class MeterAsset:
    asset_id: str
    customer_id: str
    meter_type: str
    installed_date: str   # ISO date string
    manufacturer: str = ""
    serial_number: str = ""
    status: str = "operational"  # operational / faulty / replaced / removed

    @property
    def cert_due_date(self) -> str:
        years = _CERT_PERIOD_YEARS.get(self.meter_type, 10)
        d = date.fromisoformat(self.installed_date)
        from datetime import timedelta
        cert_date = d.replace(year=d.year + years)
        return cert_date.isoformat()

    @property
    def days_until_cert(self) -> int:
        due = date.fromisoformat(self.cert_due_date)
        today = date.today()
        return (due - today).days

    @property
    def cert_overdue(self) -> bool:
        return self.days_until_cert < 0

    @property
    def cert_due_soon(self) -> bool:
        return 0 <= self.days_until_cert <= 365


class MeterAssetRegister:
    """Company register of all meter assets."""

    def __init__(self):
        self._assets: dict[str, MeterAsset] = {}  # asset_id -> asset

    def register(self, asset: MeterAsset) -> MeterAsset:
        self._assets[asset.asset_id] = asset
        return asset

    def get(self, asset_id: str) -> MeterAsset | None:
        return self._assets.get(asset_id)

    def for_customer(self, customer_id: str) -> list[MeterAsset]:
        return [a for a in self._assets.values() if a.customer_id == customer_id]

    def operational(self) -> list[MeterAsset]:
        return [a for a in self._assets.values() if a.status == "operational"]

    def faulty(self) -> list[MeterAsset]:
        return [a for a in self._assets.values() if a.status == "faulty"]

    def cert_overdue(self) -> list[MeterAsset]:
        return [a for a in self.operational() if a.cert_overdue]

    def cert_due_soon(self) -> list[MeterAsset]:
        return [a for a in self.operational() if a.cert_due_soon and not a.cert_overdue]

    def by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for a in self._assets.values():
            counts[a.meter_type] = counts.get(a.meter_type, 0) + 1
        return counts

    def summary(self) -> dict:
        ops = self.operational()
        return {
            "total": len(self._assets),
            "operational": len(ops),
            "faulty": len(self.faulty()),
            "cert_overdue": len(self.cert_overdue()),
            "cert_due_soon": len(self.cert_due_soon()),
            "by_type": self.by_type(),
            "smart_pct": round(
                100 * sum(1 for a in ops if a.meter_type in ("SMETS1", "SMETS2")) / len(ops), 1
            ) if ops else 0.0,
        }
