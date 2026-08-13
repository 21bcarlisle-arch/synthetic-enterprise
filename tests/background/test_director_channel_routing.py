"""G-N3 routing, as a property of the SYSTEM rather than of one call (2026-08-13).

`notification_digest` landed on 2026-08-12 with instant/deferrable routing taken verbatim from
the director's own message. On 2026-08-13 a grep of the tree found:

  * exactly TWO callers passing `topic_class` anywhere, both deferrable;
  * ZERO senders for any of the four INSTANT classes -- including `publishing_down`, so the one
    event he asked to be told about immediately had nothing that could tell him;
  * every other sender unclassified, and unclassified means INSTANT.

The routing layer was therefore complete, correct, tested -- and wired to almost nothing, which
is indistinguishable from not existing. These tests are about the wiring.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from background import notification_digest as nd

ROOT = Path(__file__).resolve().parents[2]
SEARCH_ROOTS = ("background", "tools")


def _grep_files(needle: str) -> set[str]:
    r = subprocess.run(
        ["git", "grep", "-l", "--fixed-strings", needle, "--"] + list(SEARCH_ROOTS),
        cwd=str(ROOT), capture_output=True, text=True,
    )
    if r.returncode > 1:
        pytest.fail("git grep failed -- cannot answer, and an unavailable check is a failed check")
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def _senders_of(constant: str) -> set[str]:
    """Files that ROUTE a notification with this class.

    Matched on the ATTRIBUTE (`.ACTION_NEEDED`) rather than on one spelling of the module, because
    callers reach the vocabulary two legitimate ways -- `notification_digest.X` directly, and via
    a lazy accessor (`_digest_classes().X`) where importing the module at load time would couple a
    watchdog to the thing it watches. Requiring `topic_class=` in the same file keeps a same-named
    local constant from counting as a sender.
    """
    files = _grep_files(f".{constant}") & _grep_files("topic_class=")
    return {f for f in files if not f.endswith("notification_digest.py")}


@pytest.mark.parametrize("constant", ["ACTION_NEEDED", "BLOCKED_WORK", "PUBLISHING_DOWN"])
def test_every_instant_class_the_director_named_has_a_sender(constant):
    """The defect, stated as a test: a class nothing emits is a promise nothing keeps.

    DECISION_WAITING is deliberately absent from this list. It is the one of the four with no
    natural emitter today -- `action_needed.register_item` REFUSES to register anything outside
    the four reserved real-world classes, so "a decision waiting on Rich" is by construction rare
    and arrives through that path. Listing it here would either force a fake sender or sit red;
    both are worse than saying so. If a genuine emitter appears, add it to this list.
    """
    senders = _senders_of(constant)
    assert senders, (
        f"{constant} is one of the four classes the director reserved for INSTANT sending and "
        f"nothing in {SEARCH_ROOTS} emits it. That is how eighteen hours of frozen publishing "
        f"reached him by eye instead of by phone."
    )


def test_publishing_down_is_emitted_by_something_independent_of_the_publisher():
    """R15 INDEPENDENCE. A publisher that pages about its own health is the tautology: the wedged
    component reporting on itself is how the previous freeze stayed quiet too."""
    senders = _senders_of("PUBLISHING_DOWN")
    assert senders, "publishing_down has no sender"
    assert not any("process_run_complete" in s or "sim_runner" in s for s in senders), (
        f"publishing_down is emitted only from the publish pipeline itself: {senders}"
    )


def test_the_high_volume_recurring_senders_are_batched():
    """The volume he asked to cut, named by its actual sources.

    Counted from the ops NTFY mirror for 2026-08-13: reconcile drift ~12 pages (mostly the same
    five gap-ledger rows), staged-instruction announcements ~12, worktree accretion 5. None of
    them is actionable within the hour, and together they are most of the day's traffic.
    """
    expected = {
        "background/reconcile_watch.py": "DIVERGENCE",
        "background/staging_watcher.py": "FINDING_ANNOUNCEMENT",
        "background/sanity_daemon.py": "FINDING_ANNOUNCEMENT",
    }
    for path, constant in expected.items():
        src = (ROOT / path).read_text()
        assert f"notification_digest.{constant}" in src, (
            f"{path} does not declare a topic_class, so its pages default to INSTANT -- which is "
            f"the state in which the digest existed and batched nothing"
        )
    # The worktree accretion alarm declares DRIFT through the deadman's lazy accessor.
    dms = (ROOT / "background" / "deadmans_switch.py").read_text()
    worktree = dms[dms.index("_check_worktree_reconcile"):]
    assert "DRIFT" in worktree[:worktree.index("def _check_status_honesty")]


def test_a_deferrable_class_does_NOT_reach_the_wire(monkeypatch, tmp_path):
    """The mechanism itself, both directions, on the contract rather than on a source scan."""
    from background import notify as notify_mod

    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", tmp_path / "t.json")
    monkeypatch.setattr(nd, "QUEUE_FILE", tmp_path / "q.jsonl")
    monkeypatch.setattr(nd, "STATE_FILE", tmp_path / "s.json")
    sent = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda m, **k: sent.append(m) or "id1")

    deferred = notify_mod.notify("drift noise", kind="real_alarm", topic_class=nd.DIVERGENCE)
    assert deferred.startswith("deferred:"), "a deferrable class reached the wire"
    assert sent == []

    instant = notify_mod.notify("[PUBLISHING DOWN] figures frozen", kind="real_alarm",
                                topic_class=nd.PUBLISHING_DOWN)
    assert instant == "id1"
    assert sent == ["[PUBLISHING DOWN] figures frozen"]


def test_an_unclassified_notification_still_pages(monkeypatch, tmp_path):
    """G-N3's fail direction, unchanged by this wiring: the classifier fails TOWARD paging him.
    Batching the senders we understand must never turn silence into the default for the ones we
    have not looked at yet."""
    from background import notify as notify_mod

    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", tmp_path / "t.json")
    sent = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda m, **k: sent.append(m) or "id2")

    assert notify_mod.notify("something nobody classified", kind="real_alarm") == "id2"
    assert sent == ["something nobody classified"]


def test_kind_digest_is_not_a_way_to_ask_for_batching():
    """The trap that made every sanity-daemon finding instant while reading as batched.

    `kind` and `topic_class` are different axes: kind="digest" means *this message IS the batch*,
    so it is INSTANT by construction (routing it back into the queue would never terminate). A
    caller wanting batching declares a deferrable `topic_class`. Pinned because the misreading is
    natural, cost a day of instant pages, and left no trace in the sender's own name.
    """
    assert nd.is_instant(None) is True
    src = (ROOT / "background" / "notify.py").read_text()
    assert re.search(r'if kind != "digest":', src), (
        "notify() no longer exempts kind='digest' from routing -- if that changed deliberately, "
        "this test and the sanity_daemon comment that cites it both need rewriting"
    )
    # And the sender that fell into it does not SEND with kind="digest" any more. Matched on the
    # call, not the token: the fix's own comment explains the trap and necessarily quotes it.
    sanity = (ROOT / "background" / "sanity_daemon.py").read_text()
    assert not re.search(r'notify\([^)]*kind="digest"', sanity, re.DOTALL), (
        "sanity_daemon sends with kind='digest' again -- which routes AROUND the digest"
    )
