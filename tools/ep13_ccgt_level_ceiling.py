"""EP13: THE BALANCED GAS-LEVEL CEILING — what perfect knowledge of the DAILY gas level is worth
when the energy it moves has to go somewhere.

REUSE: tools/ep13_ccgt_level_ceiling.py
CLASS: CUSTOM
INDEX: searched "ccgt level", "energy balance", "residual re-decided", "daily gas", "ceiling",
       "merit order". Six EP13 bounds match "ceiling" and the near neighbour is
       `tools/ep13_ccgt_swap_ceiling.py`, whose `ccgt_level` rung is the thing this exists to
       REPAIR rather than to re-run: that rung overrides the gas term and leaves `above_ccgt_mw`
       computed from the fleet CAPACITY, so gas + coal + peaker stops summing to the thermal
       residual and the half hour is met by more or less energy than its demand. §15 of the frame
       doc says so in its own words and declines to quote the number because of it. Merging the two
       was rejected: the swap ceiling's every rung is day-total preserving and its whole reading
       depends on that, so adding a mode that moves the day total would put two different
       conservation laws behind one artefact's controls. `normalise`, `within_day_correlation`,
       `_pearson` and `level_swap` are IMPORTED from it rather than re-typed, and `day_mean` /
       `held_out` / `per_fuel_by_period` from the per-fuel oracle, so the six EP13 bounds stay
       readable in one table. `ceiling_is_unreachable_from` is deliberately NOT imported and the
       first draft's import of it was a defect -- see that function's own docstring.

WHY THIS EXISTS
---------------
§15 retired the fifth candidate — a publishable proxy for within-day CCGT dispatch, capped at
+0.0485 — and named the next hypothesis: THE DAILY AND SEASONAL LEVEL OF GAS, worth +0.116 in 2024
on `ccgt_level`. It named two things owed before that could be a target, and the first is this:

    a proper ceiling on it, with the residual re-decided so the energy balance holds

**`ccgt_level` is not a bound and §15 is explicit that it is not.** It moves the daily gas total
without re-deciding the residual's other terms, so part of what it reports is that disturbance. The
largest number this atom has produced on a live axis is therefore one nobody can attribute — and an
unattributable number can neither promote a build target nor retire one. That is the hole.

WHAT "RE-DECIDED" MEANS, AND WHY IT IS STILL ONE VARIABLE
---------------------------------------------------------
The shipped merit order derives a thermal residual from observables and then splits it::

    thermal_mw   = demand - renewables - imports - must_run      <- the energy-balance anchor
    implied_ccgt = min(thermal_mw, CCGT_CAPACITY_MW)
    above_ccgt   = max(0, thermal_mw - CCGT_CAPACITY_MW)
    coal         = min(above_ccgt, coal_capacity_for_the_year)
    peaker       = above_ccgt - coal, capped at PEAKER_HEADROOM_MW

This module re-splits that same dispatch around the imposed gas: coal and the peaker band take what
gas no longer serves, at their SHIPPED factors, rather than the energy vanishing::

    served_baseline = implied_ccgt + coal_base + peaker_base     <- the conservation anchor
    ccgt            = the imposed level, clamped to the fleet
    remaining       = served_baseline - ccgt
    coal            = min(remaining, coal_capacity_for_the_year)
    peaker          = min(remaining - coal, PEAKER_HEADROOM_MW)

**That is one intervention, not two.** The substituted quantity is the gas level; the coal/peaker
re-decision is not a second choice but the arithmetic that makes the first one conserve energy.
With no override it reduces to the shipped dispatch exactly, which is what lets the
re-implementation control below hold this file to `gci.build_shape` to floating point.

THE ANCHOR IS `served_baseline`, NOT `thermal_mw`, AND THE FIRST DRAFT HAD IT WRONG
-----------------------------------------------------------------------------------
The obvious reading of §15's instruction — *the residual re-decided so the energy balance holds* —
is ``gas + coal + peaker == thermal_mw``. **The SHIPPED model does not satisfy that**, and a
four-line smoke test at real inputs refuted it before this instrument was ever run: whenever
`thermal_mw` exceeds the CCGT fleet (30,000 MW) plus the peaker headroom (7,000 MW), the shipped
stack truncates its own residual and serves less energy than it demanded. At demand 50,000 MW with
3,000 MW of renewables the baseline is 2,000 MW short of its own residual, with no override
anywhere near it.

Conserving against a quantity the baseline itself violates would have reported the **shipped
model's truncation** as this substitution's imbalance, in every high-demand half hour, and the
control would have gone red for the world rather than for the instrument. The anchor is therefore
what the shipped stack actually DISPATCHES. The truncation is real and is counted separately as
`baseline_could_not_meet_its_own_residual` — a fact about the reconstruction, reported and not
corrected here, because correcting it would be a different pass changing a different thing.

THE UNBALANCED RUNG IS KEPT BESIDE IT ON PURPOSE
-------------------------------------------------
`level_unbalanced` reproduces §15's `ccgt_level` arithmetic in this same process, on this same
population, so the difference between the two rungs is the DISTURBANCE, MEASURED. Deleting it and
publishing only the balanced number would leave the +0.116 standing in the record with nothing to
read it against, and would make this pass an assertion that the disturbance mattered rather than a
measurement of how much.

  * `level_balanced`   truth's day mean + the model's own within-day deviations, residual
                       re-decided. **THE CEILING.** Perfect knowledge of the exact quantity a proxy
                       would approximate, everything else the shipped arithmetic, energy conserved.
                       Intended so a negative would RETIRE the candidate — and MEASURED, it cannot:
                       its own cap control refuses all six years, so it retires nothing.
  * `level_unbalanced` the identical override through §15's `above_ccgt` line. NOT A BOUND. Present
                       only as the subtrahend that sizes the disturbance.
  * `level_identity`   the model's OWN day mean + its OWN within-day deviations — algebraically the
                       model's own series. Must score the baseline exactly. THE SOUNDNESS CHECK:
                       if this gains, the rungs measure the act of substituting.
  * `level_shuffled`   truth's DAY MEANS dealt to the WRONG days. **THE NULL.** Every value and the
                       whole substitution machinery preserved; only the day a level belongs to is
                       destroyed.

THE CEILING IS ASYMMETRIC, WHICH A READER MUST KNOW BEFORE READING ANY YEAR OF IT
----------------------------------------------------------------------------------
Conserving energy means gas can only be raised as far as coal and the peakers were actually
running: `served_baseline - implied_ccgt` is the whole headroom, and in a half hour where the
residual sits below the CCGT fleet that headroom is **zero**. So the instrument can express a
downward correction to the gas level freely and an upward one only where dirtier plant was on.

This is not a defect to be patched — raising gas above what the stack served would have to
manufacture energy — but it is what defeats the instrument, and MEASURED IT DEFEATS IT EVERYWHERE.

**THE CAP BINDS ON 53%-85% OF SCORED HALF HOURS IN EVERY YEAR, SO NO YEAR HAS A READABLE RESULT.**
`the_caps_are_not_carrying_the_rung` is RED in all six. The mechanism is arithmetic rather than
bad luck: where the residual sits below the CCGT fleet, `served_baseline` IS the model's own implied
gas, so the cap fires on every half hour of every day whose true gas level runs above the model's —
roughly half of them by construction, and far more in the years §15 measured the model running LOW
(13% in 2019, where the cap binds on 83%).

**THE NUMBERS IN `years` ARE THEREFORE NOT A CEILING ON THE GAS LEVEL AND MUST NOT BE QUOTED AS
ONE.** A rung pinned to the baseline on most of its population is measuring the pin. The negative
gains are what that pin costs, not what the level is worth. The absence of a reading IS this
instrument's result, and the gap it leaves is not to be filled by quoting `level_unbalanced`
instead — that is the unattributable number this pass existed to replace.

THE CAPS ARE COUNTED, NOT ASSUMED HARMLESS. Imposed gas above what the shipped stack served is
clamped down to it; a shortfall exceeding coal capacity plus the peaker headroom is unservable and
leaves a negative balance. Both are counted per year and published, because a rung whose caps bind
often is partly measuring the caps. Past `MAX_BOUND_SHARE` its reading is refused rather than
footnoted.

FAIL CLOSED ON AN ABSENT GAS READING, carried forward from §14 rather than re-learned. A half hour
with no CCGT row is not a half hour with no gas; it is no reading. Such half hours are refused from
EVERY rung including the baseline, so all five score the identical population and no part of any
gain is a coverage difference.

R12. Every number here is a DIAGNOSTIC. Nothing in this file moves a level, changes an exit test, or
is read by the published feed — `ceiling_reaches_the_published_feed` is an AST walk over
`tools/generate_grid_intensity_feed.py`, not a promise. The series it holds is metered half-hourly
gas, the largest emissions term on the system; publishing from it would make the reconstruction
NESO's arithmetic with a different cache.

Reproduce: `python3 -m tools.ep13_ccgt_level_ceiling`
        -> `docs/observability/ep13_ccgt_level_ceiling.json`.

Preregistration: `docs/staging/done/WORKER_PREREGISTRATION_WHAT_THE_BALANCED_GAS_LEVEL_CEILING_MUST_SHOW_2026-09-03.md`.
"""

from __future__ import annotations

import ast
import json
import random
from pathlib import Path
from typing import Mapping, Sequence

from sim import grid_carbon_intensity as gci
from sim import neso_carbon_intensity as neso
from tools.ep13_ccgt_swap_ceiling import (
    _pearson,
    level_swap,
    normalise,
    within_day_correlation,
)
from tools.ep13_per_fuel_oracle_bound import day_mean, held_out, per_fuel_by_period

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_DIR / "docs" / "observability" / "ep13_ccgt_level_ceiling.json"

#: The one fuel this instrument substitutes. Named rather than parameterised, for §15's reason: the
#: ablation ladder of §14 already answered "which fuel", and a knob here would invite re-running
#: until a fuel scores.
SWAPPED_FUEL = "CCGT"

#: The peaker band's headroom, derived from the shipped constants rather than restated. This is the
#: quantity that decides whether a shortfall is servable, so a second hand-typed 7000 here would be
#: a constant that silently stops tracking the fleet it describes.
PEAKER_HEADROOM_MW = max(
    0.0, gci.TOTAL_DISPATCHABLE_MW - gci.MUST_RUN_FLOOR_MW - gci.CCGT_CAPACITY_MW
)

#: The shuffle seed for the null rung. Fixed so the null is reproducible; its job is to collapse.
NULL_SEED = 20260903

#: A year needs this many scored half hours before it is measured at all. The same bar and the same
#: reason as the five EP13 bounds before it -- roughly two weeks.
MIN_SCORED_HALF_HOURS = 600

#: The re-implementation must reproduce `gci.build_shape` on the same population to better than
#: this. NOT a tolerance on "close": with no override it is the same arithmetic on the same inputs,
#: so the only thing between the two is float association order.
MAX_REIMPLEMENTATION_DRIFT = 1e-12

#: The balanced rung's energy balance is an IDENTITY, not a tolerance. `gas + coal + peaker -
#: thermal_mw` is zero by construction wherever no cap binds; this bar exists only to absorb float
#: association order, and is six orders of magnitude below the smallest MW quantity in the model.
MAX_BALANCE_RESIDUAL_MW = 1e-6

#: How much a rung must beat the baseline by before that counts as a gain. Not a strict inequality,
#: for `ep13_peer_bound`'s reason: a control comparing two quantities its own named defect makes
#: IDENTICAL reads 1e-16 of floating point as an advantage and passes fail-open.
MIN_MATERIAL_GAIN = 0.01

#: The correct day means must clear SCRAMBLED day means by this, or the rungs are not measuring the
#: level. An order of magnitude below what a real signal would show, so the bar does not carry the
#: result.
MIN_NULL_DISCRIMINATION = 0.05

#: The identity rung reproduces the model's own series algebraically, so its gain is zero up to
#: float association order. A bar rather than an exact equality because the deviations are added and
#: subtracted through a day mean.
MAX_IDENTITY_GAIN = 0.001

#: The substituted series must actually differ from the model's own, or a zero gain is
#: uninterpretable -- equally consistent with "the level is worth nothing" and with "the
#: substitution was a no-op". Mean absolute DAY-MEAN difference, MW.
MIN_SUBSTITUTION_DISTANCE_MW = 100.0

#: Above this share of half hours with a cap binding, the balanced rung is partly measuring the caps
#: rather than the level, and its reading is refused rather than footnoted.
MAX_BOUND_SHARE = 0.25


def dispatch_rate(
    demand_mw: float,
    renewable_generation_mw: float,
    year: int,
    *,
    import_mw: float = 0.0,
    import_rate_t_per_mwh: float = 0.0,
    coal_capacity_mw: float = 0.0,
    thermal_floor_mw: float = 0.0,
    zero_carbon_must_run_mw: float | None = None,
    biomass_capacity_mw: float | None = None,
    biomass_floor_mw: float | None = None,
    ccgt_mw_override: float | None = None,
    balanced: bool = True,
) -> tuple[float, float, float, dict[str, bool]]:
    """`gci.emissions_rate_t_per_mwh`, line for line, with ONE override point and ONE moved boundary.

    Returns `(rate, implied_ccgt_mw, balance_mw, caps)` -- the rate, the gas dispatch the shipped
    merit order DECIDED for this half hour (the quantity a proxy would replace, which the shipped
    function does not expose), the energy-balance residual `gas + coal + peaker - thermal_mw`, and
    which caps bound.

    `balanced=True` moves the CCGT/coal boundary to the imposed gas so the residual is re-decided
    around it; `balanced=False` is §15's line, kept so the disturbance can be measured rather than
    asserted. **With no override the two are identical and both equal the shipped arithmetic**,
    because `max(0, thermal - min(thermal, CAP))` is `max(0, thermal - CAP)`.

    WHY THIS IS A COPY AND NOT A CALL, which is §15's reason unchanged: the shipped function returns
    one float and takes no override, and widening its signature to accept a half-hourly gas series
    would put a route to the metered mix inside `sim/` -- the one thing `sim/elexon_fuel_outturn.py`
    draws its line to prevent.
    """
    y = gci._year_of(int(year))
    worst_eff, best_eff = gci._ccgt_efficiency_band(y)
    demand_mw = float(demand_mw)
    if demand_mw <= 0.0:
        raise gci.ShapeUnavailable("a half hour with no demand has no emissions rate")

    import_mw = min(max(0.0, float(import_mw)), demand_mw)
    residual_mw = demand_mw - float(renewable_generation_mw) - import_mw
    zero_carbon_mw = (
        gci.MUST_RUN_ZERO_CARBON_MW
        if zero_carbon_must_run_mw is None
        else max(0.0, float(zero_carbon_must_run_mw))
    )
    biomass_capacity = (
        gci.MUST_RUN_BIOMASS_MW
        if biomass_capacity_mw is None
        else max(0.0, float(biomass_capacity_mw))
    )
    biomass_floor = (
        biomass_capacity
        if biomass_floor_mw is None
        else min(max(0.0, float(biomass_floor_mw)), biomass_capacity)
    )
    biomass_mw = min(max(residual_mw - zero_carbon_mw, biomass_floor), biomass_capacity)

    must_run_capacity_mw = biomass_mw + zero_carbon_mw
    must_run_mw = min(demand_mw, must_run_capacity_mw)
    thermal_mw = max(0.0, residual_mw - must_run_capacity_mw)
    floor_mw = min(max(0.0, float(thermal_floor_mw)), max(0.0, demand_mw - must_run_mw))
    thermal_mw = max(thermal_mw, floor_mw)

    # THE SHIPPED DISPATCH, COMPUTED FIRST AND UNCONDITIONALLY, because it is the conservation
    # anchor and not merely the no-override case.
    implied_ccgt_mw = min(thermal_mw, gci.CCGT_CAPACITY_MW)
    above_base_mw = max(0.0, thermal_mw - gci.CCGT_CAPACITY_MW)
    coal_base_mw = min(above_base_mw, max(0.0, float(coal_capacity_mw)))
    peaker_base_mw = min(max(0.0, above_base_mw - coal_base_mw), PEAKER_HEADROOM_MW)
    served_baseline_mw = implied_ccgt_mw + coal_base_mw + peaker_base_mw

    ccgt_mw, coal_mw, peaker_mw = implied_ccgt_mw, coal_base_mw, peaker_base_mw
    caps = {"clamped_low": False, "clamped_high": False, "capped_to_served": False}
    if ccgt_mw_override is not None:
        raw = float(ccgt_mw_override)
        caps["clamped_low"] = raw < 0.0
        caps["clamped_high"] = raw > gci.CCGT_CAPACITY_MW
        ccgt_mw = min(max(0.0, raw), gci.CCGT_CAPACITY_MW)
        if balanced:
            # THE ANCHOR IS WHAT THE SHIPPED STACK DISPATCHES, NOT `thermal_mw`. The first draft of
            # this file conserved against the residual and a four-line smoke test at real inputs
            # refuted it before it ran: the SHIPPED model already fails that identity whenever
            # `thermal_mw` exceeds the CCGT fleet plus the peaker headroom, because it truncates its
            # own residual and serves less energy than it demanded. Conserving against a quantity
            # the baseline itself violates would have reported the shipped model's truncation as
            # this substitution's imbalance, in every high-demand half hour.
            if ccgt_mw > served_baseline_mw:
                caps["capped_to_served"] = True
                ccgt_mw = served_baseline_mw
            remaining_mw = served_baseline_mw - ccgt_mw
            coal_mw = min(remaining_mw, max(0.0, float(coal_capacity_mw)))
            peaker_mw = min(max(0.0, remaining_mw - coal_mw), PEAKER_HEADROOM_MW)
        # UNBALANCED IS §15's LINE UNCHANGED: coal and the peakers stay decided from the fleet
        # CAPACITY, so they do not move when gas does. Reproducing it exactly is the whole point of
        # keeping this rung -- it is the subtrahend that sizes the disturbance.

    load_fraction = (ccgt_mw / gci.CCGT_CAPACITY_MW) if gci.CCGT_CAPACITY_MW > 0 else 0.0
    mean_dispatched_eff = best_eff - (best_eff - worst_eff) * load_fraction / 2.0

    biomass_served_mw = (
        biomass_mw * (must_run_mw / must_run_capacity_mw) if must_run_capacity_mw > 0.0 else 0.0
    )
    tonnes = (
        biomass_served_mw * (gci.BIOMASS_G_CO2_PER_KWH / 1000.0)
        + import_mw * max(0.0, float(import_rate_t_per_mwh))
        + ccgt_mw * (gci.EF_GAS_TCO2_PER_MWH_TH / mean_dispatched_eff)
        + coal_mw * gci.EF_COAL_TCO2_PER_MWH_E_BY_YEAR[y]
        + peaker_mw * (gci.EF_GAS_TCO2_PER_MWH_TH / gci.OCGT_REFERENCE_EFFICIENCY)
    )
    # THE CONSERVATION STATEMENT: the substitution moved WHICH units ran, not HOW MUCH energy ran.
    # Zero for the baseline by construction, zero for the balanced rung wherever no cap binds, and
    # exactly `ccgt_mw - implied_ccgt_mw` for the unbalanced one -- which is the defect, in MW.
    balance_mw = ccgt_mw + coal_mw + peaker_mw - served_baseline_mw
    # FLAGGED HERE AND NOT ONLY COUNTED IN THE LOOP. Pushing gas far enough down exhausts coal
    # capacity plus the peaker headroom and the shortfall becomes unservable -- so the balanced rung
    # does NOT conserve in that half hour, and a caller that could not see it would read a genuine
    # imbalance as a clean measurement. It does not fire anywhere on the real population; it fires
    # on large synthetic cuts, which is how the control battery reaches it.
    caps["unservable"] = balance_mw < -MAX_BALANCE_RESIDUAL_MW
    # REPORTED, NOT CORRECTED, and it is a fact about the SHIPPED model rather than about any
    # substitution here: when `thermal_mw` exceeds the CCGT fleet plus the peaker headroom the
    # shipped stack cannot meet its own residual and serves less than it demanded.
    caps["baseline_unserved_mw"] = thermal_mw - served_baseline_mw  # type: ignore[assignment]
    return tonnes / demand_mw, implied_ccgt_mw, balance_mw, caps


def build_rates(
    demand_by_period: Mapping[tuple[str, int], float],
    renewables_by_period: Mapping[tuple[str, int], float],
    *,
    imports_by_period: Mapping[tuple[str, int], tuple[float, float]] | None = None,
    coal_capacity_by_year: Mapping[int, float] | None = None,
    thermal_floor_by_year: Mapping[int, float] | None = None,
    zero_carbon_must_run_by_period: Mapping[tuple[str, int], float] | None = None,
    biomass_envelope_by_year: Mapping[int, Mapping[str, float]] | None = None,
    ccgt_override_by_period: Mapping[tuple[str, int], float] | None = None,
    balanced: bool = True,
    only_keys: Sequence[tuple[str, int]] | None = None,
) -> tuple[
    dict[tuple[str, int], float],
    dict[tuple[str, int], float],
    dict[tuple[str, int], float],
    dict[str, int],
    dict[tuple[str, int], bool],
]:
    """`gci.build_shape`'s loop, stopping at the RATES, and carrying the balance residual out.

    Returns `(rates, implied_ccgt_mw, balance_mw, cap counts, bound-by-key)`. Rates rather than the shape because
    the normalisation is per calendar year over whatever keys survived, so comparing rates is what
    makes `reimplementation_reproduces_the_shipped_shape` a statement about the arithmetic.
    """
    keys = list(only_keys) if only_keys is not None else list(demand_by_period)
    rates: dict[tuple[str, int], float] = {}
    implied: dict[tuple[str, int], float] = {}
    balance: dict[tuple[str, int], float] = {}
    bound_by_key: dict[tuple[str, int], bool] = {}
    caps = {
        "clamped_low": 0,
        "clamped_high": 0,
        "capped_to_served": 0,
        "unservable": 0,
        "baseline_could_not_meet_its_own_residual": 0,
    }
    for key in keys:
        demand_mw = demand_by_period.get(key)
        renewable_mw = renewables_by_period.get(key)
        if renewable_mw is None or not demand_mw or float(demand_mw) <= 0.0:
            continue
        year = int(key[0][:4])
        import_mw, import_rate = (imports_by_period or {}).get(key, (0.0, 0.0))
        envelope = (biomass_envelope_by_year or {}).get(year)
        zero_carbon_mw = (zero_carbon_must_run_by_period or {}).get(key)
        override = None if ccgt_override_by_period is None else ccgt_override_by_period.get(key)
        # AN ABSENT OVERRIDE IS A REFUSAL, NOT A FALLBACK TO THE MODEL'S OWN GAS -- §14's fail-open
        # shape, one layer over. Falling back would mix baseline half hours into a swap rung and
        # dilute the very gain being measured.
        if ccgt_override_by_period is not None and override is None:
            continue
        try:
            rate, implied_ccgt, balance_mw, cap = dispatch_rate(
                float(demand_mw),
                float(renewable_mw),
                year,
                import_mw=float(import_mw),
                import_rate_t_per_mwh=float(import_rate),
                coal_capacity_mw=float((coal_capacity_by_year or {}).get(year, 0.0)),
                thermal_floor_mw=float((thermal_floor_by_year or {}).get(year, 0.0)),
                zero_carbon_must_run_mw=(None if zero_carbon_mw is None else float(zero_carbon_mw)),
                biomass_capacity_mw=(None if envelope is None else float(envelope["capacity_mw"])),
                biomass_floor_mw=(None if envelope is None else float(envelope["floor_mw"])),
                ccgt_mw_override=(None if override is None else float(override)),
                balanced=balanced,
            )
        except (gci.ShapeUnavailable, ValueError, KeyError):
            continue
        rates[key] = rate
        implied[key] = implied_ccgt
        balance[key] = balance_mw
        for name in ("clamped_low", "clamped_high", "capped_to_served", "unservable"):
            caps[name] += int(bool(cap[name]))
        if float(cap["baseline_unserved_mw"]) > MAX_BALANCE_RESIDUAL_MW:
            caps["baseline_could_not_meet_its_own_residual"] += 1
        # PER KEY AS WELL AS IN TOTAL. The run-wide counts alone are unreadable as a control: they
        # span every year the caches cover, so a year whose caps bind on every half hour is
        # indistinguishable from one where they never do. `measure_year` needs the per-key view to
        # compute a share on the half hours it actually scored.
        bound_by_key[key] = any(
            bool(cap[name])
            for name in ("clamped_low", "clamped_high", "capped_to_served", "unservable")
        )
    return rates, implied, balance, caps, bound_by_key


def shuffled_day_levels(
    implied: Mapping[tuple[str, int], float],
    truth: Mapping[tuple[str, int], float],
    seed: int = NULL_SEED,
) -> dict[tuple[str, int], float]:
    """`level_swap` with truth's DAY MEANS dealt to the wrong days — THE NULL.

    The exact analogue of §15's null one axis over: that one scrambled truth's within-day PROFILES,
    this one scrambles the day LEVELS. Every value and the whole substitution machinery are
    preserved; only the day a level belongs to is destroyed. A gain here would mean the rungs
    measure the act of substituting rather than the level information.
    """
    truth_day = day_mean({k: truth[k] for k in implied if k in truth})
    levels: dict[str, float] = {}
    for key in implied:
        if key in truth and key in truth_day:
            levels[key[0]] = truth_day[key]
    days = sorted(levels)
    dealt = list(days)
    random.Random(seed).shuffle(dealt)
    reassigned = {day: levels[other] for day, other in zip(days, dealt)}

    implied_day = day_mean(implied)
    out: dict[tuple[str, int], float] = {}
    for key in implied:
        level = reassigned.get(key[0])
        if level is None or key not in implied_day:
            continue
        out[key] = level + (float(implied[key]) - implied_day[key])
    return out


def identity_levels(implied: Mapping[tuple[str, int], float]) -> dict[tuple[str, int], float]:
    """The model's OWN day mean plus its OWN within-day deviations — THE SOUNDNESS CHECK.

    Algebraically the model's own series, routed through the identical substitution machinery. If
    this gains, the rungs measure the act of substituting rather than what was substituted, and
    every number in the artefact is void.
    """
    implied_day = day_mean(implied)
    return {
        key: implied_day[key] + (float(implied[key]) - implied_day[key])
        for key in implied
        if key in implied_day
    }


def ceiling_is_unreachable_from(source: str) -> bool:
    """True when nothing in `source` imports THIS module — an AST walk, not a substring search.

    NOT IMPORTED FROM `ep13_ccgt_swap_ceiling`, AND THE FIRST DRAFT OF THIS FILE DID IMPORT IT.
    That function derives its subject from `Path(__file__).stem`, which is bound to the module where
    it is DEFINED, not the one that calls it — so the imported version asked "does the published feed
    import the SWAP ceiling?", answered truthfully about the wrong module, and would have reported
    this module unreachable no matter what imported it. A wall guard that cannot fail is worse than
    no wall guard, because it is read as one that passed.

    Caught by `test_the_metered_gas_series_CANNOT_REACH_the_published_feed`, whose negative leg
    hands it a source that DOES import this module and requires a refusal. The four other EP13
    bounds each define their own copy for exactly this reason; the reuse was the novel mistake.
    """
    tree = ast.parse(source)
    mine = Path(__file__).stem
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[-1] == mine for alias in node.names):
                return False
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[-1] == mine:
                return False
            if any(alias.name == mine for alias in node.names):
                return False
    return True


def _published_feed_source() -> str:
    return (PROJECT_DIR / "tools" / "generate_grid_intensity_feed.py").read_text(encoding="utf-8")


def measure_year(
    year: str,
    *,
    rungs: Mapping[str, Mapping[tuple[str, int], float]],
    published: Mapping[tuple[str, int], float],
    demand: Mapping[tuple[str, int], float],
    implied: Mapping[tuple[str, int], float],
    truth: Mapping[tuple[str, int], float],
    balance: Mapping[str, Mapping[tuple[str, int], float]],
    caps: Mapping[str, Mapping[str, int]],
    bound_by_key: Mapping[tuple[str, int], bool],
) -> dict:
    """Every rung for one year, on the half hours EVERY rung covers and nothing else."""
    score_keys = [
        k
        for k in rungs["baseline"]
        if k[0][:4] == year
        and k in published
        and held_out(k[0])
        and float(demand.get(k) or 0.0) > 0.0
        and all(k in series for series in rungs.values())
    ]
    if len(score_keys) < MIN_SCORED_HALF_HOURS:
        raise neso.NesoIntensityUnavailable(
            f"{year} has {len(score_keys)} scored half hours, under the {MIN_SCORED_HALF_HOURS} bar"
        )

    row: dict[str, object] = {}
    for name, series in rungs.items():
        row[name] = neso.compare_shapes(
            {k: series[k] for k in score_keys}, published, demand, year
        )

    correlations = {
        name: float(value["correlation"])
        for name, value in row.items()
        if isinstance(value, dict) and value.get("correlation") is not None
    }
    baseline = correlations["baseline"]
    row["gain_over_baseline"] = {
        name: correlations[name] - baseline for name in correlations if name != "baseline"
    }

    row["control_scored_half_hours"] = float(len(score_keys))

    # THE BALANCE IS REPORTED PER RUNG AND ON THIS YEAR'S SCORED HALF HOURS. A run-wide figure would
    # let a year whose caps bind constantly hide behind five that never do, and the years differ:
    # the modelled gas level falls across the window while truth's does not.
    row["control_max_abs_balance_mw"] = {
        name: max((abs(series[k]) for k in score_keys if k in series), default=0.0)
        for name, series in balance.items()
    }

    implied_day = day_mean(implied)
    truth_day = day_mean({k: truth[k] for k in implied if k in truth})
    day_keys = [k for k in score_keys if k in implied_day and k in truth_day]
    row["control_substitution_distance_mw"] = (
        sum(abs(implied_day[k] - truth_day[k]) for k in day_keys) / len(day_keys)
        if day_keys
        else 0.0
    )
    # EVERY CAP, ON THIS YEAR'S SCORED HALF HOURS. The first draft counted only the fleet clamps and
    # a non-zero balance, and MISSED `capped_to_served` -- which is by far the dominant one, binding
    # on 117,510 half hours run-wide where the clamps bind on 1,293. A control that exists to refuse
    # a rung its caps are carrying, and that does not count the cap actually carrying it, is
    # fail-open: it read 0.000-0.050 and passed every year while the rung was pinned to the baseline
    # wherever truth's gas level sat above what the shipped stack served.
    row["control_bound_share"] = sum(
        1 for k in score_keys if bound_by_key.get(k, False)
    ) / len(score_keys)
    # RUN-WIDE, AND LABELLED AS SUCH so it cannot be read as this year's. The share above is the
    # control; these are the raw totals across every year the caches cover.
    row["cap_counts_run_wide"] = {name: dict(counts) for name, counts in caps.items()}
    row["implied_gas_vs_truth"] = {
        "day_mean_correlation": _pearson(
            [implied_day[k] for k in day_keys], [truth_day[k] for k in day_keys]
        ),
        "within_day_correlation": within_day_correlation(implied, truth, score_keys),
        "mean_implied_mw": sum(implied[k] for k in score_keys) / len(score_keys),
        "mean_truth_mw": sum(truth[k] for k in score_keys if k in truth) / len(score_keys),
        "mean_abs_day_level_error_mw": row["control_substitution_distance_mw"],
    }
    return row


def verdicts(row: Mapping[str, object]) -> dict[str, bool]:
    """The controls, computed from the row that was just published rather than only asserted in a
    test — a verdict that lives only in another process is one a reader has to take on trust."""
    gains: Mapping[str, float] = row["gain_over_baseline"]  # type: ignore[assignment]
    balances: Mapping[str, float] = row["control_max_abs_balance_mw"]  # type: ignore[assignment]
    return {
        # CONTROL 1, AND IT IS THE ONE THIS WHOLE PASS EXISTS FOR. The balanced rung conserves
        # energy as an IDENTITY: gas + coal + peaker equals the thermal residual on every scored
        # half hour. Read this before any gain below it -- without it the ceiling is §15's
        # unattributable diagnostic wearing a new label.
        "the_balanced_rung_conserves_energy": (
            float(balances.get("level_balanced", 1.0)) <= MAX_BALANCE_RESIDUAL_MW
        ),
        # CONTROL 2, THE COMPLEMENT, AND IT IS WHY THE UNBALANCED RUNG IS STILL IN THE ARTEFACT. If
        # §15's arithmetic ALSO conserved energy, this pass would have repaired nothing and the
        # +0.116 would have been a bound all along. Asserting the defect exists is not the same as
        # showing it, and this shows it in the published row.
        "the_unbalanced_rung_does_NOT_conserve_energy": (
            float(balances.get("level_unbalanced", 0.0)) > MAX_BALANCE_RESIDUAL_MW
        ),
        # CONTROL 3, THE SUBSTITUTION IS NOT A NO-OP. If truth's day levels were near-identical to
        # the model's own, a zero gain would be equally consistent with "the level is worth nothing"
        # and with "nothing was substituted" -- a control whose PASS branch is unreachable.
        "the_substituted_levels_are_not_the_models_own": (
            float(row["control_substitution_distance_mw"]) > MIN_SUBSTITUTION_DISTANCE_MW  # type: ignore[arg-type]
        ),
        # CONTROL 4, THE SOUNDNESS CHECK. The model's own level through the identical machinery must
        # score the baseline. A gain here voids every other number in the row.
        "substituting_the_models_own_level_changes_nothing": (
            abs(float(gains.get("level_identity", 1.0))) < MAX_IDENTITY_GAIN
        ),
        # CONTROL 5, THE NULL DOES NOT FLATTER. Truth's day levels dealt to the wrong days keep every
        # value and the whole machinery, so a GAIN here is the machinery talking.
        #
        # KEYED TO THE PROPERTY, AND §15's FIRST DRAFT WAS NOT. It asked for `abs(gain) < 0.01` --
        # "the null collapses to nothing" -- and went RED against a sound instrument, because
        # scrambled input is not absent input: it replaces the model's own level with a WRONG level
        # and must hurt. A control pinned to a guessed answer, red because the world behaved
        # correctly. What a null owes is that it does not FLATTER.
        "the_null_does_not_gain": (
            float(gains.get("level_shuffled", 0.0)) < MIN_MATERIAL_GAIN
        ),
        # CONTROL 6, AND IT IS THE ONE THAT MAKES THE NULL MEAN SOMETHING. A null that cannot gain is
        # satisfied by an instrument reporting one constant whatever it is handed. Correct levels
        # must beat scrambled levels by a material margin, or these rungs are not measuring level.
        "correct_levels_beat_scrambled_levels": (
            float(gains.get("level_balanced", 0.0)) - float(gains.get("level_shuffled", 0.0))
            > MIN_NULL_DISCRIMINATION
        ),
        # CONTROL 7, THE CAPS ARE NOT CARRYING THE RUNG. Past this share the balanced rung is partly
        # measuring the caps rather than the level, and its reading is refused rather than footnoted.
        "the_caps_are_not_carrying_the_rung": (
            float(row["control_bound_share"]) < MAX_BOUND_SHARE  # type: ignore[arg-type]
        ),
        # REPORTED, NOT CONTROLS. These are the answers, and a control that asserts its own answer is
        # a control that cannot fail (R15 TAUTOLOGY).
        "the_level_clears_the_baseline": (
            float(gains.get("level_balanced", 0.0)) > MIN_MATERIAL_GAIN
        ),
        "the_disturbance_is_material": (
            abs(float(gains.get("level_balanced", 0.0)) - float(gains.get("level_unbalanced", 0.0)))
            >= MIN_MATERIAL_GAIN
        ),
        "the_unbalanced_rung_was_flattered": (
            float(gains.get("level_balanced", 0.0)) < float(gains.get("level_unbalanced", 0.0))
        ),
    }


def measure() -> dict:
    """Every year the caches share. Loads the real caches; fits nothing."""
    from sim import elexon_fuel_outturn as fuel
    from sim.generation_demand_history import aggregate_renewable_generation
    from tools.generate_grid_intensity_feed import (
        AGWS_CACHE,
        DEMAND_CACHE,
        aggregate_demand,
        fuel_mix,
    )

    demand = aggregate_demand(json.loads(Path(DEMAND_CACHE).read_text(encoding="utf-8")))
    wind = aggregate_renewable_generation(json.loads(Path(AGWS_CACHE).read_text(encoding="utf-8")))
    (imports, coal_capacity, _coverage, thermal_floors, must_run, _mrc, _envelope) = fuel_mix()
    floors = {y: r["floor_mw"] for y, r in thermal_floors.items()}

    # THE METERED GAS SERIES, AND IT LIVES ONLY IN THIS PROCESS. FUELHH's thermal cache is the one
    # place CCGT is published half-hourly; nothing here hands it to `sim/`.
    truth = {
        key: fuels[SWAPPED_FUEL]
        for key, fuels in per_fuel_by_period(fuel.load_cached_thermal()).items()
        if SWAPPED_FUEL in fuels
    }

    # THE POPULATION IS FIXED FIRST AND SHARED BY EVERY RUNG. A half hour with no gas reading is
    # refused from the baseline too, so no part of any gain below is a coverage difference.
    scored_keys = [k for k in demand if k in truth]

    common = dict(
        imports_by_period=imports,
        coal_capacity_by_year=coal_capacity,
        thermal_floor_by_year=floors,
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year=None,
    )
    baseline_rates, implied, baseline_balance, _, _ = build_rates(
        demand, wind, only_keys=scored_keys, **common
    )

    # THE RE-IMPLEMENTATION IS HELD TO THE SHIPPED FUNCTION BEFORE ANYTHING IS SCORED, and not only
    # by a test in another process -- a reader of this artefact has to be able to see it.
    #
    # `gci.build_shape` IS HANDED THE SAME RESTRICTED DEMAND, which is the whole subtlety: it
    # normalises per calendar year over whatever keys survive, so running it over the full demand map
    # and comparing against a baseline built on the gas-reading subset would report the COVERAGE
    # difference as arithmetic drift.
    shipped_shape = gci.build_shape({k: demand[k] for k in scored_keys}, wind, **common)
    reference = normalise(baseline_rates, demand)
    drift = max(
        (abs(reference[k] - shipped_shape[k]) for k in reference if k in shipped_shape),
        default=None,
    )

    level_override = level_swap(implied, truth)
    overrides = {
        "level_balanced": (level_override, True),
        "level_unbalanced": (level_override, False),
        "level_identity": (identity_levels(implied), True),
        "level_shuffled": (shuffled_day_levels(implied, truth), True),
    }
    rungs = {"baseline": normalise(baseline_rates, demand)}
    balance = {"baseline": baseline_balance}
    caps: dict[str, dict[str, int]] = {}
    bound_by_key: dict[str, dict[tuple[str, int], bool]] = {}
    for name, (override, is_balanced) in overrides.items():
        rates, _, rung_balance, capped, bound = build_rates(
            demand,
            wind,
            only_keys=scored_keys,
            ccgt_override_by_period=override,
            balanced=is_balanced,
            **common,
        )
        rungs[name] = normalise(rates, demand)
        balance[name] = rung_balance
        caps[name] = capped
        bound_by_key[name] = bound

    ceiling = neso._physical_ceiling_g_co2_per_kwh()
    parsed = neso.to_settlement_periods(neso.load_cached())
    actual = {
        key: float(entry["actual"])
        for key, entry in parsed.items()
        if entry.get("actual") is not None and float(entry["actual"]) <= ceiling
    }
    published = neso.published_shape(actual, demand)

    rows: dict[str, dict] = {}
    for year in sorted({k[0][:4] for k in rungs["baseline"]} & {k[0][:4] for k in published}):
        try:
            row = measure_year(
                year,
                rungs=rungs,
                published=published,
                demand=demand,
                implied=implied,
                truth=truth,
                balance=balance,
                caps=caps,
                bound_by_key=bound_by_key["level_balanced"],
            )
        except (neso.NesoIntensityUnavailable, ValueError, KeyError):
            continue
        row["controls"] = verdicts(row)
        rows[year] = row

    return {
        "measured_from": "sim/cache (Elexon FUELHH thermal + AGWS wind + demand; NESO outturn)",
        "basis": neso.PUBLISHED_BASIS,
        "split": "scored on EVEN days of the month -- the same population the other EP13 bounds score",
        "swapped_fuel": SWAPPED_FUEL,
        "what_this_is": (
            "A CEILING on the DAILY AND SEASONAL LEVEL of gas -- the candidate §15 named and could "
            "not size, because its `ccgt_level` rung moved the daily gas total without re-deciding "
            "the residual's other terms and therefore reported part of that disturbance. This hands "
            "the shipped reconstruction perfect knowledge of the day level and re-decides coal and "
            "the peaker band around it so the energy balance holds as an IDENTITY. A negative "
            "RETIRES the candidate. Up to error cancellation: a proxy whose errors offset the "
            "model's other errors could score above it, and one that does is fitting the residual."
        ),
        "why_the_unbalanced_rung_is_still_here": (
            "So the disturbance is MEASURED rather than asserted. Publishing only the balanced "
            "number would leave §15's +0.116 standing in the record with nothing to read it "
            "against, and would make this pass a claim that the disturbance mattered rather than a "
            "measurement of how much."
        ),
        "rungs": {
            "baseline": "build_shape as shipped, on the half hours with a metered gas reading",
            "level_balanced": "TRUTH's day mean + the model's own within-day deviations, residual "
            "re-decided so gas + coal + peaker == thermal_mw -- THE CEILING",
            "level_unbalanced": "the identical override through §15's `above_ccgt` line -- NOT A "
            "BOUND, present only as the subtrahend that sizes the disturbance",
            "level_identity": "the model's OWN day mean + its OWN deviations -- algebraically the "
            "model's own series. THE SOUNDNESS CHECK: a gain here voids the artefact",
            "level_shuffled": "truth's DAY MEANS dealt to the WRONG days -- THE NULL",
        },
        "conservation_anchor": (
            "`served_baseline` -- what the SHIPPED stack dispatches -- and NOT `thermal_mw`. The "
            "shipped model already fails `gas + coal + peaker == thermal_mw` whenever the residual "
            "exceeds the CCGT fleet plus the peaker headroom: it truncates and serves less than it "
            "demanded. Conserving against a quantity the baseline itself violates would report the "
            "shipped model's truncation as this substitution's imbalance in every high-demand half "
            "hour. Counted separately as `baseline_could_not_meet_its_own_residual`."
        ),
        "caps": {
            "capped_to_served": "imposed gas above what the shipped stack served, clamped down to "
            "it -- coal and the peakers cannot go negative to make room",
            "unservable": "a shortfall exceeding coal capacity plus the peaker headroom, so the "
            "balanced rung's residual goes negative and the half hour is counted",
            "clamped_low": "imposed gas below zero",
            "clamped_high": "imposed gas above the CCGT fleet capacity",
            "baseline_could_not_meet_its_own_residual": "a fact about the SHIPPED model, reported "
            "and not corrected here: `thermal_mw` exceeded the CCGT fleet plus the peaker headroom "
            "and the stack served less energy than its own residual demanded",
        },
        "peaker_headroom_mw": PEAKER_HEADROOM_MW,
        "reimplementation_drift": drift,
        "reimplementation_reproduces_the_shipped_shape": (
            drift is not None and drift < MAX_REIMPLEMENTATION_DRIFT
        ),
        "ceiling_reaches_the_published_feed": not ceiling_is_unreachable_from(
            _published_feed_source()
        ),
        "not_publishable_because": (
            "every rung holds metered half-hourly CCGT, the largest emissions term on the system. A "
            "series built from it would be NESO's arithmetic with a different cache. The value here "
            "is as a BOUND."
        ),
        "years": rows,
        "preregistration": (
            "docs/staging/done/WORKER_PREREGISTRATION_WHAT_THE_BALANCED_GAS_LEVEL_CEILING_MUST_SHOW"
            "_2026-09-03.md"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    result = measure()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print(f"reimplementation drift: {result['reimplementation_drift']!r} "
          f"-> reproduces={result['reimplementation_reproduces_the_shipped_shape']}")
    print(f"peaker headroom: {result['peaker_headroom_mw']:.0f} MW")
    print()
    print("year  baseline  balanced  unbalanced  disturb  identity  shuffled | bound  balance_mw")
    for year, row in sorted(result["years"].items()):
        gains = row["gain_over_baseline"]
        balanced = gains["level_balanced"]
        unbalanced = gains["level_unbalanced"]
        print(
            f"{year}  {row['baseline']['correlation']:8.4f}  "
            f"{balanced:+8.4f}  {unbalanced:+10.4f}  "
            f"{balanced - unbalanced:+7.4f}  "
            f"{gains['level_identity']:+8.4f}  {gains['level_shuffled']:+8.4f} | "
            f"{row['control_bound_share']:5.3f}  "
            f"{row['control_max_abs_balance_mw']['level_balanced']:.2e}"
        )
    print()
    for year, row in sorted(result["years"].items()):
        failed = [name for name, ok in row["controls"].items() if not ok]
        print(f"{year} controls: {'ALL PASS' if not failed else 'FAILED -> ' + ', '.join(failed)}")
    print(f"\n-> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
