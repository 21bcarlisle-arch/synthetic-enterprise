"""Renewable Obligation Certificate (ROC) Ledger (Phase FH).

The Renewables Obligation (RO) requires electricity suppliers to source a
specified fraction of their electricity from eligible renewable sources
(expressed as 'ROCs per MWh supplied').

Key mechanics:
- Each year, Ofgem publishes the Obligation Level (ROC/MWh)
- Suppliers must surrender ROCs (or pay buy-out price) by 1 September
- ROCs are issued by Ofgem to generators; purchased by suppliers on RECS market
- Buy-out price: set annually by Ofgem (e.g. £54.35/ROC for 2023-24)
- Late payment: 30-day interest at base rate + 3%
- Mutualisation: any unpaid shortfall redistributed to compliant suppliers

The RO closed to new generators from 31 March 2017 but obligation continues
until 2037 (for grandfathered generators with 20-year ROC accreditations).

Observability: ROC certificates are issued by Ofgem (public register).
Buy-out prices are published annually. Obligation levels are published.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


_ROC_OBLIGATION_LEVEL: Dict[int, float] = {
    2016: 0.317,   # ROC/MWh
    2017: 0.334,
    2018: 0.342,
    2019: 0.351,
    2020: 0.358,
    2021: 0.364,
    2022: 0.370,
    2023: 0.376,
    2024: 0.382,
    2025: 0.389,
}

_ROC_BUY_OUT_PRICE_GBP: Dict[int, float] = {
    2016: 43.30,
    2017: 44.77,
    2018: 46.43,
    2019: 47.22,
    2020: 48.78,
    2021: 50.80,
    2022: 52.88,
    2023: 54.35,
    2024: 56.19,
    2025: 58.10,
}


class ROCObligationStatus(str, Enum):
    OPEN = "open"
    SURRENDERED = "surrendered"
    BUY_OUT_PAID = "buy_out_paid"
    PARTIALLY_SURRENDERED = "partially_surrendered"
    DEFAULTED = "defaulted"


@dataclass(frozen=True)
class ROCObligationRecord:
    obligation_year: int
    total_mwh_supplied: float
    rocs_required: float            # mwh * obligation_level
    rocs_surrendered: float = 0.0
    buy_out_paid_gbp: float = 0.0
    status: ROCObligationStatus = ROCObligationStatus.OPEN

    @property
    def rocs_shortfall(self) -> float:
        return max(0.0, self.rocs_required - self.rocs_surrendered)

    @property
    def buy_out_cost_for_shortfall(self) -> float:
        price = _ROC_BUY_OUT_PRICE_GBP.get(self.obligation_year, 50.0)
        return self.rocs_shortfall * price

    @property
    def is_fully_compliant(self) -> bool:
        return self.rocs_shortfall <= 0.01   # small tolerance

    @property
    def compliance_pct(self) -> float:
        if self.rocs_required <= 0:
            return 100.0
        return 100.0 * self.rocs_surrendered / self.rocs_required

    def obligation_summary(self) -> str:
        return (
            "ROC " + str(self.obligation_year) + ": "
            "required=" + str(round(self.rocs_required, 1)) + " "
            "surrendered=" + str(round(self.rocs_surrendered, 1)) + " "
            "compliance=" + str(round(self.compliance_pct, 1)) + "% "
            "[" + self.status.value + "]"
        )


class ROCLedger:

    def __init__(self) -> None:
        self._obligations: List[ROCObligationRecord] = []

    def create_obligation(
        self, year: int, total_mwh_supplied: float
    ) -> ROCObligationRecord:
        obligation_level = _ROC_OBLIGATION_LEVEL.get(year, 0.35)
        roc = ROCObligationRecord(
            obligation_year=year,
            total_mwh_supplied=total_mwh_supplied,
            rocs_required=total_mwh_supplied * obligation_level,
        )
        self._obligations.append(roc)
        return roc

    def surrender_rocs(
        self, year: int, rocs_surrendered: float
    ) -> Optional[ROCObligationRecord]:
        for i, o in enumerate(self._obligations):
            if o.obligation_year == year:
                status = (
                    ROCObligationStatus.SURRENDERED
                    if rocs_surrendered >= o.rocs_required - 0.01
                    else ROCObligationStatus.PARTIALLY_SURRENDERED
                )
                updated = ROCObligationRecord(
                    obligation_year=o.obligation_year,
                    total_mwh_supplied=o.total_mwh_supplied,
                    rocs_required=o.rocs_required,
                    rocs_surrendered=rocs_surrendered,
                    buy_out_paid_gbp=o.buy_out_paid_gbp,
                    status=status,
                )
                self._obligations[i] = updated
                return updated
        return None

    def obligation_for_year(self, year: int) -> Optional[ROCObligationRecord]:
        for o in self._obligations:
            if o.obligation_year == year:
                return o
        return None

    def non_compliant_years(self) -> List[ROCObligationRecord]:
        return [
            o for o in self._obligations
            if not o.is_fully_compliant and o.status != ROCObligationStatus.OPEN
        ]

    def total_buy_out_exposure_gbp(self) -> float:
        return sum(o.buy_out_cost_for_shortfall for o in self._obligations)

    def roc_ledger_summary(self) -> str:
        n = len(self._obligations)
        n_compliant = sum(1 for o in self._obligations if o.is_fully_compliant)
        exposure = self.total_buy_out_exposure_gbp()
        return (
            "ROC Ledger: " + str(n) + " obligation years. "
            "Compliant: " + str(n_compliant) + ". "
            "Total buy-out exposure: GBP" + str(round(exposure, 0)) + "."
        )
