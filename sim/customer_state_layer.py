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

THE RUN (slice 2)
----------------
`run_phase2b` asks `first_move_out` once per domestic household, at its first term, over the
household's own supply window, and `term_window_under_move` then cuts the term the move falls in at
the move date and drops every later term. The move goes on the churn journey as
`HOME_MOVE_CHURNED`, which is the only state `is_catchable()` excludes and which nothing set until
now. It is NOT a registration loss: the supplier keeps the premise on deemed terms. That incoming
leg is not yet supplied in the run, so with the layer on the premise simply stops — which is why
`moves_active()` reads a curriculum file that defaults OFF (whether this world has moves is the
director's), and why it should stay off until the incoming deemed leg exists.

THE CHANGE-OF-TENANCY GAP (W2_36 slice 3)
-----------------------------------------
Unbilled-energy kind K4's "unknown occupier" part
(`docs/market_research/unbilled_energy_and_revenue_assurance.md` §2 K4). From the move date the
meter goes on recording, and the supplier stays registered and settles what it records, but nobody
named is liable until the incoming occupier is identified. `unnamed_kwh_after_move` is that energy.
It is the energy itself. Whether "the occupier" is later billed for it and pays is the debt side's
question, not this one's.

Two quantities are unpublished, and neither is typed here:
  - HOW LONG the premise stays unnamed. Only the expected product, P(not named by move day) times
    mean months to name, is bounded by evidence. It is the register's `q1_unnamed_months_per_cot`
    (derived from Energy UK's CoT-debt figure), so the window is that EXPECTATION and is not drawn
    per move. The total is right in expectation, and the per-move spread is not modelled.
  - WHAT THE PREMISE USES while unnamed. The void-or-occupied split and void consumption are a gap
    (`home_moves.md` §2.4). The rate is the meter point's own annual quantity (gas AQ, electricity
    EAC). In the industry those attach to the meter point and survive a change of tenancy, and the
    toggle was derived as months of an average-year bill. The leaving household's final term is
    the wrong basis: it reads one season, and at 2016 inputs a January-April gas term put 5,036 kWh
    on an April-July window.
In the run, this energy is neither settled to nor billed by the company yet, because the premise
stops at the move. Supplying the incoming deemed leg is B7 slice 3, and that is where its cost lands.

WALL. Everything here is ground truth. The move date, the occupancy ids and the void are exactly
what a supplier cannot see; the seam that will let the company see the shadows (a final read, a
cancelled DD, settled volume at a premise with nobody contracted) is a later slice.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from simulation.arrival_route import (
    ARRIVAL_DEFAULT_TARIFF_TYPE,
    home_move_rate_per_household_year,
)
from simulation.final_bill_outcome import FinalBillExposure, open_final_bill_exposure
from simulation.household import GAS_LEG_ID_SUFFIX
from simulation.household_segments import TenureType, tenure_for_customer
from simulation.meter_reads import assumption_toggle

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


ACTIVATION_PATH = (Path(__file__).resolve().parents[1]
                   / "docs" / "design" / "curriculum" / "home_moves_activation.json")


def moves_active(path: Path = ACTIVATION_PATH) -> bool:
    """Whether the run draws home moves. A missing file or a non-bool value raises: on or off is
    the director's, and neither may be inferred from a file that does not say."""
    value = json.loads(Path(path).read_text())["activated"]["value"]
    if not isinstance(value, bool):
        raise ValueError(f"{path}: activated.value must be true or false, got {value!r}")
    return value


def first_move_out(occupancy: Occupancy, supply_start: dt.date, supply_end: dt.date,
                   base_seed: int) -> Optional[HomeMove]:
    """The first move strictly inside (supply_start, supply_end), or None.

    Each year's draw is the slice-1 draw unchanged, so a household's moves do not depend on the
    window it is asked over. A move drawn on or before `supply_start` happened before this
    supplier held the account and is not a departure from the book.
    """
    if supply_end <= supply_start:
        raise ValueError(f"empty supply window {supply_start} .. {supply_end}")
    for year in range(supply_start.year, supply_end.year + 1):
        move = draw_home_move(occupancy, year, base_seed)
        if move is not None and supply_start < move.move_date < supply_end:
            return move
    return None


def term_window_under_move(term_start: dt.date, term_end: dt.date,
                           move_out: Optional[dt.date]) -> tuple[Optional[dt.date], bool]:
    """(the term's end once the move is applied, whether the move falls inside this term).

    `term_end` and `move_out` are both EXCLUSIVE: the move date is the first day the mover is not
    liable, the same day the incoming occupancy may start. A term starting on or after the move
    is not supplied to this occupancy at all, which returns (None, False).
    """
    if move_out is None or move_out >= term_end:
        return term_end, False
    if move_out <= term_start:
        return None, False
    return move_out, True


def account_move_out(customer: Optional[dict], supply_start: dt.date, supply_end: dt.date,
                     base_seed: int) -> Optional[HomeMove]:
    """The run's question for one account record. Domestic only: a business site does not move
    home, and an account with no record has no tenure to draw a hazard from."""
    if customer is None or customer.get("segment", "resi") != "resi":
        return None
    cid = customer["customer_id"]
    return first_move_out(Occupancy.of_customer(cid, tenure_for_customer(cid)),
                          supply_start, supply_end, base_seed)



def unnamed_months_per_move(setting: str = "default") -> float:
    """Expected months a vacated premise is supplied with nobody named liable: the register's
    `q1_unnamed_months_per_cot`, read at `setting` (`default`, `low` or `high`)."""
    months = assumption_toggle("q1_unnamed_months_per_cot", setting)
    if not (math.isfinite(months) and months >= 0.0):
        raise ValueError(f"q1_unnamed_months_per_cot[{setting}] is not a duration: {months!r}")
    return months


def unnamed_kwh_after_move(annual_kwh: Optional[float],
                           setting: str = "default") -> Optional[float]:
    """Expected kWh used at the vacated premise from the move date until someone is named.

    `annual_kwh` is the meter point's annual quantity. With no annual quantity there is no rate,
    so the answer is None rather than zero: a zero would read as "no gap".
    """
    if annual_kwh is None or not math.isfinite(annual_kwh) or annual_kwh <= 0.0:
        return None
    return annual_kwh / 12.0 * unnamed_months_per_move(setting)


def incoming_leg_id(incoming_occupancy_id: str, vacated_supply_point_id: str) -> str:
    """The incoming occupant's account id for one fuel leg at the vacated premise. The gas leg
    keeps the gas suffix, so `household_of` groups the incoming household's two legs as one."""
    if vacated_supply_point_id.endswith(GAS_LEG_ID_SUFFIX):
        return incoming_occupancy_id + GAS_LEG_ID_SUFFIX
    return incoming_occupancy_id


def incoming_occupant_record(vacated_leg: dict, move: HomeMove) -> dict:
    """B7 slice 3: the account the vacated leg is supplied under from the move date.

    The meter point, its annual quantity and the dwelling are the premise's and are copied. The
    account, the occupancy and the terms are new: a deemed contract on the default tariff.

    SUPPLY starts on the move date, while the OCCUPANCY start stays unknown. The supplier stays
    registered and the meter keeps recording through any void. In a void the owner is the
    deemed customer, so there is no day on which the premise is unsupplied. Who is liable, and
    when they are named, is the change-of-tenancy gap (`unnamed_kwh_after_move`). It is not a
    gap in supply.

    The record goes on the supplier's book, so it carries only what registration tells a
    supplier: the meter point, the date and the terms. The mover's identity, the void and the
    unknown occupancy start are not on it.
    """
    record = dict(vacated_leg)
    record.pop("successor_of", None)
    record.update(
        customer_id=incoming_leg_id(move.incoming.occupancy_id, vacated_leg["customer_id"]),
        occupancy_id=move.incoming.occupancy_id,
        incoming_occupant_of=vacated_leg["customer_id"],
        acquisition_date=move.move_date.isoformat(),
        acquisition_type="change_of_tenancy",
        terms=move.incoming.terms,
        tariff_type=move.incoming.tariff_type,
        data_regime=move.data_regime,
    )
    return record
