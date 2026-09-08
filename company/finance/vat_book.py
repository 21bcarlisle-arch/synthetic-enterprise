"""VAT book: UK energy VAT at 5% domestic / 20% business with quarterly returns."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from company.billing.dual_fuel_bill import SME_VAT_DE_MINIMIS_KWH_PER_DAY


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

#: THE DE MINIMIS LIMITS, DERIVED FROM THE COMMONS RATHER THAN RESTATED.
#: These were literals here — 33.0 and 145.0 — while
#: `docs/domain_artefact_library/regulatory/vat_fuel_and_power_de_minimis.json` held the same two
#: figures as the published law, and `company/billing/dual_fuel_bill` already read them from it.
#: Two homes for one legal requirement, which is the shape CLAUDE.md names as this project's most
#: expensive recurring defect. Found by `tools/published_row_scalar_census.py`, which ranks a
#: module-level scalar against every row of the commons: both literals came back as
#: specificity-1, units-agreeing collisions with the artefact — i.e. exact copies of published law.
#:
#: IMPORTED, NOT RE-READ. `dual_fuel_bill.SME_VAT_DE_MINIMIS_KWH_PER_DAY` is already a public
#: commons load that raises rather than failing open. A second loader against the same file would
#: be a second thing to keep in step, which is the defect one level up.
SME_ELEC_THRESHOLD_KWH_PER_DAY = SME_VAT_DE_MINIMIS_KWH_PER_DAY["electricity"]
SME_GAS_THRESHOLD_KWH_PER_DAY = SME_VAT_DE_MINIMIS_KWH_PER_DAY["gas"]


def classify_vat_category(
    is_residential: bool,
    daily_consumption_kwh: Optional[float] = None,
    fuel: Optional[str] = None,
) -> VATRateCategory:
    """Which VAT band a supply falls in. `fuel` is "electricity" or "gas".

    THE FUEL IS NOT OPTIONAL DETAIL, IT IS HALF THE RULE. Gas is 145 kWh/day and electricity 33
    — a factor of 4.39 — so between those two numbers the same consumption is reduced-rated for
    one fuel and standard-rated for the other. This function used to take `max()` of the two
    limits and apply it to everything, which silently answered every business electricity supply
    in the 33–145 band with GAS's rule: reduced-rated where the law says standard. That is the
    same defect `dual_fuel_bill._sme_vat_rate` carried until 2026-08-31, mirrored, and it is why
    the artefact says in its own text that the limits are NOT the same for the two fuels.

    WITH NO FUEL NAMED IT REFUSES RATHER THAN GUESSES — but only where the fuel actually decides
    the answer. Below the smallest limit and above the largest, every fuel agrees and the question
    is answerable without knowing which one it is; inside the band they disagree and there is no
    honest default, so it raises with the reason named. Picking a side there is how an invented
    reading gets read as the law.
    """
    if is_residential:
        # Unconditional: the artefact's `domestic_is_unconditional` — genuine domestic use is
        # reduced-rated with no quantity test at all. A de minimis check applied to a domestic
        # account is not redundant, it is a different rule.
        return VATRateCategory.DOMESTIC_REDUCED
    if daily_consumption_kwh is None:
        return VATRateCategory.STANDARD
    if fuel is not None:
        if fuel not in SME_VAT_DE_MINIMIS_KWH_PER_DAY:
            raise ValueError(
                f"no published de minimis limit for fuel {fuel!r}; VAT Notice 701/19 states one "
                f"for {sorted(SME_VAT_DE_MINIMIS_KWH_PER_DAY)} and this book does not invent others"
            )
        limit = SME_VAT_DE_MINIMIS_KWH_PER_DAY[fuel]
        return (
            VATRateCategory.DOMESTIC_REDUCED
            if daily_consumption_kwh <= limit
            else VATRateCategory.STANDARD
        )
    limits = SME_VAT_DE_MINIMIS_KWH_PER_DAY.values()
    if daily_consumption_kwh <= min(limits):
        return VATRateCategory.DOMESTIC_REDUCED
    if daily_consumption_kwh > max(limits):
        return VATRateCategory.STANDARD
    raise ValueError(
        f"{daily_consumption_kwh} kWh/day falls between the per-fuel de minimis limits "
        f"({SME_VAT_DE_MINIMIS_KWH_PER_DAY}), where the two fuels take opposite VAT rates, and no "
        "fuel was named. Pass `fuel=` — there is no answer here that is right for both."
    )


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
