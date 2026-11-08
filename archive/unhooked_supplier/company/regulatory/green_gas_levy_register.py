"""Green Gas Levy (GGL) Register (Phase FV).

The GGL (Green Gas Levy Regulations 2021, SI 2021/1375) funds the
Green Gas Support Scheme (GGSS) — the biomethane injection successor
to the Renewable Heat Incentive (RHI) for domestic/commercial heat.

Gas suppliers pay quarterly:
  levy = gas_meter_count × rate_gbp_per_meter_per_day × days_in_quarter

Rate published annually by DESNZ via Statutory Instrument (Levy Year
runs November to October). Observable: company reads DESNZ SI; knows
its own active gas meter count; calculates obligation from those inputs.

GGL came into force 30 November 2021. Very small absolute cost versus
ROC, CfD, or WHD — but an annually rising obligation that sits on
every gas supply point. All licensed gas suppliers must pay (no SME
or volume-based exemption for standard supply).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

# Approximate rates (GBP/meter/day) calibrated to DESNZ Statutory Instruments.
# Levy Year runs Nov–Oct; rates rise each LY as the GGSS scheme scales.
# LY1 (Nov 2021 – Oct 2022): initial year, small scheme volume.
# Rates ~0.33–0.70 GBP/meter/year across 2022-2025 (moderate but growing).
_GGL_RATE_GBP_PER_METER_PER_DAY: Dict[int, float] = {
    2022: 0.000893,   # LY1 (~£0.33/meter/year)
    2023: 0.001178,   # LY2 (~£0.43/meter/year)
    2024: 0.001507,   # LY3 (~£0.55/meter/year)
    2025: 0.001918,   # LY4 (~£0.70/meter/year, DESNZ estimate)
}

# GGL started 30 November 2021 (first Q4 2021 obligation is partial: 32 days)
_GGL_START_DATE = dt.date(2021, 11, 30)

# Standard calendar quarter end dates (month, day)
_QUARTER_END: Dict[int, tuple] = {
    1: (3, 31),
    2: (6, 30),
    3: (9, 30),
    4: (12, 31),
}

# Standard quarter lengths (non-leap year defaults; caller may override for
# leap years or the first partial quarter in Q4 2021 = 32 days)
_QUARTER_DAYS_DEFAULT: Dict[int, int] = {1: 90, 2: 91, 3: 92, 4: 92}

_PAYMENT_DAYS = 28  # days after quarter end for quarterly levy settlement


class GGLPaymentStatus(str, Enum):
    ACCRUED = "accrued"    # recorded, not yet paid
    PAID = "paid"          # payment confirmed
    OVERDUE = "overdue"    # past payment_due_date and unpaid


@dataclass(frozen=True)
class GGLQuarterlyObligation:
    year: int
    quarter: int                          # 1-4 calendar quarter
    gas_meter_count: int                  # active gas supply points (company observable)
    rate_gbp_per_meter_per_day: float     # from DESNZ SI publication
    days_in_quarter: int                  # may be non-standard for Q4 2021 (32 days)

    @property
    def total_levy_gbp(self) -> float:
        return self.gas_meter_count * self.rate_gbp_per_meter_per_day * self.days_in_quarter

    @property
    def quarter_label(self) -> str:
        names = {1: "Jan-Mar", 2: "Apr-Jun", 3: "Jul-Sep", 4: "Oct-Dec"}
        return f"{self.year} Q{self.quarter} ({names[self.quarter]})"

    @property
    def payment_due_date(self) -> dt.date:
        month, day = _QUARTER_END[self.quarter]
        qend = dt.date(self.year, month, day)
        return qend + dt.timedelta(days=_PAYMENT_DAYS)

    def is_overdue(self, as_of: dt.date) -> bool:
        return as_of > self.payment_due_date

    def obligation_summary(self) -> str:
        return (
            f"GGL {self.quarter_label}: {self.gas_meter_count} meters "
            f"x {self.rate_gbp_per_meter_per_day * 100:.4f}p/meter/day "
            f"x {self.days_in_quarter}d = £{self.total_levy_gbp:.4f}"
        )


class GreenGasLevyRegister:

    def __init__(self) -> None:
        self._obligations: List[GGLQuarterlyObligation] = []
        self._paid_keys: set = set()   # (year, quarter) pairs

    def record_obligation(
        self,
        year: int,
        quarter: int,
        gas_meter_count: int,
        rate_gbp_per_meter_per_day: Optional[float] = None,
        days_in_quarter: Optional[int] = None,
    ) -> GGLQuarterlyObligation:
        if year < 2021 or (year == 2021 and quarter < 4):
            raise ValueError(
                f"GGL did not exist before Q4 2021; cannot record {year} Q{quarter}"
            )
        rate = rate_gbp_per_meter_per_day
        if rate is None:
            rate = _GGL_RATE_GBP_PER_METER_PER_DAY.get(
                year, _GGL_RATE_GBP_PER_METER_PER_DAY[2025]
            )
        days = days_in_quarter if days_in_quarter is not None else _QUARTER_DAYS_DEFAULT[quarter]
        ob = GGLQuarterlyObligation(
            year=year,
            quarter=quarter,
            gas_meter_count=gas_meter_count,
            rate_gbp_per_meter_per_day=rate,
            days_in_quarter=days,
        )
        self._obligations.append(ob)
        return ob

    def mark_paid(self, year: int, quarter: int) -> None:
        self._paid_keys.add((year, quarter))

    def is_paid(self, year: int, quarter: int) -> bool:
        return (year, quarter) in self._paid_keys

    def obligations_for_year(self, year: int) -> List[GGLQuarterlyObligation]:
        return [o for o in self._obligations if o.year == year]

    def unpaid_obligations(self) -> List[GGLQuarterlyObligation]:
        return [o for o in self._obligations if not self.is_paid(o.year, o.quarter)]

    def overdue_obligations(self, as_of: dt.date) -> List[GGLQuarterlyObligation]:
        return [o for o in self.unpaid_obligations() if o.is_overdue(as_of)]

    def total_levy_paid_gbp(self) -> float:
        return sum(
            o.total_levy_gbp for o in self._obligations
            if self.is_paid(o.year, o.quarter)
        )

    def total_levy_accrued_gbp(self) -> float:
        return sum(o.total_levy_gbp for o in self.unpaid_obligations())

    def annual_levy_gbp(self, year: int) -> float:
        return sum(o.total_levy_gbp for o in self.obligations_for_year(year))

    def ggl_summary(self, as_of: dt.date) -> str:
        n = len(self._obligations)
        n_paid = sum(1 for o in self._obligations if self.is_paid(o.year, o.quarter))
        n_overdue = len(self.overdue_obligations(as_of))
        total = sum(o.total_levy_gbp for o in self._obligations)
        return (
            f"GGL Register ({as_of}): {n} obligations ({n_paid} paid, "
            f"{n_overdue} overdue). Total: £{total:.4f}. "
            f"Accrued: £{self.total_levy_accrued_gbp():.4f}."
        )
