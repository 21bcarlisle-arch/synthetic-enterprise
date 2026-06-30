"""Prosumer Balance Register (Phase EH).

A prosumer is simultaneously consumer (import) and generator (export).
SEG mandatory for licensed suppliers >150k domestic customers (Jan 2020).
V2G: Ofgem 2024 consultation.
Standing charges: net exporters still owe daily standing charge.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ProsumerStatus(str, Enum):
    NET_IMPORTER = "net_importer"
    NET_EXPORTER = "net_exporter"
    BALANCED = "balanced"


class V2GParticipationStatus(str, Enum):
    NOT_ENROLLED = "not_enrolled"
    ENROLLED = "enrolled"
    ACTIVE = "active"
    SUSPENDED = "suspended"


@dataclass(frozen=True)
class ProsumerPeriodBalance:
    account_id: str
    period_start: dt.date
    period_end: dt.date
    gross_import_kwh: float
    gross_export_kwh: float
    seg_rate_gbp_per_kwh: float
    standing_charge_gbp_per_day: float
    v2g_export_kwh: float = 0.0

    @property
    def net_kwh(self) -> float:
        return self.gross_import_kwh - self.gross_export_kwh

    @property
    def status(self) -> ProsumerStatus:
        net = self.net_kwh
        if net > 100:
            return ProsumerStatus.NET_IMPORTER
        if net < -100:
            return ProsumerStatus.NET_EXPORTER
        return ProsumerStatus.BALANCED

    @property
    def seg_payment_gbp(self) -> float:
        return self.gross_export_kwh * self.seg_rate_gbp_per_kwh

    @property
    def standing_charge_total_gbp(self) -> float:
        days = (self.period_end - self.period_start).days
        return self.standing_charge_gbp_per_day * days

    @property
    def net_bill_gbp(self) -> float:
        return self.standing_charge_total_gbp - self.seg_payment_gbp

    @property
    def v2g_fraction_pct(self) -> float:
        if self.gross_export_kwh == 0:
            return 0.0
        return self.v2g_export_kwh / self.gross_export_kwh * 100


class ProsumerBalanceRegister:

    def __init__(self) -> None:
        self._balances: Dict[str, List[ProsumerPeriodBalance]] = {}
        self._v2g_status: Dict[str, V2GParticipationStatus] = {}

    def record_period(self, balance: ProsumerPeriodBalance) -> ProsumerPeriodBalance:
        self._balances.setdefault(balance.account_id, []).append(balance)
        return balance

    def set_v2g_status(self, account_id: str, status: V2GParticipationStatus) -> None:
        self._v2g_status[account_id] = status

    def balances_for(self, account_id: str) -> List[ProsumerPeriodBalance]:
        return self._balances.get(account_id, [])

    def latest_balance(self, account_id: str) -> Optional[ProsumerPeriodBalance]:
        bs = self._balances.get(account_id, [])
        return max(bs, key=lambda b: b.period_end) if bs else None

    def net_exporters(self) -> List[str]:
        result = []
        for aid in self._balances:
            latest = self.latest_balance(aid)
            if latest and latest.status == ProsumerStatus.NET_EXPORTER:
                result.append(aid)
        return result

    def v2g_enrolled(self) -> List[str]:
        return [
            aid for aid, s in self._v2g_status.items()
            if s in (V2GParticipationStatus.ENROLLED, V2GParticipationStatus.ACTIVE)
        ]

    def total_seg_owed_gbp(self) -> float:
        total = 0.0
        for balances in self._balances.values():
            if balances:
                latest = max(balances, key=lambda b: b.period_end)
                bill = latest.net_bill_gbp
                if bill < 0:
                    total += abs(bill)
        return total

    def prosumer_summary(self) -> str:
        n = len(self._balances)
        n_export = len(self.net_exporters())
        n_v2g = len(self.v2g_enrolled())
        return (
            f"Prosumer Balance Register: {n} prosumer accounts. "
            f"Net exporters: {n_export}. V2G enrolled: {n_v2g}. "
            f"SEG mandatory (>150k customers); V2G: Ofgem 2024 consultation."
        )
