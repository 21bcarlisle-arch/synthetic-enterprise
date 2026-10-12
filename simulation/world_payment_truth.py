"""One world payment truth for the P&L (2026-10-12, the world lane).

THE DEFECT. The run drew whether a household paid a bill TWICE, from two models that never met:
the payment triad (`background/live_payment_triad.py`, through `payment_behaviour_source`), which
the run calls "the CANONICAL payment truth" and which every household mechanism acts on -- agreed
plans, pauses, lower payments, early-contact payments, mandate cancellations, re-presented and
later-settled bills -- and the arrears engine (`arrears_engine._resolve_bills`), whose own draw
alone set the bad debt the P&L books. So a kept plan reduced nobody's write-off, a re-presented DD
that the household paid was still written off at close, and "days behind" and "GBP bad debt" came
from different households. A debt engine graded on bad debt would be graded against a world its
own actions could not reach.

THE CORRECTION. With `UNIFIED` on, the arrears engine takes each bill's OUTCOME (paid, failed,
disputed; days late; the channel it was paid by) from the triad's record for that leg and month,
and takes the household's REPAYMENTS of its arrears from the same truth:
  * a later settlement that crossed (a re-presentation, a lump repayment, an early-contact payment),
    for the amount of the bill it settled;
  * each instalment of an agreed repayment plan the household paid, for its share of the bills the
    plan covered (the instalment over the plan's debt, times those bills' issued amounts). A plan
    the household broke repays only what was paid before it broke.
The amounts stay the issued bills' (`bill_assembly`), because how much a bill was is the bill's;
whether and when it was paid is the household's, and that now has one home.

How a repayment meets the balance is the engine's existing balance-at-close rule, extended by one
event: a repayment discharges the oldest outstanding bill first on its fuel's contract (Clayton's
Case, the running-account default the company ledger also uses --
`docs/market_research/account_hierarchy_payment_allocation.md` s.1) and, being a payment by the
debtor, restarts the limitation clock (Limitation Act 1980 s.29(5), as the engine's own payments
already do). Knowledge: `docs/market_research/bad_debt_provisioning.md`, "One payment truth".

SHIPPED OFF. `UNIFIED = False`, so the arrears engine draws as before and the shipped book is
byte-identical. Switching it on changes the shipped book's bad debt: that change is a world
correction, measured and recorded, and making it the shipped default is the seat's call because
controls elsewhere pin today's book.

NAMED SIMPLIFICATIONS:
  1. A bill the triad has no record for (a leg it does not collect, or a month outside its run)
     keeps the engine's own draw; the count is published (`fallback_bills`) so it cannot hide.
  2. A mover's final bill is decided once, in the triad, by the world's one exit model
     (`arrears_engine.mover_final_bill_outcome`); the part a gone household paid reduces the bill.
  3. The stayer provision leg (off) does not net repayments.
  4. No meter is changed for debt in the run, so no prepayment repayment exists to carry.

Pure world code: never imports `company.*` or `saas.*`; reads the triad's world-side records only.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

#: The switch. Off: the arrears engine draws its own outcomes, as shipped.
UNIFIED = False

#: The behavioural-record key the run writes and the arrears engine reads.
RECORD_KEY = "world_payment_truth"

#: What the arrears engine's last resolution took from the truth, and what it could not
#: (simplification 1). Published, never read by a decision.
LAST_COUNTS: dict = {}

_PREPAYMENT = "prepayment"
_DIRECT_DEBIT = "direct_debit"


def engine_method(triad_method: str) -> str:
    """The engine's channel vocabulary for a triad channel: DD, a meter, or paid on receipt."""
    from simulation.arrears_engine import PAY_ON_RECEIPT_METHOD, PREPAYMENT_METHOD
    if triad_method == _DIRECT_DEBIT:
        return _DIRECT_DEBIT
    if triad_method == _PREPAYMENT:
        return PREPAYMENT_METHOD
    return PAY_ON_RECEIPT_METHOD


def build(triad, through: dt.date) -> dict[str, dict]:
    """Per leg (`customer_id`): `{"outcomes": {"YYYY-MM": {...}}, "repayments": [...]}` from the
    triad's records, its crossed settlements and the world's plan book. Call after the triad's
    end-of-run walk (`collections_journeys`), whose forced crossing is the last that can move it."""
    from simulation.plan_offer_response import REPAYMENT_PLAN, plan_instalments
    out: dict[str, dict] = {}
    by_account: dict[str, list] = {}
    for r in triad.records:
        rec = out.setdefault(r.customer_id, {"outcomes": {}, "repayments": []})
        rec["outcomes"][r.due_date.isoformat()[:7]] = {
            "result": r.result, "days_late": int(r.days_late or 0),
            "method": engine_method(r.payment_method)}
        part = triad._final_bill_part_share.get((r.customer_id, r.due_date.isoformat()[:7]))
        if part:
            rec["outcomes"][r.due_date.isoformat()[:7]]["part_share"] = part
        by_account.setdefault(r.account_id, []).append(r)
    cid_of = {a: rs[0].customer_id for a, rs in by_account.items()}
    for account_id, bill_due, settled_on in triad._crossed_settlements:
        cid = cid_of.get(account_id)
        if cid is not None:
            out[cid]["repayments"].append({"date": settled_on.isoformat(), "kind": "settlement",
                                           "bill_month": bill_due.isoformat()[:7]})
    book = triad._household_plans
    for (account_id, agreed_on), terms in book._terms.items():
        cid = cid_of.get(account_id)
        if cid is None or terms.kind != REPAYMENT_PLAN or not terms.debt or not terms.instalment:
            continue
        covered = [r.due_date.isoformat()[:7] for r in by_account[account_id]
                   if r.result == "failed" and r.due_date < agreed_on
                   and (r.settled_on is None or r.settled_on > agreed_on)]
        if not covered:
            continue
        remaining = terms.debt
        for row in plan_instalments(account_id, agreed_on, through, agreements=book):
            if remaining <= 0:
                break
            paid_now = min(terms.instalment, remaining)
            remaining = round(remaining - paid_now, 2)
            if row["paid"]:
                out[cid]["repayments"].append({
                    "date": row["due"], "kind": "plan_instalment", "covered_months": covered,
                    "share": paid_now / terms.debt})
    return out


def repayment_rows(truth: dict, cid: str, bill_rows: list[dict]) -> list[dict]:
    """The leg's repayments as engine rows (`outcome: "repayment"`), each priced from the issued
    amounts of the bills it settles. A repayment for a bill the supplier never issued is dropped."""
    amount_by_month: dict[str, float] = {}
    commodity_by_month: dict[str, str] = {}
    for b in bill_rows:
        if b["outcome"] in ("failed", "dispute", "success"):
            m = b["period_end"][:7]
            amount_by_month[m] = amount_by_month.get(m, 0.0) + b["amount_gbp"]
            commodity_by_month[m] = b["commodity"]
    rows = []
    for rp in truth.get("repayments", ()):
        if rp["kind"] == "settlement":
            months = [rp["bill_month"]]
            amount = sum(amount_by_month.get(m, 0.0) for m in months)
        else:
            months = rp["covered_months"]
            amount = rp["share"] * sum(amount_by_month.get(m, 0.0) for m in months)
        commodity = next((commodity_by_month[m] for m in months if m in commodity_by_month), None)
        if commodity is None or amount <= 0:
            continue
        rows.append({"customer_id": cid, "period_end": rp["date"], "commodity": commodity,
                     "amount_gbp": round(amount, 2), "due_date": dt.date.fromisoformat(rp["date"]),
                     "method": None, "outcome": "repayment", "days_late": 0,
                     "repayment_kind": rp["kind"]})
    return rows


def truth_outcome(truth: Optional[dict], period_end: str) -> Optional[dict]:
    """The triad's outcome for the bill of `period_end`'s month, or None (the engine draws)."""
    if not truth:
        return None
    return truth["outcomes"].get(period_end[:7])
