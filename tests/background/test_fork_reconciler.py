"""FORK-LIFECYCLE reconciler (director P0, 2026-07-17, step 3).

R15 mutation coverage: the mechanism must FIRE on an orphan (a fork that never merged home past
the deadline), stay SILENT on a live in-flight fork, and NEVER reap a merged branch (it came home).
Reap-only (policy A): salvage ALWAYS precedes reap; a reap that cannot first confirm salvage is
REFUSED (never delete unsalvaged work). Report-first: detection with NO reaping.
"""
from __future__ import annotations

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


def _wt(path, branch=None, detached=False):
    return {"path": path, "branch": branch, "detached": detached}


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
    import types
    porcelain = ("worktree /repo\nHEAD abc\nbranch refs/heads/main\n\n"
                 "worktree /tmp/x\nHEAD def\ndetached\n")
    import background.fork_reconciler as FR
    orig = FR._git
    FR._git = lambda *a: porcelain if a[:2] == ("worktree", "list") else orig(*a)
    try:
        wts = FR.scan_worktrees()
    finally:
        FR._git = orig
    assert wts == [{"path": "/repo", "branch": "main", "detached": False},
                   {"path": "/tmp/x", "branch": None, "detached": True}]


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
