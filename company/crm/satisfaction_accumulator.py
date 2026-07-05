"""Company-side customer satisfaction accumulator (Dim 4 emotional).

Tracks rolling satisfaction/trust per customer from observable company-side signals:
- Bill shock events (billing records): trust drops
- CSS survey scores (css_tracker): anchors to measured satisfaction
- Complaint raised (complaint register): significant trust drop
- Complaint resolved satisfactorily: partial trust recovery
- Time without negative events: slow mean-reversion to baseline

This is a company-side model: it reads only observables the company possesses,
not SIM ground truth (income_stress, actual churn probability, SIM prices).
Consistent with the SIM/company epistemic barrier.

Observable inputs only:
  bill_shock (bool from billing records)
  css_score (float 0-10 from css_tracker surveys)
  complaint event (complaint register: raised/resolved)
"""
from __future__ import annotations

_BASELINE_SATISFACTION = 0.70
_BILL_SHOCK_DELTA = -0.05
_COMPLAINT_RAISED_DELTA = -0.10
_COMPLAINT_RESOLVED_DELTA = +0.05
_CSS_GOOD_THRESHOLD = 7.0   # CSS score >= 7 is positive
_CSS_POOR_THRESHOLD = 4.0   # CSS score < 4 is negative
_CSS_GOOD_DELTA = +0.05
_CSS_POOR_DELTA = -0.05
_MONTHLY_DECAY_RATE = 0.01  # reversion toward baseline per month of no events
_LOW_SATISFACTION_THRESHOLD = 0.50
_MIN_SATISFACTION = 0.0
_MAX_SATISFACTION = 1.0


def _clamp(value: float) -> float:
    return max(_MIN_SATISFACTION, min(_MAX_SATISFACTION, value))


class CustomerSatisfactionAccumulator:
    """Accumulate observable signals to derive a rolling satisfaction score.

    Satisfaction starts at the baseline (0.70) on first event.
    All deltas are applied immediately; decay is applied per elapsed_months.
    """

    def __init__(self) -> None:
        self._scores: dict[str, float] = {}
        self._trajectory: dict[str, dict[int, float]] = {}

    def _get_or_init(self, customer_id: str) -> float:
        if customer_id not in self._scores:
            self._scores[customer_id] = _BASELINE_SATISFACTION
        return self._scores[customer_id]

    def record_bill_shock(self, customer_id: str) -> None:
        score = self._get_or_init(customer_id)
        self._scores[customer_id] = _clamp(score + _BILL_SHOCK_DELTA)

    def record_css_score(self, customer_id: str, css_score: float) -> None:
        score = self._get_or_init(customer_id)
        if css_score >= _CSS_GOOD_THRESHOLD:
            self._scores[customer_id] = _clamp(score + _CSS_GOOD_DELTA)
        elif css_score < _CSS_POOR_THRESHOLD:
            self._scores[customer_id] = _clamp(score + _CSS_POOR_DELTA)

    def record_complaint_raised(self, customer_id: str) -> None:
        score = self._get_or_init(customer_id)
        self._scores[customer_id] = _clamp(score + _COMPLAINT_RAISED_DELTA)

    def record_complaint_resolved(self, customer_id: str) -> None:
        score = self._get_or_init(customer_id)
        self._scores[customer_id] = _clamp(score + _COMPLAINT_RESOLVED_DELTA)

    def apply_monthly_decay(self, customer_id: str, months: int = 1) -> None:
        """Revert satisfaction toward baseline at _MONTHLY_DECAY_RATE per month."""
        score = self._get_or_init(customer_id)
        for _ in range(months):
            if score > _BASELINE_SATISFACTION:
                score = max(_BASELINE_SATISFACTION, score - _MONTHLY_DECAY_RATE)
            elif score < _BASELINE_SATISFACTION:
                score = min(_BASELINE_SATISFACTION, score + _MONTHLY_DECAY_RATE)
        self._scores[customer_id] = score

    def get_satisfaction(self, customer_id: str) -> float:
        return self._get_or_init(customer_id)

    def is_low_satisfaction(self, customer_id: str) -> bool:
        return self.get_satisfaction(customer_id) < _LOW_SATISFACTION_THRESHOLD

    def low_satisfaction_customers(self) -> list[str]:
        return [cid for cid in self._scores if self.is_low_satisfaction(cid)]

    def record_year_snapshot(self, customer_id: str, year: int) -> None:
        """Snapshot the current satisfaction score under `year`.

        Idempotent per (customer_id, year): a later call for the same year
        overwrites the earlier value rather than appending a duplicate, since
        satisfaction can be read multiple times within one calendar year.
        """
        score = self.get_satisfaction(customer_id)
        self._trajectory.setdefault(customer_id, {})[year] = score

    def get_trajectory(self, customer_id: str) -> list[dict]:
        """Return [{"year": int, "satisfaction_score": float}, ...] sorted by year."""
        years = self._trajectory.get(customer_id, {})
        return [
            {"year": yr, "satisfaction_score": round(years[yr], 4)}
            for yr in sorted(years)
        ]
