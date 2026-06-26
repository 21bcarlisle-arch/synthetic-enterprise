from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


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
                 gaining_supplier: str, losing_supplier: str) -> None:
        self.account_id = account_id
        self.gaining_supplier = gaining_supplier
        self.losing_supplier = losing_supplier
        self._events: list[CoSEvent] = []
        self._record(CoSStage.SWITCH_REQUESTED, requested_date)

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


class CoSRegister:
    def __init__(self) -> None:
        self._processes: dict[str, list[CoSProcess]] = {}

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
