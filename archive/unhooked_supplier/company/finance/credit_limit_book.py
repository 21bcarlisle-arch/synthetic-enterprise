from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CounterpartyType(str, Enum):
    BANK = "bank"
    BROKER = "broker"
    GENERATOR = "generator"
    INTERCONNECTOR = "interconnector"
    CLEARING_HOUSE = "clearing_house"


@dataclass(frozen=True)
class CreditLimit:
    counterparty_id: str
    counterparty_type: CounterpartyType
    limit_gbp: float
    approved_date: str
    approved_by: str

    @property
    def is_material(self) -> bool:
        return self.limit_gbp >= 1_000_000.0


@dataclass(frozen=True)
class ExposureRecord:
    counterparty_id: str
    as_of_date: str
    current_mtm_gbp: float
    potential_future_exposure_gbp: float

    @property
    def total_exposure_gbp(self) -> float:
        return round(self.current_mtm_gbp + self.potential_future_exposure_gbp, 2)

    @property
    def utilisation_pct(self) -> float:
        return 0.0  # computed against limit in book

    @property
    def is_stress_exposure(self) -> bool:
        return self.potential_future_exposure_gbp > self.current_mtm_gbp * 2


class CreditLimitBook:
    def __init__(self) -> None:
        self._limits: dict[str, CreditLimit] = {}
        self._exposures: list[ExposureRecord] = []

    def set_limit(self, limit: CreditLimit) -> CreditLimit:
        self._limits[limit.counterparty_id] = limit
        return limit

    def get_limit(self, counterparty_id: str) -> Optional[CreditLimit]:
        return self._limits.get(counterparty_id)

    def record_exposure(self, exposure: ExposureRecord) -> ExposureRecord:
        self._exposures.append(exposure)
        return exposure

    def latest_exposure(self, counterparty_id: str) -> Optional[ExposureRecord]:
        matches = [e for e in self._exposures if e.counterparty_id == counterparty_id]
        return max(matches, key=lambda e: e.as_of_date) if matches else None

    def utilisation_pct(self, counterparty_id: str) -> float:
        limit = self._limits.get(counterparty_id)
        exp = self.latest_exposure(counterparty_id)
        if not limit or not exp or limit.limit_gbp == 0:
            return 0.0
        return round(exp.total_exposure_gbp / limit.limit_gbp * 100, 2)

    def is_breach(self, counterparty_id: str) -> bool:
        return self.utilisation_pct(counterparty_id) > 100.0

    def breaches(self) -> list[str]:
        return [cid for cid in self._limits if self.is_breach(cid)]

    def limit_summary(self) -> dict:
        total_limits = sum(l.limit_gbp for l in self._limits.values())
        total_exposure = sum(
            self.latest_exposure(cid).total_exposure_gbp
            for cid in self._limits
            if self.latest_exposure(cid)
        )
        return {
            "counterparty_count": len(self._limits),
            "total_limit_gbp": round(total_limits, 2),
            "total_exposure_gbp": round(total_exposure, 2),
            "portfolio_utilisation_pct": round(total_exposure / total_limits * 100, 2) if total_limits else 0.0,
            "breach_count": len(self.breaches()),
            "material_limits": sum(1 for l in self._limits.values() if l.is_material),
        }
