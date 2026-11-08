"""Tests for Grid Connection Queue Register -- Phase HF."""
import datetime as dt
import pytest
from company.market.grid_connection_queue_register import (
    ConnectionApplicationType, ConnectionApplicationStatus,
    GridConnectionApplicationRecord, GridConnectionQueueRegister,
    _ACTIVE, _ACCEPTED_COSTS,
)

TODAY = dt.date(2024, 6, 10)
OFFER_DATE = dt.date(2024, 7, 1)
OFFER_VALID = dt.date(2024, 10, 1)
ACC = "A001"
DNO = "UK Power Networks"
ADDR = "1 Industrial Way, Birmingham"


def make_reg():
    return GridConnectionQueueRegister()


def submit(reg=None, account=ACC, addr=ADDR, atype=ConnectionApplicationType.NEW_CONNECTION,
           capacity=500.0, dno=DNO, date=TODAY):
    if reg is None:
        reg = make_reg()
    return reg, reg.submit_application(account, addr, atype, capacity, dno, date)


class TestGridConnectionApplicationRecord:
    def test_is_active_when_submitted(self):
        _, rec = submit()
        assert rec.is_active

    def test_is_not_active_when_abandoned(self):
        reg, rec = submit()
        reg.abandon(rec.reference)
        result = reg.abandoned_applications[0]
        assert not result.is_active

    def test_is_not_energised_when_submitted(self):
        _, rec = submit()
        assert not rec.is_energised

    def test_is_energised_after_energise(self):
        reg, rec = submit()
        reg.accept_feasibility(rec.reference)
        reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        reg.accept_offer(rec.reference)
        reg.start_design(rec.reference)
        reg.start_construction(rec.reference)
        reg.energise(rec.reference, TODAY)
        result = reg.energised_applications[0]
        assert result.is_energised

    def test_offer_is_live_when_offer_issued(self):
        reg, rec = submit()
        reg.accept_feasibility(rec.reference)
        reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        result = reg.offers_pending_acceptance(OFFER_DATE)[0]
        assert result.offer_is_live(OFFER_DATE)

    def test_offer_not_live_after_valid_to(self):
        reg, rec = submit()
        reg.accept_feasibility(rec.reference)
        reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        result = reg.all_records[0]
        past_valid = OFFER_VALID + dt.timedelta(days=1)
        assert not result.offer_is_live(past_valid)

    def test_days_in_queue_before_energisation(self):
        _, rec = submit(date=TODAY)
        as_of = TODAY + dt.timedelta(days=30)
        assert rec.days_in_queue(as_of) == 30

    def test_days_in_queue_uses_energisation_date(self):
        reg, rec = submit(date=TODAY)
        reg.accept_feasibility(rec.reference)
        reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        reg.accept_offer(rec.reference)
        reg.start_design(rec.reference)
        reg.start_construction(rec.reference)
        energised_date = TODAY + dt.timedelta(days=180)
        reg.energise(rec.reference, energised_date)
        result = reg.energised_applications[0]
        assert result.days_in_queue(dt.date(2030, 1, 1)) == 180

    def test_application_summary_contains_ref(self):
        _, rec = submit()
        assert rec.reference in rec.application_summary()

    def test_frozen(self):
        _, rec = submit()
        with pytest.raises((AttributeError, TypeError)):
            rec.account_id = "other"


class TestGridConnectionQueueRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _submit(self, account=ACC, addr=ADDR, atype=ConnectionApplicationType.NEW_CONNECTION,
                capacity=500.0, dno=DNO, date=TODAY):
        return self.reg.submit_application(account, addr, atype, capacity, dno, date)

    def test_submit_returns_submitted_status(self):
        rec = self._submit()
        assert rec.status == ConnectionApplicationStatus.SUBMITTED

    def test_auto_id_prefix(self):
        rec = self._submit()
        assert rec.reference.startswith("GCQ-")

    def test_auto_id_increments(self):
        r1 = self._submit()
        r2 = self._submit(account="A002", addr="2 Other St")
        assert r1.reference != r2.reference

    def test_zero_capacity_raises(self):
        with pytest.raises(ValueError):
            self._submit(capacity=0.0)

    def test_accept_feasibility(self):
        rec = self._submit()
        result = self.reg.accept_feasibility(rec.reference)
        assert result.status == ConnectionApplicationStatus.FEASIBILITY_ACCEPTED

    def test_accept_feasibility_non_submitted_raises(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        with pytest.raises(ValueError):
            self.reg.accept_feasibility(rec.reference)

    def test_issue_offer(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        result = self.reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        assert result.status == ConnectionApplicationStatus.OFFER_ISSUED
        assert result.offer_cost_gbp == 50000.0

    def test_offer_valid_before_date_raises(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        with pytest.raises(ValueError):
            self.reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_DATE)

    def test_negative_offer_cost_raises(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        with pytest.raises(ValueError):
            self.reg.issue_offer(rec.reference, -1.0, OFFER_DATE, OFFER_VALID)

    def test_accept_offer(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        self.reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        result = self.reg.accept_offer(rec.reference)
        assert result.status == ConnectionApplicationStatus.OFFER_ACCEPTED

    def test_reject_offer(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        self.reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        result = self.reg.reject_offer(rec.reference)
        assert result.status == ConnectionApplicationStatus.OFFER_REJECTED

    def test_full_lifecycle_to_energised(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        self.reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        self.reg.accept_offer(rec.reference)
        self.reg.start_design(rec.reference)
        self.reg.start_construction(rec.reference)
        result = self.reg.energise(rec.reference, TODAY)
        assert result.status == ConnectionApplicationStatus.ENERGISED

    def test_energise_non_construction_raises(self):
        rec = self._submit()
        with pytest.raises(ValueError):
            self.reg.energise(rec.reference, TODAY)

    def test_abandon_active(self):
        rec = self._submit()
        result = self.reg.abandon(rec.reference)
        assert result.status == ConnectionApplicationStatus.ABANDONED

    def test_abandon_energised_raises(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        self.reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        self.reg.accept_offer(rec.reference)
        self.reg.start_design(rec.reference)
        self.reg.start_construction(rec.reference)
        self.reg.energise(rec.reference, TODAY)
        with pytest.raises(ValueError):
            self.reg.abandon(rec.reference)

    def test_active_applications(self):
        r1 = self._submit(account=ACC)
        r2 = self._submit(account="A002", addr="2 Other St")
        self.reg.abandon(r1.reference)
        assert len(self.reg.active_applications) == 1

    def test_offers_pending_acceptance(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        self.reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        offers = self.reg.offers_pending_acceptance(OFFER_DATE)
        assert len(offers) == 1

    def test_offers_expiring_soon(self):
        rec = self._submit()
        self.reg.accept_feasibility(rec.reference)
        self.reg.issue_offer(rec.reference, 50000.0, OFFER_DATE, OFFER_VALID)
        expiring = self.reg.offers_expiring_soon(
            OFFER_VALID - dt.timedelta(days=25), 30
        )
        assert len(expiring) == 1

    def test_applications_for_account(self):
        self._submit(account=ACC)
        self._submit(account="A002", addr="2 Other St")
        assert len(self.reg.applications_for_account(ACC)) == 1

    def test_total_committed_cost_gbp(self):
        r1 = self._submit(account=ACC)
        r2 = self._submit(account="A002", addr="2 Other St")
        self.reg.accept_feasibility(r1.reference)
        self.reg.issue_offer(r1.reference, 30000.0, OFFER_DATE, OFFER_VALID)
        self.reg.accept_offer(r1.reference)
        self.reg.accept_feasibility(r2.reference)
        self.reg.issue_offer(r2.reference, 20000.0, OFFER_DATE, OFFER_VALID)
        # r2 offer not accepted
        assert abs(self.reg.total_committed_cost_gbp - 30000.0) < 1e-9

    def test_by_application_type(self):
        self._submit(atype=ConnectionApplicationType.NEW_CONNECTION)
        self._submit(account="A002", addr="2 Other St",
                     atype=ConnectionApplicationType.GENERATION_EXPORT)
        assert len(self.reg.by_application_type(ConnectionApplicationType.GENERATION_EXPORT)) == 1

    def test_queue_summary_contains_total(self):
        self._submit()
        s = self.reg.queue_summary(TODAY)
        assert "1 total" in s

    def test_empty_queue_summary(self):
        s = self.reg.queue_summary(TODAY)
        assert "0 total" in s
