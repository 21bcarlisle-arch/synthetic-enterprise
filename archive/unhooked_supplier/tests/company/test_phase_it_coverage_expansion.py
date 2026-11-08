# Increment 3: the legs of tests/company/test_phase_it_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IT -- Coverage Depth Sprint XVII: contact_centre_metrics, complaint_register, conversation_log."""

import datetime as dt
import unittest

from company.crm.contact_centre_metrics import AgentPerformancePeriod, ContactCentreMetrics
from company.crm.conversation_log import ConversationLog, ConversationOutcome

D1 = dt.date(2024, 1, 1)
D2 = dt.date(2024, 1, 31)

def _agent(calls=100, handle=36000, fcr=80, esc=5, comp=2, csat=4.2):
    return AgentPerformancePeriod(agent_id="A1", period_start=D1, period_end=D2,
        calls_handled=calls, total_handle_time_seconds=handle,
        first_contact_resolutions=fcr, escalations=esc,
        complaints_raised=comp, avg_csat=csat)

class TestAgentPerformancePeriod(unittest.TestCase):
    def test_avg_handle_time_seconds(self):
        a = _agent(calls=100, handle=36000)
        self.assertAlmostEqual(a.avg_handle_time_seconds, 360.0, places=1)

    def test_first_contact_resolution_rate(self):
        a = _agent(calls=100, fcr=75)
        self.assertAlmostEqual(a.first_contact_resolution_rate, 75.0, places=1)

    def test_escalation_rate(self):
        a = _agent(calls=50, esc=5)
        self.assertAlmostEqual(a.escalation_rate, 10.0, places=1)

    def test_complaint_rate(self):
        a = _agent(calls=200, comp=4)
        self.assertAlmostEqual(a.complaint_rate, 2.0, places=1)

    def test_zero_calls_returns_none(self):
        a = _agent(calls=0, handle=0, fcr=0, esc=0, comp=0)
        self.assertIsNone(a.avg_handle_time_seconds)
        self.assertIsNone(a.first_contact_resolution_rate)


class TestContactCentreMetrics(unittest.TestCase):
    def _make(self, total=500, answered=450, abandoned=50, handle=180000, agents=10):
        return ContactCentreMetrics(period_start=D1, period_end=D2,
            total_calls=total, answered_within_sla_seconds=answered,
            abandoned_calls=abandoned, total_handle_time_seconds=handle,
            agents_on_duty=agents)

    def test_abandonment_rate(self):
        m = self._make(total=500, abandoned=50)
        self.assertAlmostEqual(m.abandonment_rate, round(50/550*100, 1), places=1)

    def test_sla_answer_rate(self):
        m = self._make(total=500, answered=450)
        self.assertAlmostEqual(m.sla_answer_rate, 90.0, places=1)

    def test_avg_handle_time_seconds(self):
        m = self._make(total=500, handle=150000)
        self.assertAlmostEqual(m.avg_handle_time_seconds, 300.0, places=1)

    def test_calls_per_agent(self):
        m = self._make(total=500, agents=10)
        self.assertAlmostEqual(m.calls_per_agent, 50.0, places=1)

    def test_summary_keys(self):
        m = self._make()
        s = m.summary()
        for k in ["total_calls", "abandonment_rate", "sla_answer_rate"]:
            self.assertIn(k, s)


class TestConversationLog(unittest.TestCase):
    def _ts(self, s):
        return dt.datetime.fromisoformat(s)

    def test_start_creates_conv_id(self):
        log = ConversationLog()
        c = log.start('CUST1', 'billing_query', 'phone', self._ts('2024-03-01T09:00:00'))
        self.assertEqual(c.conversation_id, 'CONV-00001')

    def test_sequential_ids(self):
        log = ConversationLog()
        c1 = log.start('A', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
        c2 = log.start('B', 'q', 'chat', self._ts('2024-03-01T10:00:00'))
        self.assertEqual(c1.conversation_id, 'CONV-00001')
        self.assertEqual(c2.conversation_id, 'CONV-00002')

    def test_conversation_is_open_before_close(self):
        log = ConversationLog()
        c = log.start('CUST', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
        self.assertTrue(c.is_open)
        self.assertIsNone(c.duration_seconds)

    def test_add_turn_stored(self):
        log = ConversationLog()
        c = log.start('CUST', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
        c.add_turn('agent', 'Hello', self._ts('2024-03-01T09:01:00'))
        self.assertEqual(len(c.turns), 1)

    def test_close_sets_outcome_and_duration(self):
        log = ConversationLog()
        c = log.start('CUST', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
        c.close(self._ts('2024-03-01T09:05:30'), ConversationOutcome.RESOLVED, csat_score=4)
        self.assertFalse(c.is_open)
        self.assertAlmostEqual(c.duration_seconds, 330.0)
        self.assertEqual(c.csat_score, 4)

    def test_invalid_csat_raises(self):
        log = ConversationLog()
        c = log.start('CUST', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
        with self.assertRaises(ValueError):
            c.close(self._ts('2024-03-01T09:05:00'), ConversationOutcome.RESOLVED, csat_score=6)

    def test_invalid_nps_raises(self):
        log = ConversationLog()
        c = log.start('CUST', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
        with self.assertRaises(ValueError):
            c.close(self._ts('2024-03-01T09:05:00'), ConversationOutcome.RESOLVED, nps_score=11)

    def test_conversations_for_customer(self):
        log = ConversationLog()
        log.start('A', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
        log.start('B', 'q', 'phone', self._ts('2024-03-01T10:00:00'))
        log.start('A', 'q', 'chat', self._ts('2024-03-01T11:00:00'))
        self.assertEqual(len(log.conversations_for_customer('A')), 2)

    def test_avg_csat(self):
        log = ConversationLog()
        for score in [4, 5, 3]:
            c = log.start('CUST', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
            c.close(self._ts('2024-03-01T09:05:00'), ConversationOutcome.RESOLVED, csat_score=score)
        self.assertAlmostEqual(log.avg_csat(), 4.0, places=1)

    def test_annual_summary_by_outcome(self):
        log = ConversationLog()
        c1 = log.start('A', 'q', 'phone', self._ts('2024-03-01T09:00:00'))
        c1.close(self._ts('2024-03-01T09:05:00'), ConversationOutcome.RESOLVED)
        c2 = log.start('B', 'q', 'chat', self._ts('2024-03-01T10:00:00'))
        c2.close(self._ts('2024-03-01T10:10:00'), ConversationOutcome.ESCALATED)
        s = log.annual_summary()
        self.assertEqual(s["total_conversations"], 2)
        self.assertEqual(s["by_outcome"].get("resolved", 0), 1)
