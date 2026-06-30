"""Renewable Gas Guarantee of Origin (RGGO) Register (Phase GV).

Renewable Gas Guarantees of Origin (RGGOs) are certificates issued by
Xoserve for biomethane injected into the GB gas grid. Suppliers offering
green gas tariffs must procure and redeem RGGOs to substantiate their
renewable gas claims.

Regulatory framework:
  Green Gas Law 2021 / Green Gas Certification Scheme (GGCS)
  RGGOs issued by Green Gas Certification Company (GGCC) under Xoserve
  One RGGO = one MWh of verified biomethane injected into the gas grid
  Annual redemption deadline: 31 March for the prior calendar year
  Unredeemed RGGOs may be traded; expired RGGOs cannot be redeemed
  Fuel Mix Disclosure (FMD): Ofgem requires RGGO evidence for green claims
  CMA Green Claims Code applies: 100% green gas must be 100% RGGO-backed

Biomethane sources (ISCC certification):
  FOOD_WASTE: anaerobic digestion of food waste (highest GHG saving)
  AGRICULTURAL_WASTE: farm-based biogas (slurry, manure, crop residues)
  SEWAGE_SLUDGE: wastewater treatment gas
  ENERGY_CROPS: purpose-grown crops (lower GHG saving; subsidy concerns)
  OTHER: mixed or unclassified

Distinct from: green_gas_levy_register.py (GGL tax payments),
rego_portfolio.py (electricity REGOs), fuel_mix_disclosure.py (FMD report).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

_REDEMPTION_DEADLINE_MONTH = 3
_REDEMPTION_DEADLINE_DAY = 31


class RGGOStatus(str, Enum):
    ISSUED = "issued"
    REDEEMED = "redeemed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BiomethaneSource(str, Enum):
    FOOD_WASTE = "food_waste"
    AGRICULTURAL_WASTE = "agricultural_waste"
    SEWAGE_SLUDGE = "sewage_sludge"
    ENERGY_CROPS = "energy_crops"
    OTHER = "other"


@dataclass(frozen=True)
class RGGORecord:
    record_id: str
    certificate_ref: str
    issue_date: dt.date
    valid_to: dt.date
    volume_mwh: float
    source: BiomethaneSource
    producer_name: str
    status: RGGOStatus = RGGOStatus.ISSUED
    redeemed_date: Optional[dt.date] = None
    redemption_account: str = ""

    @property
    def is_available(self) -> bool:
        return self.status == RGGOStatus.ISSUED

    def is_expired(self, as_of: dt.date) -> bool:
        return self.is_available and as_of > self.valid_to

    def is_redeemable(self, as_of: dt.date) -> bool:
        return self.is_available and as_of <= self.valid_to

    def rggo_summary(self) -> str:
        return (
            "RGGO " + self.record_id + " cert=" + self.certificate_ref
            + " " + str(self.volume_mwh) + "MWh"
            + " src=" + self.source.value
            + " [" + self.status.value + "]"
        )


def redemption_deadline_for_year(year: int) -> dt.date:
    return dt.date(year + 1, _REDEMPTION_DEADLINE_MONTH, _REDEMPTION_DEADLINE_DAY)


class RGGORegister:

    def __init__(self) -> None:
        self._records: List[RGGORecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "RGGO-" + str(self._counter).zfill(6)

    def register_rggo(
        self,
        certificate_ref: str,
        issue_date: dt.date,
        valid_to: dt.date,
        volume_mwh: float,
        source: BiomethaneSource,
        producer_name: str,
    ) -> RGGORecord:
        if volume_mwh <= 0:
            raise ValueError("volume_mwh must be positive")
        if valid_to <= issue_date:
            raise ValueError("valid_to must be after issue_date")
        record = RGGORecord(
            record_id=self._next_id(), certificate_ref=certificate_ref,
            issue_date=issue_date, valid_to=valid_to, volume_mwh=volume_mwh,
            source=source, producer_name=producer_name,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> RGGORecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = RGGORecord(
                    record_id=r.record_id, certificate_ref=r.certificate_ref,
                    issue_date=r.issue_date, valid_to=r.valid_to,
                    volume_mwh=r.volume_mwh, source=r.source,
                    producer_name=r.producer_name,
                    status=kwargs.get("status", r.status),
                    redeemed_date=kwargs.get("redeemed_date", r.redeemed_date),
                    redemption_account=kwargs.get("redemption_account", r.redemption_account),
                )
                self._records[i] = updated
                return updated
        raise KeyError("RGGO " + record_id + " not found")

    def redeem(
        self, record_id: str, redeemed_date: dt.date, redemption_account: str = "",
    ) -> RGGORecord:
        r = next((x for x in self._records if x.record_id == record_id), None)
        if r is None:
            raise KeyError("RGGO " + record_id + " not found")
        if not r.is_redeemable(redeemed_date):
            raise ValueError("RGGO " + record_id + " is not redeemable as of " + str(redeemed_date))
        return self._update(record_id, status=RGGOStatus.REDEEMED,
                            redeemed_date=redeemed_date, redemption_account=redemption_account)

    def cancel(self, record_id: str) -> RGGORecord:
        return self._update(record_id, status=RGGOStatus.CANCELLED)

    def expire_stale(self, as_of: dt.date) -> List[RGGORecord]:
        expired = []
        for r in self._records:
            if r.is_expired(as_of):
                updated = self._update(r.record_id, status=RGGOStatus.EXPIRED)
                expired.append(updated)
        return expired

    def available_rggo_mwh(self, as_of: dt.date) -> float:
        return sum(r.volume_mwh for r in self._records if r.is_redeemable(as_of))

    def redeemed_rggo_mwh(self) -> float:
        return sum(r.volume_mwh for r in self._records if r.status == RGGOStatus.REDEEMED)

    def by_source(self, source: BiomethaneSource) -> List[RGGORecord]:
        return [r for r in self._records if r.source == source]

    def expiring_before(self, before_date: dt.date) -> List[RGGORecord]:
        return [r for r in self._records if r.is_available and r.valid_to < before_date]

    def redemption_rate_pct(self) -> Optional[float]:
        total = sum(r.volume_mwh for r in self._records
                    if r.status in (RGGOStatus.REDEEMED, RGGOStatus.EXPIRED))
        redeemed = self.redeemed_rggo_mwh()
        all_settled = total
        if all_settled == 0:
            return None
        return round(redeemed / all_settled * 100, 1)

    def rggo_register_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        avail_mwh = round(self.available_rggo_mwh(as_of), 0)
        rdeemed_mwh = round(self.redeemed_rggo_mwh(), 0)
        return (
            "RGGO Register (" + str(as_of) + "): "
            + str(n) + " certificates. "
            + str(avail_mwh) + " MWh available, "
            + str(rdeemed_mwh) + " MWh redeemed."
        )
