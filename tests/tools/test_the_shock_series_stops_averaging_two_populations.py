"""The defect: one percentage published as the average of two different experiences.

`monthly_ops.monthly[].avg_shock_pct` was the mean of every bill-shock event in a month,
across populations who would describe what happened to them in completely different words.
Bill shock is TWO experiences in two populations, not one experience with three causes
(`docs/market_research/what_bill_shock_is.md`): for a level direct debit the shock is a
change in the amount COLLECTED and the bill is a statement that arrives and is filed; for
standard credit the shock IS the bill. Which one applies is decided entirely by how the
household pays.

Measured on the published record before the split: **70.8% of every bill shock this company
had ever published (2,238 of 3,161 events) was measured on households the definition says
the bill does not shock**, and the worst month on record -- 2016-08 at 315.6% -- contained
ZERO events of the population the arithmetic is valid for.

Every control here is keyed to the PROPERTY (a mean may not span populations; an
unattributed event may not be readmitted; an unmeasured month may not publish a zero),
never to today's numbers -- so it stays red if the fold comes back and green when the
series becomes more honest.

REUSE: `test_the_shock_series_publishes_the_bound_its_sample_earns.py` covers the BOUND on
this series and `test_generate_dashboard_monthly.py` covers its aggregation. Neither can
fail when two populations are averaged together -- both were fully green while the defect
was live and on the public artefact, which is why this file exists rather than a case
appended to either.
"""
import pytest

from tools.generate_dashboard_data import (
    SHOCK_DEFINITION_POPULATION,
    extract_monthly_ops,
)


def _ev(cid, month, pct, population):
    return {"customer_id": cid, "period_end": f"{month}-28",
            "bill_shock_pct": pct, "bill_shock_population": population}


def _series(events):
    return {"years": {"2022": {"bill_shock_events": events}}}


def _row(result, month):
    return next(r for r in result["monthly"] if r["month"] == month)


# --------------------------------------------------------------------------
# The headline may not span populations
# --------------------------------------------------------------------------

def test_the_headline_excludes_the_population_its_arithmetic_is_not_valid_for():
    """THE CENTRAL CONTROL. A direct-debit household's bill-to-bill difference may not
    reach `avg_shock_pct`, however large it is.

    The mutation this kills: folding `payment` back into the headline. Under the old
    mixed mean this month reads 904.0%; under the definition it reads 20.0%, because
    the four enormous values belong to households who do not pay the bill.
    """
    row = _row(extract_monthly_ops(_series([
        _ev("A", "2022-01", 0.20, "bill"),
        _ev("B", "2022-01", 10.0, "payment"),
        _ev("C", "2022-01", 12.0, "payment"),
        _ev("D", "2022-01", 11.0, "payment"),
        _ev("E", "2022-01", 12.0, "payment"),
    ])), "2022-01")

    assert row["avg_shock_pct"] == 20.0, (
        "the headline averaged in the payment population -- a bill-to-bill difference "
        "for households for whom the bill is not what they pay"
    )
    assert row["shock_count"] == 1
    assert row["mixed_all_population_avg_pct"] == 904.0, (
        "the pre-split figure must stay visible in the artefact, or the size of the "
        "re-partition is checkable only from the diff"
    )


def test_an_unattributed_event_is_not_readmitted_to_the_headline():
    """The naive repair that must never land.

    When the split first went in, six existing controls went red because their fixtures
    built events with no population. Defaulting a missing population to "bill" inside the
    producer would have turned all six green in one line -- and silently readmitted every
    unattributed event to definition B, which is the exact fold being removed, one level
    down. An event nobody attributed is "unknown".
    """
    row = _row(extract_monthly_ops(_series([
        {"customer_id": "A", "period_end": "2022-01-28", "bill_shock_pct": 5.0},
        _ev("B", "2022-01", 0.30, "bill"),
    ])), "2022-01")

    assert row["avg_shock_pct"] == 30.0
    assert row["shock_count"] == 1, "an unattributed event was counted as definition B"
    assert row["shock_by_population"]["unknown"]["n"] == 1


def test_a_month_with_no_event_in_the_measured_population_publishes_null_not_zero():
    """`0.0` reads as "measured, and no shock". Three real months (2016-08, 2017-01,
    2019-03) have no definition-B event at all, and 2016-08 is the 315.6% that was the
    worst month on the public artefact. A zero there would replace an overstatement with
    a different false claim rather than with a refusal."""
    row = _row(extract_monthly_ops(_series([
        _ev("A", "2022-01", 3.0, "payment"),
        _ev("B", "2022-01", 4.0, "payment"),
    ])), "2022-01")

    assert row["avg_shock_pct"] is None
    assert row["median_shock_pct"] is None
    assert row["max_shock_pct"] is None
    assert row["shock_count"] == 0
    assert row["shock_by_population"]["payment"]["n"] == 2, (
        "the population that WAS observed must still be published -- refusing the "
        "headline is not the same as deleting 70.8% of the record"
    )


# --------------------------------------------------------------------------
# The population that cannot be measured is published, not deleted
# --------------------------------------------------------------------------

def test_every_population_is_published_with_its_own_count_and_bound():
    """Two measures, named separately, never averaged into one percentage."""
    row = _row(extract_monthly_ops(_series([
        _ev("A", "2022-01", 0.20, "bill"),
        _ev("B", "2022-01", 0.40, "bill"),
        _ev("C", "2022-01", 1.00, "payment"),
        _ev("D", "2022-01", 0.60, "unknown"),
    ])), "2022-01")

    pops = row["shock_by_population"]
    assert set(pops) == {"payment", "bill", "out_of_scope", "unknown"}
    assert pops["bill"]["n"] == 2 and pops["bill"]["avg_pct"] == 30.0
    assert pops["payment"]["n"] == 1 and pops["payment"]["avg_pct"] == 100.0
    assert pops["unknown"]["n"] == 1
    assert pops["out_of_scope"]["n"] == 0, "prepayment is 0 in this world, not absent"
    assert pops["out_of_scope"]["avg_pct"] is None, (
        "an unreachable population must publish a null, never a zero"
    )


def test_the_headline_names_the_definition_it_is_a_mean_over():
    """A reader cannot infer a definition from a number. R14's shape: the figure carries
    what it is a mean over, in the artefact rather than in a source comment."""
    result = extract_monthly_ops(_series([_ev("A", "2022-01", 0.20, "bill")]))
    assert _row(result, "2022-01")["avg_shock_pct_definition"] == SHOCK_DEFINITION_POPULATION

    note = result["avg_shock_pct_definition_note"].lower()
    for owed in ("two experiences", "how it pays", "cannot yet measure", "out_of_scope"):
        assert owed in note, f"the definition note stopped saying: {owed}"


def test_the_note_states_the_prepayment_gap_as_a_gap_and_not_as_a_zero():
    """~13% of GB households are prepayment and this world has none. A reader served
    `out_of_scope: 0` with no explanation reads a measured absence."""
    note = extract_monthly_ops(
        _series([_ev("A", "2022-01", 0.20, "bill")])
    )["avg_shock_pct_definition_note"]
    assert "no prepayment channel" in note
    assert "not a measured zero" in note


# --------------------------------------------------------------------------
# The split is a re-partition, not a re-computation
# --------------------------------------------------------------------------

def test_no_event_value_is_changed_by_being_partitioned():
    """The claim the whole commit rests on: every published percentage is the same
    number it was, in a different bucket. If the partition could alter a value, the
    before/after comparison in the pre-registration would be meaningless."""
    events = [
        _ev("A", "2022-01", 0.20, "bill"),
        _ev("B", "2022-01", 9.00, "payment"),
        _ev("C", "2022-01", 0.55, "bill"),
    ]
    row = _row(extract_monthly_ops(_series(events)), "2022-01")

    assert row["mixed_all_population_count"] == 3
    assert row["mixed_all_population_avg_pct"] == pytest.approx(325.0, abs=0.1)
    assert row["shock_by_population"]["bill"]["max_pct"] == 55.0
    assert row["shock_by_population"]["payment"]["max_pct"] == 900.0
    # every event lands in exactly one population, none is dropped
    assert sum(p["n"] for p in row["shock_by_population"].values()) == 3
