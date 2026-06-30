import datetime as dt
import pytest
from company.pricing.ncc_forecast_register import (
    NCCComponent, Fuel, NCCForecastRecord, NCCForecastRegister,
    _PENCE_PER_KWH, _POUNDS_PER_CUSTOMER,
)

PERIOD_START = dt.date(2024, 10, 1)
PERIOD_END = dt.date(2025, 3, 31)
AS_OF = dt.date(2024, 9, 1)


def make_record(component=NCCComponent.BSUOS, fuel=Fuel.ELECTRICITY,
                unit_rate=0.5, unit_label=_PENCE_PER_KWH):
    return NCCForecastRecord(
        record_id="NCC-FC-00001", period_start=PERIOD_START, period_end=PERIOD_END,
        component=component, fuel=fuel, unit_rate=unit_rate, unit_label=unit_label)


class TestNCCForecastRecord:
    def test_period_months(self):
        r = make_record()
        assert r.period_months == 5

    def test_is_applicable_electricity_bsuos(self):
        r = make_record(NCCComponent.BSUOS, Fuel.ELECTRICITY)
        assert r.is_applicable_for_fuel()

    def test_is_not_applicable_gas_bsuos(self):
        r = make_record(NCCComponent.BSUOS, Fuel.GAS)
        assert not r.is_applicable_for_fuel()

    def test_is_applicable_gas_tnuos(self):
        r = make_record(NCCComponent.TNUOS, Fuel.GAS)
        assert r.is_applicable_for_fuel()

    def test_annual_cost_pence_per_kwh(self):
        r = make_record(unit_rate=1.0, unit_label=_PENCE_PER_KWH)
        assert abs(r.annual_cost_per_customer_gbp(3100.0) - 31.0) < 1e-9

    def test_annual_cost_pounds_per_customer(self):
        r = make_record(unit_rate=18.5, unit_label=_POUNDS_PER_CUSTOMER)
        assert abs(r.annual_cost_per_customer_gbp() - 18.5) < 1e-9

    def test_annual_cost_unknown_label_zero(self):
        r = make_record(unit_rate=5.0, unit_label="unknown_unit")
        assert r.annual_cost_per_customer_gbp() == 0.0

    def test_ncc_summary(self):
        s = make_record().ncc_summary()
        assert "NCC-FC-00001" in s and "bsuos" in s and "electricity" in s

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.unit_rate = 99.0


class TestNCCForecastRegister:
    def setup_method(self):
        self.reg = NCCForecastRegister()

    def test_add_forecast_stored(self):
        r = self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)
        assert r.component == NCCComponent.BSUOS

    def test_auto_id_increments(self):
        r1 = self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)
        r2 = self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.TNUOS,
            Fuel.ELECTRICITY, 1.2, _PENCE_PER_KWH)
        assert r1.record_id != r2.record_id

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            self.reg.add_forecast(PERIOD_END, PERIOD_START, NCCComponent.BSUOS,
                Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
                Fuel.ELECTRICITY, -0.1, _PENCE_PER_KWH)

    def test_forecasts_for_period(self):
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.TNUOS,
            Fuel.ELECTRICITY, 1.2, _PENCE_PER_KWH)
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.GAS, 0.1, _PENCE_PER_KWH)
        elec = self.reg.forecasts_for_period(PERIOD_START, Fuel.ELECTRICITY)
        assert len(elec) == 2

    def test_by_component(self):
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.TNUOS,
            Fuel.ELECTRICITY, 1.2, _PENCE_PER_KWH)
        assert len(self.reg.by_component(NCCComponent.BSUOS)) == 1

    def test_total_ncc_pence_per_kwh(self):
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.TNUOS,
            Fuel.ELECTRICITY, 1.2, _PENCE_PER_KWH)
        total = self.reg.total_ncc_pence_per_kwh(PERIOD_START, Fuel.ELECTRICITY)
        assert abs(total - 1.7) < 1e-9

    def test_total_ncc_excludes_pounds_per_customer(self):
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.WHD,
            Fuel.ELECTRICITY, 18.0, _POUNDS_PER_CUSTOMER)
        total = self.reg.total_ncc_pence_per_kwh(PERIOD_START, Fuel.ELECTRICITY)
        assert abs(total - 0.5) < 1e-9

    def test_total_annual_ncc_per_customer_gbp(self):
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 1.0, _PENCE_PER_KWH)
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.WHD,
            Fuel.ELECTRICITY, 20.0, _POUNDS_PER_CUSTOMER)
        total = self.reg.total_annual_ncc_per_customer_gbp(PERIOD_START, Fuel.ELECTRICITY, 3100.0)
        assert abs(total - (31.0 + 20.0)) < 1e-9

    def test_distinct_periods(self):
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)
        next_start = dt.date(2025, 4, 1)
        self.reg.add_forecast(next_start, dt.date(2025, 9, 30), NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.6, _PENCE_PER_KWH)
        periods = self.reg.distinct_periods()
        assert len(periods) == 2

    def test_ncc_forecast_summary(self):
        self.reg.add_forecast(PERIOD_START, PERIOD_END, NCCComponent.BSUOS,
            Fuel.ELECTRICITY, 0.5, _PENCE_PER_KWH)
        s = self.reg.ncc_forecast_summary(PERIOD_START, Fuel.ELECTRICITY)
        assert "electricity" in s and "1 components" in s

    def test_empty_summary(self):
        s = self.reg.ncc_forecast_summary(PERIOD_START, Fuel.ELECTRICITY)
        assert "0 components" in s
