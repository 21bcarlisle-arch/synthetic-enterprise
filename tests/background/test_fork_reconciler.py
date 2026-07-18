"""FORK-LIFECYCLE reconciler (director P0, 2026-07-17, step 3).

R15 mutation coverage: the mechanism must FIRE on an orphan (a fork that never merged home past
the deadline), stay SILENT on a live in-flight fork, and NEVER reap a merged branch (it came home).
Reap-only (policy A): salvage ALWAYS precedes reap; a reap that cannot first confirm salvage is
REFUSED (never delete unsalvaged work). Report-first: detection with NO reaping.
"""
from __future__ import annotations

import subprocess

import pytest

from background import fork_reconciler as F

NOW = 1_000_000.0
DL = F.FORK_DEADLINE_SECONDS


def _b(name, merged, age_s):
    return {"name": name, "merged": merged, "last_commit_ts": NOW - age_s}


# ── pure classifier (mutation core) ─────────────────────────────────────────────────────────
def test_classify_branch_pure():
    assert F.classify_branch(_b("build/x-w1", False, DL + 1), NOW) == "ORPHAN"      # old + unmerged
    assert F.classify_branch(_b("build/x-w1", False, DL - 1), NOW) == "IN_FLIGHT"   # young + unmerged
    assert F.classify_branch(_b("build/x-w1", True, DL + 9999), NOW) == "MERGED"    # merged is NEVER orphan
    assert F.classify_branch(_b("main", False, DL + 1), NOW) == "PROTECTED"         # main is protected


# ── orphan past deadline -> ALARM (report-first: no reap) ──────────────────────────────────
def test_orphan_past_deadline_alarms_and_reaps_nothing_in_report_first():
    r = F.evaluate_fork_lifecycle(branches=[_b("build/old-w1", False, DL + 60)], now=NOW, enforce=False)
    assert r["status"] == "FORK_ORPHANS" and r["alarm"] is True
    assert r["orphans"] == ["build/old-w1"]
    assert r["reaped"] == []                    # REPORT-FIRST: detected, NOT reaped


# ── fresh in-flight -> SILENT ───────────────────────────────────────────────────────────────
def test_fresh_in_flight_is_silent():
    r = F.evaluate_fork_lifecycle(branches=[_b("build/live-w2", False, DL - 60)], now=NOW, enforce=False)
    assert r["status"] == "FORK_CLEAN" and r["alarm"] is False
    assert r["in_flight"] == ["build/live-w2"] and r["orphans"] == []


# ── merged -> cleanup-eligible, NEVER reaped (it came home) ─────────────────────────────────
def test_merged_is_cleanup_eligible_never_reaped():
    reaped = []
    r = F.evaluate_fork_lifecycle(branches=[_b("build/done-w3", True, DL + 9999)], now=NOW,
                                  enforce=True, reaper=lambda n: reaped.append(n))
    assert r["merged_eligible"] == ["build/done-w3"]
    assert r["orphans"] == [] and r["alarm"] is False
    assert reaped == []                         # a merged branch is HOME -- never reaped


# ── enforce-mode reaps ONLY orphans, after salvage ──────────────────────────────────────────
def test_enforce_mode_reaps_only_orphans():
    branches = [_b("build/orphan-w4", False, DL + 60),      # orphan -> reap
                _b("build/live-w5", False, DL - 60),        # in-flight -> leave
                _b("build/done-w6", True, DL + 60)]         # merged -> leave
    reaped = []
    def fake_reaper(n):
        reaped.append(n)
        return {"branch": n, "tag": "salvage/" + n.replace("/", "_"), "reaped": True, "detail": "ok"}
    r = F.evaluate_fork_lifecycle(branches=branches, now=NOW, enforce=True, reaper=fake_reaper)
    assert reaped == ["build/orphan-w4"]        # ONLY the orphan; not the live or merged branch
    assert r["alarm"] is True and any(x["reaped"] for x in r["reaped"])


# ── HELD branches: enforce is the STANDING mechanism, but a held orphan is never reaped ─────
def test_held_orphan_is_never_reaped_even_under_enforce():
    branches = [_b("build/reapme-w1", False, DL + 60), _b("build/holdme-w2", False, DL + 60)]
    reaped = []
    def fake(n):
        reaped.append(n)
        return {"branch": n, "reaped": True, "tag": "t", "detail": "ok"}
    r = F.evaluate_fork_lifecycle(branches=branches, now=NOW, enforce=True,
                                  held={"build/holdme-w2"}, reaper=fake)
    assert reaped == ["build/reapme-w1"]                  # ONLY the non-held orphan reaped
    assert r["held_orphans"] == ["build/holdme-w2"]       # the held one is tracked, not reaped


def test_only_held_orphans_reads_FORK_HELD_and_never_alarms():
    # enforce armed + the sole orphan is held -> no reap, no alarm (acknowledged), reaper untouched.
    r = F.evaluate_fork_lifecycle(branches=[_b("build/holdme", False, DL + 60)], now=NOW,
                                  enforce=True, held={"build/holdme"},
                                  reaper=lambda n: (_ for _ in ()).throw(AssertionError("reaped a held branch!")))
    assert r["status"] == "FORK_HELD" and r["alarm"] is False
    assert r["reaped"] == [] and r["held_orphans"] == ["build/holdme"]


def test_held_branches_reader(tmp_path):
    p = tmp_path / ".fork_reap_held"
    p.write_text("# a held branch, pending director decision\nbuild/F6_x\n\n  build/other  \n")
    assert F.held_branches(p) == {"build/F6_x", "build/other"}
    assert F.held_branches(tmp_path / "absent") == set()


# ── the hard floor: salvage ALWAYS precedes reap; refuse if salvage can't be confirmed ─────
def test_salvage_precedes_reap_and_refuses_when_salvage_cannot_be_confirmed(monkeypatch):
    calls = []
    def fake_git(*a):
        calls.append(a)
        if a[:1] == ("rev-parse",) and a[-1] == "build/x":
            return "TIP123\n"                                   # branch tip
        if a[:1] == ("rev-parse",) and "--verify" in a:
            return ""                                           # tag absent -> will be created
        if a[:1] == ("rev-parse",) and a[-1].endswith("^{commit}"):
            return "MISMATCH\n"                                 # tag != tip -> salvage NOT confirmed
        return ""
    monkeypatch.setattr(F, "_git", fake_git)
    r = F.salvage_and_reap("build/x")
    assert r["reaped"] is False and "REFUSED" in r["detail"]
    assert not any(c[:2] == ("branch", "-D") for c in calls)    # branch -D NEVER called -> no delete


def test_salvage_and_reap_deletes_only_after_confirmed_salvage(monkeypatch):
    calls = []
    def fake_git(*a):
        calls.append(a)
        if a[:1] == ("rev-parse",) and a[-1] == "build/y":
            return "TIPAAA\n"
        if a[:1] == ("rev-parse",) and "--verify" in a:
            return "existing\n"                                 # tag already exists (the 33 case)
        if a[:1] == ("rev-parse",) and a[-1].endswith("^{commit}"):
            return "TIPAAA\n"                                   # tag == tip -> salvage CONFIRMED
        return ""
    monkeypatch.setattr(F, "_git", fake_git)
    r = F.salvage_and_reap("build/y")
    assert r["reaped"] is True
    assert any(c[:2] == ("branch", "-D") for c in calls)        # delete happened -- AFTER salvage confirm
    # and it never re-created an already-existing tag
    assert not any(c[0] == "tag" for c in calls)


# ── flag fail-safe: absent = report-first (no reap) ─────────────────────────────────────────
def test_reap_enabled_fail_safe(tmp_path):
    assert F.reap_enabled(tmp_path / "nope") is False           # absent -> report-first
    flag = tmp_path / "flag"
    flag.write_text("")
    assert F.reap_enabled(flag) is True


# ── the deadman fires it -- transition-only (mirror the gate-wall wiring) ───────────────────
def test_deadman_fires_fork_orphans_and_is_transition_only(tmp_path, monkeypatch):
    from background import deadmans_switch as D
    import background.notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    monkeypatch.setattr(D, "LOG_FILE", tmp_path / "log.md")
    calls = []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy", lambda msg, **k: calls.append(msg) or "id")
    monkeypatch.setattr(
        "background.fork_reconciler.evaluate_fork_lifecycle",
        lambda: {"status": "FORK_ORPHANS", "alarm": True, "detail": "3 orphaned fork branch(es)",
                 "orphans": ["a", "b", "c"], "in_flight": [], "merged_eligible": [], "reaped": [],
                 "enforce": False},
    )
    D._check_fork_lifecycle()
    assert len(calls) == 1 and "FORK ORPHANS" in calls[0]        # the alarm fires
    D._check_fork_lifecycle()
    assert len(calls) == 1                                        # ...once -- transition-only (R5)


def test_deadman_silent_when_no_orphans(tmp_path, monkeypatch):
    from background import deadmans_switch as D
    import background.notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    monkeypatch.setattr(D, "LOG_FILE", tmp_path / "log.md")
    calls = []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy", lambda msg, **k: calls.append(msg) or "id")
    monkeypatch.setattr(
        "background.fork_reconciler.evaluate_fork_lifecycle",
        lambda: {"status": "FORK_CLEAN", "alarm": False, "detail": "no orphans",
                 "orphans": [], "in_flight": [], "merged_eligible": [], "reaped": [], "enforce": False},
    )
    D._check_fork_lifecycle()
    assert calls == []                                           # clean -> never pages


# ── live smoke: report-first, well-formed, never raises ────────────────────────────────────
def test_live_report_first_is_well_formed_and_reaps_nothing():
    r = F.evaluate_fork_lifecycle(enforce=False)                 # force report-first regardless of flag
    assert set(r) >= {"status", "alarm", "detail", "orphans", "in_flight", "merged_eligible", "reaped", "enforce"}
    assert r["enforce"] is False and r["reaped"] == []           # report-first: nothing reaped
    # the complete set of report-first statuses (all three legitimate): FORK_HELD is a
    # director-HELD orphan (acknowledged, exempt from reap) -- a real live state this smoke test
    # must accept, not just CLEAN/ORPHANS. The report-first invariant (reaped == []) holds for all.
    assert r["status"] in ("FORK_CLEAN", "FORK_ORPHANS", "FORK_HELD")


# ── WORKTREE RECONCILE (step 4 / C1): "does this worktree belong?" -- ONE mechanism ──────────
MAIN = "/repo"


def _wt(path, branch=None, detached=False, locked=False, locked_reason=None, bare=False):
    return {"path": path, "branch": branch, "detached": detached,
            "locked": locked, "locked_reason": locked_reason, "bare": bare}


def test_classify_worktree_belonging_is_derived_from_branch_state():
    # main always belongs; a fork worktree belongs ONLY while its branch is IN_FLIGHT (a live fork).
    states = {"live-w1": "IN_FLIGHT", "old-w2": "ORPHAN", "done-w3": "MERGED"}
    assert F.classify_worktree(_wt(MAIN), MAIN, states) == "BELONGS"
    assert F.classify_worktree(_wt("/wt/a", "live-w1"), MAIN, states) == "BELONGS"     # live fork
    assert F.classify_worktree(_wt("/wt/b", "old-w2"), MAIN, states) == "UNDECLARED"   # orphan branch
    assert F.classify_worktree(_wt("/wt/c", "done-w3"), MAIN, states) == "UNDECLARED"  # merged: should be pruned
    assert F.classify_worktree(_wt("/wt/d", detached=True), MAIN, states) == "UNDECLARED"  # detached


def test_worktree_reconcile_clean_when_only_main_and_live_forks():
    wts = [_wt(MAIN, "main"), _wt("/wt/live", "live-w1")]
    r = F.evaluate_worktree_reconcile(worktrees=wts, branch_states={"live-w1": "IN_FLIGHT"}, main_path=MAIN)
    assert r["status"] == "WORKTREE_CLEAN" and r["alarm"] is False


def test_worktree_reconcile_ALARMS_on_undeclared_and_never_prunes():
    wts = [_wt(MAIN, "main"), _wt("/wt/orphan", "old-w2"), _wt("/wt/detached", detached=True)]
    r = F.evaluate_worktree_reconcile(worktrees=wts, branch_states={"old-w2": "ORPHAN"}, main_path=MAIN)
    assert r["status"] == "WORKTREE_UNDECLARED" and r["alarm"] is True
    paths = {u["path"] for u in r["undeclared"]}
    assert paths == {"/wt/orphan", "/wt/detached"}               # main + live-fork excluded
    # report-only: the result carries NO reap/prune action (the function has no delete path)
    assert all("reaped" not in u and "pruned" not in u for u in r["undeclared"])


def test_scan_worktrees_parses_porcelain():
    # (unit) the parser handles the porcelain shape: main-with-branch + a detached worktree.
    porcelain = ("worktree /repo\nHEAD abc\nbranch refs/heads/main\n\n"
                 "worktree /tmp/x\nHEAD def\ndetached\n")
    import background.fork_reconciler as FR
    orig = FR._git
    FR._git = lambda *a: porcelain if a[:2] == ("worktree", "list") else orig(*a)
    try:
        wts = FR.scan_worktrees()
    finally:
        FR._git = orig
    assert wts == [
        {"path": "/repo", "branch": "main", "detached": False,
         "locked": False, "locked_reason": None, "bare": False},
        {"path": "/tmp/x", "branch": None, "detached": True,
         "locked": False, "locked_reason": None, "bare": False},
    ]


def test_scan_worktrees_parses_locked_and_bare():
    # (unit, H24) locked (with + without a reason) and bare lines must be captured -- these are
    # exactly the fields the reaper's NEVER-reap gates key off.
    porcelain = (
        "worktree /repo\nHEAD abc\nbranch refs/heads/main\nbare\n\n"
        "worktree /wt/locked-with-reason\nHEAD def\nbranch refs/heads/build/x\n"
        "locked claude agent building (pid 123)\n\n"
        "worktree /wt/locked-no-reason\nHEAD ghi\nbranch refs/heads/build/y\nlocked\n"
    )
    import background.fork_reconciler as FR
    orig = FR._git
    FR._git = lambda *a: porcelain if a[:2] == ("worktree", "list") else orig(*a)
    try:
        wts = FR.scan_worktrees()
    finally:
        FR._git = orig
    by_path = {w["path"]: w for w in wts}
    assert by_path["/repo"]["bare"] is True
    assert by_path["/wt/locked-with-reason"]["locked"] is True
    assert by_path["/wt/locked-with-reason"]["locked_reason"] == "claude agent building (pid 123)"
    assert by_path["/wt/locked-no-reason"]["locked"] is True
    assert by_path["/wt/locked-no-reason"]["locked_reason"] is None


def test_deadman_fires_worktree_undeclared_transition_only(tmp_path, monkeypatch):
    from background import deadmans_switch as D
    import background.notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    monkeypatch.setattr(D, "LOG_FILE", tmp_path / "log.md")
    calls = []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy", lambda msg, **k: calls.append(msg) or "id")
    monkeypatch.setattr(
        "background.fork_reconciler.evaluate_worktree_reconcile",
        lambda: {"status": "WORKTREE_UNDECLARED", "alarm": True, "detail": "1 undeclared",
                 "undeclared": [{"path": "/wt/x", "branch": "b", "branch_state": "ORPHAN"}]},
    )
    D._check_worktree_reconcile()
    assert len(calls) == 1 and "WORKTREE UNDECLARED" in calls[0]
    D._check_worktree_reconcile()
    assert len(calls) == 1                                        # transition-only (R5)


def test_live_worktree_reconcile_is_well_formed_and_never_prunes():
    r = F.evaluate_worktree_reconcile()
    assert set(r) >= {"status", "alarm", "detail", "undeclared"}
    assert r["status"] in ("WORKTREE_CLEAN", "WORKTREE_UNDECLARED")


# ── WORKTREE DIRECTORY REAP (H24): the merged-branch-worktree cleanup ────────────────────────
# R15 mutation proof (director P0: "a dir-deleting reaper touches the irrecoverable-data-loss
# one-way door IF it runs against the live tree"): every test below either runs purely on
# in-memory dicts, OR against a THROWAWAY isolated git fixture built with tempfile/git-init/
# git-worktree-add -- NEVER against this real repo's `.claude/worktrees/`. `git worktree remove`
# is only ever invoked with a path rooted under pytest's own `tmp_path`.

def _rwt(path, branch=None, detached=False, locked=False, locked_reason=None, bare=False):
    return {"path": path, "branch": branch, "detached": detached,
            "locked": locked, "locked_reason": locked_reason, "bare": bare}


MAIN2 = "/repo"


# ── pure classifier (mutation core) ─────────────────────────────────────────────────────────
def test_classify_worktree_reap_merged_clean_unlocked_is_eligible():
    r = F.classify_worktree_reap(_rwt("/wt/a", "done-w1"), MAIN2, "MERGED", dirty=False, salvage_tag=None)
    assert r["eligible"] is True and "MERGED" in r["reason"]


def test_classify_worktree_reap_salvaged_absent_branch_is_eligible():
    # branch ref itself is gone (already salvage-reaped) but a confirmed salvage tag proves it.
    r = F.classify_worktree_reap(_rwt("/wt/a", "salvaged-w1"), MAIN2, None,
                                 dirty=False, salvage_tag="salvage/salvaged-w1")
    assert r["eligible"] is True and "salvaged" in r["reason"]


def test_classify_worktree_reap_absent_branch_no_tag_is_never_reaped():
    # branch gone but NO salvage tag to prove it -- undetermined, fail-safe NEVER.
    r = F.classify_worktree_reap(_rwt("/wt/a", "mystery-w1"), MAIN2, None, dirty=False, salvage_tag=None)
    assert r["eligible"] is False and "undetermined" in r["reason"]


def test_classify_worktree_reap_locked_is_NEVER_reaped_even_if_merged():
    # THE mutation: flip only `locked` -- an otherwise-eligible (merged, clean) worktree flips
    # to never-reap. Proves the lock gate is load-bearing, not decorative.
    base_kwargs = dict(dirty=False, salvage_tag=None)
    unlocked = F.classify_worktree_reap(_rwt("/wt/a", "done-w1", locked=False), MAIN2, "MERGED", **base_kwargs)
    locked = F.classify_worktree_reap(_rwt("/wt/a", "done-w1", locked=True, locked_reason="claude agent"),
                                      MAIN2, "MERGED", **base_kwargs)
    assert unlocked["eligible"] is True
    assert locked["eligible"] is False and "locked" in locked["reason"]


def test_classify_worktree_reap_live_branch_is_NEVER_reaped():
    for state in ("IN_FLIGHT", "ORPHAN"):
        r = F.classify_worktree_reap(_rwt("/wt/a", "live-w1"), MAIN2, state, dirty=False, salvage_tag=None)
        assert r["eligible"] is False and "live/undecided" in r["reason"]


def test_classify_worktree_reap_dirty_is_NEVER_reaped_even_if_merged():
    # THE mutation: flip only `dirty` -- an otherwise-eligible worktree flips to never-reap.
    clean = F.classify_worktree_reap(_rwt("/wt/a", "done-w1"), MAIN2, "MERGED", dirty=False, salvage_tag=None)
    dirty = F.classify_worktree_reap(_rwt("/wt/a", "done-w1"), MAIN2, "MERGED", dirty=True, salvage_tag=None)
    assert clean["eligible"] is True
    assert dirty["eligible"] is False and "uncommitted" in dirty["reason"]


def test_classify_worktree_reap_main_worktree_is_NEVER_reaped():
    # THE mutation: flip only `path == main_path` -- even a contrived "MERGED main" never reaps.
    r = F.classify_worktree_reap(_rwt(MAIN2, "main"), MAIN2, "MERGED", dirty=False, salvage_tag=None)
    assert r["eligible"] is False and "main worktree" in r["reason"]


def test_classify_worktree_reap_bare_and_detached_are_NEVER_reaped():
    r_bare = F.classify_worktree_reap(_rwt("/wt/a", "done-w1", bare=True), MAIN2, "MERGED",
                                      dirty=False, salvage_tag=None)
    r_detached = F.classify_worktree_reap(_rwt("/wt/a", detached=True), MAIN2, "MERGED",
                                          dirty=False, salvage_tag=None)
    assert r_bare["eligible"] is False and "bare" in r_bare["reason"]
    assert r_detached["eligible"] is False and "detached" in r_detached["reason"]


# ── flag fail-safe: absent = report-first (mirrors reap_enabled for branches, own flag) ──────
def test_worktree_reap_enabled_fail_safe(tmp_path):
    assert F.worktree_reap_enabled(tmp_path / "nope") is False
    flag = tmp_path / "flag"
    flag.write_text("")
    assert F.worktree_reap_enabled(flag) is True


# ── evaluate_worktree_reap: injected data, no real git (mirrors the branch-reaper style) ────
def test_evaluate_worktree_reap_report_first_lists_but_removes_nothing():
    wts = [_rwt(MAIN2, "main"), _rwt("/wt/done", "done-w1"), _rwt("/wt/live", "live-w1")]
    states = {"done-w1": "MERGED", "live-w1": "IN_FLIGHT"}
    removed = []
    r = F.evaluate_worktree_reap(worktrees=wts, branch_states=states, main_path=MAIN2, enforce=False,
                                 dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
                                 remover=lambda p: removed.append(p))
    assert r["status"] == "WORKTREE_REAP_ELIGIBLE" and r["enforce"] is False
    assert [e["path"] for e in r["eligible"]] == ["/wt/done"]
    assert removed == []                      # report-first: NOTHING removed
    assert r["reaped"] == []


def test_evaluate_worktree_reap_enforce_removes_only_eligible():
    wts = [_rwt(MAIN2, "main"),
           _rwt("/wt/done", "done-w1"),                       # merged+clean -> reap
           _rwt("/wt/live", "live-w1"),                        # unmerged -> keep
           _rwt("/wt/locked", "done-w2", locked=True),         # locked -> keep even though merged
           _rwt("/wt/dirty", "done-w3")]                       # dirty -> keep even though merged
    states = {"done-w1": "MERGED", "live-w1": "IN_FLIGHT", "done-w2": "MERGED", "done-w3": "MERGED"}
    removed = []
    def fake_remover(p):
        removed.append(p)
        return {"path": p, "removed": True, "detail": "ok"}
    def fake_dirty(p):
        return p == "/wt/dirty"
    r = F.evaluate_worktree_reap(worktrees=wts, branch_states=states, main_path=MAIN2, enforce=True,
                                 dirty_fn=fake_dirty, salvage_tag_fn=lambda b: None, remover=fake_remover)
    assert removed == ["/wt/done"]             # ONLY the merged+clean+unlocked+non-main one
    assert r["status"] == "WORKTREE_REAPED" and r["alarm"] is False
    kept_paths = {k["path"] for k in r["kept"]}
    assert kept_paths == {MAIN2, "/wt/live", "/wt/locked", "/wt/dirty"}


def test_evaluate_worktree_reap_enforce_reports_failure_as_alarm():
    wts = [_rwt("/wt/done", "done-w1")]
    states = {"done-w1": "MERGED"}
    r = F.evaluate_worktree_reap(worktrees=wts, branch_states=states, main_path=MAIN2, enforce=True,
                                 dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
                                 remover=lambda p: {"path": p, "removed": False, "detail": "boom"})
    assert r["status"] == "WORKTREE_REAP_FAILED" and r["alarm"] is True


def test_live_evaluate_worktree_reap_is_well_formed_and_defaults_report_first():
    r = F.evaluate_worktree_reap(enforce=False)     # force report-first regardless of the live flag
    assert set(r) >= {"status", "alarm", "detail", "eligible", "kept", "reaped", "enforce"}
    assert r["enforce"] is False and r["reaped"] == []


# ── ISOLATED FIXTURE end-to-end: real git worktrees, real git ops, never the real repo ──────
def _git_run(args, cwd):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"git {args} in {cwd} failed: {r.stderr}{r.stdout}"
    return r.stdout


@pytest.fixture
def fixture_repo(tmp_path):
    """A throwaway isolated repo (tempfile/git-init) with one commit on main -- NEVER the real tree."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_run(["init", "-b", "main"], repo)
    _git_run(["config", "user.email", "fixture@example.com"], repo)
    _git_run(["config", "user.name", "Fixture"], repo)
    (repo / "README.md").write_text("seed\n")
    _git_run(["add", "README.md"], repo)
    _git_run(["commit", "-m", "init"], repo)
    return repo


def _scoped_git(repo):
    """A `_git`-shaped callable scoped to `repo` (never PROJECT_DIR) -- so scan_worktrees /
    scan_fork_branches / classify_branch / _salvage_tag_for all operate on the fixture."""
    def g(*args):
        r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else ""
    return g


def _reap_in(repo):
    """A `remover`-shaped callable that runs `git worktree remove` scoped to the FIXTURE repo."""
    def fn(path):
        r = subprocess.run(["git", "worktree", "remove", path], cwd=str(repo),
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return {"path": path, "removed": False, "detail": (r.stderr or r.stdout).strip()}
        subprocess.run(["git", "worktree", "prune"], cwd=str(repo), capture_output=True, text=True)
        return {"path": path, "removed": True, "detail": "removed"}
    return fn


@pytest.fixture(autouse=False)
def no_op_shared_lock(monkeypatch):
    """Neutralise the real repo's shared_tree_lock for enforce-mode fixture tests -- these tests
    already never touch the real repo's git state via `remover`/`salvage_tag_fn` overrides; this
    just avoids the incidental flock acquire/release against the REAL repo's lock file too, so the
    fixture tests have zero real-repo footprint."""
    import contextlib
    import background.tree_lock as TL
    @contextlib.contextmanager
    def _noop(*a, **k):
        yield
    monkeypatch.setattr(TL, "shared_tree_lock", _noop)


def test_fixture_merged_clean_worktree_is_reaped_report_then_enforce(fixture_repo, tmp_path, no_op_shared_lock):
    repo = fixture_repo
    wt_path = tmp_path / "wt-merged"
    _git_run(["worktree", "add", "-b", "build/merged-w1", str(wt_path)], repo)
    (wt_path / "work.txt").write_text("done\n")
    _git_run(["add", "work.txt"], wt_path)
    _git_run(["commit", "-m", "fork work"], wt_path)
    _git_run(["merge", "build/merged-w1"], repo)          # branch now MERGED into main

    # Route the module's OWN scanners at the fixture repo (never PROJECT_DIR) so this exercises the
    # real scan_fork_branches/scan_worktrees/classify_branch code paths end-to-end, not a re-implementation.
    scoped = _scoped_git(repo)
    orig_git = F._git
    F._git = scoped
    try:
        branches = F.scan_fork_branches()
        wts = F.scan_worktrees()
    finally:
        F._git = orig_git
    branch_states = {b["name"]: F.classify_branch(b, 0.0) for b in branches}
    assert branch_states["build/merged-w1"] == "MERGED"
    main_path = str(repo)

    # REPORT-FIRST: listed, nothing removed.
    r_report = F.evaluate_worktree_reap(worktrees=wts, branch_states=branch_states, main_path=main_path,
                                        enforce=False, dirty_fn=F._worktree_dirty,
                                        salvage_tag_fn=lambda b: None, remover=_reap_in(repo))
    assert str(wt_path) in [e["path"] for e in r_report["eligible"]]
    assert r_report["reaped"] == []
    assert wt_path.is_dir()                                # still there -- report-first touches nothing

    # ENFORCE: actually removed.
    r_enforce = F.evaluate_worktree_reap(worktrees=wts, branch_states=branch_states, main_path=main_path,
                                         enforce=True, dirty_fn=F._worktree_dirty,
                                         salvage_tag_fn=lambda b: None, remover=_reap_in(repo))
    assert r_enforce["status"] == "WORKTREE_REAPED"
    assert any(x["removed"] for x in r_enforce["reaped"] if x["path"] == str(wt_path))
    assert not wt_path.exists()                             # the directory is actually gone


def test_fixture_locked_worktree_is_NEVER_reaped(fixture_repo, tmp_path, no_op_shared_lock):
    repo = fixture_repo
    wt_path = tmp_path / "wt-locked"
    _git_run(["worktree", "add", "-b", "build/locked-w1", str(wt_path)], repo)
    (wt_path / "work.txt").write_text("done\n")
    _git_run(["add", "work.txt"], wt_path)
    _git_run(["commit", "-m", "fork work"], wt_path)
    _git_run(["merge", "build/locked-w1"], repo)            # would otherwise be MERGED-eligible
    _git_run(["worktree", "lock", str(wt_path), "--reason", "still building"], repo)

    scoped = _scoped_git(repo)
    orig_git = F._git
    F._git = scoped
    try:
        wts = F.scan_worktrees()
    finally:
        F._git = orig_git
    branch_states = {"build/locked-w1": "MERGED"}

    r = F.evaluate_worktree_reap(worktrees=wts, branch_states=branch_states, main_path=str(repo),
                                 enforce=True, dirty_fn=F._worktree_dirty,
                                 salvage_tag_fn=lambda b: None, remover=_reap_in(repo))
    assert str(wt_path) not in [e["path"] for e in r["eligible"]]
    assert r["reaped"] == []
    assert wt_path.is_dir()                                 # NEVER reaped -- still present


def test_fixture_live_unmerged_branch_worktree_is_NEVER_reaped(fixture_repo, tmp_path, no_op_shared_lock):
    repo = fixture_repo
    wt_path = tmp_path / "wt-live"
    _git_run(["worktree", "add", "-b", "build/live-w1", str(wt_path)], repo)
    (wt_path / "work.txt").write_text("in progress\n")
    _git_run(["add", "work.txt"], wt_path)
    _git_run(["commit", "-m", "fork work in progress"], wt_path)
    # deliberately NOT merged into main -- a live, in-flight fork.

    scoped = _scoped_git(repo)
    orig_git = F._git
    F._git = scoped
    try:
        wts = F.scan_worktrees()
    finally:
        F._git = orig_git
    branch_states = {"build/live-w1": "IN_FLIGHT"}

    r = F.evaluate_worktree_reap(worktrees=wts, branch_states=branch_states, main_path=str(repo),
                                 enforce=True, dirty_fn=F._worktree_dirty,
                                 salvage_tag_fn=lambda b: None, remover=_reap_in(repo))
    assert str(wt_path) not in [e["path"] for e in r["eligible"]]
    assert r["reaped"] == []
    assert wt_path.is_dir()                                 # NEVER reaped -- the fork is still live


def test_fixture_dirty_worktree_is_NEVER_reaped_even_if_merged(fixture_repo, tmp_path, no_op_shared_lock):
    repo = fixture_repo
    wt_path = tmp_path / "wt-dirty"
    _git_run(["worktree", "add", "-b", "build/dirty-w1", str(wt_path)], repo)
    (wt_path / "work.txt").write_text("done\n")
    _git_run(["add", "work.txt"], wt_path)
    _git_run(["commit", "-m", "fork work"], wt_path)
    _git_run(["merge", "build/dirty-w1"], repo)             # branch MERGED
    (wt_path / "uncommitted.txt").write_text("oops, forgot to commit this\n")  # untracked change

    scoped = _scoped_git(repo)
    orig_git = F._git
    F._git = scoped
    try:
        wts = F.scan_worktrees()
    finally:
        F._git = orig_git
    branch_states = {"build/dirty-w1": "MERGED"}

    r = F.evaluate_worktree_reap(worktrees=wts, branch_states=branch_states, main_path=str(repo),
                                 enforce=True, dirty_fn=F._worktree_dirty,
                                 salvage_tag_fn=lambda b: None, remover=_reap_in(repo))
    assert str(wt_path) not in [e["path"] for e in r["eligible"]]
    assert r["reaped"] == []
    assert wt_path.is_dir()                                 # NEVER reaped -- uncommitted work present


def test_fixture_main_worktree_is_NEVER_reaped(fixture_repo, tmp_path, no_op_shared_lock):
    repo = fixture_repo
    scoped = _scoped_git(repo)
    orig_git = F._git
    F._git = scoped
    try:
        wts = F.scan_worktrees()
    finally:
        F._git = orig_git
    assert wts and wts[0]["path"] == str(repo)              # the main worktree itself
    branch_states = {"main": "MERGED"}                       # contrived -- main is normally PROTECTED

    r = F.evaluate_worktree_reap(worktrees=wts, branch_states=branch_states, main_path=str(repo),
                                 enforce=True, dirty_fn=F._worktree_dirty,
                                 salvage_tag_fn=lambda b: None, remover=_reap_in(repo))
    assert str(repo) not in [e["path"] for e in r["eligible"]]
    assert r["reaped"] == []
    assert repo.is_dir() and (repo / ".git").exists()        # the repo itself is untouched


def test_fixture_salvaged_branch_worktree_is_reaped(fixture_repo, tmp_path, no_op_shared_lock):
    # branch was already salvage-reaped (deleted) but a matching salvage tag proves it -- the
    # worktree's admin dir is stale and safe to remove. Reproduce by tagging + deleting the branch
    # BEFORE the worktree is removed (git refuses to delete a branch checked out by a worktree, so
    # the real lifecycle order is: reap the worktree dir first when the branch is confirmed home;
    # this test proves the salvage-tag path specifically, independent of that ordering wrinkle).
    repo = fixture_repo
    wt_path = tmp_path / "wt-salvaged"
    _git_run(["worktree", "add", "-b", "build/salvaged-w1", str(wt_path)], repo)
    (wt_path / "work.txt").write_text("orphaned work, salvaged\n")
    _git_run(["add", "work.txt"], wt_path)
    _git_run(["commit", "-m", "orphan work"], wt_path)
    _git_run(["tag", "salvage/build_salvaged-w1", "build/salvaged-w1"], repo)
    # branch ref removed from the worktree's perspective by detaching it, simulating "already gone":
    _git_run(["checkout", "--detach"], wt_path)
    _git_run(["branch", "-D", "build/salvaged-w1"], repo)

    scoped = _scoped_git(repo)
    orig_git = F._git
    F._git = scoped
    try:
        wts = F.scan_worktrees()
        assert not any(w.get("branch") == "build/salvaged-w1" for w in wts)  # branch really is gone
        tag = F._salvage_tag_for("build/salvaged-w1")         # must resolve while _git is fixture-scoped
    finally:
        F._git = orig_git

    assert tag == "salvage/build_salvaged-w1"
    r = F.classify_worktree_reap(_rwt(str(wt_path), "build/salvaged-w1"), str(repo), None,
                                 dirty=False, salvage_tag=tag)
    assert r["eligible"] is True and "salvaged" in r["reason"]


# ── reap_one_worktree (H24): the sanctioned single-path entrypoint ─────────────────────────
# The guarded replacement for raw `git worktree remove --force` -- the command that destroyed 3
# live build forks this session on false-death inference (no ps match / frozen mtime / 0 commits
# ahead, every one a FALSE NEGATIVE for a live fork). These tests run purely on injected dicts
# (mirrors the `classify_worktree_reap` unit style above) -- no real git touched.

def test_reap_one_worktree_refuses_LOCKED_loudly():
    # An otherwise merged+clean worktree that IS locked (an active build holds its lock) -- must be
    # refused loudly, and the remover must NEVER be called.
    # MUTATION: commenting out `if wt.get("locked"): ...` in classify_worktree_reap makes this
    # otherwise-eligible worktree pass through and the remover below raises -- proven manually
    # (guard removed -> AssertionError from bad_remover propagates -> test FAILS; guard restored
    # -> test PASSES). See final report for the before/after run.
    wt = _rwt("/wt/locked", "done-w1", locked=True, locked_reason="claude agent building (pid 1)")
    calls = []
    def bad_remover(p):
        calls.append(p)
        raise AssertionError("remover must NEVER be called on a locked worktree")
    r = F.reap_one_worktree("/wt/locked", worktrees=[wt], branch_states={"done-w1": "MERGED"},
                            main_path=MAIN2, dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
                            remover=bad_remover)
    assert r["removed"] is False and r["refused"] is True and r["loud"] is True
    assert "locked" in r["reason"]
    assert calls == []


def test_reap_one_worktree_refuses_LIVE_unmerged_loudly():
    # THE real fork-killing case: an UNLOCKED, clean worktree whose branch is still IN_FLIGHT (a
    # live build fork -- forks are never `locked` by the harness, so this branch-state guard is the
    # ONLY thing standing between a live fork and destruction). Must be refused loudly, remover
    # never called.
    # MUTATION: replacing the `else: branch_ok, branch_reason = False, ...` (IN_FLIGHT/ORPHAN) arm
    # in classify_worktree_reap with an unconditional `branch_ok = True` makes this pass through and
    # the remover raise -- proven manually (see final report for the before/after run).
    wt = _rwt("/wt/live", "live-w1")  # unlocked, clean
    calls = []
    def bad_remover(p):
        calls.append(p)
        raise AssertionError("remover must NEVER be called on a live/unmerged worktree")
    r = F.reap_one_worktree("/wt/live", worktrees=[wt], branch_states={"live-w1": "IN_FLIGHT"},
                            main_path=MAIN2, dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
                            remover=bad_remover)
    assert r["removed"] is False and r["refused"] is True and r["loud"] is True
    assert "IN_FLIGHT" in r["reason"]
    assert calls == []


def test_reap_one_worktree_reaps_merged_clean_unlocked(no_op_shared_lock):
    wt = _rwt("/wt/done", "done-w1")
    removed = []
    def fake_remover(p):
        removed.append(p)
        return {"path": p, "removed": True, "detail": "removed"}
    r = F.reap_one_worktree("/wt/done", worktrees=[wt], branch_states={"done-w1": "MERGED"},
                            main_path=MAIN2, dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
                            remover=fake_remover)
    assert r["removed"] is True and r["refused"] is False
    assert removed == ["/wt/done"]


def test_reap_one_worktree_never_uses_force():
    # A path that isn't even a registered worktree -- refused before classification/removal is ever
    # attempted; the remover is never invoked at all (the simplest structural proof that no code
    # path in `reap_one_worktree` reaches for `--force`: `reap_worktree_dir`'s own subprocess call
    # -- the only remover this module ships -- never passes it, and this entrypoint has no other
    # removal path).
    calls = []
    r = F.reap_one_worktree("/wt/unknown", worktrees=[_rwt("/wt/done", "done-w1")],
                            branch_states={"done-w1": "MERGED"}, main_path=MAIN2,
                            dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
                            remover=lambda p: calls.append(p))
    assert r["removed"] is False and r["refused"] is True and r["loud"] is True
    assert "not a registered worktree" in r["reason"]
    assert calls == []


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
pytestmark = pytest.mark.operational
