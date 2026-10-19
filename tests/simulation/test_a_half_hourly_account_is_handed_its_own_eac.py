"""A half-hourly account is billed, before its first read, on the EAC its own use earns.

Defect this catches (2026-10-19): the HH roster records (C7-C9, and the I&C sites) carry
`eac_kwh: None`, so `opening_estimate_kwh` fell back to the TDCV MEDIUM band. C7 billed 3,100 kWh
a year against 13,230 used and was 67% of the open closing undercharge on the 19 Oct book.
Delete the `register_hh_accounts_eac` call in `run_phase2b._main`, or make the function skip
every record, and a test here reds.
"""
from __future__ import annotations

import ast
import copy
import inspect
from datetime import date

import simulation.run_phase2b as p2b
from company.billing.unread_month_estimate import opening_estimate_kwh
from simulation.hh_consumption import is_hh_customer, load_hh_consumption


def _book_and_reads():
    book = copy.deepcopy(p2b.ELEC_CUSTOMERS)
    reads = {c["customer_id"]: load_hh_consumption(c["customer_id"])
             for c in book if is_hh_customer(c)}
    return book, reads


def test_every_unregistered_hh_record_is_written_and_no_other():
    book, reads = _book_and_reads()
    # Every HH roster record is unregistered today, so one is registered here: without it the
    # skip below is never taken and a function that rewrites every HH record passes.
    next(c for c in book if c["customer_id"] == "C8")["eac_kwh"] = 4_000.0
    unregistered = {c["customer_id"] for c in book if is_hh_customer(c) and c["eac_kwh"] is None}
    registered = {c["customer_id"]: c["eac_kwh"] for c in book if c["eac_kwh"] is not None}
    assert "C8" in registered and "C8" in reads
    # Both sides of the partition must be populated, or a function that writes everything (or
    # nothing) could pass one of the two asserts below.
    assert unregistered and registered
    written = {cid for cid, _, _ in p2b.register_hh_accounts_eac(book, reads)}
    assert written == unregistered
    assert {c["customer_id"]: c["eac_kwh"] for c in book
            if c["customer_id"] in registered} == registered


def test_c7s_first_year_estimate_is_its_own_use_not_the_tdcv_band():
    book, reads = _book_and_reads()
    c7 = next(c for c in book if c["customer_id"] == "C7")
    start, end = date(2016, 1, 1), date(2016, 12, 31)
    band = opening_estimate_kwh("electricity", c7, start, end)
    p2b.register_hh_accounts_eac(book, reads)
    own = sum(sum(day) for d, day in reads["C7"].items() if d <= end.isoformat())
    estimate = opening_estimate_kwh("electricity", c7, start, end)
    assert band < own / 3, (band, own)  # the defect is present on the unwritten record
    assert abs(estimate - own) / own < 0.05, (estimate, own)


def test_main_calls_the_registration():
    tree = ast.parse(inspect.getsource(p2b._main))
    called = {n.func.id for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "register_hh_accounts_eac" in called
