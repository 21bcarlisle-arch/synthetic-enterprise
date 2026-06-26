from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DrawdownReason(str, Enum):
    WHOLESALE_SETTLEMENT = 'wholesale_settlement'
    WORKING_CAPITAL = 'working_capital'
    BSC_CREDIT_COVER = 'bsc_credit_cover'
    SEASONAL_CASHFLOW = 'seasonal_cashflow'
    EMERGENCY = 'emergency'


@dataclass(frozen=True)
class CreditFacility:
    facility_id: str
    lender: str
    limit_gbp: float
    interest_rate_pct: float
    commitment_fee_pct: float
    maturity_date: dt.date

    @property
    def daily_commitment_fee_gbp(self) -> float:
        return round(self.limit_gbp * self.commitment_fee_pct / 100 / 365, 2)


@dataclass
class FacilityDrawdown:
    drawdown_id: str
    facility_id: str
    amount_gbp: float
    drawdown_date: dt.date
    reason: DrawdownReason
    repaid_date: Optional[dt.date] = None
    repaid_amount_gbp: Optional[float] = None

    @property
    def is_outstanding(self) -> bool:
        return self.repaid_date is None

    def interest_accrued_gbp(self, as_of: dt.date, rate_pct: float) -> float:
        if not self.is_outstanding:
            end = self.repaid_date
        else:
            end = as_of
        days = max(0, (end - self.drawdown_date).days)
        return round(self.amount_gbp * rate_pct / 100 / 365 * days, 2)


class CreditFacilityBook:
    def __init__(self) -> None:
        self._facilities: dict[str, CreditFacility] = {}
        self._drawdowns: list[FacilityDrawdown] = []
        self._next_dd = 1

    def register_facility(self, facility_id: str, lender: str, limit_gbp: float,
                           interest_rate_pct: float, commitment_fee_pct: float,
                           maturity_date: dt.date) -> CreditFacility:
        f = CreditFacility(
            facility_id=facility_id, lender=lender, limit_gbp=limit_gbp,
            interest_rate_pct=interest_rate_pct, commitment_fee_pct=commitment_fee_pct,
            maturity_date=maturity_date,
        )
        self._facilities[facility_id] = f
        return f

    def drawdown(self, facility_id: str, amount_gbp: float,
                 drawdown_date: dt.date, reason: DrawdownReason) -> FacilityDrawdown:
        facility = self._facilities[facility_id]
        outstanding = self.outstanding_balance(facility_id)
        if outstanding + amount_gbp > facility.limit_gbp:
            raise ValueError(
                f'Drawdown of {amount_gbp} would breach facility limit {facility.limit_gbp}'
            )
        dd = FacilityDrawdown(
            drawdown_id=f'DD-{self._next_dd:04d}', facility_id=facility_id,
            amount_gbp=amount_gbp, drawdown_date=drawdown_date, reason=reason,
        )
        self._next_dd += 1
        self._drawdowns.append(dd)
        return dd

    def repay(self, drawdown_id: str, repaid_date: dt.date,
              repaid_amount_gbp: Optional[float] = None) -> FacilityDrawdown:
        for dd in self._drawdowns:
            if dd.drawdown_id == drawdown_id:
                dd.repaid_date = repaid_date
                dd.repaid_amount_gbp = repaid_amount_gbp or dd.amount_gbp
                return dd
        raise KeyError(drawdown_id)

    def outstanding_balance(self, facility_id: str) -> float:
        return round(sum(dd.amount_gbp for dd in self._drawdowns
                         if dd.facility_id == facility_id and dd.is_outstanding), 2)

    def total_interest_accrued_gbp(self, as_of: dt.date) -> float:
        total = 0.0
        for dd in self._drawdowns:
            facility = self._facilities[dd.facility_id]
            total += dd.interest_accrued_gbp(as_of, facility.interest_rate_pct)
        return round(total, 2)

    def utilisation_pct(self, facility_id: str) -> float:
        f = self._facilities[facility_id]
        if f.limit_gbp == 0:
            return 0.0
        return round(self.outstanding_balance(facility_id) / f.limit_gbp * 100, 1)
