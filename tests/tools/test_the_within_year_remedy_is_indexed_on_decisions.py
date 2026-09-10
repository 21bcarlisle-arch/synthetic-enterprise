"""The withdrawal has a route out; these ask whether the route is priced in the right unit.

THE DEFECT EACH TEST NAMES is written on the test. The class is this project's most expensive
recurring shape: two correct figures whose ratio is not a quantity. `discrimination_auc_within_year`
shipped "about four times as many would halve the interval" with `same_year_pairs` as the subject
of "as many". The permuted half-width falls as `1/sqrt(decisions)`; same-year pairs grow as the
SQUARE of decisions. Four times the pairs is twice the decisions and a 29% narrower interval, so the
published remedy was wrong by a factor of four in the unit a reader would have bought a book in.

TWO OF THESE ARE MEASUREMENTS AND NOT ASSERTIONS, and they are the ones that can refuse the block.
`test_the_within_year_null_falls_as_one_over_root_decisions` permutes the stratified null -- a
different construction from the unstratified one the sibling file checks, because `retained` is
shuffled WITHIN each year -- at four sizes and demands the measured constants agree. And
`test_replicating_the_rows_moves_the_null_and_not_the_answer` is the whole seeds refusal: it
replicates one book's rows and watches an unchanged figure walk outside its own null.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from tools.generate_value_arms_data import (
    _pooled_within_year_auc,
    _within_year_concordance,
)

PROJECT = Path(__file__).resolve().parents[2]
ARTEFACT = (PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json")

#: FEWER DRAWS THAN THE PUBLISHER'S 8,000, deliberately. These tests read the SHAPE of the law --
#: whether a constant holds across four sample sizes -- not an endpoint anyone publishes, and the
#: Monte-Carlo error at 2,000 is an order of magnitude below the effect they are looking for. The
#: seed is the publisher's so a green here and a red on the page cannot be a seed difference.
DRAWS = 2000
SEED = 20260910


@pytest.fixture(scope="module")
def rows():
    if not ARTEFACT.exists():
        pytest.skip("the three-arm artefact is not on disk")
    belief = json.loads(ARTEFACT.read_text()).get("belief_vs_outcome") or {}
    scored = [r for r in belief.get("scored_decisions") or []
              if isinstance(r, dict) and isinstance(r.get("believed_p_retain"), (int, float))
              and isinstance(r.get("retained"), bool) and isinstance(r.get("term_start"), str)]
    if not scored:
        pytest.skip("this artefact publishes no per-decision scored rows")
    return scored


@pytest.fixture(scope="module")
def artefact(rows):
    """The whole three-arm artefact, read once. The fixture exists so a test that needs the
    artefact does not open it itself -- `tools/substring_source_scan_census` reads a `read_text`
    inside a `test_*` body as a control reading source as text, and it is right to: the way to
    settle that here is to stop doing it, not to freeze a row saying this one is fine."""
    return json.loads(ARTEFACT.read_text())


@pytest.fixture(scope="module")
def block(artefact):
    return _within_year_concordance(artefact["belief_vs_outcome"], artefact)


def _by_year(rows, copies=1):
    out = {}
    for row in rows:
        out.setdefault(row["term_start"][:4], []).extend(dict(row) for _ in range(copies))
    return out


def _null(by_year, draws=DRAWS):
    """The publisher's own null construction, at this file's draw count."""
    rng = random.Random(SEED)
    values = []
    for _ in range(draws):
        permuted = {}
        for year, records in by_year.items():
            flags = [r["retained"] for r in records]
            rng.shuffle(flags)
            permuted[year] = [dict(r, retained=f) for r, f in zip(records, flags)]
        drawn, _pairs = _pooled_within_year_auc(permuted)
        if drawn is not None:
            values.append(drawn)
    values.sort()
    return values[int(0.025 * len(values))], values[int(0.975 * len(values))]


def test_the_within_year_null_falls_as_one_over_root_decisions(rows):
    """DEFECT: the remedy inverts `half_width = k / sqrt(n)` with `n` in DECISIONS. If the
    stratified null -- permuted within year, which is not the construction the unstratified curve
    was checked on -- does not obey that law, every count the block publishes is wrong and nothing
    else here would notice."""
    constants = []
    for copies in (1, 2, 4, 8):
        low, high = _null(_by_year(rows, copies))
        n = len(rows) * copies
        constants.append(((high - low) / 2.0) * (n ** 0.5))
    # THE TOLERANCE IS ON THE SPREAD OF THE FOUR, not on any one of them against a pinned value:
    # a control keyed to today's constant reds when the run changes and stays green when the law
    # breaks. An eightfold change in n moving the constant by under a tenth IS the law holding.
    assert max(constants) / min(constants) < 1.12, constants


def test_replicating_the_rows_moves_the_null_and_not_the_answer(rows):
    """DEFECT: `run_seeds.supplies_it` is False on the ground that duplicating rows adds no
    ordering information. If replication moved the point estimate, that reasoning would be wrong
    and pooling seeds would be a real route -- so this is the refusal's own falsifier.

    It is also the demonstration the page publishes: an unchanged figure walking outside its own
    null as the rows are copied is what "more rows is not more evidence" looks like."""
    observed, _pairs = _pooled_within_year_auc(_by_year(rows, 1))
    widths = []
    escaped_at = None
    for copies in (1, 2, 4, 5, 6):
        replicated, _p = _pooled_within_year_auc(_by_year(rows, copies))
        assert replicated == pytest.approx(observed, abs=1e-12), (copies, replicated, observed)
        low, high = _null(_by_year(rows, copies))
        widths.append(high - low)
        if escaped_at is None and not low <= observed <= high:
            escaped_at = copies
    assert widths == sorted(widths, reverse=True), widths
    # ...AND THE ESCAPE ACTUALLY HAPPENS. Without this the test passes on a null that never closes
    # far enough to matter, which is the flattering half of the same finding.
    assert escaped_at is not None and escaped_at <= 8, escaped_at


def test_the_requirement_is_stated_in_both_units_and_they_are_not_the_same_number(block):
    """DEFECT: the published sentence quoted a decisions-indexed law against a pair count. A block
    that carries only one of the two units lets the next reader make the same substitution."""
    remedy = block["what_would_settle_it"]
    assert remedy["available"], remedy
    decisions_multiple = remedy["the_requirement"]["times_this_run"]
    pairs_multiple = remedy["in_same_year_pairs"]["times_this_runs_pairs"]
    assert pairs_multiple == pytest.approx(decisions_multiple ** 2)
    assert pairs_multiple > decisions_multiple
    assert remedy["in_same_year_pairs"]["same_year_pairs_needed"] > block["same_year_pairs"]


def test_the_account_count_is_the_population_and_not_the_artefacts_sample(block, rows):
    """DEFECT: `accounts_needed` divides by a decisions-per-account rate. `auc_population.accounts`
    published 17 -- the accounts in the artefact's ten-row samples -- for a population of 66, and
    reading that would have overstated the required book by nearly four times."""
    households = {str(r["account"]).split("_")[0] for r in rows}
    assert block["accounts"] == len(households)
    assert block["what_would_settle_it"]["the_requirement"]["scored_accounts_this_run"] == (
        len(households))


def test_the_cost_refuses_to_price_a_larger_book_rather_than_extrapolating(block):
    """DEFECT: one clean probe point multiplied by the book multiple reads exactly like a measured
    cost. The block may state this book's cost as a FLOOR and must not state the larger book's at
    all until the probe declares a slope."""
    cost = block["what_would_settle_it"]["the_cost"]
    here = cost["this_book"]
    assert here["peak_mb_at_least"] > 0 and here["machine_hours_at_least"] > 0
    larger = cost["a_larger_book"]
    if not larger.get("available"):
        assert larger.get("reason")
        # NO NUMBER FOR THE THING IT CANNOT PRICE. A refusal that still publishes a figure for the
        # larger book is the fail-open shape: a reader takes the number and drops the caveat.
        assert "peak_mb" not in larger and "machine_hours" not in larger


def test_the_independence_gap_is_not_repaired_by_dropping_the_contaminated_accounts(block):
    """DEFECT: the obvious repair -- score only the decisions both arms agreed about -- conditions
    on a post-treatment variable and biases toward the null. A block that named the contaminated
    accounts without refusing that repair invites it."""
    gap = block["the_grading_population_is_not_independent"]
    assert gap["available"], gap
    # KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. This line read `is False` until
    # `run_value_cycle_ab.belief_against_control_outcomes` was written, and it would have gone red
    # on the day the run first supplied the grading -- the code becoming MORE honest. What must
    # hold on either branch is that the block never leaves the reader with a bare flag: a refusal
    # carries its reason, and an availability carries the figure and the residual caveat.
    if gap["is_it_available_today"]:
        graded = gap["graded_against_the_control_arms_outcomes"]
        assert graded["auc_population"] and graded["scored_decisions"]
        assert "THE POPULATION" in gap["what_is_still_not_independent"]
    else:
        assert gap["why_not"] and gap["what_would_have_to_be_recorded"]
    moved = gap["outcome_moved_by_the_arms_own_price"]
    assert moved["scored_rows_on_those_accounts"] > 0
    assert moved["departures_on_those_accounts"] <= moved["departures"]
    assert "post-treatment" in gap["dropping_them_is_not_the_repair"]
    # ...AND THE ROUTE IT LEAVES OPEN IS A DIFFERENT POPULATION, not a smaller one.
    assert any("MUST NOT BE A FUNCTION OF THE BELIEF" in clause
               for clause in gap["what_an_independent_population_must_look_like"])


def test_BOTH_availability_branches_can_be_taken(artefact):
    """THE CONTROL OVER THE WHOLE PARTITION, written once rather than a leg per branch.

    Asserting the rare branch CAN be taken comes before asserting what it does; this project has
    entered that trap through three different doors in one afternoon.

    BOTH SIDES ARE NOW CONSTRUCTED, and the reason is this control's own history. It was written
    on 2026-09-10 against a premise it stated as fact -- *"every artefact on disk today takes the
    refusal branch"* -- and so it read the refusal side straight off the live artefact and only
    built the available one. That premise was spent the same day, by the A/B pass this control
    exists to make worth running: the artefact now carries
    `belief_against_control_outcomes.available: True`, the unmutated side went to the AVAILABLE
    branch, and the control went red for the single reason that the code had become more honest.

    That is the failure this file's subject was fixed for, reappearing one level up in the thing
    doing the checking. A control keyed to today's artefact goes red when the answer improves and
    green when the claim rots. So neither side is read from disk: the field is REMOVED for one and
    SUPPLIED for the other, over one artefact differing in exactly that field, and the pair stays
    a real partition whichever branch the live run happens to be on.
    """
    stripped = {k: v for k, v in artefact.items() if k != "belief_against_control_outcomes"}
    without = _within_year_concordance(artefact["belief_vs_outcome"], stripped)

    graded = {
        "available": True,
        "discrimination_auc": 0.61,
        "auc_population": {"retained": 80, "left": 40},
        "priced_and_scored": 120,
        "population_terms_absent_from_the_control_world": 3,
        "scored_share_of_priced": 120 / 123,
    }
    with_it = _within_year_concordance(
        artefact["belief_vs_outcome"],
        {**artefact, "belief_against_control_outcomes": graded})

    a = without["the_grading_population_is_not_independent"]
    b = with_it["the_grading_population_is_not_independent"]
    assert a["is_it_available_today"] is False and b["is_it_available_today"] is True
    assert b["graded_against_the_control_arms_outcomes"]["discrimination_auc"] == 0.61
    # THE CAVEAT SURVIVES THE FIGURE ARRIVING. The outcome becomes independent of the belief;
    # the population does not, and a block that dropped the caveat when the number landed would
    # hand the reader the stronger conclusion no run on this book supports.
    assert "conditioned on value-arm survival" in b["what_is_still_not_independent"]
    assert "why_not" not in b
