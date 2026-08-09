"""R15 controls for the W2_5 <-> C7 false-flag direction (atom D15).

WHAT THIS FILE IS DEFENDING. Until 2026-08-09 this pair published a RECALL-ONLY
number: the gap ledger read 0.0081 -- "nearly perfect" -- and a company that
flagged EVERY customer-year would have scored the same perfect 0.0. The D13
DISCOVER established that the settled negative exists (`income_stress` is a
discrete LOW/MODERATE/HIGH state machine, so "LOW at both year ends" is a state
and not a threshold) and that the choice of negative population swings the
measured false-flag rate x2.88 with company behaviour held literally fixed.

So the defect these tests exist to catch is NOT "the rate is wrong". It is:

  * a negative population derived as the LEFTOVER of another one (the naive
    `universe - truth`, which scores 2772 customer-years of real, carried-in
    distress as the company's false flags), and
  * a denominator choice that stops being VISIBLE -- one published rate with the
    two alternatives unmeasured, so a reader cannot tell which company the
    number is holding to account.

Every test below is a differential: it fails on the mutated code, not merely on
a broken one. Nothing here re-implements the scorer -- the measurements come
from `tools.couple_w2_5_c7` and `background.gap_metric` -- and the population
membership is re-derived from the SIM rather than from the sets under test.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from background.gap_metric import GapResult, detection_measures, format_detection_summary
from simulation.household import IncomeStress
from simulation.life_events import generate_life_events, household_at_date
from tools import couple_w2_5_c7 as pair

R13_DOC = Path(__file__).resolve().parents[2] / "docs" / "design" / \
    "D15_FALSE_FLAG_EXCLUSION_R13_CHOICE.md"

# Small enough to run in ~1s, large enough that all three populations and both
# error directions are non-empty (each test asserts its own non-vacuity).
_N, _START, _END = 300, 2016, 2021


@pytest.fixture(scope="module")
def pops():
    return pair.partition_populations(_N, _START, _END)


@pytest.fixture(scope="module")
def measures(pops):
    return pair.false_flag_measures(pops)


# ---------------------------------------------------------------------------
# The three populations
# ---------------------------------------------------------------------------

def test_the_three_populations_partition_the_universe_exactly(pops):
    """Disjoint AND exhaustive. A case in two populations is counted in two
    denominators; a case in none silently leaves the scored universe, which is
    the cheapest way to move either rate without anyone seeing it."""
    a, b, c = pops.must_flag, pops.neither, pops.must_not_flag
    # VACUITY GUARD: a partition of an empty set satisfies everything below.
    assert a and b and c, "a population is empty -- this control proves nothing"
    assert not (a & b) and not (a & c) and not (b & c)
    assert a | b | c == pops.universe
    assert pops.flagged <= pops.universe
    assert pops.carried_high <= pops.neither, (
        "the carried-HIGH band is basis B's exclusion and must be a subset of "
        "NEITHER -- a HIGH year with a distress event dated in it is truth"
    )


def test_each_population_is_re_derived_from_the_sim_not_from_the_others(pops):
    """R15 INDEPENDENCE. The membership check below is recomputed from
    `simulation.life_events` -- the source the partition is ABOUT -- not from
    the returned sets. A test that partitioned the sets against each other
    would pass on any self-consistent lie, including the complement derivation
    this atom exists to forbid."""
    checked = 0
    for hh in pair._make_population(_N):
        events = generate_life_events(hh, _START, _END)
        distress_years = {int(e.event_date[:4]) for e in events
                          if e.event_type in pair._DISTRESS_HARM}
        for year in range(_START, _END + 1):
            instance = f"{hh.customer_id}:{year}"
            before = household_at_date(hh, events, f"{year - 1}-12-31").income_stress
            after = household_at_date(hh, events, f"{year}-12-31").income_stress
            if year in distress_years:
                assert instance in pops.must_flag
            elif before is IncomeStress.LOW and after is IncomeStress.LOW:
                assert instance in pops.must_not_flag
            else:
                assert instance in pops.neither, (
                    f"{instance} carries income stress ({before} -> {after}) "
                    "with no distress event dated in the year -- a flag on it is "
                    "CORRECT and it belongs in neither direction's denominator"
                )
            checked += 1
    assert checked == len(pops.universe)


def test_the_neither_set_is_really_carried_distress(pops):
    """The NEITHER population's whole justification is that the household is in
    real distress. If it were merely "the rest", this assertion would fail."""
    assert len(pops.neither) > 0.02 * len(pops.universe), (
        "the carried-distress band is negligible here -- the x2.88 swing this "
        "atom is about would not reproduce and the fixture is unrepresentative"
    )


def test_classify_fires_on_the_complement_derivation(monkeypatch):
    """R15 MUST-FIRE, on precisely the defect the atom names. Redefine NEITHER
    as the complement of the truth predicate -- the shape that scored 2772 real
    distress years as false flags -- and a settled LOW/LOW case now matches TWO
    populations, so `_classify` raises instead of quietly double-counting it."""
    mutated = dict(pair._POPULATION_PREDICATES)
    mutated[pair.NEITHER] = lambda ev, sb, sa: not ev          # the complement
    monkeypatch.setattr(pair, "_POPULATION_PREDICATES", mutated)

    with pytest.raises(ValueError, match="partition broken"):
        pair._classify(False, IncomeStress.LOW, IncomeStress.LOW)


def test_classify_fires_when_a_case_matches_nothing(monkeypatch):
    """The other half of the must-fire: a case falling out of every population
    (a fourth income_stress state, say) leaves the scored universe silently."""
    mutated = dict(pair._POPULATION_PREDICATES)
    mutated[pair.NEITHER] = lambda ev, sb, sa: False
    monkeypatch.setattr(pair, "_POPULATION_PREDICATES", mutated)

    with pytest.raises(ValueError, match="partition broken"):
        pair._classify(False, IncomeStress.HIGH, IncomeStress.HIGH)


# ---------------------------------------------------------------------------
# The R13 choice: all three candidates, measured, every run
# ---------------------------------------------------------------------------

def test_every_candidate_basis_is_scored_on_every_run(measures):
    """An unmeasured alternative is how a denominator choice stops being
    visible. All three are scored, and each result carries the basis it was
    scored on -- no false-flag rate on this pair is readable without it."""
    assert set(measures) == set(pair.EXCLUSION_BASES)
    for key, result in measures.items():
        assert result.components["exclusion_basis"] == key
        assert key in result.note
        assert result.components["false_flag_rate"] is not None
        assert result.components["n_negatives"] > 0


def test_the_exclusion_boundary_swings_the_rate_severalfold(measures):
    """The finding, reproduced as a control: the same company scores several-fold
    differently depending only on which cases a flag is counted wrong on."""
    rate = {k: r.components["false_flag_rate"] for k, r in measures.items()}
    naive = rate["A_naive_universe_minus_truth"]
    mid = rate["B_exclude_carried_high"]
    settled = rate["C_settled_low_at_both_ends"]
    assert naive > mid > settled > 0.0
    assert naive / settled > 2.0, (
        f"the exclusion boundary no longer moves the rate ({naive} -> "
        f"{settled}); either the world stopped carrying distress forward or the "
        "bases collapsed into each other, and the R13 choice this atom put to "
        "the director would be moot"
    )


def test_the_company_is_literally_fixed_across_the_three_bases(measures):
    """R12 discipline made mechanical: the swing is a property of the MEASURE,
    not of company behaviour. Every basis scores the same flags and the same
    miss direction -- only the denominator moves."""
    results = list(measures.values())
    assert len({r.components["flagged_size"] for r in results}) == 1
    assert len({r.components["missed_failure_rate"] for r in results}) == 1
    assert len({r.components["truth_size"] for r in results}) == 1


def test_folding_the_carried_distress_band_back_in_moves_the_rate(pops, measures):
    """R15: the published band is not a no-op. Fold NEITHER back into the
    negative population -- exactly the naive derivation -- and the rate MUST
    move. A band that changed nothing would be decoration."""
    published = measures[pair.PUBLISHED_EXCLUSION_BASIS]
    folded = detection_measures(
        pops.must_flag, pops.flagged, universe=pops.universe,
        negative_set=pops.must_not_flag | pops.neither,
        exclusion_reason="", harm=pops.harm)
    assert folded.components["n_excluded"] == 0
    assert folded.components["false_flag_rate"] > \
        published.components["false_flag_rate"] * 1.5


def test_a_carried_distress_flag_is_not_a_false_flag_but_a_settled_one_is(pops):
    """THE DISCRIMINATION THE ATOM DEMANDS, proven both ways on one world.

    Two companies differing by ONE flag each: one flags a household carrying
    distress from a prior year (correct -- it must not score against the
    company), one flags a household demonstrably LOW at both year ends (wrong --
    it must). Under the published basis the first counts 0 false flags and the
    second counts 1. Under the naive basis BOTH count 1, which is the defect."""
    carried = sorted(pops.neither)[0]
    settled = sorted(pops.must_not_flag)[0]

    def n_false_flags(flagged, basis):
        return pair.false_flag_measures(
            pops.with_flagged(flagged))[basis].components["n_false_flags"]

    published, naive = pair.PUBLISHED_EXCLUSION_BASIS, "A_naive_universe_minus_truth"
    assert n_false_flags({carried}, published) == 0
    assert n_false_flags({settled}, published) == 1
    # ... and the mutation: the naive denominator cannot tell them apart.
    assert n_false_flags({carried}, naive) == 1
    assert n_false_flags({settled}, naive) == 1


def test_neither_degenerate_company_can_buy_a_good_score(pops):
    """The debt this atom closes, measured directly: the retired recall-only
    metric handed a company that flagged EVERYTHING a perfect 0.0."""
    for basis in pair.EXCLUSION_BASES:
        everything = pair.false_flag_measures(pops.with_flagged(pops.universe))[basis]
        nobody = pair.false_flag_measures(pops.with_flagged(set()))[basis]
        assert everything.gap == pytest.approx(0.5), basis
        assert nobody.gap == pytest.approx(0.5), basis
    real = pair.false_flag_measures(pops)[pair.PUBLISHED_EXCLUSION_BASIS]
    assert 0.0 < real.gap < 0.5, "the real company scores no better than a degenerate"


# ---------------------------------------------------------------------------
# The exclusion is PUBLISHED, not silent (D10's rule)
# ---------------------------------------------------------------------------

def test_every_excluded_case_travels_with_its_reason(measures):
    """The reason lives in the components, which reach the gap ledger -- not in
    prose a ledger reader never sees."""
    excluding = {k: r for k, r in measures.items() if r.components["n_excluded"]}
    assert excluding, "no basis excludes anything -- this control is vacuous"
    for key, result in excluding.items():
        assert str(result.components["exclusion_reason"]).strip(), key
        assert "income_stress" in result.components["exclusion_reason"] or \
            "carr" in result.components["exclusion_reason"], key


def test_an_unexplained_exclusion_raises(pops):
    """R15 MUST-FIRE on the publication rule itself: shrinking the denominator
    without saying why is refused at the scorer, not caught in review."""
    with pytest.raises(ValueError, match="exclusion_reason"):
        detection_measures(
            pops.must_flag, pops.flagged, universe=pops.universe,
            negative_set=pops.must_not_flag, exclusion_reason="  ",
            harm=pops.harm)


# ---------------------------------------------------------------------------
# The choice is a NAMED, REVERSIBLE constant with a record
# ---------------------------------------------------------------------------

def test_the_published_basis_is_one_constant_the_director_can_move(pops):
    """The R13 call is a one-line edit with a measurable consequence, not a
    rewrite: point the constant at another basis and the published rate moves to
    that basis's rate."""
    assert pair.PUBLISHED_EXCLUSION_BASIS in pair.EXCLUSION_BASES
    measures = pair.false_flag_measures(pops)
    for key in pair.EXCLUSION_BASES:
        assert measures[key].components["exclusion_basis"] == key
    assert measures[pair.PUBLISHED_EXCLUSION_BASIS].components["false_flag_rate"] != \
        measures["A_naive_universe_minus_truth"].components["false_flag_rate"]


def test_the_r13_record_exists_and_names_every_candidate():
    """The record cannot outrun the code: the doc the director reads must name
    the constant's CURRENT value and every candidate it was chosen against."""
    assert R13_DOC.is_file(), f"{R13_DOC} is missing -- the choice has no record"
    text = R13_DOC.read_text(encoding="utf-8")
    for key in pair.EXCLUSION_BASES:
        assert key in text, f"{key} is scored but absent from the R13 record"
    assert pair.PUBLISHED_EXCLUSION_BASIS in text
    assert "R12" in text, "the hazard (the recommendation is the LOWEST rate) is unstated"


def test_the_measure_call_carries_every_candidate_rate():
    """A downstream reader of the headline gets the alternatives with it."""
    result, stats = pair.measure(120, 2016, 2019)
    assert set(stats["by_exclusion_basis"]) == set(pair.EXCLUSION_BASES)
    assert result.components["candidate_false_flag_rates"] == stats["by_exclusion_basis"]
    assert stats["exclusion_basis"] == pair.PUBLISHED_EXCLUSION_BASIS
    assert "PROVISIONAL" in result.components["exclusion_basis_provenance"]


# ---------------------------------------------------------------------------
# One name, one quantity (the D16 class, applied at birth)
# ---------------------------------------------------------------------------

def test_this_pair_does_not_publish_another_dimensions_name(measures):
    """The shared renderer's default nouns are the payment triad's. This pair's
    truth is a distress year and its false flags are not dunning, so it names
    what IT measured -- and the triad's default is left byte-identical."""
    rendered = pair.format_pair_summary(measures[pair.PUBLISHED_EXCLUSION_BASIS])
    assert "wrongful-dunning" not in rendered
    assert pair.FALSE_FLAG_NAME in rendered and pair.TRUTH_NOUN in rendered
    payment_shaped = format_detection_summary(GapResult(
        metric="detection", gap=0.1, raw_gap=0.1, g0=0.5, baseline="b",
        components={"missed_failure_rate": 0.1, "false_flag_rate": 0.1,
                    "truth_size": 10, "n_false_flags": 1, "n_negatives": 10,
                    "n_excluded": 0}, note=""))
    assert "the wrongful-dunning exposure" in payment_shaped
    assert "truly-failed" in payment_shaped


def test_the_headline_never_renders_as_a_bare_scalar(measures):
    """Both directions with their denominators, or nothing -- the anti-decay
    rule the recall-only 0.0081 was published against."""
    rendered = pair.format_pair_summary(measures[pair.PUBLISHED_EXCLUSION_BASIS])
    assert "missed_failure_rate" in rendered and "false_flag_rate" in rendered
    table = pair.format_r13_choice_table(measures)
    for key in pair.EXCLUSION_BASES:
        assert key in table
    assert "PUBLISHED" in table


# ---------------------------------------------------------------------------
# Determinism and the legacy view
# ---------------------------------------------------------------------------

def test_the_partition_is_deterministic():
    """C-S2: same inputs -> byte-identical coupled outcome."""
    a = pair.partition_populations(80, 2016, 2018)
    b = pair.partition_populations(80, 2016, 2018)
    assert (a.must_flag, a.neither, a.must_not_flag, a.flagged) == \
           (b.must_flag, b.neither, b.must_not_flag, b.flagged)


def test_build_scenario_is_a_view_not_a_second_derivation():
    """Two copies of the coupled loop drifting apart is the sibling-half defect
    this repo has already paid for; the legacy 4-tuple is a projection."""
    truth, flagged, harm, stats = pair.build_scenario(80, 2016, 2018)
    p = pair.partition_populations(80, 2016, 2018)
    assert truth == set(p.must_flag) and flagged == set(p.flagged)
    assert harm == p.harm and stats == p.stats
