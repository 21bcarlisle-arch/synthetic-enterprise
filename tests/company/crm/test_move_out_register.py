"""The company files our household's move-out notice off the wire, and only for points it holds."""
from __future__ import annotations

import datetime as dt

import pytest

from company.crm.move_out_register import MoveOutRegister
from simulation.move_out_notice_feed import MoveOutNoticeFeed


def _wires(points, move=dt.date(2023, 3, 16)):
    return MoveOutNoticeFeed().wire_notices_for_move(points, move)


def test_a_notice_for_a_held_point_is_filed_with_its_three_fields():
    """Defect: a notice decoded but not filed, or filed with a date the wire did not carry. The rare
    branch (a point the book holds) asserted first, then what is filed."""
    reg = MoveOutRegister(holds=lambda sp: sp in {"C1", "C1g"})
    filed = [reg.receive_move_out_wire(w) for w in _wires(["C1", "C1g"])]
    assert all(n is not None for n in filed)
    assert reg.notices() == [
        {"supply_point_id": "C1", "move_out_date": "2023-03-16", "notified_on": "2023-03-14"},
        {"supply_point_id": "C1g", "move_out_date": "2023-03-16", "notified_on": "2023-03-14"},
    ]
    assert reg.notice_for("C1", "2023-03-16") is not None


def test_a_notice_for_a_point_not_on_the_book_is_an_exception_not_a_filing():
    """Defect: the register filing a notice for a point another supplier holds."""
    reg = MoveOutRegister(holds=lambda sp: False)
    assert reg.receive_move_out_wire(_wires(["X9"])[0]) is None
    assert reg.notices() == [] and reg.exceptions()[0]["supply_point_id"] == "X9"


def test_a_notice_carrying_the_destination_is_refused_as_a_leak():
    """Defect: the world's destination premise reaching the company on the notice."""
    wire = _wires(["C1"])[0]
    wire["envelope"]["payload"]["move_destination"] = "PREM-abc"
    with pytest.raises(ValueError, match="world truth"):
        MoveOutRegister(holds=lambda sp: True).receive_move_out_wire(wire)


def test_a_register_without_the_book_refuses_rather_than_filing_everything():
    """Defect: a register that cannot ask whether it holds the point filing every notice."""
    with pytest.raises(ValueError, match="supply book"):
        MoveOutRegister().receive_move_out_wire(_wires(["C1"])[0])
