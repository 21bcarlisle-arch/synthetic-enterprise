"""D7 -- the reshaped AGEING dimension, and the mutations that prove it measures.

Atom: `D7_ageing_gap_metric_reshape`. Replaces the single prevalence-normalised
ageing scalar (refuted in docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md)
with three measures, each on the denominator it is about:

    understated_arrears_rate = misses        / n_truly_overdue
    overstated_arrears_rate  = false_ageings / n_truly_current
    mean_bucket_displacement = mean |rank(belief) - rank(truth)| over TRULY-OVERDUE
    mean_overstatement_displacement = the same, over TRULY-CURRENT
    balanced_bucket_displacement    = mean of the two          # THE HEADLINE

Atom `D22_ageing_ordinal_is_one_directional` (2026-08-10) added the last two and
moved the headline onto the balanced term. Before it, `gap` was the truly-overdue
displacement alone and an indiscriminate over-ager -- a company dating its whole
current book at `90+` -- scored 0.000000, bit-identical to a perfect dater. The
D22 section at the bottom of this file holds that measurement, and the mutants
that make both halves of the repair falsifiable.

R15 IS THE POINT OF THIS FILE, not a footnote. Every property below is asserted
against the real measures AND against a NAMED MUTANT that breaks exactly that
property -- and the assertion is required to FAIL on the mutant. A prevalence-
invariance test that passes on a prevalence-sensitive measure would be theatre,
which is the failure mode this whole atom exists to remove; three of the four
mutants here are shapes I would plausibly have written instead, including the
one the D6 DISCOVER caught itself drafting (`_MUTANT_ordinal_over_no_skill`).

The measures' expected values come from the population's CONSTRUCTION (a company
that misses 40% of real arrears and false-ages 15 settled invoices), never from
running the metric to see what it says. The metric is the thing on trial.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

import pytest

from background.gap_metric import (
    AGEING_BUCKET_ORDER,
    ageing_gap,
    format_ageing_summary,
)

_MEASURE_KEYS = (
    "understated_arrears_rate",
    "overstated_arrears_rate",
    "mean_bucket_displacement",
    # The two D22 measures are swept by the SAME properties as the three
    # originals, deliberately: a headline exempt from the prevalence check is
    # how the pooled-mean repair would have got in.
    "mean_overstatement_displacement",
    "balanced_bucket_displacement",
)

N_CURRENT = 1000
N_FALSE_AGEINGS = 15
MISS_FRACTION = 0.4
PREVALENCE_SWEEP = (5, 10, 20, 50, 100)


# ---------------------------------------------------------------------------
# The population: ONE fixed company behaviour, an adjustable world.
# ---------------------------------------------------------------------------

def population(n_overdue: int, n_current: int = N_CURRENT):
    """Truth + belief for a company whose behaviour is defined in per-class terms
    and therefore does NOT change as the world's arrears prevalence changes:

      * it MISSES 40% of genuinely-90+ invoices (believes them settled),
      * it dates the other 60% correctly,
      * it false-ages a FIXED 15 truly-settled invoices as 90+ (wrongful dunning).

    So by construction, independent of any metric: understated = 0.40,
    overstated = 15/n_current, displacement = 0.40 * 3 buckets = 1.20.
    """
    n_missed = round(MISS_FRACTION * n_overdue)
    truth = ["current"] * n_current + ["90+"] * n_overdue
    belief = (
        ["90+"] * N_FALSE_AGEINGS
        + ["current"] * (n_current - N_FALSE_AGEINGS)
        + ["current"] * n_missed
        + ["90+"] * (n_overdue - n_missed)
    )
    assert len(truth) == len(belief)
    return truth, belief


MeasuresFn = Callable[[List[str], List[str]], Dict[str, Optional[float]]]


def _real_measures(truth, belief) -> Dict[str, Optional[float]]:
    c = ageing_gap(truth, belief).components
    return {k: c[k] for k in _MEASURE_KEYS}


# ---------------------------------------------------------------------------
# THE MUTANTS -- each breaks exactly one named property.
# ---------------------------------------------------------------------------

_RANK = {b: i for i, b in enumerate(AGEING_BUCKET_ORDER)}
_CURRENT = AGEING_BUCKET_ORDER[0]


def _MUTANT_ordinal_over_no_skill(truth, belief) -> Dict[str, Optional[float]]:
    """THE TRAP the D6 DISCOVER caught in its own first draft: ordinal
    displacement divided by the NO-SKILL displacement. Looks prevalence-safe (the
    numerator is ordinal now!) and is not -- the divisor counts the truth's class
    balance, so it re-imports the defect whole."""
    m = _real_measures(truth, belief)
    disp_all = sum(abs(_RANK[b] - _RANK[t]) for t, b in zip(truth, belief)) / len(truth)
    no_skill = sum(_RANK[t] for t in truth) / len(truth)
    m["mean_bucket_displacement"] = (disp_all / no_skill) if no_skill else None
    return m


def _MUTANT_displacement_over_whole_population(truth, belief) -> Dict[str, Optional[float]]:
    """Absolute, no ratio -- but averaged over EVERY invoice instead of the
    truly-overdue ones. The denominator is now the population size, which the
    class balance moves. The milder shape of the same mistake."""
    m = _real_measures(truth, belief)
    m["mean_bucket_displacement"] = (
        sum(abs(_RANK[b] - _RANK[t]) for t, b in zip(truth, belief)) / len(truth)
    )
    return m


def _MUTANT_understated_over_population(truth, belief) -> Dict[str, Optional[float]]:
    """`misses / n` instead of `misses / n_truly_overdue` -- the wrong denominator
    on the measure most likely to be quoted."""
    m = _real_measures(truth, belief)
    misses = sum(1 for t, b in zip(truth, belief) if t != _CURRENT and b == _CURRENT)
    m["understated_arrears_rate"] = misses / len(truth)
    return m


def _MUTANT_hamming_not_ordinal(truth, belief) -> Dict[str, Optional[float]]:
    """Defect 3 restored: a right/wrong error rate over the truly-overdue instead
    of a bucket DISTANCE. Off-by-one and stone-blind become the same number."""
    m = _real_measures(truth, belief)
    over = [(t, b) for t, b in zip(truth, belief) if t != _CURRENT]
    m["mean_bucket_displacement"] = (
        sum(1 for t, b in over if t != b) / len(over) if over else None
    )
    return m


# ---------------------------------------------------------------------------
# The properties, each written once and run against real + mutant.
# ---------------------------------------------------------------------------

def _assert_prevalence_invariant(measures: MeasuresFn) -> None:
    """D6 Defect 2 must be gone: hold the company fixed, move the world's arrears
    prevalence over a twentyfold range, and every measure must be EXACTLY flat."""
    observed = {k: set() for k in _MEASURE_KEYS}
    for n_overdue in PREVALENCE_SWEEP:
        truth, belief = population(n_overdue)
        m = measures(truth, belief)
        for k in _MEASURE_KEYS:
            observed[k].add(round(m[k], 9))
    for k in _MEASURE_KEYS:
        assert len(observed[k]) == 1, (
            f"{k} moved with world prevalence while the company was held fixed: "
            f"{sorted(observed[k])}"
        )


def _assert_ordinal_severity_is_graded(measures: MeasuresFn) -> None:
    """D6 Defect 3 must be gone: on an ORDERED bucket space, one-bucket-out must
    score strictly better than stone-blind."""
    truth = ["current"] * N_CURRENT + ["90+"] * 10
    off_by_one = ["current"] * N_CURRENT + ["60-90"] * 10
    blind = ["current"] * (N_CURRENT + 10)

    d_off = measures(truth, off_by_one)["mean_bucket_displacement"]
    d_blind = measures(truth, blind)["mean_bucket_displacement"]
    assert d_off < d_blind, (
        f"one-bucket-out ({d_off}) must score better than stone-blind ({d_blind}) "
        "-- the buckets are ordered"
    )


def test_measures_are_what_the_population_was_built_to_contain():
    """Anchor. Without this the invariance tests below could pass vacuously on a
    measure that returned a constant for every input."""
    truth, belief = population(50)
    m = _real_measures(truth, belief)
    assert m["understated_arrears_rate"] == pytest.approx(MISS_FRACTION)
    assert m["overstated_arrears_rate"] == pytest.approx(N_FALSE_AGEINGS / N_CURRENT)
    assert m["mean_bucket_displacement"] == pytest.approx(MISS_FRACTION * 3)
    # The over-ageing half, from the same construction: 15 settled invoices
    # dated `90+` is 3 buckets each over the whole truly-current book.
    over = N_FALSE_AGEINGS * 3 / N_CURRENT
    assert m["mean_overstatement_displacement"] == pytest.approx(over)
    assert m["balanced_bucket_displacement"] == pytest.approx(
        (MISS_FRACTION * 3 + over) / 2)

    perfect = _real_measures(truth, truth)
    assert perfect == {
        "understated_arrears_rate": 0.0,
        "overstated_arrears_rate": 0.0,
        "mean_bucket_displacement": 0.0,
        "mean_overstatement_displacement": 0.0,
        "balanced_bucket_displacement": 0.0,
    }


def test_defect_2_is_gone_the_measures_are_prevalence_invariant():
    _assert_prevalence_invariant(_real_measures)


@pytest.mark.parametrize("mutant", [
    _MUTANT_ordinal_over_no_skill,
    _MUTANT_displacement_over_whole_population,
    _MUTANT_understated_over_population,
], ids=["ordinal_over_no_skill", "displacement_over_whole_population",
        "understated_over_population"])
def test_R15_the_prevalence_check_FIRES_on_a_prevalence_shaped_denominator(mutant):
    """R15: the invariance test must be able to FAIL. Each mutant re-introduces a
    denominator that counts the truth's class balance; the SAME assertion that
    passes above must reject it."""
    with pytest.raises(AssertionError, match="moved with world prevalence"):
        _assert_prevalence_invariant(mutant)


def test_defect_1_is_gone_finding_all_arrears_beats_finding_none():
    """The row that convicted the old metric: a company that finds EVERY real
    arrears case with a 1.5% false-positive rate scored 1.50 -- 'worse than
    reporting no arrears at all'. On the reshaped measures it must dominate the
    no-skill company on every axis it is actually better on, and pay for its
    false alarms only on the axis they belong to."""
    truth = ["current"] * N_CURRENT + ["90+"] * 10
    finds_all = (["90+"] * N_FALSE_AGEINGS + ["current"] * (N_CURRENT - N_FALSE_AGEINGS)
                 + ["90+"] * 10)
    no_skill = ["current"] * (N_CURRENT + 10)

    good = _real_measures(truth, finds_all)
    blind = _real_measures(truth, no_skill)

    assert good["understated_arrears_rate"] == 0.0
    assert blind["understated_arrears_rate"] == 1.0
    assert good["mean_bucket_displacement"] == 0.0
    assert blind["mean_bucket_displacement"] == 3.0
    # The false alarms are NOT hidden and NOT laundered through the other class's
    # denominator: they are the wrongful-dunning exposure, priced on their own.
    assert good["overstated_arrears_rate"] == pytest.approx(0.015)
    assert blind["overstated_arrears_rate"] == 0.0


def test_defect_3_is_gone_displacement_is_ordinal():
    _assert_ordinal_severity_is_graded(_real_measures)


def test_R15_the_ordinal_check_FIRES_on_a_hamming_error_rate():
    """R15: restore Defect 3 and the ordinal assertion must reject it."""
    with pytest.raises(AssertionError, match="must score better than stone-blind"):
        _assert_ordinal_severity_is_graded(_MUTANT_hamming_not_ordinal)


# ---------------------------------------------------------------------------
# Fail-loud / fail-open (R15 patterns 2 and 3)
# ---------------------------------------------------------------------------

def test_an_unknown_bucket_label_RAISES_rather_than_scoring_as_perfect():
    """FAIL-OPEN guard. If the bucket vocabulary drifts on either side, an
    unrankable label must stop the measurement. The fail-open alternative -- treat
    what you cannot rank as displacement 0 -- would report a vocabulary break as
    perfect dating, which is the R15 fail-open pattern exactly."""
    truth = ["current", "90+", "90+"]
    with pytest.raises(ValueError, match="outside the ordered bucket space"):
        ageing_gap(truth, ["current", "90+", "120+"])
    with pytest.raises(ValueError, match="outside the ordered bucket space"):
        ageing_gap(["current", "90+", "0-30"], ["current", "90+", "90+"])

    # And the fail-open shape it is guarding against really would score perfect:
    forgiving = {b: i for i, b in enumerate(AGEING_BUCKET_ORDER)}
    disp = sum(abs(forgiving.get(b, 0) - forgiving.get(t, 0))
               for t, b in zip(truth, ["current", "90+", "120+"]) if t != "current")
    assert disp == 3, (
        "a tolerant ranker scores the drifted label as a 3-bucket error here only "
        "because truth is 90+; with the drift on the TRUTH side it would read 0"
    )


def test_a_population_with_no_overdue_invoices_is_UNDEFINED_not_zero():
    """VACUITY guard. No truly-overdue invoices means the overdue-denominated
    measures have nothing to measure. `None`, never 0.0 -- a vacuous population is
    not a perfectly-dated one (the 1557/1557-passed-while-the-field-was-absent
    shape)."""
    result = ageing_gap(["current"] * 20, ["current"] * 18 + ["90+"] * 2)
    c = result.components

    assert c["n_truly_overdue"] == 0
    assert c["understated_arrears_rate"] is None
    assert c["mean_bucket_displacement"] is None
    assert result.gap is None
    assert "vacuity" in c
    # The measure that IS defined here still reports.
    assert c["overstated_arrears_rate"] == pytest.approx(0.1)
    assert "undefined" in format_ageing_summary(result)


def test_empty_or_mismatched_input_raises():
    with pytest.raises(ValueError, match="empty population"):
        ageing_gap([], [])
    with pytest.raises(ValueError, match="same length"):
        ageing_gap(["current"], ["current", "90+"])


# ---------------------------------------------------------------------------
# THE EXCLUSION BAND (atom D16_ageing_negative_population_is_unexcluded)
# ---------------------------------------------------------------------------
# The band exists because this dimension applied no rule at all while its
# sibling applied D11's, so the pair published one named quantity as two numbers
# 3.5x apart. At the METRIC level what has to hold is narrower and harder: the
# band must actually move the measures it is applied to, must leave nothing
# half-excluded, and must be impossible to apply silently.

def test_an_excluded_case_leaves_EVERY_population_not_just_the_current_one():
    """Half-excluding a case would leave the displacement mean measuring a
    population the two rates do not -- three measures over three different
    denominators, which is the shape D7 exists to have removed."""
    truth = ["current", "current", "30-60", "30-60"]
    belief = ["60-90", "current", "current", "30-60"]
    full = ageing_gap(truth, belief).components
    banded = ageing_gap(
        truth, belief,
        excluded=[False, True, False, True],
        exclusion_reason="test band",
    ).components

    assert full["n"] == 4 and banded["n"] == 2
    assert banded["n_excluded"] == 2
    assert banded["n_truly_current"] == 1 and banded["n_truly_overdue"] == 1
    # The excluded overdue case is out of the displacement population too.
    assert full["mean_bucket_displacement"] == pytest.approx(0.5)
    assert banded["mean_bucket_displacement"] == pytest.approx(1.0)
    assert banded["overstated_arrears_rate"] == pytest.approx(1.0)


def test_an_exclusion_without_a_reason_RAISES():
    """R15 / the D10 rule. An unexplained exclusion silently shrinks a
    denominator, which is the cheapest way to make a published rate look better
    than it is -- and this rate is one the company is scored on."""
    with pytest.raises(ValueError, match="no `exclusion_reason` was given"):
        ageing_gap(["current", "30-60"], ["30-60", "30-60"], excluded=[True, False])
    # A blank reason is not a reason.
    with pytest.raises(ValueError, match="no `exclusion_reason` was given"):
        ageing_gap(["current", "30-60"], ["30-60", "30-60"],
                   excluded=[True, False], exclusion_reason="   ")
    # No exclusion, no reason required -- the band is optional, not mandatory.
    assert ageing_gap(["current", "30-60"], ["30-60", "30-60"],
                      excluded=[False, False]).components["n_excluded"] == 0


def test_a_misaligned_or_total_exclusion_RAISES_rather_than_scoring_a_remnant():
    """FAIL-LOUD on the two ways a mask goes wrong. A short mask would zip
    silently and exclude arbitrary rows; a full mask would leave nothing to
    score, and measures over nothing are the fail-open shape the band exists to
    avoid."""
    with pytest.raises(ValueError, match="mis-aligned mask"):
        ageing_gap(["current", "30-60"], ["30-60", "30-60"],
                   excluded=[True], exclusion_reason="short")
    with pytest.raises(ValueError, match="no population left to score"):
        ageing_gap(["current", "30-60"], ["30-60", "30-60"],
                   excluded=[True, True], exclusion_reason="everything")


def test_the_exclusion_is_published_wherever_the_rate_is_printed():
    """D10's published-not-silent rule, at the render site. A denominator that
    has had a band removed must say so where a reader meets it -- otherwise the
    alignment that made two dimensions comparable is invisible at exactly the
    place someone compares them."""
    result = ageing_gap(
        ["current", "current", "30-60"], ["30-60", "current", "30-60"],
        excluded=[False, True, False],
        exclusion_reason="paid past grace -- the company was right to chase",
    )
    assert result.components["n_excluded"] == 1
    text = format_ageing_summary(result)
    assert "1 case(s) in neither population" in text
    assert "the company was right to chase" in text
    # And the rate must NOT be printed under the name that belongs to the
    # detection dimension (D16).
    assert "NOT the wrongful-dunning exposure" in text


# ---------------------------------------------------------------------------
# The headline must not be readable as a normalised score
# ---------------------------------------------------------------------------

def test_the_headline_is_displacement_and_says_it_has_no_baseline():
    """The old scalar did its damage by being quotable as 'ageing 1.1538'. The
    replacement's headline is in BUCKETS and carries, in the fields that travel
    into the gap ledger and on to site/data/proof.json, an explicit statement that
    there is no baseline -- so `gap == 1.0` here cannot be read as 'no better
    than blind'."""
    truth, belief = population(50)
    result = ageing_gap(truth, belief)

    assert result.metric == "ageing"
    assert result.gap == pytest.approx(
        result.components["balanced_bucket_displacement"])
    assert result.g0 == 0.0
    assert "NONE" in result.baseline
    entry = result.to_ledger_entry("D5_account_hierarchy_payments")
    assert "NO NORMALISER" in entry["components"]["normalisation"]
    assert "NOT a [0,1]" in entry["components"]["headline_units"]

    summary = format_ageing_summary(result)
    assert "buckets" in summary and "no baseline" in summary
    assert "understated_arrears_rate" in summary and "overstated_arrears_rate" in summary
    assert "wrongful-dunning" in summary


# ---------------------------------------------------------------------------
# ATOM D22 -- the headline must count BOTH error directions
# ---------------------------------------------------------------------------
# The defect this section closes was found by a register that scores every
# published dimension's own INDISCRIMINATE DEGENERATE through its own shipped
# scorer (`tools.couple_w2_11_d5.HEADLINE_DIRECTION_COVERAGE`). The ageing
# headline was a mean over the truly-overdue invoices alone, so the degenerate
# that is perfect in that direction and maximally wrong in the other scored
# EXACTLY what a perfect dater scores. Two mutants below hold the repair
# falsifiable in both of the ways it could have been done wrong: reverting to the
# one-directional headline, and taking the pooled mean that would have re-imported
# the D6 prevalence defect.

# The two degenerates, in the vocabulary of the population above: a company that
# dates every truly-overdue invoice perfectly and dumps its whole current book in
# `90+`, and its mirror.
def _over_ager(truth):
    return [t if t != _CURRENT else "90+" for t in truth]


def _under_dater(truth):
    return [_CURRENT] * len(truth)


def _assert_headline_counts_both_directions(measures: MeasuresFn) -> None:
    """The D22 property: an INDISCRIMINATE company must not score what a PERFECT
    one scores, in EITHER direction. Written as one property so the real measure
    and the mutants below are held to the same words."""
    truth, _ = population(100)
    perfect = measures(truth, list(truth))["balanced_bucket_displacement"]
    for name, degenerate in (("over-ageing", _over_ager(truth)),
                             ("under-dating", _under_dater(truth))):
        assert sum(1 for a, b in zip(truth, degenerate) if a != b) > 0, (
            f"the {name} degenerate changed nothing -- it proves nothing")
        got = measures(truth, degenerate)["balanced_bucket_displacement"]
        assert got != pytest.approx(perfect), (
            f"the headline cannot tell an indiscriminate {name} company "
            f"({got}) from a perfect dater ({perfect})"
        )


def _MUTANT_headline_is_the_overdue_term_only(truth, belief):
    """THE PRE-D22 HEADLINE, restored exactly: `gap` is the displacement over the
    truly-overdue population alone. This is not a hypothetical -- it is the shape
    this scorer shipped with until 2026-08-10, and it is what every ledger entry
    before that date carries."""
    m = _real_measures(truth, belief)
    m["balanced_bucket_displacement"] = m["mean_bucket_displacement"]
    return m


def _MUTANT_headline_is_the_pooled_mean(truth, belief):
    """THE OBVIOUS REPAIR, and the wrong one: average the displacement over every
    invoice. It counts both directions -- and its denominator counts the truth's
    class balance, so it re-imports D6 Defect 2 that the atom before this one
    removed."""
    m = _real_measures(truth, belief)
    m["balanced_bucket_displacement"] = (
        sum(abs(_RANK[b] - _RANK[t]) for t, b in zip(truth, belief)) / len(truth)
    )
    return m


def test_D22_the_headline_counts_both_error_directions():
    _assert_headline_counts_both_directions(_real_measures)


def test_R15_the_direction_check_FIRES_on_the_pre_D22_headline():
    """R15: the property above must be able to FAIL. Restore the one-directional
    headline and it must reject it -- naming the over-ageing direction, not the
    one the old measure could already see."""
    with pytest.raises(AssertionError,
                       match="indiscriminate over-ageing company"):
        _assert_headline_counts_both_directions(
            _MUTANT_headline_is_the_overdue_term_only)


def test_R15_the_prevalence_check_FIRES_on_a_pooled_mean_headline():
    """The second way the repair could have gone wrong. A pooled mean passes the
    direction check honestly, so only the prevalence check convicts it -- which
    is why the headline is swept by BOTH properties and not just the new one."""
    _assert_headline_counts_both_directions(_MUTANT_headline_is_the_pooled_mean)
    with pytest.raises(AssertionError, match="moved with world prevalence"):
        _assert_prevalence_invariant(_MUTANT_headline_is_the_pooled_mean)


def test_D22_the_measured_numbers_the_atom_was_opened_on():
    """The measurement itself, pinned: what the old headline scored on the two
    degenerates and what this one scores. The atom's whole claim is that these
    were EQUAL, so the equality has to be visible in the test that closed it."""
    truth = ["current"] * 900 + ["30-60"] * 40 + ["60-90"] * 30 + ["90+"] * 30
    perfect = ageing_gap(truth, list(truth)).components
    over = ageing_gap(truth, _over_ager(truth)).components
    over_by_one = ageing_gap(
        truth, ["30-60" if t == "current" else t for t in truth]).components

    # The old headline: all three identical, which is the defect.
    assert (perfect["mean_bucket_displacement"]
            == over["mean_bucket_displacement"]
            == over_by_one["mean_bucket_displacement"] == 0.0)
    # The headline that replaced it: graded, ordinal, and non-zero in exactly
    # the direction the old one could not see. Stone-blind over-ageing (3
    # buckets on every current invoice, halved) scores 1.5; off-by-one scores
    # 0.5 -- the off-by-one/stone-blind distinction this dimension exists to
    # make, now available in BOTH directions.
    assert perfect["balanced_bucket_displacement"] == 0.0
    assert over["balanced_bucket_displacement"] == pytest.approx(1.5)
    assert over_by_one["balanced_bucket_displacement"] == pytest.approx(0.5)
    # ...and the rate cannot separate those last two, which is why the ordinal
    # term has to.
    assert over["overstated_arrears_rate"] == over_by_one["overstated_arrears_rate"]


def test_D22_a_missing_truth_class_leaves_the_headline_UNDEFINED_not_halved():
    """VACUITY, the D22 half. With one truth class empty the headline must be
    `None` -- NOT the surviving term, which would silently restore the
    one-directional headline on exactly the populations where it cannot be
    checked. Both directions, because the fail-open is symmetric."""
    no_current = ageing_gap(["30-60", "90+"], ["30-60", "60-90"])
    assert no_current.components["n_truly_current"] == 0
    assert no_current.components["mean_overstatement_displacement"] is None
    assert no_current.components["mean_bucket_displacement"] == pytest.approx(0.5)
    assert no_current.gap is None, (
        "the headline fell back to the term that IS defined -- the "
        "one-directional shape D22 removed, on the population where nobody "
        "would notice")
    assert "truly-current" in no_current.components["vacuity"]

    no_overdue = ageing_gap(["current"] * 4, ["current", "current", "30-60", "90+"])
    assert no_overdue.gap is None
    assert no_overdue.components["mean_overstatement_displacement"] == pytest.approx(1.0)
    assert "truly-overdue" in no_overdue.components["vacuity"]

    # And the caveat says UNKNOWN rather than letting a reader infer zero.
    for r in (no_current, no_overdue):
        assert "UNKNOWN" in r.components["ordinal_direction_caveat"]


def test_D22_the_headline_says_it_is_balanced_wherever_it_is_printed():
    """The D7 anti-decay mechanism applied to the new headline: this dimension
    went wrong twice by being quotable as a bare scalar. The rendered line must
    carry the headline's TWO halves, and the components that travel into the gap
    ledger must say which measurement this is -- a reader diffing a pre-2026-08-10
    entry against a later one is comparing two different quantities."""
    truth, belief = population(50)
    result = ageing_gap(truth, belief)
    summary = format_ageing_summary(result)

    assert "BALANCED over both directions" in summary
    assert "mean_bucket_displacement" in summary
    assert "mean_overstatement_displacement" in summary
    assert "cannot say which direction it came from" in summary

    entry = result.to_ledger_entry("D5_account_hierarchy_payments")
    caveat = entry["components"]["ordinal_direction_caveat"]
    assert "atom D22" in caveat
    assert "TRULY-OVERDUE" in caveat
    assert "not comparable with this headline" in caveat, (
        "a ledger reader can compare the pre-D22 figure with this one and be "
        "told nothing")
    assert "BALANCED" in entry["components"]["headline_units"]


def test_bucket_order_matches_the_companys_own_ageing_vocabulary():
    """The harness redeclares the bucket order rather than importing it from
    `company/` (harness code, no company import for a constant) -- so pin the two
    together, or a drift on either side silently changes what displacement means.
    R15 independence: the expected order is derived by EXERCISING the company's
    own function over days-overdue, not by reading its source constant."""
    from company.billing.arrears_engine import age_bucket

    seen: List[str] = []
    for days in range(0, 200):
        b = age_bucket(days)
        if b not in seen:
            seen.append(b)          # first-appearance order == ascending severity
    assert tuple(seen) == AGEING_BUCKET_ORDER


def test_the_ageing_dimension_routes_through_the_reshaped_measure():
    """The finding must stay attached to the code it is about (the mirror of the
    D6 test this replaces): if `score_triad` stops using `ageing_gap`, everything
    above is characterizing something the live triad no longer runs."""
    import inspect

    from tools import couple_w2_11_d5

    # WHITESPACE-INSENSITIVE deliberately (D16, which made this call
    # multi-line when it grew the exclusion band): a control keyed to ONE
    # syntactic form of the thing it checks goes green-then-blind the first
    # time someone reformats the line -- a shape this repo has already been
    # caught by (an AST guard silently disabled by a type hint).
    src = inspect.getsource(couple_w2_11_d5.score_triad)
    compact = "".join(src.split())
    assert "ageing_gap(true_ageing_labels,belief_ageing_labels," in compact
    assert "misapplication_gap(true_ageing_labels" not in src, (
        "the retired prevalence-normalised scalar is back on the ageing dimension "
        "-- re-read docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md"
    )
