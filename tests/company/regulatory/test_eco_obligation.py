import pytest
from company.regulatory.eco_obligation import (
    ECOObligationBook, ECODelivery, ECOPhase, MeasureCategory
)


def _delivery(did="D001", phase=ECOPhase.ECO4, year=2023, cid="C1",
              cat=MeasureCategory.INSULATION, co2=2.5, cost=800.0, fuel_poor=True):
    return ECODelivery(
        delivery_id=did, phase=phase, delivery_year=year, customer_id=cid,
        category=cat, co2_saved_tonnes=co2, cost_gbp=cost, is_fuel_poor=fuel_poor,
    )


def test_cost_per_tonne_co2():
    d = _delivery(co2=2.5, cost=500.0)
    assert abs(d.cost_per_tonne_co2 - 200.0) < 0.01


def test_cost_per_tonne_zero_co2():
    d = _delivery(co2=0.0, cost=100.0)
    assert d.cost_per_tonne_co2 == 0.0


def test_record_and_filter_by_phase():
    book = ECOObligationBook()
    book.record_delivery(_delivery(phase=ECOPhase.ECO4))
    book.record_delivery(_delivery(did="D002", phase=ECOPhase.ECO3))
    assert len(book.deliveries_for_phase(ECOPhase.ECO4)) == 1


def test_deliveries_for_year():
    book = ECOObligationBook()
    book.record_delivery(_delivery(year=2023))
    book.record_delivery(_delivery(did="D002", year=2022))
    assert len(book.deliveries_for_year(2023)) == 1


def test_total_co2_saved():
    book = ECOObligationBook()
    book.record_delivery(_delivery(co2=2.5))
    book.record_delivery(_delivery(did="D002", co2=3.0))
    assert abs(book.total_co2_saved_tonnes() - 5.5) < 0.01


def test_total_cost():
    book = ECOObligationBook()
    book.record_delivery(_delivery(cost=1000.0))
    book.record_delivery(_delivery(did="D002", cost=500.0))
    assert abs(book.total_cost_gbp() - 1500.0) < 0.01


def test_estimated_annual_obligation():
    book = ECOObligationBook(annual_electricity_supplied_mwh=10_000.0)
    eco4_gbp = book.estimated_annual_obligation_gbp(ECOPhase.ECO4)
    assert abs(eco4_gbp - 68_000.0) < 0.01


def test_fuel_poor_pct():
    book = ECOObligationBook()
    book.record_delivery(_delivery(fuel_poor=True))
    book.record_delivery(_delivery(did="D002", fuel_poor=False))
    book.record_delivery(_delivery(did="D003", fuel_poor=True))
    assert abs(book.fuel_poor_delivery_pct() - (2/3*100)) < 0.1


def test_eco_summary_keys():
    book = ECOObligationBook()
    book.record_delivery(_delivery())
    s = book.eco_summary()
    for k in ("total_deliveries", "total_co2_saved_tonnes", "total_cost_gbp",
               "fuel_poor_delivery_pct", "eco4_estimated_annual_gbp"):
        assert k in s


def test_eco_summary_empty():
    book = ECOObligationBook()
    s = book.eco_summary()
    assert s["total_deliveries"] == 0
    assert s["total_co2_saved_tonnes"] == 0.0
