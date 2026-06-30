"""Tests for Tariff Benchmarking Register (Phase EZ)."""
import datetime as dt
import pytest
from company.market.tariff_benchmarking import (
    SupplierRank, TariffType, CompetitorTariff, TariffBenchmarkSnapshot,
    TariffBenchmarkingRegister,
)

DATE = dt.date(2024, 1, 15)


def make_competitor(name="OVO", rate=28.0, sc=50.0, bill=850.0, date=DATE):
    return CompetitorTariff(
        supplier_name=name, tariff_type=TariffType.SVT,
        snapshot_date=date, electricity_unit_rate_pence=rate,
        electricity_standing_charge_pence=sc, annual_bill_gbp_typical=bill,
    )


def make_snap(company=28.0, competitors=None, date=DATE):
    comps = competitors or [make_competitor(rate=26.0), make_competitor("EDF", rate=30.0)]
    return TariffBenchmarkSnapshot(
        snapshot_date=date, tariff_type=TariffType.SVT,
        company_unit_rate_pence=company,
        competitor_tariffs=tuple(comps),
    )


class TestCompetitorTariff:
    def test_annual_bill_at(self):
        t = make_competitor(rate=28.0, sc=50.0)
        bill = t.annual_bill_at(2900.0)
        expected = 2900.0 * 28.0 / 100 + 365 * 50.0 / 100
        assert bill == pytest.approx(expected)


class TestTariffBenchmarkSnapshot:
    def test_market_avg_rate(self):
        snap = make_snap(competitors=[
            make_competitor(rate=26.0), make_competitor("EDF", rate=30.0)
        ])
        assert snap.market_avg_rate_pence == pytest.approx(28.0)

    def test_market_avg_no_competitors(self):
        snap = make_snap(company=28.0, competitors=[])
        assert snap.market_avg_rate_pence == pytest.approx(28.0)

    def test_company_premium_positive(self):
        snap = make_snap(company=30.0, competitors=[make_competitor(rate=26.0)])
        assert snap.company_premium_pence == pytest.approx(4.0)

    def test_company_premium_negative(self):
        snap = make_snap(company=24.0, competitors=[make_competitor(rate=26.0)])
        assert snap.company_premium_pence == pytest.approx(-2.0)

    def test_is_above_market(self):
        snap = make_snap(company=31.0, competitors=[make_competitor(rate=26.0)])
        assert snap.is_above_market

    def test_not_above_market(self):
        snap = make_snap(company=25.0, competitors=[make_competitor(rate=26.0)])
        assert not snap.is_above_market

    def test_rank_cheapest(self):
        snap = make_snap(company=20.0, competitors=[
            make_competitor(rate=26.0), make_competitor("EDF", rate=30.0)
        ])
        assert snap.supplier_rank == SupplierRank.CHEAPEST

    def test_rank_most_expensive(self):
        snap = make_snap(company=35.0, competitors=[
            make_competitor(rate=26.0), make_competitor("EDF", rate=28.0)
        ])
        assert snap.supplier_rank == SupplierRank.MOST_EXPENSIVE

    def test_benchmark_summary(self):
        snap = make_snap()
        s = snap.benchmark_summary()
        assert "Tariff Benchmark" in s
        assert "rank=" in s


class TestTariffBenchmarkingRegister:
    def test_record_and_retrieve(self):
        reg = TariffBenchmarkingRegister()
        reg.record(make_snap())
        latest = reg.latest_for(TariffType.SVT)
        assert latest is not None

    def test_latest_returns_most_recent(self):
        reg = TariffBenchmarkingRegister()
        reg.record(make_snap(date=dt.date(2024, 1, 1)))
        reg.record(make_snap(date=dt.date(2024, 6, 1)))
        latest = reg.latest_for(TariffType.SVT)
        assert latest.snapshot_date == dt.date(2024, 6, 1)

    def test_snapshots_above_market(self):
        reg = TariffBenchmarkingRegister()
        reg.record(make_snap(company=35.0))  # above
        reg.record(make_snap(company=25.0))  # below
        assert len(reg.snapshots_above_market()) == 1

    def test_avg_company_premium(self):
        reg = TariffBenchmarkingRegister()
        reg.record(make_snap(company=30.0, competitors=[make_competitor(rate=28.0)]))  # +2p
        reg.record(make_snap(company=26.0, competitors=[make_competitor(rate=28.0)]))  # -2p
        assert reg.avg_company_premium_pence() == pytest.approx(0.0)

    def test_tariff_benchmark_summary(self):
        reg = TariffBenchmarkingRegister()
        reg.record(make_snap())
        s = reg.tariff_benchmark_summary(DATE)
        assert "Tariff Benchmarking" in s
