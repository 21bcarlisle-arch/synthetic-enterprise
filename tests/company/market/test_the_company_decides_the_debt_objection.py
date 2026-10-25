"""The company decides a debt objection from its own ledger, under its own policy.

Defect it names: no company code decided an objection -- the world drew it (EP12) -- so the
register's UNPAID_DEBT ground was never raised by anything.
"""
from __future__ import annotations

import datetime as dt

from company.interfaces.transfer_objection import (
    open_transfer_objection_register,
    request_debt_objection,
)
from company.market.transfer_objection_register import (
    DE_MINIMIS_GBP_PER_FUEL,
    PREPAYMENT_DAP_CEILING_GBP,
    SLC14_MIN_DAYS_SINCE_NOTICE,
    DebtObjectionPolicy,
    ObjectionGround,
    TransferObjectionRegister,
    decide_debt_objection,
)

_DAY = dt.date(2023, 3, 2)


def _decide(bills, *, prepayment=False, fuels=1, policy=DebtObjectionPolicy(), register=None):
    return decide_debt_objection(register or TransferObjectionRegister(), "C1", "SW-1", _DAY,
                                 bills, prepayment=prepayment, fuels=fuels, policy=policy)


def test_an_objection_can_be_raised_and_can_be_declined():
    """The whole partition is reachable, so a guard that refuses everything cannot pass."""
    register = TransferObjectionRegister()
    raised = _decide(((250.0, 60),), register=register)
    declined = _decide(((250.0, 20),))
    assert raised.objected and not declined.objected
    assert register.by_ground(ObjectionGround.UNPAID_DEBT) == [raised.record]
    assert raised.record.switch_request_submitted == _DAY


def test_only_debt_past_the_slc14_clock_counts():
    at_clock = _decide(((500.0, SLC14_MIN_DAYS_SINCE_NOTICE),))
    past_clock = _decide(((500.0, SLC14_MIN_DAYS_SINCE_NOTICE + 1),))
    assert not at_clock.objected and "28 days" in at_clock.reason
    assert past_clock.objected and past_clock.objectionable_debt == 500.0
    # A young bill's balance is not part of what an objection is raised for.
    assert _decide(((300.0, 40), (900.0, 10))).objectionable_debt == 300.0
    assert not _decide(None).objected  # never billed


def test_the_de_minimis_is_per_fuel_and_none_objects_on_any_permitted_debt():
    at = _decide(((DE_MINIMIS_GBP_PER_FUEL, 60),))
    over = _decide(((DE_MINIMIS_GBP_PER_FUEL + 0.01, 60),))
    assert not at.objected and "de-minimis" in at.reason and over.objected
    assert not _decide(((350.0, 60),), fuels=2).objected  # under 2 x 200
    assert _decide(((450.0, 60),), fuels=2).objected
    assert _decide(((5.0, 60),), policy=DebtObjectionPolicy(de_minimis_gbp_per_fuel=None)).objected


def test_a_prepayment_debt_under_the_dap_ceiling_moves_with_the_customer():
    under = _decide(((PREPAYMENT_DAP_CEILING_GBP - 1, 90),), prepayment=True)
    at = _decide(((PREPAYMENT_DAP_CEILING_GBP, 90),), prepayment=True)
    assert not under.objected and "Debt Assignment Protocol" in under.reason
    assert at.objected


def test_the_door_hands_back_plain_values_only():
    register = open_transfer_objection_register()
    answer = request_debt_objection(register, "C9", "2023-03-02", ((400.0, 45),),
                                    prepayment=False, fuels=1)
    assert answer == {"objected": True, "reason": answer["reason"], "objectionable_debt": 400.0,
                      "objection_id": "OBJ-00001"}
    assert all(isinstance(v, (bool, str, float)) for v in answer.values())
    assert request_debt_objection(register, "C9", "2023-03-02", ((400.0, 10),),
                                  prepayment=False, fuels=1)["objection_id"] is None
