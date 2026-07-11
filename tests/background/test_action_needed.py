"""Tests for background/action_needed.py -- the durable "waiting on Rich"
register + daily re-ping (2026-07-11 director rule)."""
from datetime import datetime, timedelta, timezone

import pytest

from background import action_needed


@pytest.fixture
def path(tmp_path):
    return tmp_path / "register.json"


def test_load_register_empty_when_missing(path):
    assert action_needed.load_register(path) == {}


def test_format_action_needed_shape():
    msg = action_needed.format_action_needed("routines-env-id", "do X", "via Y", "because Z")
    assert msg.startswith("[ACTION NEEDED] routines-env-id")
    assert "What: do X" in msg
    assert "How: via Y" in msg
    assert "Why: because Z" in msg


def test_register_item_persists_and_starts_open(path):
    entry = action_needed.register_item("a", "what", "how", "why", path=path)
    assert entry["resolved"] is False
    assert entry["item_id"] == "a"
    reloaded = action_needed.load_register(path)
    assert reloaded["a"]["what"] == "what"


def test_register_item_preserves_first_asked_at_on_reregister(path):
    first = action_needed.register_item("a", "what", "how", "why", path=path, now="2026-07-11T05:00:00+00:00")
    second = action_needed.register_item("a", "what2", "how2", "why2", path=path, now="2026-07-12T05:00:00+00:00")
    assert first["first_asked_at"] == "2026-07-11T05:00:00+00:00"
    assert second["first_asked_at"] == "2026-07-11T05:00:00+00:00"  # unchanged
    assert second["last_pinged_at"] == "2026-07-12T05:00:00+00:00"  # updated
    assert second["what"] == "what2"  # details can be refreshed


def test_resolve_item_marks_resolved_not_deleted(path):
    action_needed.register_item("a", "what", "how", "why", path=path)
    action_needed.resolve_item("a", path=path)
    entry = action_needed.load_register(path)["a"]
    assert entry["resolved"] is True


def test_open_items_excludes_resolved(path):
    action_needed.register_item("a", "w", "h", "y", path=path)
    action_needed.register_item("b", "w", "h", "y", path=path)
    action_needed.resolve_item("b", path=path)
    open_ids = {e["item_id"] for e in action_needed.open_items(path=path)}
    assert open_ids == {"a"}


def test_due_for_reping_empty_when_recently_pinged(path):
    now = datetime.now(timezone.utc).isoformat()
    action_needed.register_item("a", "w", "h", "y", path=path, now=now)
    assert action_needed.due_for_reping(path=path, now=now) == []


def test_due_for_reping_returns_item_after_24h(path):
    asked_at = datetime(2026, 7, 10, 5, 0, 0, tzinfo=timezone.utc)
    action_needed.register_item("a", "w", "h", "y", path=path, now=asked_at.isoformat())
    just_under = (asked_at + timedelta(hours=23, minutes=59)).isoformat()
    just_over = (asked_at + timedelta(hours=24, minutes=1)).isoformat()
    assert action_needed.due_for_reping(path=path, now=just_under) == []
    due = action_needed.due_for_reping(path=path, now=just_over)
    assert len(due) == 1
    assert due[0]["item_id"] == "a"


def test_due_for_reping_excludes_resolved(path):
    asked_at = datetime(2026, 7, 10, 5, 0, 0, tzinfo=timezone.utc)
    action_needed.register_item("a", "w", "h", "y", path=path, now=asked_at.isoformat())
    action_needed.resolve_item("a", path=path)
    later = (asked_at + timedelta(days=5)).isoformat()
    assert action_needed.due_for_reping(path=path, now=later) == []


def test_default_path_honours_module_level_monkeypatch(tmp_path, monkeypatch):
    fake_path = tmp_path / "monkeypatched_register.json"
    monkeypatch.setattr(action_needed, "REGISTER_PATH", fake_path)
    action_needed.register_item("a", "w", "h", "y")  # no path= argument
    assert fake_path.exists()
    assert action_needed.open_items() != []
