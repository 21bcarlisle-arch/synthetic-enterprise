"""The baseline comparison must reach the RENDERED page, not just the feed.

THE DEFECT IT SERVES. On 2026-08-28 a grep for `level_share_of_advantage`, `value_cycle_ab` and
`selection_gbp` across `site/`, `tools/generate_dashboard_data.py`, `saas/reporting/` and
`docs/reports/` returned one file -- `site/data/delivery.json` -- carrying a lane claim and not a
figure. The site published a profitable supplier at £153,245 net and said nothing about the
flat-rules run that matches it. The director's thesis contains the requirement in terms: *"there
has to be a BASELINE to beat -- the same book run by a supplier applying flat rules with no
per-customer view -- or 'it performed well' means nothing."*

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE JSON. This project's own
`test_published_caveat_reaches_the_reader.py` records the class: for a day the corrected sentence
was in the code, in the tree, and NOT in what a browser put on screen, and nothing was red,
because every assertion took an in-process object as its subject. A feed carrying `selection_gbp`
proves nothing about whether a reader meets it. So this drives the REAL door through its own boot
path with `site/_live_harness.mjs` and asserts on what the page actually rendered.

R15 -- the mutations, each run and reverted:
  * delete the `#arms-split` render -> `test_the_selection_leg_reaches_the_reader_as_a_negative` reds.
  * delete the `#arms-errorbar` render -> `test_the_error_bar_reaches_the_reader_before_the_number`
    reds (this is the one that matters most: the point estimate is 25x smaller than its own spread,
    so publishing it bare would be the misleading version of an honest result).
  * render the level arm's missing realised net as £0 ->
    `test_a_figure_the_run_never_computed_renders_as_an_absence_not_a_zero` reds.
  * render `is_the_published_supplier.statement` only when `same_supplier` is true ->
    `test_a_divergent_published_run_renders_as_a_divergence` reds.
  * drop the `Provisional` pill -> `test_the_reading_is_labelled_provisional_where_a_reader_sees_it`
    reds.
The null rung is `test_an_unavailable_feed_renders_an_absence_and_never_a_zero`: it must stay green
through all five, because every one of them is about what a reader meets, not about the feed.
"""
from __future__ import annotations

import copy
import html as html_lib
import json
import re
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "capabilities" / "index.html"
FEED = SITE / "data" / "value_arms.json"
GROWTH = SITE / "data" / "book_growth.json"
CAPS = SITE / "data" / "capabilities_door.json"

#: The elements this section renders into. All of them, so a section that renders half of itself
#: is a red rather than a silently thinner page.
PANELS = ("arms-headline", "arms-published", "arms-realised", "arms-split",
          "arms-errorbar", "arms-decisions", "arms-note")


def _text(fragment: str) -> str:
    """What a READER sees: tags stripped and entities decoded.

    Asserting against raw innerHTML is how a correct page gets reported red -- the door escapes
    everything through its own `esc()` before assigning, so `&quot;` and `&mdash;` are in the
    string and never on the screen.
    """
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict) -> dict:
    """Drive the real door with the given feed and return {id: rendered text a reader sees}."""
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    payload = {
        "../data/value_arms.json": feed,
        "../data/book_growth.json": json.loads(GROWTH.read_text(encoding="utf-8")),
        "../data/capabilities_door.json": json.loads(CAPS.read_text(encoding="utf-8")),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(DOOR)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        "the door asked for a feed this test did not supply ({}), so whatever it rendered is not "
        "what a browser would".format(meta.get("unresolved")))
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    rendered = {}
    for panel in PANELS:
        element = out.get(panel) or {}
        rendered[panel] = _text(element.get("innerHTML") or "") or _text(
            element.get("textContent") or "")
    return rendered


def _live_feed() -> dict:
    if not FEED.is_file():
        pytest.fail("site/data/value_arms.json is missing -- the published comparison has no "
                    "feed, reported as a failure and never skipped")
    return json.loads(FEED.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def live() -> dict:
    feed = _live_feed()
    if not feed.get("available"):
        pytest.fail("the published arm comparison is unavailable ({}), so the door renders no "
                    "comparison and this control cannot run".format(feed.get("reason")))
    return _render(feed)


def _gbp(value: float) -> str:
    return "£{:,}".format(round(value))


# ── the three arms, and the money ────────────────────────────────────────────────────────────

def test_the_baseline_and_the_arm_reach_the_rendered_page(live):
    feed = _live_feed()
    arms = {a["key"]: a for a in feed["realised"]["arms"]}
    rendered = live["arms-realised"]

    assert _gbp(arms["control"]["net_gbp"]) in rendered, (
        "the flat-rules baseline's net margin is not on the page a reader opens")
    assert _gbp(arms["value"]["net_gbp"]) in rendered, (
        "the per-customer arm's net margin is not on the page a reader opens")
    assert feed["realised"]["clock"] in rendered, "the table renders money without its clock (R14)"


def test_a_figure_the_run_never_computed_renders_as_an_absence_not_a_zero(live):
    """The level arm has no realised net -- the run's bridge never summed it. A rendered £0 there
    would read as "the level arm earned nothing", which is the opposite of what it did."""
    assert "not on this clock" in live["arms-realised"]
    assert "£0" not in live["arms-realised"], (
        "a figure the run never computed rendered as zero pounds")


def test_the_selection_leg_reaches_the_reader_as_a_negative(live):
    feed = _live_feed()
    selection = feed["provisioned"]["selection_gbp"]
    assert selection < 0, (
        "the selection leg is no longer negative -- a real change in the result, and the sentence "
        "the page renders about it must be re-read rather than this assertion flipped")

    rendered = live["arms-split"]
    assert "−£{:,}".format(abs(round(selection))) in rendered, (
        "the value of the per-customer choosing does not reach the reader with its sign")
    assert "the choosing is therefore worth" in rendered.lower()
    # The level arm is what makes the split readable at all: without its figure on the page the
    # negative is an unexplained assertion.
    level = [a for a in feed["provisioned"]["arms"] if a["key"] == "level"][0]
    assert _gbp(level["net_gbp"]) in rendered, "the level arm's own net margin is not rendered"


def test_the_price_level_is_quoted_to_the_penny(live):
    """£44.50/MWh against £2.00/MWh is the whole finding. Rounded to '£45 against £2' the page
    would be restating a number the arm did not charge."""
    feed = _live_feed()
    assert "£{:.2f}/MWh".format(feed["provisioned"]["level_gbp_per_mwh"]) in live["arms-split"]
    assert "£{:.2f}/MWh".format(feed["provisioned"]["control_gbp_per_mwh"]) in live["arms-split"]


def test_the_superseded_clock_is_declared_where_the_split_is_read(live):
    assert "settled-provisioned" in live["arms-split"]
    assert "superseded" in live["arms-split"].lower(), (
        "the split renders on a clock the run superseded inside itself and does not say so")


# ── the error bar, which is the reason the number cannot be quoted bare ──────────────────────

def test_the_error_bar_reaches_the_reader_before_the_number(live):
    feed = _live_feed()
    eb = feed["error_bar"]
    rendered = live["arms-errorbar"]

    assert rendered.strip(), (
        "the door rendered NOTHING where the error bar goes. The point estimate is {}x smaller "
        "than its own spread, so publishing it bare is the misleading version of an honest "
        "result".format(round(eb["spread_to_point_estimate_ratio"])))
    assert "−£{:,}".format(abs(round(eb["min_gbp"]))) in rendered
    assert _gbp(eb["max_gbp"]) in rendered
    assert _gbp(eb["stdev_gbp"]) in rendered, "the spread is described without its width"


def test_the_error_bar_says_the_instrument_cannot_resolve_it(live):
    feed = _live_feed()
    assert feed["error_bar"]["distinguishable_from_zero"] is False
    assert "cannot yet resolve" in live["arms-errorbar"], (
        "the page reports a spread wider than the effect without telling the reader what that "
        "means for the number above it")


# ── how few decisions it rests on ────────────────────────────────────────────────────────────

def test_the_decision_count_and_its_concentration_reach_the_reader(live):
    feed = _live_feed()
    dec = feed["decisions"]
    rendered = live["arms-decisions"]

    assert str(dec["value_arm_priced"]) in rendered
    assert str(dec["level_arm_priced"]) in rendered
    for account in dec["accounts_named_in_the_decision_sample"]:
        assert account in rendered, (
            "account {} is among the scored decisions and is not named on the page -- a "
            "per-customer result that hides how few customers it covers".format(account))


# ── the claim that could rot ─────────────────────────────────────────────────────────────────

def test_the_published_supplier_claim_reaches_the_reader(live):
    feed = _live_feed()
    pub = feed["realised"]["is_the_published_supplier"]
    assert pub["same_supplier"] is True, (
        "the published run and the baseline arm have diverged -- a real finding, not a test to "
        "relax")
    assert pub["statement"] in live["arms-published"], (
        "the sentence that connects this comparison to the figures the rest of the site "
        "publishes never reaches the page")


def test_a_divergent_published_run_renders_as_a_divergence():
    """THE LOAD-BEARING NULL. The day the site publishes a different run, the reader must meet the
    divergence -- not a page that quietly stops mentioning the relationship, and not one that goes
    on asserting an identity that has lapsed."""
    feed = copy.deepcopy(_live_feed())
    control = [a for a in feed["realised"]["arms"] if a["key"] == "control"][0]["net_gbp"]
    pub = feed["realised"]["is_the_published_supplier"]
    pub.update({
        "same_supplier": False,
        "published_run_net_gbp": control + 40_000.0,
        "gap_gbp": 40_000.0,
        "statement": ("The published run's net margin (£{:,.2f}) is NOT the baseline arm's "
                      "(£{:,.2f}) -- they differ by £40,000.00.".format(
                          control + 40_000.0, control)),
    })
    rendered = _render(feed)

    assert "is NOT the baseline arm's" in rendered["arms-published"]
    assert "40,000.00" in rendered["arms-published"], (
        "the divergence rendered without its size")
    assert "IS the baseline" not in rendered["arms-published"]


# ── the null rung, and the label ─────────────────────────────────────────────────────────────

def test_an_unavailable_feed_renders_an_absence_and_never_a_zero():
    """"The selection leg is worth nothing" and "we could not read the file" are the two readings
    this whole surface exists to keep apart. A zero renders them identically."""
    rendered = _render({"available": False,
                        "reason": "The three-arm A/B artefact could not be read."})

    note = rendered["arms-note"]
    assert "could not be read" in note, "an unavailable comparison rendered no reason"
    for panel in ("arms-realised", "arms-split", "arms-decisions", "arms-headline"):
        assert not rendered[panel].strip(), (
            "{} rendered content from a feed that carries no comparison".format(panel))
        assert "£0" not in rendered[panel]


def test_the_reading_is_labelled_provisional_where_a_reader_sees_it(live):
    """PROVISIONAL is what keeps this figure retractable, and therefore what puts publishing it
    inside this seat's own authority rather than among the four reserved classes."""
    feed = _live_feed()
    assert feed["provisional"] is True
    assert "Provisional" in live["arms-headline"], (
        "the reading is labelled provisional in the feed and not on the page")
    assert "PROVISIONAL" in live["arms-note"]
    assert "not a cue to tune" in live["arms-note"], (
        "the page publishes a losing arm without the R12 sentence that says losing is a "
        "permitted answer")
