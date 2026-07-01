import pytest
from company.regulatory.warm_home_discount import (
    WHDBook, WHDRecord, WHDEligibilityBasis
)


def test_core_group_2022_rate():
    book = WHDBook()
    r = book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    assert abs(r.discount_gbp - 150.0) < 0.01
    assert r.is_core_group is True


def test_broader_group_2021_rate():
    book = WHDBook()
    r = book.record_discount("C1", 2021, WHDEligibilityBasis.BROADER_GROUP, "2021-12")
    assert abs(r.discount_gbp - 140.0) < 0.01
    assert r.is_core_group is False


def test_records_for_year():
    book = WHDBook()
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    book.record_discount("C2", 2022, WHDEligibilityBasis.BROADER_GROUP, "2022-12")
    book.record_discount("C3", 2021, WHDEligibilityBasis.CORE_GROUP, "2021-12")
    assert len(book.records_for_year(2022)) == 2


def test_has_received_whd():
    book = WHDBook()
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    assert book.has_received_whd("C1", 2022) is True
    assert book.has_received_whd("C1", 2021) is False
    assert book.has_received_whd("C2", 2022) is False


def test_total_discounted_for_year():
    book = WHDBook()
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    book.record_discount("C2", 2022, WHDEligibilityBasis.BROADER_GROUP, "2022-12")
    total = book.total_discounted_gbp(2022)
    assert abs(total - 300.0) < 0.01


def test_levy_recoverable_before_recovery():
    book = WHDBook()
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    assert abs(book.levy_recoverable_gbp() - 150.0) < 0.01


def test_mark_levy_recovered():
    book = WHDBook()
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    book.record_discount("C1", 2021, WHDEligibilityBasis.CORE_GROUP, "2021-12")
    n = book.mark_levy_recovered(2022)
    assert n == 1
    assert abs(book.levy_recoverable_gbp() - 140.0) < 0.01


def test_core_broader_counts():
    book = WHDBook()
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    book.record_discount("C2", 2022, WHDEligibilityBasis.BROADER_GROUP, "2022-12")
    book.record_discount("C3", 2022, WHDEligibilityBasis.BROADER_GROUP, "2022-12")
    assert book.core_group_count(2022) == 1
    assert book.broader_group_count(2022) == 2


def test_whd_summary_keys():
    book = WHDBook()
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    s = book.whd_summary(2022)
    for k in ("scheme_year", "total_records", "total_discounted_gbp",
               "core_group", "broader_group", "levy_recoverable_gbp"):
        assert k in s


def test_whd_summary_empty_year():
    book = WHDBook()
    s = book.whd_summary(2022)
    assert s["total_records"] == 0
    assert s["total_discounted_gbp"] == 0.0


def test_records_for_account():
    book = WHDBook()
    book.record_discount("C1", 2021, WHDEligibilityBasis.CORE_GROUP, "2021-12")
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    book.record_discount("C2", 2022, WHDEligibilityBasis.BROADER_GROUP, "2022-12")
    assert len(book.records_for_account("C1")) == 2


# --- Phase LM depth tests ---

def test_account_id_stored():
    book = WHDBook()
    r = book.record_discount("ACCT_LM", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    assert r.account_id == "ACCT_LM"


def test_scheme_year_stored():
    book = WHDBook()
    r = book.record_discount("C1", 2023, WHDEligibilityBasis.CORE_GROUP, "2023-12")
    assert r.scheme_year == 2023


def test_eligibility_basis_stored():
    book = WHDBook()
    r = book.record_discount("C1", 2022, WHDEligibilityBasis.BROADER_GROUP, "2022-12")
    assert r.eligibility_basis == WHDEligibilityBasis.BROADER_GROUP


def test_applied_month_stored():
    book = WHDBook()
    r = book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-11")
    assert r.applied_month == "2022-11"


def test_levy_recovered_default_false():
    book = WHDBook()
    r = book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    assert r.levy_recovered is False


def test_core_group_2015_rate_140():
    book = WHDBook()
    r = book.record_discount("C1", 2015, WHDEligibilityBasis.CORE_GROUP, "2015-12")
    assert r.discount_gbp == pytest.approx(140.0)


def test_core_group_unknown_year_fallback():
    book = WHDBook()
    r = book.record_discount("C1", 2030, WHDEligibilityBasis.CORE_GROUP, "2030-12")
    assert r.discount_gbp == pytest.approx(150.0)


def test_total_discounted_no_year_filter():
    book = WHDBook()
    book.record_discount("C1", 2021, WHDEligibilityBasis.CORE_GROUP, "2021-12")
    book.record_discount("C2", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    total = book.total_discounted_gbp()
    assert total == pytest.approx(290.0)


def test_record_discount_returns_record():
    book = WHDBook()
    result = book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    assert isinstance(result, WHDRecord)


def test_mark_levy_recovered_returns_count():
    book = WHDBook()
    book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-12")
    book.record_discount("C2", 2022, WHDEligibilityBasis.BROADER_GROUP, "2022-12")
    n = book.mark_levy_recovered(2022)
    assert n == 2
