"""An item naming a pre-registration was handed out after that prereg's graded result had landed.

THE DEFECT, 2026-09-28: `grade-the-balance-rule-two-state-diff-against-the-cefd2c04a-baseline` was
drawn at 04:27; `7dc8f150d` had landed `SEAT_RESULT_THE_TWO_STATE_DIFF_RERUN_UNDER_THE_BALANCE_AT_
CLOSE_RULE_2026-09-28.md` at 02:57. The item named only the prereg, which is the file that does not
change when the grading is done, so no draw-time check could see it.

KEYED TO THE PROPERTY: a same-stem `SEAT_RESULT_` on origin/main, any date, any staging room. The
fixture below is a throwaway repo, never the live tree.

MUTATIONS (each must fire):
  (a) drop `result_note` from `doorbell` -- `test_THE_DOORBELL_CARRIES_IT_AND_STILL_CARRIES_THE_WORK`;
  (b) fire without a result (e.g. match any `SEAT_RESULT_`, or ignore the stem) --
      `test_THE_PARTITION_...` (the no-result and other-stem legs);
  (c) require the result's date to equal the prereg's -- `test_THE_PARTITION_...` (spent leg);
  (d) look only in `records/` -- `test_A_RESULT_FILED_IN_ANOTHER_ROOM_IS_STILL_FOUND` (the archive
      leg alone cannot catch it: its first add IS in `records/`);
  (e) read the working tree rather than origin/main -- `test_AN_UNLANDED_RESULT_IS_NOT_A_LANDED_ONE`.
"""
import subprocess

import pytest

from background import delivery_lane as dl

STEM = "THE_TWO_STATE_DIFF_RERUN_UNDER_THE_BALANCE_AT_CLOSE_RULE"
PREREG = f"docs/staging/records/SEAT_PREREG_{STEM}_2026-09-27.md"
RESULT = f"docs/staging/records/SEAT_RESULT_{STEM}_2026-09-28.md"


def _git(repo, *args):
    return subprocess.run(("git", "-C", str(repo)) + args, check=True, capture_output=True,
                          text=True).stdout.strip()


def _commit(repo, path, msg):
    f = repo / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(msg + "\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", msg)
    return _git(repo, "rev-parse", "--short=9", "HEAD")


def _publish(repo):
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


@pytest.fixture
def repo(tmp_path, monkeypatch):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@t")
    _git(r, "config", "user.name", "t")
    _commit(r, PREREG, "prereg")
    _publish(r)
    monkeypatch.setattr(dl, "PROJECT_DIR", r)
    return r


def _item(what=f"then grade B1-B5 in {PREREG}."):
    return {"id": "grade-it", "what": what, "why": "the effect is still open"}


def test_THE_PARTITION_spent_and_outstanding_are_both_reachable(repo):
    """One control over the whole partition, the rare branch asserted reachable FIRST."""
    silent_before = dl.result_note(_item())
    _commit(repo, "docs/staging/records/SEAT_RESULT_SOME_OTHER_SUBJECT_2026-09-28.md", "other")
    _publish(repo)
    silent_other_stem = dl.result_note(_item())
    sha = _commit(repo, RESULT, "result")
    _publish(repo)
    spent = dl.result_note(_item())
    assert spent and silent_before == "" and silent_other_stem == ""
    assert sha in spent and RESULT in spent
    assert f"--premise-spent grade-it {sha}" in spent


def test_AN_ARCHIVED_RESULT_NAMES_ITS_FIRST_LANDING_NOT_THE_MOVE(repo):
    sha = _commit(repo, RESULT, "result")
    (repo / "docs/staging/done").mkdir(parents=True)
    _git(repo, "mv", RESULT, RESULT.replace("/records/", "/done/"))
    _git(repo, "commit", "-qm", "archive")
    _publish(repo)
    note = dl.result_note(_item())
    assert sha in note, note


def test_A_RESULT_FILED_IN_ANOTHER_ROOM_IS_STILL_FOUND(repo):
    sha = _commit(repo, RESULT.replace("/records/", "/"), "result at the queue root")
    _publish(repo)
    assert sha in dl.result_note(_item())


def test_AN_UNLANDED_RESULT_IS_NOT_A_LANDED_ONE(repo):
    _commit(repo, RESULT, "result")  # committed locally, origin/main not advanced
    assert dl.result_note(_item()) == ""


def test_A_RESULT_NAMED_ONLY_IN_DONE_MEANS_IS_A_COMPLETION_MARKER_NOT_A_PREMISE(repo):
    _commit(repo, RESULT, "result")
    _publish(repo)
    item = {"id": "x", "what": "do the thing", "why": "", "done_means": f"graded in {PREREG}"}
    assert dl.result_note(item) == ""


def test_AN_UNANSWERABLE_GIT_IS_SILENT_AND_NEVER_RAISES(repo, monkeypatch):
    monkeypatch.setattr(dl, "_git", lambda *a, **k: None)
    assert dl.result_note(_item()) == ""


def test_THE_DOORBELL_CARRIES_IT_AND_STILL_CARRIES_THE_WORK(repo, monkeypatch):
    """An annotation, never a filter: the work is still in the doorbell beside the note."""
    for name in ("premise_note", "landed_since_note", "rival_note", "successor_note", "path_note"):
        monkeypatch.setattr(dl, name, lambda *a, **k: "")
    sha = _commit(repo, RESULT, "result")
    _publish(repo)
    bell = dl.doorbell(_item())
    assert "RESULT CHECK" in bell and sha in bell
    assert "then grade B1-B5" in bell
    assert bell.index("RESULT CHECK") < bell.index("then grade B1-B5")
