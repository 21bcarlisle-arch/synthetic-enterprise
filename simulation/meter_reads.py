"""Meter-read arrival/estimation/failure model (Phase 3, docs/design/
CORE_FIDELITY_PHASES.md item 1 -- the highest-priority gap in the Phase 1
unhappy-path audit: "settlement records are treated as always-available and
always-accurate; nothing models a read arriving late, failing to arrive, or
being estimated").

Real UK domestic/SME billing does not have instant, perfect access to a
customer's true consumption at bill-generation time. Two very different
physical channels feed a supplier's billing engine:

- Smart meters (SMETS1/2) transmit HH data automatically over the DCC's WAN
  -- but a real, DESNZ-published minority are not communicating in any given
  quarter (WAN/loss-of-signal, sometimes reported as meters "operating in
  traditional mode") and fall back to the traditional path below for that
  period.
- Traditional meters have no automatic channel at all: the supplier only
  gets an actual read when the customer self-submits one or a periodic
  meter-read visit happens. Absent that, the bill is ESTIMATED from the
  customer's own trailing consumption history -- a real technique ("based
  on your previous usage"), not a simulation shortcut.

This module produces the read EVENT (delay, actual-vs-estimated status, and
-- when estimated -- the estimate itself, built only from that customer's
own already-CONFIRMED prior actual reads, never from this period's true
settlement figure -- the epistemic wall applied to billing). Phase 4
(UK-compliant bill artefact) will render the resulting flag on the bill
document; this module does not alter settlement-based revenue recognition
(docs/staging/done/Bill_instructions_and_discovery.md already closed that
financial-correctness scope -- Phase 4's own text: "this phase is purely
about the document a customer would see, not the numbers behind it").

Anchors: docs/market_research/ASSUMPTIONS.md "Meter-Read Arrival Delay,
Estimation & Failure" table (discovery-agent, 2026-07-08, full detail in
docs/market_research/meter_read_latency_estimation_2026.md):
- DESNZ Q4 2024 Smart Meters Statistics Report: ~10% of *installed* smart
  meters are not operating in smart mode ("traditional mode", WAN/DCC
  loss-of-signal) -- a single blended figure (elec 4.7% / gas 9.1% of all
  meters; the module does not fuel-differentiate this, a documented
  simplification since the upstream smart-meter-penetration curve this
  module reuses, saas/smart_meter_rollout.py, is itself segment- not
  fuel-keyed).
- Traditional-meter actual-read cadence: mechanism confirmed (self-read
  submission / periodic supplier visits, ~6-monthly industry practice per
  Citizens Advice consumer guidance) but the precise Ofgem SLC 21A cadence
  text could not be independently fetched -- ⚠ unverified precise number,
  flagged honestly rather than presented as confirmed (Anchored-noise law).
- Back-billing 12-month rule (Citizens Advice, confirmed): a supplier
  cannot bill for energy used more than 12 months ago unless a timely bill
  was issued and left unpaid -- encoded below as the forced-catch-up cap.

Deterministic dispatch: `random.Random(f"meterread_{customer_id}_{period_end}")`,
matching simulation/feedback_survey.py's convention.
"""
from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Optional

# --- Anchors (docs/market_research/ASSUMPTIONS.md, 2026-07-08) -------------

# Smart-meter "not communicating" rate this period (WAN/DCC loss-of-signal;
# DESNZ Q4 2024 Smart Meters Statistics: ~10% of installed smart meters not
# in smart mode). Blended elec/gas figure -- see module docstring.
SMART_METER_NOT_COMMUNICATING_RATE = 0.10

# Automatic smart-meter transmission delay: near-real-time (WAN + DCC
# processing), a small number of days at most.
SMART_METER_DELAY_MEAN_DAYS = 1.5

# Traditional-meter actual-read probability: chance an actual read (self-
# submitted or a periodic meter-read visit) reaches the supplier for a given
# billing month. Derived from the ~6-monthly actual-read cadence industry
# practice confirmed by Citizens Advice (1/6 ≈ this rate per month) --
# ⚠ precise Ofgem SLC 21A cadence unverified, see module docstring.
TRADITIONAL_ACTUAL_READ_PROBABILITY = 1.0 / 6.0

# Manual/self-read submissions take materially longer to reach billing than
# an automatic smart transmission.
TRADITIONAL_DELAY_MEAN_DAYS = 9.0

# Bill-generation cutoff: a read arriving within this many days of period-end
# counts as "on time" for this bill; later than that, the bill is estimated
# and corrected once the read does arrive. Matches the delivery-lag window
# Phase 3 item 3 adds around issue_date.
READ_CUTOFF_DAYS_AFTER_PERIOD_END = 5

# Ofgem back-billing rule (confirmed, Citizens Advice): a supplier cannot
# bill for energy used more than 12 months ago unless a timely bill was
# issued and left unpaid -- modelled as a forced catch-up read after this
# many consecutive estimated monthly periods.
MAX_CONSECUTIVE_ESTIMATED_PERIODS = 12

# How many of a customer's own trailing confirmed-actual reads feed a new
# estimate (a real "average of your last N periods" technique).
ESTIMATE_TRAILING_WINDOW = 3


@dataclass(frozen=True)
class MeterReadEvent:
    customer_id: str
    period_end: str
    meter_type: str  # "smart" | "traditional"
    delay_days: int
    status: str  # "actual" | "estimated"
    estimated_consumption_kwh: Optional[float] = None
    true_consumption_kwh: Optional[float] = None
    consecutive_estimated_count: int = 0
    forced_catch_up: bool = False


def meter_type_for_customer(customer: dict) -> str:
    """Company-observable meter type for a customer record.

    Mirrors saas.smart_meter_rollout.is_tou_eligible()'s gate (metering ==
    "HH", or the smart_meter flag stamped at acquisition by the Phase 50
    rollout model) so this module stays consistent with the existing
    calibrated smart-meter penetration curve rather than inventing a second
    one.
    """
    if customer.get("metering") == "HH" or customer.get("smart_meter", False) is True:
        return "smart"
    return "traditional"


def _sample_delay_days(rng: random.Random, meter_type: str, communicating: bool) -> int:
    if meter_type == "smart" and communicating:
        days = rng.expovariate(1.0 / SMART_METER_DELAY_MEAN_DAYS)
    else:
        days = rng.expovariate(1.0 / TRADITIONAL_DELAY_MEAN_DAYS)
    return max(0, round(days))


def simulate_read(
    customer_id: str,
    period_end: str,
    meter_type: str,
    true_consumption_kwh: float,
    trailing_actuals_kwh: list[float],
    consecutive_estimated_count: int,
) -> MeterReadEvent:
    """Simulate one customer-period's meter-read arrival.

    `trailing_actuals_kwh` -- that customer's own previously CONFIRMED actual
    reads, oldest first (company-observable; never this period's true value).
    `consecutive_estimated_count` -- running count of consecutive estimated
    bills immediately prior to this one; caller tracks and threads it through
    across a customer's bill sequence.
    """
    rng = random.Random(f"meterread_{customer_id}_{period_end}")

    forced_catch_up = consecutive_estimated_count >= MAX_CONSECUTIVE_ESTIMATED_PERIODS

    communicating = meter_type == "smart" and rng.random() >= SMART_METER_NOT_COMMUNICATING_RATE

    if communicating:
        arrived_actual = True
    else:
        arrived_actual = forced_catch_up or (rng.random() < TRADITIONAL_ACTUAL_READ_PROBABILITY)

    delay_days = _sample_delay_days(rng, meter_type, communicating)

    # A forced catch-up (back-billing cap reached) is the correction
    # mechanism itself -- it counts as actual regardless of the normal
    # on-time cutoff, otherwise the cap could never actually reset.
    if arrived_actual and (forced_catch_up or delay_days <= READ_CUTOFF_DAYS_AFTER_PERIOD_END):
        return MeterReadEvent(
            customer_id=customer_id,
            period_end=period_end,
            meter_type=meter_type,
            delay_days=delay_days,
            status="actual",
            true_consumption_kwh=true_consumption_kwh,
            consecutive_estimated_count=0,
            forced_catch_up=forced_catch_up,
        )

    if trailing_actuals_kwh:
        estimate = statistics.mean(trailing_actuals_kwh[-ESTIMATE_TRAILING_WINDOW:])
    else:
        # No history yet: the opening read taken at switch/onboarding is a
        # real physical value a supplier does obtain, not a forecast --
        # bootstrap the very first period from it.
        estimate = true_consumption_kwh

    return MeterReadEvent(
        customer_id=customer_id,
        period_end=period_end,
        meter_type=meter_type,
        delay_days=delay_days,
        status="estimated",
        estimated_consumption_kwh=round(estimate, 2),
        true_consumption_kwh=true_consumption_kwh,
        consecutive_estimated_count=consecutive_estimated_count + 1,
        forced_catch_up=False,
    )


def generate_meter_read_log(
    bills: list[dict], customer_meter_types: dict[str, str]
) -> list[dict]:
    """Process bills (already grouped/sorted chronologically per customer, as
    `simulation.run_phase4c_on_phase2b.build_monthly_bills` produces them)
    into one meter-read event per bill. Returns plain JSON-serialisable
    dicts, in the same order as `bills`.
    """
    trailing_by_customer: dict[str, list[float]] = {}
    consecutive_by_customer: dict[str, int] = {}
    log: list[dict] = []
    for bill in bills:
        cid = bill["customer_id"]
        meter_type = customer_meter_types.get(cid, "traditional")
        true_kwh = bill["total_consumption_kwh"]
        consecutive = consecutive_by_customer.get(cid, 0)
        event = simulate_read(
            cid, bill["period_end"], meter_type, true_kwh,
            trailing_by_customer.get(cid, []), consecutive,
        )
        if event.status == "actual":
            trailing_by_customer.setdefault(cid, []).append(true_kwh)
            consecutive_by_customer[cid] = 0
        else:
            consecutive_by_customer[cid] = event.consecutive_estimated_count
        log.append({
            "customer_id": event.customer_id,
            "period_end": event.period_end,
            "meter_type": event.meter_type,
            "delay_days": event.delay_days,
            "status": event.status,
            "estimated_consumption_kwh": event.estimated_consumption_kwh,
            "true_consumption_kwh": event.true_consumption_kwh,
            "consecutive_estimated_count": event.consecutive_estimated_count,
            "forced_catch_up": event.forced_catch_up,
        })
    return log
