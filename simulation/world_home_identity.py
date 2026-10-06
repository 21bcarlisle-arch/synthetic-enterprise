"""WHICH HOMES a run's world contains, as something a later artefact can be compared against.

THE DEFECT THIS EXISTS FOR, and it is not hypothetical. `departure_level_anchor.world_level_identity`
publishes a digest that is stamped `world_identity` at the top of every run artefact, and
`docs/design/blind_envelope_arms_2026-09-11.json` names it as the sole warrant that its five arms are
comparable. That digest covers the departure LEVEL and nothing else -- it is keyed to the property it
names and is right about it. But the home stock demonstrably moved between `3957ba848` and this tree
(`0d86d6dfe`, "the world's homes are drawn from the fitted joint now"), the anchor module is
byte-identical across that change, and so **one digest value, `39a192ce04c1eda8`, spans two different
home populations**. A reader who takes a matching `world_identity` as "same world" is reading a name
that covers half of what it says.

WHY A PROBE DRAW AND NOT A DIGEST OF THE PARAMETERS. The stock is produced by a joint, a rake onto
published marginals, a per-home draw and a physics mapping, in that order. Digesting the joint would
miss a change to the physics; digesting the physics constants would miss a change to the joint; and
digesting both would still miss a change to the draw that sits between them. The probe runs the whole
chain that a real run runs -- `net_new_acquisition.year_premise_stock`, the function the world's homes
actually come from -- and digests what comes out. Anything that moves a home moves this.

WHY THAT IS AFFORDABLE, and this is the thing that was assumed away.
`SEAT_FINDING_THE_WORLD_IDENTITY_DIGEST_IS_BLIND_TO_THE_HOME_STOCK_2026-09-15.md` declined to propose
this instrument on the grounds that "the stock is resolved by a multi-minute world resolve that no
artefact header can afford to do". That is true of resolving a RUN's population and false of a fixed
probe: measured 2026-09-15, `PROBE_SIZE` homes through the whole chain costs **under a second cold and
under 10ms warm**. The finding's remedy section is corrected by this module rather than quietly
dropped -- the objection was to the cost, and the cost was never measured.

WHAT THIS IS NOT. It is not a claim about which homes a particular run drew. A run picks its own seed,
its own size and its own year mix, and two runs sharing this digest still drew different individual
homes. What it says is that they drew them from the same stock through the same physics, which is
exactly the question "is the world this was measured in still the world" asks and the departure digest
cannot answer.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json

#: The probe's three coordinates. FIXED, and they are not a tuning surface: the digest's whole value
#: is that it is the same probe in every world, so a run that varied them would be comparing a
#: measurement of the stock against a measurement of the probe. The year is inside the published
#: switching record and mid-decade, the seed is the date the blind-envelope arms were filed, and the
#: size is set below.
PROBE_YEAR = 2020
PROBE_SEED = 20260911

#: 96 HOMES, and the number is a trade and not a round figure. The draw is deterministic per home id,
#: so a stock change that moves any drawn home at all moves the digest -- one home would be enough to
#: DETECT a wholesale change and far too few to detect a change that moves a minority of the stock.
#: 96 costs under 10ms warm and, on the two stock paths this tree can still build (fitted joint vs
#: the pre-2026-09-10 path), separates them on the first home. It is not a sample anybody should read
#: a statistic off: it identifies, it does not estimate.
PROBE_SIZE = 96

#: HOW THE GENERATOR EXPOSES A HOME'S FABRIC: every field of `fabric_physics.FabricParameters`, not
#: the three-axis subset `tools/settlement_per_axis_gain.FABRIC_AXES` grades on. The subset is what
#: the chooser places a candidate on; this is what the world's physics actually got, and a change that
#: moved thermal mass without moving floor area is a different world by any reading.
FABRIC_IS = "every field of simulation.fabric_physics.FabricParameters"

#: Six decimal places, matching the departure part's own quantisation, so that a float whose last bit
#: moved for a reason nobody can name does not read as a new world.
_PLACES = 6


def _probe_vectors(*, from_fitted_joint: bool | None = None) -> list[list[str]]:
    """The probe stock's fabric records, in draw order, quantised to strings.

    IN DRAW ORDER, NOT SORTED. `year_premise_stock` is deterministic in `(base_seed, year, n)` and
    hands home `i` to slot `i`; a change that permuted which home lands in which slot would hand a
    run a different book at the same seed, and sorting would hide exactly that.
    """
    # Imported inside the call: `net_new_acquisition` is the world's acquisition machinery and pulls
    # a large tree behind it, and an artefact header that asks for an identity should not pay for
    # that at import time. The same reason `year_premise_stock` imports its own joint lazily.
    from simulation import fabric_physics
    from simulation.net_new_acquisition import year_premise_stock

    stock = year_premise_stock(
        PROBE_YEAR, base_seed=PROBE_SEED, n=PROBE_SIZE, from_fitted_joint=from_fitted_joint
    )
    fields = [f.name for f in dataclasses.fields(fabric_physics.FabricParameters)]
    rows = []
    for premise in stock:
        parameters = fabric_physics.fabric_parameters(premise.household)
        rows.append([f"{float(getattr(parameters, name)):.{_PLACES}f}" for name in fields])
    return rows


def home_stock_identity(*, from_fitted_joint: bool | None = None) -> dict:
    """WHICH HOMES the world contains, as a digest a later artefact can be compared against.

    `from_fitted_joint` IS HERE SO THE CONTROL CAN REACH THE FAILING CASE, and that is its only
    caller. `None` is the live world and is what every publisher uses. Passing `False` builds the
    pre-2026-09-10 stock -- the one the 09-11 arms were measured in -- which is the one other home
    population this tree can still construct, and it is the case the departure digest provably cannot
    tell apart from the live one. A guard that can only be shown to refuse is a guard that might
    refuse everything; this parameter is how the other half gets asserted.
    """
    rows = _probe_vectors(from_fitted_joint=from_fitted_joint)
    canonical = json.dumps(rows, separators=(",", ":"))
    return {
        "digest": hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16],
        "probe_year": PROBE_YEAR,
        "probe_seed": PROBE_SEED,
        "probe_size": PROBE_SIZE,
        "fabric_is": FABRIC_IS,
        "what_this_identifies": (
            "the HOME STOCK the world draws from -- {} homes drawn through "
            "`net_new_acquisition.year_premise_stock`, the function a run's own homes come from, and "
            "then through the fabric physics, digested as {}. Two runs sharing this digest drew "
            "their homes from the same stock through the same physics; two that do not saw "
            "different houses, however close their timestamps and however well their departure "
            "levels agree.".format(PROBE_SIZE, FABRIC_IS)
        ),
        "what_this_does_not_cover": (
            "WHICH homes a particular run drew. A run chooses its own seed, size and year mix, so "
            "two runs sharing this digest still hold different individual houses -- this says they "
            "came out of the same country, not that they are the same. It also covers only the "
            "FABRIC: a change to heating fuel, appliances or occupancy that leaves every thermal "
            "parameter alone does not move it -- that is the `demand` part beside this one -- and "
            "the departure LEVEL is a separate part with its own digest."
        ),
    }


#: THE DEMAND PROBE'S WEEK AND PLACE. The same 96 homes, run for one REAL week of the archive, so a
#: change to what a home DOES with its fabric moves a digest the way a change to the fabric already
#: does. January because every one of the 2026-10-06 demand changes fires in the cold: the boiler's
#: pump and fan, the supplementary heater (5 of the 96 own one), and a HES season factor that is
#: furthest from 1 in midwinter. The site is the one the supplementary heater's own normal is taken
#: from. Like the coordinates above, these are fixed and not a tuning surface.
DEMAND_PROBE_SITE = "C1"
DEMAND_PROBE_START = (PROBE_YEAR, 1, 13)
DEMAND_PROBE_DAYS = 7


def _demand_vectors() -> list[list[str]]:
    """Each probe home's half-hourly electricity then gas for the probe week, quantised, in draw
    order. Measured 2026-10-06: ~0.75s for the stock and ~0.7s for 96 traces (~7ms each), so about
    1.5s cold for the whole part -- two orders above the stock probe, and still a header cost."""
    import datetime as dt

    from simulation.fabric_physics import latitude_for_weather_site
    from simulation.net_new_acquisition import year_premise_stock
    from simulation.premise_trace import generate_premise_trace, load_trace_weather

    start = dt.date(*DEMAND_PROBE_START)
    weather = load_trace_weather(
        DEMAND_PROBE_SITE, start=start, end=start + dt.timedelta(days=DEMAND_PROBE_DAYS - 1))
    if len(weather) != DEMAND_PROBE_DAYS:
        raise ValueError(f"the {DEMAND_PROBE_SITE} archive holds {len(weather)} of the "
                         f"{DEMAND_PROBE_DAYS} probe days from {start}")
    latitude = latitude_for_weather_site(DEMAND_PROBE_SITE)
    rows = []
    for premise in year_premise_stock(PROBE_YEAR, base_seed=PROBE_SEED, n=PROBE_SIZE):
        trace = generate_premise_trace(
            premise_id=premise.premise_id, household=premise.household, weather=weather,
            seed=PROBE_SEED, latitude_deg=latitude)
        rows.append([f"{v:.{_PLACES}f}" for commodity in ("electricity", "gas")
                     for day in trace.half_hourly(commodity) for v in day])
    return rows


def home_demand_identity() -> dict:
    """WHAT THE WORLD'S HOMES DO, as a digest a later artefact can be compared against.

    THE DEFECT THIS EXISTS FOR (2026-10-06). Four changes landed in one day that each moved a
    fabric-path home's metered demand -- the boiler's pump and fan, HES's cooking and laundry
    season, supplementary electric heating, and per-home appliance ownership (`owned_stock`) -- and
    neither the departure digest nor the home-stock digest moved, because the houses were the same
    houses. A value-arms bound taken that morning and one taken that night carried one world stamp
    from two demand worlds. This is `home_stock_identity`'s defect one layer down, and it is fixed
    the same way: run the generator a real run runs on a fixed probe, and digest what comes out.
    """
    canonical = json.dumps(_demand_vectors(), separators=(",", ":"))
    return {
        "digest": hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16],
        "probe_site": DEMAND_PROBE_SITE,
        "probe_start": "{:04d}-{:02d}-{:02d}".format(*DEMAND_PROBE_START),
        "probe_days": DEMAND_PROBE_DAYS,
        "probe_size": PROBE_SIZE,
        "what_this_identifies": (
            "the DEMAND the world's homes generate -- the same {} probe homes as the `homes` part, "
            "each run through `premise_trace.generate_premise_trace` for {} real days of the {} "
            "archive from {}, digested as half-hourly electricity and gas. Anything that changes "
            "what a home draws in that week moves it: appliances, their ownership and season, the "
            "boiler's own electricity, supplementary heat, the thermal solve, the archive itself."
            .format(PROBE_SIZE, DEMAND_PROBE_DAYS, DEMAND_PROBE_SITE,
                    "{:04d}-{:02d}-{:02d}".format(*DEMAND_PROBE_START))
        ),
        "what_this_does_not_cover": (
            "what `fabric_demand_path` layers on top of the trace -- the comfort constraint from "
            "last year's bill, away days, life-event segments -- and anything that only shows "
            "outside a January week. It identifies, it does not estimate: no figure should be "
            "read off these homes."
        ),
    }


__all__ = [
    "DEMAND_PROBE_DAYS",
    "DEMAND_PROBE_SITE",
    "DEMAND_PROBE_START",
    "FABRIC_IS",
    "PROBE_SEED",
    "PROBE_SIZE",
    "PROBE_YEAR",
    "home_demand_identity",
    "home_stock_identity",
]
