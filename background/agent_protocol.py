"""Inter-agent message protocol — Phase (Architecture Stage 4).

Defines AgentMessage, the standard message format for all new inter-agent
communication in the background stack. Additive only — does not replace
existing NTFY or staging file formats, which remain stable and working.

AgentMessage is for new structured communication going forward.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class IntentType(str, Enum):
    """Known message intents. Unknown values are rejected by AgentMessage.from_dict()."""

    RUN_COMPLETE = "run_complete"
    RUN_STARTED = "run_started"
    RUN_FAILED = "run_failed"
    DISCOVERY_FINDING = "discovery_finding"
    HEALTH_CHECK = "health_check"
    OBSERVABILITY_UPDATE = "observability_update"
    STAGING_FILE_DETECTED = "staging_file_detected"
    NTFY_INBOUND = "ntfy_inbound"
    COMMITTEE_WAKE_UP = "committee_wake_up"


@dataclass
class AgentMessage:
    """Standard inter-agent message format.

    sender: agent name (e.g. "sim-runner", "discovery-agent")
    receiver: intended recipient or "broadcast"
    intent: one of IntentType (string value)
    payload: arbitrary dict — content depends on intent
    timestamp: ISO 8601 UTC string — set automatically if not provided
    session_id: optional trace ID linking related messages in one session
    """

    sender: str
    receiver: str
    intent: str
    payload: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str | None = None

    def __post_init__(self) -> None:
        # Validate intent against known values
        known = {e.value for e in IntentType}
        if self.intent not in known:
            raise ValueError(
                f"Unknown intent '{self.intent}'. "
                f"Known intents: {sorted(known)}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "intent": self.intent,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentMessage":
        """Deserialise from dict. Raises ValueError on unknown intent or missing fields."""
        required = {"sender", "receiver", "intent", "payload", "timestamp"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Missing required fields: {sorted(missing)}")
        return cls(
            sender=data["sender"],
            receiver=data["receiver"],
            intent=data["intent"],      # __post_init__ validates this
            payload=data["payload"],
            timestamp=data["timestamp"],
            session_id=data.get("session_id"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def observability_update(
        cls,
        sender: str,
        status: str,
        last_action: str,
        anomaly: str | None = None,
        session_id: str | None = None,
    ) -> "AgentMessage":
        """Convenience constructor for the most common message type."""
        return cls(
            sender=sender,
            receiver="broadcast",
            intent=IntentType.OBSERVABILITY_UPDATE.value,
            payload={
                "status": status,
                "last_action": last_action,
                "anomaly": anomaly,
            },
            session_id=session_id,
        )
