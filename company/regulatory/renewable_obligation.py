from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# THE SAME TWO PUBLISHED SERIES `roc_ledger` reads, from the same commons. Until
# 2026-08-19 this module carried a THIRD set of values for them: buy-out prices that were
# the published series shifted and perturbed (2022-23 as GBP54.35 against a published
# GBP52.88), and obligation levels around 0.09 ROC/MWh — roughly a fifth of the published
# 0.47-0.49, a units-looking error that no control could name because no control
# enumerated this module. Two tables of law cannot disagree; the readings may.
from company.regulatory.ro_commons import (  # noqa: E402
    BUY_OUT_PRICE_GBP_PER_ROC as _BUYOUT_PRICE_GBP_PER_ROC,
    OBLIGATION_LEVEL_ROC_PER_MWH as _OBLIGATION_LEVEL_ROC_PER_MWH,
)


class ROSettlementMethod(str, Enum):
    SURRENDER_ROC = "surrender_roc"
    BUYOUT = "buyout"
    MIXED = "mixed"


@dataclass(frozen=True)
class ROAnnualReturn:
    obligation_year: int
    electricity_supplied_mwh: float
    rocs_surrendered: float
    rocs_purchased: float
    settlement_method: ROSettlementMethod

    @property
    def obligation_level(self) -> float:
        return _OBLIGATION_LEVEL_ROC_PER_MWH.get(self.obligation_year, 0.10)

    @property
    def obligation_rocs(self) -> float:
        return round(self.electricity_supplied_mwh * self.obligation_level, 2)

    @property
    def shortfall_rocs(self) -> float:
        return max(0.0, round(self.obligation_rocs - self.rocs_surrendered, 2))

    @property
    def buyout_cost_gbp(self) -> float:
        buyout_price = _BUYOUT_PRICE_GBP_PER_ROC.get(self.obligation_year, 55.0)
        return round(self.shortfall_rocs * buyout_price, 2)

    @property
    def roc_cost_gbp(self) -> float:
        return round(self.rocs_purchased * 3.5, 2)

    @property
    def total_ro_cost_gbp(self) -> float:
        return round(self.buyout_cost_gbp + self.roc_cost_gbp, 2)

    @property
    def is_compliant(self) -> bool:
        return self.shortfall_rocs == 0.0


class RenewableObligationBook:
    def __init__(self) -> None:
        self._returns: list[ROAnnualReturn] = []

    def file_return(self, ro_return: ROAnnualReturn) -> ROAnnualReturn:
        self._returns.append(ro_return)
        return ro_return

    def return_for_year(self, year: int) -> Optional[ROAnnualReturn]:
        for r in self._returns:
            if r.obligation_year == year:
                return r
        return None

    def compliance_record(self) -> list[dict]:
        return [
            {
                "year": r.obligation_year,
                "obligation_rocs": r.obligation_rocs,
                "surrendered_rocs": r.rocs_surrendered,
                "shortfall_rocs": r.shortfall_rocs,
                "buyout_cost_gbp": r.buyout_cost_gbp,
                "total_ro_cost_gbp": r.total_ro_cost_gbp,
                "compliant": r.is_compliant,
            }
            for r in sorted(self._returns, key=lambda r: r.obligation_year)
        ]

    def total_buyout_spend_gbp(self) -> float:
        return round(sum(r.buyout_cost_gbp for r in self._returns), 2)

    def non_compliant_years(self) -> list[int]:
        return [r.obligation_year for r in self._returns if not r.is_compliant]

    def ro_summary(self) -> dict:
        if not self._returns:
            return {"years_filed": 0, "total_buyout_gbp": 0.0, "non_compliant_years": []}
        return {
            "years_filed": len(self._returns),
            "total_buyout_gbp": self.total_buyout_spend_gbp(),
            "non_compliant_years": self.non_compliant_years(),
            "total_ro_cost_gbp": round(sum(r.total_ro_cost_gbp for r in self._returns), 2),
        }
