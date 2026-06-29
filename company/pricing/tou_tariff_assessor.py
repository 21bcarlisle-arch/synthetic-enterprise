from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class DemandShapeClass(str, Enum):
    OVERNIGHT_HEAVY = "overnight_heavy"
    STANDARD_FLAT = "standard_flat"
    PEAK_HEAVY = "peak_heavy"
    WINTER_HEAVY = "winter_heavy"

_SHAPE_FRACTIONS: dict = {}
_SHAPE_FRACTIONS["overnight_heavy"] = {"overnight": 0.90, "standard": 0.08, "peak": 0.02}
_SHAPE_FRACTIONS["standard_flat"]   = {"overnight": 0.20, "standard": 0.60, "peak": 0.20}
_SHAPE_FRACTIONS["peak_heavy"]      = {"overnight": 0.15, "standard": 0.60, "peak": 0.25}
_SHAPE_FRACTIONS["winter_heavy"]    = {"overnight": 0.25, "standard": 0.55, "peak": 0.20}

WHOLESALE_BAND_NORMAL_GBP_MWH: dict = {"overnight": 35.0, "standard": 42.0, "peak": 65.0}
WHOLESALE_BAND_CRISIS_GBP_MWH: dict = {"overnight": 280.0, "standard": 380.0, "peak": 520.0}
DEFAULT_FLAT_RATE_P_PER_KWH: float = 28.5
DEFAULT_TOU_OVERNIGHT_P_PER_KWH: float = 7.5
DEFAULT_TOU_STANDARD_P_PER_KWH: float = 28.5
DEFAULT_TOU_PEAK_P_PER_KWH: float = 45.0


@dataclass(frozen=True)
class WholesaleBandRates:
    overnight_gbp_mwh: float
    standard_gbp_mwh: float
    peak_gbp_mwh: float

    @classmethod
    def normal(cls) -> "WholesaleBandRates":
        b = WHOLESALE_BAND_NORMAL_GBP_MWH
        return cls(overnight_gbp_mwh=b["overnight"], standard_gbp_mwh=b["standard"], peak_gbp_mwh=b["peak"])

    @classmethod
    def crisis(cls) -> "WholesaleBandRates":
        b = WHOLESALE_BAND_CRISIS_GBP_MWH
        return cls(overnight_gbp_mwh=b["overnight"], standard_gbp_mwh=b["standard"], peak_gbp_mwh=b["peak"])


@dataclass(frozen=True)
class ToURateStructure:
    overnight_p_per_kwh: float
    standard_p_per_kwh: float
    peak_p_per_kwh: float

    @classmethod
    def default(cls) -> "ToURateStructure":
        return cls(
            overnight_p_per_kwh=DEFAULT_TOU_OVERNIGHT_P_PER_KWH,
            standard_p_per_kwh=DEFAULT_TOU_STANDARD_P_PER_KWH,
            peak_p_per_kwh=DEFAULT_TOU_PEAK_P_PER_KWH,
        )


@dataclass(frozen=True)
class ToUProfitabilityComparison:
    account_id: str
    year: int
    shape_class: DemandShapeClass
    annual_kwh: float
    flat_rate_p_per_kwh: float
    flat_revenue_gbp: float
    wholesale_cost_gbp: float
    flat_margin_gbp: float
    tou_overnight_rate_p_per_kwh: float
    tou_standard_rate_p_per_kwh: float
    tou_peak_rate_p_per_kwh: float
    tou_revenue_gbp: float
    tou_margin_gbp: float

    @property
    def margin_delta_gbp(self) -> float:
        return round(self.tou_margin_gbp - self.flat_margin_gbp, 2)

    @property
    def is_tou_beneficial_for_supplier(self) -> bool:
        return self.tou_margin_gbp > self.flat_margin_gbp

    @property
    def customer_saving_gbp(self) -> float:
        return round(self.flat_revenue_gbp - self.tou_revenue_gbp, 2)

    @property
    def flat_margin_pct(self) -> float:
        if self.flat_revenue_gbp == 0:
            return 0.0
        return round(self.flat_margin_gbp / self.flat_revenue_gbp * 100, 2)

    @property
    def tou_margin_pct(self) -> float:
        if self.tou_revenue_gbp == 0:
            return 0.0
        return round(self.tou_margin_gbp / self.tou_revenue_gbp * 100, 2)

    @property
    def supplier_preferred_tariff(self) -> str:
        return "tou" if self.is_tou_beneficial_for_supplier else "flat"


class ToUTariffAssessorBook:
    """Records ToU vs flat tariff profitability comparisons."""

    def __init__(self) -> None:
        self._comparisons: list = []

    def assess(
        self,
        account_id: str,
        year: int,
        annual_kwh: float,
        shape_class: DemandShapeClass,
        flat_rate_p_per_kwh: float,
        wholesale_band_rates: WholesaleBandRates,
        tou_rates: Optional[ToURateStructure] = None,
    ) -> ToUProfitabilityComparison:
        if tou_rates is None:
            tou_rates = ToURateStructure.default()
        fractions = _SHAPE_FRACTIONS[shape_class.value]
        overnight_kwh = annual_kwh * fractions["overnight"]
        standard_kwh = annual_kwh * fractions["standard"]
        peak_kwh = annual_kwh * fractions["peak"]
        wholesale_cost_gbp = round(
            overnight_kwh * wholesale_band_rates.overnight_gbp_mwh / 1000.0
            + standard_kwh * wholesale_band_rates.standard_gbp_mwh / 1000.0
            + peak_kwh * wholesale_band_rates.peak_gbp_mwh / 1000.0,
            2,
        )
        flat_revenue_gbp = round(annual_kwh * flat_rate_p_per_kwh / 100.0, 2)
        flat_margin_gbp = round(flat_revenue_gbp - wholesale_cost_gbp, 2)
        tou_revenue_gbp = round(
            overnight_kwh * tou_rates.overnight_p_per_kwh / 100.0
            + standard_kwh * tou_rates.standard_p_per_kwh / 100.0
            + peak_kwh * tou_rates.peak_p_per_kwh / 100.0,
            2,
        )
        tou_margin_gbp = round(tou_revenue_gbp - wholesale_cost_gbp, 2)
        comparison = ToUProfitabilityComparison(
            account_id=account_id, year=year, shape_class=shape_class,
            annual_kwh=annual_kwh, flat_rate_p_per_kwh=flat_rate_p_per_kwh,
            flat_revenue_gbp=flat_revenue_gbp, wholesale_cost_gbp=wholesale_cost_gbp,
            flat_margin_gbp=flat_margin_gbp,
            tou_overnight_rate_p_per_kwh=tou_rates.overnight_p_per_kwh,
            tou_standard_rate_p_per_kwh=tou_rates.standard_p_per_kwh,
            tou_peak_rate_p_per_kwh=tou_rates.peak_p_per_kwh,
            tou_revenue_gbp=tou_revenue_gbp, tou_margin_gbp=tou_margin_gbp,
        )
        self._comparisons.append(comparison)
        return comparison

    def assessments_for(self, account_id: str) -> list:
        return [c for c in self._comparisons if c.account_id == account_id]

    def overnight_heavy_assessments(self, year=None) -> list:
        records = self._for_year(year)
        return [c for c in records if c.shape_class == DemandShapeClass.OVERNIGHT_HEAVY]

    def flat_preferred_accounts(self, year=None) -> list:
        return [c for c in self._for_year(year) if not c.is_tou_beneficial_for_supplier]

    def tou_preferred_accounts(self, year=None) -> list:
        return [c for c in self._for_year(year) if c.is_tou_beneficial_for_supplier]

    def total_customer_saving_gbp(self, year=None) -> float:
        return round(sum(c.customer_saving_gbp for c in self._for_year(year)), 2)

    def portfolio_summary(self, year=None) -> dict:
        records = self._for_year(year)
        if not records:
            return {"accounts_assessed": 0}
        return {
            "accounts_assessed": len(records),
            "flat_preferred_count": len(self.flat_preferred_accounts(year)),
            "tou_preferred_count": len(self.tou_preferred_accounts(year)),
            "overnight_heavy_count": len(self.overnight_heavy_assessments(year)),
            "total_customer_saving_if_all_tou_gbp": self.total_customer_saving_gbp(year),
        }

    def _for_year(self, year) -> list:
        if year is None:
            return list(self._comparisons)
        return [c for c in self._comparisons if c.year == year]
