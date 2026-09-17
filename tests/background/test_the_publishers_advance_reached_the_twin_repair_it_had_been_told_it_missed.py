"""THE PUBLISHER'S ADVANCE HAND-ROLLED THE FAST-FORWARD, SO ONE REPAIR REACHED TWO CALLERS OF THREE.

`_refused_advance_cause` has said so in its own docstring since it landed, about the function
sitting twelve lines below it:

    "this module has already paid for the copy-instead-of-call shape once, at this very function:
     the ahead-count was reused and the advance was hand-rolled, so when the twin-clearing repair
     landed in `advance_shared_tree` it reached the reconciler's two legs and not this one."

THE REPAIR IT MISSED. A `git merge --ff-only` refuses on an UNTRACKED local file whose path the
incoming commit also adds -- even when the local bytes are identical to the ones origin is about
to write there. Measured on this tree 2026-09-04: **13 of 14 blocking paths were files about to be
replaced by themselves**, and every one of them was a staging note origin already held.
`origin_reconcile.advance_shared_tree` removes exactly those and asks git again;
`_advance_to_origin_or_say_why` ran its own merge and refused.

WHAT THAT COST, and it is not the reconciler's cost. The reconciler retries every five minutes. The
publisher gets ONE attempt at the end of a 672s cycle, and its refusal throws that whole cycle away
at the door -- so the same blocking twin that costs the reconciler a cadence costs the publisher a
simulation, a gate and a page nobody sees.

WHAT IS ASSERTED HERE. That the publisher's advance now reaches the twin repair, and what it is
and is not willing to clear on the way. Real git throughout: the property under test is git's own
`--ff-only` refusal and the hash equality that answers it, and a stub asserting against a stub
would be a tautology in both directions.

AND THAT SECOND CLAUSE CHANGED ON 2026-09-17, so it is stated here rather than left to be
discovered in a diff. It used to read *"and that reaching it did not widen what the publisher is
willing to delete"*, with a leg requiring the fork to stay OPEN over any untracked file whose bytes
were not origin's. That leg pinned the 7.68-day wedge: the copy origin adds is never the copy on
disk, because landing a staging document edits it. An untracked draft of a document origin also
adds is now cleared -- after its bytes reach a ref and the recovery route has been run -- and
`test_an_untracked_draft_origin_also_adds_survives_on_a_ref_and_the_fork_closes` carries the
correction beside the claim it replaced. Tracked holder work is unchanged and still refuses.

SEPARATE FROM THE SIBLING THAT GRADES THE HELPER.
`test_the_advance_refused_on_files_it_was_about_to_write_back_unchanged.py` grades
`advance_shared_tree`'s own decision. Nothing there is reachable from the publish path, and a
helper's control is exactly what a hand-rolled second copy passes while carrying none of it -- that
is the whole shape this file exists to catch, so the subject here is the SEAM and not the helper.
"""

from __future__ import annotations

import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest

from background import origin_reconcile as orc
from background import process_run_complete as prc


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=120)


def _identify(repo: Path) -> None:
    _git(repo, "config", "user.email", "seat@example.invalid")
    _git(repo, "config", "user.name", "seat")


NOTE = "docs/staging/SEAT_FINDING_SOMETHING_2026-09-05.md"
NOTE_BYTES = "a finding, written twice in two trees\n"


@pytest.fixture
def behind_with_an_incoming_note(tmp_path):
    """A clone one commit behind an origin whose incoming commit ADDS `NOTE`.

    The local tree does not have that path at all yet, so each test below decides what to put
    there -- nothing, the identical bytes, or different ones. That choice is the whole partition.
    """
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", str(origin))

    local = tmp_path / "local"
    _git(tmp_path, "clone", str(origin), str(local))
    _identify(local)
    (local / "seed.txt").write_text("seed\n")
    _git(local, "add", "seed.txt")
    _git(local, "commit", "-m", "seed")
    _git(local, "push", "origin", "HEAD:main")

    other = tmp_path / "other"
    _git(tmp_path, "clone", str(origin), str(other))
    _identify(other)
    (other / NOTE).parent.mkdir(parents=True, exist_ok=True)
    (other / NOTE).write_text(NOTE_BYTES)
    _git(other, "add", NOTE)
    _git(other, "commit", "-m", "the note origin holds")
    _git(other, "push", "origin", "HEAD:main")

    return local, origin


@pytest.fixture
def unlocked(monkeypatch):
    """The advance takes the SHARED tree lock, which belongs to the real project directory and is
    contended by a live daemon; waiting on it here would grade the daemon's schedule.

    The lock itself is asserted structurally by
    `test_the_advance_writes_the_shared_tree_under_the_tree_lock` in the sibling suite, so removing
    it from the code still fails a control.
    """
    @contextmanager
    def _no_lock():
        yield

    monkeypatch.setattr(prc, "tree_lock", _no_lock)


def _write_untracked_note(local: Path, text: str) -> Path:
    path = local / NOTE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _origin_head(origin_bare: Path) -> str:
    """Read the BARE repo rather than the clone's tracking ref, which is only as fresh as the last
    fetch -- reading that would make the precondition and the verdict agree by construction."""
    return _git(origin_bare, "rev-parse", "main").stdout.strip()


# ── the precondition, before either verdict is graded ────────────────────────────────────────

def test_the_twin_really_does_refuse_a_plain_fast_forward(behind_with_an_incoming_note):
    """WITHOUT THIS THE WHOLE FILE IS UNFALSIFIABLE. Every control below turns on a byte-identical
    untracked twin blocking a fast-forward; if git happily advanced over one, the "advance"
    assertion would pass on a tree that was never blocked and would prove nothing about the repair.

    So git is asked directly, with no publisher and no helper in the way.
    """
    local, _origin = behind_with_an_incoming_note
    _write_untracked_note(local, NOTE_BYTES)
    _git(local, "fetch", "origin", "main")

    refused = _git(local, "merge", "--ff-only", "origin/main")

    assert refused.returncode != 0, \
        "an untracked file at a path the incoming commit adds must block the fast-forward, or " \
        "there is no defect here to repair"
    assert NOTE in (refused.stderr + refused.stdout)


# ── the repair reaching the publisher ────────────────────────────────────────────────────────

def test_a_byte_identical_twin_no_longer_costs_the_publisher_a_whole_cycle(
        behind_with_an_incoming_note, unlocked):
    """THE DEFECT. The publisher's advance ran its own merge, took git's refusal, and dropped a
    completed 672s cycle over a file whose bytes origin was about to write to that exact path.

    MUTATION: hand-roll the merge again -- replace the `advance_shared_tree` call with a bare
    `_run(["git", "merge", "--ff-only", "origin/main"], ...)` -- and this reds, which is the state
    the code was in before this commit.
    """
    local, origin = behind_with_an_incoming_note
    _write_untracked_note(local, NOTE_BYTES)

    result = prc._advance_to_origin_or_say_why(local)

    assert result["advanced"] is True, result["reason"]
    assert _head(local) == _origin_head(origin), \
        "the tree must actually be level, not merely claim it"
    assert (local / NOTE).read_text() == NOTE_BYTES, \
        "the twin comes back TRACKED with identical content -- a removal that lost bytes would " \
        "be this path deleting a lane's work, which is the one thing it may never do"


def test_a_clean_tree_still_advances_and_deletes_nothing(behind_with_an_incoming_note, unlocked):
    """THE NULL FOR THE LEG ABOVE. A tree with no twin at all must still advance, so the assertion
    there cannot be satisfied by an advance that only ever fires when something was removed.

    MUTATION: make the helper's first fast-forward unreachable (always go through the removal leg)
    and this reds -- there is nothing to remove, so nothing would advance.
    """
    local, origin = behind_with_an_incoming_note

    result = prc._advance_to_origin_or_say_why(local)

    assert result["advanced"] is True, result["reason"]
    assert _head(local) == _origin_head(origin)


# ── and reaching it did not widen what the publisher will delete ─────────────────────────────

def test_an_untracked_draft_origin_also_adds_survives_on_a_ref_and_the_fork_closes(
        behind_with_an_incoming_note, unlocked):
    """THE SAFETY NULL, REWRITTEN ON 2026-09-17, AND WHAT IT USED TO SAY IS KEPT HERE BESIDE IT.

    IT SAID: *"A local file that is NOT what origin holds is somebody's unlanded work: it must
    survive, and the fork must stay open"* -- and asserted `advanced is False` with the draft still
    on disk. That was right about the FIRST half and wrong about the second, and the second half is
    what it actually pinned.

    WHAT IT COST. `surgical_land --content` does not write the shared working tree, and a staging
    document is routinely EDITED in the act of landing it, so the copy origin adds is never the
    copy on disk here -- the twin sweep cannot match it and this leg required the fork to stay
    open. Measured on the live shared tree 2026-09-17: one such draft, 8,906 bytes against origin's
    9,846 at the same path, held a checkout five commits behind while `.publish_gate_state.json`
    carried `last_clean_publish: null` and a wedge 7.68 days old, and every daemon on the box ran
    superseded code. The class refills once per landing, so there was no exit.

    WHAT SURVIVES OF THE OLD PROPERTY, WHICH IS THE PART THAT MATTERED. The bytes are not
    destroyed. They reach `refs/preserved/origin-reconcile-orphan/<slug>` and the advertised
    recovery route is RUN before the file is removed -- both legs asserted below, against real git.
    And the path is not emptied: what stands there afterwards is origin's copy of the same
    document, which is why this is not "deleting a lane's work to buy a fast-forward" but
    superseding a draft by the landed version of itself.

    WHAT IS NOT LICENSED BY THIS, and has its own leg below: a TRACKED path a lane is holding
    dirty. That work exists in no other form and the lane is mid-turn on it, so it still refuses
    everything -- see `test_a_tracked_dirty_path_blocks_the_advance_and_clears_no_untracked_twin`.

    MUTATION: drop `set(orphans)` from `advance_shared_tree`'s `resolvable` union and the fork
    stays open, so the first assertion reds.
    """
    local, origin = behind_with_an_incoming_note
    mine = "MINE, and origin has never seen these bytes\n"
    _write_untracked_note(local, mine)
    _git(local, "fetch", "origin", "main")
    slug = orc.refresh_slug(local)

    result = prc._advance_to_origin_or_say_why(local)

    assert result["advanced"] is True, result["reason"]
    assert _head(local) == _origin_head(origin), \
        "the fork must actually close -- a checkout behind origin runs superseded code in every " \
        "daemon on the box, which is the cost this leg used to require"
    assert (local / NOTE).read_text() == NOTE_BYTES, \
        "the path is not emptied: origin's copy of the same document stands there afterwards"

    ref = orc.ORPHAN_PRESERVED_PREFIX + slug
    stored = _git(local, "show", "{}:{}".format(ref, NOTE))
    assert stored.returncode == 0 and stored.stdout == mine, \
        "the draft's own bytes must be readable from the preservation ref: {}".format(
            stored.stderr)
    found = _git(local, "log", "--all", "--format=%H", "-S", mine.rstrip("\n"), "--", NOTE)
    assert found.stdout.strip(), \
        "the `git log --all -S` route the refusal advertises must reach the preserved commit; one " \
        "that does not is a preservation in name only"


def test_an_untracked_file_origin_does_not_touch_is_never_preserved_or_removed(
        behind_with_an_incoming_note, unlocked):
    """THE NULL FOR THE LEG ABOVE, and the boundary of what it licenses.

    The class is "an untracked draft of a document origin ADDS at the same path". A file origin has
    no copy of is not in it, is not blocking anything, and must be left exactly where it is -- an
    advance that swept the untracked set generally would pass the leg above and quietly clear every
    lane's scratch file on the box.

    MUTATION, AND IT TAKES BOTH GATES: hand `untracked_orphan_verdicts` the whole untracked set
    rather than the blocking intersection, AND drop its own refusal of a path `origin/main` holds
    nothing at. Then the scratch file is preserved and unlinked for no advance and this reds.

    WIDENING THE CANDIDATE SET ALONE IS AN EQUIVALENCE, measured rather than assumed: the verdict
    function asks `origin/main` for the path's bytes and refuses when there are none, so the
    scratch file is offered and declined. Two independent gates hold this boundary, and saying so
    is the difference between a control that looks dead to the next reader and one that is not.
    """
    local, origin = behind_with_an_incoming_note
    _write_untracked_note(local, NOTE_BYTES)
    scratch = local / "docs" / "staging" / "SEAT_SCRATCH_NOBODY_ELSE_HAS_2026-09-17.md"
    scratch.write_text("a draft origin has never heard of\n")

    result = prc._advance_to_origin_or_say_why(local)

    assert result["advanced"] is True, result["reason"]
    assert scratch.read_text() == "a draft origin has never heard of\n", \
        "a file origin does not touch is not this mechanism's business at all"
    assert _head(local) == _origin_head(origin)


def test_a_tracked_dirty_path_blocks_the_advance_and_clears_no_untracked_twin(
        behind_with_an_incoming_note, unlocked, tmp_path):
    """ALL-OR-NOTHING, ACROSS THE SEAM. A single `FF_MODIFIED` path means no fast-forward is
    possible however many twins are cleared, so clearing them would be a deletion bought for no
    advance -- the one shape in which this could actually cost someone something.

    The helper holds that property; what is asserted here is that the publisher's call INHERITS it
    rather than passing arguments that defeat it.

    MUTATION: pass the helper a `twins_fn` or `blockers_fn` that ignores the modified path and this
    reds -- the twin disappears while the tree stays exactly as behind as it was.
    """
    local, origin = behind_with_an_incoming_note
    # A tracked file the incoming commit also touches, edited here: `FF_MODIFIED`.
    _git(local, "fetch", "origin", "main")
    (local / "seed.txt").write_text("seed\nanother lane was here\n")
    _write_untracked_note(local, NOTE_BYTES)
    # ...and make origin's next commit touch `seed.txt`, so the modification really does collide.
    other = tmp_path / "other2"
    _git(tmp_path, "clone", str(tmp_path / "origin.git"), str(other))
    _identify(other)
    (other / "seed.txt").write_text("seed\nand origin moved it too\n")
    _git(other, "add", "seed.txt")
    _git(other, "commit", "-m", "origin touches seed")
    _git(other, "push", "origin", "HEAD:main")
    before_head = _head(local)

    result = prc._advance_to_origin_or_say_why(local)

    assert result["advanced"] is False
    assert (local / NOTE).exists(), \
        "nothing may be removed when removing it could not have produced an advance"
    assert _head(local) == before_head


# ── the refusal a reader acts on ─────────────────────────────────────────────────────────────

def test_the_refusal_still_carries_the_verdict_the_clause_and_gits_own_words(
        behind_with_an_incoming_note, unlocked, tmp_path):
    """ROUTING THE ACT THROUGH THE HELPER MUST NOT COST THE SENTENCE. Only two of
    `advance_shared_tree`'s refusal branches quote git, and the branch a dirty publish tree takes
    is not one of them -- so a refusal assembled purely from the helper's reason would drop the
    ground truth its own verdict is derived from and become unfalsifiable.

    MUTATION: build the reason from `adv["reason"]` alone and the last assertion reds; drop
    `_refused_advance_cause` and the first two do.
    """
    local, _origin = behind_with_an_incoming_note
    _git(local, "fetch", "origin", "main")
    (local / "seed.txt").write_text("seed\nanother lane was here\n")
    other = tmp_path / "other2"
    _git(tmp_path, "clone", str(tmp_path / "origin.git"), str(other))
    _identify(other)
    (other / "seed.txt").write_text("seed\nand origin moved it too\n")
    _git(other, "add", "seed.txt")
    _git(other, "commit", "-m", "origin touches seed")
    _git(other, "push", "origin", "HEAD:main")

    reason = prc._advance_to_origin_or_say_why(local)["reason"]

    assert "seed.txt" in reason, "the clause names every blocking path, where git names only one"
    assert orc.FF_MODIFIED in reason, "the KIND is what decides who clears it"
    assert "overwritten" in reason, \
        "git's own words are the ground truth the clause is derived from and may not be replaced " \
        "by it -- the helper's reason does not carry them on this branch"
