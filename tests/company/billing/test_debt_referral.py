import pytest
from datetime import date
from company.billing.debt_referral import (
    DebtAdviceOrg, DebtReferral, DebtReferralBook, ReferralStatus,
    REFERRAL_THRESHOLD_GBP
)


@pytest.fixture
def book():
    return DebtReferralBook()


def test_refer_creates_referral(book):
    r = book.refer("C1", 350.0, date(2022, 3, 1))
    assert r.customer_id == "C1"
    assert r.total_debt_gbp == 350.0
    assert r.status == ReferralStatus.REFERRED
    assert r.org == DebtAdviceOrg.STEP_CHANGE  # default


def test_refer_with_specific_org(book):
    r = book.refer("C1", 350.0, date(2022, 3, 1), org=DebtAdviceOrg.CITIZENS_ADVICE)
    assert r.org == DebtAdviceOrg.CITIZENS_ADVICE


def test_update_status_to_accepted(book):
    r = book.refer("C1", 350.0, date(2022, 3, 1))
    ok = book.update_status(r.referral_id, ReferralStatus.ACCEPTED, date(2022, 3, 15))
    assert ok
    assert r.status == ReferralStatus.ACCEPTED
    assert r.response_date == date(2022, 3, 15)


def test_update_status_unknown_id(book):
    assert book.update_status(999, ReferralStatus.ACCEPTED) is False


def test_outstanding_referrals_excludes_resolved(book):
    r1 = book.refer("C1", 350.0, date(2022, 3, 1))
    r2 = book.refer("C2", 500.0, date(2022, 3, 1))
    book.update_status(r1.referral_id, ReferralStatus.COMPLETED)
    outstanding = book.outstanding_referrals()
    assert r2 in outstanding
    assert r1 not in outstanding


def test_eligible_for_referral_above_threshold():
    assert DebtReferralBook.eligible_for_referral(200.0) is True


def test_not_eligible_below_threshold():
    assert DebtReferralBook.eligible_for_referral(199.99) is False


def test_referrals_for_customer(book):
    book.refer("C1", 300.0, date(2022, 3, 1))
    book.refer("C1", 400.0, date(2022, 6, 1))
    book.refer("C2", 250.0, date(2022, 3, 1))
    c1_refs = book.referrals_for_customer("C1")
    assert len(c1_refs) == 2
    assert all(r.customer_id == "C1" for r in c1_refs)


def test_annual_summary(book):
    r1 = book.refer("C1", 300.0, date(2022, 3, 1))
    r2 = book.refer("C2", 400.0, date(2022, 6, 1))
    book.update_status(r1.referral_id, ReferralStatus.ACCEPTED)
    book.update_status(r2.referral_id, ReferralStatus.DECLINED)
    s = book.annual_summary(2022)
    assert s["total_referred"] == 2
    assert s["accepted"] == 1
    assert s["declined"] == 1
    assert s["outstanding"] == 0


def test_annual_summary_empty_year(book):
    s = book.annual_summary(2020)
    assert s["total_referred"] == 0


def test_is_resolved_flag(book):
    r = book.refer("C1", 300.0, date(2022, 3, 1))
    assert not r.is_resolved
    book.update_status(r.referral_id, ReferralStatus.COMPLETED)
    assert r.is_resolved


# --- Phase LH depth tests ---

def test_referral_id_sequential(book):
    r1 = book.refer("C1", 300.0, date(2022, 3, 1))
    r2 = book.refer("C2", 400.0, date(2022, 4, 1))
    assert r1.referral_id == 1
    assert r2.referral_id == 2


def test_referral_date_stored(book):
    r = book.refer("C1", 300.0, date(2022, 6, 15))
    assert r.referral_date == date(2022, 6, 15)


def test_threshold_value():
    assert REFERRAL_THRESHOLD_GBP == pytest.approx(200.0)


def test_exact_threshold_eligible():
    assert DebtReferralBook.eligible_for_referral(200.0) is True


def test_outcome_notes_none_default(book):
    r = book.refer("C1", 300.0, date(2022, 3, 1))
    assert r.outcome_notes is None


def test_response_date_none_default(book):
    r = book.refer("C1", 300.0, date(2022, 3, 1))
    assert r.response_date is None


def test_no_response_is_resolved(book):
    r = book.refer("C1", 300.0, date(2022, 3, 1))
    book.update_status(r.referral_id, ReferralStatus.NO_RESPONSE)
    assert r.is_resolved is True


def test_referred_not_resolved(book):
    r = book.refer("C1", 300.0, date(2022, 3, 1))
    assert r.is_resolved is False


def test_update_sets_notes(book):
    r = book.refer("C1", 300.0, date(2022, 3, 1))
    book.update_status(r.referral_id, ReferralStatus.ACCEPTED, notes="agreed plan")
    assert r.outcome_notes == "agreed plan"


def test_annual_summary_has_year_key(book):
    book.refer("C1", 300.0, date(2023, 1, 1))
    s = book.annual_summary(2023)
    assert s["year"] == 2023
