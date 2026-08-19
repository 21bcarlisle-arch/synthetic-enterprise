#!/usr/bin/env python3
"""R15 proof for the two-rooms repair (director instruction, 2026-08-19).

This control DELETES FILES, so the mutation that matters most is not "does it fire" but "does it
refuse". A repairer that removes a document carrying something no other copy has is worse than
the commit refusal it exists to clear, and worse in a way nobody notices until the content is
wanted. So the conflict case is driven hardest.

The safe predicate is deliberately narrow: the root copy's text must be wholly contained in the
archived copy. That held for both real instances on 2026-08-19 -- each archived copy was the root
text plus an appended discharge section -- and anything outside it is left alone by design.
"""
from __future__ import annotations

import subprocess

import pytest

from background import staging_two_rooms_repair as tr


def _rooms(tmp_path, root_text=None, done_text=None, name="WORKER_FINDING_X.md"):
    root = tmp_path / "staging"
    done = root / "done"
    done.mkdir(parents=True, exist_ok=True)
    if root_text is not None:
        (root / name).write_text(root_text, encoding="utf-8")
    if done_text is not None:
        (done / name).write_text(done_text, encoding="utf-8")
    return root


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------
def test_a_document_in_both_rooms_is_a_duplicate(tmp_path):
    root = _rooms(tmp_path, "the finding", "the finding\n\nDischarged.")
    assert [n for n, _, _ in tr.duplicates(root)] == ["WORKER_FINDING_X.md"]


def test_a_document_in_one_room_only_is_not(tmp_path):
    assert tr.duplicates(_rooms(tmp_path, "the finding", None)) == []
    (tmp_path / "staging" / "WORKER_FINDING_X.md").unlink()
    assert tr.duplicates(_rooms(tmp_path, None, "the finding")) == []


# ---------------------------------------------------------------------------
# The predicate -- both sides
# ---------------------------------------------------------------------------
def test_MUTATION_the_archived_copy_containing_the_root_copy_is_SAFE(tmp_path):
    """The real shape: the archive is the root text plus an appended discharge."""
    root = _rooms(tmp_path, "the finding", "the finding\n\n## Discharged\n\nrepaired here.")
    name, r, a = tr.duplicates(root)[0]
    assert tr.classify(r, a) == tr.SAFE


def test_MUTATION_a_root_copy_saying_something_the_archive_does_NOT_is_a_CONFLICT(tmp_path):
    """THE test. If the root copy carries a sentence the archive lacks, deleting it destroys
    the only copy of that sentence. The repairer must decline, even though declining leaves
    every commit in the tree refused -- a refusal is recoverable and a deletion is not."""
    root = _rooms(tmp_path, "the finding\n\nAND A LATER AMENDMENT", "the finding")
    name, r, a = tr.duplicates(root)[0]
    assert tr.classify(r, a) == tr.CONFLICT


def test_MUTATION_a_conflicting_duplicate_is_LEFT_ON_DISK(tmp_path):
    """Driven through `repair()` rather than `classify()`, because the property that matters is
    that the FILE survives, not that a function returned a string."""
    root = _rooms(tmp_path, "root says more", "archive says less")
    res = tr.repair(root)
    assert res["repaired"] == [] and res["conflicts"] == ["WORKER_FINDING_X.md"]
    assert (root / "WORKER_FINDING_X.md").is_file(), "a conflicting root copy was deleted"


def test_MUTATION_an_unreadable_pair_is_a_CONFLICT_not_a_repair(tmp_path):
    """Fail-closed toward KEEPING: if the comparison cannot be made, the file stays. An
    unreadable file is the case where 'is it redundant?' is least knowable."""
    root = _rooms(tmp_path, "x", "x")
    name, r, a = tr.duplicates(root)[0]
    r.unlink()
    r.mkdir()  # a directory where a file was: read_text raises
    assert tr.classify(r, a) == tr.CONFLICT


# ---------------------------------------------------------------------------
# The repair
# ---------------------------------------------------------------------------
def test_a_redundant_root_copy_is_removed_and_the_archive_survives(tmp_path):
    root = _rooms(tmp_path, "the finding", "the finding\n\nDischarged.")
    res = tr.repair(root)
    assert res["repaired"] == ["WORKER_FINDING_X.md"] and res["conflicts"] == []
    assert not (root / "WORKER_FINDING_X.md").exists()
    assert (root / "done" / "WORKER_FINDING_X.md").is_file(), "the ARCHIVE was deleted"


def test_MUTATION_the_deletion_is_STAGED_not_merely_unlinked(tmp_path):
    """The half that makes the repair stick. Removing the file from the working tree alone
    leaves the path tracked at HEAD, and anything that restores a tracked path brings it back --
    which is the shape of the recurrence this exists to end. Driven against a REAL git repo,
    because the property is about git's index, not about the filesystem."""
    repo = tmp_path / "repo"
    (repo / "docs" / "staging" / "done").mkdir(parents=True)
    dup = repo / "docs" / "staging" / "WORKER_FINDING_X.md"
    dup.write_text("the finding", encoding="utf-8")
    (repo / "docs" / "staging" / "done" / "WORKER_FINDING_X.md").write_text(
        "the finding\n\nDischarged.", encoding="utf-8")
    for args in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "seed"]):
        subprocess.run(["git", *args], cwd=str(repo), check=True, capture_output=True)

    import background.staging_two_rooms_repair as mod
    original = mod.PROJECT_DIR
    try:
        mod.PROJECT_DIR = repo
        mod.repair(repo / "docs" / "staging")
    finally:
        mod.PROJECT_DIR = original

    staged = subprocess.run(["git", "diff", "--cached", "--name-status"], cwd=str(repo),
                            capture_output=True, text=True).stdout
    assert "D\tdocs/staging/WORKER_FINDING_X.md" in staged, (
        "the removal was not staged -- the path stays tracked at HEAD and can be restored, "
        f"which is the whole recurrence. staged diff was: {staged!r}"
    )


def test_a_clean_tree_repairs_nothing(tmp_path):
    root = _rooms(tmp_path, "only here", None)
    assert tr.repair(root) == {"repaired": [], "conflicts": []}


# ---------------------------------------------------------------------------
# The worker seat
# ---------------------------------------------------------------------------
def test_observe_is_silent_when_there_is_nothing_to_do(monkeypatch):
    """R5. This runs every worker cycle; a line per cycle is how a signal becomes noise."""
    monkeypatch.setattr(tr, "repair", lambda *a, **k: {"repaired": [], "conflicts": []})
    assert tr.observe() == {"changed": False}


def test_observe_alarms_on_a_conflict_it_cannot_fix(monkeypatch):
    monkeypatch.setattr(tr, "repair", lambda *a, **k: {"repaired": [], "conflicts": ["A.md"]})
    r = tr.observe()
    assert r["changed"] and "NOT SAFELY REPAIRABLE" in r["alarm"] and "A.md" in r["alarm"]


def test_MUTATION_a_repair_fault_cannot_take_the_worker_down(monkeypatch):
    """It runs inside the daemon loop. A governor that can kill the daemon is a worse outage
    than the commit refusal it was fixing."""
    def boom(*a, **k):
        raise RuntimeError("disk gone")

    monkeypatch.setattr(tr, "repair", boom)
    r = tr.observe()
    assert r["changed"] and "TWO-ROOMS REPAIR FAILED" in r["alarm"]


def test_the_worker_calls_it():
    """The no-caller class, again. Four manual clears happened because nothing automatic was
    watching; a repair nobody runs would be the fifth."""
    import inspect
    from background import background_worker
    assert "staging_two_rooms_repair" in inspect.getsource(background_worker.main)
