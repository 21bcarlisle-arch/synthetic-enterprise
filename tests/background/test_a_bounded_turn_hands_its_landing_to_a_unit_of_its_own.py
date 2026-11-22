"""A landing a bounded executor turn starts runs in a unit of its own, so teardown cannot kill it.

Evidence: on 22 Nov `surgical_land` was SIGKILLed with the seat-executor cgroup at teardown four
times (pids 2309122, 3176409, 945604, 2268653), each logged DOOMED-AT-TEARDOWN a moment before the
kill. See `background/bounded_landing.py`.
"""
from __future__ import annotations

import io
import subprocess

import pytest

from background import bounded_landing as bl
from background import seat_executor
from tools import surgical_land

TURN = {bl.TURN_ENV: "1", bl.DEADLINE_ENV: "10000", bl.WORK_ID_ENV: "some-claim"}


def _route(env, *, launch_ok=True, now=0.0):
    calls = {"launch": [], "follow": [], "salvage": []}

    def launch(argv, cwd, env_):
        calls["launch"].append(argv)
        if not launch_ok:
            raise RuntimeError("systemd-run refused")
        return "longjob-land-x", "/tmp/x.log"

    def follow(unit, log, left, *, out):
        calls["follow"].append((unit, left))
        return 0

    def salvage(cwd, *, now=None):
        calls["salvage"].append(cwd)
        return "refs/salvage/bounded-landing/x"

    out = io.StringIO()
    rc = bl.hand_off(["-m", "msg", "a.py"], cwd="/tmp", env=env, launch=launch, follow=follow,
                     salvage=salvage, now=now, out=out)
    return rc, calls, out.getvalue()


def test_every_branch_of_the_hand_off_can_be_taken():
    """One control over the partition: outside a turn nothing changes; inside one the landing is
    handed off and followed; a failed hand-off lands in place with time to spare and is REFUSED,
    with its diff salvaged, inside the landing window; and inside the unit it never hands off twice.

    MUTATION (must fire): make `in_bounded_turn` return False (row 2 lands in place), or drop the
    window comparison (row 3 or row 4 takes the other leg)."""
    outside = _route({})
    handed = _route(TURN)
    early = _route(TURN, launch_ok=False, now=0.0)                       # 10000 s left
    late = _route(TURN, launch_ok=False, now=10000 - bl.LANDING_WINDOW_SECONDS + 1)
    in_unit = _route(dict(TURN, **{bl.IN_UNIT_ENV: "longjob-land-x"}))

    assert outside[0] is None and not outside[1]["launch"]
    assert handed[0] == 0 and handed[1]["follow"] == [("longjob-land-x", 10000.0)]
    assert "HANDED OFF" in handed[2]
    assert early[0] is None and not early[1]["salvage"] and "landing in place" in early[2]
    assert late[0] == 3 and late[1]["salvage"] == ["/tmp"]
    assert "REFUSED" in late[2] and "systemd-run refused" in late[2]
    assert "refs/salvage/bounded-landing/x" in late[2]
    assert in_unit[0] is None and not in_unit[1]["launch"]


def test_surgical_land_hands_off_before_it_gates_anything(monkeypatch):
    """The wire itself: `surgical_land.main`, inside a turn, returns the hand-off's status and never
    reaches its own landing.

    MUTATION (must fire): delete the `bounded_landing.hand_off` call in `surgical_land.main`."""
    seen = []

    def fake_hand_off(argv, **kw):
        seen.append(argv)
        return 0

    monkeypatch.setattr(bl, "hand_off", fake_hand_off)
    monkeypatch.setattr(surgical_land, "land",
                        lambda *a, **k: pytest.fail("landed in the turn's own cgroup"))
    assert surgical_land.main(["-m", "a message", "some/path.py"]) == 0
    assert seen == [["-m", "a message", "some/path.py"]]


def test_the_turn_environment_names_the_turn_its_deadline_and_its_claim():
    """MUTATION (must fire): drop any of the three keys from `turn_env`."""
    env = seat_executor.turn_env("the-claim", 1000.0, base={})
    assert env[bl.TURN_ENV] == "1"
    assert float(env[bl.DEADLINE_ENV]) == 1000.0 + seat_executor.SESSION_TIMEOUT_SECONDS
    assert env[bl.WORK_ID_ENV] == "the-claim"
    assert bl.in_bounded_turn(env) and bl.seconds_left(env, now=1000.0) > bl.LANDING_WINDOW_SECONDS


def test_teardown_waits_for_a_landing_in_its_cgroup_and_never_for_scratch():
    """Never warn DOOMED and then return into the kill over a landing. Both legs: a landing is
    waited for until it leaves; a stray probe is not waited for at all; the unit's bound ends the
    wait and says so.

    MUTATION (must fire): drop the `surgical_land` match (row 1 returns at once), or drop the
    bound (row 3 never ends)."""
    landing = {"pid": 7, "cmdline": "python3 -m tools.surgical_land -m x a.py"}
    probe = {"pid": 8, "cmdline": "python3 /tmp/probe.py"}
    clock = [0.0]

    def sleep(s):
        clock[0] += s

    samples = iter([[landing, probe], [landing, probe], [probe]])
    left = seat_executor.wait_for_landings_in_cgroup(
        0.0, doomed=lambda: next(samples), sleep=sleep, clock=lambda: clock[0])
    assert left == [] and clock[0] == 30.0

    clock[0] = 0.0
    assert seat_executor.wait_for_landings_in_cgroup(
        0.0, doomed=lambda: [probe], sleep=sleep, clock=lambda: clock[0]) == []
    assert clock[0] == 0.0

    lines = []
    stuck = seat_executor.wait_for_landings_in_cgroup(
        0.0, doomed=lambda: [landing], sleep=sleep, clock=lambda: clock[0], log=lines.append)
    assert stuck == [landing] and "EXHAUSTED" in lines[-1]
    assert clock[0] <= seat_executor.UNIT_TIMEOUT_SECONDS


def test_a_refused_landing_leaves_its_diff_on_a_salvage_ref(tmp_path):
    """The refusal's promise is that the work outlives it. A real repo: a tracked edit and an
    untracked file come back from the ref, and the worktree's own index is untouched."""
    tmp_path = tmp_path / "repo"
    tmp_path.mkdir()

    def git(*a):
        return subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "a.txt").write_text("one\n")
    git("add", "a.txt")
    git("commit", "-qm", "base")
    (tmp_path / "a.txt").write_text("two\n")
    (tmp_path / "new.txt").write_text("fresh\n")

    ref = bl.save_salvage_ref(str(tmp_path), now=0.0)
    assert ref and ref.startswith(bl.SALVAGE_REF_PREFIX)
    patch = git("cat-file", "-p", ref).stdout.decode()
    assert "+two" in patch and "+fresh" in patch
    assert git("status", "--porcelain").stdout.decode().splitlines() == [" M a.txt", "?? new.txt"]


def test_a_stand_down_names_why_each_focus_item_was_not_drawn(tmp_path):
    """Defect (22 Nov, 13:25Z-15:26Z): "no unclaimed focus item" every tick, and the words were the
    same whether the record was unreadable or an item was claimed. Both legs: a record the reader
    refuses says NO DIRECTION with the reason; a claimed item names its store and holder's note.

    MUTATION (must fire): drop the `direction is None` leg (row 1 names nothing), or the claim
    lookup (row 2 reads as an unrecorded skip)."""
    import json
    import time
    from datetime import datetime, timezone

    import yaml

    from background import delivery_lane

    record = {"version": 1, "oriented_at": datetime.now(timezone.utc).isoformat(),
              "thesis_read": "reading", "not_now": [{"what": "x", "why": "y"}], "wrong": [],
              "for_the_director": [],
              "focus": [{"id": "not-an-atom-one", "why": "because", "side": "supplier"},
                        {"id": "not-an-atom-two", "why": "because", "side": "supplier"}]}
    store = tmp_path / ".claims.json"
    now = time.time()
    store.write_text(json.dumps({"not-an-atom-two": {"claimed_at": now - 600,
                                                     "note": "the gas lane",
                                                     "paths": []}}))
    for lst in (delivery_lane.LAST_FINISHED_SKIPS, delivery_lane.LAST_STRETCH_SKIPS,
                delivery_lane.LAST_AREA_STOP_SKIPS, delivery_lane.LAST_EMPTY_TURN_SKIPS,
                delivery_lane.LAST_HELD_SKIPS):
        lst.clear()

    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(dict(record, focus=[
        {"id": "x", "why": "see the item above", "side": "supplier"}])))
    note = delivery_lane.why_no_focus_item(direction_path=bad, stores=[(store, 6000.0)])
    assert "NO DIRECTION" in note and "TWO homes" in note

    good = tmp_path / "good.yaml"
    good.write_text(yaml.safe_dump(record))
    note = delivery_lane.why_no_focus_item(now=now, direction_path=good,
                                           stores=[(store, 6000.0)])
    assert "not-an-atom-two: CLAIMED in .claims.json 10 min ago by 'the gas lane'" in note
    assert "not-an-atom-one: skipped by" in note
