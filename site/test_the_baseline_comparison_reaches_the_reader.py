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
DD_ARMS = SITE / "data" / "dd_opening_arms.json"

#: The elements this section renders into. All of them, so a section that renders half of itself
#: is a red rather than a silently thinner page.
PANELS = ("arms-headline", "arms-published", "arms-realised", "arms-household", "arms-split",
          "arms-errorbar", "arms-decisions", "arms-method", "arms-inference", "arms-note",
          "arms-market", "arms-sample", "arms-departure", "arms-svt-belief")


def _text(fragment: str) -> str:
    """What a READER sees: tags stripped and entities decoded.

    Asserting against raw innerHTML is how a correct page gets reported red -- the door escapes
    everything through its own `esc()` before assigning, so `&quot;` and `&mdash;` are in the
    string and never on the screen.
    """
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict, growth: dict | None = None) -> dict:
    """Drive the real door with the given feed and return {id: rendered text a reader sees}.

    `growth` overrides the book-growth feed. It is a parameter rather than a constant because the
    sample bound below is authored by THAT producer and read by this page, so the only way to
    prove the page reads it -- rather than printing a number that happens to match -- is to drive
    the door with a different one.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    payload = {
        "../data/value_arms.json": feed,
        # The door gained a FOURTH feed on 2026-09-03 (the opening direct-debit
        # comparison). Same reason as the line above: the harness rejects a url the
        # caller did not supply, so every feed the door fetches has to be supplied here
        # or this control reds on a page that is fine.
        "../data/dd_opening_arms.json": json.loads(DD_ARMS.read_text(encoding="utf-8")),
        "../data/book_growth.json": (
            json.loads(GROWTH.read_text(encoding="utf-8")) if growth is None else growth),
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


def test_the_selection_leg_reaches_the_reader_with_its_own_sign(live):
    """WHICHEVER SIGN IT IS, and that restatement is the repair (2026-08-29).

    This pinned `selection < 0` -- the state on the day it was written -- and its own failure
    message said the page's sentence should be re-read rather than the assertion flipped. On
    2026-08-29 the run came back at +£453 and it fired, which is the control working. Pinning the
    new sign would just re-arm the same trap: what is checked now is that the figure reaches a
    reader carrying whatever sign it has, and that the panel says why that size is not a
    direction. A control keyed to the property survives the result moving; this one did not.
    """
    feed = _live_feed()
    selection = feed["provisioned"]["selection_gbp"]
    rendered = live["arms-split"]

    signed = ("−£{:,}".format(abs(round(selection))) if selection < 0
              else "+£{:,}".format(round(selection)))
    assert signed in rendered, (
        "the value of the per-customer choosing ({}) does not reach the reader with its "
        "sign".format(signed))
    assert "the choosing is therefore worth" in rendered.lower()
    assert "not a direction" in rendered, (
        "the superseded panel publishes a signed selection figure with no seed spread behind it "
        "and does not say so, so the size reads as a finding about which way it went")
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


def test_the_page_says_WHICH_FIGURE_the_error_bar_is_a_bar_on(live):
    """A band and a headline figure on one page, and nothing saying they are the same quantity.

    THE DEFECT, at the door. The generator bounded the SUPERSEDED clock's selection leg while the
    headline three paragraphs up stated the REALISED one -- £453 against £1,816, £1,362 apart --
    and the page rendered "about 6× the estimate itself" over a band a reader could only assume
    belonged to the number they had just read. Fixed in the generator; this is the leg that keeps
    the fix visible to the person the page is for, because a correct feed rendered without its
    subject is the same page to them.

    KEYED TO THE PROPERTY. It reconciles what the page says the bar bounds against the split the
    headline states, at whatever values the run produces. Fires on: dropping the
    `bounds_figure_clock` render, or the two drifting back onto different clocks.
    """
    feed = _live_feed()
    eb, split = feed["error_bar"], feed["realised"]["split"]
    if not eb.get("bounds_figure_clock"):
        pytest.skip("this run's split is not on the spread's clock -- the bar bounds nothing, and "
                    "`test_a_split_on_another_clock_leaves_the_bar_with_NOTHING_TO_PLACE` owns it")
    rendered = live["arms-errorbar"]

    assert eb["bounds_figure_gbp"] == split["selection_gbp"], (
        "the feed's error bar bounds £{!r} and the headline states £{!r}".format(
            eb["bounds_figure_gbp"], split["selection_gbp"]))
    assert _gbp(eb["bounds_figure_gbp"]) in rendered, (
        "the page publishes a band without the figure it is a band ON, so a reader cannot tell "
        "which of the two selection legs on this page it belongs to")
    assert eb["bounds_figure_clock"] in rendered, (
        "the bounded figure is rendered without its clock, on a page that carries two")


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

    THE SKIP IS ON THE VALUE AND THE ASSERT IS ON THE KEY, and until 2026-09-03 it was one
    `.get()` doing both. `_staleness_caveat`'s caller emits `staleness_caveat` UNCONDITIONALLY,
    `None` when the two runs are contemporaneous -- so the producer already distinguishes "there
    is nothing to say" from "nobody asked". `.get()` collapsed them, and a producer that stopped
    emitting the key at all would have skipped this control silently and forever, which is the
    exact fail-open shape this suite exists to refuse. Skipping on a VALUE the producer
    guarantees is legitimate; skipping on a KEY's absence is a control that cannot fail.
    """
    error_bar = _live_feed()["error_bar"]
    assert "staleness_caveat" in error_bar, (
        "the feed's error_bar carries no `staleness_caveat` key at all. The producer emits it "
        "unconditionally (None when there is nothing to say), so its ABSENCE means the producer "
        "changed -- and this control must red for that, never skip past it")
    caveat = error_bar["staleness_caveat"]
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


def test_the_page_never_attributes_the_small_surface_to_one_cause(live):
    """The note used to attribute the whole small surface to ONE eligibility guard.

    RE-KEYED 2026-09-04, and the re-keying is the finding. This asserted the literal sentence
    "small by design AND by plumbing" -- a two-bucket attribution over a three-class subject. On
    the run it was green against, the "plumbing" bucket was 1,223 SVT households and 12 arm
    declines: not one line of plumbing. The control was pinned to an ANSWER, so it stayed green
    while the answer went false, and it would have gone RED the day the page started telling the
    truth. That is the exact backwards shape CLAUDE.md names.

    Keyed now to the property: every non-empty exclusion class the feed reports must reach the
    reader with its own count, and the page must never state one cause for the whole remainder.

    Fires on: collapsing the classes back to a single attribution, and on a class reaching the
    feed but not the rendered page.
    """
    dec = _live_feed()["decisions"]
    exclusions = dec.get("why_the_rest_were_not_priced") or []
    assert len(exclusions) >= 3, (
        "fewer than three exclusion stages reached the feed, so the attribution below is being "
        "made on a population that has emptied: {}".format(exclusions))
    classes = {e["exclusion_class"] for e in exclusions}
    assert len(classes) >= 2, (
        "every exclusion is in one class -- the split this note exists to state has collapsed: "
        "{}".format(sorted(classes)))
    rendered = live["arms-decisions"]
    # EVERY CLASS, WITH ITS COUNT, IN FRONT OF THE READER. A class that reaches the feed and stops
    # at the JSON is the failure this page has shipped twice.
    by_class = {}
    for e in exclusions:
        by_class[e["exclusion_class"]] = by_class.get(e["exclusion_class"], 0) + e["count"]
    for name, count in by_class.items():
        assert "{:,}".format(count) in rendered, (
            "the {} class holds {:,} renewals and that count never reaches the rendered page"
            .format(name, count))
    # AND THE EVIDENCE UNDER THE LARGEST DROP. The product gate's cause was wrong for five days
    # and nothing on the page let a reader check it, because the per-product counts stopped at
    # the feed. They must be rendered.
    gate = [e for e in exclusions if e["stage"] == "product_not_upliftable"]
    if gate and gate[0].get("by_tariff_type"):
        for product in gate[0]["by_tariff_type"]:
            assert product["tariff_type"] in rendered, (
                "the product gate refused {:,} renewals on `{}` and the page names the cause "
                "without ever naming the product".format(
                    product["count"], product["tariff_type"]))


# ── the bound: what the world could do about either arm ──────────────────────────────────────

def test_the_comparison_never_reaches_the_reader_unbounded(live):
    """THE PROPERTY: whatever the world can do, a reader meets it, and meets it as a bound.

    Deliberately NOT keyed to today's sentence. The director's C2 correction reads "a market that
    could not react to either" and was HALF FALSE within half an hour of being written, when the
    competitor's defence leg landed. A control pinned to that wording would now be defending a
    stale claim; a control pinned to "the comparison carries the bound the world's own probe
    reports" survives the ceiling leg landing too.

    Fires on: deleting the `#arms-market` render, or letting it fall through to empty when the
    feed carries no `market_reaction` block.
    """
    rendered = live["arms-market"]
    assert rendered.strip(), (
        "the comparison rendered with no statement of what the world could do about either arm -- "
        "an unbounded internal comparison is the reading this block exists to prevent")
    assert "internal" in rendered.lower(), (
        "the rendered bound never tells the reader the comparison is an internal one between two "
        "of our own policies: {}".format(rendered))


def test_the_rendered_bound_matches_the_world_the_probe_actually_found(live):
    """The bound must agree with the probe, leg by leg, on the surface a reader receives.

    This is what stops the sentence drifting off the world in EITHER direction: apologising for a
    world that has stopped needing it, or claiming a competitive pressure that does not exist.

    Fires on: hard-coding either clause on the page, or the feed and the page disagreeing.
    """
    reaction = _live_feed().get("market_reaction") or {}
    if not reaction.get("available"):
        pytest.fail("the world's competitive reference could not be probed for this publish ({}) "
                    "-- reported as a failure, never skipped, because an unavailable probe is an "
                    "unavailable control (R15)".format(reaction.get("reason")))
    rendered = live["arms-market"].lower()

    if reaction["defends"]:
        assert "does defend" in rendered, (
            "the probe found a market that defends and the page does not say so -- the bound is "
            "now overstating the gap: {}".format(rendered))
    else:
        assert "nothing" in rendered and "defend" in rendered, (
            "the probe found nothing defending and the page does not say so: {}".format(rendered))

    if reaction["contests_the_ceiling"]:
        assert "ceiling is contested" in rendered, (
            "the probe found a contested ceiling and the page still says over-pricing is free")
    else:
        assert "no competitive consequence" in rendered, (
            "the probe found nothing contesting the ceiling, so the page must say over-pricing "
            "carries no competitive consequence: {}".format(rendered))


def test_MUTATION_a_world_that_cannot_react_renders_the_directors_own_bound():
    """The killer mutation, and it is the world's own no-op point.

    `competitor_reference` documents CHASE=0 as the setting that reproduces the world exactly as it
    stood before the module -- so a feed built from a market that cannot react must render C2's
    sentence, not today's half-of-one. If this renders the same text as the live feed, the page is
    printing a constant and the control above is a tautology (R15's PASS-branch shape).
    """
    from tools.generate_value_arms_data import _reaction_sentence

    dead = _reaction_sentence(defends=False, contests=False, decay=None)
    feed = copy.deepcopy(_live_feed())
    feed["market_reaction"] = {"available": True, "defends": False,
                               "contests_the_ceiling": False, "statement": dead}
    rendered = _render(feed)["arms-market"]

    assert "could not move" in rendered, (
        "a world that cannot react rendered something else entirely: {}".format(rendered))
    assert "does defend" not in rendered, (
        "the page rendered the defence clause for a world with no defence in it -- the sentence "
        "is not coming from the feed")
    assert rendered != _render(_live_feed())["arms-market"], (
        "the page renders the SAME bound for a reacting and a non-reacting world, so it is "
        "printing a constant and reads nothing from the probe")


def test_MUTATION_a_missing_reaction_block_still_bounds_the_comparison():
    """FAIL-OPEN, the shape R15 names first. A feed with no `market_reaction` at all must still
    leave the reader told the comparison is internal -- silence there reads exactly like a
    comparison that never needed a bound."""
    feed = copy.deepcopy(_live_feed())
    feed.pop("market_reaction", None)
    rendered = _render(feed)["arms-market"]

    assert rendered.strip(), "a feed with no reaction block rendered nothing at all"
    assert "internal" in rendered.lower(), (
        "a missing bound fell through to a comparison with no qualification on it: {}".format(
            rendered))


# ── the account count above is a sample size, not the business ───────────────────────────────
#
# THE DEFECT THESE SERVE. `#arms-decisions` renders "the book is N settled accounts" and every
# per-account figure on this page is computed over that N. N is not the business: the settlement
# engine takes a uniform sample of what the campaign won -- 90 of 505 on the 2026-08-29 record, a
# rate of 0.1789 -- so a reader dividing by it has divided by a sample. The growth curve higher up
# the same page already says so about ITSELF; nothing said it about the arms.


def _growth_feed() -> dict:
    if not GROWTH.is_file():
        pytest.fail("site/data/book_growth.json is missing -- the sample bound has no source, "
                    "reported as a failure and never skipped (R15)")
    return json.loads(GROWTH.read_text(encoding="utf-8"))


def test_the_book_on_this_page_is_named_as_a_sample_of_the_business(live):
    """THE PROPERTY: a reader who meets the account count also meets what it is a count OF.

    Fires on: deleting the `#arms-sample` render, or letting it fall through to empty.
    """
    growth = _growth_feed()
    rate = growth.get("settlement_sample_rate")
    if rate is None:
        pytest.fail("the campaign record carries no settlement_sample_rate, so this control's "
                    "subject is UNAVAILABLE and that is a failure, not a skip (R15)")
    rendered = live["arms-sample"]

    assert rendered.strip(), (
        "the page publishes a settled-account count and says nothing about what fraction of the "
        "business it is -- silence there reads as 'this book is the supplier'")
    if rate < 1:
        assert "sample" in rendered.lower(), (
            "the book is {:.1%} of what the company won and the page does not use the word: "
            "{}".format(rate, rendered))


def test_the_sample_bound_carries_the_producers_own_numbers_and_not_its_own(live):
    """The page must RENDER the campaign's rate, never author one beside it.

    Two producers for one number is how `book_growth.json` and this section would start
    disagreeing about the same field while both looked right. So the assertion is on the
    published values, to one decimal on the percentage and to the whole count.

    Fires on: hard-coding the percentage, or reading a different field for the win count.
    """
    growth = _growth_feed()
    rate, won = growth.get("settlement_sample_rate"), growth.get("settlement_funnel_wins")
    if rate is None or won is None or not 0 < rate < 1:
        pytest.fail("the campaign record cannot express a sample below 1 (rate={}, won={}), so "
                    "this control cannot run and reports that as a failure".format(rate, won))
    rendered = live["arms-sample"]

    assert "{:.1f}%".format(rate * 100) in rendered, (
        "the rendered share is not the producer's {:.1f}%: {}".format(rate * 100, rendered))
    assert "{:,}".format(int(won)).replace(",", "") in rendered.replace(",", ""), (
        "the rendered win count is not the producer's {}: {}".format(won, rendered))
    assert "{:.3f}".format(rate) in rendered, (
        "the page tells a reader the count is a sample without giving them the divisor that "
        "turns it back into the supplier: {}".format(rendered))


def test_MUTATION_a_book_that_is_the_whole_business_says_so_instead():
    """The killer mutation, at the point where the defect disappears rather than at a wrong value.

    If the settlement engine could settle every win, this sentence must change, not merely
    re-state a smaller percentage. A page that renders the same words for a 17.9% sample and a
    100% book is printing a constant, and the two controls above are tautologies (R15's
    unreachable-PASS-branch shape).
    """
    growth = copy.deepcopy(_growth_feed())
    growth["settlement_sample_rate"] = 1.0
    growth["settlement_funnel_wins"] = growth.get("settlement_funnel_wins") or 505
    whole = _render(_live_feed(), growth=growth)["arms-sample"]
    live_text = _render(_live_feed())["arms-sample"]

    assert "not a sample" in whole.lower(), (
        "a book that IS the business rendered something else: {}".format(whole))
    assert whole != live_text, (
        "the page renders the SAME sample bound for a 17.9% book and a complete one, so it is "
        "printing a constant and reads nothing from the campaign record")
    assert "17.9%" not in whole, (
        "the complete-book branch still carries today's sample percentage, so the figure is "
        "authored on the page rather than read from the feed")


def test_MUTATION_an_unreadable_campaign_record_still_bounds_the_account_count():
    """FAIL-OPEN, the shape R15 names first. A growth feed with no rate in it must leave the
    reader told the count is an unknown fraction of the business -- never silent, which reads
    exactly like a book that needed no qualification."""
    growth = copy.deepcopy(_growth_feed())
    growth.pop("settlement_sample_rate", None)
    rendered = _render(_live_feed(), growth=growth)["arms-sample"]

    assert rendered.strip(), "a record with no sample rate rendered nothing at all"
    assert "could not be read" in rendered, (
        "an unreadable sample rate fell through to a count with no qualification on it: "
        "{}".format(rendered))
    assert "unknown fraction" in rendered, (
        "the absence branch does not tell the reader what it costs them: {}".format(rendered))


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


# ── the funnel between the two decision counts this page shows ───────────────────────────────
#
# THE DEFECT (2026-08-30). The page rendered "20 decisions priced" in the decisions block and a
# concordance "on 6 decisions" in the method block, with nothing between them. A reader taking
# the interval as earned on the twenty would be reading the page exactly as written.


def _skill_feed(drop_out):
    """The live feed with a known-good method block and a drop-out under test."""
    feed = dict(_live_feed())
    feed["method_skill"] = {
        "available": True, "concordance": 0.3333, "null_point": 0.5,
        "null_95_low": 0.1333, "null_95_high": 0.8667, "p_two_sided": 0.47,
        "inside_the_null": True, "decisions_scored": 6, "accounts": 5,
        "what_it_is": "Does the arm's own per-customer price rank the value JOINTLY created?",
        "reading": "The observed value sits INSIDE the interval a random signal produces.",
        "drop_out": drop_out,
    }
    return feed


_ELIGIBILITY_ONLY = {
    "available": True, "priced_decisions": 20, "decisions_scored": 6, "declined": 0,
    "by_reason": [
        {"reason": "the_priced_term_carried_no_settled_row", "count": 14,
         "class": "eligibility",
         "means": "the account DOES settle, but this priced term has no settled record inside "
                  "its own 365 days."},
    ],
    "by_class": {"join": 0, "coverage": 0, "eligibility": 14},
    "the_sample_can_be_widened_from_this_book": False,
    "reading": "20 priced decisions, 6 scored. THE SAMPLE CANNOT BE WIDENED FROM THIS BOOK.",
}


def test_the_page_says_how_many_of_the_priced_decisions_the_figure_actually_rests_on():
    """Both counts, and the drop between them, in the block that carries the interval.

    Fires on: the funnel being dropped from the render, or the page showing the scored count
    without the priced one it has to be read against.
    """
    rendered = _render(_skill_feed(_ELIGIBILITY_ONLY))["arms-method"]
    assert "priced 20 decisions" in rendered, (
        "the method block does not say how many decisions the arm priced: {}".format(rendered))
    assert "rests on 6" in rendered, "the block does not say what the figure rests on"
    # THE ROW ITSELF, as a reader sees it: the count against the reason, not a total. The
    # harness returns rendered TEXT, so this is the string on the page and not the markup
    # behind it — a checker reading the markup would pass on a table nobody can see.
    assert re.search(r"14\s+the account DOES settle", rendered), (
        "the 14 dropped decisions are not broken out against a reason: {}".format(rendered))
    assert "Ours to widen?" in rendered, (
        "the funnel is a table of counts with no answer to the reader's question")


def test_a_drop_the_world_caused_and_a_drop_we_caused_do_not_read_the_same(dummy=None):
    """THE WHOLE POINT OF THE BLOCK, and the reading that can fail.

    MUTATION: reclassify the same fourteen decisions from `eligibility` to `join`. The page must
    change its answer to the reader's actual question — can this sample be widened? A render
    that shows the counts but says the same thing either way is a table, not a finding.
    """
    eligibility = _render(_skill_feed(_ELIGIBILITY_ONLY))["arms-method"]
    joined = copy.deepcopy(_ELIGIBILITY_ONLY)
    joined["by_reason"][0]["class"] = "join"
    joined["by_class"] = {"join": 14, "coverage": 0, "eligibility": 0}
    joined["the_sample_can_be_widened_from_this_book"] = True
    widenable = _render(_skill_feed(joined))["arms-method"]

    assert "no &mdash; no outcome exists" in eligibility or "no — no outcome exists" in eligibility
    assert "failed join" in widenable, (
        "a decision we failed to join does not read as ours on the page")
    assert "failed join" not in eligibility, (
        "an eligibility rule the concordance needs reads as a defect of ours")


def test_a_run_predating_the_funnel_says_so_rather_than_showing_nothing():
    """FAIL-CLOSED, and visibly. The published artefact predates this block, so the absence
    branch is the one a reader sees first — and a silent absence beside two counts that do not
    match is the defect this whole section exists to close.

    Fires on: rendering an empty string when the feed carries no funnel.
    """
    rendered = _render(_skill_feed({
        "available": False,
        "reason": "the run that produced this artefact predates the drop-out funnel.",
    }))["arms-method"]
    assert "Not shown" in rendered, (
        "a feed with no funnel rendered no statement that it has none: {}".format(rendered))
    assert "predates the drop-out funnel" in rendered


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
    """WHATEVER the check concluded, the reader is told — and told the matching thing.

    THIS USED TO PIN `same_supplier is True` and call any other state "a real finding, not a test
    to relax". That was right about the divergence case and wrong as a control: on 2026-08-28 the
    check gained a third state — WITHHELD, for when the run artefact it reads is not the figure
    the site publishes — and this test reddened on a feed that had become more honest, not less.
    A control keyed to one of three answers cannot tell an improvement from a regression.

    What must hold is that the sentence the check produced is the sentence the reader meets.
    """
    feed = _live_feed()
    pub = feed["realised"]["is_the_published_supplier"]
    rendered = live["arms-published"]
    assert pub["statement"].strip(), "the check produced no sentence at all"
    # The door's `prose()` turns `--` into an em dash on the way to the screen, so the comparison
    # is on the normalised text. Matching raw would fail on a page that renders correctly.
    def _dashes(s):
        return s.replace("--", "\u2014").replace(" \u2014 ", " \u2014 ")
    assert _dashes(pub["statement"]) in _dashes(rendered), (
        "the sentence that connects this comparison to the figures the rest of the site "
        "publishes never reaches the page")
    if pub["same_supplier"] is not True:
        assert "IS the baseline" not in rendered, (
            "the page still tells the reader the published supplier IS the baseline arm while "
            "the check says otherwise")


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
    for panel in ("arms-realised", "arms-household", "arms-split", "arms-decisions",
                  "arms-headline"):
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


# ── both sides of one comparison, on one row ─────────────────────────────────────────────────
#
# THE DEFECT THESE SERVE. Until 2026-08-28 every figure on this surface was OURS. The mission's
# own sentence -- "value is created and THEN shared, so every decision has two sides" -- is a
# claim the page could not support in either direction, because a reader met only what the
# company earned. Charging a household the cap looks like a win in a single column and reads as
# an obvious transfer the moment the second one is beside it. The subject here is the RENDERED
# DOM for the same reason the rest of this file's is: a household figure sitting in the feed and
# not on the page proves nothing about what a reader meets.


def _feed_with_household(saving=(1000.0, 500.0, 250.0)) -> dict:
    """The live feed with a household side that scored all three arms."""
    feed = copy.deepcopy(_live_feed())
    feed["household"] = {
        "available": True,
        "clock": "settled-realised",
        "basis": "settled clock; counterfactual = the published default tariff",
        "what_it_is": "What the households on each arm's book kept.",
        "what_this_is_not": "This is not value CREATED.",
        "not_a_target": "A diagnostic, not a target.",
        "excludes": [
            {"currency": "money", "state": "measured", "what": "What each household paid us."},
            {"currency": "carbon", "state": "designed, never measured",
             "what": "Nothing instruments what a household's carbon did."},
            {"currency": "time", "state": "absent",
             "what": "No measure of a household's time exists anywhere in this project."},
        ],
        "arms": [
            {"key": key, "name": name, "role": "r", "household_saving_gbp": value,
             "household_saving_pct_of_counterfactual": 3.5, "coverage_pct": 88.0,
             "absent_reason": None}
            for key, name, value in zip(("control", "value", "level"),
                                        ("Flat rules", "Per-customer", "Flat at the same level"),
                                        saving)
        ],
    }
    return feed


def test_the_household_side_reaches_the_reader_in_the_same_table_as_the_company_side():
    """ONE ROW, not one page each. Two sides on two surfaces is not the claim being made: a
    reader who meets our net margin here and a household saving elsewhere cannot tell whether an
    arm earned more by CREATING more or by keeping more of the same surplus.

    Fires on: dropping the column, or rendering the household figure into its own section.
    """
    feed = _feed_with_household()
    rendered = _render(feed)
    table = rendered["arms-realised"]

    assert "What households kept" in table, (
        "the realised table renders no household column, so the page still has one side")
    for arm, household in zip(feed["realised"]["arms"], feed["household"]["arms"]):
        assert _gbp(household["household_saving_gbp"]) in table, (
            "the {} arm's household figure is not in the table a reader reads".format(arm["key"]))
        if arm["net_gbp"] is not None:
            assert _gbp(arm["net_gbp"]) in table, (
                "the {} arm's own net margin left the table when the household column "
                "arrived".format(arm["key"]))


def test_an_unscored_household_side_renders_its_reason_and_never_a_zero():
    """£0 saved is EXACTLY what "we charged them the default tariff and shared nothing" produces
    -- the worst answer this figure can return. Rendering an unmeasured side as zero would
    publish that answer as though it had been measured."""
    feed = copy.deepcopy(_live_feed())
    feed["household"] = {
        "available": False,
        "reason": "the run that produced this artefact predates the household side",
        "excludes": _feed_with_household()["household"]["excludes"],
        "what_this_is_not": "This is not value CREATED.",
        "not_a_target": "A diagnostic, not a target.",
    }
    rendered = _render(feed)

    assert "not shown" in rendered["arms-household"], (
        "an unmeasured household side rendered no statement that it is unmeasured")
    assert "predates the household side" in rendered["arms-household"], (
        "the absence reached the reader without its reason")
    assert "What households kept" not in rendered["arms-realised"], (
        "an empty household column was rendered, which reads as a measured blank")
    assert "£0" not in rendered["arms-household"]


def test_the_two_currencies_this_figure_does_not_reach_are_on_the_page():
    """The mission promises money, TIME and CARBON. This figure reaches one of the three, and a
    number published without that is a number a reader takes for the whole of "value shared"."""
    rendered = _render(_feed_with_household())["arms-household"]
    assert "carbon" in rendered and "designed, never measured" in rendered
    assert "time" in rendered and "absent" in rendered
    assert "not value CREATED" in rendered, (
        "the page publishes a share of a surplus as though it were value created")
    assert "not a target" in rendered.lower(), (
        "the household figure reaches the reader with no R12 statement beside it")


def test_an_arm_with_no_household_figure_renders_an_absence_beside_its_own_net_margin():
    """A per-arm absence must not become a blank cell that reads as zero, and must not borrow
    another arm's figure."""
    feed = _feed_with_household()
    feed["household"]["arms"][2] = {
        "key": "level", "name": "Flat at the same level", "role": "r",
        "household_saving_gbp": None, "absent_reason": "this arm did not run",
    }
    rendered = _render(feed)["arms-realised"]
    assert "not measured" in rendered, (
        "an arm the run never scored rendered as a blank rather than as an absence")
    assert rendered.count(_gbp(1000.0)) == 1, (
        "an arm with no household figure was filled from another arm's")


# ── the page may name a winner only where the contrast cleared its own floor ─────────────────
#
# THE DEFECT, AT THE DOM. Until 2026-08-29 the headline named a winner on every run, while the
# error bar three paragraphs below it said the same figure moves further than that across three
# re-runs that changed nothing but a dice roll. A reader met the winner first. Both blocks were
# true; the page was not.
#
# KEYED TO THE PROPERTY. This does not pin "we cannot tell" -- it recomputes, from the feed's own
# published bounds, which case the run is in, and requires the RENDERED sentence to match. The day
# the book is big enough for a contrast to clear its spread, the direction comes back and this
# stays green; a page that goes on refusing, or goes back to asserting, reds either way.

#: Every rendered sentence on this surface that names a winner, KEYED TO THE CONTRAST IT NAMES.
#
# THE SCOPE DEFECT THIS SPLIT REPAIRS (2026-08-31). These four phrases used to be one flat tuple
# checked against the SELECTION leg's spread alone -- but the first two are the arm-vs-control
# contrast (`value_advantage_gbp`) and only the last two are the selection contrast. The composer
# has always gated each against its own spread (`_BOUNDED_CONTRASTS` names all three separately;
# `_arm_vs_control_clause` takes `advantage_spread`), so the control's scope was wider than its
# claim: it read one contrast's bound and vetoed another contrast's sentence.
#
# It could not fire until today. While `contrast_bounds.available` was false the `stdev is None`
# branch suppressed both groups together, and on the 2026-08-29 run both contrasts happened to be
# unresolvable at once (£607 against ±£990, £1,816 against ±£2,578), so the OR never diverged from
# the AND. The 2026-08-31 floor is the first run where they disagree -- £12,071 clears its ±£2,291
# while £2,574 sits inside its ±£3,776 -- and the flat tuple made the page's correct refusal on the
# selection leg veto its earned direction on the headline leg.
_DIRECTIONAL_CLAIMS_BY_CONTRAST = {
    "value_advantage_gbp": ("MORE than flat rules", "LESS than flat rules"),
    "selection_gbp": ("the per-customer choosing is worth less than nothing",
                      "the choosing itself carried part of it"),
}


def test_the_page_names_a_winner_only_where_the_contrast_cleared_its_floor(live):
    feed = _live_feed()
    split = (feed.get("realised") or {}).get("split") or {}
    bounds = (feed.get("contrast_bounds") or {})
    headline = live["arms-headline"]

    selection = split.get("selection_gbp")
    if selection is None:
        pytest.fail("the live feed carries no selection leg, so this control's subject is absent")

    # EACH CONTRAST AGAINST ITS OWN FLOOR, never one against another's. A contrast the feed does
    # not report is not evidence its sign is safe to state, so it takes the no-spread branch.
    for contrast, claims in _DIRECTIONAL_CLAIMS_BY_CONTRAST.items():
        spread = ((bounds.get("contrasts") or {}).get(contrast) or {}) \
            if bounds.get("available") else {}
        value, stdev = split.get(contrast), spread.get("stdev_gbp")
        said = [c for c in claims if c in headline]

        if stdev is None or value is None:
            assert not said, (
                "the page named a winner on `{}` with no measured spread behind it: {}".format(
                    contrast, headline))
            continue
        if abs(value) > stdev:
            assert said, (
                "`{}` cleared its own seed spread and the page still refused to say which way it "
                "went -- a refusal that cannot be withdrawn is not a reading: {}".format(
                    contrast, headline))
            assert _gbp(stdev).lstrip("-") in headline or "clearing the" in headline, (
                "a direction was published without the spread it beat")
        else:
            assert not said, (
                "the page named a winner on `{}`, a contrast INSIDE its own error bar: {}".format(
                    contrast, headline))

    selection_spread = ((bounds.get("contrasts") or {}).get("selection_gbp") or {}) \
        if bounds.get("available") else {}
    stdev = selection_spread.get("stdev_gbp")
    if stdev is not None and abs(selection) <= stdev:
        assert "CANNOT RESOLVE" in headline, headline
        # THE REMEDY MUST REACH THE READER, AND IT MUST BE THE MEASURED ONE. This pinned the words
        # "larger SETTLED BOOK" until 2026-08-29 -- a control keyed to today's answer, which would
        # have gone red the moment the page stopped asserting an unmeasured remedy and stayed green
        # while the claim rotted. What the page owes a reader is the remedy its own
        # `floor_decomposition` supports, so that is what is checked, branch by branch.
        decomposition = feed.get("floor_decomposition") or {}
        if not decomposition.get("available"):
            expected = "has not been established"
        # A DECOMPOSITION MEASURED ON ANOTHER BOOK IS NOT A WEAKER REMEDY, IT IS A REMEDY FOR A
        # DIFFERENT QUESTION (2026-08-31). The composer refuses before reading a figure out of it
        # (`_what_would_resolve_it`), and this rung was missing here -- so on the first run where
        # the two books diverged (20 of 1,369 measured, 120 of 1,953 published) this ladder
        # demanded the page quote a remedy denominated in a priced count it no longer has. Read
        # off the feed's published verdict, never recomputed here, so the two cannot drift.
        elif decomposition.get("measured_on_this_page_s_book") is False:
            expected = "has not been established"
            assert "FROM A DIFFERENT BOOK" in headline, (
                "the page dropped the remedy but not the reason, so a reader cannot tell a "
                "refusal from an omission: {}".format(headline))
        elif not decomposition.get("share_is_decisive"):
            expected = "too close to the"
        elif decomposition.get("larger_settled_book_would_resolve_it"):
            expected = "larger SETTLED BOOK"
        else:
            expected = "cannot be resolved at any book"
        assert expected in headline, (
            "the page's remedy does not match the split it published: `floor_decomposition` says "
            "{!r} and the headline does not carry it: {}".format(expected, headline))
        assert "More seeds would not resolve it" in headline, (
            "the page dropped the half of the remedy that is arithmetic and always true")


def test_the_withdrawn_sentence_reaches_the_reader_beside_the_one_that_replaced_it(live):
    """A correction a reader cannot see is one they cannot check. This page's whole claim on
    anyone's trust is that it publishes the unflattering direction -- worth nothing if it can also
    un-publish one silently."""
    feed = _live_feed()
    withdrawn = feed.get("withdrawn_claim") or {}
    assert withdrawn.get("note"), "the feed carries no withdrawal for the page to render"

    note = live["arms-note"]
    assert "WITHDRAWN" in note, (
        "the withdrawal is in the feed and not on the page: {}".format(note))
    assert "worth less than nothing" in note, (
        "the page announces a withdrawal without the words it withdrew, so a reader cannot tell "
        "what stopped being claimed")
    assert "withdrawn, not reversed" in note, (
        "the page lets a reader take the withdrawal for the opposite claim")


# ── whose customers the method has priced ─────────────────────────────────────────────────────
#
# THE DEFECT (2026-08-30). `#arms-decisions` said how MANY decisions the reading rests on and
# named the accounts, and never said the thing a reader needs: that every one of them is an
# account the company was FOUNDED with, and that not one of the 158 it won or drew has ever had
# a renewal reach the arm. The mission's claim is that the value comes from inference over the
# customers the method FINDS, so "the method has never priced a customer the company won" is a
# fact about the enterprise value claim and belongs on the surface, not in an observability file.

def test_the_verdict_on_whose_customers_the_arm_reached_reaches_the_reader(live):
    """Fires on: dropping the paragraph from the door, or from the feed that fills it.

    KEYED TO THE VERDICT THE FEED STATES, NOT TO ONE OF THEM (2026-08-31). This test used to
    assert the STRUCTURAL verdict -- "the method has NEVER priced a customer the company won",
    with its "GATE, not a book size" clause -- through the live page. That was true of every run
    up to 2026-08-30 and it stopped being true the moment the standard-variable product shipped:
    the 2026-08-31 run priced 58 accounts the company found rather than started with, and this
    control went red for the single reason that the thing it described had been fixed. A control
    that reds when the world improves is keyed to today's answer, so it now checks that WHICHEVER
    verdict the feed states is the one the reader gets, and the branch the live run is not in is
    driven from a constructed feed below.
    """
    who = (_live_feed()["decisions"] or {}).get("who_the_method_has_priced") or {}
    assert who.get("available") is True, (
        "the live feed carries no verdict on whose customers the arm reached, so the paragraph "
        "below cannot be rendered: {}".format(who))
    # The door runs every string through `prose()`, which turns ` -- ` into an em dash before the
    # reader sees it. Comparing the raw feed string against the rendered one without undoing that
    # is how a correct page gets reported red.
    rendered = _text(live["arms-decisions"]).replace(" — ", " -- ")
    assert who["sentence"] in rendered, "the verdict reached the feed and not the reader"
    # The clause that only the STRUCTURAL verdict earns, asserted in both directions so neither
    # branch can be rendered as the other.
    if who["verdict"] == "structural":
        assert "GATE, not a book size" in rendered
    else:
        assert "GATE, not a book size" not in rendered, (
            "a run that HAS priced a won account was rendered with the structural gate clause, "
            "which tells the reader no book size would ever reach one: {}".format(rendered))


def test_MUTATION_a_run_that_priced_no_won_account_renders_the_other_verdict(live):
    """NULL RUNG on the RENDERED string, not just on the feed. A door that prints one sentence
    whatever the feed says is a constant wearing a measurement's clothes -- and this panel is the
    one whose whole purpose is to be able to return the unflattering answer.

    THE BRANCH DRIVEN HERE IS THE ONE THE LIVE RUN IS NOT IN, and which that is flipped on
    2026-08-31. Until then the live page was structural and this rung constructed `reached`; the
    standard-variable product made `reached` the live state, so this now constructs the structural
    verdict. Both branches stay reachable either way, which is the property.
    """
    feed = copy.deepcopy(_live_feed())
    who = feed["decisions"]["who_the_method_has_priced"]
    who["verdict"] = "structural"
    who["won_or_drawn_accounts_priced"] = 0
    who["sentence"] = ("The method has NEVER PRICED A CUSTOMER THE COMPANY WON. Every account it "
                       "priced was in the opening roster, and the reason is the product GATE, not "
                       "a book size: there is no book size at which the first one is priced.")
    rendered = _text(_render(feed)["arms-decisions"])
    assert "GATE, not a book size" in rendered
    assert "NEVER PRICED A CUSTOMER THE COMPANY WON" in rendered


def test_MUTATION_a_feed_with_no_verdict_renders_no_claim_about_it():
    """FAIL-CLOSED. An artefact that cannot say whose customers the arm reached must leave the
    reader with nothing there rather than the last run's sentence or a guessed one.
    """
    feed = copy.deepcopy(_live_feed())
    feed["decisions"]["who_the_method_has_priced"] = {"available": False, "reason": "no funnel"}
    rendered = _text(_render(feed)["arms-decisions"])
    assert "GATE, not a book size" not in rendered
    assert "never priced a customer" not in rendered.lower()
    # The panel still renders its other content, so this is an absence and not a blank page.
    assert "renewals" in rendered


def test_the_gate_claim_carries_the_strength_of_its_own_premise(live):
    """Fires on: dropping `premise_basis` from the door, or from the feed that fills it.

    "There is no book size at which the first one is priced" asks for a curriculum change. Whether
    its premise was MEASURED on the run's own roster or argued from the code path is the reader's
    to weigh -- and today's artefact predates the measurement, so the page must say so rather
    than let the strongest wording ride on the weakest evidence.
    """
    who = (_live_feed()["decisions"] or {}).get("who_the_method_has_priced") or {}
    assert who.get("premise_basis"), (
        "the live feed states the gate claim with no basis beside it: {}".format(who))
    rendered = _text(live["arms-decisions"]).replace(" — ", " -- ")
    assert who["premise_basis"] in rendered, "the basis reached the feed and not the reader"


def test_MUTATION_a_page_whose_feed_states_no_basis_prints_no_basis_clause():
    """FAIL-CLOSED. A door that prints "Basis:" whatever the feed says would attach the last
    run's strength to this run's claim -- and this panel's whole purpose is to be readable about
    how much it knows."""
    feed = copy.deepcopy(_live_feed())
    feed["decisions"]["who_the_method_has_priced"].pop("premise_basis", None)
    rendered = _text(_render(feed)["arms-decisions"])
    assert "Basis:" not in rendered
    # The verdict itself still renders, so this is an absence and not a blanked panel. Keyed to
    # whatever verdict the feed states -- see the rename above for why naming one went stale.
    assert feed["decisions"]["who_the_method_has_priced"]["sentence"] in rendered.replace(
        " — ", " -- ")


# ── the belief AUC, and the interval it went out without ─────────────────────────────────────
#
# THE DEFECT THESE SERVE. For four days `#arms-decisions` rendered "The company's own belief about
# who will leave scored 0.130 on the usual rank measure" followed by a CONSTANT sentence reading
# any value below 0.50 as worse than a coin flip. Three things were wrong on the screen, not in
# the feed: no interval (a random signal scores 0.24 to 0.76 on ten departures, so the same page
# had called 0.4653 — two-sided p 0.80 — the same finding); the wrong subject (`believed_p_retain`
# is the retention the arm expected AT THE PRICE IT CHOSE, not a forecast of who would leave); and
# a corroboration claim between two results that share a cause.

def test_the_belief_figure_never_reaches_the_reader_without_its_interval(live):
    """FAIL-CLOSED ON THE BOUND. An AUC on ten departures with no null beside it is the figure
    this whole repair is about; if the number renders and the interval does not, the page is back
    where it started.

    Fires on: dropping `auc_reading` from the render, or composing a reading that omits the null.
    """
    feed = _live_feed()
    auc = feed["decisions"].get("discrimination_auc")
    if auc is None:
        pytest.skip("this run published no belief AUC")
    rendered = live["arms-decisions"]
    assert "{:.3f}".format(auc) in rendered, "the belief figure does not reach the reader"
    bound = feed["decisions"]["auc_attribution"]["null_bound"]
    assert bound["available"], "the live feed carries no null for the figure it publishes"
    for edge in ("null_95_low", "null_95_high"):
        assert "{:.2f}".format(bound[edge]) in rendered, (
            "the belief figure is on the page without the range a signal carrying no information "
            "reaches on {} departures".format(bound["left"]))
    assert "{} departures".format(bound["left"]) in rendered, (
        "the page states a rank statistic without the sample it is computed over")


def test_the_page_says_WHAT_THE_BELIEF_IS_A_BELIEF_ABOUT(live):
    """The subject, corrected on the screen and not only in the feed.

    Fires on: restoring "the company's own belief about who will leave" — which is a different and
    much larger claim, and is contradicted by the same company's estimate scoring 0.534 over 708
    renewals on 2026-08-30.
    """
    rendered = live["arms-decisions"]
    assert "survive the price it chose" in rendered
    assert "own belief about who will leave" not in rendered


def test_the_reader_is_told_the_arm_produced_the_departures_it_is_graded_on(live):
    """THE FINDING, on the page. Five of the ten accounts the arm priced left under the value arm
    and did not leave under the control, so half the positive class is the arm's own doing.

    Fires on: publishing the AUC with its interval and without its endogeneity — which would be an
    honest-looking number answering a question nobody asked.
    """
    rendered = live["arms-decisions"]
    caused = _live_feed()["decisions"]["auc_attribution"][
        "priced_accounts_the_arm_itself_drove_out"]
    assert caused, "the live feed names no account the arm drove out -- nothing to render"
    assert "did NOT leave under the control" in rendered
    for account in caused:
        assert account in rendered, "{} is missing from the rendered cause".format(account)


def test_a_figure_INSIDE_its_null_renders_as_UNRESOLVED_on_the_page():
    """THE PASS BRANCH, driven through the door because the live run is in the other one.

    A page that can only ever print "backwards" is a constant verdict wearing a gate's clothes.
    This drives the door with the 2026-08-27 run's own figure — 0.4653 on 16 retained and 9
    departed, two-sided p 0.80 — which the superseded reading called worse than a coin flip.

    Fires on: re-pinning the rendered reading to `auc < 0.5`.
    """
    feed = copy.deepcopy(_live_feed())
    dec = feed["decisions"]
    dec["discrimination_auc"] = 0.4652777777777778
    dec["auc_attribution"]["null_bound"].update(
        {"available": True, "retained": 16, "left": 9, "null_95_low": 0.264,
         "null_95_high": 0.736, "p_two_sided": 0.80283, "inside_the_null": True})
    dec["auc_reading"] = (
        "Measured on 9 departures and 16 retentions. A signal carrying no information at all "
        "scores between 0.26 and 0.74 on a population this size. The observed value is INSIDE "
        "that interval, so this run does not distinguish the belief from a coin flip in either "
        "direction.")
    rendered = _render(feed)["arms-decisions"]
    assert "0.465" in rendered
    assert "INSIDE that interval" in rendered
    assert "worse than a coin flip" not in rendered


def test_the_reader_is_told_WHICH_departures_or_why_they_are_not_named(live):
    """A rank statistic on ten departures that does not say which ten is a number nobody can
    check. The live run's artefact predates the field that carries them, so the page must print
    the ABSENCE -- not a blank, and not ten of them out of twenty.

    Fires on: rendering nothing when `the_departures.available` is false.
    """
    rendered = live["arms-decisions"]
    departures = _live_feed()["decisions"]["auc_attribution"]["the_departures"]
    if departures["available"]:
        assert "{} departures it is computed over".format(departures["count"]) in rendered
        for row in departures["departures"]:
            assert row["account"] in rendered
    else:
        assert "Which departures: not listed" in rendered
        assert "ships with the next A/B run" in rendered


def test_the_departures_reach_the_reader_by_name_once_a_run_carries_them():
    """THE PASS BRANCH, through the door's own JavaScript. The absent branch is what the live feed
    exercises, so without this the render that finally names them would ship unseen."""
    feed = copy.deepcopy(_live_feed())
    feed["decisions"]["auc_attribution"]["the_departures"] = {
        "available": True, "count": 2, "agrees_with_auc_population": True,
        "departures": [
            {"account": "C6", "term_start": "2017-04-01", "believed_p_retain": 0.62,
             "chosen_margin_gbp_per_mwh": 60.0},
            {"account": "C9", "term_start": "2019-07-01", "believed_p_retain": 0.95,
             "chosen_margin_gbp_per_mwh": 60.0},
        ]}
    rendered = _render(feed)["arms-decisions"]
    assert "2 departures it is computed over" in rendered
    assert "C6 (2017-04-01)" in rendered and "C9 (2019-07-01)" in rendered
    assert "not listed" not in rendered


def _row(bucket: dict) -> str:
    """One believed-retention band as a reader reads across it, in `_text`'s collapsed form."""
    return "{:.1f}–{:.1f} {} {}% {}%".format(
        bucket["believed_from"], bucket["believed_to"], bucket["n"],
        round(bucket["realised_retention_rate"] * 100),
        round(bucket["realised_retention_rate_under_a_flipped_label"] * 100))


def test_the_reversal_reaches_the_reader_as_a_TABLE_and_not_an_adjective(live):
    """The page calls this belief BACKWARDS. Until 2026-08-30 the reader's only evidence for that
    was the scalar it describes, because the departures cannot be named on this run's artefact.
    The believed-versus-realised bands were in the artefact all along.

    Fires on: rendering the reading without the bucket rows, or rendering rows without their
    realised rates.
    """
    table = _live_feed()["decisions"]["auc_attribution"]["by_believed_bucket"]
    if not table["available"]:
        assert "What the reversal looks like: not shown" in _text(live["arms-decisions"])
        return
    rendered = _text(live["arms-decisions"])
    assert "What the reversal looks like." in rendered
    for bucket in table["buckets"]:
        # THE WHOLE ROW, not its cells. Two of these bands realise 0% and two flip to 100%, so a
        # per-cell substring assertion passes on "0%" the moment "100%" is anywhere on the page --
        # it would go green against a table with every row in the wrong place.
        assert _row(bucket) in rendered, (
            "the band {:.1f}-{:.1f} is not rendered as a row a reader can read across".format(
                bucket["believed_from"], bucket["believed_to"]))


def test_the_flipped_column_is_on_the_page_beside_the_real_one(live):
    """WITHOUT IT THIS TABLE ARGUES FOR THE SIGN ERROR THE PARAGRAPH BELOW REFUTES.

    Flipped, these bands read monotone the right way and look better than any belief on this page.
    A reader shown only the real column has been handed the case FOR an inverted label, three
    inches above the paragraph that refutes it.

    Fires on: rendering the table without the flipped rates, or without saying which leg settles
    the sign.
    """
    table = _live_feed()["decisions"]["auc_attribution"]["by_believed_bucket"]
    if not table["available"]:
        pytest.skip("this run publishes no bucket table")
    rendered = _text(live["arms-decisions"])
    assert "If the labels were flipped" in rendered
    for bucket in table["buckets"]:
        assert _row(bucket) in rendered, (
            "a band is on the page without the flipped rate beside it")
    assert "settled on the LEVEL beside it and not here" in rendered


def test_a_withheld_bucket_table_prints_its_absence_rather_than_nothing():
    """THE OTHER BRANCH, THROUGH THE DOOR'S OWN JAVASCRIPT. The live feed publishes the table, so
    the refusal path -- a run whose bands do not reconcile with the rank statistic's population --
    would otherwise ship unrendered and unseen.

    Fires on: rendering "" when `available` is false.
    """
    feed = copy.deepcopy(_live_feed())
    feed["decisions"]["auc_attribution"]["by_believed_bucket"] = {
        "available": False,
        "reason": "the buckets count 14 decisions and the rank statistic's population counts 20."}
    rendered = _text(_render(feed)["arms-decisions"])
    assert "What the reversal looks like: not shown" in rendered
    assert "the buckets count 14 decisions" in rendered


def test_the_reader_is_told_the_backwards_figure_is_not_a_sign_error(live):
    """THE FIRST THING A COMPETENT READER SUSPECTS, answered where they meet the figure.

    The page tells a reader this belief ranked customers BACKWARDS. An estimator strongly wrong in
    a consistent direction is the classic signature of a comparison taken against the wrong side
    of the outcome label, and until 2026-08-30 the page gave a reader no way at all to tell the
    finding apart from a bug in our own code -- the answer existed, in the feed, and stopped at
    the JSON.

    Fires on: rendering the AUC and its reading without the attribution paragraphs.
    """
    rendered = live["arms-decisions"]
    check = _live_feed()["decisions"]["auc_attribution"]["polarity_check"]
    if not check["available"]:
        pytest.skip("this run's history carries no believed/realised pair to check")
    assert "Is it a sign error?" in _text(rendered)
    assert ("No." if check["refuted"] else "NOT ESTABLISHED.") in _text(rendered)
    assert "invariant under the flip" in _text(rendered), (
        "the caveat that the subject run cannot vote on its own polarity is not on the page")


def test_an_unrefuted_polarity_branch_never_renders_as_settled():
    """THE OTHER BRANCH, THROUGH THE DOOR'S OWN JAVASCRIPT. `refuted: False` is the verdict this
    page would need to print if a future run's history stopped closing the branch, and the live
    feed will never exercise it. A page that says "No." whatever the field holds is decorating.

    Fires on: hard-coding the "No." answer instead of composing it from `refuted`.
    """
    feed = copy.deepcopy(_live_feed())
    check = feed["decisions"]["auc_attribution"]["polarity_check"]
    check["refuted"] = False
    check["reason"] = "2 of 4 runs that can discriminate sit CLOSER to the flipped label."
    rendered = _text(_render(feed)["arms-decisions"])
    assert "NOT ESTABLISHED." in rendered
    assert "sit CLOSER to the flipped label" in rendered


def test_the_oracle_ceiling_reaches_the_reader_as_a_number_not_a_verdict(live):
    """"The population is not unrankable" is an assertion; 0.762 against a 0.5 null is evidence.
    The branch-closing FIGURE must be on the page, not just the conclusion it licenses.

    Fires on: rendering the "this book ranks" sentence without the ceiling it rests on.
    """
    rendered = _text(live["arms-decisions"])
    grade = _live_feed()["decisions"]["auc_attribution"]["independent_grade"]
    assert "Is the population simply unrankable?" in rendered
    assert "{:.3f}".format(grade["oracle_ceiling_auc"]) in rendered, (
        "the oracle ceiling that closes the instrument-defect branch is not on the page")
    assert str(grade["renewals"]) in rendered


# ── the 20 → 6 funnel, and the code that drew the book it was measured on ─────────────────────


def test_the_drop_out_funnel_reaches_the_reader_broken_out_by_class(live):
    """The answer this page computed for two stretches and never published.

    A reader met "20 decisions priced" and a concordance interval scored on 6 a few hundred
    pixels apart, with nothing between them. The gap is the whole question of whether the sample
    can be widened, and the classes are the answer: a join failure is ours to fix, a coverage gap
    is data we owe, an eligibility drop is not available at any book size.

    Fires on: rendering the totals without the class split, which is the reading that makes the
    14 look like plumbing.
    """
    rendered = _text(live["arms-method"])
    drop = _live_feed()["method_skill"]["drop_out"]
    assert drop["available"] is True, (
        "the live feed withholds the funnel, so this control is measuring an absence -- fix the "
        "promoted artefact, not this test")
    assert "The arm priced {} decisions and this figure rests on {}".format(
        drop["priced_decisions"], drop["decisions_scored"]) in rendered
    for row in drop["by_reason"]:
        assert str(row["count"]) in rendered
    assert "no — no outcome exists" in rendered
    assert "yes — an input we owe" in rendered


def test_the_reader_is_told_the_sample_cannot_be_widened_by_our_own_code(live):
    """THE CONSEQUENCE, which is the durable half of the whole block.

    The classification does not depend on the population, so it survives the provenance problem
    that withholds the counts. What it says is that the concordance interval three lines above is
    not a number that gets better by trying harder here -- and a reader who takes it for one has
    read the page backwards.

    Fires on: publishing the funnel without its consequence.
    """
    rendered = _text(live["arms-method"])
    assert "cannot be widened by fixing our own code" in rendered
    assert "ZERO are a join we failed to make" in rendered


def test_MUTATION_a_run_with_a_join_failure_is_told_the_gap_is_OURS(live):
    """NULL RUNG. The sentence above must be a reading of the classes, not a constant.

    A join failure is a DEFECT and it is ours to fix here with no world change. A page that says
    "cannot be widened by fixing our own code" over a non-zero join count would be telling the
    reader to stop looking at the one class they should act on.

    Fires on: hard-coding either sentence; on a consequence composed from the total rather than
    from the class split.
    """
    # THE PRODUCER'S OWN COMPOSER, not a hand-written sentence. A fixture that typed the join
    # wording would prove only that the door renders a string it was handed.
    from tools.generate_value_arms_data import _widening_consequence

    feed = copy.deepcopy(_live_feed())
    drop = feed["method_skill"]["drop_out"]
    drop["by_class"] = {"join": 3, "coverage": 4, "eligibility": 10}
    drop["consequence"] = _widening_consequence(drop["by_class"])
    rendered = _text(_render(feed)["arms-method"])
    assert "3 are a join we failed to make" in rendered
    assert "cannot be widened by fixing our own code" not in rendered, (
        "a run WITH a join failure was told its sample cannot be widened -- the page is printing "
        "a constant, not the classes")


def _book_counts(feed):
    """The settled-book counts, from whichever branch the live feed is currently in.

    THE LIVE BRANCH FLIPPED ON 2026-08-31. Until then every run predated the producing-commit
    stamp, so `book.available` was False and the counts sat in `unlabelled_counts` -- and three
    controls below popped that key off the live feed to build their fixtures. The 2026-08-31 run
    carries the stamp, so the key is gone and they raised `KeyError` for the single reason that
    the provenance gap they were written about had been closed. The counts are the same numbers
    in both branches; only their address moves.
    """
    book = feed["book"]
    return dict(book.get("unlabelled_counts") or
                {k: v for k, v in book.items()
                 if k not in ("available", "produced_by", "why_the_counts_are_withheld",
                              "unlabelled_counts")})


def _feed_with_an_unlabelled_book(feed):
    """The feed as it looks for a run whose draw code cannot be named -- the REFUSAL branch.

    Constructed rather than read, because the live run can name its code. A control for the
    withheld branch that can only be driven by a live artefact in that branch stops being a
    control the day the artefact improves, which is what happened here.
    """
    counts = _book_counts(feed)
    provenance = {"stated": False, "commit": None, "short": None,
                  "reason": "this artefact predates the producing-commit stamp.",
                  "counts_are_labelled_by_the_code_that_made_them": False}
    feed["book"] = {"available": False, "produced_by": provenance,
                    "why_the_counts_are_withheld": (
                        "These counts describe a population, and this run cannot name the code "
                        "that drew it. " + provenance["reason"]
                        + " A count published without the tree that made it reads as a fact "
                          "about the supplier when it may be a fact about code that has since "
                          "been replaced."),
                    "unlabelled_counts": counts}
    feed["producing_commit"] = provenance
    # THE SECOND ROUTE THE COUNT REACHES THE PAGE BY. `_decisions` withholds it on the same
    # provenance gate, and a fixture that strips only `book` leaves the decisions panel still
    # printing "The book is 164 settled accounts" -- which is the very sentence this branch
    # exists to suppress, arriving by the other door.
    feed["decisions"] = dict(feed.get("decisions") or {}, book_accounts_settled=None)
    return feed


def test_a_run_that_cannot_name_the_code_that_drew_its_book_shows_no_book_count(live):
    """The counts go on the page labelled by the code that made them, or they do not go on it.

    "167 settled billing accounts" reads to every reader as a fact about this supplier. On the
    run promoted 2026-08-30 it is a fact about a population the tree no longer draws, and the
    artefact cannot say otherwise because it predates the producing-commit stamp.

    Fires on: rendering the count from either of its two feed routes when the feed withholds it;
    on printing "null settled accounts", which is the shape a naive withdrawal leaves behind.
    """
    feed = _feed_with_an_unlabelled_book(copy.deepcopy(_live_feed()))
    assert feed["book"]["available"] is False
    count = str(feed["book"]["unlabelled_counts"]["billing_accounts_settled_in_window"])
    rendered = _render(feed)
    note = _text(rendered["arms-note"])
    assert "settled-book counts are withheld" in note
    assert "predates the producing-commit stamp" in note
    assert count + " settled billing accounts" not in note
    decisions = _text(rendered["arms-decisions"])
    assert "null settled accounts" not in decisions
    assert "undefined settled accounts" not in decisions
    assert count + " settled accounts" not in decisions


def test_a_run_that_CAN_name_its_code_puts_the_count_back_with_the_commit(live):
    """THE PASS BRANCH -- the one that stops this being a page that only ever refuses.

    R15: a control whose pass branch is unreachable reports a constant. Keyed to the property, so
    the first stamped run promoted here restores the count with nobody editing a string.

    Fires on: hard-coding the withheld wording; on restoring the count without its label, which
    is the state the page was in when both provenance traps went unnoticed.
    """
    feed = copy.deepcopy(_live_feed())
    counts = _book_counts(feed)
    feed["book"] = dict(counts, available=True, produced_by={
        "stated": True, "commit": "a" * 40, "short": "a" * 9,
        "publishing_tree_commit": "a" * 40,
        "produced_by_the_tree_it_publishes_from": True,
        "counts_are_labelled_by_the_code_that_made_them": True,
        "reading": "Produced and published by the same tree (aaaaaaaaa)."})
    feed["producing_commit"] = feed["book"]["produced_by"]
    feed["decisions"]["book_accounts_settled"] = counts["billing_accounts_settled_in_window"]
    rendered = _render(feed)
    note = _text(rendered["arms-note"])
    assert "{} settled billing accounts".format(
        counts["billing_accounts_settled_in_window"]) in note
    assert "the same code this page runs (aaaaaaaaa)" in note
    assert "withheld" not in note
    assert "{} settled accounts".format(
        counts["billing_accounts_settled_in_window"]) in _text(rendered["arms-decisions"])


# ── the world every figure on this page was measured in ──────────────────────────────────────
#
# THE DEFECT THESE SERVE (2026-08-30). This page publishes an advantage over a baseline, and the
# rest of the site publishes the churn, retention and lifetime figures that come out of the same
# world. The single quantity that decides what any of them is worth is how readily a customer
# leaves in that world -- and the repository has been able to print that comparison, against the
# published GB switching record, since `tools/measure_departure_level.py` landed. No reader could
# see it. On the day it was drawn the world sat 3.15x below the record; by the time this shipped
# the level anchor had landed and every comparable year was inside the band. That is exactly why
# what goes on the page is the PROPERTY -- the world's level, the published band, and whether the
# one is inside the other -- and not a caveat about the miss, which would already be a stale
# apology somebody had to remember to delete.
#
# R15 -- the mutations, each run and each firing exactly the assertion named:
#   * delete the `#arms-departure` render -> all four checks below red.
#   * drop the published-band column from the row -> the band assertion reds and only that one.
#   * drop the world's own level column -> the level assertion reds and only that one.
#   * render a constant instead of `dl.statement` -> the verdict assertion reds.
# Run against a COPY of the door driven through the same harness, not by editing the shared tree:
# another lane's publish suite was mid-flight, and mutating a door it reads manufactures a red in
# somebody else's hook chain.


def _band(year: dict) -> str:
    """The published band as a reader reads it, with the en dash the door renders."""
    return "{:.1f}–{:.1f}%".format(year["band_lo_pct"], year["band_hi_pct"])


def test_the_worlds_departure_level_and_the_published_band_both_reach_the_reader(live):
    """BOTH FIGURES, YEAR BY YEAR, and the verdict between them.

    Fires on: dropping the `#arms-departure` render; dropping either column from the table;
    rendering the sentence without the years it was read from.
    """
    dl = _live_feed().get("departure_level") or {}
    assert dl.get("available") is True, (
        "the live feed carries no measured departure level ({}), so the page cannot state the "
        "world its figures were measured in -- fix the producer, not this test".format(
            dl.get("reason")))
    rendered = live["arms-departure"]
    assert rendered.strip(), (
        "the page renders an advantage over a baseline and says nothing about how readily a "
        "customer leaves the world it was measured in")
    assert dl["statement"].replace(" -- ", " — ") in rendered, (
        "the verdict reached the feed and not the reader")
    for year in dl["years"]:
        assert "{:.2f}%".format(year["world_pct"]) in rendered, (
            "{}'s realised departure level is not on the page a reader opens".format(
                year["year"]))
        assert _band(year) in rendered, (
            "{}'s published band is not on the page, so the level beside it is a number with "
            "nothing to be judged against".format(year["year"]))
        assert ("inside" if year["inside_band"] else "OUTSIDE") in rendered


def test_the_level_on_the_page_is_the_one_the_measuring_tool_REPORTS(live):
    """TWO PRODUCERS FOR ONE NUMBER is how the page and the tool would start disagreeing about the
    same quantity while both looked right. So the rendered figures are reconciled against a live
    call to the module that owns the denominators, not against the feed that rendered them.

    Fires on: the feed drifting off the tool; a page that authors its own level.
    """
    from tools.measure_departure_level import (
        inside_band,
        published_bands,
        world_realised_rate_pct,
    )

    bands, world = published_bands(), world_realised_rate_pct()
    assert world, "the captured run carries no comparable departure years"
    rendered = live["arms-departure"]
    for year, level in sorted(world.items()):
        lo, hi = bands[year]
        assert "{:.2f}%".format(round(level, 2)) in rendered, (
            "the tool measures {} at {:.2f}% and the page does not carry it".format(year, level))
        assert "{:.1f}–{:.1f}%".format(lo, hi) in rendered
        assert ("inside" if inside_band(level, lo, hi) else "OUTSIDE") in rendered


def test_MUTATION_a_world_OUTSIDE_the_published_band_says_so_and_says_which_way():
    """THE NULL RUNG, and it is the state the world was in when this was written.

    A page that renders the same paragraph for a world inside the record's band and one running at
    a third of it is printing a constant, and the two controls above are tautologies (R15's
    unreachable-branch shape). The mutated feed is the PRE-ANCHOR world -- 4.93% against a 15.50%
    midpoint -- and the sentence is composed by the PRODUCER's own function, so this proves the
    door renders a reading and not a string this test handed it.

    Fires on: hard-coding either branch on the page; dropping the direction, which is the half a
    reader needs to know which way to discount everything below it.
    """
    from tools.generate_value_arms_data import _departure_statement

    feed = copy.deepcopy(_live_feed())
    dl = feed["departure_level"]
    for year in dl["years"]:
        year["world_pct"] = 4.93
        year["inside_band"] = False
    dl["all_inside_the_band"] = False
    dl["years_inside_the_band"] = 0
    dl["world_mean_pct"] = 4.93
    dl["statement"] = _departure_statement(4.93, 15.50, 0, len(dl["years"]), None)
    rendered = _render(feed)["arms-departure"]

    assert "OUTSIDE" in rendered, (
        "every year of this world sits outside the published band and the page does not say so")
    assert "reads HIGH" in rendered, (
        "the page states the size of the miss without its direction, so a reader cannot tell "
        "which way to discount the figures below: {}".format(rendered))
    assert "4.93%" in rendered
    assert rendered != _render(_live_feed())["arms-departure"], (
        "the page renders the SAME statement for a world inside the record's band and one at a "
        "third of it, so it is printing a constant and reads nothing from the measurement")


def test_MUTATION_a_level_that_could_not_be_MEASURED_still_bounds_the_page():
    """FAIL-OPEN, the shape R15 names first. A publish that cannot measure the world's departure
    level must leave a reader told the figures are unbounded on that dimension. Silence there
    reads exactly like a page whose figures needed no such qualification -- which is the state
    this page was in for its whole life before today.

    Fires on: rendering nothing when the block says `available: false`.
    """
    from tools.generate_value_arms_data import _DEPARTURE_UNAVAILABLE

    feed = copy.deepcopy(_live_feed())
    feed["departure_level"] = {
        "available": False,
        "reason": "the captured run could not be read",
        "statement": _DEPARTURE_UNAVAILABLE,
    }
    rendered = _render(feed)["arms-departure"]

    assert rendered.strip(), "a feed that could not measure the world rendered nothing at all"
    assert "COULD NOT BE ESTABLISHED" in rendered
    assert "unbounded" in rendered, (
        "the absence reached the reader without what it costs them: {}".format(rendered))
    assert "inside" not in rendered.lower(), (
        "an unmeasured world still rendered a verdict about the band")


def test_MUTATION_a_feed_with_NO_departure_block_at_all_still_bounds_the_page():
    """The other route into the same absence, and the one a stale producer takes. A feed written
    before this block existed carries no key at all, and the door must not fall through to silence
    on it."""
    feed = copy.deepcopy(_live_feed())
    feed.pop("departure_level", None)
    rendered = _render(feed)["arms-departure"]

    assert rendered.strip(), "a feed with no departure block rendered nothing at all"
    assert "COULD NOT BE ESTABLISHED" in rendered
    assert "unbounded" in rendered


def test_a_count_drawn_by_code_the_page_no_longer_runs_names_BOTH_trees(live):
    """THE MIDDLE STATE, and the normal one for any run longer than the landing cadence.

    An attributable count stays on the page. What changes is that the page names the tree that
    drew it AND the tree publishing it, instead of letting a reader assume they are the same.

    Fires on: collapsing this into either neighbour -- withholding an attributable count, or
    rendering a stale run as current.
    """
    feed = copy.deepcopy(_live_feed())
    counts = _book_counts(feed)
    feed["book"] = dict(counts, available=True, produced_by={
        "stated": True, "commit": "b" * 40, "short": "b" * 9,
        "publishing_tree_commit": "c" * 40,
        "produced_by_the_tree_it_publishes_from": False,
        "counts_are_labelled_by_the_code_that_made_them": True,
        "reading": "Produced at bbbbbbbbb and published from ccccccccc."})
    feed["producing_commit"] = feed["book"]["produced_by"]
    note = _text(_render(feed)["arms-note"])
    assert "{} settled billing accounts".format(
        counts["billing_accounts_settled_in_window"]) in note
    assert "code this page no longer runs" in note
    assert "bbbbbbbbb" in note and "ccccccccc" in note


# ── the standing rule: independence is not inference ─────────────────────────────────────────
#
# Director, 2026-08-30: "the belief-versus-truth gap may be published as a measurement, never as
# evidence of skill, and the two must not appear in one sentence without the null interval beside
# them. If the concordance sits inside its null, the page says WE CANNOT TELL, in those words."
#
# The interval half was already enforced above. These two are the words half, and they are a PAIR:
# one asserts the phrase appears when the reading is inside its null, the other that it disappears
# when the reading clears it. Either alone is satisfiable by a constant.


def test_a_reading_INSIDE_its_null_says_WE_CANNOT_TELL_where_a_reader_sees_it(live):
    """The phrase the director specified, in the rendered DOM, not in the feed.

    The page already printed the interval and the artefact's own reading -- "does not distinguish
    the method from chance in either direction" -- which is the same fact in language a reader
    carries away as a near-miss. A softer synonym is the defect: it moves the reader while every
    flag beside it says the figure is unusable.

    Fires on: dropping the `cannot_tell` render, or softening the phrase in
    `tools/inference_claim.CANNOT_TELL`.
    """
    msk = _live_feed().get("method_skill") or {}
    if not msk.get("cannot_tell"):
        pytest.skip("the live concordance clears its null; the other half of this pair covers it")

    rendered = live["arms-method"]
    assert "we cannot tell" in rendered.lower(), (
        "the concordance sits inside the interval a random signal produces and the page does not "
        "say we cannot tell, in those words")
    # And the numbers are in the same breath as the phrase, never the phrase alone.
    assert "{:.3f}".format(msk["concordance"]) in rendered
    assert "{:.3f}".format(msk["null_95_low"]) in rendered


def test_a_reading_that_CLEARS_its_null_does_not_say_it():
    """THE OTHER HALF OF THE NULL. A caveat that renders unconditionally is a constant, and a
    constant caveat teaches a reader to skip the one that matters.

    Driven through the door with a concordance well outside its own interval, because the live
    run is in the other branch and a test that can only see one branch is a test of today's run.

    AND `inside_the_null` IS LEFT STALE AT TRUE ON PURPOSE. The sentence is computed by
    `tools/inference_claim.cannot_tell_sentence` from the three numbers; the flag beside it is one
    more thing that can rot, and a page that re-derives the verdict from the flag would print the
    caveat over a reading that clears its own null. Setting the two to disagree is the only way to
    tell which one the page is actually reading.

    Fires on: rendering `cannot_tell` from `msk.inside_the_null` rather than from the computed
    sentence. Rendering it UNCONDITIONALLY does NOT fire and that is an equivalence, not a gap:
    `prose(null)` is the empty string, so an always-true branch emits an empty paragraph and no
    phrase. Established rather than assumed.
    """
    feed = copy.deepcopy(_live_feed())
    msk = feed.get("method_skill") or {}
    if not msk.get("available"):
        pytest.skip("the live feed carries no method-skill reading to drive")
    msk.update({"concordance": 0.94, "null_95_low": 0.133, "null_95_high": 0.867,
                "inside_the_null": True, "cannot_tell": None})

    rendered = _render(feed)["arms-method"]

    assert "0.940" in rendered, "the driven reading did not reach the page at all"
    assert "we cannot tell" not in rendered.lower(), (
        "the page says we cannot tell about a reading that clears its own null, which makes the "
        "phrase a constant rather than a verdict")


# ── the OTHER leg: independence, and whether it reaches anyone ────────────────────────────────
#
# The pair above enforces leg TWO of the standing rule -- "can the method's ranking be told from
# chance". On 2026-08-31 a reader-side check found that leg ONE reached no published surface at
# all: `tools/couple_value_based_pricing` composed the whole verdict -- `sides_are_independent`,
# `the_method_clears_its_null`, `publishable_as_evidence_of_skill` and the sentence derived from
# them -- into `docs/observability/value_based_pricing_arms.json`, and nothing under `site/` reads
# that file. Worse, the committed copy of it predated `tools/inference_claim` and carried no
# verdict at all. So the page could say "we cannot tell whether the method works" while saying
# nothing about whether the two sides were even arrived at independently, which is the leg the
# director's own instance-of-the-rule was written about.
#
# These three are the reader-side control that this cannot silently recur.


def test_the_INDEPENDENCE_verdict_reaches_the_reader_and_not_only_the_skill_leg(live):
    """The composed verdict, in the rendered DOM of the published door.

    A guard that fails closed into an observability file nobody reads has not failed closed on the
    surface, which is what CLAUDE.md's rule asks for: "'we cannot tell' is a result, it belongs on
    the page, not in a footnote."

    Fires on: dropping the `inference_claim` render from `site/capabilities/index.html`, or
    dropping the block from `tools/generate_value_arms_data.build`.
    """
    claim = _live_feed().get("inference_claim") or {}
    assert claim.get("sentence"), (
        "the published feed carries no `inference_claim.sentence`, so the standing rule's verdict "
        "reaches no reader -- which is the exact defect this control exists for")

    rendered = live["arms-inference"]
    # Compared CLAUSE BY CLAUSE rather than whole-string: the door's `prose()` turns " -- " into
    # an em dash before assigning, so a whole-sentence `in` test reports a correct page red. The
    # clauses are split on the same separator the door rewrites, so every one of them is checked.
    for clause in (c.strip() for c in claim["sentence"].split(" -- ")):
        assert _text(clause) in rendered, (
            "the standing rule's verdict is in the feed and not on the page: {!r} is missing"
            .format(clause[:80]))


def test_the_page_prints_the_verdict_it_is_GIVEN_and_never_one_it_composes(live):
    """THE BRANCH. Driven with the OPPOSITE verdict, because the live run is in one branch and a
    control that can only see one branch is a control over today's answer.

    `tools/inference_claim._sentence` derives the prose from the flags so the two cannot disagree;
    the risk this catches is the page re-deriving prose of its own from `sides_are_independent`,
    which would give one claim two authors and let the page assert what the flag beside it denies.
    So the flags are left at the LIVE values and only the sentence is swapped: a page composing
    its own text would print the live branch and fail.

    Fires on: rendering a hand-written sentence chosen from `ic.sides_are_independent` rather than
    rendering `ic.sentence`.
    """
    feed = copy.deepcopy(_live_feed())
    claim = feed.get("inference_claim") or {}
    if not claim.get("sentence"):
        pytest.fail("the live feed carries no verdict to drive")
    claim["sentence"] = ("The two sides descend from one source, so the gap is two fits of one "
                         "series and we cannot tell whether the company inferred anything.")

    rendered = _render(feed)["arms-inference"]

    assert "descend from one source" in rendered, (
        "the driven verdict did not reach the page, so the page is printing prose of its own")
    assert "removes the objection that we were measuring our own reflection" not in rendered, (
        "the page printed the live branch's wording over a driven verdict that says the opposite")


def test_the_counts_a_reader_SEES_have_a_machine_readable_companion_beside_them():
    """THE PROSE FIGURE AND ITS STRUCTURED FORM, on the same published surface.

    Until 2026-08-31 `tools/generate_value_arms_data._inference_claim` published only the CLAUSE
    off the front of the distance reading, so `inference_claim.accuracy` read `null` in the feed
    while the sentence a reader gets carried live counts ("4 of 6 years, by up to 16.5pp"). A
    figure a reader can see and nothing downstream can check is the shape this project keeps
    paying for: no door, no drift check and no consumer could establish that the sentence's
    numbers were the guard's numbers, so the sentence was the only source for its own figures.

    THE KEY IS ASSERTED PRESENT EVEN WHEN NULL, and that is the fail-closed half. An unreachable
    guard publishes `record_distance: None` with the reason in `why`; a publisher that dropped the
    block publishes nothing. Those are different facts and only one is a defect, so a missing key
    is the failure and a null value on an unavailable claim is not.

    Fires on: reverting the publisher to `...get("clause")`, or renaming the key without moving
    the reader-facing counts with it.
    `docs/design/THE_ACTED_BELIEF_IS_A_BOOK_QUANTITY_2026-08-31.md`.
    """
    claim = _live_feed().get("inference_claim") or {}
    assert "record_distance" in claim, (
        "the published feed carries no `inference_claim.record_distance`, so the counts in the "
        "rendered sentence have no machine-readable companion and nothing can check them")
    if not claim.get("available"):
        assert claim["record_distance"] is None
        return
    distance = claim["record_distance"]
    assert isinstance(distance, dict), (
        "`record_distance` published as {!r} on an AVAILABLE claim -- an available guard that "
        "cannot say how far the belief sits from the record is not available".format(distance))
    # THE REFUSAL TRAVELS WITH THE NUMBERS. A consumer that reads `years_outside` and
    # `max_distance_pp` without `accuracy_reading_available` beside them would reconstruct exactly
    # the reading the 2026-08-31 determination withdrew.
    assert distance["accuracy_reading_available"] is False
    assert distance.get("why_no_accuracy_reading")
    if distance.get("applies"):
        # And the structured counts ARE the counts in the prose, not a second source for them.
        assert "{} of {}".format(distance["years_outside"], distance["years_checked"]) in \
            claim["sentence"], (
            "the sentence's counts and the structured companion disagree, which is the two-source "
            "defect the companion was published to close")


def test_the_verdict_SURVIVES_a_run_that_carries_no_method_skill_reading():
    """THE FAIL-OPEN THE OBVIOUS PLACEMENT WOULD HAVE CREATED.

    Both `method_skill` branches in the door assign `arms-method.innerHTML`, and a run whose
    artefact carries neither assigns nothing at all. Rendering the verdict into that same element
    would delete it exactly when the page has least to stand on -- an artefact-less run is when
    "we cannot tell whether this is evidence of anything" matters most, and it is also when it
    would have vanished. The verdict does not depend on that artefact and must not share its
    lifetime, which is why it has an element of its own.

    Fires on: moving the `inference_claim` render into `arms-method`, or inside the
    `if (msk.available)` branch.
    """
    feed = copy.deepcopy(_live_feed())
    claim = feed.get("inference_claim") or {}
    if not claim.get("sentence"):
        pytest.fail("the live feed carries no verdict to drive")
    feed["method_skill"] = {"available": False, "withheld": False}

    rendered = _render(feed)["arms-inference"]

    for clause in (c.strip() for c in claim["sentence"].split(" -- ")):
        assert _text(clause) in rendered, (
            "a run with no method-skill artefact loses the standing rule's verdict as well, so "
            "the page falls silent about what it may claim precisely when it can claim least")


def test_the_world_these_figures_were_measured_in_reaches_the_reader_before_the_number(live):
    """The world caveat must reach the RENDERED page, ahead of the advantage it qualifies.

    THE DEFECT (2026-09-03). The published beat -- the per-customer arm earning £12,071 more than
    flat rules -- was measured 2026-08-31. `simulation/departure_level_anchor.py` has been
    re-fitted twice since, and on the arms' own capture population that swap moves whole-book
    expected departure +19.06pp summed across 2017-2024 against published bands 0.5-3.6pp wide.
    Departure rate is how much book there is to win or lose, so it is the surface the whole
    comparison sits on. Every control on the feed passed; none could express "the world this was
    measured in is not the world".

    THE SUBJECT IS THE DOM AND POSITION IS PART OF THE CLAIM. A reader who meets £12,071 and
    learns three paragraphs later that it describes a superseded world has already taken the
    figure as current -- so this asserts the caveat renders BEFORE the advantage, not merely
    that it renders. Same shape, and same reason, as the error-bar rung above.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. It reads the feed's own verdict and asserts
    whichever case that verdict is in, so the day the arms are re-run in the live world this goes
    green on the ABSENCE of the caveat rather than reddening on a page that became more honest --
    the failure `test_the_error_bar_says_the_instrument_cannot_resolve_it` above records.

    Fires on: dropping the clause from the headline; appending it after the advantage instead of
    before it; or rendering the feed's `world_provenance` refusal as silence.
    """
    feed = _live_feed()
    wp = feed.get("world_provenance") or {}
    rendered = live["arms-headline"]
    assert rendered.strip(), "the door rendered nothing where the headline goes"

    current = wp.get("available") is True and wp.get("superseded") is False
    if current:
        assert "READ THIS AS HISTORY" not in rendered, (
            "the page told a reader to read a CURRENT run as history -- the caveat is a constant, "
            "not a reading of the run's own world stamp")
        return

    # KEYED TO THE PROPERTY, NOT TO THE SENTENCE. There are two ways not to be current and they
    # get different words: every leg stale in ONE world is history, whereas a live figure bounded
    # by a spread from another world is `c30b98048` and must NOT be called history. Pinning this
    # rung to the history wording alone would go red on the day the page became more precise --
    # exactly backwards, and the failure this file already records one rung above.
    lead = ("THE FIGURE BELOW AND THE BOUND ON IT WERE MEASURED IN DIFFERENT WORLDS"
            if wp.get("one_world_across_every_figure") is False else "READ THIS AS HISTORY")
    assert lead in rendered, (
        "the feed says these figures were not measured in the live world ({}), and a reader met "
        "no such statement".format(str(wp.get("reason", ""))[:160]))
    # POSITION IS THE CLAIM. The caveat must precede the money, or it is a footnote.
    caveat_at = rendered.index(lead)
    money = re.search(r"£[\d,]{4,}", rendered)
    assert money is not None, "the headline states no figure at all -- the deletion branch"
    assert caveat_at < money.start(), (
        "the world caveat rendered AFTER the figure it qualifies, so a reader meets the number "
        "first: " + rendered[:200])
    # SUPERSEDED-WITH-PROVENANCE, NOT DELETION. The honestly-measured figures stay on the page.
    # RE-KEYED 2026-09-04, to the FIGURE and not to the direction. This asserted "MORE than flat
    # rules" -- a DIRECTIONAL claim, present only while an unstamped bound was licensing one. The
    # property is that the superseded comparison is dated rather than deleted, and the figure is
    # what carries it; the direction is a separate claim the page may withdraw for good reason,
    # and on 2026-09-04 it did, because that bound's floor names no world. A control pinned to
    # the direction goes red for the page becoming MORE honest, which is exactly backwards.
    assert _superseded_advantage_rendered(rendered), (
        "the superseded comparison was removed rather than dated -- deletion is not the "
        "correction, and a reader can no longer size what the world change cost")


def _superseded_advantage_rendered(rendered: str) -> str:
    """The superseded run's own advantage figure as the page renders it, or `""` if it is gone.

    READ FROM THE FEED, NEVER TYPED, and read as a NUMBER rather than as the sentence around it.
    Two rungs here asserted "MORE than flat rules" to mean "the 2026-08-31 comparison is still on
    the page". That string is a DIRECTION, and the page states a direction only while a bound has
    earned one -- so on 2026-09-04, when the bound behind it turned out to come from a floor that
    names no world and the direction was properly withdrawn, both rungs went red for the page
    becoming more honest. Deletion and withdrawal-of-a-direction are different acts and only the
    first is the defect these rungs exist for.

    FAIL-CLOSED. A feed with no superseded split returns `""`, and every caller treats that as the
    figure being absent -- an unreadable feed must not read as a page that kept its figures.
    """
    figure = ((_live_feed().get("realised") or {}).get("split") or {}).get("value_advantage_gbp")
    if not isinstance(figure, (int, float)):
        return ""
    money = "£{:,.0f}".format(abs(figure))
    return money if money in rendered else ""


def test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved(live):
    """The current-world contrast must render, and it must render UNBOUNDED and say so.

    THE DEFECT (2026-09-03). The arms were re-run over the departure level this world runs at
    today (`value_cycle_ab_s1_three_arm_20260903.json`, world `39a192ce04c1eda8`), and the page
    published only the 2026-08-31 figures under a "read this as history" headline. So the page
    held the one figure that WAS current and told the reader nothing about it -- withholding is
    not the correction, dating is.

    AND THE OPPOSITE FAILURE IS WORSE. The floor legs for this world are still running, so the
    only noise floor on disk was measured in the superseded world. Publishing the new contrast
    with the old bound -- or with any verdict derived from it -- is `c30b98048` exactly: "the
    bound that decided 'cannot resolve' was measured in another world". £2,335.87 over the old
    ±£2,291.07 is 1.02x, and that ratio is not a quantity, because the two numbers count
    departures at two different rates. **A page that printed it would look more rigorous and be
    less true**, which is why the refusal is asserted here and not left to review.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. The figure is read from the feed, never typed,
    so this rung does not go red when the arms are re-run again. `bound_available` drives which
    branch is asserted, so the day the floor legs land in this world and the page states a real
    verdict, this rung follows the feed rather than reddening on a page that became MORE
    resolved. And when no current-world run exists at all, it asserts the page makes no claim
    about now -- the fail-closed leg, which is the state the page was in before this landed.

    Fires on: dropping `_current_world_clause` from the headline; publishing the current figure
    without its refusal; deriving a "clears / does not clear" verdict for it from the superseded
    floor; or deleting the superseded figures instead of dating them.
    """
    feed = _live_feed()
    cw = feed.get("current_world") or {}
    rendered = live["arms-headline"]
    assert rendered.strip(), "the door rendered nothing where the headline goes"

    if not cw.get("available"):
        # FAIL CLOSED. No run in the live world means the page may not speak about now at all.
        assert "IN THE WORLD AS IT IS NOW" not in rendered, (
            "the page made a statement about the world as it is now while the feed says no run "
            "in that world was readable ({})".format(cw.get("why_not")))
        return

    advantage = cw.get("value_advantage_gbp")
    assert isinstance(advantage, (int, float)), (
        "the current-world block is available and carries no advantage figure, so the page has "
        "nothing to state and the availability flag is fail-open")
    # READ FROM THE FEED, NEVER TYPED. A hardcoded "£2,336" is true when written and cannot
    # notice the next re-run -- the shape this whole claim exists to remove.
    money = "£{:,.0f}".format(advantage)
    assert money in rendered, (
        "the feed carries a contrast measured in the LIVE world ({} at {}) and a reader met no "
        "such figure; the page published only the superseded run".format(
            money, cw.get("generated_at")))

    # THE DATE IS ON THE SURFACE, because "the world as it is now" is not something a reader can
    # place and "measured 2026-09-03" is. This is the direction's own done-condition.
    when = cw.get("generated_at")
    assert when and when in rendered, (
        "the current-world figure rendered without the date it was measured on, so a reader "
        "cannot tell how current 'current' is")

    if cw.get("bound_available"):
        # A BOUND BUYS A VERDICT *OR* A NAMED REASON THERE IS NONE -- never silence, and never a
        # bare verdict. This rung asserted `resolved is not None` outright until 2026-09-03, which
        # was keyed to TODAY'S ANSWER ("a bound implies a verdict") rather than to the property.
        # It went red the day the page became MORE honest -- withholding a verdict its own floor's
        # re-draws reverse -- which is this project's own named backwards-control shape. The
        # property is that the reader is never left to infer the verdict's absence.
        withheld = cw.get("verdict_withheld_because")
        assert cw.get("resolved") is not None or withheld, (
            "the feed claims a bound for the current world, states no verdict from it, and gives "
            "no reason -- 'no bound', 'did not clear' and 'the verdict is one draw's' are three "
            "different states and a reader meets them as one")
        if withheld:
            # THE WITHHOLDING MUST REACH THE READER, with the range that reverses it. A payload
            # that withholds while the page still prints CLEARS is the fail-open this whole rung
            # exists for, pointed the other way.
            assert "STATES NO VERDICT" in rendered, (
                "the feed withheld the verdict ({}) and the page did not tell the reader"
                .format(withheld[:120]))
            assert "CLEARS" not in rendered, (
                "the feed withheld the verdict and the page still states one")
            stability = cw.get("verdict_stability") or {}
            for edge in ("redraw_min_gbp", "redraw_max_gbp"):
                figure = stability.get(edge)
                assert isinstance(figure, (int, float)), (
                    "the verdict was withheld for a range the feed does not carry, so the reason "
                    "is unfalsifiable")
                assert "£{:,.0f}".format(figure) in rendered, (
                    "the page withheld the verdict without showing {} -- the reader is told there "
                    "is no verdict and not what reverses it".format(edge))
            return
        # AND THE VERDICT MUST REACH THE READER. A feed that resolves while the page still prints
        # the refusal is the same fail-open one step along: the reader meets "STATES NO VERDICT"
        # under a figure the site has in fact bounded.
        assert "STATES NO VERDICT" not in rendered, (
            "the feed holds a bound measured in this world and the page still tells the reader it "
            "has none")
        stdev = (cw.get("bound") or {}).get("stdev_gbp")
        assert isinstance(stdev, (int, float)), (
            "the feed claims a bound and carries no spread to show, so the verdict is unfalsifiable")
        assert "£{:,.0f}".format(stdev) in rendered, (
            "the verdict rendered without the spread it was decided against, so a reader must "
            "take the gate on trust rather than check it")
        assert ("CLEARS" in rendered) is bool(cw.get("resolved")), (
            "the rendered verdict disagrees with the feed's `resolved`")
        # THE SMALLER CLAIM IS SAID OUT LOUD. This figure can clear its floor while being a fifth
        # of the superseded one, because the floor fell further than the advantage did. A bare
        # "clears" lets a reader take a collapse for a win, which is the direction's own warning
        # about a result that moves the flattering way.
        assert "SMALLER advantage" in rendered, (
            "the current-world verdict rendered without saying the advantage SHRANK between "
            "worlds, so a page that resolved a collapsed figure reads as the company improving")
        return

    # NO BOUND MEANS NO VERDICT, AND THE PAGE MUST SAY SO BESIDE THE FIGURE -- not below it, and
    # not only in the feed. An unbounded figure published bare reads as resolved.
    assert "STATES NO VERDICT" in rendered, (
        "the current-world figure rendered with no bound and no statement that it has none, so "
        "a reader meets it as though it were resolved")
    assert cw.get("resolved") is None, (
        "the feed states a verdict on a figure it holds no same-world bound for; `resolved` must "
        "be None -- 'not measured' and 'measured and did not clear' are different states")
    # THE RATIO THAT MUST NEVER BE FORMED. Both numbers are correct and their ratio is not a
    # quantity. Asserted on the rendered text because that is where it would do the damage.
    head, _, tail = rendered.partition(money)
    del head
    stated = tail[:400]
    assert not re.search(r"\d+(\.\d+)?\s*(x|×)\b", stated), (
        "the page priced the current-world figure as a multiple of a bound -- the only bound it "
        "holds was measured in the superseded world, which is the c30b98048 defect: " + stated[:180])

    # SUPERSEDED-WITH-PROVENANCE, NOT DELETION, and the current figure comes FIRST. The older run
    # stays on the page with its date; a reader who meets it first has taken it as the answer.
    # Keyed to the FIGURE and not to a direction -- see the sibling rung above for why.
    superseded = _superseded_advantage_rendered(rendered)
    assert superseded, (
        "the superseded comparison was deleted rather than kept beside the current one")
    assert rendered.index(money) < rendered.index(superseded), (
        "the superseded figure rendered ahead of the one measured in the live world")


def test_MUTATION_an_unbounded_current_figure_is_never_rendered_bare():
    """The rung above must red when the refusal is stripped from the clause but the figure stays.

    This is the mutation that matters, because it is the shape a well-meaning edit produces: the
    figure is the news, the caveat is long, and a page that keeps one and drops the other looks
    tidier and is the fail-open. Run against the builder rather than the door so it needs no
    browser, and asserted on the composed headline, which is what the door renders.
    """
    from tools import generate_value_arms_data as gvad

    # THE MODULE'S OWN PATHS, not a second copy of them here. A path written down twice is a path
    # that goes stale in one place, and this rung would then measure a file the page never reads.
    three_arm = json.loads(gvad.THREE_ARM_PATH.read_text(encoding="utf-8"))
    current = json.loads(gvad.CURRENT_WORLD_THREE_ARM_PATH.read_text(encoding="utf-8"))
    floor = json.loads(gvad.NOISE_FLOOR_PATH.read_text(encoding="utf-8"))
    built = gvad.build(three_arm, floor, None, None, current)
    headline = built["headline"]
    cw = built["current_world"]
    assert cw["available"], "the committed current-world artefact no longer names the live world"
    money = "£{:,.0f}".format(cw["value_advantage_gbp"])
    assert money in headline and "STATES NO VERDICT" in headline, (
        "the live builder does not put the current figure and its refusal in the headline "
        "together, so the rung above cannot be failed by separating them")

    # THE MUTATION: keep the figure, drop the refusal. The rung above must not survive it.
    #
    # EVERY OCCURRENCE, AND THE PUNCTUATION IS NOT PART OF THE SUBJECT (2026-09-04). This stripped
    # the phrase with a trailing colon and exactly once. Both facts were properties of the one
    # sentence the headline held when it was written: the clause now ends in a full stop, and the
    # headline carries TWO refusals, because the selection leg -- the only leg that could be value
    # created rather than moved -- gained its own bound and its own withheld verdict. A single
    # keyed replacement removed neither, and this rung's own last assertion is what caught it.
    mutated = headline.replace("THIS PAGE STATES NO VERDICT ON THAT FIGURE", "")
    assert money in mutated, "the mutation removed the figure too, so it tests nothing"
    assert "STATES NO VERDICT" not in mutated, (
        "the refusal survived its own removal -- the assertion in the rung above is satisfied by "
        "some other sentence, which makes it an equivalence rather than a control")


# ── can the company order who leaves ─────────────────────────────────────────────────────────
#
# THE READING THE WHOLE THESIS TURNS ON, and until 2026-08-31 it reached no reader. The claim
# under test is that the advantage comes from INFERENCE and never from ACCESS; the SVT route is
# the one population where that sentence is measurable, because the belief is formed after the
# roll, on a route it does not seed, and the world's own hazard is scored on the same rows. The
# reading moved 0.4691 -> 0.5482 per exposure-day against a ceiling of 0.6091 that clears, and
# it lived in two staging documents and a design note while `site/` carried only the superseded
# figure inside a lane-claim string.
#
# R15 -- the mutations, each run and reverted:
#   * publish `belief_auc` instead of `exposure_offset.belief_auc_per_exposure_day` ->
#     `test_the_superseded_uncorrected_reading_never_reaches_the_reader` reds. This is the one
#     that matters: the uncorrected figure CLEARS its null and reads "the belief orders who
#     leaves", and this project has already published that mistake once.
#   * drop the ceiling row from the render -> `test_the_belief_reaches_the_reader_beside_its
#     _ceiling_and_never_alone` reds.
#   * render `inside_the_null` with a two-branch ternary -> `test_an_arm_with_no_interval_renders
#     _unknown_and_never_the_flattering_reading` reds.
#   * return early when `svt_drift_belief.available` is false ->
#     `test_an_unavailable_reading_renders_its_reason_and_never_an_empty_block` reds.
# The null rung is `test_a_reading_that_clears_its_null_is_not_reported_as_cannot_tell`: it must
# stay green throughout, because every mutation above is about what a reader meets and none of
# them is about a belief that actually works.


def _svt(feed: dict) -> dict:
    block = feed.get("svt_drift_belief") or {}
    if not block.get("available"):
        pytest.fail("the live feed carries no SVT belief reading ({}), reported as a failure "
                    "and never skipped".format(block.get("why")))
    return block


def test_the_belief_reaches_the_reader_beside_its_ceiling_and_never_alone(live):
    """A belief's AUC means nothing without the one a perfect reader of this world would reach.

    0.548 looks like a result on its own and is a failure against a ceiling of 0.609 that clears.
    Both figures, on the page, or the reading is not published.

    Fires on: dropping the ceiling row, or rendering the arms without it.
    """
    block = _svt(_live_feed())
    rendered = live["arms-svt-belief"]
    belief = block["arms"][0]

    assert "{:.4f}".format(belief["per_exposure_day"]) in rendered, (
        "the company's belief about the route carrying most of its departures is not on the page")
    assert "{:.4f}".format(block["ceiling"]) in rendered, (
        "the belief is published without the ceiling it is a failure against, so a reader cannot "
        "tell a shortfall from a result")
    assert "{:.4f}".format(block["ceiling_null_low"]) in rendered, (
        "the ceiling is published without the interval that makes it a signal rather than a "
        "number")


def test_a_ceiling_verdict_whose_world_is_unknown_is_withheld_where_the_reader_sees_it(live):
    """A RESOLVED DIRECTION MAY NOT BE READ OFF AN ARTEFACT THAT NAMES NO WORLD.

    THE DEFECT. `svt_drift_belief_grade.json` carries neither `world_identity` nor
    `generated_at`. The page rendered `ceiling_clears` from it as a green "the signal is there"
    -- a resolved direction -- two paragraphs under a headline stating that no direction on this
    page may be read as resolved, because the departure level decides how much signal there is
    to find and this grade cannot say which level it was measured over. Every other bound on
    this page was made to name its world on 2026-09-04; this block was the one left, and it is
    the one that RESOLVES rather than refuses, so it failed open in the flattering direction.

    THE THIRD STATE IS THE POINT. Withholding the verdict as `False` would render "no signal
    established", which reads as a grading that came back empty. It did not come back empty --
    it was never placed in a world. The two must not collapse.

    Fires on: restoring the two-branch ternary in `arms-svt-belief` (the null then renders as
    "no signal established"); dropping `ceiling_verdict_withheld_because` from the render;
    or publishing `clears_the_null` unconditionally in `_svt_drift_belief`.

    WHAT THIS DELIBERATELY DOES NOT ASSERT, so nobody re-adds it: that the ceiling and its
    interval survive the withholding. Blanking that row reds
    `test_the_belief_reaches_the_reader_beside_its_ceiling_and_never_alone` above -- verified by
    mutation, not assumed -- and a second control over one property is the duplication this
    repository names as a defect in its own right.
    """
    block = _svt(_live_feed())
    rendered = live["arms-svt-belief"]

    if block.get("measured_in_world"):
        pytest.skip("the grade now names world {}, so the verdict is legitimately stated and "
                    "this control has nothing to withhold".format(block["measured_in_world"]))

    assert block["ceiling_clears"] is None, (
        "the grade names no world, so the ceiling's DIRECTION must be withheld as None -- "
        "False would say the ceiling was graded and did not clear, which is a different claim")
    assert "the signal is there" not in rendered, (
        "the page states a resolved direction off a grade that cannot say which world it was "
        "measured in -- the exact reading the headline above it refuses")
    assert "no signal established" not in rendered, (
        "the withheld verdict rendered as a grading that came back empty; 'we cannot say which "
        "world this was graded in' and 'it does not clear' are different states")
    assert "world unknown" in rendered.lower(), (
        "nothing in the verdict cell tells a reader the direction was withheld")
    assert "names no world" in rendered.lower(), (
        "the verdict is withheld and the reason is not on the page beside it, which is a "
        "refusal a reader cannot check")


def test_the_reading_inside_its_null_says_we_cannot_tell_where_a_reader_sees_it(live):
    """The director's words, on the surface, not in a footnote.

    "If the concordance sits inside its null, the page says we cannot tell, in those words."
    The belief reads 0.5482 inside [0.4125, 0.5866], so the page must say so.

    Fires on: rendering the table without the sentence, or softening the phrase.
    """
    block = _svt(_live_feed())
    rendered = live["arms-svt-belief"]

    assert block["arms"][0]["inside_the_null"] is True, (
        "this control assumes the belief still cannot be told from chance; if that changed, the "
        "reading is a FINDING and this test must be rewritten deliberately rather than deleted")
    assert "we cannot tell" in rendered.lower(), (
        "the belief sits inside its null and the page does not say we cannot tell, in those words")


def test_the_superseded_uncorrected_reading_never_reaches_the_reader(live):
    """THE MISTAKE THIS PROJECT HAS ALREADY MADE ONCE, and the reason the offset key is the only
    quotable one.

    The artefact carries a bare `belief_auc` of 0.6220 that CLEARS its null and reads "the belief
    orders who leaves", beside a per-exposure-day reading of 0.5482 that does not. Cap segments
    run 1-92 days, so the bare figure credits the belief with what the billing calendar was
    doing. `delivery.json.what_it_got_wrong` records the uncorrected 0.6054 having been published
    where the offset 0.4691 belonged.

    Fires on: publishing `belief_auc` in place of the offset reading.
    """
    rendered = live["arms-svt-belief"]
    route = (json.loads(
        (SITE.parent / "docs" / "observability" / "svt_drift_belief_grade.json")
        .read_text(encoding="utf-8")).get("per_route") or {}).get("svt_segment") or {}
    for arm in route.get("company_belief") or []:
        if not arm.get("available") or arm.get("belief_auc") is None:
            continue
        assert "{:.4f}".format(arm["belief_auc"]) not in rendered, (
            "the SUPERSEDED uncorrected reading for `{}` is on the page. It clears its null and "
            "the quotable one does not, so a reader meets the flattering half of a figure the "
            "artefact itself withdrew".format(arm.get("field")))


def test_an_arm_with_no_interval_renders_unknown_and_never_the_flattering_reading():
    """A missing bound is a third state, not a pass.

    An arm whose null could not be computed has not cleared anything. A two-branch ternary would
    print "orders who leaves" for it, which is the fail-open direction on the one figure this
    page exists to bound.

    Fires on: rendering `inside_the_null` with `v ? ... : ...`.
    """
    feed = copy.deepcopy(_live_feed())
    _svt(feed)["arms"][0]["inside_the_null"] = None
    feed["svt_drift_belief"]["arms"][0]["null_95_low"] = None
    feed["svt_drift_belief"]["arms"][0]["null_95_high"] = None

    rendered = _render(feed)["arms-svt-belief"]

    assert "no interval" in rendered.lower(), (
        "an arm carrying no null renders no third state, so a reader cannot tell an unbounded "
        "reading from a bounded one")
    assert "orders who leaves" not in rendered.split("no interval")[-1].lower(), (
        "an arm with no interval is reported as having cleared one -- the fail-open reading")


def test_an_unavailable_reading_renders_its_reason_and_never_an_empty_block():
    """THE NULL RUNG FOR THE ABSENCE. An unavailable check is a failed check.

    A publish that could not produce the reading must say so with its reason. An omitted
    paragraph and a discharged caveat look identical to a reader, which is exactly how this
    reading went unpublished for a day in the first place.

    Fires on: returning early when `available` is false.
    """
    feed = copy.deepcopy(_live_feed())
    feed["svt_drift_belief"] = {
        "available": False,
        "why": "the belief grade artefact could not be read for this publish",
        "sentence": ("On whether the company can order who leaves the standard variable tariff, "
                     "we cannot tell: the artefact could not be read."),
        "arms": [],
        "ceiling": None,
    }

    rendered = _render(feed)["arms-svt-belief"]

    assert "we cannot tell" in rendered.lower(), (
        "an unproducible reading renders no verdict at all, so the page falls silent instead of "
        "failing closed")
    assert "could not be read" in rendered.lower(), (
        "the page reports an absence without its reason, so a reader cannot tell a broken "
        "producer from a belief nobody has built")


def test_a_reading_that_clears_its_null_is_not_reported_as_cannot_tell():
    """THE NULL RUNG. This block must be able to report a SUCCESS.

    A control that can only ever say "we cannot tell" is pinned to today's answer, not to the
    property -- it would stay green while the belief became genuinely good and go red for the
    right reason never. Driven with an arm moved above its own interval.
    """
    feed = copy.deepcopy(_live_feed())
    arm = _svt(feed)["arms"][0]
    arm["per_exposure_day"] = 0.7100
    arm["inside_the_null"] = False
    arm["cannot_tell"] = None
    feed["svt_drift_belief"]["sentence"] = (
        "The company's belief about who leaves the standard variable tariff clears the interval "
        "a signal carrying no information reaches.")

    rendered = _render(feed)["arms-svt-belief"]

    assert "0.7100" in rendered, "a belief that cleared its null does not reach the page"
    assert "orders who leaves" in rendered.lower(), (
        "a belief that clears its null is not reported as clearing it, so this block cannot "
        "publish a success and its failures mean nothing")
