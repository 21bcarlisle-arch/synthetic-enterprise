"""A running `surgical_land` whose `-m` names an item's id holds that item from the draw.

THE DEFECT (2026-10-25). `_mid_landing` read a live landing's message for the ledger, but the
draw's `held_grade` matched only held paths, changed identifiers and new-file names, so an item a
landing was carrying right then was offered to a second lane. The wider leg the direction item
asked for, an ORIGIN commit naming the id, is not built: replayed over 7 days it fired on 62 of
238 continuations, nearly all at birth on their own hand-off commit
(docs/staging/SEAT_FINDING_A_COMMIT_NAMING_A_CONTINUATION_IS_NOT_ITS_FINISH_REPLAYED_AGAIN_2026-10-25.md).

The landing here is a real process whose argv is a `surgical_land` command line, read back from
`/proc` by the production `_live_landings`, so the argv parse is under test too.

MUTATIONS (each must fire):
  * delete the id leg in `held_grade` -- the named arm stops refusing.
  * drop the whole-word look-arounds -- the longer-id arm refuses.
  * make the leg refuse on any landing -- the unnamed arm refuses.
"""

from __future__ import annotations

import subprocess
import sys
import time

import pytest

from background import delivery_lane as dl

_REAL_LIVE_LANDINGS = dl._live_landings  # captured before conftest's autouse patch

#: The real row from the continuation store, as it stood when 4566ce348 spent its premise.
ITEM = {
    "id": "knowledge-pack-verification-census",
    "what": "Count, per 25 Oct evidence pack, the [unverified] items confirmed, corrected and still "
            "open, and publish the counts in the Knowledge index or the map's coverage counts",
    "why": "The verify steer's report-back is the one part not done.",
    "done_means": "the index shows the per-pack table",
}


@pytest.fixture
def landing():
    """Spawn a sleeping process whose argv is a surgical_land command line; yield a starter."""
    procs: list[subprocess.Popen] = []

    def start(message: str) -> int:
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)",
                                 "-m", "tools.surgical_land", "-m", message,
                                 "site/knowledge/index.html"])
        procs.append(proc)
        deadline = time.time() + 10
        while time.time() < deadline:
            if any(h["holder"] == f"surgical_land pid {proc.pid}" for h in _REAL_LIVE_LANDINGS()):
                return proc.pid
            time.sleep(0.05)
        raise AssertionError("the spawned landing never appeared in /proc")

    yield start
    for proc in procs:
        proc.kill()
        proc.wait()


def _grade(pid: int):
    mine = [h for h in _REAL_LIVE_LANDINGS() if h["holder"] == f"surgical_land pid {pid}"]
    assert mine, "the landing left /proc before it was graded"
    hit, _context = dl.held_grade(ITEM, mine, vocabulary=({}, 1))
    return hit


def test_a_landing_naming_the_id_holds_it_and_one_that_does_not_leaves_it_offered(landing):
    named = _grade(landing("Per-pack census on the Knowledge index\n\n"
                           "NEXT: none -- direction item knowledge-pack-verification-census, finished"))
    longer = _grade(landing("NEXT: knowledge-pack-verification-census-second-pass"))
    unnamed = _grade(landing("The Germany, Italy and Spain lists stop naming what the second read closed"))

    # The whole partition in one assertion: a guard that refuses everything fails the second and
    # third legs, and one that refuses nothing fails the first.
    assert (named is not None, longer is None, unnamed is None) == (True, True, True), (
        named, longer, unnamed)
    assert "is landing it now: its message names knowledge-pack-verification-census" in named[1]
