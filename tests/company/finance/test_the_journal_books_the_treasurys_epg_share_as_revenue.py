"""The journal's revenue includes the Treasury's EPG share, as `saas.ledger.derive_pnl`'s does.

`company/finance/double_entry.to_journal_entry` returned None for `epg_receipt_event`, so the
management accounts dropped every pound HM Treasury paid under the Energy Price Guarantee:
£252,708 of 2022-23 revenue on the a6b7a0fd47 book, the whole of the gap between the ledger's
£3.28M and the settlement records' £3.54M (`docs/market_research/supplier_financial_reporting.md`
§1a, gap 5). Mutation: delete the `epg_receipt_event` branch -> both tests red.
"""
from __future__ import annotations

import pytest

from company.finance.double_entry import build_journal, income_statement, to_journal_entry
from saas.ledger import (
    derive_pnl,
    make_billing_event,
    make_epg_receipt_event,
    make_vat_remittance_event,
)

_BILL = {
    "customer_id": "SYN-TEST-1",
    "period_start": "2023-01-01",
    "period_end": "2023-01-31",
    "total_amount_gbp": 105.0,
    "vat_gbp": 5.0,
    "hmt_epg_receipt_gbp": 40.0,
    "epg_support_gbp": 40.0,
}


def _events():
    billing = make_billing_event("SYN-TEST-1", "electricity", "2023-01-01", 105.0, 300.0)
    return [billing, make_vat_remittance_event(_BILL), make_epg_receipt_event(_BILL)]


def test_an_epg_receipt_is_posted_cash_in_to_revenue():
    entry = to_journal_entry(make_epg_receipt_event(_BILL))
    assert entry is not None, "the journal drops the EPG receipt"
    assert (entry["debit_account"], entry["credit_account"]) == ("1001", "4001")


def test_the_journal_revenue_matches_the_ledger_revenue_on_an_epg_bill():
    events = _events()
    ledger_revenue = derive_pnl(events)["revenue_gbp"]
    journal_revenue = income_statement(build_journal(events))["revenue_gbp"]
    assert ledger_revenue == pytest.approx(140.0)
    assert journal_revenue == pytest.approx(ledger_revenue)
