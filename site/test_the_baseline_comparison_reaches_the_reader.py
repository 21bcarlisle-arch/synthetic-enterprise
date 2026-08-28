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
          "arms-errorbar", "arms-decisions", "arms-method", "arms-note")


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


def test_a_figure_the_run_never_computed_renders_as_an_absence_not_a_zero():
    """A net margin the run never computed must render as an absence. A £0 there would read as
    "this arm earned nothing", which is the opposite of "we could not put it on this clock".

    ITS SUBJECT IS A CONSTRUCTED FEED, NOT THE LIVE ONE (2026-08-28). This used to assert the
    absence against the live page, which was sound only while the level arm's realised net was
    genuinely unrecoverable. On 2026-08-28 the A/B tool was repaired to put all three arms on the
    realised clock, the figure arrived, and this control's own subject stopped existing -- the
    shape where a page consolidation deletes the only instance a control was watching and the
    control is quietly dropped with it. Re-aimed rather than deleted: it now drives the door with
    the level arm's figure REMOVED, so it tests the door's absence path directly and keeps
    testing it however the live run comes out. The live page's positive case is asserted in
    `test_every_arm_that_has_a_figure_renders_it`.
    """
    feed = copy.deepcopy(_live_feed())
    level = [a for a in feed["realised"]["arms"] if a["key"] == "level"][0]
    level["net_gbp"] = None
    level["advantage_gbp"] = None
    level["absent_reason"] = "the run never summed it"
    rendered = _render(feed)

    assert "not on this clock" in rendered["arms-realised"], (
        "a net margin the run never computed did not render as an absence")
    assert "£0" not in rendered["arms-realised"], (
        "a figure the run never computed rendered as zero pounds")


def test_every_arm_that_has_a_figure_renders_it(live):
    """The positive half: an arm the run DID score reaches the reader as its own number.

    Written when the level arm's realised net became recoverable (2026-08-28). Until then the
    page told a reader the baseline existed and beat us, and could not tell them by how much --
    the hole this whole comparison exists to fill, sitting in the middle of it.
    """
    feed = _live_feed()
    rendered = live["arms-realised"]
    scored = [a for a in feed["realised"]["arms"] if a["net_gbp"] is not None]
    assert scored, "no arm on the realised clock carries a figure at all"
    for arm in scored:
        assert _gbp(arm["net_gbp"]) in rendered, (
            "the {} arm has a realised net margin of {} in the feed and it is not on the page a "
            "reader opens".format(arm["key"], _gbp(arm["net_gbp"])))


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
    """The PROPERTY, not the sentence: whichever case the reading is in, the page must tell the
    reader that nothing here resolves the selection effect.

    This control used to pin the literal string "cannot yet resolve", which was the wording of
    ONE of the two cases. On 2026-08-28 the point estimate moved outside the band its spread was
    measured over, the generator's reading correctly changed to say so, and this test reddened on
    a page that had become MORE honest, not less. A control keyed to a sentence goes red when the
    sentence improves and stays green when the claim rots -- exactly backwards.
    """
    feed = _live_feed()
    eb = feed["error_bar"]
    assert eb["distinguishable_from_zero"] is False
    rendered = live["arms-errorbar"]
    inside = eb["point_estimate_inside_the_measured_band"]
    if inside:
        assert "cannot yet resolve" in rendered, (
            "the page reports a spread wider than the effect without telling the reader what "
            "that means for the number above it")
    else:
        assert "nothing here resolves the selection effect" in rendered, (
            "the estimate has left the range its spread was measured over and the page does not "
            "tell the reader that this resolves nothing")


def test_an_error_bar_older_than_its_figure_says_so_on_the_page(live):
    """R11 on a caveat rather than a number, and the caveat is DERIVED.

    The noise floor was measured on 2026-08-27; the point estimate was re-taken on 2026-08-28
    after `simulation/competitor_reference.py` gave the market the ability to DEFEND. A spread
    measured where nothing could react is not a confidence interval on a figure measured where
    it can, and a reader shown the two side by side without that sentence is being told the
    number is bounded when it is not.

    The feed derives the caveat by comparing the two artefacts' own `generated_at` stamps, so
    this control keeps working for the NEXT world change rather than pinning this one.

    MUTATION: drop the `staleness_caveat` render from `site/capabilities/index.html` and this
    reds; make the two artefacts contemporaneous and the caveat correctly disappears, which is
    why the assertion is conditional on the feed rather than unconditional on the page.
    """
    caveat = _live_feed()["error_bar"].get("staleness_caveat")
    if not caveat:
        pytest.skip("the error bar and the point estimate come from the same run -- nothing to say")
    rendered = live["arms-errorbar"]
    assert "OLDER THAN THE FIGURE IT BOUNDS" in rendered, (
        "the published error bar predates the figure it bounds and the page does not say so")
    assert "DEFEND" in rendered, (
        "the page says the error bar is old without naming what changed between the two runs")


def test_the_coverage_denominator_is_renewals_and_not_accounts(live):
    """THE DENOMINATOR IS THE CLAIM. Until 2026-08-28 this panel read "25 renewals ... out of a
    book of 210 settled accounts" -- a renewal numerator over an account denominator. It reads as
    roughly a tenth of the book; the arm in fact priced 2.07% of the renewals the world offered.
    The artefact had carried `renewal_funnel.value_arm.renewals_the_world_offered` all along and
    nothing read it.

    Fires on: publishing the account count as the coverage denominator again, or dropping the
    renewal count and the percentage from the rendered sentence.
    """
    dec = _live_feed()["decisions"]
    offered = dec.get("renewals_the_world_offered")
    assert isinstance(offered, int) and offered > dec["value_arm_priced"], (
        "the feed carries no renewals-offered denominator, so the coverage claim cannot be made "
        "honestly: {!r}".format(offered))
    rendered = live["arms-decisions"]
    assert str(offered) in rendered, (
        "the page does not say how many renewals the world offered, so a reader cannot see what "
        "share of them the arm priced")
    share = dec["priced_share_of_renewals_offered"]
    assert "{:.2f}%".format(share * 100) in rendered, (
        "the coverage percentage does not reach the reader")
    # Teeth: the account count is still published (concentration is a real and separate fact),
    # but it must not be the thing the priced count is divided by.
    assert dec["book_accounts_settled"] != offered


def test_the_page_says_the_small_surface_is_design_as_well_as_plumbing(live):
    """The note used to attribute the whole small surface to ONE eligibility guard and conclude
    it was "small by PLUMBING, not by design". The funnel says 755 of the 1,184 unpriced renewals
    are deliberate scope -- term 0 and gas -- and 429 are the product-label gap.

    Fires on: reverting to a single-cause attribution, which understates the arm's designed scope
    by roughly two to one.
    """
    dec = _live_feed()["decisions"]
    exclusions = dec.get("why_the_rest_were_not_priced") or []
    assert len(exclusions) >= 3, (
        "fewer than three exclusion stages reached the feed, so the attribution below is being "
        "made on a population that has emptied: {}".format(exclusions))
    assert any(e["by_design"] for e in exclusions) and any(not e["by_design"] for e in exclusions), (
        "every exclusion is classified the same way -- the split this note exists to state has "
        "collapsed")
    rendered = live["arms-decisions"]
    assert "small by design AND by plumbing" in rendered, (
        "the page attributes the small decision surface to one cause again")


def test_the_method_number_never_appears_without_its_interval(live):
    """A48 ON THE PAGE, FAIL-CLOSED. The director's mission says the enterprise value is the
    METHOD; the figures above it are the evidence. But the first live reading was 0.6136 on twelve
    decisions, a value a random signal reaches about one run in six, and this surface had already
    carried three other pairs of correct numbers whose relationship was not a quantity.

    So the rule is: no interval, no number. Whichever branch the feed is in, the page must never
    show the concordance without the range a random signal produces.

    Fires on: rendering the point estimate in the withheld branch, or dropping the interval from
    the available one.
    """
    msk = _live_feed().get("method_skill") or {}
    rendered = live["arms-method"]
    assert rendered.strip(), "the method block rendered nothing at all"

    if msk.get("available"):
        assert "{:.3f}".format(msk["concordance"]) in rendered
        assert "{:.3f}".format(msk["null_95_low"]) in rendered, (
            "the method number is on the page without the range a random signal produces")
        assert "{:.3f}".format(msk["null_95_high"]) in rendered
        assert str(msk["decisions_scored"]) in rendered, (
            "the figure is published without saying how few decisions it rests on")
    else:
        assert "withheld" in rendered.lower(), (
            "the method figure is unavailable and the page does not say so")
        # THE TEETH. The withheld branch knows the number and must not print it.
        withheld = msk.get("concordance_withheld")
        if withheld is not None:
            assert "{:.3f}".format(withheld) not in rendered, (
                "the withheld branch printed the very number it exists to withhold")
            assert "{:.4f}".format(withheld) not in rendered


def test_the_available_branch_renders_the_number_WITH_its_interval():
    """The other half of the fail-closed rule, and it cannot wait for a run to exercise it.

    No artefact carries `method_skill.null_spread` yet, so the live feed is in the WITHHELD branch
    and the AVAILABLE branch would ship untested — a render nobody has seen, waiting for the first
    run that carries the field. Driven here against a synthetic feed with the real 2026-08-28
    values, through the door's own JavaScript.

    Fires on: rendering the concordance without the interval, or without how few decisions it
    rests on.
    """
    feed = dict(_live_feed())
    feed["method_skill"] = {
        "available": True, "concordance": 0.6136363636, "null_point": 0.5,
        "null_95_low": 0.2835, "null_95_high": 0.7165, "p_two_sided": 0.3037,
        "inside_the_null": True, "decisions_scored": 12, "accounts": 5,
        "churn_auc_for_contrast": 0.4652777,
        "what_it_is": "Does the arm's own per-customer price rank the value JOINTLY created?",
        "reading": "The observed value sits INSIDE the interval a random signal produces.",
    }
    rendered = _render(feed)["arms-method"]
    assert "0.614" in rendered, "the method number does not reach the reader"
    assert "0.283" in rendered and "0.717" in rendered, (
        "the number is on the page without the range a random signal produces")
    assert "12 decisions on 5 accounts" in rendered, (
        "the figure is published without saying how few decisions it rests on")
    assert "INSIDE the interval" in rendered, (
        "the page shows the number and the interval without telling the reader what their "
        "relationship means")
    # The contrast that makes the pair a reading rather than two figures.
    assert "0.465" in rendered


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
