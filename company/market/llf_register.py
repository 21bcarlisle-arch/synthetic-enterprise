"""Line Loss Factor (LLF) Register (Phase GL).

Line Loss Factors (LLFs) adjust metered electricity consumption for
transmission and distribution losses in the electricity network.

When electricity travels from the generation source through the Grid
and distribution network to a customer, some energy is lost as heat
in cables and transformers. LLFs quantify this loss so that settlement
quantities reflect the actual energy purchased at the grid boundary.

Settlement quantity = Metered quantity x LLF

LLF > 1.0 means more energy is lost on the distribution network
(typically rural/remote meters; LLF up to ~1.10-1.15)
LLF < 1.0 would mean network gain (very rare; rounding/measurement)
LLF = 1.0 means no net distribution losses (EHV/HV connection directly
to transmission; typical for large industrial customers)

DNOs publish LLFs annually for the profile year (April-March).
Elexon administers; LLF classes are assigned by DNO per LV network.
Regulatory basis: BSC Section S; LLF methodology in BSC Procedure BSCP128.

Financial impact for suppliers:
  - Must purchase LLF-adjusted volumes from wholesale market
  - LLF increase for a meter = higher settlement cost for that customer
  - Pricing models must bake in LLF; flat 1.0 assumption is an error
  - Typical domestic LLF: 1.00-1.05
  - High-loss rural: up to 1.12; HV-connected I&C: often 1.0

Distinct from Transmission Loss Multipliers (TLMs), which are national
and handled at BSC level (not tracked per-meter by suppliers).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class LLFRecord:
    record_id: str
    mpan: str
    dno_code: str
    llf_class: str
    llf_value: float
    effective_from: dt.date
    effective_to: Optional[dt.date] = None

    @property
    def is_current(self) -> bool:
        return self.effective_to is None

    def is_effective_as_of(self, as_of: dt.date) -> bool:
        if as_of < self.effective_from:
            return False
        if self.effective_to is not None and as_of >= self.effective_to:
            return False
        return True

    @property
    def loss_uplift_pct(self) -> float:
        return round((self.llf_value - 1.0) * 100, 4)

    def llf_summary(self) -> str:
        to_str = str(self.effective_to) if self.effective_to else "current"
        return (
            "LLF " + self.record_id + " mpan=" + self.mpan
            + " class=" + self.llf_class + " value=" + str(self.llf_value)
            + " [" + str(self.effective_from) + " to " + to_str + "]"
        )


class LLFRegister:

    def __init__(self) -> None:
        self._records: List[LLFRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "LLF-" + str(self._counter).zfill(5)

    def register_llf(
        self,
        mpan: str,
        dno_code: str,
        llf_class: str,
        llf_value: float,
        effective_from: dt.date,
        effective_to: Optional[dt.date] = None,
    ) -> LLFRecord:
        if llf_value <= 0:
            raise ValueError("llf_value must be positive; got " + str(llf_value))
        if effective_to is not None and effective_to <= effective_from:
            raise ValueError("effective_to must be after effective_from")
        record = LLFRecord(
            record_id=self._next_id(),
            mpan=mpan,
            dno_code=dno_code,
            llf_class=llf_class,
            llf_value=llf_value,
            effective_from=effective_from,
            effective_to=effective_to,
        )
        self._records.append(record)
        return record

    def update_llf(
        self,
        mpan: str,
        new_llf_class: str,
        new_llf_value: float,
        effective_from: dt.date,
        dno_code: Optional[str] = None,
    ) -> LLFRecord:
        for i, r in enumerate(self._records):
            if r.mpan == mpan and r.is_current:
                closed = LLFRecord(
                    record_id=r.record_id,
                    mpan=r.mpan,
                    dno_code=r.dno_code,
                    llf_class=r.llf_class,
                    llf_value=r.llf_value,
                    effective_from=r.effective_from,
                    effective_to=effective_from,
                )
                self._records[i] = closed
                break
        return self.register_llf(
            mpan=mpan,
            dno_code=dno_code or "unknown",
            llf_class=new_llf_class,
            llf_value=new_llf_value,
            effective_from=effective_from,
        )

    def current_llf_for(self, mpan: str, as_of: dt.date) -> Optional[LLFRecord]:
        candidates = [r for r in self._records if r.mpan == mpan and r.is_effective_as_of(as_of)]
        return candidates[-1] if candidates else None

    def historical_for_mpan(self, mpan: str) -> List[LLFRecord]:
        return sorted([r for r in self._records if r.mpan == mpan], key=lambda r: r.effective_from)

    def all_current_as_of(self, as_of: dt.date) -> List[LLFRecord]:
        return [r for r in self._records if r.is_effective_as_of(as_of)]

    def by_dno(self, dno_code: str) -> List[LLFRecord]:
        return [r for r in self._records if r.dno_code == dno_code]

    def high_loss_meters(self, as_of: dt.date, threshold: float = 1.05) -> List[LLFRecord]:
        return [r for r in self.all_current_as_of(as_of) if r.llf_value >= threshold]

    def average_llf_as_of(self, as_of: dt.date) -> Optional[float]:
        current = self.all_current_as_of(as_of)
        if not current:
            return None
        return round(sum(r.llf_value for r in current) / len(current), 5)

    def portfolio_loss_uplift_pct(self, as_of: dt.date) -> Optional[float]:
        avg = self.average_llf_as_of(as_of)
        return None if avg is None else round((avg - 1.0) * 100, 4)

    def llf_register_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_cur = len(self.all_current_as_of(as_of))
        avg = self.average_llf_as_of(as_of)
        avg_str = str(avg) if avg is not None else "n/a"
        return (
            "LLF Register (" + str(as_of) + "): " + str(n) + " records "
            + "(" + str(n_cur) + " current). Avg LLF: " + avg_str + "."
        )
