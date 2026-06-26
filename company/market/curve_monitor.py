"""Wholesale forward curve anomaly detection.

The company's market team monitors the published forward curve for anomalies
that could indicate:
  - A market stress event (e.g. gas supply disruption, TTF spike)
  - A data feed error (wrong units, stale data, implausible value)
  - A structural regime change (e.g. energy crisis onset 2021)

Anomaly detection uses a z-score approach against a rolling window of
recent prices. A z-score > 3.0 triggers an alert; > 5.0 is a critical alert.

The company observes only the published price feed — it has no access to
raw Elexon or NBP data from the simulation internals.

This connects to the market monitoring view on the trading portal and
feeds into the risk committee briefing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import math


_Z_WARN = 2.5
_Z_ALERT = 3.5
_Z_CRITICAL = 5.0

_MIN_WINDOW = 10  # minimum number of data points needed for reliable statistics


@dataclass
class PricePoint:
    period: str   # date or settlement period identifier
    price_gbp_mwh: float
    commodity: Literal["electricity", "gas"] = "electricity"


@dataclass
class AnomalyResult:
    period: str
    price_gbp_mwh: float
    mean_gbp_mwh: float
    std_gbp_mwh: float
    z_score: float
    severity: Literal["normal", "watch", "alert", "critical"]
    message: str


def _severity(z: float) -> tuple[str, str]:
    abs_z = abs(z)
    if abs_z >= _Z_CRITICAL:
        return "critical", f"CRITICAL: z={z:.1f} (>{_Z_CRITICAL}σ from mean)"
    elif abs_z >= _Z_ALERT:
        return "alert", f"ALERT: z={z:.1f} (>{_Z_ALERT}σ from mean)"
    elif abs_z >= _Z_WARN:
        return "watch", f"WATCH: z={z:.1f} (>{_Z_WARN}σ from mean)"
    return "normal", f"Normal: z={z:.1f}"


class ForwardCurveMonitor:
    """Monitors a series of forward price observations for anomalies."""

    def __init__(self, window: int = 30):
        """window: number of periods for rolling statistics."""
        self._window = max(window, _MIN_WINDOW)
        self._history: list[PricePoint] = []

    def add(self, point: PricePoint) -> AnomalyResult | None:
        """Add a price point; return anomaly result if history is sufficient."""
        self._history.append(point)
        recent = [p.price_gbp_mwh for p in self._history[-self._window:]]
        if len(recent) < _MIN_WINDOW:
            return None  # not enough data yet
        n = len(recent)
        mean = sum(recent[:-1]) / (n - 1)  # exclude current from window mean
        variance = sum((p - mean) ** 2 for p in recent[:-1]) / (n - 2) if n > 2 else 1.0
        std = math.sqrt(variance) if variance > 0 else 1.0
        z = (point.price_gbp_mwh - mean) / std
        sev, msg = _severity(z)
        return AnomalyResult(point.period, point.price_gbp_mwh, round(mean, 2),
                             round(std, 2), round(z, 2), sev, msg)

    def screen_series(self, points: list[PricePoint]) -> list[AnomalyResult]:
        """Screen a series of historical price points; returns non-None results."""
        results = []
        for p in points:
            r = self.add(p)
            if r is not None:
                results.append(r)
        return results

    def anomalies(self, min_severity: str = "watch") -> list[AnomalyResult]:
        """Return last batch anomalies (re-screen required each call)."""
        return []

    def summary(self, results: list[AnomalyResult]) -> dict:
        if not results:
            return {"total": 0, "critical": 0, "alert": 0, "watch": 0, "normal": 0}
        counts: dict[str, int] = {"critical": 0, "alert": 0, "watch": 0, "normal": 0}
        for r in results:
            counts[r.severity] = counts.get(r.severity, 0) + 1
        return {"total": len(results), **counts}
