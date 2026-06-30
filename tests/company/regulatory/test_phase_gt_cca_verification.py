import datetime as dt
import pytest
from company.regulatory.cca_verification_register import (
    CCASector, CCAStatus, CCAVerificationRecord, CCAVerificationRegister,
    _CCL_ELECTRICITY_DISCOUNT_PCT, _CCL_GAS_DISCOUNT_PCT,
    _CERTIFICATE_EXPIRY_WARNING_DAYS,
)

ACCOUNT = "ACC-001"
MPAN = "1012345678901"
CERT_REF = "CCA-2024-001234"
VALID_FROM = dt.date(2024, 1, 1)
VALID_TO = dt.date(2025, 12, 31)
AS_OF = dt.date(2024, 6, 1)


def make_record(status=CCAStatus.ACTIVE):
    return CCAVerificationRecord(
        record_id="CCA-VER-00001", account_id=ACCOUNT, mpan=MPAN,
        sector=CCASector.CHEMICALS, certificate_ref=CERT_REF,
        valid_from=VALID_FROM, valid_to=VALID_TO, status=status)


class TestCCAVerificationRecord:
    def test_is_active(self):
        assert make_record().is_active
    def test_is_not_active_suspended(self):
        assert not make_record(CCAStatus.SUSPENDED).is_active
    def test_is_valid_as_of_within_dates(self):
        assert make_record().is_valid_as_of(AS_OF)
    def test_is_not_valid_before_start(self):
        assert not make_record().is_valid_as_of(dt.date(2023, 12, 31))
    def test_is_not_valid_after_end(self):
        assert not make_record().is_valid_as_of(dt.date(2026, 1, 1))
    def test_is_not_valid_when_suspended(self):
        assert not make_record(CCAStatus.SUSPENDED).is_valid_as_of(AS_OF)
    def test_is_expiring_soon_within_warning(self):
        r = make_record()
        near = VALID_TO - dt.timedelta(days=_CERTIFICATE_EXPIRY_WARNING_DAYS - 1)
        assert r.is_expiring_soon(near)
    def test_is_not_expiring_soon_distant(self):
        r = make_record()
        far = VALID_TO - dt.timedelta(days=_CERTIFICATE_EXPIRY_WARNING_DAYS + 1)
        assert not r.is_expiring_soon(far)
    def test_is_not_expiring_soon_when_suspended(self):
        r = make_record(CCAStatus.SUSPENDED)
        near = VALID_TO - dt.timedelta(days=_CERTIFICATE_EXPIRY_WARNING_DAYS - 1)
        assert not r.is_expiring_soon(near)
    def test_electricity_discount_when_active(self):
        assert make_record().electricity_ccl_discount_pct() == _CCL_ELECTRICITY_DISCOUNT_PCT
    def test_electricity_discount_zero_when_suspended(self):
        assert make_record(CCAStatus.SUSPENDED).electricity_ccl_discount_pct() == 0.0
    def test_gas_discount_when_active(self):
        assert make_record().gas_ccl_discount_pct() == _CCL_GAS_DISCOUNT_PCT
    def test_gas_discount_zero_when_revoked(self):
        assert make_record(CCAStatus.REVOKED).gas_ccl_discount_pct() == 0.0
    def test_cca_summary(self):
        s = make_record().cca_summary()
        assert "CCA-VER-00001" in s and ACCOUNT in s and CERT_REF in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = CCAStatus.SUSPENDED


class TestCCAVerificationRegister:
    def setup_method(self):
        self.reg = CCAVerificationRegister()

    def test_register_certificate_stored(self):
        r = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        assert r.is_active

    def test_auto_id_increments(self):
        r1 = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        r2 = self.reg.register_certificate("ACC-002", "MPAN-002", CCASector.METALS,
            "CCA-2024-002", VALID_FROM, VALID_TO)
        assert r1.record_id != r2.record_id

    def test_invalid_dates_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
                CERT_REF, VALID_TO, VALID_FROM)

    def test_suspend(self):
        r = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        susp = self.reg.suspend(r.record_id, AS_OF)
        assert susp.status == CCAStatus.SUSPENDED and susp.suspension_date == AS_OF

    def test_revoke(self):
        r = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        rev = self.reg.revoke(r.record_id)
        assert rev.status == CCAStatus.REVOKED

    def test_mark_expired(self):
        r = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        exp = self.reg.mark_expired(r.record_id)
        assert exp.status == CCAStatus.EXPIRED

    def test_mark_pending_renewal(self):
        r = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        pend = self.reg.mark_pending_renewal(r.record_id)
        assert pend.status == CCAStatus.PENDING_RENEWAL

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.revoke("CCA-VER-99999")

    def test_active_certificates(self):
        r = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        self.reg.suspend(r.record_id, AS_OF)
        self.reg.register_certificate("ACC-002", "MPAN-002", CCASector.METALS,
            "CCA-002", VALID_FROM, VALID_TO)
        assert len(self.reg.active_certificates()) == 1

    def test_valid_for_account(self):
        self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        rec = self.reg.valid_for_account(ACCOUNT, AS_OF)
        assert rec is not None and rec.account_id == ACCOUNT

    def test_valid_for_account_none_when_expired(self):
        r = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        self.reg.mark_expired(r.record_id)
        assert self.reg.valid_for_account(ACCOUNT, AS_OF) is None

    def test_valid_for_account_none_when_missing(self):
        assert self.reg.valid_for_account("UNKNOWN", AS_OF) is None

    def test_expiring_soon(self):
        self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        near = VALID_TO - dt.timedelta(days=30)
        assert len(self.reg.expiring_soon(near)) == 1

    def test_by_sector(self):
        self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        self.reg.register_certificate("ACC-002", "MPAN-002", CCASector.METALS,
            "CCA-002", VALID_FROM, VALID_TO)
        assert len(self.reg.by_sector(CCASector.CHEMICALS)) == 1

    def test_suspended_certificates(self):
        r = self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        self.reg.suspend(r.record_id, AS_OF)
        assert len(self.reg.suspended_certificates()) == 1

    def test_cca_eligible_mpans(self):
        self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            "CCA-002", dt.date(2025, 1, 1), dt.date(2026, 12, 31))
        mpans = self.reg.cca_eligible_mpans(AS_OF)
        assert MPAN in mpans and len(mpans) == 1

    def test_cca_register_summary(self):
        self.reg.register_certificate(ACCOUNT, MPAN, CCASector.CHEMICALS,
            CERT_REF, VALID_FROM, VALID_TO)
        s = self.reg.cca_register_summary(AS_OF)
        assert "1 certificates" in s and "1 active" in s
