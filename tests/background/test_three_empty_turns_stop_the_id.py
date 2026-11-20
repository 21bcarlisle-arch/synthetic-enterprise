"""Three empty turns in a row stop an id from being offered, and the stop is filed once.

The director's 20 Nov steer: "a failing check after three rounds brings in a human". The live
executor re-offered an empty item with no limit: one id took 43 turns on the night of 11-12 Oct.
`docs/market_research/three_empty_turns_then_stop_2026-11-20.md` is the K8 page.

Each test names the mutation it dies to.
"""
from __future__ import annotations

import subprocess

import pytest

from background import alarm_repetition, delivery_lane, seat_executor

T0 = 1_763_600_000.0  # 2025-11-20 00:53 UTC, a whole-minute-safe anchor


def _line(kind: str, wid: str, minute: int) -> str:
    import time as _t

    stamp = _t.strftime("%Y-%m-%d %H:%M", _t.gmtime(T0 + 60 * minute))
    if kind == "N":
        return (f"- [{stamp} UTC] LANDED NOTHING: {wid}, bound paths unchanged since abc "
                f"(rc=0) -- why{minute}")
    if kind == "F":
        return f"- [{stamp} UTC] FINISHED {wid}: rc=0 -- moved"
    return f"- [{stamp} UTC] RUNNING {wid} in /wt on abc -- model m"


def _runs(tmp_path, lines):
    log = tmp_path / "log.md"
    log.write_text("\n".join(lines) + "\n")
    return seat_executor.empty_streaks(path=log)


def test_the_whole_partition_offer_stop_reset_release(tmp_path):
    """One control over the partition, so a stop that refuses everything cannot pass.

    MUTATIONS: `< EMPTY_TURNS_BEFORE_STOP` -> `<= ...` (third no longer stops: leg 2); drop the
    `runs.pop` on FINISHED (the reset leg); drop either release comparison (legs 4 and 5); return a
    reason unconditionally (leg 1).
    """
    item = {"id": "x", "written_at": 0.0}
    two = _runs(tmp_path, [_line("N", "x", 0), _line("R", "x", 1), _line("N", "x", 2)])
    three = _runs(tmp_path, [_line("N", "x", m) for m in (0, 2, 4)])
    reset = _runs(tmp_path, [_line("N", "x", 0), _line("N", "x", 2), _line("F", "x", 3),
                             _line("N", "x", 4)])
    plan = {
        "offer_after_two": seat_executor.stopped_after_empty_turns(item, two) is None,
        "stop_after_three": seat_executor.stopped_after_empty_turns(item, three) is not None,
        "finished_resets": seat_executor.stopped_after_empty_turns(item, reset) is None,
        "rewrite_releases": seat_executor.stopped_after_empty_turns(
            {"id": "x", "written_at": T0 + 60 * 6}, three) is None,
        "landing_releases": seat_executor.stopped_after_empty_turns(
            item, three, landed_at=T0 + 60 * 6) is None,
        # A rewrite inside the last empty minute cannot be ordered against it: the stop holds.
        "same_minute_holds": seat_executor.stopped_after_empty_turns(
            {"id": "x", "written_at": T0 + 60 * 4 + 30}, three) is not None,
    }
    assert all(plan.values()), plan
    assert len(reset["x"]) == 1 and "why4" in reset["x"][0][1]


def test_the_draw_skips_a_stopped_id_and_takes_the_next(tmp_path, monkeypatch):
    """The stop is a skip, not a stall: the walk goes on to the next focus item.

    MUTATION: remove `and not _emptied(item)` from the focus loop and `stopped` is drawn.
    """
    log = tmp_path / "log.md"
    log.write_text("\n".join(_line("N", "stopped", m) for m in (0, 2, 4)) + "\n")
    runs = seat_executor.empty_streaks(path=log)
    monkeypatch.setattr(delivery_lane, "_empty_turn_runs", lambda path: runs)
    monkeypatch.setattr(delivery_lane.seat_continuation, "live", lambda now=None: [])
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus",
                        lambda atoms: [{"id": "stopped", "what": "a"}, {"id": "next", "what": "b"}])
    for name in ("_atom_ids", "_retired_ids", "_stretch_refusals", "_area_stops"):
        # Empty: nothing retired, stretched or stopped.
        monkeypatch.setattr(delivery_lane, name, lambda *a, **k: {})
    monkeypatch.setattr(delivery_lane, "_result_landed", lambda item: False)
    monkeypatch.setattr(delivery_lane, "finished_on_origin", lambda item, path=None: None)
    monkeypatch.setattr(delivery_lane, "_live_holders", lambda: [])
    monkeypatch.setattr(delivery_lane, "held_grade", lambda *a, **k: (None, []))
    monkeypatch.setattr(delivery_lane, "_ledger_vocabulary", lambda store: ({}, 0))
    monkeypatch.setattr(delivery_lane, "_self_issued_chain", lambda store: 0)
    monkeypatch.setattr(delivery_lane, "_focus_waited_through", lambda store: 0)

    item = delivery_lane.next_item(path=tmp_path / "claims.json")
    assert item is not None and item["id"] == "next", item
    assert [i["id"] for i, _ in delivery_lane.LAST_EMPTY_TURN_SKIPS] == ["stopped"]
    assert "EMPTY-TURN STOP" in delivery_lane.empty_turn_note(delivery_lane.LAST_EMPTY_TURN_SKIPS)


def test_an_explicit_store_never_reads_the_live_log(monkeypatch):
    """A test's isolated store must not see the real executor's runs; the production call must.

    Both legs, so a guard that returns {} always cannot pass. MUTATION: drop the `path is not None`
    return (leg 1 fires); return {} unconditionally (leg 2 fires).
    """
    live = {"x": [(T0, "LANDED NOTHING: x")]}
    monkeypatch.setattr(seat_executor, "empty_streaks", lambda path=None: live)
    assert delivery_lane._empty_turn_runs(path=object()) == {}
    assert delivery_lane._empty_turn_runs(path=None) == live


@pytest.fixture()
def turn(tmp_path, monkeypatch):
    """A run_once that reaches the verdict without the shared tree, the network or a session."""
    monkeypatch.setattr(seat_executor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(seat_executor, "_shared_tree_log", lambda: tmp_path / "log.md")
    monkeypatch.setattr(seat_executor, "PID_FILE", tmp_path / "executor.pid")
    monkeypatch.setattr(seat_executor, "WORKTREE", tmp_path / "wt")
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: False)
    monkeypatch.setattr(seat_executor, "_another_executor_is_running", lambda: False)
    monkeypatch.setattr(seat_executor, "_is_handed_off", lambda item, now=None: True)
    monkeypatch.setattr(seat_executor, "_resolve_claude", lambda: "claude")
    monkeypatch.setattr(seat_executor, "ensure_worktree", lambda base: tmp_path / "wt")
    monkeypatch.setattr(seat_executor, "guard_live_ledger_write", lambda path, writer="": path)
    monkeypatch.setattr(seat_executor.delivery_lane, "CLAIMS_FILE", tmp_path / "claims.json")
    monkeypatch.setattr(seat_executor.seat_work_in_hand, "CLAIMS_FILE", tmp_path / "wih.json")
    monkeypatch.setattr(seat_executor.delivery_lane, "next_item",
                        lambda **k: {"id": "the-item", "what": "w", "why": "y"})
    monkeypatch.setattr(seat_executor, "bound_landing", lambda wid: (0.0, []))
    monkeypatch.setattr(alarm_repetition, "STAGING_DIR", tmp_path / "staging")
    (tmp_path / "wt").mkdir()

    def fake_run(cmd, **kwargs):
        if cmd[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="basesha0000\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
    monkeypatch.setattr(seat_executor.subprocess, "run", fake_run)
    return tmp_path


def test_the_third_empty_turn_files_once_and_names_its_reasons(turn, monkeypatch):
    """The filing fires on the third empty turn, not the second, and not again on the fourth.

    MUTATIONS: delete the `file_empty_turns` call in `run_once` (nothing is filed); `==` -> `>=`
    (the fourth turn logs a second STOPPED line).
    """
    filed = []
    real = seat_executor.file_empty_turns
    monkeypatch.setattr(seat_executor, "file_empty_turns",
                        lambda wid, run, **k: filed.append((wid, len(run))) or real(wid, run, **k))
    for _ in range(2):
        seat_executor.run_once()
    assert filed == [], "filed before the third empty turn"
    seat_executor.run_once()
    assert filed == [("the-item", 3)]
    seat_executor.run_once()
    assert filed == [("the-item", 3)], "filed again on the fourth turn"

    log = (turn / "log.md").read_text()
    assert log.count("STOPPED the-item") == 1
    docs = list((turn / "staging").glob("WORKER_FINDING_REPEATING_ALARM_THREE_EMPTY_TURNS_*.md"))
    assert len(docs) == 1, docs
    text = docs[0].read_text()
    assert "the-item" in text and text.count("LANDED NOTHING: the-item") >= 3
