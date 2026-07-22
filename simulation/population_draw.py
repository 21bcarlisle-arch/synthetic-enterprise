"""World-side per-run stochastic population draw (W2_2_population_draw).

WHAT THIS IS
------------
A per-run STOCHASTIC generator of SYNTHETIC new-customer acquisitions for the
years 2021-2025. It exists to close a decisive, quantified gap the atom's own
FRAME pass found: `saas/customers.py`'s hand-authored cast was acquired 13-in-
2016 (founding cohort) plus a one-per-year trickle across 2017-2020, and ZERO
new acquisitions exist anywhere from 2021 through 2025 -- the book is completely
static for the entire second half of the ten-year replay.

This module is ADDITIVE, not REPLACIVE (FRAME decision, 2026-07-13). It does
NOT touch the 24 hand-authored customers -- those stay the fixed narrative core
that 370 downstream test/dashboard references depend on. It draws a per-run
synthetic cohort ON TOP of that core, with its own unambiguous `SYN-` customer
IDs, so "book composition varies run to run" without any one-way-door risk to
already-built mechanisms.

WALL DISCIPLINE (record verbatim, .claude/rules/epistemic-wall-sim.md)
----------------------------------------------------------------------
This is WORLD/sim code. It MUST NOT import `company.*` or `saas.*`. The two
anchored numeric inputs it needs -- the Direct-Debit payment share and the
TDCV consumption bands -- are therefore DUPLICATED here as module constants,
NOT imported, exactly as `simulation/settlement_timetable.py` duplicates its
Elexon constants. The single source of TRUTH remains, respectively,
`docs/market_research/ASSUMPTIONS.md` (DD share) and
`company/compliance/domain_invariants.py` (TDCV bands); a drift-guard test
(`tests/simulation/test_population_draw.py`) imports/reads those sources
directly -- tests/ may import anything -- and asserts these duplicated
constants never drift apart from their sources.

RNG SUBSTREAM DISCIPLINE (C-S2, CLAUDE.md -- non-negotiable)
-----------------------------------------------------------
Every draw here comes from THIS subsystem's OWN named, seeded substream
(`_substream()` derives an isolated `random.Random` from a SHA-256 of the
stream name + base seed). It NEVER touches the global `random` module and can
NEVER shift any other subsystem's output sequence -- the direct lesson of the
real 01:09Z incident where adding draws to a shared life-event RNG shifted
every downstream draw. Proven by `test_substream_isolation_*`.

DETERMINISTIC REPLAY (C-S2): same `base_seed` -> byte-identical population,
every run. Proven by `test_deterministic_replay`.

EVENT-ARRIVAL TOLERANCE (C-S1): acquisitions are modelled as an ordered stream
of individual EVENTS (`iter_acquisition_events()`), one customer at a time with
its own date -- never a batch assumed complete at once.

BASELINE vs CURRICULUM (R13): this is a synthetic CURRICULUM draw, not a
baseline edit. Its `data_regime` is "synthetic". Its rate/segment/band
selection weights are DIAGNOSTICS, never targets (R12/Law A) -- they are the
director's curriculum instrument, never tuned toward a company-P&L outcome.

HONEST SIMPLIFICATIONS (R10, dated)
-----------------------------------
- 2026-07-13: NO anchored population-level REGION distribution exists in this
  codebase (FRAME pass recorded this honestly). Region is emitted as the
  explicit placeholder `_PLACEHOLDER_REGION` ("UNKNOWN_SYNTHETIC"), not a
  fabricated real region. Overridable by the caller.
- 2026-07-13: NO anchored population-level SEGMENT marginal for NEW
  acquisitions exists. `DEFAULT_SEGMENT_WEIGHTS` is a documented placeholder
  (resi-dominant, reflecting that real domestic suppliers acquire
  overwhelmingly residential accounts BY COUNT -- I&C is a small number of
  large accounts), OVERRIDABLE via the `segment_weights` argument with a real
  marginal at integration. Not claimed as anchored.
- 2026-07-13: consumption-BAND selection weights and commodity-mix weights are
  likewise documented placeholders, overridable. Only the band RANGES (TDCV)
  and the DD SHARE are anchored.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Mapping, Optional, Tuple

from simulation.household_segments import TenureType, tenure_for_customer

# ---------------------------------------------------------------------------
# DUPLICATED ANCHORED CONSTANTS -- see WALL DISCIPLINE above. Keep numerically
# identical to their sources at any future touch; the drift-guard test fails
# closed if they diverge.
# ---------------------------------------------------------------------------

# Direct-Debit payment share, DESNZ "Quarterly Energy Prices: June 2026"
# (end-March 2026), via docs/market_research/ASSUMPTIONS.md. SOURCE OF TRUTH:
# ASSUMPTIONS.md -- "Direct Debit was 72% of standard electricity customers and
# 75% of gas customers".
DD_SHARE_ELEC = 0.72
DD_SHARE_GAS = 0.75

# TDCV consumption bands (Ofgem TDCV 2026 review). SOURCE OF TRUTH:
# company/compliance/domain_invariants.py::TDCV_{ELEC,GAS}_{LOW,MEDIUM,HIGH}
# (RangeInvariant.low/.high). Duplicated (kWh/year low, high).
TDCV_BANDS_KWH: Dict[str, Dict[str, Tuple[float, float]]] = {
    "electricity": {
        "LOW": (1400.0, 1800.0),
        "MEDIUM": (2300.0, 2700.0),
        "HIGH": (3600.0, 4000.0),
    },
    "gas": {
        "LOW": (5500.0, 6500.0),
        "MEDIUM": (9000.0, 10000.0),
        "HIGH": (13000.0, 15000.0),
    },
}

# ---------------------------------------------------------------------------
# DOCUMENTED PLACEHOLDER WEIGHTS (R10) -- NOT anchored, overridable. See the
# HONEST SIMPLIFICATIONS block in the module docstring.
# ---------------------------------------------------------------------------
_PLACEHOLDER_REGION = "UNKNOWN_SYNTHETIC"

DEFAULT_SEGMENT_WEIGHTS: Dict[str, float] = {"resi": 0.80, "SME": 0.15, "I&C": 0.05}
DEFAULT_COMMODITY_WEIGHTS: Dict[str, float] = {"electricity": 0.72, "gas": 0.28}
DEFAULT_BAND_WEIGHTS: Dict[str, float] = {"LOW": 0.30, "MEDIUM": 0.45, "HIGH": 0.25}

# Acquisition cadence -- DIRECTOR CURRICULUM "PROFILE B: TRICKLE CONTINUATION"
# (BUILD_THE_BACKLOG.md, director P0, signed). Profile B is a TRICKLE: roughly
# one new customer joins per year on average, stochastically -- not a growth
# explosion, not static. This is the director's CURRICULUM instrument (R13:
# "population draws" are named/versioned/director-authored, never agent-tuned),
# and it matches the hand-authored cast's own established 2017-2020 cadence
# (~1 new customer/year). Realised as Poisson(lambda=1.0) acquisitions/year, so
# the per-year mean and the whole-window mean both land at ~1/yr. This is a
# DIAGNOSTIC rate (R12/Law A), never tuned toward a company-P&L outcome; a
# different curriculum profile is a director-authored change of this constant,
# not an agent-side adjustment.
DEFAULT_ACQUISITIONS_PER_YEAR_LAMBDA = 1.0

DEFAULT_START_YEAR = 2021
DEFAULT_END_YEAR = 2025  # inclusive

STREAM_NAME = "W2_2_population_draw"


# ---------------------------------------------------------------------------
# Substream construction -- the C-S2 heart of this module.
# ---------------------------------------------------------------------------
def _substream(base_seed: int, salt: str = "") -> random.Random:
    """Return an ISOLATED `random.Random` seeded deterministically from this
    subsystem's own name + `base_seed` (+ optional salt).

    Isolation is structural: a fresh `random.Random` instance whose seed is a
    SHA-256 digest of (`STREAM_NAME`:`salt`:`base_seed`). It shares no state
    with the global `random` module or any other subsystem's substream, so a
    draw here can never shift another subsystem's sequence.
    """
    key = f"{STREAM_NAME}:{salt}:{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _poisson(rng: random.Random, lam: float) -> int:
    """Knuth's algorithm for a Poisson draw from an isolated Random."""
    if lam <= 0:
        return 0
    target = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        p *= rng.random()
        if p <= target:
            return k
        k += 1


def _weighted_choice(rng: random.Random, weights: Mapping[str, float]) -> str:
    """Deterministic weighted categorical draw from an isolated Random."""
    keys = list(weights.keys())
    cum: List[float] = []
    running = 0.0
    for key in keys:
        running += weights[key]
        cum.append(running)
    total = running
    x = rng.random() * total
    for key, threshold in zip(keys, cum):
        if x <= threshold:
            return key
    return keys[-1]


@dataclass(frozen=True)
class SyntheticCustomer:
    """One synthetically-drawn acquisition event (world-side).

    Fields mirror the anchored attributes only; `to_customer_dict()` renders a
    `saas/customers.py`-shaped dict for the eventual (L2) integration point,
    which is the layer permitted to see saas -- this module never imports it.
    """
    customer_id: str
    acquisition_date: str  # ISO YYYY-MM-DD
    segment: str
    commodity: str
    payment_method: str  # "direct_debit" | "other"
    consumption_band: str  # LOW | MEDIUM | HIGH
    eac_kwh: float
    region: str
    tariff_type: Optional[str] = None
    data_regime: str = "synthetic"
    acquisition_type: str = "synthetic_draw"
    # SEGMENTATION_GENERATOR_BUILD_PLAN.md step 1: the customer's SIM-truth cohort
    # (12-axis population-coverage taxonomy). DEFAULT-OFF (None) -- only populated
    # when the caller explicitly asks (`assign_cohorts=True`), so existing callers
    # get a byte-identical SyntheticCustomer stream unless they opt in (proven by
    # `test_cohort_draw_default_off_is_byte_identical`). This is HIDDEN SIM TRUTH:
    # it must NEVER cross `company/interfaces/sim_interface.py` (SEGMENTATION_
    # RECONCILIATION_FRAME.md §0 canonical wall ruling) -- `to_customer_dict()`
    # deliberately does NOT include it.
    cohort: Optional["Cohort"] = None

    def to_customer_dict(self) -> dict:
        """Render a saas-shaped customer dict (for the L2 integration layer)."""
        return {
            "customer_id": self.customer_id,
            "acquisition_date": self.acquisition_date,
            "acquisition_type": self.acquisition_type,
            "segment": self.segment,
            "commodity": self.commodity,
            "payment_method": self.payment_method,
            "consumption_band": self.consumption_band,
            "eac_kwh": self.eac_kwh,
            "location": {"lat": None, "lon": None, "region": self.region},
            "tariff_type": self.tariff_type,
            "data_regime": self.data_regime,
        }


def _draw_one(
    rng: random.Random,
    customer_id: str,
    acquisition_date: dt.date,
    segment_weights: Mapping[str, float],
    commodity_weights: Mapping[str, float],
    band_weights: Mapping[str, float],
    region: str,
    base_seed: int,
    assign_cohorts: bool = False,
) -> SyntheticCustomer:
    segment = _weighted_choice(rng, segment_weights)
    commodity = _weighted_choice(rng, commodity_weights)
    band = _weighted_choice(rng, band_weights)
    low, high = TDCV_BANDS_KWH[commodity][band]
    eac = round(rng.uniform(low, high), 1)
    dd_share = DD_SHARE_ELEC if commodity == "electricity" else DD_SHARE_GAS
    payment_method = "direct_debit" if rng.random() < dd_share else "other"
    # DEFAULT OFF (assign_cohorts=False): `cohort` stays None and every prior
    # field/draw above is untouched, so the byte-identical-by-default guarantee
    # holds structurally -- `assign_cohort()` draws from its OWN named substream
    # (keyed on customer_id, never `rng`), so calling it here can never perturb
    # this function's own draw sequence either way (C-S2 isolation).
    cohort = assign_cohort(customer_id, base_seed, region=region) if assign_cohorts else None
    return SyntheticCustomer(
        customer_id=customer_id,
        acquisition_date=acquisition_date.isoformat(),
        segment=segment,
        commodity=commodity,
        payment_method=payment_method,
        consumption_band=band,
        eac_kwh=eac,
        region=region,
        cohort=cohort,
    )


def iter_acquisition_events(
    base_seed: int,
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
    acquisitions_per_year_lambda: float = DEFAULT_ACQUISITIONS_PER_YEAR_LAMBDA,
    segment_weights: Optional[Mapping[str, float]] = None,
    commodity_weights: Optional[Mapping[str, float]] = None,
    band_weights: Optional[Mapping[str, float]] = None,
    region: str = _PLACEHOLDER_REGION,
    assign_cohorts: bool = False,
) -> Iterator[SyntheticCustomer]:
    """Yield synthetic acquisition EVENTS one at a time, in date order
    (C-S1 event-arrival tolerance: a consumer must NOT assume batch
    completeness). Deterministic in `base_seed`.

    Per year in [start_year, end_year], draws a Poisson(lambda) count of new
    acquisitions, each on a drawn day-of-year, each with anchored DD/consumption
    attributes and placeholder segment/region. All draws come from this
    subsystem's own isolated substream.

    `assign_cohorts` (default False, SEGMENTATION_GENERATOR_BUILD_PLAN.md step 1):
    when True, each yielded customer also carries its SIM-truth `Cohort` (the
    12-axis population-coverage taxonomy). Default OFF so existing callers see a
    byte-identical stream -- proven by `test_cohort_draw_default_off_is_byte_
    identical`.
    """
    segment_weights = segment_weights or DEFAULT_SEGMENT_WEIGHTS
    commodity_weights = commodity_weights or DEFAULT_COMMODITY_WEIGHTS
    band_weights = band_weights or DEFAULT_BAND_WEIGHTS

    rng = _substream(base_seed)
    for year in range(start_year, end_year + 1):
        n = _poisson(rng, acquisitions_per_year_lambda)
        # Draw each acquisition's day-of-year, then sort so events arrive in
        # chronological order within the year.
        days_in_year = (dt.date(year, 12, 31) - dt.date(year, 1, 1)).days
        day_offsets = sorted(rng.randint(0, days_in_year) for _ in range(n))
        for i, offset in enumerate(day_offsets, start=1):
            acq_date = dt.date(year, 1, 1) + dt.timedelta(days=offset)
            cid = f"SYN-{year}-{i:03d}"
            yield _draw_one(
                rng,
                customer_id=cid,
                acquisition_date=acq_date,
                segment_weights=segment_weights,
                commodity_weights=commodity_weights,
                band_weights=band_weights,
                region=region,
                base_seed=base_seed,
                assign_cohorts=assign_cohorts,
            )


def draw_population(base_seed: int, **kwargs) -> List[SyntheticCustomer]:
    """Convenience: materialise the full synthetic cohort as an ordered list.

    Prefer `iter_acquisition_events()` where the consumer can process events
    as they arrive (C-S1). This batch form is for tests and callers that
    genuinely need the whole cohort at once.
    """
    return list(iter_acquisition_events(base_seed, **kwargs))


# ═══════════════════════════════════════════════════════════════════════════
# SEGMENTATION GENERATOR — step 1 (SIM cohort draw) + step 2 (tenure→adoption
# gating), per docs/design/SEGMENTATION_GENERATOR_BUILD_PLAN.md and the
# CANONICAL WALL RULING (docs/design/SEGMENTATION_RECONCILIATION_FRAME.md §0):
# segmentation ground truth lives ENTIRELY behind the wall. Every attribute
# below is HIDDEN SIM TRUTH -- it must NEVER cross
# `company/interfaces/sim_interface.py`. Nothing in this section is imported
# by, or importable from, `company/*` or `saas/*` (WALL DISCIPLINE, this
# module's own top-of-file rule; verified by `tools/epistemic_verifier`).
#
# CURRICULUM (R13): the five director-set values below are read LIVE from
# `docs/design/segmentation_curriculum_v1.json` every call (never hardcoded
# here) -- a curriculum change is one versioned edit to that file, never a
# code change. Axis LEVELS (the taxonomy itself) and the observed-block
# conditional SHAPES are structural, not curriculum, and stay in code.
# ═══════════════════════════════════════════════════════════════════════════

COHORT_STREAM_NAME = "W2_2_cohort_draw"
_CURRICULUM_PATH = Path(__file__).resolve().parents[1] / "docs" / "design" / "segmentation_curriculum_v1.json"

_curriculum_cache: Optional[dict] = None


def _load_cohort_curriculum(path: Optional[Path] = None) -> dict:
    """Read the director-set curriculum JSON (R13). Cached per-process (the
    file is director-edited between runs, not mid-run); pass `path` to bypass
    the cache in tests. Raises if the file is missing/malformed -- an absent
    curriculum is a FAILED read (R15 fail-closed), never a silent default that
    would let an unset director dial pass as a value."""
    global _curriculum_cache
    if path is not None:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    if _curriculum_cache is None:
        with open(_CURRICULUM_PATH, "r", encoding="utf-8") as f:
            _curriculum_cache = json.load(f)
    return _curriculum_cache


def _cohort_substream(customer_id: str, base_seed: int, axis: str) -> random.Random:
    """An ISOLATED `random.Random` for one cohort AXIS of one customer,
    seeded from a stable sha256 of (COHORT_STREAM_NAME, axis, customer_id,
    base_seed) -- C-S2. Distinct from `_substream()` above (a different
    stream NAME entirely) and keyed per-customer (not sequential), so
    `assign_cohort()` is callable standalone, in any order, for any
    customer_id -- including the 24 hand-authored customers this module
    never draws acquisitions for -- without perturbing `iter_acquisition_
    events()`'s own sequential substream in any way."""
    key = f"{COHORT_STREAM_NAME}::{axis}::{customer_id}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


# ---------------------------------------------------------------------------
# Axis taxonomy (docs/market_research/population_coverage/cohort_schema.json).
# Structural, not curriculum -- a taxonomy change is a schema change, tracked
# there, not a curriculum edit.
# ---------------------------------------------------------------------------
TENURE_LEVELS: Tuple[str, ...] = ("own_outright", "own_mortgage", "private_rent", "social_rent")
ACCOMMODATION_LEVELS: Tuple[str, ...] = ("detached", "semi", "terraced", "flat", "caravan")
CARS_LEVELS: Tuple[str, ...] = ("0", "1", "2plus")
NSSEC_LEVELS: Tuple[str, ...] = ("higher", "intermediate", "routine_semi", "unemployed_student")
HEATING_FUEL_LEVELS: Tuple[str, ...] = (
    "mains_gas", "mixed", "electric", "oil", "lpg_bottled", "heat_network", "other_offgas",
)

# ---------------------------------------------------------------------------
# TENURE RECONCILIATION (BUILD_PLAN step 2's ⚠ "reconcile the two tenure
# representations FIRST"). `simulation.household_segments.tenure_for_customer`
# is the EXISTING deterministic 3-level draw (owner_occupier/private_renter/
# social_renter), already relied on by 370+ test references and by
# `customer_events.py`'s live churn-tenure adjustment. Rather than drawing a
# SECOND, independent 4-level tenure (which could disagree with the first for
# the same customer_id -- exactly the reconciliation risk flagged), the cohort
# tenure is a strict REFINEMENT: it calls tenure_for_customer() as the anchor
# and, only for OWNER_OCCUPIER, splits it into own_outright/own_mortgage via
# its own named substream. private_rent/social_rent map 1:1. This guarantees
# `collapse_cohort_tenure(cohort_tenure_for_customer(cid, seed)) ==
# tenure_for_customer(cid)` for EVERY customer_id, ALWAYS -- tenure_for_
# customer stays the deterministic fallback/source of truth for the hand-
# authored + SYN customers, exactly as the BUILD_PLAN requires.
#
# The outright/mortgage split (35%/30% of the 65% owner-occupier share) is the
# SAME EHS 2023-24 anchor already cited in household_segments.py's own
# TENURE_POPULATION_SHARE docstring -- not a new figure.
# ---------------------------------------------------------------------------
_OWNER_OUTRIGHT_SHARE_WITHIN_OWNERS = 35.0 / 65.0  # EHS 2023-24: 35% outright of 65% owner-occupier

_TENURE_TYPE_TO_COHORT: Dict[TenureType, str] = {
    TenureType.PRIVATE_RENTER: "private_rent",
    TenureType.SOCIAL_RENTER: "social_rent",
}
_COHORT_TO_TENURE_TYPE: Dict[str, TenureType] = {
    "private_rent": TenureType.PRIVATE_RENTER,
    "social_rent": TenureType.SOCIAL_RENTER,
    "own_outright": TenureType.OWNER_OCCUPIER,
    "own_mortgage": TenureType.OWNER_OCCUPIER,
}


def cohort_tenure_for_customer(customer_id: str, base_seed: int) -> str:
    """The cohort-schema (4-level) tenure for `customer_id` -- a deterministic
    REFINEMENT of `tenure_for_customer()`, never a second independent draw
    (see module note above). Stable for a given (customer_id, base_seed)."""
    base = tenure_for_customer(customer_id)
    if base in _TENURE_TYPE_TO_COHORT:
        return _TENURE_TYPE_TO_COHORT[base]
    # OWNER_OCCUPIER: refine via its own named substream.
    rng = _cohort_substream(customer_id, base_seed, "tenure_owner_split")
    return "own_outright" if rng.random() < _OWNER_OUTRIGHT_SHARE_WITHIN_OWNERS else "own_mortgage"


def collapse_cohort_tenure(cohort_tenure: str) -> TenureType:
    """Collapse a 4-level cohort tenure back to the 3-level `TenureType` --
    the round-trip that proves the reconciliation (own_outright/own_mortgage
    -> OWNER_OCCUPIER; private_rent/social_rent map 1:1)."""
    return _COHORT_TO_TENURE_TYPE[cohort_tenure]


# ---------------------------------------------------------------------------
# The COUPLED OBSERVED BLOCK: accommodation/cars/nssec sampled from
# P(A|T)·P(C|T)·P(S|T) given the tenure spine T (cohort_schema.json's own
# "block" grouping). HONEST SIMPLIFICATION (R10, dated 2026-07-21): no full
# published conditional cross-tab at this exact 4x5 / 4x3 / 4x4 granularity is
# checked into this repo (none exists in open UK data at this joint
# granularity -- see the fusion register's own tenure×fabric/cars/nssec
# entries). These are DOCUMENTED SHAPES that reproduce the DIRECTION and the
# real measured Cramér's V from `population_fusion_assumptions_register.json`
# (tenure×fabric V=0.273, tenure×cars V=0.303 -- the strongest measured pair,
# tenure×nssec V=0.229), NOT a cited conditional-percentage table -- the same
# "shape reproduces the anchor" discipline `household_budget.py` already uses
# for its income ladder. Base national marginals are order-of-magnitude
# EHS/Census-consistent estimates (R10), tilted per tenure by direction only.
# ---------------------------------------------------------------------------

_ACCOMMODATION_NATIONAL: Dict[str, float] = {
    "detached": 0.23, "semi": 0.26, "terraced": 0.26, "flat": 0.24, "caravan": 0.01,
}
# Tenure×fabric V=0.273 (register, evidenced): owner tenures skew to
# houses/better fabric, rented tenures skew to flats (register's own prior,
# not refuted by the measurement, just weaker than "strong").
_ACCOMMODATION_TILT_BY_TENURE: Dict[str, Dict[str, float]] = {
    "own_outright": {"detached": 1.6, "semi": 1.2, "terraced": 0.9, "flat": 0.30, "caravan": 1.5},
    "own_mortgage": {"detached": 1.4, "semi": 1.3, "terraced": 1.0, "flat": 0.40, "caravan": 0.5},
    "private_rent": {"detached": 0.5, "semi": 0.7, "terraced": 1.1, "flat": 1.8, "caravan": 0.5},
    "social_rent": {"detached": 0.3, "semi": 0.8, "terraced": 1.2, "flat": 1.9, "caravan": 0.3},
}

_CARS_NATIONAL: Dict[str, float] = {"0": 0.235, "1": 0.424, "2plus": 0.341}
# Tenure×cars V=0.303 (register, evidenced -- the STRONGEST measured pair);
# tail cell "no cars | social_rented" 2.1x lift.
_CARS_TILT_BY_TENURE: Dict[str, Dict[str, float]] = {
    "own_outright": {"0": 0.6, "1": 1.0, "2plus": 1.4},
    "own_mortgage": {"0": 0.5, "1": 0.9, "2plus": 1.5},
    "private_rent": {"0": 1.4, "1": 1.1, "2plus": 0.6},
    "social_rent": {"0": 2.1, "1": 1.0, "2plus": 0.35},
}

_NSSEC_NATIONAL: Dict[str, float] = {
    "higher": 0.35, "intermediate": 0.24, "routine_semi": 0.29, "unemployed_student": 0.12,
}
# Tenure×nssec V=0.229 (register, evidenced); tail cell "full-time students |
# private rented" 3.3x lift.
_NSSEC_TILT_BY_TENURE: Dict[str, Dict[str, float]] = {
    "own_outright": {"higher": 1.5, "intermediate": 1.1, "routine_semi": 0.7, "unemployed_student": 0.3},
    "own_mortgage": {"higher": 1.6, "intermediate": 1.2, "routine_semi": 0.6, "unemployed_student": 0.3},
    "private_rent": {"higher": 0.8, "intermediate": 0.9, "routine_semi": 1.0, "unemployed_student": 1.9},
    "social_rent": {"higher": 0.3, "intermediate": 0.6, "routine_semi": 1.5, "unemployed_student": 1.6},
}


def _tilted_weights(national: Mapping[str, float], tilt: Mapping[str, float]) -> Dict[str, float]:
    """A tenure-tilted, renormalised weight table: raw_k = national_k *
    tilt_k (default 1.0), then normalised to sum to 1. The tenure-agnostic
    `national` marginal is recovered exactly when every tilt is 1.0."""
    raw = {k: v * tilt.get(k, 1.0) for k, v in national.items()}
    total = sum(raw.values())
    return {k: v / total for k, v in raw.items()}


# ---------------------------------------------------------------------------
# heating_fuel PINNED TO REGION (BUILD_PLAN step 1; the fusion register's own
# "open_data_degradation_finding" -- the 2021 Census DROPPED the fuel x
# tenure/dwelling cross-tab 2011 had, so fuel is crossed against the BLOCK and
# pinned to region only). HONEST SIMPLIFICATION (R10, dated 2026-07-21):
# aggregate fuel x region is near-uniform (V=0.070, register-evidenced) BUT
# the off-gas TAIL is strongly regional (oil-only 0.12% London vs 7.83% Wales,
# ~65x; heat_network tail concentrated in London, 3.8x) -- both DIRECTLY cited
# in the register. The table below is a documented SHAPE reproducing that
# DIRECTION (mains_gas bulk stays near-uniform; the off-gas tail is pinned to
# the regions the register names), not a cited full 7-level x 10-region table
# (none is published at this granularity -- the register's own finding).
# ---------------------------------------------------------------------------

_HEATING_FUEL_NATIONAL: Dict[str, float] = {
    "mains_gas": 0.74, "mixed": 0.09, "electric": 0.08,
    "oil": 0.02, "lpg_bottled": 0.005, "heat_network": 0.03, "other_offgas": 0.035,
}
# Region tilt multipliers (default 1.0 = national). Only regions the register
# names a real tail effect for get a non-trivial tilt; every other region
# stays at the near-uniform national shape (matching the evidenced aggregate
# V=0.070 finding -- region barely moves the mains_gas bulk).
_HEATING_FUEL_TILT_BY_REGION: Dict[str, Dict[str, float]] = {
    "Wales": {"oil": 6.0, "lpg_bottled": 4.0, "other_offgas": 2.5, "mains_gas": 0.85, "heat_network": 0.3},
    "South West": {"oil": 4.0, "lpg_bottled": 3.0, "other_offgas": 2.0, "mains_gas": 0.9, "heat_network": 0.3},
    "North East": {"oil": 2.0, "lpg_bottled": 1.5, "mains_gas": 0.97, "heat_network": 0.5},
    "London": {"heat_network": 4.0, "electric": 1.3, "mains_gas": 0.95, "oil": 0.03, "lpg_bottled": 0.1},
}


def heating_fuel_weights_for_region(region: str) -> Dict[str, float]:
    """The region-pinned heating_fuel weight table (public function so the
    company-discovery twin's own EPC/region prior can be built consistently,
    though it must derive its own independent copy per the WALL DISCIPLINE
    duplication convention rather than importing this one)."""
    tilt = _HEATING_FUEL_TILT_BY_REGION.get(region, {})
    return _tilted_weights(_HEATING_FUEL_NATIONAL, tilt)


# ---------------------------------------------------------------------------
# green_stance / price_sensitivity / channel_pref -- CROSSED (independent),
# drawn straight from the director curriculum marginals (R13). No basis to
# fuse these onto the block (fusion register: residual unmeasurable -> cross,
# the enforced FUSION_BAR_RESIDUAL_v1 gate).
# ---------------------------------------------------------------------------

_CURRICULUM_KEY_BY_AXIS: Dict[str, str] = {
    "green_stance": "green_stance_marginals",
    "price_sensitivity": "price_sensitivity_marginals",
    "channel_pref": "channel_pref_marginals",
}


def _draw_curriculum_axis(customer_id: str, base_seed: int, axis: str, curriculum: dict) -> str:
    rng = _cohort_substream(customer_id, base_seed, axis)
    marginals = curriculum[_CURRICULUM_KEY_BY_AXIS[axis]]["value"]
    return _weighted_choice(rng, marginals)


def region_weights_from_curriculum(curriculum: Optional[dict] = None) -> Dict[str, float]:
    """The director-set synthetic-acquisition region marginal
    (curriculum key `region_marginal_synthetic_acquisitions`, R10-flagged
    'closer to FIDELITY than difficulty' in the curriculum file itself)."""
    c = curriculum if curriculum is not None else _load_cohort_curriculum()
    return c["region_marginal_synthetic_acquisitions"]["value"]


#: The three low-carbon assets whose adoption is tenure-gated per-asset. Kept in
#: sync with `simulation.life_events`' three gated adoption events (solar_install
#: -> solar_pv, ev_acquired -> ev, heat_pump_installed -> heat_pump).
ADOPTION_ASSETS = ("solar_pv", "ev", "heat_pump")


def low_carbon_adoption_eligibility_multiplier(
    cohort_tenure: str, asset: Optional[str] = None, curriculum: Optional[dict] = None
) -> float:
    """BUILD_PLAN step 2: the tenure→low-carbon-adoption gating STRENGTH,
    read live from the director curriculum (`tenure_adoption_gating_strength`,
    R13 -- never hardcoded here).

    ASSET-AGNOSTIC (asset=None, the original signature -- byte-identical): rented
    tenures (`gated_tenures`) get the scalar `renter_adoption_propensity_multiplier`
    (0.17 ≈ the 7%/42% owner-vs-renter agency ratio); all others get
    `owner_multiplier` (1.0). Unchanged so every existing caller/test is preserved.

    PER-ASSET (asset in ADOPTION_ASSETS -- director CONFIRMED 2026-07-22): reads
    `value["per_asset"][asset][cohort_tenure]`. Solar/EV/heat-pump gate rented
    tenures DIFFERENTLY (a roof-mod needs a landlord's permission; an EV only needs
    off-street parking, already carried by `has_driveway`; a heat pump is the
    landlord's capital call) -- so a single scalar over-collapses three physically
    distinct barriers. ASSERTED R13 curriculum, falsifiable (population register),
    NEVER tuned to company outcomes. If the per_asset table is absent or lacks this
    asset/tenure, FALLS BACK to the asset-agnostic scalar (fail-safe, never raises
    on a curriculum that predates this refinement).

    A pure function -- independently testable and wireable into any per-premise
    adoption draw (e.g. `simulation.life_events.generate_life_events`'s own optional
    `adoption_eligibility_multiplier`) without this module knowing about the caller.
    """
    c = curriculum if curriculum is not None else _load_cohort_curriculum()
    gating = c["tenure_adoption_gating_strength"]["value"]
    if asset is not None:
        per_asset = gating.get("per_asset") or {}
        asset_table = per_asset.get(asset)
        if isinstance(asset_table, dict) and cohort_tenure in asset_table:
            return float(asset_table[cohort_tenure])
        # fail-safe: an older curriculum without per_asset -> asset-agnostic scalar
    if cohort_tenure in gating["gated_tenures"]:
        return float(gating["renter_adoption_propensity_multiplier"])
    return float(gating["owner_multiplier"])


def low_carbon_adoption_eligibility_multipliers_by_asset(
    cohort_tenure: str, curriculum: Optional[dict] = None
) -> dict:
    """The full per-asset multiplier map for a tenure, ready to pass straight to
    `generate_life_events(adoption_eligibility_multiplier=...)`: one factor per
    asset in ADOPTION_ASSETS. Each entry resolves via the per-asset table with the
    asset-agnostic scalar as its fail-safe fallback (see the single-asset fn)."""
    return {
        asset: low_carbon_adoption_eligibility_multiplier(cohort_tenure, asset, curriculum)
        for asset in ADOPTION_ASSETS
    }


@dataclass(frozen=True)
class Cohort:
    """A customer's SIM-truth cohort cell (9 of the schema's 12 axes -- solar_PV/
    EV/home_battery are OUT OF SCOPE here, already generated elsewhere per the
    BUILD_PLAN's own verified inventory: `simulation.household`'s deterministic
    baseline + `simulation.adoption_geography`'s national/regional S-curves;
    home_battery has no generator anywhere yet, an explicit R10 gap, not
    silently fabricated here). HIDDEN SIM TRUTH -- see module-section docstring.
    """
    customer_id: str
    tenure: str              # 4-level (own_outright/own_mortgage/private_rent/social_rent)
    accommodation: str
    cars: str
    nssec: str
    heating_fuel: str
    region: str
    green_stance: str        # NO company observable -- hidden truth only, ever
    price_sensitivity: str
    channel_pref: str


def assign_cohort(customer_id: str, base_seed: int, *, region: Optional[str] = None,
                  curriculum: Optional[dict] = None) -> Cohort:
    """BUILD_PLAN step 1: draw `customer_id`'s SIM-truth cohort cell.

    Deterministic in (customer_id, base_seed) -- callable for ANY customer_id
    (hand-authored, SYN-*, or a future acquisition), not just the ones this
    module itself sequentially draws (C-S2: `_cohort_substream` keys directly
    on customer_id, no dependency on draw order). `region`, if given, PINS the
    region (e.g. to the value `iter_acquisition_events` already drew for this
    customer via a DIFFERENT mechanism) rather than drawing a second,
    possibly-conflicting one; if omitted, region is drawn from the curriculum's
    own synthetic-acquisition marginal.
    """
    c = curriculum if curriculum is not None else _load_cohort_curriculum()

    tenure = cohort_tenure_for_customer(customer_id, base_seed)

    accommodation = _weighted_choice(
        _cohort_substream(customer_id, base_seed, "accommodation"),
        _tilted_weights(_ACCOMMODATION_NATIONAL, _ACCOMMODATION_TILT_BY_TENURE.get(tenure, {})),
    )
    cars = _weighted_choice(
        _cohort_substream(customer_id, base_seed, "cars"),
        _tilted_weights(_CARS_NATIONAL, _CARS_TILT_BY_TENURE.get(tenure, {})),
    )
    nssec = _weighted_choice(
        _cohort_substream(customer_id, base_seed, "nssec"),
        _tilted_weights(_NSSEC_NATIONAL, _NSSEC_TILT_BY_TENURE.get(tenure, {})),
    )

    if region is None:
        region = _weighted_choice(
            _cohort_substream(customer_id, base_seed, "region"),
            region_weights_from_curriculum(c),
        )

    heating_fuel = _weighted_choice(
        _cohort_substream(customer_id, base_seed, "heating_fuel"),
        heating_fuel_weights_for_region(region),
    )

    green_stance = _draw_curriculum_axis(customer_id, base_seed, "green_stance", c)
    price_sensitivity = _draw_curriculum_axis(customer_id, base_seed, "price_sensitivity", c)
    channel_pref = _draw_curriculum_axis(customer_id, base_seed, "channel_pref", c)

    return Cohort(
        customer_id=customer_id,
        tenure=tenure,
        accommodation=accommodation,
        cars=cars,
        nssec=nssec,
        heating_fuel=heating_fuel,
        region=region,
        green_stance=green_stance,
        price_sensitivity=price_sensitivity,
        channel_pref=channel_pref,
    )
