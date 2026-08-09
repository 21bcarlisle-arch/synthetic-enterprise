"""The supply-book seam's contract — and the one property that could break it silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 2 routed sixteen `simulation.* -> saas.customers` imports through
`company.interfaces.supply_book`. The *routing* is already policed: the
epistemic-wall ratchet fails on any SIM module that imports `saas.customers`
directly, and that check carries its own mutation proof.

What nothing policed is the seam's **identity contract**. The three rosters are
mutable module-level lists that the running simulation appends to
(`run_phase2b` registers each fresh-market acquisition into
`ACQUIRED_CUSTOMERS`) and that test teardown clears in place. If an accessor
here ever returns a defensive copy — the single most natural "tidy-up" someone
will reach for, and the kind of change a reviewer waves through — the
simulation would append registrations into a list nobody reads and clear a list
nobody wrote to. Nothing would raise. The suite would stay green and the world
would be wrong.

That is the exact shape R15 names FAIL-SILENT, so it gets a control that fires
on it. Each test below is written so that the named defect (a copy, a re-bind,
a delegation quietly pointed somewhere else) reds it, and `test_mutation_*`
proves that claim by performing the defect rather than asserting it is
impossible.
"""

from __future__ import annotations

import importlib

import pytest

import saas.customers as roster
from company.interfaces import supply_book

# --------------------------------------------------------------------------
# The identity contract.
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("accessor", "live"),
    [
        ("registered_supply_points", "CUSTOMERS"),
        ("successor_supply_points", "SUCCESSOR_CUSTOMERS"),
        ("acquired_supply_points", "ACQUIRED_CUSTOMERS"),
    ],
)
def test_accessor_returns_the_live_roster_object_not_a_copy(accessor, live):
    """`is`, not `==`. Equality would pass on a copy — which is the defect."""
    got = getattr(supply_book, accessor)()
    expected = getattr(roster, live)
    assert got is expected, (
        f"supply_book.{accessor}() must return the LIVE {live} object. It returned a "
        "different object, so runtime registrations and in-place clears will not be "
        "visible through the seam (see the seam module's IDENTITY section)."
    )


def test_a_runtime_registration_is_visible_through_the_seam():
    """The behaviour the identity contract exists to protect, exercised end to end."""
    book = supply_book.acquired_supply_points()
    before = len(book)
    predecessor = supply_book.registered_supply_points()[0]
    point = supply_book.register_acquired_point(
        "C_SEAMPROBE", predecessor, "2021-06-30"
    )
    try:
        book.append(point)
        assert len(supply_book.acquired_supply_points()) == before + 1
        assert supply_book.registered_point("C_SEAMPROBE") is point
    finally:
        roster._clear_acquired_customers()
    assert supply_book.acquired_supply_points() == []
    assert supply_book.registered_point("C_SEAMPROBE") is None


def test_register_acquired_point_does_not_itself_join_the_book():
    """Building a registration record and putting it on the book are separate acts.

    If this ever changed, the caller's own append would double-register.
    """
    predecessor = supply_book.registered_supply_points()[0]
    supply_book.register_acquired_point("C_SEAMPROBE2", predecessor, "2021-06-30")
    try:
        assert supply_book.registered_point("C_SEAMPROBE2") is None
    finally:
        roster._clear_acquired_customers()


# --------------------------------------------------------------------------
# The delegation contract — the seam answers what the roster answers.
# --------------------------------------------------------------------------

def test_registered_point_answers_for_every_book_and_says_no_to_a_stranger():
    for point in (
        supply_book.registered_supply_points() + supply_book.successor_supply_points()
    ):
        assert supply_book.registered_point(point["customer_id"]) is point
    assert supply_book.registered_point("NOT_ON_ANY_BOOK") is None


def test_settlement_input_is_identity_plus_supply_start_only():
    """Settlement takes exactly two fields from registration — no more, no fewer.

    A widening here is how the seam would quietly start leaking CRM detail into
    the settlement pipeline.
    """
    point = supply_book.registered_supply_points()[0]
    assert supply_book.settlement_input(point) == {
        "customer_id": point["customer_id"],
        "acquisition_date": point["acquisition_date"],
    }


# --------------------------------------------------------------------------
# R15 mutation proofs — perform the defect, assert the control reds.
# --------------------------------------------------------------------------

def test_mutation_a_copying_accessor_reds_the_identity_check(monkeypatch):
    """The named defect: someone makes an accessor 'safe' by returning a copy."""
    monkeypatch.setattr(
        supply_book, "acquired_supply_points", lambda: list(roster.ACQUIRED_CUSTOMERS)
    )

    # The identity check fires...
    with pytest.raises(AssertionError):
        test_accessor_returns_the_live_roster_object_not_a_copy(
            "acquired_supply_points", "ACQUIRED_CUSTOMERS"
        )

    # ...and so does the behaviour it protects: the append lands nowhere.
    before = len(roster.ACQUIRED_CUSTOMERS)
    supply_book.acquired_supply_points().append({"customer_id": "C_LOST"})
    assert len(roster.ACQUIRED_CUSTOMERS) == before, (
        "sanity: a copy really does swallow the registration"
    )
    assert supply_book.registered_point("C_LOST") is None


def test_mutation_a_widened_settlement_projection_reds_its_check(monkeypatch):
    """The named defect: the settlement projection starts carrying CRM fields."""
    monkeypatch.setattr(
        supply_book,
        "settlement_input",
        lambda point: {
            "customer_id": point["customer_id"],
            "acquisition_date": point["acquisition_date"],
            "segment": point.get("segment"),
        },
    )
    with pytest.raises(AssertionError):
        test_settlement_input_is_identity_plus_supply_start_only()


def test_the_seam_is_importable_without_importing_the_sim():
    """The seam is COMPANY-side code. It must not drag the simulated world in.

    Re-imported fresh so a module already resident from another test cannot make
    this pass by accident.
    """
    importlib.reload(supply_book)
    source = importlib.import_module("company.interfaces.supply_book").__doc__ or ""
    assert "supply book" in source.lower()
    import company.interfaces.supply_book as sb

    for name in dir(sb):
        value = getattr(sb, name)
        module = getattr(value, "__module__", "") or ""
        assert not module.startswith(("sim.", "simulation.")), (
            f"{name} came from {module}: the seam has acquired a SIM-side dependency, "
            "which inverts the direction it exists to police"
        )
