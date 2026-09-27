"""A chart's rendered stamp is never older than its own page's data date.

THE DEFECT, found by the director by eye more than once (DIRECTOR_OBSERVATION_PUBLISHED_SURFACE_
NAV_AND_STAMPS_2026-08-12 item 2; named again in the 2026-09-27 trial instruction as "chart stamps
reading a year older than their own page's data date"). The wholesale page's header said data
2026-07 while every chart under it said "as of 2025-06-07".

WHY THE FEED CONTROL BESIDE IT DOES NOT CLOSE THIS. `tests/tools/test_site_freshness_stamps.py`
reads `site/data/*.json`, not the page, and compares the header against the NEWEST datum (`max`):
one chart left a year behind beside a current one is invisible to it, and so is a page whose
script renders a stamp from a different field than the one that test walks. This file reads what
the READER is shown -- every published door driven by its own JavaScript over the published
(index) bytes -- and compares every chart caption, one by one, with the page's own date.

THE VOCABULARY IS THE PAGE'S, and it is the limit of this control, stated rather than discovered:
the page date is the `Data: <date>` text of an element classed `stamp`, and a chart stamp is a
`chart-src` caption that says `as of <date>` (a caption that claims no vintage is a legend). On 2026-09-27 exactly one door renders either
(`/knowledge/electricity-wholesale/`: four captions, `2025-06-07`, under `Data: 2025-06`). A chart
captioned in other words is not in the subject; `test_the_population_is_not_empty` keeps the
subject from silently becoming nothing, and a caption that renders with no date, or captions on
a page with no date, FAIL rather than drop out.

Month granularity, as the feed control uses: `2025-06` and `2025-06-07` do not disagree, and a
day-exact rule would fire on formatting alone (`test_MUTATION_a_same_month_chart_does_not_fire`).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from test_every_door_element_a_reader_meets import _door_path, _drive  # noqa: E402
from test_the_browser_reading import published_site  # noqa: E402

_DATE = r"(\d{4}-\d{2}(?:-\d{2})?)"
_PAGE_DATE = re.compile(r'class="[^"]*\bstamp\b[^"]*"[^>]*>\s*Data:\s*' + _DATE)
_CAPTION = re.compile(r'<div class="chart-src">(.*?)</div>', re.S)
_AS_OF = re.compile(r"\bas of\s+" + _DATE)
#: The page's script SOURCE is not what a reader sees; its templates hold `as of '+esc(x)+'`.
_SCRIPT = re.compile(r"<script\b.*?</script\s*>", re.S | re.I)

#: The fixture page for the mutations: the one door that renders both stamps today.
_WHOLESALE_DOOR = "knowledge/electricity-wholesale/index.html"
_WHOLESALE_FEED = "data/knowledge_wholesale.json"


def stamp_problems(html: str) -> tuple[str | None, list[str], list[str]]:
    """(page date, chart stamps, problems) read from one door's RENDERED html."""
    page_dates = _PAGE_DATE.findall(html)
    captions = _CAPTION.findall(html)
    stamps, problems = [], []
    # A caption that does not say "as of" is a legend, not a stamp (weather-cells' is one), so
    # it is outside the subject. A caption that SAYS "as of" and gives no readable date is inside
    # it, and fails.
    claiming = [c for c in captions if re.search(r"\bas of\b", c)]
    for caption in claiming:
        found = _AS_OF.findall(caption)
        if not found:
            problems.append(f"a chart caption says 'as of' with no readable date: {caption.strip()[:120]!r}")
        stamps += found
    if claiming and not page_dates:
        problems.append(
            f"{len(claiming)} chart stamp(s) render but the page renders no 'Data:' date, so "
            "nothing says whether they are current -- fail closed rather than drop out"
        )
    page = max(page_dates, default=None)
    if page is not None:
        for stamp in stamps:
            if stamp[:7] < page[:7]:
                problems.append(
                    f"a chart is stamped 'as of {stamp}' under a page that says 'Data: {page}' -- "
                    "the chart is older than the page claims; restamp the page to the data, or "
                    "refresh the chart"
                )
    return page, stamps, problems


def _shown(door: Path, rendered: dict) -> str:
    """What the reader is shown: the served markup without its scripts, plus every element the
    door's own script wrote."""
    served = _SCRIPT.sub(" ", door.read_text(encoding="utf-8"))
    return served + " ".join(c.get("innerHTML", "") for c in rendered.values())


def _render_all(docroot: Path) -> dict[str, str]:
    out = {}
    for door in sorted(docroot.glob("**/index.html")):
        rendered = _drive(door, docroot)
        rendered.pop("_meta", None)
        out[_door_path(door, docroot)] = _shown(door, rendered)
    return out


@pytest.fixture(scope="module")
def rendered():
    if shutil.which("node") is None:
        pytest.skip("node is not available to drive the doors")
    with published_site() as (_base, docroot):
        doors = _render_all(docroot)
    assert doors, "no published door was found, so this door has no subject"
    return doors


def _render_one_with_feed_edit(edit) -> str:
    """Drive the wholesale door over a published extract whose feed `edit` has changed. The
    extract is a temp directory, never the working tree."""
    if shutil.which("node") is None:
        pytest.skip("node is not available to drive the doors")
    with published_site() as (_base, docroot):
        feed = docroot / _WHOLESALE_FEED
        payload = json.loads(feed.read_text())
        edit(payload)
        feed.write_text(json.dumps(payload))
        door = docroot / _WHOLESALE_DOOR
        out = _drive(door, docroot)
        out.pop("_meta", None)
        return _shown(door, out)


def test_no_chart_stamp_is_older_than_its_page(rendered):
    failures = {path: stamp_problems(html)[2] for path, html in rendered.items()}
    failures = {p: f for p, f in failures.items() if f}
    assert not failures, json.dumps(failures, indent=1)


def test_the_population_is_not_empty(rendered):
    """ANTI-VACUITY: at least one door must render both a page date and a chart stamp, or the
    green above is a green over nothing."""
    graded = {p: stamp_problems(h)[:2] for p, h in rendered.items()}
    graded = {p: g for p, g in graded.items() if g[0] and g[1]}
    assert graded, "no published door renders both a 'Data:' date and a chart 'as of' stamp"


def test_MUTATION_a_chart_a_year_older_than_its_page_fires():
    def backdate(p):
        series = p["rungs"]["live_evidence"]["price_series"]
        series["as_of"] = f"{int(series['as_of'][:4]) - 1}{series['as_of'][4:]}"

    problems = stamp_problems(_render_one_with_feed_edit(backdate))[2]
    assert any("older than the page" in p for p in problems), problems


def test_MUTATION_the_historical_case_a_page_date_ahead_of_its_charts_fires():
    """The instance the director read on 2026-08-12: header 2026-07 over charts of 2025-06-07."""
    def overstate(p):
        p["meta"]["data_freshness"]["as_of"] = "2026-07"

    problems = stamp_problems(_render_one_with_feed_edit(overstate))[2]
    assert sum("older than the page" in p for p in problems) >= 4, problems


def test_MUTATION_a_same_month_chart_does_not_fire():
    """NOT-ALWAYS-RED: a day-level difference inside the page's month is not the defect."""
    def same_month(p):
        series = p["rungs"]["live_evidence"]["price_series"]
        series["as_of"] = series["as_of"][:7] + "-01"

    page, stamps, problems = stamp_problems(_render_one_with_feed_edit(same_month))
    assert page and stamps and not problems, (page, stamps, problems)


def test_MUTATION_a_caption_with_no_date_fails_closed():
    assert stamp_problems('<div class="chart-src">p/MWh &middot; as of undefined</div>')[2]
    assert not stamp_problems('<div class="chart-src">Solid: one partition. Dashed: each alone</div>')[2], (
        "a legend caption that claims no vintage is not a stamp"
    )
    assert stamp_problems('<div class="chart-src">as of 2025-06-07</div>')[2], (
        "captions under a page with no 'Data:' date must fail, not drop out"
    )


def test_MUTATION_a_chart_one_month_behind_its_page_fires():
    """The rule is month-granular, not year-granular: a comparison that only read the year let a
    chart a month behind its page through, and survived every other test here until this one."""
    def one_month_back(p):
        series = p["rungs"]["live_evidence"]["merit_order"]
        y, m = int(series["as_of"][:4]), int(series["as_of"][5:7])
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
        series["as_of"] = f"{y:04d}-{m:02d}-28"

    problems = stamp_problems(_render_one_with_feed_edit(one_month_back))[2]
    assert any("older than the page" in p for p in problems), problems
