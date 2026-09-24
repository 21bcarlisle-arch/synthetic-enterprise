#!/usr/bin/env python3
"""THE DEFECT: a repeating-alarm document WAS its own state store, so clearing it lost everything.

Until 2026-09-24 `background/alarm_repetition.py` kept no state anywhere. Every count in a
document's header was derived from that document's own dated lines -- its header said so in those
words -- so the file was three things at once: the state store, the published work item, and a
TRACKED path that origin carries its own copy of. Any two are fine; all three are a self-refilling
merge collision. Measured that day: the shared tree ten commits behind origin/main, the
fast-forward refused on nine of these documents, and its daemons running code 55 modules behind
because of it.

The fix is a store on an untracked path with the document derived from it. THE PROPERTY THAT MAKES
THAT WORTH ANYTHING, and the only one these tests assert: **clearing the document costs nothing but
the rendering.** Not "the store exists", not "the json has the right keys" -- a control keyed to
the presence of a mechanism is green the day the mechanism stops working.

Every test here is written so that DELETING the store makes it fail. `test_MUTATION_without_the_store_the_history_IS_lost`
is that statement made directly, so the suite cannot be passing for a reason other than the one it
claims.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import pytest

from background import alarm_repetition as ar

ALARM = "[daemon] the producer failed after 252s"
KEY = "producer:sim-producer-failed"
DAY = 86400.0
#: 2026-09-15T00:00:00Z. A FIXED instant, not `time.time()`: every assertion here is about which
#: DATES survive a clear, and a fixture on the wall clock would answer differently on a day the
#: run straddles midnight UTC.
_2026_09_15 = 1_789_430_400.0


def _fire(staging: Path, *, at: float, message: str = ALARM, key: str = KEY,
          first_ts: float | None = None) -> None:
    """One firing of one alarm at wall-clock `at`, through the ordinary door."""
    ar.escalate(message, key=key, first_ts=at if first_ts is None else first_ts,
                repeats=3, staging_dir=staging, now=at)


def _document(staging: Path) -> Path:
    found = sorted(staging.glob("WORKER_FINDING_REPEATING_ALARM_*.md"))
    assert len(found) == 1, f"expected exactly one document, found {[p.name for p in found]}"
    return found[0]


@pytest.fixture
def burned_in(tmp_path):
    """A document whose condition has been observed on four consecutive days, by two members."""
    staging = tmp_path / "staging"
    staging.mkdir()
    start = _2026_09_15
    for day in range(4):
        _fire(staging, at=start + day * DAY, first_ts=start)
    # A SECOND MEMBER OF THE SAME FAMILY, so the instance list has something to lose too. It has
    # to differ in the key's TAIL and not in the message: `normalise` removes elapsed times, so
    # "failed after 252s" and "failed after 981s" are one member by design, and a fixture that
    # varied the seconds would be asserting two members while producing one.
    _fire(staging, at=start + 4 * DAY, key="producer:sim-producer-timed-out",
          message="[daemon] the producer timed out after 900s", first_ts=start)
    return staging, start


def test_clearing_the_document_loses_NOTHING_the_next_firing_rebuilds_it(burned_in):
    """THE PROPERTY. Delete the rendering; the condition's history survives the deletion.

    Asserted on the DERIVED COUNTS rather than on the json's contents, because the counts are what
    a draw reads and what a seat ranks on. A store that held every date and rendered none of them
    would pass an existence check and fail this one, which is the right way round.
    """
    staging, start = burned_in
    before = ar.document_counts(_document(staging))
    assert before.days == 5 and before.members == 2, before

    _document(staging).unlink()
    assert not list(staging.glob("*.md"))

    _fire(staging, at=start + 5 * DAY, first_ts=start)

    after = ar.document_counts(_document(staging))
    assert after.days == 6, f"the five observed days did not survive the clear: {after}"
    assert after.members == 2, f"the second family member was lost by the clear: {after}"
    assert after.first == before.first, (
        f"the episode's start moved when the document was cleared: {before.first} -> {after.first}")


def test_MUTATION_without_the_store_the_history_IS_lost(burned_in):
    """The same clear, with the store removed first. THIS MUST FAIL TO PASS.

    Without this the test above proves only that `escalate` writes a document. It is the one leg
    that establishes the store is what carries the history, rather than something else in the
    module happening to reconstruct it -- and it is the exact defect as it stood before the split:
    five observed days and two members reduced to one day and one member by an `rm`.
    """
    staging, start = burned_in
    ar._state_file(staging).unlink()
    _document(staging).unlink()

    _fire(staging, at=start + 5 * DAY, first_ts=start)

    after = ar.document_counts(_document(staging))
    assert after.days == 1, f"something other than the store rebuilt the history: {after}"
    assert after.members == 1, f"something other than the store rebuilt the members: {after}"


def test_the_rebuilt_document_is_a_SUPERSET_of_the_store_not_a_summary_of_it(burned_in):
    """A re-derived document must still carry the dated LINES its header counts.

    The store is only falsifiable from the artefact while the document's own pure reader --
    `_observation_dates`, which knows nothing about the store -- returns the same set the store
    holds. A rebirth that wrote the header and dropped the lines would publish counts nobody could
    check, which is this project's most expensive recurring shape.
    """
    staging, start = burned_in
    _document(staging).unlink()
    _fire(staging, at=start + 5 * DAY, first_ts=start)

    path = _document(staging)
    from_document = ar._observation_dates(path, path.read_text(encoding="utf-8"))
    from_store = set(ar.absorb(path)["observed"])
    assert from_document == from_store, (
        f"the document and the store disagree; only in the store: {from_store - from_document}, "
        f"only in the document: {from_document - from_store}")


def test_a_replayed_line_says_it_is_a_RECORD_and_not_todays_observation(burned_in):
    """Five dated lines appearing at once must not read as five firings happening now."""
    staging, start = burned_in
    _document(staging).unlink()
    _fire(staging, at=start + 5 * DAY, first_ts=start)

    replayed = [ln for ln in _document(staging).read_text(encoding="utf-8").splitlines()
                if "re-derived" in ln]
    assert replayed, "the replayed lines do not say where they came from"
    assert all("not today's" in ln for ln in replayed), replayed


def test_the_store_never_SHRINKS_when_a_document_is_edited_down(burned_in):
    """Union, never subtraction. A hand-trimmed document cannot delete an observation.

    The seat edits these documents. A store that agreed with whatever the document currently says
    would be the old defect with an extra file in it.
    """
    staging, start = burned_in
    path = _document(staging)
    held = set(ar.absorb(path)["observed"])

    path.write_text("# gutted\n\n## Still live\n\n## Instances seen\n", encoding="utf-8")
    assert set(ar.absorb(path)["observed"]) >= held, "the store shrank to match a trimmed document"


def test_an_ARCHIVED_condition_that_returns_does_not_inherit_the_closed_episodes_dates(burned_in):
    """The one thing the store must forget, and the one thing it must not.

    `escalate()` deliberately does not search `done/`: a condition returning after archival is a
    NEW episode and an R3 two-strike signal. The store has to make the same cut, or the returning
    document's header would claim continuous observation across the gap -- the same error arriving
    through the store instead of through the filename. The closed episode is kept beside the live
    one, because the second strike is only legible against the first.
    """
    staging, start = burned_in
    path = _document(staging)
    ar._archive_cleared(
        ar.Reask(path=path, key=KEY, family="producer", verdict=ar.CLEARED,
                 last_observed="2026-09-20", reason="nothing observed it for three days"),
        today="2026-09-24")
    assert not list(staging.glob("*.md")), "the archive did not remove the live document"

    _fire(staging, at=start + 40 * DAY, first_ts=start + 40 * DAY)
    returned = ar.document_counts(_document(staging))
    assert returned.days == 1, f"the new episode inherited the closed one's dates: {returned}"

    stored = json.loads(ar._state_file(staging).read_text(encoding="utf-8"))
    episodes = [e for entry in stored["documents"].values() for e in entry["episodes"]]
    assert episodes and len(episodes[0]["observed"]) == 5, (
        f"the closed episode was discarded rather than retired: {episodes}")


def test_the_store_lives_on_an_UNTRACKED_path_outside_the_staging_room():
    """The defect was a TRACKED path rewritten in place. A store that is tracked is the defect.

    Asked of git directly rather than by reading `.gitignore` for a string: the question is whether
    this repository would commit the file, and only git can answer that.
    """
    store = ar.ALARM_STATE_FILE
    assert ar.STAGING_DIR not in store.parents, (
        f"the store sits inside the staging room, where the merge collision was: {store}")
    ignored = subprocess.run(["git", "check-ignore", "-q", str(store)],
                             cwd=ar.PROJECT_DIR, capture_output=True)
    assert ignored.returncode == 0, (
        f"{store} is not ignored by git -- every firing would dirty a tracked path again, which "
        f"is the FF_MODIFIED collision this store was split out to end")
    assert not subprocess.run(["git", "ls-files", "--error-unmatch", str(store)],
                              cwd=ar.PROJECT_DIR, capture_output=True).returncode == 0, (
        f"{store} is tracked despite being ignored -- an ignore does not untrack an added file")


def test_a_test_run_cannot_write_the_REAL_store(monkeypatch, tmp_path):
    """The readers seed the store as a side effect of being read, so the guard has to cover reads.

    `escalate()` has carried a guard of this shape since the day five test fixtures appeared in the
    director's queue. The split added a second door into the real tree -- merely COUNTING a real
    document would have written the live store -- and it needed the same guard, not a similar one.
    """
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_a_test_run_cannot_write_the_REAL_store")
    assert ar._write_state(ar.STAGING_DIR, {"documents": {"x": {}}}) is False
    assert ar._write_state(tmp_path, {}) is True, (
        "the guard is scoped to the real directory, or it makes the module untestable")


def test_the_store_answers_for_a_document_in_in_progress_and_the_root_alike(tmp_path):
    """Parking a document must not give it a second, empty history.

    `_live_finding_for` treats the root and `in_progress/` as one room. A store that keyed on the
    containing directory would hand a parked document a blank slate on the day somebody moved it,
    which is exactly when a reader most wants its age.
    """
    staging = tmp_path / "staging"
    (staging / "in_progress").mkdir(parents=True)
    start = _2026_09_15
    _fire(staging, at=start)
    path = _document(staging)
    before = ar.document_counts(path)

    parked = staging / "in_progress" / path.name
    path.rename(parked)
    assert ar.document_counts(parked).days == before.days
    assert ar._staging_dir_of(parked) == ar._staging_dir_of(path)
