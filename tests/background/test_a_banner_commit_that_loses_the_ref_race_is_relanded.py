"""A BANNER COMMIT THAT LOSES THE REF RACE IS RE-LANDED ON THE NEW HEAD, NOT FILED AS A REFUSAL.

08:46Z on 2 Nov: the paused banner's hook chain ran for minutes and passed, then git's own ref
update said `fatal: cannot lock ref 'HEAD': is at 491243e09... but expected a9e9128aa...` because
another lane committed meanwhile. `_commit_and_push_paths` filed that as the chain refusing, and
the publisher's classifier called it UNNAMEABLE. A chain that passed on a tree which no longer
exists has returned no verdict at all, so the move is to re-gate on the new HEAD through
`surgical_land.land`, the same clean-extract route the content publish takes.

The partition, before any leg: a lost ref race takes the re-land, and a real gate refusal does
not. A guard that re-landed EVERYTHING would turn a red gate into a retried one, and that is how
a flaky test becomes a landed regression.
"""
from __future__ import annotations

import pytest

from background import process_run_complete as prc
from background import publish_cause as pc
from tests.background.test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line import (
    _drive,
    _record,
)
from tools import surgical_land

#: git's real text, byte for byte from sim-runner-log.md at 08:46Z 2 Nov.
LOST_REF = ("fatal: cannot lock ref 'HEAD': is at 491243e09628a6186ce85942fe7be0a8ad288c90 "
            "but expected a9e9128aa01d20e45e20544825c3126cfd6c6310")


@pytest.fixture
def state_file(tmp_path, monkeypatch):
    """The tracked gate-state file and the log go to `tmp_path` before anything runs."""
    path = tmp_path / ".publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", path)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    return path


@pytest.fixture
def landings(monkeypatch):
    """Records each `land` call; `outcome` sets what the next one does."""
    calls = []
    outcome = {"sha": "relanded1", "raise": None, "lose": 0}

    def fake_land(root, paths, message, attempts=1, on_lost=None, **kwargs):
        calls.append({"root": root, "paths": list(paths), "attempts": attempts})
        for attempt in range(1, outcome["lose"] + 1):
            if on_lost is not None:
                on_lost(attempt, surgical_land.BaseMoved("moved", "a" * 40, "b" * 40))
        if outcome["raise"] is not None:
            raise outcome["raise"]
        return outcome["sha"]

    monkeypatch.setattr(surgical_land, "land", fake_land)
    return calls, outcome


def test_a_lost_ref_race_is_relanded_and_a_gate_refusal_is_not(state_file, tmp_path, monkeypatch,
                                                              landings):
    """THE PARTITION. Mutation: drop the `_lost_the_ref_race` branch and the first leg makes no
    `land` call and returns False; make the predicate always true and the second leg calls it."""
    calls, _ = landings
    assert _drive(monkeypatch, tmp_path, commit_rc=128, commit_tail=LOST_REF,
                  local_head="relanded1", remote_head="relanded1") is True, \
        "a banner whose chain passed and whose ref moved must publish after the re-land"
    assert len(calls) == 1, "the moved HEAD must be re-landed exactly once, got {}".format(calls)
    assert calls[0]["paths"] == ["site/data/tick_heartbeat.json"], \
        "the re-land must name the same paths, repo-relative as the extract needs them"
    assert _record(state_file) is None, "a race that was re-landed and published is not a refusal"

    calls.clear()
    assert _drive(monkeypatch, tmp_path, commit_rc=1, commit_tail="a gate said no") is False
    assert calls == [], "a gate's NO must never be retried as if it were a race"
    assert _record(state_file)["cause"] == pc.GATE_REFUSAL


def test_a_relanding_that_loses_every_race_names_the_race_not_a_gate(state_file, tmp_path,
                                                                    monkeypatch, landings):
    """Mutation: record GATE_REFUSAL on exhaustion and this reds -- no test was judged there."""
    _, outcome = landings
    outcome["lose"] = prc.PUBLISH_LAND_ATTEMPTS
    outcome["raise"] = surgical_land.LandingRefused("HEAD moved under the gate on all attempts")
    assert _drive(monkeypatch, tmp_path, commit_rc=128, commit_tail=LOST_REF) is False
    record = _record(state_file)
    assert record["cause"] == pc.LOST_COMMIT_RACE
    assert pc.LOST_COMMIT_RACE in pc.NO_TEST_JUDGED_CAUSES


def test_a_relanding_the_new_tree_refuses_is_a_gate_refusal(state_file, tmp_path, monkeypatch,
                                                           landings):
    """The other side: the re-land WON the race and the gate said NO on the new tree. That is a
    verdict about a real tree, so it is GATE_REFUSAL, and calling it a race would hide a red."""
    _, outcome = landings
    outcome["raise"] = surgical_land.LandingRefused("pre-commit hook refused: 1 failed")
    assert _drive(monkeypatch, tmp_path, commit_rc=128, commit_tail=LOST_REF) is False
    assert _record(state_file)["cause"] == pc.GATE_REFUSAL
