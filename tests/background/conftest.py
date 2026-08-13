"""Directory-scoped test isolation for the supervisor draw/rest ladder.

CLASS FIX (R10), 2026-07-24, WEDGE3_AND_RUNG1_MECHANISE: the RUNG-1 publish-gate-wedge
detector (`supervisor._publish_gate_wedge_active`, wired as the TOP rung of both
`_self_refill_draw` and `_is_drained_and_gated`) reads the REAL on-disk
`.publish_gate_state.json` + `.last_tested_hash`. Any test in this directory that exercises
the draw/rest ladder WITHOUT isolating those two files silently leaks the live gate state: when
the real gate is wedged AND HEAD != last_tested_hash, the rung fires and every "map empty -> rest"
/ "draws forward-discovery" assertion flips (12 such tests red-ed the publish gate the moment the
rung landed -- the fork's own full-suite run false-greened only because HEAD == last_tested_hash
at that instant kept the detector transiently silent).

This is the exact "new always-drawable rung needs fixture isolation" class the F-lane draw hit
before (see test_supervisor.py::_isolate). Rather than re-patch each file on touch, this autouse
fixture neutralises the leak for the WHOLE directory: it points both state files at a clean,
absent tmp path (an absent/empty state => detector returns None => no phantom wedge). The one
test that genuinely needs a wedged state (test_publish_gate_wedge_draw.py) writes it in the test
BODY via its own monkeypatch, which runs after this fixture's setup and therefore wins; the tests
that already isolate explicitly (test_supervisor.py::_isolate) merely point at a different clean
tmp -- also non-wedged, so correctness is unaffected either way.
"""
import os
import subprocess
from pathlib import Path

import pytest

from background import gap_ledger_reconciler, supervisor
from tests.background import env_constant_sync as _env_sync

REPO_ROOT = Path(__file__).resolve().parents[2]
_GIT_DIR = REPO_ROOT / ".git"


@pytest.fixture(autouse=True)
def _isolate_publish_gate_wedge_state(tmp_path, monkeypatch):
    """Default every test in tests/background/ to a NON-wedged publish-gate state so the
    RUNG-1 wedge detector cannot leak the real gate state into unrelated draw/rest assertions.
    Tests that need a specific wedged state override these paths in their own body."""
    monkeypatch.setattr(
        supervisor, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json", raising=False
    )
    monkeypatch.setattr(
        supervisor, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash", raising=False
    )
    # RUNG-7 PLANNER (director ruling WORK_IS_THE_DEFAULT 2026-07-23): the planner reads the real
    # DIRECTOR_AXES.md, which is populated -> planner fires -> rest is never legitimate. That would
    # flip every "map empty -> rest" assertion in this dir (same fixture-isolation class as the wedge
    # state above). Default the axes path to an ABSENT tmp file so the planner does NOT fire by
    # default; the R15 planner tests point it at a populated file explicitly.
    monkeypatch.setattr(
        supervisor, "DIRECTOR_AXES_PATH", tmp_path / "DIRECTOR_AXES_absent.md", raising=False
    )
    # EIGHTH CLASS (2026-07-27, DIRECTOR_RULING_EIGHTH_CLASS): the `blocked_mints` level (wired into
    # authorized_set_enumeration + _is_drained_and_gated) reads the REAL docs/staging/in_progress/
    # for parked PLANNER_MINTED_* mints -- the live tree routinely holds a blocked batch, which would
    # flip every "map empty -> rest" assertion in this dir (the exact fixture-isolation class this
    # conftest already fixes for the wedge state + axes). Default STAGING_DIR to a clean empty tmp so
    # no blocked mints leak in; the EIGHTH-CLASS tests write mints into their own tmp staging body.
    _staging = tmp_path / "staging_isolated"
    (_staging / "in_progress").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(supervisor, "STAGING_DIR", _staging, raising=False)
    # RUNG 1b OPERATIONAL-LAYER PERSISTENT-RED (director console 2026-07-25): the FOURTH instance of
    # the same class this fixture already fixes three times above -- `_operational_red_persistent_draw`
    # reads the REAL .operational_layer_signal.json and sits ABOVE every product/HARDEN lane, so
    # whenever the live operational suite is red it wins the draw and flips every "map empty -> rest" /
    # "draws lane X" assertion in this directory. It really was red on 2026-08-08 (consecutive_red 4),
    # and it red-ed the publish gate through two unrelated files
    # (test_forward_discovery_draw.py, test_governance_refusal.py) whose subjects have nothing to do
    # with it. Default to an ABSENT tmp path -- absent => detector returns None (proven by
    # test_operational_red_persistent_draw.py::test_silent_on_absent_file), so no phantom red. The
    # rung's own tests set this path in their body, which runs after this fixture and therefore wins.
    monkeypatch.setattr(
        supervisor, "OPERATIONAL_LAYER_SIGNAL_FILE",
        tmp_path / ".operational_layer_signal_absent.json", raising=False,
    )
    # RUNG 4b STALE-GAP-ROW (2026-08-10) -- the FIFTH instance of this same class, and the one that
    # wedged publishing for the ~13 minutes it took to find it. `_stale_gap_row_draw` holds no path
    # of its own: it imports `background.gap_ledger_reconciler` and reconciles the REAL
    # docs/observability/coupled_gap_ledger.json against the REAL git history. At HEAD that ledger
    # had 13 refreshable rows, so the rung fired and refused rest -- reddening ELEVEN tests across
    # this directory whose subjects (forward-discovery, propose-half) have nothing to do with gap
    # measurements. The tree passed the identical tests only because the working copy of the ledger
    # happened to be freshly re-rendered; the gate judges a clean HEAD checkout, so the wedge was
    # invisible locally. Pin the reconciler's LEDGER_PATH at an ABSENT tmp file: absent => an empty
    # ledger => no row is refreshable => the rung is silent (asserted, not assumed, by
    # test_rest_ladder_isolation.py::test_the_gap_rung_is_silent_under_this_fixture). The rung's own
    # tests inject `work=` directly, so this pin cannot weaken them.
    monkeypatch.setattr(
        gap_ledger_reconciler, "LEDGER_PATH",
        tmp_path / "coupled_gap_ledger_absent.json", raising=False,
    )
    # OPS13 PRODUCT INTERLEAVE (2026-08-13) -- the SIXTH instance, caught the day it landed and
    # isolated in the same breath. `_apply_product_interleave` runs on every three-lane grant and
    # PERSISTS the unpaid-harness ledger, so any test in this directory that exercises the draw
    # writes its synthetic atom ids into the LIVE docs/observability/.product_interleave_state.json
    # -- observed: `{"owed": ["H1_test_atom", "H1_test_atom"]}` from
    # test_supervisor_blocker_precedence.py. The leak runs the other way too (a real owed id makes
    # the next test's arm force a product-side draw it did not ask for). An absent tmp path is a
    # clean slate, which is the state every test in here that is not about the interleave wants.
    monkeypatch.setattr(
        supervisor, "PRODUCT_INTERLEAVE_STATE_FILE",
        tmp_path / ".product_interleave_state_absent.json", raising=False,
    )


# ── THE GHOST-PUSHER TRIPWIRE (issue #11) ────────────────────────────────────────────────────
# WHAT THIS CATCHES. background/ is the half of this repo that holds push credentials, and its
# publish path commits and pushes as an ordinary side-effect of an ordinary function call. A test
# in this directory that forgets to point PROJECT_DIR at a tmp tree therefore does not merely
# "leak state" the way the fixtures above do -- it manufactures a REAL commit on the REAL
# checkout and fires a REAL `git push origin HEAD:main`. That is the proven cause of every
# unexplained main push of the week: test_process_run_complete.py reached
# `_refresh_published_liveness_on_skip` on the real tree and made a `chore(liveness)... (git=abc)`
# commit, which failed to land only for want of credentials on the machine that ran it.
#
# WHY A TRIPWIRE AND NOT JUST THE FIX. The instance fix (isolate that file's tests) and the class
# fix (the seat guard on the side-effect itself) are both in this change, but neither of them
# stops the NEXT test in this directory from calling the next credential-holding function on the
# real tree. R10: an absurdity-class defect is not closed by an instance fix. This asserts the
# invariant directly -- NO test in tests/background/ may move the real repo's HEAD -- so the whole
# class fails automatically and loudly, naming the test and the commit it manufactured.
#
# TWO SCOPES, ON PURPOSE. The per-test check is the diagnostic one: it fails the exact test that
# committed, which is the thing a person needs to know. The session-scoped one is the outer
# bound -- it catches a commit made anywhere the per-test window does not cover (session-scoped
# fixture setup/teardown, collection, a detached child that lands its commit after the last test).
#
# COST. The per-test check reads .git/HEAD and one ref file: no subprocess, microseconds, so it is
# affordable on every test in the directory. `git log` runs only on the failure path.


def _real_repo_head() -> str:
    """The real checkout's current HEAD sha, read from .git directly (no subprocess).

    Returns a sentinel string rather than raising on anything unexpected: this is a
    tripwire, and a tripwire that explodes on an odd checkout would fail honest tests.
    A sentinel still compares equal to itself, so the before/after check stays valid --
    it simply cannot detect a move it could not read.
    """
    try:
        if not _GIT_DIR.exists():
            # NO REPOSITORY AT ALL -- the publish gate's clean HEAD checkout
            # (DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09) is a `git archive` extraction
            # with no .git, and there is no real checkout there for a test to ghost-push into.
            # Return a constant WITHOUT shelling out: the subprocess fallback below collided
            # with every test that stubs `subprocess.run`, whose stub answered this call with a
            # Mock/None and turned the tripwire into `AttributeError: 'NoneType' has no
            # attribute 'stdout'` -- 9 errors that exist only in the archive, never in the repo.
            # A constant also satisfies the tripwire honestly: before == after, nothing moved,
            # because nothing here could move.
            return "no-git-dir"
        if not _GIT_DIR.is_dir():  # worktree/submodule: .git is a file -> ask git once
            out = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT),
                capture_output=True, text=True, timeout=15,
            )
            # Defensive: a stubbed subprocess can return anything, and a tripwire that raises
            # is worse than one that cannot see.
            return (getattr(out, "stdout", "") or "").strip() or "unreadable"
        head = (_GIT_DIR / "HEAD").read_text().strip()
        if not head.startswith("ref: "):
            return head  # detached HEAD: the sha is right there
        ref = head[5:].strip()
        loose = _GIT_DIR / ref
        if loose.is_file():
            return loose.read_text().strip()
        packed = _GIT_DIR / "packed-refs"
        if packed.is_file():
            for line in packed.read_text().splitlines():
                if line.endswith(" " + ref):  # "<sha> <ref>"
                    return line.split()[0]
        return "unborn:" + ref
    except (OSError, subprocess.SubprocessError):
        return "unreadable"


# ── TRIPWIRE vs COLLEAGUE (EPISODE4 item 1, 2026-08-09) ──────────────────────────────────────
# The guard above compared HEAD before/after and blamed "this test session" for ANY move. On a box
# where an autonomous worker commits several times an hour and the suite takes ~11 minutes, that
# is not a tripwire, it is a collision detector: a real D14 build commit landing mid-run failed a
# 22,525-green suite, the publish gate booked it as `test_regression`, and publishing could only
# succeed in the lulls between colleagues' commits. MEASURED cause, twice.
#
# THE DISCRIMINATOR. Git records no PID, so attribution has to be arranged in advance: this
# process stamps a sentinel COMMITTER identity into its own environment at conftest import, before
# any test spawns anything. Every `git commit` reached from inside this pytest process -- however
# many subprocess layers down -- inherits it. A colleague's commit, made from a different process
# tree, cannot carry it. So `before..after` partitions cleanly into "mine" and "theirs", and only
# "mine" is a ghost push.
#
# WHY COMMITTER AND NOT AUTHOR. Author survives rebases, cherry-picks and `--author` overrides;
# committer records who actually performed the commit, which is exactly the question.
#
# FAIL-CLOSED ON UNATTRIBUTABLE (R15). If HEAD moved and the log cannot be read, the check cannot
# answer -- and an unavailable check is a FAILED check. That is rare (a git hiccup), unlike a
# concurrent commit, which is routine; so the split keeps the guard's teeth without paying the
# false-positive tax it was actually costing.
GHOST_SENTINEL_EMAIL = "pytest-ghost-tripwire@invalid"
os.environ.setdefault("GIT_COMMITTER_EMAIL", GHOST_SENTINEL_EMAIL)

_ROW_SEP = "\x1f"


def partition_commits(rows: list[tuple[str, str, str]]) -> tuple[list[str], list[str]]:
    """PURE (mutation-testable). rows = [(sha, committer_email, subject)].

    -> (mine, theirs): commits this pytest process committed, and commits it did not.
    Only `mine` is a ghost push; `theirs` is a colleague working normally and must be ignored."""
    mine = [f"{sha} {subj}" for sha, email, subj in rows if email == GHOST_SENTINEL_EMAIL]
    theirs = [f"{sha} {subj}" for sha, email, subj in rows if email != GHOST_SENTINEL_EMAIL]
    return mine, theirs


def _commit_rows(before: str, after: str) -> list[tuple[str, str, str]] | None:
    """(sha, committer_email, subject) for before..after; None if unreadable (-> fail-closed)."""
    try:
        out = subprocess.run(
            ["git", "log", f"--format=%h{_ROW_SEP}%ce{_ROW_SEP}%s", f"{before}..{after}"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=15,
        )
        if out.returncode != 0:
            return None
    except (OSError, subprocess.SubprocessError):
        return None
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split(_ROW_SEP, 2)
        if len(parts) == 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def ghost_verdict(before: str, after: str, rows: list[tuple[str, str, str]] | None,
                  where: str) -> str | None:
    """PURE (mutation-testable): the failure message, or None if this is not a ghost push.

    Kept pure and separate from `_assert_head_unmoved` deliberately -- the autouse per-test
    fixture below calls that function at teardown, so a test that monkeypatched its internals
    would trip the very tripwire it is testing. The decision has to be reachable without
    patching module globals."""
    if after == before:
        return None
    if rows is None:
        return (
            "GHOST PUSHER (unattributable): {} -- HEAD moved {} -> {} and `git log` could not be "
            "read, so this check could not tell a test's commit from a colleague's. R15: an "
            "unavailable check is a FAILED check.".format(where, before[:9], after[:9])
        )
    mine, theirs = partition_commits(rows)
    if not mine:
        return None  # a colleague committed while we ran -- routine here, never our tripwire
    return (
        "GHOST PUSHER: {} moved the REAL repo's HEAD.\n"
        "  {} -> {}\n"
        "  commit(s) THIS TEST PROCESS manufactured (committer {}):\n    {}\n"
        "{}"
        "A test in tests/background/ must never commit to the real checkout. This one reached a "
        "credential-holding publish path on the real tree -- almost always a missing "
        "`monkeypatch.setattr(<module>, \"PROJECT_DIR\", tmp_path)`. Isolate it; do not silence "
        "this fixture.".format(
            where, before[:9], after[:9], GHOST_SENTINEL_EMAIL,
            "\n    ".join(mine),
            "  (also in range, NOT ours: {})\n".format("; ".join(theirs)) if theirs else "",
        )
    )


def _assert_head_unmoved(before: str, where: str) -> None:
    after = _real_repo_head()
    if after == before:
        return
    msg = ghost_verdict(before, after, _commit_rows(before, after), where)
    if msg:
        pytest.fail(msg)


@pytest.fixture(autouse=True, scope="session")
def _no_test_may_commit_to_the_real_repo():
    """Outer bound: the real repo's HEAD is where it was when this session started."""
    before = _real_repo_head()
    yield
    _assert_head_unmoved(before, "this test session")


@pytest.fixture(autouse=True)
def _this_test_may_not_commit_to_the_real_repo(request):
    """Per-test tripwire: fails the exact test that manufactured the commit."""
    before = _real_repo_head()
    yield
    _assert_head_unmoved(before, request.node.nodeid)


# ── THE STALE-ENV-CONSTANT TRIPWIRE (H31) ────────────────────────────────────────────────────
# WHAT THIS CATCHES. A test that leaves a module-level env-derived constant (e.g.
# `background.ntfy_utils.WAKE_HMAC_KEY`) out of sync with os.environ poisons every later test in
# the process: four test_ntfy_utils.py signing tests failed purely on collection order while the
# test that broke them stayed green. Full rationale, and the AST-derived registry that makes this
# a CLASS guard rather than a list that decays, live in tests/background/env_constant_sync.py.
#
# WHY A HOOK AND NOT A FIXTURE. The defect IS a teardown-ordering defect, so the check must run
# after ALL fixture finalizers -- crucially after `monkeypatch` restores os.environ, since the
# expected value is computed FROM os.environ. A fixture finalizer's position relative to the
# test's own monkeypatch depends on setup order; `pytest_runtest_teardown(trylast=True)` is
# unambiguously last, because the internal impl that runs fixture finalizers is an ordinary
# hookimpl that trylast sorts behind. Verified empirically, not assumed.
#
# BASELINE-RELATIVE. Divergences already present when the session starts are recorded once and
# never re-reported, so a pre-existing oddity in the checkout cannot fail an unrelated test. Only
# a divergence a test INTRODUCES is attributed to it.

_ENV_CONSTANT_REGISTRY = _env_sync.build_registry()
_ENV_CONSTANT_BASELINE_BAD: set[str] = {
    c.dotted for c, _a, _e in _env_sync.diverged(_ENV_CONSTANT_REGISTRY)
}


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    """Fail the test that desynchronised a module env constant -- and repair it, so the
    cascade stops here rather than reddening whatever happens to be collected next."""
    offenders = [
        (c, actual, expected)
        for c, actual, expected in _env_sync.diverged(_ENV_CONSTANT_REGISTRY)
        if c.dotted not in _ENV_CONSTANT_BASELINE_BAD
    ]
    if not offenders:
        return
    for const, _actual, _expected in offenders:
        _env_sync.repair(const)  # later tests must not inherit this
    pytest.fail(
        "{}\n\n{}".format(
            item.nodeid,
            "\n\n".join(_env_sync.describe(c, a, e) for c, a, e in offenders),
        ),
        pytrace=False,
    )
