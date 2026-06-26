import pytest
from company.pricing.tariff_smoothing import TariffDecision, TariffSmoothingBook, SmoothedRateStatus


def _dec(year, commodity="electricity", rate=15.0, cost=12.0, reserve=0.0):
    return TariffDecision(year=year, commodity=commodity, unit_rate_p_per_kwh=rate,
                          wholesale_cost_p_per_kwh=cost, smoothing_reserve_applied_p=reserve)


def test_gross_margin():
    d = _dec(2022, rate=14.0, cost=16.0)
    assert abs(d.gross_margin_p_per_kwh - (-2.0)) < 0.001


def test_is_loss_making_true():
    d = _dec(2022, rate=14.0, cost=16.0)
    assert d.is_loss_making is True
    assert d.status == SmoothedRateStatus.BELOW_COST


def test_is_loss_making_false():
    d = _dec(2020, rate=16.0, cost=12.0)
    assert d.is_loss_making is False
    assert d.status == SmoothedRateStatus.PROFITABLE


def test_marginal_status():
    d = _dec(2021, rate=12.1, cost=12.0)
    assert d.status == SmoothedRateStatus.MARGINAL


def test_record_decision_accumulates():
    book = TariffSmoothingBook()
    book.record_decision(_dec(2020))
    book.record_decision(_dec(2021))
    assert len(book.decisions_for_commodity("electricity")) == 2


def test_loss_making_years_filtered():
    book = TariffSmoothingBook()
    book.record_decision(_dec(2020, rate=16.0, cost=12.0))
    book.record_decision(_dec(2021, rate=14.0, cost=18.0))
    book.record_decision(_dec(2022, rate=14.0, cost=20.0))
    loss = book.loss_making_years("electricity")
    assert len(loss) == 2
    assert all(d.is_loss_making for d in loss)


def test_max_bill_shock_pct():
    book = TariffSmoothingBook()
    book.record_decision(_dec(2020, rate=10.0, cost=8.0))
    book.record_decision(_dec(2021, rate=12.0, cost=10.0))
    book.record_decision(_dec(2022, rate=28.0, cost=22.0))
    shock = book.max_bill_shock_pct("electricity")
    assert abs(shock - (28.0 - 12.0) / 12.0 * 100) < 0.01


def test_smoothing_summary_keys():
    book = TariffSmoothingBook()
    book.record_decision(_dec(2020))
    book.record_decision(_dec(2022, rate=14.0, cost=20.0))
    s = book.smoothing_summary()
    for k in ("total_decisions", "cumulative_reserve_p_per_kwh",
              "loss_making_elec_years", "loss_making_gas_years",
              "max_elec_bill_shock_pct", "max_gas_bill_shock_pct"):
        assert k in s


def test_smoothing_reserve_accumulated():
    book = TariffSmoothingBook()
    book.record_decision(_dec(2020, reserve=0.5))
    book.record_decision(_dec(2021, reserve=-0.3))
    s = book.smoothing_summary()
    assert abs(s["cumulative_reserve_p_per_kwh"] - 0.2) < 0.001


def test_decisions_for_year():
    book = TariffSmoothingBook()
    book.record_decision(_dec(2022, "electricity"))
    book.record_decision(_dec(2022, "gas"))
    book.record_decision(_dec(2021, "electricity"))
    yr = book.decisions_for_year(2022)
    assert len(yr) == 2


def test_crisis_2022_scenario():
    book = TariffSmoothingBook()
    for yr, rate, cost, res in [
        (2020, 15.0, 8.0, 0.5),
        (2021, 20.0, 15.0, 0.3),
        (2022, 30.0, 35.0, -2.0),
        (2023, 25.0, 20.0, 0.5),
    ]:
        book.record_decision(_dec(yr, rate=rate, cost=cost, reserve=res))
    assert book.loss_making_years("electricity") == [book.decisions_for_year(2022)[0]]
    assert book.max_bill_shock_pct("electricity") > 0
    s = book.smoothing_summary()
    assert s["loss_making_elec_years"] == 1
