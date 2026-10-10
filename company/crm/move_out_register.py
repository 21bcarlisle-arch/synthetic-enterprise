"""The supplier's register of move-out notices: our households telling us they are moving out.

REUSE: company/crm/move_out_register.py
CLASS: CUSTOM
INDEX: searched "move out", "home move", "notice", "register" under company/. `cos_process.CoSRegister`
       files the registration service's notices of a SWITCH; `PriorityServicesRegister` files a
       household's disclosure of a circumstance. A move-out notice is neither: it is the household
       ending its contract on a move (SLC 24.1(a)), the one moment a move-with-us offer can be made
       before it goes (home_moves.md s.8.4). Same shape as the PSR register (transport reader, then
       the book's question), its own register because its subject and its readers differ.

WHAT THE COMPANY HOLDS AFTER A NOTICE: the supply point, the move-out date and the day it was told
(`interface/contracts/move_out_notice_seam.py`). Not where the household is going: it was not told.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Callable, Mapping

from company.interfaces.wall_protocol import decode_framed_notification
from interface.contracts.move_out_notice_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    MOVE_OUT_NOTIFICATION_TYPE,
    MOVE_OUT_SENDER,
    OBSERVABLE_PAYLOAD_FIELDS,
    MoveOutNotice,
)

#: Why a notice was held as an exception rather than filed.
NOT_ON_THIS_BOOK = "no registration on this supplier's book"


def decode_move_out_payload(raw: Any) -> MoveOutNotice:
    """A move-out notice off the wire, or a refusal that says why. THE COMPANY'S BELT: a world-truth
    field is refused as a leak BEFORE the closed-set check."""
    if not isinstance(raw, Mapping):
        raise ValueError(f"move-out payload must be a mapping, got {type(raw).__name__}")
    leaking = sorted(set(raw) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise ValueError(f"move-out notice carries world truth: {leaking}")
    expected = set(OBSERVABLE_PAYLOAD_FIELDS["MoveOutNotice"])
    if set(raw) != expected:
        raise ValueError(f"move-out payload fields {sorted(raw)} are not the contract's "
                         f"{sorted(expected)}")
    return MoveOutNotice(supply_point_id=str(raw["supply_point_id"]),
                         move_out_date=date.fromisoformat(raw["move_out_date"]),
                         notified_on=date.fromisoformat(raw["notified_on"]))


def read_move_out_wire(wire: Any):
    """TRANSPORT ONLY: a framed notice, authenticated, version-checked and decoded, from the
    household move-contact channel only. It holds no book; `MoveOutRegister.receive_move_out_wire`
    is the reader that asks whether this supplier holds the point."""
    sender, notification = decode_framed_notification(wire, decode_payload=decode_move_out_payload)
    if sender != MOVE_OUT_SENDER or notification.notification_type != MOVE_OUT_NOTIFICATION_TYPE:
        raise ValueError(f"{sender!r}/{notification.notification_type!r} is not a household's "
                         "move-out notice, so it cannot end a contract on a move")
    return notification


class MoveOutRegister:
    """Every move-out notice this supplier has filed, by supply point."""

    def __init__(self, holds: Callable[[str], bool] | None = None) -> None:
        """`holds(supply_point_id)` answers "is this point registered to us?" from the supplier's
        own book when a notice arrives. Without it every notice is refused (`_admit`)."""
        self._holds = holds
        self._notices: list[MoveOutNotice] = []
        self._exceptions: list[dict] = []

    def receive_move_out_wire(self, wire: Any) -> MoveOutNotice | None:
        """A framed notice as the household's contact channel hands it over: read by
        `read_move_out_wire`, then admitted against this supplier's own book."""
        notification = read_move_out_wire(wire)
        if not self._admit(notification):
            return None
        self._notices.append(notification.payload)
        return notification.payload

    def _admit(self, notification) -> bool:
        """THE BOOK'S QUESTION: is the point this notice names one we supply? A notice for a point
        not on the book files nothing; it is kept in `exceptions()` with its reason."""
        if self._holds is None:
            raise ValueError("MoveOutRegister: opened without the supply book, so it cannot tell "
                             "whether this supplier holds the point a notice names -- open it "
                             "with `holds=` (`company.interfaces.supply_book.open_move_out_register`)")
        notice = notification.payload
        if not self._holds(notice.supply_point_id):
            self._exceptions.append({"supply_point_id": notice.supply_point_id,
                                     "notified_on": notice.notified_on.isoformat(),
                                     "reason": NOT_ON_THIS_BOOK})
            return False
        return True

    def notices(self) -> list[dict]:
        """Every filed notice, in arrival order, as the company holds it."""
        return [{"supply_point_id": n.supply_point_id,
                 "move_out_date": n.move_out_date.isoformat(),
                 "notified_on": n.notified_on.isoformat()} for n in self._notices]

    def notice_for(self, supply_point_id: str, move_out_date: str) -> MoveOutNotice | None:
        """The notice held for this point and move date, or None."""
        held = [n for n in self._notices if n.supply_point_id == supply_point_id
                and n.move_out_date.isoformat() == move_out_date]
        return held[-1] if held else None

    def exceptions(self) -> list[dict]:
        """Notices received for points this supplier does not hold."""
        return list(self._exceptions)
