"""Where a household that moves with us goes, and the home it finds there.

REUSE: simulation/move_destination.py
CLASS: CUSTOM
INDEX: searched "destination", "mover_arrives", "move with us", "draw_premise". `sim/customer_state_layer`
       draws the destination only as an id (`HomeMove.mover_arrives`); `simulation/household_siting`
       sites a household in a region; `premise_population.draw_premise_from_joint` is the world's
       own premise draw (the one `net_new_acquisition.year_premise_stock` uses). This module joins
       the three for the one household that needs a destination: a mover supplied at its new home.

THE KNOWLEDGE IT RESTS ON is `docs/market_research/home_moves.md` §8.6 (choices 3 and 4) and
`docs/market_research/how_far_gb_households_move_and_what_their_new_home_uses.md`:

  * REGION. The destination stays in the origin's ONS region with probability
    `q1_move_destination_in_region_share` (default 0.519, the DERIVED lower bound from ONS IM2020-T7b
    and T8). Otherwise it is drawn from the world's own regional household mix
    (`population_draw.region_weights_from_curriculum`) with the origin removed. That mix stands in
    for the ONS flow marginals, which are not carried in the repo; named, not sourced.
  * ADDRESS AND WEATHER. The household siting draw for the destination's id, inside that region. The
    weather follows that cell. This world prices nationally, so the region re-rates no tariff.
  * DWELLING. The world's premise draw for the destination's id. The household keeps what is its
    own (EV, income stress); the dwelling, its solar and its battery are the new home's. Use
    switches to the new dwelling on the move date; how fast real use converges is a GAP (G8.8).

All draws are keyed on the destination premise id, which the world already drew, so a destination
is identical whatever else is in the run.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import functools
from dataclasses import dataclass
from typing import Optional

from simulation.meter_reads import assumption_toggle
from simulation.rng_substream import substream

NAMESPACE = "move_destination"

#: The authored roster carries a city in `location.region`, not an ONS region. Geography, not a
#: parameter: each city lies in exactly one ONS region (the Cotswolds mostly in the South West).
ONS_REGION_OF_ROSTER_PLACE: dict[str, str] = {
    "Birmingham": "West Midlands",
    "Cotswolds": "South West",
    "Glasgow": "Scotland",
    "London": "London",
    "Manchester": "North West",
    "Teesside": "North East",
}


@dataclass(frozen=True)
class Destination:
    premise_id: str
    region: str
    in_origin_region: bool
    lat: float
    lon: float
    output_area: Optional[str]
    premise: object  # premise_population.DrawnPremise


def in_region_share(setting: str = "default") -> float:
    """The share of moves that stay in the origin's ONS region (the toggle register's row)."""
    return assumption_toggle("q1_move_destination_in_region_share", setting)


def ons_region_of(record: dict) -> Optional[str]:
    """The ONS region a supply point's record sits in, or None if it names none we can place."""
    place = (record.get("location") or {}).get("region")
    return ONS_REGION_OF_ROSTER_PLACE.get(place, place)


def destination_region(premise_id: str, origin_region: str, base_seed: int,
                       share: Optional[float] = None) -> tuple[str, bool]:
    """(the destination's ONS region, whether it is the origin's)."""
    from simulation.population_draw import region_weights_from_curriculum

    p = in_region_share() if share is None else share
    rng = substream(NAMESPACE, f"region::{premise_id}", base_seed)
    if rng.random() < p:
        return origin_region, True
    others = {r: w for r, w in region_weights_from_curriculum().items() if r != origin_region}
    total = sum(others.values())
    x, acc = rng.random() * total, 0.0
    for region, weight in sorted(others.items()):
        acc += weight
        if x < acc:
            return region, False
    return sorted(others)[-1], False


@functools.lru_cache(maxsize=1)
def _fitted_joint():
    from simulation.premise_population import fitted_stock_joint

    return fitted_stock_joint()


def draw_destination(premise_id: str, origin_record: dict, move_date: dt.date,
                     base_seed: int) -> Optional[Destination]:
    """The destination for a mover supplied at its new home, or None where the world cannot site it
    (an origin with no placeable region, or a region the siting frame has no cells for)."""
    from simulation.household_siting import coordinate_for_customer, output_area_for_customer
    from simulation.premise_population import draw_premise_from_joint

    origin = ons_region_of(origin_record)
    if origin is None:
        return None
    region, same = destination_region(premise_id, origin, base_seed)
    sited = coordinate_for_customer(premise_id, base_seed, region)
    if sited is None:
        return None
    premise = draw_premise_from_joint(premise_id, base_seed=base_seed, as_of=move_date,
                                      fitted=_fitted_joint())
    return Destination(premise_id=premise_id, region=region, in_origin_region=same,
                       lat=sited[0], lon=sited[1],
                       output_area=output_area_for_customer(premise_id, base_seed, region),
                       premise=premise)


def household_at_destination(mover_now, destination: Destination):
    """The mover's household as it lives at the new home: the new dwelling, with the household's
    own EV and income stress carried."""
    return dataclasses.replace(
        destination.premise.household,
        customer_id=mover_now.customer_id,
        has_ev=mover_now.has_ev,
        ev_charger_kw=mover_now.ev_charger_kw,
        income_stress=mover_now.income_stress,
        output_area=destination.output_area,
    )


def next_move_from_destination(move, from_date: dt.date, supply_end: dt.date, base_seed: int):
    """A follower's next move, drawn on the world's own hazard at the destination it moved to, from
    `from_date` (the end of the term it carried: a household does not move twice inside one term,
    named). The household keeps its tenure: whether movers change tenure is not drawn (named)."""
    from sim.customer_state_layer import Occupancy, first_move_out
    from simulation.household_segments import tenure_for_customer

    arrived = move.mover_arrives
    start = max(from_date, move.move_date)
    if supply_end <= start:
        return None
    return first_move_out(
        Occupancy(premise_id=arrived.premise_id, occupancy_id=arrived.occupancy_id,
                  tenure=tenure_for_customer(arrived.occupancy_id)),
        start, supply_end, base_seed)


def shape_across_a_move(before, after, move_date_iso: str):
    """A `shape_fn(date_str) -> [48 kWh]` that is the old home's before the move date and the new
    home's from it."""
    def shape_fn(date_str: str) -> list[float]:
        return (after if date_str[:10] >= move_date_iso else before)(date_str)
    return shape_fn
