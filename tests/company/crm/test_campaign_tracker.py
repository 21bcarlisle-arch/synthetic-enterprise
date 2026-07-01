import datetime as dt
import pytest
from company.crm.campaign_tracker import (
    CampaignType, ContactOutcome, ContactChannel, CampaignContact,
    Campaign, CampaignTracker
)


def test_create_campaign():
    t = CampaignTracker()
    c = t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 500,
                          ContactChannel.PHONE)
    assert c.is_active
    assert c.contacts_made == 0
    assert c.conversion_rate is None


def test_record_converted_contact():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                       ContactChannel.PHONE)
    cc = t.record_contact('RCH2022', 'C001', dt.date(2022, 10, 2),
                          ContactOutcome.CONVERTED, 'AGT01')
    assert cc.is_converted
    assert cc.is_reached


def test_no_answer_not_reached():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                       ContactChannel.PHONE)
    cc = t.record_contact('RCH2022', 'C001', dt.date(2022, 10, 2), ContactOutcome.NO_ANSWER)
    assert not cc.is_converted
    assert not cc.is_reached


def test_conversion_rate():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                       ContactChannel.PHONE)
    t.record_contact('RCH2022', 'C001', dt.date(2022, 10, 2), ContactOutcome.CONVERTED)
    t.record_contact('RCH2022', 'C002', dt.date(2022, 10, 2), ContactOutcome.REFUSED)
    t.record_contact('RCH2022', 'C003', dt.date(2022, 10, 2), ContactOutcome.NO_ANSWER)
    c = t.get('RCH2022')
    # reached: C001 + C002 = 2; converted: 1 -> 50%
    assert c.conversion_rate == pytest.approx(50.0)


def test_contact_rate():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.DEBT_COLLECTION, dt.date(2022, 10, 1), 100,
                       ContactChannel.PHONE)
    t.record_contact('RCH2022', 'C001', dt.date(2022, 10, 2), ContactOutcome.CONVERTED)
    t.record_contact('RCH2022', 'C002', dt.date(2022, 10, 2), ContactOutcome.NO_ANSWER)
    c = t.get('RCH2022')
    # total 2, reached 1 -> 50%
    assert c.contact_rate == pytest.approx(50.0)


def test_close_campaign():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                       ContactChannel.EMAIL)
    t.close_campaign('RCH2022', dt.date(2022, 10, 31))
    assert not t.get('RCH2022').is_active
    assert len(t.active_campaigns()) == 0


def test_campaigns_by_type():
    t = CampaignTracker()
    t.create_campaign('RCH1', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                       ContactChannel.PHONE)
    t.create_campaign('DC1', CampaignType.DEBT_COLLECTION, dt.date(2022, 10, 1), 50,
                       ContactChannel.PHONE)
    renewal_campaigns = t.campaigns_by_type(CampaignType.RENEWAL_CHASE)
    assert len(renewal_campaigns) == 1
    assert renewal_campaigns[0].campaign_id == 'RCH1'


def test_summary_dict():
    t = CampaignTracker()
    t.create_campaign('WHD22', CampaignType.WHD_OUTREACH, dt.date(2022, 10, 1), 300,
                       ContactChannel.POST)
    t.record_contact('WHD22', 'C001', dt.date(2022, 10, 5), ContactOutcome.CONVERTED)
    s = t.get('WHD22').summary()
    assert s['campaign_type'] == 'whd_outreach'
    assert s['converted'] == 1
    assert 'contact_rate_pct' in s


# --- Phase KF depth tests ---

def test_campaign_id_stored():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                      ContactChannel.PHONE)
    assert t.get('RCH2022').campaign_id == 'RCH2022'


def test_campaign_type_stored():
    t = CampaignTracker()
    t.create_campaign('DC1', CampaignType.DEBT_COLLECTION, dt.date(2022, 10, 1), 50,
                      ContactChannel.PHONE)
    assert t.get('DC1').campaign_type == CampaignType.DEBT_COLLECTION


def test_channel_stored():
    t = CampaignTracker()
    t.create_campaign('EM1', CampaignType.SURVEY, dt.date(2022, 10, 1), 200,
                      ContactChannel.EMAIL)
    assert t.get('EM1').channel == ContactChannel.EMAIL


def test_conversion_rate_none_when_no_contacts():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                      ContactChannel.PHONE)
    assert t.get('RCH2022').conversion_rate is None


def test_refused_is_reached():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                      ContactChannel.PHONE)
    cc = t.record_contact('RCH2022', 'C001', dt.date(2022, 10, 2), ContactOutcome.REFUSED)
    assert cc.is_reached is True


def test_callback_arranged_is_reached():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                      ContactChannel.PHONE)
    cc = t.record_contact('RCH2022', 'C001', dt.date(2022, 10, 2),
                          ContactOutcome.CALLBACK_ARRANGED)
    assert cc.is_reached is True


def test_contacts_made_count():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                      ContactChannel.PHONE)
    t.record_contact('RCH2022', 'C001', dt.date(2022, 10, 2), ContactOutcome.CONVERTED)
    t.record_contact('RCH2022', 'C002', dt.date(2022, 10, 2), ContactOutcome.REFUSED)
    assert t.get('RCH2022').contacts_made == 2


def test_active_campaigns_excludes_closed():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                      ContactChannel.PHONE)
    t.create_campaign('DC1', CampaignType.DEBT_COLLECTION, dt.date(2022, 10, 1), 50,
                      ContactChannel.PHONE)
    t.close_campaign('DC1', dt.date(2022, 10, 31))
    active = t.active_campaigns()
    assert len(active) == 1
    assert active[0].campaign_id == 'RCH2022'


def test_campaigns_by_type_empty_when_no_match():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                      ContactChannel.PHONE)
    result = t.campaigns_by_type(CampaignType.SURVEY)
    assert result == []


def test_contact_channel_stored():
    t = CampaignTracker()
    t.create_campaign('RCH2022', CampaignType.RENEWAL_CHASE, dt.date(2022, 10, 1), 100,
                      ContactChannel.PHONE)
    cc = t.record_contact('RCH2022', 'C001', dt.date(2022, 10, 2), ContactOutcome.CONVERTED)
    assert cc.channel == ContactChannel.PHONE
