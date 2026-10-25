"""The Knowledge index renders the 25 Oct pack check counts from their feed, and fails closed."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
INDEX = HERE / "index.html"
LIVE_HARNESS = SITE / "_live_harness.mjs"
CENSUS_URL = "../data/pack_verification_census.json"
CENSUS = json.loads((SITE / "data" / "pack_verification_census.json").read_text(encoding="utf-8"))


def _render(feeds: dict) -> dict:
    proc = subprocess.run(["node", str(LIVE_HARNESS), str(INDEX)], input=json.dumps(feeds),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[:600]
    return json.loads(proc.stdout)


def test_the_rendered_totals_are_the_feeds():
    t = CENSUS["total"]
    text = _render({CENSUS_URL: CENSUS})["census-total"]["textContent"]
    for phrase in (f"{t['packs']} packs carrying {t['items']} flags", f"{t['confirmed']} confirmed",
                   f"{t['corrected']} corrected", f"{t['open']} still open"):
        assert phrase in text, f"{phrase!r} not in {text!r}"


def test_MUTATION_a_checked_pack_changes_the_rendered_row():
    c = json.loads(json.dumps(CENSUS))
    r = c["packs"][0]
    r.update(tally_recorded=True, confirmed=77, partly_confirmed=0, open=4)
    html = _render({CENSUS_URL: c})["census-table"]["innerHTML"]
    assert html.count("<tr>") == len(c["packs"]) + 1
    assert '<td class="n">77</td>' in html


def test_a_page_with_no_count_is_said_not_rendered_as_zero():
    c = json.loads(json.dumps(CENSUS))
    c["packs"][0].update(tally_recorded=False, confirmed=0, corrected=0, unpublished=0)
    html = _render({CENSUS_URL: c})["census-table"]["innerHTML"]
    assert "The page states no count" in html


def test_MUTATION_FAIL_CLOSED_an_unreachable_census_says_so():
    out = _render({})
    assert "could not be loaded" in out["census-total"]["textContent"]
    assert not (out.get("census-table") or {}).get("innerHTML", "").strip()
