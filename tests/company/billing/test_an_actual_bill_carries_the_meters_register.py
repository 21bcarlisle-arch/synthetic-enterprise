"""An actual bill after an estimated run prints the meter's register, not the ledger's running index.

Defect (OCC-01e79fcf2d4fg Nov 2021): the ledger printed an actual closing read as the previous
printed register plus the month's kWh, so after an estimated run it was 1,618.9 where the meter
read 6,514.85. The bill now carries the company's own register (`register_reads`) and the ledger
prints it. Harness as test_the_estimate_window_holds_only_what_the_meter_told_the_supplier.py.
"""

from __future__ import annotations

import pytest

from tests.company.billing.test_the_estimate_window_holds_only_what_the_meter_told_the_supplier import (
    M,
    _Feed,
    _month,
)


def _bills():
    rows = (_month("C1", 9, 230.0) + _month("C1", 10, 420.0) + _month("C1", 11, 700.0)
            + _month("C1", 12, 1000.0))
    return {b["period_end"][:7]: b for b in M.build_monthly_bills(rows, _Feed())}


def test_the_actual_bill_after_a_run_carries_the_register_the_meter_showed():
    b = _bills()["2023-11"]
    # Sep read 230; Oct unread; Nov read: the register has advanced 230 + 420 + 700.
    assert b["register_closing_kwh"] == pytest.approx(1350.0, abs=0.5)
    # The printed advance is the usage this bill charges, so closing - opening reconciles to it.
    assert (b["register_closing_kwh"] - b["register_opening_kwh"]
            == pytest.approx(b["total_consumption_kwh"], abs=0.01))
    # Control: the branch is taken at all, and an estimated bill carries no register of its own.
    assert "register_closing_kwh" not in _bills()["2023-10"]
