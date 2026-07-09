"""Customer lifecycle event log — Phase 6b / Phase 7e.

Provides `roll_lifecycle_event()`, called by `run_phase2b.main()` at each
billing-account renewal point (electricity legs only; gas legs share the
billing-account decision — see `saas.customer_reaction._billing_account_id`).

The roll is fully deterministic: `random.Random(f"{billing_account}_{term_start}")`.
Two identical runs always produce the same event sequence. Tests can force
specific outcomes by patching `_RANDOM_CLASS` or seeding via a known
`customer_id` + `term_start_str` combination.

Phase 7e adds a second deterministic roll when an account churns: did we win
the home-mover's business? Seed: `f"win_{billing_account}_{term_start_str}"`.
`home_move_won` appears on every event dict (False for renewals; True/False for
churns). When True, `run_phase2b.main()` activates the successor customer.

Architecture note: this module sits at the interface between the sim (raw
settlement records) and the SaaS layer (churn/win-rate models). It imports
from `saas/` (churn_model, home_move_win_rate, customer_reaction) — the same
cross-seam boundary as `simulation/run_phase4c_on_phase2b.py`. This is
intentional: Phase 6b turns existing *risk scores* into actual *events*, and
the models that compute those scores already live in `saas/`.
"""
import random as _random
from datetime import date

from company.crm.churn_model import estimate_churn_probability
from saas.churn_model import build_churn_risk
from saas.customer_reaction import _billing_account_id
from saas.home_move_win_rate import build_home_move_win_rates
from simulation.household import IncomeStress
from simulation.market_switching_propensity import market_switching_multiplier
from simulation.switching_propensity import adjust_churn_probability
from simulation.satisfaction_churn import adjust_churn_for_satisfaction

PRICE_DIFFERENTIAL_PCT = 0.0  # matches run_phase4c_on_phase2b.py


def roll_lifecycle_event(
    customer_id: str,
    term_start_str: str,
    commodity: str,
    records_so_far: list[dict],
    customers: list[dict],
    price_differential_pct: float = PRICE_DIFFERENTIAL_PCT,
    old_rate_gbp_per_mwh: float | None = None,
    new_rate_gbp_per_mwh: float | None = None,
    retention_modifier: float | None = None,
    precomputed_company_estimate: float | None = None,
    passive_churn_cap: float | None = None,
    income_stress: IncomeStress | None = None,
    satisfaction_score: float | None = None,
    market_year: int | None = None,
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
       realized_churn_probability, random_roll}

    `churn_probability` is the raw, pre-adjustment SIM base rate (bill-shock
    driven, from `saas.churn_model`) -- informational only, never what the
    dice roll actually used. `effective_retention_probability` is the true
    probability used for the roll, after every adjustment (passive cap,
    market conditions, income stress, satisfaction, retention offer).
    `realized_churn_probability` (Phase QA) is `1 - effective_retention_probability`
    captured BEFORE the retention-offer adjustment -- the correct ground
    truth to compare a company churn estimate against, since the estimate is
    computed before the company decides whether to make an offer.

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
    effective_p_retain = renewal_data["effective_retention_probability"]
    # Phase 33: passive renewers have lower SIM ground-truth churn — cap the
    # churn probability at passive_churn_cap before applying any retention modifier.
    if passive_churn_cap is not None:
        p_churn_raw = 1.0 - effective_p_retain
        effective_p_retain = 1.0 - min(p_churn_raw, passive_churn_cap)
    # Phase NS: apply market-conditions switching multiplier (savings elasticity).
    # Suppresses churn in crisis years (2022: no cheaper alternatives); amplifies in
    # high-competition years (2016-2018). Applied before income_stress so market
    # opportunity ceiling is set first, then individual customer frictions modify it.
    if market_year is not None:
        p_churn_market = (1.0 - effective_p_retain) * market_switching_multiplier(market_year)
        effective_p_retain = 1.0 - min(p_churn_market, 0.95)
    # Phase MZ: apply income_stress switching propensity before retention modifier.
    # Layer 2 dimension 3 (2026-07-09): tenure applied in the same call --
    # renters switch less (see switching_propensity.py's module note).
    if income_stress is not None:
        from simulation.household_segments import tenure_for_customer
        tenure = tenure_for_customer(billing_account).value
        p_churn_stress = adjust_churn_probability(1.0 - effective_p_retain, income_stress, tenure)
        effective_p_retain = 1.0 - p_churn_stress
    # Phase NF: apply SIM-side satisfaction score before retention modifier
    if satisfaction_score is not None:
        p_churn_sat = adjust_churn_for_satisfaction(1.0 - effective_p_retain, satisfaction_score)
        effective_p_retain = 1.0 - p_churn_sat
    # Phase QA: capture the true pre-retention-offer probability. This is what
    # the company's churn estimate (computed before any retention decision) is
    # actually trying to predict -- comparing it against a probability that
    # already bakes in the company's own retention action would be circular
    # (the company would look "wrong" purely because its own intervention
    # worked).
    effective_p_retain_pre_offer = effective_p_retain
    if retention_modifier is not None:
        p_churn_base = 1.0 - effective_p_retain
        effective_p_retain = 1.0 - p_churn_base * (1.0 - retention_modifier)
    retained = roll <= effective_p_retain

    # Phase 7e: when an account churns, roll whether we win the home-mover's
    # business. Separate seed so it never interferes with the churn roll.
    home_move_won = False
    if not retained:
        win_roll = _random.Random(f"win_{billing_account}_{term_start_str}").random()
        home_move_won = win_roll <= renewal_data["win_probability"]

    # Phase 11b: company's observable-data churn estimate
    company_churn_estimate: float | None = precomputed_company_estimate
    churn_estimate_error_pct: float | None = None
    if company_churn_estimate is None and old_rate_gbp_per_mwh is not None and new_rate_gbp_per_mwh is not None:
        acq_date = next(
            (c["acquisition_date"] for c in customers if c["customer_id"] == billing_account),
            term_start_str,
        )
        tenure_years = (date.fromisoformat(term_start_str) - date.fromisoformat(acq_date)).days / 365.25
        company_churn_estimate = round(
            estimate_churn_probability(old_rate_gbp_per_mwh, new_rate_gbp_per_mwh, tenure_years), 4
        )
    # Phase QA: realized_churn_probability is the true, fully-adjusted (passive
    # cap / market conditions / income stress / satisfaction) probability that
    # was actually rolled against, captured BEFORE any retention-offer effect.
    # Prior to this phase, churn_estimate_error_pct compared the company's
    # estimate against renewal_data["churn_probability"] -- the raw, pre-
    # adjustment bill-shock base rate that was never the number the dice roll
    # used. That mismatch was the source of the apparent systematic ~-80%
    # "underestimate" pattern the company's model showed at nearly every
    # renewal: the comparison was against a number the SIM itself discarded.
    realized_churn_probability = round(1.0 - effective_p_retain_pre_offer, 4)
    if company_churn_estimate is not None:
        sim_prob = realized_churn_probability
        if sim_prob:
            churn_estimate_error_pct = round(
                (company_churn_estimate - sim_prob) / sim_prob, 4
            )

    return {
        "customer_id": billing_account,
        "event_date": term_start_str,
        "commodity": commodity,
        "event_type": "renewed" if retained else "churned",
        "churn_probability": round(renewal_data["churn_probability"], 4),
        "win_probability": round(renewal_data["win_probability"], 4),
        "effective_retention_probability": round(effective_p_retain, 4),
        "realized_churn_probability": realized_churn_probability,
        "random_roll": round(roll, 4),
        "home_move_won": home_move_won,
        "company_churn_estimate": company_churn_estimate,
        "churn_estimate_error_pct": churn_estimate_error_pct,
        "retention_offered": retention_modifier is not None,
        "market_switching_multiplier": round(market_switching_multiplier(market_year), 4) if market_year is not None else None,
    }
