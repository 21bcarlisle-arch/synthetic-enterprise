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
