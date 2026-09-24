"""The RULER under the size-term movement must reach the rendered page, including "we cannot tell".

THE DEFECT IT SERVES.
`fc390b918` (2026-09-23) gave the company's churn belief a sourced household-size term and
published the arms table before and after it, one seed each: net margin advantage 14,074 -> 13,440,
gross margin -9,299 -> +12,152, enterprise value 6,143 -> 7,642. `/capabilities/` renders the
CHANGE -- `arms-churn-belief-size` is the account of what the term did to the belief -- and until
this element it rendered nothing that could tell a reader whether any of those movements can be
distinguished from noise. Every other bound in that section measures the spread of readings WITHIN
one configuration; the size-term contrast is a difference BETWEEN two read at the same seed, so
none of them can price it. A change published on a page whose only bounds cannot grade it is the
flattering half of a result.

WHAT MADE THE MISSING BOUND EXPENSIVE RATHER THAN MERELY ABSENT. The published floor the section
does carry is degenerate for this purpose twice over -- it is marginal, not paired, and
`SEAT_FINDING_THE_NARROW_WIDTH_BEHIND_THE_PUBLISHED_SELECTION_SIGN_IS_A_REPEATED_DRAW` establishes
5 of its 18 draws are repeats -- so a reader looking for a ruler would have found one that both
measures the wrong thing and overstates its own width. `tools/size_term_paired_floor.py` measured
the right one over five paired seeds (5101-5105, one leg per process, ~53 minutes a leg) and the
answer is unflattering: exactly one of the four figures that commit published clears its own
paired floor.

WHY "CANNOT TELL" IS THE SUBJECT OF THIS FILE AND NOT A CAVEAT IN IT. Three of the four rows are
unresolvable and two of those come out with the paired spread WIDER than two independent draws
would have been -- the design's own common-random-numbers hypothesis refuted on the rows it
mattered for. CLAUDE.md: "Fail closed, and say so on the surface. 'We cannot tell' is a result. It
belongs on the page, not in a footnote." So the legs below assert that the unresolvable rows are
rendered as loudly as the one that clears, and the null control is what stops the fix being
"always print a warning".

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE FEED. `value_arms.json` carrying
`size_term_paired_floor` proves nothing about whether a reader meets it. This drives the REAL door
through `site/_live_harness.mjs` and asserts on what the page put in the element, against the
PUBLISHED (index) bytes of both -- see `site/test_the_published_bytes_reader.py` for why a door
test that reads the working tree cannot tell "the reader can see this" from "someone in this tree
has fixed it and not landed it".

R15 -- WHAT MAKES EACH LEG ABLE TO FAIL. Every leg drives the door with a MUTATED feed and asserts
the rendered text follows it, so a page printing today's answer as a literal reds on the mutation
while passing on the live feed:

  * drop the `#arms-size-term-floor` render, or leave the element at its placeholder ->
    `test_the_ruler_under_the_published_movement_reaches_the_rendered_page` red.
  * re-derive the verdict from the mean and the spread instead of reading the feed's boolean ->
    `test_the_verdict_word_is_the_FEEDS_boolean_and_not_re_derived_on_the_page` red. This is the
    load-bearing leg: the comparison `sems_from_zero >= sems_needed_to_state_a_sign` is the
    ARTEFACT's own stated rule, and a page that re-implements it would go on applying the old rule
    after the artefact changed its bar.
  * render "cannot tell" muted, or omit it -> `test_an_unresolvable_row_is_rendered_as_LOUDLY_as_
    one_that_clears` red, and its null control
    `test_a_feed_whose_rows_all_clear_renders_NO_amber_verdict` is what stops the fix being an
    unconditional warning.
  * hard-code any figure in the table -> `test_every_figure_in_the_table_is_the_FEEDS` red.
  * render the floor WITHOUT the published move it grades ->
    `test_the_published_one_seed_move_is_on_the_page_beside_the_floor_that_grades_it` red. A floor
    beside no contrast is a spread nobody asked for; the pair is the claim.
  * type the headline count instead of counting it ->
    `test_the_headline_count_is_COUNTED_from_the_booleans_and_not_a_literal` red.
  * drop the family size, or render a short family as a whole one ->
    `test_the_seeds_that_completed_BOTH_legs_are_named_because_they_are_the_bound` red.
  * state the pairing hypothesis unconditionally, either way ->
    `test_whether_the_pairing_bought_anything_is_read_from_the_feed_and_BOTH_branches_render` red.
  * fail OPEN on an unreadable artefact (omit the block rather than say so) ->
    `test_an_unavailable_floor_renders_its_REASON_and_never_an_omission` red.

THE NULL RUNG is `test_an_unavailable_floor_renders_its_REASON_and_never_an_omission`, and what it
discriminates is stated precisely rather than flatteringly: it stays green when the FEED carries no
floor and reds when the page renders nothing in its place, because "the ruler could not be built"
and "the movement cannot be resolved" are the two states this block exists to keep apart -- and
they are the two a reader is most likely to conflate, since both leave the commit's figures
ungraded. It reds along with everything else on the mutation that deletes the element, correctly,
and that is not evidence of anything.

The producer's own refusals -- an unreadable artefact, an artefact with no paired differences, a
family too small to carry a spread -- are reachable only from the generator and are swept in
`tests/tools/test_generate_value_arms_data.py`; this file drives mutated FEEDS and structurally
cannot reach them.
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

# THE SUBJECTS, AS PATHS IN GIT AND NOT FILES ON DISK. Same reason as every other door test here;
# the argument is in `site/test_the_published_bytes_reader.py` rather than paraphrased.
DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/value_arms.json"
GROWTH_REL = "site/data/book_growth.json"
CAPS_REL = "site/data/capabilities_door.json"
DD_ARMS_REL = "site/data/dd_opening_arms.json"

#: The element this file is about. It sits directly under `arms-churn-belief-size` -- the block
#: that says what the size term CHANGED -- because the change and its ruler are one claim.
PANEL = "arms-size-term-floor"

#: The feed key the panel is rendered from.
BLOCK = "size_term_paired_floor"


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    """THE RELAPSE GUARD. Reads this file's own AST rather than my having been careful."""
    refuse_working_tree_reads(__file__, (DOOR_REL, FEED_REL, GROWTH_REL, CAPS_REL, DD_ARMS_REL))


def _prose(sentence: str) -> str:
    """The door's own `prose()`, mirrored -- INCLUDING what it does to the house-style dash.

    The feed is authored in the repository's plain-text style where an em dash is typed `--`, and
    the door typesets it before a reader sees it. `feed_string in rendered_text` is therefore a
    comparison against a string the page CANNOT emit for every sentence carrying one, and this
    block's `how_to_read_this` carries two.
    """
    return re.sub(r"\s+", " ", sentence).replace(" -- ", " — ")


def _text(fragment: str) -> str:
    """What a READER sees: tags stripped, entities decoded, whitespace collapsed."""
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict, raw: bool = False) -> str:
    """Drive the real door with `feed` and return what `#arms-size-term-floor` shows.

    FAIL-CLOSED: a missing harness, an unresolved fetch, a script error or an element the page
    never wrote all raise here rather than degrading to an empty string that a `not in` assertion
    would happily pass on.

    `raw` returns the UNSTRIPPED innerHTML for the one claim `_text` is blind to: this block's
    COLOUR. "cannot tell" set in muted grey and "cannot tell" set in amber are the same string,
    and the difference between them is the whole of this block's honesty.
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


def _row(feed: dict, name: str) -> dict:
    for row in feed[BLOCK]["rows"]:
        if row["row"] == name:
            return row
    raise AssertionError("the published floor carries no {!r} row".format(name))


@pytest.fixture(scope="module")
def live() -> str:
    feed = _live_feed()
    block = feed.get(BLOCK) or {}
    if not block.get("available"):
        pytest.fail(
            "the published paired floor is unavailable ({}), so the page grades none of the "
            "figures the size-term commit published and the legs below cannot run".format(
                block.get("why")))
    return _render(feed)


@pytest.fixture(scope="module")
def live_block() -> dict:
    return (_live_feed().get(BLOCK) or {})


def test_the_ruler_under_the_published_movement_reaches_the_rendered_page(live, live_block):
    """The floor was measured over five paired seeds and reached no reader until this element.

    Fires on: deleting the element, deleting its assignment, or leaving it at a placeholder.
    """
    assert live, (
        "the page rendered NOTHING into #{} -- the movement the size-term commit published is on "
        "the page with no bound that can grade it".format(PANEL))
    assert "told apart from noise" in live, (
        "the block rendered without the heading that says what it answers: {!r}".format(live[:300]))
    for row in live_block["rows"]:
        if row["was_published_by_the_commit"]:
            assert row["row"] in live, (
                "the commit published a move for {} and the page grades it nowhere: {!r}".format(
                    row["row"], live[:600]))


def test_the_verdict_word_is_the_FEEDS_boolean_and_not_re_derived_on_the_page(live):
    """The page must READ `the_contrast_clears_its_own_floor`, never recompute it.

    THE DEFECT THIS IS ABOUT. `sems_from_zero >= sems_needed_to_state_a_sign` is the ARTEFACT's own
    stated rule, carried onto the block in `how_to_read_the_distance` and applied once, in the
    generator. A page that re-implemented it would be a second author of the comparison -- and
    would go on applying yesterday's rule after the artefact changed its bar, which is exactly how
    a surface comes to disagree with the measurement it is rendering while looking correct.

    THE MUTATION LEAVES EVERY NUMBER ALONE. Only the boolean flips, so a page deriving the verdict
    from the mean and the spread renders the unchanged word and reds here. Both directions are
    driven: a page hard-coding either verdict survives only one of them.
    """
    assert "cannot tell" in live and "clears its floor" in live, (
        "the live feed carries rows on both sides of the bar and the page renders only one kind "
        "of verdict: {!r}".format(live[:600]))

    lifted = copy.deepcopy(_live_feed())
    for row in lifted[BLOCK]["rows"]:
        row["the_contrast_clears_its_own_floor"] = True
    assert "cannot tell" not in _render(lifted), (
        "every row's boolean says it clears its floor and the page still calls a row "
        "unresolvable, so the verdict is not read from the feed")

    sunk = copy.deepcopy(_live_feed())
    for row in sunk[BLOCK]["rows"]:
        row["the_contrast_clears_its_own_floor"] = False
    assert "clears its floor" not in _render(sunk), (
        "no row's boolean says it clears its floor and the page still says one does, so the "
        "verdict is re-derived on the page or printed as a literal")


def test_a_row_the_page_cannot_grade_is_rendered_as_NOT_STATED_and_never_as_a_refusal(live):
    """Three states, not two. An ungraded row is not a row that failed to clear.

    Fires on: collapsing `the_contrast_clears_its_own_floor` to a two-branch ternary, which prints
    "cannot tell" for a row whose artefact could not state a bar at all -- a refusal the
    measurement never made, attributed to it by the page.
    """
    blank = copy.deepcopy(_live_feed())
    _row(blank, "net_margin_gbp")["the_contrast_clears_its_own_floor"] = None
    rendered = _render(blank)
    assert "not stated" in rendered, (
        "a row whose floor states no verdict rendered as one of the two verdicts: {!r}".format(
            rendered[:600]))


def test_an_unresolvable_row_is_rendered_as_LOUDLY_as_one_that_clears(live):
    """"We cannot tell" is a RESULT and must not be quieter than the row that cleared.

    CLAUDE.md: it belongs on the page, not in a footnote. Three of the four figures the commit
    published are unresolvable, and a block that set them in muted grey while setting the fourth
    in the body colour would leave a reader with the impression the term is established.

    Fires on: styling the unresolvable verdict `var(--muted)`, or dropping it.

    THE SUBJECT IS THE RAW MARKUP because stripped to text an amber qualifier and a grey footnote
    are the same string.
    """
    raw = _render(_live_feed(), raw=True)
    assert "cannot tell" in raw, "the page renders no unresolvable verdict at all"
    amber = re.findall(r'<span style="color:var\(--amber\);">\s*cannot tell\s*</span>', raw)
    assert amber, (
        "the unresolvable verdict is not set in the finding colour -- a result rendered as a "
        "footnote is the shape this block exists to refuse: {!r}".format(raw[:900]))


def test_a_feed_whose_rows_all_clear_renders_NO_amber_verdict():
    """THE NULL CONTROL on the leg above, so the fix cannot be "always print a warning".

    A block that emitted the amber verdict unconditionally would pass every assertion in this file
    that only looks for it. This drives a feed in which every row clears and asserts the page says
    so plainly -- and in the headline sentence's colour too, which is the one a reader takes.
    """
    cleared = copy.deepcopy(_live_feed())
    for row in cleared[BLOCK]["rows"]:
        row["the_contrast_clears_its_own_floor"] = True
        row["pairing_reduced_the_spread"] = True
        row["ratio_paired_to_independent"] = 0.5
    raw = _render(cleared, raw=True)
    assert "cannot tell" not in raw, (
        "every row clears its floor and the page still renders an unresolvable verdict")
    assert "var(--amber)" not in raw, (
        "every row clears its floor and the headline is still set as a warning: {!r}".format(
            raw[:900]))


def test_the_published_one_seed_move_is_on_the_page_beside_the_floor_that_grades_it(live):
    """The floor and the contrast are ONE claim; a spread beside no contrast grades nothing.

    THE DEFECT THIS IS ABOUT. The whole reason this ruler was built is that `fc390b918` published
    three figures and the page carried no bound that could price them. Rendering the floor without
    those figures beside it would reproduce the defect in the other direction -- a reader would
    meet a spread and have to go and find the number it is a spread about.

    Fires on: dropping the published column, or rendering it as a blank for a row the commit
    published no move for (a blank reads as zero, which is a claim the commit never made).
    """
    moved = copy.deepcopy(_live_feed())
    _row(moved, "net_margin_gbp")["published_one_seed_move"] = -987654.0
    assert "987,654" in _render(moved), (
        "the published one-seed move is not read from the feed, so the page grades a figure it is "
        "not showing")

    absent = copy.deepcopy(_live_feed())
    _row(absent, "net_margin_gbp")["published_one_seed_move"] = None
    rendered = _render(absent)
    assert "not published" in rendered, (
        "a row the commit published no move for rendered as a blank, which a reader reads as "
        "zero: {!r}".format(rendered[:600]))


def test_every_figure_in_the_table_is_the_FEEDS(live):
    """No number a reader meets here may be typed on the page.

    Fires on: hard-coding the paired mean, the spread, the distance, the bar or the ratio --
    each of which is today's answer and each of which goes stale the moment a seed is added.
    """
    marked = copy.deepcopy(_live_feed())
    row = _row(marked, "gross_margin_gbp")
    row["paired_mean"] = 314159.0
    row["paired_stdev"] = 271828.0
    row["sems_from_zero"] = 9.91
    row["sems_needed_to_state_a_sign"] = 8.88
    row["ratio_paired_to_independent"] = 0.33
    rendered = _render(marked)
    for needle in ("314,159", "271,828", "9.91", "8.88", "0.33"):
        assert needle in rendered, (
            "{!r} was mutated in the feed and the page rendered something else, so that figure is "
            "a literal: {!r}".format(needle, rendered[:900]))


def test_the_headline_count_is_COUNTED_from_the_booleans_and_not_a_literal(live):
    """"N of M figures clear this floor" must follow the feed, not today's answer.

    THE DEFECT THIS IS ABOUT. The sentence a reader takes away from this block is the count, and a
    literal there is a claim pinned to the current state -- which CLAUDE.md names as going stale
    in the direction that flatters: the page would go on saying one row clears after a sixth seed
    moved the bar under it.

    Fires on: typing either number, and on counting the wrong population (every row, rather than
    the rows the commit actually published a move for).
    """
    published = [r for r in _live_feed()[BLOCK]["rows"]
                 if r["was_published_by_the_commit"] and r["published_one_seed_move"] is not None]
    cleared = [r for r in published if r["the_contrast_clears_its_own_floor"] is True]
    assert "{} of the {} figures".format(len(cleared), len(published)) in live, (
        "the headline count disagrees with the feed's own booleans: {!r}".format(live[:400]))

    lifted = copy.deepcopy(_live_feed())
    _row(lifted, "enterprise_value_gbp")["the_contrast_clears_its_own_floor"] = True
    assert "{} of the {} figures".format(len(cleared) + 1, len(published)) in _render(lifted), (
        "one more row was marked as clearing its floor and the headline count did not move, so "
        "it is a literal")


def test_the_seeds_that_completed_BOTH_legs_are_named_because_they_are_the_bound(live, live_block):
    """The family size IS the width: the bar is t(n-1) and widens as legs die.

    THE DEFECT THIS IS ABOUT, and it is the one the run this artefact came from was most exposed
    to. Each leg is its own process because the first attempt at this measurement was OOM-killed
    at 1h26m having written nothing; legs die here. A block that rendered five pairs with the same
    words it would render six is a block that cannot tell a reader the bound was wider than
    planned, and publishing survivors as if they were the family asked for is the specific failure
    the run was instructed to refuse.

    Fires on: dropping the seed list, or rendering a count that is not the feed's.
    """
    for seed in live_block["seeds_measured"]:
        assert str(seed) in live, (
            "seed {} completed both legs and is not named on the page, so a reader cannot check "
            "the family the bar was derived from".format(seed))
    shorter = copy.deepcopy(_live_feed())
    shorter[BLOCK]["seeds_measured"] = shorter[BLOCK]["seeds_measured"][:2]
    rendered = _render(shorter)
    assert "over 2 paired seeds" in rendered, (
        "the family shrank and the page still described the old one: {!r}".format(rendered[:400]))


def test_whether_the_pairing_bought_anything_is_read_from_the_feed_and_BOTH_branches_render(live):
    """The design's own hypothesis, graded on the page, both ways.

    THE CLAIM THIS PROTECTS. Common random numbers only cancel while the two legs' books stay
    together, and the size term changes prices, which changes who stays. On the live feed the
    paired spread came out WIDER than two independent draws would have been on two rows -- the
    hypothesis refuted where it mattered most. That inverts how the unresolvable verdicts read:
    they are the best available ruler failing, not a worse ruler being used, and a page that left
    the ratio column to be interpreted would have let a reader draw the opposite conclusion.

    Fires on: stating the sentence unconditionally (the null branch below), dropping it, or
    counting rows the feed does not mark.
    """
    widened = [r for r in _live_feed()[BLOCK]["rows"]
               if r["pairing_reduced_the_spread"] is False]
    if widened:
        assert "WIDER" in live, (
            "{} row(s) came out wider than independent draws and the page does not say so, so a "
            "reader reads their verdict as a weaker ruler".format(len(widened)))
        assert "On {} row".format(len(widened)) in live, (
            "the count of widened rows disagrees with the feed: {!r}".format(live[:600]))

    helped = copy.deepcopy(_live_feed())
    for row in helped[BLOCK]["rows"]:
        row["pairing_reduced_the_spread"] = True
    assert "WIDER" not in _render(helped), (
        "no row widened and the page still says the pairing bought nothing, so the sentence is "
        "unconditional")


def test_an_unavailable_floor_renders_its_REASON_and_never_an_omission():
    """THE NULL RUNG. "The ruler could not be built" and "the move cannot be resolved" are two
    states, and both leave the commit's figures ungraded -- so they are the two a reader is most
    likely to conflate.

    Fires on: failing OPEN, which here means rendering an empty element rather than saying the
    artefact is missing. An absent paragraph and a discharged one look identical to a reader.
    """
    gone = copy.deepcopy(_live_feed())
    why = ("the paired floor artefact could not be read, so the movement the belief's size term "
           "produced has no ruler on this page")
    gone[BLOCK] = {"available": False, "why": why, "rows": [], "seeds_measured": []}
    rendered = _render(gone)
    assert rendered, (
        "the floor is unavailable and the page rendered NOTHING -- a reader meets the size term's "
        "published movement with no sign that its ruler is missing")
    assert _prose(why) in rendered, (
        "the page did not give the reason the ruler is absent: {!r}".format(rendered[:600]))
    assert "cannot tell" not in rendered, (
        "an unreadable artefact rendered as a measurement that came out unresolvable, which is "
        "the one confusion this leg exists to refuse")
