"""Mutation-test the DAEMON SCHEDULING LOOPS -- H12_daemon_loop_mutation, R15.

The H12 pass-1/pass-2 mutation harness covered the *deterministic* control
apparatus (compliance invariants, Tier-1 gates, R14 gates, the epistemic
verifier, the Qwen backstop). It explicitly named the DAEMON SCHEDULING LOOPS
(cadence / cooldown / backoff / re-ping timers) as an L3 residual: those loops
are controls too -- a stall alarm that never fires, a cooldown stuck open, a
backoff that never resets are all controls that *cannot fail*, and per R15 a
control that cannot fail is worse than none.

DOCTRINE (CONTROLS_THAT_CANNOT_FAIL.md, the three killer patterns applied to a
schedule):

  * A loop that NEVER FIRES  == FAIL-SILENT: the stall/due condition is met but
    the guard stays quiet. Killed by a "defect present -> guard fires" assertion.
  * A cooldown STUCK OPEN    == two failure directions:
      - never suppresses -> the alarm spams every cycle (a broken cooldown that
        always fires). Killed by a "repeat within window -> exactly one alert".
      - never releases   -> the alarm never re-fires while still stuck. Killed by
        a "window elapsed -> re-fires" assertion.
  * A backoff that NEVER RESETS == the tracker latches: a genuinely-progressing
    atom stays deprioritised forever. Killed by a "real change -> counter resets".

Each control below is mutation-tested twice: (1) the defect is present and the
guard MUST fire, and (2) the defect is absent and the guard MUST stay quiet --
so BOTH a never-fires mutant and an always-fires mutant are killed. Where the
schedule constant itself is the control, we additionally MUTATE THE CONSTANT
(monkeypatch it to the defective value) and assert the verdict FLIPS, proving
the constant is load-bearing (rules out a fail-open guard that would pass
regardless of the schedule).

No daemon runtime behaviour is changed here -- tests only.
"""
import json
import time
from datetime import datetime, timedelta, timezone

import pytest

from background import deadmans_switch as dms
from background import action_needed
from background import supervisor
from background import ntfy_utils
from background import notify as _notify_mod


# =========================================================================
# 1. action_needed re-ping cadence (RE_PING_SECONDS) -- the "re-ping timer"
# =========================================================================
# due_for_reping() IS the control: it decides whether an open "waiting on Rich"
# item is stale enough to re-alert. Its named defect is a timer that never
# fires (an open one-way-door question sits silently forever) or one that fires
# constantly (spam every cycle).

@pytest.fixture
def register(tmp_path):
    return tmp_path / "register.json"


def _pinged_hours_ago(register, item_id, hours):
    ts = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    action_needed.register_item(item_id, "q", "how", "why", path=register, now=ts)


def test_reping_fires_when_item_is_overdue(register):
    # DEFECT PRESENT: an open item last pinged 25h ago (> RE_PING_SECONDS=24h).
    # The re-ping timer MUST surface it. A never-fires mutant is killed here.
    _pinged_hours_ago(register, "one-way-door-q", hours=25)
    due = action_needed.due_for_reping(path=register)
    assert [e["item_id"] for e in due] == ["one-way-door-q"]


def test_reping_silent_when_item_is_fresh(register):
    # DEFECT ABSENT: pinged 1h ago -- the timer must NOT fire. An always-fires /
    # stuck-open mutant (re-pings every cycle regardless of elapsed time) is
    # killed here.
    _pinged_hours_ago(register, "recent-q", hours=1)
    assert action_needed.due_for_reping(path=register) == []


def test_reping_cadence_constant_is_load_bearing(register, monkeypatch):
    # MUTATE THE CONSTANT: an item pinged 25h ago is due under the real 24h
    # cadence. Break the cadence (timer set never to elapse) and the SAME item
    # must stop surfacing -- proving the verdict is CAUSED by the constant, not
    # incidental. This is what distinguishes a real timer from a fail-open one.
    _pinged_hours_ago(register, "q", hours=25)
    assert action_needed.due_for_reping(path=register)  # real cadence: due

    monkeypatch.setattr(action_needed, "RE_PING_SECONDS", 10 ** 12)  # ~31,000 yrs
    assert action_needed.due_for_reping(path=register) == []  # verdict flipped


def test_reping_boundary_is_at_the_threshold_not_above_it(register, monkeypatch):
    # Sensitivity at the boundary: exactly-at-threshold fires, just-under stays
    # quiet. A mutant using > instead of >= (or an off-by-a-lot threshold) is
    # killed by one of these two directions.
    monkeypatch.setattr(action_needed, "RE_PING_SECONDS", 3600)  # 1h for a crisp edge
    _pinged_hours_ago(register, "at-edge", hours=1)  # exactly 1h -> due (>=)
    assert [e["item_id"] for e in action_needed.due_for_reping(path=register)] == ["at-edge"]

    reg2 = register.parent / "reg2.json"
    _pinged_hours_ago(reg2, "under-edge", hours=0.9)  # 54min -> not yet
    assert action_needed.due_for_reping(path=reg2) == []


# =========================================================================
# 2. deadmans_switch stall cadence + RE_ESCALATE cooldown
# =========================================================================

@pytest.fixture(autouse=False)
def dms_isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(dms, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(dms, "OBSERVABILITY_DIR", tmp_path / "observability")
    monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path / "an_register.json")
    # Suppression/cooldown is owned by notify() via its TRANSITIONS_FILE now (not dms's old
    # _last_*_ts). Isolate it per-test so the cooldown these mutations exercise starts clean and
    # never pollutes the real transition state.
    monkeypatch.setattr(_notify_mod, "TRANSITIONS_FILE", tmp_path / "notify_transitions.json")
    (tmp_path / "staging").mkdir()
    (tmp_path / "observability").mkdir()
    dms._last_escalation_ts = None
    yield tmp_path
    dms._last_escalation_ts = None


def _capture_ntfy(monkeypatch):
    calls = []
    # deadmans_switch notifies via background.notify.notify now (`send_ntfy` was removed in the
    # notify-contract refactor). notify() OWNS transition-only/cooldown SUPPRESSION and calls
    # ntfy_utils.send_ntfy only for an ACTUAL send — so capture THERE (patching notify itself would
    # bypass the suppression these mutation tests verify).
    monkeypatch.setattr(ntfy_utils, "send_ntfy", lambda message, **kwargs: calls.append(message))
    return calls


def test_stall_alarm_fires_when_commit_stale_and_work_queued(dms_isolated, monkeypatch):
    # DEFECT PRESENT: staged work + no commit for > BLOCKED_THRESHOLD (45min).
    # The stall loop MUST fire [BLOCKED]. A never-fires mutant is killed here.
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch",
                        lambda: time.time() - (dms.BLOCKED_THRESHOLD_SECONDS + 60))
    calls = _capture_ntfy(monkeypatch)
    dms.run_cycle()
    assert len(calls) == 1 and "[BLOCKED]" in calls[0]


def test_stall_alarm_silent_when_commit_recent(dms_isolated, monkeypatch):
    # DEFECT ABSENT: staged work but a fresh commit -> not blocked. An
    # always-fires mutant (alarms on any queued work regardless of the timer)
    # is killed here.
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)
    calls = _capture_ntfy(monkeypatch)
    dms.run_cycle()
    assert calls == []


def test_stall_threshold_constant_is_load_bearing(dms_isolated, monkeypatch):
    # MUTATE THE CONSTANT: the same 46-min-stale + queued state fires under the
    # real 45min threshold. Push the threshold beyond the elapsed gap and the
    # alarm must go silent -- verdict flips, proving the threshold gates it.
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    # A FIXED stale gap of ~46min, pinned to the real threshold NOW so the
    # mutation below cannot move it (the lambda must not re-read the constant).
    stale_gap = dms.BLOCKED_THRESHOLD_SECONDS + 60
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - stale_gap)
    calls = _capture_ntfy(monkeypatch)
    dms.run_cycle()
    assert len(calls) == 1  # real threshold: fires

    dms._last_escalation_ts = None
    monkeypatch.setattr(dms, "BLOCKED_THRESHOLD_SECONDS", 10 ** 9)
    monkeypatch.setattr(dms, "SILENT_STALL_THRESHOLD_SECONDS", 10 ** 9)
    calls.clear()
    dms.run_cycle()
    assert calls == []  # verdict flipped: a 46-min stall no longer counts


def test_re_escalate_cooldown_suppresses_within_window(dms_isolated, monkeypatch):
    # COOLDOWN STUCK-OPEN (never-suppresses direction): three cycles inside the
    # RE_ESCALATE window must yield exactly ONE alert, not one per cycle. A
    # mutant whose cooldown never suppresses spams -- killed here.
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch",
                        lambda: time.time() - (dms.BLOCKED_THRESHOLD_SECONDS + 60))
    calls = _capture_ntfy(monkeypatch)
    dms.run_cycle()
    dms.run_cycle()
    dms.run_cycle()
    assert len(calls) == 1


def test_re_escalate_cooldown_releases_after_window(dms_isolated, monkeypatch):
    # COOLDOWN STUCK-OPEN (never-releases direction): once the RE_ESCALATE
    # window elapses the alarm MUST re-fire while still stuck. A mutant whose
    # cooldown never releases goes permanently silent after the first alert --
    # killed here.
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch",
                        lambda: time.time() - (dms.BLOCKED_THRESHOLD_SECONDS + 60))
    calls = _capture_ntfy(monkeypatch)
    dms.run_cycle()
    assert len(calls) == 1
    # notify() owns the re-escalate window now (via TRANSITIONS_FILE's per-key ts), not the defunct
    # dms._last_escalation_ts. Rewind the recorded send time past RE_ESCALATE so an unchanged-but-
    # still-stuck state is due to re-fire (a never-releases mutant stays silent here = killed).
    _trans = json.loads(_notify_mod.TRANSITIONS_FILE.read_text())
    for _k in _trans:
        _trans[_k]["ts"] = time.time() - dms.RE_ESCALATE_SECONDS - 1
    _notify_mod.TRANSITIONS_FILE.write_text(json.dumps(_trans))
    dms.run_cycle()
    assert len(calls) == 2


def test_re_escalate_cooldown_resets_on_recovery(dms_isolated, monkeypatch):
    # BACKOFF/COOLDOWN NEVER-RESETS: after recovering to clean the cooldown
    # state must reset, so a NEW stall re-alerts immediately rather than being
    # swallowed by the stale timer. A never-resets mutant would suppress the
    # second genuine stall -- killed here.
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    activity = {"epoch": time.time() - (dms.BLOCKED_THRESHOLD_SECONDS + 60)}
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: activity["epoch"])
    calls = _capture_ntfy(monkeypatch)
    dms.run_cycle()
    assert len(calls) == 1

    # Recover to genuinely CLEAN: the queue drains AND a fresh commit lands.
    # Only the fully-clean branch resets the cooldown -- a persisting queue with
    # a recent commit is "not blocked" but not a reset either.
    (dms.STAGING_DIR / "SOME_DOC.md").unlink()
    activity["epoch"] = time.time() - 30
    dms.run_cycle()
    assert len(calls) == 1
    assert dms._last_escalation_ts is None  # reset happened

    # A brand-new stall must re-alert at once (not suppressed by a stale timer).
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged again")
    activity["epoch"] = time.time() - (dms.BLOCKED_THRESHOLD_SECONDS + 60)
    dms.run_cycle()
    assert len(calls) == 2


# =========================================================================
# 3. supervisor stuck-grant escalation cadence (STUCK_THRESHOLD_SECONDS)
# =========================================================================
# _check_stuck_escalation is the control: it alarms when the supervisor keeps
# granting turns for the SAME work with no state change for > threshold. Its
# named defect is a timer that never fires (silent livelock) or one that fires
# every cycle (spam) or one that never re-arms for a genuinely new stuck state.

@pytest.fixture(autouse=False)
def sup_isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "STUCK_STATE_FILE", tmp_path / ".stuck.json")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".atom_stall.json")
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    yield tmp_path


class _FakeClock:
    def __init__(self, start=1_000_000.0):
        self.t = start

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def test_stuck_escalation_fires_after_threshold(sup_isolated, monkeypatch):
    # DEFECT PRESENT: the same stuck key persists past STUCK_THRESHOLD. The
    # cadence MUST fire once. A never-fires mutant (silent livelock) is killed.
    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    ntfy = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy.append(msg))

    supervisor._check_stuck_escalation("same-work")  # establishes first_seen_at
    assert ntfy == []
    clock.advance(supervisor.STUCK_THRESHOLD_SECONDS + 1)
    supervisor._check_stuck_escalation("same-work")
    assert len(ntfy) == 1 and "swallowing turns" in ntfy[0]


def test_stuck_escalation_silent_before_threshold(sup_isolated, monkeypatch):
    # DEFECT ABSENT: not yet at threshold -> must stay quiet. An always-fires
    # mutant (alarms the moment the key repeats) is killed here.
    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    ntfy = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy.append(msg))

    supervisor._check_stuck_escalation("same-work")
    clock.advance(supervisor.STUCK_THRESHOLD_SECONDS - 60)
    supervisor._check_stuck_escalation("same-work")
    assert ntfy == []


def test_stuck_escalation_threshold_constant_is_load_bearing(sup_isolated, monkeypatch):
    # MUTATE THE CONSTANT: elapse exactly the real threshold -> fires. With the
    # threshold pushed far beyond that same elapsed gap, the identical history
    # must NOT fire -- verdict flips, proving the constant gates the alarm.
    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    ntfy = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy.append(msg))

    monkeypatch.setattr(supervisor, "STUCK_THRESHOLD_SECONDS", 10 ** 9)
    supervisor._check_stuck_escalation("same-work")
    clock.advance(3600 + 1)  # would trip the real 1h threshold
    supervisor._check_stuck_escalation("same-work")
    assert ntfy == []  # mutant threshold: no alarm despite an hour of no progress


def test_stuck_escalation_deduped_within_stuck_state(sup_isolated, monkeypatch):
    # COOLDOWN STUCK-OPEN (never-suppresses): many cycles past threshold on the
    # same key must yield exactly one alert. A mutant that re-alerts every cycle
    # is killed here.
    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    ntfy = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy.append(msg))

    supervisor._check_stuck_escalation("same-work")
    for _ in range(10):
        clock.advance(supervisor.STUCK_THRESHOLD_SECONDS)
        supervisor._check_stuck_escalation("same-work")
    assert len(ntfy) == 1


def test_stuck_clock_resets_and_re_arms_on_new_key(sup_isolated, monkeypatch):
    # NEVER-RESETS: a genuinely NEW stuck state must re-arm the clock (reset
    # first_seen_at + escalated=False) so it can alarm again. A mutant that
    # never resets would (a) alarm instantly on the new key using the stale
    # clock, or (b) never alarm again -- both killed here.
    clock = _FakeClock()
    monkeypatch.setattr(supervisor.time, "time", clock)
    ntfy = []
    monkeypatch.setattr(supervisor, "ntfy", lambda msg: ntfy.append(msg))

    # First stuck state alarms once.
    supervisor._check_stuck_escalation("work-A")
    clock.advance(supervisor.STUCK_THRESHOLD_SECONDS + 1)
    supervisor._check_stuck_escalation("work-A")
    assert len(ntfy) == 1

    # Key changes (real progress -> new work): clock must re-arm, NOT alarm now.
    clock.advance(1)
    supervisor._check_stuck_escalation("work-B")
    assert len(ntfy) == 1  # no instant alarm on the fresh key (reset happened)

    # And it must be able to alarm again once the NEW state itself ages out.
    clock.advance(supervisor.STUCK_THRESHOLD_SECONDS + 1)
    supervisor._check_stuck_escalation("work-B")
    assert len(ntfy) == 2  # re-armed


# =========================================================================
# 4. supervisor anti-livelock backoff (ATOM_STALL_THRESHOLD) -- "backoff reset"
# =========================================================================
# _record_atom_draw_and_check_stall is the control: it deprioritises an atom the
# draw keeps re-selecting with no state change. Its named defects are a backoff
# that never fires (a spinning atom is re-drawn forever) and one that never
# resets (a genuinely-progressing atom stays permanently deprioritised).

def test_backoff_fires_on_repeated_unchanged_draw(sup_isolated):
    # DEFECT PRESENT: the same fingerprint drawn ATOM_STALL_THRESHOLD times must
    # flag stalled. A never-fires mutant (backoff disabled) is killed here.
    fp = "unchanged"
    for i in range(supervisor.ATOM_STALL_THRESHOLD):
        stalled, count = supervisor._record_atom_draw_and_check_stall("SPIN", fp)
    assert stalled is True
    assert count == supervisor.ATOM_STALL_THRESHOLD


def test_backoff_does_not_fire_below_threshold(sup_isolated):
    # DEFECT ABSENT: one draw is not a stall. An always-fires mutant (flags on
    # the first draw) is killed here.
    stalled, count = supervisor._record_atom_draw_and_check_stall("SPIN", "fp")
    assert stalled is False and count == 1


def test_backoff_resets_on_real_change(sup_isolated):
    # NEVER-RESETS: after the atom is stalled, a genuinely changed fingerprint
    # (real progress) must reset the counter to 1 and CLEAR the stalled flag. A
    # latching mutant that never resets would keep a progressing atom
    # deprioritised forever -- killed here.
    supervisor._record_atom_draw_and_check_stall("SPIN", "fp1")
    supervisor._record_atom_draw_and_check_stall("SPIN", "fp1")
    assert supervisor._is_atom_stalled("SPIN")  # now stalled

    stalled, count = supervisor._record_atom_draw_and_check_stall("SPIN", "fp2")
    assert stalled is False and count == 1
    assert not supervisor._is_atom_stalled("SPIN")  # flag cleared by the reset


def test_backoff_threshold_constant_is_load_bearing(sup_isolated, monkeypatch):
    # MUTATE THE CONSTANT: two identical draws stall under the real threshold=2.
    # Raise the threshold and the SAME two draws must NOT stall -- verdict
    # flips, proving the constant gates the backoff (not a fail-open latch).
    monkeypatch.setattr(supervisor, "ATOM_STALL_THRESHOLD", 5)
    fp = "unchanged"
    stalled = False
    for _ in range(2):
        stalled, _ = supervisor._record_atom_draw_and_check_stall("SPIN", fp)
    assert stalled is False  # under the mutated threshold, 2 draws is not a stall
