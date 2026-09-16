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
from pathlib import Path

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


def row(p, session_id="s1"):
    """One seat's row out of the keyed store.

    The store is `{"seats": {session_id: beat}}` since 2026-09-16, and the `beat` fixture above
    still writes the PRE-KEYED flat shape on purpose: it is what every linked worktree's git
    checkout of this tracked file holds, so `_adopt_legacy` reading it as a one-row store is a
    live path and not a migration artefact. Every leg below therefore exercises both shapes.
    """
    return sc._seats(json.loads(p.read_text())).get(session_id, {})


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
    rec = row(p)
    assert rec["tool_count"] == 3
    assert [t["tool"] for t in rec["recent_tools"]] == ["Read", "Edit", "Bash"]
    assert rec["ts"] == NOW + 2


def test_the_tail_is_BOUNDED(tmp_path):
    """It is a tail, not a transcript. Claude Code already keeps the transcript."""
    p = tmp_path / ".seat_heartbeat.json"
    for i in range(sc.TOOL_TAIL * 3):
        sc.note_activity("Bash", session_id="s1", path=p, now=NOW + i)
    assert len(row(p)["recent_tools"]) == sc.TOOL_TAIL


def test_TWO_SEATS_BEATING_AT_ONCE_ARE_TWO_ROWS_AND_NEITHER_OVERWRITES_THE_OTHER(tmp_path):
    """THE DEFECT THE KEYED STORE WAS BUILT FOR, measured live on 2026-09-16T14:20Z: two seats
    beating in two trees at once, into a record that could hold one.

    Under the old single-record store the later beat replaced the earlier one wholesale, so the
    population had exactly one survivor and every reader got the survivor's answer.
    """
    p = tmp_path / ".seat_heartbeat.json"
    sc.note_activity("Bash", session_id="seat-A", path=p, now=NOW)
    sc.note_activity("Read", session_id="seat-B", path=p, now=NOW + 1)
    sc.note_activity("Edit", session_id="seat-A", path=p, now=NOW + 2)

    seats = sc._seats(json.loads(p.read_text()))
    assert set(seats) == {"seat-A", "seat-B"}
    assert seats["seat-A"]["tool_count"] == 2, "B's beat swallowed A's history"
    assert seats["seat-B"]["tool_count"] == 1, "A's beat swallowed B's history"
    assert [t["tool"] for t in seats["seat-A"]["recent_tools"]] == ["Bash", "Edit"]


def test_a_seat_with_NO_session_id_still_gets_its_OWN_row(tmp_path):
    """The degenerate key, and the direction it must not collapse in.

    The hook can hand us a payload without a session id. Keying every such seat on `""` would
    rebuild the single-valued record in the one case nobody would think to look at, so the key
    falls back to pid-and-tree — a weaker identity, but an identity.
    """
    p = tmp_path / ".seat_heartbeat.json"
    sc.note_activity("Bash", session_id="", pid=111, path=p, now=NOW)
    sc.note_activity("Read", session_id="", pid=222, path=p, now=NOW + 1)
    assert len(sc._seats(json.loads(p.read_text()))) == 2


def test_the_store_is_BOUNDED_and_drops_the_OLDEST_beats(tmp_path):
    """Rows are removed as they are swept, so hitting the ceiling means the sweep has stopped.
    Dropping oldest-first is the direction that keeps the LIVE seats the executor must see."""
    p = tmp_path / ".seat_heartbeat.json"
    for i in range(sc.MAX_SEATS + 5):
        sc.note_activity("Bash", session_id=f"seat-{i:03d}", path=p, now=NOW + i)
    seats = sc._seats(json.loads(p.read_text()))
    assert len(seats) == sc.MAX_SEATS
    assert "seat-000" not in seats and f"seat-{sc.MAX_SEATS + 4:03d}" in seats


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
                        lambda tree=None: ["simulation/net_new_acquisition.py", "docs/design/X.md"])
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: "abc1234 the commit before it died")
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
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: ["a.py"])
    staging = tmp_path / "staging"
    staging.mkdir()
    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is None
    assert not list(staging.glob("*.md"))


def test_a_seat_that_died_holding_NOTHING_files_nothing(beat, no_seat, tmp_path, monkeypatch):
    """A clean tree and no claims is a session that finished. Filing here would be the noise
    this module exists to replace."""
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1)
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: [])
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "no-claims.json")
    staging = tmp_path / "staging"
    staging.mkdir()
    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is None
    assert not list(staging.glob("*.md"))


# ---------------------------------------------------------------------------
# The gap the 5-minute sweep alone used to be unable to close
# ---------------------------------------------------------------------------

def test_a_NEW_session_arriving_on_a_cold_heartbeat_does_NOT_DESTROY_the_old_ones_state(
    beat, no_seat, tmp_path, monkeypatch
):
    """THE RACE THE SWEEP USED TO MISS — re-keyed to the PROPERTY, not to the old mechanism.

    Seat dies at 10:00. A fresh session starts at 10:05 and runs a tool. On the single-record
    store that beat OVERWROTE the dead seat's only record: `ts` was refreshed before the
    20-minute silence threshold was ever reached, the sweep never saw a dead seat, and the dead
    session's uncommitted work was orphaned in silence. `note_activity` answered it by filing
    the handoff itself, inline, before overwriting.

    The keyed store answers it by not overwriting anything, so the inline filing was deleted.
    This test therefore asserts what was actually wanted — the predecessor's state SURVIVES a
    new session's arrival and is still there for `sweep()` — rather than that a particular
    mechanism ran. Keyed to the old mechanism it would have gone red on the repair that made it
    unnecessary, which is exactly backwards (CLAUDE.md: key a control to the property).
    """
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 60, session_id="old-session")
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: ["half/an/edit.py"])
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: "deadbeef before it died")
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    sc.note_activity("Read", session_id="NEW-session", path=p, now=NOW, staging_dir=staging)

    survivor = row(p, "old-session")
    assert survivor, "the new session's beat destroyed the dead seat's record"
    assert survivor["ts"] == NOW - (sc.SILENT_AFTER_SECONDS + 60), "its clock was refreshed"
    assert row(p, "NEW-session")["tool_count"] == 1, "a new session starts its own count"

    filed = sc.sweep(path=p, now=NOW, staging_dir=staging)
    assert filed, "the sweep could not reach the state the new session had left intact"
    assert "half/an/edit.py" in (tmp_path / "staging" / Path(filed).name).read_text()


def test_MUTATION_a_LIVE_seat_in_ANOTHER_TREE_cannot_suppress_a_dead_seats_handoff(
    no_seat, tmp_path, monkeypatch
):
    """THE FAIL-SILENT THAT MADE THE SHARED-TREE REDIRECT REFUSABLE, now the thing under test.

    Two seats beat into one book. One dies holding work; the other is alive and stamping. On a
    single-valued record the live seat's beat IS the record, `state()` reads LIVE, `sweep()`
    never fires, and the dead seat's uncommitted work is orphaned — the survivor's answer, in
    the one place it files nothing. This is the leg that fires if `sweep()` is ever rewritten
    to consult the population verdict instead of walking rows.
    """
    p = tmp_path / ".seat_heartbeat.json"
    sc.note_activity("Edit", session_id="dead-seat", path=p, now=NOW - sc.SILENT_AFTER_SECONDS - 60)
    sc.note_activity("Bash", session_id="live-seat", path=p, now=NOW - 5)
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: ["orphaned/work.py"])
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: "abc1234")
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")

    assert sc.state(path=p, now=NOW) == LIVE, "the population verdict is the union, by design"
    filed = sc.sweep(path=p, now=NOW, staging_dir=staging)
    assert filed, "a live seat suppressed a dead seat's handoff"
    assert not row(p, "dead-seat"), "the swept row must be removed"
    assert row(p, "live-seat"), "sweeping one seat deleted a LIVE seat's row"


def test_MUTATION_the_SAME_session_on_a_cold_heartbeat_hands_nothing_over(
    beat, no_seat, tmp_path, monkeypatch
):
    """The null control: a slow tool call is not a death.

    Same silence, same everything, and the seat is still beating into its own row. If a long
    commit gate could hand the seat's own live work to somebody else, every fifteen-minute gate
    run would fork the tree — the expensive error this module refuses to make.
    """
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 60, session_id="s1")
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: ["still/being/edited.py"])
    sc.note_activity("Read", session_id="s1", path=p, now=NOW, staging_dir=staging)
    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is None
    assert not list(staging.glob("*.md"))


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
    right for a recurring alarm about an unchanged condition, wrong when the second
    interruption is holding something else entirely: folding it into the first would discard
    exactly the state this module exists to preserve.

    THE SUBJECT USED TO VARY BY SESSION ID FOR THIS REASON AND THAT WAS THE WRONG DISCRIMINATOR
    (2026-08-25) -- it made every interruption distinct, including eighteen consecutive ones
    over the same unadopted work. It then varied by the AREAS of the held work, which was the
    wrong discriminator too: a tree whose dirty set moved by one directory filed another
    document, and the director found NINE of them in the staging root on 2026-08-28, all
    saying the same thing and all ahead of his own guidance in an alphabetical draw.

    NEITHER ARGUMENT LOSES, AND THIS TEST IS NOW ABOUT THE SECOND ONE ONLY (2026-08-28). The
    identity is the CONDITION -- one document, keyed `seat-continuity` -- and the payload is
    the EPISODE, appended as its own section. So the property this test has always been
    about, that the second death's held state is not silently discarded, is asserted on the
    CONTENT rather than on the file count. Its sibling
    `test_the_SAME_unadopted_work_across_two_deaths_is_ONE_document` is the other half, and
    the two together are the actual contract.
    """
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: "abc1234")
    staging = tmp_path / "staging"
    staging.mkdir()
    p, write = beat

    write(sc.SILENT_AFTER_SECONDS + 1, session_id="session-one")
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: ["first/edit.py"])
    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is not None

    write(sc.SILENT_AFTER_SECONDS + 1, session_id="session-two")
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: ["second/quite/different.py"])
    assert sc.sweep(path=p, now=NOW + 86_400, staging_dir=staging) is not None

    docs = sorted(staging.glob("*.md"))
    assert len(docs) == 1, "one condition, one queue item"
    text = docs[0].read_text(encoding="utf-8")
    assert "first/edit.py" in text, "the FIRST death's held state was overwritten"
    assert "second/quite/different.py" in text, (
        "the SECOND death's held state was discarded -- exactly the loss the 2026-08-25 "
        "argument warned about, and the reason the episodes are appended rather than folded"
    )
    assert text.count(sc.EPISODES_HEADING) == 1, "one heading, however many episodes"
    assert text.count("#### What it left in the tree") == 2, "two deaths, two episodes"



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


# ---------------------------------------------------------------------------
# The eighteen copies (2026-08-25) -- and the two halves that must stay true
# ---------------------------------------------------------------------------

def test_the_SAME_unadopted_work_across_two_deaths_is_ONE_document(
    beat, no_seat, tmp_path, monkeypatch
):
    """THE DEFECT, IN MINIATURE. Measured on the live tree the morning it was found: eighteen
    handoff documents in nine hours -- SESSION_B_C_D_A_A_E, SESSION_F_E_EE_A_E, SESSION_C_C_A
    and fifteen more -- one every thirty minutes, all listing the same paths, every one of them
    saying "Nothing was claimed". They filled the head of the tick's draw queue and pushed three
    self-drawable mints to positions 43-46 of 48, where no bounded session ever reached them.

    A second seat dying over work nobody has adopted yet is the SAME condition continuing, and
    `alarm_repetition` already knows how to say that: it appends a dated still-live line to the
    document that exists. What defeated it was the session id in the subject.
    """
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: "abc1234")
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: ["simulation/hedged_settlement.py"])
    staging = tmp_path / "staging"
    staging.mkdir()
    p, write = beat

    write(sc.SILENT_AFTER_SECONDS + 1, session_id="c7e894aa-3221-45f7-8713-b1a18a6232a9")
    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is not None
    write(sc.SILENT_AFTER_SECONDS + 1, session_id="f0e2ee4a-e5b1-4c3d-9a2b-77c0d5e1a884")
    sc.sweep(path=p, now=NOW + 1800, staging_dir=staging)

    docs = sorted(staging.glob("*.md"))
    assert len(docs) == 1, (
        f"the same unadopted work filed {len(docs)} documents; every one of them is a page of "
        f"the tick's draw queue spent on work already in it: {[d.name for d in docs]}"
    )


def test_the_document_SAYS_what_work_it_is_about(beat, no_seat, tmp_path, monkeypatch):
    """A reader must be able to see what is held, and the session id must never be the subject.

    THIS USED TO ASSERT ON THE FILENAME (2026-08-25: "the handoff is not named for what it
    holds, so the queue cannot be read"). The concern was right and the remedy put a VARYING
    payload into the IDENTITY, which is what filed nine documents about one condition. The
    filename now names the condition; the document says what is held, which is where a reader
    was going to look anyway once the queue is one item instead of nine.
    """
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: "abc1234")
    monkeypatch.setattr(sc, "_uncommitted_paths",
                        lambda tree=None: ["simulation/hedged_settlement.py", "tests/simulation/t.py"])
    staging = tmp_path / "staging"
    staging.mkdir()
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1, session_id="c7e894aa-3221-45f7-8713-b1a18a6232a9")
    sc.sweep(path=p, now=NOW, staging_dir=staging)

    doc = next(staging.glob("*.md"))
    text = doc.read_text(encoding="utf-8")
    assert "simulation/hedged_settlement.py" in text and "tests/simulation/t.py" in text, (
        "the handoff does not say what it holds, so the queue cannot be read"
    )
    assert "C7E894AA" not in doc.name.upper(), "the session id is back in the subject"
    assert "C7E894AA" not in text.upper(), "the session id is back in the body"


# ---------------------------------------------------------------------------
# The handoff is about the tree the DEAD SEAT was in, not the one sweeping it
# ---------------------------------------------------------------------------

def test_the_handoff_reads_the_tree_the_DEAD_SEAT_was_beating_in(no_seat, tmp_path, monkeypatch):
    """THE DEFECT THE KEYED STORE INTRODUCES IF NOBODY LOOKS FOR IT, and it fired no leg until
    this one existed.

    One book per machine means the shared tree's 5-minute sweep now files for seats that died in
    LINKED WORKTREES. Their uncommitted work is in THEIR tree. A handoff built from the sweeper's
    own `PROJECT_DIR` would be confidently, plausibly wrong — it would name real files, really
    held by somebody, just not by the seat the document is about, and the next tick would adopt
    another lane's live work on the strength of it.

    Found by mutation: replacing `_uncommitted_paths(rec.get("tree"))` with `_uncommitted_paths()`
    passed the entire suite, because every other fixture stubs that function with a lambda that
    ignores its argument. That is the equivalence-or-missing-test question answered the unflattering
    way, so the stub here DISCRIMINATES ON THE TREE instead of ignoring it.
    """
    p = tmp_path / ".seat_heartbeat.json"
    dead_tree, sweeper_tree = tmp_path / "linked-worktree", tmp_path / "shared"
    for t in (dead_tree, sweeper_tree):
        t.mkdir()
    monkeypatch.setattr(sc, "PROJECT_DIR", sweeper_tree)
    monkeypatch.setattr(sc, "_uncommitted_paths", lambda tree=None: (
        ["a-lane-the-dead-seat-held/its_edit.src"] if Path(tree or "") == dead_tree
        else ["a-lane-still-live/another_lanes_work.src"]))
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: (
        "dead1234 on the worktree" if Path(tree or "") == dead_tree else "swept999 on the shared tree"))
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")

    sc.note_activity("Edit", session_id="died-in-a-worktree", path=p,
                     now=NOW - sc.SILENT_AFTER_SECONDS - 60)
    assert row(p, "died-in-a-worktree")["tree"] == str(sweeper_tree)
    # ...and that seat was in the LINKED worktree, which is what the row has to remember.
    store = json.loads(p.read_text())
    store["seats"]["died-in-a-worktree"]["tree"] = str(dead_tree)
    p.write_text(json.dumps(store), encoding="utf-8")

    staging = tmp_path / "staging"
    staging.mkdir()
    filed = sc.sweep(path=p, now=NOW, staging_dir=staging)
    text = Path(filed).read_text(encoding="utf-8")

    # THE FIXTURE PATHS ARE DELIBERATELY NOT REAL TREE PATHS. What is asserted on below is the
    # generated handoff MARKDOWN, not Python source -- but a literal under a real top-level
    # directory makes `substring_source_scan_census` read this as a control scanning source as
    # text, which it is not. Fictional prefixes say what the stub is and clear the detector
    # without routing a non-member through the remedy for members.
    assert "a-lane-the-dead-seat-held/its_edit.src" in text
    assert "a-lane-still-live/another_lanes_work.src" not in text, (
        "the handoff listed the SWEEPER's uncommitted work as the dead seat's: a tick adopting "
        "this would edit files another live lane is holding")
    assert "dead1234" in text and "swept999" not in text
    assert str(dead_tree) in text, "the reader is not told which tree to cd to"


def test_a_seat_whose_TREE_IS_GONE_files_anyway_and_does_not_read_as_CLEAN(
    no_seat, tmp_path, monkeypatch
):
    """A linked worktree removed since the seat died is an UNKNOWN, never an empty tree.

    `_uncommitted_paths` returning `[]` here would hit `_handoff_for`'s died-holding-nothing
    guard and file silently nothing — the R15 fail-silent, reached by the one input the keyed
    store makes reachable (the sweeper outliving the tree it is filing about).
    """
    p = tmp_path / ".seat_heartbeat.json"
    sc.note_activity("Edit", session_id="s1", path=p, now=NOW - sc.SILENT_AFTER_SECONDS - 60)
    store = json.loads(p.read_text())
    store["seats"]["s1"]["tree"] = str(tmp_path / "a-worktree-that-was-deleted")
    p.write_text(json.dumps(store), encoding="utf-8")
    from background import seat_work_in_hand
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")

    assert sc._uncommitted_paths(tmp_path / "a-worktree-that-was-deleted") is None
    staging = tmp_path / "staging"
    staging.mkdir()
    filed = sc.sweep(path=p, now=NOW, staging_dir=staging)
    assert filed, "a vanished tree read as a clean one and the death was filed nowhere"
    assert "UNKNOWN, not empty" in Path(filed).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# _uncommitted_paths: source, not the daemons' own exhaust
# ---------------------------------------------------------------------------

def test_the_held_paths_are_SOURCE_and_exclude_the_daemons_own_output(monkeypatch):
    """A bare `git status --porcelain` answered 582 on the live tree, of which 397 were
    documents in `docs/staging/` and 84 were logs under `docs/observability/` that daemons
    rewrite every minute. The handoff listed sixty log files, said "…and 499 more", and buried
    the 49 real source paths -- an entire uncommitted VAT-basis repair among them.

    THE EXCLUSION IS NOT RE-IMPLEMENTED HERE, and the test is shaped to prove that rather than
    to re-state it: `tree_divergence` already owns the list of what the machine rewrites, for
    the daily squatting report, and a second copy of it in this module would be a second opinion
    that drifts. So this asserts the DELEGATION plus the one exclusion that is genuinely local.
    """
    from background import tree_divergence

    # The inherited half -- daemon output never reaches this module at all.
    assert tree_divergence._is_generated("docs/observability/worker-tick-log.md")
    assert tree_divergence._is_generated("site/data/customers.json")

    # The local half -- a staged doc is already IN the draw, so naming it as unadopted work
    # tells the reader about the queue he is reading it from.
    monkeypatch.setattr(tree_divergence, "changed_paths", lambda _d=None: [
        "simulation/hedged_settlement.py",
        "docs/staging/WORKER_FINDING_SOMETHING_2026-08-25.md",
    ])
    assert sc._uncommitted_paths() == ["simulation/hedged_settlement.py"]


def test_a_seat_that_died_holding_ONLY_MACHINE_OUTPUT_files_NOTHING(
    beat, no_seat, tmp_path, monkeypatch
):
    """THE GUARD THAT HAD BECOME UNREACHABLE. `_handoff_for` has always said "died holding
    nothing, file nothing" -- but the old `git status --porcelain` counted `docs/observability/`,
    which is never clean, so the condition could not be true and every dead seat filed, forever,
    whatever it had or had not been doing.

    The stub returns what `changed_paths` really returns (it has already dropped observability
    and site/ itself); what is left to exercise here is the staging exclusion, which is this
    module's own and is the self-referential half -- the handoff counting the previous handoff.
    """
    from background import seat_work_in_hand, tree_divergence
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    monkeypatch.setattr(tree_divergence, "changed_paths",
                        lambda _d=None: ["docs/staging/WORKER_FINDING_X_2026-08-25.md",
                                         "docs/staging/in_progress/PLANNER_MINTED_y.md"])
    staging = tmp_path / "staging"
    staging.mkdir()
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1)

    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is None
    assert not list(staging.glob("*.md"))


def test_MUTATION_one_real_source_path_among_the_exhaust_still_files(
    beat, no_seat, tmp_path, monkeypatch
):
    """The null half of the test above -- without it, "files nothing" would also be satisfied by
    a filter that swallowed everything, which is the fail-open shape R15 names second."""
    from background import seat_work_in_hand, tree_divergence
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: "abc1234")
    monkeypatch.setattr(tree_divergence, "changed_paths",
                        lambda _d=None: ["docs/staging/WORKER_FINDING_X_2026-08-25.md",
                                         "simulation/hedged_settlement.py"])
    staging = tmp_path / "staging"
    staging.mkdir()
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1)

    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is not None
    text = next(staging.glob("*.md")).read_text(encoding="utf-8")
    assert "simulation/hedged_settlement.py" in text
    assert "WORKER_FINDING_X" not in text


def test_an_UNREADABLE_tree_files_ANYWAY_and_says_the_list_is_UNKNOWN(
    beat, no_seat, tmp_path, monkeypatch
):
    """R15 fail-silent, in the direction this repo has already ruled on for alarms: "a git
    failure returns None, which the caller must treat as a FAILED check. For an ALARM the safe
    failure is to page anyway -- never to suppress on a check that did not run."

    Rendering an unreadable tree as a clean one would tell the reader the seat left nothing,
    which is the single most expensive sentence this document could contain.
    """
    from background import seat_work_in_hand, tree_divergence
    monkeypatch.setattr(seat_work_in_hand, "CLAIMS_FILE", tmp_path / "none.json")
    monkeypatch.setattr(sc, "_last_commit", lambda tree=None: "abc1234")
    monkeypatch.setattr(tree_divergence, "changed_paths", lambda _d=None: None)
    staging = tmp_path / "staging"
    staging.mkdir()
    p, write = beat
    write(sc.SILENT_AFTER_SECONDS + 1)

    assert sc.sweep(path=p, now=NOW, staging_dir=staging) is not None
    text = next(staging.glob("*.md")).read_text(encoding="utf-8")
    assert "could not be read" in text and "UNKNOWN, not empty" in text
    assert "The tree is clean" not in text
