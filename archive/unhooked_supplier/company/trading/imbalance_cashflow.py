"""Imbalance Cash Flow Register (Phase FT).

Tracks the financial flows resulting from BSC settlement imbalance:
- Net Open Position (NOP) = Metered Volume - Contracted Volume
- Short position (consumed more than contracted): pays SBP (System Buy Price)
- Long position (consumed less than contracted): receives SSP (System Sell Price)

SBP > SSP by design (dual cash-out mechanism) to incentivize accurate forecasting.
The spread (SBP-SSP) can be very large during crisis periods.

Cash flow impact on liquidity:
- Settlement runs: Initial Settlement (D+2 working days), Reconciliation (14 working days),
  Final Reconciliation, and then Amended Final (every 28 days for ~14 months)
- Elexon runs settlement each working day; cash flows follow with 5-day payment terms

This module provides aggregate visibility of imbalance cash flows for:
1. Liquidity management (cash in/out from BSC settlement)
2. Risk reporting to board
3. Input to BSC credit register (Phase FI)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class SettlementRunType(str, Enum):
    INITIAL = "initial"           # D+2 working days
    RECONCILIATION = "reconciliation"   # D+14
    FINAL = "final"
    AMENDED_FINAL = "amended_final"


class ImbalanceDirection(str, Enum):
    SHORT = "short"   # consumed more than contracted -> pays SBP
    LONG = "long"     # consumed less -> receives SSP
    FLAT = "flat"     # within tolerance


_FLAT_TOLERANCE_MWH = 0.5


@dataclass(frozen=True)
class ImbalanceCashFlowRecord:
    settlement_date: dt.date
    run_type: SettlementRunType
    nop_mwh: float           # positive = short, negative = long
    sbp_gbp_per_mwh: float
    ssp_gbp_per_mwh: float
    payment_due_date: dt.date

    @property
    def direction(self) -> ImbalanceDirection:
        if abs(self.nop_mwh) <= _FLAT_TOLERANCE_MWH:
            return ImbalanceDirection.FLAT
        return ImbalanceDirection.SHORT if self.nop_mwh > 0 else ImbalanceDirection.LONG

    @property
    def cash_flow_gbp(self) -> float:
        if self.direction == ImbalanceDirection.FLAT:
            return 0.0
        if self.direction == ImbalanceDirection.SHORT:
            return -abs(self.nop_mwh) * self.sbp_gbp_per_mwh  # outflow
        return abs(self.nop_mwh) * self.ssp_gbp_per_mwh        # inflow

    @property
    def is_outflow(self) -> bool:
        return self.cash_flow_gbp < 0

    @property
    def sbp_ssp_spread(self) -> float:
        return self.sbp_gbp_per_mwh - self.ssp_gbp_per_mwh

    def cashflow_summary(self) -> str:
        return (
            "ImbCashFlow " + str(self.settlement_date) + " " + self.run_type.value + ": "
            "NOP=" + str(round(self.nop_mwh, 1)) + "MWh "
            "[" + self.direction.value + "] "
            "GBP" + str(round(self.cash_flow_gbp, 0))
        )


class ImbalanceCashFlowRegister:

    def __init__(self) -> None:
        self._records: List[ImbalanceCashFlowRecord] = []

    def record(self, r: ImbalanceCashFlowRecord) -> ImbalanceCashFlowRecord:
        self._records.append(r)
        return r

    def records_for_date(self, date: dt.date) -> List[ImbalanceCashFlowRecord]:
        return [r for r in self._records if r.settlement_date == date]

    def short_records(self) -> List[ImbalanceCashFlowRecord]:
        return [r for r in self._records if r.direction == ImbalanceDirection.SHORT]

    def long_records(self) -> List[ImbalanceCashFlowRecord]:
        return [r for r in self._records if r.direction == ImbalanceDirection.LONG]

    def total_net_cashflow_gbp(self) -> float:
        return sum(r.cash_flow_gbp for r in self._records)

    def pending_payments_gbp(self, as_of: dt.date) -> float:
        return sum(
            r.cash_flow_gbp for r in self._records
            if r.is_outflow and r.payment_due_date >= as_of
        )

    def total_sbp_paid_gbp(self) -> float:
        return sum(-r.cash_flow_gbp for r in self.short_records())

    def total_ssp_received_gbp(self) -> float:
        return sum(r.cash_flow_gbp for r in self.long_records())

    def cashflow_register_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        net = self.total_net_cashflow_gbp()
        pending = abs(self.pending_payments_gbp(as_of))
        return (
            "Imbalance Cash Flow (" + str(as_of) + "): "
            + str(n) + " records. "
            "Net: GBP" + str(round(net, 0)) + ". "
            "Pending outflows: GBP" + str(round(pending, 0)) + "."
        )
