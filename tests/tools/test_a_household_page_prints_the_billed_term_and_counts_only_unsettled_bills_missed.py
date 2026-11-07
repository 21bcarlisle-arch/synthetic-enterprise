"""Every leg of the two household-page rows the eighth cold read owed (N16 and N15 on the page).

INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM: a printed bill's tariff names a term in force over its
period. The defect it names: "Standard Variable (Electricity)" printed from the account on bills the
run recorded as fixed (PROS-2016-0187, SYN-2016-185).

INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED: a printed "M missed" counts no bill that cash or
credit met by its due date. The defect it names: "4 missed" on SYN-2016-368, whose bills the Energy
Bills Support Scheme paid on time.

"""
from __future__ import annotations

from tools import domain_invariant_runner as runner


def _grade(inv_id, *accounts):
    r = runner.run([{"id": inv_id}], {a["customer_id"]: a for a in accounts})[0]
    return (r["status"], sorted(b["side"] for b in r.get("breach_examples") or ()),
            sorted(f["side"] for f in r.get("flag_examples") or ()))


def _terms(*spans):
    return [{"tariff_type": t, "tariff_effective_from": a, "tariff_effective_to": b} for t, a, b in spans]


def _tariff_page(label, term="fixed", terms=(("fixed", "2020-01-01", "2021-01-01"),), fuel="electricity"):
    return {"customer_id": "T", "segment": "resi", "payments": [],
            "periods": [{"period_start": "2020-01-01", "period_end": "2020-12-31", "commodity": fuel,
                         "contracted_terms": _terms(*terms)}],
            "printed": {"invoices": [{"date": "2020-06-30", "period_start": "2020-06-01", "period_end": "2020-06-30",
                                      "commodity": fuel, "term_tariff_type": term, "tariff_name": label}]}}


def test_every_leg_of_the_page_tariff_row_is_reachable():
    i = "INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM"
    assert _grade(i, _tariff_page("Fixed (Electricity)")) == ("CLEAN", [], [])
    # The account-level name the page used to print, on a fixed bill.
    assert _grade(i, _tariff_page("Standard Variable (Electricity)"))[:2] == ("BREACHED", ["printed name"])
    assert _grade(i, _tariff_page("Standard Variable (Electricity)", term="svt"))[:2] == (
        "BREACHED", ["term not in force"])
    assert _grade(i, _tariff_page("Fixed (Gas)"))[:2] == ("BREACHED", ["fuel"])
    assert _grade(i, _tariff_page("Tracker (Electricity)"))[2] == ["label not read"]
    straddle = (("fixed", "2020-01-01", "2020-06-15"), ("svt", "2020-06-15", None))
    assert _grade(i, _tariff_page("Fixed (Electricity)", terms=straddle)) == (
        "FLAGGED", [], ["term changed mid-bill"])
    assert _grade(i, _tariff_page("Deemed (Electricity)", term="deemed",
                                  terms=(("deemed", "2020-01-01", None),)))[2] == ["name unmapped"]


def _household(missed, *, scheme=0.0, cash=60.0, paid_on="2020-02-10", failed=False, credit=0.0):
    payments = [{"invoice_number": 1, "payment_date": paid_on, "amount_gbp": cash,
                 "outcome": "failed" if failed else "success"}]
    if scheme:
        payments.append({"invoice_number": 1, "payment_date": "2020-02-01", "amount_gbp": 0.0,
                         "outcome": "credit", "scheme_credit_gbp": scheme})
    return {"customer_id": "H", "segment": "resi", "payments": [],
            "periods": [{"period_start": "2020-01-01", "period_end": "2020-01-31", "commodity": "electricity"}],
            "bill_record": {"invoices": [{"invoice_number": 1, "document_type": "bill", "issue_date": "2020-02-01",
                                          "due_date": "2020-02-15", "total_amount_gbp": 60.0,
                                          "credit_applied_gbp": credit}],
                            "payments": payments},
            "printed": {"household": "H", "payment_tallies": [{"iso": "2020-03-01", "missed": missed}]}}


def test_every_leg_of_the_missed_bill_row_is_reachable():
    i = "INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED"
    assert _grade(i, _household(0)) == ("CLEAN", [], [])
    assert _grade(i, _household(1, cash=0.0)) == ("CLEAN", [], [])
    # SYN-2016-368: the scheme paid the bill on time and the page counted it missed.
    assert _grade(i, _household(1, cash=0.0, scheme=60.0))[:2] == ("BREACHED", ["counted missed when settled"])
    assert _grade(i, _household(1, cash=0.0, credit=60.0))[:2] == ("BREACHED", ["counted missed when settled"])
    # A returned DD stays missed though a later credit bill cleared it.
    assert _grade(i, _household(1, failed=True, credit=60.0)) == ("CLEAN", [], [])
    assert _grade(i, _household(1, paid_on="2020-03-01")) == ("CLEAN", [], [])
    assert _grade(i, _household(0, cash=0.0))[2] == ["fewer missed than unsettled"]
    assert _grade(i, _household(1, cash=20.0))[2] == ["part-paid in window"]
