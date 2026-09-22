"""The account of WHY the choosing has nothing to find must reach the RENDERED page.

THE DEFECT IT SERVES.
`/capabilities/` publishes a selection leg that is negative in all three of its re-draw families,
bounds it, and refuses it a sign. Every one of those is honest and none of them is an account:
a reader who meets "we cannot call the side" and leaves has been told the MEASUREMENT was
inconclusive, when the company's own churn model says where a conclusion would have had to come
from. `tools/churn_belief_size_response.py` measured that on 2026-09-22 and landed at 7179a7087 --
consumption reaches `estimate_churn_probability` through one term, `bill_stress`, identically zero
below a declared bill threshold, so the belief is EXACTLY flat in household size for 235 of this
book's 244 supply legs, over a book where the world's own churn response spans 11.57x in that same
dimension. Until this block the reading lived in `docs/observability/` and reached no reader.

That is the same shape `site/test_the_baseline_comparison_reaches_the_reader.py` and
`_svt_drift_belief` were built out of and the same one CLAUDE.md names: a measurement that is
correct, landed, tested and invisible is a measurement nobody is held by.

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE FEED. `value_arms.json` carrying
`churn_belief_size.reading` proves nothing about whether a reader meets it. This drives the REAL
door through its own boot path with `site/_live_harness.mjs` and asserts on what the page put in
the element, against the PUBLISHED (index) bytes of both -- a door test that reads the working
tree cannot tell "the reader can see this" from "someone in this tree has fixed it and not landed
it", which is the defect `site/test_the_published_bytes_reader.py` exists for.

R15 -- WHAT MAKES EACH LEG ABLE TO FAIL. Every leg below drives the door with a MUTATED feed and
asserts the rendered text follows it, so a page that printed the sentence as a literal would red
on the mutation while passing on the live feed:

  * print the reading as a constant instead of reading `churn_belief_size.reading` ->
    `test_the_reading_a_reader_meets_is_the_FEEDS_and_not_a_literal` red (it renders a marked
    sentence the page cannot have authored).
  * drop the `#arms-churn-belief-size` render, or leave the element at its placeholder ->
    `test_the_account_of_the_flat_belief_reaches_the_rendered_page` red.
  * render the block with the arms feed's own book counts, or with no population line ->
    `test_the_reader_is_told_this_is_NOT_the_book_the_arms_above_are_scored_over` red. This is the
    load-bearing leg: 244 supply legs rendered inside a section scored over 154 accounts, with
    nothing saying they are different books, is the "before dividing two numbers, say what each
    one counts" defect with the division left to the reader.
  * hard-code the spread, the leg counts or the knee ->
    `test_every_figure_in_the_block_is_the_FEEDS` red.
  * drop the unsourced-threshold caveat ->
    `test_the_unsourced_threshold_is_MARKED_where_a_reader_meets_it` red, and its null control
    `test_a_feed_that_establishes_its_threshold_renders_NO_caveat` is what stops the fix being
    "always print a warning".
  * render the asymmetry verdict unconditionally ->
    `test_the_asymmetry_verdict_is_read_from_the_feed_and_BOTH_branches_are_reachable` red. The
    three-way segment column has the same shape: `world_reads_their_own_bill` null is "not
    stated", which is not "no".
  * fail OPEN on an unreadable artefact (omit the paragraph rather than say so) ->
    `test_an_unavailable_reading_renders_its_REASON_and_never_an_omission` red.

THE NULL RUNG is `test_an_unavailable_reading_renders_its_REASON_and_never_an_omission`, and what
it discriminates is stated precisely rather than flatteringly: it is the leg that stays green when
the FEED carries no reading and reds when the page invents one, because "the artefact could not be
read" and "the belief is flat" are the two states this block exists to keep apart. It reds along
with everything else on the mutation that deletes the element -- correctly, and it is not evidence
of anything: a page with no block at all is not one of the two states it tells apart.

THE SWEEP, RUN 2026-09-22 BEFORE THIS FILE LANDED. Seven mutations of the render, each caught by
the leg written for it: deleting the assignment (12 legs red), printing the reading as a literal
(3 -- the two neighbours read the same sentence and say so), rendering the asymmetry verdict
unconditionally (1), dropping the population caveat (1), collapsing the three-valued segment
column to two branches (1), styling the finding muted instead of amber (1), and dropping the
unsourced-threshold caveat (1). The producer's own refusals are swept in
`tests/tools/test_generate_value_arms_data.py` -- this file drives mutated FEEDS and structurally
cannot reach them.
"""
from __future__ import annotations

import copy
import html as html_lib
import json
import math
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

# THE SUBJECTS, AS PATHS IN GIT AND NOT FILES ON DISK. Same reason as every other door test here;
# the argument is in `site/test_the_published_bytes_reader.py` rather than paraphrased.
DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/value_arms.json"
GROWTH_REL = "site/data/book_growth.json"
CAPS_REL = "site/data/capabilities_door.json"
DD_ARMS_REL = "site/data/dd_opening_arms.json"

#: The element this file is about. One element, one lifetime -- see the door's own comment for why
#: it sits under the error bar rather than inside it.
PANEL = "arms-churn-belief-size"


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    """THE RELAPSE GUARD. Reads this file's own AST rather than my having been careful."""
    refuse_working_tree_reads(__file__, (DOOR_REL, FEED_REL, GROWTH_REL, CAPS_REL, DD_ARMS_REL))


def _prose(sentence: str) -> str:
    """The door's own `prose()`, mirrored -- INCLUDING what it does to the house-style dash.

    THE DEFECT THIS AVOIDS, and it is the same one `_gbp` in
    `site/test_the_baseline_comparison_reaches_the_reader.py` was written for. The feed is authored
    in the repository's plain-text style, where an em dash is typed `--`; the door typesets it to a
    real em dash before a reader sees it. So `feed_string in rendered_text` is, for every sentence
    carrying a dash, a comparison against a string the page CANNOT emit -- and the artefact's
    `reading` carries three of them. A leg written that way reds on a correct page.
    """
    return re.sub(r"\s+", " ", sentence).replace(" -- ", " — ")


def _esc(sentence: str) -> str:
    """The door's own `esc()` then `prose()`, for the legs that read RAW markup.

    Deliberately NOT `html.escape`: that escapes the apostrophe as well, and this feed's sentences
    are full of them. Mirroring the four characters the door actually replaces is the difference
    between asserting on the page's bytes and asserting on a plausible guess at them.
    """
    for char, entity in (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;")):
        sentence = sentence.replace(char, entity)
    return sentence.replace(" -- ", " &mdash; ")


def _kwh(value: float) -> str:
    """The page's own kWh rounding, mirrored -- and JavaScript does not round the way Python does.

    `toLocaleString` rounds a half AWAY FROM ZERO (20000.5 -> 20,001) and `round()` rounds a half
    to EVEN (20000.5 -> 20000). The live artefact's knee at £150/MWh is exactly 20000.5, so a leg
    built on `round()` would red on a page rendering the correct figure -- a control disagreeing
    with its subject on the one input the data happens to occupy, which is the shape the sibling
    door test's `_gbp` docstring records.
    """
    return "{:,}".format(int(math.floor(float(value) + 0.5)))


def _text(fragment: str) -> str:
    """What a READER sees: tags stripped, entities decoded, whitespace collapsed.

    The door escapes every feed string through its own `esc()` before assigning, so asserting
    against raw innerHTML is how a correct page gets reported red.
    """
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict, raw: bool = False) -> str:
    """Drive the real door with `feed` and return what `#arms-churn-belief-size` shows.

    FAIL-CLOSED: a missing harness, an unresolved fetch, a script error or an element the page
    never wrote all raise here rather than degrading to an empty string that a `not in` assertion
    would happily pass on.

    `raw` returns the UNSTRIPPED innerHTML, and it exists for the one claim `_text` is blind to:
    this block's colour. Amber qualifies, muted footnotes, and stripped to text the two are
    identical -- so a mutation that rendered the finding as a grey aside would survive every text
    assertion in this file.
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


@pytest.fixture(scope="module")
def live() -> str:
    feed = _live_feed()
    block = feed.get("churn_belief_size") or {}
    if not block.get("available"):
        pytest.fail(
            "the published churn-belief reading is unavailable ({}), so the page renders no "
            "account of the selection leg and the legs below cannot run".format(block.get("why")))
    return _render(feed)


@pytest.fixture(scope="module")
def live_block() -> dict:
    return (_live_feed().get("churn_belief_size") or {})


def test_the_account_of_the_flat_belief_reaches_the_rendered_page(live, live_block):
    """The measurement landed on 2026-09-22 and reached no reader until this element.

    Fires on: deleting the element, deleting its assignment, or leaving it at a placeholder.
    """
    assert live, "the page rendered NOTHING into #{} -- the account of the selection leg's " \
                 "refusal is invisible to a reader".format(PANEL)
    assert "Why the choosing has so little to find" in live, (
        "the block rendered without the heading that says what it answers: {!r}".format(live[:300]))
    assert _prose(live_block["reading"]) in live, (
        "the artefact's own reading is not what the page put on screen. Rendered: {!r}".format(
            live[:600]))


def test_the_reading_a_reader_meets_is_the_FEEDS_and_not_a_literal(live_block):
    """The page must READ the sentence, not print one that happens to match today's artefact.

    THE DEFECT THIS IS ABOUT. `churn_belief_size.reading` is the measurement's own conclusion,
    lifted verbatim through the generator. A page that re-authored it would be a second author of
    a conclusion it never measured -- and would go on stating it after the measurement moved. So
    the subject is a MARKED sentence the page cannot have authored.

    Fires on: any re-wording, truncation or restatement of the reading at either the producer or
    the render.
    """
    marked = copy.deepcopy(_live_feed())
    sentinel = "THE BELIEF MOVES FREELY IN HOUSEHOLD SIZE ON EVERY LEG OF THIS BOOK."
    marked["churn_belief_size"]["reading"] = sentinel
    rendered = _render(marked)
    assert sentinel in rendered, (
        "the page did not render the feed's reading, so the sentence it shows is its own: "
        "{!r}".format(rendered[:600]))
    assert _prose(live_block["reading"]) not in rendered, (
        "the live reading survived a feed that no longer carries it -- the page is printing a "
        "literal")


def test_every_figure_in_the_block_is_the_FEEDS(live, live_block):
    """The counts, the spread and the knee are read, never typed beside the sentence.

    CLAUDE.md: a number a page states is a claim, and a claim typed beside a figure is true when
    typed and cannot notice the next run. Each figure is driven to a value the live artefact does
    not carry, so a hard-coded one fails here and passes on the live feed.

    Fires on: rendering any of these as a literal, or reading one from a different field.
    """
    assert str(live_block["legs_below_the_knee"]) in live
    # THE MULTIPLICATION SIGN IS PART OF THE SUBJECT. The artefact's own reading
    # carries the same number as plain text ("spans 11.57x"), so a bare "11.57"
    # would match the SENTENCE and say nothing about whether the page derived the
    # figure -- and the negative leg below would be unfalsifiable for the same
    # reason. The rendered form the page composes is the one with the sign on it.
    assert "{:.2f}\u00d7".format(live_block["world_multiplier_spread"]) in live

    moved = copy.deepcopy(_live_feed())
    block = moved["churn_belief_size"]
    block["supply_legs"] = 9871
    block["legs_below_the_knee"] = 9013
    block["legs_above_the_knee"] = 858
    block["share_below_the_knee"] = 0.9131
    block["world_multiplier_spread"] = 3.14
    block["world_multiplier_low"] = 1.2
    block["world_multiplier_high"] = 3.77
    block["knee_gbp"] = 4321.0
    rendered = _render(moved)
    # THE LEG COUNTS CARRY NO THOUSANDS SEPARATOR and the money does -- the door prints a
    # count through `esc()` and a sterling figure through `gbp()`. Each is asserted in the
    # page's own form and not a uniform invented one: a leg that invents a format is
    # testing its own guess at the render rather than the render.
    for expected in ("9013", "858", "91.3%", "3.14\u00d7", "£4,321"):
        assert expected in rendered, (
            "{!r} is not on the page, so that figure is not read from the feed. "
            "Rendered: {!r}".format(expected, rendered[:900]))
    assert "{:.2f}\u00d7".format(live_block["world_multiplier_spread"]) not in rendered, (
        "the live spread survived a feed that no longer carries it -- it is a literal")


def test_the_knee_is_rendered_as_a_BILL_with_its_kWh_at_EVERY_probed_rate(live, live_block):
    """A knee quoted in kWh alone is a different claim from the one that was measured.

    WHY THIS IS ITS OWN LEG. The threshold is a previous ANNUAL BILL, so the consumption it
    corresponds to moves 2.67x across the rate deck this book was billed at. A page that rendered
    "12,000 kWh" and stopped would have a reader believe the company's belief turns on a meter
    reading, which is the frame the artefact explicitly refuses -- and the generator refuses to
    publish at all when the artefact stops saying so.

    Fires on: rendering one rate row, rendering the knee in kWh without its rate, or dropping the
    spread across rates.
    """
    assert "BILL" in live and "not a consumption" in live
    for row in live_block["knee_by_rate"]:
        assert _kwh(row["knee_kwh"]) in live, (
            "the knee at £{}/MWh is not on the page".format(row["old_rate_gbp_per_mwh"]))
    assert "{:.2f}".format(live_block["knee_kwh_spread_across_the_probe_rates"]) in live


def test_the_reader_is_told_this_is_NOT_the_book_the_arms_above_are_scored_over(live,
                                                                                live_block):
    """THE LOAD-BEARING LEG. A count over one population, rendered inside a section scored over
    another, with nothing saying so.

    The artefact measures 244 supply legs out of `site/data/customers.json`. The arms comparison
    this block sits inside is scored over 154 accounts whose per-account rows are not persisted at
    all. Those are different books, the artefact says so in its own words, and adjacency is what
    would make a reader take them for one. This asserts the artefact's OWN string reaches the
    screen -- not a paraphrase composed by the page, which would be a claim about a reconciliation
    nobody ran.

    Fires on: dropping the caveat, paraphrasing it, or rendering the block with the arms feed's
    own book counts.
    """
    caveat = live_block.get("population_is_not_this_pages_book")
    assert caveat, "the feed carries no population caveat, so the page cannot render one"
    assert _text(caveat) in live, (
        "the reader is shown this book's counts inside the arms section with nothing saying it is "
        "a different book. Rendered: {!r}".format(live[:900]))

    silent = copy.deepcopy(_live_feed())
    silent["churn_belief_size"]["population_is_not_this_pages_book"] = None
    assert _text(caveat) not in _render(silent), (
        "the caveat survived a feed that no longer carries it -- the page is authoring the "
        "population claim itself")


def test_the_unsourced_threshold_is_MARKED_where_a_reader_meets_it(live, live_block):
    """The knee's position is set by a constant this repo's own register lists as unsourced.

    CLAUDE.md: an honest `None` with a named reason is worth more than a plausible number, because
    the number will be read as established. The same applies at the surface -- an unsourced figure
    rendered unmarked IS read as established.

    Fires on: dropping `the_thresholds_own_origin` from the render.
    """
    origin = live_block.get("the_thresholds_own_origin")
    assert origin, "the feed carries no origin statement for the threshold"
    assert "NOT ESTABLISHED" in origin, (
        "this leg assumes the live threshold is unsourced; the artefact now says {!r}, so the "
        "leg's subject has changed and it must be re-derived rather than re-pointed".format(
            origin[:200]))
    assert _text(origin) in live


def test_a_feed_that_establishes_its_threshold_renders_NO_caveat():
    """THE NULL CONTROL for the leg above, and the reason the fix is not "always warn".

    A guard that prints a warning on every render is a guard a reader learns to skip past on the
    one day it changes.

    Fires on: rendering the caveat unconditionally.
    """
    sourced = copy.deepcopy(_live_feed())
    origin = sourced["churn_belief_size"]["the_thresholds_own_origin"]
    sourced["churn_belief_size"]["the_thresholds_own_origin"] = None
    rendered = _render(sourced)
    assert _text(origin) not in rendered
    # ...and the block itself is still there, so this is a silenced caveat and not a silenced page.
    assert "Why the choosing has so little to find" in rendered


def test_the_asymmetry_verdict_is_read_from_the_feed_and_BOTH_branches_are_reachable(live):
    """The claim that the belief varies exactly where the world does not is the FEED'S verdict.

    WHY BOTH BRANCHES ARE ASSERTED IN ONE TEST. CLAUDE.md's rule for a branch that exists to be
    taken rarely: assert it CAN be taken before asserting what it does. A verdict rendered
    unconditionally passes every one-sided leg, and this sentence is the sharpest thing on the
    block -- an unconditional render would keep stating it after the model gained a size term.

    Fires on: rendering the sentence unconditionally, or on a two-branch read of a three-valued
    verdict.
    """
    assert "where the belief varies, the world does not" in live

    feed = _live_feed()
    off = copy.deepcopy(feed)
    off["churn_belief_size"]["the_belief_varies_where_the_world_does_not"] = False
    unknown = copy.deepcopy(feed)
    unknown["churn_belief_size"]["the_belief_varies_where_the_world_does_not"] = None
    assert "where the belief varies, the world does not" not in _render(off)
    assert "where the belief varies, the world does not" not in _render(unknown)


def test_a_segment_the_artefact_cannot_answer_for_is_NOT_rendered_as_a_no(live):
    """Three states, not two: "not stated" and "the world does not read their bill" differ.

    A two-branch ternary prints the second for the first, which is a measurement the artefact
    never made appearing on the page as one it did.

    Fires on: collapsing the null branch into the false one.
    """
    assert re.search(r"\bno\b", live), (
        "no segment is marked as one the world does not read a bill for, so the three-way column "
        "has nothing in it to distinguish"
    )
    blank = copy.deepcopy(_live_feed())
    for segment in blank["churn_belief_size"]["segments"]:
        segment["world_reads_their_own_bill"] = None
    rendered = _render(blank)
    assert "not stated" in rendered, (
        "a segment carrying no answer rendered as an answer: {!r}".format(rendered[:600]))


def test_the_segment_rows_a_reader_meets_are_the_FEEDS(live, live_block):
    """Every segment the artefact cut, with its own leg count -- not a subset and not a literal.

    Fires on: rendering one segment, dropping a row, or typing the counts.
    """
    for segment in live_block["segments"]:
        assert str(segment["segment"]) in live
        assert str(segment["legs"]) in live

    extra = copy.deepcopy(_live_feed())
    extra["churn_belief_size"]["segments"] = [
        {"segment": "microbusiness", "legs": 7717, "above_the_knee": 41,
         "world_reads_their_own_bill": True}]
    rendered = _render(extra)
    assert "microbusiness" in rendered and "7,717" in rendered or "7717" in rendered, (
        "a segment the feed carries did not reach the page: {!r}".format(rendered[:600]))


def test_the_finding_is_rendered_as_a_FINDING_and_not_as_a_footnote(live_block):
    """The one claim stripped text is blind to: this block's colour.

    A page that renders an unflattering reading in muted grey has published it and hidden it at
    once. The reading is amber -- the page's own colour for "this qualifies the figures beside
    it" -- and that is asserted against the RAW markup because `_text` cannot see it.

    Fires on: styling the reading muted, or dropping the style attribute altogether.
    """
    raw = _render(_live_feed(), raw=True)
    sentence = _esc(live_block["reading"])
    position = raw.find(sentence[:60])
    assert position > 0, "the reading is not in the rendered markup at all"
    opening = raw.rfind("<p", 0, position)
    assert "var(--amber)" in raw[opening:position], (
        "the reading is rendered without the page's qualifying colour, so a reader meets the "
        "finding styled as a footnote: {!r}".format(raw[opening:position]))


def test_an_unavailable_reading_renders_its_REASON_and_never_an_omission():
    """THE NULL RUNG. "The artefact could not be read" and "the belief is flat" are different.

    An absent paragraph and a discharged one look identical to a reader, and this is the account
    of the page's own central refusal -- the one place a silence is most likely to be read as
    "there was nothing to say".

    Fires on: rendering the unavailable branch as an empty element, or rendering the live sentence
    on a feed that carries none.
    """
    absent = copy.deepcopy(_live_feed())
    absent["churn_belief_size"] = {
        "available": False,
        "why": "the churn-belief size artefact could not be read. Rebuild it with `python3 -m "
               "tools.churn_belief_size_response`",
        "reading": None,
        "segments": [],
    }
    rendered = _render(absent)
    assert "could not be read" in rendered, (
        "an unreadable artefact rendered as a silence: {!r}".format(rendered))
    assert "tools.churn_belief_size_response" in rendered, (
        "the refusal reached the reader without naming how to resolve it")
    assert "235" not in rendered, "a figure survived a feed that carries none"
