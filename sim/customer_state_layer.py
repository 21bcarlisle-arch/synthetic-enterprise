"""The customer state layer, slice 1: a HOME MOVE as a first-class world transition.

Map atom B7 (`docs/design/B7_CUSTOMER_STATE_MOVES_AND_SHOCKS_FRAME.md`). The life-event stream
(`simulation/life_events.py`) emits job loss, illness, divorce, retirement and a new child; nothing in
the world emits a move. This module does — and only that. Income-shock depth and composition change
are the atom's later slices and are not started here.

WHAT A MOVE IS, SAID BEFORE IT IS DRAWN
---------------------------------------
For a supplier a move is a change in who is liable at a metering point while the meter stays put
(`docs/market_research/home_moves.md` §1). So the world needs two identities the old `customer_id`
conflated:

  - a PREMISE — the metering point. It never moves.
  - an OCCUPANCY — the liable household at that premise, for a window. It ends.

A move at premise P is therefore THREE transitions, not one:

  1. `OccupancyEnded` at P — the credit exit. It opens a final-bill exposure through
     `simulation/final_bill_outcome.open_final_bill_exposure`, the machinery that already resolves
     paid / late / partial / unpaid / gone away behind the wall.
  2. `OccupancyStarted` at P — a stranger moves in and is supplied on a DEEMED contract without
     agreeing anything (Ofgem, *Guidance on Deemed Contracts*, 2023, ¶2.10).
  3. `OccupancyStarted` at the mover's NEW premise — also deemed, until they choose terms.

The "credit exit plus two deemed entries" is not asserted; it falls out of the identity split.

A premise that never moves keeps `occupancy_id == customer_id`, so this layer is byte-identical to
today for every household whose occupancy outlives the run.

THE RATE, AND WHY IT IS A PREMISE-TURNOVER RATE
-----------------------------------------------
The hazard is `simulation.arrival_route.home_move_rate_per_household_year(tenure)`: EHS 2024-25
move-ins into a tenure over households in it. A move-in at a dwelling is the end of the previous
occupancy there, so per dwelling the move-in rate IS the occupancy turnover rate. It is imported,
not restated: one source, one number. It is a LOWER bound (that function's reconciliation carries
the 0.18m of the 1.8m headline that EHS does not break out by tenure).

GAPS CARRIED, NOT FILLED (each would be a number picked because a number was needed)
-------------------------------------------------------------------------------------
  - VOID LENGTH. No published domestic void-period length (`home_moves.md` §2.4). The incoming
    occupancy's `start_date` is therefore `None`, bounded below by the move-out date, with the
    reason on the object. Downstream may not bill it from a guessed date.
  - SEASONALITY. No official monthly series of moves (§2.2). The move date is drawn uniformly over
    the year — the no-information case, named as a simplification, not a finding.
  - ENDED AND NEW HOUSEHOLDS. 17% of EHS moves are new households (no vacated dwelling behind
    them), and the count of ended households is unpublished (§2.1). This slice always pairs the
    vacated leg with a mover leg, so it neither creates new households nor ends any.

RNG DISCIPLINE (C-S2)
---------------------
Every draw is on a NAMED substream under the `customer_state` namespace, keyed on the premise and
occupancy it concerns — never sequential, never the bare `f"{seed}:{name}"` key `life_events.py`
uses. Onset (`move_hazard`) and the date (`move_date`) are separate streams, so changing how the date
is drawn cannot change WHICH occupancies move. `SUBSTREAMS` is the registry; a draw from an
unregistered name raises rather than falling back to a shared generator.

WALL. Everything here is ground truth. The move date, the occupancy ids and the void are exactly
what a supplier cannot see; the seam that will let the company see the shadows (a final read, a
cancelled DD, settled volume at a premise with nobody contracted) is a later slice.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import math
import random
from dataclasses import dataclass
from typing import Optional

from simulation.arrival_route import (
    ARRIVAL_DEFAULT_TARIFF_TYPE,
    home_move_rate_per_household_year,
)
from simulation.final_bill_outcome import FinalBillExposure, open_final_bill_exposure
from simulation.household_segments import TenureType

NAMESPACE = "customer_state"

#: Every substream this layer may draw from. Adding a name must leave every other stream's draws
#: byte-identical — the key includes the name, so it does.
SUBSTREAMS: tuple[str, ...] = ("move_hazard", "move_date", "move_destination", "incoming_occupant")

#: The legal relationship both entries start on. Not a product label: the PRODUCT a deemed arrival
#: is priced on is `ARRIVAL_DEFAULT_TARIFF_TYPE` (see `simulation/arrival_route.py` on why that
#: is the default tariff and not this world's spot-plus `deemed` product).
DEEMED_TERMS = "deemed_contract"

VOID_GAP_UNKNOWN_REASON = (
    "no published domestic void-period length (docs/market_research/home_moves.md §2.4); the "
    "incoming occupancy starts no earlier than the move-out date and its start is not drawn"
)


def _substream(base_seed: int, stream: str, *key: str) -> random.Random:
    if stream not in SUBSTREAMS:
        raise KeyError(f"{stream!r} is not a registered {NAMESPACE} substream: {SUBSTREAMS}")
    material = ":".join((NAMESPACE, stream, str(base_seed), *key))
    digest = hashlib.sha256(material.encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _derived_id(prefix: str, base_seed: int, stream: str, *key: str) -> str:
    return f"{prefix}-{_substream(base_seed, stream, *key).getrandbits(48):012x}"


@dataclass(frozen=True)
class Occupancy:
    """A liable household at a premise. The default occupancy of a drawn customer is the customer."""

    premise_id: str
    occupancy_id: str
    tenure: TenureType

    @classmethod
    def of_customer(cls, customer_id: str, tenure: TenureType,
                    premise_id: Optional[str] = None) -> "Occupancy":
        return cls(premise_id=premise_id or customer_id, occupancy_id=customer_id, tenure=tenure)


@dataclass(frozen=True)
class OccupancyEnded:
    """The credit exit: liability for `occupancy_id` at `premise_id` ends on `end_date`."""

    premise_id: str
    occupancy_id: str
    end_date: dt.date

    def final_bill_exposure(self, account_id: str, fuel: str,
                            net_balance_gbp: float) -> FinalBillExposure:
        return open_final_bill_exposure(
            account_id=account_id, supply_point_id=self.premise_id, fuel=fuel,
            closure_date=self.end_date, net_balance_gbp=net_balance_gbp,
            customer_id=self.occupancy_id,
        )


@dataclass(frozen=True)
class OccupancyStarted:
    """A deemed entry. `start_date` is None when it is a GAP; `starts_no_earlier_than` always holds."""

    premise_id: str
    occupancy_id: str
    starts_no_earlier_than: dt.date
    start_date: Optional[dt.date]
    start_date_unknown_reason: Optional[str]
    terms: str = DEEMED_TERMS
    tariff_type: str = ARRIVAL_DEFAULT_TARIFF_TYPE


@dataclass(frozen=True)
class HomeMove:
    move_date: dt.date
    vacated: OccupancyEnded
    incoming: OccupancyStarted
    mover_arrives: OccupancyStarted
    data_regime: str = "synthetic"

    @property
    def transitions(self) -> tuple:
        return (self.vacated, self.incoming, self.mover_arrives)


def move_hazard_per_year(tenure: TenureType) -> float:
    if not isinstance(tenure, TenureType):
        raise TypeError(f"tenure must be a TenureType, got {tenure!r}")
    rate = home_move_rate_per_household_year(tenure)
    if not (isinstance(rate, float) and math.isfinite(rate) and 0.0 < rate < 1.0):
        raise ValueError(f"move hazard for {tenure.value} is not a probability: {rate!r}")
    return rate


def draw_home_move(occupancy: Occupancy, year: int, base_seed: int) -> Optional[HomeMove]:
    """Whether `occupancy` moves out during `year`, and the three transitions if it does."""
    hazard = move_hazard_per_year(occupancy.tenure)
    key = (occupancy.premise_id, occupancy.occupancy_id, str(year))
    if _substream(base_seed, "move_hazard", *key).random() >= hazard:
        return None

    first = dt.date(year, 1, 1)
    days_in_year = (dt.date(year + 1, 1, 1) - first).days
    move_date = first + dt.timedelta(days=_substream(base_seed, "move_date", *key).randrange(days_in_year))

    new_premise = _derived_id("PREM", base_seed, "move_destination", *key)
    incoming_id = _derived_id("OCC", base_seed, "incoming_occupant", *key)
    return HomeMove(
        move_date=move_date,
        vacated=OccupancyEnded(occupancy.premise_id, occupancy.occupancy_id, move_date),
        incoming=OccupancyStarted(
            premise_id=occupancy.premise_id, occupancy_id=incoming_id,
            starts_no_earlier_than=move_date, start_date=None,
            start_date_unknown_reason=VOID_GAP_UNKNOWN_REASON,
        ),
        mover_arrives=OccupancyStarted(
            premise_id=new_premise, occupancy_id=occupancy.occupancy_id,
            starts_no_earlier_than=move_date, start_date=move_date,
            start_date_unknown_reason=None,
        ),
    )
