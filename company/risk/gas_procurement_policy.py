"""Gas Procurement Policy Book — Phase 309.

The gas side of a UK supplier must maintain minimum forward cover against its
supply obligation. Unlike electricity (where the risk committee evolves hedge
fractions via VaR), gas procurement is managed via a cover-based policy:
the company must have at least MIN_COVER_PCT of its next-quarter supply
obligation purchased forward on NBP (via the OTC book, Ph253).

2022 learning: suppliers with <40% forward cover when NBP spiked 10x faced
ruinous spot purchases. Industry post-mortem recommends minimum 80% cover
at any point in the delivery period. Ofgem now monitors gas procurement
cover as part of supplier financial resilience checks.

Epistemic constraint: only uses company-observable data — forward cover
from own OTC book, supply obligation estimated from own AQ register,
NBP SBP from published market data. No SIM internals accessed.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

# Post-2022 best practice: 80% minimum forward cover 3 months ahead.
# Suppliers who failed 2021-22 had cover ratios below 40%.
GAS_MIN_COVER_PCT = 0.80
GAS_MAX_COVER_PCT = 1.05  # slight overhedge acceptable
GAS_STOP_LOSS_SBP_THRESHOLD_GBP_PER_MWH = 100.0  # trigger review if SBP exceeds this

_COVER_TARGETS_BY_YEAR: dict[int, dict] = {
    # Post-2022 targets reflect Ofgem guidance on supplier resilience
    2016: {"min_cover_pct": 0.70, "max_cover_pct": 1.05},
    2017: {"min_cover_pct": 0.70, "max_cover_pct": 1.05},
    2018: {"min_cover_pct": 0.70, "max_cover_pct": 1.05},
    2019: {"min_cover_pct": 0.75, "max_cover_pct": 1.05},
    2020: {"min_cover_pct": 0.75, "max_cover_pct": 1.05},
    2021: {"min_cover_pct": 0.80, "max_cover_pct": 1.05},
    2022: {"min_cover_pct": 0.85, "max_cover_pct": 1.05},  # tightened mid-crisis
    2023: {"min_cover_pct": 0.80, "max_cover_pct": 1.05},
    2024: {"min_cover_pct": 0.80, "max_cover_pct": 1.05},
    2025: {"min_cover_pct": 0.80, "max_cover_pct": 1.05},
}
_DEFAULT_TARGET = {"min_cover_pct": GAS_MIN_COVER_PCT, "max_cover_pct": GAS_MAX_COVER_PCT}


class GasProcurementStatus(str, Enum):
    COMPLIANT        = "compliant"
    SHORT_COVER      = "short_cover"      # cover < min_cover_pct
    OVER_HEDGED      = "over_hedged"      # cover > max_cover_pct
    STOP_LOSS_ALERT  = "stop_loss_alert"  # SBP > crisis threshold regardless of cover


@dataclass(frozen=True)
class GasCoverTarget:
    year: int
    min_cover_pct: float
    max_cover_pct: float


@dataclass(frozen=True)
class GasProcurementCheck:
    check_date: str          # ISO date
    supply_obligation_mwh: float
    forward_cover_mwh: float
    nbp_sbp_gbp_per_mwh: float

    @property
    def cover_pct(self) -> float:
        if self.supply_obligation_mwh <= 0:
            return 1.0
        return round(self.forward_cover_mwh / self.supply_obligation_mwh, 4)

    @property
    def is_crisis_alert(self) -> bool:
        return self.nbp_sbp_gbp_per_mwh > GAS_STOP_LOSS_SBP_THRESHOLD_GBP_PER_MWH

    def status(self, target: GasCoverTarget) -> GasProcurementStatus:
        if self.is_crisis_alert:
            return GasProcurementStatus.STOP_LOSS_ALERT
        if self.cover_pct < target.min_cover_pct:
            return GasProcurementStatus.SHORT_COVER
        if self.cover_pct > target.max_cover_pct:
            return GasProcurementStatus.OVER_HEDGED
        return GasProcurementStatus.COMPLIANT

    def shortfall_mwh(self, target: GasCoverTarget) -> float:
        min_required = self.supply_obligation_mwh * target.min_cover_pct
        return max(0.0, round(min_required - self.forward_cover_mwh, 2))


class GasProcurementPolicyBook:
    def __init__(self) -> None:
        self._checks: list[tuple[GasProcurementCheck, GasCoverTarget]] = []

    def cover_target_for_year(self, year: int) -> GasCoverTarget:
        t = _COVER_TARGETS_BY_YEAR.get(year, _DEFAULT_TARGET)
        return GasCoverTarget(year=year, min_cover_pct=t["min_cover_pct"], max_cover_pct=t["max_cover_pct"])

    def check_cover(
        self,
        check_date: str,
        supply_obligation_mwh: float,
        forward_cover_mwh: float,
        nbp_sbp_gbp_per_mwh: float,
        year: int,
    ) -> GasProcurementCheck:
        check = GasProcurementCheck(
            check_date=check_date,
            supply_obligation_mwh=supply_obligation_mwh,
            forward_cover_mwh=forward_cover_mwh,
            nbp_sbp_gbp_per_mwh=nbp_sbp_gbp_per_mwh,
        )
        target = self.cover_target_for_year(year)
        self._checks.append((check, target))
        return check

    def checks_for_year(self, year: int) -> list[GasProcurementCheck]:
        return [c for c, _ in self._checks if c.check_date.startswith(str(year))]

    def non_compliant_checks(self, year: int | None = None) -> list[GasProcurementCheck]:
        items = [(c, t) for c, t in self._checks if not year or c.check_date.startswith(str(year))]
        return [c for c, t in items if c.status(t) != GasProcurementStatus.COMPLIANT]

    def crisis_alerts(self) -> list[GasProcurementCheck]:
        return [c for c, _ in self._checks if c.is_crisis_alert]

    def mean_cover_pct(self, year: int | None = None) -> float:
        checks = self.checks_for_year(year) if year else [c for c, _ in self._checks]
        if not checks:
            return 0.0
        return round(sum(c.cover_pct for c in checks) / len(checks), 4)

    def policy_summary(self, year: int | None = None) -> dict:
        checks = self.checks_for_year(year) if year else [c for c, _ in self._checks]
        items = [(c, t) for c, t in self._checks if not year or c.check_date.startswith(str(year))]
        non_compliant = [c for c, t in items if c.status(t) != GasProcurementStatus.COMPLIANT]
        return {
            "total_checks": len(checks),
            "non_compliant_checks": len(non_compliant),
            "crisis_alert_checks": len([c for c in checks if c.is_crisis_alert]),
            "mean_cover_pct": self.mean_cover_pct(year),
            "compliance_rate_pct": round(
                (1 - len(non_compliant) / len(checks)) * 100, 1
            ) if checks else 100.0,
        }
