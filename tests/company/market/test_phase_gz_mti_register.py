"""Tests for Meter Technical Investigation Register -- Phase GZ (SLC 21A)."""
import datetime as dt
import pytest
from company.market.meter_technical_investigation_register import (
    Fuel, MeterTestType, MeterTestOutcome, MTIStatus,
    MeterTechnicalInvestigationRegister,
    _add_working_days, _ELECTRICITY_WITHIN_TOLERANCE_CHARGE_GBP, _SLA_WORKING_DAYS,
)

TODAY = dt.date(2024, 6, 10)
ACC = "A001"
MPAN = "1000000000001"


def make_reg():
    return MeterTechnicalInvestigationRegister()


def commission(reg=None, account=ACC, mpan=MPAN, fuel=Fuel.ELECTRICITY,
               test_type=MeterTestType.IN_SITU, date=TODAY):
    if reg is None:
        reg = make_reg()
    return reg, reg.commission_investigation(account, mpan, fuel, test_type, date)


class TestAddWorkingDays:
    def test_five_wd_skips_weekend(self):
        result = _add_working_days(dt.date(2024, 6, 10), 5)
        assert result == dt.date(2024, 6, 17)

    def test_20_wd_from_monday(self):
        result = _add_working_days(dt.date(2024, 6, 10), 20)
        assert result == dt.date(2024, 7, 8)

    def test_zero_days(self):
        d = dt.date(2024, 6, 10)
        assert _add_working_days(d, 0) == d


class TestMTIRecord:
    def test_is_open_when_commissioned(self):
        _, rec = commission()
        assert rec.is_open

    def test_is_not_open_after_completed(self):
        reg, rec = commission()
        completed = reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 0.5)
        assert not completed.is_open

    def test_outcome_due_date_is_20_wd(self):
        _, rec = commission()
        expected = _add_working_days(TODAY, _SLA_WORKING_DAYS)
        assert rec.outcome_due_date == expected

    def test_is_not_overdue_before_sla(self):
        _, rec = commission()
        assert not rec.is_overdue(TODAY)

    def test_is_overdue_after_sla(self):
        _, rec = commission()
        overdue_date = _add_working_days(TODAY, _SLA_WORKING_DAYS + 1)
        assert rec.is_overdue(overdue_date)

    def test_is_not_overdue_when_completed(self):
        reg, rec = commission()
        late = _add_working_days(TODAY, _SLA_WORKING_DAYS + 5)
        reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, late, 1.0)
        completed = reg.investigations_for_account(ACC)[0]
        assert not completed.is_overdue(late)

    def test_rebill_required_when_outside_tolerance(self):
        reg, rec = commission()
        reg.record_outcome(rec.reference, MeterTestOutcome.OUTSIDE_TOLERANCE, TODAY, 5.0, 365)
        result = reg.investigations_for_account(ACC)[0]
        assert result.rebill_required

    def test_rebill_not_required_within_tolerance(self):
        reg, rec = commission()
        reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        result = reg.investigations_for_account(ACC)[0]
        assert not result.rebill_required

    def test_electricity_within_tolerance_charges_customer(self):
        reg, rec = commission(fuel=Fuel.ELECTRICITY)
        reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        result = reg.investigations_for_account(ACC)[0]
        assert abs(result.customer_charge_gbp - _ELECTRICITY_WITHIN_TOLERANCE_CHARGE_GBP) < 1e-9

    def test_gas_within_tolerance_no_charge(self):
        reg, rec = commission(fuel=Fuel.GAS)
        reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 0.8)
        result = reg.investigations_for_account(ACC)[0]
        assert result.customer_charge_gbp == 0.0

    def test_outside_tolerance_no_charge(self):
        reg, rec = commission(fuel=Fuel.ELECTRICITY)
        reg.record_outcome(rec.reference, MeterTestOutcome.OUTSIDE_TOLERANCE, TODAY, 5.0, 365)
        result = reg.investigations_for_account(ACC)[0]
        assert result.customer_charge_gbp == 0.0

    def test_rebill_period_stored_when_outside_tolerance(self):
        reg, rec = commission()
        reg.record_outcome(rec.reference, MeterTestOutcome.OUTSIDE_TOLERANCE, TODAY, 5.0, 180)
        result = reg.investigations_for_account(ACC)[0]
        assert result.rebill_period_days == 180

    def test_rebill_period_zeroed_when_within_tolerance(self):
        reg, rec = commission()
        reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0, 180)
        result = reg.investigations_for_account(ACC)[0]
        assert result.rebill_period_days == 0

    def test_is_within_tolerance_property(self):
        reg, rec = commission()
        reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        result = reg.investigations_for_account(ACC)[0]
        assert result.is_within_tolerance

    def test_mti_summary_contains_reference(self):
        _, rec = commission()
        assert rec.reference in rec.mti_summary()

    def test_frozen(self):
        _, rec = commission()
        with pytest.raises((AttributeError, TypeError)):
            rec.account_id = "other"


class TestMTIRegister:
    def setup_method(self):
        self.reg = make_reg()

    def test_commission_returns_commissioned_status(self):
        rec = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                                MeterTestType.IN_SITU, TODAY)
        assert rec.status == MTIStatus.COMMISSIONED

    def test_auto_id_prefix(self):
        rec = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                                MeterTestType.IN_SITU, TODAY)
        assert rec.reference.startswith("MTI-")

    def test_auto_id_increments(self):
        r1 = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                               MeterTestType.IN_SITU, TODAY)
        r2 = self.reg.commission_investigation(ACC, "2000000000001", Fuel.GAS,
                                               MeterTestType.REMOVED_TO_LAB, TODAY)
        assert r1.reference != r2.reference

    def test_record_outcome_completes(self):
        rec = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                                MeterTestType.IN_SITU, TODAY)
        completed = self.reg.record_outcome(
            rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.5)
        assert completed.status == MTIStatus.COMPLETED

    def test_record_outcome_unknown_ref_raises(self):
        with pytest.raises(KeyError):
            self.reg.record_outcome("MTI-99999", MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 0.5)

    def test_record_outcome_twice_raises(self):
        rec = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                                MeterTestType.IN_SITU, TODAY)
        self.reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        with pytest.raises(ValueError):
            self.reg.record_outcome(rec.reference, MeterTestOutcome.OUTSIDE_TOLERANCE, TODAY, 5.0)

    def test_cancel_open(self):
        rec = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                                MeterTestType.IN_SITU, TODAY)
        cancelled = self.reg.cancel(rec.reference)
        assert cancelled.status == MTIStatus.CANCELLED

    def test_cancel_completed_raises(self):
        rec = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                                MeterTestType.IN_SITU, TODAY)
        self.reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        with pytest.raises(ValueError):
            self.reg.cancel(rec.reference)

    def test_cancel_unknown_ref_raises(self):
        with pytest.raises(KeyError):
            self.reg.cancel("MTI-99999")

    def test_open_investigations(self):
        r1 = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                               MeterTestType.IN_SITU, TODAY)
        self.reg.commission_investigation("A002", "2000000000001", Fuel.GAS,
                                          MeterTestType.REMOVED_TO_LAB, TODAY)
        self.reg.record_outcome(r1.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        assert len(self.reg.open_investigations) == 1

    def test_completed_investigations(self):
        rec = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                                MeterTestType.IN_SITU, TODAY)
        assert len(self.reg.completed_investigations) == 0
        self.reg.record_outcome(rec.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        assert len(self.reg.completed_investigations) == 1

    def test_rebill_required_investigations(self):
        rec = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                                MeterTestType.IN_SITU, TODAY)
        self.reg.record_outcome(rec.reference, MeterTestOutcome.OUTSIDE_TOLERANCE, TODAY, 8.0, 365)
        assert len(self.reg.rebill_required_investigations) == 1

    def test_overdue_investigations(self):
        self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                          MeterTestType.IN_SITU, TODAY)
        late = _add_working_days(TODAY, _SLA_WORKING_DAYS + 1)
        assert len(self.reg.overdue_investigations(late)) == 1

    def test_not_overdue_within_sla(self):
        self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                          MeterTestType.IN_SITU, TODAY)
        on_due = _add_working_days(TODAY, _SLA_WORKING_DAYS)
        assert len(self.reg.overdue_investigations(on_due)) == 0

    def test_investigations_for_account(self):
        self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                          MeterTestType.IN_SITU, TODAY)
        self.reg.commission_investigation("A002", "2000000000001", Fuel.GAS,
                                          MeterTestType.IN_SITU, TODAY)
        assert len(self.reg.investigations_for_account(ACC)) == 1

    def test_investigations_for_mpan(self):
        self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                          MeterTestType.IN_SITU, TODAY)
        self.reg.commission_investigation(ACC, "2000000000001", Fuel.GAS,
                                          MeterTestType.IN_SITU, TODAY)
        assert len(self.reg.investigations_for_mpan(MPAN)) == 1

    def test_by_fuel(self):
        self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                          MeterTestType.IN_SITU, TODAY)
        self.reg.commission_investigation(ACC, "2000000000001", Fuel.GAS,
                                          MeterTestType.IN_SITU, TODAY)
        assert len(self.reg.by_fuel(Fuel.ELECTRICITY)) == 1
        assert len(self.reg.by_fuel(Fuel.GAS)) == 1

    def test_by_test_type(self):
        self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                          MeterTestType.IN_SITU, TODAY)
        self.reg.commission_investigation(ACC, "2000000000001", Fuel.GAS,
                                          MeterTestType.REMOVED_TO_LAB, TODAY)
        assert len(self.reg.by_test_type(MeterTestType.REMOVED_TO_LAB)) == 1

    def test_total_customer_charges_gbp(self):
        r1 = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                               MeterTestType.IN_SITU, TODAY)
        r2 = self.reg.commission_investigation("A002", "2000000000001", Fuel.ELECTRICITY,
                                               MeterTestType.IN_SITU, TODAY)
        self.reg.record_outcome(r1.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        self.reg.record_outcome(r2.reference, MeterTestOutcome.OUTSIDE_TOLERANCE, TODAY, 6.0, 365)
        assert abs(self.reg.total_customer_charges_gbp - _ELECTRICITY_WITHIN_TOLERANCE_CHARGE_GBP) < 1e-9

    def test_accuracy_dispute_rate_none_when_empty(self):
        assert self.reg.accuracy_dispute_rate_pct() is None

    def test_accuracy_dispute_rate_pct(self):
        r1 = self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                               MeterTestType.IN_SITU, TODAY)
        r2 = self.reg.commission_investigation("A002", "2000000000001", Fuel.ELECTRICITY,
                                               MeterTestType.IN_SITU, TODAY)
        self.reg.record_outcome(r1.reference, MeterTestOutcome.OUTSIDE_TOLERANCE, TODAY, 5.0, 365)
        self.reg.record_outcome(r2.reference, MeterTestOutcome.WITHIN_TOLERANCE, TODAY, 1.0)
        assert abs(self.reg.accuracy_dispute_rate_pct() - 50.0) < 1e-9

    def test_mti_register_summary_contains_total(self):
        self.reg.commission_investigation(ACC, MPAN, Fuel.ELECTRICITY,
                                          MeterTestType.IN_SITU, TODAY)
        s = self.reg.mti_register_summary(TODAY)
        assert "1 investigations" in s

    def test_empty_register_summary(self):
        s = self.reg.mti_register_summary(TODAY)
        assert "0 investigations" in s
