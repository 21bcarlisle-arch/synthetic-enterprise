"""Prepayment meter (PPM) debt loading: regulated process under Ofgem PPM Rules 2019."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class PPMDebtLoadStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"   # voluntary or Ofgem-directed pause
    COMPLETED = "completed"   # debt fully recovered


_MAX_DEBT_LOAD_GBP_DOMESTIC = 250.0  # Ofgem PPM Rules 2019
_MAX_RECOVERY_RATE_PCT = 5.0          # max 5% of each top-up
_EMERGENCY_CREDIT_MIN_GBP = 5.0       # must always be accessible


@dataclass(frozen=True)
class PPMDebtLoad:
    account_id: str
    mprn_or_mpan: str
    debt_amount_gbp: float
    load_date: dt.date
    recovery_rate_pct: float        # fraction of each top-up withheld for debt
    is_domestic: bool = True
    is_smart_meter: bool = False
    customer_consented: bool = False
    status: PPMDebtLoadStatus = PPMDebtLoadStatus.ACTIVE

    @property
    def max_load_gbp(self) -> float:
        return _MAX_DEBT_LOAD_GBP_DOMESTIC if self.is_domestic else self.debt_amount_gbp

    @property
    def is_compliant(self) -> bool:
        if self.debt_amount_gbp > self.max_load_gbp:
            return False
        if self.recovery_rate_pct > _MAX_RECOVERY_RATE_PCT:
            return False
        if self.is_smart_meter and not self.customer_consented:
            return False
        return True

    def expected_recovery_days(self, monthly_spend_gbp: float) -> Optional[float]:
        if monthly_spend_gbp <= 0 or self.recovery_rate_pct <= 0:
            return None
        daily_spend = monthly_spend_gbp / 30.0
        daily_recovery = daily_spend * (self.recovery_rate_pct / 100.0)
        return round(self.debt_amount_gbp / daily_recovery, 1)


def _update_load(r: PPMDebtLoad, **kwargs) -> PPMDebtLoad:
    fields = {
        "account_id": r.account_id,
        "mprn_or_mpan": r.mprn_or_mpan,
        "debt_amount_gbp": r.debt_amount_gbp,
        "load_date": r.load_date,
        "recovery_rate_pct": r.recovery_rate_pct,
        "is_domestic": r.is_domestic,
        "is_smart_meter": r.is_smart_meter,
        "customer_consented": r.customer_consented,
        "status": r.status,
    }
    fields.update(kwargs)
    return PPMDebtLoad(**fields)


class PPMDebtLoadingBook:
    """Tracks debt loaded onto prepayment meters.

    Real calibration (Ofgem 2023 PPM investigation):
    - Max domestic load: GBP250 per fuel
    - Recovery rate cap: 5% per top-up (prevents emergency credit exhaustion)
    - Smart PPM consent: required since 2019 reform; traditional PPMs do not need consent
    - 2023 British Gas scandal: journalists went undercover; warrants used to
      forcibly install PPMs on vulnerable customers; Ofgem banned forced-fitting April 2023
    - PPM in-home poverty trap: customers self-rationing energy to clear debt
    - ~3% of domestic customers have active debt loads at any time
    """

    def __init__(self) -> None:
        self._records: Dict[str, PPMDebtLoad] = {}

    def record_load(self, load: PPMDebtLoad) -> PPMDebtLoad:
        self._records[load.account_id] = load
        return load

    def suspend(self, account_id: str) -> PPMDebtLoad:
        r = _update_load(self._records[account_id], status=PPMDebtLoadStatus.SUSPENDED)
        self._records[account_id] = r
        return r

    def complete(self, account_id: str) -> PPMDebtLoad:
        r = _update_load(self._records[account_id], status=PPMDebtLoadStatus.COMPLETED)
        self._records[account_id] = r
        return r

    def active_loads(self) -> List[PPMDebtLoad]:
        return [r for r in self._records.values() if r.status == PPMDebtLoadStatus.ACTIVE]

    def non_compliant_loads(self) -> List[PPMDebtLoad]:
        return [r for r in self._records.values() if not r.is_compliant]

    def smart_meter_consents_missing(self) -> List[PPMDebtLoad]:
        return [
            r for r in self.active_loads()
            if r.is_smart_meter and not r.customer_consented
        ]

    def total_loaded_gbp(self) -> float:
        return round(sum(r.debt_amount_gbp for r in self.active_loads()), 2)

    def loading_summary(self) -> dict:
        active = self.active_loads()
        return {
            "total_accounts": len(self._records),
            "active_loads": len(active),
            "suspended": sum(1 for r in self._records.values() if r.status == PPMDebtLoadStatus.SUSPENDED),
            "completed": sum(1 for r in self._records.values() if r.status == PPMDebtLoadStatus.COMPLETED),
            "non_compliant": len(self.non_compliant_loads()),
            "smart_meter_consents_missing": len(self.smart_meter_consents_missing()),
            "total_loaded_gbp": self.total_loaded_gbp(),
        }
