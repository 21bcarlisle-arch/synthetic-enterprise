"""The move-out notice seam -- our household telling us it stops occupying its premises on a date.

WHAT CROSSES: one notice per supply point the household holds with us: the point, the date it stops
occupying the premises, and the day it told us. Nothing else. That is the minimal honest observable
of `docs/market_research/home_moves.md` s.8.2: the customer is identified on contact, the date is
the content of the notice, and when it arrived is the supplier's own contact record.

ITS CLOCK IS THE LICENCE'S, NOT A CHOSEN LEAD TIME. SLC 24.1(a) ends a domestic contract on the
move date "if the Domestic Customer has notified the licensee at least two Working Days before" it.
The world ends a mover's liability on the move date (`run_phase2b`, `term_window_under_move`), so it
has already decided that every mover notified in time, and the LATEST notice consistent with that is
two Working Days before the move (s.8.1). `notified_on` is that day: the least warning a supplier
gets from a customer who notifies in time, so it cannot flatter a retention offer.

WHAT DOES NOT CROSS, AND WHY EACH IS ABSENT RATHER THAN NONE:
  * The destination premise. A household names it only if it chooses to, no industry flow links
    the two premises, and the share who tell is not published (s.8.5 G8.2). No field, so nothing
    can read a destination the supplier was never given (`GAPS["destination"]`).
  * Why they move, their tenure, who moves in next, whether the home will stand empty (s.8.2).
  * A forwarding address and a final read: real, sometimes given, unsized (`GAPS`).

UNSOLICITED BY CONSTRUCTION: the household tells its supplier; the supplier does not ask. So the
only envelope specialisation is a `WallNotification`.

NO SIM/GENERATOR/COMPANY SYMBOL: pure contract, checked by
`tests/interface/test_move_out_notice_seam.py`.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from interface.contracts.wall_envelope import WallNotification

# First release numbered 2: dialect 1 has no notification (`registration_loss_seam` says why).
SCHEMA_VERSION = 2

#: The household's own contact with its supplier about a move. Its own stream, apart from the
#: disclosure channel (`psr_registration_seam`), because `sequence` is a position in ONE sender's
#: stream and the two are produced independently.
MOVE_OUT_SENDER = "HOUSEHOLD-MOVE-CONTACT-01"
MOVE_OUT_NOTIFICATION_TYPE = "domestic_move_out_notice"

#: SLC 24.1(a): "at least two Working Days before the date on which he stops owning or occupying".
NOTICE_WORKING_DAYS = 2


@dataclass(frozen=True)
class MoveOutNotice:
    """`supply_point_id` is the company's own key for the meter point (this world mints no MPxNs;
    `registration_loss_seam.RegistrationLossNotice` says why that plays the MPxN's part).
    `move_out_date` is the first day the household no longer occupies the premises, the day its
    contract ends under SLC 24.1(a). `notified_on` is the day it told us."""

    supply_point_id: str
    move_out_date: dt.date
    notified_on: dt.date


MoveOutWallNotification = WallNotification[MoveOutNotice]

UNSOLICITED_PAYLOAD_TYPES: tuple[type, ...] = (MoveOutNotice,)

OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "MoveOutNotice": ("supply_point_id", "move_out_date", "notified_on"),
}

#: World truth that must never ride on a notice: the spellings `sim/customer_state_layer.py` and
#: the run loop use for the move's hidden facts.
FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = (
    "mover_arrives",
    "move_destination",
    "premise_id",
    "occupancy_id",
    "incoming",
    "tenure",
    "void_days",
    "household",
)

GAPS: dict[str, str] = {
    "destination": (
        "Whether a mover names its destination, and how often, is not published "
        "(home_moves.md s.8.5 G8.2). The notice has no destination field."
    ),
    "late_or_no_notice": (
        "Movers who notify late or never (SLC 24.1(b)) are real and unsized (OFG1164 2.2, 2.4, "
        "2.8; s.8.5 G8.1). The world draws none, so every notice is on time; when they are "
        "sourced, a late notice moves the liability end too, not only this date."
    ),
    "lead_time": (
        "Every notice is dated at the latest the licence allows. A household that tells its "
        "supplier weeks ahead gives more warning; the lead-time distribution is not published."
    ),
    "bank_holidays": (
        "Working Days here are Monday to Friday. Counting a bank holiday as a Working Day dates "
        "the notice later than a real one could be, so it can only shorten the warning."
    ),
    "forwarding_address_and_final_read": (
        "Sometimes given on the notice (s.8.2); the shares are not published. Not carried."
    ),
}


def _is_working_day(day: dt.date) -> bool:
    """Monday to Friday (`GAPS["bank_holidays"]`)."""
    return day.weekday() < 5


def latest_notice_date(move_out_date: dt.date) -> dt.date:
    """The latest day a household can tell us and still end its contract on `move_out_date`
    under SLC 24.1(a): the second Working Day before it."""
    day, counted = move_out_date, 0
    while counted < NOTICE_WORKING_DAYS:
        day -= dt.timedelta(days=1)
        if _is_working_day(day):
            counted += 1
    return day


def notice_observed_at(notified_on: dt.date) -> dt.datetime:
    """When the supplier learns of it: the day it is given, because the notice is the household's
    own contact with the supplier."""
    return dt.datetime.combine(notified_on, dt.time())
