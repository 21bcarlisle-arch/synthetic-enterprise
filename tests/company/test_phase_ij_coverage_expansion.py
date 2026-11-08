"""Phase IJ: deeper coverage for campaign_tracker, marketing_budget, acquisition_cohort."""
import datetime as dt
import pytest

# ===== campaign_tracker =====
from company.crm.campaign_tracker import (
    CampaignTracker, CampaignType, ContactOutcome, ContactChannel
)


def _tracker():
    t = CampaignTracker()
    t.create_campaign("C001", CampaignType.RENEWAL_CHASE,
                       dt.date(2022,1,1), 200, ContactChannel.EMAIL)
    t.create_campaign("C002", CampaignType.DEBT_COLLECTION,
                       dt.date(2022,2,1), 50, ContactChannel.PHONE)
    return t


class TestCampaignTracker:
    def test_contact_id_format(self):
        t = _tracker()
        contact = t.record_contact("C001", "CU1", dt.date(2022,1,5),
                                    ContactOutcome.CONVERTED)
        assert contact.contact_id == "CTT-0001"

    def test_is_converted(self):
        t = _tracker()
        c = t.record_contact("C001", "CU1", dt.date(2022,1,5),
                              ContactOutcome.CONVERTED)
        assert c.is_converted

    def test_is_reached_for_callback(self):
        t = _tracker()
        c = t.record_contact("C001", "CU1", dt.date(2022,1,5),
                              ContactOutcome.CALLBACK_ARRANGED)
        assert c.is_reached

    def test_is_not_reached_for_no_answer(self):
        t = _tracker()
        c = t.record_contact("C001", "CU1", dt.date(2022,1,5),
                              ContactOutcome.NO_ANSWER)
        assert not c.is_reached

    def test_conversion_rate(self):
        t = _tracker()
        t.record_contact("C001", "CU1", dt.date(2022,1,5), ContactOutcome.CONVERTED)
        t.record_contact("C001", "CU2", dt.date(2022,1,6), ContactOutcome.REFUSED)
        camp = t.get("C001")
        # 1 converted / 2 reached = 50%
        assert camp.conversion_rate == pytest.approx(50.0)

    def test_contact_rate(self):
        t = _tracker()
        t.record_contact("C001", "CU1", dt.date(2022,1,5), ContactOutcome.CONVERTED)
        t.record_contact("C001", "CU2", dt.date(2022,1,6), ContactOutcome.NO_ANSWER)
        camp = t.get("C001")
        # 1 reached out of 2 total = 50%
        assert camp.contact_rate == pytest.approx(50.0)

    def test_active_campaign_before_close(self):
        t = _tracker()
        active = t.active_campaigns()
        assert len(active) == 2

    def test_close_campaign_removes_from_active(self):
        t = _tracker()
        t.close_campaign("C001", dt.date(2022,3,31))
        active = t.active_campaigns()
        assert len(active) == 1

    def test_campaigns_by_type(self):
        t = _tracker()
        debt = t.campaigns_by_type(CampaignType.DEBT_COLLECTION)
        assert len(debt) == 1

    def test_summary_keys(self):
        t = _tracker()
        s = t.get("C001").summary()
        assert "conversion_rate_pct" in s and "contact_rate_pct" in s and "is_active" in s


# ===== acquisition_cohort =====
from company.crm.acquisition_cohort import (
    AcquisitionCohort, AcquisitionChannel
)


def _cohort():
    c = AcquisitionCohort("COH-2022-01", 2022, 1, AcquisitionChannel.PRICE_COMPARISON)
    c.add_customer("CU1", dt.date(2022,1,15), 150.0, 1200.0)
    c.add_customer("CU2", dt.date(2022,1,20), 200.0, 1800.0)
    c.add_customer("CU3", dt.date(2022,2,1), 120.0, 960.0)
    return c


class TestAcquisitionCohort:
    def test_lifetime_months_active(self):
        c = _cohort()
        months = c.customers[0].lifetime_months(dt.date(2023,1,15))
        # 365 days / 30.4375 ≈ 12.0
        assert months == pytest.approx(12.0, abs=0.5)

    def test_lifetime_revenue_gbp(self):
        c = _cohort()
        cu1 = c.customers[0]
        months = cu1.lifetime_months(dt.date(2023,1,15))
        expected = round(1200/12 * months, 2)
        assert cu1.lifetime_revenue_gbp(dt.date(2023,1,15)) == pytest.approx(expected, rel=0.01)

    def test_net_clv_subtracts_cac(self):
        c = _cohort()
        cu1 = c.customers[0]
        clv = cu1.net_clv_gbp(dt.date(2023,1,15))
        rev = cu1.lifetime_revenue_gbp(dt.date(2023,1,15))
        assert clv == pytest.approx(rev - 150.0, rel=0.01)

    def test_churn_marks_inactive(self):
        c = _cohort()
        c.churn_customer("CU1", dt.date(2022,7,1))
        assert not c.customers[0].is_active

    def test_retention_rate_after_churn(self):
        c = _cohort()
        c.churn_customer("CU1", dt.date(2022,7,1))
        assert c.retention_rate_pct() == pytest.approx(200/3, abs=1.0)

    def test_total_acquisition_cost(self):
        c = _cohort()
        assert c.total_acquisition_cost_gbp() == pytest.approx(470.0)

    def test_avg_net_clv(self):
        c = _cohort()
        as_of = dt.date(2023,1,15)
        avg = c.avg_net_clv_gbp(as_of)
        expected = sum(cu.net_clv_gbp(as_of) for cu in c.customers) / 3
        assert avg == pytest.approx(expected, rel=0.01)

    def test_payback_months(self):
        c = _cohort()
        pm = c.payback_months(dt.date(2023,1,15))
        avg_rev_per_month = (1200+1800+960)/3/12
        avg_cac = 470/3
        assert pm == pytest.approx(avg_cac / avg_rev_per_month, abs=0.5)

    def test_cohort_summary_keys(self):
        c = _cohort()
        s = c.cohort_summary(dt.date(2023,1,15))
        assert "payback_months" in s and "avg_net_clv_gbp" in s

    def test_active_count(self):
        c = _cohort()
        c.churn_customer("CU2", dt.date(2022,9,1))
        assert c.active_count() == 2
