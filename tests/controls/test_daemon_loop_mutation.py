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


def _sent_hours_ago(register, item_id, hours):
    # The re-ping cadence keys on last_sent_at (the CONFIRMED-send clock), NOT
    # last_pinged_at (2026-07-18 [ACT]-paging class fix: a registered-but-never-
    # SENT item stays due). So a cadence fixture must mark the item SENT `hours`
    # ago, not merely registered -- register_item alone leaves last_sent_at unset,
    # which correctly reads as never-sent => always due (a separate behaviour,
    # tested elsewhere), not as a fresh page.
    ts = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    # The `what` must be a genuinely RESERVED ask since 2026-08-03 -- `register_item` refuses
    # anything outside the four real-world classes (THE_STANDARD §2). These cases are about the
    # re-ping CADENCE, not about what may be asked, so any reserved ask serves.
    action_needed.register_item(item_id, "authorise spending real money on the paid feed",
                                "how", "why", path=register, now=ts)
    action_needed.mark_sent(item_id, path=register, now=ts)


def test_reping_fires_when_item_is_overdue(register):
    # DEFECT PRESENT: an open item last SENT 25h ago (> RE_PING_SECONDS=24h).
    # The re-ping timer MUST surface it. A never-fires mutant is killed here.
    _sent_hours_ago(register, "one-way-door-q", hours=25)
    due = action_needed.due_for_reping(path=register)
    assert [e["item_id"] for e in due] == ["one-way-door-q"]


def test_reping_silent_when_item_is_fresh(register):
    # DEFECT ABSENT: SENT 1h ago -- the timer must NOT fire. An always-fires /
    # stuck-open mutant (re-pings every cycle regardless of elapsed time) is
    # killed here.
    _sent_hours_ago(register, "recent-q", hours=1)
    assert action_needed.due_for_reping(path=register) == []


def test_reping_cadence_constant_is_load_bearing(register, monkeypatch):
    # MUTATE THE CONSTANT: an item SENT 25h ago is due under the real 24h
    # cadence. Break the cadence (timer set never to elapse) and the SAME item
    # must stop surfacing -- proving the verdict is CAUSED by the constant, not
    # incidental. This is what distinguishes a real timer from a fail-open one.
    _sent_hours_ago(register, "q", hours=25)
    assert action_needed.due_for_reping(path=register)  # real cadence: due

    monkeypatch.setattr(action_needed, "RE_PING_SECONDS", 10 ** 12)  # ~31,000 yrs
    assert action_needed.due_for_reping(path=register) == []  # verdict flipped


def test_reping_boundary_is_at_the_threshold_not_above_it(register, monkeypatch):
    # Sensitivity at the boundary: exactly-at-threshold fires, just-under stays
    # quiet. A mutant using > instead of >= (or an off-by-a-lot threshold) is
    # killed by one of these two directions.
    monkeypatch.setattr(action_needed, "RE_PING_SECONDS", 3600)  # 1h for a crisp edge
    _sent_hours_ago(register, "at-edge", hours=1)  # exactly 1h -> due (>=)
    assert [e["item_id"] for e in action_needed.due_for_reping(path=register)] == ["at-edge"]

    reg2 = register.parent / "reg2.json"
    _sent_hours_ago(reg2, "under-edge", hours=0.9)  # 54min -> not yet
    assert action_needed.due_for_reping(path=reg2) == []


# =========================================================================
# 2. deadmans_switch stall cadence + RE_ESCALATE cooldown
# =========================================================================

# The checks `dms_isolated` below neutralises, and the ones it deliberately lets run for real.
# Named constants rather than a literal inside the fixture so the CLASS GUARD at the end of this
# section can pin them against what `run_cycle` actually calls -- see that test for why.
NEUTRALISED_BY_DMS_ISOLATED = (
    "_check_pull_loop_transport",
    "_check_fork_lifecycle",
    "_check_worktree_reconcile",
    "_check_status_honesty",
    "_check_operational_layer_signal",
    # The two below were found by the class guard on its FIRST run -- neither was in the original
    # list and neither is targeted by any test in this file. Both scan REAL primary state
    # (`_open_blocked_mints()` / `_self_drawable_undrawn()` read the live maturity map and
    # docs/staging/in_progress/) and both `notify(kind="real_alarm")`, which _capture_ntfy records
    # -- so a fire appends to `calls` and breaks the `assert len(calls) == 1` these tests are built
    # on. They stayed quiet only by accident of arithmetic: they need since_commit >= 2h and the
    # stall tests pin their gap at BLOCKED_THRESHOLD + 60s (~46min). Any test here that used a
    # longer gap would have paged the director from a unit test. That is latent, not isolated.
    "_check_open_mint_escalation",
    "_check_drawable_undrawn_escalation",
    # ADDED 2026-08-13 by this section's own class guard, on the FIRST cycle after `run_cycle`
    # gained it in c8284059b. Exactly the shape the guard was built for, and it caught it in one
    # commit rather than the eighteen days `_check_operational_layer_signal` went unnoticed.
    # Disqualified on all three counts, not one: it PAGES (`notify(kind="real_alarm")` on the
    # PUBLISHING_DOWN class, which _capture_ntfy records -- a fire appends to `calls` and breaks
    # the `assert len(calls) == 1` every test here is built on); it reads
    # `publish_freshness.STATE_FILE`, an ABSOLUTE path into the real docs/observability/ that
    # this fixture's OBSERVABILITY_DIR patch does not reach; and `publish_freshness.snapshot()`
    # shells out to git for `last_committed_ts`. Not latent either -- publishing is stale RIGHT
    # NOW (the wedge these tests sit inside), so its alarm branch is the live one.
    "_check_content_publishing",
    # NOT a `_check_*` name, and that is the whole point -- see the class guard below, whose
    # subject was widened on 2026-08-13 because this function proved the guard was watching a
    # NAMING CONVENTION rather than a call set. `run_cycle` calls it every cycle; it reads
    # `notification_digest.QUEUE_FILE` (again an absolute path into the real docs/observability/)
    # and SENDS the batched digest through the same `ntfy_utils.send_ntfy` that `_capture_ntfy`
    # records -- observed as a second entry ("[DIGEST] 21 batched item(s)") breaking
    # `assert len(calls) == 1` in all six stall/cooldown tests.
    # BOUND, R9 -- what did NOT happen: the real high-water mark did not move. `flush` advances
    # it only on a CONFIRMED delivery and `_capture_ntfy`'s lambda returns None, so the queue
    # stayed intact (.ntfy_digest_state.json mtime unchanged across the run that observed this).
    # The director lost no batched item. Neutralised for the count, not for a data loss.
    "_flush_notification_digest",
)

# Allowed to run for real, each for a stated reason. A check earns a place here only if it is
# cheap, read-only, spawns NO subprocess, and cannot page -- i.e. it cannot perturb the
# `assert len(calls) == 1` assertions these mutation tests are made of.
RUN_FOR_REAL_BY_DMS_ISOLATED = {
    # Reads `git rev-parse --is-bare-repository` and logs. No subprocess suite, no notify path.
    "_check_repo_not_bare": "cheap read-only git query; logs only, never notifies",
    # The seven below were surfaced by WIDENING the class guard past `_check_*` on 2026-08-13.
    # None was a new addition to `run_cycle` -- every one had been running for real in these 12
    # cycles all along, unexamined, because the guard could not see a name that did not start
    # with `_check`. Each is recorded with WHY it is safe, so the next reader inherits a decision
    # rather than an omission.
    "_digest_classes": "lazy `import notification_digest` returning the module; no I/O, no notify",
    "_reping_open_action_needed_items":
        "CAN page, but the fixture patches action_needed.REGISTER_PATH to tmp_path, so it reads an "
        "empty register and has nothing to re-ping -- isolated by construction, not by luck",
    "_unprocessed_staging_files":
        "reads the PATCHED STAGING_DIR only; must run for real -- it is how these tests get work "
        "onto the queue at all",
    "_self_drawable_undrawn":
        "reads `STAGING_DIR / in_progress` -- the PATCHED dir (its own docstring says it uses the "
        "live STAGING_DIR precisely so the test patch isolates it); read-only, never notifies",
    "_usage_pause_active": "reads the PATCHED OBSERVABILITY_DIR pause file; read-only, never notifies",
    "_misparked_actionable_in_progress":
        "read-only, no subprocess, cannot page. CAVEAT, stated rather than hidden: it reads the "
        "FROZEN `_IN_PROGRESS_DIR` (real docs/staging/in_progress/), which the STAGING_DIR patch "
        "does NOT reach. It can only APPEND to `staged`, and every assertion here is on the notify "
        "count, so live content cannot flip a verdict -- but if a test ever asserts on len(staged), "
        "this is the one to isolate first",
    "_rest_is_proven_legitimate":
        "imports supervisor and reads real disk, but is short-circuited out on every path here "
        "(`(not staged) and stall_by_clock and ...`) and cannot page -- it returns a bool that "
        "fails safe toward alarm",
}

# The machinery these tests EXIST to exercise. Neutralising any of it in the fixture would delete
# the subject rather than isolate it, so the guard must not demand a fixture classification for it.
# `last_activity_epoch` is the commit clock itself: every stall/cooldown test monkeypatches it
# per-case to place the gap, which is a stronger isolation than the fixture could give it.
_INFRA_NOT_A_CHECK = frozenset({
    "run_cycle", "log", "notify", "clear_transition", "last_activity_epoch",
})


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
    # run_cycle() runs 5 OTHER independent checks (pull-loop transport, gate-wall, fork-lifecycle,
    # worktree-reconcile, status-honesty) that each scan REAL repo/process state and can PAGE. No test
    # here targets them, so no-op them -- otherwise these stall/commit-clock mutation tests flake on
    # live state (a real fork orphan added a 2nd page => assert len(calls)==1 failed; R2 caught it in
    # the running gate though the test passed in isolation).
    # `_check_gate_wall` dropped from this list 2026-08-03: the function was DELETED with the
    # permission machinery (it paged a GATE_VIOLATION whenever an atom advanced with no
    # director-console authorization -- an alarm on the machine doing what THE_STANDARD requires).
    # raising=False is deliberately NOT used: if a name here stops existing, that should fail loudly
    # rather than silently no-op a check this fixture believes it is neutralising.
    #
    # `_check_operational_layer_signal` ADDED 2026-08-12 -- it was the one check `run_cycle` gained
    # after this list was written, and the list did not move with it. OBSERVED, not inferred: at
    # 04:26Z the live publish gate's own content suite (pid 855448, `-m 'not operational'`) had
    # `pytest tests/ -m 'operational or join_report_only or scale_report_only'` as a CHILD process,
    # with PYTEST_CURRENT_TEST=tests/controls/test_daemon_loop_mutation.py::test_stall_alarm_fires_
    # when_commit_stale_and_work_queued. The signal throttles on
    # process_run_complete.OPERATIONAL_LAYER_STATE_FILE -- an absolute path into the REAL
    # docs/observability/, which this fixture's OBSERVABILITY_DIR patch does not reach -- so the
    # first of these 12 run_cycle() calls after each hour boundary read the live throttle, found
    # itself due, and launched the ENTIRE operational suite nested inside the content gate. That is
    # what made a gate cycle take 40+ minutes against a 5-9 minute commit interval, and it wrote
    # the live .operational_layer_signal.json from inside a test.
    for _chk in NEUTRALISED_BY_DMS_ISOLATED:
        monkeypatch.setattr(dms, _chk, lambda *a, **k: None)
    (tmp_path / "staging").mkdir()
    (tmp_path / "observability").mkdir()
    dms._last_escalation_ts = None
    yield tmp_path
    dms._last_escalation_ts = None


def test_dms_isolated_accounts_for_every_check_run_cycle_calls():
    """R10 CLASS GUARD: the fixture's neutralise-list is a hand-maintained enumeration, and a
    hand-maintained enumeration of someone else's call set rots silently. This makes it rot LOUDLY.

    THE CLASS, not the instance. The instance was `_check_operational_layer_signal`: added to
    `run_cycle`, never added to `dms_isolated`, and therefore executed for real inside 12 mutation
    tests -- where it spawned the entire `-m operational` pytest suite as a child of the publish
    gate's own content suite and wrote the live docs/observability/ throttle file. Adding that one
    name back is an instance fix and R10 forbids closing here on one. The defect that PRODUCED it is
    that nothing related the fixture's list to `run_cycle`'s body, so the next check added to
    `run_cycle` would land in exactly the same hole. This test is that relation.

    NOT A TAUTOLOGY (R15): the two sides come from independent sources. The expected side is read
    from `run_cycle`'s own SOURCE -- the actual call set, which changes when a developer edits the
    daemon. The actual side is the fixture's declared constants. Neither is derived from the other,
    so this fails when they diverge in either direction:
      * a check added to `run_cycle` and not classified here -> UNACCOUNTED (the observed defect);
      * a name classified here that `run_cycle` no longer calls -> STALE (the list keeps
        neutralising a ghost, which is how `_check_gate_wall` lingered after it was deleted).
    """
    import inspect
    import re

    src = inspect.getsource(dms.run_cycle)
    # SUBJECT WIDENED 2026-08-13. This used to match `_check_[A-Za-z0-9_]+` only, which made the
    # guard's real subject a NAMING CONVENTION rather than run_cycle's call set -- so
    # `_flush_notification_digest` sat in the loop sending the live digest through these 12 cycles
    # and the guard reported all-accounted-for. A guard that only sees the names it expects is the
    # same defect one level up ("a test isolates the paths it thought of"), so match EVERY call and
    # keep only those that resolve to a module-level callable on `dms`: that set moves when the
    # daemon is edited, under any name a future author picks.
    called = {
        name
        for name in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", src)
        if name not in _INFRA_NOT_A_CHECK and callable(getattr(dms, name, None))
    }

    # FAIL-CLOSED on a lost subject (R15 fail-silent doctrine): if `run_cycle` is refactored so no
    # `_check_*` call is textually visible, this guard would pass over an empty set and prove
    # nothing. An unavailable check is a FAILED check -- say so instead of going green.
    assert called, (
        "run_cycle() no longer shows any _check_*() call in its source -- this guard has lost its "
        "subject and is green over nothing. Re-point it at however run_cycle now dispatches its "
        "checks before trusting it again."
    )

    # THE ESCAPE HATCH IS ITSELF PINNED (R15 fail-open, found by mutation-testing this guard on
    # 2026-08-13). `_INFRA_NOT_A_CHECK` subtracts from the subject, so anyone who drops a name into
    # it silences this guard for that name -- the mutant "hide `_flush_notification_digest` behind
    # the infra set" passed GREEN until this pin existed. A bypass with no control on it is the
    # fail-open pattern, so the set is pinned to its four notify-plumbing entries plus the commit
    # clock. Widening it is legal, but it must be a DELIBERATE edit here that says why -- never a
    # quiet way to make a red name go away.
    assert set(_INFRA_NOT_A_CHECK) == {
        "run_cycle", "log", "notify", "clear_transition", "last_activity_epoch",
    }, (
        "_INFRA_NOT_A_CHECK has changed to {}. It subtracts from this guard's subject, so every "
        "name in it is a check that will run FOR REAL and never be reported. Justify the new entry "
        "here (it must be machinery these tests exercise directly, or something each test patches "
        "itself) rather than using this set to quiet an unaccounted name.".format(
            sorted(_INFRA_NOT_A_CHECK))
    )

    classified = set(NEUTRALISED_BY_DMS_ISOLATED) | set(RUN_FOR_REAL_BY_DMS_ISOLATED)

    unaccounted = called - classified
    assert not unaccounted, (
        "run_cycle() calls {} which dms_isolated neither neutralises nor deliberately allows.\n"
        "Every one of the 12 run_cycle() calls in this file will therefore execute it FOR REAL, "
        "against live repo/process/observability state.\n"
        "Decide which it is:\n"
        "  * it scans real state, pages, writes outside tmp_path, or spawns a subprocess\n"
        "      -> add it to NEUTRALISED_BY_DMS_ISOLATED;\n"
        "  * it is cheap, read-only and cannot notify\n"
        "      -> add it to RUN_FOR_REAL_BY_DMS_ISOLATED with the reason.\n"
        "This is the hole _check_operational_layer_signal fell through on 2026-08-12: it launched "
        "the whole operational suite inside the publish gate.".format(sorted(unaccounted))
    )

    stale = classified - called
    assert not stale, (
        "dms_isolated classifies {} but run_cycle() no longer calls it. A neutralise-list entry "
        "for a function that is gone is dead weight that hides the next real addition (and "
        "monkeypatch.setattr will raise once the attribute itself disappears). Drop it.".format(
            sorted(stale))
    )


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
