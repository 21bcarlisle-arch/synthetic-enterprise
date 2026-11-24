"""A record the run builds for a grade must survive the reducer into the published book.

THE DEFECT (found 2026-11-21, delivery seat). `extract_report_data` is a publication WHITELIST: the
published `run_output_*.json` is its reduced output, and a `phase2b` key it does not name is dropped
silently. Three records were landed on the producer side with their own tests and none was named
here: KNIFE3's `company_debt_recovery` (1624411d2), B8's `retention_holdout_by_desk_year`
(775a3c46c) and the dual household's `riding_leg_answers` (c41e70832). Each producer test calls
`run_phase2b` or reads its source, so all three were green while no published book could carry
the record. Five supplier grades were queued on the next book; three of them would have opened it
and found nothing. Same class as `test_extract_report_data_forwards_svt_departures_and_decisions`.

KEYED TO THE PROPERTY, not to a count: whatever rows the run put in come out unchanged, and a run
that recorded nothing publishes `None`, never an empty table that reads as a measured zero.

THE NAMED MUTATION. Delete any one of the three lines in `extract_report_data` and its present-case
leg fires with a KeyError; give any of them a default (`.get(key, [])` or `{}`) and its absent-case
leg fires.
"""
import json

import pytest

from saas.reporting.annual_report import extract_report_data
from tests.saas.reporting.test_annual_report import _run_output

GRADING_RECORDS = {
    "company_debt_recovery": {
        "as_of": "2025-12-31",
        "write_offs": [{"account": "C1", "date": "2023-04-01", "gbp": 312.4,
                        "invoice_ref": "INV-C1-2022-11", "reason": "statute_barred"}],
        "agency_remittances": [{"account": "C1", "invoice_ref": "INV-C1-2022-11", "stage": "dca",
                                "date": "2023-09-01", "gbp": 40.0, "on_a_ref_written_off": True}],
        "learned": {"cells": {"over_a_year_past_due": {"written_off_gbp": 312.4,
                                                       "recovered_gbp": 40.0, "debts": 1}}},
    },
    "retention_holdout_by_desk_year": {
        "renewal_offer": {"assigned": True, "by_year": {"2019": {"treated": 9, "holdout": 1}}},
        "save_offer": {"assigned": False, "why": "the standing policy runs no save-offer coin"},
    },
    # 23 Nov: B8's blind coin per considered renewal; the switch-on's P3 reads would_offer on it.
    "retention_blind_holdout_log": [
        {"customer_id": "C1", "event_date": "2017-06-01", "commodity": "electricity",
         "arm": "holdout", "company_churn_estimate": 0.41, "would_offer": True,
         "stayed_at_decision": False},
    ],
    "riding_leg_answers": [
        {"customer_id": "C1g", "riding_leg": "gas", "answer": "renewed", "basis": "household"},
    ],
    # 21 Nov: the wins the world refused to supply, which grading the supplied wins reads beside.
    "won_switches_not_supplied": [
        {"customer_id": "SYN-2016-163_3", "won_on": "2017-03-31", "predecessor": "SYN-2016-163",
         "reason": "won from a gas-only household"},
    ],
    # 22 Nov: reg 6C, the erroneous gains returned to their old supplier and any the world kept.
    "erroneous_gains_returned": [
        {"customer_id": "SYN-2016-144_3", "returned_on": "2017-05-18", "agreed_on": "2017-04-18",
         "basis": "stated belief: the last day reg 6C allows"},
    ],
    "erroneous_gains_not_returned": [
        {"customer_id": "SYN-2016-301_3", "due_on": "2018-01-29",
         "reason": "the return falls after the run's window"},
    ],
}


@pytest.mark.parametrize("key", sorted(GRADING_RECORDS))
def test_a_grading_record_the_run_built_is_published_unchanged(key):
    run_output = _run_output()
    run_output["phase2b"][key] = GRADING_RECORDS[key]

    data = extract_report_data(run_output)

    assert data[key] == GRADING_RECORDS[key], (
        f"`{key}` is in the run's phase2b result and missing from the published book: "
        "extract_report_data does not forward it")
    # The book is written with `json.dumps` and no `default=`; the record must cross as it is.
    assert json.loads(json.dumps(data[key])) == GRADING_RECORDS[key]


@pytest.mark.parametrize("key", sorted(GRADING_RECORDS))
def test_a_run_that_recorded_nothing_publishes_none_not_an_empty_record(key):
    data = extract_report_data(_run_output())  # phase2b carries none of the three

    assert data[key] is None, (
        f"`{key}` arrived as {data[key]!r} from a run that never recorded it: an empty record "
        "reads as a measured zero")
