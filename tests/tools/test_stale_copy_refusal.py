"""The defect: a pathspec stages the WORKING-TREE copy, so a lane holding a stale copy of a file
silently reverts another lane's landed commit, and every gate downstream is green on it because the
tree it reverts to was valid an hour ago.

Each test names the specific way this control could be useless rather than merely exercising it.
"""
from __future__ import annotations

import ast
import builtins
import re
import subprocess
from pathlib import Path

import pytest

from tools import stale_copy_refusal as scr
from tools import surgical_land
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


# --------------------------------------------------------------------------- the merge (--merge)
#
# The defect: `violations()` took `parent` and `result` and nothing else, so on a merge it could not
# tell the OTHER history's landed, declared deletion from THIS lane's stale working copy. It refused
# both, and the only route through was `--drops` -- which then credits this landing with a deletion
# that belongs to the other lane, defeating the guard's own attribution. Measured 2026-09-08;
# `22df46614` is the commit that carries the misattributed drop.

#: Far enough apart that an edit to `alpha` and a deletion of the helper are not adjacent hunks --
#: otherwise git conflicts and the test would be measuring conflict handling instead.
WIDE = (
    "def alpha():\n    return 1\n\n\n"
    "def middle_one():\n    return 'a longer distinctive line, middle of the file'\n\n\n"
    "def middle_two():\n    return 'a second longer distinctive line, still the middle'\n\n\n"
    "def freshly_landed_helper(argument):\n"
    '    """A distinctive line that appears exactly once in this file."""\n'
    "    return argument * 41 + 7\n"
)
WITHOUT_HELPER = WIDE[:WIDE.index("def freshly_landed_helper")].rstrip("\n") + "\n"


def _diverge(repo: Path, ours: str | None, theirs: str) -> tuple[str, str, str, list[str]]:
    """Two histories from one base. Returns (parent, ref, merged tree, changed paths).

    The merged tree comes from `surgical_land.build_merge_tree` -- the real subject. A hand-built
    result tree would be `a fake more permissive than its subject`: the whole question here is what
    git's own merge produces for a path each side did or did not touch."""
    _commit(repo, "m.py", WIDE, "the base both sides share")
    _run(repo, "branch", "other")
    if ours is None:
        _commit(repo, "elsewhere.py", "def ours():\n    return 'this side worked elsewhere'\n",
                "this side never opens m.py")
    else:
        _commit(repo, "m.py", ours, "this side edits m.py too")
    parent = _run(repo, "rev-parse", "HEAD").strip()
    _run(repo, "checkout", "-q", "other")
    _commit(repo, "m.py", theirs, "the other lane deliberately drops the helper, and declares it")
    ref = _run(repo, "rev-parse", "HEAD").strip()
    _run(repo, "checkout", "-q", "main")
    merged = surgical_land.build_merge_tree(repo, parent, ref)
    changed = surgical_land.changed_paths(repo, parent + "^{tree}", merged)
    return parent, ref, merged, changed


def test_a_merge_over_a_path_this_side_never_touched_lands(repo: Path) -> None:
    """LEG 1 OF THE PARTITION. Adopting the other history's evolution of a file this side has not
    opened since the merge-base cannot delete anything of ours -- there is nothing of ours in it."""
    parent, ref, merged, changed = _diverge(repo, None, WITHOUT_HELPER)
    poison = scr.violations(repo, parent, merged, changed)
    assert [v.path for v in poison] == ["m.py"], (
        "POISON ROUND FIRST: told nothing about the merge, the guard must still refuse this tree, "
        "or leg 2 below is green for want of anything to refuse rather than because it works")
    assert scr.violations(repo, parent, merged, changed, merge_ref=ref) == [], (
        "the merge ref is threaded and this side never touched m.py, so this must land; refusing "
        "it is what forced 22df46614 to declare another lane's deletion as its own")
    assert scr.adopted_from_merge(repo, parent, ref, changed) == frozenset({"m.py"})


def test_a_merge_over_a_path_this_side_edited_is_still_refused(repo: Path) -> None:
    """LEG 2, AND IT IS THE WHOLE POPULATION THE GUARD WAS BUILT FOR. Both histories changed the
    file; adopting theirs deletes work of ours. The exemption must not reach it."""
    ours = WIDE.replace("    return 1\n", "    return 99\n")
    parent, ref, merged, changed = _diverge(repo, ours, WITHOUT_HELPER)
    losses = scr.violations(repo, parent, merged, changed, merge_ref=ref)
    assert [v.path for v in losses] == ["m.py"], (
        "a path this side edited must still be refused on a merge; if the merge ref buys a blanket "
        "pass, the guard is off for exactly the landing kind that reconciles two lanes")
    assert scr.adopted_from_merge(repo, parent, ref, changed) == frozenset()


def test_the_result_equals_the_ref_predicate_would_have_exempted_the_deletion_this_guard_exists_for(
        repo: Path) -> None:
    """THE TEMPTING PREDICATE, MEASURED AND REFUTED. 'Exempt a path whose result blob equals the
    merged ref's blob' reopens `a_merge_that_adopts_one_sides_rewrite_silently_deletes_the_other
    _sides_purely_additive_work`. Here the other history already carries this side's added line, so
    the merge result IS its blob byte for byte -- and it drops a name this side still has. The
    predicate that ships keys on THIS side's history, so it refuses; the blob predicate would not.
    """
    mine = "MINE = 'this side added this'\n\n\n"
    ours = WIDE.replace("def middle_one", mine + "def middle_one")
    theirs = WITHOUT_HELPER.replace("def middle_one", mine + "def middle_one")
    parent, ref, merged, changed = _diverge(repo, ours, theirs)
    assert scr.blob_at(repo, merged, "m.py") == scr.blob_at(repo, ref, "m.py"), (
        "the fixture no longer demonstrates the wrong predicate's failure: the result and the "
        "ref's blob must be identical for 'result == ref' to have exempted this")
    losses = scr.violations(repo, parent, merged, changed, merge_ref=ref)
    assert [v.path for v in losses] == ["m.py"]
    assert "freshly_landed_helper" in losses[0].detail or losses[0].rule == scr.PREDATES


def test_the_merge_refusal_does_not_name_a_remedy_the_merge_door_refuses(repo: Path) -> None:
    """A REFUSAL WHOSE STATED REMEDY DOES NOT EXIST IS PRESSURE TOWARD BYPASS. The default text
    diagnoses a working-tree copy and sends the lane to `--content`; `--merge` reads no working-tree
    copy and REFUSES `--content` outright, so on a merge both sentences are false of the landing
    they refuse."""
    # BOTH remedy shapes, because they name DIFFERENT working-tree doors and a merge refuses each:
    # holder work sends the lane to `--content`, a rival copy to `refresh_to_head`. Testing only one
    # left the other free to leak, which is how the per-path remedy reintroduced this defect.
    holder = scr.Loss("m.py", scr.SUBSET, ("freshly_landed_helper",), gains=("mine_only",))
    rival = scr.Loss("m.py", scr.SUBSET, ("freshly_landed_helper",), gains=())
    for loss, door in ((holder, "--content"), (rival, "refresh_to_head")):
        plain = scr.refusal_text([loss])
        merged = scr.refusal_text([loss], merge_ref="deadbeef1234")
        assert door in plain and "WORKING-TREE" in plain, (
            "the fixture no longer reaches the branch that names {}".format(door))
        assert door not in merged, (
            "the merge refusal names {}, a door `--merge` refuses outright".format(door))
        assert "WORKING-TREE" not in merged
        assert "--resolve" in merged and "deadbeef1" in merged and "m.py" in merged
        assert "--drops" in merged, "the declared-deletion route must still be named"


def test_the_landing_door_hands_the_guard_the_merge_ref(repo: Path) -> None:
    """FAIL-SILENT, the wiring half. The predicate is unreachable in production unless
    `_land_once` actually passes the other parent -- and it is one call site for both landing
    kinds. Read as code, so a comment describing the wiring cannot satisfy it."""
    src = searchable(
        (Path(__file__).resolve().parents[2] / "tools" / "surgical_land.py").read_text())
    assert "merge_ref=merge_parent" in src, (
        "the guard is back to seeing only (parent, result) on a merge")
    assert "stale_copy_refusal.refusal_text(reverts, merge_ref=merge_parent)" in src
    exempt = src.index("stale_copy_refusal.adopted_from_merge(")
    named = src.index("[stale-copy] {} path(s) adopted from {}", exempt)
    assert named > exempt, (
        "an exemption nobody can see is a hole -- the adopted paths must be printed by the landing")


# ------------------------------------------------------------------- the pre-commit door (--staged)


def _stage(root: Path, path: str, text: str) -> None:
    (root / path).write_text(text)
    _run(root, "add", path)


def test_the_cheap_door_refuses_a_staged_copy_that_predates_the_landing(repo: Path) -> None:
    """THE DEFECT THIS LEG OWNS, and it is the one the guard did not cover for its first day alive:
    `surgical_land` called this control and `git commit -- <path>` did not, so the careful door was
    guarded and the cheap, commoner one was open. A lane holding a stale copy reverted a landing by
    naming its path and every gate below was green on it."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    _stage(repo, "m.py", STALE_WITH_OWN_WORK)
    rc, text = scr.staged(repo, env={})
    assert rc == 1, "the staged stale copy was waved through the door it now has to face"
    assert "m.py" in text and "isolate_hunks" in text


def test_the_cheap_door_lets_an_honest_commit_through(repo: Path) -> None:
    """THE OTHER HALF OF THE PARTITION, and without it the leg above passes on a guard that refuses
    EVERYTHING -- which is the shape CLAUDE.md names: a guard that refuses everything passes every
    test that only asks whether it refuses correctly. A door that stops honest work is pressure
    toward `--no-verify`, and bypass is a wall."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    _stage(repo, "m.py", LANDED.replace("return 1", "return 99") + "\ndef mine():\n    return 0\n")
    rc, text = scr.staged(repo, env={})
    assert rc == 0, text
    assert "none reverts a landing" in text


def test_the_subject_is_the_staged_half_and_never_the_working_tree(repo: Path) -> None:
    """A PARTIAL COMMIT is the routine case on this shared tree -- CLAUDE.md's own discipline is to
    stage a precise pathspec -- and it is exactly where `the index` and `the disk` diverge. Reading
    the working copy here would judge a file the commit is not making, in BOTH directions: it would
    refuse a clean staged copy because of an unstaged one, and pass a stale staged copy because the
    disk had since been refreshed. This asserts the second, which is the fail-open one."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    _stage(repo, "m.py", STALE_WITH_OWN_WORK)          # the stale bytes are what would be COMMITTED
    (repo / "m.py").write_text(LANDED)                 # ...while the disk has since been refreshed
    rc, _text = scr.staged(repo, env={})
    assert rc == 1, (
        "a working-tree read passed a commit that reverts a landing, because the disk was clean "
        "and the index was not")


def test_an_index_that_will_not_write_out_is_a_failed_check_and_not_a_skip(repo: Path) -> None:
    """R15 FAIL-CLOSED. An unavailable check is a failed check; the alternative is a control that
    certifies whenever it cannot run, which is the direction that authorises what it guards."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    (repo / ".git" / "index").write_bytes(b"not an index")
    rc, text = scr.staged(repo, env={})
    assert rc == 1 and "could NOT RUN" in text, text


def test_a_repo_with_no_head_is_open_and_that_is_a_different_state(repo: Path) -> None:
    """Open, not fail-open: a first commit has no landing behind it to revert. Kept apart from the
    unwriteable-index leg above on purpose -- folding "nothing to check" into "could not check"
    is how a fail-closed rule acquires a silent hole."""
    fresh = repo.parent / "fresh"
    fresh.mkdir()
    _run(fresh, "init", "-q", "-b", "main")
    rc, text = scr.staged(fresh, env={})
    assert rc == 0 and "no HEAD" in text


def test_the_paired_skip_names_the_tree_and_a_token_for_any_other_tree_is_ignored(repo: Path):
    """THE SKIP IS THE ONE PLACE THIS COULD BECOME A BYPASS, so it is keyed to the tree sha and
    re-derived here rather than believed. `surgical_land` has already asked this question, WITH the
    landing's `--drops`, on the tree it names -- re-asking there would not add a check, it would
    delete the escape hatch at the only legal landing door. A token naming anything else is a claim
    about a tree nobody judged, and the check runs."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    _stage(repo, "m.py", STALE_WITH_OWN_WORK)
    tree = _run(repo, "write-tree").strip()

    rc, text = scr.staged(repo, env={scr.ALREADY_GATED_ENV: tree})
    assert rc == 0 and "already judged" in text, "the paired skip did not fire on its own tree"
    assert tree[:9] in text, "a skip that does not name the tree it trusted is unauditable"

    other = _run(repo, "rev-parse", "HEAD^{tree}").strip()
    assert other != tree
    rc, _ = scr.staged(repo, env={scr.ALREADY_GATED_ENV: other})
    assert rc == 1, "a token naming a DIFFERENT tree bought a pass -- that is a bypass, not a skip"
    rc, _ = scr.staged(repo, env={scr.ALREADY_GATED_ENV: "true"})
    assert rc == 1, "a truthy non-sha token bought a pass"


def test_the_guard_is_wired_into_the_cheap_door_too(repo: Path) -> None:
    """FAIL-SILENT, the same argument as the landing-door leg above and the reason this whole turn
    existed: the control was real, proven and reachable from exactly one caller, and the other
    caller is the one most commits actually go through.

    THE HOOK IS A SHELL SCRIPT, so `tools/python_code_text.searchable` -- the remedy for a control
    that reads source as text -- does not apply: it is a Python tokeniser. What that remedy buys is
    that prose cannot satisfy the assertion, and the shape below buys the same thing a different
    way: it selects the lines that RUN something (`python3 ...` at column zero) rather than
    rejecting the ones that look like comments. A commented-out gate line reads `# python3 ...` and
    is not selected, so neither the presence check nor the ordering can be satisfied by a comment.
    """
    hook = (Path(__file__).resolve().parents[2] / "tools" / "git-hooks" / "pre-commit").read_text()
    ran = [ln for ln in hook.splitlines() if ln.startswith("python3 ")]
    assert "python3 -m tools.stale_copy_refusal --staged || exit 1" in ran, (
        "the cheap door is unguarded again; a pathspec commit can revert a landing")
    order = [i for i, ln in enumerate(ran) if "stale_copy_refusal --staged" in ln]
    gate = [i for i, ln in enumerate(ran) if "pre_commit_test_gate" in ln]
    assert order and gate and order[0] < gate[0], (
        "this refusal is about the TREE, not the tests -- no suite can find it, so running the "
        "suite first only spends a full cycle to reach the same answer")


def test_a_restage_by_the_hook_chain_itself_re_asks_only_the_paths_it_moved(repo: Path) -> None:
    """THE WEDGE THIS OWNS, and it is a control that could not fail in the register's exact sense.

    The first block of `tools/git-hooks/pre-commit` re-stamps `docs/status/LATEST.md` and re-adds
    it. Any landing carrying that path therefore hands the hook a token for tree T and writes out
    tree T', the sha comparison fails, and the whole question is re-asked WITHOUT the caller's
    merge ref -- so a merge that `violations(merge_ref=...)` passed is refused for adopting the
    other history's landed deletions, with `refresh_to_head` printed as the remedy and HEAD itself
    behind. Eleven publish refusals and 36 hours of nothing published, 2026-09-21.

    KEYED TO THE PARTITION, NOT TO TODAY'S PATHS. Both legs below run on ONE tree state, so a
    guard that refused everything or passed everything fails one of them: the path the caller
    judged must NOT be re-asked, and the path the hook moved MUST be.
    """
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    _commit(repo, "n.py", "def beta():\n    return 1\n\n\ndef landed_in_n():\n    return 2\n", "n")

    # What the caller judged (WITH a merge ref / --drops it does not share): a rival copy of m.py
    # that supplies no name HEAD lacks. A bare re-ask refuses exactly this.
    _stage(repo, "m.py", RIVAL_SUPPLYING_NOTHING)
    judged = _run(repo, "write-tree").strip()

    # Then the hook chain itself re-stages a SECOND path, as the LATEST.md stamp does.
    _stage(repo, "n.py", "def beta():\n    return 1\n\n\ndef landed_in_n():\n    return 2\n\n\n"
                         "def a_stamp_the_hook_added():\n    return 3\n")
    moved = _run(repo, "write-tree").strip()
    assert moved != judged, "the fixture must reproduce the index moving under the token"

    rc, text = scr.staged(repo, env={scr.ALREADY_GATED_ENV: judged})
    assert rc == 0, (
        "a path the caller already judged was re-asked because the hook chain re-staged a "
        "DIFFERENT one -- this is the false refusal that wedged the fork:\n" + text)
    assert "n.py" in text and "m.py" not in text, (
        "the pass must name what it DID ask, or it is indistinguishable from a blanket skip: " + text)

    # THE MUTATION LEG. Same token, same shape -- the hook's own re-stage now reverts a landing.
    _stage(repo, "n.py", "def beta():\n    return 1\n")
    rc, text = scr.staged(repo, env={scr.ALREADY_GATED_ENV: judged})
    assert rc == 1 and "n.py" in text, (
        "the delta re-ask cannot fail, so it is not a check: a path the hook moved into a revert "
        "was passed:\n" + text)


def test_surgical_land_hands_the_hook_the_tree_it_actually_judged(repo: Path) -> None:
    """THE FAIL-OPEN THIS FORBIDS. `rederive_in` REBINDS `result_tree` on a merge, after the
    violations call. Handing the hook the post-rederive sha would assert a verdict for a tree no
    verdict describes -- and the hook, trusting it, would skip. Read as code so a comment saying
    the right thing cannot satisfy it."""
    src = searchable(
        (Path(__file__).resolve().parents[2] / "tools" / "surgical_land.py").read_text())
    call = src.index("stale_copy_refusal.violations(")
    pin = src.index("gated_tree = result_tree", call)
    rederive = src.index("result_tree, rederived = rederive_in(", call)
    gate = src.index("run_gate(checkout, hook_rel, gated_tree=gated_tree)", call)
    assert call < pin < rederive < gate, (
        "the token must be pinned to the judged tree BEFORE the re-derive can rebind it")
    assert "env[stale_copy_refusal.ALREADY_GATED_ENV] = gated_tree" in src


# ------------------------------------------------- which door the refusal sends the lane through

def _commands(text: str) -> list[str]:
    """The RUNNABLE doors in a refusal -- what a lane will actually paste. Asserting on the tool
    NAME instead would red on prose that explains why the other door does not apply, which is
    exactly what a refusal should say; the property is that only one door is offered."""
    return re.findall(r"python3 -m tools\.\w+", text)


#: A RIVAL copy that supplies NOTHING HEAD lacks. Not hypothetical: two of the eight copies the
#: 2026-09-08 census found on the shared tree are this shape, and the refusal sent both of them to
#: `isolate_hunks`, which correctly refuses at both ends -- so the lane had no move at all.
RIVAL_SUPPLYING_NOTHING = (
    "def alpha():\n"
    '    """an alternative wording of exactly the same behaviour, and nothing else"""\n'
    "    return 1\n"
)


def test_a_copy_supplying_nothing_head_lacks_is_sent_to_refresh_to_head(repo: Path) -> None:
    """THE FINDING'S OWN DEFECT. One remedy printed for two shapes is a remedy that is wrong for
    one of them, and the wrong half is the half with no legal move -- which is the pressure that
    points at `git checkout <path>`, the wall."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), RIVAL_SUPPLYING_NOTHING)
    assert loss is not None and loss.gains == (), (
        "a copy with no name of its own was not recognised as one")
    commands = _commands(loss.render())
    assert commands and all("refresh_to_head" in c for c in commands), (
        "the lane is still being sent to a tool that will refuse it whichever branch it takes: "
        "{}".format(commands))


def test_a_copy_carrying_holder_work_is_still_sent_to_isolate_hunks(repo: Path) -> None:
    """THE MIRROR, and the one that matters more: `refresh_to_head` OVERWRITES BYTES. Naming it for
    a copy that carries an unlanded function would destroy that lane's work through the repair for
    losing it."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), STALE_WITH_OWN_WORK)
    assert loss is not None and loss.gains == ("my_own_new_function",)
    commands = _commands(loss.render())
    assert commands and all("isolate_hunks" in c for c in commands), (
        "a copy holding unlanded work was pointed at the tool that overwrites it: "
        "{}".format(commands))


def test_neither_door_is_named_when_the_copy_cannot_be_read(repo: Path) -> None:
    """FAIL-CLOSED ON THE ADVICE TOO. A door named on a guess is worse than no advice: one of the
    two destroys bytes, and 'cannot tell' is a result that belongs on the surface."""
    _commit(repo, "p.html", "<div id='landed_anchor_one'></div>\n", "lane B lands a page anchor")
    loss = scr.judge(repo, "p.html", scr.blob_at(repo, "HEAD", "p.html"),
                     "<div id='landed_anchor_one'></div>\n")
    assert loss is None, "an identical page copy is not a loss"
    unreadable = scr.Loss("x.py", scr.PREDATES, ("a line",), "abc123", gains=None)
    text = unreadable.render()
    assert "cannot tell which door" in text
    assert not _commands(text), (
        "a runnable door was printed on a guess, and one of the two overwrites bytes: "
        "{}".format(_commands(text)))


# ------------------------------------------------------------ rule 3: the index nobody is holding
#
# The defect: `surgical_land` never refreshes the shared index, so a FAILED cycle's blobs sit there
# indefinitely while every working-tree reading agrees with HEAD. Banked as
# THE_SHARED_INDEX_STILL_HELD_THE_FAILED_CYCLES_PRE_LANDING_BLOBS (2026-09-09).
#
# Each test below names the way this rule could be useless. The two that matter most are the
# NEGATIVE ones: a rule that flags every staged path would pass every positive test here and be
# worthless, because it would refuse the ordinary staging that three concurrent lanes always have.


def _stage_then_restore(root: Path, path: str, staged_text: str) -> None:
    """Make residue exactly the way the real one is made: stage some other version, then leave the
    working copy equal to HEAD. This is what a failed landing cycle leaves behind."""
    head_text = _run(root, "show", "HEAD:{}".format(path))
    (root / path).write_text(staged_text)
    _run(root, "add", path)
    (root / path).write_text(head_text)


def test_an_index_entry_no_working_copy_asks_for_is_residue(repo: Path) -> None:
    """THE LIVE SHAPE. The index holds a version of a path that disk does not; a commit from it
    reverts HEAD while `git status` shows only the `MM` that every lane reads as another lane's
    work in flight."""
    _stage_then_restore(repo, "m.py", "def alpha():\n    return 999\n")
    assert scr.index_residue(repo) == ["m.py"]


def test_a_lanes_real_staged_work_is_not_residue(repo: Path) -> None:
    """THE FAILURE THAT WOULD MAKE THIS RULE WORTHLESS. A guard that refuses everything passes every
    positive test. Ordinary staged work -- in the index AND on disk -- must be invisible here, or
    the rule fires on the normal state of a tree three lanes are writing."""
    (repo / "m.py").write_text("def alpha():\n    return 2\n")
    _run(repo, "add", "m.py")
    assert scr.index_residue(repo) == []


def test_the_whole_partition_is_reachable_in_one_tree(repo: Path) -> None:
    """ONE CONTROL OVER THE PARTITION, not a leg per branch. Both answers must be reachable in the
    same tree: a rule that can only ever say 'residue' and one that can only ever say 'clean' both
    pass a suite made of single-sided tests."""
    _stage_then_restore(repo, "m.py", "def alpha():\n    return 999\n")
    (repo / "mine.py").write_text("def mine():\n    return 0\n")
    _run(repo, "add", "mine.py")

    residue = scr.index_residue(repo)
    staged_all = {p for p in _run(repo, "diff", "--cached", "--name-only").split() if p}

    assert residue == ["m.py"], "the frozen entry was not seen"
    assert "mine.py" in staged_all, "the fixture failed to stage the honest work at all"
    assert "mine.py" not in residue, "honest staged work was called residue"
    assert set(residue) < staged_all, (
        "residue must be a STRICT subset of what is staged -- equal means the rule is flagging "
        "everything, empty means it is flagging nothing")


def test_a_staged_deletion_with_the_file_still_on_disk_is_residue(repo: Path) -> None:
    """THE HALF-STAGED ARCHIVE MOVE, live on the shared tree the morning this landed: the index had
    dropped a `docs/staging/done/` document that HEAD and disk both still carried. Committing it
    deletes a document another control calls `.exists()` on."""
    _run(repo, "rm", "-q", "--cached", "m.py")
    assert (repo / "m.py").exists(), "the fixture removed the file from disk, which is a real move"
    assert scr.index_residue(repo) == ["m.py"]


def test_a_genuine_archive_move_is_not_residue(repo: Path) -> None:
    """THE FALSE POSITIVE THAT WOULD TURN THIS RULE OFF. `git mv` stages a deletion of the old path
    too -- and a door that refuses honest work through the one legal landing door is the pressure
    toward bypass. The old path is gone from DISK as well, so the working tree does not agree with
    HEAD and the path is out of scope."""
    (repo / "done").mkdir()
    _run(repo, "mv", "m.py", "done/m.py")
    assert scr.index_residue(repo) == []


def test_a_staged_add_of_a_file_absent_from_head_and_from_disk_is_residue(repo: Path) -> None:
    """THE THIRD LIVE SHAPE. Two of these were pre-archive ROOT copies of documents HEAD already
    held under `done/` and `records/` -- byte-identical, so committing them would have recreated
    the duplicate that reds the staging gate. Absence at both ends still counts as the working tree
    agreeing with HEAD."""
    (repo / "ghost.py").write_text("def ghost():\n    return 1\n")
    _run(repo, "add", "ghost.py")
    (repo / "ghost.py").unlink()
    assert scr.index_residue(repo) == ["ghost.py"]


def test_the_refusal_names_the_paths_and_the_runnable_repair(repo: Path) -> None:
    """A refusal that says why is how you discover the refusal itself was wrong. It must also print
    the repair that does NOT touch the working tree -- disk is the only copy that is correct here,
    so `git checkout` and `git stash` would destroy the good bytes."""
    _stage_then_restore(repo, "m.py", "def alpha():\n    return 999\n")
    text = scr.index_residue_text(scr.index_residue(repo))
    assert "m.py" in text
    assert "git reset HEAD -- m.py" in text
    assert "checkout" not in text and "stash" not in text, (
        "the refusal pointed at a door that overwrites the only correct copy")
    assert "none:" in scr.index_residue_text([]), "the clean verdict must still say what it checked"


# ------------------------------------------------------- rule 4: the census's own base is the trunk


def _trunk_at(root: Path, sha: str) -> None:
    """Give the repo an `origin/main` pointing at `sha`. A real ref, not a fake reader: `_base_state`
    asks git, and a stub that answered for it would be `a fake more permissive than its subject`."""
    _run(root, "update-ref", "refs/remotes/origin/main", sha)


def test_the_census_states_when_its_own_base_is_behind_the_trunk(repo: Path) -> None:
    """The defect: every REMEDY the census prints is computed against HEAD, and HEAD in a shared
    checkout is routinely behind `origin/main`. ONE control over the WHOLE partition -- level,
    behind, and absent -- because a control that only knows what the behind case must say goes
    green the day the caveat fires on every tree forever."""
    head = _run(repo, "rev-parse", "HEAD").strip()
    assert scr.base_caveat(repo) == "", (
        "a repo with NO origin/main has no trunk to be stale against, and a caveat there would red "
        "every archive checkout -- a control failing against a passer-by")
    _trunk_at(repo, head)
    assert scr.base_caveat(repo) == "", "the base IS the trunk and the census owes no caveat"
    ahead = _commit(repo, "m.py", LANDED, "the trunk moves on")
    _run(repo, "reset", "--hard", "-q", head)
    _trunk_at(repo, ahead)
    caveat = scr.base_caveat(repo)
    assert caveat, "HEAD is behind the trunk and the census said nothing about its own base"
    assert "1 commit(s) behind" in caveat, (
        "the caveat must carry the LAG it was measured at, not a fixed sentence: " + caveat)
    assert "surgical_land --content" in caveat, (
        "the caveat must name the door the inverted reading sends the lane through, because that "
        "is the door that writes over the trunk")


def test_a_copy_the_trunk_supersedes_reads_as_holder_work_when_the_base_is_behind(repo: Path):
    """The inversion the caveat exists for, reproduced rather than asserted about. `gains_over` is
    which door the lane walks through -- empty is `refresh_to_head`, non-empty is
    `surgical_land --content`. Ask it against a behind HEAD and a copy the trunk ALREADY holds comes
    back as holder work, which sends the lane to land a revert of the trunk.

    Measured on the live tree 2026-09-15: the census called `tools/generate_value_arms_data.py`
    holder work for supplying `BLIND_ENVELOPE_ARMS_PATH`, which `origin/main` had held since
    `78829dbf9`."""
    head = _run(repo, "rev-parse", "HEAD").strip()
    trunk = _commit(repo, "m.py", LANDED, "the trunk lands freshly_landed_helper")
    _run(repo, "reset", "--hard", "-q", head)
    _trunk_at(repo, trunk)
    head_text = scr.blob_at(repo, "HEAD", "m.py")
    trunk_text = scr.blob_at(repo, "origin/main", "m.py")
    assert scr.gains_over(head_text, LANDED, "m.py") == ("freshly_landed_helper",), (
        "against the BEHIND base the copy reads as holder work -- this is the defect, and if this "
        "leg stops holding the caveat is guarding nothing")
    assert scr.gains_over(trunk_text, LANDED, "m.py") == (), (
        "against the TRUNK the same copy supplies nothing, so the honest door was refresh_to_head "
        "all along and the two bases disagree about which door exists")


#: The copy taken BEFORE the landing below. It keeps every module-level name (`alpha` is the only
#: one either side declares), so the symbol-subset leg is blind to it by construction: what the
#: landing changed is an ARGUMENT at a call site, and rule 2 does not read call sites.
PRE_CALL_SITE_LANDING = (
    "def alpha():\n"
    "    first = helper(\n"
    "        1,\n"
    "    )\n"
    "    second = helper(\n"
    "        2,\n"
    "    )\n"
    "    return first + second\n"
)

#: `dcb8c6d10` against `simulation/renewals.py`, reduced to its shape. Every line it adds is thrown
#: away by one filter or the other: three COMMENTS, and `fuel="electricity",` added TWICE, so the
#: uniqueness filter drops it as unable to discriminate. Five added lines, zero survivors.
CALL_SITE_LANDING = (
    "def alpha():\n"
    "    # THIS BUILDER IS ELECTRICITY'S AND NAMES IT: it took no fuel until gas needed one,\n"
    "    # and it now refuses to guess -- a builder that guesses a commodity is one that\n"
    "    # prices the wrong fuel in silence and says nothing whatever about having done so.\n"
    "    first = helper(\n"
    "        1,\n"
    '        fuel="electricity",\n'
    "    )\n"
    "    second = helper(\n"
    "        2,\n"
    '        fuel="electricity",\n'
    "    )\n"
    "    return first + second\n"
)


def test_a_landing_whose_added_lines_are_all_filtered_still_yields_evidence(repo: Path) -> None:
    """MUTATION: delete the `comments_are_evidence` fallback in `distinctive_lines` and this FIRES.

    THE FILTERS ARE ALSO A FAIL-OPEN, which is the half this file already knew about the duplicate
    filter -- `test_a_repeated_line_is_not_evidence_of_freshness` says in terms that an empty set
    makes rule 1 unreachable -- and never asked about the comment filter. `judge` guards rule 1
    with `if distinctive:`, so a filter that empties the set does not weaken the question, it
    DELETES it, and the copy is graded by the symbol leg alone.

    Live instance, 2026-09-16: `dcb8c6d10` added exactly three comments and one twice-repeated line
    to `simulation/renewals.py`. Both filters fired, the evidence set was empty, and a working copy
    twelve days older than the landing -- missing the `fuel=` argument the same commit had just
    made required -- was graded CLEAN by the census while the tests it broke went red."""
    _commit(repo, "m.py", PRE_CALL_SITE_LANDING, "the base the landing lands over")
    sha = _commit(repo, "m.py", CALL_SITE_LANDING, "a landing whose every added line is filtered")
    assert scr.distinctive_lines(repo, "m.py", sha), (
        "every added line was filtered away, so rule 1 is never asked and the staleness question "
        "is deleted rather than answered -- this is the fail-open, not a conservative reading")


def test_the_comment_fallback_does_not_displace_code_evidence(repo: Path) -> None:
    """THE OTHER SIDE OF THE PARTITION, and the reason this is a fallback and not a widening.

    A control whose evidence set silently grew to include every comment would be a DIFFERENT
    control: comments travel with cherry-picks, rewraps and reverts, so preferring them over code
    would make the refusal noisier everywhere it already works. Asserting the fallback FIRES says
    nothing about whether it fires only where it is needed -- so assert the strong branch is still
    taken while code evidence exists, or `comments_are_evidence=True` may as well be unconditional.
    Both branches are constructed here because a fallback that had quietly become the only branch
    would pass the test above and nothing else in this file would notice."""
    _commit(repo, "m.py", PRE_CALL_SITE_LANDING, "the base")
    mixed = CALL_SITE_LANDING + "\n\ndef beta():\n    return 8675309\n"
    sha = _commit(repo, "m.py", mixed, "a landing carrying BOTH comments and distinctive code")
    distinctive = scr.distinctive_lines(repo, "m.py", sha)
    assert any("8675309" in d for d in distinctive), "the code line is the strong evidence"
    assert not any(d.startswith("#") for d in distinctive), (
        "while code evidence survives, the comment filter still applies -- the fallback must be "
        "reachable ONLY where the strong set is empty, or it is a widening wearing a fallback's name")


def test_a_call_site_only_stale_copy_is_refused(repo: Path) -> None:
    """THE CONSEQUENCE, end to end: what `judge` actually returns for the live shape.

    The two rules are not redundant here, they are BOTH blind. Rule 2 compares declared names and
    this copy keeps every one of them -- only an argument inside a call differs. So rule 1 emptied
    is the whole of the control, and without the fallback `judge` returns None on a copy that
    reverts a landing. The `scr.PREDATES` leg is asserted explicitly because a refusal arriving by
    any other rule would be the right answer for the wrong reason."""
    _commit(repo, "m.py", PRE_CALL_SITE_LANDING, "the base")
    _commit(repo, "m.py", CALL_SITE_LANDING, "the landing")
    head_text = scr.blob_at(repo, "HEAD", "m.py")
    assert scr.symbols(head_text, "m.py") == scr.symbols(PRE_CALL_SITE_LANDING, "m.py"), (
        "if the two sides ever declare different names, rule 2 can see this copy and rule 1 is no "
        "longer the only thing standing between it and a clean verdict -- the test would still "
        "pass, and would have stopped being about the hole it was written for")
    loss = scr.judge(repo, "m.py", head_text, PRE_CALL_SITE_LANDING)
    assert loss is not None, "a copy predating the landing was graded clean"
    assert loss.rule == scr.PREDATES, "it must be refused AS predating the landing"


# ------------------------------------------------------- the third verdict: a name HEAD CUT ON PURPOSE
#
# The defect, banked as THE_HOLDER_WORK_VERDICT_NAMED_A_FORBIDDEN_IMPORT_AS_WORK_TO_LAND_AND_IT_WAS_
# RED_ON_THE_TREE (2026-09-16): "supplies a name HEAD lacks" is a SET DIFFERENCE, and a set
# difference cannot tell a name HEAD never had from one HEAD deleted on purpose. The live instance
# was an import HEAD forbids in a comment naming the 33-hour outage it caused, and the remedy
# printed beside it was `surgical_land --content` -- land it back.
#
# Each test below names the way this discriminator could be useless. The two that matter most are
# the NEGATIVE ones: a discriminator that called EVERY new name a cut would pass every positive
# test here and be far worse than the defect, because the cut door OVERWRITES BYTES.

#: HEAD's bytes: the helper the copy still carries was DELETED here, on purpose, and a distinctive
#: line landed with the deletion. This is the live shape -- a test that went red as designed, an
#: import cut for a measured outage -- not an invented one.
CUT_LANDING = (
    "def alpha():\n    return 1\n\n\n"
    "def replacement_helper(argument):\n"
    '    """The one distinctive line this landing added, appearing exactly once."""\n'
    "    return argument * 41 + 7\n"
)

#: The stale copy: taken before that landing, so it still binds the deleted name and nothing else.
COPY_CARRYING_THE_CUT = (
    "def alpha():\n    return 1\n\n\n"
    "def deliberately_deleted_helper():\n    return 'the decision HEAD recorded by removing me'\n"
)


def _cut_fixture(repo: Path) -> str:
    """Bind the name, then DELETE it in a landing. Returns the deleting commit."""
    _commit(repo, "m.py", COPY_CARRYING_THE_CUT, "the helper is written")
    return _commit(repo, "m.py", CUT_LANDING, "the helper is deleted on purpose")


def test_a_name_head_deleted_on_purpose_is_a_cut_and_never_holder_work(repo: Path) -> None:
    """THE DEFECT ITSELF. Before this discriminator the verdict read 'so it is HOLDER WORK' and sent
    the lane to `surgical_land --content`, which lands the deletion back. The set difference is
    IDENTICAL in both cases, so nothing about the name alone can tell them apart -- only git can."""
    removed_at = _cut_fixture(repo)
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), COPY_CARRYING_THE_CUT)
    assert loss is not None and loss.gains == ("deliberately_deleted_helper",), (
        "the fixture no longer reaches the holder-work verdict, so it cannot show it was wrong")
    assert [c.name for c in loss.cuts] == ["deliberately_deleted_helper"], (
        "a name HEAD deleted on purpose is still reading as a name HEAD never had")
    assert loss.cuts[0].commit == removed_at, "the cut must name the commit that removed it"
    text = loss.render()
    assert removed_at[:9] in text, "the reader cannot check the claim without the commit"
    assert "--content" not in text, (
        "the land-it remedy is still printed for a copy whose only 'new' name re-creates a "
        "deletion: {}".format(text))
    assert _commands(text) and all("refresh_to_head" in c for c in _commands(text)), (
        "a copy that supplies nothing HEAD did not delete is a rival copy, and the door for one is "
        "the refresh: {}".format(_commands(text)))


def test_a_name_head_never_had_is_still_holder_work(repo: Path) -> None:
    """THE NEGATIVE CONTROL, and it is the one that matters more: the cut door OVERWRITES BYTES. A
    discriminator that answered 'cut' for every unfamiliar name would pass the test above and
    destroy a lane's unlanded work through the repair for losing it."""
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), STALE_WITH_OWN_WORK)
    assert loss is not None and loss.gains == ("my_own_new_function",)
    assert loss.cuts == () and loss.novel == ("my_own_new_function",), (
        "a name this history never bound was called a deliberate deletion, which points the "
        "overwriting door at a lane's real work")
    assert not loss.is_rival, "holder work must never read as a rival copy"


def test_a_name_that_only_ever_APPEARED_is_not_a_cut(repo: Path) -> None:
    """THE PICKAXE IS THE CANDIDATE FINDER, NOT THE ORACLE. `git log -S` moves on any occurrence of
    the token -- a comment, a docstring, a call site. Reading those as 'HEAD once had this name'
    would call a copy's genuinely new function a re-creation, on the strength of a sentence
    mentioning it. The live instance's own HEAD docstring says in words that its test is deleted,
    so this is the normal case and not a contrived one."""
    _commit(repo, "m.py", "def alpha():\n    # mentions never_bound_helper and nothing more\n"
                          "    return 1\n", "a comment mentioning a name")
    _commit(repo, "m.py", LANDED, "lane B lands a helper")
    supplies = "def alpha():\n    return 2\n\n\ndef never_bound_helper():\n    return 'new'\n"
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), supplies)
    assert loss is not None and "never_bound_helper" in (loss.gains or ()), (
        "the fixture no longer supplies the name, so it cannot show how it is classified")
    assert loss.cuts == (), (
        "a name that only ever appeared in a COMMENT was read as a binding HEAD deleted")
    assert scr.cut_of(repo, "m.py", "never_bound_helper") is None


def test_a_copy_carrying_both_a_cut_and_real_work_may_never_be_landed_whole(repo: Path) -> None:
    """THE MIXED SHAPE, and the reason the cut verdict is not simply the rival-copy verdict. Some of
    this copy IS holder work, so the refresh would destroy it -- and landing the file whole puts the
    deletion back. Only hunk selection is legal, and the refusal has to say which hunks."""
    removed_at = _cut_fixture(repo)
    mixed = COPY_CARRYING_THE_CUT + "\n\ndef genuinely_new_work():\n    return 'unlanded'\n"
    loss = scr.judge(repo, "m.py", scr.blob_at(repo, "HEAD", "m.py"), mixed)
    assert loss is not None and loss.novel == ("genuinely_new_work",) and len(loss.cuts) == 1, (
        "the fixture no longer produces a copy that is BOTH, which is what this test is about")
    assert not loss.is_rival, "a copy carrying unlanded work must never be sent to the overwriter"
    text = loss.render()
    assert "--content" in text and "NOT `--content" in text, (
        "the whole-file door must be named only to forbid it: {}".format(text))
    assert _commands(text) and all("isolate_hunks" in c for c in _commands(text)), (
        "the only legal move is hunk selection: {}".format(_commands(text)))
    assert removed_at[:9] in text and "genuinely_new_work" in text, (
        "the lane cannot select correctly unless the refusal names both halves")


def test_the_whole_three_way_partition_is_reachable_in_one_tree(repo: Path) -> None:
    """A CONTROL OVER THE PARTITION, NOT A LEG PER BRANCH. A discriminator stuck on any one answer
    passes two of the three tests above; only asking for all three at once refuses it."""
    removed_at = _cut_fixture(repo)
    head = scr.blob_at(repo, "HEAD", "m.py")
    cut = scr.judge(repo, "m.py", head, COPY_CARRYING_THE_CUT)
    holder = scr.judge(repo, "m.py", head,
                       "def alpha():\n    return 1\n\n\ndef mine():\n    return 2\n")
    rival = scr.judge(repo, "m.py", head, "def alpha():\n    return 1\n")
    assert cut is not None and holder is not None and rival is not None
    assert cut.cuts and cut.is_rival, "the cut verdict is unreachable"
    assert not holder.cuts and holder.novel and not holder.is_rival, "holder work is unreachable"
    assert rival.gains == () and not rival.cuts and rival.is_rival, "the rival verdict is unreachable"
    assert removed_at[:9] in cut.render()


def test_a_census_that_cannot_import_its_own_siblings_ANSWERS_and_never_raises(
        repo: Path, monkeypatch) -> None:
    """The composition from
    `SEAT_FINDING_THE_STALE_COPY_CENSUS_CRASHES_IN_THE_SHARED_TREE_BECAUSE_ITS_OWN_SIBLING_MODULES_NEVER_REACHED_DISK_2026-09-08.md`,
    where `--census` raised `ImportError` for every lane in the shared tree at once.

    A lane landed `landing_pair`/`refresh_to_head` to origin through `surgical_land` -- which never
    writes the working tree, deliberately -- the shared tree could not fast-forward because three
    unrelated lanes held live bytes, and this module was left on disk importing two siblings the
    tree had never received. Every step is another lane's correct behaviour, which is why nothing
    else could see it.

    THE ASSERTION IS ON THE READER'S SURFACE AND NOT ON THE ABSENCE OF A RAISE. Returning `{}` also
    does not raise, and reads as *every door is open* -- the flattering answer, and the one this
    project's whole `fail closed, and SAY SO` rule exists to refuse.
    """
    real_import = builtins.__import__

    def without_siblings(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "tools" and any(f in (fromlist or ()) for f in ("landing_pair", "refresh_to_head")):
            raise ImportError("cannot import name 'landing_pair' from 'tools' (unknown location)")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", without_siblings)
    out = scr.door_verdicts([], repo)

    assert list(out) == [scr.UNGRADED_DOORS], (
        "a census that could not ask any door reported no shut door, which is not the same thing")
    said = out[scr.UNGRADED_DOORS]
    assert "MISSING, not clean" in said, "the reader must be told the column is absent, not empty"
    # The durable workaround, because a refusal that names no move is a refusal nobody can act on
    # -- and this one needs no fast-forward and cannot touch another lane's bytes.
    assert "--root" in said and "origin/main" in said, (
        "the refusal names no way out: {}".format(said))


def test_the_sentinel_key_cannot_be_mistaken_for_a_censused_path(repo: Path) -> None:
    """The anti-collision leg for the mapping above, and it is not pedantry: `door_verdicts` is
    keyed by path and the caller renders `verdicts[loss.path]` under each row. A sentinel a real
    path could equal would render the caveat as one file's door verdict and hide the caveat."""
    assert "\0" in scr.UNGRADED_DOORS, "a sentinel a filename could hold is not a sentinel"
    losses, no_opinion = scr.census(repo)
    assert scr.UNGRADED_DOORS not in {loss.path for loss in losses} | set(no_opinion)
