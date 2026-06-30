"""Tests for Marketing Campaign Register (Phase DT)."""
import datetime as dt
import pytest
from company.crm.marketing_campaign_register import (
    CampaignChannel, CampaignStatus, CampaignType,
    MarketingCampaignRecord, MarketingCampaignRegister,
    _DOOR_TO_DOOR_COOLING_OFF_DAYS,
)


@pytest.fixture
def reg():
    return MarketingCampaignRegister()


DATE = dt.date(2024, 4, 1)


def create_campaign(reg, channel=CampaignChannel.EMAIL, ctype=CampaignType.ACQUISITION,
                    budget=5000.0, opt_in=True):
    return reg.create(
        name="Test Campaign",
        channel=channel,
        campaign_type=ctype,
        start_date=DATE,
        budget_gbp=budget,
        opt_in_compliant=opt_in,
    )


def update(reg, cid, sends=1000, responses=50, conversions=10, spend=2000.0):
    return reg.update_performance(cid, sends, responses, conversions, spend)


class TestMarketingCampaignRecord:
    def test_response_rate_pct(self, reg):
        rec = create_campaign(reg)
        reg.update_performance(rec.campaign_id, sends=1000, responses=50,
                               conversions=10, spend_gbp=2000.0)
        updated = reg.get(rec.campaign_id)
        assert updated.response_rate_pct == pytest.approx(5.0)

    def test_conversion_rate_pct(self, reg):
        rec = create_campaign(reg)
        reg.update_performance(rec.campaign_id, sends=1000, responses=50,
                               conversions=20, spend_gbp=2000.0)
        updated = reg.get(rec.campaign_id)
        assert updated.conversion_rate_pct == pytest.approx(2.0)

    def test_cost_per_acquisition(self, reg):
        rec = create_campaign(reg)
        update(reg, rec.campaign_id, conversions=10, spend=2000.0)
        updated = reg.get(rec.campaign_id)
        assert updated.cost_per_acquisition_gbp == pytest.approx(200.0)

    def test_zero_conversions_cpa(self, reg):
        rec = create_campaign(reg)
        update(reg, rec.campaign_id, conversions=0, spend=500.0)
        assert reg.get(rec.campaign_id).cost_per_acquisition_gbp == pytest.approx(0.0)

    def test_budget_utilisation_pct(self, reg):
        rec = create_campaign(reg, budget=5000.0)
        update(reg, rec.campaign_id, spend=2500.0)
        assert reg.get(rec.campaign_id).budget_utilisation_pct == pytest.approx(50.0)

    def test_is_door_to_door(self, reg):
        rec = create_campaign(reg, channel=CampaignChannel.DOOR_TO_DOOR)
        assert rec.is_door_to_door

    def test_requires_opt_in_email(self, reg):
        rec = create_campaign(reg, channel=CampaignChannel.EMAIL)
        assert rec.requires_opt_in

    def test_requires_opt_in_sms(self, reg):
        rec = create_campaign(reg, channel=CampaignChannel.SMS)
        assert rec.requires_opt_in

    def test_direct_mail_no_opt_in_required(self, reg):
        rec = create_campaign(reg, channel=CampaignChannel.DIRECT_MAIL)
        assert not rec.requires_opt_in

    def test_draft_initially(self, reg):
        rec = create_campaign(reg)
        assert rec.status == CampaignStatus.DRAFT


class TestMarketingCampaignRegister:
    def test_unique_ids(self, reg):
        r1 = create_campaign(reg)
        r2 = create_campaign(reg)
        assert r1.campaign_id != r2.campaign_id

    def test_active_campaigns(self, reg):
        r1 = create_campaign(reg)
        r2 = create_campaign(reg)
        update(reg, r1.campaign_id)  # sets ACTIVE
        assert len(reg.active_campaigns()) == 1

    def test_non_compliant_campaigns(self, reg):
        r1 = create_campaign(reg, channel=CampaignChannel.EMAIL, opt_in=False)
        r2 = create_campaign(reg, channel=CampaignChannel.EMAIL, opt_in=True)
        r3 = create_campaign(reg, channel=CampaignChannel.DIRECT_MAIL, opt_in=False)
        # r3 doesn't require opt-in so not counted as non-compliant
        non_comp = reg.non_compliant_campaigns()
        assert len(non_comp) == 1
        assert non_comp[0].campaign_id == r1.campaign_id

    def test_by_channel(self, reg):
        create_campaign(reg, channel=CampaignChannel.EMAIL)
        create_campaign(reg, channel=CampaignChannel.SMS)
        create_campaign(reg, channel=CampaignChannel.EMAIL)
        by_ch = reg.by_channel()
        assert by_ch[CampaignChannel.EMAIL.value] == 2
        assert by_ch[CampaignChannel.SMS.value] == 1

    def test_total_spend(self, reg):
        r1 = create_campaign(reg)
        r2 = create_campaign(reg)
        update(reg, r1.campaign_id, spend=1000.0)
        update(reg, r2.campaign_id, spend=2000.0)
        assert reg.total_spend_gbp() == pytest.approx(3000.0)

    def test_total_conversions(self, reg):
        r1 = create_campaign(reg)
        r2 = create_campaign(reg)
        update(reg, r1.campaign_id, conversions=10)
        update(reg, r2.campaign_id, conversions=5)
        assert reg.total_conversions() == 15

    def test_best_cpa(self, reg):
        r1 = create_campaign(reg)
        r2 = create_campaign(reg)
        update(reg, r1.campaign_id, conversions=10, spend=1000.0)  # £100/conv
        update(reg, r2.campaign_id, conversions=10, spend=500.0)   # £50/conv
        best = reg.best_cpa()
        assert best is not None
        assert best.campaign_id == r2.campaign_id

    def test_best_cpa_none_when_no_conversions(self, reg):
        create_campaign(reg)
        assert reg.best_cpa() is None

    def test_cooling_off_constant(self):
        assert _DOOR_TO_DOOR_COOLING_OFF_DAYS == 14

    def test_summary_string(self, reg):
        create_campaign(reg)
        s = reg.campaign_summary()
        assert "Marketing Campaign Register" in s
        assert "GDPR" in s
