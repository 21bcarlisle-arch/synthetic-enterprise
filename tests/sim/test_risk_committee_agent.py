import json

from sim import risk_committee_agent as agent


def test_call_local_strips_think_block_and_fences(monkeypatch):
    raw = (
        '<think>the customer looks risky, bump it up</think>\n'
        '```json\n'
        '{"reasoning": "elevated VaR", "adjustments": '
        '[{"customer_id": "C1", "old_hedge_fraction": 0.30, "new_hedge_fraction": 0.50}]}\n'
        '```'
    )

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"message": {"content": raw}}).encode()

    monkeypatch.setattr(agent.urllib.request, "urlopen", lambda *a, **k: FakeResponse())

    decision = agent._call_local("some context")

    assert decision["reasoning"] == "elevated VaR"
    assert decision["adjustments"][0]["new_hedge_fraction"] == 0.50


def test_invoke_enforces_minimum_adjustment(tmp_path, monkeypatch):
    handshake = tmp_path / "handshake.md"
    handshake.write_text("Risk Committee Wake-Up — context")
    log_file = tmp_path / "risk-committee-log.md"
    monkeypatch.setattr(agent, "HANDSHAKE_FILE", str(handshake))
    monkeypatch.setattr(agent, "COMMITTEE_LOG_FILE", str(log_file))

    # agent proposes a tiny +0.02 bump — below the +0.10 floor
    monkeypatch.setattr(agent, "_call_local", lambda context: {
        "reasoning": "minor concern",
        "adjustments": [{"customer_id": "C1", "old_hedge_fraction": 0.30, "new_hedge_fraction": 0.32}],
    })

    adjustments = agent.invoke("2020-01-01", 1, {"C1": 0.30})

    assert adjustments == {"C1": 0.40}


def test_invoke_enforces_maximum_adjustment(tmp_path, monkeypatch):
    handshake = tmp_path / "handshake.md"
    handshake.write_text("Risk Committee Wake-Up — context")
    log_file = tmp_path / "risk-committee-log.md"
    monkeypatch.setattr(agent, "HANDSHAKE_FILE", str(handshake))
    monkeypatch.setattr(agent, "COMMITTEE_LOG_FILE", str(log_file))

    # agent proposes a huge +0.60 jump — above the +0.30 ceiling
    monkeypatch.setattr(agent, "_call_local", lambda context: {
        "reasoning": "severe concern",
        "adjustments": [{"customer_id": "C1", "old_hedge_fraction": 0.30, "new_hedge_fraction": 0.90}],
    })

    adjustments = agent.invoke("2020-01-01", 1, {"C1": 0.30})

    assert adjustments == {"C1": 0.60}


def test_invoke_never_decreases_hedge_fraction(tmp_path, monkeypatch):
    handshake = tmp_path / "handshake.md"
    handshake.write_text("Risk Committee Wake-Up — context")
    log_file = tmp_path / "risk-committee-log.md"
    monkeypatch.setattr(agent, "HANDSHAKE_FILE", str(handshake))
    monkeypatch.setattr(agent, "COMMITTEE_LOG_FILE", str(log_file))

    # agent tries to decrease — silently held at current value, no adjustment returned
    monkeypatch.setattr(agent, "_call_local", lambda context: {
        "reasoning": "risk looks lower now",
        "adjustments": [{"customer_id": "C1", "old_hedge_fraction": 0.30, "new_hedge_fraction": 0.10}],
    })

    adjustments = agent.invoke("2020-01-01", 1, {"C1": 0.30})

    assert adjustments == {}


def test_fast_mode_skips_llm_and_applies_minimum_increase(tmp_path, monkeypatch):
    handshake = tmp_path / "handshake.md"
    handshake.write_text("Risk Committee Wake-Up — context")
    log_file = tmp_path / "risk-committee-log.md"
    monkeypatch.setattr(agent, "HANDSHAKE_FILE", str(handshake))
    monkeypatch.setattr(agent, "COMMITTEE_LOG_FILE", str(log_file))
    monkeypatch.setenv("SIM_FAST_MODE", "1")

    # _call_local must NOT be invoked in fast mode
    monkeypatch.setattr(agent, "_call_local", lambda ctx: (_ for _ in ()).throw(AssertionError("LLM called in fast mode")))

    adjustments = agent.invoke("2020-01-01", 1, {"C1": 0.50, "C2": 0.85})

    # C1: 0.50 + 0.10 = 0.60, C2: 0.85 + 0.10 = 0.95
    assert adjustments == {"C1": 0.60, "C2": 0.95}
    log_text = log_file.read_text()
    assert "[FAST-MODE]" in log_text


def test_fast_mode_does_not_adjust_customers_already_fully_hedged(tmp_path, monkeypatch):
    handshake = tmp_path / "handshake.md"
    handshake.write_text("context")
    log_file = tmp_path / "log.md"
    monkeypatch.setattr(agent, "HANDSHAKE_FILE", str(handshake))
    monkeypatch.setattr(agent, "COMMITTEE_LOG_FILE", str(log_file))
    monkeypatch.setenv("SIM_FAST_MODE", "1")

    adjustments = agent.invoke("2020-01-01", 1, {"C1": 1.00, "C2": 0.70})

    # C1 is already at 1.0 — mock skips it; C2 gets bumped to 0.80
    assert "C1" not in adjustments
    assert adjustments == {"C2": 0.80}


def test_invoke_logs_decision(tmp_path, monkeypatch):
    handshake = tmp_path / "handshake.md"
    handshake.write_text("Risk Committee Wake-Up — context")
    log_file = tmp_path / "risk-committee-log.md"
    monkeypatch.setattr(agent, "HANDSHAKE_FILE", str(handshake))
    monkeypatch.setattr(agent, "COMMITTEE_LOG_FILE", str(log_file))

    monkeypatch.setattr(agent, "_call_local", lambda context: {
        "reasoning": "elevated VaR, bump hedge",
        "adjustments": [{"customer_id": "C1", "old_hedge_fraction": 0.30, "new_hedge_fraction": 0.50}],
    })

    agent.invoke("2020-01-01", 1, {"C1": 0.30})

    log_text = log_file.read_text()
    assert "elevated VaR, bump hedge" in log_text
    assert "C1: 0.30 → 0.50" in log_text
