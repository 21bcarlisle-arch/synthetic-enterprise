"""The defect: a pathspec stages the WORKING-TREE copy, so a lane holding a stale copy of a file
silently reverts another lane's landed commit, and every gate downstream is green on it because the
tree it reverts to was valid an hour ago.

Each test names the specific way this control could be useless rather than merely exercising it.
"""
from __future__ import annotations

import ast
import re
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
