"""PB4 must reach the RENDERED page: whether a household shops is not how far price moves it.

THE DEFECT IT SERVES. The world has drawn engagement and price elasticity apart since 2026-09-05
(`simulation/household_segments.active_renewal_probability_for_customer` against
`simulation/population_draw.price_elasticity_for_customer`), and the atom's level was held at 1
for a month for one stated reason: "nothing renders PB4 to a reader". A separation nobody can see
is indistinguishable, from outside, from a world where a household that never switches simply
does not care what it pays -- which is the reading the director's P4 exists to refuse.

THE SUBJECT IS THE RENDERED DOM, driven through the door's own boot path with
`site/_live_harness.mjs`, for the reason `test_the_opening_direct_debit_comparison_reaches_the_reader.py`
gives: a feed carrying a figure proves nothing about whether a reader meets it.

R15 -- the mutations, each run and reverted:
  * delete the `engsep-headline` render -> `test_the_disengaged_but_price_sensitive_count_reaches_the_reader`
  * render the elasticity mean without its interval -> `test_no_sensitivity_reaches_the_reader_without_its_bound`
  * drop the payment-channel table -> `test_both_tables_reach_the_reader_with_every_group`
  * render the bill-shock branch as if established -> `test_the_bill_shock_gap_reaches_the_reader_while_it_is_absent`
  * drop the by-construction sentence -> `test_the_reader_is_told_the_zero_association_is_built_in`
The null rung is `test_an_unavailable_feed_renders_an_absence_and_never_a_zero`, green through all five.
"""
from __future__ import annotations

import html as html_lib
import json
import re
import subprocess
from pathlib import Path

import pytest
from test_the_published_bytes_reader import published_file, published_json

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/engagement_separation.json"
ARMS_REL = "site/data/value_arms.json"
GROWTH_REL = "site/data/book_growth.json"
CAPS_REL = "site/data/capabilities_door.json"
DD_ARMS_REL = "site/data/dd_opening_arms.json"

PANELS = ("engsep-headline", "engsep-archetype", "engsep-channel", "engsep-construction",
          "engsep-gap", "engsep-note")


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict) -> dict:
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    payload = {
        "../data/engagement_separation.json": feed,
        "../data/dd_opening_arms.json": published_json(DD_ARMS_REL),
        "../data/billing_accuracy.json": published_json("site/data/billing_accuracy.json"),
        "../data/value_arms.json": published_json(ARMS_REL),
        "../data/book_growth.json": published_json(GROWTH_REL),
        "../data/capabilities_door.json": published_json(CAPS_REL),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(published_file(DOOR_REL))],
        input=json.dumps(payload), capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        "the door asked for a feed this test did not supply ({})".format(meta.get("unresolved")))
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    rendered = {}
    for panel in PANELS:
        element = out.get(panel) or {}
        rendered[panel] = _text(element.get("innerHTML") or "") or _text(
            element.get("textContent") or "")
    return rendered


@pytest.fixture(scope="module")
def feed() -> dict:
    f = published_json(FEED_REL)
    if not f.get("available"):
        pytest.fail("the published engagement reading is unavailable ({}), so the door renders "
                    "nothing and this control cannot run".format(f.get("reason")))
    return f


@pytest.fixture(scope="module")
def live(feed) -> dict:
    return _render(feed)


def test_the_disengaged_but_price_sensitive_count_reaches_the_reader(feed, live):
    """DEFECT: the one consequence a reader can act on -- disengaged is not price-insensitive --
    stays in the feed."""
    d = feed["disengaged_but_price_sensitive"]
    assert d["above_book_mean_elasticity"] > 0, (
        "no disengaged household is more price-sensitive than average, so the headline's claim "
        "has no instance on this book and the section would be arguing from nothing")
    rendered = live["engsep-headline"]
    assert "{} disengaged".format(d["disengaged"]) in rendered
    assert str(d["above_book_mean_elasticity"]) in rendered
    a = feed["association"]
    assert "{:+.2f}".format(a["rho"]) in rendered, (
        "the rank correlation does not reach the reader beside the count it qualifies")


def test_no_sensitivity_reaches_the_reader_without_its_bound(feed, live):
    """DEFECT: a mean over 14 households published bare reads as a precision it has not earned."""
    for key, panel in (("by_archetype", "engsep-archetype"), ("by_channel", "engsep-channel")):
        rendered = live[panel]
        for g in feed[key]:
            low, high = g["elasticity"]["ci95"]
            assert "95% {:.2f} to {:.2f}".format(low, high) in rendered, (
                "a group's price sensitivity reaches the reader without its 95% interval")


def test_both_tables_reach_the_reader_with_every_group(feed, live):
    """DEFECT: the payment-channel table is the half a SUPPLIER can see; losing it leaves only the
    hidden archetype, which no company could act on."""
    assert set(PANELS) <= set(live)
    for key, panel in (("by_archetype", "engsep-archetype"), ("by_channel", "engsep-channel")):
        rendered = live[panel]
        assert feed[key], "the feed has no {} groups".format(key)
        for g in feed[key]:
            assert "{:.1f}%".format(100 * g["engagement_mean"]) in rendered, (
                "a group's chance of looking does not reach the reader ({})".format(key))
            assert "{} of {}".format(g["above_book_mean_elasticity"], g["n"]) in rendered


def test_the_bill_shock_gap_reaches_the_reader_while_it_is_absent(feed, live):
    """DEFECT: an unestablished amplitude rendered as nothing reads as 'a bill shock does not make
    a household look', which nothing establishes. Keyed to the FEED's own flag, so the day the
    amplitude is sourced the control asks for the figure instead of going red for being honest."""
    bs = feed["bill_shock_amplitude"]
    rendered = live["engsep-gap"]
    if bs["established"]:
        assert str(bs["value"]) in rendered
    else:
        assert "not known" in rendered and "2022" in rendered, (
            "the bill-shock gap does not reach the reader with its reason")


def test_the_reader_is_told_the_zero_association_is_built_in(live):
    """DEFECT: a correlation near zero, unexplained, reads as a finding about real households.
    It is a property of how this world draws them, and the page must say so."""
    assert "drawn independently" in live["engsep-construction"]


def test_the_note_names_the_commit_and_population(feed, live):
    assert str(feed["households"]) in live["engsep-note"]
    assert feed["published_from"]["commit"][:9] in live["engsep-note"]


def test_an_unavailable_feed_renders_an_absence_and_never_a_zero():
    rendered = _render({"available": False, "reason": "measured nothing"})
    assert "absent rather than empty" in rendered["engsep-note"]
    assert rendered["engsep-headline"] == ""
    assert not re.search(r"\b0\.0%", rendered["engsep-archetype"] + rendered["engsep-channel"])
