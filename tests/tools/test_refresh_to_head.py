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
    _run(root, "add", "m.py", "notes.md", "dep.py", "d.py")
    _run(root, "commit", "-qm", "base")
    (root / "m.py").write_text(LANDED)
    (root / "dep.py").write_text(DEP_AFTER)
    # THE DRAFT'S NAMES ARE COMMITTED BY NOBODY, and that is the whole difference between this
    # class and the one `cut_of` already closed. `d.py` gains the three-way control here and never
    # held the `honest_point_estimate` one, so `git log -S` finds no deletion to attribute and the
    # lane's copy reads as holder work. Committing the draft first would make its names CUTS --
    # which the 2026-09-16 door already admits -- and the fixture would grade green with the
    # defect still in.
    (root / "d.py").write_text(D_LANDED)
    _run(root, "add", "m.py", "dep.py", "d.py")
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
    HEAD plus the unlanded work and nothing else."""
    from tools.isolate_hunks import group_opcodes, reconstruct
    from tools.stale_copy_refusal import landable_hunks

    (repo / "m.py").write_text(HOLDER_APPENDS)
    landable = landable_hunks(LANDED, HOLDER_APPENDS, "m.py")
    assert landable, "no hunk was called landable, so the cited remedy names nothing"
    assert all(str(gid) in rth.judge_copy(repo, "m.py").reason for gid in landable), (
        "the verdict cites a hunk selection the reader cannot find in `--survey`")
    base, work = LANDED.splitlines(keepends=True), HOLDER_APPENDS.splitlines(keepends=True)
    ops, groups = group_opcodes(base, work)
    built = "".join(reconstruct(base, work, ops, groups, set(landable)))
    assert "freshly_landed_helper" in built and "my_own_unlanded_function" in built, (
        "the selection this verdict names does not build HEAD-plus-the-holder's-work, so the "
        "remedy sends a lane to a landing that loses something")
