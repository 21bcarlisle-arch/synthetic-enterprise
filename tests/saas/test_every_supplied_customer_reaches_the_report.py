"""Every account a run supplies must resolve in the report, from whichever book it was put on.

THE DEFECT (22 Nov 2026). Book b1c7d76b16 died at 07:57:16Z with KeyError 'SYN-2016-144_3' in
`build_cost_to_serve`: f80fe3951 put won switches on supply from ACQUIRED_CUSTOMERS, and the CLV
snapshot's roster in `annual_report` was a hand-written union that never named that book. The same
KeyError killed a run on OCC-* on 8 Oct and was fixed for that one list. Four unions in the module
differed from each other. Now there is one, `saas.customers.every_supplied_customer`, and this puts
one settled record from EACH registration book through `extract_report_data`.

KEYED TO THE PROPERTY: every list `saas.customers` keeps as a supply book is found by name
(`*_CUSTOMERS`, a list), so a sixth book is covered the day it is added, without editing this
file.

THE NAMED MUTATION. Drop ACQUIRED_CUSTOMERS (or any book) from `every_supplied_customer` and
`test_one_record_from_every_book_survives_the_reducer` raises KeyError in `build_cost_to_serve`.
Give a reader back a hand-written union that misses a book and the same test fails.
"""
import pytest

import saas.customers as sc
from saas.reporting.annual_report import extract_report_data
from tests.saas.reporting.test_annual_report import _record, _run_output

SUPPLY_BOOKS = sorted(
    name for name, value in vars(sc).items()
    if (name == "CUSTOMERS" or name.endswith("_CUSTOMERS")) and isinstance(value, list)
)


def test_the_census_finds_the_five_books():
    # A census that found nothing would make every leg below vacuous.
    assert {"CUSTOMERS", "SUCCESSOR_CUSTOMERS", "ACQUIRED_CUSTOMERS", "DRAWN_CUSTOMERS",
            "INCOMING_OCCUPANT_CUSTOMERS"} <= set(SUPPLY_BOOKS)


@pytest.fixture
def one_account_per_book():
    added: list[tuple[list, dict]] = []
    ids: dict[str, str] = {}
    for book in SUPPLY_BOOKS:
        cid = f"T-{book}"
        record = {"customer_id": cid, "segment": "resi", "acquisition_date": "2016-01-01",
                  "commodity": "electricity", "eac_kwh": 3100.0}
        getattr(sc, book).append(record)
        added.append((getattr(sc, book), record))
        ids[book] = cid
    yield ids
    for book, record in added:
        book.remove(record)


def test_every_supplied_customer_names_every_book(one_account_per_book):
    roster = {c["customer_id"] for c in sc.every_supplied_customer()}
    missing = [book for book, cid in one_account_per_book.items() if cid not in roster]
    assert not missing, f"every_supplied_customer() omits the book(s) {missing}"


def test_one_record_from_every_book_survives_the_reducer(one_account_per_book):
    run_output = _run_output()
    records = run_output["phase2b"]["all_records"]
    for cid in one_account_per_book.values():
        records.append(_record(cid, "electricity", "2016-02-01", 1, 7.0, 1.0, 6.0, 50.0, 1010.0))
        records.append(_record(cid, "electricity", "2017-02-01", 1, 7.0, 1.0, 6.0, 50.0, 1012.0))
    # A renewal per account, so the CLV snapshot (the reader that raised on 22 Nov) runs over them.
    run_output["churn_risk"] = {
        cid: [{"renewal_period": "2016-06", "churn_probability": 0.2}]
        for cid in list(one_account_per_book.values()) + ["C1"]
    }
    data = extract_report_data(run_output)
    lifetime = data["per_customer_lifetime"]
    missing = [book for book, cid in one_account_per_book.items() if cid not in lifetime]
    assert not missing, f"per_customer_lifetime dropped the account(s) from {missing}"
    for year in ("2016", "2017"):
        assert set(one_account_per_book.values()) <= set(data["years"][year]["active_customer_ids"])
