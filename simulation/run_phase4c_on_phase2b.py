"""Phase 4c applied to the full Phase 2b portfolio — end-to-end run.

Phase 4c-4 through 4c-6 (`saas/bill_generator.py`, `saas/payment_behaviour.py`,
`saas/contact_model.py`) were built and tested against small hand-written
settlement fixtures. This script is the follow-up flagged in
`docs/observability/PHASE_4c_SUMMARY.md`'s Open Questions: it runs the full
Phase 2b simulation once, groups its `all_records` settlement output into
monthly bills per customer (chronological, carrying `previous_bill_total_gbp`
for the bill-shock clarity penalty), then feeds those bills through 4c-5
(payment behaviour) and 4c-6 (contact/complaints) to produce portfolio-level
billing-experience figures for the real 10-account portfolio (6 electricity +
4 gas).

4c-2 (weather-driven demand shapes) and 4c-3 (weather->price sensitivity) are
NOT included here — both modify `simulation/settlement.py`'s inputs
(consumption shape, forward price) rather than consuming its output, so
wiring them in is a separate, larger re-run of `simulation/run_phase2b.py`
itself, not a downstream pass over its existing records. Flagged as a further
follow-up.

Delegation note: hand-written (orchestration-adjacent, per protocol).

Phase 5b: this script is also the single entry point for the combined
2b+4b+4c run output used by `saas/reporting/annual_report.py`. Rather than
have `run_phase4b_on_phase2b.py` call `run_phase2b()` a second time (a
separate, non-deterministic ~100-minute run with different committee
decisions), `main()` here runs Phase 2b once and feeds the same
`all_records`/`CUSTOMERS` through the 4b customer-value builders
(`cost_to_serve`, `churn_model`, `home_move_win_rate`, `enterprise_value`)
as well as the 4c billing-experience builders. `--save-json` persists the
reduced report data (via `saas.reporting.annual_report.extract_report_data`)
to `docs/reports/run_output_latest.json` plus a versioned copy stamped with
the current git commit and timestamp.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import saas.payment_behaviour as payment_behaviour_module
from company.billing.back_billing import BackBillingAssessment, BackBillingReason
from saas.bill_generator import (
    BILL_SHOCK_PENALTY_FACTOR,
    MAX_CLARITY_SCORE,
    MIN_CLARITY_SCORE,
    generate_bill,
)
from saas.churn_model import build_churn_risk
from saas.contact_model import build_contact_model
from saas.cost_to_serve import build_cost_to_serve, build_cost_to_serve_ledger_events
from saas.customers import ACQUIRED_CUSTOMERS, CUSTOMERS, SUCCESSOR_CUSTOMERS, get_customer
from saas.enterprise_value import build_enterprise_value
from saas.home_move_win_rate import build_home_move_win_rates
from saas.ledger import build_ledger, derive_pnl, ledger_summary, make_cost_to_serve_event
from saas.payment_behaviour import build_payment_behaviour
from simulation.arrears_engine import (
    compute_emergent_bad_debt,
    apply_emergent_bad_debt,
    compute_debt_recovery,
    apply_debt_recovery,
)
from simulation.contact_centre import generate_contact_centre_log
from simulation.credit_refund_events import generate_credit_refund_log
from simulation.meter_reads import (
    MeterReadEvent,
    generate_meter_read_log,
    meter_type_for_customer,
    simulate_read,
)
from simulation.run_phase2b import main as run_phase2b
from tools.contact_centre_port import ContactCentreMessage
from tools.meter_read_port import MeterReadMessage

PRICE_DIFFERENTIAL_PCT = 0.0  # matches run_phase4b_on_phase2b.py


def _get_all_customers() -> list[dict]:
    """Live customer list including Phase 8a acquired customers.

    Must be a function (not a module-level constant) because ACQUIRED_CUSTOMERS
    is populated by run_phase2b.main() after import time.
    """
    return CUSTOMERS + SUCCESSOR_CUSTOMERS + ACQUIRED_CUSTOMERS

RUN_OUTPUT_LATEST_PATH = Path("docs/reports/run_output_latest.json")
RUN_OUTPUT_VERSIONED_DIR = Path("docs/reports")


def _billing_month(settlement_date: str) -> str:
    """'YYYY-MM-DD' -> 'YYYY-MM'."""
    return settlement_date[:7]


def _year_ago_month(month: str) -> str:
    """'YYYY-MM' -> the same calendar month one year earlier."""
    yr, mo = month.split("-")
    return f"{int(yr) - 1}-{mo}"


def _prior_calendar_month(month: str) -> str:
    """'YYYY-MM' -> the immediately preceding calendar month (year rolls
    back at January)."""
    yr, mo = int(month[:4]), int(month[5:7])
    if mo == 1:
        return f"{yr - 1}-12"
    return f"{yr}-{mo - 1:02d}"


def _estimated_settlement_records(
    settlement_records: list[dict], ratio: float, commodity: str
) -> list[dict]:
    """Rescale real settlement records to reflect an ESTIMATED consumption
    quantity while preserving (a) the real per-MWh commodity unit rate and
    (b) the fixed daily standing charge exactly.

    Each record's `consumption_kwh` and its commodity portion of `revenue_gbp`
    are scaled by `ratio` (estimated_kwh / true_kwh); the standing-charge field
    is left untouched (a fixed daily charge does not move with metered volume).
    Because commodity revenue and consumption scale by the identical factor, a
    bill built from these records has the SAME average unit rate as the true
    bill -- the estimate is priced at the real rate, only the quantity differs.
    This is the point of D3 step 1: the estimate-labelled bill no longer mixes
    true consumption into an estimate, collapsing the unit-rate divergence.
    """
    sc_field = "gas_standing_charge_gbp" if commodity == "gas" else "standing_charge_gbp"
    scaled = []
    for record in settlement_records:
        sc = record.get(sc_field, 0.0)
        commodity_portion = record["revenue_gbp"] - sc
        new_record = dict(record)
        new_record["consumption_kwh"] = record["consumption_kwh"] * ratio
        new_record["revenue_gbp"] = commodity_portion * ratio + sc
        scaled.append(new_record)
    return scaled


def _annotate_billing_basis(bill: dict, event, true_bill: dict) -> dict:
    """Additive D3 provenance on a bill dict -- existing fields untouched.

    Every bill gains `billing_basis` ("actual" | "estimated"). An estimated
    bill also carries the TRUE-vs-BILLED pair so the divergence is directly
    measurable (and so step 2, actual-read catch-up rebilling, has the true
    figures it will reconcile against once a real read arrives).
    """
    annotated = dict(bill)
    annotated["billing_basis"] = event.status
    if event.status == "estimated":
        annotated["true_consumption_kwh"] = true_bill["total_consumption_kwh"]
        annotated["true_commodity_amount_gbp"] = true_bill["commodity_amount_gbp"]
        annotated["true_total_amount_gbp"] = true_bill["total_amount_gbp"]
        annotated["estimated_consumption_kwh"] = event.estimated_consumption_kwh
        annotated["consecutive_estimated_count"] = event.consecutive_estimated_count
    return annotated


# Below this delta, real suppliers typically do not bother billing a
# correction (matches the same £5 real-world convention already used by
# company/billing/smart_meter_reconciliation.py's `is_material`, kept as its
# own named constant here rather than imported since that module models a
# different real mechanism -- annual smart-meter AQ reconciliation -- not the
# per-actual-read catch-up this pipeline builds; see _resolve_catchup below).
CATCHUP_MATERIALITY_THRESHOLD_GBP = 5.0


def _resolve_catchup(
    customer_id: str, segment: str, pending_run: list[dict], billing_date_iso: str
) -> dict | None:
    """D3 step 2: when an actual read arrives, reconcile a just-ended run of
    consecutive ESTIMATED bills against what they should have charged.

    `pending_run` is the list of estimated bills' own {period_start,
    period_end, true_total_amount_gbp, total_amount_gbp} since the customer's
    last actual (or forced-catch-up) read -- both totals already fully priced
    (VAT/non-commodity/standing charge included) by generate_bill(), so their
    difference is already correctly gross, no re-pricing needed.

    Undercharges (supplier owes itself more) are subject to the Ofgem SLC 31A
    12-month back-billing cap (company/billing/back_billing.py, reason
    ESTIMATED_READ_CORRECTED -- built for exactly this scenario, previously
    unwired). Overcharges (credit owed to the customer) are NEVER capped --
    the cap protects consumers from late supplier demands, it does not let a
    supplier withhold a refund (same real-world asymmetry already documented
    in company/billing/smart_meter_reconciliation.py's `recoverable_gbp`).

    Returns None if there was no estimated run to resolve (the common case:
    the customer's read arrived on time last period too).
    """
    if not pending_run:
        return None

    # `+ 0.0` normalises a floating-point -0.0 (a near-exact-zero sum can land
    # on negative zero) to plain 0.0 -- cosmetic, but a customer-facing "-0.0"
    # correction is a real, avoidable rendering artifact (Expert-Hour finding,
    # 2026-07-12).
    raw_delta_gbp = round(
        sum(p["true_total_amount_gbp"] - p["total_amount_gbp"] for p in pending_run), 2
    ) + 0.0
    period_start = pending_run[0]["period_start"]
    period_end = pending_run[-1]["period_end"]
    billing_date = datetime.fromisoformat(billing_date_iso).date()
    is_domestic = segment == "resi"

    if raw_delta_gbp > 0:
        assessment = BackBillingAssessment(
            account_id=customer_id,
            billing_date=billing_date,
            consumption_period_start=datetime.fromisoformat(period_start).date(),
            consumption_period_end=datetime.fromisoformat(period_end).date(),
            billed_amount_gbp=raw_delta_gbp,
            reason=BackBillingReason.ESTIMATED_READ_CORRECTED,
            is_domestic=is_domestic,
        )
        chargeable_gbp = assessment.capped_amount_gbp
        written_off_gbp = assessment.written_off_gbp
        cap_applied = assessment.cap_applies
        direction = "undercharge"
    else:
        chargeable_gbp = raw_delta_gbp
        written_off_gbp = 0.0
        cap_applied = False
        direction = "overcharge"

    return {
        "period_start": period_start,
        "period_end": period_end,
        "periods_covered": len(pending_run),
        "direction": direction,
        "raw_delta_gbp": raw_delta_gbp,
        "chargeable_gbp": round(chargeable_gbp, 2) + 0.0,
        "written_off_gbp": round(written_off_gbp, 2) + 0.0,
        "back_billing_cap_applied": cap_applied,
        "is_material": abs(chargeable_gbp) >= CATCHUP_MATERIALITY_THRESHOLD_GBP,
    }


def build_monthly_bills(all_records: list[dict], churned_ids: set[str] | None = None) -> list[dict]:
    """Group `all_records` (from `simulation.settlement.run_settlement`) into
    one bill per customer per calendar month, in chronological order, via
    `saas.bill_generator.generate_bill`.

    Each customer's bills carry `previous_bill_total_gbp` from their own
    prior month, enabling the bill-shock clarity penalty. `contract_type` is
    looked up per customer from `saas.customers.CUSTOMERS`.

    Director-flagged 2026-07-10 (docs/design/BILL_SHOCK_DEFINITION_FINDING.md):
    the existing `bill_shock_pct` (month-N vs month-N-1) conflates normal
    seasonal consumption swings with a genuine surprise -- a resi customer's
    real December bill vs November bill is an expected jump, not a shock.
    Adds an ADDITIVE (not replacing) `bill_shock_yoy_pct`: the same bill
    compared against the SAME CALENDAR MONTH a year earlier, which nets out
    seasonality by construction (comparing like-for-like months). Also adds
    `bill_shock_likely_seasonal`: True when the raw month-on-month shock is
    large but the year-over-year comparison for the same month is small --
    a real, reasoned diagnostic signal (not a full redesign; contract-end
    SVT-reversion and DD-recalculation event detection remain a separate,
    bigger piece of work needing new SIM state, registered in PRIORITIES.md,
    not built here).

    `churned_ids` (D3 step 2 Expert-Hour finding, 2026-07-12): accounts that
    churn/succeed mid a run of estimated bills would otherwise carry that
    unresolved true-vs-billed delta into oblivion -- no more bills ever
    arrive to fold a catch-up onto. Real UK practice (Ofgem SLC 21B) requires
    a final bill at supply end, normally on a final read -- modelled here as
    forcing the customer's LAST bill in this dataset to resolve as if that
    final read had arrived, same as `company/billing/account_closure.py`'s
    own (separately unwired) `receive_final_read()` concept.
    """
    churned_ids = churned_ids or set()
    by_customer_month: dict[str, dict[str, list[dict]]] = {}
    for record in all_records:
        customer_id = record["customer_id"]
        month = _billing_month(record["settlement_date"])
        by_customer_month.setdefault(customer_id, {}).setdefault(month, []).append(record)

    bills = []
    for customer_id, months in by_customer_month.items():
        customer_data = get_customer(customer_id)
        contract_type = customer_data.get("contract_type", "fixed_1yr")
        segment = customer_data.get("segment", "resi")
        commodity = customer_data.get("commodity", "electricity")
        # D3 step 1 (docs/design/maturity_map.yaml "Estimated billing &
        # catch-up rebilling cycle"): decide per bill whether a real read
        # arrived or the bill is ESTIMATED, and when estimated bill the
        # estimate at the real unit rate instead of the true (not-yet-known)
        # consumption. Uses the SAME deterministic dispatch, arguments and
        # per-customer state-threading (trailing confirmed actuals + running
        # consecutive-estimated count) as generate_meter_read_log(), computed
        # here a second time on purpose (additive-first, no change to
        # meter_reads.py or its own call site); the identical seed means the
        # two always agree. De-duplicating the two call sites is a documented
        # follow-up, not this step.
        meter_type = (
            meter_type_for_customer(customer_data) if customer_data else "traditional"
        )
        # `previous_bill_total_gbp` is threaded on the TRUE bill total exactly
        # as before this change, so the actual-read path is byte-identical in
        # every run (mixed or not), not just an all-actual one.
        previous_bill_total_gbp = None
        trailing_actuals_kwh: list[float] = []
        consecutive_estimated = 0
        pending_estimated_run: list[dict] = []
        sorted_months = sorted(months)
        for month_idx, month in enumerate(sorted_months):
            # TRUE-consumption bill from the real settlement records -- the
            # unchanged actual-read path, and the source of the real unit rate
            # and standing charge an estimated bill reuses.
            true_bill = generate_bill(
                customer_id, months[month], contract_type,
                previous_bill_total_gbp, segment, commodity,
            )
            event = simulate_read(
                customer_id, true_bill["period_end"], meter_type,
                true_bill["total_consumption_kwh"],
                trailing_actuals_kwh, consecutive_estimated,
            )
            is_final_bill_for_customer = month_idx == len(sorted_months) - 1
            if (
                event.status != "actual"
                and is_final_bill_for_customer
                and customer_id in churned_ids
            ):
                # SLC 21B final-bill-at-closure: force this closing account's
                # last-ever bill to resolve on a final read rather than
                # leaving a run of estimated bills (and their unresolved
                # true-vs-billed delta) permanently unreconciled.
                event = MeterReadEvent(
                    customer_id=customer_id, period_end=true_bill["period_end"],
                    meter_type=meter_type, delay_days=0, status="actual",
                    true_consumption_kwh=true_bill["total_consumption_kwh"],
                    consecutive_estimated_count=0, forced_catch_up=True,
                )
            if event.status == "actual":
                bill = _annotate_billing_basis(true_bill, event, true_bill)
                # D3 step 2: this real read resolves any pending run of
                # estimated bills since the last one -- fold the reconciled
                # correction (capped per Ofgem SLC 31A where it's an
                # undercharge) onto THIS bill, matching how a real catch-up
                # correction actually appears: as an adjustment on the next
                # real bill, not a separate artifact.
                catchup = _resolve_catchup(
                    customer_id, segment, pending_estimated_run, bill["period_end"]
                )
                # Materiality gate (Expert-Hour finding, 2026-07-12): a real
                # supplier doesn't bother billing/crediting a correction below
                # CATCHUP_MATERIALITY_THRESHOLD_GBP -- previously computed and
                # exposed but never actually consulted, so a genuinely £0.00
                # correction was still stamped onto the bill as a real event.
                if catchup is not None and catchup["is_material"]:
                    bill["catchup_applied"] = True
                    bill["catchup_period_start"] = catchup["period_start"]
                    bill["catchup_period_end"] = catchup["period_end"]
                    bill["catchup_periods_covered"] = catchup["periods_covered"]
                    bill["catchup_direction"] = catchup["direction"]
                    bill["catchup_raw_delta_gbp"] = catchup["raw_delta_gbp"]
                    bill["catchup_adjustment_gbp"] = catchup["chargeable_gbp"]
                    bill["catchup_written_off_gbp"] = catchup["written_off_gbp"]
                    bill["catchup_back_billing_cap_applied"] = catchup["back_billing_cap_applied"]
                    bill["catchup_is_material"] = catchup["is_material"]
                    bill["total_amount_gbp"] = round(
                        bill["total_amount_gbp"] + catchup["chargeable_gbp"], 2
                    )
                    # A catch-up correction changes what the customer is
                    # actually charged THIS bill -- generate_bill() already
                    # computed bill_shock_pct/clarity_score against the
                    # pre-catchup total, so both must be recomputed against
                    # the corrected total or the bill would present an
                    # internally-inconsistent shock/clarity figure (a real
                    # catch-up bill is exactly the kind of surprise this
                    # project's own bill-shock mechanic exists to capture).
                    if previous_bill_total_gbp:
                        old_shock = bill.get("bill_shock_pct") or 0.0
                        new_shock = abs(
                            bill["total_amount_gbp"] - previous_bill_total_gbp
                        ) / previous_bill_total_gbp
                        bill["bill_shock_pct"] = new_shock
                        clarity = bill["clarity_score"]
                        clarity += min(old_shock, 1.0) * BILL_SHOCK_PENALTY_FACTOR
                        clarity -= min(new_shock, 1.0) * BILL_SHOCK_PENALTY_FACTOR
                        bill["clarity_score"] = max(
                            MIN_CLARITY_SCORE, min(MAX_CLARITY_SCORE, clarity)
                        )
                pending_estimated_run = []
                trailing_actuals_kwh.append(true_bill["total_consumption_kwh"])
                consecutive_estimated = 0
            else:
                true_kwh = true_bill["total_consumption_kwh"]
                est_kwh = event.estimated_consumption_kwh
                if true_kwh > 0 and est_kwh is not None:
                    scaled = _estimated_settlement_records(
                        months[month], est_kwh / true_kwh, commodity
                    )
                    estimated_bill = generate_bill(
                        customer_id, scaled, contract_type,
                        previous_bill_total_gbp, segment, commodity,
                    )
                else:
                    # Degenerate zero-metered month: no real per-MWh rate to
                    # price an estimate against -- fall back to the true bill
                    # amount (rare); the billing_basis annotation still records
                    # the estimate.
                    estimated_bill = true_bill
                bill = _annotate_billing_basis(estimated_bill, event, true_bill)
                consecutive_estimated = event.consecutive_estimated_count
                pending_estimated_run.append({
                    "period_start": bill["period_start"],
                    "period_end": bill["period_end"],
                    "true_total_amount_gbp": bill["true_total_amount_gbp"],
                    "total_amount_gbp": bill["total_amount_gbp"],
                })
            bills.append(bill)
            previous_bill_total_gbp = true_bill["total_amount_gbp"]

    # Additive year-over-year comparison (see docstring above) -- a second
    # pass since it needs every bill for a customer already generated to
    # look back a full year, not just the immediately-prior one.
    totals_by_customer_month: dict[str, dict[str, float]] = {}
    mom_shock_by_customer_month: dict[str, dict[str, bool]] = {}
    for bill in bills:
        month = _billing_month(bill["period_end"])
        totals_by_customer_month.setdefault(bill["customer_id"], {})[month] = bill["total_amount_gbp"]
        mom_pct = bill.get("bill_shock_pct")
        mom_shock_by_customer_month.setdefault(bill["customer_id"], {})[month] = bool(
            mom_pct is not None and mom_pct >= 0.20
        )

    for bill in bills:
        month = _billing_month(bill["period_end"])
        year_ago_total = totals_by_customer_month.get(bill["customer_id"], {}).get(_year_ago_month(month))
        if year_ago_total is None or year_ago_total == 0:
            bill["bill_shock_yoy_pct"] = None
            bill["bill_shock_likely_seasonal"] = False
            continue
        yoy_pct = abs(bill["total_amount_gbp"] - year_ago_total) / year_ago_total
        bill["bill_shock_yoy_pct"] = yoy_pct
        mom_pct = bill.get("bill_shock_pct")
        # Exclude "shock aftermath" months (phase-close-evaluator finding,
        # 2026-07-10): a genuine anomaly month produces a large MoM shock
        # when it occurs; the FOLLOWING month, reverting back to a normal
        # baseline, ALSO shows a large MoM swing (the mirror image of the
        # drop back down) while its YoY stays small (both this and last
        # year's same month are normal) -- mislabelling that reversion month
        # itself as "seasonal" when the real cause is the PRIOR month's
        # anomaly, not this month's own seasonal pattern. Excluded by
        # checking the immediately-prior calendar month wasn't itself
        # flagged as a MoM shock.
        prior_month_was_shock = mom_shock_by_customer_month.get(bill["customer_id"], {}).get(
            _prior_calendar_month(month), False
        )
        bill["bill_shock_likely_seasonal"] = bool(
            mom_pct is not None and mom_pct >= 0.20 and yoy_pct < 0.20
            and not prior_month_was_shock
        )

    return bills


def main(report_end: str | None = None, policy=None):
    phase2b_result = run_phase2b(report_end=report_end, policy=policy)
    all_records = phase2b_result["all_records"]

    # D3 step 2 (Expert-Hour finding, 2026-07-12): computed here (moved
    # earlier than its pre-existing use below, for generate_credit_refund_log)
    # so a churning account's own last bill can force-resolve any pending
    # estimated run rather than leaving it unreconciled forever.
    churned_ids = set(phase2b_result.get("churned_billing_accounts", []))

    bills = build_monthly_bills(all_records, churned_ids)

    # Phase 3 (CORE_FIDELITY_PHASES.md item 1): meter-read arrival/
    # estimation/failure events, one per bill -- company-observable data
    # layer only, does not alter settlement-based revenue recognition above.
    all_customers_for_meter_type = _get_all_customers()
    customer_meter_types = {
        c["customer_id"]: meter_type_for_customer(c) for c in all_customers_for_meter_type
    }
    # WALLED_INTERFACES reference-flow conversion (W4_1_typed_adapters): the
    # meter-read crossing now travels as versioned typed messages
    # (tools.meter_read_port.MeterReadMessage) rather than raw dicts. This is a
    # transport-shape change only -- `to_log_entry()` is a lossless identity on
    # the pre-conversion dict, so every downstream consumer of `meter_read_log`
    # is unaffected. Migrating those consumers to accept the message directly
    # is the follow-on "generalize the pattern" step, not done here.
    meter_read_messages = [
        MeterReadMessage.from_log_entry(entry)
        for entry in generate_meter_read_log(bills, customer_meter_types)
    ]
    meter_read_log = [message.to_log_entry() for message in meter_read_messages]

    # Phase 3 (CORE_FIDELITY_PHASES.md item 2): SLC 14 credit-refund
    # activation -- company/billing/credit_refund.py already had the real
    # SLA mechanic but no caller anywhere in simulation/. DD customers who
    # churn carrying a positive DD-smoothing credit balance now raise a real
    # refund event with an on-time/breach outcome. `churned_ids` computed
    # above, before build_monthly_bills.
    customer_segments = {
        c["customer_id"]: c.get("segment", "resi") for c in all_customers_for_meter_type
    }
    credit_refund_log = generate_credit_refund_log(bills, customer_segments, churned_ids)

    # Phase QD: replace the flat get_bad_debt_rate() formula baked into
    # all_records by run_phase2b's real-time settlement loop with the real,
    # emergent bad debt from the same payment/arrears model that drives the
    # per-customer billing ledger (tools.generate_billing_ledger) -- so the
    # board-reported bad_debt_gbp is an outcome of simulated payment
    # behaviour, not a calibrated assumption.
    emergent_bad_debt = compute_emergent_bad_debt(
        bills,
        phase2b_result.get("per_customer_behavioral", {}),
        churned_ids,
    )
    apply_emergent_bad_debt(all_records, emergent_bad_debt)

    # Phase [debt-branch, docs/design/PROCESS_MODEL.md Section 4]: real
    # post-write-off DCA recovery / debt-sale proceeds, applied as a
    # reduction to the bad debt just written off above -- same bills/
    # behavioral/churned inputs as compute_emergent_bad_debt() so the two
    # line up on the identical set of written-off cases.
    debt_recovery = compute_debt_recovery(
        bills,
        phase2b_result.get("per_customer_behavioral", {}),
        churned_ids,
    )
    apply_debt_recovery(all_records, debt_recovery)

    payment_behaviour = build_payment_behaviour(bills)
    contact_model = build_contact_model(bills)

    # Phase 3 (CORE_FIDELITY_PHASES.md item 4): contact-centre first-response
    # time, distinct from feedback_survey's complaint *resolution* timer --
    # reuses contact_model's already-computed per-bill contact_probability
    # as the trigger, adds the channel + first-response latency layer.
    # WALLED_INTERFACES reference-flow conversion (W4_1_typed_adapters, third
    # flow): the customer-contact crossing now travels as versioned typed
    # messages (tools.contact_centre_port.ContactCentreMessage) rather than raw
    # dicts. Transport-shape change only -- `to_log_entry()` is a lossless
    # identity on the pre-conversion dict, so the downstream consumer of
    # `contact_centre_log` (annual_report.py's SLC 25C SLA-breach check) is
    # unaffected. All fields are company-observable contact-centre operational
    # data; unlike meter reads / the acquisition funnel there is no SIM-internal
    # ground-truth field on this seam.
    contact_centre_messages = [
        ContactCentreMessage.from_log_entry(entry)
        for entry in generate_contact_centre_log(bills, contact_model)
    ]
    contact_centre_log = [message.to_log_entry() for message in contact_centre_messages]

    all_customers = _get_all_customers()
    cost_to_serve = build_cost_to_serve(all_records, all_customers)
    churn_risk = build_churn_risk(all_records, all_customers)
    home_move_win_rates = build_home_move_win_rates(churn_risk, all_customers, PRICE_DIFFERENTIAL_PCT)
    enterprise_value = build_enterprise_value(
        churn_risk, cost_to_serve, all_customers, PRICE_DIFFERENTIAL_PCT
    )

    avg_clarity = sum(b["clarity_score"] for b in bills) / len(bills)
    shocked = [b for b in bills if b["bill_shock_pct"] is not None]
    avg_bill_shock = sum(b["bill_shock_pct"] for b in shocked) / len(shocked) if shocked else 0.0
    total_bad_debt = sum(
        record["bad_debt_provision_gbp"]
        for records in payment_behaviour.values()
        for record in records
    )

    print("\n" + "=" * 60)
    print("=== Phase 4c billing experience layer (full portfolio) ===")
    print("=" * 60)

    print(f"\nBills generated:                 {len(bills)}")
    print(f"Average clarity score:            {avg_clarity:>12.3f}")
    print(f"Average bill shock (where shown): {avg_bill_shock:>12.1%}")
    print(f"Total bad debt provision:        £{total_bad_debt:>12.2f}")
    print(f"Avg complaint probability:        {contact_model['portfolio']['avg_complaint_probability']:>12.3f}")
    print(f"Service quality score:            {contact_model['portfolio']['service_quality_score']:>12.3f}")
    print(f"Enterprise value (4b):           £{enterprise_value['portfolio']['enterprise_value_gbp']:>12.2f} "
          f"across {enterprise_value['portfolio']['account_count']} billing accounts")
    print(f"Cost to serve (portfolio):       £{cost_to_serve['portfolio']['cost_to_serve_gbp']:>12.2f}")
    print(f"Net margin after cost to serve:  £{cost_to_serve['portfolio']['net_margin_gbp']:>12.2f}")

    print(f"\n{'Account':<8} {'Bills':>6} {'AvgClarity':>11} {'CreditRisk':>11} {'BadDebt£':>10}")
    for customer in CUSTOMERS:
        customer_id = customer["customer_id"]
        customer_bills = [b for b in bills if b["customer_id"] == customer_id]
        if not customer_bills:
            continue
        avg_customer_clarity = sum(b["clarity_score"] for b in customer_bills) / len(customer_bills)
        credit_risk = payment_behaviour[customer_id][0]["credit_risk"]
        bad_debt = sum(r["bad_debt_provision_gbp"] for r in payment_behaviour[customer_id])
        print(
            f"{customer_id:<8} {len(customer_bills):>6} {avg_customer_clarity:>11.3f} "
            f"{credit_risk:>11} {bad_debt:>10.2f}"
        )

    # Phase 8a: merge acquisition_spend and fixed_cost events into the ledger
    # CTS reconciliation fix (docs/staging/drafts/NEXT_PHASE.md option B):
    # also emit monthly cost_to_serve_event totals so ledger account 6100
    # ("Cost to Serve") stops always netting to £0 against the non-zero
    # figure `cost_to_serve` (above) already reports for pricing/CLV.
    cost_to_serve_ledger_events = build_cost_to_serve_ledger_events(all_records, all_customers)
    extra_events = (
        phase2b_result.get("acquisition_spend_events", [])
        + phase2b_result.get("fixed_cost_events", [])
        + [make_cost_to_serve_event(e["month"], e["amount_gbp"]) for e in cost_to_serve_ledger_events]
    )
    ledger_events = build_ledger(
        all_records, bills, payment_behaviour_module,
        extra_events=extra_events or None,
    )
    ledger_pnl = derive_pnl(ledger_events)
    ledger_meta = ledger_summary(ledger_events)

    return {
        "phase2b": phase2b_result,
        "bills": bills,
        "meter_read_log": meter_read_log,
        "credit_refund_log": credit_refund_log,
        "contact_centre_log": contact_centre_log,
        "payment_behaviour": payment_behaviour,
        "contact_model": contact_model,
        "cost_to_serve": cost_to_serve,
        "churn_risk": churn_risk,
        "home_move_win_rates": home_move_win_rates,
        "enterprise_value": enterprise_value,
        "price_differential_pct": PRICE_DIFFERENTIAL_PCT,
        "ledger_events": ledger_events,
        "ledger_pnl": ledger_pnl,
        "ledger_meta": ledger_meta,
        "won_successor_activations": phase2b_result.get("won_successor_activations", {}),
        # Phase 8a: growth mandate outputs
        "acquisition_spend_events": phase2b_result.get("acquisition_spend_events", []),
        "fixed_cost_events": phase2b_result.get("fixed_cost_events", []),
        "acquired_customers": phase2b_result.get("acquired_customers", []),
        "growth_mandate": phase2b_result.get("growth_mandate", "flat"),
    }


def _git_commit_hash() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def save_run_output_json(run_output: dict) -> tuple[Path, Path]:
    """Reduce `run_output` via `annual_report.extract_report_data()` and
    persist it to `docs/reports/run_output_latest.json` plus a versioned
    copy stamped with the current git commit hash and UTC timestamp.

    Returns (latest_path, versioned_path). Imported lazily to avoid a
    circular import (`annual_report` imports `main` from this module).
    """
    from saas.reporting.annual_report import extract_report_data

    data = extract_report_data(run_output)
    commit_hash = _git_commit_hash()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    data["_cache_meta"] = {
        "git_commit": commit_hash,
        "generated_at_utc": timestamp,
    }

    RUN_OUTPUT_VERSIONED_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2)

    RUN_OUTPUT_LATEST_PATH.write_text(payload)
    versioned_path = RUN_OUTPUT_VERSIONED_DIR / f"run_output_{commit_hash}_{timestamp}.json"
    versioned_path.write_text(payload)

    return RUN_OUTPUT_LATEST_PATH, versioned_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the combined Phase 2b+4b+4c pipeline")
    parser.add_argument(
        "--save-json", action="store_true",
        help="Persist the reduced report data to docs/reports/run_output_latest.json "
        "plus a versioned copy stamped with the git commit hash and timestamp",
    )
    args = parser.parse_args()

    _staging_dir = Path("docs/staging")
    _staging_dir.mkdir(parents=True, exist_ok=True)
    _run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    _pending_marker = _staging_dir / f"run_pending_{_run_ts}.md"
    _pending_marker.write_text(
        f"# Run in progress — action required on completion\n\n"
        f"Started: {_run_ts}\n\n"
        "When this run finishes: regenerate the annual report (`make report` or "
        "`python3 -m saas.reporting.annual_report --from-json docs/reports/run_output_latest.json`), "
        "update LATEST.md with key figures, commit, push to GitHub, and send NTFY digest.\n\n"
        "Delete this file once done.\n"
    )

    try:
        output = main()

        if args.save_json:
            latest_path, versioned_path = save_run_output_json(output)
            print(f"\nSaved report data to {latest_path} and {versioned_path}")

        # Write a completion marker so the next session knows results are ready to publish
        _complete_marker = _staging_dir / f"run_complete_{_run_ts}.md"
        _complete_marker.write_text(
            f"# Run complete — publish results\n\n"
            f"Completed: {datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}\n"
            f"Output: {latest_path if args.save_json else 'not saved (no --save-json)'}\n\n"
            "Action: regenerate annual report, update LATEST.md, commit, push, send NTFY.\n\n"
            "Delete this file once done.\n"
        )
        _pending_marker.unlink(missing_ok=True)

    except Exception as exc:
        import traceback

        from background.ntfy_utils import send_ntfy
        err_summary = f"{type(exc).__name__}: {exc}"
        send_ntfy(
            f"Run FAILED at save/extract step: {err_summary}\n"
            "Sim itself may have completed — check phase*_run.log",
            headers={"X-Priority": "5", "X-Tags": "rotating_light"},
        )
        traceback.print_exc()
        raise
