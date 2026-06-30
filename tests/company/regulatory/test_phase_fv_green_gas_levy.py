"""Tests for Phase FV: Green Gas Levy (GGL) Register."""
import datetime as dt
import pytest
from company.regulatory.green_gas_levy_register import (
    GGLPaymentStatus,
    GGLQuarterlyObligation,
    GreenGasLevyRegister,
    _GGL_RATE_GBP_PER_METER_PER_DAY,
    _GGL_START_DATE,
)

RATE_2022 = _GGL_RATE_GBP_PER_METER_PER_DAY[2022]
RATE_2023 = _GGL_RATE_GBP_PER_METER_PER_DAY[2023]

# ── helpers ──────────────────────────────────────────────────────────────────

def make_ob(year=2022, quarter=1, meters=500, rate=None, days=90):
    r = rate if rate is not None else RATE_2022
    return GGLQuarterlyObligation(
        year=year,
        quarter=quarter,
        gas_meter_count=meters,
        rate_gbp_per_meter_per_day=r,
        days_in_quarter=days,
    )


# ── GGLQuarterlyObligation ───────────────────────────────────────────────────

class TestGGLQuarterlyObligation:

    def test_total_levy_gbp(self):
        ob = make_ob(meters=1000, rate=0.001, days=90)
        assert abs(ob.total_levy_gbp - 90.0) < 1e-9

    def test_total_levy_gbp_partial_quarter(self):
        ob = make_ob(year=2021, quarter=4, meters=500, rate=RATE_2022, days=32)
        expected = 500 * RATE_2022 * 32
        assert abs(ob.total_levy_gbp - expected) < 1e-9

    def test_quarter_label_q1(self):
        ob = make_ob(quarter=1)
        assert "2022 Q1" in ob.quarter_label
        assert "Jan-Mar" in ob.quarter_label

    def test_quarter_label_q4(self):
        ob = make_ob(quarter=4)
        assert "2022 Q4" in ob.quarter_label
        assert "Oct-Dec" in ob.quarter_label

    def test_payment_due_date_q1(self):
        ob = make_ob(year=2023, quarter=1)
        assert ob.payment_due_date == dt.date(2023, 4, 28)

    def test_payment_due_date_q2(self):
        ob = make_ob(year=2022, quarter=2)
        assert ob.payment_due_date == dt.date(2022, 7, 28)

    def test_payment_due_date_q3(self):
        ob = make_ob(year=2022, quarter=3)
        assert ob.payment_due_date == dt.date(2022, 10, 28)

    def test_payment_due_date_q4_rolls_to_next_year(self):
        ob = make_ob(year=2022, quarter=4)
        assert ob.payment_due_date == dt.date(2023, 1, 28)

    def test_is_overdue_on_due_date_not_overdue(self):
        ob = make_ob(year=2022, quarter=1)  # due Apr 28 2022
        assert not ob.is_overdue(dt.date(2022, 4, 28))

    def test_is_overdue_after_due_date(self):
        ob = make_ob(year=2022, quarter=1)
        assert ob.is_overdue(dt.date(2022, 4, 29))

    def test_obligation_summary_contains_key_fields(self):
        ob = make_ob(meters=200)
        s = ob.obligation_summary()
        assert "200" in s
        assert "£" in s
        assert "2022 Q1" in s

    def test_obligation_is_frozen(self):
        ob = make_ob()
        with pytest.raises((AttributeError, TypeError)):
            ob.gas_meter_count = 999


# ── GreenGasLevyRegister ─────────────────────────────────────────────────────

class TestGreenGasLevyRegister:

    def setup_method(self):
        self.reg = GreenGasLevyRegister()

    def test_record_obligation_stored(self):
        ob = self.reg.record_obligation(2022, 1, 300)
        assert ob.year == 2022
        assert ob.quarter == 1
        assert ob.gas_meter_count == 300

    def test_record_obligation_pre_ggl_q1_2021_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_obligation(2021, 1, 100)

    def test_record_obligation_year_2020_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_obligation(2020, 4, 100)

    def test_record_obligation_q4_2021_is_valid(self):
        ob = self.reg.record_obligation(2021, 4, 100, days_in_quarter=32)
        assert ob.year == 2021 and ob.quarter == 4 and ob.days_in_quarter == 32

    def test_default_rate_lookup(self):
        ob = self.reg.record_obligation(2023, 2, 400)
        assert abs(ob.rate_gbp_per_meter_per_day - RATE_2023) < 1e-12

    def test_custom_rate_used_when_provided(self):
        ob = self.reg.record_obligation(2022, 1, 100, rate_gbp_per_meter_per_day=0.005)
        assert abs(ob.rate_gbp_per_meter_per_day - 0.005) < 1e-12

    def test_mark_paid_and_is_paid(self):
        self.reg.record_obligation(2022, 1, 300)
        assert not self.reg.is_paid(2022, 1)
        self.reg.mark_paid(2022, 1)
        assert self.reg.is_paid(2022, 1)

    def test_obligations_for_year_filters(self):
        self.reg.record_obligation(2022, 1, 300)
        self.reg.record_obligation(2022, 2, 310)
        self.reg.record_obligation(2023, 1, 320)
        assert len(self.reg.obligations_for_year(2022)) == 2
        assert len(self.reg.obligations_for_year(2023)) == 1

    def test_unpaid_obligations_excludes_paid(self):
        self.reg.record_obligation(2022, 1, 300)
        self.reg.record_obligation(2022, 2, 310)
        self.reg.mark_paid(2022, 1)
        unpaid = self.reg.unpaid_obligations()
        assert len(unpaid) == 1
        assert unpaid[0].quarter == 2

    def test_overdue_obligations_uses_as_of(self):
        self.reg.record_obligation(2022, 1, 300)  # due Apr 28 2022
        self.reg.record_obligation(2022, 2, 310)  # due Jul 28 2022
        overdue = self.reg.overdue_obligations(dt.date(2022, 5, 1))
        assert len(overdue) == 1
        assert overdue[0].quarter == 1

    def test_overdue_excludes_paid(self):
        self.reg.record_obligation(2022, 1, 300)
        self.reg.mark_paid(2022, 1)
        assert len(self.reg.overdue_obligations(dt.date(2025, 1, 1))) == 0

    def test_total_levy_paid_gbp(self):
        ob1 = self.reg.record_obligation(2022, 1, 1000, rate_gbp_per_meter_per_day=0.001, days_in_quarter=90)
        self.reg.record_obligation(2022, 2, 1000, rate_gbp_per_meter_per_day=0.001, days_in_quarter=91)
        self.reg.mark_paid(2022, 1)
        assert abs(self.reg.total_levy_paid_gbp() - ob1.total_levy_gbp) < 1e-9

    def test_total_levy_accrued_gbp(self):
        self.reg.record_obligation(2022, 1, 1000, rate_gbp_per_meter_per_day=0.001, days_in_quarter=90)
        ob2 = self.reg.record_obligation(2022, 2, 1000, rate_gbp_per_meter_per_day=0.001, days_in_quarter=91)
        self.reg.mark_paid(2022, 1)
        assert abs(self.reg.total_levy_accrued_gbp() - ob2.total_levy_gbp) < 1e-9

    def test_annual_levy_gbp_includes_paid(self):
        ob1 = self.reg.record_obligation(2022, 1, 1000, rate_gbp_per_meter_per_day=0.001, days_in_quarter=90)
        ob2 = self.reg.record_obligation(2022, 2, 1000, rate_gbp_per_meter_per_day=0.001, days_in_quarter=91)
        self.reg.mark_paid(2022, 1)
        expected = ob1.total_levy_gbp + ob2.total_levy_gbp
        assert abs(self.reg.annual_levy_gbp(2022) - expected) < 1e-9

    def test_ggl_summary_includes_counts(self):
        self.reg.record_obligation(2022, 1, 300)
        self.reg.record_obligation(2022, 2, 310)
        self.reg.mark_paid(2022, 1)
        s = self.reg.ggl_summary(dt.date(2022, 8, 1))
        assert "2 obligations" in s
        assert "1 paid" in s

    def test_ggl_summary_empty_register(self):
        s = self.reg.ggl_summary(dt.date(2024, 1, 1))
        assert "0 obligations" in s

    def test_ggl_start_date_constant(self):
        assert _GGL_START_DATE == dt.date(2021, 11, 30)

    def test_rate_rises_year_on_year(self):
        years = sorted(_GGL_RATE_GBP_PER_METER_PER_DAY.keys())
        for i in range(len(years) - 1):
            assert (
                _GGL_RATE_GBP_PER_METER_PER_DAY[years[i]]
                < _GGL_RATE_GBP_PER_METER_PER_DAY[years[i + 1]]
            )

    def test_multiple_payments_correct_accounting(self):
        self.reg.record_obligation(2022, 1, 500)
        self.reg.record_obligation(2022, 2, 500)
        self.reg.record_obligation(2022, 3, 500)
        self.reg.mark_paid(2022, 1)
        self.reg.mark_paid(2022, 2)
        assert len(self.reg.unpaid_obligations()) == 1
        assert self.reg.unpaid_obligations()[0].quarter == 3
