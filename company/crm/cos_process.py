from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional

from company.interfaces.wall_protocol import decode_framed_notification
from interface.contracts.registration_loss_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    LOSS_NOTICE_SENDERS,
    OBSERVABLE_PAYLOAD_FIELDS,
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


class CoSRegister:
    def __init__(self) -> None:
        self._processes: dict[str, list[CoSProcess]] = {}
        self._loss_notice_ids: set[tuple[str, str]] = set()

    def receive_loss_wire(self, wire: Any) -> bool:
        """A framed registration-loss message as a registration service hands it over:
        authenticated, version-checked, decoded, then filed by `receive_loss_notice`.

        A sender the registry knows but that is not a registration service (the Bacs
        bureau, say) is refused: only those services can tell us a registration ended."""
        sender, notification = decode_framed_notification(wire, decode_payload=decode_loss_payload)
        if sender not in LOSS_NOTICE_SENDERS:
            raise ValueError(
                f"CoSRegister: {sender!r} is not a registration service, so it cannot tell "
                "this supplier it lost a registration"
            )
        return self.receive_loss_notice(notification)

    def receive_loss_notice(self, notification: WallNotification) -> bool:
        """File a registration-loss notice (`interface/contracts/registration_loss_seam`).

        Returns False for a redelivery of a notice already filed, keyed on the
        sender's own (sender, notification_id) -- the stream is at-least-once.

        The process opens at OBJECTION_CLEARED, dated when the notice was observed:
        a Secured Inactive notice is sent once the registration is past the point
        it could be cancelled, which it reaches only through a closed objection
        window. The gaining supplier is None because the notice does not name it.
        The switch stays in progress until a final read arrives, which no seam
        delivers yet.
        """
        payload = notification.payload
        if not isinstance(payload, _LOSS_PAYLOAD_TYPES):
            raise ValueError(
                f"CoSRegister: {type(payload).__name__!r} is not a registration-loss "
                "notice -- see registration_loss_seam.UNSOLICITED_PAYLOAD_TYPES"
            )
        key = (notification.sender, notification.notification_id)
        if key in self._loss_notice_ids:
            return False
        self._loss_notice_ids.add(key)
        proc = CoSProcess(
            payload.supply_point_id, notification.observed_at.date().isoformat(),
            None, THIS_SUPPLIER,
            opening_stage=CoSStage.OBJECTION_CLEARED,
            supply_effective_from=payload.supply_effective_from_date.isoformat(),
            registration_ref=payload.registration_ref,
        )
        self._processes.setdefault(payload.supply_point_id, []).append(proc)
        return True

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
