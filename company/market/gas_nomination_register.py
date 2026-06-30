"""Gas Transportation Nomination Register.

UNC: suppliers nominate gas volumes to NGG by 08:30 for each gas day.
Imbalance tolerance: small shippers \xb15%. Cash-out applies outside tolerance.
Gas day: 06:00-06:00 (vs electricity 00:30-00:30).
Epistemic: company knows its own nominations. Actual from meter reads.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum


class NominationStatus(str, Enum):
    INITIAL = "initial"
    REVISED = "revised"
    CONFIRMED = "confirmed"
    SETTLED = "settled"


class ImbalanceDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
    BALANCED = "balanced"


_IMBALANCE_TOLERANCE_PCT = 5.0


@dataclass(frozen=True)
class GasNominationRecord:
    gas_day: date
    portfolio_id: str
    nominated_kwh: float
    actual_consumed_kwh: float | None
    status: NominationStatus
    revised_nominated_kwh: float | None = None

    @property
    def effective_nominated_kwh(self) -> float:
        return self.revised_nominated_kwh if self.revised_nominated_kwh is not None else self.nominated_kwh

    @property
    def imbalance_kwh(self) -> float | None:
        if self.actual_consumed_kwh is None:
            return None
        return self.effective_nominated_kwh - self.actual_consumed_kwh

    @property
    def imbalance_pct(self) -> float | None:
        if self.actual_consumed_kwh is None or self.actual_consumed_kwh == 0:
            return None
        return (self.imbalance_kwh or 0) / self.actual_consumed_kwh * 100

    @property
    def direction(self) -> ImbalanceDirection | None:
        imb_pct = self.imbalance_pct
        if imb_pct is None:
            return None
        if abs(imb_pct) <= _IMBALANCE_TOLERANCE_PCT:
            return ImbalanceDirection.BALANCED
        return ImbalanceDirection.LONG if imb_pct > 0 else ImbalanceDirection.SHORT

    @property
    def is_in_tolerance(self) -> bool | None:
        direction = self.direction
        if direction is None:
            return None
        return direction == ImbalanceDirection.BALANCED


class GasNominationRegister:
    def __init__(self, portfolio_id: str = "DEFAULT") -> None:
        self.portfolio_id = portfolio_id
        self._records: list[GasNominationRecord] = []

    def nominate(self, gas_day: date, nominated_kwh: float, status: NominationStatus = NominationStatus.INITIAL) -> GasNominationRecord:
        record = GasNominationRecord(gas_day=gas_day, portfolio_id=self.portfolio_id, nominated_kwh=nominated_kwh, actual_consumed_kwh=None, status=status)
        self._records.append(record)
        return record

    def revise(self, gas_day: date, revised_kwh: float) -> GasNominationRecord:
        old = next(r for r in self._records if r.gas_day == gas_day)
        updated = GasNominationRecord(gas_day=old.gas_day, portfolio_id=old.portfolio_id, nominated_kwh=old.nominated_kwh, actual_consumed_kwh=old.actual_consumed_kwh, status=NominationStatus.REVISED, revised_nominated_kwh=revised_kwh)
        self._records = [updated if r.gas_day == gas_day else r for r in self._records]
        return updated

    def settle(self, gas_day: date, actual_kwh: float) -> GasNominationRecord:
        old = next(r for r in self._records if r.gas_day == gas_day)
        updated = GasNominationRecord(gas_day=old.gas_day, portfolio_id=old.portfolio_id, nominated_kwh=old.nominated_kwh, actual_consumed_kwh=actual_kwh, status=NominationStatus.SETTLED, revised_nominated_kwh=old.revised_nominated_kwh)
        self._records = [updated if r.gas_day == gas_day else r for r in self._records]
        return updated

    @property
    def settled_records(self) -> list[GasNominationRecord]:
        return [r for r in self._records if r.status == NominationStatus.SETTLED]

    @property
    def out_of_tolerance_days(self) -> list[GasNominationRecord]:
        return [r for r in self.settled_records if r.is_in_tolerance is False]

    @property
    def short_days(self) -> list[GasNominationRecord]:
        return [r for r in self.out_of_tolerance_days if r.direction == ImbalanceDirection.SHORT]

    @property
    def long_days(self) -> list[GasNominationRecord]:
        return [r for r in self.out_of_tolerance_days if r.direction == ImbalanceDirection.LONG]

    @property
    def mean_imbalance_pct(self) -> float | None:
        settled = self.settled_records
        if not settled:
            return None
        imb_pcts = [r.imbalance_pct for r in settled if r.imbalance_pct is not None]
        if not imb_pcts:
            return None
        return sum(imb_pcts) / len(imb_pcts)

    def nomination_summary(self) -> str:
        n = len(self._records)
        n_settled = len(self.settled_records)
        n_out = len(self.out_of_tolerance_days)
        lines = [
            "Gas Nomination Register (UNC) — Portfolio: {}".format(self.portfolio_id),
            "Nominations: {:d} | Settled: {:d} | Out of tolerance: {:d}".format(n, n_settled, n_out),
            "Short days: {:d} | Long days: {:d}".format(len(self.short_days), len(self.long_days)),
        ]
        return chr(10).join(lines)
