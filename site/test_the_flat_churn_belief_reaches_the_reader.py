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

THAT PARAGRAPH IS THE DEFECT'S HISTORY AND NO LONGER ITS STATE (2026-09-23). `fc390b918` gave the
belief a size term sourced to the same Ofgem/BMG survey the world's multiplier cites, and the
finding INVERTED: the belief now hears the size of 216 of the arms' book's 226 legs and is deaf to
10, and those 10 are the largest households on it. The account the page owes a reader is
unchanged in KIND -- why a per-customer arm has little to win -- so this file's subject is
unchanged and its legs are re-derived rather than re-pointed, one by one, each saying what moved
under it. The paragraph above is kept rather than rewritten because it is what the legs below were
built against, and a history rewritten to match today's answer is how a door comes to look like it
always knew.

WHAT THE INVERSION COST, AND IT IS THE REASON THIS FILE NOW HAS A WITHDRAWAL LEG. The producer's
consumer, `_churn_belief_size_response`, refused to publish the block at all when the artefact
stopped saying "the knee is a BILL" -- a fail-closed refusal keyed to a particular ANSWER rather
than to the question being answered. It was right to refuse a stale sentence and wrong about what
made it stale, so the page withdrew the whole block for ten publisher cycles and a reader met
nothing where the best thing built that stretch should have been. The refusal is re-keyed to
`the_belief_is_flat_below_a_knee`, which the artefact states either way.

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
    assert str(live_block["legs_the_belief_hears"]) in live
    # THE MULTIPLICATION SIGN IS PART OF THE SUBJECT. The artefact's own reading
    # carries the same number as plain text ("spans 11.57x"), so a bare "11.57"
    # would match the SENTENCE and say nothing about whether the page derived the
    # figure -- and the negative leg below would be unfalsifiable for the same
    # reason. The rendered form the page composes is the one with the sign on it.
    assert "{:.2f}\u00d7".format(live_block["world_multiplier_spread"]) in live

    moved = copy.deepcopy(_live_feed())
    block = moved["churn_belief_size"]
    block["legs_graded"] = 9871
    block["legs_the_belief_hears"] = 9013
    block["legs_the_belief_is_deaf_to"] = 858
    block["share_the_belief_hears"] = 0.9131
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


def test_the_DEAF_EDGE_is_rendered_at_EVERY_probed_rate_with_its_spread(live, live_block):
    """The edge above which the belief stops hearing size, at every rate, never at one.

    RE-DERIVED 2026-09-23, ON THIS LEG'S OWN INSTRUCTION, AND THE SUBJECT IT HAD IS GONE. It used
    to assert that the page rendered the knee as a BILL and not a consumption, at every probed
    rate, with its spread. `fc390b918` gave `estimate_churn_probability` a sourced size term, so
    the belief responds to consumption from the first metered kWh and there is no knee to render
    -- the probe that found it returns the bottom of its bracket at every rate, and the artefact
    withdraws `the_knee_is_a_bill_not_a_consumption` by name.

    WHAT SURVIVED THE RE-DERIVATION IS THE DEFECT, NOT THE FIGURE. The leg existed because a page
    that quotes ONE rate has a reader believe the belief turns on a meter reading, when the edge
    it is really about travels with the price deck. That is still true and it is still the edge
    this block is about -- it has moved from where the response BEGINS to where it STOPS, because
    both of the belief's consumption terms are ceilinged. So the leg asks the same question of the
    edge that is load-bearing now: every rate, and the spread across them.

    Fires on: rendering one rate row, rendering the edge without its rate, dropping the spread.
    """
    for row in live_block["deaf_edge_by_rate"]:
        assert _kwh(row["deaf_above_kwh"]) in live, (
            "the deaf edge at £{}/MWh is not on the page".format(row["old_rate_gbp_per_mwh"]))
    assert "{:.2f}".format(live_block["deaf_edge_kwh_spread_across_the_probe_rates"]) in live


def test_the_page_does_NOT_still_call_the_belief_flat_below_a_knee(live, live_block):
    """The retired claim is gone from the page, and the page says the retirement happened.

    THE DEFECT, AND IT RAN FOR TEN PUBLISHER CYCLES. `site/data/value_arms.json` carried a reading
    measured against code that no longer existed, under a fresh `generated_at` -- a stale
    intermediate republishing as a current feed. The two halves of the remedy are separable and
    only one of them is the obvious one: removing the false sentence is necessary, and a reader
    who met it and comes back to find a DIFFERENT sentence in the same place has been silently
    revised at. So both are asserted.

    WHY THE CONTROL IS A MUTATED FEED AND NOT AN `else` ON THE LIVE VERDICT. I wrote the else
    first -- "if the artefact says the belief IS flat below a knee, assert the page says so" --
    and it is a branch that can never pass, which is worse than one that is merely never taken.
    The flat-belief sentence does not exist anywhere any more: `reading()` composes ONE sentence
    from the deafness census, so a belief that went flat again would publish "hears ... for 0 of
    226", not the retired wording. An else keyed to a string no producer can emit is a leg that
    would red on the very change it claims to license. The reachable control is the withdrawal's
    own null: drive the feed with no withdrawal and assert the paragraph goes, and the block
    stays -- the same grammar as the threshold caveat's null control below.

    Fires on: reinstating the flat-belief sentence; publishing the new reading with no account of
    what it replaced; rendering the withdrawal unconditionally.
    """
    assert live_block["the_belief_is_flat_below_a_knee"] is False, (
        "this leg assumes the live artefact's verdict is that the belief is NOT flat below a "
        "knee. It now says {!r}, so the subject has changed and this must be re-derived rather "
        "than re-pointed".format(live_block["the_belief_is_flat_below_a_knee"]))
    assert "FLAT in household size" not in live, (
        "the page still tells a reader the belief is flat in household size, and the artefact's "
        "own verdict is that it is not")
    assert live_block["what_was_withdrawn_and_why"], (
        "the artefact withdrew a published claim and carries no account of it")
    assert _prose(live_block["what_was_withdrawn_and_why"]) in live, (
        "the withdrawal is in the feed and not on the page, so a reader who met the old sentence "
        "meets its replacement with no sign that anything was retracted")

    silent = copy.deepcopy(_live_feed())
    silent["churn_belief_size"]["what_was_withdrawn_and_why"] = None
    rendered = _render(silent)
    assert _prose(live_block["what_was_withdrawn_and_why"]) not in rendered, (
        "the withdrawal survived a feed that no longer carries it -- the page is printing a "
        "literal, and it will go on announcing a retraction after the retraction is old news")
    assert "Why the choosing has so little to find" in rendered, (
        "dropping the withdrawal took the block with it; this is a silenced paragraph, not a "
        "silenced page")


def test_the_reader_is_told_WHICH_book_these_counts_are_over(live, live_block):
    """THE LOAD-BEARING LEG, and its subject inverted on 2026-09-22 without the leg going away.

    It used to assert a warning: the block measured the tree's 164-account book while the arms
    comparison around it is scored over 154 accounts, and adjacency is what would make a reader
    take them for one. The measurement can now cut the arms' OWN book -- `site/data/customers.json`
    at the commit the run recorded, reconciled against the four counts the run published about its
    own book -- so the counts here and the arms above describe the same accounts.

    WHAT IS ASSERTED IS THE PROPERTY, NOT EITHER ANSWER. A reader must be told which book these
    counts are over, in the artefact's own words, on every render. That claim is true whether the
    arms' book was identified or the block fell back to the tree's, and it is what goes red if the
    page ever stops saying. Pinning "this is NOT the arms' book" would have gone red for the code
    becoming MORE honest, which is exactly backwards.

    Fires on: dropping either string, paraphrasing one, or rendering the block with no population
    line at all.
    """
    which = live_block.get("which_book")
    assert which, "the feed does not say which book these counts are over"
    assert _text(which) in live, (
        "the reader is shown counts inside the arms section with nothing saying which book they "
        "are over. Rendered: {!r}".format(live[:900]))

    caveat = live_block.get("population_is_not_this_pages_book")
    assert caveat, "the feed carries no population line, so the page cannot render one"
    assert _text(caveat) in live

    for field in ("which_book", "population_is_not_this_pages_book"):
        silent = copy.deepcopy(_live_feed())
        original = silent["churn_belief_size"][field]
        silent["churn_belief_size"][field] = None
        assert _text(original) not in _render(silent), (
            "`{}` survived a feed that no longer carries it -- the page is authoring the "
            "population claim itself".format(field))


def test_a_book_that_is_NOT_the_arms_own_is_rendered_as_a_WARNING(live_block):
    """The fallback must look different from the provenance, or the fallback is invisible.

    When the arms' book cannot be identified this block renders the tree's book instead, and a
    reader who cannot tell that from the identified case is being shown counts about a different
    population in the same muted grey. The colour is DERIVED from
    `arms_book_unavailable_because` rather than hard-coded, and both branches are exercised here
    because a branch that exists to be taken rarely is the one that quietly stops being takeable.
    """
    # RAW HTML, because the claim is about COLOUR and `_text` is blind to it by construction —
    # the helper's own docstring says so.
    identified = _render(_live_feed(), raw=True)
    assert live_block.get("arms_book_unavailable_because") is None, (
        "the live feed could not identify the arms' book: {}".format(
            live_block.get("arms_book_unavailable_because")))

    fell_back = copy.deepcopy(_live_feed())
    fell_back["churn_belief_size"]["arms_book_unavailable_because"] = (
        "git could not produce the roster at that commit")
    warned = _render(fell_back, raw=True)
    assert warned != identified, (
        "a block rendered from a book that is NOT the arms' own is indistinguishable from one "
        "that is -- the fallback cannot be seen")
    assert warned.count("var(--amber)") > identified.count("var(--amber)"), (
        "the fallback is not marked. Identified: {} amber, fell back: {}".format(
            identified.count("var(--amber)"), warned.count("var(--amber)")))


def test_the_unsourced_threshold_is_MARKED_where_a_reader_meets_it(live, live_block):
    """The knee's position is not established, and the page must say so where a reader meets it.

    CLAUDE.md: an honest `None` with a named reason is worth more than a plausible number, because
    the number will be read as established. The same applies at the surface -- an unsourced figure
    rendered unmarked IS read as established.

    RE-DERIVED 2026-09-23, on this leg's own instruction. It used to ground itself on "a constant
    this repo's own register lists as unsourced", and that ground is gone: the register now carries
    an origin for `BILL_STRESS_THRESHOLD_GBP`. The VERDICT did not move -- no published source
    gives a bill level at which GB switching rises, and 3,000 was deliberately not re-picked -- so
    the assertion below survives, and it would have survived on rot alone. That is exactly the
    failure this leg warned about, so the subject is restated: the page must mark the LEVEL as not
    established AND send the reader to the reading that refuted the SHAPE. Either half alone is a
    caveat with nowhere to go, or a citation that reads as a source for the number.

    Fires on: dropping `the_thresholds_own_origin` from the render; publishing the caveat with no
    reading behind it.
    """
    origin = live_block.get("the_thresholds_own_origin")
    assert origin, "the feed carries no origin statement for the threshold"
    assert "NOT ESTABLISHED" in origin, (
        "this leg assumes the live threshold's LEVEL is unestablished; the artefact now says {!r}. "
        "If a source has since been found, this leg's subject has changed and it must be "
        "re-derived rather than re-pointed".format(origin[:200]))
    assert "is_there_a_bill_level_at_which_switching_rises" in origin, (
        "the caveat names no reading. A gap filed and then orphaned is a gap nobody can act on, "
        "and this repository's recurring shape is a sourced anchor that reaches no reader; the "
        "artefact says {!r}".format(origin[:200]))
    # `_prose`, NOT `_text`, AND THE DIFFERENCE IS THE HOUSE-STYLE DASH. This read `_text(origin)`
    # and passed for as long as the origin sentence happened to contain no ` -- `. The sentence
    # gained one when the caveat was rewritten to name its reading, and the door typesets that to
    # a real em dash before a reader sees it -- so the comparison was against a string the page
    # cannot emit, and it went red on a correct render. Exactly the defect `_prose` was written
    # for, entered here through a feed edit rather than a door edit.
    assert _prose(origin) in live


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
    assert _prose(origin) not in rendered
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
    assert "is the one segment the world does not read a bill for" in live

    feed = _live_feed()
    off = copy.deepcopy(feed)
    off["churn_belief_size"]["the_belief_varies_where_the_world_does_not"] = False
    unknown = copy.deepcopy(feed)
    unknown["churn_belief_size"]["the_belief_varies_where_the_world_does_not"] = None
    assert "is the one segment the world does not read a bill for" not in _render(off)
    assert "is the one segment the world does not read a bill for" not in _render(unknown)


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
