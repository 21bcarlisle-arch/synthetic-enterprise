"""OPS1 sub-step 4: the drift control made LIVE — periodic reconcile, transition-only paging.

The load-bearing property is that this is the LIVE consumer the reconcile lacked (its absence let a
live worker-seat declared `held` produce no HELD_VIOLATED, 2026-07-17). R5: it pages only on a drift
TRANSITION, never a heartbeat; a clean run logs and stays silent."""
from __future__ import annotations

from pathlib import Path

import pytest

from background import reconcile_watch as W


@pytest.fixture(autouse=True)
def _isolate_the_gap_ledger_source(monkeypatch):
    """The gap-ledger reconcile is the THIRD drift source and it reads real git + the real ledger.
    A new source that a test lets fall through to live disk silently flips every clean/drift
    assertion in this file the moment the live ledger goes stale — the same fixture-isolation
    class the F-lane draw rung hit. Default it to clean here; the tests that exercise it inject
    their own rows in the body, which runs after this fixture and therefore wins."""
    monkeypatch.setattr(W._gap, "reconcile", lambda *a, **k: [])


def _clean():
    proc = [{"session": "sim-runner", "status": "OK", "alarm": False},
            {"session": "supervisor", "status": "HELD", "alarm": False}]
    sched = [{"kind": "unit", "item": "file-api.service", "status": "OK", "alarm": False}]
    return proc, sched


def _drift():
    proc = [{"session": "supervisor", "status": "HELD_VIOLATED", "alarm": True},
            {"session": "sim-runner", "status": "OK", "alarm": False}]
    sched = [{"kind": "cron", "item": "0 * * * * evil", "status": "UNDECLARED_CRON", "alarm": True}]
    return proc, sched


def test_signature_is_order_independent_and_empty_when_clean():
    proc, sched = _clean()
    assert W.drift_signature(proc, sched) == []
    proc2, sched2 = _drift()
    sig = W.drift_signature(proc2, sched2)
    assert "P:supervisor:HELD_VIOLATED" in sig
    assert "S:0 * * * * evil:UNDECLARED_CRON" in sig


def test_clean_report_says_clean_and_lists_nothing():
    proc, sched = _clean()
    sig, summary = W.build_report(proc, sched)
    assert sig == [] and "clean" in summary


def test_drift_report_lists_each_alarm():
    proc, sched = _drift()
    sig, summary = W.build_report(proc, sched)
    assert "supervisor: HELD_VIOLATED" in summary
    assert "UNDECLARED_CRON" in summary


@pytest.fixture
def _wired(monkeypatch, tmp_path):
    pages = []
    monkeypatch.setattr(W, "STATE_FILE", tmp_path / ".reconcile_watch_state.json")
    monkeypatch.setattr(W, "LOG_FILE", tmp_path / "reconcile-watch-log.md")
    return pages


def test_clean_run_does_not_page(_wired):
    proc, sched = _clean()
    paged = W.run(proc, sched, notify=lambda *a, **k: _wired.append((a, k)))
    assert paged is False and _wired == []


def test_drift_appears_pages_once_then_stays_silent_until_change(_wired):
    proc, sched = _drift()
    notify = lambda *a, **k: _wired.append((a, k))
    assert W.run(proc, sched, notify=notify) is True          # transition clean->drift: page
    assert len(_wired) == 1
    assert W.run(proc, sched, notify=notify) is False         # same drift: no repeat (R5)
    assert len(_wired) == 1


def test_drift_clearing_pages_a_recovery(_wired):
    notify = lambda *a, **k: _wired.append((a, k))
    dp, ds = _drift()
    W.run(dp, ds, notify=notify)                              # drift -> page (rotating_light)
    cp, cs = _clean()
    assert W.run(cp, cs, notify=notify) is True               # cleared -> page (recovery)
    assert _wired[-1][1]["headers"]["X-Tags"] == "white_check_mark"


def test_drift_present_is_typed_high_priority(_wired):
    dp, ds = _drift()
    W.run(dp, ds, notify=lambda *a, **k: _wired.append((a, k)))
    assert _wired[0][1]["headers"]["X-Tags"] == "rotating_light"
    assert _wired[0][1]["headers"]["X-Priority"] == "high"

# --- the gap-ledger source, wired in 2026-08-09 ------------------------------------------------
# H_GAP's three-times-registered residual: eleven couple_*/gap tools, no production caller, so
# their published rows go stale unseen. This watch is the caller — the reconcile is report-only,
# so being SEEN on a transition is the whole mechanism.

def _gap_drift():
    return [{"item": "W1_11_fabric_physics_core", "kind": "row", "producers": [],
             "status": "stale", "detail": "producer moved"},
            {"item": "W2_7_willingness_classification", "kind": "row", "producers": [],
             "status": "current", "detail": "unchanged"}]


def test_a_stale_gap_row_reaches_the_drift_signature_under_its_own_prefix():
    proc, sched = _clean()
    sig = W.drift_signature(proc, sched, _gap_drift())
    assert sig == ["G:W1_11_fabric_physics_core:stale"]


def test_a_gap_row_measured_by_current_code_adds_nothing():
    proc, sched = _clean()
    current_only = [r for r in _gap_drift() if r["status"] == "current"]
    assert W.drift_signature(proc, sched, current_only) == []


def test_gap_drift_pages_on_its_own_even_when_processes_are_clean(_wired):
    """The property that matters: this source can page by itself. A third source folded in so
    that it can only ever ride along with process drift would be decorative."""
    proc, sched = _clean()
    notify = lambda *a, **k: _wired.append((a, k))  # noqa: E731
    assert W.run(proc, sched, notify=notify, gap_results=_gap_drift()) is True
    assert "gap:stale" in _wired[0][0][0]
    assert _wired[0][1]["headers"]["X-Tags"] == "rotating_light"


def test_the_summary_caps_the_gap_lines_and_SAYS_SO_while_the_signature_keeps_them_all():
    """No silent caps: an elided line must be counted out loud, and the transition signal must
    still see every item or a change inside the tail could not page."""
    many = [{"item": f"W9_{i}_x", "kind": "row", "producers": [], "status": "stale",
             "detail": "d"} for i in range(W._GAP_SUMMARY_CAP + 3)]
    proc, sched = _clean()
    sig, summary = W.build_report(proc, sched, many)
    assert len(sig) == len(many)
    assert summary.count("[gap:stale]") == W._GAP_SUMMARY_CAP
    assert "and 3 further gap-ledger" in summary


def test_run_falls_through_to_the_live_reconcile_when_no_rows_are_injected(monkeypatch):
    """Production must not need the caller to pass rows — otherwise the wiring is inert."""
    seen = []
    monkeypatch.setattr(W._gap, "reconcile", lambda *a, **k: seen.append(1) or [])
    proc, sched = _clean()
    W.run(proc, sched, notify=lambda *a, **k: None)
    assert seen == [1]


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811

pytestmark = pytest.mark.operational


# ── DAEMONS RUNNING CODE THAT IS NO LONGER HEAD (2026-08-21) ────────────────────────────────
# R2, "committed != running", is a permanent rule here and it was being broken at scale: three
# daemons 57, 63 and 65 changed loaded modules behind, four days stale. The supervisor was
# drawing work on four-day-old logic and a publishing-down alarm fixed that morning was inert in
# the process that runs it.
#
# The control was NOT missing. `evaluate_boot_sha_drift` computed it exactly and `health_check`
# phrased the fault well. Its only caller was `start_worker.sh` -- stack startup -- so it ran at
# the one moment drift cannot exist and never while it accumulated. health-check-log.md's last
# entry was 2026-07-29, twenty-three days earlier.

def test_a_daemon_far_behind_head_is_reported():
    """The observed incident."""
    out = W._drift_report(evaluate=lambda: {"stale_detail": {
        "supervisor": ["m"] * 57, "background-worker": ["m"] * 63}})
    assert any("supervisor (57 modules behind)" in line for line in out)
    assert any("background-worker (63 modules behind)" in line for line in out)


def test_ordinary_churn_is_not_reported():
    """ALWAYS-RED IS THE FAILURE MODE HERE, not under-reporting. This tree takes ~20 commits a
    day, so every daemon is 1-2 modules behind within minutes of restarting. A detector that
    fires on that gets ignored -- which is exactly how four days of real drift went unseen while
    a correct control computed it."""
    assert W._drift_report(evaluate=lambda: {"stale_detail": {
        "sim-runner": ["m"] * 2, "deadmans-switch": ["m"]}}) == []


def test_the_threshold_sits_in_the_gap_the_measurement_found():
    """1-2 is churn, 57+ is stale, and nothing was observed between. A threshold inside that gap
    is read from the data; one outside it would be a preference."""
    assert 2 < W.DRIFT_MODULE_THRESHOLD < 57


def test_the_drift_check_never_restarts_anything():
    """REPORT-ONLY (G-R3). Redeploying a daemon mid-work has its own blast radius and belongs to
    a decision, not to a reconcile pass -- a watcher that quietly restarted things is the
    accretion OPS1 forbids."""
    # The CODE, not the prose. First cut grepped the whole source and tripped on this
    # function's own docstring, which contains "restart" precisely because it promises not to --
    # a check reading text it should not have been reading, which is the day's recurring shape
    # in miniature.
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(W._drift_report).strip())
    fn = tree.body[0]
    if (fn.body and isinstance(fn.body[0], ast.Expr)
            and isinstance(fn.body[0].value, ast.Constant)):
        fn.body = fn.body[1:]                      # drop the docstring
    code = ast.unparse(ast.Module(body=fn.body, type_ignores=[])).lower()
    for verb in ("restart", "systemctl", "kill", "terminate"):
        assert verb not in code, f"the drift reporter must not {verb}"


# ── THE MEMORY THAT COULD NOT SAY IT HAD BEEN LOST (2026-09-05) ─────────────────────────────
# `_load_last` answered `[]` for an ABSENT state file and `[]` for every corrupt one, and `[]` is
# this carrier's CLEAN BASELINE. So a corrupt file beside a currently-clean reconcile made
# `sig != last` False and the RECOVERY page was never sent: the director keeps holding the last
# alarm he received, with nothing recording that the all-clear was swallowed. The eleven other
# conflations on this census fail LOUD (a duplicate page, an extra run); this one was the only one
# that failed QUIET, which is why it is the one that got a direction rather than a shrug.


def _corrupt(path, raw="{not json"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw)


def test_the_recovery_page_a_lost_memory_used_to_swallow(_wired):
    """THE OBSERVED DEFECT. Corrupt memory + clean reconcile: under the old loader `last` was `[]`,
    `sig` was `[]`, so `changed` was False and nothing was sent."""
    _corrupt(W.STATE_FILE)
    proc, sched = _clean()
    assert W.run(proc, sched, notify=lambda *a, **k: _wired.append((a, k))) is True
    assert len(_wired) == 1
    assert _wired[0][1]["headers"]["X-Tags"] == "white_check_mark"


def test_the_page_says_the_transition_claim_could_not_be_made(_wired):
    """Fail closed AND say so on the surface. An all-clear that silently means 'clean now, and we
    cannot tell you what it was' is a stronger claim than we hold."""
    _corrupt(W.STATE_FILE)
    proc, sched = _clean()
    W.run(proc, sched, notify=lambda *a, **k: _wired.append((a, k)))
    assert "PRESENT AND UNREADABLE" in _wired[0][0][0]
    assert "clean" in _wired[0][0][0], "the current reconcile must still be stated, not replaced"


def test_a_lost_memory_beside_live_drift_still_pages_the_alarm_not_a_recovery(_wired):
    """The other half of the branch: `cleared` widened to include the unreadable case, so it has to
    be shown NOT firing when there is drift to report. A watcher that answered white_check_mark
    while eight items were diverging would be worse than the defect it replaced."""
    _corrupt(W.STATE_FILE)
    dp, ds = _drift()
    assert W.run(dp, ds, notify=lambda *a, **k: _wired.append((a, k))) is True
    assert _wired[0][1]["headers"]["X-Tags"] == "rotating_light"
    assert _wired[0][1]["headers"]["X-Priority"] == "high"


def test_an_absent_memory_is_still_the_clean_baseline_and_a_first_clean_run_stays_silent(_wired):
    """THE DIRECTION THAT WAS DELIBERATELY NOT CHANGED. The loader's original argument is sound and
    the repair must not take it with it: a first clean run is not a transition. Over-correcting to
    'anything that is not a readable signature pages' would make every fresh install page once,
    which is the always-red shape this file already refuses elsewhere."""
    assert not W.STATE_FILE.exists()
    proc, sched = _clean()
    assert W.run(proc, sched, notify=lambda *a, **k: _wired.append((a, k))) is False
    assert _wired == []


def test_a_corrupt_memory_pages_once_and_not_on_every_tick(_wired):
    """WHAT MAKES PAGING AFFORDABLE. `run` saves the signature on every page, so the corrupt file
    is replaced in the same pass. If it were not, this repair would trade one swallowed all-clear
    for a page every five minutes -- and an always-red watcher is an ignored watcher."""
    _corrupt(W.STATE_FILE)
    proc, sched = _clean()
    notify = lambda *a, **k: _wired.append((a, k))  # noqa: E731
    assert W.run(proc, sched, notify=notify) is True
    assert W.run(proc, sched, notify=notify) is False
    assert len(_wired) == 1


def test_the_lost_bytes_are_kept_before_the_recovery_overwrites_them(_wired):
    """The page forces a `_save`, and that save is what destroys the only copy of what we had.
    Preserve first, or the recovery erases the evidence of the loss it is recovering from."""
    _corrupt(W.STATE_FILE, '{"drift": ["G:only_record_of_this:stale"]')
    proc, sched = _clean()
    W.run(proc, sched, notify=lambda *a, **k: _wired.append((a, k)))
    kept = list(W.STATE_FILE.parent.glob(f"{W.STATE_FILE.name}.unreadable*"))
    assert kept, "the corrupt bytes were overwritten by the save the loss itself triggered"
    assert "only_record_of_this" in kept[0].read_text()


@pytest.mark.parametrize("raw,expected", [
    (None, []),                                    # ABSENT -- the clean baseline, on purpose
    ('{"drift": ["G:x:stale"], "at": "t"}', ["G:x:stale"]),   # READABLE
    ("", None),                                    # a truncated write leaves a zero-length file
    ("{not json", None),
    ("null", None),                                # parses -- which is why an except never saw it
    ("[1, 2, 3]", None),                           # parses, and is not a mapping
    ('{"at": "t"}', None),                         # a mapping with no record in it
    ('{"drift": "abc"}', None),                    # `len()` answers 3 for this one
    ('{"drift": [1, 2]}', None),                   # a list whose ITEMS are not a signature
])
def test_the_whole_prior_partition_answers_and_both_answers_occur(_wired, raw, expected):
    """ONE CONTROL OVER THE PARTITION, not a leg per shape. Nothing here may raise -- this loader
    runs on a five-minute timer inside the watcher that reports everything else being broken -- and
    the parametrisation is written so that a loader which answered `None` to EVERYTHING would fail
    the first two rows, and one that answered `[]` to everything (today's defect) would fail the
    other seven. A guard that refuses everything passes every test of a guard."""
    if raw is not None:
        _corrupt(W.STATE_FILE, raw)
    assert W._load_last() == expected


# ── A WATCHER THAT REPORTED A FORK IT WAS STANDING NEXT TO, FOREVER (2026-09-24) ────────────
# `background/origin_reconcile` was built to run on a cadence and had none: nothing on this box was
# trying to merge. Measured cost -- the publisher refused 51 times over 71.7h, a reader's figures
# went 74.1h stale, and this module's own log carried hours of
# `reconcile DRIFT (9 alarm(s)); unchanged -> log only` while the shared tree sat 38 behind origin
# and 4 ahead. The control below is the one that was missing: a diverged tree that gets REPORTED
# and not ACTED ON is the defect, so the test reds on exactly that.


#: A subject that is NOT this test process's own tree, so "which tree did it ask about" is an
#: observable fact rather than a coincidence. `PROJECT_DIR` can never equal this by accident.
_SUBJECT = Path("/var/tmp/not-the-importing-tree")


def _subject(path=_SUBJECT):
    """The shared-tree resolver, injected. `None` models an unestablishable main worktree."""
    return lambda: path


def _fork(behind, ahead):
    """Records the project it was ASKED ABOUT -- the subject is half of what this leg gets right."""
    calls = []

    def fn(project):
        calls.append(project)
        return (behind, ahead)
    fn.calls = calls
    return fn


def _reconciler(status="RECONCILED", detail="d"):
    """Records its calls, so 'did it act' is a fact about the call and not about the log text."""
    calls = []

    def fn(_project):
        calls.append(_project)
        return {"status": status, "detail": detail}
    fn.calls = calls
    return fn


def test_a_diverged_tree_is_ACTED_ON_and_not_merely_reported():
    """THE OBSERVED DEFECT, and the whole reason this leg exists. 38 behind / 4 ahead is the state
    the shared tree actually sat in while this watcher logged it every five minutes."""
    rec = _reconciler()
    line = W._reconcile_the_fork(state_fn=_fork(38, 4), reconcile_fn=rec,
                                 subject_fn=_subject())
    assert rec.calls, "a diverged tree was reported and NOT acted on -- this is the whole defect"
    assert "38 behind, 4 ahead" in line and "RECONCILED" in line


def test_a_level_tree_is_not_touched_and_says_nothing():
    """THE ANTI-TAUTOLOGY ARM, keyed to the CALL rather than to a word. A leg that reconciled
    unconditionally would pass the test above and would run a git merge every five minutes
    forever; and a level tree has nothing to say, so it must not put a line in the log either."""
    rec = _reconciler()
    assert W._reconcile_the_fork(state_fn=_fork(0, 0), reconcile_fn=rec,
                                 subject_fn=_subject()) is None
    assert rec.calls == [], "a level tree must not be reconciled"


@pytest.mark.parametrize("behind,ahead,should_act", [
    (0, 0, False),      # LEVEL -- the common case
    (38, 4, True),      # DIVERGED -- the observed defect
    (38, 0, True),      # BEHIND only -- origin_reconcile fast-forwards
    (0, 4, True),       # AHEAD only -- origin_reconcile pushes
    (None, 4, False),   # origin unreadable -- never act on a state that was not observed
    (38, None, False),  # the ahead leg unreadable -- same rule, other direction
])
def test_the_whole_fork_partition_answers_and_BOTH_answers_occur(behind, ahead, should_act):
    """ONE CONTROL OVER THE PARTITION, not a leg per shape. Written so that a version which acted
    on EVERYTHING fails the three False rows, and one that acted on NOTHING (today's defect) fails
    the three True rows -- a guard that refuses everything passes every test of a guard.

    The three True rows are separate on purpose: `behind`-only and `ahead`-only are real forks with
    real legs in `origin_reconcile`, and a leg keyed to `behind and ahead` would close the merge
    case while leaving a local-only landing unpushed forever -- which is half of the measured
    incident, not a hypothetical."""
    rec = _reconciler()
    W._reconcile_the_fork(state_fn=_fork(behind, ahead), reconcile_fn=rec,
                          subject_fn=_subject())
    assert bool(rec.calls) is should_act


def test_the_subject_is_the_SHARED_TREE_and_not_the_tree_this_module_was_imported_from():
    """THE DEFECT `origin_reconcile.shared_tree` WAS BUILT FOR, RE-IMPORTABLE THROUGH THIS CALLER.

    `PROJECT_DIR` is `Path(__file__).parent.parent`. The unit sets WorkingDirectory to the shared
    tree, so in production today the two AGREE -- which is what makes this latent rather than
    absent, and is exactly why a control keyed to today's answer would be worthless. This repo
    carries ten linked worktrees and the seats run in them; imported from one, a `PROJECT_DIR`
    subject asks the fork question of a tree nothing publishes from and answers LEVEL while the
    shared tree sits behind with the publisher failing.

    Keyed to the PROPERTY -- both legs must be asked about whatever the resolver returned -- so it
    reds on a revert to `PROJECT_DIR` and equally on any future half-fix that threads the subject
    into one leg and not the other. `_SUBJECT` cannot equal `PROJECT_DIR` by accident."""
    state, rec = _fork(38, 4), _reconciler()
    W._reconcile_the_fork(state_fn=state, reconcile_fn=rec, subject_fn=_subject())
    assert state.calls == [_SUBJECT], (
        f"the fork was READ against {state.calls} rather than the shared tree {_SUBJECT}")
    assert rec.calls == [_SUBJECT], (
        f"the fork was ACTED ON in {rec.calls} rather than the shared tree {_SUBJECT}")
    assert W.PROJECT_DIR != _SUBJECT, "the control is vacuous unless the two can differ"


def test_an_unestablishable_shared_tree_REFUSES_rather_than_defaulting_to_its_own():
    """FAIL CLOSED, AND SAY SO. `shared_tree` returns None when the main worktree cannot be
    established from git. Defaulting to `PROJECT_DIR` there would restore the defect on precisely
    the machines where git could not answer -- so nothing is read and nothing is acted on, and the
    log carries the cause rather than a silent skip that reads like a level tree."""
    state, rec = _fork(38, 4), _reconciler()
    line = W._reconcile_the_fork(state_fn=state, reconcile_fn=rec, subject_fn=_subject(None))
    assert state.calls == [] and rec.calls == [], "an unknown subject must not be acted on"
    assert line and "NOT ATTEMPTED" in line and "shared tree could not be established" in line


def test_the_live_subject_resolver_is_origin_reconciles_shared_tree_not_a_second_copy():
    """WIRED TO THE REAL RESOLVER. The two tests above prove the leg USES its subject_fn; this one
    proves production's default IS `origin_reconcile.shared_tree`, so a local re-derivation of the
    same idea -- the thing that caused this bug -- cannot slip back in unnoticed.

    THE LIVE ARM IS KEYED TO THE PROPERTY AND NOT TO WHERE PYTEST WAS INVOKED, and the first draft
    of it was not. It asserted `shared_tree() == PROJECT_DIR` flat, which is true only in the main
    checkout: run from any of this repo's ten linked worktrees the resolver CORRECTLY returns the
    shared tree while `PROJECT_DIR` is the worktree, so the control read the resolver working as
    the failure and would have reded this module for every lane that runs it from a worktree --
    measured, not predicted: `/var/tmp/se-origin-main-20260925`, 72 passed and this one red.
    The property holds in both places: whatever the resolver returns is a MAIN checkout, which
    carries a `.git` DIRECTORY where a linked worktree carries a `gitdir:` FILE; and where this
    tree is itself that main checkout the two must be the same path."""
    import inspect

    from background import origin_reconcile as orc
    src = inspect.getsource(W._reconcile_the_fork)
    assert "subject_fn or _orc.shared_tree" in src, "the default subject is not shared_tree"
    assert callable(orc.shared_tree)
    if not (W.PROJECT_DIR / ".git").exists():
        pytest.skip("this tree is not a git checkout (a `git archive` extract has no `.git`), so "
                    "the resolver has no subject to resolve and this arm cannot be asked -- the "
                    "source assertions above have already run")
    resolved = orc.shared_tree()
    assert resolved is not None and (resolved / ".git").is_dir(), (
        f"the resolver returned {resolved}, which is not a main checkout -- a main checkout carries "
        "a `.git` directory and a linked worktree a `gitdir:` file")
    if (W.PROJECT_DIR / ".git").is_dir():
        assert resolved == W.PROJECT_DIR, (
            f"this tree {W.PROJECT_DIR} IS a main checkout and the resolver returned {resolved}, so "
            "the two disagree for a reason that is not worktree locality")
    else:
        assert resolved != W.PROJECT_DIR, (
            f"this tree is a LINKED worktree and the resolver returned it ({resolved}) -- that is "
            "the PROJECT_DIR defect back in the resolver itself")


def test_an_unreadable_fork_says_so_rather_than_going_quiet():
    """Fail closed AND say so. 'We could not tell' is a result and belongs in the log; returning
    None here would make an unreadable origin indistinguishable from a level tree."""
    line = W._reconcile_the_fork(state_fn=_fork(None, None), reconcile_fn=_reconciler(),
                                 subject_fn=_subject())
    assert line and "UNREADABLE" in line


@pytest.mark.parametrize("status,settled", [
    ("LEVEL", True), ("RECONCILED", True), ("PUSHED", True), ("FAST_FORWARDED", True),
    ("NOT_ADVANCED", False), ("REFUSED_CONFLICT", False), ("GATE_RUNNING", False),
    ("ERROR", False), ("UNREADABLE", False),
])
def test_a_fork_that_did_not_close_is_logged_as_STILL_OPEN(status, settled):
    """THE STATUS MUST DESCRIBE THE SUBJECT, NOT THE STEPS -- the lesson `origin_reconcile` paid 29
    commits to learn. It reported RECONCILED whenever the merge and push succeeded while the fork
    it was closing grew by one each time. A log line that reads the same for REFUSED_CONFLICT as
    for RECONCILED would re-import that defect into the caller.

    Both answers occur here, so a classifier answering 'settled' to everything fails the five
    False rows and one answering 'STILL OPEN' to everything fails the four True rows."""
    line = W._reconcile_the_fork(state_fn=_fork(38, 4), reconcile_fn=_reconciler(status=status),
                                 subject_fn=_subject())
    assert ("STILL OPEN" in line) is not settled
    assert status in line, "the log must name the status, not just grade it"


def test_the_fork_leg_is_LIVE_in_run_without_the_caller_wiring_it(_wired):
    """Production must not need the caller to pass anything -- otherwise the wiring is inert, which
    is the exact failure class this whole module was built to catch (a control whose only caller is
    stack startup). Mirrors `test_run_falls_through_to_the_live_reconcile_when_no_rows_are_injected`
    for the gap source."""
    seen = []
    proc, sched = _clean()
    W.run(proc, sched, notify=lambda *a, **k: None,
          reconcile_fork=lambda: seen.append(1) or "fork line")
    assert seen == [1]
    assert "fork line" in W.LOG_FILE.read_text(), "the rc must reach the log, not be discarded"


def test_the_slow_fork_merge_runs_AFTER_the_page_not_before(_wired):
    """ORDER IS LOAD-BEARING AND IS THEREFORE CONTROLLED. The merge can run for 25 minutes against
    a five-minute tick; sequenced before the page, a wedged merge silently delays every drift alarm
    this module exists to send. Paging first means a wedged merge costs a late reconcile, never a
    late alarm."""
    order = []
    dp, ds = _drift()
    W.run(dp, ds, notify=lambda *a, **k: order.append("page"),
          reconcile_fork=lambda: order.append("fork") or None)
    assert order == ["page", "fork"], f"the merge must not precede the page; got {order}"


def test_a_failing_fork_reconcile_does_not_stop_the_watcher(_wired):
    """FAIL-SAFE, same as every other rider on this timer. The reconcile is the thing that must not
    stop, and this leg shells out to git and a 25-minute gate -- by far the likeliest to throw."""
    def boom():
        raise RuntimeError("git unavailable")
    dp, ds = _drift()
    paged = W.run(dp, ds, notify=lambda *a, **k: _wired.append(1), reconcile_fork=boom)
    assert paged is True and len(_wired) == 1, "the page must survive a failing fork reconcile"
    assert "fork reconcile failed" in W.LOG_FILE.read_text()


def test_every_settled_status_is_a_real_origin_reconcile_status():
    """KEYED TO THE PROPERTY, NOT TO A LITERAL LIST. A status renamed or dropped in
    `origin_reconcile` must not leave a dead string here that silently never matches again --
    which would grade every closed fork STILL OPEN and would be invisible, because the log would
    still be written and would still look like the mechanism working."""
    from background import origin_reconcile as orc
    for status in W._FORK_SETTLED:
        assert getattr(orc, status, None) == status, (
            f"{status!r} is not a live origin_reconcile status")


def test_the_settled_set_differs_from_mains_exit_code_by_FAST_FORWARDED_on_purpose():
    """THE DIFFERENCE IS DELIBERATE AND IS PINNED SO IT CANNOT BE 'TIDIED' AWAY.

    `origin_reconcile.main` exits 1 on FAST_FORWARDED; this module grades it SETTLED, because a
    fast-forward IS the fork closing -- the shared tree arriving at origin with nothing of ours to
    land. It is also the outcome this leg will produce most often, so grading it STILL OPEN would
    make the log line always-red, and an always-red line is an ignored one.

    A later reader 'aligning' the two would silently re-introduce that. This test reds if the sets
    are made equal in EITHER direction, and it reads main's real success tuple rather than a copy
    of it, so it also reds if main's set changes underneath the claim."""
    import ast
    import inspect

    from background import origin_reconcile as orc
    tree = ast.parse(inspect.getsource(orc.main).strip())
    compares = [n for n in ast.walk(tree)
                if isinstance(n, ast.Compare) and isinstance(n.ops[0], ast.In)]
    mains = {e.id for c in compares for e in ast.walk(c.comparators[0])
             if isinstance(e, ast.Name)}
    assert mains == {"LEVEL", "RECONCILED", "PUSHED"}, (
        f"main's exit-0 set changed to {mains}; re-judge the FAST_FORWARDED split deliberately")
    assert set(W._FORK_SETTLED) - mains == {"FAST_FORWARDED"}
    assert not mains - set(W._FORK_SETTLED), "every exit-0 status must also grade as settled here"


def test_a_failing_drift_check_does_not_stop_the_reconcile(monkeypatch):
    """FAIL-SAFE: this rides the reconcile timer, and the reconcile is the thing that must not
    stop. An exception here is logged and swallowed."""
    def boom():
        raise RuntimeError("git unavailable")
    monkeypatch.setattr(W, "_drift_report", lambda *a, **k: boom())
    paged = W.run(proc_results=[], sched_results=[], gap_results=[], notify=lambda *a, **k: None)
    assert paged is False


# ── THE TWO FAIL-SAFES ON THIS TIMER THAT COULD NOT FAIL (found 2026-09-24) ─────────────────
# Found by mutating this module while adding the fork leg, not by reading it. `run` carries FOUR
# `except Exception -> _log and continue` riders; narrowing the except to a type nothing raises
# left the whole file GREEN for the seat-claim sweep and the seat-continuity sweep. Only the
# boot-sha rider had a control. So two of the four could have been deleted, or could have started
# propagating, and the suite would have said the mechanism was working -- on the five-minute timer
# whose entire job is reporting that other things are broken. Same shape as the finding that put
# the fork leg here: a control that only fires when it cannot.


@pytest.mark.parametrize("attr,marker", [
    ("sweep", "seat claims released"),
    ("_seat_continuity_sweep", "handoff filed"),
])
def test_a_failing_seat_sweep_does_not_stop_the_reconcile(_wired, monkeypatch, attr, marker):
    """Neither sweep may take the tick down, and the failure must be VISIBLE rather than silent --
    a swallowed exception that logs nothing is indistinguishable from a sweep that found nothing.

    Parametrised over both riders because they are the same defect twice, and a leg-per-rider would
    have let the next one added arrive uncontrolled exactly as these two did."""
    def boom(*a, **k):
        raise RuntimeError("the sweep exploded")
    if attr == "sweep":
        monkeypatch.setattr(W._seat, "sweep", boom)
    else:
        import background.seat_continuity as sc
        monkeypatch.setattr(sc, "sweep", boom)

    proc, sched = _clean()
    assert W.run(proc, sched, notify=lambda *a, **k: _wired.append(1)) is False
    log = W.LOG_FILE.read_text()
    assert "failed (reconcile continues)" in log, "the swallowed failure left no trace in the log"
    assert marker not in log, "a failed sweep must not report as a successful one"
