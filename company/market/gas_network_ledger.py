from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

_NTS_RATE_P_PER_KWH: dict[int, float] = {
    2016: 0.30, 2017: 0.31, 2018: 0.32, 2019: 0.33, 2020: 0.34,
    2021: 0.36, 2022: 0.41, 2023: 0.37, 2024: 0.30, 2025: 0.30,
}

_LDZ_RATE_P_PER_KWH: dict[int, float] = {
    2016: 1.10, 2017: 1.14, 2018: 1.18, 2019: 1.22, 2020: 1.24,
    2021: 1.34, 2022: 1.54, 2023: 1.39, 2024: 1.13, 2025: 1.13,
}

_GGL_RATE_GBP_PER_METER_YEAR: dict[int, float] = {
    2016: 0.0, 2017: 0.0, 2018: 0.0, 2019: 0.0, 2020: 0.0,
    2021: 2.10, 2022: 2.10, 2023: 0.45, 2024: 0.38, 2025: 0.38,
}


class GasTransporterZone(str, Enum):
    CADENT_NW = 'cadent_nw'
    CADENT_NG = 'cadent_ng'
    CADENT_WM = 'cadent_wm'
    NORTHERN = 'northern'
    SOUTHERN = 'southern'
    WALES_WEST = 'wales_west'
    SGN_SCOTLAND = 'sgn_scotland'
    SGN_SOUTH = 'sgn_south'


@dataclass(frozen=True)
class GasNetworkCharge:
    mprn: str
    settlement_date: str
    consumption_mwh: float
    aq_kwh: float
    zone: GasTransporterZone
    nts_rate_gbp_per_mwh: float
    ldz_rate_gbp_per_mwh: float
    ggl_rate_gbp_per_meter_year: float
    days_in_period: int = 1

    @property
    def nts_charge_gbp(self) -> float:
        return round(self.consumption_mwh * self.nts_rate_gbp_per_mwh, 4)

    @property
    def ldz_charge_gbp(self) -> float:
        return round(self.consumption_mwh * self.ldz_rate_gbp_per_mwh, 4)

    @property
    def ggl_charge_gbp(self) -> float:
        return round(self.ggl_rate_gbp_per_meter_year / 365 * self.days_in_period, 4)

    @property
    def total_charge_gbp(self) -> float:
        return round(self.nts_charge_gbp + self.ldz_charge_gbp + self.ggl_charge_gbp, 4)

    @property
    def unit_cost_p_per_kwh(self) -> float:
        if self.consumption_mwh == 0:
            return 0.0
        return round(self.total_charge_gbp / (self.consumption_mwh * 1000) * 100, 4)


class GasNetworkLedger:
    def __init__(self) -> None:
        self._charges: list[GasNetworkCharge] = []

    @staticmethod
    def nts_rate_for_year(year: int) -> float:
        return _NTS_RATE_P_PER_KWH.get(year, 0.30)

    @staticmethod
    def ldz_rate_for_year(year: int) -> float:
        return _LDZ_RATE_P_PER_KWH.get(year, 1.13)

    @staticmethod
    def ggl_rate_for_year(year: int) -> float:
        return _GGL_RATE_GBP_PER_METER_YEAR.get(year, 0.0)

    def record_charge(self, charge: GasNetworkCharge) -> GasNetworkCharge:
        self._charges.append(charge)
        return charge

    def charges_for_mprn(self, mprn: str) -> list[GasNetworkCharge]:
        return [c for c in self._charges if c.mprn == mprn]

    def charges_for_year(self, year: int) -> list[GasNetworkCharge]:
        return [c for c in self._charges if c.settlement_date.startswith(str(year))]

    def total_nts_gbp(self, year=None) -> float:
        charges = self.charges_for_year(year) if year else self._charges
        return round(sum(c.nts_charge_gbp for c in charges), 2)

    def total_ldz_gbp(self, year=None) -> float:
        charges = self.charges_for_year(year) if year else self._charges
        return round(sum(c.ldz_charge_gbp for c in charges), 2)

    def total_ggl_gbp(self, year=None) -> float:
        charges = self.charges_for_year(year) if year else self._charges
        return round(sum(c.ggl_charge_gbp for c in charges), 2)

    def annual_cost_breakdown(self, year: int) -> dict:
        nts = self.total_nts_gbp(year)
        ldz = self.total_ldz_gbp(year)
        ggl = self.total_ggl_gbp(year)
        return {'year': year, 'nts_gbp': nts, 'ldz_gbp': ldz, 'ggl_gbp': ggl,
                'total_gbp': round(nts + ldz + ggl, 2)}

    def cost_trend(self) -> list[dict]:
        years = sorted({c.settlement_date[:4] for c in self._charges})
        return [self.annual_cost_breakdown(int(y)) for y in years]

    def gas_network_summary(self) -> dict:
        total = round(sum(c.total_charge_gbp for c in self._charges), 2)
        zones = {c.zone.value for c in self._charges}
        return {
            'total_charges_recorded': len(self._charges),
            'total_charged_gbp': total,
            'zones_covered': sorted(zones),
            'nts_rate_range': (min(_NTS_RATE_P_PER_KWH.values()),
                               max(_NTS_RATE_P_PER_KWH.values())),
            'ldz_rate_range': (min(_LDZ_RATE_P_PER_KWH.values()),
                               max(_LDZ_RATE_P_PER_KWH.values())),
            'ggl_peak_rate_gbp_per_meter_year': max(_GGL_RATE_GBP_PER_METER_YEAR.values()),
            'ggl_active_years': [yr for yr, r in sorted(_GGL_RATE_GBP_PER_METER_YEAR.items()) if r > 0],
        }
