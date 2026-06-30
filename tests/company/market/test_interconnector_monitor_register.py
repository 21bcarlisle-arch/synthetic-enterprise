"""Tests for Interconnector Monitor Register (Phase DP)."""
import datetime as dt
import pytest
from company.market.interconnector_monitor_register import (
    InterconnectorID, FlowDirection, InterconnectorObservation,
    InterconnectorMonitorRegister,
    _CAPACITY_MW, _COMMISSIONED_YEAR,
)


@pytest.fixture
def reg():
    return InterconnectorMonitorRegister()


DATE = dt.date(2024, 1, 15)


def record(reg, interconnector=InterconnectorID.IFA, flow=500.0,
           gb_price=80.0, cont_price=70.0, period=17):
    return reg.record(
        interconnector=interconnector,
        settlement_date=DATE,
        settlement_period=period,
        flow_mw=flow,
        gb_price=gb_price,
        continental_price=cont_price,
    )


class TestInterconnectorObservation:
    def test_import_direction(self, reg):
        obs = record(reg, flow=500.0)
        assert obs.direction == FlowDirection.IMPORT

    def test_export_direction(self, reg):
        obs = record(reg, flow=-300.0)
        assert obs.direction == FlowDirection.EXPORT

    def test_zero_direction(self, reg):
        obs = record(reg, flow=3.0)
        assert obs.direction == FlowDirection.ZERO

    def test_utilisation_pct(self, reg):
        # IFA capacity = 2000 MW, flow = 500
        obs = record(reg, interconnector=InterconnectorID.IFA, flow=500.0)
        assert obs.utilisation_pct == pytest.approx(25.0)

    def test_export_utilisation(self, reg):
        obs = record(reg, interconnector=InterconnectorID.IFA, flow=-1000.0)
        assert obs.utilisation_pct == pytest.approx(50.0)

    def test_price_differential(self, reg):
        obs = record(reg, gb_price=90.0, cont_price=70.0)
        assert obs.price_differential_gbp == pytest.approx(20.0)

    def test_arbitrage_aligned_import(self, reg):
        # GB price > continental → importing is correct
        obs = record(reg, flow=500.0, gb_price=90.0, cont_price=70.0)
        assert obs.is_arbitrage_aligned

    def test_arbitrage_misaligned_import(self, reg):
        # GB price < continental → should be exporting, not importing
        obs = record(reg, flow=500.0, gb_price=70.0, cont_price=90.0)
        assert not obs.is_arbitrage_aligned

    def test_arbitrage_aligned_export(self, reg):
        obs = record(reg, flow=-500.0, gb_price=70.0, cont_price=90.0)
        assert obs.is_arbitrage_aligned

    def test_arbitrage_zero_flow_always_aligned(self, reg):
        obs = record(reg, flow=0.0, gb_price=70.0, cont_price=90.0)
        assert obs.is_arbitrage_aligned


class TestInterconnectorMonitorRegister:
    def test_record_and_retrieve(self, reg):
        r = record(reg)
        obs = reg.observations_for(InterconnectorID.IFA)
        assert len(obs) == 1
        assert obs[0] is r

    def test_filter_by_date(self, reg):
        record(reg, interconnector=InterconnectorID.IFA)
        reg.record(InterconnectorID.IFA, dt.date(2024, 2, 1), 1, 300.0, 80.0, 70.0)
        obs = reg.observations_for(InterconnectorID.IFA, date=DATE)
        assert len(obs) == 1

    def test_imports_list(self, reg):
        record(reg, flow=500.0)
        record(reg, flow=-300.0)
        record(reg, flow=100.0)
        assert len(reg.imports()) == 2

    def test_exports_list(self, reg):
        record(reg, flow=-500.0)
        record(reg, flow=200.0)
        assert len(reg.exports()) == 1

    def test_non_arbitrage_aligned(self, reg):
        record(reg, flow=500.0, gb_price=90.0, cont_price=70.0)  # aligned
        record(reg, flow=300.0, gb_price=70.0, cont_price=90.0)  # misaligned
        assert len(reg.non_arbitrage_aligned()) == 1

    def test_avg_gb_price(self, reg):
        record(reg, gb_price=80.0)
        record(reg, gb_price=100.0)
        assert reg.avg_gb_price() == pytest.approx(90.0)

    def test_avg_gb_price_empty(self, reg):
        assert reg.avg_gb_price() == 0.0

    def test_high_utilisation(self, reg):
        # IFA: 500/2000 = 25% (not high)
        record(reg, interconnector=InterconnectorID.IFA, flow=500.0)
        # NSL: 1200/1400 = 85.7% (high)
        record(reg, interconnector=InterconnectorID.NSL, flow=1200.0)
        high = reg.high_utilisation(threshold_pct=80.0)
        assert len(high) == 1

    def test_total_import_capacity(self):
        total = InterconnectorMonitorRegister.total_gb_import_capacity_mw()
        # Sum: 2000+1000+1000+1000+1400+500+500+1400 = 8800
        assert total == pytest.approx(8800.0)

    def test_capacity_dict_complete(self):
        for ic in InterconnectorID:
            assert ic in _CAPACITY_MW

    def test_commissioned_years(self):
        assert InterconnectorMonitorRegister.commissioned_year(InterconnectorID.IFA) == 1985
        assert InterconnectorMonitorRegister.commissioned_year(InterconnectorID.VIKING) == 2023

    def test_all_commissioned_years_present(self):
        for ic in InterconnectorID:
            assert ic in _COMMISSIONED_YEAR

    def test_summary_string(self, reg):
        record(reg)
        s = reg.interconnector_summary()
        assert "Interconnector Monitor" in s
        assert "8,800" in s
