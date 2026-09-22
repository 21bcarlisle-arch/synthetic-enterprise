"""The published `selection_gbp` must tell a reader WHICH WAY it is wrong and BY HOW MUCH.

THE DEFECT THIS EXISTS FOR (2026-09-19, Lane 0, the director's own item). The arms page published
a negative-leaning `selection_gbp` beside an honest caveat -- `_one_book`'s sentence, which says
this run never asked whether the two arms priced the same renewals -- and that caveat carried no
SIZE. A published figure with a known bias direction and no magnitude is a "we cannot tell" hiding
behind a number: the reader gets something that looks measured next to something that looks
decorative, and no way to tell whether the contamination is worth £5 or £5,000. It is worth £810.

WHAT IS ASSERTED, AND WHY IT IS ONE CLAIM AND NOT THREE. A reader of the arms page can see, without
opening a staging document: the DIRECTION of the bias, ONE magnitude for it, and WHICH BOOK that
magnitude came from. Those three travel together or the panel has not done its job -- a direction
with no size is the defect this repairs, and a size with no book is an invitation to subtract it
from the figure it sits beside, which would be arithmetic across two instruments 20 paths apart.

THE RUNG THAT MATTERS MOST IS THE NEGATIVE ONE, and the item that drew this work named it as its
own falsifier before any of this was written:

    "What would prove it insufficient: the £810.18 appearing anywhere on the page without the
     sentence that `value_advantage_gbp` did not move by a penny on any of the twelve seeds."

A +£810.18 at t = 55.86 printed beside a thesis quantity is exactly the shape that gets read as
"the selection leg is now positive and significant", and it is not: the whole advantage was
bit-identical on all twelve seeds and the £810.18 moved from one leg of the decomposition to the
other. So `test_the_magnitude_never_reaches_the_reader_without_the_sentence_that_nothing_was_
created` is the control this file is really for, and the others are its supports.

WHY THE SIZE AND ITS COUNTER-SENTENCE ARE ONE STRING IN THE FEED, which is a design decision this
file exists to hold in place. `_population_repair_bias` composes `clause` with both halves welded
together and the door renders `clause` and nothing else. The alternative -- `magnitude_gbp` as a
key and the counter-sentence as a sibling key -- fails open on the first renderer that reaches for
the number alone, and every renderer reaches for the number alone eventually, because the number
is the part that fits in a table cell. The mutation rung below poisons exactly that: a feed whose
clause keeps the magnitude and drops the counter, which is what a future well-meaning edit would
produce, and it reds.

KEYED TO THE PROPERTY, NEVER TO TODAY'S RUN OR TODAY'S NUMBER. Nothing here pins £810.18 as a
string a page must contain. What is asserted is the RELATION: whatever magnitude the feed carries
reaches the reader, and never without its counter. The day the page publishes a run taken after the
level arm was given the per-customer arm's refusal frontier, `same_priced_population` answers True,
the whole block goes unavailable and the clause comes off the page -- and
`test_both_sides_of_the_partition_are_reachable` asserts that state is REACHABLE rather than
asserting today's answer, so this file goes quiet with the page instead of reddening for it
becoming more honest.

R15 -- THE MUTATIONS, each applied and reverted:
  * drop the counter-sentence from the feed's clause, keep the magnitude
        -> `..._without_the_sentence_that_nothing_was_created` reds. This is the discriminating
           poison: every presence check in this file is green through it, because the direction,
           the magnitude and the book are all still on the page.
  * `_population_repair_bias` returns `available: False` on every branch
        -> `test_both_sides_of_the_partition_are_reachable` reds on its bias leg (DID NOT RENDER).
           A guard that refuses its whole partition passes every "does it refuse correctly" rung,
           which is why the partition is asserted over BOTH states in ONE control rather than a
           leg per branch.
  * `_population_repair_bias` returns `available: True` on every branch, including `answer is True`
        -> the same control reds on its repaired leg. Both directions are covered by one assert.
  * stop rendering `caveats[1]` in the door (revert the page to the single `caveat` slot)
        -> the reader rungs red. The generator-side block is still perfect in the feed, which is
           the whole point of driving the door rather than reading the payload.
  * render the clause MUTED rather than amber
        -> `test_the_bias_qualifies_the_figure_rather_than_footnoting_it` reds. Stripped to text
           the two are identical, so every other rung here survives it; on this page amber means
           "this qualifies the figure above" and muted means "footnote".

FAIL-CLOSED (R15). A missing harness, a door whose script throws, a feed that will not parse, a
panel the door left empty: each is a FAILURE here and never a skip, because "the bias is
unpublished" and "the bias is fine" must not report the same colour.
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
    published_blob,
    published_file,
    published_json,
    refuse_working_tree_reads,
)

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent
HARNESS = SITE / "_live_harness.mjs"

# THE SUBJECTS AS PATHS IN GIT, never files on disk -- see `test_the_published_bytes_reader` for
# why the index copy is the subject. A door test that reads the working tree cannot tell "the
# reader can see this" from "someone in this tree has fixed it and not landed it", and those are
# the only two states it exists to separate.
DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/value_arms.json"
GROWTH_REL = "site/data/book_growth.json"
CAPS_REL = "site/data/capabilities_door.json"
DD_ARMS_REL = "site/data/dd_opening_arms.json"

#: The panel the re-draw band and its per-leg definitions render into. Named rather than searched
#: for across the whole page: a clause that reached SOME element would satisfy a page-wide grep
#: while sitting somewhere a reader of the figure never looks.
PANEL = "arms-redraw"


def test_this_control_never_reads_a_working_tree_copy_of_its_own_subjects():
    refuse_working_tree_reads(__file__, (DOOR_REL, FEED_REL, GROWTH_REL, CAPS_REL, DD_ARMS_REL))


def _text(fragment: str) -> str:
    """Tags stripped and entities resolved -- what a READER sees, not what the door assigned."""
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict, raw: bool = False) -> str:
    """Drive the REAL door with `feed` and return what `#arms-redraw` put on screen."""
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    door = published_file(DOOR_REL)
    assert door.read_text() == published_blob(DOOR_REL), (
        "the materialised door is not the published bytes, so this control has no subject")
    payload = {
        "../data/value_arms.json": feed,
        "../data/dd_opening_arms.json": published_json(DD_ARMS_REL),
        "../data/book_growth.json": published_json(GROWTH_REL),
        "../data/capabilities_door.json": published_json(CAPS_REL),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(door)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=180,
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
    inner = element.get("innerHTML") or ""
    assert inner.strip(), (
        "the door left #{} empty, so the bias is UNPUBLISHED -- and an empty panel and a correct "
        "one must not report the same colour (R15)".format(PANEL))
    if raw:
        return inner
    return _text(inner) or _text(element.get("textContent") or "")


def _bias(feed: dict) -> dict:
    """The feed's own bias block, or a FAILURE naming what is missing."""
    leg = ((feed.get("current_world") or {}).get("selection_leg") or {})
    block = leg.get("population_repair_bias")
    assert isinstance(block, dict), (
        "the published feed carries no `current_world.selection_leg.population_repair_bias`, so "
        "the page has nothing to state the bias FROM. Regenerate with "
        "`tools/generate_value_arms_data.py`.")
    return block


def _published_feed() -> dict:
    return published_json(FEED_REL)


def test_the_bias_direction_and_one_magnitude_reach_the_reader():
    """DIRECTION, SIZE and BOOK, on the surface, from the feed's own figures."""
    feed = _published_feed()
    block = _bias(feed)
    if not block.get("available"):
        pytest.fail(
            "the published run carries the two-populations repair, so no bias is claimed -- but "
            "then `test_both_sides_of_the_partition_are_reachable` is the control that should be "
            "asserting this state, not this one. Reason given: {}".format(block.get("reason")))
    rendered = _render(feed)

    # THE DIRECTION. Asserted as the feed's own word, so a feed that one day says `upward` is
    # checked against what the page prints rather than against `downward` as a literal.
    direction = (block.get("direction") or "").upper()
    assert direction, "the bias block states no direction, which is half of what it is for"
    assert direction in rendered.upper(), (
        "the page never tells a reader WHICH WAY the figure is wrong. The feed says {!r} and the "
        "rendered panel does not contain it.".format(direction))

    # THE SIZE, as the page's own formatting of the feed's own number -- never a hard-coded £810.
    magnitude = block.get("magnitude_gbp")
    assert isinstance(magnitude, (int, float)), "the bias block carries no magnitude"
    printed = "£{:,.2f}".format(magnitude)
    assert printed in rendered, (
        "the magnitude {} never reaches the reader -- the caveat is back to a direction with no "
        "size, which is the defect this panel was repaired for".format(printed))

    # THE BOOK IT CAME FROM. Without this the reader is invited to subtract it from the figure
    # beside it, which is arithmetic across two instruments.
    instrument = block.get("measured_on_commit")
    against = block.get("measured_against_commit")
    assert instrument and against, "the bias block does not name the two books it was measured on"
    assert instrument in rendered and against in rendered, (
        "the page states a size without saying which book produced it ({} against {}), so a "
        "reader cannot tell it is a different instrument from the run above".format(
            instrument, against))


def test_the_magnitude_never_reaches_the_reader_without_the_sentence_that_nothing_was_created():
    """THE ITEM'S OWN FALSIFIER, and the reason this file exists.

    Every other rung here is a presence check and all of them are green on a page that publishes
    "+£810.18, t = 55.86" beside the thesis quantity with no counter. That page is WRONG, and
    wrong in the single most expensive direction available: it reads as "the selection leg is now
    positive and significant". The whole advantage did not move by a penny.
    """
    feed = _published_feed()
    block = _bias(feed)
    assert block.get("available"), (
        "no bias is published, so this control has no subject -- and that is a state "
        "`test_both_sides_of_the_partition_are_reachable` owns, not a pass here")
    rendered = _render(feed)
    printed = "£{:,.2f}".format(block["magnitude_gbp"])
    assert printed in rendered, "the magnitude is not on the page at all"

    # THE COUNTER, asserted as the PROPERTY rather than as a sentence: the reader is told the
    # whole advantage did not move, and told the size moved BETWEEN the legs. Both halves, because
    # "unchanged" alone does not say where £810 went and "moved between legs" alone does not say
    # the total held.
    moved = block.get("total_advantage_moved_gbp")
    assert moved == 0, (
        "the bias block no longer records that the whole advantage was unmoved, so the counter "
        "it publishes is not the measured one")
    assert "£0.00" in rendered, (
        "THE SIZE IS ON THE PAGE WITHOUT THE SENTENCE THAT NOTHING WAS CREATED. A reader meets "
        "{} beside the thesis quantity and is never told the whole advantage moved by £0.00 on "
        "every one of those seeds. This is the exact shape the item that drew this work named as "
        "its own falsifier.".format(printed))
    assert block.get("is_a_correction_to_the_figure_above") is False, (
        "the bias block no longer disclaims being a correction to the figure it sits beside")
    assert "NOT A CORRECTION" in rendered.upper(), (
        "the page states a size beside the figure and never says it is NOT a correction to it, "
        "so the arithmetic a reader is invited to do is subtraction across two instruments")


def _shared(block: dict) -> dict:
    """The bias block's reading of the repaired book, or a FAILURE naming what is missing."""
    shared = block.get("sign_on_the_shared_population")
    assert isinstance(shared, dict), (
        "the bias block carries no `sign_on_the_shared_population`, so the page states which way "
        "the figure is wrong and never what it is worth where it is not wrong. Regenerate with "
        "`tools/generate_value_arms_data.py`.")
    return shared


def test_the_bias_size_never_reaches_the_reader_without_the_sign_on_the_shared_population():
    """THE SECOND FALSIFIER, and the one the bias size CREATED (2026-09-20, Lane 0).

    `..._without_the_sentence_that_nothing_was_created` defends against the size being read as a
    GAIN. This defends against the remaining reading, which the repair above made available for
    the first time: the size being read as a CORRECTION the reader applies themselves. A page that
    says "+£270.21" and "biased downward by £810.18" and stops there has handed a reader two
    numbers and one obvious operation, and the total they reach -- about £1,080, positive -- is a
    number this project has never measured and cannot state.

    The instrument that priced the bias drew a family on its own repaired book in the same turn.
    That family puts the choosing at a NEGATIVE mean and cannot state a sign at all: 0.166 of the
    2.0 SEMs it needs. Both readings came off one instrument on one day and only the flattering
    one reached the page. So the property asserted here is that they travel together.

    KEYED TO THE PROPERTY, NOT TO -£259.29. Nothing below pins the mean, the SEM count or the
    seed price as literals. What is asserted is that WHATEVER the feed's shared-population reading
    says, the reader meets it -- and never meets its mean without the refusal that the sign is not
    stateable. The day a wider family DOES state a sign, `sign_is_stateable` turns True, the
    refusal leg goes quiet by itself and the reader rung still holds.
    """
    feed = _published_feed()
    block = _bias(feed)
    assert block.get("available"), (
        "no bias is published, so this control has no subject -- and that is a state "
        "`test_both_sides_of_the_partition_are_reachable` owns, not a pass here")
    shared = _shared(block)
    rendered = _render(feed)
    printed = "£{:,.2f}".format(block["magnitude_gbp"])
    assert printed in rendered, "the magnitude is not on the page at all"

    if not shared.get("available"):
        # FAILING CLOSED IS A PASS ONLY IF IT IS SAID OUT LOUD. A missing family restores exactly
        # the state this rung exists to end, so silence here is the defect and the reason must be
        # the thing that reaches the reader instead.
        why = shared.get("why_not") or ""
        assert why, "the shared-population block is unavailable and records no reason"
        assert "NOT STATED HERE" in rendered.upper(), (
            "no family drawn on the repaired book is readable, and the page says nothing about "
            "it -- so a reader meets {} with a bias direction and no indication that what the "
            "figure is worth unbiased is unmeasured. A 'we cannot tell' belongs on the page, not "
            "in a missing file.".format(printed))
        return

    # THE MEAN, as the page's own formatting of the feed's own number. The minus goes BEFORE the
    # symbol because that is what the clause composes, and a rung that accepted either spelling
    # would be green on a page that printed "£-259.29" at a reader.
    mean = shared.get("mean_gbp")
    assert isinstance(mean, (int, float)), "the shared-population block carries no mean"
    mean_printed = ("-£{:,.2f}".format(abs(mean)) if mean < 0 else "£{:,.2f}".format(mean))
    assert mean_printed in rendered, (
        "the page prices the BIAS at {} and never tells the reader what the choosing is worth on "
        "the book where the bias is absent ({}). The only arithmetic left available to them is "
        "adding the two, and the number that produces has never been measured.".format(
            printed, mean_printed))

    # AND THE MEAN NEVER TRAVELS WITHOUT ITS DISTANCE. This is the discriminating half: a page
    # carrying "-£259.29" alone states a DIRECTION the family cannot carry, which is the same
    # defect as the bias size alone, pointing the other way.
    if shared.get("sign_is_stateable") is False:
        assert "NOT STATEABLE" in rendered.upper(), (
            "the mean {} reaches the reader and the refusal does not, so the page states that "
            "the choosing is worth less than nothing on a fair population -- a direction this "
            "family is {} SEMs from being able to carry".format(
                mean_printed, shared.get("sems_from_zero")))
        assert "CANNOT TELL" in rendered.upper(), (
            "the page never states the result in the words the result is in. 'We cannot tell' "
            "is this leg's finding, and a finding that only appears as a small number beside a "
            "large one is not published")
        # THE DISTANCE, AND "THERE IS NO FINITE DISTANCE" IS ONE OF ITS ANSWERS (2026-09-22).
        # This leg read `seeds_needed_to_state_a_sign` and required an int, which made it a
        # control keyed to TODAY'S ANSWER in the exact way this file's own docstring above
        # disclaims: it went RED the day the producer stopped publishing 1,744 -- a count whose
        # denominator is an estimate a sixth of a standard error from zero, so it had no upper
        # bound and 1,744 was merely where the arithmetic happened to land. A bare count is the
        # WEAKER publication, not the stronger one, and a door that demands it rewards the
        # defect. The property is unchanged and is still both-sided: a refusal must carry its
        # distance, so the reader can tell one more draws would close from one that never
        # resolves. What changed is that the second of those is now sayable.
        needed = shared.get("seeds_needed_to_state_a_sign")
        if isinstance(needed, int) and needed > 0:
            assert "{:,}".format(needed) in rendered, (
                "the page refuses to state a sign and never says how far it is from stating "
                "one. A refusal without its distance cannot be told from one that will never "
                "resolve")
        else:
            assert shared.get("seeds_needed_unavailable"), (
                "the shared-population block publishes no seed price and no reason for "
                "withholding one, so the refusal is a shrug rather than a measurement")
            interval = shared.get("seeds_needed_interval") or {}
            assert interval.get("has_no_upper_bound") is True, (
                "no seed price is published and the block does not say the price is unbounded "
                "either, so a reader cannot tell a withheld count from an uncomputed one")
            # THE ENDPOINTS IT WAS PRICED OVER REACH THE READER. This is what stops the
            # withholding from being silence: the day the producer drops the sentence, these
            # numbers leave the page and this goes red. Endpoints past the search ceiling arrive
            # as `None` -- a measurement, not a gap -- and carry no numeral to look for.
            priced = [interval.get(k) for k in (
                "at_the_point_estimate", "price_at_the_low_end_of_the_denominator",
                "price_at_the_high_end_of_the_denominator")]
            assert any(isinstance(p, int) for p in priced), (
                "the block claims an unbounded price and priced it at no point at all, so the "
                "claim rests on nothing a reader could check: {!r}".format(interval))
            for count in [p for p in priced if isinstance(p, int)]:
                assert ("{} seeds".format(count) in rendered
                        or "{:,} seeds".format(count) in rendered), (
                    "the block priced the question at {} seeds and the reader never meets that "
                    "number, so the page refuses without saying what the refusal rests "
                    "on".format(count))

    # THE TWO INSTRUMENTS STAY TWO. The whole point of the mean is that it is NOT this page's run,
    # and a block that let itself be netted against the published figure would rebuild the defect.
    assert shared.get("may_be_netted_against_the_published_figure") is False, (
        "the shared-population block no longer disclaims being nettable against the figure it "
        "sits beside, which is the arithmetic across two instruments this panel refuses")
    assert shared.get("is_this_pages_run") is False, (
        "the shared-population block claims to be this page's own run, which it is not -- it was "
        "drawn on the repair instrument, 20 paths of pricing code away")


def test_MUTATION_a_clause_that_keeps_the_bias_size_and_drops_the_shared_population_sign_is_caught():
    """The poison that produces TODAY'S PAGE, applied to the feed and never to the door.

    Before 2026-09-20 the clause ended at "The choosing figure stands as published." Every other
    rung in this file is green on that string -- the direction, the size, the book and the
    nothing-was-created counter are all still in it. What it does not carry is any statement of
    what the choosing is worth where the populations match, and that omission is the one a reader
    fills in themselves, upward. So the mutation is the clause truncated at exactly the sentence
    it used to end on.
    """
    feed = _published_feed()
    block = _bias(feed)
    if not block.get("available"):
        pytest.fail("no bias is published; this control has no subject")
    shared = _shared(block)
    if not shared.get("available"):
        pytest.skip("no family on the repaired book, so the sentence to poison is the fail-closed "
                    "one and `..._without_the_sign_on_the_shared_population` already drives it")

    clause = block["clause"]
    marker = "AND HERE IS WHAT THE SAME INSTRUMENT SAYS"
    assert marker in clause, (
        "the clause no longer composes the shared-population sentence, so this mutation has "
        "nothing to cut and the control it proves is not the one running")
    cut = clause.split(marker)[0].strip()

    poisoned = copy.deepcopy(feed)
    poisoned["current_world"]["selection_leg"]["population_repair_bias"] = dict(
        block, clause=cut)
    shown = _render(poisoned)

    printed = "£{:,.2f}".format(block["magnitude_gbp"])
    # THE POISON IS REAL: the page still looks complete by every earlier rung's standard.
    assert printed in shown, "the poisoned feed did not even render the size"
    assert "£0.00" in shown, (
        "the poison cut the nothing-was-created counter too, so it is a cruder mutation than "
        "intended and does not isolate the shared-population sentence")
    # AND THE SIGN IS GONE, which is what the real control must red on.
    mean = shared.get("mean_gbp")
    mean_printed = ("-£{:,.2f}".format(abs(mean)) if mean < 0 else "£{:,.2f}".format(mean))
    assert mean_printed not in shown, (
        "the poison failed: the shared-population mean reached the reader from somewhere other "
        "than the clause, which would mean the welding this rung defends is not load-bearing")
    assert "CANNOT TELL" not in shown.upper(), (
        "the poison failed: the refusal reached the reader from another element, so cutting the "
        "clause is not what this control is actually detecting")


def test_the_bias_qualifies_the_figure_rather_than_footnoting_it():
    """AMBER, not muted. On this page the colour is the claim about the figure's standing.

    Stripped to text an amber qualification and a muted footnote are identical, so every other
    rung in this file survives a mutation that renders this block muted -- and a reader who meets
    the size in footnote grey reads the figure above as standing unqualified.
    """
    feed = _published_feed()
    block = _bias(feed)
    if not block.get("available"):
        pytest.fail("no bias is published; this control has no subject")
    raw = _render(feed, raw=True)
    clause = block.get("clause") or ""
    head = html_lib.escape(clause.split(".")[0])[:60]
    assert head, "the bias block carries no clause"
    window = raw[max(0, raw.find(head) - 400):raw.find(head)] if head in raw else ""
    assert head in raw, (
        "the bias clause is not in the door's markup at all, so its styling cannot be judged")
    assert "--amber" in window, (
        "the bias clause is rendered without the amber that says it QUALIFIES the figure above. "
        "In muted it reads as a footnote and the figure reads as standing unqualified.")


def test_both_sides_of_the_partition_are_reachable():
    """ONE CONTROL OVER THE WHOLE PARTITION, because a guard that refuses everything passes every
    "does it refuse correctly" rung this file could otherwise write.

    The bias block is a three-valued question (`same_priced_population` answering None, False or
    True) collapsed onto two page states. Both states are driven through the REAL door here:

      * a run WITHOUT the repair  -> the clause is on the page.
      * a run WITH the repair     -> the clause is GONE, with nothing left behind.

    Asserting only the first is how a block that renders unconditionally stays green while the
    page tells a reader a repaired run is contaminated. Asserting only the second is how a block
    that renders NEVER stays green while the caveat silently leaves the page. Neither is written
    as its own test on purpose -- a leg per branch is what let the same trap be entered three
    times in one afternoon through three different doors.
    """
    import sys
    sys.path.insert(0, str(PROJECT))
    from tools.generate_value_arms_data import _population_repair_bias

    # GENERATOR SIDE: the partition is a property of the artefact's own field, so it is exercised
    # on synthetic artefacts rather than by waiting for a repaired run to be published.
    without = _population_repair_bias(
        {"decision_population": {"priced_by_arm": {"level_arm": 281, "value_arm": 214}}})
    measured_false = _population_repair_bias(
        {"decision_population": {"same_priced_population": {"answer": False},
                                 "priced_by_arm": {"level_arm": 107, "value_arm": 104}}})
    with_repair = _population_repair_bias(
        {"decision_population": {"same_priced_population": {"answer": True}}})
    assert without["available"] and measured_false["available"], (
        "a run that never asked, and a run that asked and got False, must BOTH take the bias "
        "branch -- absence here is not neutrality, it is the signature of a run that predates "
        "the repair")
    assert not with_repair["available"], (
        "a run carrying the repair still claims a bias, so this block would go on asserting a "
        "defect in runs where it was measured away")
    assert with_repair.get("reason"), "the cleared branch is silent about WHY it cleared"

    # READER SIDE: both states driven through the real door, because the generator being right is
    # not the claim -- the claim is what a reader sees.
    feed = _published_feed()
    biased = copy.deepcopy(feed)
    biased["current_world"]["selection_leg"]["population_repair_bias"] = without
    shown = _render(biased)
    assert "£{:,.2f}".format(without["magnitude_gbp"]) in shown, (
        "the door did not render a bias block that IS available -- the clause reaches no reader")

    repaired = copy.deepcopy(feed)
    repaired["current_world"]["selection_leg"]["population_repair_bias"] = with_repair
    gone = _render(repaired)
    assert "£{:,.2f}".format(without["magnitude_gbp"]) not in gone, (
        "the door renders the bias magnitude even when the published run CARRIES the repair, so "
        "the clause can never come off the page and will one day be defaming a clean run")
    assert "BIASED DOWNWARD" not in gone.upper(), (
        "the repaired state still tells a reader the figure is biased downward")

    # AND THE PANEL IS STILL A PANEL IN BOTH STATES. A door that renders the cleared state by
    # throwing, or by emptying the block the legs live in, would satisfy the absence check above.
    assert "of which, the choosing" in gone, (
        "the cleared state took the selection leg's own definition off the page with it")


def test_MUTATION_a_clause_that_keeps_the_size_and_drops_the_counter_is_caught():
    """THE POISON THIS FILE WAS WRITTEN AROUND, applied to the FEED and never to the door.

    A test may not edit production. Each page must satisfy its OWN feed, so the mutation is a feed
    whose `clause` carries the direction, the size and the book -- everything the presence rungs
    look for -- and has had the counter-sentence cut out of it. That is precisely what a future
    edit "tightening the wording" produces, and it is invisible to every other control here.
    """
    feed = _published_feed()
    block = _bias(feed)
    if not block.get("available"):
        pytest.fail("no bias is published; this control has no subject")

    poisoned = copy.deepcopy(feed)
    clause = block["clause"]
    cut = clause.split("THAT SIZE IS NOT A GAIN")[0] + (
        "AND IT IS A DIFFERENT BOOK FROM THIS ONE: it was measured on `{}` against `{}`.".format(
            block["measured_on_commit"], block["measured_against_commit"]))
    assert "£0.00" not in cut and "NOT A CORRECTION" not in cut.upper(), (
        "the poison did not actually remove the counter, so this mutation proves nothing")
    poisoned["current_world"]["selection_leg"]["population_repair_bias"] = dict(block, clause=cut)

    shown = _render(poisoned)
    printed = "£{:,.2f}".format(block["magnitude_gbp"])
    # THE POISON IS REAL: the size still reaches the reader and the page still looks complete.
    assert printed in shown, "the poisoned feed did not even render the size"
    assert (block.get("direction") or "").upper() in shown.upper(), (
        "the poisoned feed dropped the direction too, so it is a cruder mutation than intended "
        "and does not prove the counter is what is being defended")
    # AND THE COUNTER IS GONE, which is what the real control must red on.
    assert "£0.00" not in shown, (
        "the poison failed: the counter-sentence reached the reader from somewhere other than "
        "the clause, which would mean the welding this file defends is not load-bearing")
