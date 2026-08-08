"""D7 -- the reshaped AGEING dimension, and the mutations that prove it measures.

Atom: `D7_ageing_gap_metric_reshape`. Replaces the single prevalence-normalised
ageing scalar (refuted in docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md)
with three measures, each on the denominator it is about:

    understated_arrears_rate = misses        / n_truly_overdue
    overstated_arrears_rate  = false_ageings / n_truly_current
    mean_bucket_displacement = mean |rank(belief) - rank(truth)| over TRULY-OVERDUE

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

    perfect = _real_measures(truth, truth)
    assert perfect == {
        "understated_arrears_rate": 0.0,
        "overstated_arrears_rate": 0.0,
        "mean_bucket_displacement": 0.0,
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
    assert result.gap == pytest.approx(result.components["mean_bucket_displacement"])
    assert result.g0 == 0.0
    assert "NONE" in result.baseline
    entry = result.to_ledger_entry("D5_account_hierarchy_payments")
    assert "NO NORMALISER" in entry["components"]["normalisation"]
    assert "NOT a [0,1]" in entry["components"]["headline_units"]

    summary = format_ageing_summary(result)
    assert "buckets" in summary and "no baseline" in summary
    assert "understated_arrears_rate" in summary and "overstated_arrears_rate" in summary
    assert "wrongful-dunning" in summary


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

    src = inspect.getsource(couple_w2_11_d5.score_triad)
    assert "ageing_gap(true_ageing_labels, belief_ageing_labels)" in src
    assert "misapplication_gap(true_ageing_labels" not in src, (
        "the retired prevalence-normalised scalar is back on the ageing dimension "
        "-- re-read docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md"
    )
