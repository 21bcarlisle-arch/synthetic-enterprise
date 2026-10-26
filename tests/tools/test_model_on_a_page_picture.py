"""The front-door diagram is generated from the canon page's words and the map's levels
(tools/model_on_a_page_picture.py; director 27 Jul and 24 Oct)."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from tools import model_on_a_page_picture as mp

SVG_NS = "{http://www.w3.org/2000/svg}"
# a state the map decides: a lone marker glyph, the engine's "<glyph> <stage word>", or a sheet's chip word
_STATE = re.compile(r"^[._~]$|(?:^|\s)[._~] (?:done|in build|not started)$|^(?:LIVE|BUILDING|PLANNED)$")


def words(svg: str) -> list[str]:
    out = []
    for t in ET.fromstring(svg).iter(SVG_NS + "text"):
        s = _STATE.sub("", "".join(t.itertext()).strip())
        if s:
            out.append(s)
    return out


def hrefs(svg: str) -> set[str]:
    return {a.get("href") for a in ET.fromstring(svg).iter(SVG_NS + "a")}


def test_the_served_picture_says_what_the_canon_page_says():
    # Words only: the markers follow the map, which other lanes move between publishes.
    served = mp.OUT.read_text(encoding="utf-8")
    assert words(served) == words(mp.build()), (
        "site/assets/model-on-a-page.svg no longer says what '## The picture' in "
        "THE_MODEL_ON_A_PAGE.md says. Edit the canon page, then run tools/model_on_a_page_picture.py; "
        "never edit the SVG by hand (27 Jul).")


def test_a_word_changed_on_the_canon_page_changes_the_picture(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text(mp.DOC.read_text(encoding="utf-8").replace(
        "Discovery loop", "Inference loop"), encoding="utf-8")
    assert "Inference loop" in mp.build(doc=doc) and "Discovery loop" not in mp.build(doc=doc)


def test_every_state_the_map_can_give_reaches_the_picture():
    spec = mp.load_spec()
    item = spec["now"]["items"][0]
    item["atoms"] = ["A", "B"]
    glyph = lambda lv: re.search(  # noqa: E731
        r'<text x="64" y="1664"[^>]*>(.)</text>', mp.render(spec, lv, mp.SHEETS)).group(1)
    assert glyph({"A": {"current": 3, "target": 3}, "B": {"current": 2, "target": 2}}) == "."
    assert glyph({"A": {"current": 3, "target": 3}, "B": {"current": 1, "target": 2}}) == "_"
    assert glyph({"A": {"current": 0, "target": 3}, "B": {"current": 0, "target": 2}}) == "~"
    # an atom the map does not hold can never read as done
    assert glyph({"A": {"current": 3, "target": 3}}) != "."


def test_a_line_that_names_no_atom_is_refused_by_name():
    spec = mp.load_spec()
    spec["now"]["items"][0]["atoms"] = []
    with pytest.raises(mp.PictureSpecError, match="names no atom"):
        mp.render(spec, {}, mp.SHEETS)


def test_a_box_given_more_lines_than_room_is_refused_not_clipped():
    spec = mp.load_spec()
    spec["world"]["boxes"][0]["lines"].append("a fourth line")
    with pytest.raises(mp.PictureSpecError, match="The real record has 4 lines and room for 3"):
        mp.render(spec, {}, mp.SHEETS)


def test_a_band_links_to_its_sheet_only_when_the_sheet_exists(tmp_path):
    spec, levels = mp.load_spec(), {}
    assert "<a href" not in mp.render(spec, levels, tmp_path)
    (tmp_path / "world").mkdir()
    (tmp_path / "world" / "index.html").write_text("x")
    svg = mp.render(spec, levels, tmp_path)
    assert svg.count("<a href") == 1 and 'href="./model/world/"' in svg


def test_the_front_door_picture_shows_plain_names_and_no_canon_code():
    """Steer of 26 Oct: the home diagram showed internal codes (M1, G1, R5, R6 ...). The picture
    carries plain names; the codes stay in the canon page, the alt text and the sheets. KEYED TO THE
    PROPERTY: the canon page still writes codes (the first assert), and none reaches the picture.
    MUTATION: drop the CANON_CODE pass from build() -> the second assert reds."""
    assert mp.CANON_CODE.search(mp.DOC.read_text(encoding="utf-8")), (
        "the canon page carries no bracketed code, so this control has nothing to hold back")
    text = " ".join(t.text or "" for t in ET.fromstring(mp.build()).iter() if t.tag.endswith("text"))
    assert not mp.CANON_CODE.search(text), mp.CANON_CODE.search(text)
