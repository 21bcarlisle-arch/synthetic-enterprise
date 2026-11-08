"""Meter Point Administration Number (MPAN) and Meter Point Reference Number (MPRN) management.

Every UK supply point has a government-issued identifier:
- MPAN (13 digits): electricity, issued by the local DNO
- MPRN (10 digits): gas, issued by Xoserve

These are used in Elexon/Xoserve settlement reconciliation, switching flows,
and regulatory reporting. The company discovers these through meter reads,
Data Transfer Network (DTN) messages, and site visits.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


_MPAN_RE = re.compile(r"^\d{13}$")
_MPRN_RE = re.compile(r"^\d{6,10}$")

# Top-line value for UK DNO regions (profile class embedded in MPAN structure)
PROFILE_CLASS_LABELS = {
    1: "Domestic Unrestricted",
    2: "Domestic Economy 7",
    3: "Non-Domestic Unrestricted",
    4: "Non-Domestic Economy 7",
    5: "Non-Domestic HH max demand (LV)",
    6: "Non-Domestic HH max demand (HV)",
    7: "Aggregated supplies (LV)",
    8: "Aggregated supplies (HV)",
}


@dataclass
class MeterPoint:
    customer_id: str
    commodity: Literal["electricity", "gas"]
    mpan: str | None = None  # 13-digit string for electricity
    mprn: str | None = None  # 6-10 digit string for gas
    profile_class: int | None = None  # 1-8 (electricity only)
    gsp_group: str | None = None  # GSP group code e.g. "_A" to "_P"
    registered: bool = False
    registered_date: str = ""

    @property
    def reference(self) -> str | None:
        return self.mpan if self.commodity == "electricity" else self.mprn

    @property
    def profile_class_label(self) -> str:
        if self.profile_class is None:
            return "Unknown"
        return PROFILE_CLASS_LABELS.get(self.profile_class, f"PC{self.profile_class}")


def validate_mpan(mpan: str) -> bool:
    """Return True if mpan is a valid 13-digit MPAN string."""
    return bool(_MPAN_RE.match(mpan.replace(" ", "")))


def validate_mprn(mprn: str) -> bool:
    """Return True if mprn is 6-10 digits (Xoserve format)."""
    return bool(_MPRN_RE.match(mprn.replace(" ", "")))


def infer_profile_class(segment: str, metering: str = "") -> int:
    """Infer likely profile class from customer segment and metering type.

    PC1/2: domestic; PC3/4: non-domestic unrestricted/E7; PC5-8: HH/I&C.
    """
    seg = segment.lower()
    met = metering.lower()
    if seg == "resi":
        return 2 if "e7" in met or "economy" in met else 1
    if seg == "sme":
        return 4 if "e7" in met or "economy" in met else 3
    if seg in ("ic", "i&c", "i_c"):
        return 5
    return 3  # default non-domestic


class MeterPointRegistry:
    """Company-layer registry of all known meter points."""

    def __init__(self):
        self._points: dict[str, list[MeterPoint]] = {}  # customer_id -> list

    def register(self, point: MeterPoint) -> MeterPoint:
        """Add or replace meter point for a customer/commodity combination."""
        pts = self._points.setdefault(point.customer_id, [])
        for i, p in enumerate(pts):
            if p.commodity == point.commodity:
                pts[i] = point
                return point
        pts.append(point)
        return point

    def get(self, customer_id: str, commodity: Literal["electricity", "gas"]) -> MeterPoint | None:
        for p in self._points.get(customer_id, []):
            if p.commodity == commodity:
                return p
        return None

    def electricity(self, customer_id: str) -> MeterPoint | None:
        return self.get(customer_id, "electricity")

    def gas(self, customer_id: str) -> MeterPoint | None:
        return self.get(customer_id, "gas")

    def all_for_customer(self, customer_id: str) -> list[MeterPoint]:
        return list(self._points.get(customer_id, []))

    def unregistered(self) -> list[MeterPoint]:
        """Return meter points not yet confirmed registered with Elexon/Xoserve."""
        return [
            p
            for pts in self._points.values()
            for p in pts
            if not p.registered
        ]

    def summary(self) -> dict:
        all_pts = [p for pts in self._points.values() for p in pts]
        return {
            "total": len(all_pts),
            "electricity": sum(1 for p in all_pts if p.commodity == "electricity"),
            "gas": sum(1 for p in all_pts if p.commodity == "gas"),
            "registered": sum(1 for p in all_pts if p.registered),
            "unregistered": sum(1 for p in all_pts if not p.registered),
            "customers": len(self._points),
        }
