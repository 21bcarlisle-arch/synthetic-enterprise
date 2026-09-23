"""The defect: a rival working copy HEAD strictly supersedes had NO legal repair, so the pressure
pointed at `git checkout <path>`, which is the wall.

The danger in the fix is the mirror image -- a tool that writes HEAD over a working copy is
`git checkout` unless its refusals hold, so every test here names a way the refusals could be
useless rather than exercising the happy path twice.
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest

from tools import refresh_to_head as rth
from tools import stale_copy_refusal as scr
from tools.stale_copy_refusal import judge


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

#: KIND B AS THIS FILE FIRST WROTE IT, and it was MIS-SPECIFIED -- kept under its own name because
#: the correction is the finding. It was labelled "carries a name of its own, the drawn remedy
#: applies to this one", and the drawn remedy (`isolate_hunks --keep N`, then `--content`) has NO
#: legal application to it: it REPLACES `freshly_landed_helper` in a single indivisible hunk, so
#: every selection that takes `my_own_unlanded_function` also deletes landed work. That is
#: `SEAT_FINDING_THE_HOLDER_WORK_RULE_COUNTS_NAMES_SO_A_RENAMED_DRAFT_READS_AS_WORK_TO_LAND`'s
#: whole point, standing in this suite's own fixture for nine days: at the level of a symbol SET a
#: replacement and an addition are identical, so the fixture that was supposed to prove the Kind-B
#: branch was an instance of the defect instead.
RIVAL_KIND_B = (
    "def alpha():\n    return 1\n\n\n"
    "def my_own_unlanded_function():\n"
    "    return 'work that only exists in this lane and nowhere else'\n"
)

#: GENUINE HOLDER WORK, which is what `RIVAL_KIND_B` was believed to be: it ADDS and deletes
#: nothing, so `--keep` has a selection and the land-it door is the right one to be sent to.
HOLDER_APPENDS = LANDED + (
    "\n\ndef my_own_unlanded_function():\n"
    "    return 'work that only exists in this lane and nowhere else'\n"
)

#: An ORDINARY EDIT on top of the landing: it has the distinctive line, and its symbol set is
#: HEAD's exactly. Nothing is stale about it.
ORDINARY_EDIT = LANDED.replace("return argument * 41 + 7", "return argument * 41 + 8")

#: A REPLACEMENT WRITTEN ON TOP OF THE LANDING, which is the shape `--base-wins` must not touch.
#: It renames `alpha` in one indivisible hunk, so `--keep` has no selection and the verdict is
#: `REPLACEMENT` exactly as for `RIVAL_KIND_B` -- and it carries every distinctive line of the
#: landing, so the stale-copy control has NO complaint about it. The verdict is the same and the
#: clock's answer is the opposite, which is the only thing separating the flag from `git checkout`.
REPLACEMENT_ON_TOP_OF_THE_LANDING = LANDED.replace("def alpha():", "def beta():")

#: THE MIDDLE OF THE CLOCK'S THREE ANSWERS, and the one `--base-wins` must not take. It keeps ONE
#: of the landing's distinctive lines and rewords the rest under its own name, so it is a
#: REPLACEMENT by the hunk test and `predates_landing_carrying_some` by the clock: older than the
#: commit, but holding part of it, so it may be that commit edited rather than a draft that
#: preceded it. The test that uses it backdates its mtime, which is the other half of `PARTIAL`.
PARTIAL_CARRY_REPLACEMENT = (
    "def alpha():\n    return 1\n\n\n"
    "def my_own_helper(argument):\n"
    '    """this lane\'s own wording for the same thing"""\n'
    "    return argument * 41 + 7\n"
)

#: `k.py` exists for ONE leg: a copy that is stale by the clock AND still has a landable hunk. The
#: padding is load-bearing rather than decorative -- `isolate_hunks.group_opcodes` merges changes
#: within its context window, so without it the deletion of the landed helper and the addition of
#: the lane's own function group into a single hunk and the file grades `REPLACEMENT` again,
#: testing nothing. Six fillers put them in separate hunks, which is what gives `--keep` a
#: selection and this copy a door.
_FILLER = "".join("def filler_{}():\n    return {}\n\n\n".format(i, i) for i in range(6))
K_BASE = "def alpha():\n    return 1\n\n\n" + _FILLER + "def gamma():\n    return 3\n"
K_LANDED = ("def alpha():\n    return 1\n\n\n"
            "def freshly_landed_helper(argument):\n"
            '    """A distinctive line that appears exactly once in this file."""\n'
            "    return argument * 41 + 7\n\n\n" + _FILLER + "def gamma():\n    return 3\n")
#: Older than the landing (it has not one of the landing's lines) and it APPENDS its own work in a
#: hunk of its own. The clock refuses it; `isolate_hunks --keep` can still save the work.
K_STALE_BUT_LANDABLE = K_BASE + (
    "\n\ndef my_own_unlanded_function():\n"
    "    return 'work that only exists in this lane and nowhere else'\n")


# ------------------------------------------------- the API that MOVED, which is the r1 instance
#
# `SEAT_FINDING_THE_R1_COPYS_MISSING_PARTNER_IS_IN_A_SALVAGE_COMMIT_AND_HEAD_SUPERSEDED_IT_UNDER_
# NEW_NAMES_2026-09-08`, reduced to two modules and two commits. A lane drafted controls against
# `honest_point_estimate`; the landing that followed replaced that estimator with a different one
# under a different name, and renamed the controls to match. The lane's working copy survives,
# supplies names HEAD lacks, and is worth nothing: run it and every one of those names raises
# `AttributeError`. The old name still EXISTS in the first commit, which is the correction the
# finding itself is -- three documents read "absent from HEAD" as "exists nowhere" because they
# asked branches rather than `git log --all -S`.

DEP_BEFORE = (
    "def honest_point_estimate(book):\n"
    '    """the estimator the first design shipped"""\n'
    "    return sum(book) / len(book)\n"
)
DEP_AFTER = (
    "def three_way_estimate(book):\n"
    '    """the estimator that replaced it -- a different design, not a rename"""\n'
    "    return sorted(book)[len(book) // 2]\n"
)

#: The shared ancestor both sides keep. It matters that this EXISTS and that the landing MODIFIED
#: `d.py` rather than creating it: `distinctive_lines` is "what this commit ADDED", so on a file a
#: commit creates, the draft's own import line is evidence of the landing and rule 2 never fires.
#: A control file a landing creates outright is not the population either finding is about.
D_BASELINE = (
    "import dep\n\n\n"
    "def test_the_module_is_importable():\n"
    "    assert dep is not None\n"
)
#: The lane's stale working copy of the control file: written against the dead API.
DEAD_DRAFT = D_BASELINE + (
    "\n\ndef test_the_reported_maximum_is_biased_up_on_an_empty_book():\n"
    "    assert dep.honest_point_estimate([1, 2, 3]) == 2\n"
)
#: What HEAD carries for the same property, under the new name.
D_LANDED = D_BASELINE + (
    "\n\ndef test_the_three_way_estimate_recovers_a_target_that_is_really_there():\n"
    "    assert dep.three_way_estimate([1, 2, 3]) == 2\n"
)
#: The dangerous neighbour: a dead draft with ONE genuinely live name beside it. Overwriting this
#: destroys unlanded work, so the dead names must never license a write for the whole file.
DEAD_DRAFT_PLUS_LIVE = DEAD_DRAFT + (
    "\n\ndef test_a_control_that_runs_perfectly_well_today():\n"
    "    assert dep.three_way_estimate([1, 2, 3]) == 2\n"
)
#: THE FALSE POSITIVE DEADNESS CANNOT RULE OUT, appended to what HEAD landed: a lane writing the
#: control BEFORE the module it will grade. Every static and every dynamic reading of this is the
#: same as the dead draft's -- an attribute that is not there. What separates them is that the base
#: has no complaint about this copy, which is rule 2 and is why rule 2 survives the flag.
TEST_FIRST_APPEND = (
    "\n\ndef test_the_estimator_i_am_about_to_write():\n"
    "    assert dep.not_written_yet([1, 2, 3]) == 2\n"
)


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
    (root / "dep.py").write_text(DEP_BEFORE)
    (root / "d.py").write_text(D_BASELINE)
    (root / "k.py").write_text(K_BASE)
    _run(root, "add", "m.py", "notes.md", "dep.py", "d.py", "k.py")
    _run(root, "commit", "-qm", "base")
    (root / "m.py").write_text(LANDED)
    (root / "dep.py").write_text(DEP_AFTER)
    (root / "k.py").write_text(K_LANDED)
    # THE DRAFT'S NAMES ARE COMMITTED BY NOBODY, and that is the whole difference between this
    # class and the one `cut_of` already closed. `d.py` gains the three-way control here and never
    # held the `honest_point_estimate` one, so `git log -S` finds no deletion to attribute and the
    # lane's copy reads as holder work. Committing the draft first would make its names CUTS --
    # which the 2026-09-16 door already admits -- and the fixture would grade green with the
    # defect still in.
    (root / "d.py").write_text(D_LANDED)
    _run(root, "add", "m.py", "dep.py", "d.py", "k.py")
    _run(root, "commit", "-qm", "lane B lands a helper, and dep's API moves under it")
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
    (repo / "m.py").write_text(HOLDER_APPENDS)
    rc, text = rth.refresh(repo, ["m.py"], "kind-b", write=True)
    assert rc == 1 and rth.SUPPLIES_NEW in text
    assert "my_own_unlanded_function" in text, "the refusal did not name what it was protecting"
    assert (repo / "m.py").read_text() == HOLDER_APPENDS, "a refused path was written anyway"
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
    for content, state in ((RIVAL_KIND_A, rth.REFRESHABLE), (HOLDER_APPENDS, rth.SUPPLIES_NEW),
                           (RIVAL_KIND_B, rth.REPLACEMENT),
                           (ORDINARY_EDIT, rth.NOT_SUPERSEDED), (LANDED, rth.AT_HEAD)):
        (repo / "m.py").write_text(content)
        got = rth.judge_copy(repo, "m.py").state
        assert got == state, "{} was judged {}, not {}".format(state, got, state)
        states.add(got)
    states.add(rth.judge_copy(repo, "notes.md").state)
    states.add(rth.judge_copy(repo, "brand_new.py").state)
    (repo / "d.py").write_text(DEAD_DRAFT)
    states.add(rth.judge_copy(repo, "d.py").state)
    assert states == {rth.REFRESHABLE, rth.SUPPLIES_NEW, rth.REPLACEMENT, rth.SUPERSEDED_DEAD,
                      rth.NOT_SUPERSEDED, rth.AT_HEAD, rth.NO_READER, rth.NO_BASE}


# --------------------------------------- rule 1 asks NEVER BOUND, not merely ABSENT (2026-09-16)
#
# The defect, banked as THE_HOLDER_WORK_VERDICT_NAMED_A_FORBIDDEN_IMPORT_AS_WORK_TO_LAND: a name
# HEAD DELETED on purpose is not holder work, and reading it as holder work shut this door against
# exactly the copies the census sends here -- the census named the refresh, the refresh answered
# `refused_supplies_names_head_lacks`, and the only remaining route was the land-it door that puts
# the deletion back. Measured live on `tests/simulation/test_the_tariff_type_read_has_one_home.py`.

#: HEAD DELETED this helper on purpose -- a test that went red as designed, an import cut for a
#: measured outage. The copy still carrying it supplies a name HEAD lacks and is not holder work.
CUT_BY_HEAD = (
    "def alpha():\n    return 1\n\n\n"
    "def helper_head_deleted_on_purpose():\n    return 'the decision HEAD recorded'\n"
)


def _head_deletes_the_helper(repo: Path) -> None:
    """Bind the helper, then DELETE it in the landing HEAD now holds."""
    for text, message in ((CUT_BY_HEAD, "the helper is written"),
                          (LANDED, "the helper is deleted on purpose")):
        (repo / "m.py").write_text(text)
        _run(repo, "add", "m.py")
        _run(repo, "commit", "-qm", message)


def test_a_copy_whose_only_new_name_head_deleted_is_refreshable(repo: Path) -> None:
    """THE DOOR THE CENSUS NAMES MUST BE OPEN. This is the finding's own instance: the census sends
    a copy here precisely because its 'new' name is a re-creation of a deletion, and until this
    asked NEVER BOUND rather than ABSENT the tool refused it for being what it was sent for."""
    _head_deletes_the_helper(repo)
    (repo / "m.py").write_text(CUT_BY_HEAD)
    verdict = rth.judge_copy(repo, "m.py")
    assert verdict.state == rth.REFRESHABLE, (
        "the door the stale-copy census names for a cut is still shut: [{}] {}".format(
            verdict.state, verdict.reason))
    assert "CUT ON PURPOSE" in verdict.reason, (
        "the refresh is licensed by a deletion the reader cannot see, so the write is silent about "
        "the one fact that licenses it")


def test_a_copy_carrying_a_cut_AND_an_unlanded_name_is_still_refused(repo: Path) -> None:
    """THE DIRECTION THAT DESTROYS WORK, and the whole reason the widening is per name rather than
    per copy. This tool OVERWRITES BYTES: one genuinely new name beside the cut must still refuse,
    or the repair for losing a lane's work becomes the way it is lost."""
    _head_deletes_the_helper(repo)
    (repo / "m.py").write_text(CUT_BY_HEAD + "\n\ndef my_own_unlanded_function():\n    return 2\n")
    verdict = rth.judge_copy(repo, "m.py")
    # KEYED TO THE PROPERTY, NOT TO THE STATE STRING. This used to assert `SUPPLIES_NEW`, and the
    # copy it builds REPLACES `freshly_landed_helper`, so it is a REPLACEMENT on the 2026-09-17
    # split -- a strictly narrower refusal. Pinning the leg to the old string would have made it go
    # red for the code becoming more honest, which is backwards. What this leg is FOR is that the
    # unlanded name is never overwritten and is named on the way out; both states satisfy that and
    # `REFRESHABLE` is the one that must never appear.
    assert verdict.refused, (
        "a copy holding unlanded work was cleared for overwriting because a CUT sat beside it")
    assert verdict.gains == ("my_own_unlanded_function",), (
        "the refusal must name the unlanded work and not the cut: {}".format(verdict.gains))


# ------------------------------------------- the third and fourth states (2026-09-17)
#
# THE DEFECT, and it is one defect that two 2026-09-08 findings each saw half of. Rule 1 asked
# "does this copy supply a name the base lacks", and answered YES for three different copies that
# need three different answers: genuine unlanded work, a REPLACEMENT whose every hunk deletes
# landed work, and a DRAFT AGAINST A DEAD API that cannot run at all. Both doors were keyed to that
# one count, so they failed in the same direction on the same input -- `isolate_hunks` offered to
# land dead-API tests and `refresh_to_head` refused to discard them. The two findings BLOCKED lane
# `H_harness` for nine days, which is how `SITE4_ia_register_and_nav` and `H47_the_orientation_
# header_states_a_figure_it_computes` sat at level 0 with every control they name passing.
#
# Every test below names the way its own branch could be useless, because the permissive one of the
# four OVERWRITES A LANE'S BYTES and the restrictive ones are what stop it.


def test_a_draft_against_a_dead_api_is_refused_until_the_flag_is_typed(repo: Path) -> None:
    """THE DEFAULT MUST STAY SHUT. A lane writing the control BEFORE the module it grades produces
    a byte-identical file to this one -- the difference is intent and intent is not on disk. So
    deadness may inform a person and must never, by itself, license the write."""
    (repo / "d.py").write_text(DEAD_DRAFT)
    verdict = rth.judge_copy(repo, "d.py")
    assert verdict.state == rth.SUPERSEDED_DEAD, (
        "a draft against an API no committed tree defines was graded [{}]".format(verdict.state))
    rc, text = rth.refresh(repo, ["d.py"], "dead", write=True)
    assert rc == 1 and (repo / "d.py").read_text() == DEAD_DRAFT, (
        "the copy was overwritten without anyone typing --superseded")
    assert "--superseded" in text, "a refusal with no next move is where a bypass comes from"


def test_the_flag_actually_opens_the_door_and_heads_bytes_land_on_disk(repo: Path) -> None:
    """REACHABILITY. Every other leg here asserts a refusal, and a door that refuses even when the
    flag is typed passes all of them while repairing none of the copies it was built for -- which
    is exactly the state the r1 copy sat in: no `--content` route and no `refresh` route either."""
    (repo / "d.py").write_text(DEAD_DRAFT)
    rc, text = rth.refresh(repo, ["d.py"], "dead", write=True, superseded=True)
    assert rc == 0, text
    assert (repo / "d.py").read_text() == D_LANDED, (
        "the flag was typed and the copy was still not replaced by HEAD's bytes")
    found = _run(repo, "log", "--all", "--format=%H", "-S", "honest_point_estimate", "--",
                 "d.py").split()
    assert any(_run(repo, "show", "{}:d.py".format(sha)) == DEAD_DRAFT for sha in found), (
        "the discarded draft is not reachable by the recovery route this tool advertises")


def test_one_live_name_beside_the_dead_ones_shuts_the_door_even_with_the_flag(repo: Path) -> None:
    """THE DIRECTION THAT DESTROYS WORK. `--superseded` admits a copy whose names are ALL dead; a
    single name that runs is unlanded work, and a flag that waved the file through because most of
    it was dead would make the repair for losing a lane's work the way it is lost."""
    (repo / "d.py").write_text(DEAD_DRAFT_PLUS_LIVE)
    verdict = rth.judge_copy(repo, "d.py", superseded=True)
    assert verdict.state != rth.REFRESHABLE, (
        "a copy carrying a LIVE unlanded control was cleared for overwriting because dead drafts "
        "sat beside it: [{}]".format(verdict.state))
    assert "test_a_control_that_runs_perfectly_well_today" in verdict.gains, (
        "the refusal must name the live work it is protecting, not the dead drafts: {}".format(
            verdict.gains))


def test_the_flag_does_not_relax_the_base_must_supersede_it_rule(repo: Path) -> None:
    """RULES 2 AND 3 ARE UNTOUCHED, and without this leg `--superseded` is `git checkout` with a
    longer name. A draft against a dead API that the base has NO complaint about is an ordinary
    edit someone is mid-way through, and reverting it is the wall."""
    (repo / "d.py").write_text(D_LANDED + TEST_FIRST_APPEND)
    verdict = rth.judge_copy(repo, "d.py", superseded=True)
    assert verdict.state == rth.NOT_SUPERSEDED, (
        "the flag reverted a copy the stale-copy control has no complaint about, which is "
        "`git checkout <path>` wearing this tool's name: [{}]".format(verdict.state))


def test_the_missing_attribute_and_the_commit_that_did_bind_it_reach_the_reader(
        repo: Path) -> None:
    """THE SURFACE IS THE LICENCE, and the second half is the finding's own correction. Three
    documents called the r1 copy's missing partner non-existent because they asked branches; it was
    in a salvage commit all along and `git log --all -S` found it in one command. A reader deciding
    whether the module is worth reviving needs that commit named, and an exemption nobody can see
    is a hole."""
    (repo / "d.py").write_text(DEAD_DRAFT)
    verdict = rth.judge_copy(repo, "d.py")
    assert [(d.module, d.attr) for d in verdict.dead] == [("dep.py", "honest_point_estimate")], (
        "the verdict does not say WHICH attribute is missing from WHICH module: {}".format(
            verdict.dead))
    assert verdict.dead[0].elsewhere, (
        "the commit that DID bind the attribute was not looked up, so the reader is told the name "
        "is missing and not that it is recoverable -- which is the error the finding corrects")
    rendered = verdict.render()
    assert "honest_point_estimate" in rendered and "dep" in rendered, (
        "the dead names are not printed, so the one fact licensing the write is invisible")


def test_a_copy_whose_every_hunk_deletes_landed_work_is_not_called_holder_work(
        repo: Path) -> None:
    """THE VERDICT THAT COST MOST: it said LAND THIS, of a copy whose landing is a revert. The
    remedy it printed -- `isolate_hunks --keep N` -- has no legal selection here, because the
    addition and the deletion are ONE hunk. Naming the state is the repair; picking a side is a
    judgement neither door may make."""
    (repo / "m.py").write_text(RIVAL_KIND_B)
    verdict = rth.judge_copy(repo, "m.py")
    assert verdict.state == rth.REPLACEMENT, (
        "a copy with no landable hunk was graded [{}] and sent to a door that lands a "
        "revert".format(verdict.state))
    assert "freshly_landed_helper" in verdict.drops, (
        "the refusal must name the LANDED work the copy would delete: {}".format(verdict.drops))
    assert "isolate_hunks" not in verdict.reason, (
        "the replacement verdict still prints the `--keep` remedy, and there is no `--keep` "
        "selection here -- a remedy that cannot be performed is the pressure toward bypass")


def test_a_copy_that_appends_without_deleting_is_still_holder_work(repo: Path) -> None:
    """THE OTHER SIDE OF THE SPLIT, and the reason the clause is per HUNK and not per FILE. A
    file-level 'does it drop any landed name' test would swallow this one too and strand a lane's
    real work behind a refusal with no door -- refusing everything is not the safe direction when
    the alternative move is `git checkout`."""
    (repo / "m.py").write_text(HOLDER_APPENDS)
    verdict = rth.judge_copy(repo, "m.py")
    assert verdict.state == rth.SUPPLIES_NEW, (
        "genuine holder work was graded [{}], so the lane has no door at all".format(
            verdict.state))
    assert "isolate_hunks" in verdict.reason, "holder work must be sent to the land-it door"


def test_the_holder_work_verdict_names_a_hunk_the_landing_tool_agrees_with(repo: Path) -> None:
    """A CITED INDEX THAT THE TOOL DOES NOT AGREE WITH IS WORSE THAN NO INDEX. The verdict now
    prints which hunks `--keep` should take, and it earns that only by numbering them the way
    `isolate_hunks --survey` does -- so this asserts the selection it names actually reconstructs
    HEAD plus the unlanded work and nothing else.

    THIS LEG ASKS `reconstruct`, WHICH IS THE 0-BASED SIDE, and on its own it is the flattering
    half of the question -- it proved the cited indices agree with the internal API they came out
    of, which they did while the reader-facing ones were shifted by one for the function's whole
    life. Kept because it is still the check that the selection does not LOSE work; the numbering
    claim in the name is carried by
    `test_the_cited_hunks_are_selectable_by_the_tool_the_refusal_names` below, which types them at
    `--keep`. Feeding `landable` here needs the same `- 1` `--keep` applies, for the same reason."""
    from tools.isolate_hunks import group_opcodes, reconstruct
    from tools.stale_copy_refusal import landable_hunks

    (repo / "m.py").write_text(HOLDER_APPENDS)
    landable = landable_hunks(LANDED, HOLDER_APPENDS, "m.py")
    assert landable, "no hunk was called landable, so the cited remedy names nothing"
    assert all(str(gid) in rth.judge_copy(repo, "m.py").reason for gid in landable), (
        "the verdict cites a hunk selection the reader cannot find in `--survey`")
    base, work = LANDED.splitlines(keepends=True), HOLDER_APPENDS.splitlines(keepends=True)
    ops, groups = group_opcodes(base, work)
    built = "".join(reconstruct(base, work, ops, groups, {gid - 1 for gid in landable}))
    assert "freshly_landed_helper" in built and "my_own_unlanded_function" in built, (
        "the selection this verdict names does not build HEAD-plus-the-holder's-work, so the "
        "remedy sends a lane to a landing that loses something")


def test_the_cited_hunks_are_selectable_by_the_tool_the_refusal_names(
        repo: Path, tmp_path: Path) -> None:
    """THE INDEX IS TYPED AT `--keep`, WHICH IS THE ONLY SURFACE A READER HAS, and for the whole
    life of `landable_hunks` nothing asked it there. The sibling above fed the cited indices to
    `reconstruct` -- the 0-based internal the numbers came out of -- so it answered "do these agree
    with themselves" and passed while the refusal printed indices `--keep` rejects outright.

    The defect this names, measured on the real tree before the fix: `refresh_to_head` refused
    `simulation/premise_population.py` with *"land hunk(s) 0, 1"*, and
    `isolate_hunks --keep 0 --keep 1` answered *"REFUSED: hunk 0 does not exist (4 in this file)"*.
    A reader who dropped the impossible 0 and ran `--keep 1` alone would have landed ONE of the two
    hunks and believed they had both -- the silent half, and the worse one.

    So this runs `isolate_hunks.build` with exactly the digits the refusal prints. It reds if
    `landable_hunks` returns `gid` instead of `gid + 1`, and it reds the other way too: shift it by
    two and the selection stops reproducing the holder's work."""
    (repo / "m.py").write_text(HOLDER_APPENDS)
    verdict = rth.judge_copy(repo, "m.py")
    assert verdict.state == rth.SUPPLIES_NEW, verdict.state
    from tools.stale_copy_refusal import landable_hunks
    cited = landable_hunks(LANDED, HOLDER_APPENDS, "m.py")
    assert cited, "no hunk was called landable, so there is no cited index to type"

    # `isolate_hunks` reads the path from ITS OWN repo root, so the fixture has to be the one it
    # sees. Monkeypatching the module global is the seam -- reaching for the real tree here would
    # make the control's subject whatever the shared worktree happens to hold.
    import tools.isolate_hunks as iso
    out = tmp_path / "isolated.py"
    saved_repo, saved_head = iso._REPO, iso.head_lines
    try:
        iso._REPO = repo
        iso.head_lines = lambda path: LANDED.splitlines(keepends=True)
        rc = iso.build("m.py", [str(gid) for gid in cited], out)
    finally:
        iso._REPO, iso.head_lines = saved_repo, saved_head
    assert rc == 0, "the tool the refusal names REFUSED the selection the refusal printed"
    # AS CODE, NOT AS TEXT. The names below are `def`s in the fixture, and the isolated bytes also
    # carry the docstrings that NAME them -- so a raw `in` over the source would be satisfied by a
    # hunk that landed the prose describing the helper and not the helper, which is the same
    # flattering reading this whole test exists to close one level up.
    from tools.python_code_text import searchable
    built = searchable(out.read_text())
    assert "my_own_unlanded_function" in built, (
        "the cited selection, typed at `--keep`, did not take the holder's work -- the refusal "
        "names an index that silently lands less than it promises")
    assert "freshly_landed_helper" in built, (
        "the cited selection reverted landed work, which is the thing `--keep` exists to avoid")


# ------------------------------------------------------------------- `--base-wins`, and its edge
#
# THE STATE WITH NO EXIT. `REPLACEMENT` names a judgement and hands it to a person, which was the
# repair. But only ONE of the two answers a person can give was enactable: "the copy wins" is a
# landing, and "the base wins" is a discard that nothing legal here performed -- so a REPLACEMENT
# resolved for the base sat in the shared tree permanently, with the stale-copy door refusing every
# landing over it. `WORKER_RESULT_THE_THREE_CLEARABLE_REVERTS_ARE_GONE_AND_THE_TWO_LEFT_NEED_A_DOOR
# _THAT_ENACTS_THE_BASE_WINNING_2026-09-22` is two live files in that state.


def test_base_wins_refreshes_a_replacement_the_clock_says_predates_its_landing(repo: Path) -> None:
    """REACHABILITY FIRST, and stated against the DEFAULT in the same test. A flag that refuses
    every copy passes every refusal leg below while clearing none of the files it was built for,
    and asserting the default refusal beside it is what proves the flag is the thing that moved."""
    (repo / "m.py").write_text(RIVAL_KIND_B)
    assert rth.judge_copy(repo, "m.py").state == rth.REPLACEMENT, (
        "the fixture is not in the state the flag is about, so this proves nothing about it")
    rc, text = rth.refresh(repo, ["m.py"], "base-wins", write=True, base_wins=True)
    assert rc == 0, text
    assert (repo / "m.py").read_text() == LANDED, (
        "the REPLACEMENT was not discarded, so the state the finding calls unexitable still has "
        "no exit: {}".format(text))
    assert rth.PREDATES in text, "the verdict does not say which clock rule licensed the write"


def test_the_line_level_surface_this_branch_destroys_reaches_the_reader_and_the_probe(
        repo: Path) -> None:
    """`discarded` IS NOT DECORATION ON THIS BRANCH -- it is the input to `_probe`, and without it
    `verify_recoverable` takes its no-probe route and never RUNS the `git log --all -S` lookup the
    tool advertises. A preservation that is only claimed is the whole thing rule 3 exists to stop.
    Asserted on the field and not on the rendered text, because the supplied NAMES are printed
    beside it and would answer a text search for the same string -- the flattering reading."""
    (repo / "m.py").write_text(RIVAL_KIND_B)
    verdict = rth.judge_copy(repo, "m.py", base_wins=True)
    assert verdict.state == rth.REFRESHABLE
    assert any("my_own_unlanded_function" in line for line in verdict.discarded), (
        "the lines this branch is about to destroy were not collected: {}".format(
            verdict.discarded))
    assert rth._probe(verdict) is not None, (
        "there is no probe, so the advertised recovery search is skipped and the preservation is "
        "asserted rather than verified on the branch that destroys the most")


def test_base_wins_refuses_a_copy_that_carries_SOME_of_its_landing(repo: Path) -> None:
    """THE RULE SET IS NARROWER THAN 'the control has a complaint', and the gap is this copy.
    `PARTIAL` says it holds some of the landing's own lines, so it MAY have been written on top of
    it and edited -- the clock has not established it is the older draft, only that it is older
    than the commit. Widening `BASE_WINS_RULES` to any complaint at all discards a lane's edit to
    a landed file, and every other leg here stays green while it does.

    AND IT IS STILL TRUE OF CODE AFTER 2026-09-23, when `PARTIAL` was admitted for DATA. The licence
    is `refresh_to_head.base_wins_rules`, asked here BY PATH rather than read off the raw tuple, so
    a widening applied to the wrong suffix class reds this leg instead of sliding past it."""
    (repo / "m.py").write_text(PARTIAL_CARRY_REPLACEMENT)
    os.utime(repo / "m.py", (time.time() - 99_999, time.time() - 99_999))
    loss = judge(repo, "m.py", LANDED, PARTIAL_CARRY_REPLACEMENT)
    assert loss is not None and loss.rule not in rth.base_wins_rules("m.py"), (
        "the fixture is not in the PARTIAL state, so the narrowing is not exercised: {}".format(
            None if loss is None else loss.rule))
    verdict = rth.judge_copy(repo, "m.py", base_wins=True)
    assert verdict.state == rth.REPLACEMENT, (
        "a copy carrying part of its own landing was discarded under `--base-wins`, so the flag "
        "admits any complaint rather than the clock's own two: [{}]".format(verdict.state))


def test_base_wins_still_refuses_a_replacement_the_clock_has_no_complaint_about(
        repo: Path) -> None:
    """THE LEG THAT STOPS THIS BEING `git checkout <path>`. A REPLACEMENT written ON TOP of the
    landing is an ordinary rename someone is mid-way through: same verdict, opposite clock. If the
    flag keyed on the verdict alone it would discard a lane's live work and read as correct."""
    (repo / "m.py").write_text(REPLACEMENT_ON_TOP_OF_THE_LANDING)
    verdict = rth.judge_copy(repo, "m.py", base_wins=True)
    assert verdict.state == rth.REPLACEMENT, (
        "a copy the stale-copy control has NO complaint about was cleared for overwriting under "
        "`--base-wins`, so the flag is a revert button: [{}]".format(verdict.state))
    assert "no complaint" in verdict.reason, (
        "the refusal does not say WHY the flag did not reach it, so the next reader cannot tell "
        "a missing precondition from a tool that ignores its own flag")
    rc, _ = rth.refresh(repo, ["m.py"], "base-wins", write=True, base_wins=True)
    assert rc == 1 and (repo / "m.py").read_text() == REPLACEMENT_ON_TOP_OF_THE_LANDING, (
        "a refused path was written anyway")


def test_base_wins_does_not_reach_a_stale_copy_that_still_has_a_landable_hunk(
        repo: Path) -> None:
    """THE EXCLUSION THE FINDING'S OWN PROPOSAL DID NOT MAKE, and it is the difference between
    'no door applies' and 'I prefer the base'. This copy IS older than its landing -- the same
    clock evidence that licenses the leg above -- and `isolate_hunks --keep` can lift its work out
    without the revert. Admitting it would destroy recoverable work where a route existed, which
    is the harm the prohibition on `git checkout <path>` is for."""
    (repo / "k.py").write_text(K_STALE_BUT_LANDABLE)
    plain = rth.judge_copy(repo, "k.py")
    assert plain.state == rth.SUPPLIES_NEW and rth.landable_hunks(
        K_LANDED, K_STALE_BUT_LANDABLE, "k.py"), (
        "the fixture has no landable hunk, so the exclusion this test is about is not exercised")
    verdict = rth.judge_copy(repo, "k.py", base_wins=True)
    assert verdict.state == rth.SUPPLIES_NEW, (
        "`--base-wins` discarded a copy whose work a landing door could have saved: [{}]".format(
            verdict.state))
    assert "isolate_hunks" in verdict.reason, "the door that does apply was not named"
    assert (repo / "k.py").read_text() == K_STALE_BUT_LANDABLE


def test_the_bytes_a_base_wins_refresh_discards_come_back_by_the_advertised_search(
        repo: Path) -> None:
    """RULE 3 IS UNCHANGED, and it has to be asserted on THIS branch rather than inferred from the
    Kind-A one: the whole point of the state is that the copy supplies names, so it destroys MORE
    than a Kind-A refresh does and the preservation matters more, not less."""
    (repo / "m.py").write_text(RIVAL_KIND_B)
    rc, _ = rth.refresh(repo, ["m.py"], "base-wins", write=True, base_wins=True)
    assert rc == 0
    probe = "work that only exists in this lane and nowhere else"
    found = _run(repo, "log", "--all", "--format=%H", "-S", probe, "--", "m.py").split()
    assert found, "the discarded work is not reachable by the route the tool advertises"
    assert _run(repo, "show", "{}:m.py".format(found[0])) == RIVAL_KIND_B


def test_the_flag_is_off_by_default_everywhere_the_tool_is_called(repo: Path) -> None:
    """A RELAXATION THAT DEFAULTS ON IS NOT A RELAXATION, it is the new behaviour. `judge_copy`
    and `refresh` are both called by other modules (`background.origin_reconcile` among them) with
    no opinion about this flag, and each must still get the refusal."""
    (repo / "m.py").write_text(RIVAL_KIND_B)
    assert rth.judge_copy(repo, "m.py").state == rth.REPLACEMENT
    rc, text = rth.refresh(repo, ["m.py"], "base-wins", write=True)
    assert rc == 1 and rth.REPLACEMENT in text
    assert (repo / "m.py").read_text() == RIVAL_KIND_B
    assert "--base-wins" not in text, (
        "the default refusal advertises the flag, so every reader of an ordinary REPLACEMENT is "
        "pointed at the one door that must stay a deliberate choice")


# ------------------------------------------- `--base-wins` on a DATA path, where it never reached
#
# THE FLAG WAS SHUT FOR THE WHOLE POPULATION IT WAS BUILT FOR, in two independent ways, and every
# leg above stayed green while it was: they are all `.py`. Measured 2026-09-23 on the three feed
# inputs of the capabilities publisher (`svt_drift_belief_grade.json` and two
# `ladder_churn_factors*.json`), which is the live instance.
#
#   1. `judge_copy`'s DATA_SUFFIXES branch returned on `supplies` several screens ABOVE the
#      `base_wins` consultation, so a `.json` path never reached the flag at all. And a JSON leaf
#      name carries its own VALUE, so a regenerated artefact -- same schema, every figure moved --
#      "supplies" every leaf it holds by construction. A stale regeneration is precisely what
#      `--base-wins` exists to discard and was the one copy that could never get to it.
#
#   2. The Python branch gates on `judge`, whose first line is
#      `Path(path).suffix not in READABLE -> None`, and READABLE is `.html/.js/.py`. `judge` is
#      STRUCTURALLY UNABLE to have a complaint about a `.json`, so gating a data path on it agrees
#      with every answer by returning None to all of them. Simply routing data paths to the same
#      gate would have restored an equally unreachable branch. The module docstring says the flag
#      "is gated on the CLOCK (`base_wins_rules`)", and `clock_judge` is the oracle that name
#      refers to -- it reads all three live files as predates_landing_by_clock /
#      predates_landing_carrying_some where `judge` reads all three as no complaint.


def _data_repo_with_a_stale_regeneration(repo: Path, carries_some: bool) -> Path:
    """A committed JSON report, then a landing that moves every value, then a working copy that
    PREDATES the landing -- the live shape. `carries_some` keeps one of the landing's own lines so
    the clock reads PARTIAL rather than CLOCK, which is the other side of the partition."""
    (repo / "report.json").write_text('{\n  "alpha": 1,\n  "beta": 2\n}\n')
    _run(repo, "add", "report.json")
    _run(repo, "commit", "-qm", "the report is first published")
    (repo / "report.json").write_text('{\n  "alpha": 10,\n  "beta": 20,\n  "gamma": 30\n}\n')
    _run(repo, "add", "report.json")
    _run(repo, "commit", "-qm", "the report is regenerated and every figure moves")
    # The rival: an OLDER run's output. Same schema, different values -- so it "supplies" leaves by
    # value alone. mtime is forced behind the landing, which is what the clock reads.
    stale = ('{\n  "alpha": 10,\n  "beta": 7\n}\n' if carries_some
             else '{\n  "alpha": 3,\n  "beta": 7\n}\n')
    (repo / "report.json").write_text(stale)
    old = time.time() - 86400
    os.utime(repo / "report.json", (old, old))
    return repo


def test_base_wins_reaches_a_DATA_replacement_the_clock_says_predates_its_landing(
        repo: Path) -> None:
    """REACHABILITY FIRST, and against the DEFAULT in the same test, exactly as the `.py` leg does.

    This is the leg that did not exist, and its absence is why the flag could be shut for every
    `.json` in the tree while the whole file above passed. Without `--base-wins` the copy must
    still be refused -- otherwise this proves the door is open, not that the flag opened it."""
    _data_repo_with_a_stale_regeneration(repo, carries_some=False)
    assert rth.judge_copy(repo, "report.json").state == rth.SUPPLIES_NEW, (
        "the fixture is not in the state the flag is about, so this proves nothing about it")
    verdict = rth.judge_copy(repo, "report.json", base_wins=True)
    assert verdict.state == rth.REFRESHABLE, (
        "`--base-wins` did not reach a data path the clock says predates its own landing, so the "
        "flag is still shut for the population it was built for: [{}] {}".format(
            verdict.state, verdict.reason))
    rc, text = rth.refresh(repo, ["report.json"], "base-wins-data", write=True, base_wins=True)
    assert rc == 0, text
    assert '"gamma": 30' in (repo / "report.json").read_text(), (
        "the stale regeneration was not discarded, so the base still cannot win on a data "
        "artefact: {}".format(text))
    assert rth.CLOCK in text, "the verdict does not say which clock rule licensed the write"


def test_base_wins_on_a_DATA_path_ADMITS_a_copy_that_carries_SOME_of_its_landing(
        repo: Path) -> None:
    """THE QUESTION THIS FILE LEFT OPEN ON 2026-09-23, NOW MEASURED AND ANSWERED THE OTHER WAY.

    The version of this test it replaces asserted the opposite and said why: `BASE_WINS_RULES` was
    deliberately NOT widened to PARTIAL for data, because whether "carries some of the landing's
    distinctive lines" means anything about a document where a line is a VALUE and not a statement
    was a real question, and answering it silently inside a door that DISCARDS bytes is how a
    lane's work gets destroyed. It was filed rather than assumed. It has now been measured -- see
    `refresh_to_head.base_wins_rules` for the numbers and the pre-registration that fixed them
    before the answer was known -- and the carry is coincidence: on the two live files this was
    commissioned for, 57 of 57 and 1032 of 1060 carried lines appear verbatim in a sibling report
    that cannot have been derived from the landing. The prediction is kept beside the result rather
    than the test quietly flipped.

    THE CLOCK GUARD IS WHAT THIS DOES NOT RELAX, and `test_base_wins_on_a_DATA_path_still_refuses_
    a_copy_the_clock_has_NO_complaint_about` is the leg that says so."""
    _data_repo_with_a_stale_regeneration(repo, carries_some=True)
    head_text = _run(repo, "show", "HEAD:report.json")
    work_text = (repo / "report.json").read_text()
    clock = scr.clock_judge(repo, "report.json", head_text, work_text)
    assert clock is not None and clock.rule == scr.PARTIAL, (
        "the fixture is not in the PARTIAL state, so the widening this test is about is not "
        "exercised at all: {}".format(None if clock is None else clock.rule))
    assert scr.PARTIAL not in rth.base_wins_rules("m.py"), (
        "PARTIAL was admitted for CODE too, where a distinctive line is a statement and a share is "
        "evidence of derivation -- the measurement licenses this for data and for nothing else")
    verdict = rth.judge_copy(repo, "report.json", base_wins=True)
    assert verdict.state == rth.REFRESHABLE, (
        "a data copy the clock says predates its own landing, whose entire carry is the figures "
        "that did not move, is still refused -- so the two `ladder_churn_factors` copies this was "
        "commissioned for cannot be cleared: [{}] {}".format(verdict.state, verdict.reason))
    assert scr.PARTIAL in verdict.reason, (
        "the verdict does not name the clock rule that licensed the write, so a reader cannot tell "
        "which of the three admitted it: {}".format(verdict.reason))


def test_base_wins_on_a_DATA_path_still_refuses_a_copy_the_clock_has_NO_complaint_about(
        repo: Path) -> None:
    """THE LEG THAT STOPS THE WIDENING ABOVE BEING `git checkout <path>` FOR EVERY `.json`.

    Admitting PARTIAL removes one vouch; it must not remove the clock. This copy is a regeneration
    written AFTER its landing -- an ordinary edit someone is mid-way through, same leaf arithmetic,
    opposite clock -- and if the flag keyed on the suffix rather than on `taken_before` it would
    discard live work and read as correct."""
    _data_repo_with_a_stale_regeneration(repo, carries_some=True)
    now = time.time()
    os.utime(repo / "report.json", (now, now))  # NEWER than the landing: the clock says nothing
    head_text = _run(repo, "show", "HEAD:report.json")
    work_text = (repo / "report.json").read_text()
    assert scr.clock_judge(repo, "report.json", head_text, work_text) is None, (
        "the clock still complains about a copy newer than its landing, so this fixture cannot "
        "show that the clock is what the flag rests on")
    verdict = rth.judge_copy(repo, "report.json", base_wins=True)
    assert verdict.state == rth.SUPPLIES_NEW, (
        "a data copy the clock has NO complaint about was discarded under `--base-wins`, so "
        "widening the rule set turned the flag into a revert button for any stale-looking JSON: "
        "[{}]".format(verdict.state))
    assert "no complaint" in verdict.reason, (
        "the refusal does not say WHY the flag did not reach it, so the operator cannot tell a "
        "missing precondition from a tool ignoring its own flag: {}".format(verdict.reason))


def test_no_caller_in_this_module_asks_the_oracle_that_is_BLIND_to_the_suffix_it_holds(
        repo: Path) -> None:
    """THE ORDERING INVARIANT NOTHING PINNED, and it is the second defect of 2026-09-23 wearing a
    later date.

    `judge` opens with `Path(path).suffix not in READABLE -> None`, so it is STRUCTURALLY UNABLE to
    have a complaint about a `.json` -- and a field unable to answer a question agrees with every
    answer to it. `judge_copy`'s two remaining `judge` calls are safe for data today ONLY because
    the `DATA_SUFFIXES` branch returns several screens above them. That is an ordering fact about
    one function, not a guard: move the branch, or add a suffix to `DATA_SUFFIXES` without moving
    it, and the blindness comes back silently -- exactly as it arrived the first time.

    A SPY AND NOT AN AST READ, because the claim is about which calls RUN and a source scan would
    grade a call in dead code the same as one on the live path. And the spy is PROVEN ABLE TO FIRE
    on the `.py` fixture in this same test, because a spy that records nothing satisfies a
    zero-calls assertion perfectly while measuring nothing at all."""
    seen: list[str] = []
    real = rth.judge

    def spy(root, path, head_text, new_text, parent="HEAD"):
        seen.append(path)
        return real(root, path, head_text, new_text, parent=parent)

    _data_repo_with_a_stale_regeneration(repo, carries_some=True)
    (repo / "m.py").write_text(RIVAL_KIND_B)
    rth.judge = spy
    try:
        # Every `.json` state that reaches a decision: the flag off, the flag on, and the
        # leaf-subset branch with nothing supplied. One state per door the data branch has.
        rth.judge_copy(repo, "report.json")
        rth.judge_copy(repo, "report.json", base_wins=True)
        data_calls = list(seen)
        rth.judge_copy(repo, "m.py", base_wins=True)
        code_calls = seen[len(data_calls):]
    finally:
        rth.judge = real
    assert code_calls, (
        "the spy recorded NOTHING even on a `.py` copy, so it is not on the path it claims to "
        "watch and the zero-calls assertion below would pass however blind the tool got")
    assert not data_calls, (
        "`judge_copy` asked `judge` about {}, and `judge` returns None for every suffix outside "
        "READABLE ({}) -- so that gate agrees with every answer and whatever it guards is "
        "unreachable. Route the data path to `clock_judge`.".format(
            data_calls, "/".join(scr.READABLE)))


def test_base_wins_on_a_DATA_path_is_not_gated_on_an_oracle_that_cannot_ANSWER(repo: Path) -> None:
    """THE SECOND DEFECT, named directly, because fixing only the first restores an equally dead
    branch and every other leg here would still pass.

    `judge` returns None for a `.json` by construction -- `.json` is not in READABLE. A field
    structurally unable to answer a question agrees with every answer to it, so a `--base-wins`
    gated on `judge` refuses every data path no matter what the clock says. This asserts the two
    oracles actually DISAGREE on the fixture, which is what makes the choice between them
    load-bearing rather than cosmetic."""
    _data_repo_with_a_stale_regeneration(repo, carries_some=False)
    head_text = _run(repo, "show", "HEAD:report.json")
    work_text = (repo / "report.json").read_text()
    assert scr.judge(repo, "report.json", head_text, work_text) is None, (
        "`judge` now has a complaint about a data path; if READABLE has grown to include `.json` "
        "this test's premise is gone and the gate choice should be revisited, not this assertion "
        "relaxed")
    clock = scr.clock_judge(repo, "report.json", head_text, work_text)
    assert clock is not None and clock.rule in rth.BASE_WINS_RULES, (
        "the clock does not complain about the fixture either, so this file proves nothing about "
        "which oracle the gate should ask: {}".format(clock))
