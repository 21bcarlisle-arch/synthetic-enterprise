"""THE READING A READER MEETS FIRST IS THE UNCONDITIONED ONE, and the withheld reason is said once.

TWO DEFECTS, ONE FIELD, both found 2026-09-23 in `tools/generate_value_arms_data.py`.

THE FIRST IS THE ORDERING. `method_skill.concordance` -- 0.482 on 54 decisions -- led the
capabilities page's method block under the caption "Does the method work?". The block's own
`survivorship` split establishes that ALL 44 decisions that figure could not score are renewals the
world recorded as departures and that not one scored decision is, so the published headline answers
"GIVEN the household stayed, did the arm's price rank the joint value?" while the caption asks the
unconditional question -- and the split's own text says a larger book does not fix it. The estimand
that DOES answer the caption was already computed, already in the payload one key away, and pointed
the unflattering way: 0.4396 on 85 decisions. One concept, two populations, the split chosen before
the definition, with the flattering cut published as the headline. That is this project's named
recurring failure and this is the control that makes the repair unable to rot back.

THE SECOND IS THE DUPLICATION. `_seed_spreads` withholds every bound on a clock for ONE reason, and
`_selection_sentence` composes TWO refusals from it. Both legs were withheld on the published run,
so `headline` went out carrying the same ~1,000-character paragraph twice, verbatim, in one field.
`_cannot_resolve`'s own docstring had already argued the rule for the REMEDY -- "a remedy stapled to
each printed the same forty words twice in one paragraph" -- and the reason was left behind.

KEYED TO THE PROPERTIES, NOT TO TODAY'S FIGURES. Nothing here asserts that the estimand is 0.4396 or
that it reads below chance; the day it clears its null it still leads, and the day a third cut lands
it still leads. What is pinned is that the row leading the list is the one whose population is not
selected by survival, that each row carries its own n and its own interval, that the conditioning
clause is READ off the split rather than asserted, and that one withheld reason reaches the reader
once with both legs still refusing.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import generate_value_arms_data as gva  # noqa: E402

#: A withheld reason long and odd enough that a second copy cannot be mistaken for prose the
#: composer happened to repeat. The defect was a verbatim repeat, so the control counts occurrences.
A_WITHHELD_REASON = (
    "THE ERROR BAR IS OLDER THAN THE FIGURE IT BOUNDS, and this sentence is the marker a "
    "duplicate would carry."
)


def _published_block() -> dict:
    """The method-skill block the page actually publishes, from the canonical run artefact."""
    three_arm = gva._read(gva.THREE_ARM_PATH)
    if not three_arm:
        raise AssertionError(
            "the canonical three-arm artefact is unreadable at {}, so this control is measuring "
            "an absence -- fix the artefact, not this test".format(gva.THREE_ARM_PATH))
    return gva._method_skill(three_arm)


def test_the_unconditioned_estimand_is_the_reading_a_reader_meets_first():
    """THE DEFECT ITSELF. Fires on the survivor cut being restored to the head of the list.

    The assertion is over the CONDITIONING FLAG, never over which key or which number came first:
    a control pinned to `fixed_horizon` by name goes green the day a differently-named unselected
    cut takes the lead, and a control pinned to 0.4396 reds the day the run moves. What is
    published first must be a reading whose population was not selected by survival.
    """
    block = _published_block()
    order = block["reading_order"]
    assert order["available"] is True, (
        "the published run carries no reading order at all ({}), so this control is measuring an "
        "absence rather than the ordering".format(order.get("reason")))
    assert len(order["readings"]) >= 2, (
        "only one reading reached the page, so no ordering was published and the survivor cut "
        "leads by default with nothing saying so")

    lead = order["readings"][0]
    assert lead["conditioned_on_survival"] is False, (
        "the reading a reader meets first is conditioned on survival (or its conditioning was "
        "never measured), which is the defect: the caption asks the unconditional question")
    assert any(r["conditioned_on_survival"] for r in order["readings"][1:]), (
        "the survivor cut is not published beside the estimand -- a rung reported alone is a rung "
        "chosen, and dropping the conditioned one is the same defect in the other direction")


def test_every_reading_carries_its_own_population_and_its_own_interval():
    """NO BORROWED BOUNDS. Fires on a row published without the n or the interval it earned.

    This is the fail-closed rule one rung up from `_horizon_leg_published`, arriving through the
    ordering instead of through the figure: two concordances over two populations sharing one
    interval is exactly what this block has published before.
    """
    order = _published_block()["reading_order"]
    seen_populations = set()
    for reading in order["readings"]:
        for field in ("concordance", "null_95_low", "null_95_high", "decisions", "accounts"):
            assert reading.get(field) is not None, (
                "reading {} reached the page without its own {}".format(reading["key"], field))
        assert str(reading["decisions"]) in reading["sentence"], (
            "reading {} does not name the population it is scored over in the sentence a reader "
            "sees".format(reading["key"]))
        assert "{:.3f}".format(reading["concordance"]) in reading["sentence"]
        assert "{:.3f}".format(reading["null_95_low"]) in reading["sentence"], (
            "reading {} states a figure without the interval a no-information signal reaches on "
            "its OWN decisions".format(reading["key"]))
        seen_populations.add((reading["decisions"], reading["accounts"]))
    assert len(seen_populations) == len(order["readings"]), (
        "two readings are published over the same population, so one of them is the other under a "
        "second name and the page invites a difference that is not a quantity")
    assert order["not_combined"], (
        "the page publishes two populations and says nothing about differencing them")


def _order_with_split(split: dict | None) -> dict:
    """The real composer, driven with one survivorship split and the published estimand."""
    block = _published_block()
    return gva._skill_reading_order(block, split, block["fixed_horizon"])


def test_the_conditioning_clause_is_READ_off_the_split_and_never_asserted():
    """THREE STATES, THREE SENTENCES, and the partition asserted by DISTINCTNESS.

    "This figure is not conditioned on survival" and "nobody measured whether it is" are opposite
    instructions to a reader, and a control that only checked the amber case would pass a composer
    that collapsed the two. So all three are driven and the three sentences are required to be
    three, not two.

    Fires on: the clause being typed rather than read; any two of the three states collapsing.
    """
    sentences = {}
    for name, split in (
            ("conditioned", {"available": True,
                             "the_concordance_is_conditioned_on_survival": True,
                             "decisions_dropped_for_no_settled_row": 44}),
            ("not_conditioned", {"available": True,
                                 "the_concordance_is_conditioned_on_survival": False,
                                 "decisions_dropped_for_no_settled_row": 44}),
            ("never_measured", {"available": False, "reason": "the split is absent"})):
        order = _order_with_split(split)
        survivor = [r for r in order["readings"]
                    if r["key"] == gva.SURVIVOR_READING_KEY]
        assert survivor, "the survivor cut vanished from the ordering on the {} split".format(name)
        sentences[name] = survivor[0]["sentence"]

    assert len(set(sentences.values())) == 3, (
        "two of the three conditioning states render the same sentence, so a reader cannot tell "
        "them apart: {}".format(sorted(sentences)))
    assert "conditional on survival" in sentences["conditioned"]
    assert "conditional on survival" not in sentences["not_conditioned"], (
        "a run whose split says the figure is NOT survivor-conditioned still carries the caveat, "
        "which is a caveat asserted rather than read")
    assert "not measured on this run" in sentences["never_measured"], (
        "an unmeasured split renders as one of the two answers instead of saying it was not asked")


def test_a_run_with_no_estimand_says_WHY_the_survivor_cut_leads():
    """FAIL CLOSED, AND SAY SO. Fires on the block reverting to the flattering cut in silence.

    A page that quietly leads with the survivor cut is indistinguishable from one that asked for
    the estimand and was told no, and the second is the state a reader has to be able to see.
    """
    block = _published_block()
    absent = {"available": False, "reason": "this run predates the fixed-horizon estimand."}
    order = gva._skill_reading_order(block, block["survivorship"], absent)

    assert order["available"] is True, "the block withheld the survivor cut it can still publish"
    assert len(order["readings"]) == 1
    assert order["readings"][0]["key"] == gva.SURVIVOR_READING_KEY
    assert order["the_estimand_verdict_is_in_the_lead"] is False
    assert order["reason"] and "predates the fixed-horizon estimand" in order["reason"], (
        "the survivor cut leads and the page does not carry the producer's own reason for it")


def _resolve_verdict(block: dict, reading: dict):
    """The door's own resolver, in Python: walk `verdict_key` from the method-skill block."""
    if not reading.get("verdict_key"):
        return None
    node = block
    for part in reading["verdict_key"].split("."):
        node = (node or {}).get(part)
    return node


def test_a_readings_verdict_is_NAMED_and_never_copied_onto_the_row():
    """ONE SENTENCE, ONE HOME IN THE PAYLOAD. Fires on the row carrying a copy of its verdict.

    A copy renders the same words and leaves the field that OWNS them rendering nowhere, and that
    is load-bearing here rather than tidy: `_skill_sample_size_explanation` says "the figure beside
    this" and is registered in the pointer census against `.method_skill.cannot_tell`. A page
    rendering a copy points a reader at something the door does not render -- which is how this
    control was bought, by `test_every_undriven_pointer_is_true_from_the_region_it_lands_in`
    refusing the first draft of this change.
    """
    block = _published_block()
    for reading in block["reading_order"]["readings"]:
        assert "cannot_tell" not in reading, (
            "reading {} carries a COPY of its verdict, so the field that owns that sentence can "
            "stop rendering with nothing noticing".format(reading["key"]))
        resolved = _resolve_verdict(block, reading)
        assert reading.get("verdict_key") is None or isinstance(resolved, str) and resolved, (
            "reading {} names `{}` for its verdict and nothing resolves there, so the page "
            "renders a figure with no refusal beside it".format(
                reading["key"], reading.get("verdict_key")))


def test_the_estimand_verdict_travels_with_its_figure_exactly_once():
    """The flag the page reads to stop printing one sentence in two places.

    `readingOrder` renders the estimand's "we cannot tell" beside its own number, so
    `fixedHorizonBlock` must not render it again -- the duplication being repaired in `headline` in
    the same change, arriving through a different door.

    Fires on: the lead carrying the verdict while the flag says it does not, or the reverse.
    """
    block = _published_block()
    order = block["reading_order"]
    lead = order["readings"][0]
    assert order["the_estimand_verdict_is_in_the_lead"] is bool(_resolve_verdict(block, lead)), (
        "the flag the page gates the bridge's verdict on disagrees with whether the lead actually "
        "carries that sentence, so the page either prints it twice or not at all")


def test_one_withheld_reason_reaches_the_headline_once_and_both_legs_still_refuse():
    """THE DUPLICATION, AND THE FALL-THROUGH THE FIX COULD HAVE INTRODUCED.

    Counting to one is only half of it. `_cannot_resolve` chooses its branch on whether a reason
    EXISTS and takes the text only to decide whether to print it, because a second leg that saw
    `None` and fell through would publish "no seed spread has been measured for that contrast on
    this clock" -- a refusal naming a cause nobody observed, which is strictly worse than the
    repetition it replaced.

    Fires on: the reason being printed per leg again; the second leg losing its refusal; the
    second leg claiming no floor was ever run.
    """
    sentence = gva._selection_sentence(
        4327.0, 0.5, 4579.0, {"available": False, "reason": A_WITHHELD_REASON}, None, None)

    assert sentence.count(A_WITHHELD_REASON) == 1, (
        "the withheld reason reaches the reader {} times in one field".format(
            sentence.count(A_WITHHELD_REASON)))
    assert sentence.count("Its DIRECTION is not stated here") == 2, (
        "one of the two withheld legs stopped stating its own refusal, so a reader meets a figure "
        "with no sign and nothing saying the sign was withheld")
    assert "No seed spread has been measured" not in sentence, (
        "the second leg fell through to the never-measured branch, which names a cause nobody "
        "observed and sends the reader to re-run a floor that has already been run")


def test_the_reason_is_STILL_PRINTED_when_only_one_leg_is_withheld():
    """THE OTHER SIDE OF THE SAME GATE, and the reason this is not a flag.

    A run where only the selection leg is withheld must carry the full reason on that leg: the
    token is taken by whichever refusal reaches it first, so "first" must not mean "the advantage
    leg or nobody".

    Fires on: the reason being attached to one particular leg rather than to the first that needs
    it.
    """
    sentence = gva._selection_sentence(
        4327.0, 0.5, None, {"available": False, "reason": A_WITHHELD_REASON}, None, None)
    assert sentence.count(A_WITHHELD_REASON) == 1, (
        "the only withheld leg on this run reaches the reader without its reason")
