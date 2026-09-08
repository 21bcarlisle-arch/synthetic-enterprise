"""The defect: a lane's work is not path-shaped, and every tool in the stale-copy remedy is.

Measured on the live tree 2026-09-08 (the addendum to
`SEAT_FINDING_THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES`):
`tests/tools/test_commit_refusal_attribution.py` is one of the eight refused copies and calls
`attr.decompose_outage`, which exists only in the shared tree's UNCOMMITTED copy of
`tools/commit_refusal_attribution.py` -- a file no control names, because it is not stale. A seat
following the refusal path by path lands the test without the function and reds HEAD for every
lane. Nothing in the route says to look for the other half.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import isolate_hunks as ih
from tools import landing_pair as lp
from tools.python_code_text import searchable


def _run(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout


#: The consumer, in the shape that actually broke: `from tools import x as attr` then `attr.NAME`.
#: That is `references()`'s shape 3, the one the original supplier-left-behind defect wore.
CONSUMER = (
    "from tools import commit_refusal_attribution as attr\n"
    "\n"
    "def test_the_outage_decomposes():\n"
    "    assert attr.decompose_outage('x')\n"
)

LANDED_SUPPLIER = "def already_landed(row):\n    return row\n"
UNCOMMITTED_SUPPLIER = LANDED_SUPPLIER + "\n\ndef decompose_outage(text):\n    return [text]\n"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo with this project's first-party roots, because `tree_python_files` filters
    on them by name and a fixture under any other directory would be invisible to the whole
    control -- an empty referent set, which passes vacuously."""
    root = tmp_path / "r"
    (root / "tools").mkdir(parents=True)
    (root / "tests" / "tools").mkdir(parents=True)
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "tools" / "commit_refusal_attribution.py").write_text(LANDED_SUPPLIER)
    (root / "tests" / "tools" / "test_commit_refusal_attribution.py").write_text(
        "from tools import commit_refusal_attribution as attr\n\n\n"
        "def test_landed():\n    assert attr.already_landed(1) == 1\n")
    _run(root, "add", "-A")
    _run(root, "commit", "-qm", "base")
    return root


CONSUMER_PATH = "tests/tools/test_commit_refusal_attribution.py"
SUPPLIER_PATH = "tools/commit_refusal_attribution.py"


def test_the_measured_case_names_the_other_half(repo: Path) -> None:
    """THE DEFECT ITSELF, rebuilt. Without this the refusal sends a seat to land a consumer whose
    supplier is in another lane's uncommitted file, and the first thing that notices is the tree
    going red for everyone."""
    (repo / SUPPLIER_PATH).write_text(UNCOMMITTED_SUPPLIER)
    (repo / CONSUMER_PATH).write_text(CONSUMER)
    pairs = lp.pairs_for(CONSUMER, CONSUMER_PATH, lp.index_tree(repo, "HEAD"), repo)
    assert len(pairs) == 1, "the pair was not found: {}".format(pairs)
    assert pairs[0].supplier == SUPPLIER_PATH
    assert pairs[0].symbols == ("decompose_outage",)
    assert "part of the same landing" in pairs[0].render()


def test_a_name_the_landing_tree_already_supplies_is_not_a_pair(repo: Path) -> None:
    """THE OTHER HALF OF REACHABILITY. A detector that pairs everything is as useless as one that
    pairs nothing, and it is the shape that survives a suite of positive cases."""
    (repo / SUPPLIER_PATH).write_text(UNCOMMITTED_SUPPLIER)
    source = ("from tools import commit_refusal_attribution as attr\n"
              "\n\ndef t():\n    return attr.already_landed(1)\n")
    assert lp.pairs_for(source, CONSUMER_PATH, lp.index_tree(repo, "HEAD"), repo) == []


def test_a_name_no_tree_supplies_is_reported_as_that_and_not_as_a_pair(repo: Path) -> None:
    """FOLDING THE TWO TOGETHER WOULD PUBLISH THE WORSE STATE AS THE BETTER ONE. 'Land these two
    together' is actionable; 'this name exists nowhere' is a different problem with a different
    fix, and one row saying `PAIR` for both reads as the whole answer."""
    (repo / CONSUMER_PATH).write_text(CONSUMER)
    pairs = lp.pairs_for(CONSUMER, CONSUMER_PATH, lp.index_tree(repo, "HEAD"), repo)
    assert len(pairs) == 1 and pairs[0].supplier is None
    assert "NO tree supplies it" in pairs[0].render()
    assert "PAIR" not in pairs[0].render()


def test_an_untracked_new_module_counts_as_the_other_half(repo: Path) -> None:
    """A wholly new module is the same pair one file up. A supplier search that only walked
    TRACKED changes would answer 'no supplier anywhere' -- the reading that looks like a clean
    result, and the one that sends a seat hunting for a file that is sitting right there."""
    (repo / "tools" / "brand_new_helper.py").write_text("def helps():\n    return 1\n")
    source = "from tools.brand_new_helper import helps\n\n\ndef t():\n    return helps()\n"
    pairs = lp.pairs_for(source, CONSUMER_PATH, lp.index_tree(repo, "HEAD"), repo)
    assert len(pairs) == 1 and pairs[0].supplier == "tools/brand_new_helper.py", pairs


def test_a_supplier_blob_that_will_not_parse_supplies_nothing_rather_than_everything(
        repo: Path) -> None:
    """FAIL-OPEN, THE FIRST KILLER. Treating an unparseable module as dynamic would make every
    reference into it resolve, and a broken blob at HEAD is exactly when you most want the check."""
    (repo / SUPPLIER_PATH).write_text("def broken(:\n")
    _run(repo, "add", "-A")
    _run(repo, "commit", "-qm", "a broken blob lands")
    (repo / SUPPLIER_PATH).write_text(UNCOMMITTED_SUPPLIER)
    index = lp.index_tree(repo, "HEAD")
    assert "tools.commit_refusal_attribution" in index.by_module, (
        "the path must stay in by_module or its consumers report the wrong shape of absence")
    assert "tools.commit_refusal_attribution" not in index.facts, (
        "an unparseable blob was given a facts entry; a dynamic or empty one resolves or "
        "misreports every reference into it")
    pairs = lp.pairs_for(CONSUMER, CONSUMER_PATH, index, repo)
    assert pairs and pairs[0].supplier == SUPPLIER_PATH


def test_the_consumers_own_file_is_never_its_own_other_half(repo: Path) -> None:
    """A file cannot be the pair of itself. Without the exclusion, judging the ISOLATED bytes
    against the WORKING copy of the same path would let a hunk you just dropped supply the name
    the hunk you kept needs -- and report `paired, land them together` about one file."""
    (repo / "tools" / "solo.py").write_text("from tools import solo\n")
    _run(repo, "add", "-A")
    _run(repo, "commit", "-qm", "solo lands without its helper")
    (repo / "tools" / "solo.py").write_text(
        "from tools import solo\n\n\ndef helper():\n    return 1\n"
        "\n\ndef t():\n    return solo.helper()\n")
    isolated = "from tools import solo\n\n\ndef t():\n    return solo.helper()\n"
    pairs = lp.pairs_for(isolated, "tools/solo.py", lp.index_tree(repo, "HEAD"), repo)
    assert len(pairs) == 1 and pairs[0].supplier is None, (
        "the file supplied its own missing name from the copy on disk: {}".format(pairs))


# ------------------------------------------------------- the early door: isolate_hunks refuses


def test_isolate_hunks_refuses_half_a_landing_and_writes_nothing(
        repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WHY THIS IS NOT LEFT TO THE LANDING GATE. `symbol_landing_check` asks the same question and
    would red the commit -- but only at the landing door, after the survey, the selection, the
    build and the typed command. Asking one pass earlier costs one whole-tree read."""
    monkeypatch.setattr(ih, "_REPO", repo)
    (repo / SUPPLIER_PATH).write_text(UNCOMMITTED_SUPPLIER)
    (repo / CONSUMER_PATH).write_text(CONSUMER)
    out = tmp_path / "isolated.py"
    with pytest.raises(SystemExit) as exc:
        ih.build(CONSUMER_PATH, ["/decompose_outage/"], out)
    assert "HALF a landing" in str(exc.value) and SUPPLIER_PATH in str(exc.value)
    assert not out.exists(), "bytes were written for a landing that reds the tree at HEAD"


def test_isolate_hunks_still_builds_when_every_name_resolves(
        repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """REACHABILITY OF THE PERMISSIVE BRANCH. A pair check that refuses every isolation passes
    every refusal test above while making the tool it guards unusable."""
    monkeypatch.setattr(ih, "_REPO", repo)
    (repo / CONSUMER_PATH).write_text(
        "from tools import commit_refusal_attribution as attr\n\n\n"
        "def test_landed():\n    assert attr.already_landed(2) == 2\n")
    out = tmp_path / "isolated.py"
    assert ih.build(CONSUMER_PATH, ["1"], out) == 0
    assert out.exists() and "already_landed(2)" in searchable(out.read_text()), (
        "the isolated bytes were not built, so the pair check refuses everything")


def test_bytes_that_do_not_parse_are_reported_as_unaskable_not_as_no_pair(repo: Path) -> None:
    """CANNOT ASK IS NOT NO PAIR. Returning "" here would let a silence read as a clean check --
    and it is not a refusal either: the parse verdict belongs to the gate, not to a byte-builder."""
    verdict = ih.pair_refusal(CONSUMER_PATH, "def broken(:\n", root=repo)
    assert "COULD NOT ASK" in verdict
    assert not verdict.startswith("REFUSED"), (
        "a byte-builder refused on a syntax verdict that is the gate's subject")


def test_a_non_python_path_is_not_claimed(repo: Path) -> None:
    """The resolver is a Python one. Saying nothing about a `.html` page is honest; the stale-copy
    census reports its own no-opinion population for exactly this reason."""
    assert ih.pair_refusal("site/harness/index.html", "<div id='x'></div>", root=repo) == ""
