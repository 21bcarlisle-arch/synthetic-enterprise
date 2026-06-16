"""Customer lifecycle event log — Phase 6b.

Provides `roll_lifecycle_event()`, called by `run_phase2b.main()` at each
billing-account renewal point (electricity legs only; gas legs share the
billing-account decision — see `saas.customer_reaction._billing_account_id`).

The roll is fully deterministic: `random.Random(f"{billing_account}_{term_start}")`.
Two identical runs always produce the same event sequence. Tests can force
specific outcomes by patching `_RANDOM_CLASS` or seeding via a known
`customer_id` + `term_start_str` combination.

Architecture note: this module sits at the interface between the sim (raw
settlement records) and the SaaS layer (churn/win-rate models). It imports
from `saas/` (churn_model, home_move_win_rate, customer_reaction) — the same
cross-seam boundary as `simulation/run_phase4c_on_phase2b.py`. This is
intentional: Phase 6b turns existing *risk scores* into actual *events*, and
the models that compute those scores already live in `saas/`.
"""
import random as _random

from saas.churn_model import build_churn_risk
from saas.customer_reaction import _billing_account_id
from saas.home_move_win_rate import build_home_move_win_rates

PRICE_DIFFERENTIAL_PCT = 0.0  # matches run_phase4c_on_phase2b.py


def roll_lifecycle_event(
    customer_id: str,
    term_start_str: str,
    commodity: str,
    records_so_far: list[dict],
    customers: list[dict],
    price_differential_pct: float = PRICE_DIFFERENTIAL_PCT,
) -> dict | None:
    """Compute and roll the churn/renewal event for a billing account at a
    renewal point.

    Call only for electricity legs (`commodity == "electricity"`) at
    `term_index >= 1` — gas legs share the billing-account-level decision.

    `records_so_far` must contain only settlement records up to (not
    including) the current term start — Point-in-Time safe by construction
    when called from `run_phase2b.main()` before the current term is settled.

    Returns a lifecycle event dict:
      {customer_id (billing account), event_date, commodity,
       event_type: "renewed"|"churned",
       churn_probability, win_probability, effective_retention_probability,
       random_roll}

    Returns None if no renewal data is available in the churn model (can
    happen when `records_so_far` is too short to compute bill-shock history
    for this account's first renewal point).
    """
    billing_account = _billing_account_id(customer_id)
    term_month = term_start_str[:7]

    churn_risk = build_churn_risk(records_so_far, customers)
    win_rates = build_home_move_win_rates(churn_risk, customers, price_differential_pct)

    renewal_data = next(
        (r for r in win_rates.get(billing_account, []) if r["renewal_period"] == term_month),
        None,
    )
    if renewal_data is None:
        return None

    roll = _random.Random(f"{billing_account}_{term_start_str}").random()
    retained = roll <= renewal_data["effective_retention_probability"]

    return {
        "customer_id": billing_account,
        "event_date": term_start_str,
        "commodity": commodity,
        "event_type": "renewed" if retained else "churned",
        "churn_probability": round(renewal_data["churn_probability"], 4),
        "win_probability": round(renewal_data["win_probability"], 4),
        "effective_retention_probability": round(renewal_data["effective_retention_probability"], 4),
        "random_roll": round(roll, 4),
    }
