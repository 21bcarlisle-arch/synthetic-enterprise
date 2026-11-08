from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

# BSUoS (Balancing Services Use of System) charge rate £/MWh by year
# Charged to suppliers for their share of the grid balancing cost
# 2021-22 crisis: BSUoS doubled then trebled; recovery announced 2023 (move to fixed tariff)
_BSUOS_RATE_GBP_PER_MWH: dict[int, float] = {
    2016: 2.10, 2017: 2.30, 2018: 2.55, 2019: 2.80,
    2020: 3.20, 2021: 4.10, 2022: 6.85, 2023: 5.40, 2024: 4.20, 2025: 3.80,
}


@dataclass(frozen=True)
class BSUoSCharge:
    account_id: str
    charge_period: str  # YYYY-MM
    consumption_mwh: float
    rate_gbp_per_mwh: float

    @property
    def charge_gbp(self) -> float:
        return round(self.consumption_mwh * self.rate_gbp_per_mwh, 2)

    @property
    def is_crisis_period(self) -> bool:
        return self.charge_period[:4] in {"2021", "2022"}


class BSUoSLedger:
    def __init__(self) -> None:
        self._charges: list[BSUoSCharge] = []

    @staticmethod
    def rate_for_year(year: int) -> float:
        return _BSUOS_RATE_GBP_PER_MWH.get(year, 3.50)

    def record_charge(self, charge: BSUoSCharge) -> BSUoSCharge:
        self._charges.append(charge)
        return charge

    def charges_for_account(self, account_id: str) -> list[BSUoSCharge]:
        return [c for c in self._charges if c.account_id == account_id]

    def charges_for_year(self, year: int) -> list[BSUoSCharge]:
        return [c for c in self._charges if c.charge_period.startswith(str(year))]

    def total_charged_gbp(self, year: Optional[int] = None) -> float:
        charges = self.charges_for_year(year) if year else self._charges
        return round(sum(c.charge_gbp for c in charges), 2)

    def crisis_uplift_multiple(self) -> float:
        """How many times higher 2022 BSUoS was vs 2016 baseline."""
        return round(
            _BSUOS_RATE_GBP_PER_MWH.get(2022, 6.85) / _BSUOS_RATE_GBP_PER_MWH.get(2016, 2.10), 2
        )

    def annual_rate_trend(self) -> list[dict]:
        return [
            {"year": yr, "rate_gbp_per_mwh": rate}
            for yr, rate in sorted(_BSUOS_RATE_GBP_PER_MWH.items())
        ]

    def bsuos_summary(self, year: Optional[int] = None) -> dict:
        return {
            "total_charges": len(self._charges),
            "total_charged_gbp": self.total_charged_gbp(year),
            "crisis_uplift_multiple": self.crisis_uplift_multiple(),
            "peak_rate_gbp_per_mwh": max(_BSUOS_RATE_GBP_PER_MWH.values()),
            "peak_rate_year": max(_BSUOS_RATE_GBP_PER_MWH, key=_BSUOS_RATE_GBP_PER_MWH.get),
        }
