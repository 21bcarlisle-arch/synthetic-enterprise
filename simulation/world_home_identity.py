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
            "parameter alone does not move it, and the departure LEVEL is a separate part with its "
            "own digest."
        ),
    }


__all__ = [
    "FABRIC_IS",
    "PROBE_SEED",
    "PROBE_SIZE",
    "PROBE_YEAR",
    "home_stock_identity",
]
