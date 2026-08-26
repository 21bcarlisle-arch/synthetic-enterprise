"""R11 for the delivery record: the four questions must ARRIVE ON THE PAGE, not in a JSON file.

Director, 2026-08-25: *"I can't see any of this without someone reading git logs to me. I want to
open one page and know what the machine did, what it decided, what it got wrong, and what it's
doing next. Harness was meant to be that and isn't."*

WHY IT DRIVES THE REAL DOOR. R11 means the assertion is on the value a browser RENDERS, never on a
string in the repo. The failure this shape catches is the one that actually ships: the page
deploys fine, its feed 404s or drifts schema, and every panel sits on a placeholder forever. The
class control for that is `site/test_door_render_functions_are_wired.py`, filed the day a live
door served "Loading…" under a heading for eight days.

TWO STATES, BOTH TESTED, and the second is the one that matters more today. The seat has not run
on a fresh clone, so the panels must render an HONEST ABSENCE rather than nothing at all -- a
machine that reports no decisions and a machine that has not been asked to decide look identical
from outside unless the page says which it is.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "harness" / "index.html"
DATA = SITE / "data"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

#: Every feed the door boots from, as written in the page. FAIL-CLOSED: the harness rejects a url
#: the fixture did not supply, so a door that grows a fifth feed reds here instead of silently
#: testing its absence path.
FEED_FILES = {
    "../data/proof.json": "proof.json",
    "../data/delivery.json": "delivery.json",
    "../data/director_delta.json": "director_delta.json",
    "../data/director_reserved.json": "director_reserved.json",
}

PANELS = ("delivery-kpis", "delivery-did", "delivery-decided", "delivery-wrong",
          "delivery-next", "director-delta")


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def _render(overrides: dict | None = None) -> dict:
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing — the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    feeds = {}
    for url, name in FEED_FILES.items():
        path = DATA / name
        if not path.is_file():
            pytest.fail(f"{path} does not exist, so the page a reader gets cannot be rendered")
        feeds[url] = json.loads(path.read_text(encoding="utf-8"))
    feeds.update(overrides or {})
    proc = subprocess.run(["node", str(HARNESS), str(DOOR)],
                          input=json.dumps(feeds), capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, f"the render harness failed: {proc.stderr[-2000:]}"
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        f"the door asked for a feed this test did not supply: {meta.get('unresolved')}")
    assert not meta.get("scriptError"), f"the door's own script threw: {meta.get('scriptError')}"
    return out


@pytest.fixture(scope="module")
def rendered():
    return _render()


@pytest.mark.parametrize("panel", PANELS)
def test_every_delivery_panel_actually_RENDERS(rendered, panel):
    """MUTATION (must fire): define a render function and never call it -- the exact defect that
    served a live door "Loading…" for eight days."""
    assert panel in rendered, f"#{panel} is not on the page at all"
    body = _text(rendered[panel]["innerHTML"])

    assert body, f"#{panel} rendered nothing, so a reader sees an empty heading"
    assert "Loading" not in body, f"#{panel} is still on its placeholder"


def test_the_page_answers_WHAT_IT_DID_with_work_separated_from_republishing(rendered):
    """The honest half of "what it did": an auto-process republish is not work, and a page that
    counts it as work makes a quiet day look busy."""
    kpis = _text(rendered["delivery-kpis"]["innerHTML"])

    assert "pieces of real work" in kpis
    assert "routine republishes, not counted as work" in kpis


def test_the_page_answers_WHAT_IT_DECIDED_and_shows_what_was_TURNED_DOWN(rendered):
    """The rejections are the reviewable half -- the director's own reason for asking for them:
    *"record the options you considered and why you chose as you did. That record is what I
    review, and it's what makes it safe for you not to ask."*

    MUTATION (must fire): render only the chosen focus.
    """
    decided = rendered["delivery-decided"]["innerHTML"]
    live = json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))["what_it_decided"]
    if not live.get("available"):
        # HONEST ABSENCE, not a skip. This is the state of a fresh clone and of any stretch the
        # seat has not yet oriented, so it is the state most readers will actually meet.
        assert "no valid direction record" in _text(decided)
        assert "not that it has stopped" in _text(decided), (
            "an absent direction must say the machine is still working, or a reader reads it as "
            "a stall"
        )
        return
    assert "Turned down, and why" in decided
    assert "Chose" in decided


def test_an_empty_WHAT_IT_GOT_WRONG_says_WHICH_kind_of_empty_it_is(rendered):
    """A machine reporting no mistakes is either not looking or not saying, and both read
    identically from outside.

    MUTATION (must fire): render an empty panel, or the word "None".

    THE EMPTY STATE IS READ FROM THE DATA, NOT GREPPED OUT OF THE HTML (2026-08-26). This
    condition was `if "recorded" in body:` -- a WORD standing in as a proxy for a STATE, on the
    reasoning that the empty-state sentence happens to contain it. On 2026-08-26 the seat had
    recorded 27 mistakes, one of which used the word "recorded" in its own prose, so a fully
    populated panel took the empty-state branch and demanded a sentence that has no business
    being there. It refused the publish commit, at 06:52, on the FIRST cycle after the map-split
    landing had cleared the real cause -- a control firing on the success path, which is the
    class this whole morning was about.

    A substring is not a state. `delivery.json` says which state it is in, so ask it.
    """
    body = _text(rendered["delivery-wrong"]["innerHTML"])
    assert body and body != "None"

    entries = (json.loads((DATA / "delivery.json").read_text(encoding="utf-8"))
               .get("what_it_got_wrong") or {}).get("entries") or []
    if entries:
        # POPULATED: the panel must actually carry the mistakes, not a summary of them. Read the
        # first entry's own words back out of the rendering, so a panel that renders the count
        # and drops the text fails here rather than passing on a plausible-looking number.
        first = _text(entries[0].get("what", ""))[:60]
        assert first and first in body, (
            "the panel has {} recorded mistake(s) and does not carry the first one's text -- a "
            "reader is being told the number and not the finding".format(len(entries))
        )
        return
    assert "not that nothing went wrong" in body or "no orientation has recorded" in body, (
        "the panel is EMPTY and does not say which kind of empty: a machine that found no "
        "mistakes and one that never looked read identically from outside"
    )


def test_WHAT_IT_IS_DOING_NEXT_states_that_direction_can_never_BLOCK_work(rendered):
    """The property a reader needs in order to trust the mechanism at all: a wrong instruction
    slows this machine down and can never wedge it."""
    body = _text(rendered["delivery-next"]["innerHTML"])

    assert "can never zero one" in body or "never obeyed by force" in body


def test_the_director_delta_does_not_claim_he_has_LOOKED(rendered):
    """SITE9's ruling was overturned on 2026-08-25 -- *"Rebuild the delta as a section on
    /harness/"* -- and the honesty that makes the panel publishable travels with it. The stamp
    currently reads `bootstrap-at-build-time (not a director read receipt)`: nobody has marked a
    read. A panel headed "since you last looked" over that stamp would be asserting he has.

    MUTATION (must fire): render `last_look_at` as a read receipt without checking
    `last_look_recorded_by`.
    """
    feed = json.loads((DATA / "director_delta.json").read_text(encoding="utf-8"))
    body = _text(rendered["director-delta"]["innerHTML"])

    if str(feed.get("last_look_recorded_by", "")).startswith("bootstrap"):
        assert "not a record of anyone reading anything" in body
    assert "Measured against a position recorded on" in body


def test_a_MISSING_delivery_feed_renders_a_stated_absence_and_not_a_blank_page():
    """FAIL-CLOSED at the reader, which is the only place it counts. The door's own `.catch()`
    branch must produce words; a blank panel under a live heading is the failure this whole file
    exists for.

    MUTATION (must fire): drop the `.catch()` from the delivery fetch.
    """
    out = _render({"../data/delivery.json": None})
    body = _text(out["delivery-did"]["innerHTML"])

    assert body, "a broken feed leaves the panel silently empty"
