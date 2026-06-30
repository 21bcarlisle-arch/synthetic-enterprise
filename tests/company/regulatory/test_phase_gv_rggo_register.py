import datetime as dt
import pytest
from company.regulatory.rggo_register import (
    RGGOStatus, BiomethaneSource, RGGORecord, RGGORegister, redemption_deadline_for_year,
)

ISSUE = dt.date(2024, 4, 1)
VALID_TO = dt.date(2025, 3, 31)
AS_OF = dt.date(2024, 10, 1)
CERT = "RGGO-GB-2024-001234"
PRODUCER = "Green Biogas Ltd"


def make_record(status=RGGOStatus.ISSUED, volume=500.0):
    return RGGORecord(
        record_id="RGGO-000001", certificate_ref=CERT,
        issue_date=ISSUE, valid_to=VALID_TO, volume_mwh=volume,
        source=BiomethaneSource.FOOD_WASTE, producer_name=PRODUCER, status=status)


class TestRGGORecord:
    def test_is_available_issued(self):
        assert make_record().is_available
    def test_is_not_available_redeemed(self):
        assert not make_record(RGGOStatus.REDEEMED).is_available
    def test_is_expired_past_valid_to(self):
        r = make_record()
        assert r.is_expired(VALID_TO + dt.timedelta(days=1))
    def test_is_not_expired_before_valid_to(self):
        assert not make_record().is_expired(AS_OF)
    def test_is_not_expired_when_redeemed(self):
        assert not make_record(RGGOStatus.REDEEMED).is_expired(VALID_TO + dt.timedelta(1))
    def test_is_redeemable_within_dates(self):
        assert make_record().is_redeemable(AS_OF)
    def test_is_not_redeemable_after_valid_to(self):
        assert not make_record().is_redeemable(VALID_TO + dt.timedelta(1))
    def test_is_not_redeemable_when_cancelled(self):
        assert not make_record(RGGOStatus.CANCELLED).is_redeemable(AS_OF)
    def test_rggo_summary(self):
        s = make_record().rggo_summary()
        assert "RGGO-000001" in s and CERT in s and "500.0" in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = RGGOStatus.REDEEMED


class TestRedemptionDeadline:
    def test_redemption_deadline_2024(self):
        assert redemption_deadline_for_year(2024) == dt.date(2025, 3, 31)
    def test_redemption_deadline_2023(self):
        assert redemption_deadline_for_year(2023) == dt.date(2024, 3, 31)


class TestRGGORegister:
    def setup_method(self):
        self.reg = RGGORegister()

    def test_register_rggo_stored(self):
        r = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        assert r.is_available

    def test_auto_id_increments(self):
        r1 = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        r2 = self.reg.register_rggo("RGGO-002", ISSUE, VALID_TO, 200.0,
            BiomethaneSource.SEWAGE_SLUDGE, PRODUCER)
        assert r1.record_id != r2.record_id

    def test_zero_volume_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_rggo(CERT, ISSUE, VALID_TO, 0.0,
                BiomethaneSource.FOOD_WASTE, PRODUCER)

    def test_invalid_dates_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_rggo(CERT, VALID_TO, ISSUE, 500.0,
                BiomethaneSource.FOOD_WASTE, PRODUCER)

    def test_redeem_stored(self):
        r = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        redeemed = self.reg.redeem(r.record_id, AS_OF, "CUST-001")
        assert redeemed.status == RGGOStatus.REDEEMED
        assert redeemed.redeemed_date == AS_OF

    def test_redeem_expired_raises(self):
        r = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        with pytest.raises(ValueError):
            self.reg.redeem(r.record_id, VALID_TO + dt.timedelta(1))

    def test_redeem_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.redeem("RGGO-999999", AS_OF)

    def test_cancel(self):
        r = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        cancelled = self.reg.cancel(r.record_id)
        assert cancelled.status == RGGOStatus.CANCELLED

    def test_expire_stale(self):
        r = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        expired = self.reg.expire_stale(VALID_TO + dt.timedelta(1))
        assert len(expired) == 1 and expired[0].status == RGGOStatus.EXPIRED

    def test_expire_stale_not_expired_yet(self):
        self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        expired = self.reg.expire_stale(AS_OF)
        assert len(expired) == 0

    def test_available_rggo_mwh(self):
        r = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        self.reg.register_rggo("RGGO-002", ISSUE, VALID_TO, 200.0,
            BiomethaneSource.SEWAGE_SLUDGE, PRODUCER)
        self.reg.redeem(r.record_id, AS_OF)
        assert abs(self.reg.available_rggo_mwh(AS_OF) - 200.0) < 1e-9

    def test_redeemed_rggo_mwh(self):
        r = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        self.reg.redeem(r.record_id, AS_OF)
        assert abs(self.reg.redeemed_rggo_mwh() - 500.0) < 1e-9

    def test_by_source(self):
        self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        self.reg.register_rggo("RGGO-002", ISSUE, VALID_TO, 200.0,
            BiomethaneSource.SEWAGE_SLUDGE, PRODUCER)
        assert len(self.reg.by_source(BiomethaneSource.FOOD_WASTE)) == 1

    def test_expiring_before(self):
        self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        self.reg.register_rggo("RGGO-002", ISSUE, dt.date(2026, 3, 31), 200.0,
            BiomethaneSource.SEWAGE_SLUDGE, PRODUCER)
        expiring = self.reg.expiring_before(dt.date(2025, 12, 31))
        assert len(expiring) == 1

    def test_redemption_rate_pct(self):
        r = self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        self.reg.register_rggo("RGGO-002", ISSUE, VALID_TO, 500.0,
            BiomethaneSource.SEWAGE_SLUDGE, PRODUCER)
        self.reg.redeem(r.record_id, AS_OF)
        self.reg.expire_stale(VALID_TO + dt.timedelta(1))
        rate = self.reg.redemption_rate_pct()
        assert rate is not None and abs(rate - 50.0) < 1e-9

    def test_redemption_rate_none_when_no_settled(self):
        self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        assert self.reg.redemption_rate_pct() is None

    def test_rggo_register_summary(self):
        self.reg.register_rggo(CERT, ISSUE, VALID_TO, 500.0,
            BiomethaneSource.FOOD_WASTE, PRODUCER)
        s = self.reg.rggo_register_summary(AS_OF)
        assert "1 certificates" in s

    def test_empty_summary(self):
        s = self.reg.rggo_register_summary(AS_OF)
        assert "0 certificates" in s
