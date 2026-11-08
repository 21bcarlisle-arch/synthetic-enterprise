# Increment 3: the legs of tests/company/test_phase_iq_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IQ: deeper coverage for contact_journey, multisite_account, clv_cohort_book."""
import datetime as dt
import pytest

# ===== contact_journey =====
from company.crm.contact_journey import (
    ContactJourney, ContactChannel, ContactPurpose, ContactOutcome
)


def _journey():
    j = ContactJourney()
    j.set_prefs("C1", ContactChannel.EMAIL, bill_by_post=False, paper_free=True)
    j.set_prefs("C2", ContactChannel.PHONE, bill_by_post=True, paper_free=False)
    j.log_attempt("C1", ContactChannel.EMAIL, ContactPurpose.BILL,
                   dt.datetime(2022,3,1,9,0), ContactOutcome.OPENED)
    j.log_attempt("C1", ContactChannel.EMAIL, ContactPurpose.RENEWAL_OFFER,
                   dt.datetime(2022,4,1,9,0), ContactOutcome.BOUNCED)
    j.log_attempt("C2", ContactChannel.PHONE, ContactPurpose.DEBT_CHASE,
                   dt.datetime(2022,5,1,10,0), ContactOutcome.COMPLETED)
    j.log_attempt("C3", ContactChannel.SMS, ContactPurpose.TARIFF_CHANGE,
                   dt.datetime(2022,6,1,9,0), ContactOutcome.OPTED_OUT)
    return j


class TestContactJourney:
    def test_paper_free_discount_eligible(self):
        j = _journey()
        prefs = j.get_prefs("C1")
        assert prefs.paper_free_discount_eligible  # paper_free=True, bill_by_post=False

    def test_not_eligible_when_bill_by_post(self):
        j = _journey()
        prefs = j.get_prefs("C2")
        assert not prefs.paper_free_discount_eligible

    def test_attempt_id_format(self):
        j = _journey()
        assert j._attempts[0].attempt_id == "CA-00001"

    def test_was_successful_opened(self):
        j = _journey()
        assert j._attempts[0].was_successful  # OPENED

    def test_was_not_successful_bounced(self):
        j = _journey()
        assert not j._attempts[1].was_successful  # BOUNCED

    def test_delivery_rate_email(self):
        j = _journey()
        # 1 OPENED (success) + 1 BOUNCED (not) = 50%
        rate = j.delivery_rate_pct(ContactChannel.EMAIL, 2022)
        assert rate == pytest.approx(50.0)

    def test_total_contact_cost_gbp(self):
        j = _journey()
        # EMAIL=0.2p, EMAIL=0.2p, PHONE=350p, SMS=4p = 354.6p = £3.546
        cost = j.total_contact_cost_gbp(2022)
        assert cost == pytest.approx((0.2 + 0.2 + 350.0 + 4.0) / 100, abs=0.001)

    def test_opted_out_customers(self):
        j = _journey()
        assert "C3" in j.opted_out_customers()

    def test_contact_summary_keys(self):
        j = _journey()
        s = j.contact_summary(2022)
        assert "total_attempts" in s and "total_cost_gbp" in s

    def test_was_successful_completed(self):
        j = _journey()
        assert j._attempts[2].was_successful  # COMPLETED


# ===== multisite_account =====
from company.crm.multisite_account import (
    MultisiteAccount, MultisitePortfolio, SiteCategory, BillingFrequency
)


def _account():
    acc = MultisiteAccount("ACC001", "BigCorp Ltd", BillingFrequency.CONSOLIDATED,
                            "Alice", credit_limit_gbp=500_000.0)
    acc.add_site("M001", "Head Office", "EC1A 1BB", SiteCategory.HEAD_OFFICE,
                  5_000_000.0, 500.0, 11.0)
    acc.add_site("M002", "Warehouse", "M1 1AE", SiteCategory.WAREHOUSE,
                  2_000_000.0, 200.0, 0.4)  # LV = not HV
    acc.add_site("M003", "Data Centre", "SE1 9AB", SiteCategory.DATA_CENTRE,
                  8_000_000.0, 800.0, 33.0)
    return acc


class TestMultisiteAccount:
    def test_is_hv(self):
        acc = _account()
        assert acc.supply_points[0].is_hv  # 11kV

    def test_is_not_hv_lv(self):
        acc = _account()
        assert not acc.supply_points[1].is_hv  # 0.4kV

    def test_annual_mwh(self):
        acc = _account()
        assert acc.supply_points[0].annual_mwh == pytest.approx(5000.0)

    def test_site_count(self):
        acc = _account()
        assert acc.site_count == 3

    def test_total_annual_mwh(self):
        acc = _account()
        assert acc.total_annual_mwh == pytest.approx(15000.0)

    def test_peak_site(self):
        acc = _account()
        # Data Centre at 8,000,000 kWh is largest
        assert acc.peak_site.mpan == "M003"

    def test_hv_sites_count(self):
        acc = _account()
        hv = acc.hv_sites()
        assert len(hv) == 2  # Head Office + Data Centre

    def test_remove_site(self):
        acc = _account()
        removed = acc.remove_site("M002")
        assert removed and acc.site_count == 2

    def test_account_summary_keys(self):
        acc = _account()
        s = acc.account_summary()
        assert "total_annual_mwh" in s and "hv_sites" in s

    def test_portfolio_total_mwh(self):
        port = MultisitePortfolio()
        port.create_account("A1", "Corp1", BillingFrequency.MONTHLY, "Bob", 100_000)
        acc = port.get("A1")
        acc.add_site("M1", "Site1", "SW1A", SiteCategory.RETAIL_UNIT, 1_000_000.0, 100.0)
        assert port.total_portfolio_mwh() == pytest.approx(1000.0)
