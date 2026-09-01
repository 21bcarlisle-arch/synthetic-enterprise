"""Monthly bill assembly — the supplier's OWN billing run.

WHY THIS LIVES COMPANY-SIDE (KNIFE pass 3, `A_composition_lift`, step 11,
2026-08-10). Assembling a customer's monthly bill from that customer's settled
records is a supplier's own work: it decides the billing period, whether the
bill goes out on a real read or an ESTIMATE, and — when a real read finally
arrives — how a run of estimated bills is reconciled under the Ofgem SLC 31A
back-billing cap. None of that is world physics; every line of it is the
company's own routine, which a real supplier is free to change without telling
anyone. It sat in `simulation/run_phase4c_on_phase2b.py` for composition
reasons, where it reached into `company/billing/` and `saas/` for three of that
module's thirteen wall crossings.

THIS IS THE EMITTER TWO OTHER DESIGNS WERE WAITING ON. `B5` (collections tone)
and `B4` (DD review outcome) each recorded, in their own seam modules, that
they could deliver only a PULL and not the PUSH their design asks for, for one
structural reason stated identically in both: there was no company-side bill
emitter to stamp an attribute onto, because bill emission itself sat on the SIM
side. It no longer does. Both docstrings are updated in the same commit; the
pushes themselves are separate work and are NOT done here.

WHAT DID NOT MOVE, AND WHY THAT IS THE POINT. Whether a meter read actually
ARRIVES is world physics — a supplier observes reads, it does not decide them.
So this module never imports the simulated world. It receives a `ReadArrivalFeed`
(below) from its caller and asks it what arrived. That inversion is the whole
cut: had `build_monthly_bills` been moved with its `simulation.meter_reads`
imports intact, it would have traded three class-(b) crossings for three
class-(a) ones — the STRICTLY FORBIDDEN direction, which is at zero and stays
there.

BEHAVIOUR IS UNCHANGED AND THAT IS BY CONSTRUCTION, NOT BY ASSERTION. The feed
is injection, not reimplementation: the world-side adapter
(`simulation.meter_reads.SimulatedReadFeed`) calls the same
`meter_type_for_customer` / `simulate_read` with the same arguments in the same
order as the inlined code did, so the identical objects come back. There is no
seed to re-derive and no second code path to keep in step — the deliberate
difference from the read DUPLICATION this module's own docstring below still
records as a follow-up.

Epistemic note, because this module reads `true_*` fields: an ESTIMATED bill
carries the true-vs-billed pair for divergence analytics only (same treatment
as `MeterReadMessage.true_consumption_kwh` — see `tools/meter_read_port.py`).
The one place a true figure drives a DECISION is `_resolve_catchup`, and it
does so only once an ACTUAL read has arrived — at which point the real
consumption is genuinely known to the supplier, which is what a catch-up bill
IS.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from company.billing.account_adjustment_register import (
    AccountAdjustmentRecord,
    AdjustmentDirection,
    AdjustmentStatus,
    AdjustmentType,
)
from company.billing.back_billing import BackBillingAssessment, BackBillingReason
from company.interfaces.supply_book import registered_point as get_customer
from saas.bill_generator import (
    BILL_SHOCK_BASELINE_FLOOR_GBP,
    BILL_SHOCK_PENALTY_FACTOR,
    MAX_CLARITY_SCORE,
    MIN_CLARITY_SCORE,
    generate_bill,
)

__all__ = [
    "CATCHUP_MATERIALITY_THRESHOLD_GBP",
    "ReadArrival",
    "ReadArrivalFeed",
    "build_monthly_bills",
]


@runtime_checkable
class ReadArrival(Protocol):
    """What the company can see about one customer-period's read.

    Structural on purpose: the world's own `MeterReadEvent` satisfies it as-is,
    so nothing had to change shape for this cut. The company reads exactly these
    three attributes and nothing else.
    """

    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


@runtime_checkable
class ReadArrivalFeed(Protocol):
    """The supplier's meter-read feed, supplied by whoever runs the billing.

    In the simulation that is `simulation.meter_reads.SimulatedReadFeed`; going
    live it is a real D0010/DTC feed adapter, behind this unchanged Protocol —
    the same swap `tools/meter_read_port.py::MeterReadPort` was built for.
    """

    def meter_type_for(self, customer: dict | None) -> str:
        """The customer's meter type ('traditional' | 'smart' | ...)."""

    def read_for(
        self,
        customer_id: str,
        period_end: str,
        meter_type: str,
        true_consumption_kwh: float,
        trailing_actuals_kwh: list[float],
        consecutive_estimated_count: int,
    ) -> ReadArrival:
        """Whether a read arrived for this customer-period, and what it said."""

    def final_read_for(
        self,
        customer_id: str,
        period_end: str,
        meter_type: str,
        true_consumption_kwh: float,
    ) -> ReadArrival:
        """A closing read for an account leaving supply (SLC 21B final bill).

        The company decides WHEN one is demanded; the feed says what such a
        read looks like, because constructing a read is the world's business.
        """


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

    write_off_adjustment: AccountAdjustmentRecord | None = None

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

        # ADVISOR_STEER_BACKBILLING_GATE.md item 1: "the unrecoverable
        # tranche is a WRITE-OFF -- a real P&L event (write-off machinery
        # exists since the C1 fix)". That machinery is
        # company/billing/account_adjustment_register.py's
        # AdjustmentType.BACK_BILLING_CREDIT -- built and tested, never
        # wired to this mechanism until now (R3: reuse the one real
        # write-off mechanism rather than invent a second, competing one).
        # Auto-applied, not pending-approval: SLC 21BA makes this
        # write-off a legal requirement, not a discretionary goodwill
        # spend the register's approval tiers were designed to gate.
        if written_off_gbp > 0:
            write_off_adjustment = AccountAdjustmentRecord(
                record_id="ADJ-BB-" + customer_id + "-" + period_end,
                account_id=customer_id,
                adjustment_type=AdjustmentType.BACK_BILLING_CREDIT,
                direction=AdjustmentDirection.CREDIT,
                amount_gbp=round(written_off_gbp, 2),
                reason=(
                    "SLC 21BA 12-month back-billing cap: consumption "
                    f"period {period_start} to {period_end} pre-dates the "
                    "recoverable window with no recorded customer-fault "
                    "attribution -- excess written off, not charged"
                ),
                raised_date=billing_date,
                status=AdjustmentStatus.APPLIED,
                approved_by="system:slc_21ba_cap",
                applied_date=billing_date,
            )
    else:
        chargeable_gbp = raw_delta_gbp
        written_off_gbp = 0.0
        cap_applied = False
        direction = "overcharge"

    result = {
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
    if write_off_adjustment is not None:
        result["write_off_adjustment_id"] = write_off_adjustment.record_id
        result["write_off_adjustment_reason"] = write_off_adjustment.reason
        result["write_off_adjustment_status"] = write_off_adjustment.status.value
    return result


def build_monthly_bills(
    all_records: list[dict],
    read_feed: ReadArrivalFeed,
    churned_ids: set[str] | None = None,
    read_events_out: list | None = None,
) -> list[dict]:
    """Group the supplier's own settled records into one bill per customer per
    calendar month, in chronological order, via
    `saas.bill_generator.generate_bill`.

    POINT-IN-TIME BOUNDING, stated because this is company-side code handed a
    whole settled history (the `block_point_in_time_read` heuristic flags that
    shape, correctly, and this is the answer rather than a suppression). No
    as_of/bisect bound is needed here because no bill reads forward of itself:
    the records are PARTITIONED per customer per calendar month before any bill
    is built, each bill is priced from its OWN month's partition only, and every
    cross-month read is strictly backward — `previous_bill_total_gbp` from the
    prior month, `_year_ago_month` from twelve months earlier,
    `_prior_calendar_month` for the shock-aftermath exclusion, and the pending
    estimated run accumulated since the customer's LAST actual read. The one
    forward-looking fact is `is_final_bill_for_customer`, which is closure, not
    foresight: a supplier knows an account is leaving supply when it bills it
    out. This is a verbatim move of long-standing logic, so the property is
    inherited, not newly claimed — nothing about the ordering changed here.

    `read_feed` is the supplier's meter-read feed (see `ReadArrivalFeed`): the
    world says what arrived, this function decides what to bill.

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

    `read_events_out` (2026-08-15, EP8 finding "the meter seam is computed
    twice"): an optional sink the caller passes to receive the `MeterReadEvent`
    each bill was ACTUALLY assembled from, in `bills` order, one per bill. It
    is how the published meter-read log stops being a second, independent
    re-derivation of the same decision -- see
    `simulation.meter_reads.meter_read_log_from_events`. Nothing about the
    bills changes when it is passed; it is a pure observation of work already
    done here, which is why the events (not the bill dicts) carry it.
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
        # consecutive-estimated count) as generate_meter_read_log().
        #
        # 2026-08-15 (EP8 finding, docs/design/simplifications/
        # EP8_adapter_dcc_duis.yaml finding 2): this used to say "the identical
        # seed means the two always agree", and that was FALSE -- this call
        # site alone applies the SLC 21B final-read override below, so a
        # separately re-derived log disagreed on every churned account's final
        # bill (3 of 3 overrides in the 2026-08-14 run). THIS is now the only
        # place the decision is made: the events are handed back through
        # `read_events_out` and the published log is projected from them.
        meter_type = read_feed.meter_type_for(customer_data)
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
            event = read_feed.read_for(
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
                event = read_feed.final_read_for(
                    customer_id, true_bill["period_end"], meter_type,
                    true_bill["total_consumption_kwh"],
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
                    if "write_off_adjustment_id" in catchup:
                        bill["catchup_write_off_adjustment_id"] = catchup["write_off_adjustment_id"]
                        bill["catchup_write_off_adjustment_reason"] = catchup["write_off_adjustment_reason"]
                        bill["catchup_write_off_adjustment_status"] = catchup["write_off_adjustment_status"]
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
                    # Same floor as `generate_bill` and for the same reason: a baseline too
                    # small to divide by is refused, not divided by anyway.
                    if (
                        previous_bill_total_gbp is not None
                        and abs(previous_bill_total_gbp) >= BILL_SHOCK_BASELINE_FLOOR_GBP
                    ):
                        old_shock = bill.get("bill_shock_pct") or 0.0
                        # `abs()` on the DENOMINATOR too -- see `saas/bill_generator` for why.
                        # An issued total can be negative (a catch-up credit); a true bill never
                        # was, which is why this only became reachable when the baseline moved to
                        # the issued bill.
                        new_shock = abs(
                            bill["total_amount_gbp"] - previous_bill_total_gbp
                        ) / abs(previous_bill_total_gbp)
                        bill["bill_shock_pct"] = new_shock
                        # The denominator moves with the ratio, or publishing it would be worse
                        # than not publishing it: a baseline that disagreed with the shock beside
                        # it would read as authoritative and be wrong, and the control that checks
                        # reproducibility would be checking this line against itself.
                        bill["bill_shock_baseline_gbp"] = previous_bill_total_gbp
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
            # One event per bill, in bills order -- appended here, in the same
            # step that appends the bill, so the two lists cannot fall out of
            # alignment by construction (the caller joins them positionally).
            if read_events_out is not None:
                read_events_out.append(event)
            # THE BILL THE HOUSEHOLD WAS ISSUED, not the one it would have received had the read
            # been actual (2026-09-01, pre-registered in `WORKER_PREREGISTRATION_WHAT_BASELINING_
            # ON_THE_ISSUED_BILL_MUST_SHOW_2026-09-01`, landed as `34d5120c7` BEFORE this change).
            #
            # This was `true_bill["total_amount_gbp"]`, so `bill_shock_pct` differenced every bill
            # against a bill nobody received: 63% of this book is estimated, the household got the
            # ESTIMATE, and the instrument measured against the TRUTH. Measured on the published
            # book, 9,813 of 10,655 pairs (92.1%) reproduce against the previous true total and
            # 3,198 (30.0%) against the issued one -- which is what made the field irreproducible
            # from its own artefact.
            #
            # WHY IT MATTERS RATHER THAN BEING TIDIER: on a run of estimates the household receives
            # the SAME estimate each month, so its experienced movement is near zero, and then the
            # catch-up month is one large jump. Flat, flat, flat, bang -- which is the shape the
            # published record describes ("a catch-up after months of estimates") and the shape the
            # true-bill baseline smooths away, because the true series moves every month while the
            # household's actual bills did not.
            #
            # AND IT NARROWS A TIMING EXPOSURE. `true_bill` is priced off the real settlement
            # records for a month the company has only ESTIMATED, so baselining on it made a
            # published field depend on a quantity the company could not have known when it issued
            # the bill. The issued total is what the company itself sent.
            previous_bill_total_gbp = bill["total_amount_gbp"]

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

