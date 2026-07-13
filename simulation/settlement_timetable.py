"""World-side settlement-run revision timetable (W3_2_settlement_timetable).

Real UK settlement is not a single, final-form figure produced at delivery
time -- it is revised over a sequence of real Elexon settlement runs:
R1 (~1 month post-delivery), R2 (~3 months), R3 (~5 months), and RF (Final
Reconciliation, ~28 months), each resolving a further share of the total
adjustment volume (60% / 25% / 12% / 3% respectively). This module is the
SIM/WORLD side of that mechanism -- it produces the sequence of revised
settlement figures a real supplier would actually observe over time, one
run at a time. It does NOT model the company's own exposure/risk estimate
of this timetable; that is company/regulatory/settlement_reconciliation.py
(company-side, already built, Elexon-anchored) -- decisively a different
atom, see this atom's own DISCOVER-pass record in docs/design/
maturity_map.yaml (W3_2_settlement_timetable).

Architecture (FRAME decision, W3_2_settlement_timetable): built on
W1_reveal_over_time's existing bitemporal spine
(company/interfaces/bitemporal_event_log.py::BitemporalEventLog), not a new
mechanism -- "one architecture, not two", the same principle already
applied to D2_three_clocks/G2. valid_time = the settlement day the figure
is ABOUT; transaction_time = each real run's own publication date (R1 ~1mo
post-delivery, R2 ~3mo, R3 ~5mo, RF ~28mo). BitemporalEventLog is reused
directly (not reimplemented) because it is explicitly the shared seam
class -- its own docstring: "Lives in company/interfaces/ (the one
location explicitly exempt from the epistemic-wall import check) -- this
IS the seam, not a violation of it." Importing it here does not leak any
company state into the SIM, nor any SIM state into company: it is a
stateless, generic, dependency-free data structure (no shared global
instance, no company business data); this module constructs and owns its
own private BitemporalEventLog instance. This is judged NOT to be a wall
violation, but it is flagged explicitly here per
.claude/rules/epistemic-wall-sim.md's own instruction to flag rather than
assume -- if a future reviewer disagrees, the fix is a small, mechanical
one (duplicate a minimal record/query shape sim-side instead).

WALL NOTE on the calibration constants below: they mirror
company/regulatory/settlement_reconciliation.py's own real, Elexon-
anchored constants (Elexon Settlement Performance Reports) EXACTLY --
duplicated here, not imported, because .claude/rules/epistemic-wall-sim.md
is unambiguous that sim-side code must never import company.*/saas.*
modules other than through company/interfaces/sim_interface.py, and
settlement_reconciliation.py is ordinary company-side business logic, not
the seam. settlement_reconciliation.py remains the single source of TRUTH
for these figures; tests/simulation/test_settlement_timetable.py imports
it directly (tests/ may import anything) to assert these two constant
sets never drift apart.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List, Literal

from dateutil.relativedelta import relativedelta

from company.interfaces.bitemporal_event_log import BitemporalEventLog, BitemporalRecord

# ---------------------------------------------------------------------------
# Calibration constants -- see WALL NOTE above. Keep numerically identical
# to company/regulatory/settlement_reconciliation.py's own
# _R1_MONTHS/_R2_MONTHS/_R3_MONTHS/_RF_MONTHS and
# _R1_SHARE/_R2_SHARE/_R3_SHARE/_RF_SHARE/_HH_RECON_VARIANCE/
# _NON_HH_RECON_VARIANCE constants at any future touch.
# ---------------------------------------------------------------------------
R1_MONTHS = 1
R2_MONTHS = 3
R3_MONTHS = 5     # ~17 weeks
RF_MONTHS = 28    # Final Reconciliation

R1_SHARE = 0.60
R2_SHARE = 0.25
R3_SHARE = 0.12
RF_SHARE = 0.03
assert abs((R1_SHARE + R2_SHARE + R3_SHARE + RF_SHARE) - 1.0) < 1e-9, (
    "settlement run shares must sum to exactly 1.0 -- RF must fully resolve the gap"
)

HH_VARIANCE = 0.005       # +-0.5% for HH-metered I&C customers
NON_HH_VARIANCE = 0.040   # +-4.0% for profile-class non-HH meters

RunName = Literal["initial", "R1", "R2", "R3", "RF"]
MeterType = Literal["HH", "non_HH"]

# (run name, months post-delivery, share of the total gap resolved AT this run)
_RUNS: list[tuple[RunName, int, float]] = [
    ("R1", R1_MONTHS, R1_SHARE),
    ("R2", R2_MONTHS, R2_SHARE),
    ("R3", R3_MONTHS, R3_SHARE),
    ("RF", RF_MONTHS, RF_SHARE),
]


def variance_band(meter_type: MeterType) -> float:
    """Fractional variance band (of the reference/initial value) that real
    reconciliation adjustments fall within -- +-0.5% HH, +-4% non-HH."""
    if meter_type == "HH":
        return HH_VARIANCE
    if meter_type == "non_HH":
        return NON_HH_VARIANCE
    raise ValueError(f"unknown meter_type {meter_type!r} -- expected 'HH' or 'non_HH'")


@dataclass(frozen=True)
class SettlementRunEvent:
    """One emitted revision of a settlement figure."""
    run: RunName
    publication_date: dt.date
    value: float
    cumulative_share_resolved: float
    record: BitemporalRecord


def emit_settlement_timetable(
    log: BitemporalEventLog,
    entity_id: str,
    fact_type: str,
    delivery_date: dt.date,
    initial_value: float,
    true_final_value: float,
    meter_type: MeterType = "HH",
    allow_out_of_band: bool = False,
) -> List[SettlementRunEvent]:
    """Emit the real R1/R2/R3/RF revision sequence for one settlement
    figure into `log`, as a sequence of BitemporalEventLog records sharing
    one valid_time (`delivery_date`, the settlement day the figure is
    ABOUT) and one transaction_time per real run (that run's own
    publication date, `delivery_date` + R1/R2/R3/RF months).

    `initial_value` is the delivery-time (unrevised) estimate; the actual
    real settlement mechanism recognises this as knowable immediately, so
    it is also recorded at `delivery_date` itself (run="initial") -- this
    is what lets a query as-of any date before R1 return something rather
    than None.

    `true_final_value` is the value the RF run resolves to EXACTLY (R1+R2+
    R3+RF shares sum to 1.0 by construction, asserted at import time).

    The requested gap (true_final_value - initial_value) is checked
    against the real +-0.5% (HH) / +-4% (non-HH) variance band (as a
    fraction of `initial_value`) -- raises ValueError if it is implausibly
    large for the given meter_type, unless `allow_out_of_band=True` is
    passed for a deliberate stress-test case. This is a plausibility check
    on the INPUT, not output tuning (R12): it never adjusts the values
    themselves, only validates the caller's own scenario is realistic.

    Returns the ordered list of emitted SettlementRunEvent (initial, R1,
    R2, R3, RF) for convenience/assertions -- `log` is the durable record;
    the return value is not itself persisted state.
    """
    gap = true_final_value - initial_value
    reference = abs(initial_value) if initial_value else abs(true_final_value)
    if reference:
        max_band = reference * variance_band(meter_type)
        if not allow_out_of_band and abs(gap) > max_band + 1e-9:
            raise ValueError(
                f"requested revision gap {gap:.6f} exceeds the {meter_type} "
                f"variance band (+-{variance_band(meter_type) * 100:.2f}% of "
                f"{reference:.6f} = +-{max_band:.6f}); this settlement "
                f"scenario is not realistic for a real meter of this type. "
                f"Pass allow_out_of_band=True for a deliberate stress case."
            )

    events: List[SettlementRunEvent] = []

    initial_record = log.record(
        entity_id=entity_id,
        fact_type=fact_type,
        valid_time=delivery_date,
        transaction_time=dt.datetime.combine(delivery_date, dt.time(0, 0)),
        value=initial_value,
        superseded_by_run=None,
    )
    events.append(SettlementRunEvent("initial", delivery_date, initial_value, 0.0, initial_record))

    cumulative_share = 0.0
    for run_name, months, share in _RUNS:
        cumulative_share += share
        publication_date = delivery_date + relativedelta(months=months)
        value = initial_value + cumulative_share * gap
        record = log.record(
            entity_id=entity_id,
            fact_type=fact_type,
            valid_time=delivery_date,
            transaction_time=dt.datetime.combine(publication_date, dt.time(0, 0)),
            value=value,
            superseded_by_run=run_name,
        )
        events.append(SettlementRunEvent(run_name, publication_date, value, cumulative_share, record))

    return events
