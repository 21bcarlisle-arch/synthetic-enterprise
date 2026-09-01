"""The defect: the year table's average bill shock is one mean over two populations.

`monthly_ops.monthly[].avg_shock_pct` was split at `98db658f2` and reached the published
surface. `financial.annual[].avg_bill_shock_pct` was not, and it is the LARGER subject --
every bill with a computable shock (6,094 on the run this was written for) against the
flagged-only 1,748 -- and it is the figure the year table shows.

Measured before the split: `payment` n=4,366 mean 45.58%, `bill` n=1,696 mean 38.40%,
`unknown` n=32 mean 23.15%, published as a single ~43% with no `n` and no bound at all.

Every control here is keyed to the PROPERTY, never to today's numbers: that the two
definitions are published separately, that the subject is ALL computable bills and not the
flagged ones, that an unattributed bill is not readmitted, and that an unobserved cell
refuses rather than publishes a zero. So each stays red if the fold comes back and green
when the series becomes more honest.

REUSE: `test_the_shock_series_stops_averaging_two_populations.py` is the sibling control for
the MONTHLY series and shares its vocabulary deliberately. It cannot fail for this field --
it never calls `extract_financial`, and the two series read different parts of the run output
(`years[].bill_shock_events` vs top-level `bills`), which is precisely how one got split and
the other did not. `test_generate_dashboard_financial*` covers the annual row's money fields
and was fully green while this mean spanned both populations.
"""
import pytest

from tools.generate_dashboard_data import extract_financial

POPULATIONS = ("payment", "bill", "out_of_scope", "unknown")


def _bill(cid, year, pct, population="bill", month="06"):
    b = {"customer_id": cid, "period_end": f"{year}-{month}-28", "bill_shock_pct": pct}
    if population is not None:
        b["bill_shock_population"] = population
    return b


def _data(bills, years=("2022",), flagged=None):
    return {
        "years": {y: {"bill_shock_events": list(flagged or [])} for y in years},
        "bills": list(bills),
    }


def _row(result, year):
    return next(r for r in result["annual"] if r["year"] == int(year))


# --------------------------------------------------------------------------
# The two definitions are published separately
# --------------------------------------------------------------------------

def test_each_definition_is_published_with_its_own_mean_and_count():
    """THE CENTRAL CONTROL. A direct-debit household's bill-to-bill difference and a
    standard-credit household's bill are two quantities, and the year row must carry both
    under their own names.

    The mutation this kills: publishing only the mixed mean. Here that single figure is
    52.5% -- a number neither population experienced, sitting between 90% and 15%.
    """
    row = _row(extract_financial(_data([
        _bill("A", "2022", 0.10, "bill"),
        _bill("B", "2022", 0.20, "bill"),
        _bill("C", "2022", 0.80, "payment"),
        _bill("D", "2022", 1.00, "payment"),
    ])), "2022")

    pops = row["bill_shock_by_population"]
    assert set(pops) == set(POPULATIONS) | {"mixed_all_population"}
    assert pops["bill"]["n"] == 2 and pops["bill"]["avg_pct"] == 15.0
    assert pops["payment"]["n"] == 2 and pops["payment"]["avg_pct"] == 90.0
    assert pops["mixed_all_population"]["avg_pct"] == 52.5, (
        "the pre-split figure must stay visible in the artefact, or the size of the "
        "re-partition is checkable only from the diff"
    )


def test_every_population_carries_the_bound_its_own_sample_earns():
    """`avg_bill_shock_pct` has never carried an `n` or an interval of any kind. A mean
    over four bills and a mean over four hundred are not the same statement, and this
    distribution's median is near zero against a mean in the forties."""
    row = _row(extract_financial(_data(
        [_bill(f"C{i}", "2022", 0.10 + i / 100.0, "bill") for i in range(30)]
    )), "2022")

    b = row["bill_shock_by_population"]["bill"]
    assert b["n"] == 30
    assert b["ci95_low"] is not None and b["ci95_high"] is not None
    assert b["ci95_low"] < b["avg_pct"] < b["ci95_high"]
    assert b["median_pct"] is not None and b["max_pct"] is not None


def test_a_cell_too_thin_to_bound_itself_says_so_beside_a_real_count():
    """"We cannot tell" is a result. A single bill must publish its value and REFUSE an
    interval -- a one-observation [x, x] would state perfect confidence off one bill,
    which is the fail-open reading of the whole field."""
    pops = _row(extract_financial(_data([
        _bill("A", "2022", 0.42, "bill"),
    ])), "2022")["bill_shock_by_population"]

    assert pops["bill"]["n"] == 1
    assert pops["bill"]["avg_pct"] == 42.0
    assert pops["bill"]["ci95_low"] is None and pops["bill"]["ci95_high"] is None


# --------------------------------------------------------------------------
# The subject is every computable bill -- not the flagged ones
# --------------------------------------------------------------------------

def test_the_split_covers_every_computable_bill_and_not_only_the_flagged_shocks():
    """The wrong implementation that reads plausibly: partition `bill_shock_events`, which
    is what the monthly series does and where the population field was first threaded.

    That is a DIFFERENT AND SMALLER subject -- flagged shocks are movements at or above
    the 20% threshold, 1,748 of the 6,094 computable bills on the real run. Under it this
    year reads n=1; the field it is splitting is a mean over all four.
    """
    data = _data(
        [_bill("A", "2022", 0.01, "bill"), _bill("B", "2022", 0.02, "bill"),
         _bill("C", "2022", 0.03, "bill"), _bill("D", "2022", 0.90, "bill")],
        flagged=[{"customer_id": "D", "period_end": "2022-06-28",
                  "bill_shock_pct": 0.90, "bill_shock_population": "bill"}],
    )
    pops = _row(extract_financial(data), "2022")["bill_shock_by_population"]

    assert pops["bill"]["n"] == 4, (
        "the annual split read the flagged events instead of every computable bill"
    )
    assert pops["mixed_all_population"]["n"] == 4


def test_a_bill_with_no_computable_shock_is_absent_rather_than_counted_at_zero():
    """A first bill, and any bill under `BILL_SHOCK_BASELINE_FLOOR_GBP`, carries `None`.
    Counting it at 0.0 would drag every mean toward a number no household experienced --
    the same published-measured-zero shape the sign fix refused."""
    pops = _row(extract_financial(_data([
        _bill("A", "2022", 0.40, "bill"),
        _bill("B", "2022", None, "bill"),
        _bill("C", "2022", None, "payment"),
    ])), "2022")["bill_shock_by_population"]

    assert pops["bill"]["n"] == 1 and pops["bill"]["avg_pct"] == 40.0
    assert pops["payment"]["n"] == 0 and pops["payment"]["avg_pct"] is None
    assert pops["mixed_all_population"]["n"] == 1


# --------------------------------------------------------------------------
# Nothing is folded, and nothing unobserved is published as a zero
# --------------------------------------------------------------------------

def test_an_unattributed_bill_is_not_readmitted_to_either_definition():
    """The naive repair that must never land: defaulting a missing population to "bill"
    turns fixture reds green in one line and silently readmits every unattributed bill to
    definition B. 32 real bills carry no `payment_channel`."""
    pops = _row(extract_financial(_data([
        _bill("A", "2022", 0.40, "bill"),
        _bill("B", "2022", 5.00, population=None),
    ])), "2022")["bill_shock_by_population"]

    assert pops["bill"]["n"] == 1, "an unattributed bill was counted as definition B"
    assert pops["unknown"]["n"] == 1 and pops["unknown"]["avg_pct"] == 500.0


def test_a_population_this_world_cannot_produce_publishes_null_and_never_zero():
    """~13% of GB households are prepayment and this world has none. `out_of_scope: 0.0`
    would be an unobservable published as a measured zero."""
    pops = _row(extract_financial(_data([
        _bill("A", "2022", 0.40, "bill"),
    ])), "2022")["bill_shock_by_population"]

    assert pops["out_of_scope"]["n"] == 0, "prepayment is 0 in this world, not absent"
    assert pops["out_of_scope"]["avg_pct"] is None
    assert pops["out_of_scope"]["ci95_low"] is None


def test_a_published_year_with_no_computable_bill_carries_an_explicit_empty_block():
    """Keyed on the years being PUBLISHED, not on the years that happen to have bills. A
    missing key reads as "not applicable"; an empty block reads as "nothing observed",
    which is what it is."""
    result = extract_financial(_data(
        [_bill("A", "2022", 0.40, "bill")], years=("2021", "2022")
    ))
    pops = _row(result, "2021")["bill_shock_by_population"]

    assert set(pops) == set(POPULATIONS) | {"mixed_all_population"}
    assert all(pops[p]["n"] == 0 for p in POPULATIONS)
    assert all(pops[p]["avg_pct"] is None for p in POPULATIONS)


# --------------------------------------------------------------------------
# The split is a re-partition, and it reconciles
# --------------------------------------------------------------------------

def test_the_populations_partition_the_bills_exactly_once_each():
    """Every computable bill lands in exactly one population; none is dropped and none is
    double-counted. Without this the two published means could both be right and still
    not describe the book."""
    bills = ([_bill(f"P{i}", "2022", 0.10, "payment") for i in range(7)]
             + [_bill(f"B{i}", "2022", 0.30, "bill") for i in range(3)]
             + [_bill("U", "2022", 0.50, population=None)])
    pops = _row(extract_financial(_data(bills)), "2022")["bill_shock_by_population"]

    assert sum(pops[p]["n"] for p in POPULATIONS) == 11
    assert pops["mixed_all_population"]["n"] == 11


def test_the_mixed_figure_is_the_count_weighted_mean_of_the_populations():
    """What makes the split checkable from the artefact alone rather than from the diff.
    If the mixed figure stopped reconciling, the field kept for continuity would have
    become a third, unexplained number."""
    pops = _row(extract_financial(_data([
        _bill("A", "2022", 0.10, "bill"),
        _bill("B", "2022", 0.30, "bill"),
        _bill("C", "2022", 1.00, "payment"),
        _bill("D", "2022", 0.60, population=None),
    ])), "2022")["bill_shock_by_population"]

    weighted = sum(
        pops[p]["avg_pct"] * pops[p]["n"] for p in POPULATIONS if pops[p]["n"]
    ) / sum(pops[p]["n"] for p in POPULATIONS)
    assert pops["mixed_all_population"]["avg_pct"] == pytest.approx(weighted, abs=0.05)


def test_no_bill_value_is_changed_by_being_partitioned():
    """Every published percentage is the same number it was, in a different bucket. If
    the partition could alter a value the pre-registration's before/after comparison would
    be meaningless."""
    pops = _row(extract_financial(_data([
        _bill("A", "2022", 0.20, "bill"),
        _bill("B", "2022", 9.00, "payment"),
        _bill("C", "2022", 0.55, "bill"),
    ])), "2022")["bill_shock_by_population"]

    assert pops["bill"]["max_pct"] == 55.0
    assert pops["payment"]["max_pct"] == 900.0
    assert pops["mixed_all_population"]["max_pct"] == 900.0


# --------------------------------------------------------------------------
# The note says what the figure beside it is
# --------------------------------------------------------------------------

def test_the_legacy_note_admits_the_field_spans_both_populations():
    """The note used to answer the population question in the WRONG DIMENSION -- which
    bills, never which households -- so it read as a field whose population question was
    settled. That is worse than silence, and it is the shape graded at `63deb6405` one
    level down."""
    note = _row(extract_financial(_data([_bill("A", "2022", 0.40, "bill")])),
                "2022")["avg_bill_shock_pct_population"].lower()

    assert "both populations" in note, "the note still does not say which HOUSEHOLDS"
    assert "bill_shock_by_population" in note, "the note does not point at the split"
    assert "fraction" in note, (
        "the note does not warn that this field is a fraction while its sibling "
        "block publishes percentages"
    )
