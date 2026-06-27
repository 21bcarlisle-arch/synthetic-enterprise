"""VAT book: UK energy VAT at 5% domestic / 20% business with quarterly returns."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class VATRateCategory(str, Enum):
    DOMESTIC_REDUCED = "domestic_reduced"   # 5%: residential / qualifying SME
    STANDARD = "standard"                   # 20%: I&C / non-qualifying business
    ZERO = "zero"                           # 0%: charity / severely disabled (SLC exception)
    EXEMPT = "exempt"                       # rare: e.g. certain financial charges


_VAT_RATES: Dict[VATRateCategory, float] = {
    VATRateCategory.DOMESTIC_REDUCED: 0.05,
    VATRateCategory.STANDARD: 0.20,
    VATRateCategory.ZERO: 0.00,
    VATRateCategory.EXEMPT: 0.00,
}

# SME qualifying threshold (HMRC concession: domestic rate if <= 33kWh/day elec or 145kWh/day gas)
SME_ELEC_THRESHOLD_KWH_PER_DAY = 33.0
SME_GAS_THRESHOLD_KWH_PER_DAY = 145.0


def classify_vat_category(
    is_residential: bool,
    daily_consumption_kwh: Optional[float] = None,
) -> VATRateCategory:
    if is_residential:
        return VATRateCategory.DOMESTIC_REDUCED
    if daily_consumption_kwh is not None and daily_consumption_kwh <= max(
        SME_ELEC_THRESHOLD_KWH_PER_DAY, SME_GAS_THRESHOLD_KWH_PER_DAY
    ):
        return VATRateCategory.DOMESTIC_REDUCED
    return VATRateCategory.STANDARD


@dataclass(frozen=True)
class VATTransaction:
    account_id: str
    transaction_date: dt.date
    net_amount_gbp: float
    vat_category: VATRateCategory

    @property
    def vat_rate(self) -> float:
        return _VAT_RATES[self.vat_category]

    @property
    def vat_gbp(self) -> float:
        return round(self.net_amount_gbp * self.vat_rate, 2)

    @property
    def gross_amount_gbp(self) -> float:
        return round(self.net_amount_gbp + self.vat_gbp, 2)


@dataclass(frozen=True)
class VATQuarterlyReturn:
    period_start: dt.date
    period_end: dt.date
    output_vat_gbp: float   # collected from customers
    input_vat_gbp: float    # paid on business purchases (simplified: ~8% of output for suppliers)

    @property
    def net_vat_due_gbp(self) -> float:
        return round(self.output_vat_gbp - self.input_vat_gbp, 2)

    @property
    def is_repayment(self) -> bool:
        return self.net_vat_due_gbp < 0


def _quarter_boundaries(year: int, quarter: int) -> Tuple[dt.date, dt.date]:
    start_month = (quarter - 1) * 3 + 1
    start = dt.date(year, start_month, 1)
    end_month = start_month + 2
    end_year = year
    if end_month > 12:
        end_month -= 12
        end_year += 1
    import calendar
    last_day = calendar.monthrange(end_year, end_month)[1]
    end = dt.date(end_year, end_month, last_day)
    return start, end


class VATBook:
    """Tracks output VAT on energy sales and prepares quarterly returns.

    Real data:
    - Domestic gas/electricity: 5% reduced rate since Finance Act 1994 (EC Directive)
    - Business energy: 20% standard rate
    - SME qualifying threshold: <=33 kWh/day electricity or <=145 kWh/day gas -> domestic rate
    - Quarterly VAT returns to HMRC; payment within 1 month + 7 days of quarter end
    - 2022: billing errors (wrong rate applied) caused significant customer refunds
    - Input VAT on purchases: ~5-10% of output VAT for a typical supplier
    """

    def __init__(self) -> None:
        self._transactions: List[VATTransaction] = []

    def record_transaction(self, txn: VATTransaction) -> VATTransaction:
        self._transactions.append(txn)
        return txn

    def transactions_for_period(self, start: dt.date, end: dt.date) -> List[VATTransaction]:
        return [t for t in self._transactions if start <= t.transaction_date <= end]

    def quarterly_return(
        self,
        year: int,
        quarter: int,
        input_vat_estimate_pct: float = 0.08,
    ) -> VATQuarterlyReturn:
        start, end = _quarter_boundaries(year, quarter)
        period_txns = self.transactions_for_period(start, end)
        output_vat = round(sum(t.vat_gbp for t in period_txns), 2)
        input_vat = round(output_vat * input_vat_estimate_pct, 2)
        return VATQuarterlyReturn(
            period_start=start,
            period_end=end,
            output_vat_gbp=output_vat,
            input_vat_gbp=input_vat,
        )

    def total_output_vat_gbp(self, year: Optional[int] = None) -> float:
        txns = self._transactions
        if year is not None:
            txns = [t for t in txns if t.transaction_date.year == year]
        return round(sum(t.vat_gbp for t in txns), 2)

    def transactions_by_category(self) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for t in self._transactions:
            k = t.vat_category.value
            result[k] = result.get(k, 0) + 1
        return result

    def vat_summary(self) -> dict:
        return {
            "total_transactions": len(self._transactions),
            "total_output_vat_gbp": self.total_output_vat_gbp(),
            "by_category": self.transactions_by_category(),
        }
