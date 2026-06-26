from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

_BUYOUT_PRICE_GBP_PER_ROC: dict[int, float] = {
    2016: 44.33, 2017: 45.58, 2018: 46.94, 2019: 48.78,
    2020: 50.05, 2021: 50.80, 2022: 54.35, 2023: 55.63,
    2024: 57.30, 2025: 59.06,
}
_OBLIGATION_LEVEL_ROC_PER_MWH: dict[int, float] = {
    2016: 0.0634, 2017: 0.0748, 2018: 0.0896, 2019: 0.0992,
    2020: 0.0945, 2021: 0.0965, 2022: 0.1053, 2023: 0.0930,
    2024: 0.0955, 2025: 0.0980,
}


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
