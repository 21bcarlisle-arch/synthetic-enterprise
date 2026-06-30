"""Phase IN: deeper coverage for network_charge_ledger, carbon_emissions, ofgem_supply_return."""
import datetime as dt
import pytest

# ===== network_charge_ledger =====
from company.market.network_charge_ledger import (
    NetworkChargeLedger, NetworkChargeType
)


def _ledger():
    ledger = NetworkChargeLedger()
    ledger.set_rate(2022, NetworkChargeType.TNUOS, "electricity", 25.0)
    ledger.set_rate(2022, NetworkChargeType.DUOS, "electricity", 15.0)
    ledger.post_charge("C1", "M001", dt.date(2022,1,1), dt.date(2022,3,31),
                        NetworkChargeType.TNUOS, 10.0, 25.0)
    ledger.post_charge("C1", "M001", dt.date(2022,1,1), dt.date(2022,3,31),
                        NetworkChargeType.DUOS, 10.0, 15.0)
    ledger.post_charge("C2", "M002", dt.date(2022,4,1), dt.date(2022,6,30),
                        NetworkChargeType.BSUOS, 5.0, 8.0)
    return ledger


class TestNetworkChargeLedger:
    def test_get_rate_returns_latest(self):
        ledger = _ledger()
        assert ledger.get_rate(2022, NetworkChargeType.TNUOS, "electricity") == pytest.approx(25.0)

    def test_get_rate_none_when_absent(self):
        ledger = _ledger()
        assert ledger.get_rate(2023, NetworkChargeType.TNUOS, "electricity") is None

    def test_charge_gbp(self):
        ledger = _ledger()
        rec = ledger._records[0]
        assert rec.charge_gbp == pytest.approx(250.0)  # 10 MWh * 25

    def test_total_charges_gbp_for_customer(self):
        ledger = _ledger()
        total = ledger.total_charges_gbp("C1", dt.date(2022,1,1), dt.date(2022,3,31))
        assert total == pytest.approx(400.0)  # 250 + 150

    def test_total_charges_gbp_no_overlap(self):
        ledger = _ledger()
        total = ledger.total_charges_gbp("C1", dt.date(2023,1,1), dt.date(2023,3,31))
        assert total == pytest.approx(0.0)

    def test_charges_by_type(self):
        ledger = _ledger()
        by_type = ledger.charges_by_type(2022)
        assert "tnuos" in by_type and "duos" in by_type

    def test_portfolio_total_gbp(self):
        ledger = _ledger()
        total = ledger.portfolio_total_gbp(2022)
        # TNUoS=250, DUoS=150, BSUoS=40
        assert total == pytest.approx(440.0)

    def test_annual_summary_keys(self):
        ledger = _ledger()
        s = ledger.annual_summary(2022)
        assert "total_gbp" in s and "by_type" in s and "record_count" in s

    def test_annual_summary_record_count(self):
        ledger = _ledger()
        s = ledger.annual_summary(2022)
        assert s["record_count"] == 3

    def test_charges_by_type_bsuos(self):
        ledger = _ledger()
        by_type = ledger.charges_by_type(2022)
        assert by_type.get("bsuos") == pytest.approx(40.0)  # 5*8


# ===== carbon_emissions =====
from company.regulatory.carbon_emissions import (
    FuelMixRecord, CustomerCarbonFootprint, build_customer_footprint
)


def _mix():
    return FuelMixRecord(
        year=2022,
        coal_pct=5.0, gas_pct=35.0, nuclear_pct=20.0,
        wind_pct=25.0, solar_pct=5.0, hydro_pct=5.0,
        biomass_pct=3.0, imports_pct=2.0,
    )


class TestCarbonEmissions:
    def test_total_pct(self):
        m = _mix()
        assert m.total_pct == pytest.approx(100.0)

    def test_renewable_pct(self):
        m = _mix()
        assert m.renewable_pct == pytest.approx(35.0)

    def test_low_carbon_pct(self):
        m = _mix()
        assert m.low_carbon_pct == pytest.approx(58.0)  # 35+20+3

    def test_emission_intensity_weighted(self):
        m = _mix()
        expected = (
            0.05*820 + 0.35*490 + 0.20*12 + 0.25*11 + 0.05*41
            + 0.05*24 + 0.03*230 + 0.02*300
        )
        assert m.emission_intensity_g_per_kwh == pytest.approx(expected, abs=0.5)

    def test_electricity_co2_kg(self):
        m = _mix()
        fp = build_customer_footprint("C1", 2022, 4000.0, 10000.0, m)
        # 4000 kWh * intensity / 1000
        expected = round(4000 * m.emission_intensity_g_per_kwh / 1000, 1)
        assert fp.electricity_co2_kg == pytest.approx(expected)

    def test_gas_co2_kg(self):
        m = _mix()
        fp = build_customer_footprint("C1", 2022, 4000.0, 10000.0, m)
        # 10000 kWh * 183 g / 1000
        assert fp.gas_co2_kg == pytest.approx(1830.0)

    def test_total_co2_kg(self):
        m = _mix()
        fp = build_customer_footprint("C1", 2022, 4000.0, 10000.0, m)
        assert fp.total_co2_kg == pytest.approx(fp.electricity_co2_kg + fp.gas_co2_kg)

    def test_total_co2_tonnes(self):
        m = _mix()
        fp = build_customer_footprint("C1", 2022, 4000.0, 10000.0, m)
        assert fp.total_co2_tonnes == pytest.approx(fp.total_co2_kg / 1000, abs=0.001)

    def test_build_customer_footprint(self):
        m = _mix()
        fp = build_customer_footprint("C1", 2022, 3000.0, 12000.0, m)
        assert fp.customer_id == "C1"
        assert fp.electricity_kwh == 3000.0

    def test_summary_keys(self):
        m = _mix()
        fp = build_customer_footprint("C1", 2022, 3000.0, 8000.0, m)
        s = fp.summary()
        assert "electricity_co2_kg" in s and "total_co2_tonnes" in s


# ===== ofgem_supply_return =====
from company.regulatory.ofgem_supply_return import (
    OfgemReturnBook, OfgemSupplyReturn
)


def _book():
    b = OfgemReturnBook()
    b.file_return(2021, dt.date(2022,3,31), 4500, 100, 50,
                   80.0, 30.0, 45, 120.0, 200, 500.0)
    b.file_return(2022, dt.date(2023,3,31), 5000, 120, 60,
                   100.0, 40.0, 60, 110.0, 250, 600.0)
    return b


class TestOfgemSupplyReturn:
    def test_total_customers(self):
        b = _book()
        r = b.get(2022)
        assert r.total_customers == 5180

    def test_complaints_per_100(self):
        b = _book()
        r = b.get(2022)
        assert r.complaints_per_100_customers == pytest.approx(60/5000*100)

    def test_is_submitted(self):
        b = _book()
        assert b.get(2022).is_submitted

    def test_whd_penetration_pct(self):
        b = _book()
        r = b.get(2022)
        assert r.whd_penetration_pct == pytest.approx(250/5000*100)

    def test_missing_years(self):
        b = _book()
        missing = b.missing_years(2020, 2023)
        assert 2020 in missing and 2023 in missing
        assert 2021 not in missing and 2022 not in missing

    def test_all_returns_sorted(self):
        b = _book()
        returns = b.all_returns()
        assert returns[0].year < returns[1].year

    def test_get_none_when_absent(self):
        b = _book()
        assert b.get(2019) is None

    def test_summary_keys(self):
        b = _book()
        s = b.get(2022).summary()
        assert "complaints_per_100_customers" in s and "whd_penetration_pct" in s

    def test_complaints_per_100_none_when_no_residential(self):
        r = OfgemSupplyReturn(2023, dt.date(2024,3,31), 0, 10, 5,
                               1.0, 1.0, 0, 0.0, 0, 0.0)
        assert r.complaints_per_100_customers is None

    def test_solr_events_default_zero(self):
        b = _book()
        assert b.get(2022).solr_events == 0
