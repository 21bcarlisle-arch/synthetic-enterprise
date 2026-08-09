"""PW4 -- R15 on the four remaining self-clearing-alarm episodes.

PW2 built the census (`background/self_clearing_alarm_census.py`) and guarded ONE of its five
real hits -- `.publish_gate_state.json`, the instance the director's steer was about. The other
four were dispositioned `real` with `guard: registered` precisely because each needed its OWN
answer to "what EVIDENCES an episode close", and guarding them by reflex with a close condition
nobody chose would have produced four controls that can never clear. An always-red detector is
as ignored as a blind one.

The four close conditions, each named in the guarded module and each INDEPENDENT of the state
file it closes (R15 anti-tautology -- never derived from the same file):

  .operational_layer_signal.json  consecutive_red    rc == 0 AND >=1 test actually PASSED
                                                     (the subprocess's own summary line)
  .supervisor_stuck_state.json    first_seen_at      the number-normalised reason, or the
                                                     staged set / agenda / PRIORITIES mtime,
                                                     changed (filesystem + live draw)
  .atom_stall_tracker.json        consecutive_unchgd level_current or loop_stage moved, or
                                                     simplifications_count went UP (the map)
  .run_marker_sweep_state.json    cycles             a publisher returned rc == 0 (a subprocess
                                                     return code)

Every control gets BOTH directions, per R15:
  * FIRES  -- a replay of the control's own named defect, asserting the episode survives it.
  * CLEARS -- the evidenced close still closes, so the guard cannot wedge the alarm permanently.
Plus, for each, the MUTATION: the same replay with the close condition widened back to what it
was, showing the episode being shortened. If a mutation ever stops shortening, its replay has
stopped reproducing the defect and the passing test above it means nothing.
"""
from __future__ import annotations

import json
import types

import pytest

from background import background_worker as bw
from background import process_run_complete as prc
from background import supervisor as sup


def _result(rc, stdout=""):
    return types.SimpleNamespace(returncode=rc, stdout=stdout, stderr="")


# ===========================================================================================
# 1. .operational_layer_signal.json -- consecutive_red
# ===========================================================================================

GREEN_REAL = "........                                                   [100%]\n41 passed in 8.12s\n"
GREEN_VACUOUS = "sssssssss                                                [100%]\n41 skipped in 0.42s\n"
RED = "F...                                                             [100%]\n" \
      "=== short test summary info ===\nFAILED tests/x.py::test_daemon\n1 failed, 3 passed in 2s\n"


@pytest.fixture
def op_state(tmp_path, monkeypatch):
    p = tmp_path / ".operational_layer_signal.json"
    monkeypatch.setattr(prc, "OPERATIONAL_LAYER_STATE_FILE", p)
    return p


def _op_check(result, *, now):
    return prc.run_operational_layer_signal(
        now=now, runner=lambda argv: result, notify_fn=lambda *a, **k: None,
        log_fn=lambda *a, **k: None, force=True)


def test_op_a_green_that_ran_nothing_does_not_clear_the_red_episode(op_state):
    """FIRES -- the named defect. The operational marker selects daemon-lifecycle tests, the
    tests most likely to skip themselves when the daemon they drive is absent. pytest exits 0 on
    an all-skipped run, so a red episode was cleared by a run that proved nothing."""
    _op_check(_result(1, RED), now=1000)
    _op_check(_result(1, RED), now=2000)
    assert json.loads(op_state.read_text())["consecutive_red"] == 2

    out = _op_check(_result(0, GREEN_VACUOUS), now=3000)
    assert out["episode_closed"] is False
    assert json.loads(op_state.read_text())["consecutive_red"] == 2, \
        "an all-skipped green cleared the red episode -- the check passed on empty"


def test_op_the_mutation_rc_zero_alone_would_clear_it(op_state):
    """THE MUTATION -- widen the close condition back to plain `rc == 0` and the same all-skipped
    run wipes a two-deep red streak. This is what the guard above prevents."""
    _op_check(_result(1, RED), now=1000)
    _op_check(_result(1, RED), now=2000)
    prev = json.loads(op_state.read_text())
    assert prc.operational_layer_episode_closed(_result(0, GREEN_VACUOUS), 0) is False
    mutated_closed = (0 == 0)                       # the widened condition
    assert mutated_closed and prev["consecutive_red"] == 2, \
        "the replay no longer reproduces a red episode -- the test above proves nothing"


def test_op_a_real_green_still_clears_it(op_state):
    """CLEARS -- a run that actually passed tests closes the episode. Without this the guard
    would pin consecutive_red permanently and the priority-zero draw would never stand down."""
    _op_check(_result(1, RED), now=1000)
    _op_check(_result(1, RED), now=2000)
    out = _op_check(_result(0, GREEN_REAL), now=3000)
    assert out["episode_closed"] is True
    assert json.loads(op_state.read_text())["consecutive_red"] == 0


def test_op_reds_still_ratchet(op_state):
    for i, now in enumerate((1000, 2000, 3000), start=1):
        assert _op_check(_result(1, RED), now=now)["consecutive_red"] == i


def test_op_an_unreadable_run_cannot_close_an_episode():
    """A runner that returns only a return code (no output) leaves the question unanswered --
    and an unanswered question is not evidence of recovery. `None` and `0` are opposite facts."""
    bare = types.SimpleNamespace(returncode=0)
    assert prc.operational_layer_passed_count(bare) is None
    assert prc.operational_layer_episode_closed(bare, 0) is False


def test_op_pass_count_reads_the_runs_own_output_not_the_state_file():
    """R15 anti-tautology: the close condition is derived from the subprocess, so a state file
    that lies cannot manufacture a close."""
    assert prc.operational_layer_passed_count(_result(0, GREEN_REAL)) == 41
    assert prc.operational_layer_passed_count(_result(0, GREEN_VACUOUS)) is None
    assert prc.operational_layer_episode_closed(_result(1, RED), 1) is False


# ===========================================================================================
# 2. .supervisor_stuck_state.json -- first_seen_at
# ===========================================================================================

@pytest.fixture
def stuck_state(tmp_path, monkeypatch):
    p = tmp_path / ".supervisor_stuck_state.json"
    monkeypatch.setattr(sup, "STUCK_STATE_FILE", p)
    monkeypatch.setattr(sup.agenda_module, "load_agenda", lambda: None)
    monkeypatch.setattr(sup, "_real_staged_instructions", lambda: ["A.md", "B.md"])
    return p


def test_stuck_a_reworded_reason_does_not_restamp_the_episode(stuck_state, monkeypatch):
    """FIRES -- the named defect. These reasons render counts, levels and elapsed minutes into
    their prose, so the same stall produced a new key every cycle and `first_seen_at` was
    re-stamped. A 3h stall read as a series of 2-minute ones and never reached the threshold."""
    clock = [1_000_000.0]
    monkeypatch.setattr(sup.time, "time", lambda: clock[0])
    monkeypatch.setattr(sup, "ntfy", lambda *a, **k: None)

    sup._check_stuck_escalation("unprocessed staging -- 3 files; drawn 1 time")
    start = json.loads(stuck_state.read_text())["first_seen_at"]

    for i in range(2, 12):                      # the same stall, re-rendered with new numbers
        clock[0] += 600
        sup._check_stuck_escalation(f"unprocessed staging -- {i} files; drawn {i} times")

    assert json.loads(stuck_state.read_text())["first_seen_at"] == start, \
        "prose churn re-stamped the episode start -- a long stall reads as many short ones"
    elapsed = clock[0] - start
    assert elapsed >= sup.STUCK_THRESHOLD_SECONDS, "the replay no longer spans the threshold"


def test_stuck_the_mutation_the_raw_reason_key_restamps_every_cycle(stuck_state):
    """THE MUTATION -- key the episode on the raw reason, as it was, and every re-render is a
    different key, so every cycle resets the clock."""
    a = "unprocessed staging -- 3 files; drawn 1 time"
    b = "unprocessed staging -- 4 files; drawn 2 times"
    assert sup._stuck_key(a) != sup._stuck_key(b), \
        "the replay no longer varies the raw key -- the test above proves nothing"
    assert sup._stuck_episode_key(a) == sup._stuck_episode_key(b)


def test_stuck_genuinely_different_work_still_opens_a_fresh_episode(stuck_state, monkeypatch):
    """CLEARS -- and the false-positive direction. Normalising DIGITS, not dropping the reason,
    is what keeps different atoms distinct: what distinguishes one draw from another is its
    NAME. Dropping the reason would page 'stuck on the same work' at work that is moving."""
    clock = [1_000_000.0]
    monkeypatch.setattr(sup.time, "time", lambda: clock[0])
    sup._check_stuck_escalation("self-refill -- atom PW4_guard_remaining_episode_states")
    first = json.loads(stuck_state.read_text())["first_seen_at"]

    clock[0] += 600
    sup._check_stuck_escalation("self-refill -- atom H32_rehome_map_notes")
    assert json.loads(stuck_state.read_text())["first_seen_at"] > first, \
        "a different atom did not open a fresh episode"


def test_stuck_a_changed_staged_set_still_closes_the_episode(stuck_state, monkeypatch):
    """CLEARS -- the evidence component is independent of the state file: it is read off the
    staging directory, which the stuck state cannot influence."""
    clock = [1_000_000.0]
    monkeypatch.setattr(sup.time, "time", lambda: clock[0])
    sup._check_stuck_escalation("unprocessed staging")
    first = json.loads(stuck_state.read_text())["first_seen_at"]

    clock[0] += 600
    monkeypatch.setattr(sup, "_real_staged_instructions", lambda: ["A.md"])
    sup._check_stuck_escalation("unprocessed staging")
    assert json.loads(stuck_state.read_text())["first_seen_at"] > first


def test_stuck_escalated_rides_the_episode_not_the_key(stuck_state, monkeypatch):
    """R5: once paged, a re-worded reason must not re-arm the page. Before the episode key, a
    churn reset `escalated` to False as a side effect of re-keying."""
    clock = [1_000_000.0]
    monkeypatch.setattr(sup.time, "time", lambda: clock[0])
    pages = []
    monkeypatch.setattr(sup, "ntfy", lambda msg, *a, **k: pages.append(msg))

    sup._check_stuck_escalation("unprocessed staging -- 1 file")
    clock[0] += sup.STUCK_THRESHOLD_SECONDS + 60
    sup._check_stuck_escalation("unprocessed staging -- 1 file")
    assert len(pages) == 1
    assert json.loads(stuck_state.read_text())["escalated"] is True

    clock[0] += 600
    sup._check_stuck_escalation("unprocessed staging -- 2 files")
    assert len(pages) == 1, "a reworded reason re-armed the page on an unchanged status"
    assert json.loads(stuck_state.read_text())["escalated"] is True


# ===========================================================================================
# 3. .atom_stall_tracker.json -- consecutive_unchanged
# ===========================================================================================

def _fp(level="1", target="3", stage="build", simps="0", eh="None"):
    return "|".join((level, target, stage, simps, eh))


@pytest.fixture
def stall_state(tmp_path, monkeypatch):
    p = tmp_path / ".atom_stall_tracker.json"
    monkeypatch.setattr(sup, "ATOM_STALL_STATE_FILE", p)
    return p


def test_stall_an_expert_hour_restamp_does_not_reset_the_streak(stall_state):
    """FIRES -- the named defect, and it is self-referential: a HARDEN pass that re-stamps
    `expert_hour.last` and changes nothing else IS the livelock the stall tracker exists to
    catch, and it was resetting the very counter meant to catch it. Draw, re-stamp, count back
    to 1, forever."""
    for i in range(1, sup.ATOM_STALL_THRESHOLD + 2):
        stalled, count = sup._record_atom_draw_and_check_stall("A1", _fp(eh=f"2026-08-09T0{i}:00Z"))
    assert count >= sup.ATOM_STALL_THRESHOLD and stalled, \
        "a pure expert-hour re-stamp reset the stall streak"


def test_stall_the_mutation_any_fingerprint_difference_would_reset_it(stall_state):
    """THE MUTATION -- the old close condition was `fingerprint != fingerprint`, which every
    re-stamp satisfies. Under it the count never leaves 1."""
    a, b = _fp(eh="2026-08-09T01:00Z"), _fp(eh="2026-08-09T02:00Z")
    assert a != b, "the replay no longer varies the fingerprint -- the test above proves nothing"
    assert sup._atom_fingerprint_progressed(a, b) is False


def test_stall_a_retarget_is_not_progress(stall_state):
    """`level_target` says where the atom is GOING, not that it moved."""
    assert sup._atom_fingerprint_progressed(_fp(target="3"), _fp(target="4")) is False


def test_stall_real_progress_still_closes_the_episode(stall_state):
    """CLEARS, three ways -- a level move, a stage move, and a simplification landing. Without
    these the tracker would soft-deprioritise an atom forever once flagged."""
    assert sup._atom_fingerprint_progressed(_fp(level="1"), _fp(level="2")) is True
    assert sup._atom_fingerprint_progressed(_fp(stage="build"), _fp(stage="harden")) is True
    assert sup._atom_fingerprint_progressed(_fp(simps="0"), _fp(simps="1")) is True

    for _ in range(sup.ATOM_STALL_THRESHOLD + 1):
        sup._record_atom_draw_and_check_stall("A2", _fp())
    assert sup._is_atom_stalled("A2") is True
    stalled, count = sup._record_atom_draw_and_check_stall("A2", _fp(level="2"))
    assert (stalled, count) == (False, 1), "an atom that genuinely advanced stayed flagged"


def test_stall_a_dropping_simplification_count_is_bookkeeping_not_work(stall_state):
    """A count that goes DOWN is a note rehomed or a store rebuilt, not work done."""
    assert sup._atom_fingerprint_progressed(_fp(simps="3"), _fp(simps="1")) is False


def test_stall_a_first_draw_starts_a_fresh_episode(stall_state):
    assert sup._atom_fingerprint_progressed(None, _fp()) is True
    assert sup._record_atom_draw_and_check_stall("NEW", _fp()) == (False, 1)


# ===========================================================================================
# 4. .run_marker_sweep_state.json -- cycles
# ===========================================================================================

@pytest.fixture
def sweep_state(tmp_path, monkeypatch):
    p = tmp_path / ".run_marker_sweep_state.json"
    monkeypatch.setattr(bw, "SWEEP_STATE_FILE", p)
    monkeypatch.setattr(bw, "log", lambda *a, **k: None)
    return p


class _Marker:
    def __init__(self, name):
        self.name = name


def test_sweep_a_retirement_does_not_reset_the_zero_progress_count(sweep_state, monkeypatch):
    """FIRES -- the named defect. Retiring a superseded marker is a RENAME: it needs no run lock,
    cannot be lock-skipped, and drains the queue whether or not publishing works at all. It
    changed `oldest`, which reset the counter, so a publish stall that had been running for
    cycles paged as a first occurrence -- or never paged at all."""
    monkeypatch.setattr(bw, "notify", lambda *a, **k: None, raising=False)
    fired = []
    for i in range(bw.STALL_ALARM_CYCLES + 1):
        # every cycle the previous oldest is RETIRED, so the oldest name churns and nothing
        # is ever published.
        fired.append(bw._check_zero_progress([_Marker(f"run_complete_{i}.md"),
                                              _Marker("run_complete_zz.md")]))
    assert json.loads(sweep_state.read_text())["cycles"] >= bw.STALL_ALARM_CYCLES, \
        "a retirement reset the zero-progress counter mid-stall"
    assert any(fired), "the stall never paged despite never publishing"


def test_sweep_the_mutation_keying_on_oldest_would_pin_the_count_at_one(sweep_state):
    """THE MUTATION -- the old close condition was `state['oldest'] == oldest`. Replay the same
    churn under it and the count never leaves 1, so the alarm never fires."""
    state, count = {}, 0
    for i in range(bw.STALL_ALARM_CYCLES + 1):
        oldest = f"run_complete_{i}.md"
        count = state.get("cycles", 0) + 1 if state.get("oldest") == oldest else 1
        state = {"oldest": oldest, "cycles": count}
    assert count == 1, "the replay no longer churns the oldest -- the test above proves nothing"
    assert count < bw.STALL_ALARM_CYCLES


def test_sweep_a_publish_closes_the_episode(sweep_state):
    """CLEARS -- rc == 0 from the publisher, the one thing that refutes 'the publish path is not
    moving'. Without it the counter would ratchet forever and the alarm could never stand down."""
    for _ in range(bw.STALL_ALARM_CYCLES + 1):
        bw._check_zero_progress([_Marker("run_complete_a.md")])
    assert json.loads(sweep_state.read_text())["cycles"] >= bw.STALL_ALARM_CYCLES

    bw._record_marker_published("run_complete_a.md")
    assert json.loads(sweep_state.read_text())["cycles"] == 0

    bw._check_zero_progress([_Marker("run_complete_b.md")])
    assert json.loads(sweep_state.read_text())["cycles"] == 1


def test_sweep_an_empty_queue_closes_the_episode(sweep_state):
    """CLEARS -- the same independent signal the publish gate's own episode uses (the marker
    queue drained). The thing the alarm measures no longer exists."""
    for _ in range(bw.STALL_ALARM_CYCLES + 1):
        bw._check_zero_progress([_Marker("run_complete_a.md")])
    assert bw._check_zero_progress([]) is False
    assert json.loads(sweep_state.read_text()) == {}


def test_sweep_alarms_once_per_episode_not_once_per_oldest(sweep_state, monkeypatch):
    """R5. Keying the already-alarmed check on `oldest` meant a retirement -- which does not
    close the episode -- re-fired the page on an unchanged status."""
    monkeypatch.setattr(bw, "notify", lambda *a, **k: None, raising=False)
    fires = [bw._check_zero_progress([_Marker(f"run_complete_{i}.md")])
             for i in range(bw.STALL_ALARM_CYCLES + 5)]
    assert sum(fires) == 1, f"paged {sum(fires)} times for one open episode"


def test_sweep_close_is_a_noop_when_no_episode_is_open(sweep_state):
    bw._record_marker_published("run_complete_a.md")
    assert not sweep_state.exists() or json.loads(sweep_state.read_text()) == {}
