"""The L2 sheets one tap down from the front-door diagram (tools/model_on_a_page_sheets.py;
director 9 Oct and 24 Oct)."""
from __future__ import annotations

import re
import sys

import pytest

from tools import model_on_a_page_picture as mp
from tools import model_on_a_page_sheets as ms

sys.path.insert(0, str(ms.SITE))
from test_the_front_door_diagram_carries_no_statistics import statistics_in  # noqa: E402

from tests.tools.test_model_on_a_page_picture import hrefs, words  # noqa: E402

SHEETS = mp.load_spec().get("sheets") or {}


def test_there_is_a_sheet_to_check():
    assert "world" in SHEETS, "the world sheet (the steer's first) is gone from the canon page"


@pytest.mark.parametrize("band", sorted(SHEETS))
def test_the_served_sheet_says_what_the_canon_page_says(band):
    built = ms.build()
    for path, body in built.items():
        if band not in path.as_posix():
            continue
        served = path.read_text(encoding="utf-8")
        if path.suffix == ".svg":
            assert words(served) == words(body), "{} differs from the canon page; run {}".format(
                path.relative_to(ms.ROOT), "tools/model_on_a_page_sheets.py")
        else:
            strip = lambda s: re.sub(r'alt="[^"]*"', "", s)  # noqa: E731 -- alt carries map states
            assert strip(served) == strip(body)


@pytest.mark.parametrize("band", sorted(SHEETS))
def test_a_sheet_carries_no_statistic(band):
    svg = (ms.SITE / "assets" / "model-{}.svg".format(band)).read_text(encoding="utf-8")
    assert statistics_in("\n".join(words(svg))) == []


@pytest.mark.parametrize("band", sorted(SHEETS))
def test_the_door_and_the_picture_open_the_sheet(band):
    door = (ms.SITE / "index.html").read_text(encoding="utf-8")
    assert 'href="./model/{}/"'.format(band) in door, "nothing on the door's HTML routes to the sheet"
    assert "./model/{}/".format(band) in hrefs(mp.OUT.read_text(encoding="utf-8"))


@pytest.mark.parametrize("band", sorted(SHEETS))
def test_every_link_on_a_sheet_lands_on_a_served_page(band):
    page = ms.SITE / "model" / band / "index.html"
    for href in re.findall(r'href="([^"#]+)', page.read_text(encoding="utf-8")):
        target = (page.parent / href).resolve()
        assert (target / "index.html").is_file() or target.is_file(), "{} -> {}".format(band, href)


def test_a_row_short_of_a_cell_is_refused_by_name():
    sheet = dict(SHEETS["world"])
    sheet["rows"] = [sheet["rows"][0][:2]]
    with pytest.raises(mp.PictureSpecError, match="row 1 of 'The world' has 2 cells for 3 columns"):
        ms.render_svg(sheet, {})


def test_a_list_sheet_draws_no_arrows_and_a_chain_sheet_does():
    sheet = dict(SHEETS["world"])
    assert "marker-end" in ms.render_svg(sheet, {})
    sheet["arrows"] = False
    assert "marker-end" not in ms.render_svg(sheet, {})
