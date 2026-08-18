"""A committed record that says DISCHARGED must name a falsifier the repository has.

THE `tests/` HALF of the class H27 Expert Hour #35 opened and deliberately left open
(`site/test_the_site_lane_runs_no_untracked_control.py` is the SITE half; the finding is
`docs/staging/done/WORKER_FINDING_THE_SITE_GATE_COUNTS_AN_UNTRACKED_CONTROL_IN_ITS_OWN_GREEN_2026-08-18.md`).

WHY THE SUBJECT IS NOT "UNTRACKED `tests/**/test_*.py`". #35 measured 10 untracked test
modules on disk and refused to make them the population: on a shared working tree with
several lanes live, untracked-at-this-instant is normal and transient, and a repo-wide
census of it would be born red on another lane's in-flight editor. That refusal was right
and it still is. The honest subject #35 named instead, and this file implements, is

    a path that a COMMITTED record cites on its `**Discharged:**` line
    and that the repository does not contain.

That is not a race. A discharge is a CLOSED CLAIM, already committed: it asserts, in a
document any clone can read, that the named falsifier exists and pins the defect. Whether
some other lane is mid-edit has no bearing on whether a claim already made is true.

WHAT THIS FOUND ON ITS FIRST RUN, and it is worse in kind than the site instance rather
than merely a second copy of it (measured 2026-08-18 against the real tree, HEAD 19b56a53e):

    tests/saas/test_clv_margin_basis.py
    tests/tools/test_derived_basis_parentage_gate.py
        <- docs/staging/done/WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_
           THAT_EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK_2026-08-17.md
    tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py
        <- docs/staging/done/WORKER_FINDING_THE_WORLDS_DWELLING_FOR_A_DRAWN_
           HOME_IS_THE_COMPANYS_OWN_ESTIMATE_2026-08-17.md

All three are on disk, none is ignored, and `git log --all` on each is empty. The SITE
instance was one untracked test whose SUBJECT was committed, so the repair was a one-line
`git add`. These are not: each of the three fails to even IMPORT against HEAD, because the
repair it certifies is uncommitted too --

    tools.generate_dashboard_data.UNKNOWN_COST_BASIS          HEAD 0 / worktree 5
    tools.generate_dashboard_data._check_derived_basis_parentage  HEAD 0 / worktree 3
    saas.clv_model.CLV_MARGIN_BASIS                          HEAD 0 / worktree 3
    saas.property_model.BASIS_SAAS_APPROXIMATION             HEAD 0 / worktree 2

(measured by `git show HEAD:<file>` against the working copy, and by running all three in a
detached worktree at HEAD: 3 errors during collection, ImportError on each of those names).
So the record does not merely cite a missing test -- the whole repaired mechanism it
declares closed exists on one machine. #35's own assumption, that "cited by a committed
record" would be a subject free of the sequencing problem, is FALSE, and that is this
control's finding: the sequencing problem is not avoided by picking a better population,
it is what the population is made of.

WHY THIS IS A RATCHET AND NOT A BARE ASSERTION. The three above cannot be greened from
here. Landing them means landing another lane's uncommitted repair to `saas/clv_model.py`,
`saas/property_model.py`, `tools/generate_dashboard_data.py` and the new untracked
`simulation/dwelling_records.py` -- sweeping a live lane's work into this commit, which is
the thing the shared-tree rules forbid outright. Deleting them to go green is worse. So the
three are DECLARED below, dated, with the change set each waits on, and everything else
fails immediately. The list is checked in BOTH directions (see the stale-entry test): an
entry that stops being a violation must be deleted, so the ratchet cannot rot into a
permanent exemption.

R15, THE THREE KILLER PATTERNS, each given a mutation test below that performs the named
defect and is asserted to PASS on it:
  TAUTOLOGY   -- resolving cited paths against the FILESYSTEM (`Path.exists()`) instead of
                 the index. All three violations are on disk, so that checker is green on
                 the shipped defect. This is not hypothetical: it is the exact shape that
                 already let 77 dead evidence paths sit unnoticed across 84 atoms.
  FAIL-OPEN   -- a marker that matches nothing (population 0) with the vacuity floor
                 removed: nothing to check, so nothing fails.
  FAIL-SILENT -- `git` unavailable or exiting non-zero, swallowed into an empty set. An
                 unavailable check is a FAILED check, so both raise here.

WHY THE INDEX AND NOT `HEAD`, on both sides. At pre-commit time the honest question is
"will the commit about to be made contain this", and that is the index. A record and its
falsifier added together in one commit are legitimately present. Post-commit the index
matches HEAD and the two readings coincide.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]

# The marker a finding uses to close itself. Anchored at line start: a discharge is its own
# line in this project's finding format, and an unanchored match would pull in prose that
# merely discusses discharges.
_DISCHARGE_MARKER = r"^\*\*Discharged:\*\*"

# A discharge line reads every backtick as a path unless it is filtered, and these documents
# use backticks for symbols, prose emphasis and pytest node ids as well. A token counts as a
# repo path only if it is relative, contains a separator and ends in an extension the repo
# actually stores.
_BACKTICKED = re.compile(r"`([^`]+)`")
_PATH_EXT = (
    ".py", ".mjs", ".mts", ".ts", ".js",
    ".json", ".yaml", ".yml", ".md", ".html", ".sh",
)

# Vacuity floors. Measured 2026-08-18: 72 records carrying a discharge line, 88 distinct
# cited paths. A broken marker, a moved root or a stricter token filter would empty the
# population and this control would then pass forever with nothing in it. Floors are set
# well below the measurement so ordinary archiving does not trip them -- they catch the
# mechanism breaking, not the corpus shrinking.
_MIN_RECORDS = 30
_MIN_CITED_PATHS = 40

# THE RATCHET. Declared violations, each with the date it was measured and the uncommitted
# change set it waits on. Adding a line here is a deliberate, reviewable act; the stale-entry
# test below deletes the incentive to leave one behind.
_KNOWN_UNLANDED: dict[str, str] = {
    "tests/saas/test_clv_margin_basis.py": (
        "2026-08-18, H27 Hour #36. Waits on the uncommitted CLV margin-basis repair "
        "(`saas/clv_model.py::CLV_MARGIN_BASIS`, absent at HEAD). Owning lane must land "
        "the repair and this falsifier together."
    ),
    "tests/tools/test_derived_basis_parentage_gate.py": (
        "2026-08-18, H27 Hour #36. Waits on the uncommitted R14 parentage gate "
        "(`tools/generate_dashboard_data.py::_check_derived_basis_parentage` and "
        "`UNKNOWN_COST_BASIS`, both absent at HEAD)."
    ),
    "tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py": (
        "2026-08-18, H27 Hour #36. Waits on the uncommitted KNIFE3 B12 dwelling split -- "
        "`simulation/dwelling_records.py` is in no commit on any ref and "
        "`saas/property_model.py::BASIS_SAAS_APPROXIMATION` is absent at HEAD."
    ),
}


def _git(*args: str) -> str:
    """Run git, or FAIL. R15 fail-silent: an unavailable subject is a failed check.

    Returning an empty string on error would make every cited path look untracked (loud,
    but for the wrong reason) or -- worse, depending on which side swallowed it -- make the
    comparison vacuous and green.
    """
    try:
        r = subprocess.run(
            ["git", *args], cwd=str(PROJECT),
            capture_output=True, text=True, timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover - environment
        raise AssertionError(
            f"could not run `git {' '.join(args)}` ({exc!r}) -- this control's subject is "
            "unavailable, so it cannot say anything. An unavailable check is a FAILED "
            "check (R15 fail-silent), never a pass"
        ) from exc
    if r.returncode not in (0, 1):  # git grep exits 1 for "no matches", which is not an error
        raise AssertionError(
            f"`git {' '.join(args)}` exited {r.returncode}: {r.stderr.strip()!r}. An "
            "unavailable check is a FAILED check"
        )
    return r.stdout


def _paths_the_repository_has() -> set[str]:
    """Subject B: the index -- what the commit being made will carry."""
    tracked = {ln.strip() for ln in _git("ls-files").splitlines() if ln.strip()}
    assert tracked, (
        "`git ls-files` listed NOTHING. Either this is not a git work tree or the index is "
        "empty -- in both cases the comparison below would be vacuous"
    )
    return tracked


def _discharge_citations(marker: str = _DISCHARGE_MARKER) -> tuple[dict[str, set[str]], int]:
    """Subject A: what committed records CLAIM. Read from the index, not the working tree.

    Returns (cited path -> set of citing records, number of discharge lines seen). The
    records are read from git rather than from disk on purpose: the claim's authority comes
    from being committed, and a working-tree read would both admit an uncommitted record's
    claim and miss a committed record whose working copy has been moved or archived.
    """
    out = _git("grep", "--cached", "-n", "-e", marker, "--", "*.md")
    cited: dict[str, set[str]] = {}
    lines = 0
    for raw in out.splitlines():
        record, _, rest = raw.partition(":")
        _, _, text = rest.partition(":")
        if not record:
            continue
        lines += 1
        for token in _BACKTICKED.findall(text):
            token = token.strip().split("::")[0].strip()  # drop pytest node ids
            if "/" not in token or not token.endswith(_PATH_EXT):
                continue
            if token.startswith(("http", "/", "~", ".")):
                continue
            cited.setdefault(token, set()).add(record)
    return cited, lines


def _violations(
    cited: dict[str, set[str]] | None = None,
    have: set[str] | None = None,
) -> dict[str, set[str]]:
    if cited is None:
        cited, _ = _discharge_citations()
    if have is None:
        have = _paths_the_repository_has()
    return {p: srcs for p, srcs in cited.items() if p not in have}


def _describe(path: str, srcs: set[str]) -> str:
    where = "on disk here only" if (PROJECT / path).exists() else "in no tree at all"
    return f"{path}  ({where})\n" + "".join(
        f"        cited as DISCHARGED by: {s}\n" for s in sorted(srcs)
    )


# --------------------------------------------------------------------------------------
# The population must be real before any verdict about it means anything.
# --------------------------------------------------------------------------------------

def test_the_citation_population_is_not_vacuous():
    """VACUITY GUARD. A green verdict over an empty population is not a green verdict."""
    cited, records = _discharge_citations()
    assert records >= _MIN_RECORDS, (
        f"only {records} committed records carry a `**Discharged:**` line (floor "
        f"{_MIN_RECORDS}); 72 were measured on 2026-08-18. The marker, the pathspec or the "
        "index read is what changed -- fix the mechanism, do not lower the floor"
    )
    assert len(cited) >= _MIN_CITED_PATHS, (
        f"only {len(cited)} distinct paths are cited across those lines (floor "
        f"{_MIN_CITED_PATHS}); 88 were measured on 2026-08-18. The token filter is what "
        "changed -- fix it, do not lower the floor"
    )


# --------------------------------------------------------------------------------------
# The tripwire.
# --------------------------------------------------------------------------------------

def test_no_committed_discharge_cites_a_falsifier_the_repository_does_not_have():
    """THE TRIPWIRE. A discharge naming a file no clone contains is a claim, not a closure.

    `tools/pre_commit_test_gate.py` and every `pytest` run collect from the WORKING TREE,
    so such a falsifier is collected, passes, and is counted in the green -- while the
    assurance the committed record advertises exists on exactly one machine.
    """
    unexpected = {
        p: s for p, s in _violations().items() if p not in _KNOWN_UNLANDED
    }
    assert not unexpected, (
        "a COMMITTED record says DISCHARGED and names a falsifier that is in no commit:\n"
        "    " + "    ".join(_describe(p, s) for p, s in sorted(unexpected.items()))
        + "\nRepair: land the falsifier AND the repair it certifies, in the same commit as "
        "the record that claims them. If the repair belongs to another lane and cannot be "
        "landed from here, do not delete the falsifier and do not weaken this control -- "
        "add the path to _KNOWN_UNLANDED with the date and the change set it waits on, so "
        "the debt is declared instead of invisible."
    )


def test_every_declared_exemption_is_still_a_real_violation():
    """THE RATCHET'S SECOND DIRECTION -- without this it rots into a permanent exemption.

    An entry that has been landed must be DELETED from the list. Left behind, it would
    silently re-exempt the same path if it were ever un-landed again, which is precisely how
    a ratchet stops being one.
    """
    live = _violations()
    stale = sorted(p for p in _KNOWN_UNLANDED if p not in live)
    assert not stale, (
        "these paths are declared in _KNOWN_UNLANDED but are no longer violations -- they "
        "have been landed, which is the good outcome:\n  - " + "\n  - ".join(stale)
        + "\nDelete each from _KNOWN_UNLANDED. The list only ever shrinks."
    )


# --------------------------------------------------------------------------------------
# R15 -- each mutation performs a named defect and is asserted to PASS on it, which is what
# makes the control above evidence rather than decoration.
# --------------------------------------------------------------------------------------

def test_MUTATION_resolving_citations_against_the_filesystem_goes_blind():
    """TAUTOLOGY/wrong-subject: `Path.exists()` instead of the index passes on the defect.

    The shipped defect is 'the repository does not have it', not 'nobody has it'. A checker
    that asks the local filesystem is answering a question the defect never fails.

    TWO ARMS, and the split is not cosmetic -- the pre-commit gate taught it. The gate builds
    the tree this commit WOULD create in an isolated worktree, where the three declared
    violations are absent from disk (they are untracked, so a clean tree does not have them).
    A first draft of this test asserted "at least one live violation is present on this
    machine" as a precondition and was REFUSED there: a control about machine-local state
    that itself depended on machine-local state. The structural arm below runs everywhere and
    is the actual proof; the real-history arm runs additionally wherever the defect is
    physically present, and says so when it is not.
    """
    # ARM 1, structural and deterministic: the two subjects disagree exactly where the defect
    # lives -- a path the filesystem has and the index does not.
    cited = {"tests/example_falsifier.py": {"docs/staging/done/EXAMPLE.md"}}
    filesystem_has = {"tests/example_falsifier.py"}
    index_has: set[str] = set()

    control_sees = _violations(cited=cited, have=index_has)
    mutant_sees = {p for p in cited if p not in filesystem_has}

    assert control_sees, "the control must see a cited path the index does not carry"
    assert not mutant_sees, (
        "the filesystem-resolving mutant was expected to be BLIND to it -- if it is not, the "
        "control above is not distinguishable from the checker this project already knows "
        "fails (77 dead evidence paths across 84 atoms went unnoticed behind exactly it)"
    )

    # ARM 2, the same claim against real history wherever the tree actually carries it.
    real = _violations()
    on_disk = {p for p in real if (PROJECT / p).exists()}
    if not on_disk:
        pytest.skip(
            "no live violation is present on disk here (expected in a clean tree or the "
            "gate's isolated worktree) -- arm 1 above is the proof, and it ran"
        )
    mutant_on_real = {p for p in _discharge_citations()[0] if not (PROJECT / p).exists()}
    assert not (on_disk & mutant_on_real), (
        "the filesystem-resolving mutant was expected to be BLIND to the on-disk violations "
        f"{sorted(on_disk)} and it saw some of them"
    )


def test_MUTATION_a_marker_that_matches_nothing_passes_without_the_vacuity_floor():
    """FAIL-OPEN: an empty population has no violations in it.

    The floor in `test_the_citation_population_is_not_vacuous` is the only thing standing
    between a broken marker and a permanent green.
    """
    cited, records = _discharge_citations(marker=r"^\*\*Dischargd:\*\*")  # typo'd on purpose
    assert records == 0 and not cited, "precondition: the mutated marker must match nothing"
    assert not _violations(cited=cited), (
        "the empty-population mutant was expected to PASS -- that is the fail-open this "
        "control's vacuity floor exists to close"
    )
    with pytest.raises(AssertionError):
        assert records >= _MIN_RECORDS, "the floor fires on the mutant"


def test_MUTATION_git_unavailable_fails_rather_than_passing_quietly(monkeypatch):
    """FAIL-SILENT: an unavailable subject must FAIL, never be read as 'nothing wrong'."""
    def _boom(*_a, **_k):
        raise OSError("git not on PATH")

    monkeypatch.setattr(subprocess, "run", _boom)
    with pytest.raises(AssertionError, match="unavailable check is a FAILED check"):
        _paths_the_repository_has()


def test_MUTATION_a_non_zero_git_exit_fails_rather_than_passing_quietly(monkeypatch):
    """FAIL-SILENT, second door: git present but refusing (not a work tree, corrupt index)."""
    class _Res:
        returncode = 128
        stdout = ""
        stderr = "fatal: not a git repository"

    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: _Res())
    with pytest.raises(AssertionError, match="unavailable check is a FAILED check"):
        _paths_the_repository_has()


def test_MUTATION_an_empty_index_listing_is_not_read_as_a_clean_repository(monkeypatch):
    """FAIL-SILENT, third door: git succeeds and says nothing.

    An empty tracked set would make EVERY cited path a violation, not zero -- but the
    diagnosis would be wrong and the message useless, so it is refused at the source.
    """
    class _Res:
        returncode = 0
        stdout = "\n  \n"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: _Res())
    with pytest.raises(AssertionError, match="listed NOTHING"):
        _paths_the_repository_has()
