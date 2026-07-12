"""Tests for background/director_twin.py -- DIRECTOR_TWIN.md's builder-facing
twin. Uses an injectable invoke_fn throughout so no real `claude -p` process
is spawned in the test suite (slow, non-deterministic, costs real tokens) --
one real live invocation is exercised manually/separately, not in CI.
"""
import pytest

from background import director_twin


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    canon = tmp_path / "DIRECTOR_CANON.md"
    canon.write_text("# Canon\n\n**Version: 1.**\n\nSome canon text.\n\n## Changelog\n- v1: initial\n")
    monkeypatch.setattr(director_twin, "CANON_PATH", canon)
    monkeypatch.setattr(director_twin, "TWIN_LOG_PATH", tmp_path / "twin_log.jsonl")
    monkeypatch.setattr(director_twin, "OVERTURNS_LOG_PATH", tmp_path / "overturns.jsonl")


def _fake_invoke(prompt: str) -> str:
    return "This is a test answer, citing section 2."


def test_ordinary_question_answered_in_seconds_and_logged():
    answer = director_twin.ask_twin(
        "should W2_2_population_draw be sequenced before or after W1_2_generate_futures?",
        context_pack="both are epoch 3, W1_2 has no dependency, W2_2 has no dependency either",
        invoke_fn=_fake_invoke,
    )
    assert answer.routed_to_director is False
    assert answer.answer == "This is a test answer, citing section 2."
    assert answer.latency_seconds >= 0

    entries = director_twin._read_jsonl(director_twin.TWIN_LOG_PATH)
    assert len(entries) == 1
    assert entries[0]["routed_to_director"] is False
    assert entries[0]["canon_version"] == 1


def test_values_question_routes_to_director_never_calls_invoke():
    calls = []

    def _tracking_invoke(prompt):
        calls.append(prompt)
        return "should never be called"

    answer = director_twin.ask_twin(
        "which fitness function should the tournament use?",
        invoke_fn=_tracking_invoke,
    )
    assert answer.routed_to_director is True
    assert answer.answer is None
    assert calls == []  # never consulted the canon/LLM at all

    entries = director_twin._read_jsonl(director_twin.TWIN_LOG_PATH)
    assert len(entries) == 1
    assert entries[0]["routed_to_director"] is True
    assert entries[0]["category"] == "values_decision"


def test_uncertain_flag_routes_to_director():
    answer = director_twin.ask_twin("ambiguous edge case", uncertain=True, invoke_fn=_fake_invoke)
    assert answer.routed_to_director is True


def test_current_canon_version_reads_real_file():
    assert director_twin.current_canon_version() == 1


def test_overturn_bumps_canon_version_and_appends_changelog():
    answer = director_twin.ask_twin("some question", invoke_fn=_fake_invoke)
    new_version = director_twin.overturn(
        answer.entry_id, corrected_answer="actually do X instead", reason="the twin missed the R13 curriculum split"
    )
    assert new_version == 2
    assert director_twin.current_canon_version() == 2

    canon_text = director_twin.CANON_PATH.read_text()
    assert "overturn on entry" in canon_text
    assert "R13 curriculum split" in canon_text

    overturns = director_twin._read_jsonl(director_twin.OVERTURNS_LOG_PATH)
    assert len(overturns) == 1
    assert overturns[0]["entry_id"] == answer.entry_id


def test_fidelity_metric_reflects_overturns():
    a1 = director_twin.ask_twin("q1", invoke_fn=_fake_invoke)
    director_twin.ask_twin("q2", invoke_fn=_fake_invoke)
    director_twin.ask_twin("which fitness function", invoke_fn=_fake_invoke)  # routed, not answered

    metric_before = director_twin.fidelity_metric()
    assert metric_before["answered"] == 2
    assert metric_before["routed_to_director"] == 1
    assert metric_before["overturned"] == 0
    assert metric_before["overturn_rate"] == 0.0

    director_twin.overturn(a1.entry_id, "corrected", "reason")
    metric_after = director_twin.fidelity_metric()
    assert metric_after["overturned"] == 1
    assert metric_after["overturn_rate"] == 0.5


def test_fidelity_metric_none_when_nothing_answered_yet():
    metric = director_twin.fidelity_metric()
    assert metric["answered"] == 0
    assert metric["overturn_rate"] is None
