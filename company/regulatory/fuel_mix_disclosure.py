from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

_UK_AVG_MIX: dict[str, dict[str, float]] = {
    "2016": {"coal": 0.091, "gas": 0.424, "nuclear": 0.199, "renewables": 0.247, "other": 0.039},
    "2017": {"coal": 0.067, "gas": 0.399, "nuclear": 0.204, "renewables": 0.290, "other": 0.040},
    "2018": {"coal": 0.050, "gas": 0.381, "nuclear": 0.196, "renewables": 0.333, "other": 0.040},
    "2019": {"coal": 0.022, "gas": 0.383, "nuclear": 0.176, "renewables": 0.378, "other": 0.041},
    "2020": {"coal": 0.016, "gas": 0.359, "nuclear": 0.170, "renewables": 0.430, "other": 0.025},
    "2021": {"coal": 0.023, "gas": 0.386, "nuclear": 0.154, "renewables": 0.397, "other": 0.040},
    "2022": {"coal": 0.018, "gas": 0.385, "nuclear": 0.148, "renewables": 0.411, "other": 0.038},
    "2023": {"coal": 0.005, "gas": 0.360, "nuclear": 0.144, "renewables": 0.453, "other": 0.038},
}


class FuelSource(str, Enum):
    COAL = "coal"
    GAS = "gas"
    NUCLEAR = "nuclear"
    RENEWABLES = "renewables"
    OTHER = "other"
    UNSPECIFIED = "unspecified"


@dataclass(frozen=True)
class FuelMixDisclosure:
    disclosure_year: int
    coal_pct: float
    gas_pct: float
    nuclear_pct: float
    renewables_pct: float
    other_pct: float
    unspecified_pct: float
    rego_covered_mwh: float
    total_retail_mwh: float

    @property
    def total_pct(self) -> float:
        return round(self.coal_pct + self.gas_pct + self.nuclear_pct
                     + self.renewables_pct + self.other_pct + self.unspecified_pct, 2)

    @property
    def rego_coverage_pct(self) -> float:
        if self.total_retail_mwh <= 0:
            return 0.0
        return round(self.rego_covered_mwh / self.total_retail_mwh * 100, 2)

    @property
    def is_100pct_renewable(self) -> bool:
        return self.renewables_pct >= 99.9

    def vs_uk_average(self) -> dict:
        uk = _UK_AVG_MIX.get(str(self.disclosure_year), {})
        return {
            "coal_delta": round(self.coal_pct - uk.get("coal", 0) * 100, 2),
            "gas_delta": round(self.gas_pct - uk.get("gas", 0) * 100, 2),
            "nuclear_delta": round(self.nuclear_pct - uk.get("nuclear", 0) * 100, 2),
            "renewables_delta": round(self.renewables_pct - uk.get("renewables", 0) * 100, 2),
        }


class FuelMixDisclosureBook:
    def __init__(self) -> None:
        self._disclosures: list[FuelMixDisclosure] = []

    def file_disclosure(self, disclosure: FuelMixDisclosure) -> FuelMixDisclosure:
        self._disclosures.append(disclosure)
        return disclosure

    def disclosure_for_year(self, year: int) -> Optional[FuelMixDisclosure]:
        for d in self._disclosures:
            if d.disclosure_year == year:
                return d
        return None

    def renewable_trend(self) -> list[dict]:
        return [
            {"year": d.disclosure_year, "renewables_pct": d.renewables_pct,
             "is_100pct_renewable": d.is_100pct_renewable}
            for d in sorted(self._disclosures, key=lambda d: d.disclosure_year)
        ]

    def fmd_summary(self) -> dict:
        if not self._disclosures:
            return {"years_filed": 0, "latest_renewables_pct": 0.0}
        latest = max(self._disclosures, key=lambda d: d.disclosure_year)
        return {
            "years_filed": len(self._disclosures),
            "latest_year": latest.disclosure_year,
            "latest_renewables_pct": latest.renewables_pct,
            "is_100pct_renewable": latest.is_100pct_renewable,
            "rego_coverage_pct": latest.rego_coverage_pct,
        }
