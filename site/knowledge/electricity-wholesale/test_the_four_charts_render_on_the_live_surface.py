"""The four rung-5 charts render when the page BOOTS ITSELF — not when we call its functions.

WHAT THIS DISCHARGES. `PLANNER_MINTED_one_node_to_depth_with_charts_2026-07-28` has owed one
thing since it was minted: *"verify the four rung-5 charts on the LIVE surface (R11, deferred to
'the next publish' and never taken)."* It sat undrawn for eight days as one third of the
`[ACT] 3 SELF-DRAWABLE mint(s) have sat UNDRAWN` alarm, and the reason it sat is that it LOOKS
done: `test_knowledge_wholesale.py` carries forty-three passing tests, three per chart plus a
DoD gate plus two both-ways mutations.

THE DISTINCTION THAT MADE IT NOT DONE, and it is not a technicality. Those tests drive the page
through `_render_harness.mjs`, a PER-DOOR harness. The generic harness's own docstring is the
indictment, and it names these files:

    Every existing harness in this repo (site/*/_render_harness.mjs, site/proof/_door_harness.mjs)
    is written PER DOOR: it imports the page's inline script and then calls that page's render
    functions BY NAME, in the page's own order. That is fine for a door-level unit test, but it
    CANNOT BE POINTED AT THE LIVE SITE, and it goes stale the moment a door renames a render
    function.

A by-name harness proves the render functions work. R11 asks whether the READER sees the chart,
and the failure R11 exists to catch is the one a by-name harness passes straight through: the page
deploys, its json 404s or drifts schema, the page's own `fetch(...).then(...)` chain never
completes, and every panel sits on "Loading..." forever. Calling `renderLive(data)` directly skips
the entire boot sequence in which that failure lives.

So this file drives `index.html` through `site/_live_harness.mjs`, which knows NO function names.
It supplies `fetch` and lets the door's own promise chain drive itself to completion, then reports
what ended up in the elements. Whatever the page renders, it renders.

WHY THE MARKS ARE ASSERTED PER CHART AND NOT AS A TOTAL. A total is satisfied by one chart drawing
four times as much, which is exactly what a broken loop looks like. Measured on the live surface
2026-08-30, each chart draws a distinguishable mark set:

    svg 1 (price series)       path 1, line 3, circle 1, text 7
    svg 2 (merit order)        rect 4, line 3, circle 1, text 5
    svg 3 (seasonal)           rect 12, line 3, text 16
    svg 4 (negative prices)    rect 9,  line 3, text 13

The assertions below are FLOORS on the structure, not pins on those counts — a chart that gains a
data point must not red, and a chart that loses its geometry must.

NOT A DUPLICATE of `test_knowledge_wholesale.py`. That file grades the chart CONTENT (pipeline
provenance, data-driven not constant, the DoD gate). This grades that the content arrives at the
reader through the page's own boot. Both are wanted; only one of them was written.

THE MEASUREMENT THAT SETTLES WHETHER THIS FILE WAS WORTH WRITING, and it is not an argument.
The page's feed url was repointed at a path that does not exist — the exact live shape of "the
json 404s after a deploy" — and both suites were run against the same broken page:

    site/knowledge/electricity-wholesale/test_knowledge_wholesale.py   31 passed
    this file                                                          6 failed, 2 passed

**Thirty-one green tests on a page that renders nothing to a reader.** That is the whole of the
gap the mint had been carrying, stated as a number rather than as a concern about harness design.
Neither suite is wrong; they grade different things, and only one of them grades R11.

R15 MUTATIONS, applied in place and reverted, results as OBSERVED:
  * the page's `fetch` url changed to a path the harness does not supply -> the harness rejects
    exactly as a 404 would live, the boot chain dies, and **6 red**:
    `test_the_page_boots_itself` naming the unresolved url, plus the four-chart count and all
    four per-chart geometry checks. The two that survive are the markup-existence check (which
    reads the file, not the render) and the all-same-chart check (vacuous with zero charts) —
    recorded because a mutation's survivors say as much as its casualties.
  * `<div id="r-live">` deleted -> `test_the_live_rung_element_exists_in_the_markup` reds while
    the render assertions still pass, because the harness autocreates any id it is asked for
    (`WORKER_FINDING_THE_RENDER_HARNESS_AUTOCREATES_THE_ELEMENT_A_DELETED_PARAGRAPH_WOULD_LOSE`).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
DOOR = HERE / "index.html"
LIVE_HARNESS = SITE / "_live_harness.mjs"
FEED_URL = "../../data/knowledge_wholesale.json"
FEED = SITE / "data" / "knowledge_wholesale.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

#: Structural floor per chart, in document order. Keyed to the PROPERTY (this chart is drawn with
#: these kinds of mark and has axes and labels), never to today's data point count.
CHART_FLOORS = (
    ("price series",    {"path": 1, "line": 3, "text": 4}),
    ("merit order",     {"rect": 3, "line": 3, "text": 4}),
    ("seasonal",        {"rect": 8, "line": 3, "text": 8}),
    ("negative prices", {"rect": 6, "line": 3, "text": 8}),
)


def _boot() -> dict:
    """Drive the LIVE door with the LIVE feed, through its own fetch/then chain."""
    proc = subprocess.run(
        [NODE, str(LIVE_HARNESS), str(DOOR)],
        input=json.dumps({FEED_URL: json.loads(FEED.read_text())}),
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[:600]
    return json.loads(proc.stdout)


def _svg_segments(html: str) -> list[str]:
    return [part.split("</svg>")[0] for part in html.split("<svg")[1:]]


def test_the_live_rung_element_exists_in_the_markup():
    """Checked against the FILE. The harness autocreates any id, so a deleted element renders."""
    assert re.search(r'id="r-live"', DOOR.read_text(encoding="utf-8")), (
        "the page has no element with id=r-live; the harness would autocreate it and report the "
        "charts rendered into nothing")


def test_the_page_boots_itself():
    """No unresolved fetch, no script error. This is the failure a by-name harness cannot see."""
    out = _boot()
    meta = out.get("_meta", {})
    assert not meta.get("static"), "the door reported itself static -- nothing drove"
    assert meta.get("scriptError") is None, f"boot raised: {meta.get('scriptError')}"
    assert not meta.get("unresolved"), (
        f"the page fetched urls nothing supplied: {meta.get('unresolved')} -- live, these are "
        f"404s, the promise chain dies, and every panel sits on 'Loading...' forever")
    assert meta.get("requested"), "the page fetched nothing at all"


def test_four_charts_reach_the_reader_through_the_pages_own_boot():
    """R11: the value RENDERED on the live surface, not the source string in the repo."""
    live = _boot().get("r-live", {}).get("innerHTML", "")
    assert live.strip(), "the live-evidence rung rendered empty"
    segments = _svg_segments(live)
    assert len(segments) == 4, (
        f"{len(segments)} chart(s) reached the reader, not 4. The mint this discharges is "
        f"'one node filled to full depth, WITH CHARTS'; a node with three is not that.")


@pytest.mark.parametrize("index,name,floor", [
    (i, n, f) for i, (n, f) in enumerate(CHART_FLOORS)])
def test_each_chart_draws_its_own_geometry(index: int, name: str, floor: dict):
    """Per chart, not as a total: a total is satisfied by one chart drawing four times as much."""
    segments = _svg_segments(_boot().get("r-live", {}).get("innerHTML", ""))
    assert len(segments) > index, f"no {index + 1}th chart to grade"
    seg = segments[index]
    for mark, minimum in floor.items():
        found = seg.count("<" + mark)
        assert found >= minimum, (
            f"chart {index + 1} ({name}) drew {found} <{mark}>, floor {minimum} -- it has lost "
            f"its geometry, or the chart order changed and this control is now grading the "
            f"wrong subject")


def test_the_charts_are_not_all_the_same_chart():
    """Four svgs that are byte-identical would satisfy every count above and show one chart."""
    segments = _svg_segments(_boot().get("r-live", {}).get("innerHTML", ""))
    assert len(set(segments)) == len(segments), (
        "two charts rendered identical markup -- the loop is drawing one series four times")
