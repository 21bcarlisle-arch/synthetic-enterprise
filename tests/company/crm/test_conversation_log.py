import datetime as dt
import pytest
from company.crm.conversation_log import (
    ConversationOutcome, ConversationTurn, CustomerConversation, ConversationLog
)

DT = dt.datetime


def test_start_conversation():
    log = ConversationLog()
    conv = log.start('C001', 'billing_query', 'phone', DT(2023, 6, 1, 10, 0), 'AGENT01')
    assert conv.is_open
    assert conv.customer_id == 'C001'


def test_add_turns():
    log = ConversationLog()
    conv = log.start('C002', 'tariff_query', 'webchat', DT(2023, 6, 1, 10, 0))
    conv.add_turn('agent', 'Hello, how can I help?', DT(2023, 6, 1, 10, 0))
    conv.add_turn('customer', 'I want to query my bill.', DT(2023, 6, 1, 10, 1))
    assert len(conv.turns) == 2
    assert conv.turns[0].speaker == 'agent'


def test_close_conversation_with_csat():
    log = ConversationLog()
    conv = log.start('C003', 'payment_difficulty', 'phone', DT(2023, 6, 1, 10, 0))
    conv.close(DT(2023, 6, 1, 10, 20), ConversationOutcome.RESOLVED, csat_score=5)
    assert not conv.is_open
    assert conv.outcome == ConversationOutcome.RESOLVED
    assert conv.csat_score == 5


def test_duration_seconds():
    log = ConversationLog()
    conv = log.start('C004', 'complaint', 'phone', DT(2023, 6, 1, 10, 0))
    conv.close(DT(2023, 6, 1, 10, 15), ConversationOutcome.ESCALATED)
    assert conv.duration_seconds == pytest.approx(900.0)


def test_invalid_csat_raises():
    log = ConversationLog()
    conv = log.start('C005', 'query', 'email', DT(2023, 6, 1, 10, 0))
    with pytest.raises(ValueError):
        conv.close(DT(2023, 6, 1, 10, 5), ConversationOutcome.RESOLVED, csat_score=6)


def test_invalid_nps_raises():
    log = ConversationLog()
    conv = log.start('C006', 'query', 'portal', DT(2023, 6, 1, 10, 0))
    with pytest.raises(ValueError):
        conv.close(DT(2023, 6, 1, 10, 5), ConversationOutcome.RESOLVED, nps_score=11)


def test_avg_csat():
    log = ConversationLog()
    c1 = log.start('C007', 'query', 'phone', DT(2023, 6, 1, 10, 0))
    c2 = log.start('C008', 'query', 'phone', DT(2023, 6, 1, 11, 0))
    c1.close(DT(2023, 6, 1, 10, 15), ConversationOutcome.RESOLVED, csat_score=4)
    c2.close(DT(2023, 6, 1, 11, 15), ConversationOutcome.RESOLVED, csat_score=2)
    assert log.avg_csat() == pytest.approx(3.0)


def test_resolution_rate():
    log = ConversationLog()
    c1 = log.start('C009', 'query', 'phone', DT(2023, 6, 1, 10, 0))
    c2 = log.start('C010', 'query', 'phone', DT(2023, 6, 1, 11, 0))
    c1.close(DT(2023, 6, 1, 10, 15), ConversationOutcome.RESOLVED)
    c2.close(DT(2023, 6, 1, 11, 15), ConversationOutcome.ESCALATED)
    assert log.resolution_rate() == pytest.approx(0.5)


def test_annual_summary_keys():
    log = ConversationLog()
    c = log.start('C011', 'query', 'phone', DT(2023, 6, 1, 10, 0))
    c.close(DT(2023, 6, 1, 10, 10), ConversationOutcome.RESOLVED, csat_score=5, nps_score=9)
    s = log.annual_summary()
    assert 'total_conversations' in s
    assert 'avg_csat' in s
    assert 'resolution_rate' in s
    assert s['by_outcome']['resolved'] == 1
