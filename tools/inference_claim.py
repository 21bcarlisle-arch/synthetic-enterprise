"""INDEPENDENCE IS NOT INFERENCE — the standing rule, in one place, applied from numbers.

Director, 2026-08-30, on what the rebuilt co-calibration guard unlocks:

    "Independence is not inference. The verdict removes the objection that we were measuring our
    own reflection; it does not establish the company knows anything. The method scores 0.614
    against a null of 0.283-0.717 and cannot be told from chance. So the belief-versus-truth gap
    may be published as a measurement, never as evidence of skill, and the two must not appear in
    one sentence without the null interval beside them. If the concordance sits inside its null,
    the page says we cannot tell, in those words. And the company being outside the band 8 of 10
    years is independence and inaccuracy at once -- a large gap is as likely to be error as
    insight, and nothing we publish should let that be misread."

WHY THIS IS A MODULE AND NOT A CORRECTED SENTENCE. The instance that prompted it was one clause
in `tools/couple_value_based_pricing._co_calibration_clause`, which read:

    "The two sides no longer share a calibration source, so that gap now speaks to the company's
     own inference."

Correcting that string would leave the RULE nowhere, and the next surface that quotes the gap
would have to rediscover it. Worse, the flag behind that clause --
`publishable_as_evidence_of_inference` -- was literally `not provenance["co_calibrated"]`, i.e.
the codebase encoded "independent therefore inferring" as an identity. That is the thing being
corrected, so it is corrected once, here, and both the summary and the ledger row read it.

THE RULE, AS THREE CLAIMS THAT ARE NOT THE SAME CLAIM:

  1. THE GAP IS A MEASUREMENT. It is always publishable as one. A real disagreement between what
     the company believed and what the world delivered is a fact about this run, and nothing in
     here withholds it.
  2. THE GAP IS EVIDENCE OF SKILL only if BOTH: the two sides were arrived at independently
     (necessary -- otherwise we are measuring our own reflection), AND the method's own ranking
     clears the interval a random signal produces on this many decisions (also necessary --
     otherwise the measurement cannot be told from chance). Independence is the first leg alone
     and was being read as the whole thing.
  3. A LARGE GAP IS NOT A LARGE RESULT. The company sits outside the published band in 8 of 10
     years, by up to 17.3pp. That is independence and inaccuracy at once: the gap it produces is
     as likely to be the company being wrong as the company knowing something. Any surface that
     quotes the gap carries that clause, because "the company's estimator differs from the world"
     and "the company's estimator is bad" produce the same number.

FAIL-CLOSED, ON BOTH LEGS. A missing skill reading, an absent null spread, an unreadable
artefact and an undecidable side all resolve to `None`, and `None` never satisfies leg 2 --
`is True` is the test, not truthiness. "We could not check" is not "it cleared".

WHAT NO EDIT TO THIS FILE CAN DO. `publishable_as_evidence_of_skill` is composed only from the
two `is True` tests; there is no string, docstring or witness anywhere in the composition, for
the same reason `shared_calibration_holds` no longer has one. The prose is DERIVED from the
verdict rather than sitting beside it, so a sentence cannot disagree with the flag it decorates.
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: The run artefact that carries the method's own ranking against the interval a random signal
#: produces. Read rather than recomputed: `tools/generate_value_arms_data._method_skill` rejected
#: recomputing the spread from the artefact's own n for exactly this reason -- it is
#: arithmetically identical and creates a SECOND source for one figure.
SKILL_ARTEFACT = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json"

#: The words the director specified, verbatim, for the case where the reading sits inside its
#: own null. Held as a constant so the phrase cannot drift into a softer one ("suggestive",
#: "early evidence") while the flag beside it stays False.
CANNOT_TELL = "we cannot tell"

THE_RULE = (
    "The belief-versus-truth gap is publishable as a MEASUREMENT and never as evidence of skill "
    "unless the two sides are independent AND the method's own ranking clears the interval a "
    "random signal produces on this many decisions. Independence alone removes the objection "
    "that we were measuring our own reflection; it does not establish that the company knows "
    "anything."
)


def skill_reading(payload: dict | None = None, artefact: Path | None = None) -> dict:
    """The method's ranking and the interval a random signal reaches, or a refusal.

    `clears_the_null` is TRUE only when the run says the observed value fell OUTSIDE the
    interval. It is FALSE when the run says it fell inside, and NONE whenever the question could
    not be put -- artefact missing, unreadable, no `method_skill`, no `null_spread`, or a spread
    that does not carry `observed_inside_the_null_interval`. None is not False: one means the
    method did not clear its null and the other means we do not know, and they are reported
    apart because only the second is fixable by running something.
    """
    src = SKILL_ARTEFACT if artefact is None else artefact
    if payload is None:
        try:
            payload = json.loads(src.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return _no_reading(f"the run artefact could not be read ({type(exc).__name__})")
    ms = (payload or {}).get("method_skill") or {}
    if not ms.get("available"):
        return _no_reading(str(ms.get("reason") or "this run carried no method-skill reading"))
    spread = ms.get("null_spread") or {}
    if not spread.get("available"):
        return _no_reading(
            "this run carries a concordance but no null spread, so there is no interval to "
            "clear: " + str(spread.get("reason") or "the spread is absent"))
    inside = spread.get("observed_inside_the_null_interval")
    interval = spread.get("null_95_interval") or [None, None]
    if not isinstance(inside, bool) or interval[0] is None or interval[1] is None:
        return _no_reading("the null spread carries no decidable interval for this run")
    return {
        "available": True,
        "concordance": ms.get("concordance"),
        "null_95_low": interval[0],
        "null_95_high": interval[1],
        "null_point": ms.get("null_constant_signal_concordance"),
        "p_two_sided": spread.get("p_two_sided"),
        "decisions_scored": ms.get("decisions_scored"),
        "clears_the_null": not inside,
        "why": None,
    }


def _no_reading(why: str) -> dict:
    return {"available": False, "concordance": None, "null_95_low": None, "null_95_high": None,
            "null_point": None, "p_two_sided": None, "decisions_scored": None,
            "clears_the_null": None, "why": why}


def _independence(provenance: dict | None) -> bool | None:
    """TRUE only on a verdict that positively says the sides do not share a source.

    A provenance dict that is missing, or that carries no `co_calibrated` boolean, is None --
    the same fail-closed shape as the skill leg, and for the same reason.
    """
    if not isinstance(provenance, dict):
        return None
    co = provenance.get("co_calibrated")
    if not isinstance(co, bool):
        return None
    return not co


def accuracy_clause(provenance: dict | None) -> dict:
    """WHAT INDEPENDENCE COSTS, computed from the same record independence was computed from.

    Independence and accuracy are opposite readings of one measurement here: the company's table
    is independent BECAUSE it is nowhere near the published record. A surface that reports the
    first without the second lets a reader take the size of the gap as the size of the insight,
    when a company that is simply wrong produces exactly the same number.
    """
    sides = ((provenance or {}).get("sides") or {})
    company = sides.get("company") or {}
    outside = company.get("years_outside_the_band") or []
    checked = company.get("years_checked")
    if not outside:
        return {"applies": False, "years_outside": 0, "years_checked": checked,
                "max_distance_pp": None, "clause": ""}
    distances = []
    for row in outside:
        band = row.get("band_pct") or [None, None]
        reads = row.get("reads_pct")
        if reads is None or band[0] is None or band[1] is None:
            continue
        distances.append(round(max(band[0] - reads, reads - band[1]), 2))
    worst = max(distances) if distances else None
    return {
        "applies": True,
        "years_outside": len(outside),
        "years_checked": checked,
        "max_distance_pp": worst,
        "clause": (
            "The company's estimator is outside the published band in {} of {} years{} -- so "
            "this is independence and inaccuracy at once. A gap that size is as likely to be "
            "the company being wrong as the company knowing something, and the two produce the "
            "same number."
        ).format(len(outside), checked if checked is not None else len(outside),
                 "" if worst is None else ", by up to {:.1f}pp".format(worst)),
    }


def cannot_tell_sentence(*, subject: str, observed, null_low, null_high,
                         n=None, unit: str = "decisions") -> str | None:
    """THE WORDS, for any figure on any surface that sits inside its own null.

    Returns the sentence when the reading cannot be told from chance, and `None` when it can --
    so a caller renders it or does not, and never has to decide which case it is in. Whether the
    reading clears its null is COMPUTED here from the three numbers rather than read off an
    `inside_the_null` flag the artefact happens to carry: a flag is one more thing that can be
    stale, and the comparison is two `<=`.

    UNDECIDABLE COUNTS AS CANNOT TELL. A missing observed value or a missing bound returns the
    sentence, not None. "We have no interval" and "the interval swallows the reading" are
    different reasons and the same answer to a reader.

    Written for the concordance the director named, and applied to the AUC beside it because that
    figure is the same class -- a rank statistic on a small sample, published next to a claim
    about what the company knows.
    """
    if observed is None or null_low is None or null_high is None:
        return "On {}, {}: this run carries no interval to weigh the reading against.".format(
            subject, CANNOT_TELL)
    if null_low <= observed <= null_high:
        span = "" if n is None else " on {} {}".format(n, unit)
        return ("On {}, {}: {:.3f} sits inside the {:.3f}–{:.3f} a signal carrying no "
                "information reaches{}.").format(subject, CANNOT_TELL, observed,
                                                 null_low, null_high, span)
    return None


def inference_claim(provenance: dict | None, skill: dict | None = None) -> dict:
    """THE ONE PLACE THE RULE IS APPLIED. Composed from two `is True` tests and nothing else.

    Returns the flags a machine reader consults AND the sentence a human reader gets, derived
    from the same verdict so they cannot disagree. The sentence always carries the interval
    whenever it names the reading, which is the director's second condition: the gap and the
    skill claim "must not appear in one sentence without the null interval beside them".
    """
    skill = skill_reading() if skill is None else skill
    independent = _independence(provenance)
    clears = skill.get("clears_the_null")
    # THE COMPOSITION. `is True` on both legs, so None -- the fail-closed value on either side --
    # can never satisfy it. `and` not `or`: independence is necessary and not sufficient, which
    # is the entire correction.
    supported = (independent is True) and (clears is True)
    accuracy = accuracy_clause(provenance)
    return {
        "rule": THE_RULE,
        "the_gap_is_a_measurement": True,
        "sides_are_independent": independent,
        "the_method_clears_its_null": clears,
        "publishable_as_evidence_of_skill": supported,
        "skill_reading": skill,
        "accuracy": accuracy,
        "sentence": _sentence(independent, clears, skill, accuracy, supported),
    }


def _interval_phrase(skill: dict) -> str:
    """The interval, in the same clause as the reading it bounds, or an explicit absence."""
    if not skill.get("available"):
        return "with no interval available to weigh it against"
    return ("{:.3f} against {:.3f}–{:.3f} for a signal carrying no information, on {} "
            "decisions").format(skill["concordance"], skill["null_95_low"], skill["null_95_high"],
                                skill.get("decisions_scored"))


def _sentence(independent, clears, skill, accuracy, supported) -> str:
    """The prose, DERIVED from the flags above rather than written beside them.

    Every branch that mentions the method's reading mentions its interval in the same breath,
    and every branch that is not `supported` contains the words the director specified.
    """
    tail = (" " + accuracy["clause"]) if accuracy.get("applies") else ""
    if independent is not True:
        why = ("the two sides descend from one source, so the gap is two fits of one series"
               if independent is False else
               "whether the two sides are independent could not be established, and an "
               "unavailable check is a failed check")
        return ("The belief-versus-truth gap is a measurement and not evidence of skill: {}. On "
                "whether the method carries information at all, {} ({}).{}").format(
            why, CANNOT_TELL, _interval_phrase(skill), tail)
    if clears is not True:
        why = ("the method's ranking sits INSIDE the interval a random signal produces"
               if clears is False else
               "this run carries no decidable reading of the method: " + str(skill.get("why")))
        return ("The two sides are independent, which removes the objection that we were "
                "measuring our own reflection -- it does not establish that the company knows "
                "anything. The gap is published as a measurement only: {}, so on whether the "
                "method works {} ({}).{}").format(why, CANNOT_TELL, _interval_phrase(skill), tail)
    return ("The two sides are independent and the method's own ranking clears the interval a "
            "random signal produces ({}), so the gap is quotable as evidence that the company "
            "inferred something.{}").format(_interval_phrase(skill), tail)


if __name__ == "__main__":  # pragma: no cover - operator surface
    from tools.couple_value_based_pricing import shared_calibration_holds
    claim = inference_claim(shared_calibration_holds())
    print(json.dumps({k: v for k, v in claim.items() if k != "rule"}, indent=1))
