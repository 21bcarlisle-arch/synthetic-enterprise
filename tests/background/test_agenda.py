"""Tests for background/agenda.py -- the open-agenda continuation marker
(docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md, Deliverable 1a).

The nudge-once-per-snapshot mechanism (should_nudge/record_nudged) was
retired 2026-07-09 (doorbell failure #4) -- background/supervisor.py is now
the sole turn-granting authority for open agenda work, re-reading
load_agenda() fresh every cycle. See test_supervisor.py for its coverage.
"""
from background import agenda


def _patch_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(agenda, "AGENDA_FILE", tmp_path / "agenda.json")


def test_load_agenda_none_when_absent(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    assert agenda.load_agenda() is None


def test_set_and_load_agenda(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.set_agenda("Phase 3", "item 2", "wire credit_refund.py")
    loaded = agenda.load_agenda()
    assert loaded["phase"] == "Phase 3"
    assert loaded["step"] == "item 2"
    assert loaded["next_action"] == "wire credit_refund.py"
    assert "updated_at" in loaded


def test_clear_agenda_removes_file(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.set_agenda("Phase 3", "item 2", "wire credit_refund.py")
    agenda.clear_agenda()
    assert agenda.load_agenda() is None


def test_clear_agenda_safe_when_nothing_to_clear(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    agenda.clear_agenda()  # must not raise


def test_nudge_once_mechanism_is_retired():
    """Doorbell failure #4 root cause: guard against this ever being
    reintroduced. Turn-granting for open agenda work lives solely in
    background/supervisor.py now."""
    assert not hasattr(agenda, "should_nudge")
    assert not hasattr(agenda, "record_nudged")
    assert not hasattr(agenda, "is_stale_enough_to_nudge")
    assert not hasattr(agenda, "NUDGE_STATE_FILE")

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
