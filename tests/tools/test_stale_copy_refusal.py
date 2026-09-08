"""The defect: a pathspec stages the WORKING-TREE copy, so a lane holding a stale copy of a file
silently reverts another lane's landed commit, and every gate downstream is green on it because the
tree it reverts to was valid an hour ago.

Each test names the specific way this control could be useless rather than merely exercising it.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

from tools import stale_copy_refusal as scr
from tools.python_code_text import searchable
from tools.symbol_landing_check import _bound_names


def _run(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo. NOT a fake: this control's whole subject is git trees, and a fake tree
    reader would be `a fake more permissive than its subject` -- the shape that turns a fail-open
    into a green suite."""
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "m.py").write_text("def alpha():\n    return 1\n")
    _run(root, "add", "m.py")
    _run(root, "commit", "-qm", "base")
    return root


def _commit(root: Path, path: str, text: str, message: str) -> str:
    (root / path).write_text(text)
    _run(root, "add", path)
    _run(root, "commit", "-qm", message)
    return _run(root, "rev-parse", "HEAD").strip()


LANDED = (
    "def alpha():\n    return 1\n\n\n"
    "def freshly_landed_helper(argument):\n"
    '    """A distinctive line that appears exactly once in this file."""\n'
    "    return argument * 41 + 7\n"
)

#: The stale copy: taken BEFORE `freshly_landed_helper` landed, and carrying its own edit, so it is
#: NOT a strict symbol subset. This is what the live tree actually looks like -- measured, 2026-09-08.
STALE_WITH_OWN_WORK = (
    "def alpha():\n    return 2\n\n\n"
    "def my_own_new_function():\n    return 'mine'\n"
)


def test_a_copy_predating_the_landing_is_refused(repo: Path) -> None:
    """THE DEFECT ITSELF. The stale copy adds a name of its own, so the strict-subset rule that was
    originally specified passes it -- and it deletes `freshly_landed_helper` all the same."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), STALE_WITH_OWN_WORK)
    assert loss is not None and loss.rule == scr.PREDATES, (
        "a copy containing none of the last landing's distinctive lines was not refused; this is "
        "the exact mechanism behind A_REWRITE_DELETED_THE_BINDING_REPAIR")
    assert any("freshly_landed_helper" in d for d in loss.detail)


def test_the_strict_subset_rule_alone_would_have_passed_that_copy(repo: Path) -> None:
    """THE REFUTATION, kept as a control so it cannot quietly stop being true. Pinning this is what
    stops someone 'simplifying' the module back to the rule that measured zero on the live tree."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    before = scr.symbols(scr.blob_at(repo, "HEAD", "m.py"), "m.py")
    after = scr.symbols(STALE_WITH_OWN_WORK, "m.py")
    assert not (after < before), (
        "if this copy IS a strict subset the two rules are not distinguishable here and this "
        "fixture no longer demonstrates why rule 1 exists")
    assert "freshly_landed_helper" in before - after


def test_a_fresh_copy_that_has_the_landing_is_not_refused(repo: Path) -> None:
    """FALSE-POSITIVE FLOOR. This control sits in the ONE legal landing door; if it refuses honest
    work it becomes the pressure toward bypass that surgical_land exists to remove."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    edited = LANDED.replace("return 1", "return 99") + "\ndef mine():\n    return 0\n"
    assert scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), edited) is None


def test_the_identity_is_not_refused(repo: Path) -> None:
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    head = scr.blob_at(repo, "HEAD", "m.py")
    assert scr.judge(repo, "m.py", head, head) is None


def test_a_strict_symbol_subset_is_refused_when_the_landing_is_old(repo: Path) -> None:
    """RULE 2 EARNS ITS PLACE. The deleted name came from an OLDER commit than the last one to
    touch the path, so rule 1 is satisfied and only the subset rule can see the deletion."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    _commit(repo, "m.py", LANDED + "\nRECENT = 1\n", "a later, unrelated landing")
    # Keeps the recent landing's line; drops the older `freshly_landed_helper`. Adds nothing.
    dropped = "def alpha():\n    return 1\n\n\nRECENT = 1\n"
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), dropped)
    assert loss is not None and loss.rule == scr.SUBSET
    assert "freshly_landed_helper" in loss.detail


def test_a_lost_method_is_seen_and_a_module_level_reader_would_miss_it(repo: Path) -> None:
    """`_bound_names` alone is module-level, and the landed work a stale copy most often drops is a
    METHOD -- every top-level name survives, so a module-level-only reader calls the sets equal."""
    with_method = "class K:\n    def one(self):\n        pass\n\n    def two(self):\n        pass\n"
    without = "class K:\n    def one(self):\n        pass\n"
    assert "K.two" in (scr.symbols(with_method, "m.py") - scr.symbols(without, "m.py"))
    assert _bound_names(ast.parse(with_method).body) == _bound_names(ast.parse(without).body), (
        "if the module-level reader already tells these apart, _class_members is dead weight")


def test_an_unreadable_suffix_yields_no_opinion_and_never_an_empty_set(repo: Path) -> None:
    """VACUITY. Folded to an empty set, both sides compare equal, no strict subset exists, and the
    path is waved through WHILE LOOKING CHECKED -- useless without ever being fail-open."""
    assert scr.symbols("anything at all", "docs/x.md") is None
    assert scr.symbols("{}", "site/data/dashboard.json") is None


def test_an_unparseable_python_blob_is_a_finding_not_a_skip(repo: Path) -> None:
    """FAIL-CLOSED. An unavailable check is a failed check."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"),
                     LANDED + "\ndef broken(:\n")
    assert loss is not None and loss.rule in (scr.PREDATES, scr.UNPARSEABLE)


def test_a_new_file_and_a_deletion_are_both_outside_the_subject(repo: Path) -> None:
    """A wholly new file is not contested and a deletion is explicit; refusing either would be a
    false positive in the door every landing goes through."""
    assert scr.judge(repo, "new.py", None, "def a():\n    pass\n") is None
    assert scr.judge(repo, "m.py", "def a():\n    pass\n", None) is None


def test_a_repeated_line_is_not_evidence_of_freshness(repo: Path) -> None:
    """THE DISTINCTIVE FILTER, and it is why the population is 8 and not 5. Without it, one
    coincidentally-repeated line reads as 'the copy has some of the landing' and two genuinely
    stale files escaped -- measured on the shared tree, 2026-09-08."""
    dup = "def alpha():\n    return 1\n\n\ndef b():\n    x = 12345\n\n\ndef c():\n    x = 12345\n"
    sha = _commit(repo, "m.py", dup, "lands two identical lines and two names")
    distinctive = scr.distinctive_lines(repo, "m.py", sha)
    assert "x = 12345" not in distinctive, "a line added twice cannot discriminate either way"
    assert any("def b()" in d for d in distinctive), (
        "the filter must not empty the evidence set -- an empty set makes rule 1 unreachable")


def test_the_drops_escape_hatch_exempts_only_what_it_names(repo: Path) -> None:
    """A deliberate deletion must be landable, or the door refuses honest work; and the exemption
    must be per-path, or one declaration blankets the commit."""
    # BOTH files must be landed INCREMENTALLY. A file whose most recent commit CREATED it has that
    # commit's whole content as its added lines, so a rewrite sharing any one of them (here
    # `def alpha():`) is not a copy that predates anything -- correct, and it would make n.py a
    # silent non-subject rather than the exempted one this test is about.
    _commit(repo, "n.py", "def alpha():\n    return 1\n", "n.py starts life")
    _commit(repo, "m.py", LANDED, "lane B lands a helper in m")
    _commit(repo, "n.py", LANDED, "lane B lands the same helper in n")
    # A REAL resulting tree carrying a stale copy of BOTH -- the subject violations() judges.
    (repo / "m.py").write_text(STALE_WITH_OWN_WORK)
    (repo / "n.py").write_text(STALE_WITH_OWN_WORK)
    _run(repo, "add", "m.py", "n.py")
    stale_tree = _run(repo, "write-tree").strip()

    both = scr.violations(repo, "HEAD", stale_tree, ["m.py", "n.py"])
    assert {v.path for v in both} == {"m.py", "n.py"}, (
        "the unexempted tree must refuse both, or the exemption below proves nothing")
    one = scr.violations(repo, "HEAD", stale_tree, ["m.py", "n.py"], allow=frozenset({"m.py"}))
    assert {v.path for v in one} == {"n.py"}, (
        "--drops must exempt ONLY the path it names; a declaration that blankets the commit is "
        "an exemption wearing a pathspec")


def test_the_refusal_names_the_path_and_the_route_out(repo: Path) -> None:
    """A refusal that does not say why is how a lane learns to reach for a bypass. The wall needs
    the door named in the same breath."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), STALE_WITH_OWN_WORK)
    text = scr.refusal_text([loss])
    assert "m.py" in text
    assert "isolate_hunks" in text and "--content" in text, (
        "the refusal must name the legal move; without it this is pressure toward --no-verify")
    assert "--drops" in text


def test_the_guard_is_wired_into_the_landing_door(repo: Path) -> None:
    """FAIL-SILENT. A control invoked only by someone typing its name is permanently unavailable
    and therefore permanently passing. `surgical_land` is the only legal landing move, so that is
    where this has to be called from -- asserted against the source, because importing and calling
    `_land_once` here would run a full gate.

    READ AS CODE, never as text. `searchable()` blanks comments and prose strings while preserving
    every offset, so this cannot be satisfied by a docstring that merely DESCRIBES the wiring --
    which is the failure mode `tests/architecture/test_a_control_reads_python_as_code.py` exists to
    refuse, and which this test was written with on its first draft."""
    src = searchable(
        (Path(__file__).resolve().parents[2] / "tools" / "surgical_land.py").read_text())
    assert "stale_copy_refusal.violations(" in src
    assert "stale_copy_refusal.refusal_text(" in src
    build = src.index("files = changed_paths(root, parent_tree, result_tree)")
    call = src.index("stale_copy_refusal.violations(")
    extract = src.index("EXTRACT_ROOT.mkdir(parents=True, exist_ok=True)", build)
    assert build < call < extract, (
        "the refusal must sit between the resulting tree and the extract: after it there is a "
        "tree to judge, and before the extract it costs nothing to refuse")
