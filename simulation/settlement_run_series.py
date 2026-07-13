"""World-side wiring of a real settled book into the settlement-run revision
timetable (W3_2_settlement_timetable, L2 integration step).

simulation/settlement_timetable.py::emit_settlement_timetable() is the pure
MECHANISM -- given a delivery-time (initial) figure and the true final
figure, it emits the R1/R2/R3/RF revision sequence on the bitemporal spine.
This module is the ORCHESTRATION that feeds it REAL settled data (matching
simulation/README.md's "room with the clock on the wall" pattern -- code
here may read both sides of the seam, as long as it only ever hands over
what was knowable at the simulated moment).

WHERE THE REVISION GAP COMES FROM (real, not fabricated -- Historical
Ground Truth / R12 / R13):
UK settlement reconciliation restates a supplier's BILLED figure as
estimated consumption is replaced by actual metered consumption over the
R1..RF runs (company/regulatory/settlement_reconciliation.py's own words:
"Outstanding reconciliation pool: billed revenue still subject to
adjustment"; "actual < estimated consumption -> net credit in late
reconciliation"). The sim already produces BOTH figures from real,
independent mechanisms:

  * the TRUE final settled figure -- simulation/settlement.py::run_settlement
    (and the hedge-aware generators) settle from the customer's TRUE
    consumption shape; this is the RF / true-final value, UNCHANGED.
  * the DELIVERY-TIME estimate -- simulation/meter_reads.py emits, per bill
    period, an `estimated_consumption_kwh` built ONLY from that customer's
    own prior CONFIRMED actual reads (never this period's true value -- the
    blindfold applied to billing). When a read arrives late/missing the
    bill is estimated; that estimate is exactly the delivery-time figure the
    initial settlement run would have used.

So the initial/final gap is a genuine, pre-existing consequence of the
meter-read model, NOT a number invented here and NOT tuned toward any P&L
target. This module only READS those two existing outputs and derives the
initial figure by scaling the true settled value by the book's own
estimated/true consumption ratio for the period -- it never mutates a
settled record, never changes a final settled figure or final margin. The
RF value the timetable resolves to is, by construction, the untouched true
settled figure (final-value-neutral -- proven in
tests/simulation/test_settlement_run_series.py::TestFinalValueNeutrality).

GRANULARITY (documented simplification, R10): real Elexon runs are keyed
per settlement DAY; the meter-read estimate is a per-bill-MONTH figure. This
module aggregates the settled book to the (book, bill-month) level and emits
ONE timetable per month, valid_time = that month's last settled date -- the
honest match to where the estimate's own granularity lives, and the same
book/monthly aggregation the company-side reconciliation exposure model
already uses. Per-settlement-day emission would require distributing the
monthly estimate across days by a proxy shape; deferred as an L3 refinement.
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict
from typing import Callable

from company.interfaces.bitemporal_event_log import BitemporalEventLog
from simulation.settlement_timetable import (
    MeterType,
    SettlementRunEvent,
    emit_settlement_timetable,
)


def _month_key(date_str: str) -> str:
    """'YYYY-MM-DD' -> 'YYYY-MM' (the bill-month bucket)."""
    return date_str[:7]


def _estimated_consumption_for_period(event: dict) -> float | None:
    """The delivery-time consumption figure a bill for this meter-read event
    would have settled on. An 'actual' read has no estimation gap (the true
    value was known in time); an 'estimated' read carries its own estimate.
    Returns None if this event carries no usable figure."""
    if event.get("status") == "estimated" and event.get("estimated_consumption_kwh") is not None:
        return float(event["estimated_consumption_kwh"])
    if event.get("status") == "actual" and event.get("true_consumption_kwh") is not None:
        # An actual read settles at the true value -- no revision gap.
        return float(event["true_consumption_kwh"])
    return None


def build_settlement_revision_log(
    settled_records: list[dict],
    meter_read_log: list[dict],
    *,
    book_id: str = "book",
    value_field: str = "revenue_gbp",
    consumption_field: str = "consumption_kwh",
    meter_type: MeterType = "non_HH",
    log: BitemporalEventLog | None = None,
    allow_out_of_band: bool = False,
) -> tuple[BitemporalEventLog, dict[str, list[SettlementRunEvent]]]:
    """Emit the real R1/R2/R3/RF revision sequence for a settled book, one
    timetable per bill-month, into a bitemporal log.

    `settled_records` -- the real output of a settlement generator
    (simulation/settlement.py::run_settlement etc.): a flat list of dicts
    each carrying at least `customer_id`, `settlement_date` ('YYYY-MM-DD'),
    `consumption_field` and `value_field`. This is the TRUE, final book.
    It is only READ here, never mutated.

    `meter_read_log` -- the real output of
    simulation/meter_reads.py::generate_meter_read_log: one event per
    (customer, bill period_end) carrying the delivery-time
    `estimated_consumption_kwh` (when the bill was estimated) and the
    `true_consumption_kwh`. This supplies the genuine delivery-time estimate.

    For each (book, bill-month):
      true_final = sum of `value_field` over the month's settled records
                   (the UNCHANGED true settled figure -> becomes RF exactly)
      ratio      = book estimated consumption / book true consumption
                   for the month (1.0 when every read was actual, or when a
                   customer-month has no meter-read event)
      initial    = true_final * ratio   (the delivery-time estimated figure)

    `emit_settlement_timetable` then produces the initial + R1/R2/R3/RF
    records; RF resolves EXACTLY to `true_final` (final-value-neutral).

    Returns (log, {month_key: [SettlementRunEvent, ...]}).
    """
    if log is None:
        log = BitemporalEventLog()

    # (customer_id, month) -> delivery-time estimated consumption for that bill.
    est_by_cust_month: dict[tuple[str, str], float] = {}
    for event in meter_read_log:
        cid = event.get("customer_id")
        period_end = event.get("period_end")
        if cid is None or period_end is None:
            continue
        est = _estimated_consumption_for_period(event)
        if est is not None:
            est_by_cust_month[(cid, _month_key(period_end))] = est

    # Aggregate the settled book per month: true consumption (per customer, so
    # we can pair it with each customer's own estimate), true settled value,
    # and the delivery anchor date (the month's last settled date).
    month_true_cons: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    month_value: dict[str, float] = defaultdict(float)
    month_anchor: dict[str, str] = {}
    for rec in settled_records:
        cid = rec["customer_id"]
        sdate = rec["settlement_date"]
        mkey = _month_key(sdate)
        month_true_cons[mkey][cid] += float(rec[consumption_field])
        month_value[mkey] += float(rec[value_field])
        if mkey not in month_anchor or sdate > month_anchor[mkey]:
            month_anchor[mkey] = sdate

    events_by_month: dict[str, list[SettlementRunEvent]] = {}
    for mkey in sorted(month_value.keys()):
        true_final_value = month_value[mkey]

        book_true = 0.0
        book_est = 0.0
        for cid, true_cons in month_true_cons[mkey].items():
            book_true += true_cons
            # A customer-month with no meter-read event settles at its true
            # value (no revision) -- honest default, never a fabricated gap.
            book_est += est_by_cust_month.get((cid, mkey), true_cons)

        ratio = (book_est / book_true) if book_true else 1.0
        initial_value = true_final_value * ratio

        delivery_date = dt.date.fromisoformat(month_anchor[mkey])
        events = emit_settlement_timetable(
            log,
            entity_id=book_id,
            fact_type=f"settlement_{value_field}",
            delivery_date=delivery_date,
            initial_value=initial_value,
            true_final_value=true_final_value,
            meter_type=meter_type,
            allow_out_of_band=allow_out_of_band,
        )
        events_by_month[mkey] = events

    return log, events_by_month


def bills_from_settled_records(
    settled_records: list[dict],
    *,
    consumption_field: str = "consumption_kwh",
) -> list[dict]:
    """Roll a flat settled series up into the monthly-bill shape
    simulation/meter_reads.py::generate_meter_read_log consumes: one dict
    per (customer, bill-month) with `customer_id`, `period_end` (the month's
    last settled date) and `total_consumption_kwh`, chronologically ordered
    per customer. This is the same aggregation the real bill pipeline
    performs -- provided here so a settled book can be turned into a
    meter-read log (and hence a revision log) without reaching into the
    Phase-4 bill machinery. `total_consumption_kwh` is the customer's TRUE
    monthly consumption; the estimation happens inside meter_reads.py."""
    by_cust_month: dict[tuple[str, str], dict] = {}
    for rec in settled_records:
        cid = rec["customer_id"]
        sdate = rec["settlement_date"]
        mkey = _month_key(sdate)
        key = (cid, mkey)
        bucket = by_cust_month.get(key)
        if bucket is None:
            by_cust_month[key] = {
                "customer_id": cid,
                "period_end": sdate,
                "total_consumption_kwh": float(rec[consumption_field]),
            }
        else:
            bucket["total_consumption_kwh"] += float(rec[consumption_field])
            if sdate > bucket["period_end"]:
                bucket["period_end"] = sdate
    # Chronological per customer (meter_reads.py threads trailing history in order).
    return sorted(by_cust_month.values(), key=lambda b: (b["customer_id"], b["period_end"]))
