# Increment 3: the legs of tests/company/test_phase_ie_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IE: deeper coverage for solr_intake, risk_appetite, renewals_book."""
import datetime as dt
import pytest


# ===== renewals_book =====
from company.crm.renewals_book import (
    RenewalsBook, RenewalOutcome, OfferType
)

def _rb():
    book = RenewalsBook()
    book.add("C1","resi",dt.date(2022,12,31),RenewalOutcome.RENEWED,
             OfferType.BETTER_TARIFF,28.0,12,was_outbound_contact=True)
    book.add("C2","resi",dt.date(2022,12,31),RenewalOutcome.SWITCHED_AWAY,
             OfferType.SAME_TARIFF,31.0,12,was_outbound_contact=False)
    book.add("C3","resi",dt.date(2022,12,31),RenewalOutcome.RENEWED,
             OfferType.SAME_TARIFF,30.0,12,was_outbound_contact=False)
    book.add("C4","resi",dt.date(2022,12,31),RenewalOutcome.MOVED_OUT,None,None,None)
    return book

class TestRenewalsBookExpanded:
    def test_accepted_property(self):
        book = _rb()
        r = book._records[0]
        assert r.accepted

    def test_not_accepted_switched_away(self):
        book = _rb()
        r = book._records[1]
        assert not r.accepted

    def test_renewal_rate_excludes_moved_out(self):
        book = _rb()
        rate = book.renewal_rate(2022)
        # C1 renewed, C2 switched, C3 renewed, C4 excluded -> 2/3 = 66.7%
        assert rate == pytest.approx(66.7, rel=0.01)

    def test_lapse_rate_complement(self):
        book = _rb()
        assert book.lapse_rate(2022) == pytest.approx(100 - book.renewal_rate(2022), rel=0.01)

    def test_renewal_rate_none_for_empty_year(self):
        book = _rb()
        assert book.renewal_rate(2020) is None

    def test_outbound_lift_positive(self):
        book = _rb()
        # outbound: C1 = 1/1 = 100%; inbound: C2=0, C3=1, C4=0 -> 1/3 = 33.3%; lift = 66.7%
        lift = book.outbound_lift(2022)
        assert lift == pytest.approx(66.7, rel=0.01)

    def test_by_offer_type_keys(self):
        book = _rb()
        by_ot = book.by_offer_type(2022)
        assert "better_tariff" in by_ot and "same_tariff" in by_ot

    def test_by_offer_type_renewal_rate(self):
        book = _rb()
        by_ot = book.by_offer_type(2022)
        # better_tariff: 1 total, 1 renewed = 100%
        assert by_ot["better_tariff"]["renewal_rate"] == pytest.approx(100.0)

    def test_annual_summary_keys(self):
        book = _rb()
        s = book.annual_summary(2022)
        assert "renewal_rate_pct" in s and "by_offer_type" in s

    def test_segment_filter(self):
        book = _rb()
        # All are resi; filtering by sme gives None
        assert book.renewal_rate(2022,"sme") is None
