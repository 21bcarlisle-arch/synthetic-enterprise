from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class AnnualStatement:
    """Annual energy statement (SLC 31B) for a domestic customer."""
    customer_id: str
    year: int
    consumption_kwh: float
    total_cost_gbp: float
    effective_unit_rate_ppm: float     # pence per kWh (average effective)
    sc_ppd: float                      # standing charge pence per day
    tariff_name: str
    tariff_type: str                   # "fixed" | "variable"
    prev_year_consumption_kwh: Optional[float] = None
    consumption_change_pct: Optional[float] = None
    market_avg_cost_gbp: Optional[float] = None
    estimated_saving_gbp: Optional[float] = None   # negative = customer already paying less


def _consumption_change(current: float, prev: Optional[float]) -> Optional[float]:
    if prev is None or prev == 0:
        return None
    return round((current - prev) / prev * 100.0, 1)


def _estimated_saving(total_cost: float, market_avg: Optional[float]) -> Optional[float]:
    if market_avg is None:
        return None
    return round(market_avg - total_cost, 2)


@dataclass
class AnnualStatementBook:
    """Issues and stores annual energy statements for the portfolio."""

    _statements: Dict[Tuple[str, int], AnnualStatement] = field(default_factory=dict)

    def generate(
        self,
        customer_id: str,
        year: int,
        consumption_kwh: float,
        total_cost_gbp: float,
        effective_unit_rate_ppm: float,
        sc_ppd: float,
        tariff_name: str,
        tariff_type: str,
        prev_year_consumption_kwh: Optional[float] = None,
        market_avg_cost_gbp: Optional[float] = None,
    ) -> AnnualStatement:
        change_pct = _consumption_change(consumption_kwh, prev_year_consumption_kwh)
        saving = _estimated_saving(total_cost_gbp, market_avg_cost_gbp)
        stmt = AnnualStatement(
            customer_id=customer_id,
            year=year,
            consumption_kwh=consumption_kwh,
            total_cost_gbp=total_cost_gbp,
            effective_unit_rate_ppm=effective_unit_rate_ppm,
            sc_ppd=sc_ppd,
            tariff_name=tariff_name,
            tariff_type=tariff_type,
            prev_year_consumption_kwh=prev_year_consumption_kwh,
            consumption_change_pct=change_pct,
            market_avg_cost_gbp=market_avg_cost_gbp,
            estimated_saving_gbp=saving,
        )
        self._statements[(customer_id, year)] = stmt
        return stmt

    def get(self, customer_id: str, year: int) -> Optional[AnnualStatement]:
        return self._statements.get((customer_id, year))

    def statements_for_customer(self, customer_id: str) -> List[AnnualStatement]:
        return [s for (cid, _), s in self._statements.items() if cid == customer_id]

    def issued_for_year(self, year: int) -> List[str]:
        """Customer IDs that have received a statement for the given year."""
        return [cid for (cid, yr) in self._statements if yr == year]

    def overdue(self, as_of: date, all_customer_ids: List[str]) -> List[str]:
        """Customers missing a statement for the previous calendar year (SLC 31B)."""
        required_year = as_of.year - 1
        issued = set(self.issued_for_year(required_year))
        return [cid for cid in all_customer_ids if cid not in issued]

    def summary(self, year: int) -> dict:
        stmts = [s for (_, yr), s in self._statements.items() if yr == year]
        n = len(stmts)
        if n == 0:
            return {"year": year, "total_issued": 0, "avg_consumption_kwh": 0.0, "avg_cost_gbp": 0.0}
        return {
            "year": year,
            "total_issued": n,
            "avg_consumption_kwh": round(sum(s.consumption_kwh for s in stmts) / n, 1),
            "avg_cost_gbp": round(sum(s.total_cost_gbp for s in stmts) / n, 2),
        }
