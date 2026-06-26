from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


_UK_AVG_RESI_ELEC_KWH = 3100.0
_UK_AVG_RESI_GAS_KWH = 12000.0
_UK_AVG_SME_ELEC_KWH = 25000.0
_UK_AVG_SME_GAS_KWH = 55000.0
_UK_AVG_IC_ELEC_KWH = 500000.0

_SEASONAL_ELEC_FACTORS = {
    'Q1': 1.18, 'Q2': 0.88, 'Q3': 0.82, 'Q4': 1.12
}

_SEASONAL_GAS_FACTORS = {
    'Q1': 1.55, 'Q2': 0.85, 'Q3': 0.55, 'Q4': 1.05
}


@dataclass(frozen=True)
class SegmentLoadForecast:
    segment: str
    commodity: str
    account_count: int
    annual_mwh: float
    q1_mwh: float
    q2_mwh: float
    q3_mwh: float
    q4_mwh: float

    @property
    def monthly_avg_mwh(self) -> float:
        return round(self.annual_mwh / 12, 2)


@dataclass(frozen=True)
class PortfolioLoadForecast:
    year: int
    segments: tuple

    @property
    def total_elec_mwh(self) -> float:
        return sum(s.annual_mwh for s in self.segments if s.commodity == 'electricity')

    @property
    def total_gas_mwh(self) -> float:
        return sum(s.annual_mwh for s in self.segments if s.commodity == 'gas')

    def quarterly_elec_mwh(self, quarter: str) -> float:
        return sum(
            getattr(s, f'{quarter.lower()}_mwh')
            for s in self.segments if s.commodity == 'electricity'
        )

    def quarterly_gas_mwh(self, quarter: str) -> float:
        return sum(
            getattr(s, f'{quarter.lower()}_mwh')
            for s in self.segments if s.commodity == 'gas'
        )

    def summary(self) -> dict:
        return {
            'year': self.year,
            'total_elec_mwh': round(self.total_elec_mwh, 0),
            'total_gas_mwh': round(self.total_gas_mwh, 0),
            'q1_elec_mwh': round(self.quarterly_elec_mwh('q1'), 0),
            'q3_elec_mwh': round(self.quarterly_elec_mwh('q3'), 0),
            'q1_gas_mwh': round(self.quarterly_gas_mwh('q1'), 0),
            'q3_gas_mwh': round(self.quarterly_gas_mwh('q3'), 0),
        }


def _segment_forecast(segment: str, commodity: str, account_count: int) -> SegmentLoadForecast:
    if commodity == 'electricity':
        if segment == 'RESI':
            avg_kwh = _UK_AVG_RESI_ELEC_KWH
        elif segment == 'SME':
            avg_kwh = _UK_AVG_SME_ELEC_KWH
        else:
            avg_kwh = _UK_AVG_IC_ELEC_KWH
        factors = _SEASONAL_ELEC_FACTORS
    else:
        if segment == 'RESI':
            avg_kwh = _UK_AVG_RESI_GAS_KWH
        else:
            avg_kwh = _UK_AVG_SME_GAS_KWH
        factors = _SEASONAL_GAS_FACTORS
    annual_kwh = avg_kwh * account_count
    annual_mwh = annual_kwh / 1000.0
    return SegmentLoadForecast(
        segment=segment,
        commodity=commodity,
        account_count=account_count,
        annual_mwh=round(annual_mwh, 2),
        q1_mwh=round(annual_mwh * factors['Q1'] / 4, 2),
        q2_mwh=round(annual_mwh * factors['Q2'] / 4, 2),
        q3_mwh=round(annual_mwh * factors['Q3'] / 4, 2),
        q4_mwh=round(annual_mwh * factors['Q4'] / 4, 2),
    )


def build_portfolio_forecast(
    year: int,
    resi_accounts: int,
    sme_accounts: int,
    ic_accounts: int,
    include_gas: bool = True,
) -> PortfolioLoadForecast:
    segments = []
    segments.append(_segment_forecast('RESI', 'electricity', resi_accounts))
    segments.append(_segment_forecast('SME', 'electricity', sme_accounts))
    if ic_accounts > 0:
        segments.append(_segment_forecast('IC', 'electricity', ic_accounts))
    if include_gas:
        segments.append(_segment_forecast('RESI', 'gas', resi_accounts))
        segments.append(_segment_forecast('SME', 'gas', sme_accounts))
    return PortfolioLoadForecast(year=year, segments=tuple(segments))
