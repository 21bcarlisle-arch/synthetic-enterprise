"""A leg that leaves level DD in debit is sent a closing statement for the scheme's debit, and the
page says what it still asks (payments_and_direct_debit_2026-10-25.md, "What is owed", amended
10 Nov 2026).

The defect: SYN-2016-536g left level DD in 2020 owing GBP 112.14 that no invoice, case or statement
on the page asked for, to the book's end (78f82e4242). The balance carried it and nothing demanded it.
"""
from tools.generate_billing_ledger import leaver_closing_statement
from tools.generate_payment_ledger_data import build_account_ledger

AS_OF = "2025-07-04"
LEVEL = 30.0


def _leg(later_cash: list[float], *, months_after: int = 3, level_months: int = 4) -> dict:
    """Four winter months on a GBP 30 level DD against GBP 50 bills (GBP 80 of debit), then bills of
    GBP 20 paid on receipt. `later_cash[n]` is what the household pays against the n-th later bill."""
    invoices, payments, n = [], [], 1000
    for m in range(level_months):
        issue = f"2020-{m + 2:02d}-05"
        invoices.append({"invoice_number": n, "issue_date": issue, "due_date": f"2020-{m + 2:02d}-19",
                         "total_amount_gbp": 50.0, "outstanding_gbp": 0.0})
        payments.append({"invoice_number": n, "payment_date": f"2020-{m + 1:02d}-20",
                         "amount_gbp": LEVEL, "method": "direct_debit", "outcome": "success",
                         "level_dd": True})
        n += 1
    for m in range(months_after):
        issue = f"2020-{m + 2 + level_months:02d}-05"
        invoices.append({"invoice_number": n, "issue_date": issue,
                         "due_date": f"2020-{m + 2 + level_months:02d}-19",
                         "total_amount_gbp": 20.0, "outstanding_gbp": 0.0})
        payments.append({"invoice_number": n, "payment_date": f"2020-{m + 2 + level_months:02d}-19",
                         "amount_gbp": later_cash[m], "method": "standard_credit", "outcome": "success"})
        n += 1
    cust = {"invoices": invoices, "payments": payments, "arrears_history": []}
    cust["balance_gbp"] = -build_account_ledger(cust, AS_OF)["current_balance_gbp"]
    return cust


def _statement(cust: dict):
    return leaver_closing_statement(cust, build_account_ledger(cust, AS_OF)["entries"])


def test_an_unpaid_scheme_debit_is_asked_and_a_paid_one_is_asked_and_met():
    # The partition first: both branches can be reached. A leaver that pays each later bill's face
    # leaves the GBP 80 owed; one that pays GBP 80 more on its first later bill has met it.
    unpaid = _statement(_leg([20.0, 20.0, 20.0]))
    met = _statement(_leg([100.0, 20.0, 20.0]))
    assert unpaid is not None and met is not None
    assert unpaid["outstanding_gbp"] > 0 and met["outstanding_gbp"] == 0

    assert unpaid["asked_gbp"] == 80.0 and unpaid["outstanding_gbp"] == 80.0
    assert unpaid["issue_date"] == "2020-06-05" and unpaid["due_date"] == "2020-07-03"
    assert met["asked_gbp"] == 80.0


def test_the_statement_is_a_demand_not_a_charge():
    cust = _leg([20.0, 20.0, 20.0])
    before = cust["balance_gbp"]
    cust["closing_statement"] = _statement(cust)
    assert build_account_ledger(cust, AS_OF)["current_balance_gbp"] == -before == 80.0


def test_no_statement_while_on_level_or_when_a_final_bill_states_the_balance():
    assert _statement(_leg([], months_after=0)) is None
    assert _statement(_leg([20.0], months_after=1)) is None


def test_what_an_open_case_already_asks_is_not_asked_twice():
    # The second winter collection is returned and its bill's case stays open at GBP 50: the
    # statement asks the rest of the GBP 110 debit, and the two together ask it once.
    cust = _leg([20.0, 20.0, 20.0])
    returned = cust["payments"][1]
    returned["outcome"] = "failed"
    cust["invoices"][1]["outstanding_gbp"] = 50.0
    cust["arrears_history"] = [{"invoice_number": returned["invoice_number"], "arrears_gbp": 50.0,
                                "stages": [{"stage": "DD_FAILED", "date": "2020-02-21",
                                            "note": "Direct debit returned"}]}]
    cust["balance_gbp"] = -build_account_ledger(cust, AS_OF)["current_balance_gbp"]
    st = _statement(cust)
    assert cust["balance_gbp"] == -110.0
    assert st["asked_gbp"] == 60.0 and st["outstanding_gbp"] == 60.0


def test_a_case_repaid_after_leaving_was_still_asking_on_the_day_of_leaving():
    cust = _leg([20.0, 20.0, 20.0])
    returned = cust["payments"][1]
    returned["outcome"] = "failed"
    cust["arrears_history"] = [{"invoice_number": returned["invoice_number"], "arrears_gbp": 0.0,
                                "stages": [{"stage": "DD_FAILED", "date": "2020-02-21",
                                            "note": "Direct debit returned"},
                                           {"stage": "ARREARS_REPAID", "date": "2020-08-01",
                                            "amount_gbp": 50.0, "note": "Payment of GBP50.00"}]}]
    cust["balance_gbp"] = -build_account_ledger(cust, AS_OF)["current_balance_gbp"]
    st = _statement(cust)
    assert cust["balance_gbp"] == -60.0
    assert st["asked_gbp"] == 60.0 and st["outstanding_gbp"] == 60.0
