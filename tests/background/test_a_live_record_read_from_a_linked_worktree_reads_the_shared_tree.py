#!/usr/bin/env python3
"""A LIVE RECORD READ FROM A LINKED WORKTREE MUST READ THE SHARED TREE'S COPY.

THE DEFECT THIS FIRES ON, measured 2026-09-16 and not hypothetical.
`docs/observability/.publish_gate_state.json` is TRACKED. Its only commit is `f534b9f3d`
(2026-07-17), content `{"alerted_at": null, "failures": []}`. Every linked worktree -- which is
where the seat executor mandates that delivery turns run -- checks that placeholder out. Handed
to `process_run_complete._read_publish_gate_state`, every `setdefault` in it lands on the
flattering value: `episode_failures` 0, `total_red` 0, `wedge_since` None,
`state_unavailable` False. It reads as a publisher that has never failed. The live file on the
shared tree at the same moment read `episode_failures: 34`, `last_clean_publish: null`, and
`blocking_tests` naming a test that had already been fixed.

A drawn Lane 0 item walked into exactly this: its done-condition was "read
`.publish_gate_state.json` for `last_clean_publish != null` and `episode_failures == 0`", and
followed literally from the worktree it was issued in, the placeholder answers *yes* to the
second clause and omits the first. Releasing the claim on that reading would have recorded a
146-hour publish wedge as cleared on the strength of a two-month-old empty file.

WHY IT IS A CLASS AND NOT AN INSTANCE (R10). `guard_live_ledger_write` fixed the WRITE side at
the choke point and derives its room -- anything under `docs/observability/` -- rather than
listing it. The READ side had been fixed once, privately, for one file:
`seat_executor._shared_tree_log`, after the same rebinding made `ids_run_since` answer `[]` and
an orientation report `drawn: [], steered: false`. Statically, 75 live-state paths are written
by the daemons; 30 are tracked; 23 had HEAD content differing from live when this was measured.
One of the 23 was closed. This closes the room.

CORRECTION, 2026-09-16, LEFT BESIDE THE CLAIM IT CORRECTS. "This closes the room" was wrong on
two counts and both were found by asking the tracked set the question directly rather than
trusting the enumeration. (1) The room is 54 tracked records whose live bytes differ from HEAD's,
not 23; 23 was the subset that had been listed. (2) `.publish_gate_state.json` -- the file this
whole control is named for -- had THREE readers and the commit wired one. The other two were
`supervisor._publish_gate_wedge_active` and `model_tier_report._gate_failures`, and both answered
"no failures" on the placeholder. The head was open while this docstring said the tail was the
work. The five legs at the bottom of this file wire the readers proven flattering; the survey and
the four readers proven FAIL-SAFE (and so deliberately left alone) are in
`docs/staging/SEAT_FINDING_THE_LIVE_RECORD_RESOLVER_WAS_NOT_EVEN_WIRED_INTO_THE_OTHER_TWO_READERS_OF_THE_FILE_IT_WAS_NAMED_FOR_2026-09-16.md`.

WHAT CAN FAIL HERE. The redirect is the rare branch, so it is asserted REACHABLE over the whole
partition before anything asserts what it does -- a resolver that redirected NOTHING would pass
every "does it leave ordinary paths alone" leg on its own.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT))

from background.live_ledger_guard import shared_tree_live_record  # noqa: E402

LIVE = json.dumps({"episode_failures": 34, "last_clean_publish": None})
STALE = json.dumps({"alerted_at": None, "failures": []})


def _git(*args, cwd):
    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args],
        cwd=str(cwd), capture_output=True, text=True, check=True)


@pytest.fixture
def trees(tmp_path):
    """A real main tree and a real linked worktree, with the record TRACKED and the worktree's
    checkout deliberately stale -- the shape git actually produces, not a mock of it."""
    main = tmp_path / "main"
    main.mkdir()
    _git("init", "-q", "-b", "main", cwd=main)
    rec = main / "docs" / "observability"
    rec.mkdir(parents=True)
    (rec / "state.json").write_text(STALE)          # what gets COMMITTED, as on 2026-07-17
    _git("add", "-A", cwd=main)
    _git("commit", "-qm", "placeholder", cwd=main)

    linked = tmp_path / "linked"
    _git("worktree", "add", "-q", "--detach", str(linked), cwd=main)

    # The shared tree's copy moves on; the worktree keeps git's checkout of the placeholder.
    (rec / "state.json").write_text(LIVE)
    assert (linked / "docs" / "observability" / "state.json").read_text() == STALE, \
        "fixture is not reproducing the defect: the worktree checkout should be the placeholder"
    return main, linked


def _patched(monkeypatch, tree):
    import background.live_ledger_guard as g
    monkeypatch.setattr(g, "PROJECT_DIR", tree)
    monkeypatch.setattr(g, "LIVE_RECORD_DIR", tree / "docs" / "observability")


def test_the_partition_is_reachable_in_both_directions(trees, monkeypatch):
    """ONE control over the WHOLE partition, written first and deliberately.

    Every other test below asks "does it leave X alone". A resolver whose body was
    `return path` -- the exact pre-fix behaviour -- passes all of them. This is the only
    assertion that cannot be satisfied by doing nothing, so it is the one that proves the
    branch can be TAKEN before anything asserts what taking it does."""
    main, linked = trees
    record = "docs/observability/state.json"

    _patched(monkeypatch, linked)
    redirected = shared_tree_live_record(linked / record)

    _patched(monkeypatch, main)
    left_alone = shared_tree_live_record(main / record)

    assert redirected != linked / record, \
        "the linked worktree's read was NOT redirected -- the rare branch is unreachable"
    assert left_alone == main / record, \
        "the main tree's read WAS redirected -- the resolver fires on everything, so it grades nothing"


def test_the_linked_worktree_reads_the_live_figure_not_the_checked_out_placeholder(trees, monkeypatch):
    """The defect in its own terms: 34 failures, not a clean publisher."""
    main, linked = trees
    _patched(monkeypatch, linked)

    resolved = shared_tree_live_record(linked / "docs" / "observability" / "state.json")

    # `.get`, not `[...]`: the placeholder does not merely carry a WRONG figure, it carries NO
    # such key -- and the reader's own setdefault is what turns that absence into a clean 0. A
    # KeyError here would grade the same defect with a traceback instead of a reading.
    assert json.loads(resolved.read_text()).get("episode_failures") == 34, (
        "a delivery turn in a linked worktree read the committed placeholder as live state -- "
        "this is how a 146-hour publish wedge reads as never having failed")


def test_a_path_outside_the_live_record_room_is_never_redirected(trees, monkeypatch):
    """The room is the same room `is_live_record_path` derives. A source file that happens to
    sit in a worktree is not a live record and must not be re-pointed at another tree."""
    main, linked = trees
    outside = linked / "background" / "supervisor.py"

    _patched(monkeypatch, linked)

    assert shared_tree_live_record(outside) == outside


def test_a_record_the_shared_tree_does_not_have_falls_back_to_the_callers_own_path(trees, monkeypatch):
    """FAILS TO THE CALLER'S EXISTING BEHAVIOUR. Every caller already handles a missing file;
    turning that into a raise would break orientation paths that must survive it."""
    main, linked = trees
    only_here = linked / "docs" / "observability" / "never_committed.json"
    only_here.write_text("{}")

    _patched(monkeypatch, linked)

    assert shared_tree_live_record(only_here) == only_here


def test_the_publish_gate_reader_routes_through_the_resolver(tmp_path, monkeypatch):
    """THE WIRING, graded by behaviour rather than by reading the call site.

    Reverting `_read_publish_gate_state` to read `PUBLISH_GATE_STATE_FILE` directly makes this
    fail: the substituted resolver would be ignored and the live figure never seen."""
    import background.process_run_complete as pcr

    live = tmp_path / "state.json"
    live.write_text(json.dumps({"failures": [], "alerted_at": None, "episode_failures": 34,
                                "last_clean_publish": None}))
    monkeypatch.setattr(pcr, "shared_tree_live_record", lambda _p: live)

    state = pcr._read_publish_gate_state()

    assert state["episode_failures"] == 34, (
        "the publish gate reader did not resolve its state file through shared_tree_live_record, "
        "so in a linked worktree it reads git's checkout instead of the live record")


# ---------------------------------------------------------------------------
# THE WIRING, one leg per reader proven FLATTERING on the stale copy (2026-09-16).
#
# EVERY LEG IS BUILT THE SAME WAY AND THE SHAPE IS THE POINT. Two fixture directories:
# `stale/` holds what git checks out into a linked worktree, `live/` holds what the daemons
# actually wrote. The reader's MODULE CONSTANT is pointed at `stale/`, and the resolver in that
# reader's namespace is substituted with one that maps any path to its `live/` twin. So:
#
#   * wired   -> the reader resolves, reads `live/`, and reports the alarming answer;
#   * reverted to the bare constant -> it reads `stale/` and reports the flattering one.
#
# The constant is redirected too, deliberately. Substituting ONLY the resolver would leave a
# reverted reader reading the REAL `docs/observability/` file on this machine -- a control keyed
# to whatever the shared tree happens to hold today, which is the failure mode CLAUDE.md names:
# it goes red when the code becomes more honest and green when the claim rots.
#
# PRE-REGISTERED before these were run: reverting any ONE reader fails exactly its own leg and no
# other. A revert that fails nothing means the leg is a tautology; a revert that fails several
# means they are grading one thing while claiming five.
# ---------------------------------------------------------------------------


@pytest.fixture
def stale_and_live(tmp_path):
    """`(stale_dir, live_dir, resolver)` -- the two trees a linked worktree sees at once."""
    stale = tmp_path / "stale"
    live = tmp_path / "live"
    stale.mkdir()
    live.mkdir()

    def resolver(path):
        twin = live / Path(path).name
        return twin if twin.exists() else Path(path)

    return stale, live, resolver


def test_the_supervisors_wedge_draw_sees_the_live_failures_not_the_committed_placeholder(
        stale_and_live, monkeypatch):
    """`_publish_gate_wedge_active` returning None is SILENCE, and silence was the flattering
    answer: git's copy holds `{"failures": []}`, `len([]) < PUBLISH_GATE_WEDGE_MIN_FAILURES`, no
    wedge, no RUNG-1 draw -- against a live record that said the gate had failed 37 times.

    BOTH HALVES ARE REDIRECTED AND THAT IS LOAD-BEARING. This control's independence rests on
    `.publish_gate_state.json` and `.last_tested_hash` being different SOURCES, never different
    TREES; wiring one and not the other would have made it compare a live wedge against a
    two-month-old pass and call the failures stale."""
    import time

    import background.supervisor as sup
    stale, live, resolver = stale_and_live

    now = time.time()
    # TWO CLOCKS, AND THEY MUST NOT BE ONE VALUE. The wedge's AGE is composed from
    # `wedge_since`/`alerted_at`; its COUNT is composed from failures the WRITER'S WINDOW still
    # admits. This fixture stamped both from a single `now - 4h`, which was harmless for as long
    # as the reader counted the list whole -- and stopped being harmless on 2026-09-24, when
    # `_failure_is_in_window` began trimming on read. Every failure then fell outside
    # PUBLISH_GATE_WINDOW_SECONDS, the count went to zero, and the function returned None at the
    # `len(failures) < MIN` line WITHOUT EVER REACHING the resolver this leg exists to grade. The
    # leg was red for eleven days and the red was the fixture's, not the redirect's.
    #
    # Both bounds are the reader's own objects, imported, never mirrored literals -- so a window
    # or threshold that moves moves this fixture with it instead of silently emptying it again.
    wedge_started = now - 4 * sup.PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS   # well over the age bar
    observed = now - sup.PUBLISH_GATE_WINDOW_SECONDS / 4               # well inside the window
    failures = [{"ts": observed + i, "reason": "red", "git_hash": "aaaaaaaaa"} for i in range(5)]

    (stale / ".publish_gate_state.json").write_text(json.dumps({"alerted_at": None, "failures": []}))
    (live / ".publish_gate_state.json").write_text(
        json.dumps({"alerted_at": wedge_started, "wedge_since": wedge_started,
                    "failures": failures}))
    # Neither copy of the cross-check names HEAD, so the "a pass superseded these" escape is shut
    # in both worlds -- the ONLY thing that differs between them is the failure list.
    # THE STALE HASH NAMES HEAD, and that is the whole point of this half. A linked worktree is
    # checked out at some commit; git's blob for `.last_tested_hash` is a sha from that same
    # history, and a worktree detached AT that sha reads "the gate passed at HEAD" -- the escape
    # clause, which returns None. The live record names a different sha, so no pass supersedes.
    # A first draft wrote two arbitrary shas here and the leg could not fail: with NEITHER copy
    # naming HEAD the escape was shut in both worlds, so resolved and unresolved agreed. That is
    # a fixture that does not discriminate, not an equivalence in the code.
    (stale / ".last_tested_hash").write_text("deadbeef0")
    (live / ".last_tested_hash").write_text("11ve00000")

    monkeypatch.setattr(sup, "PUBLISH_GATE_STATE_FILE", stale / ".publish_gate_state.json")
    monkeypatch.setattr(sup, "LAST_TESTED_HASH_FILE", stale / ".last_tested_hash")

    # CONTROL ARM, RUN FIRST AND DELIBERATELY: the resolver reverted to the identity it was before
    # 2026-09-16. Without it this leg cannot tell a working redirect from a fixture that would draw
    # a wedge off whichever tree it read -- and a leg that cannot tell is how the eleven-day red
    # above went unread as "the redirect is broken" when the redirect was fine.
    monkeypatch.setattr(sup, "shared_tree_live_record", lambda path: path)
    assert sup._publish_gate_wedge_active(now=now, head="deadbeef0") is None, (
        "THE FIXTURE DOES NOT DISCRIMINATE: the UNREDIRECTED reader drew a wedge from the "
        "committed placeholder, so the positive assertion below would pass on a resolver that "
        "redirects nothing")

    monkeypatch.setattr(sup, "shared_tree_live_record", resolver)

    drawn = sup._publish_gate_wedge_active(now=now, head="deadbeef0")

    assert drawn is not None, (
        "the supervisor's publish-gate wedge draw read git's checked-out placeholder: a gate "
        "wedged for hours with 5 in-window failures reads as never having failed, so RUNG 1 never "
        "fires and nothing pages -- the silent direction, which is why this was invisible")


def test_the_operational_red_draw_sees_the_live_signal_not_a_frozen_green(
        stale_and_live, monkeypatch):
    """The flattering direction here is not a wrong value but a FROZEN one. The only
    `last_result` that draws is a red, and a tracked file's checkout holds what was committed
    forever -- so a linked worktree could never draw this rung however red the layer went. It
    agreed with live on the day this was found, by luck. It could not have disagreed."""
    import time

    import background.supervisor as sup
    stale, live, resolver = stale_and_live

    now = time.time()
    (stale / ".operational_layer_signal.json").write_text(json.dumps(
        {"consecutive_green": 1, "consecutive_red": 0, "last_result": "green",
         "last_run_ts": now - 30 * 24 * 3600}))
    (live / ".operational_layer_signal.json").write_text(json.dumps(
        {"consecutive_green": 0, "consecutive_red": sup.OPERATIONAL_RED_DRAWABLE_THRESHOLD + 2,
         "last_result": "red", "last_run_ts": now - 600, "blocked_by": []}))

    monkeypatch.setattr(sup, "OPERATIONAL_LAYER_SIGNAL_FILE",
                        stale / ".operational_layer_signal.json")
    monkeypatch.setattr(sup, "shared_tree_live_record", resolver)

    drawn = sup._operational_red_persistent_draw(now=now)

    assert drawn is not None, (
        "the operational-layer red rung read a committed green: the layer is UNMONITORED and the "
        "stated fail-safe direction is TOWARD drawing, and reading the wrong tree inverted it")


def test_the_stuck_tracker_sees_the_live_episode_key_not_the_pre_rename_schema(
        stale_and_live, monkeypatch):
    """Not a stale VALUE -- a stale SCHEMA. git's copy predates the `key` -> `episode_key`
    rename, so the current episode can never match it, `first_seen_at` resets every cycle, and
    the stuck episode this tracker exists to escalate never gets old enough to escalate.

    READ-ONLY BY DESIGN: `_save_stuck_state` still writes the caller's own tree, because the only
    writer is the supervisor daemon and the daemon runs on the shared tree."""
    import background.supervisor as sup
    stale, live, resolver = stale_and_live

    (stale / ".supervisor_stuck_state.json").write_text(json.dumps(
        {"escalated": False, "first_seen_at": 1784223884.0, "key": "a pre-rename episode"}))
    (live / ".supervisor_stuck_state.json").write_text(json.dumps(
        {"escalated": False, "first_seen_at": 1789000000.0, "episode_key": "the live episode"}))

    monkeypatch.setattr(sup, "STUCK_STATE_FILE", stale / ".supervisor_stuck_state.json")
    monkeypatch.setattr(sup, "shared_tree_live_record", resolver)

    state, _verdict = sup._load_stuck_state_classified()

    assert state.get("episode_key") == "the live episode", (
        "the stuck-episode tracker read a record written before the field was renamed, so no "
        "episode can ever match it and none can ever escalate")


def test_the_model_tier_report_sees_the_live_gate_failures_not_an_empty_list(
        stale_and_live, monkeypatch):
    """`except Exception: return []` already collapses unreadable into none, which is exactly why
    the stale read was invisible here: the honest "cannot tell" and the flattering "nothing
    failed" print as the same clean tier."""
    import tools.model_tier_report as mtr
    stale, live, resolver = stale_and_live

    (stale / ".publish_gate_state.json").write_text(json.dumps({"failures": []}))
    (live / ".publish_gate_state.json").write_text(json.dumps(
        {"failures": [{"ts": 1789093371.0, "kind": "test_regression", "rc": 1}]}))

    monkeypatch.setattr(mtr, "PUBLISH_GATE_STATE", stale / ".publish_gate_state.json")
    monkeypatch.setattr(mtr, "shared_tree_live_record", resolver)

    assert mtr._gate_failures(), (
        "the model-tier report read git's placeholder and reported every tier's gate as never "
        "having failed")


def test_the_console_capture_lapse_check_sees_the_live_keystroke_not_a_fortnight_ago(
        tmp_path, monkeypatch):
    """THE FLATTERING DIRECTION IS ARITHMETIC, not a missing field. `lag_h` is
    `last_human - captured_end`: an OLDER `last_human` makes the lag SMALLER, so a stale stamp
    pushes this control toward SILENCE. A control whose whole subject is one signal going stale
    was itself reading a stale signal, in the one direction that cannot fire."""
    import time

    import tools.console_instruction_record as cir

    now = time.time()
    captured_day = time.strftime("%Y-%m-%d", time.localtime(now - 20 * 24 * 3600))
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / f"DIRECTOR_CONSOLE_{captured_day}.md").write_text(f"# console {captured_day}\n")

    # THE STALE STAMP IS PLACED RELATIVE TO THE CAPTURE'S OWN END INSTANT, the way the function
    # measures it -- not "19 days ago", which was the first draft and left the leg unable to
    # fail: 19-days-ago is still ~24h after a 20-day-old capture, over the 12h bar, so the
    # reverted reader reported the lapse anyway and the mutation passed. A fixture that agrees
    # with the fixed and the broken code alike grades nothing.
    captured_end = time.mktime(time.strptime(captured_day + " 23:59", "%Y-%m-%d %H:%M"))
    stale_stamp = tmp_path / "stale_stamp"
    live_stamp = tmp_path / ".human_last_input"
    stale_stamp.write_text(str(int(captured_end + 6 * 3600)))   # 6h after the capture: no lapse
    live_stamp.write_text(str(int(now)))                        # ~20 days after it: a lapse

    monkeypatch.setattr(cir, "HUMAN_PRESENCE_STAMP", stale_stamp)
    monkeypatch.setattr(cir, "shared_tree_live_record", lambda _p: live_stamp)

    rc, message = cir.check(staging=staging, now=now)

    assert rc == 1 and "LAPSED" in message, (
        "the console-capture lapse check read git's checkout of .human_last_input, whose older "
        f"timestamp shrinks the measured lag below CAPTURE_LAG_FINDING_HOURS -- got rc={rc}: "
        f"{message}")
