"""A page header may not claim data newer than the newest datum on the page (R10 class).

WHY THIS EXISTS (2026-08-12, DIRECTOR_OBSERVATION_PUBLISHED_SURFACE_NAV_AND_STAMPS item 2).
The director read the wholesale page and saw the header claim data 2026-07 while every
chart footer beneath it read "as of 2025-06-07". He did not assert a defect — "This may be
correct — different feeds, different vintages — or it may be the published-figure staleness
class. Confirm which, and say so on the page if the difference is legitimate."

CONFIRMED AS THE DEFECT, from the artefacts rather than from the page (R9, evidence before
narrative):
  * `site/data/knowledge_wholesale.json` carried `meta.data_freshness.as_of = "2026-07"`
    with `cadence: "monthly"` and the note "Data re-renders monthly".
  * All four charts on the page (`rungs.live_evidence.{price_series, merit_order, seasonal,
    negative_prices}`) carry `as_of = "2025-06-07"`.
  * The upstream extract those charts come from, `sim/scenario/data/real_ssp_daily_mean.json`,
    genuinely ends `2025-06-07` (`end_date`, 3501 days from 2015-11-07).
So the CHARTS were honest and the HEADER was not: it claimed a vintage thirteen months newer
than any datum on the page, and a monthly re-render that had not happened. Not two feeds with
two legitimate vintages — one overstatement. The stamp was corrected to 2025-06 rather than
the data being touched: Historical Ground Truth is a wall, so the claim moves to the data,
never the data to the claim.

R10, WHY THIS IS A TEST AND NOT JUST A FIX: "an absurdity-class defect may NOT be closed with
an instance fix. Closure requires extending the invariant library so the entire class fails
automatically." The class is *a header stamp that outruns its own page*. A swept census of
`site/data/*.json` on 2026-08-12 found exactly one instance (this one); `dashboard.json` was
consistent (header 2026-08, newest datum 2026-08). One instance today is precisely when the
rule is cheap to install.

FAIL-CLOSED (R15 killer pattern 2). The subject is DISCOVERED from the files, never listed
here — a hand-kept list of pages to check is the wrong-population defect, and would go quiet
on exactly the page added after it was written. A file with no header stamp or no datum
stamp contributes no comparison and is reported, so "found nothing to check" can never be
mistaken for "checked and found nothing": `test_the_sweep_actually_found_a_page_to_check`
is the non-emptiness floor that makes the green above mean something.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
SITE_DATA = PROJECT / "site" / "data"

#: A header stamp describes the page; a datum stamp describes one figure or series on it.
HEADER_KEYS = ("as_of", "data_as_of")
DATUM_KEYS = ("as_of", "data_as_of")
#: THREE CLOCKS, and only one of them is this control's subject (R14, "no figure without
#: its clock"). Naming the other two here is the point rather than an aside: a control that
#: swept every date-shaped field would fire on both of them, and a control tuned until it
#: stopped firing would have had its subject chosen by whatever made it green.
#:   * `as_of` / `data_as_of` — THE SUBJECT. A claim about the vintage of the data shown.
#:   * `last_verified` — when the CLAIMS were last reviewed. A page may legitimately be
#:     reviewed today and carry data from last year, as the wholesale page now does and
#:     says; `test_claim_review_is_allowed_to_be_newer_than_the_data` pins that.
#:   * `generated_at` — when the FILE was rendered. `site/data/dashboard.json` carries
#:     `meta.generated_at` in 2026-08 over a sim window ending 2025-06-07, and that is
#:     correct: a render stamp is not a freshness claim about the underlying series.
#:     Treating it as one would red the auto-processor's own output on every run.

_DATE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")


def _month(stamp: str) -> str:
    """Compare at month granularity — a header saying '2026-07' and a datum '2026-07-25'
    do not disagree, and demanding day-exactness would make the control fire on nothing
    but formatting."""
    return stamp[:7]


def _walk(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield f"{path}.{key}", key, value
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _walk(value, f"{path}[{i}]")


def _stamps(payload) -> tuple[dict[str, str], dict[str, str]]:
    """(header stamps, datum stamps) — split by whether they sit under `meta`."""
    header: dict[str, str] = {}
    datum: dict[str, str] = {}
    for path, key, value in _walk(payload):
        if not isinstance(value, str) or not _DATE.match(value):
            continue
        if key in HEADER_KEYS and path.startswith(".meta"):
            header[path] = value
        elif key in DATUM_KEYS and not path.startswith(".meta"):
            datum[path] = value
    return header, datum


def _pages() -> list[tuple[Path, dict[str, str], dict[str, str]]]:
    out = []
    for path in sorted(SITE_DATA.glob("*.json")):
        try:
            payload = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        header, datum = _stamps(payload)
        if header and datum:
            out.append((path, header, datum))
    return out


def test_the_sweep_actually_found_a_page_to_check():
    """NON-EMPTINESS FLOOR. Without it, a rename of `site/data/` or a change of stamp key
    would turn the control below into a vacuous pass — the fail-open shape."""
    pages = _pages()
    assert pages, (
        "no page under site/data carries both a header stamp and a datum stamp — the "
        "control below would pass vacuously"
    )


@pytest.mark.parametrize("path", [p.name for p, _, _ in _pages()])
def test_no_header_stamp_claims_data_newer_than_its_newest_datum(path: str):
    """THE CLASS. A header is a claim about the page under it, so it cannot outrun it."""
    page = next(p for p in _pages() if p[0].name == path)
    _, header, datum = page
    newest_datum = max(_month(v) for v in datum.values())
    overstated = {k: v for k, v in header.items() if _month(v) > newest_datum}

    assert not overstated, (
        f"{path}: header stamp(s) {overstated} claim data newer than the newest datum on "
        f"the page ({newest_datum}). Either the page's data is stale and the header is "
        f"advertising a refresh that did not happen, or a datum is missing its own stamp. "
        f"Datum stamps: {datum}"
    )


def test_the_wholesale_page_states_the_vintage_of_the_charts_it_shows():
    """The instance, pinned to the surface the director actually read, so the class control
    above cannot go green by the page losing its stamps altogether."""
    payload = json.loads((SITE_DATA / "knowledge_wholesale.json").read_text())
    header = payload["meta"]["data_freshness"]["as_of"]
    charts = payload["rungs"]["live_evidence"]
    series = {k: v["as_of"] for k, v in charts.items() if isinstance(v, dict) and "as_of" in v}

    assert len(series) >= 4, f"chart floor: only {len(series)} stamped series"
    assert _month(header) == max(_month(v) for v in series.values()), (
        f"the page header says {header} while its charts say {sorted(set(series.values()))}"
    )


def test_claim_review_is_allowed_to_be_newer_than_the_data():
    """ANTI-TAUTOLOGY / not-always-red: the control must NOT fire on the legitimate case it
    was carefully scoped around, or it would push the page toward deleting a true stamp."""
    payload = json.loads((SITE_DATA / "knowledge_wholesale.json").read_text())
    verified = payload["meta"]["claim_freshness"]["last_verified"]
    data_as_of = payload["meta"]["data_freshness"]["as_of"]

    assert _month(verified) > _month(data_as_of), (
        "this page is the fixture for the legitimate case — claims reviewed after the data "
        "was captured; if that stops being true, re-point this test rather than widening "
        "the control"
    )
    assert not [
        k for k, v in _stamps(payload)[0].items() if _month(v) > _month(data_as_of)
    ], "last_verified must not be read as a data-vintage header stamp"
