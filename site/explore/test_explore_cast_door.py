"""The cast door: Explore's household cast, rendered by the page's own JavaScript from the real feed.

Done for a reader means the rendered value, not the source string (R11). This drives the page's
inline script under `site/_live_harness.mjs` with the published `explore_cast.json` and asserts what
a reader would meet: a tab for every slot, the three views of the opening moment each filled, and
an empty slot that says why rather than rendering blank. Nothing here pins a household or a figure;
those move with each run.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
INDEX = HERE / "index.html"
FEED = SITE / "data" / "explore_cast.json"
HARNESS = SITE / "_live_harness.mjs"


def _render(feed: dict, html_path: Path = INDEX) -> dict:
    proc = subprocess.run(["node", str(HARNESS), str(html_path)],
                          input=json.dumps({"../data/explore_cast.json": feed}),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[:500]
    return json.loads(proc.stdout)


@pytest.fixture(scope="module")
def feed() -> dict:
    assert FEED.is_file(), "the cast feed has never been generated (tools/generate_explore_cast.py)"
    return json.loads(FEED.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def out(feed) -> dict:
    if not HARNESS.is_file():
        pytest.skip("shared render harness not present")
    return _render(feed)


def _html(out, el):
    return (out.get(el) or {}).get("innerHTML") or ""


def test_the_cast_boots_without_a_script_error(out):
    assert not out["_meta"]["scriptErrors"], out["_meta"]["scriptErrors"]
    assert "../data/explore_cast.json" in out["_meta"]["requested"]


def test_every_slot_in_the_feed_is_offered_as_a_tab(out, feed):
    tabs = _html(out, "cast-tabs")
    assert tabs.count('role="tab"') == len(feed["slots"]) > 0
    for s in feed["slots"]:
        assert s["feature"] in tabs


def test_the_opening_moment_shows_all_three_views_filled(out, feed):
    stage = _html(out, "cast-stage")
    for side in ("customer", "company", "sim"):
        m = re.search(r'data-side="%s">(.*?)</div><div class="view"|data-side="%s">(.*)' % (side, side), stage, re.S)
        assert m, "the %s view is missing from the opening moment" % side
        body = re.sub(r"<[^>]+>", " ", m.group(1) or m.group(2))
        assert len(body.split()) > 12, "the %s view rendered almost nothing: %r" % (side, body[:200])
    first = next(s for s in feed["slots"] if s["filled"])
    assert first["moments"][first["opening"]]["title"] in stage, "the page did not open on the slot's telling moment"


def test_the_opening_tab_says_what_its_feature_is(out, feed):
    """The cold read asked what an "estimate trap" was. DEFECT: a glossary line in the feed that the
    page never renders, or a slot with none."""
    assert all(len(s.get("glossary") or "") > 20 for s in feed["slots"]), "a slot carries no glossary line"
    assert html.escape(feed["slots"][0]["glossary"], quote=False) in _html(out, "cast-stage")


def test_the_stamp_counts_the_slots_it_heads(out, feed):
    stamp = (out.get("cast-stamp") or {}).get("textContent", "")
    c = feed["coverage"]
    assert "%d of %d feature slots" % (c["filled"], c["of"]) in stamp, stamp


def test_an_empty_slot_says_why_on_the_page(tmp_path, feed):
    """Put an empty slot first, so the page opens on it: the reader must meet its reason."""
    if not HARNESS.is_file():
        pytest.skip("shared render harness not present")
    empty = {"id": "probe", "feature": "Probe feature", "rule": "a rule nobody meets", "filled": False,
             "reason": "No household in this run reached the probe stage, so the slot is empty."}
    f = dict(feed, slots=[empty] + [s for s in feed["slots"] if s["filled"]][:1])
    page = tmp_path / "index.html"
    page.write_text(INDEX.read_text(encoding="utf-8").replace(
        "slotIx = Math.max(0, f.slots.findIndex(function (s) { return s.filled; }));", "slotIx = 0;"), encoding="utf-8")
    stage = _html(_render(f, page), "cast-stage")
    assert empty["reason"] in stage and "empty in this run" in stage, stage[:300]


def test_a_missing_feed_says_so_rather_than_rendering_blank(tmp_path):
    if not HARNESS.is_file():
        pytest.skip("shared render harness not present")
    proc = subprocess.run(["node", str(HARNESS), str(INDEX)], input="{}", capture_output=True, text=True, timeout=120)
    stamp = json.loads(proc.stdout).get("cast-stamp", {}).get("textContent", "")
    assert "could not load" in stamp, stamp


def test_the_page_carries_the_cast_without_javascript(feed):
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r"<!--cast:static-->([\s\S]*?)<!--/cast:static-->", html)
    assert m and m.group(1).strip(), "the static first render is missing from the page"
    for s in feed["slots"]:
        assert s["feature"] in m.group(1), "%s is not in the page's static render" % s["feature"]
