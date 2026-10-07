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

This module produces the read EVENT: delay, and actual-vs-estimated status.
It does not make the estimate. Estimating an unread period is the supplier's
own work (`company/billing/unread_month_estimate.py`, D48 slices 3-4). Phase 4
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
  was issued and left unpaid. It is the COMPANY's rule
  (company/billing/back_billing.py), not physics: the world no longer forces
  a read after 12 estimated months (W2_36, below).

READ ABSENCE PERSISTS (W2_36, 2026-10-05). A read-exposed household
(traditional, or smart in traditional mode this month) belongs for life to
one of two classes, drawn once from its id: a small HARD-TO-READ class read
about once in four years, and the rest, read memorylessly at the rate that
reproduces the published 12-month no-read share. Both the class share and the
target are read from docs/market_research/assumption_toggles.yaml (Q2,
director's ruling 2026-10-05), never typed here. The previous process -- an
independent 1/6 a month and a forced read at 12 -- could not leave anyone
unread past 13 months (Elexon RF leaves 3% of NHH energy unread at 14 months),
so the 12-month back-billing limit could never bind; and its 12-month no-read
share (0.048 measured) was an artefact of that cap. The derivations
(the Elexon curve is near-memoryless, pi <= 0.04, and 21BA-barred revenue is
invariant in pi) are in practitioner_questions_as_assumption_toggles.md Q2.

SMART MODE IS A STATE (W2_36, 2026-10-07). A smart meter not in smart mode
stays so for the account's life, at the register's share
(q6_smart_not_in_smart_mode_share), and its household is read like a
traditional one -- by the two classes above. Drawn afresh each month, as
before, a smart home could never go a year unread.

Deterministic dispatch: `random.Random(f"meterread_{customer_id}_{period_end}")`,
matching simulation/feedback_survey.py's convention.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

ASSUMPTION_TOGGLES_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "market_research" / "assumption_toggles.yaml")


def assumption_toggle(toggle_id: str, setting: str = "default") -> float:
    """One setting (`default`, `low` or `high`) of a registered assumption toggle."""
    rows = yaml.safe_load(ASSUMPTION_TOGGLES_PATH.read_text())["toggles"]
    for row in rows:
        if row["id"] == toggle_id:
            return float(row[setting])
    raise KeyError(f"{toggle_id} is not in {ASSUMPTION_TOGGLES_PATH.name}")


# --- Anchors (docs/market_research/ASSUMPTIONS.md, 2026-07-08) -------------

# Share of installed smart meters not in smart mode (register
# q6_smart_not_in_smart_mode_share; DESNZ Q4 2024 ~10%, Ofgem 2-15% by supplier).
# Blended elec/gas -- see module docstring. A STATE the meter holds
# (`is_not_in_smart_mode`), not a fresh draw each month.
SMART_METER_NOT_COMMUNICATING_RATE = assumption_toggle("q6_smart_not_in_smart_mode_share")

# How fast such a meter returns to smart mode is NOT ESTABLISHED: DESNZ and Ofgem
# publish the stock, not transitions, and the 90-day repair duty starts in 2026,
# after the window (read_access_and_theft_duties.md gap 9). So the state is held for
# the life of the account rather than given an invented exit rate.

# Automatic smart-meter transmission delay: near-real-time (WAN + DCC
# processing), a small number of days at most.
SMART_METER_DELAY_MEAN_DAYS = 1.5

# Manual/self-read submissions take materially longer to reach billing than
# an automatic smart transmission.
TRADITIONAL_DELAY_MEAN_DAYS = 9.0

# Bill-generation cutoff: a read arriving within this many days of period-end
# counts as "on time" for this bill; later than that, the bill is estimated
# and corrected once the read does arrive. Matches the delivery-lag window
# Phase 3 item 3 adds around issue_date.
READ_CUTOFF_DAYS_AFTER_PERIOD_END = 5

# Share of read-exposed households in the hard-to-read class (register
# q2_persistent_unread_share; swept 0 / 0.01 / 0.03 by its acceptance criterion).
PERSISTENT_UNREAD_SHARE = assumption_toggle("q2_persistent_unread_share")

# Share of domestic credit customers with no bill on an actual read in the past
# 12 months: the moment the read process is calibrated to (register
# q2_no_read_12m_share; Ofgem statutory consultation 16 Nov 2017 para 1.1).
NO_READ_12M_SHARE = assumption_toggle("q2_no_read_12m_share")

# Monthly probability a hard-to-read household's bill is on an actual read:
# "about once in four years", the register's own meaning for the class
# (q2_persistent_unread_share, practitioner_questions_as_assumption_toggles.md
# Q2 derivation 2). Not separately published.
HARD_TO_READ_MONTHLY_READ_RATE = 0.02


def on_time_share(mean_delay_days: float = TRADITIONAL_DELAY_MEAN_DAYS) -> float:
    """P(an arriving read beats the bill cutoff), for the delay draw `_sample_delay_days` makes."""
    return 1.0 - math.exp(-(READ_CUTOFF_DAYS_AFTER_PERIOD_END + 0.5) / mean_delay_days)


def solve_easy_rate(persistent_share: float, no_read_12m_share: float,
                    hard_rate: float = HARD_TO_READ_MONTHLY_READ_RATE) -> float:
    """Monthly rate at which the easy class's bills are on an actual read, so that the mixture
    leaves `no_read_12m_share` of households with no read-based bill in 12 months.

    Refuses, naming why, when the hard class alone already exceeds the target.
    """
    easy_part = no_read_12m_share - persistent_share * (1.0 - hard_rate) ** 12
    if easy_part <= 0.0 or persistent_share >= 1.0:
        raise ValueError(
            f"a hard-to-read share of {persistent_share} unread at {hard_rate}/month already leaves "
            f"more than {no_read_12m_share} of homes unread for a year: no easy-class rate reaches it")
    return 1.0 - (easy_part / (1.0 - persistent_share)) ** (1.0 / 12.0)


# Probability a read ARRIVES in a month, by class. The bill is on an actual
# read only if it also beats the cutoff, so the calibrated monthly rate is
# divided by the on-time share. Tests pin these two names to force a path.
TRADITIONAL_ACTUAL_READ_PROBABILITY = (
    solve_easy_rate(PERSISTENT_UNREAD_SHARE, NO_READ_12M_SHARE) / on_time_share())
HARD_TO_READ_ACTUAL_READ_PROBABILITY = HARD_TO_READ_MONTHLY_READ_RATE / on_time_share()


def is_hard_to_read(customer_id: str) -> bool:
    """The household's read class, drawn once from its id so it persists for life."""
    return random.Random(f"readclass_{customer_id}").random() < PERSISTENT_UNREAD_SHARE


def is_not_in_smart_mode(customer_id: str) -> bool:
    """Whether the account's smart meter is in traditional mode, drawn once from its id.

    Drawn afresh each month (before 2026-10-07) a smart home was read-exposed one month in ten
    and never went a year unread; reality is a meter that stays out of smart mode (lost WAN, not
    enrolled after a switch), whose household is then read like a traditional one.
    """
    return random.Random(f"smartmode_{customer_id}").random() < SMART_METER_NOT_COMMUNICATING_RATE

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
    consecutive_estimated_count: int,
) -> MeterReadEvent:
    """Simulate one customer-period's meter-read arrival.

    `consecutive_estimated_count` -- running count of consecutive estimated
    bills immediately prior to this one; caller tracks and threads it through
    across a customer's bill sequence.

    THE FEED SAYS WHETHER A READ ARRIVED, NOT WHAT TO BILL WITHOUT ONE (D48
    slice 4, 2026-10-06). An estimate is the supplier's own work, made from
    what it holds: `company/billing/unread_month_estimate.py`. The world used
    to make one here as well -- a flat trailing mean, and for the opening
    period, before any read, this period's TRUE consumption, which put the
    household's real use on the bill under an estimate's name. Two estimators
    for one decision is the shape the VAT rule took, so this one is gone and
    an estimated event carries no figure.
    """
    rng = random.Random(f"meterread_{customer_id}_{period_end}")

    communicating = meter_type == "smart" and not is_not_in_smart_mode(customer_id)

    if communicating:
        arrived_actual = True
    else:
        read_probability = (HARD_TO_READ_ACTUAL_READ_PROBABILITY if is_hard_to_read(customer_id)
                            else TRADITIONAL_ACTUAL_READ_PROBABILITY)
        arrived_actual = rng.random() < read_probability

    delay_days = _sample_delay_days(rng, meter_type, communicating)

    if arrived_actual and delay_days <= READ_CUTOFF_DAYS_AFTER_PERIOD_END:
        return MeterReadEvent(
            customer_id=customer_id,
            period_end=period_end,
            meter_type=meter_type,
            delay_days=delay_days,
            status="actual",
            true_consumption_kwh=true_consumption_kwh,
            consecutive_estimated_count=0,
        )

    return MeterReadEvent(
        customer_id=customer_id,
        period_end=period_end,
        meter_type=meter_type,
        delay_days=delay_days,
        status="estimated",
        true_consumption_kwh=true_consumption_kwh,
        consecutive_estimated_count=consecutive_estimated_count + 1,
        forced_catch_up=False,
    )


def read_event_to_log_entry(event: MeterReadEvent) -> dict:
    """The one serialisation of a read event into a published log entry.

    Single-sourced (2026-08-15) so the log the pipeline publishes and any
    other reader of the same events cannot drift in shape.
    """
    return {
        "customer_id": event.customer_id,
        "period_end": event.period_end,
        "meter_type": event.meter_type,
        "delay_days": event.delay_days,
        "status": event.status,
        "estimated_consumption_kwh": event.estimated_consumption_kwh,
        "true_consumption_kwh": event.true_consumption_kwh,
        "consecutive_estimated_count": event.consecutive_estimated_count,
        "forced_catch_up": event.forced_catch_up,
    }


def meter_read_log_from_events(events: list[MeterReadEvent]) -> list[dict]:
    """Publish the read events a bill run ACTUALLY billed on.

    This is the pipeline's read-log path (2026-08-15, EP8 finding "the meter
    seam is computed twice"): `company.billing.monthly_bill_assembly.
    build_monthly_bills` hands back the very `MeterReadEvent` each bill was
    assembled from -- including the SLC 21B final-read override, which only
    that call site applies -- and this projects them. ONE stream, two readers.

    The previous path (`generate_meter_read_log` below) RE-DERIVED the reads
    from the same seed and so could not see that override: three published
    rows of the 2026-08-14 run said `estimated` for a period whose own bill
    said `actual`. Re-derivation is also incoherent at the first real DUIS/
    n3rgy transport, which answers a request once and has no seed to replay.
    """
    return [read_event_to_log_entry(event) for event in events]


def generate_meter_read_log(
    bills: list[dict], customer_meter_types: dict[str, str]
) -> list[dict]:
    """Re-derive one read event per bill from the seed alone.

    Kept for callers that hold bills but NOT the events those bills were
    assembled from (tests, and any standalone analysis of a bill list). It is
    NOT the pipeline's path any more and must not become one again: it cannot
    see any decision the billing call site made about a read (today, the SLC
    21B final-read override), so its output can contradict the bills it was
    derived from. `meter_read_log_from_events` is the publishing path;
    `company.compliance.population_sanity.check_read_log_matches_billing_basis`
    is the control that fails when the two disagree.

    Bills must already be grouped/sorted chronologically per customer, as
    `company.billing.monthly_bill_assembly.build_monthly_bills` produces them.
    Returns plain JSON-serialisable dicts, in the same order as `bills`. An
    estimated entry carries no figure: the estimate is the company's, and only
    the bill run that made it can publish it.
    """
    consecutive_by_customer: dict[str, int] = {}
    log: list[dict] = []
    for bill in bills:
        cid = bill["customer_id"]
        event = simulate_read(
            cid, bill["period_end"], customer_meter_types.get(cid, "traditional"),
            bill["total_consumption_kwh"], consecutive_by_customer.get(cid, 0),
        )
        consecutive_by_customer[cid] = event.consecutive_estimated_count
        log.append(read_event_to_log_entry(event))
    return log


class SimulatedReadFeed:
    """The world's side of `company.interfaces.bill_assembly.ReadArrivalFeed`.

    Added by KNIFE pass 3 (`A_composition_lift`, step 11, 2026-08-10) when
    monthly bill assembly moved to `company/billing/monthly_bill_assembly.py`.
    Deciding whether a read ARRIVES is world physics; assembling a bill from
    what arrived is the supplier's own work. This class is the whole of the
    world's half of that split.

    It is deliberately a thin pass-through and MUST stay one: it calls the same
    `meter_type_for_customer` / `simulate_read` / `MeterReadEvent` with the same
    arguments in the same order the billing code used inline before the move, so
    the identical objects come back and no run's numbers change. Any physics
    added here would be physics the old inline path did not have.
    """

    def meter_type_for(self, customer: Optional[dict]) -> str:
        """Carries the inline path's own `if customer_data else` fallback."""
        return meter_type_for_customer(customer) if customer else "traditional"

    def read_for(
        self,
        customer_id: str,
        period_end: str,
        meter_type: str,
        true_consumption_kwh: float,
        consecutive_estimated_count: int,
    ) -> MeterReadEvent:
        return simulate_read(
            customer_id, period_end, meter_type, true_consumption_kwh,
            consecutive_estimated_count,
        )

    def final_read_for(
        self,
        customer_id: str,
        period_end: str,
        meter_type: str,
        true_consumption_kwh: float,
    ) -> MeterReadEvent:
        """A closing read for an account leaving supply.

        The company decides WHEN to demand one (SLC 21B final bill); what such a
        read looks like is the world's business, which is why the construction
        lives here and not in the billing code.
        """
        return MeterReadEvent(
            customer_id=customer_id, period_end=period_end,
            meter_type=meter_type, delay_days=0, status="actual",
            true_consumption_kwh=true_consumption_kwh,
            consecutive_estimated_count=0, forced_catch_up=True,
        )
