import datetime as dt
import pytest
from company.market.map_contract_register import (
    MAPServiceType, MAPContractStatus, MAPServiceRate, MAPContractRecord,
    MAPContractRegister,
)

START = dt.date(2023, 1, 1)
END = dt.date(2026, 12, 31)
AS_OF = dt.date(2024, 6, 15)
PROVIDER = "Siemens Energy"

def make_contract(status=MAPContractStatus.ACTIVE, meters=500, rate=4.5):
    return MAPContractRecord(
        contract_id="MAPCON-00001", provider_name=PROVIDER,
        contract_start=START, contract_end=END,
        meter_count_at_start=meters, monthly_rental_rate_gbp_per_meter=rate,
        service_rates=(), status=status)

class TestMAPServiceRate:
    def test_annual_cost_estimate(self):
        r = MAPServiceRate(MAPServiceType.SMETS2_NEW_INSTALL, 100.0, "per_appointment")
        assert abs(r.annual_cost_estimate_gbp(10) - 1000.0) < 1e-9

class TestMAPContractRecord:
    def test_is_active(self):
        assert make_contract().is_active
    def test_is_not_active_expired(self):
        assert not make_contract(MAPContractStatus.EXPIRED).is_active
    def test_is_current_as_of_within_dates(self):
        assert make_contract().is_current_as_of(AS_OF)
    def test_is_not_current_before_start(self):
        assert not make_contract().is_current_as_of(dt.date(2022, 12, 31))
    def test_is_not_current_after_end(self):
        assert not make_contract().is_current_as_of(dt.date(2027, 1, 1))
    def test_is_not_current_when_expired(self):
        assert not make_contract(MAPContractStatus.EXPIRED).is_current_as_of(AS_OF)
    def test_months_remaining(self):
        c = make_contract()
        months = c.months_remaining(dt.date(2026, 10, 1))
        assert months == 3  # (2026-12-31 - 2026-10-01).days=91; 91//30=3
    def test_months_remaining_at_end(self):
        assert make_contract().months_remaining(END) == 0
    def test_monthly_rental_cost(self):
        c = make_contract(meters=100, rate=5.0)
        assert abs(c.monthly_rental_cost_gbp() - 500.0) < 1e-9
    def test_monthly_rental_override_count(self):
        c = make_contract(meters=100, rate=5.0)
        assert abs(c.monthly_rental_cost_gbp(200) - 1000.0) < 1e-9
    def test_annual_rental_cost(self):
        c = make_contract(meters=100, rate=5.0)
        assert abs(c.annual_rental_cost_gbp() - 6000.0) < 1e-9
    def test_service_rate_for_existing(self):
        rate = MAPServiceRate(MAPServiceType.SMETS2_NEW_INSTALL, 120.0, "per_appointment")
        c = MAPContractRecord(
            contract_id="X", provider_name=PROVIDER, contract_start=START, contract_end=END,
            meter_count_at_start=100, monthly_rental_rate_gbp_per_meter=4.5,
            service_rates=(rate,))
        found = c.service_rate_for(MAPServiceType.SMETS2_NEW_INSTALL)
        assert found is not None and found.unit_cost_gbp == 120.0
    def test_service_rate_for_missing(self):
        c = make_contract()
        assert c.service_rate_for(MAPServiceType.METER_REMOVAL) is None
    def test_contract_summary(self):
        s = make_contract().contract_summary()
        assert "MAPCON-00001" in s and PROVIDER in s
    def test_frozen(self):
        c = make_contract()
        with pytest.raises((AttributeError, TypeError)):
            c.provider_name = "Other"

class TestMAPContractRegister:
    def setup_method(self):
        self.reg = MAPContractRegister()
    def test_register_contract_stored(self):
        c = self.reg.register_contract(PROVIDER, START, END, 500, 4.5)
        assert c.is_active
    def test_auto_id_increments(self):
        c1 = self.reg.register_contract(PROVIDER, START, END, 500, 4.5)
        c2 = self.reg.register_contract("Itron", START, END, 300, 3.8)
        assert c1.contract_id != c2.contract_id
    def test_end_before_start_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_contract(PROVIDER, END, START, 500, 4.5)
    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_contract(PROVIDER, START, END, 500, -1.0)
    def test_negative_meter_count_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_contract(PROVIDER, START, END, -1, 4.5)
    def test_mark_expired(self):
        c = self.reg.register_contract(PROVIDER, START, END, 500, 4.5)
        exp = self.reg.mark_expired(c.contract_id)
        assert exp.status == MAPContractStatus.EXPIRED
    def test_terminate(self):
        c = self.reg.register_contract(PROVIDER, START, END, 500, 4.5)
        term_date = dt.date(2024, 12, 31)
        term = self.reg.terminate(c.contract_id, term_date)
        assert term.status == MAPContractStatus.TERMINATED and term.termination_date == term_date
    def test_mark_under_renegotiation(self):
        c = self.reg.register_contract(PROVIDER, START, END, 500, 4.5)
        renegot = self.reg.mark_under_renegotiation(c.contract_id)
        assert renegot.status == MAPContractStatus.UNDER_RENEGOTIATION
    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.mark_expired("MAPCON-99999")
    def test_active_contracts_as_of(self):
        c1 = self.reg.register_contract(PROVIDER, START, END, 500, 4.5)
        self.reg.register_contract("Itron", START, dt.date(2023, 6, 30), 200, 3.0)
        active = self.reg.active_contracts(AS_OF)
        assert len(active) == 1 and active[0].contract_id == c1.contract_id
    def test_contracts_expiring_within(self):
        self.reg.register_contract(PROVIDER, START, dt.date(2024, 7, 15), 500, 4.5)
        self.reg.register_contract("Itron", START, dt.date(2025, 1, 1), 200, 3.0)
        expiring = self.reg.contracts_expiring_within(AS_OF, 60)
        assert len(expiring) == 1
    def test_total_monthly_rental_gbp(self):
        self.reg.register_contract(PROVIDER, START, END, 100, 5.0)
        total = self.reg.total_monthly_rental_gbp(AS_OF)
        assert abs(total - 500.0) < 1e-9
    def test_by_provider(self):
        self.reg.register_contract(PROVIDER, START, END, 500, 4.5)
        self.reg.register_contract("Itron", START, END, 300, 3.8)
        by_p = self.reg.by_provider(PROVIDER)
        assert len(by_p) == 1
    def test_map_contract_summary(self):
        self.reg.register_contract(PROVIDER, START, END, 100, 5.0)
        s = self.reg.map_contract_summary(AS_OF)
        assert "1 contracts" in s and "1 active" in s
    def test_empty_summary(self):
        s = self.reg.map_contract_summary(AS_OF)
        assert "0 contracts" in s
