"""Phase MW — Payment timing driven by household income stress.

Generates synthetic payment records that are observable to the company via
PaymentBehaviourAnalytics. Income stress (SIM ground truth) cascades into
payment timing patterns; the company sees the payment records, not the stress level.

Epistemic constraint: income_stress is SIM ground truth. Payment records
(due_date, payment_date, result) are the observable signal.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

from simulation.household import IncomeStress


# Days after due date that a late payment arrives.
_PAYMENT_DELAY_DAYS: dict[IncomeStress, tuple[int, int]] = {
    IncomeStress.LOW:      (7, 14),
    IncomeStress.MODERATE: (14, 45),
    IncomeStress.HIGH:     (30, 90),
}

# Probability of direct debit failure per payment event.
_DD_FAILURE_PROBABILITY: dict[IncomeStress, float] = {
    IncomeStress.LOW:      0.03,
    IncomeStress.MODERATE: 0.12,
    IncomeStress.HIGH:     0.35,
}

# Probability of paying on time (on/before due date) given DD did not fail.
_ON_TIME_PROBABILITY: dict[IncomeStress, float] = {
    IncomeStress.LOW:      0.92,
    IncomeStress.MODERATE: 0.50,
    IncomeStress.HIGH:     0.10,
}

# Bad debt rate multiplier by stress level.
# None covers I&C / SME customers that have no household income stress.
_BAD_DEBT_MULTIPLIER: dict[IncomeStress | None, float] = {
    IncomeStress.LOW:      1.0,
    IncomeStress.MODERATE: 1.5,
    IncomeStress.HIGH:     3.0,
}


def stress_bad_debt_multiplier(income_stress: IncomeStress | None) -> float:
    """Return the bad-debt rate multiplier for the given income stress level.

    Returns 1.0 for None (I&C/SME customers without household stress).
    """
    return _BAD_DEBT_MULTIPLIER.get(income_stress, 1.0)


def generate_payment_record(
    customer_id: str,
    due_date: date,
    amount_gbp: float,
    income_stress: IncomeStress | None,
    rng: random.Random,
) -> dict:
    """Generate a synthetic payment record for a billing due date.

    Args:
        customer_id: The customer's ID.
        due_date: The date by which payment is due.
        amount_gbp: Amount billed.
        income_stress: Household income stress level. None treated as LOW.
        rng: Seeded RNG for reproducible results.

    Returns:
        Dict with: customer_id, due_date, amount_gbp, result (ON_TIME/LATE/DD_FAILED),
                   payment_date (date or None), amount_paid (float).
    """
    stress = income_stress if income_stress is not None else IncomeStress.LOW

    if rng.random() < _DD_FAILURE_PROBABILITY[stress]:
        return {
            "customer_id": customer_id,
            "due_date": due_date,
            "result": "DD_FAILED",
            "payment_date": None,
            "amount_gbp": amount_gbp,
            "amount_paid": 0.0,
        }

    if rng.random() < _ON_TIME_PROBABILITY[stress]:
        return {
            "customer_id": customer_id,
            "due_date": due_date,
            "result": "ON_TIME",
            "payment_date": due_date,
            "amount_gbp": amount_gbp,
            "amount_paid": amount_gbp,
        }

    delay_min, delay_max = _PAYMENT_DELAY_DAYS[stress]
    delay_days = rng.randint(delay_min, delay_max)
    return {
        "customer_id": customer_id,
        "due_date": due_date,
        "result": "LATE",
        "payment_date": due_date + timedelta(days=delay_days),
        "amount_gbp": amount_gbp,
        "amount_paid": amount_gbp,
    }
