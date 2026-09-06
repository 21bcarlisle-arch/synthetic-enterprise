"""BSC Settlement Run Tracking Register (Phase DH).

UK BSC P272 / SVA Settlement Process: each settlement period undergoes multiple
reconciliation runs after the first run (SF). This module does not state the
timetable — it READS it, from `company.regulatory.settlement_reconciliation.
ELEXON_RUN_MONTHS`, which carries the citation.

CORRECTED 2026-09-06. This docstring, the enum comments below and the run-months
map each stated the timetable independently, as fact, with no citation on any of
them, and all three were wrong: SF at 14 days, R1 at 5 months, R2 at 14, R3 at
26, RF at 28. Against Elexon's own timetable (Priestley, *Settlement Timetable*,
16 June 2014, slide 2, read directly — transcribed in
`docs/market_research/elexon_settlement_run_timetable_verified.md`) the scheduled
runs are SF 1 / R1 2 / R2 4 / R3 7 / RF 14 months. Elexon's RF figure (14) was
attached here to R2, and its DF figure (28 — the DISPUTES-ONLY rectification run,
which an ordinary settlement day never reaches) was attached here to RF, so this
register had every settlement day carrying a dispute-length tail and calling the
end of it "final, no further runs".

The sourced correction landed in `settlement_reconciliation.py` on 2026-08-29 and
did not reach here for nineteen days, because nothing in the tree could observe
two settlement timetables disagreeing. That is why this file now imports rather
than restates: a copy is what made the correction miss it.

Each run may produce a credit or debit adjustment vs the prior run. Suppliers must
account for these as revenue adjustments. Unmatched runs are a BSC compliance risk.

Key facts:
- Elexon distributes "Party Charge Advice Notice" (PCAN) for each run
- SVA settlement uses Profile Classes; NHH suppliers see large R2/R3 adjustments
  when smart meter actuals replace estimated consumption
- BSC SVA Agents: DC submits reads, DA aggregates, settlement auto-computes charges
- HH market (NHH migrating to HH under MHHS): R-runs closer to SF as HH is near-accurate
- Material variance threshold: Ofgem/Elexon flag if >5% vs SF

Epistemic: company can observe its own PCAN statements and settlement adjustments.
Cannot see Elexon's internal settlement engine.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from company.regulatory.settlement_reconciliation import ELEXON_RUN_MONTHS


class SettlementRunType(str, Enum):
    """The scheduled SVA runs. Timings are NOT restated here on purpose — they
    live once, in ELEXON_RUN_MONTHS; a comment carrying a month figure beside
    each member is exactly the copy that went stale."""
    SF = "SF"   # First run
    R1 = "R1"   # First Reconciliation (interim run)
    R2 = "R2"   # Second Reconciliation (interim run)
    R3 = "R3"   # Third Reconciliation (interim run)
    RF = "RF"   # Final Reconciliation -- the LAST SCHEDULED run


class AdjustmentDirection(str, Enum):
    CREDIT = "credit"    # supplier receives money back
    DEBIT = "debit"      # supplier owes more
    NIL = "nil"          # no adjustment


_SETTLEMENT_RUN_MONTHS: Dict[SettlementRunType, int] = {
    run: ELEXON_RUN_MONTHS[run.value] for run in SettlementRunType
}

_MATERIAL_VARIANCE_THRESHOLD = 0.05   # >5% vs SF = material


@dataclass(frozen=True)
class SettlementRunRecord:
    run_id: str
    settlement_date: dt.date        # the half-hourly period being settled
    run_type: SettlementRunType
    run_received_at: dt.date        # when PCAN received
    kwh_settled: float
    charges_gbp: float              # total party charge (positive = we pay)
    prior_charges_gbp: float        # charges from previous run (or 0 for SF)
    pcan_reference: Optional[str] = None

    @property
    def adjustment_gbp(self) -> float:
        if self.run_type == SettlementRunType.SF:
            return 0.0
        return self.charges_gbp - self.prior_charges_gbp

    @property
    def direction(self) -> AdjustmentDirection:
        if self.run_type == SettlementRunType.SF:
            return AdjustmentDirection.NIL
        adj = self.adjustment_gbp
        if adj < -0.01:
            return AdjustmentDirection.CREDIT
        if adj > 0.01:
            return AdjustmentDirection.DEBIT
        return AdjustmentDirection.NIL

    @property
    def variance_pct(self) -> Optional[float]:
        if self.run_type == SettlementRunType.SF or self.prior_charges_gbp == 0:
            return None
        return abs(self.adjustment_gbp) / abs(self.prior_charges_gbp)

    @property
    def is_material(self) -> bool:
        v = self.variance_pct
        return v is not None and v >= _MATERIAL_VARIANCE_THRESHOLD

    @property
    def expected_run_date(self) -> dt.date:
        months = _SETTLEMENT_RUN_MONTHS[self.run_type]
        d = self.settlement_date
        m = d.month + months
        y = d.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        return dt.date(y, m, 1)

    @property
    def is_final(self) -> bool:
        return self.run_type == SettlementRunType.RF


class BSCSettlementRunRegister:
    """Tracks BSC settlement runs and reconciliation adjustments."""

    def __init__(self) -> None:
        self._records: List[SettlementRunRecord] = []
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"SR-{self._seq:05d}"

    def record_run(
        self,
        settlement_date: dt.date,
        run_type: SettlementRunType,
        run_received_at: dt.date,
        kwh_settled: float,
        charges_gbp: float,
        prior_charges_gbp: float = 0.0,
        pcan_reference: Optional[str] = None,
    ) -> SettlementRunRecord:
        rec = SettlementRunRecord(
            run_id=self._next_id(),
            settlement_date=settlement_date,
            run_type=run_type,
            run_received_at=run_received_at,
            kwh_settled=kwh_settled,
            charges_gbp=charges_gbp,
            prior_charges_gbp=prior_charges_gbp,
            pcan_reference=pcan_reference,
        )
        self._records.append(rec)
        return rec

    def runs_for_date(self, settlement_date: dt.date) -> List[SettlementRunRecord]:
        return [r for r in self._records if r.settlement_date == settlement_date]

    def by_run_type(self, run_type: SettlementRunType) -> List[SettlementRunRecord]:
        return [r for r in self._records if r.run_type == run_type]

    def material_variances(self) -> List[SettlementRunRecord]:
        return [r for r in self._records if r.is_material]

    def credits(self) -> List[SettlementRunRecord]:
        return [r for r in self._records
                if r.direction == AdjustmentDirection.CREDIT]

    def debits(self) -> List[SettlementRunRecord]:
        return [r for r in self._records
                if r.direction == AdjustmentDirection.DEBIT]

    def total_adjustment_gbp(self) -> float:
        return sum(r.adjustment_gbp for r in self._records
                   if r.run_type != SettlementRunType.SF)

    def total_credit_gbp(self) -> float:
        return sum(-r.adjustment_gbp for r in self.credits())

    def total_debit_gbp(self) -> float:
        return sum(r.adjustment_gbp for r in self.debits())

    def finalised_dates(self) -> List[dt.date]:
        return [r.settlement_date for r in self._records if r.is_final]

    def run_type_breakdown(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self._records:
            out[r.run_type.value] = out.get(r.run_type.value, 0) + 1
        return out

    def settlement_summary(self) -> str:
        total = len(self._records)
        material = len(self.material_variances())
        net_adj = self.total_adjustment_gbp()
        credits = self.total_credit_gbp()
        debits = self.total_debit_gbp()
        finalised = len(self.finalised_dates())
        breakdown = self.run_type_breakdown()
        direction = "credit" if net_adj < 0 else "debit"
        return (
            f"BSC Settlement Run Register: {total} runs, {material} material variances. "
            f"Net adjustment: £{abs(net_adj):.2f} ({direction}). "
            f"Credits: £{credits:.2f} | Debits: £{debits:.2f}. "
            f"Finalised dates: {finalised}. Run breakdown: {breakdown}."
        )
