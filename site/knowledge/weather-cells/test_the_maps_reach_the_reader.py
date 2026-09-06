"""The weather-cell page's three visuals, driven through the page's OWN boot against the LIVE feed.

R11: done means the RENDERED value changed, not that the source string is in the repo. The failure
this exists to catch is the one a by-name harness passes straight through -- the page deploys, its
JSON 404s or drifts schema, the fetch chain dies, and every figure sits on its placeholder ellipsis
looking like a small number.

WHAT THE DIRECTOR ASKED THIS PAGE TO CONVEY, and therefore what these tests assert:

  1. **A cell is a climate class, not a region.** The map must actually show scattered same-colour
     patches, and the page must say so -- `test_the_class_map_is_DISCONTIGUOUS_and_the_page_says_so`
     measures the discontiguity rather than trusting the sentence.
  2. **The coverage curve**, so granularity reads as a price list. Both the shared partition and the
     per-driver lines must reach the reader, or the point inverts.
  3. **Half of Britain's land holds nobody**, which is why the wind map looks complicated.
"""
from __future__ import annotations

import collections
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
FEED_URL = "../../data/weather_cells.json"
FEED = SITE / "data" / "weather_cells.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _boot() -> dict:
    proc = subprocess.run(
        [NODE, str(LIVE_HARNESS), str(DOOR)],
        input=json.dumps({FEED_URL: json.loads(FEED.read_text())}),
        capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, proc.stderr[:800]
    return json.loads(proc.stdout)


def _html(out: dict, element: str) -> str:
    return out.get(element, {}).get("innerHTML", "")


def _text(out: dict, element: str) -> str:
    node = out.get(element, {})
    return node.get("textContent") or node.get("innerHTML") or ""


def test_the_page_boots_itself_against_the_live_feed():
    """No unresolved fetch and no script error. Live, an unresolved url is a 404, the promise chain
    dies, and every panel keeps its placeholder."""
    out = _boot()
    meta = out.get("_meta", {})

    assert not meta.get("static"), "the door reported itself static -- nothing drove"
    assert meta.get("scriptError") is None, f"boot raised: {meta.get('scriptError')}"
    assert not meta.get("unresolved"), (
        f"the page fetched urls nothing supplied: {meta.get('unresolved')}")
    assert meta.get("requested"), "the page fetched nothing at all"


def test_THREE_VISUALS_reach_the_reader():
    """Two maps and one curve. The director asked for three things conveyed and each has a picture;
    a page that rendered two of them is not this page."""
    out = _boot()

    for element in ("map-bands", "map-pop", "chart-curve"):
        html = _html(out, element)
        assert "<svg" in html, f"{element} rendered no svg"
        assert "<rect" in html or "<path" in html, f"{element} rendered an empty svg"


def test_the_class_map_is_DISCONTIGUOUS_and_the_page_SAYS_so():
    """THE THING THAT READS AS A BUG UNLESS IT IS SAID.

    A cell is a set of places that behave alike, not a territory, so the same colour appears in
    scattered patches. This measures it: a class map where every class were a single blob would
    have about as many runs as classes. Counting distinct fills against distinct runs is how the
    page's own claim is held to its own picture rather than to a sentence.
    """
    out = _boot()
    svg = _html(out, "map-bands")
    fills = re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg)

    assert len(set(fills)) >= 8, f"only {len(set(fills))} classes reached the map"
    assert len(fills) > 12 * len(set(fills)), (
        f"{len(fills)} runs for {len(set(fills))} classes -- the map is drawing contiguous blobs, "
        "so either the classes are regions after all or the render collapsed them")

    # BOTH SENTENCES, NOT EITHER. The first draft of this assertion was an `or` over two phrases,
    # and a mutation deleting one survived -- an `or` cannot require anything. One sentence says the
    # scattering is not a fault, the other says what a cell is instead; a reader needs both, because
    # "this is deliberate" without "here is what it means" still leaves them with a broken map.
    prose = DOOR.read_text(encoding="utf-8")
    assert "not a rendering fault" in prose, (
        "the page must TELL the reader the scattering is deliberate; without it the map reads as a "
        "bug and the reader learns the wrong thing")
    assert "not a contiguous territory" in prose, (
        "and must say what a cell IS instead -- a set of places that behave alike")


def test_the_EMPTY_PART_is_drawn_and_counted_OVER_GREAT_BRITAIN():
    """Nearly half of GB's land holds nobody, shown on the same grid rather than asserted.

    RE-KEYED 2026-09-06 FROM THE UK MASK TO GB, because the two are different denominators and the
    page was mixing them. The Met Office grid covers the United Kingdom; 14,911 of its land cells
    are outside Great Britain, have no household data, and were being counted as empty British land.
    "Half of Britain's land holds nobody" was 49.6% that way and is 47.1% over GB.
    """
    out = _boot()
    feed = json.loads(FEED.read_text())
    e = feed["emptiness"]

    assert e["land_cells"] + e["not_gb_land_cells"] == e["uk_mask_land_cells"], (
        "the GB subset and the non-GB remainder must account for the whole mask, or one of them is "
        "being double-counted")
    assert e["land_cells"] != e["uk_mask_land_cells"], (
        "if the two denominators are equal the non-GB land has stopped being separated and the "
        "emptiness figure is overstated again")
    assert abs(e["land_cells"] - e["published_gb_land_km2"]) / e["published_gb_land_km2"] < 0.03, (
        "the GB mask has drifted from the published GB land area")

    share = e["land_cells_with_households"] / e["land_cells"]
    assert 0.50 < share < 0.56, f"the occupied share of GB land moved to {share:.1%}"
    assert _text(out, "e-land").replace(",", "") == str(e["land_cells"]), (
        "the page must print the GB denominator, not the UK one")
    assert _text(out, "e-occ").replace(",", "") == str(e["land_cells_with_households"])


def test_the_DENSITY_MAP_IS_A_DENSITY_and_not_a_saturating_proportion():
    """THE DEFECT THE DIRECTOR NAMED, and the second wrong version of this panel.

    The first shaded a block by whether ANY of its twenty-five kilometres held a household -- 81%
    occupied against the 49.6% printed beside it. The second used the PROPORTION of a block's cells
    that were occupied, which saturates: a dense city and a sparse village both read as fully
    covered, and the map destroys the variation it exists to show.

    A proportion cannot exceed one, so its top band is reached by any block that is merely built-up.
    Households per km^2 spans four orders of magnitude, so THE TEST IS THAT THE BANDS DO TOO.
    """
    feed = json.loads(FEED.read_text())
    g = feed["grid"]

    labels = g["density_labels"]
    assert len(labels) >= 6, f"{len(labels)} density bands cannot show four orders of magnitude"
    assert "400" in labels[-1], (
        "the top band must be an absolute count per km2; a proportion has no such band")

    levels = collections.Counter()
    for row in g["density_rle"]:
        for part in (row.split(",") if row else []):
            count, value = part.split(":")
            levels[int(value)] += int(count)

    occupied = [lvl for lvl in levels if lvl > 0]
    assert len(occupied) >= 6, f"only {len(occupied)} occupied bands are drawn -- the ramp collapsed"
    for lvl in range(1, len(labels)):
        assert levels[lvl] > 100, (
            f"band {lvl} ({labels[lvl]}) holds {levels[lvl]} blocks; a band nearly nobody is in is "
            "a band the ramp is wasting")
    drawn = sum(levels[i] for i in range(0, len(labels)))
    assert levels[len(labels) - 1] < drawn / 3, (
        "the top band holds a third of all land -- it is saturating, which is the defect this "
        "panel was rebuilt to remove")


def test_NOT_GB_LAND_IS_DRAWN_AS_ITS_OWN_THING_and_the_page_says_why():
    """ABSENCE MUST NOT READ AS EMPTINESS -- and the defect a question about Scotland surfaced
    somewhere else entirely.

    Northern Ireland is 14,911 cells of the HadUK mask. ONSPD carries no British grid reference for
    its postcodes and this company's market is GB, so it arrives with no household data and, drawn
    as empty land, teaches a reader that Northern Ireland is depopulated.
    """
    out = _boot()
    feed = json.loads(FEED.read_text())

    levels = set()
    for row in feed["grid"]["density_rle"]:
        for part in (row.split(",") if row else []):
            levels.add(int(part.split(":")[1]))
    assert -2 in levels, "no land is marked as outside GB; the mask is being drawn as all-British"

    assert "#5b4a63" in _html(out, "map-pop"), "the non-GB land is not drawn in its own colour"
    assert "outside GB" in _html(out, "map-pop-src"), "the legend does not name it"

    prose = DOOR.read_text(encoding="utf-8")
    assert "Northern Ireland is not empty. It is not here." in prose, (
        "the page must say what the blank is, or a reader reads absence as emptiness")


def test_SCOTLANDS_BLANKS_ARE_ATTRIBUTED_and_the_figures_come_from_the_feed():
    """The director could not separate three candidates from outside: a lossier census join,
    genuinely empty terrain, or holes in the postcode-to-cell mapping. Two are honest and one is a
    defect, and they look identical on a map. The page states which, and states it with published
    numbers rather than typed ones."""
    out = _boot()
    feed = json.loads(FEED.read_text())
    bands = feed["emptiness"]["empty_share"]

    assert bands["highlands_and_north"] > bands["southern_scotland"] > bands["south_of_the_mersey"]
    assert bands["highlands_and_north"] > 0.7, (
        "if the north is not mostly empty, 'genuine terrain' is no longer the explanation and the "
        "page is asserting something the data stopped supporting")

    assert _text(out, "a-south") == f"{round(bands['southern_scotland'] * 100)}%"
    assert _text(out, "a-north") == f"{round(bands['highlands_and_north'] * 100)}%"

    # AND THE BANDS MUST BE OVER GB ONLY. A version computing them over the whole UK mask keeps the
    # ordering and the 70% threshold -- both assertions above survive it -- while quietly putting
    # Northern Ireland's 14,911 household-less cells into the northern numerators. Conservation is
    # what sees it: the bands must partition GB land and their empty counts must sum to GB's.
    e = feed["emptiness"]
    land = sum(v for k, v in bands.items() if k.endswith("_land_cells"))
    empty = sum(bands[k] * bands[k + "_land_cells"]
                for k in bands if not k.endswith("_land_cells"))
    assert abs(land - e["land_cells"]) < 0.01 * e["land_cells"], (
        f"the latitude bands cover {land:,} cells against {e['land_cells']:,} of GB land -- they "
        "are not partitioning the same land the figures count")
    assert abs(empty - (e["land_cells"] - e["land_cells_with_households"])) < 0.02 * e["land_cells"]

    prose = DOOR.read_text(encoding="utf-8")
    for probe in ("Lerwick", "Stornoway", "Braemar"):
        assert probe in prose, f"the towns refuting the missing-join theory are not named ({probe})"


def test_the_CURVE_carries_BOTH_the_shared_partition_and_the_per_driver_lines():
    """The whole point is the gap between them -- one grid serving three jobs against each driver
    held separately. A chart with only the solid line inverts the lesson into 'Britain needs a
    thousand cells'."""
    out = _boot()
    svg = _html(out, "chart-curve")

    solid = re.findall(r'<path d="[^"]+" fill="none" stroke="var\(--teal\)"', svg)
    dashed = re.findall(r'stroke-dasharray="4 3"', svg)

    assert len(solid) == 1, "the shared-partition line is missing"
    assert len(dashed) >= 3, f"{len(dashed)} per-driver lines drawn, expected one per driver"
    assert 'fill="var(--amber)"' in svg, "the 90/95/99 targets are not marked"


def test_the_HEADLINE_is_composed_from_the_feed_and_not_typed_into_the_markup():
    """A number typed into the page is a number that rots. The headline names the joint targets and
    the per-driver decision, and all three come from the feed -- so the sentence cannot disagree
    with the chart below it."""
    out = _boot()
    feed = json.loads(FEED.read_text())
    headline = _text(out, "c-headline")

    assert headline and "…" not in headline, "the headline kept its placeholder"

    # The headline quotes the ENDS of the curve and the per-driver decision -- the cheapest target,
    # the dearest, and the number that makes the point that the dearest is avoidable. The middle
    # target is deliberately not in it; a sentence naming all three reads as a list rather than a
    # contrast. Asserted as the ends specifically, so a headline that started quoting an
    # arbitrary interior point would fail rather than pass on "some number is present".
    targets = feed["coverage"]["joint_targets"]
    for target in (targets[0], targets[-1]):
        assert f"{target['cells']:,}" in headline or str(target["cells"]) in headline, (
            f"{target['cells']} cells is an END of the published curve and not in the headline")
    assert str(feed["coverage"]["decision_cells"]) in headline, (
        "the per-driver count is the point of the contrast and must be in the sentence")

    # AND THE ONLY PROOF THAT IT IS COMPOSED IS THAT IT MOVES. Checking the feed's numbers appear
    # in the sentence passes on a sentence with those numbers typed into it -- which is exactly what
    # a mutation of this test's first draft did. So the feed is CHANGED and the headline must
    # follow: R11's own rule, applied to a sentence rather than to a chart.
    altered = json.loads(FEED.read_text())
    for target in altered["coverage"]["joint_targets"]:
        target["cells"] = target["cells"] * 3 + 1
    altered["coverage"]["decision_cells"] = 7
    proc = subprocess.run(
        [NODE, str(LIVE_HARNESS), str(DOOR)], input=json.dumps({FEED_URL: altered}),
        capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, proc.stderr[:800]
    moved = _text(json.loads(proc.stdout), "c-headline")

    assert moved != headline, "the headline did not move when the feed did -- it is typed in"
    assert "7" in moved and str(altered["coverage"]["joint_targets"][-1]["cells"]) in moved.replace(",", "")


def test_a_MISSING_FEED_says_so_rather_than_rendering_a_small_number():
    """FAIL LOUD ON THE SURFACE. With nothing supplied the fetch rejects, and a page that quietly
    kept its ellipses would look like a page whose figures happened to be small."""
    proc = subprocess.run(
        [NODE, str(LIVE_HARNESS), str(DOOR)], input=json.dumps({}),
        capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, proc.stderr[:800]
    out = json.loads(proc.stdout)

    assert "did not load" in _text(out, "c-headline"), (
        "with no feed the page must say the figures are not live")
