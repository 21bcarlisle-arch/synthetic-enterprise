"""Independence is not inference — the standing rule, driven with numbers.

WHAT EACH TEST HERE NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_INDEPENDENCE_ALONE_DOES_NOT_MAKE_THE_GAP_EVIDENCE_OF_SKILL` — THE ONE THE RULE EXISTS
    FOR, and the defect is what the code actually did until 2026-08-30:
    `publishable_as_evidence_of_inference = not provenance["co_calibrated"]`, an identity between
    "the two sides don't share a source" and "the company inferred something". The first removes
    an objection; the second is a claim about skill that needs its own evidence.
  * `test_a_method_that_clears_its_null_on_DEPENDENT_sides_is_still_not_evidence` — the mirror,
    so the composition is pinned as a conjunction from both directions rather than from the side
    that happens to be live today.
  * `test_an_UNDECIDABLE_leg_never_satisfies_the_claim` — the fail-closed defect: `None` treated
    as truthy, or a missing reading recorded as a failed one. Both would let "we could not check"
    read as an answer, in opposite directions.
  * `test_a_missing_reading_is_NOT_the_same_as_a_failed_one` — the finer half of the above. A run
    with no null spread and a run whose method sat inside its null both give
    `publishable: False`, but only the first is fixable by scoring more decisions, so they must
    be distinguishable in the record.
  * `test_the_page_says_WE_CANNOT_TELL_in_those_words` — the director specified the phrase. A
    softer synonym ("early evidence", "suggestive") is the defect, because it moves the reader
    while the flag beside it stays False.
  * `test_no_sentence_names_the_reading_without_its_interval` — the second condition: the gap and
    the skill claim "must not appear in one sentence without the null interval beside them". A
    bare 0.614 reads as a result; 0.614 against 0.283-0.717 reads as what it is.
  * `test_independence_is_reported_WITH_the_inaccuracy_that_produced_it` — the defect where a
    reader takes the size of the gap for the size of the insight. The company is outside the
    published band in 8 of 10 years; that is WHY it is independent, and a company that is simply
    wrong produces the same number as one that knows something.

R15 MUTATIONS, each applied in place and reverted, with the OBSERVED result recorded:
  * `inference_claim`: `and` -> `or` in the composition -> **4 red**, the two named cases plus
    two of the undecidable parametrisations. Recorded as four rather than the two predicted,
    because a mutation firing more controls than expected is worth knowing: the conjunction is
    load-bearing in the undecidable branch as well as the two decided ones.
  * `inference_claim`: `(clears is True)` -> `bool(clears)` -> **0 red on the first pass**, and
    it is an EQUIVALENCE rather than a gap for the values `skill_reading` produces: that function
    only ever emits `True`/`False`/`None`, and `bool(None)` is already False. Established rather
    than assumed, then made load-bearing: `inference_claim` also takes an INJECTED reading, where
    a `1` or a truthy string is how a non-answer becomes an answer.
    `..._a_TRUTHY_NON_BOOLEAN_is_not_an_answer` was added and the mutation now fires **4 red**.
  * `_no_reading`: `"clears_the_null": None` -> `False` -> **3 red**
    (`..._a_missing_reading_is_NOT_the_same_as_a_failed_one`, `..._a_run_carrying_a_concordance_
    but_NO_SPREAD_is_undecidable`, `..._an_UNREADABLE_artefact_refuses_rather_than_defaulting`).
  * `_sentence`: `CANNOT_TELL` -> `"the evidence is early"` -> **1 red**
    (`..._the_page_says_WE_CANNOT_TELL_in_those_words`).
  * `_interval_phrase`: return only `"{:.3f}".format(concordance)` -> **1 red**
    (`..._no_sentence_names_the_reading_without_its_interval`).
  * `_sentence`: `tail = ""` unconditionally -> **1 red**
    (`..._independence_is_reported_WITH_the_inaccuracy_that_produced_it`).
"""
from __future__ import annotations

import pytest

from tools import inference_claim as ic


def _skill(*, clears: bool | None, available: bool = True) -> dict:
    """A method-skill reading with the shape the run artefact produces."""
    if not available:
        return ic._no_reading("this run carried no method-skill reading")
    return {"available": True, "concordance": 0.6136, "null_95_low": 0.2833,
            "null_95_high": 0.7167, "null_point": 0.5, "p_two_sided": 0.47,
            "decisions_scored": 12, "clears_the_null": clears, "why": None}


def _provenance(*, co_calibrated: bool | None, years_outside: int = 0) -> dict:
    """A shared-calibration verdict, with the company side's distance from the record."""
    outside = [{"year": 2016 + i, "reads_pct": 34.94, "band_pct": [17.0, 17.6]}
               for i in range(years_outside)]
    return {"co_calibrated": co_calibrated,
            "series": "DESNZ electricity switching series 2015-2025",
            "sides": {"company": {"years_checked": 10, "years_outside_the_band": outside},
                      "world": {"years_checked": 10, "years_outside_the_band": []}}}


def test_INDEPENDENCE_ALONE_DOES_NOT_MAKE_THE_GAP_EVIDENCE_OF_SKILL():
    """The two sides are independent AND the method cannot be told from chance.

    This is the live reading, and it is the case the old code got wrong: it published the gap as
    evidence of inference on the strength of independence alone.
    """
    claim = ic.inference_claim(_provenance(co_calibrated=False),
                               _skill(clears=False))

    assert claim["sides_are_independent"] is True
    assert claim["the_method_clears_its_null"] is False
    assert claim["publishable_as_evidence_of_skill"] is False
    # And the gap itself is NOT withheld -- it is a real measurement of a real disagreement.
    assert claim["the_gap_is_a_measurement"] is True


def test_a_method_that_clears_its_null_on_DEPENDENT_sides_is_still_not_evidence():
    """The mirror leg. A method that clears its null while both sides share a source has cleared
    a null on its own reflection, which is not a result about the world."""
    claim = ic.inference_claim(_provenance(co_calibrated=True), _skill(clears=True))

    assert claim["sides_are_independent"] is False
    assert claim["the_method_clears_its_null"] is True
    assert claim["publishable_as_evidence_of_skill"] is False


def test_BOTH_legs_together_are_what_permits_the_claim():
    """THE OTHER HALF OF THE NULL. A rule that can never be satisfied is a constant, and a
    constant caveat teaches a reader to skip it. Independent sides plus a method outside its own
    null is the case the claim is FOR, and it must come out True."""
    claim = ic.inference_claim(_provenance(co_calibrated=False), _skill(clears=True))

    assert claim["publishable_as_evidence_of_skill"] is True
    assert ic.CANNOT_TELL not in claim["sentence"]
    assert "quotable as evidence" in claim["sentence"]


@pytest.mark.parametrize("independent,clears", [(None, True), (False, None), (None, None)])
def test_an_UNDECIDABLE_leg_never_satisfies_the_claim(independent, clears):
    """`None` is not True and must never be read as one.

    A provenance dict carrying no boolean, and a run carrying no decidable reading, are both
    "we could not check". An unavailable check is a failed check, so neither can carry the claim
    -- and truthiness on either leg would let one of them through.
    """
    claim = ic.inference_claim(_provenance(co_calibrated=independent),
                               _skill(clears=clears))

    assert claim["publishable_as_evidence_of_skill"] is False
    assert ic.CANNOT_TELL in claim["sentence"]


@pytest.mark.parametrize("not_a_verdict", [1, "yes", 0.5, [True]])
def test_a_TRUTHY_NON_BOOLEAN_is_not_an_answer(not_a_verdict):
    """`is True`, not truthiness, and this is what makes that load-bearing.

    `skill_reading` only ever produces `True`/`False`/`None`, so `bool(clears)` and
    `clears is True` are equivalent on its output -- the mutation swapping them does not fire on
    the tests above, and that is an equivalence rather than a gap. But `inference_claim` takes an
    INJECTED reading too, and a JSON artefact that writes `1` for a verdict, or a caller that
    passes a truthy string, is exactly how a non-answer becomes an answer. A `1` is not a
    measurement that cleared its null; it is a field nobody validated.
    """
    skill = _skill(clears=True)
    skill["clears_the_null"] = not_a_verdict
    claim = ic.inference_claim(_provenance(co_calibrated=False), skill)

    assert claim["publishable_as_evidence_of_skill"] is False, (
        f"a `clears_the_null` of {not_a_verdict!r} carried the skill claim")
    assert ic.CANNOT_TELL in claim["sentence"]


def test_a_missing_reading_is_NOT_the_same_as_a_failed_one():
    """Two runs both give `publishable: False` and only one of them is fixable by running
    something. Recording an absent reading as a failed one loses that, and loses it in the
    direction that stops anyone looking for the fix."""
    absent = ic.skill_reading(payload={"method_skill": {"available": False,
                                                        "reason": "no reading"}})
    assert absent["clears_the_null"] is None
    assert absent["available"] is False
    assert absent["why"]

    inside = ic.skill_reading(payload={"method_skill": {
        "available": True, "concordance": 0.61, "null_constant_signal_concordance": 0.5,
        "decisions_scored": 12,
        "null_spread": {"available": True, "null_95_interval": [0.28, 0.72],
                        "observed_inside_the_null_interval": True, "p_two_sided": 0.47}}})
    assert inside["clears_the_null"] is False
    assert inside["available"] is True


def test_a_run_carrying_a_concordance_but_NO_SPREAD_is_undecidable():
    """The specific historical shape: a point estimate against a point null of 0.5, with no
    interval. That is a number a reader cannot weigh, and it must not resolve to either answer."""
    reading = ic.skill_reading(payload={"method_skill": {
        "available": True, "concordance": 0.6136,
        "null_constant_signal_concordance": 0.5, "null_spread": {"available": False}}})

    assert reading["clears_the_null"] is None
    assert reading["concordance"] is None, (
        "an undecidable reading published its point estimate anyway; the number is exactly what "
        "this branch exists to withhold")


def test_an_UNREADABLE_artefact_refuses_rather_than_defaulting(tmp_path):
    """Fail-closed on the input, not only on the answer. A control that refuses on input it
    could not READ is the shape this repository has been caught by repeatedly."""
    reading = ic.skill_reading(artefact=tmp_path / "does-not-exist.json")

    assert reading["clears_the_null"] is None
    assert "could not be read" in reading["why"]


def test_the_page_says_WE_CANNOT_TELL_in_those_words():
    """Director: 'If the concordance sits inside its null, the page says we cannot tell, in those
    words.' A synonym is the defect: it moves the reader while the flag stays False."""
    claim = ic.inference_claim(_provenance(co_calibrated=False), _skill(clears=False))

    assert ic.CANNOT_TELL in claim["sentence"]
    assert "we cannot tell" in claim["sentence"]


def test_no_sentence_names_the_reading_without_its_interval():
    """Every branch that quotes the method's reading quotes the interval in the same breath.

    Driven across all four branches rather than the live one, because the defect is a branch
    nobody is in today printing a bare number when the tree moves into it.
    """
    for independent in (True, False, None):
        for clears in (True, False, None):
            claim = ic.inference_claim(
                _provenance(co_calibrated=None if independent is None else not independent),
                _skill(clears=clears, available=clears is not None))
            sentence = claim["sentence"]
            if "0.614" in sentence or "0.6136" in sentence:
                assert "0.283" in sentence and "0.717" in sentence, (
                    "the reading is quoted with no interval beside it in the "
                    f"independent={independent}, clears={clears} branch: {sentence}")


def test_independence_is_reported_WITH_the_inaccuracy_that_produced_it():
    """The company is outside the published band in 8 of 10 years, and that is WHY it is
    independent. A surface that reports the first without the second lets a reader take the size
    of the gap for the size of the insight."""
    claim = ic.inference_claim(_provenance(co_calibrated=False, years_outside=8),
                               _skill(clears=False))

    accuracy = claim["accuracy"]
    assert accuracy["applies"] is True
    assert accuracy["years_outside"] == 8
    assert accuracy["max_distance_pp"] == pytest.approx(17.34)
    assert "8 of 10" in claim["sentence"]
    assert "as likely to be the company being wrong" in claim["sentence"]


def test_a_company_ON_the_record_carries_no_inaccuracy_clause():
    """The other half: the clause is COMPUTED from the years, not asserted, so it disappears by
    itself if the company's estimator ever lands on the record."""
    claim = ic.inference_claim(_provenance(co_calibrated=False, years_outside=0),
                               _skill(clears=True))

    assert claim["accuracy"]["applies"] is False
    assert "inaccuracy" not in claim["sentence"]
