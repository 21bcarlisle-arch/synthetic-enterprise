"""The publish verdict asks REACHABILITY, and it asks it after the cadence that absorbs the commit.

WORKER_FINDING_THE_PUBLISH_SUCCEEDS_BY_REACHABILITY_AND_IS_GRADED_BY_EQUALITY_2026-09-16.

`_publish_surface_collisions` widened the COMMIT gate on 2026-09-16: a publish commit whose paths
are disjoint from what origin is bringing may be created while BEHIND origin, because
`origin_reconcile` absorbs it on the next cadence. The PUSH verdict was not widened with it. It
read `remote_head == local_head`, and a commit created while behind can never make origin's head
equal ours -- so the exact case the commit gate was widened to admit was the case the push verdict
refused structurally, every time, no matter what happened on the remote.

The live instance: `05add41ab` put `docs/status/LATEST.md`, the annual report and every customer
file on origin at 14:41 on 2026-09-16, and the publisher recorded `push_did_not_reach_origin`.
`.publish_gate_state.json` read `last_clean_publish: null`, `episode_clean_publishes: 0`,
`episode_failures: 41`, six days into a wedge that was over.

BOTH LEGS ARE NEEDED AND THE CONTROLS PROVE IT SEPARATELY. At the instant the publisher pushed,
`05add41ab` was not yet on origin -- the reconciler carried it there minutes later -- so ancestry
alone would ALSO have answered False. The predicate's shape and the verdict's timing are two
defects, and `test_neither_leg_alone_would_have_recorded_the_clean_publish` is the one that says so.

WHAT MUST NOT WEAKEN. The equality test was not arbitrary: the 2026-07-24 origin-freeze had a bare
`git push` return rc=0 while origin stood still, a push time recorded anyway, and 3.5 hours of
every real push deferring behind a success that never happened. Reachability keeps that guard's
whole strength -- on a phantom rc=0 against an origin at an OLDER commit, ours is not an ancestor
of it -- and `test_the_phantom_up_to_date_is_still_refused` is the control that holds it there.
"""
from __future__ import annotations

import ast
import inspect
import subprocess
import textwrap
import types
from pathlib import Path

import pytest

from background import process_run_complete as prc
from background import publish_freshness as pf

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The publish that reached origin while the publisher recorded that it had not. A real commit and
#: a durable fact -- once a commit is an ancestor of `origin/main` it stays one -- so this control
#: is keyed to the instance the finding was written about and cannot drift off it.
LIVE_INSTANCE = "05add41ab"


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, "git {}: {}{}".format(" ".join(args), r.stdout, r.stderr)
    return r.stdout.strip()


def _chain(tmp_path: Path) -> tuple[Path, str, str, str]:
    """A three-commit line A -> B -> C in a throwaway repo. Returns (repo, A, B, C).

    A REAL REPOSITORY, not a stub, because the subject is a question only git can answer: `B` is an
    ancestor of `C` and is not equal to it, which is exactly the shape a disjoint publish has once
    the reconciler has merged it onto origin's line. A fake `subprocess.run` here would be a
    control probing its own fixture.
    """
    repo = tmp_path / "chain"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
    shas = []
    for n in ("a", "b", "c"):
        (repo / n).write_text(n)
        _git(repo, "add", n)
        _git(repo, "commit", "-q", "--no-verify", "-m", n)
        shas.append(_git(repo, "rev-parse", "HEAD"))
    return repo, shas[0], shas[1], shas[2]


def _equality_predicate(push_rc: int, remote_head: str, local_head: str) -> bool:
    """The predicate as it stood before this repair, kept here so the disagreement is MEASURED.

    A control that only asserts the new answer cannot tell a fix from a tautology. Every test below
    that claims the shape changed asserts both sides.
    """
    return push_rc == 0 and bool(remote_head) and remote_head == local_head


# ── LEG ONE: THE PREDICATE'S SHAPE ──────────────────────────────────────────────────────────────

def test_a_publish_that_reached_origin_behind_the_tip_is_graded_reached(tmp_path, monkeypatch):
    """THE DEFECT. Our commit is on origin and is not origin's head, and the two predicates
    disagree about whether that is a publish.

    MUTATION: restore `remote_head == local_head` as the whole body of `_push_reached_origin` and
    this fails on its first assertion.
    """
    repo, _a, ours, tip = _chain(tmp_path)
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)

    assert prc._push_reached_origin(0, tip, ours) is True
    assert _equality_predicate(0, tip, ours) is False, (
        "the two predicates must DISAGREE on this case -- if they agree, the shape did not change")


def test_the_phantom_up_to_date_is_still_refused(tmp_path, monkeypatch):
    """THE 2026-07-24 GUARD, AT FULL STRENGTH. rc=0 and origin standing still at an OLDER commit:
    our commit is not an ancestor of it, so the verdict is False and the throttle is untouched.

    MUTATION: make `_push_reached_origin` return True on rc==0 alone, or ask ancestry in the wrong
    direction (`is the remote head an ancestor of ours`), and this fails.
    """
    repo, older, _b, ours = _chain(tmp_path)
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)

    assert prc._push_reached_origin(0, older, ours) is False
    # And the two predicates AGREE here, which is the point: nothing was traded away.
    assert _equality_predicate(0, older, ours) is False


def test_an_unanswerable_ancestry_question_fails_closed(tmp_path, monkeypatch):
    """R15 FAIL-SILENT. A tip this repository has never fetched, a broken git, an empty ls-remote:
    every one of them is 'no evidence it reached origin' and never a success."""
    repo, _a, ours, _c = _chain(tmp_path)
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)

    assert prc._push_reached_origin(0, "0" * 40, ours) is False          # tip we do not hold
    assert prc._push_reached_origin(0, "", ours) is False                # ls-remote said nothing
    assert prc._push_reached_origin(0, "abc", "") is False               # no local head
    assert prc._push_reached_origin(1, "abc", "abc") is False            # transport error

    def _explode(*a, **k):
        raise OSError("git is gone")

    assert prc._commit_is_ancestor("a", "b", _run=_explode) is False


def test_the_named_live_instance_is_graded_reached():
    """THE INSTANCE THE FINDING WAS WRITTEN ABOUT, on the real repository.

    `05add41ab` carried the full figure surface to origin on 2026-09-16 and was recorded as
    `push_did_not_reach_origin`. This asks the real predicate about the real commit against the
    real `origin/main`, and requires the old one to have got it wrong.
    """
    have = subprocess.run(["git", "cat-file", "-e", LIVE_INSTANCE + "^{commit}"],
                          cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
    if have.returncode != 0:
        pytest.skip("this checkout does not hold {} (shallow clone)".format(LIVE_INSTANCE))
    # A RESOLVED SHA OR NOTHING. `git rev-parse` ECHOES ITS ARGUMENT on a ref that does not
    # exist -- rc=128, the name on stdout -- and the gate's clean extract has no `origin` remote
    # at all, so the unchecked read handed this control the literal string `origin/main` as a
    # tip and it failed there while being green on the real checkout. A question the environment
    # cannot answer is a SKIP; only a 40-hex sha is an answer.
    def _sha(rev: str) -> str:
        r = subprocess.run(["git", "rev-parse", rev], cwd=str(REPO_ROOT),
                           capture_output=True, text=True, timeout=30)
        out = r.stdout.strip()
        return out if r.returncode == 0 and len(out) == 40 else ""

    tip, ours = _sha("origin/main"), _sha(LIVE_INSTANCE)
    if not tip or not ours or tip == ours:
        pytest.skip("origin/main is unreadable here, or has not moved past the instance")

    assert prc._push_reached_origin(0, tip, ours) is True, (
        "the commit that put LATEST.md, the annual report and every customer file on origin is "
        "still graded as a push that did not reach origin")
    assert _equality_predicate(0, tip, ours) is False, (
        "the old predicate must be shown getting this instance wrong, or this control is not "
        "about the defect")


# ── LEG TWO: WHEN THE VERDICT IS TAKEN ──────────────────────────────────────────────────────────

def test_only_a_lost_race_over_paths_we_do_not_write_is_absorbable(monkeypatch):
    """The precondition, both ways round -- and `None` is not `[]`.

    MUTATION: write the collision test as `not _publish_surface_collisions(...)` and the
    'could not look' case flips to absorbable, which is the fail-open both halves exist to avoid.
    """
    race = "! [rejected] HEAD -> main (non-fast-forward)"
    fetch_first = "! [rejected] HEAD -> main (fetch first)"

    monkeypatch.setattr(prc, "_publish_surface_collisions", lambda p: [])
    assert prc._publish_is_absorbable(race, ["x"]) is True
    assert prc._publish_is_absorbable(fetch_first, ["x"]) is True, (
        "both of git's spellings for the same race must be matched -- that is why the classifier "
        "is borrowed from origin_reconcile rather than restated here")

    # A fork that lands on a path this commit writes is NOT a cadence's decision. The collision's
    # VALUE is never read -- only whether the list is empty -- and it is deliberately not spelled
    # as a real repo path: a `site/...` literal anywhere in a test file makes the whole `site`
    # tree read as this suite's subject in the whole-directory-subject census, and this suite's
    # subject is the publish verdict.
    monkeypatch.setattr(prc, "_publish_surface_collisions", lambda p: ["a-path-this-commit-writes"])
    assert prc._publish_is_absorbable(race, ["x"]) is False

    # "I could not look" is not "nothing collides".
    monkeypatch.setattr(prc, "_publish_surface_collisions", lambda p: None)
    assert prc._publish_is_absorbable(race, ["x"]) is False

    # And a push that failed for any other reason is not a race to be absorbed.
    monkeypatch.setattr(prc, "_publish_surface_collisions", lambda p: [])
    assert prc._publish_is_absorbable("fatal: Authentication failed", ["x"]) is False
    assert prc._publish_is_absorbable(None, ["x"]) is False


def test_the_recovery_runs_the_reconciler_and_re_reads_the_REMOTE(monkeypatch):
    """The recovery's two obligations: run the absorbing cadence, then ask the REMOTE what it has.

    MUTATION: return the local tracking ref (`git rev-parse origin/main`) instead of `ls-remote`'s
    answer and this fails -- the whole 2026-07-24 lesson is that the tracking ref is not evidence.
    """
    seen = {"reconciled": 0, "argv": []}

    def _fake_reconcile(*a, **k):
        seen["reconciled"] += 1
        return {"status": "RECONCILED", "detail": "merged 1 commit(s)", "pushed": True}

    import background.origin_reconcile as orc
    monkeypatch.setattr(orc, "reconcile", _fake_reconcile)

    def _fake_run(argv, **kwargs):
        seen["argv"].append(list(argv))
        out = "NEWTIP\trefs/heads/main\n" if argv[:2] == ["git", "ls-remote"] else ""
        return types.SimpleNamespace(returncode=0, stdout=out, stderr="")

    monkeypatch.setattr(prc.subprocess, "run", _fake_run)

    assert prc._reconcile_then_reread_origin() == "NEWTIP"
    assert seen["reconciled"] == 1
    assert any(a[:2] == ["git", "fetch"] for a in seen["argv"]), (
        "without a fetch, `merge-base --is-ancestor` cannot be asked about the merge the "
        "reconciler just pushed -- it answers only about objects this repository holds")
    assert any(a[:2] == ["git", "ls-remote"] for a in seen["argv"])
    assert not any("rev-parse" in a for a in seen["argv"]), (
        "the evidence must be the remote, never the local tracking ref")


def test_a_reconciler_that_cannot_run_still_fails_closed(monkeypatch):
    """The recovery may never turn an unknown into a success. If the cadence cannot run and the
    remote cannot be read, the sha is empty and `_push_reached_origin` refuses on it."""
    import background.origin_reconcile as orc

    def _explode(*a, **k):
        raise RuntimeError("worktree is wedged")

    monkeypatch.setattr(orc, "reconcile", _explode)
    monkeypatch.setattr(prc.subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(returncode=1, stdout="", stderr=""))

    tip = prc._reconcile_then_reread_origin()
    assert tip == ""
    assert prc._push_reached_origin(0, tip, "OURS") is False


def test_neither_leg_alone_would_have_recorded_the_clean_publish(tmp_path, monkeypatch):
    """THE SEQUENCE THAT ACTUALLY HAPPENED ON 2026-09-16, replayed as three gradings.

    At the instant of the push origin was at `B` and our commit `D` was not on it, so BOTH
    predicates answered False -- that is the measurement that makes the timing a second defect
    rather than a restatement of the first. Only after the reconciler merged `D` onto origin's line
    does reachability answer True, and equality still does not.

    MUTATION: delete the recovery (never call `_reconcile_then_reread_origin`) and the third
    grading is taken against `before`, which is False. Restore equality and it is False too.
    """
    repo = tmp_path / "sequence"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
    for n in ("a", "b"):
        (repo / n).write_text(n)
        _git(repo, "add", n)
        _git(repo, "commit", "-q", "--no-verify", "-m", n)
    before = _git(repo, "rev-parse", "HEAD")           # where origin stood at the push

    # Our publish commit, created on an older base -- the disjoint publish-while-behind.
    _git(repo, "checkout", "-q", "-b", "publish", "HEAD~1")
    (repo / "site_data").write_text("figures")
    _git(repo, "add", "site_data")
    _git(repo, "commit", "-q", "--no-verify", "-m", "publish")
    ours = _git(repo, "rev-parse", "HEAD")
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)

    # 1. The verdict as the publisher took it -- and ancestry agrees with equality here.
    assert _equality_predicate(0, before, ours) is False
    assert prc._push_reached_origin(0, before, ours) is False, (
        "at the instant of the push our commit was NOT on origin, so leg one alone changes "
        "nothing -- if this passes, the second leg has no measured justification")

    # 2. The cadence the commit was created to be absorbed by.
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-verify", "--no-ff", "-m", "reconcile", "publish")
    after = _git(repo, "rev-parse", "HEAD")

    # 3. The verdict re-taken against the remote as it now stands.
    assert prc._push_reached_origin(0, after, ours) is True
    assert _equality_predicate(0, after, ours) is False, (
        "equality can NEVER grade this publish as reached, whenever it is asked")


# ── THE WIRING, because a correct helper nothing calls is not a repair ──────────────────────────

def _git_commit_push_ast() -> ast.FunctionDef:
    return ast.parse(textwrap.dedent(inspect.getsource(prc.git_commit_push))).body[0]


def test_the_recovery_is_called_from_the_publish_path_and_OUTSIDE_the_tree_lock():
    """`origin_reconcile.advance_shared_tree` takes the SAME flock this function holds, and flock
    is held per open-file-description -- a second acquisition from this process blocks against
    itself until the lock timeout, leaving the shared tree behind origin. So the recovery has to
    sit after the `with stack:` block, and that is a property, not a preference.

    MUTATION: move the `_reconcile_then_reread_origin()` call inside the `with stack:` body and
    this fails.
    """
    fn = _git_commit_push_ast()
    calls = [n for n in ast.walk(fn)
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_reconcile_then_reread_origin"]
    assert len(calls) == 1, (
        "the publish path must reach the absorbing cadence exactly once -- {} call(s) found"
        .format(len(calls)))

    locked = [w for w in ast.walk(fn)
              if isinstance(w, ast.With) and ast.unparse(w.items[0].context_expr) == "stack"]
    assert locked, (
        "no `with stack:` block was found in git_commit_push, so this control has nothing to "
        "measure and would pass whatever the recovery did -- the tree-lock body was renamed")
    inside = {id(n) for w in locked for n in ast.walk(w)}
    assert id(calls[0]) not in inside, (
        "the reconciler is invoked while this process holds the tree lock; "
        "`advance_shared_tree` takes that same lock and will block against us")


def test_the_remote_ref_has_exactly_one_reader():
    """ONE READER FOR BOTH PUSH SITES. The content push and the liveness push each carried their
    own copy of the ls-remote read, and the rule they both implement -- the evidence is the remote,
    never the tracking ref -- is the kind that drifts in one copy and not the other.

    MUTATION: hand-roll a second `git ls-remote` beside either push and this fails.
    """
    src = Path(prc.__file__).read_text()
    assert src.count('"ls-remote"') == 1, (
        "process_run_complete has {} hand-rolled ls-remote reads; `_origin_main_sha` is the one "
        "reader".format(src.count('"ls-remote"')))


# ── THE SECOND READER OF THE SAME FALSE STATE ───────────────────────────────────────────────────

def test_the_freshness_line_asks_git_and_not_only_its_own_stamp(tmp_path, monkeypatch):
    """`publish.describe` told the delivery brief "figures reached origin 159.8h ago" three hours
    after `05add41ab` put those figures on origin, because this module's clock was a stamp written
    only when the publisher graded its own push True -- the same false state, read from a second
    place. Repairing the publisher alone would have left the sentence wrong until the NEXT publish.

    MUTATION: make `last_published_ts` read the stamp alone and this fails.
    """
    monkeypatch.setattr(pf, "STATE_FILE", tmp_path / ".last_content_publish.json")
    now = 1_000_000.0
    pf.record_published(now=now - 160 * 3600)                    # the stale, wrong stamp
    monkeypatch.setattr(pf, "content_on_origin_ts",
                        lambda **k: now - 3 * 3600)              # git: the figures ARE on origin

    assert pf.last_published_ts() == now - 3 * 3600
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - 3 * 3600)
    snap = pf.snapshot(now=now)
    assert snap["state"] == "publishing"
    assert "3.0h" in pf.describe(snap), pf.describe(snap)


def test_a_tracking_ref_that_is_behind_cannot_veto_a_fresh_stamp(tmp_path, monkeypatch):
    """The other direction. `refs/remotes/origin/main` moves on fetch and on push, so it can be
    BEHIND the remote -- and a source that can only MISS a publish must never be able to overrule
    one that saw it. The newer of the two wins, and each can only ever say yes."""
    monkeypatch.setattr(pf, "STATE_FILE", tmp_path / ".last_content_publish.json")
    now = 1_000_000.0
    pf.record_published(now=now - 60)
    monkeypatch.setattr(pf, "content_on_origin_ts", lambda **k: now - 99 * 3600)
    assert pf.last_published_ts() == now - 60

    # And an unreadable git is UNKNOWN from that source, never fresh and never a veto.
    monkeypatch.setattr(pf, "content_on_origin_ts", lambda **k: None)
    assert pf.last_published_ts() == now - 60
    pf.STATE_FILE.unlink()
    assert pf.last_published_ts() is None


def test_a_fresh_stamp_over_frozen_figures_still_reads_stale(monkeypatch):
    """THE 28-HOUR OUTAGE OF 2026-08-21, re-asked after this change. The stamp is written on any
    verified push whatever paths moved, so a provenance banner refreshed it every cycle while the
    figures sat still. `snapshot` closed that by taking the OLDER of the two clocks, and widening
    where the publish clock comes from must not reopen it."""
    now = 1_000_000.0
    frozen = pf.STALE_AFTER_SECONDS + 3600
    monkeypatch.setattr(pf, "last_published_ts", lambda: now - 780)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: now - frozen)
    snap = pf.snapshot(now=now)
    assert snap["state"] == "stale"
    assert pf.is_publishing_down(snap) is True
