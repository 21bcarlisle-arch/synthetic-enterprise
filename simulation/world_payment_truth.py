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

SHIPPED ON since 2026-10-12. It first landed off (`62596685a`, byte-identical book); the seat made
it the default once the rails and the mover's final bill had joined it (`c11ec1e50`), as a world
correction before any supplier result was seen. On 40 founders, budget 0, it moved bad debt from
GBP 440.85 to 116.48 and net from 31,124.47 to 31,448.84 (the freeze record has the measurement).

NAMED SIMPLIFICATIONS:
  1. A bill the triad has no record for (a leg it does not collect, or a month outside its run)
     keeps the engine's own draw; the count is published (`fallback_bills`) so it cannot hide.
  2. A mover's final bill is decided once, in the triad, by the world's one exit model
     (`arrears_engine.mover_final_bill_outcome`); the part a gone household paid reduces the bill.
  3. The stayer provision leg (off) does not net repayments.
  4. No meter is changed for debt in the run, so no prepayment repayment exists to carry.
  5. A closed account's lump after its final bill is lost (`GONE_HOUSEHOLD_PAYS_NO_LUMP`); one
     dated between the departure and that bill's due date still crosses, and plan instalments
     after close are not touched.

Pure world code: never imports `company.*` or `saas.*`; reads the triad's world-side records only.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

#: The switch. ON, the shipped world since 2026-10-12 (the seat's decision, a world correction made
#: before any supplier result was seen: bills households repaid were being written off). Off brings
#: back the engine's own draw, for comparing against books produced before the correction.
UNIFIED = True

#: A GONE HOUSEHOLD PAYS NO LUMP AFTER ITS FINAL BILL (2026-10-24). A later settlement or an
#: early-contact payment dated after a closed account's final bill fell due does not cross; the
#: closing balance is written off and the gone-household share is recovered from it by
#: `arrears_engine.post_write_off_recovery_gbp` (10.4-24.5p, the final-bill complement). Before,
#: the leaver repaid at the stayer's rate AND got that recovery. ON, a world correction made before
#: any supplier result was seen; off brings back the book of `cfe4d94be`. Knowledge:
#: `docs/market_research/debt_realism_three_world_fidelity_gaps.md` s.1a.
GONE_HOUSEHOLD_PAYS_NO_LUMP = True

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


def bill_month_of(period_index: int) -> str:
    """The month a triad record's bill charges for, "YYYY-MM", from its period index: not its due
    date's month, which is usually the next one."""
    return "{:04d}-{:02d}".format(period_index // 12, period_index % 12 + 1)


def build(triad, through: dt.date) -> dict[str, dict]:
    """Per leg (`customer_id`): `{"outcomes": {"YYYY-MM": {...}}, "repayments": [...]}` from the
    triad's records, its crossed settlements and the world's plan book. Call after the triad's
    end-of-run walk (`collections_journeys`), whose forced crossing is the last that can move it."""
    from simulation.plan_offer_response import REPAYMENT_PLAN, plan_instalments
    out: dict[str, dict] = {}
    by_account: dict[str, list] = {}
    for r in triad.records:
        rec = out.setdefault(r.customer_id, {"outcomes": {}, "repayments": []})
        month = bill_month_of(r.period_index)
        rec["outcomes"][month] = {
            "result": r.result, "days_late": int(r.days_late or 0),
            "method": engine_method(r.payment_method)}
        part = triad._final_bill_part_share.get((r.customer_id, month))
        if part:
            rec["outcomes"][month]["part_share"] = part
        by_account.setdefault(r.account_id, []).append(r)
    # A billing account holds both fuels' legs, and each leg is its own contract (SLC 27.16). Until
    # 2026-10-28 every settlement went to the account's first leg, electricity: on 5e3e9966a5 no gas
    # leg held one, 523 sat on electricity, and the reg 6D refund paid out that phantom credit.
    for _account_id, _bill_due, settled_on, month, cid in triad._crossed_settlements:
        if cid in out:
            out[cid]["repayments"].append({"date": settled_on.isoformat(), "kind": "settlement",
                                           "bill_month": month})
    book = triad._household_plans
    for (account_id, agreed_on), terms in book._terms.items():
        if (account_id not in by_account or terms.kind != REPAYMENT_PLAN or not terms.debt
                or not terms.instalment):
            continue
        # The plan covers the account's debt on both fuels; each instalment repays every covered
        # bill by the same share, so each leg is repaid its own bills' share.
        covered: dict[str, list[str]] = {}
        for r in by_account[account_id]:
            if (r.result == "failed" and r.due_date < agreed_on
                    and (r.settled_on is None or r.settled_on > agreed_on)):
                covered.setdefault(r.customer_id, []).append(bill_month_of(r.period_index))
        if not covered:
            continue
        remaining = terms.debt
        for row in plan_instalments(account_id, agreed_on, through, agreements=book):
            if remaining <= 0:
                break
            paid_now = min(terms.instalment, remaining)
            remaining = round(remaining - paid_now, 2)
            if row["paid"]:
                for leg, months in covered.items():
                    out[leg]["repayments"].append({
                        "date": row["due"], "kind": "plan_instalment", "covered_months": months,
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
