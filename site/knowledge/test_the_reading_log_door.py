"""The reading log's published side reaches the reader (director's steer of 5 Nov, items 2 and 3:
the log's published side sits under "Building it").

THE DEFECT THIS FIRES ON. The log lived only in `docs/institutional/reading_log.md`, so a reader of
the site could not see what we had read, what we rejected or why. And a published copy can drift
from its one home: a row appended to the log and missing from the page, or a page linking a row to
a map panel that does not exist. So:

  * the committed feed is what `tools.reading_log_feed` builds from the log today;
  * the page's own JavaScript, driven against that feed, renders every row once;
  * every row the feed places on the map links to a panel the map page actually has, and the
    resolver can return each of its four kinds (a resolver that placed everything, or nothing,
    would pass the other legs);
  * the Building it part links to the page.
"""
from __future__ import annotations

import html as htmllib
import json
import re
import subprocess
from pathlib import Path

import pytest

from tools import reading_log_feed as rlf

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
ROOT = SITE.parent
PAGE = HERE / "reading-log.html"
FEED_URL = "../data/reading_log.json"
FEED = json.loads((ROOT / rlf.OUT).read_text(encoding="utf-8"))


def _render(feed) -> dict:
    proc = subprocess.run(["node", str(SITE / "_live_harness.mjs"), str(PAGE)],
                          input=json.dumps({FEED_URL: feed} if feed is not None else {}),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[:600]
    out = json.loads(proc.stdout)
    assert out["_meta"]["scriptErrors"] == [], out["_meta"]["scriptErrors"]
    return out


def test_the_committed_feed_is_what_the_log_builds_today():
    assert FEED == rlf.build(), "site/data/reading_log.json is stale: run python3 -m tools.reading_log_feed --write"


def test_every_row_renders_once_and_the_count_is_the_logs():
    out = _render(FEED)
    html = out["log-rows"]["innerHTML"]
    assert html.count("<tr>") == len(FEED["rows"]) + 1
    shown = [htmllib.unescape(re.sub(r"<[^>]+>", "", c)) for c in re.findall(r'<td class="src">(.*?)</td>', html)]
    assert shown == [re.sub(r"[*`]", "", r["source"]) for r in FEED["rows"]]
    assert out["log-counts"]["textContent"].startswith(f"{len(FEED['rows'])} sources read, {FEED['rejected']} of them rejected")


def test_MUTATION_a_row_dropped_from_the_feed_is_seen_on_the_page():
    short = dict(FEED, rows=FEED["rows"][:-1])
    assert _render(short)["log-rows"]["innerHTML"].count("<tr>") == len(FEED["rows"])


def test_a_missing_feed_says_so_rather_than_showing_an_empty_table():
    out = _render(None)
    assert "could not be loaded" in out["log-counts"]["textContent"]


def test_every_map_link_lands_on_a_panel_the_map_has():
    mapped = (SITE / "model" / "map" / "index.html").read_text(encoding="utf-8")
    html = _render(FEED)["log-rows"]["innerHTML"]
    anchors = {r["placed"]["anchor"] for r in FEED["rows"] if r["placed"]["anchor"]}
    assert anchors, "no row links to the map, so the page is not placed under Building it"
    for a in anchors:
        assert f'id="{a}"' in mapped, a
        assert f'href="../model/map/#{a}"' in html, a


def test_the_resolver_can_return_each_of_its_four_kinds():
    resolve = rlf.resolver()
    # The unplaced leg needs a label no register can hold, not a practice the register lacks today:
    # "Independent review" stood here until 8 Nov, when the register took it in and this went red.
    got = {resolve(c)["kind"] for c in ("The commit gate", "Observability", "No practice by this name", "—")}
    assert got == {"concept", "step", "unplaced", "none"}, got
    assert resolve("commit gate")["anchor"] == "c-build.gate"  # an altLabel resolves to its concept


def test_MUTATION_a_row_of_the_wrong_width_is_refused_by_name():
    bad = "| Read | Source | Claim | Evidence | Verdict | Done | Concept |\n|---|---|---|---|---|---|---|\n| a | b | c |\n"
    with pytest.raises(rlf.ReadingLogUnreadable, match="3 cells"):
        rlf.rows(bad)


def test_building_it_links_to_the_reading_log():
    index = (HERE / "index.html").read_text(encoding="utf-8")
    part = index[index.index('id="part-build"'):index.index("</section>", index.index('id="part-build"'))]
    assert 'href="./reading-log.html"' in part
