"""Stock-representative premise population — the draw that replaces a chosen panel.

Atom: `C14_thermal_parameter_inference` (the population half of its L2->L3 step),
consumed by `tools/couple_fabric.py`. World-side (`simulation/`): this is BASELINE
fidelity and is fixed blind to company P&L (R13).

PURPOSE, GUARANTEES, WHY — stated first (OPS1) or the mechanism is deleted
=========================================================================

**Purpose.** Draw N domestic premises whose *composition* comes from published
England housing-stock statistics rather than from whoever wrote the fixture.

**Guarantee.** For a large enough N, the drawn population reproduces the three
published one-dimensional marginals it was raked to — property type, build era and
EPC band — within binomial sampling error, and it reproduces a published
*conditional* fact that was NOT a raking target (ONS: >80% of pre-1930 dwellings sit
in bands D-G). The second is the one that can fail: raking to marginals is free to
destroy a conditional, and nothing about matching three marginals implies the joint
is right.

**Why it is needed, and why now.** `C14`'s own L2 record named two exit conditions
for L3: wire the belief into a live decision path (done 2026-08-09,
`company/pricing/fabric_intervention.py`), and measure the gap on a POPULATION
rather than a hand-picked panel. The panel in `tools/couple_fabric.py` is ten
authored premises whose composition was *chosen to span the stock*, so no result on
it can separate the company's skill from the panel designer's taste: pick ten homes
the EPC register happens to describe badly and the company's inference looks
brilliant; pick ten it describes well and the same code looks useless. A gap number
is only a finding about a book if the book was not selected.

The blocker was located precisely and it was real: `simulation/population_draw.py`
draws *customers* (region, tenure, cohort, consumption band) and `SyntheticCustomer`
carries no `home_type`, `epc_rating` or `bedrooms`, so `simulation.household.
make_household` defaults every draw to the same `suburban_semi` — a population of
clones, which is a worse instrument than the panel, not a better one. This module
draws the PREMISE dimensions that `simulation.fabric_physics.fabric_parameters`
actually turns into a heat-loss coefficient (property type, build era, insulation,
bedrooms) and nothing else.

WHAT THIS IS NOT
----------------
It is not a supplier's book. A real supplier's customers are a *selected* subset of
the national stock (acquisition channel, tariff, region, credit). Drawing from the
national stock removes the fixture author's taste and replaces it with the
assumption that the book looks like England, which is itself false in a way nobody
here has measured. Stated so it cannot be mistaken for realism it does not have.

HOW THE JOINT IS BUILT, AND WHICH PART IS ANCHORED
--------------------------------------------------
Three published marginals exist; the JOINT does not. Crossing them independently
would produce post-2000 detached houses in band G, which is not a population any
statistic should be computed on. So:

1. A SEED joint is formed from the independent product times two *directional*
   tilts (older stock rates worse; flats rate better than houses of the same age).
   THE TILT MAGNITUDES ARE NOT ANCHORED. Only their direction is.
2. The seed is RAKED (iterative proportional fitting) onto all three published
   marginals. Raking is what makes the tilt magnitudes matter less than they look:
   whatever the tilt, the fitted joint reproduces every published marginal exactly.
3. The published CONDITIONAL that was not a raking target is then checked against
   the fitted joint (`pre_1930_share_in_bands_d_to_g`). Raking can and does move a
   conditional, so this check is independent of the fit and is allowed to fail.

HONEST SIMPLIFICATIONS (R10 — declared here, never discovered later)
--------------------------------------------------------------------
* **Bungalows are folded into DETACHED.** EHS reports bungalow as its own dwelling
  type (8% of stock); `simulation.household.PropertyType` has no such member and
  adding one would touch every `PropertyType`-keyed table in the codebase. The fold
  is toward DETACHED because a bungalow's thermal signature (large roof and ground
  floor relative to its floor area) is nearest detached. CONSEQUENCE, stated rather
  than hidden: the drawn detached share is 25%, against a published 17%.
* **The post-1990 published share is SPLIT across two sim eras and the split is not
  published.** EHS gives 1981-90 (7%) and post-1990 (21%); the sim's `BuildEra` has
  `1981_2000` and `post_2000`. The 21% is divided 30/70 between 1991-2000 and
  post-2000 on the reasoning that the post-2000 window is twice as long. Only the
  SUM is anchored, and `published_marginal_recovery` reports the sum, so the
  unanchored part of this choice cannot be validated by the marginal control and is
  not claimed to be.
* **Off-gas liquid fuel and district heat are EXCLUDED, not folded into gas.** The
  trace generator meters gas or electricity; an oil tank is neither. The
  representable heating systems are renormalised over ~94.8% of the stock and the
  excluded ~5.2% is named. Folding oil into gas would have produced a gas meter
  read for a home with no gas meter.
* **Bedrooms are an UNANCHORED placeholder shape conditioned on property type.**
  Two searches found no published stock-wide bedroom marginal. This matters more
  than it looks: bedrooms drive `fabric_physics.floor_area_m2`, which scales the
  heat-loss coefficient nearly linearly, so the LEVEL of every HLC here rests on an
  unpublished table. The RANKING between premises is far more robust to it.
* **EPC lodgement dates are drawn UNIFORMLY over the ten years before `as_of`.**
  Real lodgement is transaction-driven and skewed recent. Uniform overstates
  staleness, which widens the company's prior — i.e. it is not a flattering choice.
* **Solar PV and EVs are OFF for every drawn premise**, exactly as they are in the
  authored panel. This is deliberate one-variable-at-a-time discipline: the point of
  this build is to change WHO composed the population and nothing else, so that a
  panel-vs-population difference is attributable to composition. Switching them on
  (both anchored: EHS 2023-24 solar 5.9%, EV 7.4%) is the next change, not this one.
* **The EPC letter band reaches the company only through `insulation`.** The
  certificate seam (`tools/couple_fabric.py::_certificate_for`) reports the SIM's own
  insulation level, so the register misdescribes fabric through its U-value
  assumptions rather than through a wrong band. Unchanged by this build; named
  because a population makes the omission larger, not smaller.

C-S2 (RNG SUBSTREAM DISCIPLINE)
-------------------------------
Every draw comes from a substream keyed on `STREAM_NAME`, the premise id and the
axis, so (a) no draw here can shift another subsystem's sequence and (b) premise
`P0007` is identical whether the population has 10 members or 10,000 — growing N
appends, it does not reshuffle. This is the 17th independent derivation of the same
substream construction in this codebase; `SP2_2_rng_substream_primitive` is the atom
that collapses them and this is logged as its debt, not fixed opportunistically here
(remediation-on-touch, and this file is new rather than touched).

REUSE: simulation/premise_population.py
CLASS: SUBSYSTEM
INDEX: searched "stock representative population draw premise property type build era EPC
band", "premise population", "EHS marginal draw" -- 0 rows matched. The nearest existing
thing is `simulation/population_draw.py`, and it was READ before this was written: it draws
CUSTOMERS (region, tenure, cohort, consumption band) and `SyntheticCustomer` carries no
premise attributes at all, which is exactly the blocker C14's L2 record named. Extending it
was rejected because the two draws answer different questions and share no state -- the
`_substream` / `_weighted_choice` / `_tilted_weights` IDIOM is deliberately followed here so
`SP2_2_rng_substream_primitive` collapses both at once.
EVALUATED: `scipy.stats.contingency` (has IPF-adjacent machinery), `statsmodels` raking,
`ipfn`. REJECTED: none is a declared dependency of this repo, the fit is 168 cells and 40
lines, and the SIMPLICITY GUARD binds -- a raking dependency to fit three marginals would be
the cathedral it warns about. The convergence FAILURE mode is the part that needed owning
(published margins that sum to 100.1% make the fit infeasible), and owning it means the code
must raise rather than return quietly, which is a decision no library makes for us.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from simulation.household import (
    _EPC_TO_INSULATION,
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    PropertyType,
)

STREAM_NAME = "C14_premise_population"

# ---------------------------------------------------------------------------
# PUBLISHED MARGINALS. Every entry carries the source it came from; a share
# without one is a defect, not a default.
# ---------------------------------------------------------------------------

# EHS 2022-23 AT1_5 (MHCLG, July 2024): terraced 29%, semi-detached 25%,
# detached 17%, flat 21%, bungalow 8%. Bungalow folded into detached (see the
# HONEST SIMPLIFICATIONS block) => detached 25%.
PUBLISHED_PROPERTY_TYPE_SHARE: dict[PropertyType, float] = {
    PropertyType.TERRACED: 0.29,
    PropertyType.SEMI_DETACHED: 0.25,
    PropertyType.DETACHED: 0.17 + 0.08,
    PropertyType.FLAT: 0.21,
}
PROPERTY_TYPE_SOURCE = "EHS 2022-23 AT1_5 (MHCLG, July 2024); bungalow 8% folded into detached"

# EHS 2022-23 AT1_5: pre-1919 20%, 1919-44 15%, 1945-64 18%, 1965-80 19%,
# 1981-90 7%, post-1990 21%. The sim's era enum splits at 2000, not 1990, so the
# published post-1990 21% is divided 30/70; ONLY THE SUM IS ANCHORED.
_POST_1990_PUBLISHED_SHARE = 0.21
_SHARE_OF_POST_1990_BUILT_IN_THE_1990S = 0.30

PUBLISHED_BUILD_ERA_SHARE: dict[BuildEra, float] = {
    BuildEra.PRE_1919: 0.20,
    BuildEra.ERA_1919_1944: 0.15,
    BuildEra.ERA_1945_1964: 0.18,
    BuildEra.ERA_1965_1980: 0.19,
    BuildEra.ERA_1981_2000: 0.07
    + _POST_1990_PUBLISHED_SHARE * _SHARE_OF_POST_1990_BUILT_IN_THE_1990S,
    BuildEra.POST_2000: _POST_1990_PUBLISHED_SHARE
    * (1.0 - _SHARE_OF_POST_1990_BUILT_IN_THE_1990S),
}
BUILD_ERA_SOURCE = (
    "EHS 2022-23 AT1_5 (MHCLG, July 2024); the published post-1990 21% split 30/70 "
    "across the sim's 1981-2000 / post-2000 eras — split UNPUBLISHED, sum anchored"
)

# EHS 2022-23 Energy Chapter AT1_2 (MHCLG, July 2024). A and B are reported
# together at 3.3% and are drawn as one cell; the stored letter is "B".
EPC_BANDS: tuple[str, ...] = ("AB", "C", "D", "E", "F", "G")
PUBLISHED_EPC_BAND_SHARE: dict[str, float] = {
    "AB": 0.033,
    "C": 0.448,
    "D": 0.426,
    "E": 0.068,
    "F": 0.021,
    "G": 0.005,
}
EPC_BAND_SOURCE = "EHS 2022-23 Energy Chapter AT1_2 (MHCLG, July 2024)"

_BAND_TO_LETTER: dict[str, str] = {
    "AB": "B",
    "C": "C",
    "D": "D",
    "E": "E",
    "F": "F",
    "G": "G",
}

# ---------------------------------------------------------------------------
# THE PUBLISHED CONDITIONAL — an ORACLE, never a raking target.
#
# ONS, "Energy efficiency of housing in England and Wales: 2023" (published
# 1 November 2023, coverage April 2013 - March 2023): dwellings constructed
# before 1930 had a median EPC score of 59 in England (band E) and "more than
# 80% were rated in bands D to G"; dwellings constructed after 2011 had a median
# score of 84 (band B), with 84% of English dwellings in band B.
#
# The sim's era bands do not split at 1930, so pre-1930 is represented by
# PRE_1919 + ERA_1919_1944 — which reaches 1944 and therefore includes stock the
# ONS statement excludes. That makes the check CONSERVATIVE in a stated
# direction: the extra 1930-44 stock is newer than the cohort ONS measured, so if
# anything it pulls the D-G share DOWN, and a fitted joint clearing the bar over
# the wider window clears it over the narrower one.
# ---------------------------------------------------------------------------
OLD_STOCK_ERAS: tuple[BuildEra, ...] = (BuildEra.PRE_1919, BuildEra.ERA_1919_1944)
BANDS_D_TO_G: tuple[str, ...] = ("D", "E", "F", "G")
ONS_PRE_1930_MIN_SHARE_IN_BANDS_D_TO_G = 0.80
OLD_STOCK_CONDITIONAL_SOURCE = (
    "ONS, Energy efficiency of housing in England and Wales: 2023 (1 Nov 2023) — "
    "pre-1930 dwellings: median score 59 (band E), >80% in bands D-G"
)

# THE BAR, AND WHY IT IS NOT 0.80.
#
# The published statement is about PRE-1930 dwellings; the widest sim cohort that
# contains them is PRE_1919 + ERA_1919_1944, which reaches 1944 and therefore
# DILUTES the ONS cohort with newer stock. The bar is the published 0.80 diluted
# under the most extreme admissible assumption, so that no invented parameter
# enters it:
#
#   * worst case, the ENTIRE published 1919-44 share (15pp) is stock built after
#     1930 — the largest dilution the era bands can produce;
#   * the diluting stock is bounded below by the published all-England D-G share,
#     0.426 + 0.068 + 0.021 + 0.005 = 0.520 (EHS AT1_2), since interwar stock
#     cannot be more efficient than a national average that includes every
#     post-1990 home;
#   * cohort weights 20/(20+15) = 0.571 and 15/35 = 0.429.
#
#   0.571 x 0.80 + 0.429 x 0.520 = 0.680
#
# Both inputs are published; nothing here was fitted. FOR THE RECORD, because a
# bar chosen after seeing the number it judges is worthless: the fitted joint
# measures 0.794 and the tilt magnitudes were NOT adjusted after that was known.
# The independent product of the same three marginals measures 0.520 and FAILS
# this bar by 16 points, which is what makes it a test rather than a formality.
OLD_STOCK_MIN_SHARE_IN_BANDS_D_TO_G = 0.680

# ---------------------------------------------------------------------------
# SEED TILTS. DIRECTION is published; MAGNITUDE is not. Raking (below) fits the
# published marginals whatever these are, so they shape the JOINT only.
# ---------------------------------------------------------------------------

# Older stock rates worse. Multipliers on the independent product, per era.
_EPC_TILT_BY_ERA: dict[BuildEra, dict[str, float]] = {
    BuildEra.PRE_1919: {"AB": 0.05, "C": 0.30, "D": 1.30, "E": 3.0, "F": 5.0, "G": 8.0},
    BuildEra.ERA_1919_1944: {"AB": 0.10, "C": 0.45, "D": 1.40, "E": 2.4, "F": 3.5, "G": 4.5},
    BuildEra.ERA_1945_1964: {"AB": 0.25, "C": 0.75, "D": 1.35, "E": 1.2, "F": 1.0, "G": 0.9},
    BuildEra.ERA_1965_1980: {"AB": 0.50, "C": 1.05, "D": 1.20, "E": 0.7, "F": 0.5, "G": 0.4},
    BuildEra.ERA_1981_2000: {"AB": 1.60, "C": 1.60, "D": 0.60, "E": 0.2, "F": 0.1, "G": 0.05},
    BuildEra.POST_2000: {"AB": 6.00, "C": 1.90, "D": 0.20, "E": 0.05, "F": 0.02, "G": 0.01},
}

# Flats rate better than houses of the same age (ONS 2023: flats and maisonettes
# median 73 = band C, against semi-detached 65 = band D, the lowest English type).
_EPC_TILT_BY_PROPERTY_TYPE: dict[PropertyType, dict[str, float]] = {
    PropertyType.FLAT: {"AB": 1.8, "C": 1.35, "D": 0.80, "E": 0.65, "F": 0.55, "G": 0.50},
    PropertyType.TERRACED: {"AB": 0.95, "C": 1.00, "D": 1.00, "E": 1.05, "F": 1.10, "G": 1.10},
    PropertyType.SEMI_DETACHED: {"AB": 0.85, "C": 0.92, "D": 1.08, "E": 1.15, "F": 1.20, "G": 1.20},
    PropertyType.DETACHED: {"AB": 0.90, "C": 0.90, "D": 1.05, "E": 1.20, "F": 1.35, "G": 1.45},
}

# ---------------------------------------------------------------------------
# HEATING SYSTEM. EHS 2022-23 AT3_1 / EHS 2023-24 Low Carbon Tech AT4: ~86% of
# homes gas-fired; heat pump ~0.8% (2022). The remainder of the stock is
# electric (~8%), district heat (~2%) and off-gas liquid fuel (~3.2%).
#
# EXCLUSION, DECLARED: district heat and oil/LPG are NOT representable as a
# metered commodity here, so they are dropped and the rest renormalised over the
# remaining 94.8%. The alternative — folding them into gas — would have put a gas
# meter read on a home with no gas meter.
# ---------------------------------------------------------------------------
_GAS_FIRED_SHARE = 0.86
_HEAT_PUMP_SHARE = 0.008
_ELECTRIC_HEAT_SHARE = 0.08
EXCLUDED_HEATING_SHARE = 0.052  # district heat ~2% + oil/LPG ~3.2%
HEATING_SOURCE = "EHS 2022-23 AT3_1; EHS 2023-24 Low Carbon Technologies AT4"

# UNANCHORED splits within an anchored total (R10).
_COMBI_SHARE_OF_GAS = 0.70
_STORAGE_SHARE_OF_ELECTRIC = 0.60


def published_heating_weights() -> dict[HeatingSystem, float]:
    """The representable heating systems, renormalised over the stock that has a
    gas or electricity meter. The excluded share is a module constant, not a
    silent remainder."""
    raw = {
        HeatingSystem.GAS_BOILER_COMBI: _GAS_FIRED_SHARE * _COMBI_SHARE_OF_GAS,
        HeatingSystem.GAS_BOILER_SYSTEM: _GAS_FIRED_SHARE * (1.0 - _COMBI_SHARE_OF_GAS),
        HeatingSystem.HEAT_PUMP_AIR: _HEAT_PUMP_SHARE,
        HeatingSystem.ELECTRIC_STORAGE: _ELECTRIC_HEAT_SHARE * _STORAGE_SHARE_OF_ELECTRIC,
        HeatingSystem.ELECTRIC_DIRECT: _ELECTRIC_HEAT_SHARE * (1.0 - _STORAGE_SHARE_OF_ELECTRIC),
    }
    total = sum(raw.values())
    return {k: v / total for k, v in raw.items()}


_GAS_SYSTEMS = (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)


# ---------------------------------------------------------------------------
# METER CADENCE. Derived from anchors this repo already holds rather than from a
# new number: DESNZ Q4 2024 Smart Meters Statistics Table 5a gives domestic
# smart penetration 10.6% (2016) -> 68.9% (2024), and ~10% of installed smart
# meters are not in smart mode (already anchored in ASSUMPTIONS.md as
# `SMART_METER_NOT_COMMUNICATING_RATE`). Linear interpolation to the 2022
# measurement window gives 54.3% smart, times 0.90 communicating = 48.9% of
# premises on a daily read. The interpolation is stated as an interpolation.
# ---------------------------------------------------------------------------
_SMART_SHARE_2016 = 0.106
_SMART_SHARE_2024 = 0.689
_SMART_COMMUNICATING_RATE = 0.90
CADENCE_SOURCE = (
    "DESNZ Q4 2024 Smart Meters Statistics Table 5a (10.6% 2016 -> 68.9% 2024, "
    "LINEARLY INTERPOLATED to the window year) x 0.90 in smart mode"
)
# UNANCHORED split of the non-smart estate between monthly and quarterly reads.
_MONTHLY_SHARE_OF_TRADITIONAL = 0.50
DAILY_CADENCE_DAYS = 1
MONTHLY_CADENCE_DAYS = 30
QUARTERLY_CADENCE_DAYS = 90


def smart_read_share(year: int) -> float:
    """Share of premises whose supplier holds a DAILY read, in `year`."""
    fraction = (year - 2016) / (2024 - 2016)
    fraction = min(1.0, max(0.0, fraction))
    penetration = _SMART_SHARE_2016 + (_SMART_SHARE_2024 - _SMART_SHARE_2016) * fraction
    return penetration * _SMART_COMMUNICATING_RATE


# EPC register coverage: ~60% of stock holds a certificate, transaction-biased
# (docs/design/PREMISE_FABRIC_PHYSICS_DISCOVER.md, observed-in-report).
# Certificates are valid ten years, so a lodgement is drawn in [as_of-10y, as_of).
EPC_COVERAGE_SHARE = 0.60
EPC_VALIDITY_YEARS = 10
EPC_COVERAGE_SOURCE = "docs/design/PREMISE_FABRIC_PHYSICS_DISCOVER.md (EPC coverage ~60% of stock)"

# UNANCHORED (R10): no published stock-wide bedroom marginal was found. Bedrooms
# scale floor area and hence the LEVEL of every heat-loss coefficient here.
_BEDROOM_WEIGHTS_BY_PROPERTY_TYPE: dict[PropertyType, dict[int, float]] = {
    PropertyType.FLAT: {1: 0.35, 2: 0.50, 3: 0.15},
    PropertyType.TERRACED: {2: 0.40, 3: 0.45, 4: 0.15},
    PropertyType.SEMI_DETACHED: {2: 0.20, 3: 0.60, 4: 0.20},
    PropertyType.DETACHED: {3: 0.35, 4: 0.45, 5: 0.20},
}


# ---------------------------------------------------------------------------
# Substream construction (C-S2). See SP2_2_rng_substream_primitive.
# ---------------------------------------------------------------------------
def _substream(base_seed: int, salt: str) -> random.Random:
    key = f"{STREAM_NAME}:{salt}:{base_seed}".encode("utf-8")
    return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))


def _weighted_choice(rng: random.Random, weights: Mapping):
    """Deterministic weighted categorical draw. RAISES on a non-positive total —
    a draw from an empty distribution must fail, never silently return the last
    key (R15 fail-open)."""
    keys = list(weights.keys())
    total = sum(weights[k] for k in keys)
    if total <= 0.0 or not keys:
        raise ValueError(f"cannot draw from a distribution with total weight {total}")
    x = rng.random() * total
    running = 0.0
    for key in keys:
        running += weights[key]
        if x <= running:
            return key
    return keys[-1]


# ---------------------------------------------------------------------------
# The joint: seed, then rake.
# ---------------------------------------------------------------------------
Cell = tuple[PropertyType, BuildEra, str]


def seed_joint() -> dict[Cell, float]:
    """The independent product times the two directional tilts. NOT the joint the
    population is drawn from — `raked_joint()` is."""
    joint: dict[Cell, float] = {}
    for ptype, p_share in PUBLISHED_PROPERTY_TYPE_SHARE.items():
        for era, e_share in PUBLISHED_BUILD_ERA_SHARE.items():
            for band in EPC_BANDS:
                joint[(ptype, era, band)] = (
                    p_share
                    * e_share
                    * PUBLISHED_EPC_BAND_SHARE[band]
                    * _EPC_TILT_BY_ERA[era][band]
                    * _EPC_TILT_BY_PROPERTY_TYPE[ptype][band]
                )
    return joint


def independent_joint() -> dict[Cell, float]:
    """The tilt-free product of the three published marginals — the null the
    vacuity guard compares against, so 'the tilt did nothing' is detectable."""
    return {
        (ptype, era, band): p * e * PUBLISHED_EPC_BAND_SHARE[band]
        for ptype, p in PUBLISHED_PROPERTY_TYPE_SHARE.items()
        for era, e in PUBLISHED_BUILD_ERA_SHARE.items()
        for band in EPC_BANDS
    }


def _marginal(joint: Mapping[Cell, float], axis: int) -> dict:
    out: dict = {}
    for cell, weight in joint.items():
        out[cell[axis]] = out.get(cell[axis], 0.0) + weight
    return out


# Published percentages are ROUNDED and do not always sum to 100: EHS AT1_2's EPC
# bands sum to 100.1%. Three mutually inconsistent margins have no joint that fits
# all three, and IPF then cycles forever instead of converging — which is exactly
# what happened here on first run, at a residual of 2.9e-4, i.e. the rounding.
# Rescaling each margin to sum to 1 is the standard handling and is done EXPLICITLY,
# with a bound: anything further out than publication rounding is a wrong number
# rather than a rounded one, and RAISES instead of being quietly normalised away.
MAX_PUBLISHED_ROUNDING_SLACK = 0.005


def _normalised_target(target: Mapping, *, axis: int) -> dict:
    total = sum(target.values())
    if abs(total - 1.0) > MAX_PUBLISHED_ROUNDING_SLACK:
        raise ValueError(
            f"published marginal on axis {axis} sums to {total:.4f}, which is further "
            f"from 1 than publication rounding ({MAX_PUBLISHED_ROUNDING_SLACK}) — that is "
            "a wrong share, not a rounded one"
        )
    return {k: v / total for k, v in target.items()}


def rake(
    joint: Mapping[Cell, float],
    targets: Sequence[Mapping],
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 200,
) -> dict[Cell, float]:
    """Iterative proportional fitting of `joint` onto the three 1-D `targets`.

    RAISES if it has not converged inside `max_iterations`. A non-converged fit
    that returned quietly would hand back a joint whose marginals are not the
    published ones while every caller believed they were — fail-open, and the
    exact shape R15 names.
    """
    targets = tuple(_normalised_target(t, axis=i) for i, t in enumerate(targets))
    current = {cell: float(w) for cell, w in joint.items()}
    worst = float("inf")
    for _ in range(max_iterations):
        for axis, target in enumerate(targets):
            observed = _marginal(current, axis)
            for cell in current:
                key = cell[axis]
                have = observed.get(key, 0.0)
                if have <= 0.0:
                    continue
                current[cell] *= target.get(key, 0.0) / have
        # Measured AFTER the full sweep, across EVERY axis. Measuring an axis
        # just before its own rescaling reports the error the previous axis left,
        # which flatters the fit and would let a non-converged joint through.
        worst = max(
            max(abs(_marginal(current, axis).get(k, 0.0) - target.get(k, 0.0)) for k in target)
            for axis, target in enumerate(targets)
        )
        if worst < tolerance:
            return current
    raise RuntimeError(
        f"raking did not converge in {max_iterations} iterations (worst marginal "
        f"error {worst:.3e}); the fitted joint would not carry the published marginals"
    )


def raked_joint() -> dict[Cell, float]:
    """The distribution premises are actually drawn from."""
    return rake(
        seed_joint(),
        (
            PUBLISHED_PROPERTY_TYPE_SHARE,
            PUBLISHED_BUILD_ERA_SHARE,
            {b: PUBLISHED_EPC_BAND_SHARE[b] for b in EPC_BANDS},
        ),
    )


def conditional_share_in_bands(
    joint: Mapping[Cell, float],
    *,
    eras: Iterable[BuildEra],
    bands: Iterable[str],
) -> float:
    """P(band in `bands` | era in `eras`) under `joint` — the ORACLE statistic.

    RAISES on an empty conditioning set: a conditional over no mass is not 1.0
    and must not be reported as a pass (population vacuity guard).
    """
    era_set, band_set = set(eras), set(bands)
    denominator = sum(w for (_, era, _), w in joint.items() if era in era_set)
    if denominator <= 0.0:
        raise ValueError("no mass in the conditioning set — the conditional is undefined")
    numerator = sum(
        w for (_, era, band), w in joint.items() if era in era_set and band in band_set
    )
    return numerator / denominator


# ---------------------------------------------------------------------------
# The draw
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DrawnPremise:
    """One premise plus the two OBSERVATION-side facts a supplier would hold
    about it: how often its meter is read, and whether the register has a
    certificate for it (and how old)."""

    premise_id: str
    household: Household
    epc_band: str
    meter_cadence_days: int
    epc_lodged: dt.date | None

    @property
    def commodity(self) -> str:
        """The fuel whose register the supplier reads for heat."""
        return "gas" if self.household.heating_system in _GAS_SYSTEMS else "electricity"


def _boiler_age_for(era: BuildEra, heating: HeatingSystem) -> BoilerAge:
    if heating not in _GAS_SYSTEMS:
        return BoilerAge.NA
    return {
        BuildEra.PRE_1919: BoilerAge.OLD,
        BuildEra.ERA_1919_1944: BoilerAge.OLD,
        BuildEra.ERA_1945_1964: BoilerAge.MID,
        BuildEra.ERA_1965_1980: BoilerAge.MID,
        BuildEra.ERA_1981_2000: BoilerAge.NEW,
        BuildEra.POST_2000: BoilerAge.NEW,
    }[era]


def _draw_meter_cadence(premise_id: str, *, base_seed: int, as_of: dt.date) -> int:
    """How often the supplier actually reads this premise's register.

    OBSERVATION-side only: nothing here reaches the trace, so cadence cannot
    confound the truth it is used to estimate.
    """
    smart = smart_read_share(as_of.year)
    roll = _substream(base_seed, f"{premise_id}:cadence").random()
    if roll < smart:
        return DAILY_CADENCE_DAYS
    if roll < smart + (1.0 - smart) * _MONTHLY_SHARE_OF_TRADITIONAL:
        return MONTHLY_CADENCE_DAYS
    return QUARTERLY_CADENCE_DAYS


def _draw_epc_lodgement(premise_id: str, *, base_seed: int, as_of: dt.date) -> dt.date | None:
    """The register's certificate for this premise, or `None` where it has none.

    ABSENCE is one of the three EPC error sources C14 models, so it is drawn, not
    assigned to a hand-picked premise.
    """
    rng = _substream(base_seed, f"{premise_id}:epc")
    if rng.random() >= EPC_COVERAGE_SHARE:
        return None
    return as_of - dt.timedelta(days=rng.randrange(1, EPC_VALIDITY_YEARS * 365))


def draw_premise(
    premise_id: str,
    *,
    base_seed: int,
    as_of: dt.date,
    joint: Mapping[Cell, float] | None = None,
) -> DrawnPremise:
    """Draw ONE premise. Keyed on `premise_id`, so it is identical whatever else
    is in the population (C-S2) and whatever order the population is built in."""
    fitted = joint if joint is not None else raked_joint()
    ptype, era, band = _weighted_choice(
        _substream(base_seed, f"{premise_id}:cell"), fitted
    )
    heating = _weighted_choice(
        _substream(base_seed, f"{premise_id}:heating"), published_heating_weights()
    )
    bedrooms = _weighted_choice(
        _substream(base_seed, f"{premise_id}:bedrooms"),
        _BEDROOM_WEIGHTS_BY_PROPERTY_TYPE[ptype],
    )
    cadence = _draw_meter_cadence(premise_id, base_seed=base_seed, as_of=as_of)
    lodged = _draw_epc_lodgement(premise_id, base_seed=base_seed, as_of=as_of)

    letter = _BAND_TO_LETTER[band]
    insulation = _EPC_TO_INSULATION[letter]
    household = Household(
        customer_id=premise_id,
        property_type=ptype,
        build_era=era,
        epc_rating=letter,
        bedrooms=bedrooms,
        heating_system=heating,
        boiler_age=_boiler_age_for(era, heating),
        has_solar=False,
        solar_kwp=0.0,
        solar_install_year=None,
        has_battery=False,
        battery_kwh=0.0,
        has_ev=False,
        ev_charger_kw=0.0,
        has_smart_meter=cadence == DAILY_CADENCE_DAYS,
        smart_meter_install_year=as_of.year - 2 if cadence == DAILY_CADENCE_DAYS else None,
        insulation=insulation,
        has_driveway=ptype in (PropertyType.DETACHED, PropertyType.SEMI_DETACHED),
        roof_aspect="na" if ptype == PropertyType.FLAT else "east_west",
    )
    return DrawnPremise(
        premise_id=premise_id,
        household=household,
        epc_band=band,
        meter_cadence_days=cadence,
        epc_lodged=lodged,
    )


# --- The dwelling RECORD projection (B12) ----------------------------------
# `saas.property_model.build_properties()` builds the world's dwelling record for
# each resi electricity customer, and its contract is plain dicts in / plain dicts
# out ("no imports from sim/"), so a drawn premise reaches it through THIS
# projection rather than as a `DrawnPremise`. The vocabulary is the record's, which
# is the roster's -- the value set of `saas.property_model.
# PROPERTY_TYPE_BY_HOME_TYPE`, with `terraced` added because the four-home authored
# roster never had a terraced home and the published stock is 26% terraced.
#
# WHY THIS EXISTS AT ALL, stated so it is not mistaken for plumbing: before B12 a
# DRAWN home's dwelling record was `_derive_syn_property_fields()`, i.e. the
# SUPPLIER's own approximation of the home -- so the company's zero-knowledge modal
# guess ("D") scored 100% on the drawn cohort and 43% on the authored one, and the
# drawn cohort is the half that grows (WORKER_FINDING_THE_WORLDS_DWELLING_FOR_A_
# DRAWN_HOME_IS_THE_COMPANYS_OWN_ESTIMATE_2026-08-17). The world now draws the
# dwelling from the published EHS/ONS joint above, so the supplier's belief can be
# wrong, which is the point of the wall.
PROPERTY_TYPE_RECORD_NAME: dict[PropertyType, str] = {
    PropertyType.FLAT: "flat",
    PropertyType.TERRACED: "terraced",
    PropertyType.SEMI_DETACHED: "semi",
    PropertyType.DETACHED: "detached",
}


def dwelling_record(premise: DrawnPremise) -> dict:
    """The world's dwelling for ONE drawn home, in the property record's vocabulary.

    RAISES (never defaults) on a non-domestic property type: this draw is domestic
    and a commercial premise reaching here is a wiring defect, not a home to
    approximate.
    """
    household = premise.household
    if household.property_type not in PROPERTY_TYPE_RECORD_NAME:
        raise ValueError(
            f"{premise.premise_id}: {household.property_type} is not a domestic "
            "dwelling; the premise draw is domestic-only"
        )
    return {
        "property_type": PROPERTY_TYPE_RECORD_NAME[household.property_type],
        "epc_rating": household.epc_rating,
        "bedrooms": household.bedrooms,
    }


def draw_premise_population(
    n: int, *, base_seed: int, as_of: dt.date
) -> tuple[DrawnPremise, ...]:
    """Draw `n` premises. Growing `n` APPENDS — `P0007` never changes."""
    if n <= 0:
        raise ValueError(f"a population needs at least one premise, got {n}")
    fitted = raked_joint()
    return tuple(
        draw_premise(f"P{i:04d}", base_seed=base_seed, as_of=as_of, joint=fitted)
        for i in range(n)
    )


# ---------------------------------------------------------------------------
# The controls, as functions so the tool and the tests judge the SAME numbers.
# ---------------------------------------------------------------------------
def observed_shares(population: Sequence[DrawnPremise]) -> dict[str, dict]:
    """The three drawn marginals, plus the ORACLE conditional. Reported as
    fractions of the drawn population."""
    if not population:
        raise ValueError("cannot measure the shares of an empty population")
    n = float(len(population))
    types: dict[PropertyType, float] = {}
    eras: dict[BuildEra, float] = {}
    bands: dict[str, float] = {}
    for premise in population:
        types[premise.household.property_type] = types.get(premise.household.property_type, 0.0) + 1 / n
        eras[premise.household.build_era] = eras.get(premise.household.build_era, 0.0) + 1 / n
        bands[premise.epc_band] = bands.get(premise.epc_band, 0.0) + 1 / n
    old = [p for p in population if p.household.build_era in OLD_STOCK_ERAS]
    return {
        "property_type": types,
        "build_era": eras,
        "epc_band": bands,
        "old_stock_share_in_bands_d_to_g": (
            sum(1 for p in old if p.epc_band in BANDS_D_TO_G) / len(old) if old else None
        ),
        "old_stock_n": len(old),
    }


def published_marginal_recovery(population: Sequence[DrawnPremise]) -> dict[str, float]:
    """Worst absolute departure of each drawn marginal from its published target,
    in percentage points of the population. A DIAGNOSTIC (R12), not a target."""
    observed = observed_shares(population)
    return {
        "property_type": max(
            abs(observed["property_type"].get(k, 0.0) - v)
            for k, v in PUBLISHED_PROPERTY_TYPE_SHARE.items()
        ),
        "build_era": max(
            abs(observed["build_era"].get(k, 0.0) - v)
            for k, v in PUBLISHED_BUILD_ERA_SHARE.items()
        ),
        "epc_band": max(
            abs(observed["epc_band"].get(k, 0.0) - v)
            for k, v in PUBLISHED_EPC_BAND_SHARE.items()
        ),
    }


def distinct_cells(population: Sequence[DrawnPremise]) -> int:
    """How many distinct (property type, era, band) cells the population occupies.

    THE CLONE DETECTOR. This exists because the recorded blocker was a population
    of identical `suburban_semi` homes: a draw that silently degenerates to one
    cell would still produce a gap number, and that number would read as a
    population result.
    """
    return len({(p.household.property_type, p.household.build_era, p.epc_band) for p in population})


# ===========================================================================
# PB1 — the proposed population target, and what AO12 MEASURED it costs
# ===========================================================================
#
# PURPOSE. Deliverable 1 of DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11:
# a proposed premise-population target with the AO12 probe's measured cost beside
# it. The ruling's own governor is the point — *"if the probe says the scale is
# unaffordable on current storage, that is the answer"* — so this module must be
# able to return NO.
#
# GUARANTEE. Every cost below is READ from AO12's report artefact. Nothing here
# re-derives a per-unit constant, and nothing asserts one as a literal. Change the
# report and these numbers change; delete the report and every function here
# REFUSES rather than falling back to a default (a fallback is the fail-open shape
# R15 names — an unavailable measurement is a FAILED measurement, not a cheap one).
#
# WHY IT LIVES HERE. `PROPOSED_PREMISE_POPULATION` is a PROPOSAL, not a raise.
# `draw_premise_population`'s callers are untouched and no live path reads it: the
# population a run actually draws is a CURRICULUM instrument and moving it is the
# director's act, never a build side effect (R13). This module proposes and prices;
# it does not spend.
#
# THE FINDING THIS ENCODES. The population and the BOOK have different price lists,
# and conflating them is the error the ruling's ordering invites. Drawing premises
# is cheap and MEASURED to fit. Settling customers is 3 orders of magnitude dearer
# per head and does NOT fit. So the world can grow now; the book cannot, and the
# thing that unblocks it is the storage work, not a bigger number here.

SCALE_PROBE_REPORT_PATH = (
    Path(__file__).resolve().parents[1] / "docs" / "observability" / "scale_probe_10k" / "report.json"
)

#: The proposal. Reasoning in `docs/design/PB1_POPULATION_TARGET_AND_ITS_PRICE.md`;
#: its price is not written here because it is read from the probe (see above).
PROPOSED_PREMISE_POPULATION = 100_000

# AO12's own three-valued vocabulary, reused rather than reinvented so a reader can
# put this file and `report.json` side by side.
MEASURED = "measured"
LOWER_BOUND = "lower_bound"
UNKNOWN = "unknown"

FITS = "FITS"
DOES_NOT_FIT = "DOES_NOT_FIT"
UNDECIDED = "UNDECIDED"


class ScaleProbeUnavailable(RuntimeError):
    """The price list could not be read. Raised instead of returning a default.

    An unavailable check is a FAILED check (R15, fail-silent). Every caller of the
    pricing functions is asking "can we afford this?", and the one answer that must
    never be produced by a missing file is "yes".
    """


@dataclass(frozen=True)
class StagePrice:
    """One stage's measured cost, transcribed from `report.json`.

    `peak_rss_bytes`, `wall_s` and `output_bytes` are the three figures the ruling
    asks to see beside the target, and they are stored exactly as the probe wrote
    them — `output_bytes` stays None where the stage produced no output rather than
    becoming a 0 that would read as "free".
    """

    stage: str
    status: str
    kind: str
    unit: str
    units_completed: int
    peak_rss_bytes: int | None
    baseline_rss_bytes: int | None
    wall_s: float | None
    output_bytes: int | None
    per_unit: Mapping[str, float]
    omissions: tuple[str, ...]

    @property
    def is_floor(self) -> bool:
        """A floor can only move UP, so it can never come back FITS."""
        return self.kind == LOWER_BOUND


def load_scale_probe_report(path: Path | None = None) -> dict:
    """Read AO12's report, or REFUSE. Never returns a partial or defaulted report."""
    report_path = Path(path) if path is not None else SCALE_PROBE_REPORT_PATH
    try:
        raw = report_path.read_text()
    except OSError as exc:
        raise ScaleProbeUnavailable(
            f"AO12 scale-probe report unreadable at {report_path}: {exc}. The population "
            "target cannot be priced without it, and an unpriced target is exactly what "
            "DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11 forbids."
        ) from exc
    try:
        report = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ScaleProbeUnavailable(f"AO12 report at {report_path} is not valid JSON: {exc}") from exc
    if not isinstance(report, dict) or not report.get("stages"):
        raise ScaleProbeUnavailable(f"AO12 report at {report_path} carries no stages")
    return report


def stage_prices(report: Mapping) -> dict[str, StagePrice]:
    """Transcribe every stage, deciding MEASURED / LOWER_BOUND / UNKNOWN.

    The three-valued kind is the load-bearing part. A stage degrades to a floor when
    it did not complete, when it declared an omission, or when a per-unit cost came
    out at the instrument's resolution floor — all three mean "at least this much",
    and AO12's own §2.4 rule is that such a stage can never come back FITS.
    """
    prices: dict[str, StagePrice] = {}
    for stage in report.get("stages", []):
        name = stage.get("stage")
        if not name:
            continue
        omissions = tuple(
            o if isinstance(o, str) else str(o.get("what", o)) for o in (stage.get("unmeasured") or [])
        )
        per_unit = stage.get("per_unit") or {}
        projection = stage.get("projection") or {}
        status = stage.get("status") or UNKNOWN
        if not projection or stage.get("peak_rss_bytes") is None:
            kind = UNKNOWN
        elif status != MEASURED or omissions or (stage.get("below_resolution") or []):
            kind = LOWER_BOUND
        else:
            kind = MEASURED
        prices[name] = StagePrice(
            stage=name,
            status=status,
            kind=kind,
            unit=stage.get("unit") or "unit",
            units_completed=stage.get("units_completed") or 0,
            peak_rss_bytes=stage.get("peak_rss_bytes"),
            baseline_rss_bytes=stage.get("baseline_rss_bytes"),
            wall_s=stage.get("wall_s"),
            output_bytes=stage.get("output_bytes"),
            per_unit=dict(per_unit),
            omissions=omissions,
        )
    return prices


def _require(prices: Mapping[str, StagePrice], stage: str) -> StagePrice:
    price = prices.get(stage)
    if price is None:
        raise ScaleProbeUnavailable(
            f"AO12 report has no `{stage}` stage. A stage the probe never reached is an "
            "UNKNOWN cost, not a zero — refusing rather than pricing it at nothing."
        )
    if price.kind == UNKNOWN:
        raise ScaleProbeUnavailable(
            f"AO12 stage `{stage}` is UNKNOWN (status={price.status!r}): it produced no "
            "projection, so it has no price. Substituting 0 here is the fail-open shape "
            "this refusal exists to prevent."
        )
    return price


def projected_population_rss_bytes(n: int, prices: Mapping[str, StagePrice]) -> float:
    """What drawing `n` premises is projected to hold, by AO12's own method.

    The method is the report's, quoted from its `reading_note`: per-unit constants
    measured before the stage stopped, times the target size — plus the stage's
    baseline, which is why this is not simply `per_unit * n`.
    """
    price = _require(prices, "population_draw")
    per_unit = price.per_unit.get("rss_bytes")
    if per_unit is None:
        raise ScaleProbeUnavailable("population_draw has no per-unit RSS cost to project from")
    return float(price.baseline_rss_bytes or 0) + per_unit * n


def population_affordability(
    n: int = PROPOSED_PREMISE_POPULATION,
    *,
    report: Mapping | None = None,
    budget_bytes: float | None = None,
) -> dict:
    """COMPUTE — never judge — whether a population of `n` fits.

    Returns FITS only when the pricing stage is MEASURED and the projection sits
    under budget. A floor under budget is UNDECIDED, not FITS: the omitted work can
    only add.
    """
    report = load_scale_probe_report() if report is None else report
    prices = stage_prices(report)
    price = _require(prices, "population_draw")
    budget = float(budget_bytes if budget_bytes is not None else report["box"]["budgets"]["rss_bytes"])
    projected = projected_population_rss_bytes(n, prices)
    if projected >= budget:
        verdict = DOES_NOT_FIT
    elif price.is_floor:
        verdict = UNDECIDED
    else:
        verdict = FITS
    return {
        "n": n,
        "verdict": verdict,
        "projected_rss_bytes": projected,
        "budget_rss_bytes": budget,
        "pressure": projected / budget,
        "priced_by": price.stage,
        "kind": price.kind,
        "measured_peak_rss_bytes": price.peak_rss_bytes,
        "measured_wall_s": price.wall_s,
        "measured_output_bytes": price.output_bytes,
        "measured_units": price.units_completed,
        "omissions": price.omissions,
    }


def settlement_records_per_customer_year(report: Mapping) -> float:
    """Read the record count per customer-year out of the report's own target.

    Computed from the record rather than written down as 17,520, so a probe re-run
    at a different horizon moves this instead of silently disagreeing with it.
    """
    customers = (report.get("target") or {}).get("customers")
    stage = next((s for s in report.get("stages", []) if s.get("stage") == "settlement_build"), None)
    if not customers or stage is None or not stage.get("target_units"):
        raise ScaleProbeUnavailable(
            "cannot read records-per-customer-year: the report lacks a settlement_build "
            "target or a customer count"
        )
    return float(stage["target_units"]) / float(customers)


def settled_book_ceiling(
    *, report: Mapping | None = None, years: int = 1, budget_bytes: float | None = None
) -> dict:
    """The UPPER BOUND on customers the settlement path can hold — the expensive half.

    Why the two stages are ADDED rather than maxed: in `tools/scale_probe_10k.py`
    the serialization stage takes its baseline AFTER `run_settlement` has returned,
    so its 411 B/record is measured while the settlement working set is still held.
    A single-process build-then-serialize therefore pays both.

    Both inputs are FLOORS (settlement died at its ceiling and its own detail records
    the per-unit cost as under-stated; serialization declares the reduction omitted),
    so the customer count returned is a CEILING: the true affordable book is smaller,
    never larger. That direction is deliberate — a bound that can only be optimistic
    is the one shape a cost governor must not have.
    """
    report = load_scale_probe_report() if report is None else report
    prices = stage_prices(report)
    settlement = _require(prices, "settlement_build")
    serialization = _require(prices, "run_output_serialization")
    budget = float(budget_bytes if budget_bytes is not None else report["box"]["budgets"]["rss_bytes"])
    per_record = float(settlement.per_unit["rss_bytes"]) + float(serialization.per_unit["rss_bytes"])
    per_customer = per_record * settlement_records_per_customer_year(report) * years
    return {
        "max_customers": int(math.floor(budget / per_customer)),
        "bound_kind": "upper_bound",
        "years": years,
        "bytes_per_record": per_record,
        "bytes_per_customer_year": per_customer,
        "budget_rss_bytes": budget,
        "contributing_stages": (settlement.stage, serialization.stage),
        "both_are_floors": settlement.is_floor and serialization.is_floor,
    }
