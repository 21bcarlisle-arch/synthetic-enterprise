"""The defect: a rival working copy HEAD strictly supersedes had NO legal repair, so the pressure
pointed at `git checkout <path>`, which is the wall.

The danger in the fix is the mirror image -- a tool that writes HEAD over a working copy is
`git checkout` unless its refusals hold, so every test here names a way the refusals could be
useless rather than exercising the happy path twice.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import refresh_to_head as rth


def _run(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout


LANDED = (
    "def alpha():\n    return 1\n\n\n"
    "def freshly_landed_helper(argument):\n"
    '    """A distinctive line that appears exactly once in this file."""\n'
    "    return argument * 41 + 7\n"
)

#: KIND A -- the shape with no legal move before this tool. Another lane wrote the same file
#: independently, worded it differently, and never pulled the landing: it supplies NO name HEAD
#: lacks, so `isolate_hunks` has nothing legitimate to select and refuses both ways round.
RIVAL_KIND_A = (
    "def alpha():\n"
    '    """an alternative wording of exactly the same behaviour, and nothing else"""\n'
    "    return 1\n"
)

#: KIND B -- carries a name of its own. The drawn remedy applies to this one and this tool must not.
RIVAL_KIND_B = (
    "def alpha():\n    return 1\n\n\n"
    "def my_own_unlanded_function():\n"
    "    return 'work that only exists in this lane and nowhere else'\n"
)

#: An ORDINARY EDIT on top of the landing: it has the distinctive line, and its symbol set is
#: HEAD's exactly. Nothing is stale about it.
ORDINARY_EDIT = LANDED.replace("return argument * 41 + 7", "return argument * 41 + 8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo. The subject is git trees, refs and a throwaway index; a fake would be
    `a fake more permissive than its subject`, which is how a fail-open goes green."""
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "m.py").write_text("def alpha():\n    return 1\n")
    (root / "notes.md").write_text("# notes\n\nprose\n")
    _run(root, "add", "m.py", "notes.md")
    _run(root, "commit", "-qm", "base")
    (root / "m.py").write_text(LANDED)
    _run(root, "add", "m.py")
    _run(root, "commit", "-qm", "lane B lands a helper")
    return root


# ------------------------------------------------------ the permissive branch must be REACHABLE


def test_a_kind_a_rival_copy_is_refreshed_and_the_bytes_on_disk_become_heads(repo: Path) -> None:
    """REACHABILITY FIRST. Every other test here asserts a refusal, and a tool that refuses
    EVERYTHING passes all of them while repairing none of the eight copies it was built for."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    rc, text = rth.refresh(repo, ["m.py"], "kind-a", write=True)
    assert rc == 0, text
    assert (repo / "m.py").read_text() == LANDED, (
        "the working copy was not replaced by HEAD's bytes, so the one move this tool exists to "
        "make did not happen")


def test_the_discarded_bytes_come_back_through_the_advertised_git_log_all_dash_s(repo: Path) -> None:
    """THE PRESERVATION IS THE LICENCE. If `git log --all -S` cannot find the bytes, this tool is
    `git checkout` and the refusals were decoration. Run the search, do not print it."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    rc, _ = rth.refresh(repo, ["m.py"], "kind-a", write=True)
    assert rc == 0
    probe = "an alternative wording of exactly the same behaviour"
    found = _run(repo, "log", "--all", "--format=%H", "-S", probe, "--", "m.py").split()
    assert found, "the preserved bytes are not reachable by the recovery route the tool advertises"
    assert _run(repo, "show", "{}:m.py".format(found[0])) == RIVAL_KIND_A


def test_the_preserved_commit_is_on_no_branch(repo: Path) -> None:
    """It must not enter anyone's history. A preservation that advances a branch is a landing that
    faced no gate, and that is the hook-bypass wall wearing a helpful name."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    rth.refresh(repo, ["m.py"], "kind-a", write=True)
    assert _run(repo, "rev-parse", "HEAD").strip() == _run(repo, "rev-parse", "main").strip()
    assert _run(repo, "show", "main:m.py") == LANDED
    refs = _run(repo, "for-each-ref", "--format=%(refname)").split()
    assert rth.PRESERVED_PREFIX + "kind-a" in refs


# ----------------------------------------------------------------------------- the refusals


def test_a_copy_supplying_a_name_head_lacks_is_refused_and_not_touched(repo: Path) -> None:
    """THE REFUSAL THAT STOPS THIS BEING `git checkout`. A Kind-B copy is holder work; writing
    HEAD over it destroys a lane's unlanded function, which is the exact harm the prohibition on
    `git checkout <path>` exists to prevent."""
    (repo / "m.py").write_text(RIVAL_KIND_B)
    rc, text = rth.refresh(repo, ["m.py"], "kind-b", write=True)
    assert rc == 1 and rth.SUPPLIES_NEW in text
    assert "my_own_unlanded_function" in text, "the refusal did not name what it was protecting"
    assert (repo / "m.py").read_text() == RIVAL_KIND_B, "a refused path was written anyway"
    assert "isolate_hunks" in text, "a refusal with no next move is where a bypass comes from"


def test_an_ordinary_edit_the_stale_copy_control_does_not_refuse_is_refused_here(repo: Path) -> None:
    """WITHOUT THIS LEG THE TOOL REVERTS ANYTHING. The symbol test alone passes an ordinary edit
    that only changes a value -- same names, no new ones -- and reverting that is `git checkout`."""
    (repo / "m.py").write_text(ORDINARY_EDIT)
    verdict = rth.judge_copy(repo, "m.py")
    assert verdict.state == rth.NOT_SUPERSEDED, (
        "an edit HEAD does not supersede was licensed for refresh; the tool is a revert button")
    assert not verdict.gains, "the symbol test alone cannot see this one -- that is why leg 2 exists"


def test_a_suffix_with_no_symbol_reader_is_refused_rather_than_waved_through(repo: Path) -> None:
    """FAIL-CLOSED. 'Supplies nothing HEAD lacks' is UNESTABLISHED for a `.md` file, and an
    unestablished precondition is a failed one -- folding it to 'no names either side' would make
    every prose file eligible while looking checked."""
    (repo / "notes.md").write_text("# notes\n\nthis lane's rewrite of the prose\n")
    verdict = rth.judge_copy(repo, "notes.md")
    assert verdict.state == rth.NO_READER
    rc, _ = rth.refresh(repo, ["notes.md"], "prose", write=True)
    assert rc == 1 and "this lane's rewrite" in (repo / "notes.md").read_text()


def test_a_path_the_holder_has_staged_is_refused(repo: Path) -> None:
    """A commit makes the tree from the INDEX. Refreshing the working copy under a staged revert
    leaves the revert armed and the census clean -- repaired-looking and not repaired."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    _run(repo, "add", "m.py")
    verdict = rth.judge_copy(repo, "m.py")
    assert verdict.state == rth.STAGED, (
        "a staged rival copy was treated as refreshable; the commit it feeds still reverts")


def test_a_file_head_does_not_have_is_refused(repo: Path) -> None:
    """A wholly new file is not contested and there is no HEAD version to supersede it with."""
    (repo / "brand_new.py").write_text("def novel():\n    return 'mine alone'\n")
    assert rth.judge_copy(repo, "brand_new.py").state == rth.NO_BASE


# --------------------------------------------------------------- ordering and all-or-nothing


def test_nothing_is_written_when_the_preservation_cannot_be_verified(
        repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE ORDER IS THE SAFETY. Preserve, PROVE the bytes come back, then destroy. If the proof
    can fail after the write this tool is a data-loss machine with a reassuring log line."""
    (repo / "m.py").write_text(RIVAL_KIND_A)

    def _fails(*_args, **_kwargs):
        raise rth.RefreshError("the recovery route does not reach it")

    monkeypatch.setattr(rth, "verify_recoverable", _fails)
    with pytest.raises(rth.RefreshError):
        rth.refresh(repo, ["m.py"], "kind-a", write=True)
    assert (repo / "m.py").read_text() == RIVAL_KIND_A, (
        "the working copy was destroyed although the preservation was never proven recoverable")


def test_verify_refuses_a_preserved_commit_no_ref_reaches(repo: Path) -> None:
    """THE `-S` LEG, EXERCISED. `git log --all` walks REFS. A preservation commit that exists as a
    loose object and nothing points at it is unfindable by the advertised route and collectable by
    gc -- and its `git show <sha>` identity leg passes happily, so identity alone is not the check.
    Without this the second leg is a control that cannot fail."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    work = (repo / "m.py").read_bytes()
    _ref, commit = rth.preserve(repo, ["m.py"], "orphaned", "preserved")
    _run(repo, "update-ref", "-d", rth.PRESERVED_PREFIX + "orphaned")
    probe = "an alternative wording of exactly the same behaviour"
    with pytest.raises(rth.RefreshError, match="does not find"):
        rth.verify_recoverable(repo, commit, "m.py", work, probe)


def test_verify_refuses_when_the_preserved_blob_is_not_the_bytes_on_disk(repo: Path) -> None:
    """THE IDENTITY LEG. A preservation of the WRONG bytes is worse than none: the log line says
    the work is safe and the recovery hands back something else."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    _ref, commit = rth.preserve(repo, ["m.py"], "identity", "preserved")
    with pytest.raises(rth.RefreshError, match="PRESERVATION FAILED"):
        rth.verify_recoverable(repo, commit, "m.py", b"not what was on disk", None)


def test_a_readable_suffix_whose_reader_returns_nothing_still_fails_closed(
        repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TWO MODULES MUST AGREE AND NOTHING MAKES THEM. `READABLE` and `symbols()` both come from
    `stale_copy_refusal`, and this tool trusts their agreement: a suffix added to the first without
    a reader in the second would reach the symbol comparison with `None` on one side. Today that
    branch is unreachable -- established, not assumed -- so it is pinned as the DIVERGENCE guard it
    is, rather than deleted and re-learned the day the two lists part."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    monkeypatch.setattr(rth, "symbols", lambda text, path: None)
    verdict = rth.judge_copy(repo, "m.py")
    assert verdict.state == rth.NO_READER, (
        "an unreadable copy was licensed for refresh because one of the two lists moved")


def test_one_refused_path_stops_the_whole_run(repo: Path) -> None:
    """A lane's work is not path-shaped. Half-applying a multi-path refresh leaves a tree neither
    lane wrote, and the refusal that stopped it would be buried under a success line."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    (repo / "notes.md").write_text("# notes\n\nrewritten\n")
    rc, text = rth.refresh(repo, ["m.py", "notes.md"], "mixed", write=True)
    assert rc == 1
    assert (repo / "m.py").read_text() == RIVAL_KIND_A, "the refreshable half was applied anyway"
    assert "nothing written" in text


def test_survey_is_the_default_and_writes_nothing(repo: Path) -> None:
    """The line-level losses are what a symbol test cannot see, so they are printed BEFORE any
    byte moves. A tool whose survey mode writes has no survey mode."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    rc, text = rth.refresh(repo, ["m.py"], None, write=False)
    assert rc == 0 and "SURVEY ONLY" in text
    assert (repo / "m.py").read_text() == RIVAL_KIND_A
    assert "alternative wording" in text, (
        "the survey did not print the lines that would be discarded, so signing it off is blind")


def test_the_holders_own_index_is_not_touched_by_the_preservation(repo: Path) -> None:
    """`preserve` builds its tree through a THROWAWAY index. Writing HEAD+bytes into the real one
    would stage the preserved copy into the holder's next commit -- landing the revert this whole
    class exists to stop, out of the repair for it."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    (repo / "other.py").write_text("def unrelated():\n    return 0\n")
    _run(repo, "add", "other.py")
    before = _run(repo, "diff", "--cached", "--name-only").split()
    rth.refresh(repo, ["m.py"], "kind-a", write=True)
    assert _run(repo, "diff", "--cached", "--name-only").split() == before == ["other.py"]


def test_write_without_a_slug_is_refused(repo: Path) -> None:
    """The ref name is how a lane finds its own bytes again without already knowing the string to
    search for. An unnamed preservation is recoverable only by someone who does not need it."""
    (repo / "m.py").write_text(RIVAL_KIND_A)
    rc, text = rth.refresh(repo, ["m.py"], None, write=True)
    assert rc == 1 and "--slug" in text
    assert (repo / "m.py").read_text() == RIVAL_KIND_A


def test_every_verdict_in_the_partition_is_reachable(repo: Path) -> None:
    """ONE CONTROL OVER THE WHOLE PARTITION. Each leg above proves its own branch; this proves no
    later edit can collapse them onto one another -- a tool that answers REFUSED to every shape
    passes every refusal test in this file."""
    (repo / "notes.md").write_text("# notes\n\nrewritten prose\n")
    (repo / "brand_new.py").write_text("def novel():\n    return 1\n")
    states = set()
    for content, state in ((RIVAL_KIND_A, rth.REFRESHABLE), (RIVAL_KIND_B, rth.SUPPLIES_NEW),
                           (ORDINARY_EDIT, rth.NOT_SUPERSEDED), (LANDED, rth.AT_HEAD)):
        (repo / "m.py").write_text(content)
        got = rth.judge_copy(repo, "m.py").state
        assert got == state, "{} was judged {}, not {}".format(state, got, state)
        states.add(got)
    states.add(rth.judge_copy(repo, "notes.md").state)
    states.add(rth.judge_copy(repo, "brand_new.py").state)
    assert states == {rth.REFRESHABLE, rth.SUPPLIES_NEW, rth.NOT_SUPERSEDED, rth.AT_HEAD,
                      rth.NO_READER, rth.NO_BASE}
