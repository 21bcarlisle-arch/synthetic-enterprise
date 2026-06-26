"""Data Transfer Network (DTN) message log.

UK energy market participants exchange standardised industry messages via the DTN.
Key electricity flows: D0001 (meter read), D0150 (registration), D0301Z (switch
request), D0205 (query meter read), D0010 (EAC/AA update), D0052 (data aggregation).
Key gas flows: 806/814/816 (switching/read/query).

This module logs inbound and outbound DTN messages. The company layer only observes
message types and timestamps it would receive in real operations — it cannot see
simulation internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


_KNOWN_FLOWS = {
    # Electricity DTN flows (D-series)
    "D0001": "Meter read file",
    "D0002": "Change of agent",
    "D0010": "EAC / AA update",
    "D0052": "Aggregated meter data",
    "D0055": "Data aggregation run",
    "D0150": "Supply point registration",
    "D0205": "Query meter read",
    "D0301Z": "Supply point switch request",
    # Gas DTN flows
    "806": "Gas supply point query",
    "814": "Gas meter read",
    "816": "Gas site visit report",
    "826": "Gas supply point registration",
}


@dataclass
class DtnMessage:
    flow_id: str           # e.g. "D0001"
    direction: str         # "inbound" or "outbound"
    timestamp: str
    mpan_or_mprn: str = ""
    customer_id: str = ""
    status: str = "received"  # received / processed / rejected / pending
    notes: str = ""

    @property
    def flow_description(self) -> str:
        return _KNOWN_FLOWS.get(self.flow_id, f"Unknown flow ({self.flow_id})")


class DtnLog:
    """In-memory log of DTN messages received and sent."""

    def __init__(self):
        self._messages: list[DtnMessage] = []

    def record(self, msg: DtnMessage) -> DtnMessage:
        self._messages.append(msg)
        return msg

    def inbound(self) -> list[DtnMessage]:
        return [m for m in self._messages if m.direction == "inbound"]

    def outbound(self) -> list[DtnMessage]:
        return [m for m in self._messages if m.direction == "outbound"]

    def by_flow(self, flow_id: str) -> list[DtnMessage]:
        return [m for m in self._messages if m.flow_id == flow_id]

    def for_customer(self, customer_id: str) -> list[DtnMessage]:
        return [m for m in self._messages if m.customer_id == customer_id]

    def rejected(self) -> list[DtnMessage]:
        return [m for m in self._messages if m.status == "rejected"]

    def summary(self) -> dict:
        from collections import Counter
        flow_counts = Counter(m.flow_id for m in self._messages)
        return {
            "total": len(self._messages),
            "inbound": len(self.inbound()),
            "outbound": len(self.outbound()),
            "rejected": len(self.rejected()),
            "by_flow": dict(flow_counts),
        }

    def known_flows(self) -> dict[str, str]:
        return dict(_KNOWN_FLOWS)
