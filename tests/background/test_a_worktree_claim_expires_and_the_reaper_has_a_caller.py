"""THE WORKTREE LIFECYCLE HAD NO TERMINAL STATE — the three reasons six worktrees survived.

Director, 2026-09-01: *"Six undeclared worktrees are accreting and being reported rather than
cleared — that's the isolation machinery working with nothing tidying up behind it. Give them a
lifetime."*

Three independent defects, each sufficient on its own, stacked:

  1. THE CLAIM NEVER EXPIRED. `worktree_is_live` asked only "is the named pid alive?". Five markers
     named pid 215 — the tmux SERVER, up since 2026-08-24 and alive for as long as the console is —
     so five worktrees read as held by a live writer a full day after their writers had gone. The
     reaper refused them; `fork_salvage` skipped them.
  2. A LIVE REFUSAL SCORED AS A STUCK ONE. The `live writer` refusal was added at both reap doors
     on 2026-08-31 and never added to `_LIVE_REFUSALS`, so the one refusal that most emphatically
     means "the control is working" counted toward the alarm for a control that cannot work.
  3. THE REAPER HAD NO CALLER. `evaluate_worktree_reap` was built 2026-07-18 with two modes, its
     own arming flag and mutation-proven refusals — and no scheduler ever called it. Its own atom
     record predicted exactly this: *"an unwired reaper is prose."* The flag was armed at some
     point since, which is worse than neither, because `enforce=True` on a function nobody calls
     reads as a reaper that is running and finding nothing to do.

And one gap behind all three: every refusal was a DEAD END. `salvage_detached_head` was written as
the documented door out of the `detached ORPHAN` refusal and had never once been called.

Each test below fails if its own defect is reintroduced.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from background import deadmans_switch
from background import fork_reconciler as F
from background import seat_executor as SE


# ── 1. THE CLAIM IS A LEASE, NOT A DEED ─────────────────────────────────────────────────────
def _claimed(tmp_path, pid, age_seconds):
    """A worktree directory carrying an ownership marker written `age_seconds` ago."""
    import os
    d = tmp_path / f"wt-{pid}-{int(age_seconds)}"
    d.mkdir()
    marker = d / SE.OWNER_MARKER
    marker.write_text(f"{pid}\n")
    stamp = marker.stat().st_mtime - age_seconds
    os.utime(marker, (stamp, stamp))
    return d


def test_an_ownership_claim_expires_even_when_its_pid_is_immortal(tmp_path):
    """THE 2026-09-01 DEFECT. os.getpid() is alive for the whole test, standing in for pid 215.

    MUTATION: delete the `age < OWNER_LEASE_SECONDS` clause in `worktree_is_live` and the second
    assertion fails — an expired claim reads as a live writer again, which is exactly the state
    that made five worktrees immortal.
    """
    import os
    mine = os.getpid()
    assert SE.worktree_is_live(_claimed(tmp_path, mine, 60)) is True
    assert SE.worktree_is_live(_claimed(tmp_path, mine, SE.OWNER_LEASE_SECONDS + 60)) is False


def test_a_fresh_claim_by_a_dead_pid_is_not_live(tmp_path):
    """The lease does not REPLACE the pid check; both legs must hold. A killed writer leaves a
    fresh marker behind, and that worktree holds exactly the abandoned work the salvage sweep
    exists to rescue."""
    assert SE.worktree_is_live(_claimed(tmp_path, 2 ** 31 - 1, 5)) is False


def test_the_lease_is_derived_from_the_longest_legitimate_hold():
    """Not a picked number. A writer may hold a worktree for one bounded turn; the lease is that
    plus a grace. Keyed to the property so it survives the timeout being retuned."""
    assert SE.OWNER_LEASE_SECONDS > SE.SESSION_TIMEOUT_SECONDS


# ── 2. A REFUSAL MEANS SOMETHING, AND EVERY REFUSAL MUST SAY WHICH ──────────────────────────
def test_a_live_writers_worktree_is_spared_not_stranded():
    """MUTATION: drop "live writer" from `_LIVE_REFUSALS` and this fails. That was the live state
    of the tree for a day: five in-use worktrees counted toward `STRANDED_WORKTREE_ALARM_AT`."""
    live = ("a live writer holds this worktree -- never reaped while its process is alive; "
            "it is in use, not abandoned")
    assert F.refusal_is_stranded(live) is False


def test_every_refusal_the_classifier_can_emit_is_deliberately_classified():
    """THE CLASS FIX for defects that arrive the way this one did: a new refusal reason written at
    the door and never registered in the vocabulary that says what a refusal MEANS.

    `refusal_is_stranded` has no safe default — unlisted means STRANDED, which over-reports a live
    refusal (2026-08-31, the live writer), and listing everything means a genuinely stuck reaper
    reads as healthy (2026-08-30, the detached HEAD). So the only correct behaviour is that every
    refusal is classified ON PURPOSE, and this asserts it statically rather than waiting for one
    to be exercised.

    MUTATION: add a refusal branch to `classify_worktree_reap` returning a new reason and this
    fails until the author decides which side it belongs on.
    """
    src = Path(F.__file__).read_text()
    tree = ast.parse(src)

    def _leading_text(node):
        """The constant head of a reason expression — enough to classify, f-strings included."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str) and v.value.strip():
                    return v.value
        return None

    refusals = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = {k.value for k in node.keys if isinstance(k, ast.Constant)}
        if not {"eligible", "reason"} <= keys:
            continue
        pairs = dict(zip([getattr(k, "value", None) for k in node.keys], node.values))
        eligible = pairs.get("eligible")
        if isinstance(eligible, ast.Constant) and eligible.value is False:
            text = _leading_text(pairs["reason"])
            if text:
                refusals.append(text)

    assert len(refusals) >= 6, f"the AST scan stopped finding refusals: {refusals}"

    # Refusals this project has decided are STRANDED — the reaper is stuck on them and will stay
    # stuck without a change. Each must have an advancing step in `advance_stranded`.
    declared_stranded = ("uncommitted/untracked changes", "detached ORPHAN",
                         "branch ref absent", "detached HEAD state not determined",
                         "not a registered worktree")
    for reason in refusals:
        live = any(tok in reason for tok in F._LIVE_REFUSALS)
        stranded = any(reason.startswith(p) or p in reason for p in declared_stranded)
        assert live != stranded, (
            f"refusal is unclassified (or claims both): {reason!r}. Add its token to "
            f"_LIVE_REFUSALS if the control is WORKING when it fires, or to this test's "
            f"declared_stranded list AND give it a step in advance_stranded if it is stuck."
        )


# ── 3. THE STRANDED SET GETS ITS ONE PRESERVING STEP ────────────────────────────────────────
def test_a_detached_orphan_is_tagged_so_the_refusal_stops_being_a_dead_end():
    """`salvage_detached_head` existed, documented as the way out of this refusal, with no caller.
    A refusal naming a remedy nobody applies is a stall wearing a control's clothes."""
    kept = [{"path": "/tmp/wt", "branch": None,
             "reason": "detached ORPHAN: HEAD is unreachable from main and carries no salvage tag"
                       " -- refused until it is tagged, and STRANDED, not correctly spared"}]
    seen = {}

    def _tag(head):
        seen["head"] = head
        return {"tag": "salvage/detached-abc", "salvaged": True, "detail": "tagged and verified"}

    rows = F.advance_stranded(
        kept,
        salvage_dirty=lambda w: pytest.fail("a detached orphan is not the dirty path"),
        salvage_detached=_tag,
        head_of=lambda p: "abc123",
        live_writer_fn=lambda p: False,
    )
    assert seen["head"] == "abc123"
    assert rows == [{"path": "/tmp/wt", "step": "salvage_detached", "ok": True,
                     "detail": "salvage/detached-abc: tagged and verified"}]


def test_a_dirty_stranded_worktree_is_salvaged_not_left():
    kept = [{"path": "/tmp/wt", "branch": "build/x",
             "reason": "uncommitted/untracked changes -- never reaped"}]
    rows = F.advance_stranded(
        kept,
        salvage_dirty=lambda w: {"action": "SALVAGED", "sha": "deadbee"},
        salvage_detached=lambda h: pytest.fail("a dirty worktree is not the detached path"),
        live_writer_fn=lambda p: False,
    )
    assert rows[0]["step"] == "salvage_dirty" and rows[0]["ok"] is True


def test_advance_never_touches_a_live_writer_even_if_the_reason_string_lies():
    """The independent second gate. `refusal_is_stranded` reads a STRING this function did not
    produce, and that string's classification was wrong for a full day — so liveness is asked
    again, directly, before anything commits into the tree.

    MUTATION: delete the `live_writer_fn(path)` guard in `advance_stranded` and this fails,
    reproducing the 2026-08-31 incident (a daemon committing into a running writer's worktree)
    through the new door.
    """
    kept = [{"path": "/tmp/wt", "branch": "build/x",
             "reason": "uncommitted/untracked changes -- never reaped"}]
    rows = F.advance_stranded(
        kept,
        salvage_dirty=lambda w: pytest.fail("committed into a LIVE writer's worktree"),
        salvage_detached=lambda h: pytest.fail("tagged a LIVE writer's worktree"),
        live_writer_fn=lambda p: True,
    )
    assert rows[0]["step"] == "none" and rows[0]["ok"] is False


def test_a_correctly_spared_worktree_is_never_advanced():
    """Locked, main, bare, in-flight: the control working. Nothing is done to them."""
    kept = [{"path": "/a", "reason": "main worktree -- never reaped"},
            {"path": "/b", "reason": "locked (building) -- never reaped"},
            {"path": "/c", "reason": "branch is IN_FLIGHT -- live/undecided fork, never reaped"}]
    assert F.advance_stranded(kept, salvage_dirty=lambda w: pytest.fail("advanced a spared tree"),
                              salvage_detached=lambda h: pytest.fail("advanced a spared tree"),
                              live_writer_fn=lambda p: False) == []


def test_report_first_advances_nothing():
    """The advance rides the reap's arming flag. Unarmed means the whole lifecycle is report-only,
    exactly as it was before — this change does not arm anything."""
    wts = [{"path": "/main", "branch": None, "detached": False, "locked": False, "bare": False,
            "head": None, "locked_reason": None}]
    r = F.evaluate_worktree_reap(worktrees=wts, branch_states={}, main_path="/main", enforce=False,
                                 dirty_fn=lambda p: False, live_writer_fn=lambda p: False,
                                 advance=lambda kept: pytest.fail("advanced in report-first mode"))
    assert r["advanced"] == []


# ── 4. AN UNWIRED REAPER IS PROSE ───────────────────────────────────────────────────────────
def test_the_worktree_reaper_is_actually_called_by_the_cycle():
    """Built 2026-07-18, armed at some point, and called by NOTHING until 2026-09-01. Its own atom
    record named this failure in advance and it happened anyway, because nothing could observe it:
    a mechanism with no caller has no red state.

    MUTATION: remove `_check_worktree_reap()` from `run_cycle` and this fails.
    """
    body = inspect.getsource(deadmans_switch.run_cycle)
    assert "_check_worktree_reap()" in body

    reaper_call = inspect.getsource(deadmans_switch._check_worktree_reap)
    assert "evaluate_worktree_reap" in reaper_call, (
        "the cycle must call the REAPER, not a second reporter -- the reporter was already there "
        "and reporting is what the director asked us to stop doing on its own"
    )


# ══════════════════════════════════════════════════════════════════════════════════════════════
# THE REAPER REMOVED A LANDING WORKTREE NINE MINUTES INTO ITS OWN COMMIT GATE (2026-09-02)
#
# Every check did its job and the outcome was still wrong. The worktree carried an owner marker,
# but the marker held the pid of a shell that had already exited — `$$` from a command whose shell
# did not outlive it — so `worktree_is_live` correctly reported no writer. The gate runs in its own
# extract, so the worktree itself sat CLEAN and detached at `origin/main`: MERGED, and eligible by
# every structural rule. It was removed, and `surgical_land` spent thirty-nine more minutes gating
# against a directory that was no longer there. Publishing was down throughout.
#
# The missing question was never "is a process alive" — it was "could this possibly be abandoned
# yet". A reaper whose purpose is to clear ABANDONED directories has no business deciding that a
# directory minutes old, with work in flight, is one. `MIN_REAP_AGE_SECONDS` is that floor, and it
# is keyed to the longest legitimate thing that can be happening inside a worktree — a commit gate,
# which CLAUDE.md puts at "more than ten minutes" and which was observed at thirty-nine.
#
# It does NOT replace liveness. A writer that declares itself is spared at any age. This only stops
# a young worktree dying because nobody declared one, which is the case that actually happened.
# ══════════════════════════════════════════════════════════════════════════════════════════════

def _clean_merged_detached(path):
    return [{"path": path, "branch": None, "head": "c" * 40, "detached": True,
             "locked": False, "locked_reason": None, "bare": False}]


def _reap(path, *, age, live=False):
    return F.evaluate_worktree_reap(
        worktrees=_clean_merged_detached(path), branch_states={}, main_path="/repo",
        enforce=False, dirty_fn=lambda p: False, salvage_tag_fn=lambda b: None,
        reachable_fn=lambda h: True, detached_tag_fn=lambda h: None,
        live_writer_fn=lambda p: live, age_fn=lambda p, m=None: age)


def test_a_worktree_minutes_old_is_not_reaped_however_eligible_it_looks():
    """THE INCIDENT, at its real age. Clean, MERGED, no live writer — eligible by every other rule.

    MUTATION: drop the `MIN_REAP_AGE_SECONDS` branch and this worktree is removed, which is exactly
    what happened at 19:13 UTC with a commit gate running inside it.
    """
    r = _reap("/var/tmp/se-landing", age=9 * 60)
    assert r["eligible"] == []
    kept = r["kept"][0]["reason"]
    assert "too young to be abandoned" in kept and "9 minute(s) ago" in kept


def test_an_old_abandoned_worktree_is_still_reaped():
    """THE FLOOR THAT STOPS THIS BECOMING A PERMANENT EXEMPTION. Accretion is the disease this
    reaper exists to treat — the H24 gap was worktree dirs climbing 2 to 7 in one session — so a
    genuinely abandoned directory must still die."""
    r = _reap("/var/tmp/se-landing", age=10 * 24 * 3600)
    assert [e["path"] for e in r["eligible"]] == ["/var/tmp/se-landing"]


def test_an_unreadable_age_refuses_rather_than_assuming_old():
    """`fail_closed_on_unreadable_input`: a reaper that cannot tell how old a directory is cannot
    tell that it was abandoned. "Could not look" and "found it old" are opposite facts."""
    r = _reap("/var/tmp/se-landing", age=None)
    assert r["eligible"] == [] and "age is UNKNOWN" in r["kept"][0]["reason"]


def test_a_live_writer_is_spared_at_ANY_age():
    """The floor is additional to liveness, never a replacement: a declared writer's worktree is
    not abandoned no matter how long the turn has run."""
    r = _reap("/var/tmp/se-landing", age=10 * 24 * 3600, live=True)
    assert r["eligible"] == [] and "live writer" in r["kept"][0]["reason"]


def test_the_young_refusal_is_classified_as_SPARED_and_not_as_STRANDED():
    """THE INTERACTION THAT WOULD HAVE MADE IT WORSE, and the reason the classification test above
    exists at all.

    `advance_stranded` takes the one preserving step on every STRANDED worktree — for a dirty one
    that means COMMITTING ITS TREE. If "too young" scored as stranded, the reaper would stop
    deleting young worktrees and start committing into them instead, which is the single
    irreversible mistake available in this module. Young is a reason to leave alone.

    MUTATION: remove either token from `_LIVE_REFUSALS` and this fails.
    """
    young = "created 9 minute(s) ago, younger than the 90 minutes a commit gate can legitimately " \
            "take -- too young to be abandoned however clean it looks. See MIN_REAP_AGE_SECONDS."
    unknown = "the worktree's creation time could not be read, so its age is UNKNOWN -- refused"
    assert not F.refusal_is_stranded(young)
    assert not F.refusal_is_stranded(unknown)
    assert F.advance_stranded([{"path": "/var/tmp/se-landing", "reason": young}]) == []


def test_the_age_is_read_from_the_admin_entry_and_not_the_directory_mtime(tmp_path):
    """A BUSY LANDING WRITES FILES CONSTANTLY, so the worktree directory's own mtime is "seconds
    ago" for as long as work is happening — which would make the floor fire forever and the reaper
    never run. `git worktree add` writes `<main>/.git/worktrees/<name>/gitdir` once and nothing
    touches it afterwards, so that is the creation time.

    MUTATION: read `Path(path).stat().st_mtime` instead and this fails.
    """
    import os
    main = tmp_path / "main"
    admin = main / ".git" / "worktrees" / "wt"
    admin.mkdir(parents=True)
    gitdir = admin / "gitdir"
    gitdir.write_text("x\n")
    old = 3 * 3600
    os.utime(gitdir, (gitdir.stat().st_atime, gitdir.stat().st_mtime - old))

    wt = tmp_path / "wt"
    wt.mkdir()
    (wt / "just_written.txt").write_text("a landing is writing right now")   # dir mtime = NOW

    age = F.worktree_age_seconds(str(wt), str(main))
    assert age is not None and age > old - 60, (
        "the age came from the directory's mtime, which a live landing refreshes constantly")


def test_an_absent_admin_entry_reads_as_UNKNOWN_not_as_zero(tmp_path):
    """Zero would mean "brand new", which is the safe direction here by accident rather than by
    design — and it is the wrong ANSWER. The main worktree has no admin entry at all."""
    assert F.worktree_age_seconds(str(tmp_path / "nope"), str(tmp_path)) is None


# ══════════════════════════════════════════════════════════════════════════════════════════════
# TWO DAEMONS, TWO LIVENESS SIGNALS, AND ONE OF THEM COULD NOT SEE THE OTHER (2026-09-02)
#
# After the reaper removed a landing worktree whose owner marker held a dead pid, the landing was
# switched to `git worktree lock` — which the reaper refuses outright, and which no process death
# can invalidate. `fork_salvage` then committed into it anyway, because IT asks
# `seat_executor.worktree_is_live`, and that function knew about markers and not about locks.
#
# Not destructive — a salvage commit preserves rather than deletes — but the same class: a claim
# respected by one sweeper and invisible to the next. Both come through `worktree_is_live`, so
# teaching that one function about locks covers both, which is the whole reason it is documented as
# "THE ONE HOME FOR THE QUESTION".
# ══════════════════════════════════════════════════════════════════════════════════════════════

def _repo_with_worktree(tmp_path, *, lock_reason=None, marker_pid=None):
    import subprocess as sp
    main = tmp_path / "main"
    main.mkdir()
    for cmd in (["git", "init", "-q"],
                ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                 "--allow-empty", "-m", "base"]):
        sp.run(cmd, cwd=str(main), capture_output=True, check=True)
    wt = tmp_path / "wt"
    sp.run(["git", "worktree", "add", "--detach", "-q", str(wt)], cwd=str(main),
           capture_output=True, check=True)
    if lock_reason:
        sp.run(["git", "worktree", "lock", "--reason", lock_reason, str(wt)], cwd=str(main),
               capture_output=True, check=True)
    if marker_pid is not None:
        from background.seat_executor import OWNER_MARKER
        (wt / OWNER_MARKER).write_text(str(marker_pid) + "\n")
    return main, wt


def test_a_LOCKED_worktree_reads_as_live_with_no_marker_at_all(tmp_path, monkeypatch):
    """THE GAP THAT LET `fork_salvage` COMMIT INTO A LOCKED LANDING.

    MUTATION: remove the lock leg from `worktree_is_live` and this returns False -- and every
    sweeper that asks this question goes back to treating a locked worktree as abandoned.
    """
    import background.seat_executor as se
    main, wt = _repo_with_worktree(tmp_path, lock_reason="landing in progress")
    monkeypatch.setattr(se, "PROJECT_DIR", main)
    assert se.worktree_is_live(str(wt)) is True


def test_an_unlocked_worktree_with_no_marker_is_not_live(tmp_path, monkeypatch):
    """The floor. If a bare worktree read as live the reaper would never run and the accretion this
    module exists to stop would return — the H24 gap, 26 worktrees over 16 days."""
    import background.seat_executor as se
    main, wt = _repo_with_worktree(tmp_path)
    monkeypatch.setattr(se, "PROJECT_DIR", main)
    assert se.worktree_is_live(str(wt)) is False


def test_a_lock_is_honoured_even_though_a_dead_pid_marker_is_not(tmp_path, monkeypatch):
    """THE EXACT PAIRING FROM THE INCIDENT: a marker naming a process that has exited, and a lock.

    The marker must not rescue it -- that is the leased-claim rule, and five worktrees once spent a
    day claimed by the tmux server. The LOCK must, because a lock is a deliberate act that nobody
    leaves behind by crashing: you have to type it.
    """
    import background.seat_executor as se
    main, wt = _repo_with_worktree(tmp_path, lock_reason="landing", marker_pid=999_999)
    monkeypatch.setattr(se, "PROJECT_DIR", main)
    assert se.worktree_is_live(str(wt)) is True          # the lock carries it

    import subprocess as sp
    sp.run(["git", "worktree", "unlock", str(wt)], cwd=str(main), capture_output=True, check=True)
    assert se.worktree_is_live(str(wt)) is False          # the dead marker alone does not
