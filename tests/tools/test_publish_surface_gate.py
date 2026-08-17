"""R15 proofs for `tools/publish_surface_gate.py` -- the content publish's replacement gate.

The director approved eliminating the whole-repo hook from the content publish path on three
conditions (2026-08-17 console): the replacement's subject is exactly the surfaces that ship, it
is PROVABLY FAILABLE, and it FAILS CLOSED when it cannot run. Clause 2 is this file's whole job,
and clause 3 is most of what it drives red.

HOW THIS AVOIDS TESTING ITSELF INTO A CORNER. Every behavioural test builds a REAL git repo in
`tmp_path` and points the gate at it with `cwd=`. Nothing here runs against this repository: a
gate whose tests need the live tree in a particular state is a gate nobody can change, and the
live tree here is written by fifteen daemons.

EACH REFUSAL IS PRECEDED BY ITS OWN GREEN. `test_the_honest_surface_is_green` runs first on the
same fixture every mutation starts from, so a permanently-red gate cannot pass this file by
refusing everything -- the failure mode that makes a control look like it works.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools import pre_commit_test_gate as pctg  # noqa: E402
from tools import publish_surface_gate as psg  # noqa: E402

PASSING_TEST = "def test_ok():\n    assert True\n"


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, check=False)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo shaped like the parts of this one the gate reads: a shipping surface, a
    derived test that NAMES it, and the declared floor controls."""
    r = tmp_path / "repo"
    (r / "docs" / "status").mkdir(parents=True)
    (r / "tests" / "background").mkdir(parents=True)
    (r / "tests" / "tools").mkdir(parents=True)

    (r / "docs" / "status" / "LATEST.md").write_text("net margin: 1234\n", encoding="utf-8")
    # The DERIVED test: it is selected purely because its text names the shipping path.
    (r / "tests" / "tools" / "test_surface_consumer.py").write_text(
        "from pathlib import Path\n"
        "SURFACE = Path(__file__).resolve().parents[2] / 'docs/status/LATEST.md'\n"
        "def test_the_published_figure_is_present():\n"
        "    assert 'net margin' in SURFACE.read_text()\n",
        encoding="utf-8",
    )
    for floor in psg.SURFACE_FLOOR_TESTS:
        p = r / floor
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(PASSING_TEST, encoding="utf-8")
    # `tests/` is a PACKAGE in this repo, and the fixture has to be too. Two of the declared floor
    # controls share the basename `test_published_provenance_is_real.py` across
    # tests/background/ and tests/tools/, so without `__init__.py` pytest derives the same module
    # name for both and aborts collection -- which surfaced here as the gate reporting the honest
    # surface RED. That was the FIXTURE's shape, not the gate's: the real tree carries these
    # packages and collects both files fine (verified, 48 passed). Mirroring the real shape keeps
    # this file's greens meaningful.
    for pkg in (r / "tests", r / "tests" / "background", r / "tests" / "tools"):
        (pkg / "__init__.py").write_text("", encoding="utf-8")

    _run(r, "init", "-q", "-b", "main")
    _run(r, "config", "user.email", "t@t")
    _run(r, "config", "user.name", "t")
    _run(r, "add", "-A")
    _run(r, "commit", "-q", "-m", "base")
    # Stage a real change to the shipping surface -- the publish's own shape.
    (r / "docs" / "status" / "LATEST.md").write_text("net margin: 5678\n", encoding="utf-8")
    _run(r, "add", "docs/status/LATEST.md")
    return r


# ---------------------------------------------------------------------------
# The honest path, FIRST -- everything below is a mutation of this.
# ---------------------------------------------------------------------------

def test_the_honest_surface_is_green(repo: Path):
    code, reason, scope = psg.evaluate(cwd=repo)
    assert code == psg.EXIT_OK, reason
    assert "tests/tools/test_surface_consumer.py" in scope, scope
    assert set(psg.SURFACE_FLOOR_TESTS) <= set(scope), scope


def test_the_derived_test_is_selected_because_it_names_the_surface_not_because_it_is_listed(repo: Path):
    """The tautology killer: rename the surface the consumer names and it stops being selected,
    while nothing about this module's own constants changed."""
    before, _floor, err = psg.derive_scope(["docs/status/LATEST.md"], cwd=repo)
    assert err is None and "tests/tools/test_surface_consumer.py" in before
    after, _floor2, err2 = psg.derive_scope(["docs/reports/ANNUAL_REPORT.md"], cwd=repo)
    assert err2 is None
    assert "tests/tools/test_surface_consumer.py" not in after, after


# ---------------------------------------------------------------------------
# CLAUSE 2 -- it can fail on its own named defect (a bad published figure).
# ---------------------------------------------------------------------------

def test_a_red_surface_test_refuses_the_publish(repo: Path):
    (repo / "docs" / "status" / "LATEST.md").write_text("the figure is gone\n", encoding="utf-8")
    _run(repo, "add", "docs/status/LATEST.md")
    code, reason, _ = psg.evaluate(cwd=repo)
    assert code == psg.EXIT_RED, reason
    assert "RED" in reason


# ---------------------------------------------------------------------------
# CLAUSE 1 -- the subject is the tree the commit creates, and a mismatch is unjudgeable.
# ---------------------------------------------------------------------------

def test_a_staged_surface_modified_after_staging_is_refused_as_unjudgeable(repo: Path):
    """The precise defect that made the three-day freeze unfixable: the gate judged working-tree
    bytes the commit was not making. Note this is EXIT_CANNOT_RUN, not EXIT_RED -- the content may
    be perfectly fine; the gate simply cannot say."""
    (repo / "docs" / "status" / "LATEST.md").write_text("edited after staging\n", encoding="utf-8")
    code, reason, _ = psg.evaluate(cwd=repo)
    assert code == psg.EXIT_CANNOT_RUN, reason
    assert "index disagree" in reason or "not making" in reason, reason


def test_the_subject_check_passes_when_tree_and_index_agree(repo: Path):
    ok, why = psg.subject_is_the_commits_tree(["docs/status/LATEST.md"], cwd=repo)
    assert ok, why


# ---------------------------------------------------------------------------
# CLAUSE 3 -- fails closed. Each branch driven by removing what it depends on.
# ---------------------------------------------------------------------------

def test_a_missing_floor_control_refuses_rather_than_running_a_smaller_floor(repo: Path):
    victim = repo / psg.SURFACE_FLOOR_TESTS[0]
    victim.unlink()
    code, reason, _ = psg.evaluate(cwd=repo)
    assert code == psg.EXIT_CANNOT_RUN, reason
    assert "unavailable check is a FAILED check" in reason, reason
    assert psg.SURFACE_FLOOR_TESTS[0] in reason


def test_a_collapsed_derivation_refuses_even_though_the_floor_would_be_green(repo: Path):
    """THE VACUITY GUARD, and it is reachable only because `derive_scope` returns the derived half
    separately. The first draft unioned the floor in before asking, so this branch was dead code
    -- an unreachable refusal is a control that cannot fire, which is what R15 forbids. This test
    is the proof it is now reachable: the floor tests all still exist and would report green."""
    (repo / "tests" / "tools" / "test_surface_consumer.py").unlink()
    _run(repo, "add", "-A")
    (repo / "docs" / "status" / "LATEST.md").write_text("orphan surface\n", encoding="utf-8")
    _run(repo, "add", "docs/status/LATEST.md")
    code, reason, _ = psg.evaluate(cwd=repo)
    assert code == psg.EXIT_CANNOT_RUN, reason
    assert "VACUITY" in reason, reason
    for floor in psg.SURFACE_FLOOR_TESTS:
        assert (repo / floor).exists(), "the floor must survive, or this proves the wrong thing"


def test_an_erroring_grep_is_an_error_not_an_empty_answer(repo: Path, monkeypatch):
    """FAIL-SILENT killer, and the deliberate asymmetry with the sibling gate: there, an erroring
    grep returns nothing and is bounded by other surfaces; here the derivation is the only thing
    between a bad figure and the public site, so it has no fail-open branch."""
    def _boom(*a, **kw):
        return subprocess.CompletedProcess(args=[], returncode=128, stdout="", stderr="git exploded")
    monkeypatch.setattr(psg, "_git", _boom)
    derived, floor, err = psg.derive_scope(["docs/status/LATEST.md"], cwd=repo)
    assert err is not None and "128" in err, (derived, floor, err)


def test_git_unavailable_refuses_rather_than_reporting_nothing_staged(repo: Path, monkeypatch):
    monkeypatch.setattr(psg.shutil, "which", lambda name: None)
    paths, err = psg.staged_shipping_paths(cwd=repo)
    assert paths == [] and err is not None, (paths, err)
    code, reason, _ = psg.evaluate(cwd=repo)
    assert code == psg.EXIT_CANNOT_RUN, reason


def test_pytest_unavailable_refuses(repo: Path, monkeypatch):
    real = subprocess.run

    def _fake(cmd, *a, **kw):
        if isinstance(cmd, list) and "--version" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=127, stdout="", stderr="no pytest")
        return real(cmd, *a, **kw)

    monkeypatch.setattr(psg.subprocess, "run", _fake)
    code, reason, _ = psg.evaluate(cwd=repo)
    assert code == psg.EXIT_CANNOT_RUN, reason
    assert "pytest is not runnable" in reason, reason


# ---------------------------------------------------------------------------
# The orphan this gate closes must stay closed.
# ---------------------------------------------------------------------------

def test_this_gate_covers_every_root_the_sibling_gate_excludes_from_derivation(repo: Path):
    """`pre_commit_test_gate.PUBLISHED_OUTPUT_ROOTS` skips test derivation for those roots,
    commented "gated elsewhere". Before 2026-08-17, `docs/reports/` and `docs/status/` had no
    elsewhere -- an R11 orphan transition. This asserts the counterpart exists for EVERY excluded
    root, so adding a sixth to that tuple without adding it here fails at commit time instead of
    quietly joining the orphan."""
    uncovered = [
        root for root in pctg.PUBLISHED_OUTPUT_ROOTS
        if not any(root.startswith(mine) or mine.startswith(root)
                   for mine in psg.PUBLISH_SURFACE_ROOTS)
    ]
    assert not uncovered, (
        "PUBLISHED_OUTPUT_ROOTS excludes {} from test derivation and no PUBLISH_SURFACE_ROOT "
        "covers it -- that root ships to a reader gated by nothing".format(uncovered)
    )


def test_no_shipping_path_staged_is_a_pass_not_a_refusal(repo: Path):
    """A code-only commit must not be refused by this gate -- it has nothing to say about one."""
    _run(repo, "reset", "-q")
    (repo / "some_module.py").write_text("x = 1\n", encoding="utf-8")
    _run(repo, "add", "some_module.py")
    code, reason, scope = psg.evaluate(cwd=repo)
    assert code == psg.EXIT_OK and scope == [], (code, reason, scope)
    assert "nothing for this gate to judge" in reason
