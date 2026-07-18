"""W2_11_payment_behaviour_source -- payment-behaviour generator (sim-source,
world-side, coupled-triad W of the D5 decomposition: W2_11 source / W4_4 seam /
D5 consumption / H27 gap).

WHAT THIS IS
------------
The baseline generator of the WORLD's payment TRUTH: who truly pays when, why
a Direct Debit collection truly fails, how the arrears truly ages, and which
payment method a customer truly uses. The company never reads this module --
it observes payments only through the not-yet-built W4_4 seam (bank
statements / remittance advices / Bacs DD outcome reports), and H27
(payment-belief-vs-truth gap) scores the company's D5 inference against this
module's truth. This atom cannot reach L3 alone (COUPLED_TRIAD binding rule:
no world source reaches L3 until the gap is measured against the consuming
company capability) -- assessed honestly at generator-alone level (L1-L2),
never claimed L3 here.

REUSE, NOT REINVENTION (R13 discipline, same law bacs_rails.py states for
itself: "duplicating it here would violate R13")
------------------------------------------------------------------------
The core payment-outcome probability model (on-time / late / DD-failed by
stress tier, I&C BACS/CHAPS behaviour) is NOT reinvented here -- it already
exists, calibrated, at `simulation.arrears_engine.payment_outcome()` /
`.payment_method()` / `.arrears_stages()`, and duplicating a second calibrated
model would create exactly the two-independently-calibrated-models problem
`arrears_engine.py`'s own docstring was written to close. This module WRAPS
that existing core in three things it does not yet have, all requested by the
W2_11 FRAME:

  1. C-S2 RNG SUBSTREAM ISOLATION -- `arrears_engine`'s own batch functions
     advance ONE shared `random.Random(seed)` across bills in population
     iteration order (fine for its original purpose: a population-level
     ledger/P&L reconciliation run once). This module instead gives EVERY
     customer, and every period within a customer's history, its OWN named
     seeded substream, so a per-customer/per-period draw here can never shift
     any other subsystem's sequence, any other customer's sequence, or any
     other period's sequence -- the hard C-S2 requirement for a generator
     that other code (the future W4_4 seam, H27's gap harness) will call
     per-customer, out of population order, on demand.
  2. DD-FAILURE REASON (insufficient-funds vs cancelled/other) -- arrears_engine
     returns success/failed/dispute with no "why". This module adds the reason
     split, anchored to the SAME real Bacs ARUDD dominant-code fact
     `simulation.bacs_rails.py` already cites (see ANCHORS below).
  3. PAYMENT-METHOD MIX beyond binary DD/non-DD (standing_order / card /
     prepayment) and ARREARS-AGEING / CHRONIC-vs-TRANSIENT PATTERN
     classification -- neither exists elsewhere in named, queryable form.

COUPLING TO THE HOUSEHOLD HARDSHIP SUBSTRATE (FRAME instruction: "NOT A
SEPARATE MECHANISM ... branches on the SAME hardship substrate")
------------------------------------------------------------------------
Payment behaviour is driven by the caller-supplied `stress` (a
`simulation.household.IncomeStress` value, or an equivalent stress
trajectory) -- the SAME hardship substrate `simulation.household_budget` /
`simulation.arrears_engine` already model. This module does not invent a new
hardship variable; it takes stress as an input (exactly like
`arrears_engine.payment_outcome()` already does) and adds the three
dimensions above on top.

ANCHORS (R13 baseline, decided BLIND to company P&L -- CITED, not invented)
----------------------------------------------------------------------------
- Payment-method mix, DD share: DESNZ "Quarterly Energy Prices: June 2026"
  commentary, "Payment methods" section (fetched 2026-07-08, recorded
  `docs/market_research/ASSUMPTIONS.md` line ~114 and reused directly from
  `simulation.household_segments.DIRECT_DEBIT_SHARE_BY_FUEL`): Direct Debit
  72% of standard electricity customers / 75% of gas customers (end of March
  2026). REUSED here, not re-derived (single source of truth).
- Non-DD sub-split (standard_credit vs prepayment): Ofgem 2026, ~74% DD / 13%
  standard credit / 13% prepayment (recorded in
  `simulation.dd_attribution`'s own ANCHORS section, 2026-07-13 DISCOVER
  pass). The two non-DD shares are near-equal (13% / 13%), so this module
  splits the non-DD residual left after the fuel-specific DD anchor above
  50/50 between standard_credit and prepayment -- an anchored RATIO applied
  to a different (but consistent) DD baseline, not a fabricated split.
- ANCHORED [L], calibration GAP (R10, honestly labelled, not fabricated):
  no published sub-split of "standard credit" payment INSTRUMENT (standing
  order vs debit/credit card) was found in this codebase's research to date
  -- `_STANDARD_CREDIT_SUBMETHOD_SHARE` below is a labelled 50/50 ESTIMATE,
  not a sourced figure. Left as a documented gap for a future research pass.
- DD-failure REASON split (insufficient-funds vs cancelled/other): DIRECTION
  anchored to `simulation.bacs_rails.py`'s own citation (Pay.UK "Bacs System
  Principles" + AccessPaySuite/Hafiz Didarali reason-code references) that
  ARUDD code 0 ("Refer to Payer", i.e. insufficient funds) is the real-world
  DOMINANT DD-failure cause. The exact proportion is NOT published in either
  module's research to date; `_DD_FAILURE_REASON_SPLIT` below is a labelled
  ESTIMATE (0.85 insufficient-funds / 0.15 cancelled-or-other) that respects
  the sourced DIRECTION (insufficient-funds dominant) without claiming
  fabricated precision on the exact split -- same honesty convention
  `bacs_rails.py::resolve_submission` already applies to the full reason-code
  set (a fixed dominant code, never a uniform random pick across all codes).
- On-time/late/DD-failure probabilities by income-stress tier, and I&C
  BACS/CHAPS on-time/late/dispute probabilities: REUSED byte-for-byte from
  `simulation.arrears_engine` (this module's whole point is to not duplicate
  that calibration) -- their own external-sourcing status is inherited from
  that module, not re-asserted here.

CURRICULUM vs BASELINE (R13, Law A) -- NOT THIS MODULE'S DECISION
----------------------------------------------------------------------
Every constant in this module is the BASELINE (decided blind to company P&L,
for real-world fidelity only). Any DIFFICULTY DIAL (a "DD-failure spike"
epoch, a payment-stress scenario) is director-authored CURRICULUM and belongs
elsewhere (a named, versioned scenario artefact) -- this module exposes no
scenario switch and must never be tuned in response to company outcomes.

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
------------------------------------------------------
Pure WORLD/sim code. Must not import `company.*` or `saas.*`. Every record
carries `data_regime="synthetic"`.

RNG SUBSTREAM DISCIPLINE (C-S2, CLAUDE.md -- non-negotiable, the 01:09Z
incident)
------------------------------------------------------------------------
Every stochastic draw in this module comes from THIS subsystem's OWN named,
sha256-seeded substream (`_substream(base_seed, name)`), never the global
`random` module, and never a substream shared with any other subsystem. A
per-period draw is additionally isolated by period index inside its own
substream name (`f"payment_event::{period_index}"`), so drawing period 5 of
customer A can never shift period 3 of customer A, any period of customer B,
or any other subsystem's sequence (proven by
`tests/sim/test_w2_11_payment_behaviour_source.py`).
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Sequence

from simulation.arrears_engine import payment_outcome as _core_payment_outcome

STREAM_NAMESPACE = "W2_11_payment_behaviour_source"

# Named RNG substreams -- FIXED (per-customer, drawn once) names (C-S2).
# Per-period draws use a DYNAMIC name built from one of these bases + the
# period index (see `_period_substream`) -- still a single deterministic
# sha256 key per (base_seed, name), so C-S2 isolation holds identically.
_SUBSTREAMS = (
    "payment_method",              # persistent per-customer method archetype
    "payment_method_submethod",    # standing_order vs card sub-draw (non-DD, non-prepay)
)
_PERIOD_SUBSTREAM_BASE = "payment_event"       # + "::<period_index>"
_REASON_SUBSTREAM_BASE = "dd_failure_reason"   # + "::<period_index>"


def _substream(base_seed: int, name: str) -> random.Random:
    """Return an ISOLATED ``random.Random`` for a named mechanism substream.

    Seed is a STABLE sha256 of ``W2_11_payment_behaviour_source::<name>::<base_seed>``
    (never Python's per-process-salted ``hash()``), so the same (base_seed, name)
    yields the same stream across processes -- the hard C-S2 requirement. Each
    name seeds an independent generator; a draw here can never consume from, or
    shift, any other substream of this or any other subsystem.
    """
    key = f"{STREAM_NAMESPACE}::{name}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _period_substream(base_seed: int, base_name: str, period_index: int) -> random.Random:
    """Per-period substream: same isolation guarantee as `_substream`, keyed
    additionally by `period_index` so no two periods (of the same or a
    different customer) ever share a stream."""
    return _substream(base_seed, f"{base_name}::{period_index}")


def _base_seed_for(customer_id: str, seed: Optional[int]) -> int:
    """Resolve the base seed. Stable md5 of customer_id when no explicit seed
    is given (the built-in ``hash()`` is per-process-salted and would break
    replay across processes)."""
    if seed is not None:
        return seed
    return int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)


# ---------------------------------------------------------------------------
# ANCHORS (see module docstring for full citations).
# ---------------------------------------------------------------------------
DIRECT_DEBIT = "direct_debit"
STANDING_ORDER = "standing_order"
CARD = "card"
PREPAYMENT = "prepayment"

# DESNZ June 2026 (via simulation.household_segments.DIRECT_DEBIT_SHARE_BY_FUEL):
# DD share of standard credit/DD customers by fuel.
_DD_SHARE_BY_FUEL = {"electricity": 0.72, "gas": 0.75}

# Ofgem 2026 (via simulation.dd_attribution's own ANCHORS): ~74% DD / 13%
# standard credit / 13% prepayment -> non-DD residual splits ~50/50.
_PREPAYMENT_SHARE_OF_NON_DD = 0.50

# ESTIMATE (R10 calibration gap, not sourced): standard-credit sub-instrument.
_STANDARD_CREDIT_SUBMETHOD_SHARE = {STANDING_ORDER: 0.50, CARD: 0.50}

# ESTIMATE (direction sourced from bacs_rails.py's ARUDD-dominant-code
# citation; exact split not published).
INSUFFICIENT_FUNDS = "insufficient_funds"
CANCELLED_OTHER = "cancelled_other"
_DD_FAILURE_REASON_SPLIT = {INSUFFICIENT_FUNDS: 0.85, CANCELLED_OTHER: 0.15}

AGEING_BUCKETS = ("current", "0-30", "31-60", "61-90", "90+")


def generate_payment_method(
    customer_id: str,
    fuel: str = "electricity",
    seed: Optional[int] = None,
) -> str:
    """Persistent per-customer payment-method archetype: one of DIRECT_DEBIT,
    STANDING_ORDER, CARD, PREPAYMENT. Deterministic in (customer_id, seed, fuel).

    Reuses the fuel-specific DD anchor (`_DD_SHARE_BY_FUEL`, same figure
    `simulation.household_segments` already cites) for the DD/non-DD split,
    then the Ofgem non-DD ratio to place the non-DD residual into
    prepayment vs standard-credit, then (ESTIMATE, see module docstring) an
    even sub-split of standard-credit into standing_order/card.
    """
    base_seed = _base_seed_for(f"{customer_id}::{fuel}", seed)
    dd_share = _DD_SHARE_BY_FUEL.get(fuel, _DD_SHARE_BY_FUEL["electricity"])

    r_method = _substream(base_seed, "payment_method")
    if r_method.random() < dd_share:
        return DIRECT_DEBIT

    if r_method.random() < _PREPAYMENT_SHARE_OF_NON_DD:
        return PREPAYMENT

    r_sub = _substream(base_seed, "payment_method_submethod")
    return (
        STANDING_ORDER
        if r_sub.random() < _STANDARD_CREDIT_SUBMETHOD_SHARE[STANDING_ORDER]
        else CARD
    )


@dataclass(frozen=True)
class PaymentEvent:
    """One period's payment TRUTH (world-side ground truth; observed by the
    company only through the future W4_4 seam, never this object directly)."""
    customer_id: str
    period_index: int
    due_date: str                 # YYYY-MM-DD
    amount_gbp: float
    payment_method: str
    result: str                   # "success" | "failed" | "dispute"
    days_late: int
    payment_date: Optional[str]   # None if unpaid as of generation (failed/dispute)
    dd_failure_reason: Optional[str]  # INSUFFICIENT_FUNDS | CANCELLED_OTHER | None
    data_regime: str = "synthetic"

    @property
    def is_late(self) -> bool:
        return self.result == "success" and self.days_late > 0

    @property
    def is_unresolved(self) -> bool:
        return self.result in ("failed", "dispute")


def generate_payment_event(
    customer_id: str,
    period_index: int,
    due_date: date,
    amount_gbp: float,
    stress: str,
    payment_method: str,
    segment: str = "resi",
    seed: Optional[int] = None,
) -> PaymentEvent:
    """Generate one period's payment truth.

    Draws from this module's OWN period-isolated substream
    (`_period_substream(base_seed, "payment_event", period_index)`), then
    hands that isolated RNG into the EXISTING calibrated core
    (`simulation.arrears_engine.payment_outcome`) -- reuse, not reinvention
    (see module docstring). A second, also period-isolated, substream draws
    the DD-failure reason only when the outcome is a DD failure.

    `payment_method` (this module's own DD/standing_order/card/prepayment
    label) does not change WHICH outcome-probability tier is used: the
    underlying calibrated model (`arrears_engine.payment_outcome`) only
    distinguishes "bacs/chaps" (I&C/SME) from everything else -- there is no
    separately-anchored outcome model for standing_order/card/prepayment
    specifically, and inventing one would be exactly the un-anchored
    duplication R13 warns against (see module docstring). So every
    non-corporate method maps to the same core "direct_debit"-style outcome
    tier; only the METHOD LABEL varies.
    """
    base_seed = _base_seed_for(customer_id, seed)
    rng = _period_substream(base_seed, _PERIOD_SUBSTREAM_BASE, period_index)

    core_method = "bacs" if segment in ("ic", "I&C", "sme") else "direct_debit"
    # arrears_engine's stress-keyed dicts are upper-cased ("LOW"/"MODERATE"/
    # "HIGH"); household_demand.income_stress_trajectory() emits lower-case
    # IncomeStress.value strings ("low"/"moderate"/"high") -- normalise here
    # so a moderate/high stress period is never silently mis-read as the
    # (coincidentally identical-looking) default low-stress probability.
    core_stress = (stress or "LOW").upper()

    result, days_late = _core_payment_outcome(core_method, core_stress, rng, segment=segment)

    dd_failure_reason = None
    payment_date: Optional[str] = None
    if result == "failed":
        r_reason = _period_substream(base_seed, _REASON_SUBSTREAM_BASE, period_index)
        dd_failure_reason = (
            INSUFFICIENT_FUNDS
            if r_reason.random() < _DD_FAILURE_REASON_SPLIT[INSUFFICIENT_FUNDS]
            else CANCELLED_OTHER
        )
    elif result == "dispute":
        payment_date = None
    else:  # success (on-time or late)
        payment_date = (due_date + timedelta(days=days_late)).isoformat()

    return PaymentEvent(
        customer_id=customer_id,
        period_index=period_index,
        due_date=due_date.isoformat(),
        amount_gbp=amount_gbp,
        payment_method=payment_method,
        result=result,
        days_late=days_late,
        payment_date=payment_date,
        dd_failure_reason=dd_failure_reason,
    )


def arrears_age_days(due_date: str, as_of_date: str, payment_date: Optional[str]) -> int:
    """Pure ageing calc: days the amount has been outstanding past its due
    date, as of `as_of_date`. 0 if paid on/before `as_of_date` (or not yet
    due). Never negative."""
    due = date.fromisoformat(due_date)
    as_of = date.fromisoformat(as_of_date)
    if payment_date is not None:
        paid = date.fromisoformat(payment_date)
        if paid <= as_of:
            return 0
    age = (as_of - due).days
    return max(0, age)


def ageing_bucket(age_days: int) -> str:
    """Standard 30/60/90-day ageing bucket (matches the buckets
    H27_payment_belief_gap's FRAME names: 30/60/90+)."""
    if age_days <= 0:
        return "current"
    if age_days <= 30:
        return "0-30"
    if age_days <= 60:
        return "31-60"
    if age_days <= 90:
        return "61-90"
    return "90+"


def classify_payment_pattern(events: Sequence[PaymentEvent]) -> str:
    """Classify a customer's realised payment-event HISTORY into a pattern:
    CHRONIC (persistently late/failed), TRANSIENT (an isolated lapse), or
    CONSISTENT_ON_TIME. Purely DERIVED from already-drawn outcomes (no new
    RNG draw -- the classification is a deterministic function of the
    realised sequence, so it needs no substream of its own)."""
    if not events:
        return "CONSISTENT_ON_TIME"
    problem_count = sum(1 for e in events if e.is_late or e.is_unresolved)
    rate = problem_count / len(events)
    if rate == 0.0:
        return "CONSISTENT_ON_TIME"
    if rate >= 0.5:
        return "CHRONIC"
    return "TRANSIENT"


@dataclass(frozen=True)
class CustomerPaymentProfile:
    """A customer's full payment-behaviour truth over a billing history --
    the object H27_payment_belief_gap scores the company's D5 belief
    against. Never read by company/saas code directly (epistemic wall);
    the future W4_4 seam is the only sanctioned crossing point."""
    customer_id: str
    payment_method: str
    events: tuple  # tuple[PaymentEvent, ...]
    pattern: str
    data_regime: str = "synthetic"

    def ageing_as_of(self, as_of_date: str) -> dict:
        """{period_index: (age_days, bucket)} as of a given date -- the TRUTH
        H27 compares the company's inferred ageing against."""
        out = {}
        for e in self.events:
            age = arrears_age_days(e.due_date, as_of_date, e.payment_date)
            out[e.period_index] = (age, ageing_bucket(age))
        return out


def generate_customer_payment_history(
    customer_id: str,
    due_dates_amounts: Sequence[tuple],
    stress_trajectory: Optional[Sequence[dict]] = None,
    segment: str = "resi",
    fuel: str = "electricity",
    seed: Optional[int] = None,
) -> CustomerPaymentProfile:
    """Generate a customer's full payment-behaviour truth.

    `due_dates_amounts`: sequence of (date, amount_gbp) for each billing
    period, in period order.
    `stress_trajectory`: optional list of {"year": int, "stress": str}
    (same shape `simulation.household_demand.income_stress_trajectory`
    already produces) -- the SAME hardship substrate this module couples to
    (FRAME instruction), never a new one. Defaults every period to "low" if
    omitted or no matching year is found (I&C/SME segments have no household
    stress and should simply omit this argument).
    """
    method = generate_payment_method(customer_id, fuel=fuel, seed=seed)

    def _stress_for_year(year: int) -> str:
        if not stress_trajectory:
            return "low"
        for entry in stress_trajectory:
            if entry.get("year") == year:
                return (entry.get("stress") or "low")
        return "low"

    events = []
    for idx, (due_date, amount_gbp) in enumerate(due_dates_amounts):
        stress = _stress_for_year(due_date.year)
        ev = generate_payment_event(
            customer_id, idx, due_date, amount_gbp, stress, method,
            segment=segment, seed=seed,
        )
        events.append(ev)

    pattern = classify_payment_pattern(events)
    return CustomerPaymentProfile(
        customer_id=customer_id,
        payment_method=method,
        events=tuple(events),
        pattern=pattern,
    )
