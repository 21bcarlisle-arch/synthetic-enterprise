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
    action_needed.resolve_item("a", "answered", path=path)
    entry = action_needed.load_register(path)["a"]
    assert entry["resolved"] is True
    assert entry["answer"] == "answered"  # answer stored, not just a boolean flipped


def test_resolve_item_rejects_empty_answer_and_leaves_item_open(path):
    """The evaporation defect closed: you cannot resolve without recording the
    decision content. A rejected resolve must leave the item OPEN (still nagging)."""
    action_needed.register_item("a", "w", "h", "y", path=path)
    for bad in ("", "   ", None):
        with pytest.raises(ValueError):
            action_needed.resolve_item("a", bad, path=path)
    open_ids = {e["item_id"] for e in action_needed.open_items(path=path)}
    assert open_ids == {"a"}  # never silently closed


def test_resolve_item_stores_answer_and_timestamp(path):
    action_needed.register_item("a", "w", "h", "y", path=path)
    action_needed.resolve_item("a", "Profile B", path=path, now="2026-07-14T00:00:00+00:00")
    entry = action_needed.load_register(path)["a"]
    assert entry["resolved"] is True
    assert entry["answer"] == "Profile B"
    assert entry["resolved_at"] == "2026-07-14T00:00:00+00:00"


def test_confirm_and_resolve_sends_confirmation_and_resolves(path):
    action_needed.register_item("a", "w", "h", "y", path=path)
    sent = []
    ok = action_needed.confirm_and_resolve(
        "a", "Profile B", path=path,
        send_ntfy_fn=lambda msg, headers=None: sent.append(msg),
    )
    assert ok is True
    assert len(sent) == 1
    assert "Profile B" in sent[0] and "a" in sent[0]  # the receipt names item + decision
    assert action_needed.load_register(path)["a"]["resolved"] is True


def test_confirm_and_resolve_keeps_durable_record_even_if_send_fails(path):
    """A confirmation send failure must NOT roll back the recorded decision --
    the answer is stored first, the receipt is best-effort."""
    action_needed.register_item("a", "w", "h", "y", path=path)
    def boom(msg, headers=None):
        raise RuntimeError("ntfy unreachable")
    ok = action_needed.confirm_and_resolve("a", "Profile B", path=path, send_ntfy_fn=boom)
    assert ok is False
    entry = action_needed.load_register(path)["a"]
    assert entry["resolved"] is True and entry["answer"] == "Profile B"


def test_open_items_excludes_resolved(path):
    action_needed.register_item("a", "w", "h", "y", path=path)
    action_needed.register_item("b", "w", "h", "y", path=path)
    action_needed.resolve_item("b", "answered", path=path)
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
    action_needed.resolve_item("a", "answered", path=path)
    later = (asked_at + timedelta(days=5)).isoformat()
    assert action_needed.due_for_reping(path=path, now=later) == []


def test_default_path_honours_module_level_monkeypatch(tmp_path, monkeypatch):
    fake_path = tmp_path / "monkeypatched_register.json"
    monkeypatch.setattr(action_needed, "REGISTER_PATH", fake_path)
    action_needed.register_item("a", "w", "h", "y")  # no path= argument
    assert fake_path.exists()
    assert action_needed.open_items() != []


# ── escalate_if_one_way_door() (2026-07-13, ACTION_NEEDED_REDESIGN_AND_BOOTSTRAP.md
# item 1: "[ACTION NEEDED] fires IF AND ONLY IF the one-way-door predicate
# returns true. No judgement, no remembering, no separate heuristic. One
# code path.") ──

def test_escalate_if_one_way_door_registers_and_alerts_on_real_match(path):
    sent = []
    verdict = action_needed.escalate_if_one_way_door(
        "spend-decision-1", "spend real money on a production API subscription",
        "director confirms live", path=path, send_ntfy_fn=lambda msg: sent.append(msg),
    )
    assert verdict.is_one_way_door is True
    assert len(sent) == 1
    assert "[ACTION NEEDED] spend-decision-1" in sent[0]
    assert "real money" in sent[0].lower() or "real_money" in sent[0].lower()
    entry = action_needed.load_register(path)["spend-decision-1"]
    assert entry["resolved"] is False


def test_escalate_if_one_way_door_noop_on_routine_action(path):
    """The core property: routine work (PROCEED_BY_DEFAULT) must never
    register or alert -- silence is correct, not a missing feature."""
    sent = []
    verdict = action_needed.escalate_if_one_way_door(
        "routine-1", "refactor a helper function for clarity",
        "n/a", path=path, send_ntfy_fn=lambda msg: sent.append(msg),
    )
    assert verdict.is_one_way_door is False
    assert sent == []
    assert action_needed.load_register(path) == {}


def test_escalate_if_one_way_door_uncertain_always_escalates(path):
    """DIRECTOR_TWIN.md's own escape hatch: genuine uncertainty fails
    closed, same as classify_action() itself."""
    sent = []
    verdict = action_needed.escalate_if_one_way_door(
        "uncertain-1", "something ambiguous I can't classify confidently",
        "director reviews", uncertain=True, path=path,
        send_ntfy_fn=lambda msg: sent.append(msg),
    )
    assert verdict.is_one_way_door is True
    assert len(sent) == 1


def test_escalate_if_one_way_door_why_names_the_real_category(path):
    sent = []
    action_needed.escalate_if_one_way_door(
        "security-1", "disable the epistemic verifier hook",
        "n/a", path=path, send_ntfy_fn=lambda msg: sent.append(msg),
    )
    assert "security_safety_control" in sent[0]


def test_escalate_if_one_way_door_default_ntfy_is_real_send_ntfy(path, monkeypatch):
    """Without an injected send_ntfy_fn, the real background.ntfy_utils.send_ntfy
    is used -- confirmed by monkeypatching that module's own function and
    checking it gets called, not a lazily-imported copy that dodges the patch."""
    from background import ntfy_utils
    calls = []
    monkeypatch.setattr(ntfy_utils, "send_ntfy", lambda msg, **k: calls.append(msg))
    action_needed.escalate_if_one_way_door(
        "spend-2", "spend real money", "n/a", path=path,
    )
    assert len(calls) == 1
