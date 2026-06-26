from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

_GENERATION_RATE_P_PER_KWH: dict[str, float] = {
    "2012": 16.0, "2013": 15.44, "2014": 14.90, "2015": 14.38,
    "2016": 4.39, "2017": 4.18, "2018": 3.97, "2019": 3.68,
}
_EXPORT_RATE_P_PER_KWH: dict[str, float] = {
    "2012": 4.5, "2013": 4.77, "2014": 4.77, "2015": 4.85,
    "2016": 4.91, "2017": 4.85, "2018": 5.24, "2019": 5.24,
}
_FIT_LEVELISATION_RATE_PER_MWH: dict[int, float] = {
    2016: 8.36, 2017: 9.19, 2018: 9.40, 2019: 9.45, 2020: 0.0,
}
FIT_SCHEME_END_DATE = "2019-03-31"


class FITTechnology(str, Enum):
    SOLAR_PV = "solar_pv"
    WIND = "wind"
    MICRO_CHP = "micro_chp"
    HYDRO = "hydro"
    ANAEROBIC_DIGESTION = "anaerobic_digestion"


@dataclass(frozen=True)
class FITInstallation:
    installation_id: str
    account_id: str
    technology: FITTechnology
    capacity_kw: float
    accreditation_date: str
    tariff_group: str

    @property
    def is_active(self) -> bool:
        return self.accreditation_date <= FIT_SCHEME_END_DATE


@dataclass(frozen=True)
class FITPayment:
    installation_id: str
    quarter: str
    generation_kwh: float
    export_kwh: float
    generation_rate_p: float
    export_rate_p: float

    @property
    def generation_payment_gbp(self) -> float:
        return round(self.generation_kwh * self.generation_rate_p / 100, 2)

    @property
    def export_payment_gbp(self) -> float:
        return round(self.export_kwh * self.export_rate_p / 100, 2)

    @property
    def total_payment_gbp(self) -> float:
        return round(self.generation_payment_gbp + self.export_payment_gbp, 2)


class FITBook:
    def __init__(self) -> None:
        self._installations: dict[str, FITInstallation] = {}
        self._payments: list[FITPayment] = []

    def register_installation(self, installation: FITInstallation) -> FITInstallation:
        self._installations[installation.installation_id] = installation
        return installation

    def record_payment(self, payment: FITPayment) -> FITPayment:
        self._payments.append(payment)
        return payment

    def payments_for_installation(self, installation_id: str) -> list[FITPayment]:
        return [p for p in self._payments if p.installation_id == installation_id]

    def total_paid_gbp(self, year: Optional[int] = None) -> float:
        payments = (
            [p for p in self._payments if p.quarter.startswith(str(year))]
            if year else self._payments
        )
        return round(sum(p.total_payment_gbp for p in payments), 2)

    def levelisation_charge_gbp(self, year: int, total_mwh_supplied: float) -> float:
        rate = _FIT_LEVELISATION_RATE_PER_MWH.get(year, 0.0)
        return round(total_mwh_supplied * rate / 1000, 2)

    def installations_count(self, technology: Optional[FITTechnology] = None) -> int:
        if technology:
            return sum(1 for i in self._installations.values() if i.technology == technology)
        return len(self._installations)

    def fit_summary(self) -> dict:
        return {
            "installations": len(self._installations),
            "total_paid_gbp": self.total_paid_gbp(),
            "solar_pv_count": self.installations_count(FITTechnology.SOLAR_PV),
            "scheme_end_date": FIT_SCHEME_END_DATE,
        }
