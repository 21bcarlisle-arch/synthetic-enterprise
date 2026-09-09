"""A census of what a sample does NOT span, each test named by the defect it catches.

The class of defect here is narrow and it is the one the canon warns about: a census of absences
that quietly stops noticing an absence. Three ways that happens, and there is a test for each --
the canon gains an axis the census never hears about; an axis with no field in the sample reads as
covered; and an agreement the sample was built to produce is scored as fidelity.

THE POISON ROUNDS ARE FIRST-CLASS, not decoration. Every verdict this census returns today is
ABSENT or CARRIED_NOT_SPANNED, so a control asserting "nothing is spanned" passes on a census that
can only ever say no. `test_SPANNED_IS_A_REACHABLE_VERDICT` is what stops that reading.
"""
from __future__ import annotations

import numpy as np
import pytest

from tools import billing_axis_coverage as bac
from tools import demand_vector_coverage as dvc

CANON = bac.canon_path().read_text()


def _population(**fields):
    """A sample carrying exactly the named fields. Nothing here is a real household: the census
    reads FIELD PRESENCE and category counts, so a fixture that generated real demand would cost
    seconds per test and prove nothing extra."""
    return dict(fields)


def test_THE_AXIS_LIST_IS_READ_FROM_THE_CANON_AND_NOT_KEPT_PRIVATELY():
    """The join between the document and the table. If the parse silently returned nothing, every
    other test here would pass vacuously, so this one pins the five phrases the canon states."""
    assert bac.canon_named_axes(CANON) == (
        "meter type and read pattern", "payment method", "tariff with its dates",
        "move history", "credit position")
    # "meter type and read pattern" is ONE axis. Splitting the whole sentence on " and " -- the
    # obvious implementation -- returns six phrases and the census then refuses a canon it agrees
    # with, which is a refusal nobody can act on.
    assert len(bac.canon_named_axes(CANON)) == len(bac.CANON_AXES)


def test_AN_AXIS_ADDED_TO_THE_CANON_AND_NOT_TO_THE_CENSUS_IS_REFUSED():
    """THE DEFECT THIS WHOLE MECHANISM EXISTS FOR, and the exit criterion the atom names. The
    director adds a sixth thing a household needs; the census knows nothing about it; a hand-typed
    axis list would stay green on exactly that day.

    POISONED RATHER THAN OBSERVED: the sixth axis does not exist today, so the branch is unreachable
    from the real document and "it passed" would mean two opposite things."""
    poisoned = CANON.replace(
        "It needs a meter type and read pattern",
        "It needs a debt repayment plan, a meter type and read pattern")
    assert poisoned != CANON, "the poison did not apply -- the canon's sentence has been reworded"
    with pytest.raises(bac.UncoveredCanonAxis) as refusal:
        bac.axis_records(_population(payment_method=["direct_debit"]), canon_text=poisoned)
    assert "debt repayment plan" in str(refusal.value), (
        "the refusal must name the phrase the canon added, or the next reader cannot act on it")


def test_AN_AXIS_DROPPED_FROM_THE_CANON_IS_ALSO_REFUSED():
    """The other direction, and it is not symmetric decoration. A census that kept grading an axis
    the canon had withdrawn would be publishing an uncounted dimension the director had ruled out
    of scope -- an absence that reads as honesty and is out of date."""
    poisoned = CANON.replace(", a move history and a credit position", " and a credit position")
    assert poisoned != CANON
    with pytest.raises(bac.UncoveredCanonAxis) as refusal:
        bac.axis_records(_population(), canon_text=poisoned)
    assert "move history" in str(refusal.value)


def test_A_MISSING_CANON_DOCUMENT_REFUSES_RATHER_THAN_RETURNING_AN_EMPTY_LIST():
    """FAIL CLOSED. The staging protocol MOVES this document when the work is filed, so "the file
    is not where I looked" is a thing that WILL happen. A parse that returned () on a missing
    document would report five axes as vacuously covered on the day the canon was archived."""
    with pytest.raises(bac.UncoveredCanonAxis):
        bac.canon_named_axes("a document that does not contain the sentence")
    with pytest.raises(bac.CanonDocumentMissing) as refusal:
        bac.canon_path(root=bac.PROJECT / "tools")
    assert "docs/staging" in str(refusal.value), "the refusal must name where it looked"


def test_AN_ABSENT_AXIS_CAN_NEVER_READ_AS_SPANNED():
    """The census's own fail-open. An axis with no field in the sample has no observed
    distribution, no category count and no N -- so every one of those must be null and the verdict
    must be ABSENT, whatever published figure the axis happens to have beside it.

    THE TRAP IS SPECIFICALLY THE PUBLISHED FIGURE. Two of the four absent axes DO carry one
    (`smart_meter_penetration`, the Ofgem tariff split), and a census that scored "figure present"
    as coverage would report them spanned while the sample cannot see them at all."""
    records = {r["axis"]: r for r in bac.axis_records(_population(), canon_text=CANON)}
    assert len(records) == len(bac.CANON_AXES)
    for axis, record in records.items():
        assert record["verdict"] == "ABSENT", axis
        assert record["categories_in_the_sample"] is None, axis
        assert record["observed"] is None, axis
        assert record["n_the_answer_earns"] is None, axis
    assert records["meter_type_and_read_pattern"]["population_figure"] is not None, (
        "the trap this test exists for has gone: no absent axis carries a published figure any "
        "more, so 'figure present read as covered' can no longer happen and this is not a control")


def test_SPANNED_IS_A_REACHABLE_VERDICT():
    """A GUARD THAT REFUSES EVERYTHING PASSES EVERY TEST OF ITS REFUSALS. Today the census returns
    no SPANNED verdict at all, so nothing above distinguishes a working instrument from one wired
    to say no. One control over the whole partition: a sample carrying every axis at every category
    the world has must produce the other end of the scale."""
    rng = np.random.default_rng(0)
    spanning = _population(
        # NOT drawn from the anchor: `payment_method` is deliberately excluded here, because that
        # axis can never reach SPANNED while the sample draws it from the constant it is scored
        # against, and a fixture that hid that would be fitted to the conclusion.
        meter_type=rng.choice(["smart", "traditional"], size=500),
        tariff_type=rng.choice(["fixed", "svt"], size=500),
        move_history=rng.choice(["none", "moved"], size=500),
        credit_position=rng.choice(["clear", "in_arrears"], size=500),
    )
    verdicts = {r["axis"]: r["verdict"] for r in bac.axis_records(spanning, canon_text=CANON)}
    assert verdicts["meter_type_and_read_pattern"] == "SPANNED", verdicts
    assert verdicts["tariff_and_dates"] == "SPANNED", verdicts
    # The two axes with no published figure stay short of SPANNED even when the sample carries
    # them -- "we have a column for it" is not the same claim as "we span it", and the census must
    # not let the first stand for the second.
    assert verdicts["move_history"] == "CARRIED_NOT_SPANNED", verdicts
    assert verdicts["credit_position"] == "CARRIED_NOT_SPANNED", verdicts


def test_AN_AGREEMENT_THE_SAMPLE_WAS_BUILT_TO_PRODUCE_IS_NOT_SCORED_AS_FIDELITY():
    """THE TAUTOLOGY, and it is the one defect a reader of the output could not have caught. The
    demand sample draws payment method FROM `DD_SHARE_ELEC`, so its observed direct-debit share
    matches the published one to sampling error by construction. A census that reported that match
    as evidence would be a control that cannot fail, publishing arithmetic as a measurement."""
    records = {r["axis"]: r
               for r in bac.axis_records(_population(payment_method=["direct_debit"] * 72 +
                                                    ["not_direct_debit"] * 28), canon_text=CANON)}
    payment = records["payment_method"]
    assert payment["carried_by"] == "payment_method"
    assert payment["agrees_by_construction"] is True
    assert payment["verdict"] == "CARRIED_NOT_SPANNED"
    assert "arithmetic and not evidence" in payment["why"]
    # AND THE SECOND, INDEPENDENT REASON IS STATED SEPARATELY, because the two have different
    # remedies: the tautology is cured by a source the sample does not draw from, the missing third
    # category by a published split that does not exist yet.
    assert "3" in payment["why"] and "2 categories" in payment["why"]


def test_THE_PUBLISHED_FIGURE_IS_REACHED_AND_NOT_TRANSCRIBED(monkeypatch):
    """A VALUE ASSERTION CANNOT TELL A LITERAL COPY FROM A DERIVATION. Asserting 0.72 passes
    identically whether the census reads the anchor or has the number typed into it -- and a typed
    copy is the thing that goes stale silently when DESNZ publishes the next quarter. So the SOURCE
    is perturbed and the census's figure must move with it."""
    import simulation.population_draw as pd

    monkeypatch.setattr(pd, "DD_SHARE_ELEC", 0.41)
    moved = {r["axis"]: r for r in bac.axis_records(
        _population(payment_method=["direct_debit"]), canon_text=CANON)}
    figure = moved["payment_method"]["population_figure"]
    assert figure["share"] == pytest.approx(0.41), (
        "the census reported a direct-debit share the anchor no longer holds -- it is a copy")
    assert figure["reached_at"] == "simulation.population_draw.DD_SHARE_ELEC"
    # The N the answer earns is computed FROM that share, so it must move too. A bound pinned to
    # the old figure would be a bound about a population nobody is measuring.
    assert moved["payment_method"]["n_the_answer_earns"]["n_for_tolerance"] == (
        bac._share_interval(0.41, 1)["n_for_tolerance"])


def test_EVERY_UNCOUNTED_AXIS_IS_ACCOUNTED_FOR_IN_THE_ONE_ENUMERATION_OF_THE_ABSENCE():
    """TWO LISTS OF THE SAME ABSENCE DIVERGE. `demand_vector_coverage.UNCOUNTED_AXES` is what the
    demand N publishes as its blind spots; the axes here are what the canon says a household needs.
    If this module kept its own private enumeration, the day someone closed a gap in one list is the
    day the other started lying about it."""
    enumerated = set(dvc.UNCOUNTED_AXES)
    for axis in bac.CANON_AXES:
        missing = [name for name in axis.uncounted_as if name not in enumerated]
        assert not missing, (
            f"{axis.key} says it is enumerated as {missing} in demand_vector_coverage."
            f"UNCOUNTED_AXES, and it is not. Either the gap was closed there and this axis now has "
            f"a field, or the two lists have drifted.")


def test_THE_CENSUS_DECLARES_WHAT_IT_REDUCES_OVER_AND_THE_DECLARATION_IS_THE_FINDING():
    """W2_28's control refuses a coverage claim that does not say what it reduces over, and this
    module is one. The declaration is asserted for its SHAPE rather than its contents: exactly the
    canon's axes as the subject, and every component either reduced over or declared blind. Pinning
    today's one-of-five would go red on the day the sample became MORE honest."""
    declaration = bac.REDUCES_OVER
    assert declaration.kind == "coverage"
    assert set(declaration.of) == {a.key for a in bac.CANON_AXES}
    accounted = set(declaration.reduces_over) | set(declaration.blind_to)
    assert accounted == set(declaration.of), (
        f"{sorted(set(declaration.of) - accounted)} is a component of the subject vector this "
        f"claim neither measures nor declares itself blind to")
    assert not (set(declaration.reduces_over) & set(declaration.blind_to))
