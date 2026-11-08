# ARCHIVED LEGS of tests/company/finance/test_a_credit_balance_on_receivables_is_a_liability.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/finance/test_a_credit_balance_on_receivables_is_a_liability.py.
"""A credit balance on Trade Receivables is a liability, not a negative asset.

Found at the end of `docs/staging/WORKER_FINDING_THE_TREASURY_DRAWDOWN_FIGURE_IS_AN_
ARTEFACT_OF_SORTING_A_BALANCE_THAT_WAS_NEVER_A_SERIES_2026-08-24.md`, left open there:
once the journal keeps its signs, a real end-2019 run closes 2020 trade receivables at
**-£53.47**. Account 1100 is debit-normal, so a book whose customers have collectively
paid ahead of what they were billed nets negative -- and that is money owed BACK to
customers, not an asset of minus fifty-three pounds. Published as a negative asset it
both understates total assets and hides a liability.

`balance_sheet()` now splits the net: the debit balance stays the receivable, the credit
balance is reported as `customer_accounts_in_credit_gbp` and joins total liabilities. No
journal entry is posted -- it is a presentation rule.

R15 MUTATION RECORD -- five named mutations applied, four to
`company/finance/double_entry.py::balance_sheet` and one to the report section that
prints it, fires OBSERVED and recorded, not predicted. The unmutated tree is green.

| mutation | tests fired |
|---|---|
| M1 restore the netted read (`receivables = net("1100")`, no split) -- the named defect | 6 |
| M2 clamp the receivable but DROP it from liabilities (assets rise, nothing owed) | 2 |
| M3 fail-open: `customer_accounts_in_credit = 0.0` always | 4 |
| M4 over-reach: apply the same clamp to cash (1001) as well | 1 |
| M5 render the liability row unconditionally (£0.00 on every ordinary year) | 1 |

M4 is the one that earns its place. The split is deliberately NOT applied to cash, and
without a test saying so the exclusion is indistinguishable from an oversight -- a later
reader "completing" the pattern would report an overdrawn company as holding zero cash.
"""

import pytest

from company.finance.double_entry import balance_sheet, build_journal
from company.finance.treasury import working_capital


def _billing(cid="C1", amount=100.0, period="2022-01-01"):
    return {
        "transaction_id": f"bill-{cid}-{period}",
        "event_type": "billing_event",
        "timestamp": period,
        "customer_id": cid,
        "amount_gbp": amount,
    }


def _payment(cid="C1", amount=120.0, date="2022-02-01"):
    return {
        "transaction_id": f"pmt-{cid}-{date}",
        "event_type": "payment_received_event",
        "timestamp": date,
        "customer_id": cid,
        "amount_gbp": amount,
    }


def _settlement(cid="C1", amount=80.0, date="2022-01-01", period=1):
    return {
        "transaction_id": f"settle-{cid}-{date}-{period}",
        "event_type": "settlement_event",
        "timestamp": date,
        "customer_id": cid,
        "settlement_period": period,
        "amount_gbp": -amount,
    }


# Billed 100, paid 120: the customer is 20 ahead. This is the shape of the real
# instance -- a portfolio whose payments have overtaken its billing.
PAID_AHEAD = [_billing(amount=100.0), _payment(amount=120.0)]
OPENING = 1000.0


@pytest.fixture
def paid_ahead_bs():
    return balance_sheet(build_journal(PAID_AHEAD, opening_treasury=OPENING))














def test_working_capital_does_not_move_when_the_credit_is_reclassified():
    """A downstream published figure that must NOT change. `treasury.working_capital`
    subtracts liabilities from current assets, and the split adds the same amount to
    each side, so the working-capital line a reader sees is identical either way.
    Computed here from the components rather than asserted as a constant, so it stays
    a statement about the split and not about this fixture's arithmetic."""
    bs = balance_sheet(build_journal(PAID_AHEAD, opening_treasury=OPENING))
    netted_assets = bs["cash_gbp"] - bs["customer_accounts_in_credit_gbp"]

    assert working_capital(bs) == pytest.approx(
        netted_assets - (bs["total_liabilities_gbp"] - bs["customer_accounts_in_credit_gbp"])
        - bs["vat_payable_gbp"]
    )


def _rendered_balance_sheet_section(bs):
    """The published section, rendered. A field the report never prints is not a
    published figure, so the split is checked at the pixel and not only at the dict."""
    from saas.reporting.annual_report import _section_management_accounts

    return _section_management_accounts({
        "management_accounts": {"2020": {"income_statement": {}, "balance_sheet": bs}}
    })






