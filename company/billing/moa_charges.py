"""Meter Operator Agent (MOA) charge management.

UK energy suppliers appoint a Meter Operator Agent (MOA) to install,
maintain, and certify electricity meters at customer premises. The MOA
charges the supplier on a per-meter-point per-annum basis.

MOA charge schedule (approximate industry rates):
  - Domestic credit meter (TRAD/PPM): 12-18 GBP/year
  - Smart meter (SMETS2): 20-28 GBP/year
  - HH metered (AMR/I&C): 60-150 GBP/year depending on type
"""

from __future__ import annotations
from dataclasses import dataclass

_MOA_ANNUAL_GBP = {
    "TRAD":   {2016: 12.0, 2018: 13.0, 2020: 14.0, 2022: 15.0, 2024: 16.0},
    "PPM":    {2016: 13.0, 2018: 14.0, 2020: 15.5, 2022: 17.0, 2024: 18.0},
    "SMETS1": {2016: 18.0, 2018: 20.0, 2020: 22.0, 2022: 24.0, 2024: 24.0},
    "SMETS2": {2016: 22.0, 2018: 24.0, 2020: 26.0, 2022: 27.0, 2024: 28.0},
    "AMR":    {2016: 65.0, 2018: 70.0, 2020: 75.0, 2022: 80.0, 2024: 85.0},
}


def _interpolate_rate(rate_dict, year):
    years = sorted(rate_dict.keys())
    if year <= years[0]:
        return rate_dict[years[0]]
    if year >= years[-1]:
        return rate_dict[years[-1]]
    for i in range(len(years) - 1):
        y0, y1 = years[i], years[i + 1]
        if y0 <= year <= y1:
            r0, r1 = rate_dict[y0], rate_dict[y1]
            frac = (year - y0) / (y1 - y0)
            return round(r0 + frac * (r1 - r0), 2)
    return list(rate_dict.values())[-1]


def get_moa_annual_charge(meter_type, year):
    rate_dict = _MOA_ANNUAL_GBP.get(meter_type.upper())
    if rate_dict is None:
        return 14.0
    return _interpolate_rate(rate_dict, year)


def get_moa_daily_charge(meter_type, year):
    return round(get_moa_annual_charge(meter_type, year) / 365.0, 6)


@dataclass
class MoaInvoiceLine:
    mpan_or_mprn: str
    meter_type: str
    year: int
    days_in_period: int
    daily_charge_gbp: float
    charge_gbp: float


def calculate_moa_charges(meter_points, year):
    lines = []
    for mp in meter_points:
        daily = get_moa_daily_charge(mp["meter_type"], year)
        days = mp.get("days_in_period", 365)
        charge = round(daily * days, 2)
        lines.append(MoaInvoiceLine(
            mpan_or_mprn=mp["mpan_or_mprn"],
            meter_type=mp["meter_type"],
            year=year,
            days_in_period=days,
            daily_charge_gbp=daily,
            charge_gbp=charge,
        ))
    return lines


def moa_portfolio_cost(meter_points, year):
    return round(sum(l.charge_gbp for l in calculate_moa_charges(meter_points, year)), 2)
