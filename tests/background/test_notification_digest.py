"""G-N3/G-N4/G-N5 — the escalation channel fits the free tier by ROUTING, never by dropping.

Director, NTFY 2026-08-12: "cut the volume to fit it. Batch and summarise everything that isn't
action-needed into periodic digests ... Two requirements: nothing gets lost by being batched — a
digested item is still findable — and a dropped or rate-limited send can never be recorded as sent."

Those two requirements are the two things a batching layer gets WRONG, so each is tested in both
directions (R15): the control fires on its own named defect, and stays silent otherwise. The named
defects, spelled out at each test, are (a) a flush that drops the queue, and (b) a flush that
advances its high-water mark on a 429.
"""
from __future__ import annotations

import json

import pytest

from background import notification_digest as nd


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Point the queue and the mark at tmp_path. They are SEPARATE files by design, so the
    fixture keeps them separate too."""
    monkeypatch.setattr(nd, "QUEUE_FILE", tmp_path / "ntfy_digest_queue.jsonl")
    monkeypatch.setattr(nd, "STATE_FILE", tmp_path / ".ntfy_digest_state.json")
    return tmp_path


# ── G-N3: the routing decision ────────────────────────────────────────────────

@pytest.mark.parametrize("cls", nd.INSTANT_CLASSES)
def test_the_directors_four_classes_are_instant(cls):
    assert nd.is_instant(cls)


@pytest.mark.parametrize("cls", nd.DEFERRABLE_CLASSES)
def test_the_categories_he_named_for_batching_defer(cls):
    assert not nd.is_instant(cls)


def test_an_unclassified_notification_is_instant():
    """FAIL TOWARD PAGING HIM. A wrongly-batched alarm costs an incident; a wrongly-instant
    one costs a message. An unrecognised class is the same case as no class."""
    assert nd.is_instant(None)
    assert nd.is_instant("something_nobody_has_declared_yet")


def test_the_instant_set_is_exactly_the_four_he_named():
    """The set is CLOSED. Widening it is how a volume cut evaporates, so it is asserted
    literally rather than derived from the module it is checking (R15: independence)."""
    assert set(nd.INSTANT_CLASSES) == {
        "action_needed", "blocked_work", "decision_waiting", "publishing_down"}


# ── G-N4: nothing is lost by being batched ────────────────────────────────────

def test_a_deferred_item_is_on_disk_before_the_call_returns(store):
    nd.defer("drifted 3%", kind="real_alarm", topic_class=nd.DRIFT)
    rows = [json.loads(x) for x in nd.QUEUE_FILE.read_text().splitlines() if x.strip()]
    assert [r["message"] for r in rows] == ["drifted 3%"]
    assert rows[0]["class"] == "drift"


def test_a_digested_item_is_still_findable_afterwards(store):
    """The director's FIRST requirement, and the named defect it guards: a flush that
    consumes its queue. The queue is append-only -- flushing marks, it does not delete."""
    nd.defer("routine landing A", kind="real_alarm", topic_class=nd.ROUTINE_LANDING)
    nd.defer("routine landing B", kind="real_alarm", topic_class=nd.ROUTINE_LANDING)
    nd.flush(_send=lambda text: "real-ntfy-id-123")

    assert not nd.pending(), "a confirmed digest should clear the PENDING view"
    body = nd.QUEUE_FILE.read_text()
    assert "routine landing A" in body and "routine landing B" in body, (
        "a digested item must stay findable -- this is the defect the append-only queue exists "
        "to prevent"
    )


def test_the_digest_names_the_file_that_holds_every_line(store):
    for i in range(4):
        nd.defer(f"item {i}", kind="real_alarm", topic_class=nd.DIVERGENCE)
    text = nd.compose(nd.pending())
    assert "ntfy_digest_queue.jsonl" in text


def test_an_elided_digest_says_so_rather_than_reading_complete(store):
    """A summary that hides its own truncation is how a batched item becomes a lost one."""
    for i in range(nd._MAX_DIGEST_LINES + 10):
        nd.defer(f"item {i}", kind="real_alarm", topic_class=nd.DRIFT)
    text = nd.compose(nd.pending())
    assert "more not shown" in text
    assert "EVERY item, in full" in text


def test_a_torn_queue_line_does_not_lose_the_rest(store):
    nd.defer("good one", kind="real_alarm", topic_class=nd.DRIFT)
    with nd.QUEUE_FILE.open("a", encoding="utf-8") as fh:
        fh.write("{not json\n")
    nd.defer("good two", kind="real_alarm", topic_class=nd.DRIFT)
    assert [e["message"] for e in nd.pending()] == ["good one", "good two"]


# ── G-N5: a dropped or rate-limited send is never recorded as sent ────────────

def test_defer_returns_a_sentinel_and_never_an_id(store):
    """A batched item has NOT been sent. Any caller reading the return value as an id would
    be recording an unsent message as sent -- the director's second requirement."""
    result = nd.defer("x", kind="real_alarm", topic_class=nd.DRIFT)
    assert result.startswith("deferred:")
    assert not nd._was_delivered(result)


@pytest.mark.parametrize("sentinel", [
    None, "", "deferred:4", "suppressed:unchanged:k", "test_fixture:not-sent", "pytest-suppressed",
])
def test_no_sentinel_counts_as_a_delivery(sentinel):
    assert not nd._was_delivered(sentinel)


def test_a_real_id_counts_as_a_delivery():
    assert nd._was_delivered("Xk3jd9AbcD")


def test_a_rate_limited_digest_leaves_every_item_pending(store):
    """THE NAMED DEFECT (director's second requirement). ntfy returns 429 and the flush
    returns no id: the mark must NOT move, so the same items ride the next digest."""
    nd.defer("one", kind="real_alarm", topic_class=nd.DRIFT)
    nd.defer("two", kind="real_alarm", topic_class=nd.DRIFT)

    nd.flush(_send=lambda text: None)                    # 429 / curl failure
    assert [e["message"] for e in nd.pending()] == ["one", "two"]

    nd.flush(_send=lambda text: "real-id")               # recovered
    assert nd.pending() == []


def test_a_suppressed_digest_does_not_advance_the_mark(store):
    """The fail-SILENT direction: a send suppressed upstream is an UNSENT digest, not a
    delivered one. A checker that treats its own unavailability as success is R15's third
    killer pattern."""
    nd.defer("one", kind="real_alarm", topic_class=nd.DRIFT)
    nd.flush(_send=lambda text: "pytest-suppressed")
    assert len(nd.pending()) == 1


def test_flush_with_nothing_pending_sends_nothing(store):
    calls = []
    assert nd.flush(_send=lambda t: calls.append(t) or "id") is None
    assert calls == []


def test_maybe_flush_is_throttled_but_never_drops(store):
    nd.defer("one", kind="real_alarm", topic_class=nd.DRIFT)
    nd.flush(_send=lambda t: "id-1")                     # sets last_digest_ts
    nd.defer("two", kind="real_alarm", topic_class=nd.DRIFT)

    assert nd.maybe_flush(_send=lambda t: "id-2") is None, "not due yet"
    assert [e["message"] for e in nd.pending()] == ["two"], (
        "a throttled flush must DELAY a digest, never lose one")


# ── the wiring: notify() actually routes ──────────────────────────────────────

def test_notify_defers_a_deferrable_class_instead_of_sending(store, monkeypatch):
    from background import notify as notify_mod
    sent = []
    monkeypatch.setattr(notify_mod.ntfy_utils, "send_ntfy",
                        lambda m, headers=None, _allow_real_send=False: sent.append(m) or "id")

    result = notify_mod.notify("a finding was filed", kind="real_alarm",
                               topic_class=nd.FINDING_ANNOUNCEMENT)
    assert sent == [], "a batched item must never reach the wire"
    assert result.startswith("deferred:")
    assert [e["message"] for e in nd.pending()] == ["a finding was filed"]


def test_notify_sends_an_instant_class_immediately(store, monkeypatch):
    from background import notify as notify_mod
    sent = []
    monkeypatch.setattr(notify_mod.ntfy_utils, "send_ntfy",
                        lambda m, headers=None, _allow_real_send=False: sent.append(m) or "id")

    notify_mod.notify("publishing is down", kind="real_alarm", topic_class=nd.PUBLISHING_DOWN)
    assert sent == ["publishing is down"]
    assert nd.pending() == []


def test_an_undeclared_notify_still_pages(store, monkeypatch):
    """Every pre-existing caller keeps today's behaviour. The volume cut is opt-in per call
    site, so this change cannot silence an alarm nobody has classified yet."""
    from background import notify as notify_mod
    sent = []
    monkeypatch.setattr(notify_mod.ntfy_utils, "send_ntfy",
                        lambda m, headers=None, _allow_real_send=False: sent.append(m) or "id")

    notify_mod.notify("something old", kind="real_alarm")
    assert sent == ["something old"]


def test_the_digest_itself_is_never_batched(store, monkeypatch):
    """kind="digest" IS the batch. If it routed through the queue the digest could never be
    delivered -- the regress is asserted, not left to the reader."""
    from background import notify as notify_mod
    sent = []
    monkeypatch.setattr(notify_mod.ntfy_utils, "send_ntfy",
                        lambda m, headers=None, _allow_real_send=False: sent.append(m) or "id")

    notify_mod.notify("[DIGEST] 3 items", kind="digest", topic_class=nd.DRIFT)
    assert sent == ["[DIGEST] 3 items"]
    assert nd.pending() == []


def test_a_deferred_item_still_obeys_transition_only(store, monkeypatch):
    """R5 applies to the queue too: an unchanged status must not fill the digest with the
    noise transition-only exists to remove."""
    from background import notify as notify_mod
    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", store / ".transitions.json")

    for _ in range(3):
        notify_mod.notify("drift 3%", kind="real_alarm", topic_class=nd.DRIFT,
                          transition_key="drift", state="3%")
    assert len(nd.pending()) == 1
