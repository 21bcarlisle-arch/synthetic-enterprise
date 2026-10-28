"""E3 (2026-10-28): an actual bill after estimates opens on the last estimated reading the customer saw.

Defect (SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_FROM_ONE_READ_AND_PRINTS_6436_OPENING_
READS_NOBODY_TOOK_2026-10-28.md, E3): the ledger printed the register less the month as the opening,
a read no meter or customer gave (C3g gas Dec 2016: previous closing 3,839.2, printed opening 5,942.3);
6,435 of 6,444 estimated-to-actual transitions on the 37abacdf42 book. Practice
(back_billing_and_liability.md §13): the opening is the previous estimated reading, and the advance
covers the month plus the catch-up. So closing - opening = usage + `catchup_kwh` as printed, and every
reader of the reads subtracts the catch-up to get the period's own use.

Measured on the 37abacdf42 book's ledger rebuilt: openings off the previous closing 6,436 -> 0, every
other invariant's count unchanged; the new row grades 6,405 breaches on the old ledger and 13 on the
new (all on accounts returning from a time-of-use tariff, whose total register is not exported: E4).
"""

from __future__ import annotations

import yaml

from company.billing.pre_bill_validation import check_reads_reconcile, validate_rendered_bill_reads
from company.billing.raw_account_export import raw_account
from tools import domain_invariant_runner as runner
from tools.independent_bill_validator import _volume_from_reads

#: Oct estimated at 300 against a true 500; Nov actual, 450 used: register 1000 + 500 + 450 = 1950.
EST_CLOSING, NOV_CLOSING, NOV_USE = 1300.0, 1950.0, 450.0
CATCHUP = NOV_CLOSING - NOV_USE - EST_CLOSING  # 200 kWh under-estimated


def _invoices(opening_after_run):
    return [
        {"period_start": "2023-10-01", "period_end": "2023-10-31", "commodity": "electricity",
         "meter_serial": "S1", "read_type": "E", "opening_read_kwh": 1000.0,
         "closing_read_kwh": EST_CLOSING, "consumption_kwh": 300.0},
        {"period_start": "2023-11-01", "period_end": "2023-11-30", "commodity": "electricity",
         "meter_serial": "S1", "read_type": "A", "opening_read_kwh": opening_after_run,
         "closing_read_kwh": NOV_CLOSING, "consumption_kwh": NOV_USE,
         **({"catchup_kwh": CATCHUP} if opening_after_run == EST_CLOSING else {})},
    ]


def _grade(invoices, inv_id):
    book = [runner.Account("C1", raw_account("C1", {"invoices": invoices}))]
    inv = next(i for i in runner.load_invariants() if i["id"] == inv_id)
    return runner.ev_opening_is_previous_closing(inv, book) if inv_id.startswith("INV_OPENING_IS") \
        else dict(runner.EVALUATORS)[inv_id][0](inv, book)


def test_the_row_breaches_the_read_nobody_took_and_passes_the_last_estimate():
    """Can fail first: the old shape (opening = register less the month) is a breach."""
    old = _grade(_invoices(NOV_CLOSING - NOV_USE), "INV_OPENING_IS_THE_PREVIOUS_CLOSING")
    new = _grade(_invoices(EST_CLOSING), "INV_OPENING_IS_THE_PREVIOUS_CLOSING")
    assert len(old.breaches) == 1 and old.checked == 1, old.breaches
    assert not new.breaches and new.checked == 1


def test_the_reads_span_the_usage_plus_the_catch_up_for_every_reader():
    """MUTATION: drop the catch-up from any one reader and its leg fails."""
    nov = raw_account("C1", {"invoices": _invoices(EST_CLOSING)})["periods"][1]
    assert nov["catchup_kwh"] == CATCHUP
    assert _volume_from_reads(nov)[0] == NOV_USE
    assert runner.period_kwh(nov) == NOV_USE
    assert not _grade(_invoices(EST_CLOSING), "INV_PERIOD_MATCHES_READS").breaches
    inv = _invoices(EST_CLOSING)[1]
    assert check_reads_reconcile(inv["opening_read_kwh"], inv["closing_read_kwh"], NOV_USE, CATCHUP)
    assert not validate_rendered_bill_reads(inv)
    assert validate_rendered_bill_reads(dict(inv, catchup_kwh=None))  # the gate can still refuse


def test_an_over_estimate_reads_lower_than_the_last_estimate_and_is_not_negative_use():
    """Estimated 1,100 against a true 500: the actual read sits 150 below the last estimate. That
    is the estimate's error on the catch-up line (-600), not the meter running back."""
    invoices = _invoices(EST_CLOSING)
    invoices[0]["closing_read_kwh"] = 2100.0
    invoices[1].update(opening_read_kwh=2100.0, catchup_kwh=-600.0)
    assert not _grade(invoices, "INV_PERIOD_CONSUMPTION_NON_NEGATIVE").breaches
    invoices[1]["catchup_kwh"] = 0.0
    assert _grade(invoices, "INV_PERIOD_CONSUMPTION_NON_NEGATIVE").breaches


def test_a_band_register_carries_no_catch_up_into_the_export():
    """A band index advances by its printed kWh alone, so its readings never span the catch-up."""
    inv = dict(_invoices(EST_CLOSING)[1], registers=[
        {"register_id": "2", "label": "Peak", "opening_read_kwh": 0.0, "closing_read_kwh": 200.0},
        {"register_id": "3", "label": "Off-peak", "opening_read_kwh": 0.0, "closing_read_kwh": 250.0}])
    assert "catchup_kwh" not in raw_account("C1", {"invoices": [inv]})["periods"][0]


def test_the_row_is_in_the_invariants_file_with_its_source():
    rows = yaml.safe_load(open(runner.INVARIANTS_PATH))
    rows = rows["invariants"] if isinstance(rows, dict) else rows
    row = next(r for r in rows if r["id"] == "INV_OPENING_IS_THE_PREVIOUS_CLOSING")
    assert "back_billing_and_liability.md" in row["lower_source"] and row["severity"]["violation"] == "breach"
