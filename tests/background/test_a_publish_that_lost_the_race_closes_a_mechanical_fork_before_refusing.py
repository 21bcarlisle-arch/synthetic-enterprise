"""THE DEFECT: a publish cycle that spent a full simulation and a 672s gate was discarded at the
door because origin had moved while it ran -- and nothing tried to close the fork before dropping
the work.

Measured 2026-09-04 (`SEAT_FINDING_THE_RECONCILER_AND_THE_PUBLISHER_EACH_STAND_DOWN_FOR_THE_OTHER
_AND_THE_TREE_STAYED_BEHIND_ORIGIN_2026-09-04.md`): one publish cycle 672s median, n=7, spread 65s;
commits arriving on `origin/main` every 3.8 min median, n=61. **~2.9 arrive during one cycle**, and
`BEHIND_ORIGIN` is evaluated once, at the end of it. `13:05`, `14:27`, `15:48` -- each after a
GREEN gate and a verified provenance, each *"Done, but THE PUBLISH DID NOT LAND"*. The publish gate
state read `episode_clean_publishes 0, last_clean_publish null` against a queue that had reached
zero: the drain was TRUE and UNRECORDABLE, because nothing records a success that never commits.

And the reconciler built to close that fork out of band stands down for this gate
(`origin_reconcile.gate_is_running`) while this gate stands down for the fork
(`_divergence_refusal`). Both refusals are right; the tree stays behind anyway.

WHAT IS ASSERTED HERE. `_advance_to_origin_or_say_why` closes the fork exactly where closing it is
MECHANICAL -- a fast-forward, nothing of ours to land, git's own refusal as the guard -- and
refuses, naming its reason, everywhere else. Real git repositories throughout: git's refusal IS the
safety argument, so a fake runner asserting against a stub would be a tautology.
"""
from __future__ import annotations

import ast
import inspect
import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest

from background import process_run_complete as prc


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=120)


def _identify(repo: Path) -> None:
    _git(repo, "config", "user.email", "seat@example.invalid")
    _git(repo, "config", "user.name", "seat")


@pytest.fixture
def forked(tmp_path):
    """`(local, origin, other)` -- a clone that is ONE commit behind its origin.

    Built with real git because the property under test is git's own `--ff-only` refusal. The
    incoming commit touches `shared.txt`, so each case below can decide whether it collides.
    """
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", str(origin))

    local = tmp_path / "local"
    _git(tmp_path, "clone", str(origin), str(local))
    _identify(local)
    (local / "shared.txt").write_text("A\n")
    _git(local, "add", "shared.txt")
    _git(local, "commit", "-m", "A")
    _git(local, "push", "origin", "HEAD:main")

    other = tmp_path / "other"
    _git(tmp_path, "clone", str(origin), str(other))
    _identify(other)
    (other / "shared.txt").write_text("A\nB\n")
    (other / "arriving.txt").write_text("from origin\n")
    _git(other, "add", "shared.txt", "arriving.txt")
    _git(other, "commit", "-m", "B")
    _git(other, "push", "origin", "HEAD:main")

    return local, origin, other


@pytest.fixture
def unlocked(monkeypatch):
    """The advance takes the SHARED tree lock, which belongs to the real project directory and is
    contended by a live daemon. A test that waited on it would be grading the daemon's schedule.

    Neutralised here, and the lock is asserted separately and structurally by
    `test_the_advance_writes_the_shared_tree_under_the_tree_lock` -- so removing the lock from the
    code still fails a control, which is the point of splitting them.
    """
    @contextmanager
    def _no_lock():
        yield

    monkeypatch.setattr(prc, "tree_lock", _no_lock)


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _origin_head(origin_bare: Path) -> str:
    """Read the BARE repo, not the clone's `origin/main` tracking ref -- that ref is only as fresh
    as the last fetch, and reading it here would make the precondition and the verdict agree by
    construction rather than by fact. Same lesson `_commits_origin_is_ahead_by` carries."""
    return _git(origin_bare, "rev-parse", "main").stdout.strip()


# ── the whole partition in one control ──────────────────────────────────────────────────────
def test_the_advance_takes_all_three_of_its_verdicts_and_not_one_of_them_always(forked, unlocked,
                                                                                tmp_path):
    """A guard that refuses EVERYTHING passes every leg-by-leg refusal test written below, and a
    guard that advances everything passes the one that matters. So the partition is asserted
    together, first: all three verdicts must be REACHABLE from the same function.

    Learned the hard way in this repo -- "when a branch exists to be taken rarely, assert it CAN be
    taken before asserting what it does".
    """
    local, _origin, _other = forked

    # 1. mechanical: behind, clean, nothing of ours.
    mechanical = prc._advance_to_origin_or_say_why(local)

    # 2. a fork of our own: a local commit means origin cannot be fast-forwarded onto.
    ours = tmp_path / "ours"
    _git(tmp_path, "clone", str(tmp_path / "origin.git"), str(ours))
    _identify(ours)
    _git(ours, "reset", "--hard", "HEAD~1")
    (ours / "mine.txt").write_text("mine\n")
    _git(ours, "add", "mine.txt")
    _git(ours, "commit", "-m", "C")
    real_fork = prc._advance_to_origin_or_say_why(ours)

    # 3. git's own refusal: a local edit to a file the incoming commit changes.
    dirty = tmp_path / "dirty"
    _git(tmp_path, "clone", str(tmp_path / "origin.git"), str(dirty))
    _identify(dirty)
    _git(dirty, "reset", "--hard", "HEAD~1")
    (dirty / "shared.txt").write_text("A\nlocal edit\n")
    collision = prc._advance_to_origin_or_say_why(dirty)

    assert mechanical["advanced"] and not real_fork["advanced"] and not collision["advanced"], (
        "all three verdicts must be reachable: mechanical={} real_fork={} collision={}".format(
            mechanical, real_fork, collision))
    # And they must be told apart by their REASON, not merely by the boolean -- two refusals that
    # read alike leave the reader to rediscover which one happened.
    assert real_fork["reason"] != collision["reason"]


# ── what each verdict actually does ─────────────────────────────────────────────────────────
def test_a_mechanical_fork_is_closed_so_the_completed_cycle_can_commit(forked, unlocked):
    """The defect itself: behind origin, nothing of ours, nothing colliding -- the cycle's work was
    dropped. It must now be publishable, and the tree must really be level afterwards rather than
    merely reported so."""
    local, origin, _other = forked
    assert _head(local) != _origin_head(origin), "precondition: the clone starts behind"

    result = prc._advance_to_origin_or_say_why(local)

    assert result["advanced"] is True
    assert _head(local) == _origin_head(origin), "the tree must actually be level, not just claim it"
    assert (local / "arriving.txt").exists(), "a fast-forward updates the WORKING TREE too -- a " \
        "ref moved past its own checkout is the silent revert this must not arm"


def test_a_commit_of_our_own_is_never_fast_forwarded_away(forked, unlocked, tmp_path):
    """`ahead > 0` is a REAL fork: closing it is a judgement and needs the gated merge door. This
    path must leave it entirely alone, and say which door owns it.

    THE DOOR ASSERTION WAS KEYED TO THE WRONG DOOR (corrected 2026-09-04, later the same day).
    It demanded the literal `surgical_land --merge`, which names the act that opens the SHARED
    index -- the very thing this refusal's own docstring refuses to do unattended because
    "routinely three lanes have uncommitted work in this tree". The owner is
    `background/origin_reconcile`, which runs that same gated merge in an ISOLATED worktree. So
    the assertion now asks for the OWNER rather than for a command string, which is the property
    it always meant: a refusal for a state something else owns must name that something.
    See `SEAT_FINDING_THE_RECONCILER_IS_NOT_STARVED...` and
    `tests/background/test_a_forks_refusal_points_at_a_door_that_is_safe_in_the_shared_tree.py`.
    """
    ours = tmp_path / "ours"
    _git(tmp_path, "clone", str(tmp_path / "origin.git"), str(ours))
    _identify(ours)
    _git(ours, "reset", "--hard", "HEAD~1")
    (ours / "mine.txt").write_text("mine\n")
    _git(ours, "add", "mine.txt")
    _git(ours, "commit", "-m", "C")
    before = _head(ours)

    result = prc._advance_to_origin_or_say_why(ours)

    assert result["advanced"] is False
    assert _head(ours) == before, "our commit must still be here"
    assert "origin_reconcile" in result["reason"], "the refusal must name the door that owns it"


def test_another_lanes_uncommitted_work_makes_git_refuse_and_that_refusal_stands(forked, unlocked,
                                                                                 tmp_path):
    """THE SAFETY ARGUMENT, and it is git's rather than ours: a fast-forward cannot advance over a
    locally-modified incoming path, so another lane's work in this shared tree is never at risk.

    MUTATION: `--ff-only` -> `--no-ff` (or a `-X theirs`) and this fails, which is the state that
    would overwrite the other lane."""
    dirty = tmp_path / "dirty"
    _git(tmp_path, "clone", str(tmp_path / "origin.git"), str(dirty))
    _identify(dirty)
    _git(dirty, "reset", "--hard", "HEAD~1")
    (dirty / "shared.txt").write_text("A\nanother lane was here\n")
    before = _head(dirty)

    result = prc._advance_to_origin_or_say_why(dirty)

    assert result["advanced"] is False
    assert _head(dirty) == before
    assert (dirty / "shared.txt").read_text() == "A\nanother lane was here\n"
    assert "REFUSED" in result["reason"]


def test_an_unreadable_ahead_count_is_not_read_as_zero(forked, unlocked):
    """`None` is a third answer. Folding it into `0` would advance the tree in precisely the state
    where nothing about the fork was observed -- the fail-open shape `commits_ahead` exists to
    refuse."""
    local, _origin, _other = forked
    before = _head(local)

    result = prc._advance_to_origin_or_say_why(local, ahead_fn=lambda _p: None)

    assert result["advanced"] is False
    assert _head(local) == before
    assert "never observed" in result["reason"] or "could not be established" in result["reason"]


def test_an_unreachable_origin_leaves_the_tree_exactly_where_it_was(forked, unlocked, tmp_path):
    """Fail closed on an unreadable world: if the fetch does not answer, the ref this would advance
    onto was never read, so nothing may move."""
    local, _origin, _other = forked
    _git(local, "remote", "set-url", "origin", str(tmp_path / "does-not-exist.git"))
    before = _head(local)

    result = prc._advance_to_origin_or_say_why(local)

    assert result["advanced"] is False
    assert _head(local) == before
    assert "fetch" in result["reason"]


@pytest.mark.parametrize("boom", [OSError("no git today"),
                                  subprocess.TimeoutExpired("git", 1),
                                  ValueError("something nobody predicted")])
def test_it_never_raises_into_the_publish_cycle(forked, boom):
    """A publish path that must finish cannot be taken down by its own RECOVERY attempt. The only
    thing this function's failure may cost is the refusal that would have happened anyway; an
    uncaught exception costs rc=1, which the wedge classifier reads as a red test.

    The unpredicted `ValueError` leg is the one that matters: a catch narrowed to the two git
    exceptions passes the first two and lets the third out.
    """
    local, _origin, _other = forked

    def _explode(_argv, _timeout):
        raise boom

    result = prc._advance_to_origin_or_say_why(local, runner=_explode)
    assert result["advanced"] is False
    assert type(boom).__name__ in result["reason"], "the cause must ride out, not be swallowed"


# ── the structural properties the behaviour above cannot pin ────────────────────────────────
def _git_argvs(fn) -> list[list[str]]:
    """Every literal `["git", ...]` argv in a function, read from the AST rather than by grepping
    prose -- the docstring here discusses merging at length, and a check that reads prose cannot
    tell an argument about a merge from an act of one."""
    out = []
    for node in ast.walk(ast.parse(inspect.getsource(fn))):
        if isinstance(node, ast.List) and node.elts:
            first = node.elts[0]
            if isinstance(first, ast.Constant) and first.value == "git":
                out.append([e.value for e in node.elts if isinstance(e, ast.Constant)])
    return out


def test_it_is_only_ever_a_fast_forward_and_never_a_force_and_never_a_commit():
    """It may move a ref onto a commit origin already holds. It may never CREATE one -- a commit
    from here is the fork-widening retry `_divergence_refusal` was built to stop -- and it may
    never override git's refusal, which is the whole safety argument."""
    argvs = _git_argvs(prc._advance_to_origin_or_say_why)
    assert ["git", "merge", "--ff-only", "origin/main"] in argvs
    flat = [tok for argv in argvs for tok in argv]
    assert "commit" not in flat, "this path may not create a commit"
    assert not [t for t in flat if t in ("--force", "-f", "--no-ff", "--no-verify")]


def test_the_advance_writes_the_shared_tree_under_the_tree_lock():
    """It updates the shared working tree, so it serialises against every other git writer -- the
    exact contention `tree_lock` exists for. Split from the behavioural tests, which neutralise the
    lock, so removing it still fails something.

    MUTATION: unindent the merge out of the `with` and this fails.
    """
    src = inspect.getsource(prc._advance_to_origin_or_say_why)
    tree = ast.parse(src)
    inside = []
    for node in ast.walk(tree):
        if isinstance(node, ast.With) and "tree_lock" in ast.unparse(node.items[0].context_expr):
            inside = [tok for stmt in node.body for tok in ast.unparse(stmt).split()]
    assert inside, "the advance must take tree_lock()"
    assert any("--ff-only" in tok for tok in inside), "the merge must be INSIDE the lock"


def test_the_publisher_tries_the_advance_and_then_RE_READS_before_refusing():
    """The wiring, and the re-read is half of it. `origin_reconcile` paid 29 empty merges to learn
    that acting is not the same as having acted; a commit landing during the ~1s advance leaves
    this tree behind again and that is a real refusal.

    MUTATION: delete the second `_divergence_refusal()` and the count drops to 1; delete the
    advance call and the first assertion fails.
    """
    tree = ast.parse(inspect.getsource(prc.git_commit_push))
    calls = [n.func.id for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert calls.count("_advance_to_origin_or_say_why") == 1, \
        "the publisher must try to earn its commit before dropping a whole cycle's work"
    assert calls.count("_divergence_refusal") == 2, \
        "the state must be RE-READ after the advance, never assumed"


def test_the_refusal_still_names_why_the_advance_did_not_clear_it():
    """A refusal that says why is how the refusal itself gets found wrong. `BEHIND_ORIGIN` now has
    two distinct causes -- the fork was real, or git refused the advance -- and a reader who cannot
    tell them apart rediscovers which by hand, as three separate seats did.

    Asserted on the `_outcome(BEHIND_ORIGIN, ...)` call itself: its `evidence` must CARRY the
    advance's reason. A source grep would pass on the reason merely being computed and dropped.

    MUTATION: revert `evidence=` to the bare `_behind` and this fails.
    """
    carriers = []
    for node in ast.walk(ast.parse(inspect.getsource(prc.git_commit_push))):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_outcome"):
            continue
        if not (node.args and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "BEHIND_ORIGIN"):
            continue
        evidence = [kw.value for kw in node.keywords if kw.arg == "evidence"]
        assert evidence, "the BEHIND_ORIGIN outcome must still carry evidence"
        carriers.append("_why_not" in ast.unparse(evidence[0]))
    assert carriers and all(carriers), \
        "every BEHIND_ORIGIN refusal must say why the mechanical advance did not clear it"


def test_the_refusal_function_itself_still_only_reports():
    """`test_the_publish_paths_refusal_is_untouched` in the sibling suite asserts this and it stays
    true: the ACT lives in its own function, and `_divergence_refusal` remains a pure read. Kept
    here too because that sibling guards a different module's contract and could be retired for
    reasons that have nothing to do with this one.

    `merge` is NOT forbidden in this body: the refusal names `surgical_land --merge` as the remedy,
    which is text about a merge and not one. What is forbidden is running anything."""
    fn = ast.parse(inspect.getsource(prc._divergence_refusal)).body[0]
    body = fn.body[1:] if isinstance(fn.body[0], ast.Expr) else fn.body
    code = "\n".join(ast.unparse(n) for n in body)
    assert "AHEAD of HEAD" in code
    assert "subprocess" not in code and "run(" not in code
    assert "_advance_to_origin_or_say_why" not in code, \
        "the act stays at the CALL SITE, so the reporter can never become the actor"
