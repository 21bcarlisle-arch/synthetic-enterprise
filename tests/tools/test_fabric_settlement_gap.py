"""The settlement-switch measurement — `tools.fabric_settlement_gap`.

The expensive half (generating the book's traces) is exercised by running the tool,
not by this suite; what is pinned here is the part that decides the VERDICT, because
that is the part a fail-open would quietly turn green.
"""

from __future__ import annotations

import pytest

from tools import fabric_settlement_gap as fsg


def row(cid: str, *, elec: bool = True, gas: bool = True) -> dict:
    return {
        "customer_id": cid,
        "inside_envelope_electricity": elec,
        "inside_envelope_gas": gas,
    }


def test_a_book_inside_the_envelope_has_no_breaches():
    assert fsg.envelope_breaches([row("C1"), row("C2")]) == []


def test_a_breach_on_either_commodity_is_a_breach():
    assert fsg.envelope_breaches([row("C1"), row("C4", gas=False)]) == ["C4"]
    assert fsg.envelope_breaches([row("C4", elec=False)]) == ["C4"]


def test_MUTATION_an_unmeasured_premise_raises_rather_than_counting_as_clear():
    """FAIL-OPEN guard, and the one that matters: a row whose verdict never got
    computed must NOT be silently treated as inside the envelope. `switch_is_clear`
    is read as permission to change the settlement path — reporting it on a book
    that was never fully checked is the defect."""
    with pytest.raises(ValueError):
        fsg.envelope_breaches([row("C1"), {"customer_id": "C4"}])


def test_the_declared_belief_comes_from_the_customer_record_not_the_trace():
    """The company's BELIEF is the declared EAC/AQ. If this ever started reading the
    fabric trace instead, the gap would compare a number with itself (R15 tautology)
    and report perfect agreement forever."""
    declared = fsg._declared_annual_kwh("C4")
    assert declared["electricity"] > 0 and declared["gas"] > 0
    assert declared["gas"] == 22000
