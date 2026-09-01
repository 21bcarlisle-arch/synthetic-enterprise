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


def test_trailing_comment_does_not_void_the_hold(tmp_path):
    """R15: the hold must FAIL SAFE. A held entry annotated with why it is held used to parse
    as the whole line -- which can never equal a real branch name, so the hold silently did
    nothing and the branch was reaped on the next enforce pass. Regression for that fail-open
    (2026-08-03: found while arming enforce, with 14 real branches written this way)."""
    p = tmp_path / ".fork_reap_held"
    p.write_text(
        "worktree-agent-abc   # holds the only copy of regulation_commons/\n"
        "worktree-agent-def#no space before the hash\n"
    )
    assert F.held_branches(p) == {"worktree-agent-abc", "worktree-agent-def"}


def test_an_annotated_held_branch_actually_survives_enforce(tmp_path):
    """The parse bug above only matters because of THIS: prove end-to-end that a branch held
    with a trailing comment is not reaped when enforce is armed. Fails loudly on the reaper."""
    p = tmp_path / ".fork_reap_held"
    p.write_text("build/holdme   # annotated exactly the way the real held file is written\n")
    r = F.evaluate_fork_lifecycle(
        branches=[_b("build/holdme", False, DL + 60)], now=NOW, enforce=True,
        held=F.held_branches(p),
        reaper=lambda n: (_ for _ in ()).throw(AssertionError(f"reaped held branch {n}!")))
    assert r["reaped"] == [] and r["held_orphans"] == ["build/holdme"]


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
        if a[:1] == ("rev-parse",) and a[-1] == "refs/heads/build/y":
            # post-delete post-condition (2026-08-03): the ref is GONE once `branch -D` ran.
            # The fake has to model this now -- reaped=True is no longer asserted from the
            # absence of an error, it is asserted from the ref actually having disappeared.
            return "" if any(c[:2] == ("branch", "-D") for c in calls) else "TIPAAA\n"
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
#
# BOTH DESTINATIONS ARE COLLECTED, not just the wire. G-N3 (2026-08-12) routes an alarm by its
# `topic_class`: the instant classes reach `send_ntfy`, the deferrable ones are BATCHED into the
# periodic digest via `notification_digest.defer`. FORK ORPHANS and WORKTREE UNDECLARED were
# classed `drift` on 2026-08-13 (the worktree one had paged five times in a day about transient
# temp worktrees), which moved their destination and left these two tests asserting on an empty
# `send_ntfy` list. Collecting only the wire would now read a correctly-routed alarm as a SILENT
# one -- and the same blindness runs the other way in `test_deadman_silent_when_no_orphans`
# below, where a wire-only assertion would pass while the alarm quietly filled the digest. So
# `_alarm_channels` returns the two lists separately: `raised` proves the alarm happened at all,
# `paged`/`batched` prove where it went.
def _alarm_channels(tmp_path, monkeypatch):
    """(raised, paged, batched) -- every destination a deadman alarm can reach."""
    from background import deadmans_switch as D
    from background import notification_digest
    import background.notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    monkeypatch.setattr(D, "LOG_FILE", tmp_path / "log.md")
    raised, paged, batched = [], [], []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy",
                        lambda msg, **k: (raised.append(msg), paged.append(msg), "id")[2])
    monkeypatch.setattr(notification_digest, "defer",
                        lambda msg, **k: (raised.append(msg), batched.append(msg), "deferred:0")[2])
    return raised, paged, batched


def test_deadman_fires_fork_orphans_and_is_transition_only(tmp_path, monkeypatch):
    from background import deadmans_switch as D
    raised, paged, batched = _alarm_channels(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "background.fork_reconciler.evaluate_fork_lifecycle",
        lambda: {"status": "FORK_ORPHANS", "alarm": True, "detail": "3 orphaned fork branch(es)",
                 "orphans": ["a", "b", "c"], "in_flight": [], "merged_eligible": [], "reaped": [],
                 "enforce": False},
    )
    D._check_fork_lifecycle()
    assert len(raised) == 1 and "FORK ORPHANS" in raised[0]      # the alarm fires
    D._check_fork_lifecycle()
    assert len(raised) == 1                                       # ...once -- transition-only (R5)
    assert batched == raised and paged == []                      # ...into the digest (drift, G-N3)


def test_deadman_silent_when_no_orphans(tmp_path, monkeypatch):
    from background import deadmans_switch as D
    raised, _paged, _batched = _alarm_channels(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "background.fork_reconciler.evaluate_fork_lifecycle",
        lambda: {"status": "FORK_CLEAN", "alarm": False, "detail": "no orphans",
                 "orphans": [], "in_flight": [], "merged_eligible": [], "reaped": [], "enforce": False},
    )
    D._check_fork_lifecycle()
    assert raised == []                              # clean -> nothing raised, on EITHER channel


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
    # merged = came home, awaiting the H24 dir-reaper: a benign transient, NOT accretion. Flagging it
    # UNDECLARED paged the director on healthy churn (the 2026-07-19 transient-ping escalation).
    assert F.classify_worktree(_wt("/wt/c", "done-w3"), MAIN, states) == "PENDING_REAP"
    assert F.classify_worktree(_wt("/wt/d", detached=True), MAIN, states) == "UNDECLARED"  # detached


def test_merged_worktree_pending_reap_does_NOT_alarm_but_orphan_DOES():
    # R15 (ping-hygiene): the transient-suppression must FIRE (no alarm) on a merged-pending-reap
    # worktree, yet the genuine-accretion alarm must STILL FIRE on an unmerged orphan. A mutation that
    # reverts classify_worktree to treat MERGED as UNDECLARED would re-page on healthy churn -> caught
    # by the first assertion; a mutation that stopped alarming on orphans -> caught by the second.
    wts = [_wt(MAIN, "main"), _wt("/wt/merged", "done-w3")]
    r = F.evaluate_worktree_reconcile(worktrees=wts, branch_states={"done-w3": "MERGED"}, main_path=MAIN)
    assert r["alarm"] is False and r["status"] == "WORKTREE_CLEAN"     # transient graced -> no page
    assert r["pending_reap"] == ["/wt/merged"]                         # surfaced, not hidden
    # a genuine orphan alongside the merged transient still alarms (and only the orphan is undeclared)
    wts2 = wts + [_wt("/wt/orphan", "old-w2")]
    r2 = F.evaluate_worktree_reconcile(
        worktrees=wts2, branch_states={"done-w3": "MERGED", "old-w2": "ORPHAN"}, main_path=MAIN)
    assert r2["alarm"] is True and {u["path"] for u in r2["undeclared"]} == {"/wt/orphan"}
    assert r2["pending_reap"] == ["/wt/merged"]


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
    # `head` added 2026-08-30. It is the field that makes a DETACHED worktree determinable at
    # all -- every worktree has a HEAD and only some have a branch -- so a parser that drops it
    # sends `classify_detached_head` a None and every detached worktree back to permanently
    # refused. That is what this line is guarding, not the porcelain format.
    assert wts == [
        {"path": "/repo", "branch": "main", "head": "abc", "detached": False,
         "locked": False, "locked_reason": None, "bare": False},
        {"path": "/tmp/x", "branch": None, "head": "def", "detached": True,
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
    raised, paged, batched = _alarm_channels(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "background.fork_reconciler.evaluate_worktree_reconcile",
        lambda: {"status": "WORKTREE_UNDECLARED", "alarm": True, "detail": "1 undeclared",
                 "undeclared": [{"path": "/wt/x", "branch": "b", "branch_state": "ORPHAN"}]},
    )
    D._check_worktree_reconcile()
    assert len(raised) == 1 and "WORKTREE UNDECLARED" in raised[0]
    D._check_worktree_reconcile()
    assert len(raised) == 1                                       # transition-only (R5)
    assert batched == raised and paged == []                      # ...into the digest (drift, G-N3)


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


# ── STRANDED reporting (H24, 2026-08-03) ────────────────────────────────────────────────────
# "your worktree reaper can't reap itself, which is why those strays never clear" (director
# console). Measured live at the time: 26 worktrees, 0 eligible, and the report said
# WORKTREE_REAP_CLEAN / alarm=False -- so a population the control was STRUCTURALLY unable to
# touch read as health for 16 days. "Nothing eligible" must never again be indistinguishable
# from "nothing to do".

def _stranded_env(n_dirty=0, n_orphan=0, n_locked=0, n_merged_clean=0):
    """Build an injectable worktree population with a known refusal mix."""
    wts, states, dirty = [{"path": MAIN2, "branch": "main", "detached": False,
                           "locked": False, "locked_reason": None, "bare": False}], {}, {}
    def add(prefix, i, branch_state, is_dirty, locked=False):
        b = f"{prefix}-{i}"
        p = f"/wt/{b}"
        wts.append(_rwt(p, b, locked=locked, locked_reason="in use" if locked else None))
        states[b] = branch_state
        dirty[p] = is_dirty
    for i in range(n_dirty):       add("dirty", i, "MERGED", True)
    for i in range(n_orphan):      add("orphan", i, "ORPHAN", False)
    for i in range(n_locked):      add("locked", i, "IN_FLIGHT", False, locked=True)
    for i in range(n_merged_clean):add("done", i, "MERGED", False)
    return dict(worktrees=wts, branch_states=states, main_path=MAIN2, enforce=False,
                dirty_fn=lambda p: dirty.get(p, False), salvage_tag_fn=lambda b: None)


def test_a_standing_stranded_population_ALARMS_instead_of_reporting_clean():
    ev = F.evaluate_worktree_reap(**_stranded_env(n_dirty=16, n_orphan=5, n_locked=3))
    assert ev["status"] == "WORKTREE_REAP_STRANDED"
    assert ev["alarm"] is True, "a reaper that cannot act on its own population is not CLEAN"
    assert "16 dirty" in ev["detail"] and "5 orphan-branch" in ev["detail"]
    # the legitimately-kept ones are counted separately, not smeared into the failure
    assert "4 legitimately kept" in ev["detail"]  # 3 locked + main


def test_MUTATION_a_healthy_population_is_still_CLEAN_and_silent():
    """The other way: locked/live/main refusals are the control WORKING. A guard that alarmed on
    every non-empty `kept` would be as useless as one that never alarmed."""
    ev = F.evaluate_worktree_reap(**_stranded_env(n_locked=3))
    assert ev["status"] == "WORKTREE_REAP_CLEAN"
    assert ev["alarm"] is False


def test_a_couple_of_dirty_forks_midbuild_is_churn_not_an_alarm():
    ev = F.evaluate_worktree_reap(**_stranded_env(n_dirty=2))
    assert ev["status"] == "WORKTREE_REAP_CLEAN" and ev["alarm"] is False
    assert "2 stranded" in ev["detail"], "still COUNTED, just under the threshold"


def test_eligible_work_still_reports_ELIGIBLE_not_stranded():
    ev = F.evaluate_worktree_reap(**_stranded_env(n_dirty=16, n_merged_clean=1))
    assert ev["status"] == "WORKTREE_REAP_ELIGIBLE", "real work must not be masked by the alarm"


def test_refusal_is_stranded_splits_the_two_classes():
    for live in ("main worktree -- never reaped", "locked (in use) -- never reaped",
                 "branch is IN_FLIGHT -- live/undecided fork, never reaped"):
        assert F.refusal_is_stranded(live) is False, live
    for stuck in ("uncommitted/untracked changes -- never reaped",
                  "branch is ORPHAN -- live/undecided fork, never reaped",
                  "branch ref absent, no salvage tag -- undetermined, never reaped",
                  # MOVED OUT OF `live` ON 2026-08-30, and this is the correction that matters.
                  # A detached worktree used to be scored as correctly SPARED, so the reaper
                  # reported itself healthy while `[WORKTREE UNDECLARED]` fired 159 times over
                  # 14.3 hours naming three detached directories it could never touch. The
                  # stranded/live split exists precisely to make "0 eligible" interpretable
                  # (H24: 26 worktrees over 16 days behind a green report) and it was blind in
                  # the one population that was accumulating. An unreachable, unpinned detached
                  # HEAD is STUCK, and must read as stuck.
                  "detached ORPHAN: HEAD is unreachable from main and carries no salvage tag "
                  "-- refused until it is tagged, and STRANDED, not correctly spared",
                  "detached HEAD state not determined by the caller -- refused, and STRANDED"):
        assert F.refusal_is_stranded(stuck) is True, stuck


# ── R15: the destructive half must not report success it did not achieve ────────────────────
def test_reap_reports_failure_when_the_branch_survives_the_delete(monkeypatch):
    """FAIL-SILENT regression (2026-08-03, found live). `_git` returns '' on non-zero exit, so a
    refused `branch -D` looked identical to a successful one and salvage_and_reap returned
    reaped=True regardless. Armed for the first time, it logged "reaped 26/26" having deleted
    NOTHING -- git refuses to delete a branch checked out in a worktree. Here the ref survives
    the delete; the result must say so, and must name the worktree holding it."""
    tip = "a" * 40
    def fake_git(*args):
        if args[0] == "rev-parse" and args[1] == "b/live":
            return tip + "\n"
        if args[0] == "rev-parse" and "--verify" in args:
            # tag lookup resolves; the branch ref STILL EXISTS after the delete (the bug)
            return (tip + "\n") if args[-1].startswith("salvage/") else (tip + "\n")
        if args[0] == "rev-parse":
            return tip + "\n"
        if args[0] == "worktree" and args[1] == "list":
            return f"worktree /repo/.claude/worktrees/agent-live\nbranch refs/heads/b/live\n"
        return ""
    monkeypatch.setattr(F, "_git", fake_git)
    r = F.salvage_and_reap("b/live")
    assert r["reaped"] is False, "reported a reap that did not happen"
    assert "still present" in r["detail"]
    assert "agent-live" in r["detail"], "refusal must name the worktree holding the branch"


def test_reap_reports_success_only_when_the_ref_is_actually_gone(monkeypatch):
    """The other half of the mutation pair: identical flow, ref genuinely gone -> reaped True."""
    tip = "a" * 40
    def fake_git(*args):
        if args[0] == "rev-parse" and args[1] == "b/dead":
            return tip + "\n"
        if args[0] == "rev-parse" and "--verify" in args:
            if args[-1].startswith("refs/heads/"):
                return ""                      # the branch IS gone
            return tip + "\n"                  # the salvage tag resolves
        if args[0] == "rev-parse":
            return tip + "\n"
        return ""
    monkeypatch.setattr(F, "_git", fake_git)
    r = F.salvage_and_reap("b/dead")
    assert r["reaped"] is True and "then reaped" in r["detail"]


# ── the orphan/worktree DEADLOCK (2026-08-03) ───────────────────────────────────────────────
def _wt_reap(path="/repo/.claude/worktrees/agent-x", branch="worktree-agent-x"):
    return {"path": path, "branch": branch, "detached": False, "locked": False, "bare": False}


def test_salvaged_orphan_worktree_is_reapable_breaking_the_deadlock():
    """Before this, an ORPHAN branch + its worktree could never be cleaned in EITHER order:
    `branch -D` is refused while the branch is checked out in a worktree, and this classifier
    would not release the worktree until the branch was gone. The pair was immortal -- the real
    mechanism behind the worktree accretion. A VERIFIED salvage tag means the work is committed
    and pinned, so the directory is redundant and safe to remove first."""
    r = F.classify_worktree_reap(_wt_reap(), "/repo", "ORPHAN", dirty=False, salvage_tag="salvage/worktree-agent-x")
    assert r["eligible"] is True
    assert "confirmed-salvaged" in r["reason"]


def test_unsalvaged_orphan_worktree_is_still_never_reaped():
    """The deadlock-breaker is narrow: no salvage tag means the work is NOT provably preserved,
    so the directory must stay. This is the guard that keeps the fix from becoming a data-loss."""
    r = F.classify_worktree_reap(_wt_reap(), "/repo", "ORPHAN", dirty=False, salvage_tag=None)
    assert r["eligible"] is False and "live/undecided" in r["reason"]


def test_dirty_salvaged_orphan_worktree_is_still_never_reaped():
    """Clean-ness is still required even with a salvage tag: uncommitted work in the directory
    is by definition not in the commit the tag pins."""
    r = F.classify_worktree_reap(_wt_reap(), "/repo", "ORPHAN", dirty=True, salvage_tag="salvage/worktree-agent-x")
    assert r["eligible"] is False and "uncommitted" in r["reason"]


def test_in_flight_worktree_is_never_reaped_even_with_a_salvage_tag():
    """A LIVE fork's home is never touched -- the deadlock-breaker applies to ORPHAN only."""
    r = F.classify_worktree_reap(_wt_reap(), "/repo", "IN_FLIGHT", dirty=False, salvage_tag="salvage/worktree-agent-x")
    assert r["eligible"] is False and "live/undecided" in r["reason"]


# ── A DETACHED HEAD IS A COMMIT, AND A COMMIT IS DETERMINABLE (2026-08-30) ──────────────────
# THE DEFECT THESE FIRE ON. `classify_worktree_reap` refused every detached worktree with
# "detached/no branch -- undetermined, never reaped", and `_LIVE_REFUSALS` scored that refusal as
# the control WORKING. Both halves were wrong in the same direction, so a detached worktree was
# immortal AND invisible: `[WORKTREE UNDECLARED]` fired 159 times over 14.3 hours naming three of
# them (2026-08-26 alarm document) while the reaper reported itself clean. That is the accretion
# this module exists to stop, reappearing in the one population its own stranded/live split could
# not see. Measured before the repair: 4 undeclared worktrees, of which the reaper could act on
# exactly 1 (the branch-holding orphan); after, 4 of 4, two of them via a deliberate salvage tag.

def _wt_detached(path="/tmp/x", head="a" * 40):
    return {"path": path, "branch": None, "head": head, "detached": True,
            "locked": False, "locked_reason": None, "bare": False}


def test_a_detached_head_reachable_from_main_is_eligible():
    """It came home. Removing the directory touches no commit that is not already on main."""
    r = F.classify_worktree_reap(_wt_detached(), "/repo", None, dirty=False, salvage_tag=None,
                                 detached_head_state="MERGED")
    assert r["eligible"] is True and "already came home" in r["reason"]


def test_a_detached_head_with_a_salvage_tag_is_eligible():
    """Unmerged but pinned: the work is recoverable, so the directory is a redundant copy."""
    r = F.classify_worktree_reap(_wt_detached(), "/repo", None, dirty=False, salvage_tag=None,
                                 detached_head_state="SALVAGED")
    assert r["eligible"] is True and "confirmed-salvaged" in r["reason"]


def test_an_unpinned_unmerged_detached_head_is_refused_AND_reads_as_stranded():
    """The safety half and the visibility half, asserted together because either alone is the bug.

    Refusing without reporting STRANDED is exactly what shipped: safe, permanent, and silent.
    """
    r = F.classify_worktree_reap(_wt_detached(), "/repo", None, dirty=False, salvage_tag=None,
                                 detached_head_state="ORPHAN")
    assert r["eligible"] is False, "an unsalvaged detached HEAD must never be reaped"
    assert F.refusal_is_stranded(r["reason"]) is True, (
        "refused-and-scored-live is the exact combination that hid three worktrees for four days")


def test_a_caller_that_determines_nothing_is_refused_and_stranded():
    """FAIL CLOSED, and say which thing failed. `detached_head_state=None` means the CALLER did
    not determine it -- which is a defect in the caller, not evidence the worktree is live."""
    r = F.classify_worktree_reap(_wt_detached(), "/repo", None, dirty=False, salvage_tag=None)
    assert r["eligible"] is False
    assert "not determined by the caller" in r["reason"]
    assert F.refusal_is_stranded(r["reason"]) is True


def test_a_dirty_detached_worktree_is_refused_however_determined():
    """Uncommitted work outranks every determination. The one that would lose real work."""
    for state in ("MERGED", "SALVAGED"):
        r = F.classify_worktree_reap(_wt_detached(), "/repo", None, dirty=True, salvage_tag=None,
                                     detached_head_state=state)
        assert r["eligible"] is False and "uncommitted" in r["reason"], state


def test_classify_detached_head_is_a_pure_three_way():
    assert F.classify_detached_head("abc", reachable=True, salvage_tag=None) == "MERGED"
    assert F.classify_detached_head("abc", reachable=False, salvage_tag="t") == "SALVAGED"
    assert F.classify_detached_head("abc", reachable=False, salvage_tag=None) == "ORPHAN"
    # Reachability wins over a tag: a commit on main needs no salvage argument.
    assert F.classify_detached_head("abc", reachable=True, salvage_tag="t") == "MERGED"


def test_both_reap_doors_determine_a_detached_worktree_the_same_way():
    """`evaluate_worktree_reap` and `reap_one_worktree` must not disagree.

    Two doors with two answers is how a directory gets removed by one and refused by the other,
    and it is why the determination lives in one helper rather than being inlined twice.
    """
    wt = _wt_detached("/tmp/orphan")
    env = dict(worktrees=[wt], branch_states={}, main_path="/repo",
               dirty_fn=lambda p: False,
               reachable_fn=lambda h: False, detached_tag_fn=lambda h: None)
    ev = F.evaluate_worktree_reap(enforce=False, **env)
    assert ev["eligible"] == []
    one = F.reap_one_worktree("/tmp/orphan", remover=lambda p: {"removed": True}, **env)
    assert one["refused"] is True
    assert ev["kept"][0]["reason"] == one["reason"], "the two doors disagree"


def test_salvage_tag_name_is_one_convention(monkeypatch):
    """The writer and the reader must agree, or a salvage nobody can find is not a salvage."""
    head = "e614a788616b72a71f8a965e7f03c1555736f254"
    name = F.detached_salvage_tag_name(head)
    assert name == "salvage/detached-e614a788616b"
    def fake_git(*args):
        resolves = args[:1] == ("rev-parse",) and f"refs/tags/{name}" in args
        return head + "\n" if resolves else ""

    monkeypatch.setattr(F, "_git", fake_git)
    assert F._detached_salvage_tag_for(head) == name
    # A head with no tag reads as untagged, and a missing head is not an error.
    assert F._detached_salvage_tag_for("c" * 40) is None
    assert F._detached_salvage_tag_for(None) is None


def test_salvage_refuses_when_the_tag_does_not_verify(monkeypatch):
    """R15: an unverified tag is not a salvage. The whole safety argument for removing the
    directory rests on the commit being pinned, so a tag that did not land must say so."""
    head = "b" * 40
    calls = []

    def fake_git(*args):
        calls.append(args)
        if args[:1] == ("rev-parse",) and args[-1].endswith("^{commit}"):
            return head + "\n"
        if args[:1] == ("rev-parse",) and "refs/tags/" in args[-1]:
            return ""            # the tag never appears, before OR after `git tag`
        return ""

    monkeypatch.setattr(F, "_git", fake_git)
    r = F.salvage_detached_head(head)
    assert r["salvaged"] is False and "did not verify" in r["detail"]


# ── A LIVE WRITER'S WORKTREE IS NOT ABANDONED (2026-08-31) ───────────────────────────────────────
# The seat executor -- the first unattended WRITER in this project's history -- was armed on
# 2026-08-31 with a worktree at /var/tmp/se-seat-executor. This reaper is ARMED and had not
# destroyed it only by luck: it refuses a DIRTY worktree, and the executor is dirty for most of a
# turn. But `ensure_worktree` resets and cleans that tree at the START of every turn, so there is a
# window where it is clean and detached at origin/main -- MERGED, and by this classifier's own
# rules ELIGIBLE. `git worktree remove` on a live writer is the whole turn gone.
#
# Its sibling `fork_salvage` had already collided with the same worktree four minutes into the
# first run, committing into it while the executor worked. That is what prompted looking here.

_LIVE_WT = "/var/tmp/se-seat-executor"


def _merged_clean_detached_worktree(path=_LIVE_WT):
    """The exact shape the reaper would otherwise take: detached, reachable from main, clean."""
    return [{"path": path, "branch": None, "head": "abc1234", "detached": True,
             "locked": False, "locked_reason": None, "bare": False}]


def test_the_reaper_refuses_a_live_writers_worktree(tmp_path):
    """MUTATION: drop the `live_writer_fn` branch in `evaluate_worktree_reap` and this fires."""
    report = F.evaluate_worktree_reap(
        worktrees=_merged_clean_detached_worktree(),
        branch_states={}, main_path="/repo", enforce=False,
        dirty_fn=lambda p: False,                       # clean -- the dangerous window
        salvage_tag_fn=lambda b: None,
        reachable_fn=lambda h: True,                    # MERGED
        detached_tag_fn=lambda h: None,
        live_writer_fn=lambda p: p == _LIVE_WT,
    )
    assert report["eligible"] == []
    kept = report["kept"]
    assert len(kept) == 1 and "live writer" in kept[0]["reason"]


_FORK_WT = "/var/tmp/se-some-fork"       # a fork's worktree: NOT any daemon's declared home


def test_a_forks_worktree_IS_eligible_once_its_writer_is_gone(tmp_path):
    """THE LEG THAT STOPS LIVENESS BECOMING A PERMANENT EXEMPTION.

    A killed fork leaves its pid file behind and its worktree behind, and that directory is exactly
    the accretion this reaper exists to remove -- the H24 gap was worktree dirs climbing 2 -> 7 in
    one session. Exempting a PATH would trade one collision for unbounded accretion; only LIVENESS
    may spare a fork.

    THE SUBJECT MOVED ON 2026-09-01, and the argument is answered rather than dropped. This test
    was written against `/var/tmp/se-seat-executor`, which is now a DECLARED DAEMON HOME and is
    spared by name (see the next test for why that is not the exemption this docstring forbids).
    Its real subject was always a fork's worktree, so it uses one.
    """
    report = F.evaluate_worktree_reap(
        worktrees=_merged_clean_detached_worktree(_FORK_WT),
        branch_states={}, main_path="/repo", enforce=False,
        dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
        reachable_fn=lambda h: True, detached_tag_fn=lambda h: None,
        live_writer_fn=lambda p: False,                 # the writer has exited
    )
    assert [e["path"] for e in report["eligible"]] == [_FORK_WT]


def test_a_declared_daemon_home_is_spared_even_with_no_writer_in_it():
    """AND WHY THAT IS NOT THE PATH EXEMPTION THE TEST ABOVE FORBIDS.

    "Exempting a path trades one collision for unbounded accretion" is exactly right about a FORK,
    and false about a declared home, because the spared population is bounded at one PER DAEMON by
    construction: `ensure_worktree` creates it if absent and RESETS it if present. Reaping it
    between turns reduces nothing -- it makes the owner recreate it next turn and leaves a salvage
    tag behind each time. On a 30-minute timer that is ~50 tags a day, which is the same disease
    with a smaller footprint.

    Nothing is lost, and the owning module says so: *"this worktree holds no history worth keeping
    between turns. Anything it landed was promoted at the end of the turn that landed it, and
    anything it did not land was not finished."*

    THE FAILURE MODE IS NAMED RATHER THAN HIDDEN: if a daemon is retired, its declared home stops
    being reaped and must be removed with it. That is ONE stale directory, bounded, against
    unbounded tag growth -- and it is why the spared set is read from the OWNING MODULE's own
    declaration rather than a literal typed here, so retiring the daemon retires the exemption.
    """
    homes = F.declared_daemon_homes()
    assert homes, "no daemon declares a home worktree -- this test has lost its subject"
    report = F.evaluate_worktree_reap(
        worktrees=_merged_clean_detached_worktree(homes[0]),
        branch_states={}, main_path="/repo", enforce=False,
        dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
        reachable_fn=lambda h: True, detached_tag_fn=lambda h: None,
        live_writer_fn=lambda p: False,                 # idle between turns, not abandoned
    )
    assert report["eligible"] == []
    assert "declared daemon" in report["kept"][0]["reason"]
    # And it is the control WORKING, not the reaper stuck -- a spared home must never count toward
    # the stranded alarm, which is the mistake `live writer` made for a day.
    assert F.refusal_is_stranded(report["kept"][0]["reason"]) is False


def test_both_reap_doors_spare_a_declared_daemon_home():
    """A rule enforced at one door and not the other is a rule with a way round it, and
    `reap_one_worktree` is the door an operator calls by hand."""
    homes = F.declared_daemon_homes()
    r = F.reap_one_worktree(
        homes[0], worktrees=_merged_clean_detached_worktree(homes[0]),
        branch_states={}, main_path="/repo",
        dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
        reachable_fn=lambda h: True, detached_tag_fn=lambda h: None,
        live_writer_fn=lambda p: False,
        remover=lambda p: pytest.fail("removed a declared daemon's home worktree"),
    )
    assert r["refused"] is True and "declared daemon" in r["reason"]


def test_BOTH_reap_doors_refuse_a_live_writer(tmp_path):
    """A rule enforced at one door and not the other is a rule with a way round it, and this file
    already holds that principle for detached-HEAD determination. `reap_one_worktree` is the door
    an operator calls by hand, which is if anything the likelier one to be pointed at a live tree.

    MUTATION: remove the check from `reap_one_worktree` and this fires alone.
    """
    removed = []
    result = F.reap_one_worktree(
        _LIVE_WT,
        worktrees=_merged_clean_detached_worktree(),
        branch_states={}, main_path="/repo",
        dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
        reachable_fn=lambda h: True, detached_tag_fn=lambda h: None,
        remover=lambda p: removed.append(p) or {"removed": True},
        live_writer_fn=lambda p: True,
    )
    assert result["refused"] is True
    assert result["removed"] is False
    assert "live writer" in result["reason"]
    assert removed == [], "the remover was called on a worktree with a live process in it"


def test_the_default_liveness_answer_comes_from_the_module_that_owns_it():
    """One question, one home. `seat_executor` owns WORKTREE and PID_FILE, so it owns the answer;
    `fork_salvage` asks the same function. Two modules that do not import each other each carrying
    their own liveness rule is the ontology defect this project has been paying for all month.

    MUTATION: reimplement the probe locally in either daemon and this fires.
    """
    from background import fork_reconciler, fork_salvage, seat_executor

    probe = object()
    seen = []

    class _Spy:
        def worktree_is_live(self, path):  # pragma: no cover - shape only
            return True

    import unittest.mock as mock
    with mock.patch.object(seat_executor, "worktree_is_live",
                           lambda p: (seen.append(p), True)[1]):
        assert fork_reconciler._live_writer_default("/some/path") is True
        assert fork_salvage._is_a_live_writers_worktree("/some/path") is True
    assert seen == ["/some/path", "/some/path"], (
        "one of the daemons answered the liveness question itself instead of asking the module "
        f"that owns it: {seen}"
    )
    del probe, _Spy
