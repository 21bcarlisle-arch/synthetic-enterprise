import datetime as dt
import pytest
from company.crm.solr_register import (
    SoLRTransferRecord, SoLRStatus, SoLRDesignation, SoLRRegister,
)


def make_record(account_id="A1", supplier="BulbFail",
                transfer=dt.date(2021, 11, 1), credit=120.0,
                status=SoLRStatus.TRANSFERRED, notified=None,
                offered=None, accepted=None):
    return SoLRTransferRecord(
        account_id=account_id,
        original_supplier=supplier,
        transfer_date=transfer,
        credit_balance_claimed_gbp=credit,
        status=status,
        notification_date=notified,
        contract_offer_date=offered,
        contract_accepted_date=accepted,
    )


def make_designation(supplier="AvroCrash", customers=200_000,
                     date=dt.date(2021, 9, 22)):
    return SoLRDesignation(
        designation_date=date,
        ofgem_direction_ref="OFGEM/SOLR/2021/001",
        failed_supplier_name=supplier,
        customers_transferred=customers,
    )


class TestSoLRTransferRecord:
    def test_notification_overdue_false_if_notified(self):
        r = make_record(notified=dt.date(2021, 11, 3))
        assert r.is_notification_overdue(dt.date(2021, 11, 10)) is False

    def test_notification_overdue_false_within_5_days(self):
        r = make_record(transfer=dt.date(2021, 11, 1))
        assert r.is_notification_overdue(dt.date(2021, 11, 4)) is False

    def test_notification_overdue_true_after_5_days(self):
        r = make_record(transfer=dt.date(2021, 11, 1))
        assert r.is_notification_overdue(dt.date(2021, 11, 8)) is True

    def test_contract_offer_overdue_false_if_offered(self):
        r = make_record(offered=dt.date(2021, 11, 20))
        assert r.is_contract_offer_overdue(dt.date(2021, 12, 15)) is False

    def test_contract_offer_overdue_false_within_30_days(self):
        r = make_record(transfer=dt.date(2021, 11, 1))
        assert r.is_contract_offer_overdue(dt.date(2021, 11, 25)) is False

    def test_contract_offer_overdue_true_after_30_days(self):
        r = make_record(transfer=dt.date(2021, 11, 1))
        assert r.is_contract_offer_overdue(dt.date(2021, 12, 10)) is True

    def test_contract_offer_overdue_false_integrated(self):
        r = make_record(status=SoLRStatus.INTEGRATED)
        assert r.is_contract_offer_overdue(dt.date(2022, 1, 1)) is False

    def test_in_solr_billing_period_true(self):
        r = make_record(transfer=dt.date(2021, 11, 1))
        assert r.is_in_solr_billing_period(dt.date(2022, 1, 1)) is True

    def test_in_solr_billing_period_false_after_90_days(self):
        r = make_record(transfer=dt.date(2021, 11, 1))
        assert r.is_in_solr_billing_period(dt.date(2022, 3, 1)) is False

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.account_id = "X"


class TestSoLRRegister:
    def test_record_designation(self):
        reg = SoLRRegister()
        d = make_designation()
        reg.record_designation(d)
        assert reg.solr_summary()["designations"] == 1

    def test_record_transfer(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record())
        assert reg.solr_summary()["total_transferred"] == 1

    def test_notify(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1"))
        result = reg.notify("A1", dt.date(2021, 11, 3))
        assert result.status == SoLRStatus.NOTIFIED
        assert result.notification_date == dt.date(2021, 11, 3)

    def test_offer_contract(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1"))
        result = reg.offer_contract("A1", dt.date(2021, 11, 20))
        assert result.status == SoLRStatus.CONTRACT_OFFERED

    def test_accept_contract(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1"))
        result = reg.accept_contract("A1", dt.date(2021, 11, 25))
        assert result.status == SoLRStatus.CONTRACT_ACCEPTED

    def test_integrate(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1"))
        result = reg.integrate("A1")
        assert result.status == SoLRStatus.INTEGRATED

    def test_active_excludes_integrated(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1"))
        reg.record_transfer(make_record(account_id="A2"))
        reg.integrate("A1")
        assert len(reg.active_transfers()) == 1

    def test_overdue_notifications(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1", transfer=dt.date(2021, 11, 1)))
        assert len(reg.overdue_notifications(dt.date(2021, 11, 8))) == 1
        assert len(reg.overdue_notifications(dt.date(2021, 11, 4))) == 0

    def test_overdue_contract_offers(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1", transfer=dt.date(2021, 11, 1)))
        assert len(reg.overdue_contract_offers(dt.date(2021, 12, 10))) == 1
        assert len(reg.overdue_contract_offers(dt.date(2021, 11, 20))) == 0

    def test_in_solr_billing_period(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1", transfer=dt.date(2021, 11, 1)))
        assert len(reg.in_solr_billing_period(dt.date(2022, 1, 1))) == 1
        assert len(reg.in_solr_billing_period(dt.date(2022, 3, 1))) == 0

    def test_total_credit_claimed(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1", credit=120.0))
        reg.record_transfer(make_record(account_id="A2", credit=80.0))
        assert reg.total_credit_claimed_gbp() == 200.0

    def test_transfers_from_supplier(self):
        reg = SoLRRegister()
        reg.record_transfer(make_record(account_id="A1", supplier="BulbFail"))
        reg.record_transfer(make_record(account_id="A2", supplier="AvroCrash"))
        assert len(reg.transfers_from("BulbFail")) == 1

    def test_update_raises_not_found(self):
        reg = SoLRRegister()
        with pytest.raises(ValueError):
            reg.notify("MISSING", dt.date(2021, 11, 3))

    def test_summary_keys(self):
        reg = SoLRRegister()
        s = reg.solr_summary()
        for k in ("total_transferred", "active", "designations", "total_credit_claimed_gbp"):
            assert k in s
