"""Decision Event Ledger -- docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md Part 5.

Unifies the per-topic case studies built independently across Phases QI/QJ/QL/QM
(behavioral signal, renewal decision, churn journey, retention deferral) into one
real chronological timeline: every commercial event touching a customer, in
sequence -- renewal trigger, decision taken with its EV, offer outcome, arrears
opening, dunning cascade. Built entirely from data already computed this run
(dash["customers"] events/retention/journey_log + billing_ledger.json); no new
simulation logic, no company-layer changes.

Both build_customer_ledger and build_portfolio_event_stream operate on the
same dash-transformed, short-field-name records already threaded through
tools/generate_shadow_html.py other case-study functions (customer_id/date/...),
not the raw run_output field names (customer_id/event_date/...) -- billing_ledger
is only available at that call site, so this is where SIM-side and
company-observable records are already merged.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LedgerEvent:
    customer_id: str
    date: str
    event_type: str
    description: str
    company_belief: float | None = None
    sim_truth: float | None = None
    amount_gbp: float | None = None
    outcome: str | None = None
    # Nudge Physics Layer 1 (NUDGE_PHYSICS.md): comms framing attribute the
    # company chose for this offer -- "loss_framed" / "gain_framed".
    framing_type: str | None = None


def _journey_events(cid, journey_log):
    events = []
    for j in journey_log:
        if j.get("customer_id") != cid or not j.get("date"):
            continue
        state = j.get("state", "")
        events.append(LedgerEvent(
            customer_id=cid,
            date=j["date"],
            event_type="journey_state",
            description=(
                "Hidden churn-journey state advances to " + state.upper() +
                " (resentment score {:.1f})".format(j.get("resentment_score", 0))
            ),
            sim_truth=j.get("resentment_score"),
            outcome="resentment_burned" if j.get("is_burned") else None,
        ))
    return events


def _retention_decision_events(cid, retention):
    events = []
    for r in retention:
        if r.get("customer_id") != cid or not r.get("date"):
            continue
        cost = r.get("cost_gbp", 0.0) or 0.0
        expected_margin = r.get("expected_term_margin_gbp", 0.0) or 0.0
        ev = expected_margin - cost
        framing_type = r.get("framing_type")
        framing_note = ""
        if framing_type == "loss_framed":
            framing_note = " Comms framed as a loss (you will lose the discount)."
        elif framing_type == "gain_framed":
            framing_note = " Comms framed as a gain (save with this discount)."
        events.append(LedgerEvent(
            customer_id=cid,
            date=r["date"],
            event_type="retention_decision",
            description=(
                "Renewal window: company estimated {:.0%} churn risk, decided to "
                "offer a {:.0%} discount (cost GBP{:,.2f}) against GBP{:,.2f} "
                "expected term margin at risk -- expected value of offering "
                "GBP{:,.2f}.{}".format(
                    r.get("company_est", 0), r.get("discount_pct", 0), cost,
                    expected_margin, ev, framing_note,
                )
            ),
            company_belief=r.get("company_est"),
            sim_truth=r.get("realized_churn_p"),
            amount_gbp=ev,
            outcome=r.get("outcome"),
            framing_type=framing_type,
        ))
    return events


def _renewal_outcome_events(cid, events):
    out = []
    for e in events:
        if e.get("customer_id") != cid or not e.get("date"):
            continue
        etype = e.get("type", "")
        out.append(LedgerEvent(
            customer_id=cid,
            date=e["date"],
            event_type=("outcome_" + etype) if etype else "outcome",
            description=(
                "Renewal outcome: {} -- company believed {:.0%} churn risk at "
                "decision time, SIM realized probability was {:.0%}.".format(
                    etype.upper() if etype else "UNKNOWN",
                    e.get("company_est", 0), e.get("realized_churn_p", 0),
                )
            ),
            company_belief=e.get("company_est"),
            sim_truth=e.get("realized_churn_p"),
            outcome=etype or None,
        ))
    return out


def _arrears_events(cid, ledger_customer):
    events = []
    for case in (ledger_customer or {}).get("arrears_history", []):
        amount = case.get("arrears_gbp", 0.0)
        for stage in case.get("stages", []):
            if not stage.get("date"):
                continue
            events.append(LedgerEvent(
                customer_id=cid,
                date=stage["date"],
                event_type="arrears_" + stage.get("stage", "").lower(),
                description=stage.get("note") or stage.get("stage", ""),
                amount_gbp=amount,
                outcome=stage.get("stage"),
            ))
    return events


#: What each stage of the company desk's collections journey (`company/billing/collections_journey`)
#: says to a reader. A stage missing here is shown by the desk's own decision text, never dropped.
_COLLECTIONS_STAGE_WORDS = {
    "missed_payment": "A bill is unpaid past its due date -- collections journey opened",
    "reminder": "Reminder sent",
    "reminder_2": "Second reminder sent",
    "repayment_plan_offer": "Payment plan offered (SLC 27.8)",
    "arrangement_offered": "Affordable arrangement put to the household",
    "final_notice": "Final notice sent",
    "prepayment_or_debt_agency": "Top rung: prepayment by Consent or a debt agency",
    "disconnection_warning_or_agency": "Top rung: disconnection warning or a debt agency",
    "prepayment_offered": "Prepayment meter offered by Consent (SLC 28.22)",
    "repayment_plan_reoffer": "A further bill missed past the top rung: payment plan offered again",
    "write_off": "Written off: the debt is statute-barred (Limitation Act 1980 s.5)",
    "statement_of_account": "Statement of account sent",
    "interest_notice": "Late-payment interest notice sent (LPCDA 1998)",
    "final_demand": "Final demand sent",
    "debt_recovery": "Passed to debt recovery",
    "commercial_recovery": "Passed to commercial recovery",
    "moratorium_hold": "Collections held: Breathing Space moratorium",
    "cured": "Overdue balance cleared -- journey closed",
    "arrangement": "Arrangement agreed -- the debt leaves the dunning ladder",
    "prepayment": "Meter changed to prepayment -- journey closed",
}


def _collections_journey_events(cid, journeys):
    """`journeys` are the company desk's collections journeys on this record's own account (the
    run's `collections_journeys` rows for `ACC-<file id>`; the caller picks them, because a gas leg's
    file id is not `cid`), one event per dated stage. Beside `_arrears_events`, not instead of it: that
    is the billing ledger's per-bill notice record, and the two are different ladders until they
    are reconciled (`company/billing/arrears_engine.LEDGER_NOTICES`)."""
    events = []
    for journey in journeys or []:
        for stage in journey.get("stages", []):
            name = stage.get("stage", "")
            words = _COLLECTIONS_STAGE_WORDS.get(name, stage.get("decision") or name)
            if stage.get("overdue_gbp") is not None and name not in ("cured", "write_off"):
                words += " -- GBP%.2f overdue" % stage["overdue_gbp"]
            if name == "write_off" and stage.get("written_off_gbp") is not None:
                words += " -- GBP%.2f" % stage["written_off_gbp"]
            if name == "arrangement_offered" and stage.get("household_acceptance") is None:
                words += "; the household's answer is not known to the company: " + (
                    stage.get("acceptance_gap") or "no reason recorded")
            events.append(LedgerEvent(
                customer_id=cid,
                date=stage["on"],
                event_type="collections_" + name,
                description=words,
                amount_gbp=stage.get("written_off_gbp", stage.get("overdue_gbp")),
                outcome=journey.get("exit"),
            ))
    return events


def build_customer_ledger(cid, events, retention, journey_log, ledger_customer=None,
                          collections_journeys=None):
    all_events = (
        _journey_events(cid, journey_log)
        + _retention_decision_events(cid, retention)
        + _renewal_outcome_events(cid, events)
        + _arrears_events(cid, ledger_customer)
        + _collections_journey_events(cid, collections_journeys)
    )
    all_events.sort(key=lambda e: e.date)
    return [e.__dict__ for e in all_events]


def build_portfolio_event_stream(events, retention, journey_log, billing_ledger=None, limit=200):
    ledger_customers = (billing_ledger or {}).get("customers", {})
    all_cids = set(ledger_customers.keys())
    for src in (events, retention, journey_log):
        for item in src:
            cid = item.get("customer_id")
            if cid:
                all_cids.add(cid)

    all_events = []
    for cid in all_cids:
        all_events.extend(_retention_decision_events(cid, retention))
        all_events.extend(_renewal_outcome_events(cid, events))
        for case in ledger_customers.get(cid, {}).get("arrears_history", []):
            stages = case.get("stages", [])
            if not stages or not stages[0].get("date"):
                continue
            final_stage = stages[-1].get("stage", "")
            all_events.append(LedgerEvent(
                customer_id=cid,
                date=stages[0]["date"],
                event_type="arrears_opened",
                description=(
                    "Arrears case opened, GBP{:,.2f} -- currently/finally {}".format(
                        case.get("arrears_gbp", 0), final_stage,
                    )
                ),
                amount_gbp=case.get("arrears_gbp"),
                outcome=final_stage,
            ))

    all_events.sort(key=lambda e: e.date, reverse=True)
    if limit is not None:
        all_events = all_events[:limit]
    return [e.__dict__ for e in all_events]
