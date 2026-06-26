import datetime as dt
import pytest
from company.crm.property_improvement import (
    MeasureType, FundingScheme, PropertyImprovement, PropertyImprovementBook
)

DATE = dt.date(2023, 5, 1)


def _improvement(**kwargs):
    defaults = dict(
        customer_id="C1",
        uprn="UPRN-001",
        measure=MeasureType.CAVITY_WALL_INSULATION,
        installation_date=DATE,
        funding_scheme=FundingScheme.ECO4,
        cost_gbp=2500.0,
        epc_before="E",
        epc_after="D",
    )
    defaults.update(kwargs)
    return PropertyImprovement(**defaults)


def test_measure_types_exist():
    assert MeasureType.HEAT_PUMP_AIR_SOURCE == "heat_pump_air_source"
    assert MeasureType.SOLAR_PV == "solar_pv"
    assert MeasureType.CAVITY_WALL_INSULATION == "cavity_wall_insulation"


def test_funding_schemes_exist():
    assert FundingScheme.ECO4 == "ECO4"
    assert FundingScheme.BUS == "BUS"
    assert FundingScheme.PRIVATE == "private"


def test_grant_eco4_cavity_wall():
    imp = _improvement(measure=MeasureType.CAVITY_WALL_INSULATION,
                       funding_scheme=FundingScheme.ECO4, cost_gbp=2500.0)
    assert imp.grant_gbp == pytest.approx(2500.0)
    assert imp.customer_cost_gbp == pytest.approx(0.0)


def test_grant_bus_heat_pump():
    imp = _improvement(
        measure=MeasureType.HEAT_PUMP_AIR_SOURCE,
        funding_scheme=FundingScheme.BUS,
        cost_gbp=12000.0,
    )
    assert imp.grant_gbp == pytest.approx(7500.0)
    assert imp.customer_cost_gbp == pytest.approx(4500.0)


def test_private_funding_no_grant():
    imp = _improvement(funding_scheme=FundingScheme.PRIVATE, cost_gbp=3000.0)
    assert imp.grant_gbp == pytest.approx(0.0)
    assert imp.customer_cost_gbp == pytest.approx(3000.0)


def test_gas_saving_cavity_wall():
    imp = _improvement(measure=MeasureType.CAVITY_WALL_INSULATION)
    assert imp.annual_gas_saving_kwh == pytest.approx(1800.0)
    assert imp.annual_elec_saving_kwh == pytest.approx(0.0)


def test_elec_saving_solar_pv():
    imp = _improvement(measure=MeasureType.SOLAR_PV)
    assert imp.annual_elec_saving_kwh == pytest.approx(2000.0)
    assert imp.annual_gas_saving_kwh == pytest.approx(0.0)


def test_epc_points_heat_pump():
    imp = _improvement(measure=MeasureType.HEAT_PUMP_AIR_SOURCE)
    assert imp.epc_points_gained == 20


def test_simple_payback_years():
    # cavity wall: gas saving 1800 kWh * £0.07 = £126/yr; customer cost = £0
    imp = _improvement(
        measure=MeasureType.CAVITY_WALL_INSULATION,
        funding_scheme=FundingScheme.PRIVATE,
        cost_gbp=2000.0,
    )
    payback = imp.simple_payback_years
    expected = 2000.0 / (1800.0 * 0.07)
    assert payback == pytest.approx(expected, rel=0.01)


def test_book_record_and_for_customer():
    book = PropertyImprovementBook()
    book.record_improvement(
        "C1", "U001", MeasureType.LOFT_INSULATION, DATE,
        FundingScheme.GBIS, 600.0, "E", "D",
    )
    book.record_improvement(
        "C2", "U002", MeasureType.SOLAR_PV, DATE,
        FundingScheme.SEG, 5000.0, "D", "C",
    )
    assert len(book.for_customer("C1")) == 1
    assert len(book.for_customer("C2")) == 1
    assert len(book.for_customer("C3")) == 0


def test_book_customers_upgraded_epc():
    book = PropertyImprovementBook()
    book.record_improvement(
        "C1", "U001", MeasureType.SOLID_WALL_INSULATION,
        dt.date(2023, 3, 1), FundingScheme.ECO4, 8000.0, "F", "D",
    )
    book.record_improvement(
        "C2", "U002", MeasureType.DOUBLE_GLAZING,
        dt.date(2023, 6, 1), FundingScheme.PRIVATE, 4000.0, "E", "E",
    )
    upgraded_to_d = book.customers_upgraded_epc(2023, "D")
    assert "C1" in upgraded_to_d
    assert "C2" not in upgraded_to_d   # stayed at E


def test_book_improvement_summary():
    book = PropertyImprovementBook()
    book.record_improvement(
        "C1", "U001", MeasureType.CAVITY_WALL_INSULATION,
        DATE, FundingScheme.ECO4, 2500.0, "E", "D",
    )
    book.record_improvement(
        "C1", "U001", MeasureType.LOFT_INSULATION,
        DATE, FundingScheme.GBIS, 600.0, "D", "C",
    )
    s = book.improvement_summary(2023)
    assert s["total_measures"] == 2
    assert s["unique_customers"] == 1
    assert s["annual_gas_saving_kwh"] == pytest.approx(1800.0 + 900.0)
    assert "ECO4" in s["by_funding_scheme"]
    assert "GBIS" in s["by_funding_scheme"]
