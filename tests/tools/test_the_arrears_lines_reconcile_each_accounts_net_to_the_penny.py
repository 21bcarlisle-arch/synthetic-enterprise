"""Each account's arrears lines plus its pre-4c trading net rebuild its realised net, to the penny.

The C1 bracket put the whole selection sign on one household's -5,659.81 arrears charge and could
not split it into write-off, recovery and released placeholder, because the value-cycle artefact
carried no per-account lines (`SEAT_RESULT_PROS_2016_0098S_4218_IS_A_LEAVERS_WRITE_OFF_AND_IT_
LEAVES_IN_BOTH_STATES_2026-09-28.md`). The lines are now returned by the call that books them
(`simulation.arrears_engine.book_arrears_lines`) and graded against `net_by_billing_account_gbp`
by `tools.run_value_cycle_ab.arrears_reconciliation`. These tests book a real fixture through the
real apply step and ask the grade -- and ask it can refuse.
"""

from __future__ import annotations

import copy

import pytest

import company.interfaces.bill_assembly as bill_assembly
from simulation.arrears_engine import ARREARS_LINE_KEYS, book_arrears_lines
from tools.run_value_cycle_ab import (
    _arrears_lines_by_billing_account,
    _decisions_by_billing_account,
    _net_by_billing_account,
    arrears_reconciliation,
)


def _records():
    """Two fuel legs of account A over 2017-2018, and account B in 2018 only."""
    rows = []
    for cid, year, net, placeholder in (("A", 2017, 100.0, 3.0), ("A", 2018, 120.0, 4.0),
                                        ("Ag", 2017, 60.0, 2.0), ("Ag", 2018, 70.0, 2.5),
                                        ("B", 2018, 80.0, 1.5)):
        rows.append({"customer_id": cid, "settlement_date": f"{year}-06-30",
                     "net_margin_gbp": net, "bad_debt_gbp": placeholder,
                     "treasury_cash_balance_gbp": 0.0})
    return rows


def _lines():
    """Every line is taken somewhere, including a year after A's last record (books on its last
    row) and a year before B's first (no record: unbooked)."""
    return {
        "close": {("A", 2018): 400.0, ("A", 2019): 55.55, ("Ag", 2018): 30.0},
        "statute_bar": {("B", 2018): 12.34},
        "stayer_provision": {("B", 2017): 9.99, ("Ag", 2017): 7.0},
        "total": {("A", 2018): 400.0, ("A", 2019): 55.55, ("Ag", 2018): 30.0,
                  ("B", 2018): 12.34, ("B", 2017): 9.99, ("Ag", 2017): 7.0},
    }


_RECOVERY = {("A", 2020): 111.11, ("Ag", 2018): 5.0, ("B", 2016): 2.0}


def _booked():
    records = _records()
    lines = book_arrears_lines(records, _lines(), dict(_RECOVERY))
    return records, lines


def test_the_fixture_takes_every_line():
    """A reconciliation over lines that are all zero passes whatever the identity says."""
    _records_after, lines = _booked()
    folded = _arrears_lines_by_billing_account({"arrears_lines_by_customer": lines})
    for key in ARREARS_LINE_KEYS:
        if key == "line_rounding_gbp":
            continue
        assert any(abs(row[key]) > 0 for row in folded.values()), key


def test_the_lines_rebuild_each_accounts_realised_net_to_the_penny():
    records, lines = _booked()
    net = _net_by_billing_account(records)
    folded = _arrears_lines_by_billing_account({"arrears_lines_by_customer": lines})
    grade = arrears_reconciliation(net, folded)
    assert grade["reconciles"] is True, grade
    assert grade["accounts_graded"] == 2
    # The figures, not only the verdict: A's close write-off is both legs and the year after its
    # last record; B's pre-2018 provision and pre-2018 recovery never reached a row.
    assert folded["A"]["write_off_at_close_gbp"] == 485.55
    assert folded["A"]["dca_recovery_gbp"] == 116.11
    assert folded["A"]["placeholder_bad_debt_released_gbp"] == 11.5
    assert folded["B"]["unbooked_bad_debt_gbp"] == 9.99
    assert folded["B"]["unbooked_recovery_gbp"] == 2.0
    assert net["B"] == pytest.approx(80.0 + 1.5 - 12.34)


@pytest.mark.parametrize("line", ["write_off_at_close_gbp", "dca_recovery_gbp",
                                  "placeholder_bad_debt_released_gbp", "stayer_provision_gbp",
                                  "unbooked_bad_debt_gbp", "pre_4c_net_gbp"])
def test_a_line_a_penny_out_is_refused_and_named(line):
    records, lines = _booked()
    folded = _arrears_lines_by_billing_account({"arrears_lines_by_customer": lines})
    broken = copy.deepcopy(folded)
    broken["A"][line] += 0.01
    grade = arrears_reconciliation(_net_by_billing_account(records), broken)
    assert grade["reconciles"] is False
    assert set(grade["accounts_off_by_a_penny_or_more"]) == {"A"}


def test_an_account_the_lines_never_saw_is_a_residual_not_a_skip():
    records, lines = _booked()
    folded = _arrears_lines_by_billing_account({"arrears_lines_by_customer": lines})
    del folded["B"]
    grade = arrears_reconciliation(_net_by_billing_account(records), folded)
    assert grade["reconciles"] is False
    assert "B" in grade["accounts_off_by_a_penny_or_more"]


def test_a_run_without_the_lines_is_unavailable_not_reconciled():
    records = _records()
    assert _arrears_lines_by_billing_account({}) is None
    grade = arrears_reconciliation(_net_by_billing_account(records), None)
    assert grade["reconciles"] is None
    assert "arrears_lines_by_customer" in grade["why_not"]


def test_the_decision_fields_name_when_an_account_left_and_its_first_roll(monkeypatch):
    monkeypatch.setattr(bill_assembly, "issued_bills", lambda bills: [b for b in bills
                                                                      if not b.get("held")])
    result = {
        "phase2b": {"customer_events": [
            {"customer_id": "A", "event_date": "2020-03-22", "event_type": "churned",
             "effective_retention_probability": 0.2, "random_roll": 0.3763},
            {"customer_id": "A", "event_date": "2017-03-23", "event_type": "renewed",
             "effective_retention_probability": 0.6254, "random_roll": 0.3763},
            {"customer_id": "Ag", "event_date": "2021-01-05", "event_type": "churned",
             "effective_retention_probability": 0.1, "random_roll": 0.5},
            {"customer_id": "B", "event_date": "2018-01-01", "event_type": "acquisition"},
        ]},
        "bills": [{"customer_id": "A"}, {"customer_id": "Ag"}, {"customer_id": "A", "held": True},
                  {"customer_id": "B"}],
    }
    decisions = _decisions_by_billing_account(result)
    assert decisions["A"] == {
        "left_at": "2020-03-22", "renewal_decisions": 3, "bills_issued": 2, "successor_of": None,
        "first_renewal": {"date": "2017-03-23", "p_retain": 0.6254, "roll": 0.3763,
                          "outcome": "renewed"}}
    assert decisions["B"] == {"left_at": None, "first_renewal": None,
                              "renewal_decisions": 0, "bills_issued": 1, "successor_of": None}


def test_sub_penny_rows_still_reconcile_because_the_fold_does_not_round_each_line():
    """Real rows carry sub-penny nets. Rounding each of an account's nine lines to the penny
    before the identity re-adds them drifts the sum by up to 4.5p, and the reconciliation then
    refuses a net that was never wrong -- the 1.2p red a real run first hit."""
    records = [{"customer_id": cid, "settlement_date": f"{year}-06-30",
                "net_margin_gbp": 100.004, "bad_debt_gbp": 3.004,
                "treasury_cash_balance_gbp": 0.0}
               for cid in ("A", "Ag") for year in (2017, 2018)]
    lines = book_arrears_lines(records, {"close": {("A", 2018): 1.0}, "statute_bar": {},
                                         "stayer_provision": {},
                                         "total": {("A", 2018): 1.0}}, {})
    folded = _arrears_lines_by_billing_account({"arrears_lines_by_customer": lines})
    grade = arrears_reconciliation(_net_by_billing_account(records), folded)
    assert grade["reconciles"] is True, grade
