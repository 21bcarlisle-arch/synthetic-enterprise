import pytest
from company.regulatory.seg_book import (
    SEGTechnology,
    SEGContract,
    SEGPayment,
    SEGBook,
)


def _contract(cid="C1", mpan="M001", tech=SEGTechnology.SOLAR_PV, rate=5.0, start="2022-01-01", end=None):
    return SEGContract(customer_id=cid, mpan=mpan, technology=tech,
                       rate_p_per_kwh=rate, contract_start=start, contract_end=end)


def _payment(cid="C1", period_start="2022-06-01", period_end="2022-07-01", kwh=200.0, rate=5.0):
    return SEGPayment(customer_id=cid, period_start=period_start,
                      period_end=period_end, export_kwh=kwh, rate_p_per_kwh=rate)


class TestSEGContract:
    def test_is_active_when_no_end(self):
        c = _contract()
        assert c.is_active is True

    def test_is_not_active_when_ended(self):
        c = _contract(end="2023-01-01")
        assert c.is_active is False

    def test_frozen(self):
        c = _contract()
        with pytest.raises((AttributeError, TypeError)):
            c.rate_p_per_kwh = 99.0


class TestSEGPayment:
    def test_payment_gbp_calculation(self):
        p = _payment(kwh=200.0, rate=5.0)
        # 200 * 5 / 100 = 10.0
        assert p.payment_gbp == pytest.approx(10.0)

    def test_payment_gbp_2022_rate(self):
        p = _payment(kwh=1000.0, rate=7.5)
        assert p.payment_gbp == pytest.approx(75.0)

    def test_frozen(self):
        p = _payment()
        with pytest.raises((AttributeError, TypeError)):
            p.export_kwh = 999.0


class TestSEGBook:
    def test_seg_rate_known_year(self):
        book = SEGBook()
        assert book.seg_rate_for_year(2022) == pytest.approx(7.5)

    def test_seg_rate_fallback_unknown_year(self):
        book = SEGBook()
        rate = book.seg_rate_for_year(2030)
        assert isinstance(rate, float) and rate > 0

    def test_register_contract(self):
        book = SEGBook()
        c = book.register_contract(_contract())
        assert len(book.active_contracts()) == 1

    def test_terminate_contract(self):
        book = SEGBook()
        book.register_contract(_contract(mpan="M001"))
        result = book.terminate_contract("M001", "2023-01-01")
        assert result is not None
        assert result.is_active is False
        assert len(book.active_contracts()) == 0

    def test_terminate_unknown_mpan_returns_none(self):
        book = SEGBook()
        assert book.terminate_contract("UNKNOWN", "2023-01-01") is None

    def test_record_payment(self):
        book = SEGBook()
        book.record_payment(_payment(kwh=300.0, rate=5.0))
        assert book.total_paid_gbp() == pytest.approx(15.0)

    def test_payments_for_customer(self):
        book = SEGBook()
        book.record_payment(_payment(cid="C1"))
        book.record_payment(_payment(cid="C2"))
        assert len(book.payments_for_customer("C1")) == 1

    def test_payments_for_year(self):
        book = SEGBook()
        book.record_payment(_payment(period_start="2022-01-01"))
        book.record_payment(_payment(period_start="2023-01-01"))
        assert len(book.payments_for_year(2022)) == 1
        assert len(book.payments_for_year(2023)) == 1

    def test_total_paid_gbp_by_year(self):
        book = SEGBook()
        book.record_payment(_payment(kwh=200.0, rate=5.0, period_start="2022-06-01"))
        book.record_payment(_payment(kwh=100.0, rate=5.0, period_start="2023-06-01"))
        assert book.total_paid_gbp(2022) == pytest.approx(10.0)
        assert book.total_paid_gbp(2023) == pytest.approx(5.0)

    def test_total_export_kwh(self):
        book = SEGBook()
        book.record_payment(_payment(kwh=200.0))
        book.record_payment(_payment(kwh=150.0))
        assert book.total_export_kwh() == pytest.approx(350.0)

    def test_seg_summary_keys(self):
        book = SEGBook()
        s = book.seg_summary()
        for k in ("active_contracts", "total_contracts", "total_payments",
                  "total_export_kwh", "total_paid_gbp", "mean_rate_p_per_kwh"):
            assert k in s

    def test_seg_summary_empty(self):
        book = SEGBook()
        s = book.seg_summary()
        assert s["total_payments"] == 0
        assert s["mean_rate_p_per_kwh"] == 0.0

    def test_seg_2022_crisis_rate_higher_than_2020(self):
        book = SEGBook()
        assert book.seg_rate_for_year(2022) > book.seg_rate_for_year(2020)

    def test_active_contracts_excludes_terminated(self):
        book = SEGBook()
        book.register_contract(_contract(mpan="M001"))
        book.register_contract(_contract(mpan="M002"))
        book.terminate_contract("M001", "2023-01-01")
        assert len(book.active_contracts()) == 1
