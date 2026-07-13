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
import math
import random
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Mapping, Optional, Tuple

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
) -> SyntheticCustomer:
    segment = _weighted_choice(rng, segment_weights)
    commodity = _weighted_choice(rng, commodity_weights)
    band = _weighted_choice(rng, band_weights)
    low, high = TDCV_BANDS_KWH[commodity][band]
    eac = round(rng.uniform(low, high), 1)
    dd_share = DD_SHARE_ELEC if commodity == "electricity" else DD_SHARE_GAS
    payment_method = "direct_debit" if rng.random() < dd_share else "other"
    return SyntheticCustomer(
        customer_id=customer_id,
        acquisition_date=acquisition_date.isoformat(),
        segment=segment,
        commodity=commodity,
        payment_method=payment_method,
        consumption_band=band,
        eac_kwh=eac,
        region=region,
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
) -> Iterator[SyntheticCustomer]:
    """Yield synthetic acquisition EVENTS one at a time, in date order
    (C-S1 event-arrival tolerance: a consumer must NOT assume batch
    completeness). Deterministic in `base_seed`.

    Per year in [start_year, end_year], draws a Poisson(lambda) count of new
    acquisitions, each on a drawn day-of-year, each with anchored DD/consumption
    attributes and placeholder segment/region. All draws come from this
    subsystem's own isolated substream.
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
            )


def draw_population(base_seed: int, **kwargs) -> List[SyntheticCustomer]:
    """Convenience: materialise the full synthetic cohort as an ordered list.

    Prefer `iter_acquisition_events()` where the consumer can process events
    as they arrive (C-S1). This batch form is for tests and callers that
    genuinely need the whole cohort at once.
    """
    return list(iter_acquisition_events(base_seed, **kwargs))
