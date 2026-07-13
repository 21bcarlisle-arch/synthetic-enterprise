"""World-side hidden SME / I&C business-distress twin (W2_6_sme_distress_twin).

WHAT THIS IS
------------
A per-business, per-run STOCHASTIC generator of HIDDEN business-distress ground
truth for the commercial book (segments ``SME`` and ``I&C``). It is the business
counterpart of the residential life-event / household-budget stream: where a
household has demographic income stress (job loss, illness), a business has
sector shocks, cash-flow distress, and insolvency. Three real mechanisms:

  1. SECTOR SHOCKS  -- insolvency hazard is sector-weighted, not uniform
     (construction / wholesale-retail / accommodation-food carry the load).
  2. INSOLVENCY EVENTS -- a failed business is a BAD DEBT **and a LOST SUPPLY
     POINT**: the supplier (a low-priority creditor) writes off most of the
     balance AND loses the meter relationship -- on a tenanted premises the
     account liability transfers to the LANDLORD, accruing standing charges
     during vacancy. Not merely a write-off.
  3. LATE-PAYMENT CULTURE -- a persistent per-business TRAIT: a business that
     pays late BY HABIT while perfectly healthy and solvent. This is the
     CONFOUND at the heart of the atom: a habitual-late-payer and a genuinely
     DISTRESSED business emit the SAME observable (a late payment); the hidden
     CAUSE differs. Disentangling the two is exactly the job of the coupled
     company-side twin C8_sme_credit_risk -- which this module scores against
     via the answer-key methods below (``late_payment_cause``).

THE HIDDEN/OBSERVABLE SEAM (Architectural Law -- the company cannot see inside)
------------------------------------------------------------------------------
Everything here is HIDDEN SIM ground truth. The company layer MUST NOT read a
business's ``distress_state`` or ``late_payment_culture`` flag. It observes only
CONSEQUENCES -- a late or missed payment, a payment-pattern deterioration, the
sector code it already holds, eventually a lost supply point -- and must INFER
credit risk from those. ``is_paying_late(as_of)`` is the OBSERVABLE (identical
for culture and distress); ``late_payment_cause(as_of)`` and
``distress_state_at(as_of)`` are the ANSWER KEY, for the harness only.

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
-----------------------------------------------------
WORLD/sim code. It MUST NOT import ``company.*`` or ``saas.*``. It takes only a
customer_id + segment (+ optional sector); it never reaches across the seam.

RNG SUBSTREAM DISCIPLINE (C-S2, CLAUDE.md -- non-negotiable; the 01:09Z incident)
--------------------------------------------------------------------------------
Every draw comes from THIS subsystem's OWN named, seeded substream
(``_substream(base_seed, name)`` -> an isolated ``random.Random`` seeded from a
STABLE sha256 of ``W2_6_sme_distress::<name>::<base_seed>``). It NEVER touches
the global ``random`` module and can NEVER shift another subsystem's sequence --
population_draw, life_events and the (future) household_budget stream stay
byte-identical no matter how much this one is advanced. Each mechanism draws
from its OWN named substream, so adding a future mechanism APPENDS a name and
can never shift an existing one. Proven by ``test_sme_distress_substream_*``.

DETERMINISTIC REPLAY (C-S2): same ``base_seed`` -> byte-identical distress
profile and event stream, every run, across processes (sha256, not salted
``hash()``). Proven by ``test_deterministic_replay_*``.

EVENT-ARRIVAL TOLERANCE (C-S1): distress is an ordered, immutable EVENT stream
(``DistressEvent``); state at any date is reconstructed by replay, never assumed
batch-complete.

BASELINE vs CURRICULUM (R13): the real UK insolvency RATE and procedure mix are
BASELINE (calibrated to reality, changed only for fidelity). The distress-onset
/ recovery / late-payment-culture incidence and the sector shock MULTIPLIERS are
DIAGNOSTIC curriculum instruments (R12 / Law A) -- never tuned toward a company
P&L outcome, changed only by a director-authored curriculum edit.

ANCHORS & HONEST SIMPLIFICATIONS (R10, dated 2026-07-13; full provenance in
docs/market_research/sme_distress_twin_w2_6.md)
-------------------------------------------------------------------------------
- ANCHORED [L]: UK company insolvency rate ~50-57 per 10,000 active companies/yr
  (Insolvency Service, 12 months to 2024) -> ``_BASE_ANNUAL_INSOLVENCY_HAZARD``
  encoded as a representative 0.0055 point in that real range, NOT fabricated as
  a spurious-precision figure.
- ANCHORED [L]: insolvency procedure mix ~76% CVL (voluntary wind-down, a longer
  visible distress run-up) vs ~24% compulsory/court-forced -> ``_CVL_SHARE``.
- ANCHORED [L]: suppliers estimate up to a THIRD (~33%) of accumulated SME
  energy debt is never paid / written off. NOTE this is an AGGREGATE across
  insolvent AND eventually-paying accounts; a SINGLE insolvency's write-off is
  much HIGHER (the supplier is a low-priority creditor) -> per-insolvency
  ``writeoff_fraction`` ~ U(0.6, 1.0). The 33% aggregate is recorded, not used
  as the per-event fraction (would understate individual insolvency loss).
- ANCHORED [L]: sector concentration of insolvencies -- construction 17% >
  wholesale/retail 15% > accommodation/food 14% of all UK company insolvencies.
  SIMPLIFICATION (R10): concentration != hazard rate without each sector's
  active-population denominator (not publicly available at that granularity), so
  ``_SECTOR_SHOCK_MULT`` encodes the concentration ORDERING as RELATIVE
  curriculum multipliers, NOT measured per-sector rates. Overridable.
- SIMPLIFICATION (R10, un-anchored CURRICULUM, R13): distress onset/recovery
  hazards and late-payment-culture incidence have no clean UK per-account anchor
  (the widely-cited GBP11bn/yr and ~14,000 closures/yr late-payment figures are
  economy-wide, NOT energy-account-specific -- deliberately not conflated). They
  are director-curriculum diagnostics, overridable, never claimed as measured.
- SIMPLIFICATION (R10): the "vacant, landlord-liable" lost-supply-point outcome
  is modelled as an OUTCOME FLAG on the insolvency event (``landlord_liable``),
  gated by a ``_TENANTED_SHARE`` curriculum placeholder, not (yet) a full extra
  hidden state -- the cheaper reuse the FRAME pass recommended; extend to a
  distinct state only if evidence demands it.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, List, Mapping, Optional, Tuple

# ---------------------------------------------------------------------------
STREAM_NAMESPACE = "W2_6_sme_distress"

#: Segments this twin applies to. Residential accounts go through the
#: residential life-event stream instead (segment-gated there, W2_5 scope).
BUSINESS_SEGMENTS: Tuple[str, ...] = ("SME", "I&C")


# ---------------------------------------------------------------------------
# ANCHORED / CURRICULUM constants -- see ANCHORS & HONEST SIMPLIFICATIONS above.
# ---------------------------------------------------------------------------

# ANCHORED [L] BASELINE: UK company insolvency rate ~50-57 per 10,000 active
# companies/yr (Insolvency Service, 12 months to 2024). Representative point.
_BASE_ANNUAL_INSOLVENCY_HAZARD = 0.0055

# ANCHORED [L]: 76% of company insolvencies are CVLs (voluntary wind-down, a
# longer visible distress run-up) vs ~24% compulsory/court-forced (sudden).
_CVL_SHARE = 0.76

# ANCHORED [L] aggregate: ~33% of accumulated SME energy debt is written off.
# Recorded for reference on each insolvency event; NOT the per-event fraction.
_AGGREGATE_SME_WRITEOFF_RATE = 0.33
# Per-insolvency write-off fraction range (supplier = low-priority creditor).
_INSOLVENCY_WRITEOFF_RANGE: Tuple[float, float] = (0.60, 1.00)

# CURRICULUM (R13) DIAGNOSTIC relative sector shock multipliers, derived from the
# insolvency-concentration ORDERING (NOT measured per-sector rates -- R10).
# "other" ~ the average-risk reference; multipliers are overridable.
_SECTOR_SHOCK_MULT: dict[str, float] = {
    "construction": 1.60,          # 17% of insolvencies -- highest
    "wholesale_retail": 1.40,      # 15%
    "accommodation_food": 1.35,    # 14%
    "professional_services": 0.70,  # comparatively resilient
    "other": 0.85,
}

# CURRICULUM placeholder sector distribution for drawing a sector when the caller
# does not supply one. Documented placeholder (R10), overridable.
_DEFAULT_SECTOR_WEIGHTS: dict[str, float] = {
    "construction": 0.16,
    "wholesale_retail": 0.20,
    "accommodation_food": 0.10,
    "professional_services": 0.24,
    "other": 0.30,
}

# CURRICULUM (R13, un-anchored -- R10) distress dynamics. Genuine cash-flow
# distress; most distressed businesses RECOVER rather than fail.
_DISTRESS_ONSET_ANNUAL_HAZARD = 0.06
_DISTRESS_RECOVERY_ANNUAL_PROB = 0.55

# CURRICULUM (R13, un-anchored -- R10): incidence of the habitual-late-payer
# TRAIT (the confound). A healthy business that pays late by habit.
_LATE_PAYMENT_CULTURE_INCIDENCE = 0.20

# CURRICULUM (R10 placeholder): share of business premises that are TENANTED, so
# an insolvency transfers the meter/liability to a landlord (lost supply point +
# vacant standing charge) rather than the account simply going dark.
_TENANTED_SHARE = 0.55


# ---------------------------------------------------------------------------
# Named RNG substreams -- one per mechanism (C-S2). Adding a future mechanism
# APPENDS a name; it can never shift an existing substream's sequence.
# ---------------------------------------------------------------------------
_SUBSTREAMS: Tuple[str, ...] = (
    "sector_assignment",
    "late_payment_culture",
    "distress_onset",
    "distress_recovery",
    "insolvency_hazard",
    "insolvency_route",
    "insolvency_tenure",
    "writeoff_fraction",
    "event_day",
)


def _substream(base_seed: int, name: str) -> random.Random:
    """Return an ISOLATED ``random.Random`` for a named mechanism substream.

    Seed is a STABLE sha256 of ``W2_6_sme_distress::<name>::<base_seed>`` (never
    Python's per-process-salted ``hash()``), so the same (base_seed, name)
    yields the same stream across processes -- a hard C-S2 requirement. Each
    name seeds an independent generator, so a draw here can never consume from,
    or shift, any other substream (of this or any other subsystem).
    """
    key = f"{STREAM_NAMESPACE}::{name}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _base_seed_for(customer_id: str, seed: Optional[int]) -> int:
    """Resolve the base seed for a business's distress stream.

    Uses a STABLE md5 of the customer_id when no explicit seed is given (the
    built-in ``hash()`` is salted per process and would break replay).
    """
    if seed is not None:
        return seed
    return int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)


def is_business_segment(segment: str) -> bool:
    return segment in BUSINESS_SEGMENTS


# ---------------------------------------------------------------------------
# Domain enums
# ---------------------------------------------------------------------------
class DistressState(str, Enum):
    """Hidden business-distress state (SIM ground truth)."""
    TRADING = "trading"          # healthy / solvent
    DISTRESSED = "distressed"    # genuine cash-flow distress (may recover)
    INSOLVENT = "insolvent"      # ceased trading -- bad debt + lost supply point


class InsolvencyProcedure(str, Enum):
    CVL = "creditors_voluntary_liquidation"  # ~76%; longer visible run-up
    COMPULSORY = "compulsory_liquidation"    # ~24%; court-forced, sudden


class LatePaymentCause(str, Enum):
    """The HIDDEN cause of a late/missed payment -- the answer key the company
    twin (C8) must infer from the identical OBSERVABLE (a late payment)."""
    NONE = "none"                # paying on time
    CULTURE = "culture"          # habitual late payer, healthy & solvent
    DISTRESS = "distress"        # genuine cash-flow distress
    INSOLVENCY = "insolvency"    # ceased trading


DistressEventType = str  # "distress_onset" | "distress_recovery" | "insolvency"


@dataclass(frozen=True)
class DistressEvent:
    """An immutable hidden distress event (SIM ground truth)."""
    customer_id: str
    event_date: str          # YYYY-MM-DD
    event_type: DistressEventType
    payload: dict = field(default_factory=dict)


@dataclass(frozen=True)
class BusinessDistressProfile:
    """A business's full hidden distress truth over the simulation window.

    ``late_payment_culture`` and the ``events`` stream are HIDDEN. The
    ``*_at`` / ``*_cause`` / ``is_paying_late`` methods split cleanly into the
    single OBSERVABLE (is_paying_late) and the ANSWER KEY (everything else),
    so the harness can score the company twin without the company ever reading
    this object.
    """
    customer_id: str
    segment: str
    sector: str
    late_payment_culture: bool
    events: Tuple[DistressEvent, ...]
    data_regime: str = "synthetic"

    # -- ANSWER KEY (harness only) -------------------------------------------
    def distress_state_at(self, as_of_date: str) -> DistressState:
        """Reconstruct hidden distress state as of a date by event replay."""
        state = DistressState.TRADING
        for e in self.events:
            if e.event_date > as_of_date:
                break
            if e.event_type == "distress_onset":
                state = DistressState.DISTRESSED
            elif e.event_type == "distress_recovery":
                state = DistressState.TRADING
            elif e.event_type == "insolvency":
                state = DistressState.INSOLVENT
        return state

    def late_payment_cause(self, as_of_date: str) -> LatePaymentCause:
        """The HIDDEN cause of any late payment as of a date (answer key).

        Distress / insolvency dominate as the risk-relevant cause; a business
        that is BOTH habitually-late AND distressed is scored as DISTRESS (the
        confound the company must still resolve -- both are true, but the
        credit-risk truth is the distress). A healthy habitual-late payer is
        CULTURE. On time -> NONE.
        """
        state = self.distress_state_at(as_of_date)
        if state == DistressState.INSOLVENT:
            return LatePaymentCause.INSOLVENCY
        if state == DistressState.DISTRESSED:
            return LatePaymentCause.DISTRESS
        if self.late_payment_culture:
            return LatePaymentCause.CULTURE
        return LatePaymentCause.NONE

    # -- OBSERVABLE (what a real supplier could see) -------------------------
    def is_paying_late(self, as_of_date: str) -> bool:
        """The single OBSERVABLE: is this business late/missing on its bill?

        Identical for CULTURE and DISTRESS -- that is THE confound. The company
        may condition on this and on the sector it already holds, never on the
        hidden cause.
        """
        return self.late_payment_cause(as_of_date) != LatePaymentCause.NONE


def _random_date_in_year(year: int, rng: random.Random) -> str:
    days = (dt.date(year, 12, 31) - dt.date(year, 1, 1)).days
    return (dt.date(year, 1, 1) + dt.timedelta(days=rng.randint(0, days))).isoformat()


def _weighted_choice(rng: random.Random, weights: Mapping[str, float]) -> str:
    keys = list(weights.keys())
    running = 0.0
    cum: List[float] = []
    for k in keys:
        running += weights[k]
        cum.append(running)
    x = rng.random() * running
    for k, thresh in zip(keys, cum):
        if x <= thresh:
            return k
    return keys[-1]


def generate_business_distress(
    customer_id: str,
    segment: str,
    sim_start_year: int,
    sim_end_year: int,
    seed: Optional[int] = None,
    sector: Optional[str] = None,
    sector_weights: Optional[Mapping[str, float]] = None,
    sector_shock_mult: Optional[Mapping[str, float]] = None,
) -> BusinessDistressProfile:
    """Generate the full hidden distress profile for one SME / I&C business.

    Deterministic in ``(customer_id, seed)`` (C-S2). Every draw comes from this
    subsystem's own named substreams -- nothing else's RNG is touched.

    Raises ``ValueError`` for a non-business segment: residential accounts are
    driven by the residential life-event stream, never this twin (the atom's own
    active-defect finding -- a warehouse must not receive a "new baby" event, and
    equally a household must not receive an "insolvency" event).
    """
    if not is_business_segment(segment):
        raise ValueError(
            f"segment {segment!r} is not a business segment {BUSINESS_SEGMENTS}; "
            "residential distress is the life-event stream's job, not this twin"
        )
    sector_weights = sector_weights or _DEFAULT_SECTOR_WEIGHTS
    sector_shock_mult = sector_shock_mult or _SECTOR_SHOCK_MULT

    base_seed = _base_seed_for(customer_id, seed)
    sub = {name: _substream(base_seed, name) for name in _SUBSTREAMS}

    if sector is None:
        sector = _weighted_choice(sub["sector_assignment"], sector_weights)

    # Persistent habitual-late-payer trait (the confound) -- drawn ONCE.
    late_payment_culture = (
        sub["late_payment_culture"].random() < _LATE_PAYMENT_CULTURE_INCIDENCE
    )

    shock = sector_shock_mult.get(sector, sector_shock_mult.get("other", 1.0))
    annual_insolvency_hazard = min(1.0, _BASE_ANNUAL_INSOLVENCY_HAZARD * shock)

    events: List[DistressEvent] = []
    state = DistressState.TRADING

    for year in range(sim_start_year, sim_end_year + 1):
        if state == DistressState.INSOLVENT:
            break

        # -- Insolvency hazard (applies while trading or distressed) ---------
        if sub["insolvency_hazard"].random() < annual_insolvency_hazard:
            route = (
                InsolvencyProcedure.CVL
                if sub["insolvency_route"].random() < _CVL_SHARE
                else InsolvencyProcedure.COMPULSORY
            )
            tenanted = sub["insolvency_tenure"].random() < _TENANTED_SHARE
            writeoff = round(
                sub["writeoff_fraction"].uniform(*_INSOLVENCY_WRITEOFF_RANGE), 4
            )
            # A CVL (voluntary) has a visible distress run-up: if not already
            # distressed, record a distress_onset earlier in the year -- the
            # real detection opportunity the company's twin can exploit.
            if route == InsolvencyProcedure.CVL and state == DistressState.TRADING:
                events.append(DistressEvent(
                    customer_id=customer_id,
                    event_date=_random_date_in_year(year, sub["event_day"]),
                    event_type="distress_onset",
                    payload={"run_up": True},
                ))
            events.append(DistressEvent(
                customer_id=customer_id,
                event_date=_random_date_in_year(year, sub["event_day"]),
                event_type="insolvency",
                payload={
                    "procedure": route.value,
                    # Bad debt: supplier is a low-priority creditor.
                    "writeoff_fraction": writeoff,
                    "aggregate_writeoff_rate_ref": _AGGREGATE_SME_WRITEOFF_RATE,
                    # Lost supply point, not just a write-off:
                    "lost_supply_point": True,
                    "landlord_liable": tenanted,
                    "sector": sector,
                },
            ))
            state = DistressState.INSOLVENT
            continue

        # -- Distress onset / recovery (genuine cash-flow distress) ----------
        if state == DistressState.TRADING:
            if sub["distress_onset"].random() < _DISTRESS_ONSET_ANNUAL_HAZARD:
                events.append(DistressEvent(
                    customer_id=customer_id,
                    event_date=_random_date_in_year(year, sub["event_day"]),
                    event_type="distress_onset",
                    payload={"run_up": False},
                ))
                state = DistressState.DISTRESSED
        elif state == DistressState.DISTRESSED:
            if sub["distress_recovery"].random() < _DISTRESS_RECOVERY_ANNUAL_PROB:
                events.append(DistressEvent(
                    customer_id=customer_id,
                    event_date=_random_date_in_year(year, sub["event_day"]),
                    event_type="distress_recovery",
                    payload={},
                ))
                state = DistressState.TRADING

    events.sort(key=lambda e: e.event_date)
    return BusinessDistressProfile(
        customer_id=customer_id,
        segment=segment,
        sector=sector,
        late_payment_culture=late_payment_culture,
        events=tuple(events),
    )


def iter_distress_events(profile: BusinessDistressProfile) -> Iterator[DistressEvent]:
    """Yield a profile's hidden distress events in date order (C-S1)."""
    yield from profile.events
