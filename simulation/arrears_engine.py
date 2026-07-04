"""Phase QD -- shared payment-outcome and arrears-escalation engine.

Single source of truth for "does this invoice get paid, and if not, does the
arrears case eventually resolve or get written off" -- consumed by both:

  - `tools.generate_billing_ledger` (per-customer invoice/payment ledger), and
  - `simulation.run_phase4c_on_phase2b` (emergent bad debt fed into the board
    P&L's `bad_debt_gbp` / `net_margin_gbp`, replacing the flat
    `saas.cost_to_serve.get_bad_debt_rate()` formula that previously stood in
    for simulated payment behaviour).

Before this phase these were two independently-calibrated RNG-driven models
that happened to use similar probabilities. Moving the primitives here and
having both callers iterate the same `bills` in the same sorted order with a
single seeded RNG means they draw the identical sequence of outcomes -- the
ledger and the P&L bad debt figure are now provably the same source of truth.

Payment method / outcome probabilities:
  I&C / SME (BACS/CHAPS) -- 92% on-time, 7.3% late, 0.7% formal dispute.
  Residential (direct debit) -- driven by income_stress_trajectory:
    LOW -> 92% on-time, 3% DD failure; MODERATE -> 50% / 12%; HIGH -> 10% / 35%.

Arrears escalation (opened the day payment fails):
  Residential:  DD_FAILED -> FIRST_NOTICE(+7d) -> SECOND_NOTICE(+21d)
                -> RESOLVED(+45d) | WRITTEN_OFF(+90d)
  I&C dispute:  INVOICE_DISPUTED -> DISPUTE_NOTICE(+14d)
                -> PAYMENT_PLAN_AGREED(+30d) | WRITTEN_OFF(+60d)

A case resolves if the customer is retained past the case's lifetime, and is
written off if the customer has churned by the end of the run -- the same
"eventually_resolved = cid not in churned" rule Phase PP established.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

PAYMENT_TERMS_DAYS = 14

_DD_FAILURE_PROB = {"LOW": 0.03, "MODERATE": 0.12, "HIGH": 0.35}
_ON_TIME_PROB = {"LOW": 0.92, "MODERATE": 0.50, "HIGH": 0.10}
_LATE_DAYS = {"LOW": (3, 14), "MODERATE": (14, 45), "HIGH": (30, 90)}

_CORP_BACS_ON_TIME_PROB = 0.92
_CORP_BACS_LATE_PROB = 0.073
_CORP_BACS_DISPUTE_PROB = 0.007
_CORP_LATE_DAYS = (14, 45)
_IC_SEGMENTS = ("ic", "I&C")


def stress_for_year(behavioral: dict, year: int) -> str:
    trajectory = behavioral.get("income_stress_trajectory") or []
    for entry in trajectory:
        if entry.get("year") == year:
            return (entry.get("stress") or "LOW").upper()
    return "LOW"


def payment_method(segment: str, amount_gbp: float) -> str:
    if segment in _IC_SEGMENTS:
        return "chaps" if amount_gbp >= 10000 else "bacs"
    if segment == "sme":
        return "bacs"
    return "direct_debit"


def payment_outcome(method: str, stress: str, rng: random.Random, segment: str = "resi"):
    """Returns (outcome, days_late). outcome is one of success/failed/dispute."""
    if method in ("bacs", "chaps"):
        if segment in _IC_SEGMENTS:
            r = rng.random()
            if r < _CORP_BACS_ON_TIME_PROB:
                return ("success", 0)
            elif r < 1.0 - _CORP_BACS_DISPUTE_PROB:
                return ("success", rng.randint(*_CORP_LATE_DAYS))
            else:
                return ("dispute", 0)
        return ("success", 0)
    dd_fail_prob = _DD_FAILURE_PROB.get(stress, 0.03)
    if rng.random() < dd_fail_prob:
        return ("failed", 0)
    on_time_prob = _ON_TIME_PROB.get(stress, 0.92)
    if rng.random() < on_time_prob:
        return ("success", 0)
    lo, hi = _LATE_DAYS.get(stress, (3, 14))
    return ("success", rng.randint(lo, hi))


def arrears_stages(arrears_gbp: float, due_date: date, eventually_resolved: bool) -> list[dict]:
    stages = [
        {"stage": "DD_FAILED", "date": due_date.isoformat(), "note": "Direct debit returned"},
        {"stage": "FIRST_NOTICE", "date": (due_date + timedelta(days=7)).isoformat(),
         "note": "First overdue notice -- GBP%.2f outstanding" % arrears_gbp},
        {"stage": "SECOND_NOTICE", "date": (due_date + timedelta(days=21)).isoformat(),
         "note": "Second notice -- payment plan offered"},
    ]
    if eventually_resolved:
        stages.append({"stage": "RESOLVED", "date": (due_date + timedelta(days=45)).isoformat(),
                        "note": "Arrears cleared via payment plan"})
    else:
        stages.append({"stage": "WRITTEN_OFF", "date": (due_date + timedelta(days=90)).isoformat(),
                        "note": "Debt written off -- bad debt provision raised"})
    return stages


def ic_arrears_stages(arrears_gbp: float, due_date: date, eventually_resolved: bool) -> list[dict]:
    stages = [
        {"stage": "INVOICE_DISPUTED", "date": due_date.isoformat(),
         "note": "Invoice disputed -- GBP%.2f under formal review" % arrears_gbp},
        {"stage": "DISPUTE_NOTICE", "date": (due_date + timedelta(days=14)).isoformat(),
         "note": "Dispute notice raised -- escalated to accounts receivable"},
    ]
    if eventually_resolved:
        stages.append({"stage": "PAYMENT_PLAN_AGREED",
                        "date": (due_date + timedelta(days=30)).isoformat(),
                        "note": "Payment plan agreed -- arrears to be settled over 60 days"})
    else:
        stages.append({"stage": "WRITTEN_OFF",
                        "date": (due_date + timedelta(days=60)).isoformat(),
                        "note": "Debt written off -- bad debt provision raised"})
    return stages


def compute_emergent_bad_debt(bills: list[dict], behavioral: dict, churned_ids: set[str],
                               seed: int = 42) -> dict[tuple[str, int], float]:
    """Run the shared payment/arrears model over `bills` and return real,
    emergent bad debt: GBP written off, keyed by (customer_id, write_off_year).

    Iterates `bills` in the exact sorted order and RNG seed that
    `tools.generate_billing_ledger.generate()` uses, so a case that reaches
    WRITTEN_OFF here reaches WRITTEN_OFF there too, for the same GBP amount.
    """
    rng = random.Random(seed)
    result: dict[tuple[str, int], float] = {}
    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        year = int(period_end[:4])

        issue_date = date.fromisoformat(period_end)
        due_date = issue_date + timedelta(days=PAYMENT_TERMS_DAYS)
        stress = stress_for_year(behavioral.get(cid) or {}, year)
        method = payment_method(segment, amount)
        outcome, _days_late = payment_outcome(method, stress, rng, segment)

        if outcome not in ("failed", "dispute"):
            continue
        will_be_written_off = cid in churned_ids
        if not will_be_written_off:
            continue
        stages = (arrears_stages if outcome == "failed" else ic_arrears_stages)(
            amount, due_date, False
        )
        write_off_date = next(s["date"] for s in stages if s["stage"] == "WRITTEN_OFF")
        key = (cid, int(write_off_date[:4]))
        result[key] = round(result.get(key, 0.0) + amount, 2)
    return result


def apply_emergent_bad_debt(all_records: list[dict], emergent_by_customer_year: dict[tuple[str, int], float]) -> None:
    """Replace the flat-rate `bad_debt_gbp` already baked into `all_records`
    (by `simulation.run_phase2b`'s real-time settlement loop) with the real
    emergent figure from `compute_emergent_bad_debt`, then carry the resulting
    net_margin_gbp delta forward through every later record's cumulative
    `treasury_cash_balance_gbp`. Mutates `all_records` in place.

    Applies each customer-year's correction as a delta on top of whatever
    treasury balance was already recorded, rather than re-deriving the
    portfolio's starting treasury -- that keeps this module decoupled from
    `simulation.run_phase2b`'s constants and correct regardless of exactly
    how `all_records` was accumulated.
    """
    old_by_cy: dict[tuple[str, int], float] = {}
    last_index_by_cy: dict[tuple[str, int], int] = {}
    for i, rec in enumerate(all_records):
        key = (rec["customer_id"], int(rec["settlement_date"][:4]))
        old_by_cy[key] = old_by_cy.get(key, 0.0) + rec.get("bad_debt_gbp", 0.0)
        last_index_by_cy[key] = i

    delta_at_index: dict[int, float] = {}
    for key in set(old_by_cy) | set(emergent_by_customer_year):
        delta = emergent_by_customer_year.get(key, 0.0) - old_by_cy.get(key, 0.0)
        if abs(delta) < 1e-9:
            continue
        idx = last_index_by_cy.get(key)
        if idx is None:
            continue
        delta_at_index[idx] = delta_at_index.get(idx, 0.0) + delta

    cumulative_correction = 0.0
    for i, rec in enumerate(all_records):
        delta = delta_at_index.get(i)
        if delta is not None:
            rec["bad_debt_gbp"] = round(rec.get("bad_debt_gbp", 0.0) + delta, 6)
            rec["net_margin_gbp"] = round(rec["net_margin_gbp"] - delta, 6)
            cumulative_correction -= delta
        if cumulative_correction != 0.0 and "treasury_cash_balance_gbp" in rec:
            rec["treasury_cash_balance_gbp"] = round(rec["treasury_cash_balance_gbp"] + cumulative_correction, 2)
