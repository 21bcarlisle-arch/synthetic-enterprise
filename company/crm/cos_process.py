from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping, Optional

from company.interfaces.wall_protocol import decode_framed_notification
from interface.contracts.registration_loss_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    LOSS_NOTICE_SENDERS,
    LOSS_NOTIFICATION_TYPES,
    OBSERVABLE_PAYLOAD_FIELDS,
    PENDING_NOTIFICATION_TYPES,
    RegistrationLossNotice,
)
from interface.contracts.registration_loss_seam import (
    UNSOLICITED_PAYLOAD_TYPES as _LOSS_PAYLOAD_TYPES,
)
from interface.contracts.wall_envelope import WallNotification


class CoSStage(str, Enum):
    SWITCH_REQUESTED = "switch_requested"
    OBJECTION_WINDOW = "objection_window"   # losing supplier can object (cooling off)
    OBJECTION_CLEARED = "objection_cleared"
    FINAL_READ_REQUESTED = "final_read_requested"
    FINAL_READ_RECEIVED = "final_read_received"
    SWITCH_COMPLETE = "switch_complete"
    OBJECTED = "objected"
    CANCELLED = "cancelled"


class ObjectionReason(str, Enum):
    DEBT = "debt"
    CONTRACT_IN_FORCE = "contract_in_force"
    COOLING_OFF_PERIOD = "cooling_off_period"
    CUSTOMER_CANCELLED = "customer_cancelled"


@dataclass(frozen=True)
class CoSEvent:
    event_id: str
    account_id: str
    stage: CoSStage
    event_date: str
    gaining_supplier: Optional[str] = None
    losing_supplier: Optional[str] = None
    final_read_kwh: Optional[float] = None
    objection_reason: Optional[ObjectionReason] = None


class CoSProcess:
    """Tracks one Change of Supplier process for a single account."""

    def __init__(self, account_id: str, requested_date: str,
                 gaining_supplier: Optional[str], losing_supplier: str, *,
                 opening_stage: CoSStage = CoSStage.SWITCH_REQUESTED,
                 supply_effective_from: Optional[str] = None,
                 registration_ref: Optional[str] = None) -> None:
        """`opening_stage` is the first stage this supplier has evidence of, dated
        `requested_date`. A GAINER opens at SWITCH_REQUESTED because it sent the
        request; a LOSER opens wherever its first notice puts it and never knows the
        request date. `gaining_supplier` is None when nothing told us who it is."""
        self.account_id = account_id
        self.gaining_supplier = gaining_supplier
        self.losing_supplier = losing_supplier
        self.supply_effective_from = supply_effective_from
        self.registration_ref = registration_ref
        self._events: list[CoSEvent] = []
        self._record(opening_stage, requested_date)

    def _record(self, stage: CoSStage, date: str,
                final_read: Optional[float] = None,
                reason: Optional[ObjectionReason] = None) -> CoSEvent:
        ev = CoSEvent(
            event_id=f"{self.account_id}_{len(self._events)}",
            account_id=self.account_id, stage=stage, event_date=date,
            gaining_supplier=self.gaining_supplier,
            losing_supplier=self.losing_supplier,
            final_read_kwh=final_read, objection_reason=reason,
        )
        self._events.append(ev)
        return ev

    @property
    def current_stage(self) -> CoSStage:
        return self._events[-1].stage if self._events else CoSStage.SWITCH_REQUESTED

    @property
    def is_complete(self) -> bool:
        return self.current_stage == CoSStage.SWITCH_COMPLETE

    @property
    def is_objected(self) -> bool:
        return self.current_stage == CoSStage.OBJECTED

    @property
    def is_cancelled(self) -> bool:
        return self.current_stage == CoSStage.CANCELLED

    def clear_objection_window(self, date: str) -> CoSEvent:
        return self._record(CoSStage.OBJECTION_CLEARED, date)

    def object_to_switch(self, date: str, reason: ObjectionReason) -> CoSEvent:
        return self._record(CoSStage.OBJECTED, date, reason=reason)

    def request_final_read(self, date: str) -> CoSEvent:
        return self._record(CoSStage.FINAL_READ_REQUESTED, date)

    def receive_final_read(self, date: str, kwh: float) -> CoSEvent:
        return self._record(CoSStage.FINAL_READ_RECEIVED, date, final_read=kwh)

    def complete(self, date: str) -> CoSEvent:
        return self._record(CoSStage.SWITCH_COMPLETE, date)

    def cancel(self, date: str) -> CoSEvent:
        return self._record(CoSStage.CANCELLED, date)


#: How this company names itself as the losing party on a process it did not open.
THIS_SUPPLIER = "this_supplier"


def decode_loss_payload(raw: Any) -> RegistrationLossNotice:
    """A registration-loss notice off the wire, or a refusal that says why.

    THE COMPANY'S BELT: a field the contract forbids is refused BEFORE the closed-set
    check, so a leak is named as a leak rather than as an unexpected key."""
    if not isinstance(raw, Mapping):
        raise ValueError(f"registration-loss payload must be a mapping, got {type(raw).__name__}")
    leaking = sorted(set(raw) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise ValueError(f"registration-loss notice carries world truth: {leaking}")
    expected = set(OBSERVABLE_PAYLOAD_FIELDS["RegistrationLossNotice"])
    if set(raw) != expected:
        raise ValueError(
            f"registration-loss payload fields {sorted(raw)} are not the contract's "
            f"{sorted(expected)}"
        )
    for name in ("registration_ref", "supply_point_id", "supply_effective_from_date"):
        if not isinstance(raw[name], str) or not raw[name]:
            raise ValueError(f"registration-loss payload {name} must be a non-empty string")
    return RegistrationLossNotice(
        registration_ref=raw["registration_ref"],
        supply_point_id=raw["supply_point_id"],
        supply_effective_from_date=dt.date.fromisoformat(raw["supply_effective_from_date"]),
    )


def read_loss_wire(wire: Any) -> WallNotification:
    """TRANSPORT ONLY: a framed registration-loss message, authenticated, version-checked and
    decoded, from a sender that is a registration service. It holds no book, so it cannot ask
    whether this supplier holds the point the notice names -- `CoSRegister.receive_loss_wire`
    is the reader that can, and the one a caller should use
    (`tools/wall_channel_census.py::ANCHORED_FEEDS`).

    A sender the registry knows but that is not a registration service (the Bacs bureau, say)
    is refused: only those services can tell us a registration ended."""
    sender, notification = decode_framed_notification(wire, decode_payload=decode_loss_payload)
    if sender not in LOSS_NOTICE_SENDERS:
        raise ValueError(
            f"CoSRegister: {sender!r} is not a registration service, so it cannot tell "
            "this supplier it lost a registration"
        )
    return notification


#: Why a loss notice was held as an exception rather than filed as a loss.
NOT_ON_THIS_BOOK = "no registration on this supplier's book"


class CoSRegister:
    def __init__(self, holds: Optional[Callable[[str], bool]] = None) -> None:
        """`holds(supply_point_id)` answers "is this point registered to us?" from the
        supplier's own book. It is ASKED WHEN A NOTICE ARRIVES, not captured at opening,
        because points are acquired mid-run. A register opened without it can open switches
        but refuses to file a loss (`_admit_loss`)."""
        self._processes: dict[str, list[CoSProcess]] = {}
        self._loss_notice_ids: set[tuple[str, str]] = set()
        self._holds = holds
        self._loss_exceptions: list[dict] = []
        self._pending_notices: list[dict] = []

    def receive_loss_wire(self, wire: Any) -> bool:
        """A framed registration-loss message as a registration service hands it over:
        read by `read_loss_wire`, then admitted against this supplier's own book."""
        notification = read_loss_wire(wire)
        if not self._admit_loss(notification):
            return False
        self._file(notification)
        return True

    def receive_loss_notice(self, notification: WallNotification) -> bool:
        """File a registration-loss notice (`interface/contracts/registration_loss_seam`).

        Returns False for a redelivery of a notice already filed, keyed on the
        sender's own (sender, notification_id) -- the stream is at-least-once --
        and for a notice naming a point this supplier does not hold, which is
        kept in `loss_exceptions()` instead.

        The process opens at OBJECTION_CLEARED, dated when the notice was observed:
        a Secured Inactive notice is sent once the registration is past the point
        it could be cancelled, which it reaches only through a closed objection
        window. The gaining supplier is None because the notice does not name it.
        The switch stays in progress until a final read arrives, which no seam
        delivers yet.

        A PENDING notice (the Invitation to Intervene) is not a loss: the switch can
        still be cancelled. It is filed in `pending_switches_notified()` and opens no
        process. No decision reads it yet.
        """
        if not self._admit_loss(notification):
            return False
        self._file(notification)
        return True

    def _admit_loss(self, notification: WallNotification) -> bool:
        """THE BOOK'S QUESTION: may this notice be filed as a loss of ours?

        A real registration service sends a losing supplier notices only for its own
        registrations, so a notice for a point this supplier does not hold is an industry
        exception to be investigated, not a loss: it goes to `loss_exceptions()` and never
        opens a process. Asked AFTER the redelivery check, so a redelivered stray is one
        exception, not one per delivery."""
        if self._holds is None:
            raise ValueError(
                "CoSRegister: opened without the supply book, so it cannot tell whether this "
                "supplier holds the point a loss notice names -- open it with `holds=` "
                "(`company.interfaces.supply_book.open_change_of_supplier_register`)"
            )
        payload = notification.payload
        if not isinstance(payload, _LOSS_PAYLOAD_TYPES):
            raise ValueError(
                f"CoSRegister: {type(payload).__name__!r} is not a registration-loss "
                "notice -- see registration_loss_seam.UNSOLICITED_PAYLOAD_TYPES"
            )
        known = LOSS_NOTIFICATION_TYPES + PENDING_NOTIFICATION_TYPES
        if notification.notification_type not in known:
            raise ValueError(
                f"CoSRegister: notification_type {notification.notification_type!r} is neither "
                f"a loss {LOSS_NOTIFICATION_TYPES} nor a pending switch "
                f"{PENDING_NOTIFICATION_TYPES}, so it cannot be filed as either"
            )
        key = (notification.sender, notification.notification_id)
        if key in self._loss_notice_ids:
            return False
        self._loss_notice_ids.add(key)
        if not self._holds(payload.supply_point_id):
            self._loss_exceptions.append({
                "supply_point_id": payload.supply_point_id,
                "registration_ref": payload.registration_ref,
                "sender": notification.sender,
                "reason": NOT_ON_THIS_BOOK,
            })
            return False
        return True

    def _file(self, notification: WallNotification) -> None:
        if notification.notification_type in PENDING_NOTIFICATION_TYPES:
            self._file_pending(notification)
        else:
            self._file_loss(notification)

    def _file_loss(self, notification: WallNotification) -> None:
        payload = notification.payload
        proc = CoSProcess(
            payload.supply_point_id, notification.observed_at.date().isoformat(),
            None, THIS_SUPPLIER,
            opening_stage=CoSStage.OBJECTION_CLEARED,
            supply_effective_from=payload.supply_effective_from_date.isoformat(),
            registration_ref=payload.registration_ref,
        )
        self._processes.setdefault(payload.supply_point_id, []).append(proc)

    def _file_pending(self, notification: WallNotification) -> None:
        payload = notification.payload
        self._pending_notices.append({
            "supply_point_id": payload.supply_point_id,
            "registration_ref": payload.registration_ref,
            "supply_effective_from": payload.supply_effective_from_date.isoformat(),
            "notified_at": notification.observed_at.isoformat(),
        })

    def pending_switches_notified(self) -> list[dict]:
        """Every Invitation to Intervene this company has been sent, as it holds them."""
        return list(self._pending_notices)

    def loss_exceptions(self) -> list[dict]:
        """Loss notices this supplier was sent for points it does not hold."""
        return list(self._loss_exceptions)

    def losses_notified(self) -> list[dict]:
        """Every loss this company has been told of, as it holds them."""
        return [
            {
                "supply_point_id": p.account_id,
                "registration_ref": p.registration_ref,
                "supply_effective_from": p.supply_effective_from,
                "notified_on": p._events[0].event_date,
                "stage": p.current_stage.value,
            }
            for procs in self._processes.values() for p in procs
            if p.losing_supplier == THIS_SUPPLIER
        ]

    def open_switch(self, account_id: str, requested_date: str,
                    gaining: str, losing: str) -> CoSProcess:
        proc = CoSProcess(account_id, requested_date, gaining, losing)
        self._processes.setdefault(account_id, []).append(proc)
        return proc

    def active_for_account(self, account_id: str) -> list[CoSProcess]:
        return [p for p in self._processes.get(account_id, [])
                if not p.is_complete and not p.is_cancelled]

    def completed_switches(self) -> list[CoSProcess]:
        return [p for procs in self._processes.values() for p in procs if p.is_complete]

    def objected_switches(self) -> list[CoSProcess]:
        return [p for procs in self._processes.values() for p in procs if p.is_objected]

    def cos_summary(self) -> dict:
        all_procs = [p for procs in self._processes.values() for p in procs]
        return {
            "total_switches": len(all_procs),
            "completed": len(self.completed_switches()),
            "objected": len(self.objected_switches()),
            "in_progress": len([p for p in all_procs if not p.is_complete and not p.is_cancelled]),
        }
