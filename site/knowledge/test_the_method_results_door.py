"""What the method has shown reaches the reader under What we've learned (director's steer of 5 Nov,
item 2: "Method insight belongs there too ... That includes the 'we cannot tell' results and the
experiments that failed").

THE DEFECT THIS FIRES ON. The method's experiments were published one by one, deep in Capabilities,
and nothing a reader filtering for what we have learned could reach said what the method had found,
least of all where it found nothing or took a claim back. A results page can fail that in three
quiet ways: a status typed by hand that the source no longer supports; a source that goes missing and
its row silently drops, leaving only the flattering ones; a status vocabulary whose unflattering
branches can never be produced. So:

  * the committed feed is what `tools.method_results_feed` builds from the source feeds today;
  * every status the vocabulary names CAN be produced, each from its source field (one control over
    the whole partition, so a builder that only ever says "held" fails it);
  * "held" comes ONLY from a filed prediction: a source reaching a settled state with no prediction
    (a comparison no longer provisional, every reviewer measured) reads "measured", never "held"
    (cold read, 8 Nov: an earlier builder published those as "held" whatever the result said);
  * a missing source becomes a "we cannot tell" row naming why, never a dropped row;
  * the page's own JavaScript, driven against the feed, renders each row once with the feed's status;
  * the card sits under Building it and carries the insight layer the What we've learned filter reads.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from tools import method_results_feed as mrf

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
ROOT = SITE.parent
PAGE = HERE / "what-the-method-has-shown.html"
FEED_URL = "../data/method_results.json"
FEED = json.loads((ROOT / mrf.OUT).read_text(encoding="utf-8"))
SOURCES = ("value_arms", "dd_opening_arms", "judge_validation")


def _render(feed) -> dict:
    proc = subprocess.run(["node", str(SITE / "_live_harness.mjs"), str(PAGE)],
                          input=json.dumps({FEED_URL: feed} if feed is not None else {}),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[:600]
    out = json.loads(proc.stdout)
    assert out["_meta"]["scriptErrors"] == [], out["_meta"]["scriptErrors"]
    return out


def _root(tmp_path: Path, edit=None, drop=()) -> Path:
    (tmp_path / "site" / "data").mkdir(parents=True)
    for name in SOURCES:
        if name in drop:
            continue
        d = json.loads((SITE / "data" / f"{name}.json").read_text(encoding="utf-8"))
        if edit:
            edit(name, d)
        (tmp_path / "site" / "data" / f"{name}.json").write_text(json.dumps(d), encoding="utf-8")
    return tmp_path


def test_the_committed_feed_is_what_the_sources_build_today():
    assert FEED == mrf.build(), "site/data/method_results.json is stale: run python3 -m tools.method_results_feed --write"


def test_every_status_can_be_produced_from_its_source_field(tmp_path):
    def flip(name, d):
        if name == "dd_opening_arms":
            d["filed_prediction"]["verdict"] = "refuted"
        if name == "value_arms":
            d["provisional"] = False
        if name == "judge_validation":
            d["measurement_coverage"]["all_measured"] = True
    seen = {r["status"] for r in mrf.build(_root(tmp_path / "a"))["rows"]}
    seen |= {r["status"] for r in mrf.build(_root(tmp_path / "b", flip))["rows"]}
    assert seen == set(mrf.STATUSES), f"statuses never produced: {set(mrf.STATUSES) - seen}"


def test_MUTATION_held_needs_a_filed_prediction_a_settled_source_without_one_reads_measured(tmp_path):
    def settle(name, d):
        if name == "value_arms":
            d["provisional"] = False
        if name == "judge_validation":
            d["measurement_coverage"]["all_measured"] = True
    rows = {r["id"]: r["status"] for r in mrf.build(_root(tmp_path, settle))["rows"]}
    assert rows["pricing-arms"] == "measured" and rows["reviewers"] == "measured", rows


def test_every_status_is_counted_on_the_page_even_at_zero():
    text = _render(FEED)["mr-counts"]["textContent"]
    for s in mrf.STATUSES:
        assert f"{sum(r['status'] == s for r in FEED['rows'])} {s}" in text, (s, text)


def test_MUTATION_a_refuted_prediction_reads_did_not_hold(tmp_path):
    def refute(name, d):
        if name == "dd_opening_arms":
            d["filed_prediction"]["verdict"] = "refuted"
    row = next(r for r in mrf.build(_root(tmp_path, refute))["rows"] if r["id"] == "dd-opening")
    assert row["status"] == "did not hold"


def test_a_missing_source_is_a_row_that_says_we_cannot_tell_not_a_dropped_row(tmp_path):
    feed = mrf.build(_root(tmp_path, drop=SOURCES))
    assert {r["status"] for r in feed["rows"]} == {"we cannot tell"}
    assert len(feed["rows"]) == len(mrf.SOURCES)
    assert all("cannot be read here" in r["why_this_status"] for r in feed["rows"])


def test_every_row_renders_once_with_the_feeds_status():
    html = _render(FEED)["mr-rows"]["innerHTML"]
    assert html.count("<tr") == len(FEED["rows"]) + 1
    shown = re.findall(r'<td class="status s-([a-z-]+)">', html)
    assert shown == [r["status"].replace(" ", "-") for r in FEED["rows"]]


def test_MUTATION_a_row_dropped_from_the_feed_is_seen_on_the_page():
    short = dict(FEED, rows=FEED["rows"][:-1])
    assert _render(short)["mr-rows"]["innerHTML"].count("<tr") == len(FEED["rows"])


def test_a_missing_feed_says_so_rather_than_showing_an_empty_table():
    assert "could not be loaded" in _render(None)["mr-counts"]["textContent"]


def test_building_it_carries_the_card_where_what_weve_learned_can_find_it():
    index = (HERE / "index.html").read_text(encoding="utf-8")
    part = index[index.index('id="part-build"'):index.index("</section>", index.index('id="part-build"'))]
    card = re.search(r'<a class="card[^"]*" href="\./what-the-method-has-shown\.html"([^>]*)>', part)
    assert card, "Building it does not link to What the method has shown"
    assert 'data-layer="insight"' in card.group(1), "the card carries no insight layer, so What we've learned hides it"


def test_node_is_available_for_the_page_legs():
    assert shutil.which("node"), "the page legs need node to drive the page's own JavaScript"


def test_the_dd_claim_that_fell_is_a_withdrawn_row_with_its_words_and_reason():
    """Cold read, 8 Nov: the 3 Sep "about £200 closer" claim fell on 1 Oct and was not on the page.
    No prediction was filed for it, so it is withdrawn, not "did not hold"."""
    row = next(r for r in mrf.build()["rows"] if r["id"] == "dd-opening-withdrawn")
    claim = json.loads((SITE / "data" / "dd_opening_arms.json").read_text(encoding="utf-8"))["earlier_claims"][0]
    assert row["status"] == "withdrawn" and row["finding"] == claim["the_words"]
    assert row["why_this_status"] == claim["why"] and row["dated"] == claim["withdrawn_on"]


def test_MUTATION_a_dd_feed_that_forgets_its_earlier_claims_says_so_rather_than_dropping_the_row(tmp_path):
    def forget(name, d):
        if name == "dd_opening_arms":
            d.pop("earlier_claims", None)
    rows = {r["id"]: r for r in mrf.build(_root(tmp_path, forget))["rows"]}
    assert "dd-opening-withdrawn" not in rows
    assert rows["dd-opening-earlier"]["status"] == "we cannot tell", rows
