from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import statistics


class VaRBreachLevel(str, Enum):
    WITHIN_LIMIT = "within_limit"
    AMBER = "amber"
    RED = "red"


@dataclass(frozen=True)
class VaRObservation:
    observation_date: str
    current_var_gbp: float
    stressed_var_gbp: float
    treasury_gbp: float

    @property
    def var_as_pct_treasury(self) -> float:
        if self.treasury_gbp <= 0:
            return 0.0
        return round(self.current_var_gbp / self.treasury_gbp * 100, 2)

    @property
    def stress_uplift_pct(self) -> float:
        if self.current_var_gbp <= 0:
            return 0.0
        return round((self.stressed_var_gbp - self.current_var_gbp) / self.current_var_gbp * 100, 2)


class VaRMonitorBook:
    def __init__(
        self,
        amber_limit_gbp: float = 100_000.0,
        red_limit_gbp: float = 250_000.0,
    ) -> None:
        self._observations: list[VaRObservation] = []
        self.amber_limit_gbp = amber_limit_gbp
        self.red_limit_gbp = red_limit_gbp

    def record_observation(
        self,
        observation_date: str,
        current_var_gbp: float,
        stressed_var_gbp: float,
        treasury_gbp: float,
    ) -> VaRObservation:
        obs = VaRObservation(
            observation_date=observation_date,
            current_var_gbp=current_var_gbp,
            stressed_var_gbp=stressed_var_gbp,
            treasury_gbp=treasury_gbp,
        )
        self._observations.append(obs)
        return obs

    def breach_level(self, var_gbp: float) -> VaRBreachLevel:
        if var_gbp >= self.red_limit_gbp:
            return VaRBreachLevel.RED
        if var_gbp >= self.amber_limit_gbp:
            return VaRBreachLevel.AMBER
        return VaRBreachLevel.WITHIN_LIMIT

    def observations_for_year(self, year: int) -> list[VaRObservation]:
        return [o for o in self._observations if o.observation_date.startswith(str(year))]

    def breach_count(self, level: VaRBreachLevel, year: Optional[int] = None) -> int:
        obs = self.observations_for_year(year) if year else self._observations
        return sum(1 for o in obs if self.breach_level(o.current_var_gbp) == level)

    def peak_var(self, year: Optional[int] = None) -> Optional[VaRObservation]:
        obs = self.observations_for_year(year) if year else self._observations
        return max(obs, key=lambda o: o.current_var_gbp) if obs else None

    def mean_var_gbp(self, year: Optional[int] = None) -> float:
        obs = self.observations_for_year(year) if year else self._observations
        return round(statistics.mean(o.current_var_gbp for o in obs), 2) if obs else 0.0

    def var_trend(self) -> list[dict]:
        return [
            {
                "date": o.observation_date,
                "current_var_gbp": round(o.current_var_gbp, 2),
                "stressed_var_gbp": round(o.stressed_var_gbp, 2),
                "breach_level": self.breach_level(o.current_var_gbp).value,
                "var_pct_treasury": o.var_as_pct_treasury,
            }
            for o in sorted(self._observations, key=lambda o: o.observation_date)
        ]

    def var_summary(self, year: Optional[int] = None) -> dict:
        obs = self.observations_for_year(year) if year else self._observations
        if not obs:
            return {"observations": 0, "mean_var_gbp": 0.0, "peak_var_gbp": 0.0,
                    "amber_breaches": 0, "red_breaches": 0}
        pk = max(obs, key=lambda o: o.current_var_gbp)
        return {
            "observations": len(obs),
            "mean_var_gbp": round(statistics.mean(o.current_var_gbp for o in obs), 2),
            "peak_var_gbp": round(pk.current_var_gbp, 2),
            "peak_date": pk.observation_date,
            "amber_breaches": self.breach_count(VaRBreachLevel.AMBER, year),
            "red_breaches": self.breach_count(VaRBreachLevel.RED, year),
            "amber_limit_gbp": self.amber_limit_gbp,
            "red_limit_gbp": self.red_limit_gbp,
        }
