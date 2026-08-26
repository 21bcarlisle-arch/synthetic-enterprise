"""R15 controls for PB3 exit (d) -- the belief-vs-truth gap on book growth.

Every control here is paired with a MUTATION that names the defect it catches, so
none of them is a control that cannot fail. The three killer patterns
(CONTROLS_THAT_CANNOT_FAIL.md) are each aimed at explicitly:

  TAUTOLOGY   -- `test_MUTATION_moving_the_belief_alone_does_not_move_the_no_skill_arm`
                 proves g0 is not derived from the thing it is the baseline for.
  FAIL-OPEN   -- `test_an_unusable_record_REFUSES` x4 proves a missing / unreadable /
                 wrong-typed / empty record cannot publish a number.
  FAIL-SILENT -- `test_a_campaign_with_no_market_decided_year_is_UNDEFINED_not_zero`
                 proves an unscoreable campaign reports None (the ledger's designed
                 "unmeasured"), never a 0.0 the Proof door renders as a wall leak.

The partition control the PB3 DISCOVER pass named -- "a writer that pools the two
partitions must fail the control" -- is
`test_MUTATION_pooling_the_machine_bound_years_changes_the_headline`.
"""

from __future__ import annotations

import json

import pytest

from tools.couple_pb3_book_growth import (
    CAMPAIGN_RECORD,
    MACHINE_BINDINGS,
    TWIN_ATOM_ID,
    WORLD_ATOM_ID,
    CampaignRecordUnusable,
    is_machine_bound,
    load_campaign_record,
    measure,
)


def _year(year, quotes, wins, *, belief=0.2, realised=None, binding="growth_rate"):
    """One `by_year` row in the shape `plan_growth_campaign` actually emits."""
    return {
        "year": year,
        "quotes_issued": quotes,
        "quotes_affordable": quotes,
        "wins": wins,
        "believed_win_rate": belief,
        "realised_win_rate_used": realised,
        "planning_on": "realised" if realised is not None else "belief",
        "binding": binding,
        "spend_gbp": 0.0,
        "accounts_after": wins,
    }


def _record(rows, **extra):
    return {"by_year": list(rows), "customer_year_budget": 1200.0, **extra}


# ---------------------------------------------------------------------------
# The measurement itself
# ---------------------------------------------------------------------------

def test_the_gap_is_learned_error_over_no_skill_error():
    """The headline is exactly the ratio it declares, on arithmetic done by hand.

    Year A: believed 0.20, realised 100/1000 = 0.10 -> learned err 0.10, no-skill 0.10
    Year B: planned on 0.10, realised 300/1000 = 0.30 -> learned err 0.20, no-skill 0.10
    mean learned = 0.15, mean no-skill = 0.10, gap = 1.5
    """
    result, stats = measure(_record([
        _year(2020, 1000, 100),
        _year(2021, 1000, 300, realised=0.10),
    ]))
    assert stats["n_scored"] == 2
    assert result.raw_gap == pytest.approx(0.15)
    assert result.g0 == pytest.approx(0.10)
    assert result.gap == pytest.approx(1.5)


def test_a_company_that_learns_perfectly_scores_below_one():
    """The metric can reward, not only punish -- otherwise it is not a measurement.

    A belief equal to the outcome gives raw_gap 0 while the founding constant is
    wrong, so the gap is 0.0 -- and the direction is the one the baseline claims.
    """
    result, _ = measure(_record([
        _year(2020, 1000, 300, realised=0.30),
        _year(2021, 1000, 400, realised=0.40),
    ]))
    assert result.raw_gap == pytest.approx(0.0)
    assert result.g0 > 0
    assert result.gap == pytest.approx(0.0)


def test_the_belief_read_is_the_one_the_company_DECLARES_it_planned_on():
    """`planning_on` is read, not re-derived.

    Same two rates, opposite declarations: the graded belief follows the
    declaration. A measurement that picked the rate for itself would grade a plan
    the company never made, and both rows here would score identically.
    """
    on_belief, _ = measure(_record([
        {**_year(2021, 1000, 200, belief=0.5, realised=0.2), "planning_on": "belief"},
    ]))
    on_realised, _ = measure(_record([
        {**_year(2021, 1000, 200, belief=0.5, realised=0.2), "planning_on": "realised"},
    ]))
    assert on_belief.raw_gap == pytest.approx(0.3)    # graded on 0.5
    assert on_realised.raw_gap == pytest.approx(0.0)  # graded on 0.2


# ---------------------------------------------------------------------------
# TAUTOLOGY -- g0 must be independent of the belief it grades
# ---------------------------------------------------------------------------

def test_MUTATION_moving_the_belief_alone_does_not_move_the_no_skill_arm():
    """R15 INDEPENDENCE. Change ONLY the learned belief: raw_gap must move and g0
    must not. A g0 derived from the same number it is the baseline for would move
    with it, and the ratio would be blind to the very thing it claims to measure.
    """
    rows = [_year(2021, 1000, 300, belief=0.2, realised=0.10)]
    base, _ = measure(_record(rows))
    mutated, _ = measure(_record([{**rows[0], "realised_win_rate_used": 0.25}]))

    assert mutated.raw_gap != pytest.approx(base.raw_gap)
    assert mutated.g0 == pytest.approx(base.g0)
    assert mutated.gap != pytest.approx(base.gap)


def test_MUTATION_moving_the_OUTCOME_moves_both_arms():
    """The companion direction: truth is common to both arms, so a changed outcome
    must move g0 too. Together with the test above this pins g0 to exactly one of
    its two inputs -- which is what "independent" has to mean here.
    """
    rows = [_year(2021, 1000, 300, belief=0.2, realised=0.10)]
    base, _ = measure(_record(rows))
    mutated, _ = measure(_record([{**rows[0], "wins": 800}]))

    assert mutated.g0 != pytest.approx(base.g0)
    assert mutated.raw_gap != pytest.approx(base.raw_gap)


# ---------------------------------------------------------------------------
# THE PARTITION -- the machine-bound exclusion has to be load-bearing
# ---------------------------------------------------------------------------

def test_machine_bound_years_are_excluded_and_COUNTED():
    """Excluded, not dropped silently. A reader is owed the count and the years."""
    result, stats = measure(_record([
        _year(2020, 1000, 200, realised=0.20),
        _year(2021, 1000, 10, realised=0.20, binding="settlement_engine"),
        _year(2022, 1000, 200, realised=0.20),
    ]))
    assert stats["n_scored"] == 2
    assert stats["n_excluded_machine_bound"] == 1
    assert result.components["excluded_machine_bound_years"] == [2021]
    assert result.raw_gap == pytest.approx(0.0)


def test_MUTATION_pooling_the_machine_bound_years_changes_the_headline():
    """THE NAMED MUTATION (PB3 DISCOVER, step 3): a writer that pools the two
    partitions must fail this control.

    The engine-truncated year carries a 0.19 error the market never caused. Pooled,
    it lifts the headline from 0.0; partitioned, the headline is the market's alone.
    A partition that made no difference to the number would be decoration.
    """
    rows = [
        _year(2020, 1000, 200, realised=0.20),
        _year(2021, 1000, 10, realised=0.20, binding="settlement_engine"),
        _year(2022, 1000, 200, realised=0.20),
    ]
    partitioned, stats = measure(_record(rows))

    pooled_rows = [{**r, "binding": "growth_rate"} for r in rows]
    pooled, pooled_stats = measure(_record(pooled_rows))

    assert pooled_stats["n_excluded_machine_bound"] == 0
    assert pooled_stats["n_scored"] == 3
    assert pooled.raw_gap > partitioned.raw_gap
    assert pooled.raw_gap == pytest.approx(0.19 / 3)
    assert partitioned.raw_gap == pytest.approx(0.0)


def test_capital_bound_years_are_NOT_excluded():
    """Running out of money is a COMMERCIAL outcome and the supplier owns it.

    The exclusion is for our engine's ceiling only. Widening it to `capital` would
    quietly stop scoring the company on the constraint it is most responsible for.
    """
    assert "capital" not in MACHINE_BINDINGS
    assert not is_machine_bound({"binding": "capital"})
    _, stats = measure(_record([_year(2021, 1000, 200, realised=0.1, binding="capital")]))
    assert stats["n_scored"] == 1


# ---------------------------------------------------------------------------
# FAIL-OPEN / FAIL-SILENT -- an unusable input must never publish a number
# ---------------------------------------------------------------------------

def test_an_unusable_record_REFUSES(tmp_path):
    """Four separate unusable states, each of which must raise rather than score.

    A `0.0` published here would be read by the Proof door as `leak` -- an
    epistemic-wall breach -- so a fail-open on any of these would not merely be a
    missing measurement, it would assert a defect that was never observed.
    """
    missing = tmp_path / "absent.json"
    with pytest.raises(CampaignRecordUnusable):
        load_campaign_record(missing)

    unreadable = tmp_path / "bad.json"
    unreadable.write_text("{not json", encoding="utf-8")
    with pytest.raises(CampaignRecordUnusable):
        load_campaign_record(unreadable)

    wrong_type = tmp_path / "list.json"
    wrong_type.write_text("[]", encoding="utf-8")
    with pytest.raises(CampaignRecordUnusable):
        load_campaign_record(wrong_type)

    for empty in ({}, {"by_year": []}, {"by_year": "2016"}):
        p = tmp_path / "empty.json"
        p.write_text(json.dumps(empty), encoding="utf-8")
        with pytest.raises(CampaignRecordUnusable):
            load_campaign_record(p)


def test_a_campaign_with_no_market_decided_year_is_UNDEFINED_not_zero():
    """Every year machine-bound: the gap is None, and None is what the ledger's
    `gap_measured()` reads as unmeasured -- so PB3's L3 draw stays blocked. A 0.0
    would read as a perfect forecast on a campaign nothing scored.
    """
    result, stats = measure(_record([
        _year(2020, 1000, 10, realised=0.20, binding="settlement_engine"),
        _year(2021, 1000, 10, realised=0.20, binding="settlement_engine"),
    ]))
    assert stats["n_scored"] == 0
    assert result.gap is None
    assert "vacuity" in result.components

    from background.coupled_triad import gap_measured
    entry = result.to_ledger_entry(TWIN_ATOM_ID)
    assert gap_measured(WORLD_ATOM_ID, {WORLD_ATOM_ID: entry}) is False


def test_a_year_that_issued_no_quotes_is_dropped_not_scored_as_a_total_loss():
    """A supplier that never quoted did not lose every quote: the rate is
    UNDEFINED. Scoring 0/0 as 0.0 would invent a catastrophic year.
    """
    result, stats = measure(_record([
        _year(2020, 0, 0),
        _year(2021, 1000, 200, realised=0.20),
    ]))
    assert stats["n_scored"] == 1
    assert stats["n_dropped_undefined"] == 1
    assert result.raw_gap == pytest.approx(0.0)


def test_a_missing_declared_belief_is_dropped_never_DEFAULTED():
    """A defaulted belief is a forecast nobody made, and it would score as skill.

    The row declares `planning_on: realised` and carries no realised rate -- the
    exact shape year one has before any book exists. Substituting the founding
    belief would make raw_gap and g0 identical and the gap a flat 1.0.
    """
    _, stats = measure(_record([
        {**_year(2021, 1000, 200), "planning_on": "realised",
         "realised_win_rate_used": None},
    ]))
    assert stats["n_scored"] == 0
    assert stats["n_dropped_undefined"] == 1


def test_a_no_skill_arm_that_was_exactly_right_gives_an_UNDEFINED_gap():
    """g0 == 0: nothing to divide by. The headline is None, not an infinity and
    not a zero -- `gap_metric._normalise`'s documented degenerate branch.
    """
    result, _ = measure(_record([_year(2021, 1000, 200, belief=0.2, realised=0.15)]))
    assert result.g0 == pytest.approx(0.0)
    assert result.gap is None


# ---------------------------------------------------------------------------
# The shipped record, and the ledger contract
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not CAMPAIGN_RECORD.is_file(),
                    reason="no campaign record on this tree (needs a real run)")
def test_the_shipped_record_scores_and_declares_its_partition():
    """The measurement runs on the REAL artefact, not only on fixtures.

    Skipped rather than failed when no run has produced a record: this file is
    written by `live_population()` and is not tracked, so a fresh clone has none.
    """
    result, stats = measure(load_campaign_record())
    assert stats["n_scored"] >= 1
    assert result.gap is not None
    assert stats["n_excluded_machine_bound"] == len(
        result.components["excluded_machine_bound_years"])


def test_the_ledger_entry_is_well_formed_and_self_consistent():
    """The entry the Proof door renders declares `divisor` and the arithmetic holds.

    `GapResult.__post_init__` refuses a false declaration at construction, so this
    asserts the entry reaches the ledger shape the door's reader expects.
    """
    result, _ = measure(_record([
        _year(2020, 1000, 100),
        _year(2021, 1000, 300, realised=0.10),
    ]))
    entry = result.to_ledger_entry(TWIN_ATOM_ID)
    assert entry["twin_atom_id"] == TWIN_ATOM_ID
    assert entry["metric"] == "belief"
    assert entry["gap"] == pytest.approx(entry["raw_gap"] / entry["g0"])
    assert entry["components"]["belief_organ_atom"] is None
