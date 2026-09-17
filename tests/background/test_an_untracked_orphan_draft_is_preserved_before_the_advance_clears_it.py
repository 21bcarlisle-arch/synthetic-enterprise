"""An untracked draft of a document origin ADDS could be cleared by nothing, and it wedged the tree.

THE DEFECT, measured on the live shared tree 2026-09-17. `git rev-list --count HEAD..origin/main`
was 5 and `origin..HEAD` was 0 -- nothing here was unpushed, the checkout was simply stuck -- while
`.publish_gate_state.json` recorded `last_clean_publish: null` and a wedge 7.68 days old. Two paths
held it. One was a lane's tracked holder work, correctly refused. The other was
`docs/staging/SEAT_RESULT_THE_PUBLISHED_EIGHTEEN_POOLS_TWO_VALUE_ARMS...`: 8,906 untracked bytes a
seat wrote here at 22:36, against the 9,846 bytes the SAME seat landed to origin at 22:49 in
`471dfd417` from an isolated worktree, having edited the document in the act of landing it.

NO CLASS COULD TAKE IT AND THAT WAS STRUCTURAL, not an oversight about one file:

  * the untracked twin sweep needs hash equality, and the landed copy had gained a paragraph;
  * `stale_copy_verdicts` needs HEAD's blob as a base, and HEAD has none for an untracked path --
    asked anyway it answers `NO_BASE`, or here, "no reader for .md files";
  * `advance_shared_tree` therefore SUBTRACTED untracked non-twins out of its candidate set, so the
    path did not even reach a refusal that named it as unresolvable.

And this is what landing a staging document ordinarily does -- `surgical_land --content` does not
write the shared working tree, by design -- so the class refills once per landing and had no exit.

WHAT EACH CONTROL WOULD CATCH, and every one names its own defect:

  * `test_an_untracked_orphan_is_cleared_and_the_advance_then_succeeds` -- the repair, and the
    reachability leg for the whole new branch.
  * `test_the_orphans_bytes_are_on_a_ref_before_the_file_is_gone` -- the ORDER. Preservation before
    removal is the only thing that makes this class safe, and a repair that cleared first would
    pass every other leg here.
  * `test_a_preservation_that_fails_removes_nothing_and_does_not_advance` -- fail-closed on the new
    door: bytes on no branch are never destroyed on a preservation that did not verify.
  * `test_a_tracked_holder_copy_is_still_refused_beside_a_clearable_orphan` -- the safety property
    that must NOT have moved. Displacing holder work is what this class is not.
  * `test_the_preserved_bytes_come_back_through_the_advertised_route` -- against real git in a real
    throwaway repository: `git show` AND the `git log --all -S` lookup the reason advertises.
  * `test_an_untracked_twin_is_not_routed_through_the_preservation` -- two mechanisms for one act is
    how they drift; the twin sweep keeps its own path.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path

import pytest

from background import origin_reconcile as orc


def _completed(returncode: int, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["git"], returncode=returncode, stdout="",
                                       stderr=stderr)


def _untracked(path: str) -> dict:
    return {"path": path, "kind": orc.FF_UNTRACKED}


def _modified(path: str) -> dict:
    return {"path": path, "kind": orc.FF_MODIFIED}


class _Advance:
    """The real `advance_shared_tree` with the destructive edges injected and told apart.

    `removed`, `restored` and `preserved` are three separate lists on purpose: the whole of this
    repair is that an orphan is PRESERVED and then removed, and a harness that collected the acts
    into one list could not tell that from a removal with a preservation that never ran.
    """

    def __init__(self, ff_results, blocking, twins=(), tracked=(), orphans=None,
                 preserve_failure="", stale=None):
        self.ff_results = list(ff_results)
        self.blocking = blocking
        self.twins = twins
        self.tracked = tracked
        self.orphans = orphans
        self.stale = stale
        self.preserve_failure = preserve_failure
        self.removed: list[str] = []
        self.restored: list[str] = []
        self.preserved: list[list[str]] = []
        #: Which paths the orphan verdicts were ASKED about, apart from which ones they approved.
        #: A fixture that only records the answer cannot see a caller that widened the QUESTION:
        #: asked about a tracked holder path, this fixture's hard-coded list says `False` and the
        #: advance refuses for the right reason by luck. Measured 2026-09-17 -- the mutation that
        #: offers every blocking path to this class did not red a single leg until this list.
        self.offered: list[str] = []
        #: What was on disk, in call order: the preservation must be able to see a file the
        #: removal has not taken yet, and only an ordered log can show that.
        self.order: list[str] = []

    def _ff(self):
        return self.ff_results.pop(0)

    def _remove(self, path):
        self.order.append("remove:" + path)
        self.removed.append(path)

    def _preserve(self, paths):
        self.order.append("preserve:" + ",".join(paths))
        self.preserved.append(list(paths))
        if self.preserve_failure:
            return None, self.preserve_failure
        return "0" * 40, ""

    def _orphan_verdicts(self, _project, paths):
        self.offered.extend(paths)
        if self.orphans is None:
            return None
        return {p: (p in self.orphans, "fixture verdict") for p in paths}

    def run(self):
        return orc.advance_shared_tree(
            blockers_fn=lambda _project: self.blocking,
            twins_fn=lambda _project, _blocking: list(self.twins),
            tracked_twins_fn=lambda _project, _blocking: list(self.tracked),
            stale_fn=lambda _project, paths: {
                p: (p in (self.stale or ()), "fixture verdict") for p in paths},
            orphans_fn=self._orphan_verdicts,
            preserver=self._preserve,
            ff_fn=self._ff,
            remover=self._remove,
            restorer=lambda p: self.restored.append(p) or None,
            locker=contextlib.nullcontext,
            # LEVEL WITH ORIGIN, so the subject of every test here stays the ORPHAN logic. The real
            # `commits_ahead` reads the repository the suite runs in, which is routinely ahead.
            ahead_fn=lambda _project: 0,
        )


_ORPHAN = "docs/staging/SEAT_RESULT_A_DOCUMENT_ORIGIN_ALSO_ADDS_2026-09-17.md"


def test_an_untracked_orphan_is_cleared_and_the_advance_then_succeeds():
    """THE REPAIR, and the reachability control over the whole new branch.

    Before it, an untracked path origin adds whose bytes were not origin's was subtracted out of
    the candidate set and could be resolved by nothing, so the tree stayed behind indefinitely.

    MUTATION: drop `set(orphans)` from the `resolvable` union and the path falls into `held`, so
    `advanced` is False and the first assertion reds.
    """
    adv = _Advance(ff_results=[_completed(1, "untracked working tree files would be overwritten"),
                               _completed(0)],
                   blocking=[_untracked(_ORPHAN)], orphans=[_ORPHAN]).run()

    assert adv["advanced"] is True, \
        "the orphan draft's bytes were preserved on a ref, so clearing it lost nothing and the " \
        "fast-forward git had refused should have gone through"
    assert adv["cleared"] == [_ORPHAN], \
        "the advance must report exactly which paths it cleared -- a reader recovering one needs " \
        "its name and the ref it went to"
    assert orc.ORPHAN_PRESERVED_PREFIX in adv["reason"], \
        "the reason must name the ref the bytes went to; these bytes are on no branch and this " \
        "sentence is the only route back to them"


def test_the_orphans_bytes_are_on_a_ref_before_the_file_is_gone():
    """THE ORDER IS THE SAFETY PROPERTY. Preserve, then remove -- never the other way.

    A repair that removed first and preserved after would pass every other leg in this file and
    would destroy the bytes on any failure in between. `hash-object` on a file that is no longer
    there cannot be distinguished, downstream, from a preservation that simply did not run.

    MUTATION: move the `if orphan_set:` preservation block below the clearing loop and this reds
    on the ordering assertion while `advanced` stays True.
    """
    adv = _Advance(ff_results=[_completed(1), _completed(0)],
                   blocking=[_untracked(_ORPHAN)], orphans=[_ORPHAN])
    adv.run()

    assert adv.order == ["preserve:" + _ORPHAN, "remove:" + _ORPHAN], \
        "the bytes must reach the ref BEFORE the file leaves the disk: {}".format(adv.order)


def test_a_preservation_that_fails_removes_nothing_and_does_not_advance():
    """FAIL-CLOSED ON THE NEW DOOR. Bytes on no branch are never destroyed on an unverified save.

    This is the leg that makes the class honest. Every other resolvable class here rests on a proof
    that the bytes are already safe; this one rests on an act, and an act that did not happen must
    refuse rather than proceed as though it had.

    MUTATION: ignore the `failure` returned by `_preserve` and the advance clears the file anyway,
    so `removed` is non-empty and this reds.
    """
    adv = _Advance(ff_results=[_completed(1), _completed(0)],
                   blocking=[_untracked(_ORPHAN)], orphans=[_ORPHAN],
                   preserve_failure="the ref could not be moved")
    out = adv.run()

    assert adv.removed == [], \
        "the preservation failed, so the only copy of those bytes was still the file on disk and " \
        "it must not have been touched"
    assert out["advanced"] is False
    assert "the ref could not be moved" in out["reason"], \
        "the refusal must carry the preservation's own reason -- a caller told only that the " \
        "advance failed cannot tell an unverified save from a dirty tree"


def test_a_tracked_holder_copy_is_still_refused_beside_a_clearable_orphan():
    """THE SAFETY PROPERTY THAT MUST NOT HAVE MOVED: holder work is landed, never displaced.

    This is the live 2026-09-17 shape exactly -- one clearable orphan and one tracked working copy
    supplying names origin does not have. The new class must take the first and leave the second,
    and the all-or-nothing rule must then refuse the whole advance rather than delete a file for no
    fast-forward.

    MUTATION: widen `untracked_only` to every blocking path (drop the `- {FF_MODIFIED paths}` term)
    and the holder path is OFFERED to this class, which the third assertion reds on.

    AND THE FIRST TWO ASSERTIONS DO NOT CATCH THAT, which is why the third exists. Measured, not
    argued: with `untracked_only` widened, this file was still 9/9 green. The fixture's verdict
    function answers `False` for any path not in its hard-coded orphan list, so it happened to give
    the right answer to a question the caller should never have asked -- a catch-all fixture
    answering a widened predicate, and the refusal then arrives for the right reason by luck. What
    is keyed to the property is which paths REACHED the class, so that is what is asserted.
    """
    holder = "tests/tools/test_fold_noise_floor_family.py"
    adv = _Advance(ff_results=[_completed(1), _completed(0)],
                   blocking=[_untracked(_ORPHAN), _modified(holder)], orphans=[_ORPHAN])
    out = adv.run()

    assert adv.removed == [] and adv.preserved == [], \
        "one blocker was unresolvable, so clearing the other would have deleted a file and still " \
        "not advanced -- the named worst case"
    assert out["advanced"] is False
    assert holder in out["reason"], \
        "the refusal must name the path that held it; naming only a count is what cost three " \
        "separate rediscoveries"
    assert holder not in adv.offered, \
        "a TRACKED path must never be offered to the orphan class at all -- that class's whole " \
        "safety argument is that the path has no HEAD blob, and holder work does"


def test_an_untracked_twin_is_not_routed_through_the_preservation():
    """TWO MECHANISMS FOR ONE ACT IS HOW THEY DRIFT. A twin keeps the twin sweep's path.

    A byte-identical untracked file is already on origin, so preserving it would write a ref nobody
    needs and would make the orphan ref's population -- "bytes that exist nowhere else" -- untrue of
    its own contents, which is the one thing that ref is read for.

    MUTATION: drop `- set(resolvable)` from the orphan candidate expression and the twin is offered
    to the orphan verdicts and preserved, so `preserved` is non-empty and this reds.
    """
    twin = "docs/staging/SEAT_RESULT_A_TWIN_2026-09-17.md"
    adv = _Advance(ff_results=[_completed(1), _completed(0)],
                   blocking=[_untracked(twin)], twins=[twin], orphans=[twin])
    out = adv.run()

    assert out["advanced"] is True
    assert adv.preserved == [], \
        "the twin's bytes are already on origin, so the preservation ref must not have been asked " \
        "to carry them"
    assert adv.removed == [twin]


def test_an_unread_orphan_verdict_clears_nothing():
    """`None` IS NOT `{}`. "I could not look" must not read as "nothing is resolvable" NOR as a pass.

    MUTATION: treat a `None` verdict map as `{}` and the advance proceeds to refuse on the path for
    the wrong reason -- a state nobody read, reported as a state that was.
    """
    adv = _Advance(ff_results=[_completed(1), _completed(0)],
                   blocking=[_untracked(_ORPHAN)], orphans=None)
    out = adv.run()

    assert out["advanced"] is False and adv.removed == []
    assert "not established" in out["reason"].lower(), \
        "an unread comparison must say so: {}".format(out["reason"])


# ----------------------------------------------------------------- against real git, not a stub

@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A throwaway repository with one commit, so the preservation has a real HEAD to hang from.

    REAL GIT, because everything this fixture is for -- `read-tree`, a throwaway `GIT_INDEX_FILE`,
    `commit-tree`, and the `git log --all -S` lookup the recovery route advertises -- is git's
    behaviour and not this module's. A stub would prove the calls were made and nothing about
    whether the bytes come back, which is the only question that matters here.
    """
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=work, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=work, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=work, check=True)
    (work / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "seed.txt"], cwd=work, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "seed"], cwd=work, check=True)
    return work


def test_the_preserved_bytes_come_back_through_the_advertised_route(repo: Path):
    """The preservation's promise, RUN: `git show` returns the bytes and `-S` finds the commit.

    `verify_recoverable` makes both claims and this is where they are tested against real git for
    an UNTRACKED path -- the one shape `refresh_to_head.preserve` refuses outright, because it
    requires a HEAD entry the path does not have.

    MUTATION: replace the `update-ref` with any no-op and the commit is unreachable, so `rev-parse`
    on the ref fails and this reds. That is the load-bearing line: an object nobody references is
    collected, and the bytes go with it.

    DROPPING `-p HEAD` IS AN EQUIVALENCE HERE, AND IT IS RECORDED RATHER THAN ASSUMED AWAY. It was
    the mutation this docstring first claimed, and it did not fire: a parentless commit diffs
    against the empty tree, so every one of its files counts as added and `git log -S` finds it
    just the same. The parent buys a READABLE `git show` for whoever recovers the file -- a diff of
    the orphan alone rather than of the whole tree -- which is a property this control does not
    grade and should not pretend to.
    """
    path = "draft.md"
    unique = "a sentence that exists in exactly one place on this disk\n"
    (repo / path).write_text("shared preamble\n" + unique, encoding="utf-8")

    commit, failure = orc.preserve_untracked_orphans(repo, [path], "test-slug")
    assert failure == "", failure
    assert commit

    ref = subprocess.run(["git", "rev-parse", orc.ORPHAN_PRESERVED_PREFIX + "test-slug"],
                         cwd=repo, capture_output=True, text=True, check=True)
    assert ref.stdout.strip() == commit, \
        "the commit must be REACHABLE from the ref -- an unreferenced commit is collected and the " \
        "bytes go with it"

    shown = subprocess.run(["git", "show", "{}:{}".format(commit, path)],
                           cwd=repo, capture_output=True, text=True, check=True)
    assert shown.stdout == "shared preamble\n" + unique

    found = subprocess.run(["git", "log", "--all", "--format=%H", "-S", unique.rstrip("\n"),
                            "--", path], cwd=repo, capture_output=True, text=True, check=True)
    assert commit in found.stdout, \
        "the advertised `git log --all -S` route must reach the commit; one that does not is a " \
        "preservation in name only"


def test_the_working_index_is_not_touched_by_the_preservation(repo: Path):
    """The holder's own staged work is not this mechanism's to move.

    The preservation builds its tree through a throwaway `GIT_INDEX_FILE`. If it used the real one,
    a lane with staged work would find that work re-staged, unstaged or mixed with an orphan draft
    it never touched -- and the damage would be invisible until their next commit swept it.

    MUTATION: drop the `GIT_INDEX_FILE` env from `read-tree`/`update-index` and the orphan appears
    in the real index beside the holder's file, so this reds.
    """
    (repo / "held.txt").write_text("a lane's staged work\n", encoding="utf-8")
    subprocess.run(["git", "add", "held.txt"], cwd=repo, check=True)
    (repo / "draft.md").write_text("an orphan draft\n", encoding="utf-8")

    commit, failure = orc.preserve_untracked_orphans(repo, ["draft.md"], "test-slug")
    assert failure == "" and commit

    staged = subprocess.run(["git", "diff", "--cached", "--name-only"],
                            cwd=repo, capture_output=True, text=True, check=True)
    assert staged.stdout.split() == ["held.txt"], \
        "only the lane's own staged path may be in the real index: {!r}".format(staged.stdout)


def test_a_path_that_cannot_be_read_is_never_reported_as_preserved(repo: Path):
    """FAIL-CLOSED at the read. A missing file must refuse, not preserve an empty blob.

    An orphan that vanished between the survey and the write is the ordinary shape on a tree three
    lanes land in. Writing a zero-byte blob and calling it preserved would report a recovery route
    that returns nothing, which is strictly worse than refusing.

    MUTATION: remove all three gates together -- the `hash-object` return code, the `update-index`
    return code, and the `verify_recoverable` read-back loop -- and a commit is returned for bytes
    that were never read, so this reds.

    NO SINGLE-SITE MUTATION DEFEATS IT, AND THAT IS A MEASUREMENT, NOT A HOPE. Disabling the
    `hash-object` check alone leaves `update-index` refusing an empty blob id; disabling both
    leaves the read-back raising `OSError` on a file that is not there. Three independent gates
    close on this one path. It is worth stating which, because "the mutation did not fire" here is
    an EQUIVALENCE at each single site and would read as a dead control to the next reader.
    """
    commit, failure = orc.preserve_untracked_orphans(repo, ["never_written.md"], "test-slug")

    assert commit is None, "nothing may be reported preserved when the bytes could not be read"
    assert "never_written.md" in failure, \
        "the failure must name the path that could not be preserved: {!r}".format(failure)
