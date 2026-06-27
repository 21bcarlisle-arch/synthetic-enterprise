"""Payment Method Register — tracks how each account pays.

UK domestic energy: ~70% Direct Debit, ~15% Prepayment Meter, remainder
BACS/cheque/cash. PPM can be voluntarily chosen or debt-mandated (SLC 27).
Ofgem monitors debt-mandated PPM installs as a vulnerability indicator.

Post-2022: forced PPM fitting was Ofgem enforcement trigger (2023 scandal).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class PaymentMethod(str, Enum):
    DIRECT_DEBIT = "direct_debit"
    PREPAYMENT_METER = "prepayment_meter"
    BACS_TRANSFER = "bacs_transfer"
    CHEQUE = "cheque"
    CASH = "cash"


class PaymentMethodSource(str, Enum):
    VOLUNTARY = "voluntary"
    DEBT_MANDATED = "debt_mandated"
    VULNERABILITY_PROTECTION = "vulnerability_protection"
    DEFAULT = "default"


@dataclass(frozen=True)
class PaymentMethodRecord:
    account_id: str
    method: PaymentMethod
    effective_date: date
    source: PaymentMethodSource = PaymentMethodSource.VOLUNTARY
    notes: str = ""

    @property
    def is_prepayment(self) -> bool:
        return self.method == PaymentMethod.PREPAYMENT_METER

    @property
    def is_direct_debit(self) -> bool:
        return self.method == PaymentMethod.DIRECT_DEBIT

    @property
    def is_debt_mandated(self) -> bool:
        return self.source == PaymentMethodSource.DEBT_MANDATED


class PaymentMethodRegister:
    """Per-account payment method tracker with full change history."""

    def __init__(self) -> None:
        self._history: dict[str, list[PaymentMethodRecord]] = {}

    def set_method(
        self,
        account_id: str,
        method: PaymentMethod,
        effective_date: date,
        source: PaymentMethodSource = PaymentMethodSource.VOLUNTARY,
        notes: str = "",
    ) -> PaymentMethodRecord:
        record = PaymentMethodRecord(
            account_id=account_id,
            method=method,
            effective_date=effective_date,
            source=source,
            notes=notes,
        )
        self._history.setdefault(account_id, []).append(record)
        return record

    def current(self, account_id: str) -> Optional[PaymentMethodRecord]:
        hist = self._history.get(account_id)
        return hist[-1] if hist else None

    def history_for(self, account_id: str) -> list[PaymentMethodRecord]:
        return list(self._history.get(account_id, []))

    def accounts_by_method(self, method: PaymentMethod) -> list[str]:
        return [
            aid for aid, hist in self._history.items()
            if hist and hist[-1].method == method
        ]

    def ppm_accounts(self) -> list[str]:
        return self.accounts_by_method(PaymentMethod.PREPAYMENT_METER)

    def dd_accounts(self) -> list[str]:
        return self.accounts_by_method(PaymentMethod.DIRECT_DEBIT)

    def debt_mandated_ppm(self) -> list[str]:
        return [
            aid for aid, hist in self._history.items()
            if hist
            and hist[-1].method == PaymentMethod.PREPAYMENT_METER
            and hist[-1].source == PaymentMethodSource.DEBT_MANDATED
        ]

    def method_breakdown(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for hist in self._history.values():
            if hist:
                key = hist[-1].method.value
                counts[key] = counts.get(key, 0) + 1
        return counts

    def payment_method_summary(self) -> dict:
        total = len(self._history)
        breakdown = self.method_breakdown()
        return {
            "total_accounts": total,
            "method_breakdown": breakdown,
            "dd_count": breakdown.get("direct_debit", 0),
            "ppm_count": breakdown.get("prepayment_meter", 0),
            "bacs_count": breakdown.get("bacs_transfer", 0),
            "debt_mandated_ppm_count": len(self.debt_mandated_ppm()),
        }
