import pytest
from company.regulatory.energy_bill_support import (
    EBSSBook, EBSSCredit, EBSSCreditType,
    EBSS_MONTHLY_CREDIT_GBP, EBSS_ALT_FUEL_CREDIT_GBP, EBSS_MONTHS
)


def test_record_standard_credit():
    book = EBSSBook()
    c = book.record_credit("C1", "2022-10")
    assert abs(c.amount_gbp - 66.67) < 0.01
    assert c.credit_type == EBSSCreditType.STANDARD
    assert c.is_standard is True


def test_record_alt_fuel_credit():
    book = EBSSBook()
    c = book.record_credit("C1", "2022-11", EBSSCreditType.ALT_FUEL)
    assert abs(c.amount_gbp - 100.0) < 0.01
    assert c.is_standard is False


def test_credits_for_account():
    book = EBSSBook()
    for m in EBSS_MONTHS:
        book.record_credit("C1", m)
    book.record_credit("C2", "2022-10")
    assert len(book.credits_for_account("C1")) == 6


def test_total_credited_6_months():
    book = EBSSBook()
    for m in EBSS_MONTHS:
        book.record_credit("C1", m)
    total = book.total_for_account_gbp("C1")
    assert abs(total - 400.0) < 0.1


def test_credits_for_month():
    book = EBSSBook()
    book.record_credit("C1", "2022-10")
    book.record_credit("C2", "2022-10")
    book.record_credit("C1", "2022-11")
    assert len(book.credits_for_month("2022-10")) == 2


def test_govt_receivable_before_claim():
    book = EBSSBook()
    book.record_credit("C1", "2022-10")
    book.record_credit("C2", "2022-10")
    assert abs(book.govt_receivable_gbp() - 2 * 66.67) < 0.01


def test_mark_claimed_reduces_receivable():
    book = EBSSBook()
    book.record_credit("C1", "2022-10")
    book.record_credit("C1", "2022-11")
    book.mark_claimed("2022-10")
    assert abs(book.govt_receivable_gbp() - 66.67) < 0.01


def test_is_scheme_month():
    book = EBSSBook()
    assert book.is_scheme_month("2022-10") is True
    assert book.is_scheme_month("2022-09") is False
    assert book.is_scheme_month("2023-03") is True
    assert book.is_scheme_month("2023-04") is False


def test_monthly_summary():
    book = EBSSBook()
    book.record_credit("C1", "2022-10")
    book.record_credit("C2", "2022-10")
    s = book.monthly_summary()
    assert len(s) == 1
    assert s[0]["month"] == "2022-10"
    assert s[0]["is_ebss_month"] is True


def test_ebss_summary_keys():
    book = EBSSBook()
    book.record_credit("C1", "2022-10")
    book.record_credit("C1", "2022-11", EBSSCreditType.ALT_FUEL)
    s = book.ebss_summary()
    for k in ("total_credits", "total_credited_gbp", "govt_receivable_gbp",
               "scheme_months", "standard_credits", "alt_fuel_credits"):
        assert k in s
    assert s["standard_credits"] == 1
    assert s["alt_fuel_credits"] == 1


def test_ebss_summary_empty():
    book = EBSSBook()
    s = book.ebss_summary()
    assert s["total_credits"] == 0
    assert s["total_credited_gbp"] == 0.0
