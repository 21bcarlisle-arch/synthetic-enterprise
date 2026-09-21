"""A `.json` blocker could be proven lossless by NO class, and one of those is fatal to all of them.

THE DEFECT, measured on the live shared tree 2026-09-21 with `.publish_gate_state.json` recording
twelve `commit_did_not_land` failures and `episode_clean_publishes: 0`. Eleven paths held the
fast-forward. `tools/refresh_to_head.judge_copy` -- the losslessness judgement
`origin_reconcile.advance_shared_tree` asks of every tracked blocker the two hash sweeps could not
take -- answered SIX of them:

    "this control has no reader for .json files, so it CANNOT establish that the copy has
     nothing to lose. An unavailable check is a failed check."

Fail-closed and correct, and ALSO permanently unresolvable: no run of any producer, no landing by
any lane and no passage of time can ever turn that answer into a verdict, because it is a statement
about the READER and not about the file. Under the all-or-nothing rule in `advance_shared_tree` --
which is a safety property, not tidiness -- one permanently unresolvable path refuses every other
class beside it. Five of the six were rescued only because `generated_output_verdicts` (the fifth
class, added 2026-09-18 for exactly this shape one door over) happened to know their producer.
The sixth, `docs/design/self_clearing_alarm_dispositions.json`, is authored and no producer knows
it, so it held the tree on a question nobody had asked.

THE READER IS SCOPED TO THIS DOOR AND THE COMMIT GUARD IS UNCHANGED, which is the whole reason
`DATA_SUFFIXES` is a second constant rather than three characters added to `READABLE`.
`stale_copy_refusal.violations()` and `::judge()` gate on `READABLE` and run on EVERY commit in a
tree three lanes write, where a daemon rewriting a `.json` ledger between two commits is ordinary
operation -- widening that set would red every lane for a carrier's normal churn, which is a defect
this project has already banked once under another name. The advance's door has the opposite
problem: it is only ever asked of a path already HOLDING a fast-forward.

THE VALUE IS IN THE NAME, AND THAT IS THE FAIL-OPEN THIS CLASS WOULD OTHERWISE HAVE SHIPPED. Keyed
on the key-path alone -- the obvious reading, and the one `_PAGE_ANCHORS` warns about one class over
-- a copy that REWROTE every value while keeping the shape supplies no name the base lacks, reads as
strictly superseded, and is overwritten. That destroys an edit while looking checked, and it is not
hypothetical: the live blocker's own diff is two rewritten `why`/`loader` VALUES at keys both
documents carry. `test_a_copy_that_only_rewrote_a_value_is_refused` is that leg and it fails against
a key-only reader.

WHAT EACH CONTROL WOULD CATCH, and every one names its own defect:

  * `test_a_superseded_json_copy_is_refreshed_and_the_bytes_become_the_bases` -- REACHABILITY, and
    it comes first. Every other leg here asserts a refusal, and a reader that refuses EVERYTHING
    passes all of them while unwedging nothing. This is the branch the advance actually needs.
  * `test_the_json_verdict_partition_is_reachable_every_way_on_one_tree_state` -- one control over
    the WHOLE partition, per CLAUDE.md. A guard stuck on any single verdict fails this even when
    each single-branch leg above it is green.
  * `test_a_copy_that_only_rewrote_a_value_is_refused` -- the fail-open above. Same keys, same
    shape, different content.
  * `test_a_copy_supplying_a_key_the_base_lacks_is_refused` -- the holder-work property that must
    NOT have moved. This is the live tree's own case and displacing a lane's unlanded row is what
    this class is not.
  * `test_a_formatting_only_difference_is_not_licensed_as_a_refresh` -- the OTHER direction of the
    same honesty: two documents with identical leaves are not a supersession, and calling one
    refreshable would make this `git checkout <path>` with a nicer name, which is forbidden here.
  * `test_an_unparseable_json_blob_is_a_finding_and_never_a_skip` -- fail-closed on the new reader.
    A truncated ledger must not read as "no leaves, therefore superseded", which is the emptiness
    that wears a pass's colour.
  * `test_the_commit_guards_readable_set_did_not_widen` -- the blast radius. This is the leg that
    fails if a later hand "tidies" `DATA_SUFFIXES` into `READABLE`, and nothing else here would
    notice: every verdict leg above would stay green while every lane in the tree started refusing
    commits over a daemon's ordinary ledger write.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools import refresh_to_head as rth
from tools import stale_copy_refusal as scr


def _run(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)
    return out.stdout


#: The shape of the live blocker: a register of rows, each row a dict of prose fields.
BASE_DOC = {
    "dispositions": {
        ".alpha.json": {"verdict": "benign", "why": "a counter that only grows"},
        ".beta.json": {"verdict": "real", "why": "an episode start a writer can move"},
    },
    "_provenance": {"graded_at": "2026-09-21"},
}


def _write(root: Path, doc: dict) -> None:
    (root / "reg.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo whose HEAD carries a row the working copy will be made to lack.

    The subject is git blobs read through `blob_at`, so a fake dict-of-strings stand-in would be
    `a fake more permissive than its subject`.
    """
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    stale = json.loads(json.dumps(BASE_DOC))
    _write(root, stale)
    _run(root, "add", "reg.json")
    _run(root, "commit", "-qm", "base")
    # HEAD gains a third row. A working copy still holding the two-row document is then a rival
    # copy the base strictly supersedes -- the class the advance needs cleared.
    landed = json.loads(json.dumps(BASE_DOC))
    landed["dispositions"][".gamma.json"] = {"verdict": "benign", "why": "landed by another lane"}
    _write(root, landed)
    _run(root, "add", "reg.json")
    _run(root, "commit", "-qm", "another lane dispositions a third carrier")
    return root


def _stale_copy(root: Path) -> None:
    """Put the pre-landing two-row document back on disk, which is what a stale copy IS."""
    _write(root, BASE_DOC)


# ------------------------------------------------------ the permissive branch must be REACHABLE


def test_a_superseded_json_copy_is_refreshed_and_the_bytes_become_the_bases(repo: Path) -> None:
    """REACHABILITY FIRST. A reader that answers every `.json` with a refusal passes every other
    leg in this file and clears not one of the six blockers it was built for."""
    _stale_copy(repo)
    verdict = rth.judge_copy(repo, "reg.json")
    assert verdict.state == rth.REFRESHABLE, (
        "a copy supplying no leaf HEAD lacks and dropping one HEAD has was not judged "
        "refreshable, so the permanently-unresolvable class is still permanently unresolvable: "
        "{}".format(verdict.reason))
    rc, text = rth.refresh(repo, ["reg.json"], "json-rival", write=True)
    assert rc == 0, text
    assert json.loads((repo / "reg.json").read_text()) == json.loads(
        _run(repo, "show", "HEAD:reg.json")), (
        "the working copy was not replaced by HEAD's bytes, so the advance would refuse on this "
        "path again having been told it was cleared")


def test_the_json_verdict_partition_is_reachable_every_way_on_one_tree_state(repo: Path) -> None:
    """ONE CONTROL OVER THE WHOLE PARTITION. A guard that refuses everything -- or one stuck on any
    single verdict -- passes each single-branch leg in this file and fails here. Per CLAUDE.md:
    assert the rare branch CAN be taken before asserting what it does."""
    seen = {}

    _stale_copy(repo)
    seen[rth.judge_copy(repo, "reg.json").state] = "drops a row, supplies nothing"

    supplies = json.loads(_run(repo, "show", "HEAD:reg.json"))
    supplies["dispositions"][".delta.json"] = {"verdict": "benign", "why": "this lane's own work"}
    _write(repo, supplies)
    seen[rth.judge_copy(repo, "reg.json").state] = "supplies a row HEAD lacks"

    rewritten = json.loads(_run(repo, "show", "HEAD:reg.json"))
    rewritten["dispositions"][".alpha.json"]["why"] = "re-graded here and nowhere else"
    _write(repo, rewritten)
    seen[rth.judge_copy(repo, "reg.json").state] = "same keys, one value rewritten"

    reformatted = json.loads(_run(repo, "show", "HEAD:reg.json"))
    (repo / "reg.json").write_text(json.dumps(reformatted, indent=8, sort_keys=True) + "\n\n")
    seen[rth.judge_copy(repo, "reg.json").state] = "identical leaves, different whitespace"

    assert rth.REFRESHABLE in seen and rth.SUPPLIES_NEW in seen and rth.NOT_SUPERSEDED in seen, (
        "the JSON judgement did not reach all three of refreshable / supplies-new / "
        "not-superseded on one tree state, so it is not partitioning anything -- it reached only "
        "{}".format(seen))


# --------------------------------------------------- the refusals, each naming what it protects


def test_a_copy_that_only_rewrote_a_value_is_refused(repo: Path) -> None:
    """THE FAIL-OPEN A KEY-ONLY READER SHIPS. Every key matches; only content differs. Read on key
    paths alone this is a strict subset and the refresh overwrites an edit while looking checked --
    and it is the live blocker's own diff, which rewrote two `why`/`loader` values in place."""
    rewritten = json.loads(_run(repo, "show", "HEAD:reg.json"))
    rewritten["dispositions"][".beta.json"]["why"] = "a different grading of the same carrier"
    _write(repo, rewritten)
    verdict = rth.judge_copy(repo, "reg.json")
    assert verdict.state == rth.SUPPLIES_NEW, (
        "a copy whose keys all match HEAD but whose VALUE was edited was judged {} -- refreshing "
        "it destroys the edit".format(verdict.state))
    rc, _ = rth.refresh(repo, ["reg.json"], "value-rewrite", write=True)
    assert rc == 1
    assert json.loads((repo / "reg.json").read_text()) == rewritten, (
        "the edited bytes were overwritten despite the refusal")


def test_a_stale_copy_carrying_a_rewritten_value_does_not_lose_the_rewrite(repo: Path) -> None:
    """THE LIVE SHAPE, AND THE ONLY LEG HERE THAT PROVES DATA LOSS RATHER THAN A WRONG LABEL.

    The shared tree's own blocker is BOTH stale (it lacks rows origin landed) AND edited (it
    rewrites two `why`/`loader` values in place). Read on key paths alone those two facts combine
    into the worst answer available: the missing rows make `drops` non-empty, the rewritten values
    supply nothing, and the verdict is REFRESHABLE -- so the refresh writes the base over an
    unlanded edit and reports success. Measured against a key-only reader on this fixture: verdict
    `refreshable`, rc 0, the edit gone. `test_a_copy_that_only_rewrote_a_value_is_refused` does NOT
    catch that mutant destructively -- without a drop beside it the mutant merely mislabels and
    still refuses -- so this leg is not a louder copy of that one.
    """
    stale_and_edited = json.loads(json.dumps(BASE_DOC))
    stale_and_edited["dispositions"][".alpha.json"]["why"] = "MY UNLANDED RE-GRADING"
    _write(repo, stale_and_edited)
    verdict = rth.judge_copy(repo, "reg.json")
    assert verdict.state == rth.SUPPLIES_NEW, (
        "a copy that is stale AND carries an unlanded edit was graded {} -- the refresh would "
        "write the base over the edit and report success".format(verdict.state))
    rc, _ = rth.refresh(repo, ["reg.json"], "stale-and-edited", write=True)
    assert rc == 1
    assert json.loads((repo / "reg.json").read_text())["dispositions"][".alpha.json"]["why"] == (
        "MY UNLANDED RE-GRADING"), "the unlanded edit was destroyed by the refresh"


def test_a_copy_supplying_a_key_the_base_lacks_is_refused(repo: Path) -> None:
    """THE SAFETY PROPERTY THAT MUST NOT HAVE MOVED, and the live tree's own case: the shared
    copy of the dispositions register carries a whole row that reaches no ref anywhere. Displacing
    a lane's unlanded work is what this class is not."""
    holder = json.loads(_run(repo, "show", "HEAD:reg.json"))
    holder["dispositions"][".epsilon.json"] = {"verdict": "real", "why": "unlanded, on no ref"}
    _write(repo, holder)
    verdict = rth.judge_copy(repo, "reg.json")
    assert verdict.state == rth.SUPPLIES_NEW
    assert ".epsilon.json" in " ".join(verdict.gains), (
        "the refusal did not name the leaf it is protecting, so the holder cannot tell whether it "
        "was right: {}".format(verdict.reason))


def test_a_formatting_only_difference_is_not_licensed_as_a_refresh(repo: Path) -> None:
    """THE OTHER DIRECTION OF THE SAME HONESTY. Identical leaves are not a supersession, and
    writing HEAD over an ordinary reformat is `git checkout <path>` with a nicer name."""
    same = json.loads(_run(repo, "show", "HEAD:reg.json"))
    (repo / "reg.json").write_text(json.dumps(same, indent=4, sort_keys=False))
    verdict = rth.judge_copy(repo, "reg.json")
    assert verdict.state == rth.NOT_SUPERSEDED, (
        "two documents with equal leaves were graded {}, so a whitespace change licensed a "
        "write".format(verdict.state))


def test_an_unparseable_json_blob_is_a_finding_and_never_a_skip(repo: Path) -> None:
    """FAIL-CLOSED ON THE NEW READER. A truncated ledger must not read as 'no leaves, therefore
    nothing to lose' -- an emptiness that wears a pass's colour is this register's named killer."""
    (repo / "reg.json").write_text('{"dispositions": {"a": ')
    verdict = rth.judge_copy(repo, "reg.json")
    assert verdict.state == rth.UNPARSEABLE, (
        "a truncated JSON blob was graded {} rather than reported -- an unavailable check that "
        "does not say so is the whole defect class".format(verdict.state))


def test_the_commit_guards_readable_set_did_not_widen() -> None:
    """THE BLAST RADIUS, and the leg nothing else here would fail. `violations()` and `judge()`
    gate on `READABLE` and run on every commit in a tree three lanes write. A later hand folding
    `DATA_SUFFIXES` into `READABLE` -- which reads like tidying -- turns a daemon's ordinary
    `.json` ledger rewrite into a refusal for every lane, while every verdict leg above stays
    green. Keyed to the PROPERTY (the commit guard cannot read data files) and not to today's
    tuple contents."""
    assert ".json" not in scr.READABLE, (
        "the commit-time stale-copy guard now reads .json, so every lane's commit is judged on a "
        "carrier its own daemons rewrite between commits")
    assert ".json" in scr.DATA_SUFFIXES
    assert scr.judge(Path("."), "x.json", "{}", '{"a": 1}') is None, (
        "the commit guard formed an opinion about a .json path")
    assert scr.symbols('{"a": 1}', "x.json") is not None, (
        "the advance's reader cannot read .json, so the blocker class is unresolvable again")
