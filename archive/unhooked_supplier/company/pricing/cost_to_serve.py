from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CustomerSegment(str, Enum):
    RESIDENTIAL_CREDIT = "residential_credit"
    RESIDENTIAL_PPM = "residential_ppm"
    SME = "sme"
    IC = "i_and_c"


# Additional cost-to-serve components beyond commodity:
# customer acquisition, support, billing, smart meter, bad debt
_ACQUISITION_COST_GBP: dict[CustomerSegment, float] = {
    CustomerSegment.RESIDENTIAL_CREDIT: 60.0,
    CustomerSegment.RESIDENTIAL_PPM: 45.0,
    CustomerSegment.SME: 180.0,
    CustomerSegment.IC: 1_200.0,
}
_ANNUAL_SUPPORT_COST_GBP: dict[CustomerSegment, float] = {
    CustomerSegment.RESIDENTIAL_CREDIT: 18.0,
    CustomerSegment.RESIDENTIAL_PPM: 28.0,  # more support needed
    CustomerSegment.SME: 55.0,
    CustomerSegment.IC: 320.0,
}
_ANNUAL_BILLING_COST_GBP: dict[CustomerSegment, float] = {
    CustomerSegment.RESIDENTIAL_CREDIT: 8.0,
    CustomerSegment.RESIDENTIAL_PPM: 6.0,   # no paper bill
    CustomerSegment.SME: 22.0,
    CustomerSegment.IC: 180.0,
}


@dataclass(frozen=True)
class CostToServeBreakdown:
    account_id: str
    year: int
    segment: CustomerSegment
    consumption_mwh: float

    # Commodity cost
    wholesale_cost_p_per_kwh: float

    # Non-commodity levies (p/kWh)
    cm_p_per_kwh: float
    cfd_p_per_kwh: float
    ro_p_per_kwh: float
    fit_p_per_kwh: float
    duos_p_per_kwh: float
    tnuos_p_per_kwh: float
    bsuos_p_per_kwh: float

    # Operating costs (per account per year, converted to p/kWh)
    bad_debt_provision_gbp: float = 0.0
    smart_meter_cost_gbp: float = 0.0

    @property
    def consumption_kwh(self) -> float:
        return self.consumption_mwh * 1000.0

    @property
    def levy_p_per_kwh(self) -> float:
        return round(
            self.cm_p_per_kwh + self.cfd_p_per_kwh + self.ro_p_per_kwh +
            self.fit_p_per_kwh + self.duos_p_per_kwh + self.tnuos_p_per_kwh +
            self.bsuos_p_per_kwh, 4
        )

    @property
    def total_commodity_and_levy_p_per_kwh(self) -> float:
        return round(self.wholesale_cost_p_per_kwh + self.levy_p_per_kwh, 4)

    @property
    def annual_support_cost_gbp(self) -> float:
        return _ANNUAL_SUPPORT_COST_GBP.get(self.segment, 20.0)

    @property
    def annual_billing_cost_gbp(self) -> float:
        return _ANNUAL_BILLING_COST_GBP.get(self.segment, 10.0)

    @property
    def operating_cost_gbp(self) -> float:
        return round(
            self.annual_support_cost_gbp + self.annual_billing_cost_gbp +
            self.bad_debt_provision_gbp + self.smart_meter_cost_gbp, 2
        )

    @property
    def operating_cost_p_per_kwh(self) -> float:
        if self.consumption_kwh == 0:
            return 0.0
        return round(self.operating_cost_gbp / self.consumption_kwh * 100, 4)

    @property
    def total_cost_p_per_kwh(self) -> float:
        return round(self.total_commodity_and_levy_p_per_kwh + self.operating_cost_p_per_kwh, 4)

    @property
    def levy_pct_of_total(self) -> float:
        if self.total_cost_p_per_kwh == 0:
            return 0.0
        return round(self.levy_p_per_kwh / self.total_cost_p_per_kwh * 100, 2)


class CostToServeCalculator:
    def __init__(self) -> None:
        self._breakdowns: list[CostToServeBreakdown] = []

    @staticmethod
    def acquisition_cost_gbp(segment: CustomerSegment) -> float:
        return _ACQUISITION_COST_GBP.get(segment, 60.0)

    def record(self, breakdown: CostToServeBreakdown) -> CostToServeBreakdown:
        self._breakdowns.append(breakdown)
        return breakdown

    def breakdown_for_account(self, account_id: str) -> list[CostToServeBreakdown]:
        return [b for b in self._breakdowns if b.account_id == account_id]

    def mean_total_cost_p_per_kwh(self, year: Optional[int] = None) -> float:
        bds = [b for b in self._breakdowns if b.year == year] if year else self._breakdowns
        if not bds:
            return 0.0
        return round(sum(b.total_cost_p_per_kwh for b in bds) / len(bds), 4)

    def high_cost_accounts(self, threshold_p_per_kwh: float = 20.0) -> list[str]:
        return [b.account_id for b in self._breakdowns
                if b.total_cost_p_per_kwh > threshold_p_per_kwh]

    def cts_summary(self, year: Optional[int] = None) -> dict:
        bds = [b for b in self._breakdowns if b.year == year] if year else self._breakdowns
        return {
            "accounts_analysed": len(bds),
            "mean_total_cost_p_per_kwh": self.mean_total_cost_p_per_kwh(year),
            "mean_levy_pct": round(sum(b.levy_pct_of_total for b in bds) / len(bds), 2) if bds else 0.0,
        }
