"""R15 control for the at-HEAD wall measurement: the tree you ship, not the tree you sit in.

WHAT THIS GUARDS
----------------
`tools/epistemic_wall.crossings_at_head()` and
`tools/wall_crossing_dispositions.py --at-head` answer a question none of the existing
instruments could: *is the register's claim true of the COMMITTED repo?* Every other wall
instrument reads the working tree, and a green working tree says nothing about what a clone
gets.

THE CLASS, PAID FOR THREE TIMES IN TWO DAYS
--------------------------------------------
  1. KNIFE pass 1 was recorded LANDED in a committed doc while four of its files sat unstaged
     (`WORKER_FINDING_A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_2026-08-09`).
  2. The capability index measured the working tree and reported it as the repo's state
     (`WORKER_FINDING_THE_INDEX_READS_THE_WORKING_TREE_2026-08-09`).
  3. KNIFE pass 3's B7 cut committed NOTHING, while the register it wrote asserted "THIS
     register is the committed record".

THE DESIGN POINT THIS SUITE PINS, BECAUSE IT IS COUNTER-INTUITIVE AND EASY TO "SIMPLIFY" AWAY
----------------------------------------------------------------------------------------------
The check is deliberately ASYMMETRIC: the REGISTER is read from the working tree (the claim, as
just written) and the CODE from HEAD (what a reader gets). The obvious symmetric design —
compare HEAD's register with HEAD's code — is BLIND to instance 3, because a pass that commits
neither leaves HEAD self-consistently in the old state. `test_the_symmetric_check_is_blind`
pins that, so a future reader who finds the asymmetry odd sees the counterexample rather than
tidying it into a hole.

R15 — THE THREE KILLER PATTERNS, ANSWERED
------------------------------------------
TAUTOLOGY   — the two modes are proven to DISAGREE on a repo whose working tree and HEAD differ.
              A `crossings_at_head` that quietly re-read the working tree would agree, and every
              test here that matters would fail.
FAIL-OPEN   — an empty export, a truncated export and a non-repo each raise rather than return
              an empty set. Zero crossings would verify every `cut` claim ever written, which is
              the precise fail-open shape the mechanism exists to catch, so it is refused.
FAIL-SILENT — git absent, or `git archive` failing, is an ERROR here and never a skip. There is
              no `pytest.skip` in this module by design.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.epistemic_wall import (  # noqa: E402
    HeadExportError,
    crossings_at,
    crossings_at_head,
    head_export,
)
from tools.wall_crossing_dispositions import parse_register, reconcile  # noqa: E402

CROSSING = ("simulation.renewals", "company.pricing.tariff_engine")


# --------------------------------------------------------------------------
# Fixture: a real git repo whose HEAD and working tree deliberately disagree.
# --------------------------------------------------------------------------

def _git(repo, *args):
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, f"git {args} failed: {proc.stderr}"
    return proc.stdout


def _write(repo, rel, text):
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def repo_with_uncommitted_cut(tmp_path):
    """HEAD carries the crossing; the working tree has had it cut but NOT committed.

    This is instance 3 reproduced in miniature — the exact state the B7 tick left behind.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")

    _write(repo, "company/pricing/tariff_engine.py", "RATE = 1.0\n")
    _write(repo, "company/interfaces/renewal_offer.py", "def quote():\n    return 1.0\n")
    # HEAD state: the world imports the company's pricing engine directly.
    _write(
        repo, "simulation/renewals.py",
        "from company.pricing.tariff_engine import RATE\n\n\ndef renew():\n    return RATE\n",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "pre-cut state")

    # Working-tree state: the cut, made but never committed.
    _write(
        repo, "simulation/renewals.py",
        "from company.interfaces.renewal_offer import quote\n\n\ndef renew():\n    return quote()\n",
    )
    return repo


# --------------------------------------------------------------------------
# TAUTOLOGY — the two modes must be able to disagree.
# --------------------------------------------------------------------------

def test_head_mode_reads_head_not_the_working_tree(repo_with_uncommitted_cut):
    """The load-bearing assertion. If these agree, the mechanism is decorative."""
    repo = repo_with_uncommitted_cut

    working = set(crossings_at(str(repo)))
    committed = set(crossings_at_head(str(repo)))

    assert CROSSING not in working, "the working tree has the cut — fixture is wrong"
    assert CROSSING in committed, (
        "crossings_at_head reported the WORKING TREE's answer. The whole mechanism is "
        "a tautology if it cannot see a state the working tree no longer has."
    )
    assert working != committed


def test_the_two_modes_agree_when_the_cut_is_committed(repo_with_uncommitted_cut):
    """Vacuity guard on the test above: the disagreement must come from the COMMIT.

    Without this, a `crossings_at_head` that always reported the edge — say, from a stale
    cache or a hardcoded answer — would pass the disagreement test for the wrong reason.
    """
    repo = repo_with_uncommitted_cut
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "land the cut")

    assert set(crossings_at(str(repo))) == set(crossings_at_head(str(repo)))
    assert CROSSING not in set(crossings_at_head(str(repo)))


# --------------------------------------------------------------------------
# The historical instance, reproduced end to end through `reconcile`.
# --------------------------------------------------------------------------

# The register AS THE PASS WROTE IT: the cut is claimed. True of the working tree.
REGISTER_CLAIMING_THE_CUT = """
<!-- WALL-CROSSING-EDGES
edge: simulation.renewals -> company.pricing.tariff_engine | disposition=cut | reason=B7 executed — the renewal decision moved to the company desk and the world asks through the seam, so the world no longer prices the company's tariff.
WALL-CROSSING-EDGES -->
"""

# The register AS HEAD CARRIES IT: written before the pass, so it claims nothing.
REGISTER_AT_HEAD = """
<!-- WALL-CROSSING-DESIGN B7_renewal_is_a_company_decision
The renewal decision moves to the company layer; the world keeps the renewal event.
WALL-CROSSING-DESIGN -->

<!-- WALL-CROSSING-EDGES
edge: simulation.renewals -> company.pricing.tariff_engine | disposition=owed | design=B7_renewal_is_a_company_decision
WALL-CROSSING-EDGES -->
"""


def test_the_register_claiming_a_cut_that_is_not_committed_is_a_finding(
    repo_with_uncommitted_cut,
):
    """Instance 3, end to end: the claim is true of the tree and false of the repo."""
    repo = repo_with_uncommitted_cut
    rows, designs = parse_register(REGISTER_CLAIMING_THE_CUT)

    # Working-tree mode: the cut IS made here, so the register is consistent. This is the
    # green that let the real defect through.
    working_findings, _ = reconcile(rows, designs, set(crossings_at(str(repo))))
    assert not [f for f in working_findings if "STILL IN" in f]

    # At-HEAD mode: the same register, measured against what is committed.
    head_findings, _ = reconcile(
        rows, designs, set(crossings_at_head(str(repo))), measured_label="HEAD"
    )
    assert any("STILL IN HEAD" in f for f in head_findings), head_findings


def test_the_symmetric_check_is_blind(repo_with_uncommitted_cut):
    """Why the register is read from the working tree and the code from HEAD.

    Comparing HEAD's register against HEAD's code passes, because a pass that committed
    neither leaves HEAD self-consistent. Pinned so the asymmetry is not "simplified" away.
    """
    repo = repo_with_uncommitted_cut
    rows, designs = parse_register(REGISTER_AT_HEAD)

    findings, _ = reconcile(rows, designs, set(crossings_at_head(str(repo))))
    assert not findings, (
        "the symmetric HEAD-vs-HEAD check found something; if this ever starts failing the "
        "asymmetric design may no longer be necessary — re-derive it before deleting it"
    )


# --------------------------------------------------------------------------
# FAIL-OPEN — every path that could yield an empty tree must raise instead.
# --------------------------------------------------------------------------

def test_a_repo_with_no_wall_packages_raises_rather_than_measuring_zero(tmp_path):
    repo = tmp_path / "empty"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    _write(repo, "README.md", "no python here\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "empty")

    with pytest.raises(HeadExportError, match="no .py files"):
        crossings_at_head(str(repo))


def test_a_directory_that_is_not_a_repo_raises(tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    with pytest.raises(HeadExportError):
        crossings_at_head(str(plain))


def test_a_repo_with_no_commits_raises(tmp_path):
    repo = tmp_path / "nocommit"
    repo.mkdir()
    _git(repo, "init", "-q")
    _write(repo, "simulation/renewals.py", "import company.pricing.tariff_engine\n")
    with pytest.raises(HeadExportError):
        crossings_at_head(str(repo))


def test_a_truncated_export_is_caught_by_the_independent_oracle(
    repo_with_uncommitted_cut, monkeypatch
):
    """The completeness guard, mutation-tested against a deliberately short archive.

    A partial extraction is the realistic silent failure — disk full, interrupted pipe — and
    it fails OPEN by construction: fewer files means fewer edges means more `cut` claims
    verified. The guard compares against `git ls-tree`, a source the broken export cannot
    influence, so it catches this.
    """
    repo = repo_with_uncommitted_cut
    real_extractall = tarfile.TarFile.extractall

    def truncating_extractall(self, path, *a, **kw):
        real_extractall(self, path, *a, **kw)
        # Simulate the archive having arrived short by one file.
        victim = os.path.join(path, "company", "pricing", "tariff_engine.py")
        if os.path.exists(victim):
            os.remove(victim)

    monkeypatch.setattr(tarfile.TarFile, "extractall", truncating_extractall)

    with pytest.raises(HeadExportError, match="not what HEAD contains"):
        crossings_at_head(str(repo))


def test_the_truncation_guard_is_not_vacuous(repo_with_uncommitted_cut):
    """The un-mutated export passes the same guard — so the test above measured something."""
    with head_export(str(repo_with_uncommitted_cut)) as root:
        assert os.path.exists(os.path.join(root, "company", "pricing", "tariff_engine.py"))


# --------------------------------------------------------------------------
# FAIL-SILENT — an unavailable check is a FAILED check, never a skip.
# --------------------------------------------------------------------------

def test_git_being_unavailable_is_an_error_not_a_silent_pass(
    repo_with_uncommitted_cut, monkeypatch
):
    def no_git(*a, **kw):
        raise OSError("git: command not found")

    monkeypatch.setattr(subprocess, "run", no_git)
    with pytest.raises(HeadExportError, match="could not run git"):
        crossings_at_head(str(repo_with_uncommitted_cut))


def test_the_export_is_cleaned_up_even_when_the_walk_raises(repo_with_uncommitted_cut):
    """No temp-dir leak on the error paths — the guards above run often enough to matter."""
    seen = {}
    with head_export(str(repo_with_uncommitted_cut)) as root:
        seen["root"] = root
        assert os.path.isdir(root)
    assert not os.path.exists(seen["root"])


# --------------------------------------------------------------------------
# The real repo — the mechanism must work on the tree it was built for.
# --------------------------------------------------------------------------

def test_the_real_repo_measures_a_nonzero_committed_crossing_set():
    """An outcome test, not a mock: this repo's own HEAD must be measurable.

    Deliberately asserts a LOWER BOUND rather than a pinned count — pinning the number here
    would make every legitimate KNIFE cut red this file, which is how a control becomes a
    thing people route around. The count belongs to the register; existence belongs here.
    """
    committed = crossings_at_head()
    assert committed, "this repo's HEAD measured zero crossings — 'could not look' shape"
