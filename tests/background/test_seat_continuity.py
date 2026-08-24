"""An interrupted interactive session is recoverable without the director noticing.

WHAT IS UNDER TEST, and it is two different things that must not be allowed to cover for each
other. `state()` decides LIVE/DEAD/ABSENT from two independent signals, and the direction it
fails in is the whole design: declaring a live seat dead forks work on a shared tree, so
ambiguity must resolve to LIVE — while a check that can never say DEAD is the stall this module
was built to end. Both limbs are pinned below, in both directions.

`sweep()` then turns a death into something adoptable. Its subject is not "a document was
written" but "the document carries the state a fresh session actually needs", so the assertions
are on the CONTENT: what was claimed, what is uncommitted, where it had got to.

R15: every control has a paired mutation injecting the exact defect it guards.
"""
from __future__ import annotations

import json
import time

import pytest

from background import seat_continuity as sc

NOW = 1_787_000_000.0
LIVE, DEAD, ABSENT = sc.LIVE, sc.DEAD, sc.ABSENT


@pytest.fixture
def beat(tmp_path):
    """A heartbeat file at a chosen age. Returns (path, write)."""
    p = tmp_path / ".seat_heartbeat.json"

    def _write(age_seconds: float, *, session_id: str = "s1", tools=("Bash", "Edit")):
        p.write_text(json.dumps({
            "ts": NOW - age_seconds,
            "pid": 4242,
            "session_id": session_id,
            "tool_count": 37,
            "recent_tools": [{"tool": t, "at": NOW - age_seconds} for t in tools],
        }), encoding="utf-8")
        return p

    return p, _write


@pytest.fixture
def no_seat(monkeypatch):
    monkeypatch.setattr(sc, "_any_interactive_seat", lambda: False)


@pytest.fixture
def seat_present(monkeypatch):
    monkeypatch.setattr(sc, "_any_interactive_seat", lambda: True)


@pytest.fixture
def probe_blind(monkeypatch):
    """The probe cannot tell — an unreadable /proc, a sandbox, a raising import."""
    monkeypatch.setattr(sc, "_any_interactive_seat", lambda: None)


# ---------------------------------------------------------------------------
# state(): the verdict, and the direction it fails in
# ---------------------------------------------------------------------------

def test_a_recent_tool_call_is_alive(beat, no_seat):
    p, write = beat
    write(60)
    assert sc.state(path=p, now=NOW) == LIVE


def test_silence_AND_no_session_is_death(beat, no_seat):
    """The case the director described: an API error killed it and nothing noticed."""
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1)
    assert sc.state(path=p, now=NOW) == DEAD


def test_MUTATION_silence_with_a_session_still_running_is_NOT_death(beat, seat_present):
    """THE NULL CONTROL ON THE VERDICT, and the assertion that protects the shared tree.

    Twenty minutes of quiet is a commit gate grinding, not a corpse — this repo's gate runs
    for fifteen and has taken longer. If this ever goes DEAD, a handoff gets filed for work
    still in progress, a tick adopts it, and two writers edit one tree. That has cost this
    project before (2026-07-05).
    """
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS * 3)
    assert sc.state(path=p, now=NOW) == LIVE


def test_MUTATION_a_blind_probe_does_NOT_declare_death_on_its_own(beat, probe_blind):
    """R15 FAIL-SILENT, guarded in the safe direction: an unknown is not a verdict."""
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1)
    assert sc.state(path=p, now=NOW) == LIVE


def test_but_a_blind_probe_cannot_hold_a_dead_seat_alive_FOR_EVER(beat, probe_blind):
    """The other half of the same R15 clause, and the reason `CERTAINLY_DEAD_SECONDS` exists.

    Without this the previous test's conservatism becomes the defect: a permanently blind
    probe would mean a seat that stopped at breakfast is still "alive" at midnight, and the
    control could never fire at all — which is worse than not having it.
    """
    p, write = beat
    write(sc.CERTAINLY_DEAD_SECONDS + 1)
    assert sc.state(path=p, now=NOW) == DEAD


def test_no_heartbeat_at_all_is_ABSENT_not_DEAD(tmp_path, no_seat):
    """A machine with no seat has no dead seat. ABSENT files nothing."""
    assert sc.state(path=tmp_path / "nope.json", now=NOW) == ABSENT


def test_a_corrupt_heartbeat_is_ABSENT_not_alive(tmp_path, no_seat):
    p = tmp_path / ".seat_heartbeat.json"
    p.write_text("{ this is not json", encoding="utf-8")
    assert sc.state(path=p, now=NOW) == ABSENT


# ---------------------------------------------------------------------------
# note_activity(): written by the harness, on every tool call
# ---------------------------------------------------------------------------

def test_activity_stamps_the_tool_and_accumulates_a_tail(tmp_path):
    p = tmp_path / ".seat_heartbeat.json"
    for i, tool in enumerate(["Read", "Edit", "Bash"]):
        sc.note_activity(tool, session_id="s1", path=p, now=NOW + i)
    rec = json.loads(p.read_text())
    assert rec["tool_count"] == 3
    assert [t["tool"] for t in rec["recent_tools"]] == ["Read", "Edit", "Bash"]
    assert rec["ts"] == NOW + 2


def test_the_tail_is_BOUNDED(tmp_path):
    """It is a tail, not a transcript. Claude Code already keeps the transcript."""
    p = tmp_path / ".seat_heartbeat.json"
    for i in range(sc.TOOL_TAIL * 3):
        sc.note_activity("Bash", session_id="s1", path=p, now=NOW + i)
    assert len(json.loads(p.read_text())["recent_tools"]) == sc.TOOL_TAIL


def test_a_hook_failure_never_raises_into_the_session(tmp_path, monkeypatch):
    """A watcher that can break the thing it watches is worse than no watcher."""
    p = tmp_path / "unwritable" / ".seat_heartbeat.json"
    monkeypatch.setattr(sc.Path, "mkdir", lambda *a, **k: (_ for _ in ()).throw(OSError("nope")))
    sc.note_activity("Bash", session_id="s1", path=p, now=NOW)  # must not raise


# ---------------------------------------------------------------------------
# sweep(): the handoff, and what it has to carry
# ---------------------------------------------------------------------------

@pytest.fixture
def dead_seat_holding_work(beat, no_seat, tmp_path, monkeypatch):
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1)
    claims = tmp_path / ".claims.json"
    claims.write_text(json.dumps({
        "PB3_book_growth": {"claimed_at": NOW - 3600, "note": "starting the growth path",
                            "paths": ["simulation/net_new_acquisition.py"]},
    }), encoding="utf-8")
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", claims)
    monkeypatch.setattr(sc, "_uncommitted_paths",
                        lambda: ["simulation/net_new_acquisition.py", "docs/design/X.md"])
    monkeypatch.setattr(sc, "_last_commit", lambda: "abc1234 the commit before it died")
    return p


def test_a_dead_seat_files_a_handoff_into_staging(dead_seat_holding_work, tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    filed = sc.sweep(path=dead_seat_holding_work, now=NOW, staging_dir=staging)
    assert filed is not None
    docs = list(staging.glob("*.md"))
    assert len(docs) == 1


def test_the_handoff_carries_the_state_a_fresh_session_NEEDS(dead_seat_holding_work, tmp_path):
    """The subject is the CONTENT. A document that says "something stopped" recovers nothing.

    Three sources, and each one survives the death that produced it -- which is the point:
    anything the seat would have had to write about ITSELF is exactly what an API error stops
    it writing.
    """
    staging = tmp_path / "staging"
    staging.mkdir()
    sc.sweep(path=dead_seat_holding_work, now=NOW, staging_dir=staging)
    text = next(staging.glob("*.md")).read_text(encoding="utf-8")
    assert "PB3_book_growth" in text                      # what it claimed
    assert "starting the growth path" in text             # what it said it was doing
    assert "simulation/net_new_acquisition.py" in text    # what it left in the tree
    assert "docs/design/X.md" in text
    assert "abc1234" in text                              # where the finished part ended
    assert "Bash" in text or "Edit" in text               # where it had got to
    assert "Adopt" in text and "Discard" in text          # what to do about it


def test_the_handoff_is_written_ONCE_not_every_five_minutes(dead_seat_holding_work, tmp_path):
    """The sweep runs on a 5-minute timer. A dead seat must not file a document per tick."""
    staging = tmp_path / "staging"
    staging.mkdir()
    first = sc.sweep(path=dead_seat_holding_work, now=NOW, staging_dir=staging)
    second = sc.sweep(path=dead_seat_holding_work, now=NOW + 300, staging_dir=staging)
    assert first is not None and second is None
    assert len(list(staging.glob("*.md"))) == 1


def test_MUTATION_a_LIVE_seat_files_nothing(beat, seat_present, tmp_path, monkeypatch):
    """The null control on the whole mechanism: no death, no handoff, no noise."""
    p, write = beat
    write(60)
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda: ["a.py"])
    staging = tmp_path / "staging"
    staging.mkdir()
    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is None
    assert not list(staging.glob("*.md"))


def test_a_seat_that_died_holding_NOTHING_files_nothing(beat, no_seat, tmp_path, monkeypatch):
    """A clean tree and no claims is a session that finished. Filing here would be the noise
    this module exists to replace."""
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1)
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda: [])
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "no-claims.json")
    staging = tmp_path / "staging"
    staging.mkdir()
    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is None
    assert not list(staging.glob("*.md"))


# ---------------------------------------------------------------------------
# The gap the 5-minute sweep alone cannot close
# ---------------------------------------------------------------------------

def test_a_NEW_session_arriving_on_a_cold_heartbeat_hands_the_old_one_over(
    beat, no_seat, tmp_path, monkeypatch
):
    """THE RACE THE SWEEP MISSES, and the reason `note_activity` files handoffs at all.

    Seat dies at 10:00. A fresh session starts at 10:05 and runs a tool. Without this, the
    hook refreshes `ts` before the 20-minute silence threshold is ever reached, the sweep
    never sees a dead seat, and the dead session's uncommitted work is orphaned in silence --
    the exact outcome this module exists to prevent, reintroduced by its own heartbeat.
    """
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 60, session_id="old-session")
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda: ["half/an/edit.py"])
    monkeypatch.setattr(sc, "_last_commit", lambda: "deadbeef before it died")
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    sc.note_activity("Read", session_id="NEW-session", path=p, now=NOW,
                     staging_dir=staging)

    assert list(staging.glob("*.md")), "the predecessor's work must be handed over"
    rec = json.loads(p.read_text())
    assert rec["session_id"] == "NEW-session"
    assert rec["tool_count"] == 1, "a new session starts its own count, not the dead one's"


def test_MUTATION_the_SAME_session_on_a_cold_heartbeat_hands_nothing_over(
    beat, no_seat, tmp_path, monkeypatch
):
    """The null control: a slow tool call is not a new session.

    Same silence, same everything, one field different. If this filed a handoff, every commit
    gate that ran long would hand the seat's own live work to somebody else.
    """
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 60, session_id="s1")
    called = []
    monkeypatch.setattr(sc, "_handoff_for", lambda *a, **k: called.append(1))
    sc.note_activity("Read", session_id="s1", path=p, now=NOW)
    assert not called


def test_the_thresholds_are_ordered_so_the_escape_can_never_precede_the_verdict():
    """A guard on the two constants: the fail-silent escape must sit ABOVE the normal one.

    If `CERTAINLY_DEAD_SECONDS` were ever set below `SILENT_AFTER_SECONDS`, the two-signal
    verdict would be unreachable and every quiet seat would be declared dead without
    corroboration -- the conservative direction inverted by a constant edit.
    """
    assert sc.CERTAINLY_DEAD_SECONDS > sc.SILENT_AFTER_SECONDS


def test_a_SECOND_interruption_files_its_OWN_handoff(beat, no_seat, tmp_path, monkeypatch):
    """THE ONE THAT WOULD HAVE SILENTLY LOST WORK, caught by reading the filing path.

    `alarm_repetition` was changed on 2026-08-24 to hold ONE live document per signature --
    right for a recurring alarm about an unchanged condition, wrong here. Two interruptions
    are not one condition recurring: each carries a DIFFERENT set of uncommitted paths, so
    folding the second into the first would discard exactly the state this module exists to
    preserve. The subject varies by session for that reason.
    """
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    monkeypatch.setattr(sc, "_last_commit", lambda: "abc1234")
    staging = tmp_path / "staging"
    staging.mkdir()
    p, write = beat

    write(sc.SILENT_AFTER_SECONDS + 1, session_id="session-one")
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda: ["first/edit.py"])
    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is not None

    write(sc.SILENT_AFTER_SECONDS + 1, session_id="session-two")
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda: ["second/quite/different.py"])
    assert sc.sweep(path=p, now=NOW + 86_400, staging_dir=staging) is not None

    docs = sorted(staging.glob("*.md"))
    assert len(docs) == 2, f"each interruption needs its own handoff, got {docs}"
    bodies = "\n".join(d.read_text(encoding="utf-8") for d in docs)
    assert "first/edit.py" in bodies and "second/quite/different.py" in bodies


def test_the_heartbeat_hook_is_WIRED_into_settings_json():
    """THE POINT OF THE WHOLE MECHANISM: a hook with no caller is what shipped last time.

    `discovery_pass_ceiling` landed on 2026-08-19 against a director ruling, reached exactly
    one consumer, and watched the lane where the problem was not happening for five days. The
    same failure here is cheaper to make and harder to see: `note_activity` would keep passing
    its own unit tests while nothing ever called it, and the first anyone would learn of it is
    the next silent stall.

    Asserts the matcher too. A PreToolUse entry scoped to `Bash` would stamp on shell calls
    and not on a session that spent its last twenty minutes in Read and Edit — a heartbeat
    with holes in it, which is worse than none because it reads as a working control.
    """
    import json
    from pathlib import Path

    settings = json.loads(
        (Path(__file__).resolve().parents[2] / ".claude" / "settings.json").read_text()
    )
    entries = settings["hooks"]["PreToolUse"]
    wired = [
        e for e in entries
        if any("stamp_seat_heartbeat.py" in h.get("command", "") for h in e.get("hooks", []))
    ]
    assert wired, "the seat heartbeat hook is not wired into PreToolUse"
    assert wired[0].get("matcher") == "*", (
        f"the heartbeat must fire on EVERY tool, not {wired[0].get('matcher')!r}"
    )


def test_the_sweep_is_WIRED_into_the_five_minute_reconcile():
    """The other half of the same wiring question: who calls `sweep()` in production.

    Read as source rather than executed, because `reconcile_watch` runs a full process-and-
    schedule reconcile and importing it for this assertion would drag that in. The string is
    the contract; if the call site is renamed this reds and someone re-points it.
    """
    from pathlib import Path

    src = (Path(__file__).resolve().parents[2] / "background" / "reconcile_watch.py").read_text()
    assert "seat_continuity" in src and "seat_continuity.sweep()" in src, (
        "nothing in production calls seat_continuity.sweep() -- the mechanism is inert"
    )
