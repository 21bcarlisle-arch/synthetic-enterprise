"""Phase HS: coverage expansion for gas_interruption, solr_intake, ee_obligation_tracker."""
import datetime as dt
import pytest


# ===== solr_intake =====
from company.crm.solr_intake import (
    SoLRIntakeStatus, SoLRBatch, SoLRCustomer, SoLRBook
)

class TestSoLRBookExpanded:
    def _book(self):
        book = SoLRBook("US01")
        book.register_batch("B1","FailedCo",dt.date(2022,1,15),100)
        return book

    def test_register_batch_returns_batch(self):
        book = self._book()
        b = book._batches["B1"]
        assert b.failed_supplier == "FailedCo"
        assert b.customer_count == 100

    def test_batch_not_priced_above_cap_by_default(self):
        book = self._book()
        assert not book._batches["B1"].is_priced_above_cap

    def test_batch_above_cap(self):
        book = SoLRBook("US01")
        book.register_batch("B2","X",dt.date(2022,1,1),50, deemed_tariff_rate_pct_above_cap=5.0)
        assert book._batches["B2"].is_priced_above_cap

    def test_add_customer(self):
        book = self._book()
        c = book.add_customer("C1","B1","M1","resi")
        assert c.status == SoLRIntakeStatus.NOTIFIED
        assert not c.is_retained

    def test_mark_contacted(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        c = book.mark_contacted("C1",dt.date(2022,1,17))
        assert c.status == SoLRIntakeStatus.CONTACTED

    def test_mark_onboarded(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        c = book.mark_onboarded("C1",dt.date(2022,1,20))
        assert c.is_retained
        assert c.status == SoLRIntakeStatus.ONBOARDED

    def test_mark_switched_away(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        c = book.mark_switched_away("C1",dt.date(2022,2,1))
        assert c.status == SoLRIntakeStatus.SWITCHED_AWAY

    def test_retention_rate(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        book.add_customer("C2","B1","M2","resi")
        book.mark_onboarded("C1",dt.date(2022,1,20))
        assert book.retention_rate("B1") == pytest.approx(50.0)

    def test_contact_rate(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        book.add_customer("C2","B1","M2","resi")
        book.mark_contacted("C1",dt.date(2022,1,17))
        book.mark_onboarded("C2",dt.date(2022,1,20))
        assert book.contact_rate("B1") == pytest.approx(100.0)

    def test_batch_summary_keys(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        s = book.batch_summary("B1")
        assert "retention_rate_pct" in s and "actual_customers_received" in s
