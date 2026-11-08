"""Supplier switching request tracking.

UK energy switching uses the Data Transfer Network (DTN) / MPAS/Xoserve systems.
When a customer initiates a switch, the gaining supplier submits a Supply Point
Registration. The losing supplier has 10 working days to object. If no objection,
the switch completes on the requested transfer date.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal


_OBJECTION_WINDOW_DAYS = 14


@dataclass
class SwitchRequest:
    reference: str
    customer_id: str
    commodity: Literal["electricity", "gas"]
    direction: Literal["gain", "loss"]
    mpan_or_mprn: str
    requested_transfer_date: str
    submitted_date: str
    status: Literal["pending", "completed", "objected", "withdrawn"] = "pending"
    objection_reason: str = ""
    completed_date: str = ""
    gaining_supplier: str = ""
    losing_supplier: str = ""

    @property
    def objection_deadline(self) -> str:
        d = date.fromisoformat(self.submitted_date)
        return (d + timedelta(days=_OBJECTION_WINDOW_DAYS)).isoformat()

    @property
    def is_objectable(self) -> bool:
        today_str = date.today().isoformat()
        return self.status == "pending" and today_str <= self.objection_deadline


class SwitchingBook:
    def __init__(self):
        self._requests: list[SwitchRequest] = []

    def record(self, request: SwitchRequest) -> SwitchRequest:
        self._requests.append(request)
        return request

    def complete(self, reference: str, completed_date: str) -> bool:
        for r in self._requests:
            if r.reference == reference:
                r.status = "completed"
                r.completed_date = completed_date
                return True
        return False

    def object_to(self, reference: str, reason: str) -> bool:
        for r in self._requests:
            if r.reference == reference and r.is_objectable:
                r.status = "objected"
                r.objection_reason = reason
                return True
        return False

    def withdraw(self, reference: str) -> bool:
        for r in self._requests:
            if r.reference == reference and r.status == "pending":
                r.status = "withdrawn"
                return True
        return False

    def pending(self):
        return [r for r in self._requests if r.status == "pending"]

    def gains(self):
        return [r for r in self._requests if r.direction == "gain"]

    def losses(self):
        return [r for r in self._requests if r.direction == "loss"]

    def pending_losses(self):
        return [r for r in self._requests if r.direction == "loss" and r.status == "pending"]

    def completed_gains(self):
        return [r for r in self._requests if r.direction == "gain" and r.status == "completed"]

    def completed_losses(self):
        return [r for r in self._requests if r.direction == "loss" and r.status == "completed"]

    def switching_summary(self) -> dict:
        gc = len(self.completed_gains())
        lc = len(self.completed_losses())
        return {
            "total": len(self._requests),
            "gains_pending": sum(1 for r in self.gains() if r.status == "pending"),
            "gains_completed": gc,
            "losses_pending": len(self.pending_losses()),
            "losses_completed": lc,
            "objected": sum(1 for r in self._requests if r.status == "objected"),
            "withdrawn": sum(1 for r in self._requests if r.status == "withdrawn"),
            "net_completed": gc - lc,
        }
