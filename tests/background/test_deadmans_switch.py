"""Tests for background/deadmans_switch.py -- director-flagged incident,
2026-07-09 (block-escalation didn't reach him for hours; this is deliberately
independent of the tmux/supervisor stack that failed)."""
import json
import time

import pytest

from background import deadmans_switch as dms
from background import action_needed


def _reset_state():
    # Transition state now lives in the notify() contract, not module globals -- the fixture
    # isolates notify.TRANSITIONS_FILE to a fresh per-test tmp file, so nothing to reset here.
    pass


# register_item() REFUSES an ask that is not one of the four things THE_STANDARD §2 still
# reserves for the director (background/action_needed.py::_reserved_for_director, delegating to
# one_way_door.classify_action -- the SOLE enumeration). These tests are about the RE-PING CLOCK,
# not about what may be asked, so they need a `what` that genuinely is the director's: a real-money
# ask. The placeholder "w" they used before predates that guard and now raises NotReservedForDirector
# at registration, which is a correct refusal, not a regression to suppress.
RESERVED_WHAT = "spend real money to pay a supplier invoice"
RESERVED_WHAT2 = "spend real money to pay a second supplier invoice"


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(dms, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(dms, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(dms, "OBSERVABILITY_DIR", tmp_path / "observability")
    # The deadman delegates transition-only + re-escalate to notify(); isolate its store to a fresh
    # per-test tmp file so each test starts un-escalated and never touches the real (G-T2-protected)
    # .notify_transitions.json. Sends are captured via ntfy_utils.send_ntfy (what notify calls).
    import background.notify as _notify
    monkeypatch.setattr(_notify, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    # Isolated from the real, committed action_needed_register.json --
    # every test starts with a genuinely empty register (2026-07-11).
    monkeypatch.setattr(action_needed, "REGISTER_PATH", tmp_path / "action_needed_register.json")
    # These tests exercise the commit-clock / staging escalation via run_cycle. Isolate the
    # OTHER run_cycle checks (which read real repo state) -- the pull-loop transport health --
    # otherwise a real, unrelated LOOP_BROKEN pollutes every send_ntfy assertion here. Each has
    # its own dedicated test file.
    #
    monkeypatch.setattr("background.process_reconciler.evaluate_pull_loop",
                        lambda: {"status": "UNKNOWN", "alarm": False, "detail": "(isolated)"})
    # raising=False, deliberately (2026-08-03): deadmans_switch._check_gate_wall() and
    # gate_authorization.evaluate_gate_wall() are being deleted with the rest of the per-atom
    # permission surface (DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY). A hard setattr on a
    # name that no longer exists is a SETUP AttributeError -- it errored all 48 tests in this
    # file, and because the pre-commit gate selects impacted tests across the whole dirty tree,
    # it refused EVERY writer's commit, not just this module's. raising=False keeps the
    # isolation while the check exists and no-ops once it is gone, so this fixture is correct
    # on both sides of that deletion instead of pinning one of them.
    monkeypatch.setattr("background.gate_authorization.evaluate_gate_wall",
                        lambda: {"status": "GATE_CLEAN", "alarm": False, "detail": "(isolated)",
                                 "unauthorized": []}, raising=False)
    monkeypatch.setattr("background.fork_reconciler.evaluate_fork_lifecycle",
                        lambda: {"status": "FORK_CLEAN", "alarm": False, "detail": "(isolated)",
                                 "orphans": [], "in_flight": [], "merged_eligible": [], "reaped": [],
                                 "enforce": False})
    monkeypatch.setattr("background.fork_reconciler.evaluate_worktree_reconcile",
                        lambda: {"status": "WORKTREE_CLEAN", "alarm": False, "detail": "(isolated)",
                                 "undeclared": []})
    monkeypatch.setattr("background.status_honesty.evaluate_status_honesty",
                        lambda: {"status": "HONEST", "honest": True, "detail": "(isolated)",
                                 "stale_claims": []})
    # H23_publish_gate_scope_marker: the operational-layer signal is its own dedicated
    # surface (test_operational_layer_signal.py) -- isolate it here to a no-op so these
    # commit-clock/staging tests never trigger a real (slow) pytest -m operational run or
    # touch the real .operational_layer_signal.json.
    monkeypatch.setattr("background.process_run_complete.run_operational_layer_signal",
                        lambda **k: {"ran": False, "reason": "isolated"})
    # Content-publishing freshness reads the REAL publish clock off disk, so a genuinely stale
    # live repo would fire a [PUBLISHING DOWN] into every send_ntfy assertion in this file. Same
    # treatment as the four checks above: healthy by default, overridden by its own tests below.
    monkeypatch.setattr("background.publish_freshness.snapshot",
                        lambda *a, **k: {"state": "publishing", "published_age_seconds": 60.0,
                                         "committed_age_seconds": 60.0,
                                         "committed_but_unpublished": False})
    (tmp_path / "staging").mkdir()
    (tmp_path / "observability").mkdir()
    _reset_state()
    yield
    _reset_state()


def test_no_staged_files_is_clean_no_ntfy(monkeypatch):
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)  # recent commit
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "Clean" in dms.LOG_FILE.read_text()


def test_gitkeep_alone_does_not_count_as_staged_work(monkeypatch):
    (dms.STAGING_DIR / ".gitkeep").write_text("")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)  # recent commit
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_staged_work_with_recent_activity_not_blocked(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)  # 1 min ago
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "not blocked" in dms.LOG_FILE.read_text()


def test_staged_work_with_stale_activity_sends_blocked_ntfy(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))  # 2h ago
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]
    assert "SOME_DOC.md" in calls[0]


def test_blocked_ntfy_does_not_repeat_within_re_escalate_window(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    dms.run_cycle()
    dms.run_cycle()
    assert len(calls) == 1


def test_blocked_ntfy_re_escalates_after_re_escalate_window(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1

    # Simulate the re-escalation window having elapsed: age the notify transition store's ts.
    import background.notify as _n
    store = json.loads(_n.TRANSITIONS_FILE.read_text())
    store[dms._COMMIT_KEY]["ts"] = time.time() - dms.RE_ESCALATE_SECONDS - 1
    _n.TRANSITIONS_FILE.write_text(json.dumps(store))
    dms.run_cycle()
    assert len(calls) == 2


def test_recovering_to_clean_resets_escalation_state(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    activity = {"epoch": time.time() - (2 * 3600)}
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: activity["epoch"])
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1

    # Genuine recovery: the queue drains AND a fresh commit lands.
    (dms.STAGING_DIR / "SOME_DOC.md").unlink()
    activity["epoch"] = time.time()
    dms.run_cycle()
    # Recovery re-arms: clear_transition popped the commit key from the notify store.
    import background.notify as _n
    store = json.loads(_n.TRANSITIONS_FILE.read_text()) if _n.TRANSITIONS_FILE.exists() else {}
    assert dms._COMMIT_KEY not in store


def test_recent_commits_returns_empty_on_git_failure(monkeypatch):
    """Fail-closed primitive: an unreadable commit history is NO known progress,
    never assumed-recent activity (R15 fail-closed)."""
    def _raise(*a, **k):
        raise Exception("no git")
    monkeypatch.setattr(dms.subprocess, "run", _raise)
    assert dms._recent_commits() == []
    # ...and that propagates to 0.0 ("looks stale") at the meaningful clock:
    assert dms._last_meaningful_commit_epoch() == 0.0


# ── H23_publish_gate_scope_marker: the operational-layer signal is wired onto
# THIS timer. Mutation coverage for the signal itself lives in its own
# dedicated file (test_operational_layer_signal.py); these two tests only
# prove the WIRING -- run_cycle drives it, and a crash inside it can never
# take down the deadman cycle (matches every other _check_* in this module).

def test_run_cycle_drives_the_operational_layer_signal(monkeypatch):
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: None)
    calls = []
    monkeypatch.setattr("background.process_run_complete.run_operational_layer_signal",
                        lambda **k: calls.append(1) or {"ran": True})
    dms.run_cycle()
    assert calls == [1]


def test_operational_layer_signal_crash_does_not_crash_run_cycle(monkeypatch):
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: None)

    def _boom(**k):
        raise RuntimeError("operational check exploded")
    monkeypatch.setattr("background.process_run_complete.run_operational_layer_signal", _boom)
    dms.run_cycle()  # must not raise
    assert "operational-layer signal check error" in dms.LOG_FILE.read_text()


# ── G-N4 DIGEST LEAK (2026-08-14) — the defect that held the operational-layer signal RED for
# 9 consecutive hourly checks while `pytest -m operational` was GREEN run by hand.
#
# run_cycle() calls _flush_notification_digest(), which reads the REAL append-only digest queue
# and sends through the SAME background.ntfy_utils.send_ntfy that every `assert calls == []` in
# this file monkeypatches to capture. When the 6-hourly digest is due with anything pending, that
# digest lands in each of those lists and 27 tests here go red at once -- on the daemon's run
# only, because the daemon spawns this suite from INSIDE run_cycle, before its own flush.
#
# The pin lives at DIRECTORY scope (tests/background/conftest.py, eighth entry) so it covers
# every current and future test in here, not a hand-maintained per-file list. R15 demands the pin
# be shown to FIRE on its own named defect, so both directions are asserted below: silent under
# the fixture, and red the moment the pin is bypassed. The second test is the mutation -- if it
# ever passes, the pin has stopped being load-bearing and the first test is proving nothing.

def test_a_due_digest_does_not_leak_into_this_files_ntfy_assertions(monkeypatch):
    """SILENT DIRECTION: the digest clock is forced fully due, and run_cycle still sends
    nothing, because the directory fixture pins the queue at an absent path."""
    from background import notification_digest as nd
    monkeypatch.setattr(nd, "_read_state", lambda: {"digested_through_seq": 0, "last_digest_ts": 0})
    assert nd._due(), "the clock must genuinely be due, or this test asserts nothing"
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_the_digest_pin_fires_when_it_is_bypassed(tmp_path, monkeypatch):
    """MUTATION: restore exactly what the directory fixture removes -- a due clock over a
    NON-empty queue -- and run_cycle emits the digest into the capture list. This is the
    observed 2026-08-14 failure, reproduced deliberately."""
    from background import notification_digest as nd
    queue = tmp_path / "leaky_queue.jsonl"
    queue.write_text(json.dumps(
        {"seq": 1, "kind": "real_alarm", "class": "seeded", "message": "a batched item"}) + "\n")
    monkeypatch.setattr(nd, "QUEUE_FILE", queue)
    monkeypatch.setattr(nd, "_read_state", lambda: {"digested_through_seq": 0, "last_digest_ts": 0})
    monkeypatch.setattr(nd, "_write_state", lambda state: None)
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert any("[DIGEST]" in c for c in calls), (
        "the pin is no longer load-bearing -- a due, non-empty digest queue must reach "
        "send_ntfy through run_cycle, or the silent-direction test above proves nothing")


def test_meaningful_clock_fails_closed_and_trips_blocked_when_git_unreadable(monkeypatch):
    """End-to-end: git unreadable -> meaningful epoch 0.0 -> since_commit ~= now
    -> with queued work the alarm MUST fire. An unavailable check is a FAILED
    check (R15 FAIL-SILENT), never a silent pass."""
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: [])  # git unreadable
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]


def test_last_activity_epoch_is_the_meaningful_commit_clock_only(monkeypatch):
    """The 2026-07-14 fixes: progress is the MEANINGFUL git commit clock ALONE
    (no observability-mtime term to contaminate it; no any-commit term for the
    auto-process no-op loop to refresh)."""
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: 12345.0)
    assert dms.last_activity_epoch() == 12345.0
    assert not hasattr(dms, "_last_observability_write_epoch")


def test_is_auto_process_commit_classifier():
    """The flat-no-op discriminator: real auto-process publish subjects are
    excluded; any genuine forward-work subject (including a maturity_map level
    bump) is kept."""
    assert dms._is_auto_process_commit(
        "Auto-process run complete: report + LATEST.md + site/ (git=abc, net=£1,521,070)"
    )
    assert not dms._is_auto_process_commit("[build] deadman_liveness_fix")
    assert not dms._is_auto_process_commit("[build] H12_mutation_test_controls L2->L3")
    assert not dms._is_auto_process_commit("Wave-1 integration: bank F7->L2")


def test_flat_auto_process_commits_do_not_refresh_liveness(monkeypatch):
    """R15 MUTATION TEST -- director-named THEATRE control (2026-07-14). PROVES
    the fixed control FIRES on its own named defect.

    The OLD deadman keyed liveness on ANY git commit, so the auto-process publish
    loop's ~15min flat no-op commits (identical net=£1,521,070, no forward work)
    refreshed the staleness clock and the switch reported 'not blocked' straight
    through the real 83-min executor-idle window (22:03-23:26) -- it NEVER fired.

    Here the ONLY commits inside the last 47min are auto-process run-completes;
    the last MEANINGFUL commit is 50min old and staged work is queued. The alarm
    MUST fire now (50min > 45min BLOCKED threshold). Mutation proof: revert
    last_activity_epoch to keying on the newest commit of ANY kind and this goes
    green->red -- the 2-min-old auto-process no-op would mask the stall exactly
    as it did in production."""
    now = time.time()
    commits = [
        (now - 2 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=aa1, net=£1,521,070)"),
        (now - 17 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=bb2, net=£1,521,070)"),
        (now - 32 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=cc3, net=£1,521,070)"),
        (now - 47 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=dd4, net=£1,521,070)"),
        (now - 50 * 60, "[build] real forward progress landed here"),
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]
    assert "STEER_INSTRUCTION.md" in calls[0]
    # Staleness is measured from the MEANINGFUL commit (50min), NOT the 2-min-old
    # auto-process no-op -- the whole point of the fix.
    assert "50 min" in calls[0]


def test_recent_meaningful_commit_is_not_blocked_despite_auto_process_noise(monkeypatch):
    """The legitimate case -- the fixed control must NOT false-fire. A real
    (non-auto-process) commit landed 5min ago; auto-process no-ops surround it.
    Even with staged work queued, this is healthy: no alarm."""
    now = time.time()
    commits = [
        (now - 3 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=ee5, net=£1,521,070)"),
        (now - 5 * 60, "[build] deadman_liveness_fix"),  # genuine progress, 5min ago
        (now - 20 * 60, "Auto-process run complete: report + LATEST.md + site/ (git=ff6, net=£1,521,070)"),
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "not blocked" in dms.LOG_FILE.read_text()


def test_all_auto_process_window_looks_stale(monkeypatch):
    """A window containing NOTHING but auto-process no-ops has no meaningful
    commit -- the real one is older than the whole window, so the honest answer
    is 0.0 ('very stale'), which trips the alarm rather than masking the wedge."""
    now = time.time()
    commits = [
        (now - i * 60, "Auto-process run complete: report + LATEST.md + site/ (git=x, net=£1,521,070)")
        for i in range(1, 40)
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    assert dms._last_meaningful_commit_epoch() == 0.0


def test_is_non_progress_commit_excludes_harden_reverify():
    """WORK_DEFINITION §1 (2026-07-27): a HARDEN re-verify never refreshes the liveness clock.
    The `chore(harden` form already matched the broader `chore(` prefix; the genuinely-new
    coverage is the `[HARDEN <atom>]` form, which touches real code/tests and so previously
    counted as forward work. A genuine BUILD commit is still forward progress (no over-exclusion)."""
    assert dms._is_non_progress_commit("[HARDEN D5_account_hierarchy_payments] Rule-0 dial-yield ...")
    assert dms._is_non_progress_commit("chore(harden): re-verify B1_margin_bridge after sibling scope-change")
    assert dms._is_non_progress_commit("chore(harden-cooldown): stamp ARCH1_internal_seams pass")
    # No over-exclusion: real forward work is NOT a HARDEN commit.
    assert not dms._is_non_progress_commit("[build] real forward progress landed here")
    assert not dms._is_non_progress_commit("Wave-1 integration: bank F7->L2")


def test_harden_only_window_looks_stale(monkeypatch):
    """R15 MUTATION TEST (WORK_DEFINITION §1): a window whose ONLY commits are `[HARDEN ...]`
    re-verifications has NO meaningful commit -- the last real commit is older than the whole
    window, so the honest answer is 0.0 ('very stale'), tripping the alarm rather than letting
    re-verification churn mask an idle window. Mutation proof: drop the `is_harden_commit` call
    from `_is_non_progress_commit` and the newest `[HARDEN ...]` commit's epoch is returned instead
    (window looks FRESH) -- this assertion goes green->red."""
    now = time.time()
    commits = [
        (now - i * 60, f"[HARDEN A{i}_some_atom] Rule-0 dial-yield re-verify -- no defect")
        for i in range(1, 30)
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    assert dms._last_meaningful_commit_epoch() == 0.0


def test_harden_window_with_real_build_commit_is_not_over_excluded(monkeypatch):
    """R15 fail-open direction (WORK_DEFINITION §1): the exclusion must NOT swallow real work.
    A genuine BUILD commit surrounded by HARDEN re-verifies is still the meaningful commit --
    its epoch is returned, so the window reads as live off the real work, not the HARDEN churn."""
    now = time.time()
    build_epoch = now - 10 * 60
    commits = [
        (now - 2 * 60, "[HARDEN A1_learn_loop_chair] Rule-0 dial-yield re-verify"),
        (now - 5 * 60, "chore(harden): stamp cooldown"),
        (build_epoch, "[build] W2_2 segmentation taxonomy landed"),
        (now - 20 * 60, "[HARDEN A3_approval_interface] re-verify"),
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    assert dms._last_meaningful_commit_epoch() == build_epoch


def test_daemon_log_writes_do_not_mask_a_stale_commit(monkeypatch):
    """MUTATION/REGRESSION GUARD for the 2026-07-14 fail-silent outage (R15 --
    the control must fire on its own named defect): the OLD deadman used the
    observability-dir mtime as an 'alive' signal, so its own 15-min log write
    (plus every other daemon's) reset the staleness clock every cycle -- it
    logged 'activity recent (0min ago)' for 6 hours straight while the session
    was wedged and staged files climbed 31->59. Here we reproduce EXACTLY that
    state: a stale commit (6h) with freshly-written daemon logs in the obs dir.
    The alarm MUST fire now; if this test ever goes green->red the fail-silent
    signal has been reintroduced."""
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 6 * 3600)
    # The contaminating writes that masked the stall before:
    (dms.OBSERVABILITY_DIR / "supervisor-log.md").write_text("supervisor just logged")
    (dms.OBSERVABILITY_DIR / "deadmans-switch-log.md").write_text("the switch's own write")
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]
    assert "STEER_INSTRUCTION.md" in calls[0]


def test_silent_stall_fires_with_empty_queue(monkeypatch):
    """Backstop tier: a wedged main session with NOTHING queued but work UNDONE (rest not proven
    legitimate) still trips an alarm once no commit has landed for SILENT_STALL_THRESHOLD_SECONDS.
    The proven-rest fold (2026-07-22) only suppresses STALL when rest is PROVABLY legitimate; here
    it is not, so STALL must still fire."""
    assert dms._unprocessed_staging_files() == []  # genuinely empty queue
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: False)  # a real wedge, not a rest
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 2 * 3600)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[STALL]" in calls[0]


def test_proven_rest_suppresses_stall(monkeypatch):
    """PROVEN-REST FOLD (director console 2026-07-22, point 3; R15 direction A): empty queue + a
    stale commit BUT rest is provably legitimate (authorized set empty at every level) => NO [STALL].
    This is tonight's 19:33 false-alarm class, now fixed: a proven rest is not a stall."""
    assert dms._unprocessed_staging_files() == []
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: True)   # drained-and-gated: no work
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 2 * 3600)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []                                   # no false STALL page
    assert "suppressed" in dms.LOG_FILE.read_text() and "PROVEN" in dms.LOG_FILE.read_text()


def test_rest_is_proven_legitimate_fails_safe_toward_alarm(monkeypatch):
    """R15 killer-pattern (FAIL-SILENT guard): if the drained-and-gated check cannot run, the
    predicate returns False (NOT a silent pass), so the deadman keeps its power to fire."""
    import background.supervisor as _sup
    monkeypatch.setattr(_sup, "_is_drained_and_gated", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert dms._rest_is_proven_legitimate() is False


def test_usage_pause_suppresses_the_alarm(monkeypatch):
    """A declared usage pause (.usage_pause.json, future resume_at) is a
    KNOWN-quiet window -- no commit for hours is expected, so both tiers are
    suppressed even with queued work and a very stale commit."""
    from datetime import datetime, timedelta, timezone
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 6 * 3600)
    resume_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    (dms.OBSERVABILITY_DIR / dms.USAGE_PAUSE_FILENAME).write_text(
        json.dumps({"resume_at": resume_at})
    )
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []
    assert "Usage pause active" in dms.LOG_FILE.read_text()


def test_expired_usage_pause_does_not_suppress(monkeypatch):
    """A usage pause whose resume_at has passed is NOT a live pause -- the
    alarm must fire (fails toward alarming, never suppresses on a stale file)."""
    from datetime import datetime, timedelta, timezone
    (dms.STAGING_DIR / "STEER_INSTRUCTION.md").write_text("queued")
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 6 * 3600)
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    (dms.OBSERVABILITY_DIR / dms.USAGE_PAUSE_FILENAME).write_text(
        json.dumps({"resume_at": past})
    )
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[BLOCKED]" in calls[0]


def test_blocked_message_names_the_supervisor_stack_explicitly(monkeypatch):
    (dms.STAGING_DIR / "SOME_DOC.md").write_text("staged")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - (2 * 3600))
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert "supervisor" in calls[0].lower()


# --- 2026-07-11: daily re-ping of open [ACTION NEEDED] items (director rule) ---

def test_run_cycle_repings_a_due_action_needed_item(monkeypatch):
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item(
        "routines-env-id", RESERVED_WHAT, "via claude.ai/code",
        "the invoice is real money", now=asked_at.isoformat(),
    )
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert calls[0].startswith("[ACTION NEEDED] routines-env-id")
    assert RESERVED_WHAT in calls[0]


def test_run_cycle_does_not_reping_within_24h(monkeypatch):
    action_needed.register_item("a", RESERVED_WHAT, "h", "y")  # just registered, now
    action_needed.mark_sent("a")  # ...and CONFIRMED sent just now (the real gate)
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_run_cycle_repings_a_registered_but_never_sent_item_immediately(monkeypatch):
    """CLASS FIX (2026-07-18, director-caught incident): register_item() alone --
    with NO confirmed send -- must NOT look 'recently pinged'. An item that was
    registered (even freshly) but never successfully sent is always due, so a
    prior send failure/skip retries on the very next cycle instead of going
    silent for 24h. This is the direct regression test for the real incident:
    register_item() no longer stamps the clock should_notify()/due_for_reping()
    read."""
    action_needed.register_item("a", RESERVED_WHAT, "h", "y")  # registered, but never sent
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1  # due immediately -- registration alone never suppresses


def test_run_cycle_does_not_reping_resolved_items(monkeypatch):
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", RESERVED_WHAT, "h", "y", now=asked_at.isoformat())
    action_needed.resolve_item("a", "answered")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []


def test_run_cycle_reping_is_independent_of_staging_activity_check(monkeypatch):
    """An action-needed re-ping must fire even when staging is completely
    clean -- it is not gated on the [BLOCKED]-class staging/activity check
    at all (a genuinely different alert class, see the module docstring)."""
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", RESERVED_WHAT, "h", "y", now=asked_at.isoformat())
    assert dms._unprocessed_staging_files() == []  # staging genuinely clean
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert calls[0].startswith("[ACTION NEEDED] a")


def test_run_cycle_repings_resets_the_daily_clock(monkeypatch):
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", RESERVED_WHAT, "h", "y", now=asked_at.isoformat())
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    # A CONFIRMED successful send returns a truthy id (real send_ntfy returns the
    # ntfy-assigned msg id) -- this is what actually advances the send-clock now
    # (action_needed.mark_sent()), not the mere fact that register_item ran.
    monkeypatch.setattr("background.ntfy_utils.send_ntfy",
                         lambda msg, **k: calls.append(msg) or "mock-msg-id")
    dms.run_cycle()
    assert len(calls) == 1

    dms.run_cycle()  # immediately again -- clock was just reset by the CONFIRMED send, must stay silent
    assert len(calls) == 1


# ── R15 mutation test: a FAILED/skipped send must never look "sent" (2026-07-18,
# the real incident this fork fixes -- a caller with no SE_NTFY_TOPIC, or any other
# send failure, kept every re-register from ever actually paging the director) ──

def test_run_cycle_failed_send_leaves_item_due_then_real_send_settles_it(monkeypatch):
    """THE core proof, fails under the pre-fix behaviour: a send that FAILS (returns
    a falsy/no id -- e.g. curl unreachable, no exception) must leave the item due for
    the very next cycle, not silenced for 24h. Once a send actually SUCCEEDS, it settles
    (fire-once-then-daily resumes)."""
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", RESERVED_WHAT, "h", "y", now=asked_at.isoformat())
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled

    # Cycle 1: the send FAILS (real send_ntfy returns None on a parse/network failure).
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg) or None)
    dms.run_cycle()
    assert len(calls) == 1  # attempted
    assert action_needed.load_register()["a"].get("last_sent_at") is None  # NOT marked sent

    # Cycle 2, immediately after: still due (the failed send did not suppress it) --
    # this is exactly the incident: under the OLD behaviour register_item's clock-stamp
    # would have made this cycle silent even though nothing was ever delivered.
    dms.run_cycle()
    assert len(calls) == 2  # retried, not silenced

    # Cycle 3: the send now SUCCEEDS (a real POST would return the ntfy msg id).
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg) or "real-id-123")
    dms.run_cycle()
    assert len(calls) == 3
    assert action_needed.load_register()["a"]["last_sent_at"] is not None  # now confirmed sent

    # Cycle 4, immediately after: settled -- fire-once-then-daily resumes, stays silent.
    dms.run_cycle()
    assert len(calls) == 3


def test_run_cycle_text_reregister_does_not_suppress_a_pending_never_sent_page(monkeypatch):
    """A caller re-registering an item's text (e.g. a refreshed `what`/`how`) must NOT
    suppress a page that has never actually been confirmed sent -- register_item() is
    bookkeeping only and must never roll the send-clock forward."""
    action_needed.register_item("a", RESERVED_WHAT, "h", "y")
    action_needed.register_item("a", RESERVED_WHAT2, "h2", "y2")  # a text-only re-register, no send yet
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy",
                         lambda msg, **k: calls.append(msg) or "mock-id")
    dms.run_cycle()
    assert len(calls) == 1  # still due -- the re-register never marked it sent


def test_run_cycle_resolved_item_never_pages_even_with_failed_send_history(monkeypatch):
    """A resolved item must never page again, regardless of any prior failed-send
    history (should_notify's resolved check is checked BEFORE the sent-clock)."""
    from datetime import datetime, timedelta, timezone
    asked_at = datetime.now(timezone.utc) - timedelta(hours=25)
    action_needed.register_item("a", RESERVED_WHAT, "h", "y", now=asked_at.isoformat())
    action_needed.resolve_item("a", "answered")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time())  # not stalled
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg) or None)
    dms.run_cycle()
    assert calls == []


def test_run_complete_markers_do_not_count_as_blocked_work(monkeypatch):
    """R3 completeness (2026-07-14, director: 'run_complete markers are STILL
    landing in docs/staging -- the R3 exclusion is incomplete'): a pile of
    auto-process markers is NOT a director-instruction backlog, so it must never
    raise [BLOCKED] on its own. With a recent commit and only markers queued, the
    deadman stays silent -- the pile is processing lag, surfaced by the commit
    clock ([STALL]) only if it ever means genuine inactivity, never a false
    [BLOCKED]."""
    for i in range(30):
        (dms.STAGING_DIR / f"run_complete_2026071{i:02d}.md").write_text("marker")
    assert dms._unprocessed_staging_files() == []  # markers excluded from queued work
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 60)  # recent commit
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert calls == []  # 30 markers + recent commit -> no alarm


def test_run_complete_pile_with_stale_commit_still_stalls(monkeypatch):
    """But markers do NOT blind the backstop: if the commit clock is genuinely
    stale, [STALL] still fires even though the only things 'queued' are markers
    (this is the exact blackout shape -- markers piling while nothing commits)."""
    for i in range(30):
        (dms.STAGING_DIR / f"run_complete_2026071{i:02d}.md").write_text("marker")
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: False)  # blackout is not a rest
    monkeypatch.setattr(dms, "_last_meaningful_commit_epoch", lambda: time.time() - 2 * 3600)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert len(calls) == 1
    assert "[STALL]" in calls[0]

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational


def test_misparked_actionable_in_progress_detected_but_not_legit_blocked(tmp_path, monkeypatch):
    """R15 both directions (2026-07-20 3-hour silent-stall class fix): a WORKER that mis-parks
    ACTIONABLE work into in_progress/ (disposition banner + 'authorised NOW') is flagged so it counts
    as queued work for the [BLOCKED] alarm; a genuinely director-blocked park (no worker banner, or a
    real wall not 'authorised NOW') is NOT flagged (no over-alarm)."""
    import background.deadmans_switch as dm
    ip = tmp_path / "in_progress"
    ip.mkdir()
    # mis-parked: worker banner + actionable-now marker
    (ip / "MISPARKED_STEER.md").write_text(
        "> **[IN-PROGRESS DISPOSITION -- 2026-07-20 worker tick]**\n"
        "> **Open sub-item (DISCOVER/FRAME, authorised NOW):** build the value frontier.\n")
    # legit worker park: a real wall, no 'authorised NOW'
    (ip / "LEGIT_BLOCKED.md").write_text(
        "> **[IN-PROGRESS DISPOSITION -- worker tick]**\n"
        "> **Wall / what unblocks:** the population-generator wiring is DIRECTOR-RESERVED; blocked on his act.\n")
    # director-parked multi-part (no worker banner at all)
    (ip / "DIRECTOR_PARKED.md").write_text(
        "# DIRECTOR STEER\n> Open sub-item: awaiting the director's console decision.\n")
    monkeypatch.setattr(dm, "_IN_PROGRESS_DIR", ip)
    got = dm._misparked_actionable_in_progress()
    assert got == ["in_progress/MISPARKED_STEER.md"]   # FIRES on the mis-park
    # QUIET on both legitimate parks (mutation guard: remove the marker -> not flagged)
    assert "in_progress/LEGIT_BLOCKED.md" not in got
    assert "in_progress/DIRECTOR_PARKED.md" not in got


# ───────────── EIGHTH CLASS: pending-batch deadlock + escalation duty (2026-07-27, DIRECTOR_RULING) ─────────────
#
# The 42h silent stall had TWO independent silencers, both fixed here:
#   H2  -- the liveness clock was refreshed by NON-WORK commits: `chore(liveness)` heartbeats (~30min)
#          and the planner's OWN `planner RUNG-7: rest-with-proof` bookkeeping commit. The clock must
#          count WORK commits only, so a window of nothing-but-those looks as stale as it is.
#   duty -- rest > 2h with any mint open, or rest > 6h in ANY circumstance, must raise an [ACT];
#          NEITHER may pass through the proven-rest fold (that fold is what silenced the [STALL]).


def test_liveness_and_rest_proof_commits_are_not_meaningful_progress(monkeypatch):
    """H2 FIX, the exact 07-27 clock: the most-recent non-auto-process commit was the planner's own
    rest-with-proof bookkeeping commit, and chore(liveness) heartbeats land ~every 30min. The clock
    must SKIP both classes and return the last REAL work commit (42h back), not be refreshed by them."""
    now = time.time()
    commits = [
        (now - 1 * 3600, "planner RUNG-7: rest-with-proof 2026-07-27 (premise FALSE -- all 6 mints blocked)"),
        (now - 2 * 3600, "chore(liveness): publish heartbeat while sim output unchanged (git=de9ab1fcc)"),
        (now - 3 * 3600, "Auto-process run complete: report + LATEST.md + site/ (net=£1,521,070)"),
        (now - 42 * 3600, "feat(pricing): merit-order reconstruction landed"),
    ]
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: commits)
    assert dms._last_meaningful_commit_epoch() == now - 42 * 3600
    # The predicate directly (independence, R15): each non-work class excluded, real work not.
    assert dms._is_non_progress_commit("chore(liveness): x") is True
    assert dms._is_non_progress_commit("planner RUNG-7: rest-with-proof") is True
    assert dms._is_non_progress_commit("Auto-process run complete: y") is True
    assert dms._is_non_progress_commit("feat(pricing): real work") is False


def _write_blocked_mint(slug: str, reason_line: str = "UNBLOCKS ON: director act") -> None:
    ip = dms.STAGING_DIR / "in_progress"
    ip.mkdir(parents=True, exist_ok=True)
    (ip / f"PLANNER_MINTED_{slug}.md").write_text(f"<!-- SUPERVISOR_DRAW: blocked -->\n{reason_line}\n")


def test_blocked_mint_reason_read_from_block_release_marker():
    """R10 CLASS FIX (BLOCKED_ITEM_LITERAL_ACTS 2026-07-29): a mint whose reason lives ONLY in the
    `<!-- BLOCK_RELEASE: <token> -- <reason> -->` marker (no prose blocked_on/UNBLOCKS line -- the
    exact shape of the four items the director reported as "blocked, reason unstated") must surface
    its stated reason, NOT the generic 'reason unstated' fallback.

    MUTATION both-ways: this reds against the pre-fix parser (which read only the two prose patterns
    and would return 'reason unstated' for a marker-only mint); a control mint that carries NO
    reason at all still correctly falls back to 'reason unstated' (the fix did not make the fallback
    unreachable)."""
    ip = dms.STAGING_DIR / "in_progress"
    ip.mkdir(parents=True, exist_ok=True)
    (ip / "PLANNER_MINTED_marker_only_reason.md").write_text(
        "<!-- SUPERVISOR_DRAW: blocked -->\n"
        "<!-- BLOCK_RELEASE: director_level_up -- intra-year price-cap granularity, "
        "pending sub-annual cap-window discovery -->\n# body with no prose blocked_on line\n")
    (ip / "PLANNER_MINTED_genuinely_no_reason.md").write_text(
        "<!-- SUPERVISOR_DRAW: blocked -->\n# body, no marker, no blocked_on\n")
    got = dict(dms._open_blocked_mints())
    reason = got["PLANNER_MINTED_marker_only_reason.md"]
    assert "reason unstated" not in reason
    assert "sub-annual cap-window" in reason           # the marker's reason surfaced
    assert reason.rstrip().endswith("discovery")        # trailing ` --` stripped, not left dangling
    # fallback still reachable for a mint that truly states nothing
    assert "reason unstated" in got["PLANNER_MINTED_genuinely_no_reason.md"]


def test_open_mint_escalation_fires_after_2h_even_on_proven_rest(monkeypatch):
    """ESCALATION DUTY, the weekend: mints parked-blocked, no WORK commit for 3h, and rest 'proven
    legitimate' (the fold that silenced [STALL]) -> an [ACT] naming each blocked mint STILL fires."""
    _write_blocked_mint("ssp_negative_lift_cells_2026-07-24", "UNBLOCKS ON: merit-order reconstruction landed")
    _write_blocked_mint("value_chain_observation_window_cap_2026-07-24", "blocked_on: WVC_R twin-gated")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 3 * 3600)
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: True)  # would suppress [STALL]
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    act = [c for c in calls if "minted work item" in c and "BLOCKED" in c]
    assert len(act) == 1
    assert "ssp_negative_lift_cells" in act[0] and "merit-order" in act[0]
    assert "value_chain" in act[0]


def test_open_mint_escalation_silent_within_2h(monkeypatch):
    """MUTATION both-ways: the SAME blocked mint but only 1h since the last work commit -> NO [ACT]
    (the 2h threshold is real state, not a constant-fire)."""
    _write_blocked_mint("value_chain_observation_window_cap_2026-07-24")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 1 * 3600)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert [c for c in calls if "minted work item" in c] == []


def test_hard_rest_cap_fires_after_6h_even_on_proven_rest(monkeypatch):
    """ESCALATION DUTY: rest > 6h must page in ANY circumstance -- even a proven-legitimate rest with
    NO mints open. This is the un-suppressible backstop the proven-rest-folded [STALL] tier lacked."""
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 7 * 3600)
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: True)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert [c for c in calls if "HARD REST CAP" in c]


def test_hard_rest_cap_silent_within_6h(monkeypatch):
    """MUTATION both-ways: 5h since the last work commit, proven rest -> the 6h cap is SILENT (a
    constant-fire cap would RED this)."""
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 5 * 3600)
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: True)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert [c for c in calls if "HARD REST CAP" in c] == []


# ───────────── LAW C: INDEPENDENT primary-state read (2026-07-27, DIRECTOR_RULING_FAILURE_BIAS_LAWS) ─────────────
#
# The 42h stall trusted ONE source: the deadman's proven-rest fold consulted the supervisor's own
# `_is_drained_and_gated()` enumeration, and self-drawable mints were EXCLUDED from every pager. LAW
# C severs that -- the deadman now reads in_progress/ DIRECTLY (background.primary_state_scan, no
# supervisor import) so a self-drawable mint the tick is not drawing pages regardless of what the
# enumeration claims. Two sources that can disagree.


def _write_self_drawable_mint(slug: str, title: str = "LAW-under-test") -> None:
    ip = dms.STAGING_DIR / "in_progress"
    ip.mkdir(parents=True, exist_ok=True)
    (ip / f"PLANNER_MINTED_{slug}.md").write_text(
        f"<!-- SUPERVISOR_DRAW: self-drawable -->\n# {title}\nbody\n")


def test_self_drawable_undrawn_read_is_independent_and_excludes_blocked():
    """The independent primitive returns SELF-DRAWABLE mints and EXCLUDES blocked/unmarked ones --
    the exact complement of `_open_blocked_mints()`. Pure-disk read, no supervisor import."""
    _write_self_drawable_mint("law_a_suppression_rearm", "LAW A")
    _write_blocked_mint("some_blocked_thing")  # SUPERVISOR_DRAW: blocked
    ip = dms.STAGING_DIR / "in_progress"
    (ip / "PLANNER_MINTED_unmarked.md").write_text("# no marker\nbody\n")  # invisible by convention
    got = dms._self_drawable_undrawn()
    names = [n for n, _ in got]
    assert "PLANNER_MINTED_law_a_suppression_rearm.md" in names
    assert "PLANNER_MINTED_some_blocked_thing.md" not in names   # blocked -> not this pager's class
    assert "PLANNER_MINTED_unmarked.md" not in names             # unmarked -> excluded (fail-closed)


def test_drawable_undrawn_escalation_fires_after_2h_independent_of_enumeration(monkeypatch):
    """LAW C, direction A (INDEPENDENCE): a self-drawable mint sits undrawn, no work commit for 3h,
    and the SUPERVISOR'S enumeration reports rest proven-legitimate -- the exact false-empty class.
    An [ACT] naming the undrawn mint STILL fires, because the deadman reads disk itself and does not
    trust the tick's verdict. Mutation guard: point the check back at `_rest_is_proven_legitimate`
    (trust the enumeration) and this goes green->red."""
    _write_self_drawable_mint("failure_bias_law_a", "LAW A: suppression re-arm")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 3 * 3600)
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: True)  # enumeration says drained
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    act = [c for c in calls if "SELF-DRAWABLE mint" in c and "[ACT]" in c]
    assert len(act) == 1
    assert "failure_bias_law_a" in act[0]
    assert "LAW C" in act[0]


def test_drawable_undrawn_escalation_silent_within_2h(monkeypatch):
    """LAW C, direction B (MUTATION both-ways): the SAME undrawn mint but only 1h since the last
    work commit -> NO [ACT]. The 2h threshold is real state, not a constant-fire."""
    _write_self_drawable_mint("failure_bias_law_b", "LAW B")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 1 * 3600)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert [c for c in calls if "SELF-DRAWABLE mint" in c] == []


def test_self_drawable_mint_vetoes_proven_rest_stall(monkeypatch):
    """LAW C VETO (INDEPENDENCE): empty root queue + a stale commit (100min) + rest 'proven
    legitimate' (the supervisor verdict that WOULD fold [STALL]) -- BUT a self-drawable mint sits
    undrawn on disk. The independent read vetoes the suppression, so [STALL] fires and NAMES the
    mint. Contrast test_proven_rest_suppresses_stall (no mint present -> correctly suppressed): that
    pair is the mutation both-ways for the veto. 100min is inside [90min STALL, 120min [ACT]) so
    only the [STALL] tier is under test here."""
    assert dms._unprocessed_staging_files() == []           # root queue genuinely empty
    _write_self_drawable_mint("failure_bias_law_c", "LAW C")
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 100 * 60)
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: True)  # would suppress if trusted alone
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    stall = [c for c in calls if "[STALL]" in c]
    assert len(stall) == 1
    assert "failure_bias_law_c" in stall[0] and "LAW C" in stall[0]


# ── [PUBLISHING DOWN]: the instant class that had no sender (2026-08-13) ──────────────────────
#
# `notification_digest` names four INSTANT classes from the director's own words -- action_needed,
# blocked_work, decision_waiting, publishing_down. On 2026-08-13 a grep found ZERO callers of any
# of them, and publishing_down had never been emitted by anything. The site served day-old figures
# for eighteen hours and the director found it by looking.

def _stale(hours, **over):
    snap = {"state": "stale", "published_age_seconds": hours * 3600,
            "committed_age_seconds": hours * 3600, "committed_but_unpublished": False}
    snap.update(over)
    return snap


def test_a_content_freeze_pages_the_director(monkeypatch):
    """The incident. Eighteen hours since the figures reached origin -> an instant page."""
    monkeypatch.setattr("background.publish_freshness.snapshot", lambda *a, **k: _stale(18))
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))

    dms.run_cycle()

    down = [c for c in calls if "PUBLISHING DOWN" in c]
    assert len(down) == 1, "a content freeze must page -- this is the class with no sender"
    assert "18.0h" in down[0]


def test_a_healthy_publish_does_NOT_page(monkeypatch):
    """MUTATION both ways: the threshold is real state, not a constant-fire."""
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    dms.run_cycle()
    assert [c for c in calls if "PUBLISHING" in c] == []


def test_a_landing_heartbeat_cannot_silence_the_publishing_alarm(monkeypatch):
    """THE MASKING, as a test (director, 2026-08-13).

    Through the whole freeze, commits kept landing -- worker commits and a `chore(liveness)`
    heartbeat every thirty minutes -- so the commit-clock alarm was correctly silent and the tick
    verdict was `drew`. An alarm that consulted either of those could never have caught this. This
    fires on a fresh commit clock and a proven-legitimate rest, because its subject is the FIGURES.
    """
    monkeypatch.setattr("background.publish_freshness.snapshot", lambda *a, **k: _stale(18))
    monkeypatch.setattr(dms, "last_activity_epoch", lambda: time.time() - 60)  # just committed
    monkeypatch.setattr(dms, "_rest_is_proven_legitimate", lambda: True)
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))

    dms.run_cycle()

    assert [c for c in calls if "PUBLISHING DOWN" in c], (
        "the publishing alarm was suppressed by a healthy commit clock -- liveness is precisely "
        "what masked this freeze, so an alarm that liveness can silence is the wrong alarm"
    )
    assert [c for c in calls if "[STALL]" in c or "[BLOCKED]" in c] == []


def test_the_page_is_routed_INSTANT_not_batched(monkeypatch):
    """G-N3: publishing_down is one of the four the director reserved for immediate sending, so
    it must reach the wire rather than the digest queue. MUTATION: classify it as a deferrable
    category and this fails."""
    from background import notification_digest

    assert notification_digest.is_instant(notification_digest.PUBLISHING_DOWN)
    monkeypatch.setattr("background.publish_freshness.snapshot", lambda *a, **k: _stale(18))
    deferred = []
    monkeypatch.setattr(notification_digest, "defer",
                        lambda m, **k: deferred.append(m) or "deferred:0")
    sent = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: sent.append(msg))

    dms.run_cycle()

    assert [s for s in sent if "PUBLISHING DOWN" in s]
    assert [d for d in deferred if "PUBLISHING DOWN" in d] == []


def test_recovery_is_its_own_transition(monkeypatch):
    """R5. The director is told publishing came back, rather than having to notice an alarm
    stopped repeating -- and the recovery page does not then repeat either."""
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))
    monkeypatch.setattr("background.publish_freshness.snapshot", lambda *a, **k: _stale(18))
    dms.run_cycle()
    assert len([c for c in calls if "PUBLISHING DOWN" in c]) == 1

    calls.clear()
    dms.run_cycle()          # still stale, same state -> silent (transition-only)
    assert [c for c in calls if "PUBLISHING" in c] == []

    calls.clear()
    monkeypatch.setattr("background.publish_freshness.snapshot",
                        lambda *a, **k: {"state": "publishing", "published_age_seconds": 30.0,
                                         "committed_age_seconds": 30.0,
                                         "committed_but_unpublished": False})
    dms.run_cycle()
    assert len([c for c in calls if "PUBLISHING] Recovered" in c]) == 1

    calls.clear()
    dms.run_cycle()          # still healthy -> silent again
    assert [c for c in calls if "PUBLISHING" in c] == []


def test_committed_but_unpublished_names_its_own_cause(monkeypatch):
    """Two faults, two fixes -- and this is the one that hides best.

    On 2026-08-13 the publish path had not landed for 21.7h, and `site/data/dashboard.json` still
    reached origin twice in that window because unrelated worker commits happened to sweep the
    regenerated file along. Figures that move by luck look like figures that move, so the page has
    to say that the PUBLISH PATH is what stopped rather than implying the content is frozen.
    """
    monkeypatch.setattr("background.publish_freshness.snapshot",
                        lambda *a, **k: _stale(20, committed_age_seconds=60.0,
                                               committed_but_unpublished=True))
    calls = []
    monkeypatch.setattr("background.ntfy_utils.send_ntfy", lambda msg, **k: calls.append(msg))

    dms.run_cycle()

    down = [c for c in calls if "PUBLISHING DOWN" in c][0]
    assert "PUBLISH PATH itself is what stopped" in down
    assert "still being committed" in down


# ── R15: THE LIVE-LOG REFUSAL, ON TRIAL IN BOTH DIRECTIONS (2026-08-21) ─────────────────────
# `deadmans_switch.log()` routes its destination through `live_ledger_guard.guard_live_ledger_write`,
# closing at the choke point the class R10 forbids closing at the instance: the operational suite
# was appending fabricated `[LOOP BROKEN] ... cannot draw: import failed` lines to the live
# `docs/observability/deadmans-switch-log.md` while the transport read HEALTHY_IDLE
# (WORKER_FINDING_THE_OPERATIONAL_SUITE_WRITES_FAKE_LOOP_BROKEN_ALARMS_INTO_THE_LIVE_DEADMAN_LOG).
#
# A control that cannot fail is worse than none, so BOTH legs are asserted here:
#   * drop the `guard_live_ledger_write` call from `log()` -> `test_the_live_deadman_log_refuses_a_test_process` fails.
#   * make the guard refuse unconditionally (ignore `is_live_record_path`) -> the null control
#     `test_a_redirected_deadman_log_still_writes` fails, because the refusal would also have
#     ended the logging every one of this module's 30 call sites depends on.
# The second leg is the one that matters: the cheap way to green the first is to refuse always,
# which silences the instrument instead of isolating the fixture.
def test_the_live_deadman_log_refuses_a_test_process(monkeypatch, tmp_path):
    """The LIVE path is refused -- and refused for being live, not for being absent."""
    from background.live_ledger_guard import LiveLedgerWriteUnderTest, LIVE_RECORD_DIR

    live = LIVE_RECORD_DIR / "deadmans-switch-log.md"
    before = live.read_text() if live.exists() else None
    monkeypatch.setattr(dms, "LOG_FILE", live)
    with pytest.raises(LiveLedgerWriteUnderTest) as exc:
        dms.log("LOOP BROKEN checked (notify-gated): cannot draw: import failed")
    # The error names the writer to change, not just the fact of refusal.
    assert "deadmans_switch.log" in str(exc.value)
    # And nothing reached the record: the refusal is BEFORE the append, not after it.
    assert (live.read_text() if live.exists() else None) == before


def test_a_redirected_deadman_log_still_writes(monkeypatch, tmp_path):
    """NULL CONTROL. The same call, one field changed -- the destination -- must SUCCEED.

    This is what stops the refusal being greened by refusing everything: `log()` is the deadman's
    only diagnostic channel, and a guard that cannot tell a tmp_path from the live record would
    take the whole log out with the fixture rows."""
    dest = tmp_path / "deadmans-switch-log.md"
    monkeypatch.setattr(dms, "LOG_FILE", dest)
    dms.log("LOOP BROKEN checked (notify-gated): cannot draw: import failed")
    assert "cannot draw: import failed" in dest.read_text()
