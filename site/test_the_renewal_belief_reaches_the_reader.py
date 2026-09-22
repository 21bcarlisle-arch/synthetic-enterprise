"""The most direct test of this company's thesis must reach the RENDERED page.

THE DEFECT IT SERVES.
The mission says the company creates value by predicting the truth behind the SIM better than
average. On the renewal route -- where the priced per-customer decisions are actually made -- that
resolves to one question with one answer: does `company.crm.churn_model.estimate_churn_probability`
put the accounts that LEFT above the accounts that STAYED. It was graded on 2026-09-22 with a
2,000-permutation null, an oracle ceiling on the identical rows and a per-factor decomposition. The
belief reads 0.4988 inside [0.3829, 0.6241] -- the null's own median -- while the world's own hazard
on those same rows reads 0.7400 and clears. And it reached NO reader, because the artefact holding
it is `svt_drift_belief_grade.json` and the filename names the OTHER route.

That is a measurement that is correct, landed, tested and invisible, on the one claim this company
exists to test: the same shape `site/test_the_flat_churn_belief_reaches_the_reader.py` beside it was
written for, and the same sentence CLAUDE.md gives for it.

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE FEED. `value_arms.json` carrying
`renewal_churn_belief` proves nothing about whether a reader meets it. This drives the REAL door
through its own boot path with `site/_live_harness.mjs` and asserts on what the page put in the
element, against the PUBLISHED (index) bytes of both -- a door test that reads the working tree
cannot tell "the reader can see this" from "someone in this tree has fixed it and not landed it".

R15 -- WHAT MAKES EACH LEG ABLE TO FAIL. Every leg drives the door with a MUTATED feed and asserts
the rendered text follows it, so a page printing any of these as a literal reds on the mutation
while passing on the live feed:

  * drop the `#arms-renewal-belief` render, or leave the element at its placeholder ->
    `test_the_renewal_belief_reading_reaches_the_rendered_page` red.
  * hard-code the AUC, the interval or the ceiling ->
    `test_every_figure_in_the_block_is_the_FEEDS` red.
  * print the verdict sentence as a constant ->
    `test_the_cannot_tell_sentence_a_reader_meets_is_the_FEEDS` red, and its null control
    `test_a_belief_that_CLEARS_its_null_renders_the_other_words` is what stops the fix being
    "always print we cannot tell". That pair is the leg keyed to the PROPERTY and not to today's
    answer: on the day the belief starts ranking its departures the page must say so itself.
  * collapse the two claims into one -- publish the ceiling as the live world's signal --
    `test_the_live_world_claim_is_WITHHELD_with_its_reason` red. This is the load-bearing leg.
    "The belief did not order THESE departures while the world's hazard did" is a comparison of two
    orderings of one list and survives the capture's world; "there is this much signal to find" is
    a claim about a world this capture is not shown to have been taken in. A page that renders the
    second because it may render the first has published the flattering half of a split caveat.
  * render the within-capture verdict unconditionally ->
    `test_the_within_capture_verdict_is_read_from_the_feed_and_its_branches_are_reachable` red.
  * drop the join to the panel above ->
    `test_the_chain_to_the_flat_belief_reaches_the_reader` red. Adjacency alone would leave the
    reader to do the join, which is what the block above it already refuses.
  * quote the second grade's AUC, or omit that a second grade exists ->
    `test_the_second_grade_is_NAMED_and_none_of_its_figures_is_rendered` red. A rank statistic with
    no null is not a reading, and a second measurement a reader could find and this page did not
    mention is how a surface loses the right to be believed.
  * fail OPEN on an unreadable artefact (omit the paragraph rather than say so) ->
    `test_an_unavailable_reading_renders_its_REASON_and_never_an_omission` red.

THE NULL RUNG is `test_a_belief_that_CLEARS_its_null_renders_the_other_words`: it is the leg that
stays green on a page keyed to the property and reds on one that prints this book's answer. It is
stated as what it discriminates rather than flatteringly -- it does NOT establish that the live
reading is correct, only that the page is reading the feed's numbers to reach it.

The producer's own refusals -- the superseding-pointer refusal, the tautology guard, the missing
route -- are swept in `tests/tools/test_generate_value_arms_data.py`. This file drives mutated
FEEDS and structurally cannot reach them.
"""
from __future__ import annotations

import copy
import html as html_lib
import json
import re
import subprocess
from pathlib import Path

import pytest
from test_the_published_bytes_reader import (
    published_file,
    published_json,
    refuse_working_tree_reads,
)

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"

DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/value_arms.json"
GROWTH_REL = "site/data/book_growth.json"
CAPS_REL = "site/data/capabilities_door.json"
DD_ARMS_REL = "site/data/dd_opening_arms.json"

#: The element this file is about. Its own lifetime, beside the flat-belief panel it completes.
PANEL = "arms-renewal-belief"

#: The feed key. Named once so a rename moves one line rather than thirty.
BLOCK = "renewal_churn_belief"


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    """THE RELAPSE GUARD. Reads this file's own AST rather than my having been careful."""
    refuse_working_tree_reads(__file__, (DOOR_REL, FEED_REL, GROWTH_REL, CAPS_REL, DD_ARMS_REL))


def _prose(sentence: str) -> str:
    """The door's own `prose()`, mirrored -- INCLUDING what it does to the house-style dash.

    The feed is authored in the repository's plain-text style where an em dash is typed `--`, and
    the door typesets it before a reader sees it. `feed_string in rendered_text` is therefore a
    comparison against a string the page CANNOT emit for every sentence carrying one.
    """
    return re.sub(r"\s+", " ", sentence).replace(" -- ", " — ")


def _text(fragment: str) -> str:
    """What a READER sees: tags stripped, entities decoded, whitespace collapsed."""
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict, raw: bool = False) -> str:
    """Drive the real door with `feed` and return what `#arms-renewal-belief` shows.

    FAIL-CLOSED: a missing harness, an unresolved fetch, a script error or an element the page
    never wrote all raise here rather than degrading to an empty string a `not in` would pass on.

    `raw` returns the UNSTRIPPED innerHTML, for the one claim `_text` is blind to: this block's
    colour. Stripped to text, an amber finding and a grey aside are identical.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    payload = {
        "../data/value_arms.json": feed,
        "../data/dd_opening_arms.json": published_json(DD_ARMS_REL),
        "../data/book_growth.json": published_json(GROWTH_REL),
        "../data/capabilities_door.json": published_json(CAPS_REL),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(published_file(DOOR_REL))],
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
    element = out.get(PANEL) or {}
    html = element.get("innerHTML") or ""
    if raw:
        return html
    return _text(html) or _text(element.get("textContent") or "")


def _live_feed() -> dict:
    """The feed A READER GETS, which is the published one and not the one in this tree."""
    return published_json(FEED_REL)


def _mutate(**changes) -> dict:
    """The live feed with `renewal_churn_belief` fields replaced. Deep-copied, never in place."""
    feed = copy.deepcopy(_live_feed())
    block = feed.setdefault(BLOCK, {})
    for key, value in changes.items():
        block[key] = value
    return feed


@pytest.fixture(scope="module")
def live() -> str:
    feed = _live_feed()
    block = feed.get(BLOCK) or {}
    if not block.get("available"):
        pytest.fail(
            "the published renewal-belief grade is unavailable ({}), so the page renders no "
            "reading and the legs below cannot run".format(block.get("why")))
    return _render(feed)


@pytest.fixture(scope="module")
def live_block() -> dict:
    return _live_feed().get(BLOCK) or {}


def test_the_renewal_belief_reading_reaches_the_rendered_page(live, live_block):
    """A READER MEETS THE READING. The element is written, and it is written from the feed."""
    assert live, "the page rendered nothing into #{}".format(PANEL)
    assert _prose(live_block["sentence"]) in live, (
        "the rendered block does not carry the feed's own verdict sentence; a reader meets the "
        "panel without the reading it exists for.\nrendered: {}".format(live[:600]))


def test_every_figure_in_the_block_is_the_FEEDS(live_block):
    """MUTATE THE NUMBERS AND THE PAGE MUST FOLLOW. A literal reds here and passes on the feed.

    All four figures at once, deliberately: the defect this catches is a page that hard-codes what
    it saw once, and it does not hard-code one number at a time.
    """
    feed = _mutate(
        belief=dict(live_block["belief"], auc=0.1234, null_95_low=0.1111, null_95_high=0.2222),
        ceiling=dict(live_block["ceiling"], auc=0.9876, null_95_low=0.3333, null_95_high=0.4444),
    )
    rendered = _render(feed)
    for figure in ("0.1234", "0.1111", "0.2222", "0.9876", "0.3333", "0.4444"):
        assert figure in rendered, (
            "the page did not render the mutated figure {} -- it is printing a literal rather "
            "than the feed.\nrendered: {}".format(figure, rendered[:800]))
    # AND THE OLD ONES ARE GONE. A page that renders both is a page that appended.
    assert "{:.4f}".format(live_block["belief"]["auc"]) not in rendered
    assert "{:.4f}".format(live_block["ceiling"]["auc"]) not in rendered


def test_the_cannot_tell_sentence_a_reader_meets_is_the_FEEDS(live):
    """THE WORDS ARE THE FEED'S. A marked sentence the page cannot have authored."""
    marked = "MARKED SENTENCE THE PAGE COULD NOT HAVE AUTHORED"
    rendered = _render(_mutate(sentence=marked))
    assert marked in rendered, (
        "the page printed its own verdict sentence instead of the feed's, so a reader cannot be "
        "shown a correction the producer makes.\nrendered: {}".format(rendered[:600]))


def test_a_belief_that_CLEARS_its_null_renders_the_other_words(live_block):
    """THE NULL RUNG, AND THE PROPERTY KEY. The page must not print this book's answer.

    A control pinned to today's reading goes red when the code becomes more honest and stays green
    when the claim rots. This drives the door with a belief OUTSIDE its null and asserts the page
    stops saying "we cannot tell" -- which is what makes the live leg above evidence of anything.
    """
    clearing = dict(live_block["belief"], auc=0.9100, inside_the_null=False)
    # THE FACTOR VERDICTS ARE CLEARED TOO, and that is not a weakening of the leg. Three of the
    # four world factors legitimately read "we cannot tell" in their own column, so a bare
    # `not in rendered` would red on a correct page for a sentence this leg is not about -- the
    # "a control's own filters empty the evidence" shape, inverted. Driving a feed where the ONLY
    # possible source of those words is the belief row is what makes the assertion mean what it
    # says.
    # AND THE CEILING ROW IS CLEARED FOR THE SAME REASON AS THE FACTORS (2026-09-22). The comment
    # above enumerated the other sources of these words and neutralised them -- but it was written
    # when the ceiling CLEARED, so the ceiling row was not on the list. On the first re-capture in
    # the live world the ceiling stopped clearing (0.5911 inside [0.3620, 0.6380]) and began
    # rendering "we cannot tell" quite correctly, and this leg failed on a page that was right.
    # The rule the comment states is the one applied here: drive a feed in which the ONLY possible
    # source of the words is the belief row, and enumerate EVERY other source rather than the ones
    # that happened to be speaking on the day.
    feed = _mutate(
        belief=clearing,
        sentence="The company's belief about who leaves at renewal clears the interval a signal "
                 "carrying no information reaches.",
        within_this_capture="both_ordered_these_departures",
        ceiling=dict(live_block["ceiling"], auc=0.9500, clears_on_these_rows=True),
        factors=[dict(f, clears_its_null_alone=True) for f in live_block["factors"]])
    rendered = _render(feed)
    assert "we cannot tell" not in rendered.lower(), (
        "the page said 'we cannot tell' about a reading that CLEARS its null -- the words are a "
        "literal, not a reading of the numbers.\nrendered: {}".format(rendered[:800]))
    assert "clears the interval" in rendered
    assert "both the world and the company" in rendered.lower(), (
        "the within-capture verdict did not follow the feed onto its other branch")
    # AND THE COLOUR FOLLOWS. Amber qualifies; a finding rendered grey is a finding rendered
    # quietly, and stripped to text the two are identical.
    assert "var(--green)" in _render(feed, raw=True)


def test_the_within_capture_verdict_is_read_from_the_feed_and_its_branches_are_reachable(live):
    """FOUR STATES, EACH REACHABLE, AND THE LIVE ONE IS THE UNFLATTERING ONE.

    A verdict rendered unconditionally is not a verdict. Each of the four values the producer can
    emit must produce a different sentence, or the cell is decoration.
    """
    # ALL FOUR ARE DRIVEN, AND THE LIVE ONE IS CHECKED AGAINST ITS OWN DRIVEN TWIN (2026-09-22).
    # This opened by asserting the live verdict was "the world ordered its departures and the
    # company's belief did not" -- today's answer, written down. The first re-capture in the live
    # world moved it to the opposite corner and the leg failed on a page rendering the feed
    # perfectly. What this test is for is that the cell READS the feed; so every state is driven,
    # and the live feed's own value is asserted to render the same words its driven twin does.
    seen = {}
    for value in ("the_world_ordered_these_departures_and_the_belief_did_not",
                  "both_ordered_these_departures",
                  "neither_ordered_these_departures",
                  "the_belief_ordered_these_departures_and_the_world_did_not",
                  "cannot_be_stated"):
        seen[value] = _render(_mutate(within_this_capture=value))
    live_value = _live_feed().get(BLOCK, {}).get("within_this_capture")
    assert live_value in seen, (
        "the live block names a within-capture state this control cannot drive, so the words a "
        "reader actually meets are not under test here: {}".format(live_value))
    assert _text(seen[live_value]) == _text(live), (
        "the page a reader gets does not match the page this control drives from the feed's own "
        "verdict, so the rendered cell is not reading the feed.\nrendered: {}".format(live[:800]))
    assert len({_text(v) for v in seen.values()}) == 5, (
        "two of the five within-capture states rendered the same words, so the page is not "
        "reading the feed's verdict")
    assert "could not be stated" in seen["cannot_be_stated"].lower()


def test_the_live_world_claim_is_WITHHELD_with_its_reason(live, live_block):
    """THE LOAD-BEARING LEG. The two claims do not share a fate and the page must not merge them.

    The within-capture contrast is a comparison of two orderings of ONE list; it survives this
    capture having been taken in a different world. "There is this much signal in the live world to
    find" does not, because how much book there is to lose is what decides how much there is to
    find. The page must render the first and withhold the second, with the reason a reader can
    expand -- a refusal without its reason is the shape CLAUDE.md calls worse than no figure.
    """
    # WHICH HALF IS LIVE AND WHICH IS DRIVEN WAS SWAPPED ON 2026-09-22, and the premise this leg
    # named as the thing to watch for is exactly what happened: "if the grade has gained a world
    # this leg's premise has moved and the block must be re-read". The grade gained a world --
    # `39a192ce04c1eda8`, the live one, after the capture was re-taken -- so the WITHHELD state is
    # manufactured here and the RESOLVED state is read from the page a reader gets. The property
    # is unchanged: the two claims do not share a fate. Only which of them the live feed shows.
    withheld = _render(_mutate(
        ceiling_is_the_live_worlds_signal=None,
        measured_in_world=None,
        live_world_claim_withheld_because=(
            "THIS GRADE NAMES NO WORLD, so how much signal the live book holds is not stated."),
        world_gap={"2019": {"captured": 3.228064, "live": 6.637286,
                            "difference": 3.409222, "decisions": 124}}))
    assert "this grade names no world" in withheld.lower(), (
        "the page withheld the live-world claim without giving the reason.\nrendered: {}".format(
            withheld[:900]))
    assert "separate claim and it is not made here" in withheld.lower()
    # THE WITHIN-CAPTURE CLAIM IS STILL MADE in that same render. Dropping the caveat wholesale
    # and inheriting it wholesale are both wrong, and this is the half that must survive.
    assert "property of the list" in withheld.lower()
    # ...AND THE RESOLVED STATE IS REACHABLE TOO, so this is not a page that always refuses.
    named = _render(_mutate(ceiling_is_the_live_worlds_signal=False,
                            measured_in_world="39a192ce04c1eda8",
                            live_world_claim_withheld_because=None, world_gap=None))
    assert "separate claim and it is not made here" not in named.lower(), (
        "a grade taken in the live world still rendered the refusal, so the refusal is "
        "unconditional and establishes nothing")

    # AND THE LIVE PAGE RENDERS WHICHEVER OF THE TWO ITS OWN FEED DECLARES -- asserted against
    # that feed's `measured_in_world` rather than against either answer. Both "the capture agrees
    # with the live world" and "it does not" are legitimate states of this book: the first is what
    # a fresh capture gives, the second is what an ageing one gives, and a control that demanded
    # either would go red on the day the other became true. What must hold in both is that the
    # page's words follow the feed.
    if live_block["measured_in_world"]:
        assert live_block["live_world_claim_withheld_because"] is None
        assert "separate claim and it is not made here" not in live.lower(), (
            "the published grade names the live world and the page withheld the claim anyway")
    else:
        assert live_block["live_world_claim_withheld_because"], (
            "the page withholds the live-world claim without a reason a reader can check")
        assert _prose(live_block["live_world_claim_withheld_because"]) in live
        assert "separate claim and it is not made here" in live.lower()

    # ...AND THE THIRD STATE IS REACHABLE. A grade that names its world publishes the direction,
    # so this is not a page that always refuses.
    named = _render(_mutate(ceiling_is_the_live_worlds_signal=True,
                            measured_in_world="39a192ce04c1eda8",
                            live_world_claim_withheld_because=None))
    assert "also what there is to find today" in named.lower(), (
        "a grade taken in the live world still rendered a refusal, so the refusal is "
        "unconditional and establishes nothing")
    refusing = _render(_mutate(ceiling_is_the_live_worlds_signal=False,
                               measured_in_world="39a192ce04c1eda8",
                               live_world_claim_withheld_because=None))
    assert "no orderable signal is established" in refusing.lower()


def test_the_chain_to_the_flat_belief_reaches_the_reader(live, live_block):
    """THE JOIN IS STATED, NOT LEFT TO ADJACENCY -- which is the panel above's own rule."""
    chain = live_block.get("chain_to_the_flat_belief")
    assert chain, "the published feed carries no chain sentence, so the two panels are adjacent "\
                  "and nothing more"
    assert _prose(chain) in live, (
        "the chain joining this reading to the flat-belief panel above did not reach the "
        "page.\nrendered: {}".format(live[:900]))
    marked = "MARKED CHAIN SENTENCE THE PAGE COULD NOT HAVE AUTHORED"
    assert marked in _render(_mutate(chain_to_the_flat_belief=marked))
    # AND IT IS DROPPED, NOT INVENTED, when the other half could not be read.
    without = _render(_mutate(chain_to_the_flat_belief=None))
    assert _prose(chain) not in without


def test_the_signal_concentration_table_is_the_FEEDS_and_is_three_valued(live, live_block):
    """WHERE THE CEILING'S SIGNAL IS -- the decomposition that makes the chain an argument.

    Three states, not two: a factor the artefact carries no verdict for is not a factor that
    failed to clear, and a two-branch ternary prints the second for the first.
    """
    assert "sim_bill_shock_base" in live, (
        "the factor the route's signal is concentrated in did not reach the page")
    factors = copy.deepcopy(live_block["factors"])
    assert len(factors) >= 2, "the decomposition carries too few factors to be three-valued about"
    # THE THREE VALUES ARE DRIVEN, NOT READ OFF WHATEVER THE CAPTURE HAPPENED TO SAY (2026-09-22).
    # This asserted the LIVE table carried both a True and a False -- true of the superseded
    # capture, where bill shock cleared alone, and false of the first re-capture in the live world,
    # where not one factor clears its null alone. That is a fact about this book and not a defect
    # in the page, and a control that reds on it is pinned to yesterday's answer. What this test
    # is for is that the CELL renders three distinct words for three distinct verdicts.
    mixed = copy.deepcopy(factors)
    mixed[0]["clears_its_null_alone"] = True
    mixed[1]["clears_its_null_alone"] = False
    rendered_mixed = _render(_mutate(factors=mixed))
    assert "orders them alone" in rendered_mixed and "we cannot tell" in rendered_mixed.lower()
    unknown = copy.deepcopy(factors)
    unknown[0]["clears_its_null_alone"] = None
    assert "not stated" in _render(_mutate(factors=unknown)).lower(), (
        "a factor carrying no verdict rendered as one that failed to clear -- the flattering "
        "reading of a missing bound")


def test_the_reader_is_told_why_no_exposure_correction_is_applied_here(live, live_block):
    """TWO PANELS, TWO SCALES, AND THE PAGE SAYS WHY.

    The SVT panel one block down divides every figure by the days it was exposed for. Two panels of
    one instrument quoting on different scales with nothing saying why is how a reader concludes
    one of them forgot.
    """
    assert _prose(live_block["why_no_exposure_offset"]) in live, (
        "the page renders an uncorrected AUC beside a panel of per-exposure-day ones and never "
        "says why.\nrendered: {}".format(live[:900]))
    marked = "MARKED EXPOSURE EXPLANATION THE PAGE COULD NOT HAVE AUTHORED"
    assert marked in _render(_mutate(why_no_exposure_offset=marked))


def test_the_second_grade_is_NAMED_and_none_of_its_figures_is_rendered(live, live_block):
    """RECORDED, NOT MERGED, AND NEVER QUOTED. A figure with no null is not a reading.

    Both halves are legs. A page that hides the second grade denies a reader a measurement they
    could find; a page that quotes it publishes a rank statistic with no interval.
    """
    second = live_block.get("second_grade") or {}
    assert second.get("exists") is True, "the published feed cannot see the second grade"
    assert second.get("quotable_here") is False
    assert str(second["renewals"]) in live and str(second["departures"]) in live, (
        "the second grade was not named on the page, so a reader who finds it has found a "
        "measurement this page chose not to mention")
    assert _prose(second["why_not"]) in live
    assert _prose(second["never_averaged_because"]) in live
    # NO FIGURE FROM IT. The two AUCs that grade carries must not appear anywhere in the block.
    for forbidden in ("0.5340", "0.7618", "0.6596"):
        assert forbidden not in live, (
            "the page rendered {} -- a reading from a grade that carries no permutation "
            "null".format(forbidden))


def test_an_unavailable_reading_renders_its_REASON_and_never_an_omission():
    """FAIL-CLOSED, ON THE SURFACE. An absent account and a discharged one look identical.

    This is the leg that stays green when the FEED carries no reading and reds when the page
    invents one: "the artefact could not be read" and "the belief does not order who leaves" are
    the two states this block exists to keep apart.
    """
    feed = copy.deepcopy(_live_feed())
    why = "MARKED REASON: the belief grade artefact could not be read"
    feed[BLOCK] = {"available": False, "why": why, "sentence": "unused", "belief": None,
                   "ceiling": None, "factors": []}
    rendered = _render(feed)
    assert rendered, "an unavailable reading rendered NOTHING -- the paragraph was omitted, which "\
                     "is indistinguishable to a reader from the caveat being discharged"
    assert why in rendered, "the page did not say WHY the reading is missing.\nrendered: {}".format(
        rendered[:600])
    assert "could not be produced for this publish" in rendered
    # AND IT DOES NOT INVENT THE FINDING. No verdict, no figures.
    assert "we cannot tell:" not in rendered.lower()
    assert "the world ordered its departures" not in rendered.lower()


def test_the_finding_is_rendered_as_a_finding_and_not_as_a_grey_aside(live):
    """COLOUR IS A CLAIM. Amber qualifies; muted is a footnote, and stripped to text they match."""
    raw = _render(_live_feed(), raw=True)
    assert "var(--amber)" in raw, (
        "the reading rendered with no amber anywhere -- an unflattering finding styled as a "
        "footnote is a finding rendered quietly")
