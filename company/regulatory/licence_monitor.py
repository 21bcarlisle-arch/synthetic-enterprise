"""Standard Licence Condition (SLC) monitoring.

UK electricity and gas suppliers must comply with Standard Licence Conditions
issued by Ofgem. Key SLCs relevant to domestic/SME suppliers:

SLC 7: Billing and metering
SLC 14: Complaints handling (8-week resolution / Ombudsman access)
SLC 21C: Domestic Price Cap (amended 2017 onwards)
SLC 27: Smart meter rollout targets
SLC 27A: SMETS2 installation obligations
SLC 36: Financial obligations / capital adequacy
SLC 55: Feed-in Tariff / Export obligations

This module tracks compliance status for key SLCs using observable company data
(CRM, billing, metering — no simulation internals).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class SLCStatus:
    slc_number: str        # e.g. "SLC 14"
    description: str
    status: Literal["COMPLIANT", "MONITOR", "BREACH", "NOT_ASSESSED"]
    evidence: str = ""     # what evidence supports the status
    last_checked: str = ""


_SLC_CATALOGUE = {
    "SLC 7": "Accurate bills issued within 12 months of meter read",
    "SLC 14": "Complaints acknowledged in 2 working days; resolved within 8 weeks; Ombudsman access",
    "SLC 21C": "Domestic Price Cap — unit rates and standing charges within Ofgem cap",
    "SLC 22": "Smart metering — best endeavours to install HH / SMETS2 meters",
    "SLC 27": "Annual smart meter rollout progress reporting to Ofgem",
    "SLC 27A": "SMETS2 installation targets (phased from 2019)",
    "SLC 36": "Financial obligations — hold adequate capital, MCR compliance",
    "SLC 47": "Vulnerable customer PSR — Priority Service Register maintained",
    "SLC 55": "Export obligations (Smart Export Guarantee / SEG)",
}


class LicenceMonitor:
    """Tracks compliance status against key Standard Licence Conditions."""

    def __init__(self):
        self._statuses: dict[str, SLCStatus] = {}

    def set_status(self, slc_number: str, status: Literal["COMPLIANT", "MONITOR", "BREACH", "NOT_ASSESSED"], evidence: str = "", last_checked: str = "") -> SLCStatus:
        desc = _SLC_CATALOGUE.get(slc_number, f"SLC {slc_number}")
        s = SLCStatus(
            slc_number=slc_number,
            description=desc,
            status=status,
            evidence=evidence,
            last_checked=last_checked,
        )
        self._statuses[slc_number] = s
        return s

    def get(self, slc_number: str) -> SLCStatus | None:
        return self._statuses.get(slc_number)

    def all_statuses(self) -> list[SLCStatus]:
        return list(self._statuses.values())

    def breaches(self) -> list[SLCStatus]:
        return [s for s in self._statuses.values() if s.status == "BREACH"]

    def under_monitor(self) -> list[SLCStatus]:
        return [s for s in self._statuses.values() if s.status == "MONITOR"]

    def catalogue(self) -> dict[str, str]:
        return dict(_SLC_CATALOGUE)

    def compliance_summary(self) -> dict:
        statuses = list(self._statuses.values())
        return {
            "total_monitored": len(statuses),
            "compliant": sum(1 for s in statuses if s.status == "COMPLIANT"),
            "monitor": sum(1 for s in statuses if s.status == "MONITOR"),
            "breach": sum(1 for s in statuses if s.status == "BREACH"),
            "not_assessed": sum(1 for s in statuses if s.status == "NOT_ASSESSED"),
            "rag": "RED" if any(s.status == "BREACH" for s in statuses) else (
                   "AMBER" if any(s.status == "MONITOR" for s in statuses) else "GREEN"
            ),
        }
