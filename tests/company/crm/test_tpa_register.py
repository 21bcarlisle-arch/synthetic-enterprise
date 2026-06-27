import datetime as dt
import pytest
from company.crm.tpa_register import (
    TPARecord, TPAScope, TPARelationship, TPAStatus, TPARegister,
)


def make_record(account_id="A1", ref="TPA001",
                rel=TPARelationship.ENERGY_ADVISOR,
                scope=TPAScope.VIEW_ONLY,
                granted=dt.date(2023, 1, 1),
                expiry=dt.date(2024, 1, 1),
                name="Citizens Advice",
                status=TPAStatus.ACTIVE):
    return TPARecord(
        account_id=account_id, tpa_reference=ref,
        relationship=rel, scope=scope,
        granted_date=granted, expiry_date=expiry,
        tpa_name=name, status=status,
    )


class TestTPARecord:
    def test_is_active_within_dates(self):
        r = make_record(granted=dt.date(2023, 1, 1), expiry=dt.date(2024, 1, 1))
        assert r.is_active(dt.date(2023, 6, 1)) is True

    def test_is_active_false_after_expiry(self):
        r = make_record(expiry=dt.date(2023, 12, 31))
        assert r.is_active(dt.date(2024, 1, 15)) is False

    def test_is_active_false_revoked(self):
        r = make_record(status=TPAStatus.REVOKED)
        assert r.is_active(dt.date(2023, 6, 1)) is False

    def test_is_active_indefinite_no_expiry(self):
        r = make_record(expiry=None)
        assert r.is_active(dt.date(2030, 1, 1)) is True

    def test_has_billing_access_billing_scope(self):
        r = make_record(scope=TPAScope.BILLING_MANAGEMENT)
        assert r.has_billing_access(dt.date(2023, 6, 1)) is True

    def test_has_billing_access_false_view_only(self):
        r = make_record(scope=TPAScope.VIEW_ONLY)
        assert r.has_billing_access(dt.date(2023, 6, 1)) is False

    def test_has_billing_access_full_authority(self):
        r = make_record(scope=TPAScope.FULL_AUTHORITY)
        assert r.has_billing_access(dt.date(2023, 6, 1)) is True

    def test_has_full_authority(self):
        r = make_record(scope=TPAScope.FULL_AUTHORITY)
        assert r.has_full_authority(dt.date(2023, 6, 1)) is True

    def test_has_full_authority_false_billing(self):
        r = make_record(scope=TPAScope.BILLING_MANAGEMENT)
        assert r.has_full_authority(dt.date(2023, 6, 1)) is False

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.account_id = "X"


class TestTPARegister:
    def test_grant_authority(self):
        reg = TPARegister()
        reg.grant_authority(make_record())
        assert len(reg.all_active_tpas(dt.date(2023, 6, 1))) == 1

    def test_revoke(self):
        reg = TPARegister()
        reg.grant_authority(make_record(ref="T1"))
        result = reg.revoke("T1")
        assert result.status == TPAStatus.REVOKED
        assert len(reg.all_active_tpas(dt.date(2023, 6, 1))) == 0

    def test_expire(self):
        reg = TPARegister()
        reg.grant_authority(make_record(ref="T1"))
        result = reg.expire("T1")
        assert result.status == TPAStatus.EXPIRED

    def test_active_tpas_for_account(self):
        reg = TPARegister()
        reg.grant_authority(make_record(account_id="A1", ref="T1"))
        reg.grant_authority(make_record(account_id="A2", ref="T2"))
        assert len(reg.active_tpas_for_account("A1", dt.date(2023, 6, 1))) == 1

    def test_expiring_soon(self):
        reg = TPARegister()
        reg.grant_authority(make_record(ref="T1", expiry=dt.date(2023, 6, 20)))
        reg.grant_authority(make_record(ref="T2", expiry=dt.date(2023, 12, 31)))
        expiring = reg.expiring_soon(dt.date(2023, 6, 1), within_days=30)
        assert len(expiring) == 1

    def test_power_of_attorney_accounts(self):
        reg = TPARegister()
        reg.grant_authority(make_record(account_id="A1", ref="T1",
                                        rel=TPARelationship.POWER_OF_ATTORNEY,
                                        expiry=None))
        reg.grant_authority(make_record(account_id="A2", ref="T2",
                                        rel=TPARelationship.CARER))
        poa = reg.power_of_attorney_accounts(dt.date(2023, 6, 1))
        assert poa == ["A1"]

    def test_update_raises_not_found(self):
        reg = TPARegister()
        with pytest.raises(ValueError):
            reg.revoke("MISSING")

    def test_summary_keys(self):
        reg = TPARegister()
        reg.grant_authority(make_record(scope=TPAScope.FULL_AUTHORITY, expiry=None))
        s = reg.tpa_summary(dt.date(2023, 6, 1))
        for k in ("total_records", "active", "full_authority", "power_of_attorney"):
            assert k in s

    def test_summary_full_authority_count(self):
        reg = TPARegister()
        reg.grant_authority(make_record(ref="T1", scope=TPAScope.FULL_AUTHORITY, expiry=None))
        reg.grant_authority(make_record(ref="T2", scope=TPAScope.VIEW_ONLY, expiry=None))
        s = reg.tpa_summary(dt.date(2023, 6, 1))
        assert s["full_authority"] == 1
