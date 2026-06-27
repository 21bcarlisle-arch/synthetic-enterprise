"""Winter Disconnection Moratorium: SLC 27 / Gas SoP Regs prohibition on disconnection."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MoratoriumType(str, Enum):
    WINTER_DOMESTIC = "winter_domestic"    # Nov-Mar domestic prohibition
    VULNERABLE_YEAR_ROUND = "vulnerable_year_round"  # year-round vulnerable
    DEBT_MORATORIUM = "debt_moratorium"    # discretionary moratorium during hardship


class DisconnectionRisk(str, Enum):
    NO_RISK = "no_risk"
    PROTECTED = "protected"       # moratorium applies; cannot disconnect
    AT_RISK = "at_risk"           # outside moratorium; debt escalating


_WINTER_START_MONTH = 11  # November
_WINTER_END_MONTH = 3    # March (inclusive)


def is_winter_period(date: dt.date) -> bool:
    return date.month >= _WINTER_START_MONTH or date.month <= _WINTER_END_MONTH


@dataclass(frozen=True)
class MoratoriumRecord:
    account_id: str
    moratorium_type: MoratoriumType
    start_date: dt.date
    end_date: Optional[dt.date]  # None = ongoing (vulnerable year-round)
    reason: str = ""

    def is_active(self, as_of: dt.date) -> bool:
        if as_of < self.start_date:
            return False
        if self.end_date is not None and as_of > self.end_date:
            return False
        return True

    def protection_status(self, as_of: dt.date) -> DisconnectionRisk:
        if self.is_active(as_of):
            return DisconnectionRisk.PROTECTED
        return DisconnectionRisk.NO_RISK


class WinterMoratoriumRegister:
    """Tracks disconnection prohibitions across the customer base.

    Real calibration:
    - SLC 27 (Electricity) / Gas Suppliers SoP Regs: prohibition on disconnecting
      domestic customers during winter (1 Oct-31 Mar was historical; now 1 Nov-31 Mar
      for credit meter customers; vulnerable customers may never be disconnected).
    - Priority Services Register (PSR) customers: year-round disconnection prohibition.
    - Ofgem Voluntary agreement: some suppliers extend to 1 Oct-31 Mar.
    - 2022-23: Ofgem used moratorium powers extensively; thousands of PPM-forced-fitting
      cases later found to have breached these rules.
    - Debt moratorium: supplier discretion; often offered during cost-of-living crisis
      or as hardship support.
    """

    def __init__(self) -> None:
        self._records: List[MoratoriumRecord] = []

    def register(self, record: MoratoriumRecord) -> MoratoriumRecord:
        self._records.append(record)
        return record

    def end_moratorium(self, account_id: str, end_date: dt.date) -> Optional[MoratoriumRecord]:
        import dataclasses
        for i, r in enumerate(self._records):
            if r.account_id == account_id and r.end_date is None:
                updated = dataclasses.replace(r, end_date=end_date)
                self._records[i] = updated
                return updated
        return None

    def active_protections(self, as_of: dt.date) -> List[MoratoriumRecord]:
        return [r for r in self._records if r.is_active(as_of)]

    def is_protected(self, account_id: str, as_of: dt.date) -> bool:
        return any(
            r.account_id == account_id and r.is_active(as_of)
            for r in self._records
        )

    def can_disconnect(self, account_id: str, as_of: dt.date,
                       is_vulnerable: bool = False) -> bool:
        if self.is_protected(account_id, as_of):
            return False
        if is_winter_period(as_of):
            return False
        return True

    def vulnerable_protections(self, as_of: dt.date) -> List[MoratoriumRecord]:
        return [r for r in self.active_protections(as_of)
                if r.moratorium_type == MoratoriumType.VULNERABLE_YEAR_ROUND]

    def winter_protections(self, as_of: dt.date) -> List[MoratoriumRecord]:
        return [r for r in self.active_protections(as_of)
                if r.moratorium_type == MoratoriumType.WINTER_DOMESTIC]

    def moratorium_summary(self, as_of: dt.date) -> dict:
        active = self.active_protections(as_of)
        return {
            "total_records": len(self._records),
            "active_protections": len(active),
            "vulnerable_year_round": len(self.vulnerable_protections(as_of)),
            "winter_domestic": len(self.winter_protections(as_of)),
            "in_winter_period": is_winter_period(as_of),
        }
