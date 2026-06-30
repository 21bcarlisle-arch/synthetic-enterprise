"""Tests for Wholesale Credit Exposure Register (Phase DY)."""
import pytest
from company.trading.wholesale_credit_exposure import (
    CounterpartyType, ClearingStatus, CounterpartyCreditRating,
    WholesaleCreditRecord, WholesaleCreditExposureRegister,
    _CREDIT_LIMIT_BY_RATING, _CLEARED_EXPOSURE_HAIRCUT,
)


def make_record(cid="CP1", ctype=CounterpartyType.MAJOR_BANK,
                rating=CounterpartyCreditRating.A,
                clearing=ClearingStatus.BILATERAL_ISDA,
                gross_mtm=500_000.0, collateral=100_000.0,
                limit_override=None):
    return WholesaleCreditRecord(
        counterparty_id=cid,
        counterparty_type=ctype,
        credit_rating=rating,
        clearing_status=clearing,
        gross_mtm_gbp=gross_mtm,
        collateral_held_gbp=collateral,
        credit_limit_override_gbp=limit_override,
    )


@pytest.fixture
def reg():
    return WholesaleCreditExposureRegister()


class TestWholesaleCreditRecord:
    def test_net_exposure_bilateral(self):
        r = make_record(gross_mtm=500_000, collateral=100_000)
        # bilateral: no haircut
        assert r.net_exposure_gbp == pytest.approx(400_000.0)

    def test_net_exposure_cleared_haircut(self):
        r = make_record(gross_mtm=500_000, collateral=100_000,
                        clearing=ClearingStatus.CLEARED_CCP)
        # CCP: (500k - 100k) * 0.1 = 40k
        assert r.net_exposure_gbp == pytest.approx(40_000.0)

    def test_net_exposure_never_negative(self):
        r = make_record(gross_mtm=100_000, collateral=500_000)
        assert r.net_exposure_gbp == pytest.approx(0.0)

    def test_credit_limit_from_rating(self):
        r = make_record(rating=CounterpartyCreditRating.A)
        assert r.credit_limit_gbp == pytest.approx(2_000_000.0)

    def test_credit_limit_override(self):
        r = make_record(limit_override=750_000.0)
        assert r.credit_limit_gbp == pytest.approx(750_000.0)

    def test_utilisation_pct(self):
        r = make_record(gross_mtm=200_000, collateral=0,
                        rating=CounterpartyCreditRating.A)  # limit = 2M
        assert r.utilisation_pct == pytest.approx(10.0)

    def test_is_limit_breached_false(self):
        r = make_record(gross_mtm=500_000, collateral=0,
                        rating=CounterpartyCreditRating.AAA)  # limit = 5M
        assert not r.is_limit_breached

    def test_is_limit_breached_true(self):
        r = make_record(gross_mtm=2_000_000, collateral=0,
                        rating=CounterpartyCreditRating.BB_OR_LOWER)  # limit = 250k
        assert r.is_limit_breached

    def test_headroom(self):
        r = make_record(gross_mtm=200_000, collateral=0,
                        rating=CounterpartyCreditRating.A)  # limit=2M
        assert r.headroom_gbp == pytest.approx(1_800_000.0)

    def test_headroom_zero_when_breached(self):
        r = make_record(gross_mtm=5_000_000, collateral=0,
                        rating=CounterpartyCreditRating.UNRATED)  # limit=100k
        assert r.headroom_gbp == pytest.approx(0.0)


class TestWholesaleCreditExposureRegister:
    def test_register_and_get(self, reg):
        r = make_record()
        reg.register(r)
        assert reg.get("CP1") is r

    def test_get_missing(self, reg):
        assert reg.get("MISSING") is None

    def test_all_records(self, reg):
        reg.register(make_record("CP1"))
        reg.register(make_record("CP2"))
        assert len(reg.all_records()) == 2

    def test_limit_breaches(self, reg):
        reg.register(make_record("CP1", gross_mtm=5_000_000,
                                 rating=CounterpartyCreditRating.UNRATED))  # breached
        reg.register(make_record("CP2", gross_mtm=100_000,
                                 rating=CounterpartyCreditRating.AAA))  # ok
        assert len(reg.limit_breaches()) == 1

    def test_cleared_vs_bilateral(self, reg):
        reg.register(make_record("CP1", clearing=ClearingStatus.CLEARED_CCP))
        reg.register(make_record("CP2", clearing=ClearingStatus.BILATERAL_ISDA))
        assert len(reg.cleared_records()) == 1
        assert len(reg.bilateral_records()) == 1

    def test_total_net_exposure(self, reg):
        reg.register(make_record("CP1", gross_mtm=500_000, collateral=100_000))
        reg.register(make_record("CP2", gross_mtm=300_000, collateral=50_000))
        total = reg.total_net_exposure_gbp()
        assert total == pytest.approx(650_000.0)

    def test_total_collateral(self, reg):
        reg.register(make_record("CP1", collateral=100_000))
        reg.register(make_record("CP2", collateral=50_000))
        assert reg.total_collateral_held_gbp() == pytest.approx(150_000.0)

    def test_largest_exposure(self, reg):
        reg.register(make_record("CP1", gross_mtm=200_000, collateral=0))
        reg.register(make_record("CP2", gross_mtm=800_000, collateral=0))
        largest = reg.largest_exposure()
        assert largest is not None
        assert largest.counterparty_id == "CP2"

    def test_largest_exposure_empty(self, reg):
        assert reg.largest_exposure() is None

    def test_constants(self):
        assert _CREDIT_LIMIT_BY_RATING[CounterpartyCreditRating.AAA] == 5_000_000.0
        assert _CLEARED_EXPOSURE_HAIRCUT == pytest.approx(0.10)

    def test_summary_string(self, reg):
        reg.register(make_record())
        s = reg.credit_exposure_summary()
        assert "Wholesale Credit Exposure" in s
        assert "ISDA" in s
