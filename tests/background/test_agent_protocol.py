"""Tests for background/agent_protocol.py — Phase (Architecture Stage 4)."""

import json
import pytest
from background.agent_protocol import AgentMessage, IntentType


class TestIntentType:
    def test_all_expected_intents_present(self):
        values = {e.value for e in IntentType}
        expected = {
            "run_complete", "run_started", "run_failed",
            "discovery_finding", "health_check", "observability_update",
            "staging_file_detected", "ntfy_inbound", "committee_wake_up",
        }
        assert expected.issubset(values)

    def test_intent_type_is_string_enum(self):
        assert isinstance(IntentType.RUN_COMPLETE, str)
        assert IntentType.OBSERVABILITY_UPDATE == "observability_update"


class TestAgentMessageConstruction:
    def test_basic_construction(self):
        msg = AgentMessage(
            sender="sim-runner",
            receiver="autonomous-runner",
            intent="run_complete",
            payload={"net_gbp": 1_158_439},
        )
        assert msg.sender == "sim-runner"
        assert msg.intent == "run_complete"
        assert msg.payload["net_gbp"] == 1_158_439
        assert msg.session_id is None

    def test_timestamp_auto_populated(self):
        msg = AgentMessage(
            sender="a", receiver="b", intent="health_check", payload={}
        )
        assert msg.timestamp
        assert "T" in msg.timestamp  # ISO 8601 format

    def test_session_id_optional(self):
        msg = AgentMessage(
            sender="a", receiver="b", intent="health_check", payload={},
            session_id="sess-001",
        )
        assert msg.session_id == "sess-001"

    def test_unknown_intent_raises(self):
        with pytest.raises(ValueError, match="Unknown intent"):
            AgentMessage(
                sender="a", receiver="b", intent="made_up_intent", payload={}
            )

    def test_unknown_intent_message_lists_known(self):
        with pytest.raises(ValueError) as exc_info:
            AgentMessage(sender="a", receiver="b", intent="bogus", payload={})
        assert "observability_update" in str(exc_info.value)


class TestSerialisationRoundTrip:
    def test_to_dict_round_trip(self):
        original = AgentMessage(
            sender="discovery-agent",
            receiver="broadcast",
            intent="discovery_finding",
            payload={"domain": "electricity_pricing", "confidence": "H"},
            session_id="sess-abc",
        )
        restored = AgentMessage.from_dict(original.to_dict())
        assert restored.sender == original.sender
        assert restored.receiver == original.receiver
        assert restored.intent == original.intent
        assert restored.payload == original.payload
        assert restored.session_id == original.session_id
        assert restored.timestamp == original.timestamp

    def test_to_json_round_trip(self):
        original = AgentMessage(
            sender="sim-runner",
            receiver="broadcast",
            intent="run_complete",
            payload={"net_gbp": 500_000, "survived": True},
        )
        restored = AgentMessage.from_json(original.to_json())
        assert restored.sender == original.sender
        assert restored.payload == original.payload

    def test_json_is_valid_json(self):
        msg = AgentMessage(
            sender="a", receiver="b", intent="health_check", payload={"alive": True}
        )
        parsed = json.loads(msg.to_json())
        assert parsed["intent"] == "health_check"
        assert parsed["payload"]["alive"] is True

    def test_none_session_id_survives_round_trip(self):
        original = AgentMessage(
            sender="a", receiver="b", intent="ntfy_inbound", payload={}, session_id=None
        )
        restored = AgentMessage.from_dict(original.to_dict())
        assert restored.session_id is None


class TestDeserialisationValidation:
    def test_from_dict_rejects_unknown_intent(self):
        with pytest.raises(ValueError):
            AgentMessage.from_dict({
                "sender": "a",
                "receiver": "b",
                "intent": "unknown_intent",
                "payload": {},
                "timestamp": "2026-06-23T12:00:00Z",
            })

    def test_from_dict_rejects_missing_sender(self):
        with pytest.raises(ValueError, match="Missing required fields"):
            AgentMessage.from_dict({
                "receiver": "b",
                "intent": "health_check",
                "payload": {},
                "timestamp": "2026-06-23T12:00:00Z",
            })

    def test_from_dict_rejects_missing_payload(self):
        with pytest.raises(ValueError, match="Missing required fields"):
            AgentMessage.from_dict({
                "sender": "a",
                "receiver": "b",
                "intent": "health_check",
                "timestamp": "2026-06-23T12:00:00Z",
            })

    def test_from_dict_allows_optional_session_id_absent(self):
        msg = AgentMessage.from_dict({
            "sender": "a",
            "receiver": "b",
            "intent": "health_check",
            "payload": {},
            "timestamp": "2026-06-23T12:00:00Z",
        })
        assert msg.session_id is None


class TestObservabilityUpdateConvenience:
    def test_convenience_constructor_sets_correct_fields(self):
        msg = AgentMessage.observability_update(
            sender="sim-runner",
            status="running",
            last_action="Starting full Ollama run",
        )
        assert msg.sender == "sim-runner"
        assert msg.receiver == "broadcast"
        assert msg.intent == "observability_update"
        assert msg.payload["status"] == "running"
        assert msg.payload["last_action"] == "Starting full Ollama run"
        assert msg.payload["anomaly"] is None

    def test_convenience_constructor_with_anomaly(self):
        msg = AgentMessage.observability_update(
            sender="sim-runner",
            status="error",
            last_action="Run timed out",
            anomaly="TimeoutExpired after 7200s",
        )
        assert msg.payload["anomaly"] == "TimeoutExpired after 7200s"

    def test_convenience_constructor_session_id(self):
        msg = AgentMessage.observability_update(
            sender="a", status="idle", last_action="done",
            session_id="sess-xyz",
        )
        assert msg.session_id == "sess-xyz"
