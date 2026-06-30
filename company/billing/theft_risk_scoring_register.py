"""Energy Theft Risk Scoring Register (Phase GH).

Pre-investigation risk scoring for potential energy theft, operating
upstream of energy_theft_book.py (which handles confirmed-theft cases
and DNO notification obligations under GS(SS)5).

UK energy theft context:
  - Estimated £400M+ annual industry loss to electricity theft (UK Energy)
  - Cannabis cultivation is the single largest identified category
  - Profile triggers: very high consumption at night, no occupancy sensors,
    very low unit rates claimed by meter (meter bypassed), voltage
    anomalies indicating line tapping
  - Suppression obligations: high-risk accounts should NOT be placed on
    self-read or smart meter self-dispatch without field investigation

Supplier practice:
  - Risk scores are produced by automated models (rule-based or ML)
  - Threshold-based dispatch: e.g. CRITICAL (>=80) → immediate inspection
  - Regulatory expectation: GS(SS)5 requires notification of suspected theft
    to the relevant DNO; the risk score is the internal trigger for that
    process to begin.

Distinct from energy_theft_book.py which tracks cases once investigation
has commenced. A scored account becomes a theft_book case when
inspection is triggered.

Score-to-level mapping (industry-approximate):
  - 0-29: LOW — normal variance, no action
  - 30-59: MEDIUM — increased monitoring, next planned site visit
  - 60-79: HIGH — priority site visit required
  - 80-100: CRITICAL — immediate inspection / suspend remote access
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

_LOW_THRESHOLD = 30
_HIGH_THRESHOLD = 60
_CRITICAL_THRESHOLD = 80


class TheftRiskIndicator(str, Enum):
    HIGH_CONSUMPTION_SPIKE = "high_consumption_spike"
    LOW_CONSUMPTION_ANOMALY = "low_consumption_anomaly"        # meter bypass suspected
    METER_BYPASS_SUSPECTED = "meter_bypass_suspected"
    VOLTAGE_VARIANCE = "voltage_variance"                       # line tapping
    PAYMENT_PATTERN_ANOMALY = "payment_pattern_anomaly"        # consistent underpayment
    EMPTY_PROPERTY_HIGH_CONSUMPTION = "empty_property_high_consumption"
    CANNABIS_GROW_PROFILE = "cannabis_grow_profile"            # high/consistent 24h load
    NIGHT_PEAK_ANOMALY = "night_peak_anomaly"
    SMART_METER_TAMPER_ALERT = "smart_meter_tamper_alert"      # DCC notification


class TheftRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def _derive_risk_level(score: float) -> TheftRiskLevel:
    if score >= _CRITICAL_THRESHOLD:
        return TheftRiskLevel.CRITICAL
    if score >= _HIGH_THRESHOLD:
        return TheftRiskLevel.HIGH
    if score >= _LOW_THRESHOLD:
        return TheftRiskLevel.MEDIUM
    return TheftRiskLevel.LOW


@dataclass(frozen=True)
class TheftRiskScoringRecord:
    record_id: str                                  # TRISK-NNNNN
    account_id: str
    score_date: dt.date
    risk_score: float                               # 0-100
    indicators: Tuple[TheftRiskIndicator, ...]
    notes: str = ""
    inspection_triggered: bool = False
    inspection_triggered_date: Optional[dt.date] = None

    @property
    def risk_level(self) -> TheftRiskLevel:
        return _derive_risk_level(self.risk_score)

    @property
    def requires_inspection(self) -> bool:
        return self.risk_level in (TheftRiskLevel.HIGH, TheftRiskLevel.CRITICAL)

    @property
    def is_critical(self) -> bool:
        return self.risk_level == TheftRiskLevel.CRITICAL

    def risk_summary(self) -> str:
        inds = ", ".join(i.value for i in self.indicators) or "none"
        return (
            f"TRISK {self.record_id} acct={self.account_id} "
            f"score={self.risk_score:.0f} ({self.risk_level.value}) "
            f"indicators=[{inds}] inspection={self.inspection_triggered}"
        )


class TheftRiskScoringRegister:

    def __init__(self) -> None:
        self._records: List[TheftRiskScoringRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"TRISK-{self._counter:05d}"

    def score_account(
        self,
        account_id: str,
        score_date: dt.date,
        risk_score: float,
        indicators: Tuple[TheftRiskIndicator, ...] = (),
        notes: str = "",
    ) -> TheftRiskScoringRecord:
        if not (0.0 <= risk_score <= 100.0):
            raise ValueError(f"risk_score must be 0-100; got {risk_score}")
        record = TheftRiskScoringRecord(
            record_id=self._next_id(),
            account_id=account_id,
            score_date=score_date,
            risk_score=risk_score,
            indicators=indicators,
            notes=notes,
        )
        self._records.append(record)
        return record

    def _update(self, record_id: str, **kwargs) -> TheftRiskScoringRecord:
        for i, r in enumerate(self._records):
            if r.record_id == record_id:
                updated = TheftRiskScoringRecord(
                    record_id=r.record_id,
                    account_id=r.account_id,
                    score_date=r.score_date,
                    risk_score=r.risk_score,
                    indicators=r.indicators,
                    notes=kwargs.get("notes", r.notes),
                    inspection_triggered=kwargs.get("inspection_triggered", r.inspection_triggered),
                    inspection_triggered_date=kwargs.get("inspection_triggered_date", r.inspection_triggered_date),
                )
                self._records[i] = updated
                return updated
        raise KeyError(f"Theft risk scoring record {record_id} not found")

    def trigger_inspection(
        self, record_id: str, triggered_date: dt.date
    ) -> TheftRiskScoringRecord:
        return self._update(
            record_id,
            inspection_triggered=True,
            inspection_triggered_date=triggered_date,
        )

    def current_score_for(self, account_id: str) -> Optional[TheftRiskScoringRecord]:
        """Most recent scoring record for the account."""
        acct_records = [r for r in self._records if r.account_id == account_id]
        return max(acct_records, key=lambda r: r.score_date) if acct_records else None

    def all_scores_for(self, account_id: str) -> List[TheftRiskScoringRecord]:
        return [r for r in self._records if r.account_id == account_id]

    def accounts_above_threshold(self, threshold: float) -> List[TheftRiskScoringRecord]:
        """Latest record per account where risk_score >= threshold."""
        seen: dict = {}
        for r in sorted(self._records, key=lambda x: x.score_date):
            seen[r.account_id] = r
        return [r for r in seen.values() if r.risk_score >= threshold]

    def critical_accounts(self) -> List[TheftRiskScoringRecord]:
        return [r for r in self._records if r.is_critical]

    def inspection_required(self) -> List[TheftRiskScoringRecord]:
        """Records where inspection required but not yet triggered."""
        return [r for r in self._records if r.requires_inspection and not r.inspection_triggered]

    def by_indicator(self, indicator: TheftRiskIndicator) -> List[TheftRiskScoringRecord]:
        return [r for r in self._records if indicator in r.indicators]

    def total_high_risk_accounts(self) -> int:
        seen = {}
        for r in sorted(self._records, key=lambda x: x.score_date):
            seen[r.account_id] = r
        return sum(1 for r in seen.values() if r.risk_level in (TheftRiskLevel.HIGH, TheftRiskLevel.CRITICAL))

    def risk_scoring_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_critical = len(self.critical_accounts())
        n_inspect = len(self.inspection_required())
        high_risk = self.total_high_risk_accounts()
        return (
            f"Theft Risk Scoring Register ({as_of}): {n} records, "
            f"{high_risk} high-risk accounts ({n_critical} CRITICAL), "
            f"{n_inspect} pending inspections."
        )
