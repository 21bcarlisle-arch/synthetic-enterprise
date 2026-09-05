"""The register every daemon writes, and the counter that measures an idle machine.

FOURTH INCREMENT of the census loader sweep, ranked as the direction asks -- by what the carrier's
WRITER does. `agent_status.json` is the largest read-modify-write left: `update_agent_status` loads
the WHOLE roster, appends one entry and writes the whole file back, and `update_sim_metrics` does
the same one function away. It is also the only carrier in the sweep whose corruption reaches a
PUBLISHED surface -- `SITE_STATUS_FILE.write_text` is two lines below `STATUS_FILE.write_text`, in
the same call, under the same lock.

MEASURED BEFORE THE REPAIR (tables in the loaders' docstrings), against a live prior of two agents
one of which was eight days stale, in `error`, carrying an anomaly:

    json `null` / `[1, 2, 3]`          RAISED AttributeError, on every daemon's heartbeat path
    `{"agents": [1, 2]}`               RAISED TypeError at `a["name"]`, inside the flock
    empty / truncated / no-agents-key  no raise -- and the ENTIRE ROSTER destroyed, then published

19 of the 28 call sites across 11 modules have no enclosing try, and `supervisor.main()` calls it
as its FIRST act, outside the `while` and outside every try: an unreadable status file stopped the
escalation watchdog STARTING. `supervisor._load_idle_turn_count` is the same `json.loads(...).get`
shape; its raise escapes `run_cycle` but is caught by `main`'s loop, so the supervisor does not die
-- it logs a cycle error every two minutes forever and the tick never completes.

EVERY LEG ASSERTS THE TWO ANSWERS **DIFFER**, never that they match, and each carrier has a
REACHABILITY leg proving a live prior reaches a third answer. Without those, "differs" is satisfied
by a board that declares the roster lost on every single write.
"""
from __future__ import annotations

import json

import pytest

from background import agent_status, supervisor
from background.episode_prior import ABSENT, READABLE, UNREADABLE

#: The whole partition. `null` and `[1, 2, 3]` PARSE -- which is why an `except JSONDecodeError`
#: never saw them -- and `{"agents": [1, 2]}` is the roster that is only PARTLY right: it parses,
#: it is a mapping, it has the key, and its ENTRIES are what `a["name"]` subscripts.
UNREADABLE_RAW = pytest.mark.parametrize(
    "raw",
    [
        pytest.param("", id="empty-file"),
        pytest.param('{"agents": [', id="truncated"),
        pytest.param("null", id="json-null"),
        pytest.param("[1, 2, 3]", id="list-of-non-mappings"),
        pytest.param('{"agents": [1, 2]}', id="agents-not-mappings"),
        pytest.param('{"agents": [{"no_name": 1}]}', id="agent-without-a-name"),
    ],
)

#: One of these two is EIGHT DAYS STALE and in `error`. That is not decoration: the census row's
#: argument for `benign` is that a failing agent which stops writing makes the staleness number
#: WORSE rather than better -- an argument that holds only while its row still exists.
LIVE_BOARD = {
    "_schema_version": "1",
    "agents": [
        {"name": "supervisor", "status": "running", "last_heartbeat": "2026-09-05T00:00:00+00:00"},
        {"name": "sim-runner", "status": "error", "last_heartbeat": "2026-08-28T00:00:00+00:00",
         "anomaly": "producer starved"},
    ],
}


@pytest.fixture
def board(tmp_path, monkeypatch):
    """Both files redirected. The mirror is not optional in these legs -- a repair that keeps the
    roster on disk and still publishes the wipe has fixed nothing a reader can see."""
    status = tmp_path / "agent_status.json"
    monkeypatch.setattr(agent_status, "STATUS_FILE", status)
    monkeypatch.setattr(agent_status, "SITE_STATUS_FILE", tmp_path / "site_agent_status.json")
    return status


@pytest.fixture
def idle_counter(tmp_path, monkeypatch):
    path = tmp_path / ".supervisor_idle_turn_count.json"
    monkeypatch.setattr(supervisor, "IDLE_TURN_COUNTER_FILE", path)
    return path


def _names(path):
    return [a["name"] for a in json.loads(path.read_text(encoding="utf-8")).get("agents", [])]


# =====================================================================================
# agent_status.json -- the crash half
# =====================================================================================

@UNREADABLE_RAW
def test_no_partition_member_can_take_a_daemon_down_on_its_own_heartbeat(raw, board):
    """MUTANT: restore `json.loads(...)` under `except (JSONDecodeError, OSError)` and three of
    these six raise -- from inside the flock, on the call `supervisor.main()` makes as its first
    act with no try above it. A daemon that cannot say it is alive does not start."""
    board.write_text(raw, encoding="utf-8")

    agent_status.update_agent_status("dispatcher", status="idle", last_action="tick")

    assert _names(board) == ["dispatcher"]


@UNREADABLE_RAW
def test_the_other_write_site_survives_it_too(raw, board):
    """THE SECOND WRITE SITE, and this module's own comment is why it has its own leg: a previous
    repair here guarded `update_agent_status` and not `update_sim_metrics`, and 32 refusals
    survived it unchanged.

    ASSERTS THE DESTRUCTIVE HALF, not just the crash half, and the first draft of this leg did the
    latter only: it checked `phase == 9`, which is satisfied by any body that does not raise -- and
    the crash was already fixed inside `_load`, so reverting THIS site's repair survived it. What
    is left to this site once the loader is sound is exactly the read-modify-write: preserve the
    bytes, and say on the file that the roster was rebuilt. MUTANT: revert this site's branch to a
    bare `data = _load()[0]`."""
    board.write_text(raw, encoding="utf-8")

    agent_status.update_sim_metrics(phase=9, tests_passing=26731)

    written = json.loads(board.read_text(encoding="utf-8"))
    assert written["phase"] == 9
    assert written[agent_status.ROSTER_LOST_FIELD]["rebuilt_by"] == "update_sim_metrics"
    assert board.with_name(board.name + ".unreadable").exists(), (
        "the second write site destroyed the roster without keeping a copy"
    )


# =====================================================================================
# agent_status.json -- the destructive half, and the published surface
# =====================================================================================

def test_a_board_that_forgot_the_roster_says_so_on_the_file(board):
    """THE ONE THING A READER CANNOT RECOVER FOR THEMSELVES. A board showing three agents because
    three exist and a board showing three because it forgot the rest are the same bytes otherwise.
    MUTANT: drop the ROSTER_LOST_FIELD stamp and a silent wipe is indistinguishable from a small
    system."""
    board.write_text('{"agents": [1, 2]}', encoding="utf-8")

    agent_status.update_agent_status("dispatcher", status="idle", last_action="tick")

    lost = json.loads(board.read_text(encoding="utf-8"))[agent_status.ROSTER_LOST_FIELD]
    assert lost["rebuilt_by"] == "dispatcher"
    assert lost["old_bytes"] != "could not be preserved"


def test_the_rebuild_does_not_destroy_the_roster_it_is_rebuilding_from(board):
    """THE DESTRUCTIVE HALF. The write is the WHOLE file, so on an unreadable prior the roster
    being replaced is the only copy there was. MUTANT: drop the `preserve_unreadable` call."""
    board.write_text('{"agents": [{"name": "sim-runner", "anomaly": "starved"}, 2]}',
                     encoding="utf-8")

    agent_status.update_agent_status("dispatcher", status="idle", last_action="tick")

    kept = board.with_name(board.name + ".unreadable")
    assert "sim-runner" in kept.read_text(encoding="utf-8")


def test_the_preserved_copy_does_not_move_the_file_the_lock_is_held_on(board):
    """`preserve_unreadable` MOVES by default, and this caller holds an `fcntl` lock on the open
    handle for that inode -- so a move would drop the rebuild at a path nothing was holding while
    every other daemon writes the same file.

    KEYED TO THE INODE, and the first draft of this leg was a tautology that taught the lesson: it
    asserted `board.exists()` after the call, which is true either way because the rebuild writes
    the path back. Dropping `keep_original=True` survived it. The property that actually
    distinguishes a move from a copy is WHICH inode is at the path afterwards -- on a move the
    original inode is the one carried into the `.unreadable` copy and the path holds a new one,
    which is precisely the inode the flock is no longer on. MUTANT: drop `keep_original=True`."""
    board.write_text("null", encoding="utf-8")
    locked_inode = board.stat().st_ino

    agent_status.update_agent_status("dispatcher", status="idle", last_action="tick")

    assert board.exists(), "the locked path must survive its own preservation"
    assert board.stat().st_ino == locked_inode, (
        "the rebuild landed on a DIFFERENT inode from the one the flock was taken on -- "
        "the preserve moved the file out from under the lock"
    )
    kept = board.with_name(board.name + ".unreadable")
    assert kept.exists() and kept.stat().st_ino != locked_inode


def test_a_first_ever_board_does_not_claim_it_lost_a_roster(board):
    """FOUND BY MEASURING THE REPAIR, NOT BY REASONING ABOUT IT. `open(..., "a+")` CREATES the
    file, so `_load` sees a zero-length file on a first-ever run -- and an empty file is
    UNREADABLE, correctly, which made every fresh board announce a loss it never had and write a
    `.unreadable` copy of nothing. The loader's ABSENT branch was right and simply unreachable
    from its only caller. MUTANT: drop the `existed_before_lock` capture."""
    assert not board.exists()

    agent_status.update_agent_status("dispatcher", status="idle", last_action="tick")

    written = json.loads(board.read_text(encoding="utf-8"))
    assert agent_status.ROSTER_LOST_FIELD not in written
    assert not board.with_name(board.name + ".unreadable").exists()


def test_a_readable_board_keeps_every_agent_and_publishes_the_same_bytes(board):
    """REACHABILITY NULL CONTROL, and it carries the mirror. Without it every leg above is
    satisfied by a board that declares the roster lost on every write and rebuilds from nothing --
    which would look busy, alarm constantly, and be wrong every time. The stale `sim-runner` row is
    the point: after a wipe a failing agent is not STALE on the board, it is ABSENT from it, and
    absent reads as 'not part of this system'."""
    board.write_text(json.dumps(LIVE_BOARD), encoding="utf-8")

    agent_status.update_agent_status("dispatcher", status="idle", last_action="tick")

    assert _names(board) == ["supervisor", "sim-runner", "dispatcher"]
    mirror = json.loads(agent_status.SITE_STATUS_FILE.read_text(encoding="utf-8"))
    assert [a["name"] for a in mirror["agents"]] == _names(board), (
        "the published mirror must carry what the register carries, wipe or no wipe"
    )
    assert agent_status.ROSTER_LOST_FIELD not in json.loads(board.read_text(encoding="utf-8"))


def test_a_board_with_no_agents_key_is_readable_and_not_a_loss(board):
    """A mapping that parses and simply has no roster is READABLE with nothing in it -- a fact,
    unlike an empty FILE. MUTANT: treat a missing `agents` key as unreadable and every board that
    has only ever held sim metrics announces a loss."""
    board.write_text('{"phase": 9}', encoding="utf-8")

    agent_status.update_agent_status("dispatcher", status="idle", last_action="tick")

    written = json.loads(board.read_text(encoding="utf-8"))
    assert agent_status.ROSTER_LOST_FIELD not in written
    assert written["phase"] == 9, "the readable content must survive"


def test_absent_and_unreadable_are_different_answers_at_the_loader(board):
    """The two take the same ACTION -- a fresh roster -- and are DIFFERENT ANSWERS, which is what
    lets the caller preserve and stamp on one and stay quiet on the other. MUTANT: return the same
    verdict for both."""
    assert not board.exists()
    assert agent_status._load()[1] == ABSENT

    board.write_text("null", encoding="utf-8")
    assert agent_status._load()[1] == UNREADABLE

    board.write_text(json.dumps(LIVE_BOARD), encoding="utf-8")
    assert agent_status._load()[1] == READABLE


# =====================================================================================
# .supervisor_idle_turn_count.json -- the counter on the branch that reports an idle machine
# =====================================================================================

@UNREADABLE_RAW
def test_no_partition_member_can_wedge_the_supervisors_cycle(raw, idle_counter):
    """`_record_idle_turn` is called on the `map_exhausted` branch of `run_cycle`, which no try
    covers; `main`'s loop catches it, so the supervisor stays UP and logs a cycle error every two
    minutes without ever completing a tick. The raise lands on exactly the branch that exists to
    make an idle machine visible. MUTANT: restore `json.loads(...).get("count", 0)` under
    `except (JSONDecodeError, OSError)` and `null` and the list raise AttributeError."""
    idle_counter.write_text(raw, encoding="utf-8")

    assert supervisor._load_idle_turn_count() == 0


def test_a_live_idle_count_is_carried_forward(idle_counter):
    """REACHABILITY NULL CONTROL: a loader that answered 0 to everything would reset an all-time
    counter on every read and never once be noticed, because nothing reads it for severity."""
    idle_counter.write_text(json.dumps({"count": 417}), encoding="utf-8")

    assert supervisor._load_idle_turn_count() == 417


def test_a_boolean_count_is_not_a_count(idle_counter):
    """`isinstance(True, int)` is True, so a bare numeric check accepts `{"count": true}` and the
    next increment makes the all-time total 2 -- wrong rather than absent, which is worse.
    MUTANT: drop the bool exclusion."""
    idle_counter.write_text('{"count": true}', encoding="utf-8")

    assert supervisor._load_idle_turn_count() == 0


def test_the_counter_increments_from_a_live_prior_rather_than_restarting(idle_counter):
    """The write half: `_record_idle_turn` is `_load() + 1` and a whole-file overwrite, so a prior
    it could not read is a counter silently restarted. MUTANT: have the loader answer 0 for a
    readable prior and this is the leg that catches it rather than the read-only one above."""
    idle_counter.write_text(json.dumps({"count": 417}), encoding="utf-8")

    assert supervisor._record_idle_turn() == 418
    assert json.loads(idle_counter.read_text(encoding="utf-8"))["count"] == 418
