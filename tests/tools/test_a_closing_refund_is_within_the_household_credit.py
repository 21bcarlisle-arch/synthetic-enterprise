"""INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT: a closing refund never exceeds the household's credit across its closing fuel legs.

The defect this names (O14, the eleventh cold read, on the 6fe7827ab2 book): a dual-fuel household was
refunded its closing electricity credit while its closing gas owed more, and the debt was later written
off, because each fuel's refund read that fuel alone (home_moves.md §8.8e). Written blind to the refund
code: these pages are built by hand from §8.8e choices 21-24 and the page feed's own shape.

The breach is asserted first, so a row that grades nothing cannot pass. Then the partition: a set-off
posted on both legs before the refund passes whichever order the pages print it, a refund to exactly the
remainder passes and a penny over does not, a credit on the other leg lends nothing, and an other fuel
still on supply (choice 24) is counted unbounded, never clean.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools import domain_invariant_runner as runner

ROW = "INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT"
FILE = Path(runner.__file__).resolve().parent.parent / "docs/design/DOMAIN_INVARIANTS.yaml"
CLOSED = "2023-05-26"


def _e(on, kind, amount, balance):
    return {"date": on, "type": kind, "amount_gbp": amount, "running_balance_gbp": balance}


#: Electricity closes GBP 111.33 in credit; gas closes owing GBP 40.00 (PROS-2019-0318's shape, smaller debt).
ELEC = [_e("2023-05-01", "payment_received", -150.00, -150.00), _e(CLOSED, "invoice_raised", 38.67, -111.33)]
GAS = [_e("2023-05-01", "invoice_raised", 40.00, 40.00), _e(CLOSED, "invoice_raised", 0.00, 40.00)]
ON = "2023-06-26"

HOUSEHOLDS = {
    # Refunded on one fuel alone: the whole credit paid out while gas owes GBP 40.
    "ALONE": (ELEC + [_e(ON, "refund_debit", 111.33, 0.0)], GAS),
    # Choice 23: the set-off posts on both legs on the refund day, before the refund; the remainder is refunded.
    "SET_OFF": (ELEC + [_e(ON, "set_off_debit", 40.00, -71.33), _e(ON, "refund_debit", 71.33, 0.0)],
                GAS + [_e(ON, "set_off_credit", -40.00, 0.0)]),
    # The same set-off printed after the refund on the credit leg: it still counts once.
    "SET_OFF_PRINTED_AFTER": (ELEC + [_e(ON, "refund_debit", 71.33, -40.00), _e(ON, "set_off_debit", 40.00, 0.0)],
                              GAS + [_e(ON, "set_off_credit", -40.00, 0.0)]),
    # The set-off printed after the refund, but the refund paid the whole credit: the set-off pushed the leg into debt.
    "WHOLE_CREDIT_THEN_SET_OFF": (ELEC + [_e(ON, "refund_debit", 111.33, 0.0), _e(ON, "set_off_debit", 40.00, 40.00)],
                                  GAS + [_e(ON, "set_off_credit", -40.00, 0.0)]),
    # No set-off posted, refund exactly the remainder: the boundary passes.
    "TO_THE_REMAINDER": (ELEC + [_e(ON, "refund_debit", 71.33, -40.00)], GAS),
    # A penny over the remainder breaches; the half-penny tolerance does not absorb it.
    "A_PENNY_OVER": (ELEC + [_e(ON, "refund_debit", 71.34, -39.99)], GAS),
    # The other leg in credit lends nothing: refunding past this leg's own credit still breaches.
    "OTHER_IN_CREDIT": (ELEC + [_e(ON, "refund_debit", 120.00, 8.67)],
                        [_e("2023-05-01", "payment_received", -30.00, -30.00), _e(CLOSED, "invoice_raised", 0.00, -30.00)]),
    "UNPRINTED": (ELEC + [_e(ON, "refund_debit", 1.00, None)], GAS),
}
EXPECTED_BREACHES = {"ALONE", "WHOLE_CREDIT_THEN_SET_OFF", "A_PENNY_OVER", "OTHER_IN_CREDIT", "UNPRINTED"}


def _write(d: Path, hh: str, elec, gas, gas_final=CLOSED):
    for cid, fuel, es, final in ((hh, "electricity", elec, CLOSED), (hh + "g", "gas", gas, gas_final)):
        timeline = [{"type": "final_bill", "date": final}] if final else []
        (d / f"{cid}.json").write_text(json.dumps({
            "segment": "resi", "commodity": fuel, "base_account_id": hh, "timeline": timeline,
            "ledger": {"as_of_date": "2025-07-04", "entries": es}}))


def _grade(d: Path):
    printed = runner.load_printed(d)
    book = {cid: {"segment": "resi", "printed": pr} for cid, pr in printed.items()}
    inv = next(i for i in yaml.safe_load(FILE.read_text())["invariants"] if i["id"] == ROW)
    tally = runner.ev_closing_refund_within_household_credit(inv, [runner.Account(c, r) for c, r in book.items()])
    return inv, book, tally


def test_a_refund_on_one_fuel_while_the_other_owes_breaches(tmp_path):
    _write(tmp_path, "ALONE", *HOUSEHOLDS["ALONE"])
    _, _, tally = _grade(tmp_path)
    assert tally.checked == 1
    assert tally.breaches == [{"where": "ALONE refund on 2023-06-26", "value": 111.33, "bound": 71.33, "side": "above"}]


def test_the_row_fires_on_the_named_households_and_passes_the_rest(tmp_path):
    for hh, (elec, gas) in HOUSEHOLDS.items():
        _write(tmp_path, hh, elec, gas)
    inv, book, tally = _grade(tmp_path)
    assert {b["where"].split()[0] for b in tally.breaches} == EXPECTED_BREACHES
    assert tally.checked == len(HOUSEHOLDS) and tally.unbounded == 0
    row = runner.run([inv], book)[0]
    assert row["status"] == "BREACHED" and row["breached"] == len(EXPECTED_BREACHES), row


def test_an_other_fuel_still_on_supply_is_unbounded_never_clean(tmp_path):
    # Choice 24: gas final-billed after the refund, and gas billed after it with no final bill at all.
    _write(tmp_path, "GAS_LEAVES_LATER", *HOUSEHOLDS["ALONE"], gas_final="2023-07-31")
    elec, gas = HOUSEHOLDS["ALONE"]
    _write(tmp_path, "GAS_STAYS", elec, gas + [_e("2023-07-01", "invoice_raised", 30.0, 70.0)], gas_final=None)
    inv, book, tally = _grade(tmp_path)
    assert tally.breaches == [] and tally.checked == 0 and tally.unbounded == 2
    assert runner.run([inv], book)[0]["status"] == "UNREACHED"


def test_a_single_fuel_household_is_not_this_rows_to_grade(tmp_path):
    (tmp_path / "SOLO.json").write_text(json.dumps({
        "segment": "resi", "commodity": "electricity", "base_account_id": "SOLO",
        "timeline": [{"type": "final_bill", "date": CLOSED}],
        "ledger": {"entries": ELEC + [_e(ON, "refund_debit", 111.33, 0.0)]}}))
    _, _, tally = _grade(tmp_path)
    assert tally.checked == 0 and tally.unbounded == 0


def test_a_book_read_without_the_page_is_not_in_export_never_clean():
    inv = next(i for i in yaml.safe_load(FILE.read_text())["invariants"] if i["id"] == ROW)
    row = runner.run([inv], {"X": {"segment": "resi", "periods": []}})[0]
    assert row["status"] == "NOT_IN_EXPORT", row
