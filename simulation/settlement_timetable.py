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
import math
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
# CORRECTED 2026-08-29 from an Elexon primary document. The full reasoning lives once, beside
# the company-side pair these must equal -- `company/regulatory/settlement_reconciliation.py` --
# rather than being copied here to go stale at a different rate, which is the failure that put
# a dispute-run lag (28 months, DF) on every ordinary settlement day under the name of the last
# scheduled run (14 months, RF). Evidence:
# `docs/market_research/elexon_settlement_run_timetable_verified.md`.
R1_MONTHS = 2
R2_MONTHS = 4
R3_MONTHS = 7
RF_MONTHS = 14    # Final Reconciliation -- the LAST SCHEDULED run. DF (disputes only) is 28.

R1_SHARE = 0.3093
R2_SHARE = 0.3093
R3_SHARE = 0.2062
RF_SHARE = 0.1752
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


def variance_band_limit(
    initial_value: float, true_final_value: float, meter_type: MeterType
) -> float | None:
    """The maximum absolute revision gap the meter type's variance band
    permits for this figure, as an absolute number (band fraction * the
    reference value). The reference is |initial| (falling back to |true_final|
    when initial is 0), mirroring emit_settlement_timetable's own guard exactly.
    Returns None when there is no positive reference to measure against (both
    values 0) -- there is then no meaningful band and nothing is out of band."""
    reference = abs(initial_value) if initial_value else abs(true_final_value)
    if not reference:
        return None
    return reference * variance_band(meter_type)


def is_gap_out_of_band(
    initial_value: float, true_final_value: float, meter_type: MeterType
) -> bool:
    """True iff the revision gap (true_final - initial) exceeds the meter
    type's variance band. This is the SINGLE source of the band decision,
    shared by emit_settlement_timetable's input guard and the real-data
    orchestration in settlement_run_series.py, so the two can never drift.

    Non-finite inputs are NOT classified here (they return False): they are a
    broken-input class, not a legitimately-large gap, and are rejected up front
    by emit_settlement_timetable's own finite-check -- letting them fall through
    to that rejection keeps the reject-broken-data path single-sourced too."""
    if not (math.isfinite(initial_value) and math.isfinite(true_final_value)):
        return False
    limit = variance_band_limit(initial_value, true_final_value, meter_type)
    if limit is None:
        return False
    return abs(true_final_value - initial_value) > limit + 1e-9


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
    # Reject non-finite inputs FIRST (R15 fail-open / NaN-blind pattern): the
    # variance-band magnitude guard below is `abs(gap) > band`, and abs(nan) >
    # band is False, so a NaN initial_value/true_final_value would sail
    # straight through the plausibility check and emit all-NaN revised figures
    # silently -- worse than a rejected input, because the "initial" record
    # stays a valid number while every revision (and any bitemporal query
    # after R1) returns NaN. abs(+-inf) > (inf*share) is likewise False, so
    # inf fails open the same way. Reject both here, up front.
    for _name, _v in (("initial_value", initial_value), ("true_final_value", true_final_value)):
        if not math.isfinite(_v):
            raise ValueError(
                f"{_name}={_v!r} is not finite; a settlement figure must be a "
                f"real number. A non-finite value would defeat the variance-band "
                f"plausibility check (abs(nan)>band and abs(inf)>inf are both "
                f"False) and emit NaN/inf settlement revisions silently."
            )

    gap = true_final_value - initial_value
    if not allow_out_of_band and is_gap_out_of_band(
        initial_value, true_final_value, meter_type
    ):
        reference = abs(initial_value) if initial_value else abs(true_final_value)
        max_band = variance_band_limit(initial_value, true_final_value, meter_type)
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
