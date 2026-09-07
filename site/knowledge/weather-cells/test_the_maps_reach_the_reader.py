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


def test_the_CLASS_MAP_HAS_NO_HOLES_IN_GB_LAND():
    """THE WHITE GAPS THE DIRECTOR SAW -- in the Highlands, mid-Wales and around Manchester -- and
    they were a RENDERING HOLE, not missing data.

    1,353 blocks of GB land carried no class at all, because the clustering ran over the 121,668
    INHABITED cells while HadUK has a winter temperature for all 245,077. Uninhabited Britain had a
    perfectly good reading and no class. The classes are still FITTED on households; they are now
    APPLIED to all GB land, which is what a supplier with a customer anywhere must do anyway.

    HELD BY COVERAGE, NOT BY EQUALITY. A 5 km block is classed if any of its twenty-five kilometres
    is GB land, so block area necessarily EXCEEDS land area -- every coastal block is part sea. The
    test is that it exceeds it by a coastline's worth and not by a third of the country, and that
    it never falls short, which is what a hole looks like.
    """
    feed = json.loads(FEED.read_text())

    def levels(rows):
        out = collections.Counter()
        for row in rows:
            for part in (row.split(",") if row else []):
                count, value = part.split(":")
                out[int(value)] += int(count)
        return out

    classed = levels(feed["grid"]["bands_rle"])
    blocks = sum(v for k, v in classed.items() if k >= 0)
    land_km2 = sum(v for k, v in levels(feed["density"]["rle"]).items() if k >= 0)

    assert classed[-2] > 0, "non-GB land must stay unclassed, or the map implies cells covering it"

    ratio = blocks * 25 / land_km2
    assert ratio >= 1.0, (
        f"the class map covers {blocks * 25:,} km2 against {land_km2:,} km2 of GB land -- it is "
        "SHORT, which is what the white holes were")
    assert ratio < 1.25, (
        f"the class map overshoots GB land by {ratio - 1:.0%}; partial coastal blocks explain about "
        "a tenth, and more than that means it is classing sea or non-GB land")


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

    # KEYED TO THE PROPERTY, not to today's figure -- this number has now moved twice, from 49.6%
    # (counting Northern Ireland as empty Britain) to 52.9% to 76.1% (placing households on the
    # address record rather than on postcode centroids). A pinned range would red on the third
    # honest correction just as it did on the second.
    share = e["land_cells_with_households"] / e["land_cells"]
    addr = e["addresses"]["share_with_any_address"]
    assert 0.5 < share < addr, (
        f"households are placed in {share:.1%} of GB land against {addr:.1%} that holds any address "
        "at all. Above the address share is impossible -- a household needs an address -- and far "
        "below it is the centroid undercount coming back.")
    assert e["land_cells_with_households"] <= e["addresses"]["cells_with_any_address"], (
        "more cells hold a household than hold an address, which cannot be true")
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
    dn = feed["density"]

    assert dn["block_km"] == 1, (
        "the density map must be drawn at the resolution its caption counts at. At 5 km one hamlet "
        "colours a whole block, so almost all of Britain reads as covered beside a figure saying "
        "nearly half of it is empty -- the picture and the number measuring different things and "
        "the page presenting them as the same.")

    labels = dn["labels"]
    assert len(labels) >= 5, f"{len(labels)} density bands cannot show four orders of magnitude"
    assert "400" in labels[-1], (
        "the top band must be an absolute count per km2; a proportion has no such band")

    levels = collections.Counter()
    for row in dn["rle"]:
        for part in (row.split(",") if row else []):
            count, value = part.split(":")
            levels[int(value)] += int(count)

    occupied = [lvl for lvl in levels if lvl > 0]
    assert len(occupied) >= 5, f"only {len(occupied)} occupied bands are drawn -- the ramp collapsed"
    for lvl in range(1, len(labels)):
        assert levels[lvl] > 1000, (
            f"band {lvl} ({labels[lvl]}) holds {levels[lvl]} cells; a band nearly nobody is in is "
            "a band the ramp is wasting")
    drawn = sum(levels[i] for i in range(0, len(labels)))
    assert levels[len(labels) - 1] < drawn / 3, (
        "the top band holds a third of all land -- it is saturating, which is the defect this "
        "panel was rebuilt to remove")

    # AND THE COLOURED SHARE MUST BE THE CAPTIONED SHARE. This is the whole repair: at 1 km a
    # coloured pixel IS an occupied square kilometre, so counting the pixels must reproduce the
    # figure printed beside them. At 5 km it did not, and nothing said so.
    e = feed["emptiness"]
    coloured = sum(levels[i] for i in range(1, len(labels)))
    assert coloured == e["land_cells_with_households"], (
        f"the map colours {coloured:,} cells and the caption claims "
        f"{e['land_cells_with_households']:,} -- the picture and the number are measuring "
        "different things again")
    assert coloured + levels[0] == e["land_cells"], (
        "the map's GB land does not add up to the GB land the figures count")


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
    for row in feed["density"]["rle"]:
        for part in (row.split(",") if row else []):
            levels.add(int(part.split(":")[1]))
    assert -2 in levels, "no land is marked as outside GB; the mask is being drawn as all-British"

    # and the CLASS map must not class it either -- a class map covering Northern Ireland implies a
    # cell set that covers it, and the derivation is GB-only
    class_levels = set()
    for row in feed["grid"]["bands_rle"]:
        for part in (row.split(",") if row else []):
            class_levels.add(int(part.split(":")[1]))
    assert -2 in class_levels, "the class map is drawing non-GB land as though it had a GB class"

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

    # SCOTLAND AGAINST ENGLAND, not the Highlands against southern Scotland. The strict ordering
    # asserted here until 2026-09-07 held under two placements and broke under the third, and the
    # break is a RESULT rather than a regression: placing households on the addresses themselves
    # makes the Highlands (32.5%) marginally LESS empty than southern Scotland (34.5%), because
    # Highland glens carry scattered crofts along every road while the Southern Uplands are
    # forestry block and grouse moor. What the page claims -- that Scotland's blanks are terrain
    # rather than a broken join -- rests on Scotland being far emptier than England, and that is
    # what is asserted.
    scotland = max(bands["highlands_and_north"], bands["southern_scotland"])
    england = max(bands["south_of_the_mersey"], bands["northern_england"])
    assert scotland > 2 * england, (
        f"Scotland is {scotland:.1%} empty against {england:.1%} in England -- too close together "
        "for 'genuine terrain' to be the explanation the page gives")
    assert bands["south_of_the_mersey"] < bands["northern_england"] < scotland, (
        "the south-to-north gradient the page describes has gone")

    # WITHIN ONE POINT, NOT EQUAL. Python's round() is banker's and JavaScript's Math.round() is
    # half-up, so 0.505 renders as 50 here and 51 there -- a cross-language rounding difference, not
    # a figure that failed to come from the feed. The claim being held is provenance: the sentence
    # must track the published number, which a one-point tolerance still enforces and a stale
    # hand-typed figure would still fail.
    for element, key in (("a-south", "southern_scotland"), ("a-north", "highlands_and_north"),
                         ("a-lowland", "south_of_the_mersey")):
        rendered = int(_text(out, element).rstrip("%"))
        assert abs(rendered - bands[key] * 100) <= 1, (
            f"{element} renders {rendered}% against a published {bands[key]:.1%}")

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
