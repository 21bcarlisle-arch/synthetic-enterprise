import datetime as dt
import pytest
from company.market.llf_register import LLFRecord, LLFRegister

MPAN = "1000000000001"
DNO = "WPD"
LLF_CLASS = "ABC123"
LLF_VAL = 1.03
FROM = dt.date(2024, 4, 1)
TO = dt.date(2025, 4, 1)
AS_OF = dt.date(2024, 10, 15)

def make_record(llf=1.03, effective_to=None):
    return LLFRecord(
        record_id="LLF-00001", mpan=MPAN, dno_code=DNO,
        llf_class=LLF_CLASS, llf_value=llf,
        effective_from=FROM, effective_to=effective_to)

class TestLLFRecord:
    def test_is_current_when_no_to(self):
        assert make_record().is_current
    def test_is_not_current_when_to_set(self):
        assert not make_record(effective_to=TO).is_current
    def test_is_effective_within_dates(self):
        r = make_record(effective_to=TO)
        assert r.is_effective_as_of(AS_OF)
    def test_not_effective_before_from(self):
        r = make_record(effective_to=TO)
        assert not r.is_effective_as_of(FROM - dt.timedelta(1))
    def test_not_effective_at_to(self):
        r = make_record(effective_to=TO)
        assert not r.is_effective_as_of(TO)  # effective_to is exclusive
    def test_loss_uplift_pct_positive(self):
        r = make_record(llf=1.05)
        assert abs(r.loss_uplift_pct - 5.0) < 1e-9
    def test_loss_uplift_pct_at_unity(self):
        assert abs(make_record(llf=1.0).loss_uplift_pct) < 1e-9
    def test_llf_summary_string(self):
        s = make_record().llf_summary()
        assert "LLF-00001" in s and MPAN in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.llf_value = 1.1

class TestLLFRegister:
    def setup_method(self):
        self.reg = LLFRegister()
    def test_register_llf_stored(self):
        r = self.reg.register_llf(MPAN, DNO, LLF_CLASS, LLF_VAL, FROM)
        assert r.llf_value == LLF_VAL
    def test_auto_id_increments(self):
        r1 = self.reg.register_llf(MPAN, DNO, LLF_CLASS, LLF_VAL, FROM)
        r2 = self.reg.register_llf("1000000000002", DNO, "DEF456", 1.01, FROM)
        assert r1.record_id != r2.record_id
    def test_invalid_llf_value_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_llf(MPAN, DNO, LLF_CLASS, 0.0, FROM)
    def test_invalid_to_before_from_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_llf(MPAN, DNO, LLF_CLASS, LLF_VAL, FROM, effective_to=FROM)
    def test_update_llf_closes_previous(self):
        r = self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.03, FROM)
        new_from = dt.date(2025, 4, 1)
        self.reg.update_llf(MPAN, "NEW_CLASS", 1.05, new_from, dno_code=DNO)
        hist = self.reg.historical_for_mpan(MPAN)
        old = [h for h in hist if h.record_id == r.record_id][0]
        assert old.effective_to == new_from
    def test_update_llf_new_record_current(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.03, FROM)
        new_from = dt.date(2025, 4, 1)
        new_r = self.reg.update_llf(MPAN, "NEW_CLASS", 1.05, new_from, dno_code=DNO)
        assert new_r.is_current and new_r.llf_value == 1.05
    def test_current_llf_for_within_dates(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, LLF_VAL, FROM, effective_to=TO)
        cur = self.reg.current_llf_for(MPAN, AS_OF)
        assert cur is not None and cur.llf_value == LLF_VAL
    def test_current_llf_for_none_when_not_effective(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, LLF_VAL, FROM, effective_to=TO)
        assert self.reg.current_llf_for(MPAN, dt.date(2026, 1, 1)) is None
    def test_historical_for_mpan_sorted(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.03, FROM, effective_to=TO)
        self.reg.register_llf(MPAN, DNO, "DEF456", 1.05, TO)
        hist = self.reg.historical_for_mpan(MPAN)
        assert hist[0].effective_from <= hist[1].effective_from
    def test_all_current_as_of(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.03, FROM)
        self.reg.register_llf("1000000000002", DNO, "DEF456", 1.01, FROM)
        self.reg.register_llf("1000000000003", DNO, "GHI789", 1.07, dt.date(2025, 4, 1))
        current = self.reg.all_current_as_of(AS_OF)
        assert len(current) == 2
    def test_by_dno(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.03, FROM)
        self.reg.register_llf("1000000000002", "SPEN", "DEF456", 1.01, FROM)
        assert len(self.reg.by_dno(DNO)) == 1
    def test_high_loss_meters(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.07, FROM)
        self.reg.register_llf("1000000000002", DNO, "DEF456", 1.02, FROM)
        high = self.reg.high_loss_meters(AS_OF, threshold=1.05)
        assert len(high) == 1
    def test_average_llf_as_of(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.04, FROM)
        self.reg.register_llf("1000000000002", DNO, "DEF456", 1.02, FROM)
        avg = self.reg.average_llf_as_of(AS_OF)
        assert abs(avg - 1.03) < 1e-5
    def test_average_llf_none_when_empty(self):
        assert self.reg.average_llf_as_of(AS_OF) is None
    def test_portfolio_loss_uplift_pct(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.04, FROM)
        uplift = self.reg.portfolio_loss_uplift_pct(AS_OF)
        assert abs(uplift - 4.0) < 1e-3
    def test_llf_register_summary(self):
        self.reg.register_llf(MPAN, DNO, LLF_CLASS, 1.03, FROM)
        s = self.reg.llf_register_summary(AS_OF)
        assert "1 records" in s and "1 current" in s
    def test_empty_summary(self):
        s = self.reg.llf_register_summary(AS_OF)
        assert "0 records" in s
