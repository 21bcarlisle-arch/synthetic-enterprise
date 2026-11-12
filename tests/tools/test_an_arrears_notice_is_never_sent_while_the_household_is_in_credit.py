"""INV_NO_ARREARS_NOTICE_WHILE_THE_HOUSEHOLD_IS_IN_CREDIT: no arrears notice is dated on a day the household owes nothing.

The defect this names: a level direct-debit household dunned per bill, so its page printed "overdue"
notices while the household's account was in credit (Ofgem's 19 Sep 2014 debt-communications letter:
customers must not be misled into paying). Written blind to the dunning and ledger code: the pages are
built by hand from the page feed's own shape (`ledger.entries`, owed positive, credit negative).

One household, two fuel pages, and the control runs over the whole partition: the same notice reds
when the summed balance is nil or a credit and is clean when the household owes, and one fuel in
debit does not make the household owe while the other fuel's credit is larger.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools import domain_invariant_runner as runner

ROW = "INV_NO_ARREARS_NOTICE_WHILE_THE_HOUSEHOLD_IS_IN_CREDIT"
FILE = Path(runner.__file__).resolve().parent.parent / "docs/design/DOMAIN_INVARIANTS.yaml"
HOUSEHOLD = "SYN-2016-900"


def _e(on, kind, amount, balance):
    return {"date": on, "type": kind, "amount_gbp": amount, "running_balance_gbp": balance}


def _notice(on, balance):
    return _e(on, "notice", 0.0, balance)


def _inv():
    return next(i for i in yaml.safe_load(FILE.read_text())["invariants"] if i["id"] == ROW)


def _grade(elec, gas, tmp_path):
    """Write the household's two fuel pages, read them as the runner reads a --printed book, grade."""
    d = tmp_path / "customers"
    d.mkdir(parents=True)
    for cid, entries in ((HOUSEHOLD, elec), (HOUSEHOLD + "g", gas)):
        (d / f"{cid}.json").write_text(json.dumps({
            "commodity": "gas" if cid.endswith("g") else "electricity", "base_account_id": HOUSEHOLD,
            "ledger": {"as_of_date": "2025-01-01", "entries": entries}}))
    book = {cid: {"segment": "resi", "billing_account_id": HOUSEHOLD, "printed": pr}
            for cid, pr in runner.load_printed(d).items()}
    row = runner.run([_inv()], book)[0]
    tally = runner.ev_no_arrears_notice_while_in_credit(_inv(), [runner.Account(c, r) for c, r in book.items()])
    return row, {(b["where"], b["value"]) for b in tally.breaches}


#: Electricity owes GBP 40 from 1 Mar; a notice on 20 Mar.
ELEC_OWING = [_e("2024-03-01", "invoice_raised", 40.0, 40.0), _notice("2024-03-20", 40.0)]


def test_a_notice_while_the_household_owes_is_clean(tmp_path):
    gas = [_e("2024-02-01", "payment_received", -10.0, -10.0)]          # a small gas credit
    row, breaches = _grade(ELEC_OWING, gas, tmp_path)
    assert (row["status"], row["checked"], breaches) == ("CLEAN", 1, set())


def test_a_notice_while_the_household_is_in_credit_or_at_nil_is_red(tmp_path):
    elec = [_e("2024-03-01", "payment_received", -25.0, -25.0), _notice("2024-03-20", -25.0),
            _e("2024-04-01", "invoice_raised", 25.0, 0.0), _notice("2024-04-10", 0.0)]
    row, breaches = _grade(elec, [], tmp_path)
    assert row["status"] == "BREACHED" and row["checked"] == 2
    assert breaches == {(f"{HOUSEHOLD} {HOUSEHOLD} 2024-03-20", -25.0),
                        (f"{HOUSEHOLD} {HOUSEHOLD} 2024-04-10", 0.0)}


def test_the_two_fuel_pages_are_summed_so_one_fuels_debt_under_the_others_credit_is_red(tmp_path):
    gas = [_e("2024-01-15", "payment_received", -100.0, -100.0)]        # gas credit larger than the debt
    row, breaches = _grade(ELEC_OWING, gas, tmp_path)
    assert row["status"] == "BREACHED"
    assert breaches == {(f"{HOUSEHOLD} {HOUSEHOLD} 2024-03-20", -60.0)}
    # The other page's later entries do not count: the gas credit arriving after the notice is clean.
    gas_late = [_e("2024-03-21", "payment_received", -100.0, -100.0)]
    late_row, late = _grade(ELEC_OWING, gas_late, tmp_path / "late")
    assert (late_row["status"], late) == ("CLEAN", set())


def test_the_row_can_be_clean_and_can_be_red(tmp_path):
    """The partition in one place: the same notice line, two households, both outcomes reached."""
    clean, _ = _grade(ELEC_OWING, [], tmp_path / "a")
    red, _ = _grade(ELEC_OWING, [_e("2024-03-01", "payment_received", -40.0, -40.0)], tmp_path / "b")
    assert clean["status"] == "CLEAN" and red["status"] == "BREACHED"
    assert clean["checked"] == red["checked"] == 1


def test_a_book_read_without_its_pages_is_never_clean():
    row = runner.run([_inv()], {HOUSEHOLD: {"segment": "resi"}})[0]
    assert row["status"] == "NOT_IN_EXPORT"
