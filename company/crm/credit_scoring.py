"""Customer credit scoring and risk tier classification.

UK energy suppliers routinely credit-check new domestic customers at
onboarding to determine:
  - Whether a deposit is required (common for customers with CCJs or
    County Court Judgements, or a history of missed energy payments)
  - Whether a pre-payment meter (PPM) is appropriate as a last resort

Credit tiers map to deposit requirements and collections escalation
thresholds. The company cannot see simulation credit scores — these
are derived from observable signals: payment history, direct debit
status, account age, and complaint history.

Credit tier definitions:
  - PRIME: clean payment history, DD active, no arrears
  - STANDARD: minor late payment history, or new customer (no history)
  - SUBPRIME: missed payments (1-2 episodes), DD failed, arrears <90 days
  - HIGH_RISK: persistent arrears, bad debt history, 2+ DD failures

Pre-payment meter (PPM) is recommended for HIGH_RISK customers who
cannot supply a deposit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


_DEPOSIT_MULTIPLIERS = {
    "PRIME": 0.0,       # no deposit
    "STANDARD": 0.0,    # no deposit (new or clean-ish)
    "SUBPRIME": 1.0,    # 1 month estimated annual bill
    "HIGH_RISK": 2.0,   # 2 months estimated annual bill
}

_MONTHLY_BILL_EST_GBP = 150.0  # approx UK average monthly energy bill (2024)


@dataclass
class CreditAssessment:
    customer_id: str
    assessment_date: str
    tier: Literal["PRIME", "STANDARD", "SUBPRIME", "HIGH_RISK"]
    score: int         # 0-100 (higher = better)
    deposit_gbp: float
    ppm_recommended: bool
    flags: list[str]   # contributing signals
    assessor: str = "automated"

    @property
    def tier_label(self) -> str:
        labels = {
            "PRIME": "Prime — no deposit required",
            "STANDARD": "Standard — no deposit required",
            "SUBPRIME": "Sub-prime — deposit required",
            "HIGH_RISK": "High risk — deposit or PPM",
        }
        return labels[self.tier]


def assess_credit(
    customer_id: str,
    assessment_date: str,
    dd_active: bool,
    missed_payments: int,
    account_age_days: int,
    has_bad_debt_history: bool,
    arrears_gbp: float = 0.0,
    annual_bill_est_gbp: float = _MONTHLY_BILL_EST_GBP * 12,
) -> CreditAssessment:
    """Derive credit tier from observable payment signals."""
    flags = []
    score = 100

    if has_bad_debt_history:
        score -= 40
        flags.append("bad_debt_history")

    if missed_payments >= 3:
        score -= 30
        flags.append(f"missed_payments:{missed_payments}")
    elif missed_payments >= 1:
        score -= 15
        flags.append(f"missed_payments:{missed_payments}")

    if not dd_active:
        score -= 10
        flags.append("no_direct_debit")

    if arrears_gbp > 200:
        score -= 20
        flags.append(f"arrears:{arrears_gbp:.0f}")
    elif arrears_gbp > 50:
        score -= 10
        flags.append(f"arrears:{arrears_gbp:.0f}")

    if account_age_days < 90:
        score -= 5
        flags.append("new_account")

    score = max(0, min(100, score))

    if score >= 80:
        tier = "PRIME"
    elif score >= 60:
        tier = "STANDARD"
    elif score >= 35:
        tier = "SUBPRIME"
    else:
        tier = "HIGH_RISK"

    monthly_est = annual_bill_est_gbp / 12.0
    deposit = round(monthly_est * _DEPOSIT_MULTIPLIERS[tier], 2)
    ppm = tier == "HIGH_RISK" and deposit > 0

    return CreditAssessment(
        customer_id=customer_id,
        assessment_date=assessment_date,
        tier=tier,
        score=score,
        deposit_gbp=deposit,
        ppm_recommended=ppm,
        flags=flags,
    )
