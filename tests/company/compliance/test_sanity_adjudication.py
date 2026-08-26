"""Tests for company/compliance/sanity_adjudication.py -- the durable
finding-adjudication ledger (2026-07-11 sanity triage)."""
import pytest

from company.compliance import sanity_adjudication as ledger


@pytest.fixture
def path(tmp_path):
    return tmp_path / "ledger.json"


def test_load_ledger_empty_when_missing(path):
    assert ledger.load_ledger(path) == {}


def test_adjudicate_persists_entry(path):
    entry = ledger.adjudicate(
        "gas-kwh-unit", "adjudicated-false-positive",
        "UK gas bills are correctly stated in kWh -- standard practice, not a defect.",
        "claude", path=path, now="2026-07-11T05:00:00+00:00",
    )
    assert entry["finding_key"] == "gas-kwh-unit"
    assert entry["state"] == "adjudicated-false-positive"
    reloaded = ledger.load_ledger(path)
    assert reloaded["gas-kwh-unit"]["state"] == "adjudicated-false-positive"


def test_adjudicate_rejects_invalid_state(path):
    with pytest.raises(ValueError):
        ledger.adjudicate("x", "not-a-real-state", "evidence", "claude", path=path)


def test_get_state_none_when_unknown(path):
    assert ledger.get_state("never-seen", path=path) is None


def test_get_state_returns_latest(path):
    ledger.adjudicate("vat-mismatch", "open", "still investigating", "claude", path=path)
    ledger.adjudicate("vat-mismatch", "adjudicated-false-positive", "confirmed via arithmetic", "claude", path=path)
    assert ledger.get_state("vat-mismatch", path=path) == "adjudicated-false-positive"


def test_is_known_true_once_adjudicated(path):
    assert ledger.is_known("high-consumption", path=path) is False
    ledger.adjudicate("high-consumption", "adjudicated-real", "found a real check-level defect", "claude", path=path)
    assert ledger.is_known("high-consumption", path=path) is True


def test_open_findings_filters_by_state(path):
    ledger.adjudicate("a", "open", "e1", "claude", path=path)
    ledger.adjudicate("b", "adjudicated-real", "e2", "claude", path=path)
    ledger.adjudicate("c", "adjudicated-false-positive", "e3", "claude", path=path)
    open_keys = {e["finding_key"] for e in ledger.open_findings(path=path)}
    assert open_keys == {"a"}


def test_all_entries_returns_everything(path):
    ledger.adjudicate("a", "open", "e1", "claude", path=path)
    ledger.adjudicate("b", "adjudicated-real", "e2", "claude", path=path)
    assert len(ledger.all_entries(path=path)) == 2


def test_default_path_honours_module_level_monkeypatch(tmp_path, monkeypatch):
    """Every function's default falls back to ledger.LEDGER_PATH looked up at
    CALL time, not a stale function-definition-time default -- proves a
    caller (e.g. sanity_daemon.py) that never passes `path` explicitly still
    gets correctly redirected by a test's monkeypatch, the exact pattern
    every other daemon's *_PATH constant in this codebase already relies on."""
    fake_path = tmp_path / "monkeypatched_ledger.json"
    monkeypatch.setattr(ledger, "LEDGER_PATH", fake_path)
    ledger.adjudicate("x", "open", "evidence", "claude")  # no path= argument
    assert fake_path.exists()
    assert ledger.is_known("x") is True


def test_readjudication_overwrites_prior_verdict(path):
    ledger.adjudicate("x", "open", "not yet checked", "claude", path=path)
    ledger.adjudicate("x", "adjudicated-real", "confirmed a real check-level defect", "claude", path=path)
    entries = ledger.all_entries(path=path)
    assert len(entries) == 1
    assert entries[0]["state"] == "adjudicated-real"


# --- the hand-written row, and the reader it felled ------------------------------------
# 2026-08-26. `adjudicate()` validates and cannot write a row without a `state`, but the
# ledger is a plain JSON file and a row written into it BY HAND bypasses that writer. One
# did -- the Expert-Hour verdict on EP13_adapter_carbon_intensity carried
# `verdict`/`fix`/`method` and no `state` -- and every reader that subscripted `e["state"]`
# raised KeyError on it, taking down the daily sanity digest: the very mechanism that would
# otherwise have reported the problem. The failure silenced its own alarm.


def _handwritten_row_without_a_state(path):
    """A row as a human writes it straight into the JSON -- rich, and stateless."""
    import json
    json.dump(
        {"expert_hour:SOMETHING": {
            "finding_key": "expert_hour:SOMETHING",
            "verdict": "NOT_THIS_IS_REAL -- level held",
            "evidence": "observed-with-evidence",
        }},
        path.open("w"),
    )


def test_a_handwritten_row_with_no_state_does_not_fell_the_readers(path):
    """TOLERANCE. One malformed row must not take down `open_findings()` for the other
    102 -- the daemon that reports problems cannot be the thing a problem stops."""
    _handwritten_row_without_a_state(path)
    assert ledger.open_findings(path=path) == []
    assert ledger.get_state("expert_hour:SOMETHING", path=path) is None
    assert ledger.is_known("expert_hour:SOMETHING", path=path) is False


def test_the_malformed_row_is_LOUD_rather_than_silently_dropped(path):
    """THE OTHER HALF, and the one that makes the tolerance safe (R15).

    `.get()` alone is FAIL-OPEN: the row would simply vanish from `open_findings()` and
    nobody would learn it existed. Skipped by the readers AND named by the control is the
    only combination that is not a silent drop.
    """
    _handwritten_row_without_a_state(path)
    assert ledger.malformed_entries(path=path) == ["expert_hour:SOMETHING"]


def test_the_detector_is_not_a_constant(path):
    """NULL CONTROL. A detector that always names something is no more use than one that
    never does -- a well-formed ledger must come back clean."""
    ledger.adjudicate("a", "open", "e1", "claude", path=path)
    ledger.adjudicate("b", "adjudicated-real", "e2", "claude", path=path)
    assert ledger.malformed_entries(path=path) == []


@pytest.mark.parametrize(
    "state", [None, "", "   ", 7, [], {}],
    ids=["null", "empty", "whitespace", "int", "list", "dict"],
)
def test_a_present_but_unreadable_state_counts_as_malformed(path, state):
    """FAIL-OPEN, PINNED. A `state` that is present but not a usable string is exactly as
    unreadable as an absent one, and must not slip through on truthiness alone."""
    import json
    json.dump({"k": {"finding_key": "k", "state": state}}, path.open("w"))
    assert ledger.malformed_entries(path=path) == ["k"]


def test_a_row_that_is_not_a_dict_at_all_is_caught_not_raised(path):
    import json
    json.dump({"k": "this should have been an object"}, path.open("w"))
    assert ledger.malformed_entries(path=path) == ["k"]


def test_THE_REAL_SHIPPED_LEDGER_HAS_NO_MALFORMED_ROWS():
    """THE LOAD-BEARING ONE. Everything above judges the detector against fixtures; this
    judges the ledger the daemon actually reads. It is the assertion that would have caught
    the EP13 row on the day it was written, and it fails on the real file, not a fake one.
    """
    assert ledger.malformed_entries() == [], (
        "a row in docs/observability/sanity_adjudication_ledger.json has no readable "
        "`state` -- every reader subscripting e['state'] will KeyError on it"
    )
