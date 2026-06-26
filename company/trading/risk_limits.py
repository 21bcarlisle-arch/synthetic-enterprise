"""Wholesale trading risk limits and position governor.

The risk committee sets enforceable limits on the company's forward book.
These are hard limits — the trading desk cannot exceed them without explicit
board approval. Limits reset annually and are monitored in real time.

Limits:
- max_open_position_mwh: maximum total open MWh across all tenors
- max_single_contract_mwh: maximum size of any single forward contract
- var_limit_gbp: maximum Value-at-Risk (99th pctile) across the book
- stop_loss_gbp: MTM loss at which all new buying is suspended
- max_hedge_fraction: maximum fraction of load that can be hedged forward

Risk committee sets these annually based on treasury position and board mandate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class RiskLimit:
    limit_name: str
    value: float
    unit: str
    effective_year: int
    set_by: str = "risk_committee"
    notes: str = ""


@dataclass
class LimitCheckResult:
    limit_name: str
    current_value: float
    limit_value: float
    utilisation_pct: float
    status: Literal["OK", "WARNING", "BREACH"]  # WARNING >80%, BREACH >=100%
    message: str


class RiskGovernor:
    """Enforces position limits on the trading book."""

    def __init__(self):
        self._limits: dict[str, RiskLimit] = {}

    def set_limit(self, limit: RiskLimit) -> RiskLimit:
        self._limits[limit.limit_name] = limit
        return limit

    def get_limit(self, name: str) -> RiskLimit | None:
        return self._limits.get(name)

    def check(self, name: str, current_value: float) -> LimitCheckResult:
        limit = self._limits.get(name)
        if limit is None:
            return LimitCheckResult(
                limit_name=name, current_value=current_value,
                limit_value=0.0, utilisation_pct=0.0,
                status="OK", message=f"No limit set for {name}",
            )
        utilisation = (current_value / limit.value * 100) if limit.value > 0 else 0.0
        if utilisation >= 100.0:
            status = "BREACH"
            message = f"{name}: {current_value:.0f} {limit.unit} exceeds limit of {limit.value:.0f} {limit.unit}."
        elif utilisation >= 80.0:
            status = "WARNING"
            message = f"{name}: {utilisation:.1f}% of limit used — approaching threshold."
        else:
            status = "OK"
            message = f"{name}: {utilisation:.1f}% of limit used."

        return LimitCheckResult(
            limit_name=name,
            current_value=round(current_value, 2),
            limit_value=limit.value,
            utilisation_pct=round(utilisation, 1),
            status=status,
            message=message,
        )

    def check_all(self, current_values: dict[str, float]) -> list[LimitCheckResult]:
        results = []
        for name, limit in self._limits.items():
            current = current_values.get(name, 0.0)
            results.append(self.check(name, current))
        return results

    def governance_summary(self, current_values: dict[str, float]) -> dict:
        checks = self.check_all(current_values)
        return {
            "total_limits": len(checks),
            "ok": sum(1 for c in checks if c.status == "OK"),
            "warning": sum(1 for c in checks if c.status == "WARNING"),
            "breach": sum(1 for c in checks if c.status == "BREACH"),
            "overall_status": (
                "BREACH" if any(c.status == "BREACH" for c in checks) else
                "WARNING" if any(c.status == "WARNING" for c in checks) else
                "OK"
            ),
            "checks": checks,
        }

    def new_position_allowed(self, additional_mwh: float, current_open_mwh: float) -> bool:
        """Return True if adding additional_mwh stays within open position limit."""
        limit = self._limits.get("max_open_position_mwh")
        if limit is None:
            return True
        return (current_open_mwh + additional_mwh) <= limit.value
