import datetime as dt
import pytest
from company.market.agreed_capacity_register import (
    CapacityChangeType, CapacityChangeStatus, AgreedCapacityRecord,
    CapacityExceedanceRecord, AgreedCapacityRegister, _EXCESS_CAPACITY_MULTIPLIER,
)

MPAN = "1012345678901"
DNO = "WPD"
EFF = dt.date(2024, 1, 1)
AS_OF = dt.date(2024, 6, 1)


def make_record(capacity=500.0, prev=None, status=CapacityChangeStatus.APPLIED):
    return AgreedCapacityRecord(
        record_id="AGCAP-00001", mpan=MPAN, dno_code=DNO,
        effective_date=EFF, agreed_capacity_kva=capacity,
        change_type=CapacityChangeType.INITIAL_REGISTRATION,
        change_status=status, previous_capacity_kva=prev)


class TestAgreedCapacityRecord:
    def test_is_applied(self):
        assert make_record().is_applied
    def test_is_not_applied_pending(self):
        assert not make_record(status=CapacityChangeStatus.PENDING).is_applied
    def test_capacity_change_kva_none_when_no_prev(self):
        assert make_record().capacity_change_kva is None
    def test_capacity_change_kva_reduction(self):
        r = make_record(capacity=400.0, prev=500.0)
        assert abs(r.capacity_change_kva - (-100.0)) < 1e-9
    def test_capacity_change_kva_increase(self):
        r = make_record(capacity=600.0, prev=500.0)
        assert abs(r.capacity_change_kva - 100.0) < 1e-9
    def test_is_reduction(self):
        r = make_record(capacity=400.0, prev=500.0)
        assert r.is_reduction
    def test_is_not_reduction_increase(self):
        r = make_record(capacity=600.0, prev=500.0)
        assert not r.is_reduction
    def test_is_not_reduction_no_prev(self):
        assert not make_record().is_reduction
    def test_excess_multiplier(self):
        assert make_record().excess_capacity_charge_multiplier() == _EXCESS_CAPACITY_MULTIPLIER
    def test_capacity_summary(self):
        s = make_record().capacity_summary()
        assert "AGCAP-00001" in s and MPAN in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.agreed_capacity_kva = 999.0


class TestCapacityExceedanceRecord:
    def test_excess_charge_gbp(self):
        e = CapacityExceedanceRecord(
            exceedance_id="AGCAP-EXC-00001", mpan=MPAN,
            measurement_date=EFF, agreed_capacity_kva=500.0,
            measured_demand_kva=550.0, excess_kva=50.0,
            dnos_rate_gbp_per_kva=2.0)
        assert abs(e.excess_charge_gbp - 50.0 * 2.0 * _EXCESS_CAPACITY_MULTIPLIER) < 1e-9
    def test_utilisation_pct(self):
        e = CapacityExceedanceRecord(
            exceedance_id="X", mpan=MPAN, measurement_date=EFF,
            agreed_capacity_kva=500.0, measured_demand_kva=600.0,
            excess_kva=100.0, dnos_rate_gbp_per_kva=2.0)
        assert abs(e.utilisation_pct - 120.0) < 1e-9
    def test_utilisation_zero_capacity(self):
        e = CapacityExceedanceRecord(
            exceedance_id="X", mpan=MPAN, measurement_date=EFF,
            agreed_capacity_kva=0.0, measured_demand_kva=10.0,
            excess_kva=10.0, dnos_rate_gbp_per_kva=2.0)
        assert e.utilisation_pct == 0.0


class TestAgreedCapacityRegister:
    def setup_method(self):
        self.reg = AgreedCapacityRegister()

    def test_register_capacity_stored(self):
        r = self.reg.register_capacity(MPAN, DNO, EFF, 500.0,
            CapacityChangeType.INITIAL_REGISTRATION)
        assert r.is_applied

    def test_auto_id_increments(self):
        r1 = self.reg.register_capacity(MPAN, DNO, EFF, 500.0,
            CapacityChangeType.INITIAL_REGISTRATION)
        r2 = self.reg.register_capacity("MPAN-002", DNO, EFF, 250.0,
            CapacityChangeType.INITIAL_REGISTRATION)
        assert r1.record_id != r2.record_id

    def test_zero_capacity_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_capacity(MPAN, DNO, EFF, 0.0,
                CapacityChangeType.INITIAL_REGISTRATION)

    def test_negative_capacity_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_capacity(MPAN, DNO, EFF, -50.0,
                CapacityChangeType.INITIAL_REGISTRATION)

    def test_apply_change(self):
        r = self.reg.register_capacity(MPAN, DNO, EFF, 500.0,
            CapacityChangeType.CUSTOMER_REDUCTION,
            previous_capacity_kva=600.0)
        applied = self.reg.apply_change(r.record_id, dt.date(2024, 2, 1))
        assert applied.change_status == CapacityChangeStatus.APPLIED
        assert applied.applied_date == dt.date(2024, 2, 1)

    def test_reject_change(self):
        r = self.reg.register_capacity(MPAN, DNO, EFF, 800.0,
            CapacityChangeType.CUSTOMER_INCREASE)
        rej = self.reg.reject_change(r.record_id)
        assert rej.change_status == CapacityChangeStatus.REJECTED

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.reject_change("AGCAP-99999")

    def test_record_exceedance_stored(self):
        e = self.reg.record_exceedance(MPAN, EFF, 500.0, 550.0, 2.0)
        assert abs(e.excess_kva - 50.0) < 1e-9

    def test_exceedance_no_excess_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_exceedance(MPAN, EFF, 500.0, 500.0, 2.0)

    def test_current_capacity_for(self):
        self.reg.register_capacity(MPAN, DNO, dt.date(2023, 1, 1), 600.0,
            CapacityChangeType.INITIAL_REGISTRATION)
        self.reg.register_capacity(MPAN, DNO, dt.date(2024, 1, 1), 500.0,
            CapacityChangeType.CUSTOMER_REDUCTION, previous_capacity_kva=600.0)
        cap = self.reg.current_capacity_for(MPAN)
        assert abs(cap - 500.0) < 1e-9

    def test_current_capacity_for_none_when_missing(self):
        assert self.reg.current_capacity_for("UNKNOWN") is None

    def test_exceedances_for(self):
        self.reg.record_exceedance(MPAN, EFF, 500.0, 560.0, 2.0)
        self.reg.record_exceedance("OTHER", EFF, 200.0, 250.0, 2.0)
        assert len(self.reg.exceedances_for(MPAN)) == 1

    def test_mpans_with_exceedances(self):
        self.reg.record_exceedance(MPAN, EFF, 500.0, 560.0, 2.0)
        self.reg.record_exceedance(MPAN, EFF, 500.0, 510.0, 2.0)
        self.reg.record_exceedance("OTHER", EFF, 200.0, 250.0, 2.0)
        mpans = self.reg.mpans_with_exceedances()
        assert len(mpans) == 2

    def test_total_excess_charge_gbp(self):
        self.reg.record_exceedance(MPAN, EFF, 500.0, 550.0, 2.0)
        total = self.reg.total_excess_charge_gbp()
        assert total > 0

    def test_reduction_candidates(self):
        self.reg.record_exceedance(MPAN, EFF, 500.0, 550.0, 2.0)
        candidates = self.reg.reduction_candidates(EFF + dt.timedelta(days=30))
        assert MPAN in candidates

    def test_reduction_candidate_excluded_when_old(self):
        self.reg.record_exceedance(MPAN, dt.date(2023, 1, 1), 500.0, 550.0, 2.0)
        candidates = self.reg.reduction_candidates(AS_OF)
        assert MPAN not in candidates

    def test_capacity_summary(self):
        self.reg.register_capacity(MPAN, DNO, EFF, 500.0,
            CapacityChangeType.INITIAL_REGISTRATION)
        s = self.reg.capacity_summary(AS_OF)
        assert "1 supply points" in s
