from datetime import date
import pytest
from company.market.gas_nominations import DailyNomination, GasNominationBook

D1 = date(2022, 12, 15)  # crisis period: high NBP spot
D2 = date(2016, 6, 1)    # pre-crisis: low NBP spot
SPOT_CRISIS = 3.50        # GBP/therm (Dec 2021-22 peak)
SPOT_NORMAL = 0.35        # GBP/therm (2016 baseline)


def _book(*args):
    b = GasNominationBook()
    for a in args:
        b.nominate(a)
    return b


def test_short_position_costs_money():
    b = _book(DailyNomination(D1, "C1g", 1000.0, 2000.0, SPOT_NORMAL))
    assert b.cash_out_cost_gbp(D1, "C1g") > 0


def test_long_position_gives_haircut_credit():
    b = _book(DailyNomination(D1, "C1g", 2000.0, 1000.0, SPOT_NORMAL))
    cost = b.cash_out_cost_gbp(D1, "C1g")
    assert cost < 0  # receipt
    imb_kwh = 1000.0 - 2000.0  # -1000 kWh
    imb_therms = -1000.0 / 29.31
    expected = imb_therms * SPOT_NORMAL * 0.85
    assert abs(cost - expected) < 0.01


def test_perfect_nomination_zero_cost():
    b = _book(DailyNomination(D1, "C1g", 500.0, 500.0, SPOT_CRISIS))
    assert b.cash_out_cost_gbp(D1, "C1g") == 0.0


def test_imbalance_kwh_positive_when_short():
    b = _book(DailyNomination(D1, "C1g", 800.0, 1000.0, SPOT_NORMAL))
    assert b.imbalance_kwh(D1, "C1g") == pytest.approx(200.0)


def test_imbalance_kwh_negative_when_long():
    b = _book(DailyNomination(D1, "C1g", 1000.0, 800.0, SPOT_NORMAL))
    assert b.imbalance_kwh(D1, "C1g") == pytest.approx(-200.0)


def test_crisis_short_far_more_expensive_than_normal():
    short_kwh = 1000.0
    b_crisis = _book(DailyNomination(D1, "C1g", 5000.0, 5000.0 + short_kwh, SPOT_CRISIS))
    b_normal = _book(DailyNomination(D2, "C1g", 5000.0, 5000.0 + short_kwh, SPOT_NORMAL))
    cost_crisis = b_crisis.cash_out_cost_gbp(D1, "C1g")
    cost_normal = b_normal.cash_out_cost_gbp(D2, "C1g")
    assert cost_crisis > cost_normal * 5


def test_nomination_accuracy_all_accurate():
    b = _book(
        DailyNomination(D1, "C1g", 1000.0, 1030.0, SPOT_NORMAL),  # 3% error, within 5%
        DailyNomination(D2, "C1g", 1000.0, 980.0, SPOT_NORMAL),   # 2% error, within 5%
    )
    assert b.nomination_accuracy_pct() == 100.0


def test_nomination_accuracy_all_inaccurate():
    b = _book(
        DailyNomination(D1, "C1g", 1000.0, 1200.0, SPOT_NORMAL),  # 20% error
        DailyNomination(D2, "C1g", 1000.0, 700.0, SPOT_NORMAL),   # 30% error
    )
    assert b.nomination_accuracy_pct() == 0.0


def test_monthly_cashout_aggregates():
    jan_1 = date(2022, 1, 10)
    jan_2 = date(2022, 1, 20)
    feb_1 = date(2022, 2, 1)
    b = _book(
        DailyNomination(jan_1, "C1g", 1000.0, 1100.0, 0.50),
        DailyNomination(jan_2, "C1g", 1000.0, 1050.0, 0.50),
        DailyNomination(feb_1, "C1g", 1000.0, 1100.0, 0.50),
    )
    jan_total = b.monthly_cashout_gbp(2022, 1)
    feb_total = b.monthly_cashout_gbp(2022, 2)
    assert jan_total > 0
    assert feb_total > 0
    assert abs(jan_total - (b.cash_out_cost_gbp(jan_1, "C1g") + b.cash_out_cost_gbp(jan_2, "C1g"))) < 0.01


def test_annual_cashout_sums_months():
    jan = date(2021, 1, 15)
    dec = date(2021, 12, 15)
    b = _book(
        DailyNomination(jan, "C2g", 2000.0, 2200.0, 0.60),
        DailyNomination(dec, "C2g", 2000.0, 2400.0, 2.00),
    )
    annual = b.annual_cashout_gbp(2021)
    jan_cost = b.cash_out_cost_gbp(jan, "C2g")
    dec_cost = b.cash_out_cost_gbp(dec, "C2g")
    assert abs(annual - (jan_cost + dec_cost)) < 0.01


def test_worst_imbalance_periods_sorted_by_cost():
    b = _book(
        DailyNomination(date(2022, 1, 1), "C1g", 1000.0, 2000.0, 3.50),   # large short, high spot
        DailyNomination(date(2022, 1, 2), "C1g", 1000.0, 1010.0, 3.50),   # tiny short
        DailyNomination(date(2022, 1, 3), "C1g", 1000.0, 900.0, 0.30),    # long, small
    )
    worst = b.worst_imbalance_periods(n=2)
    assert len(worst) == 2
    assert abs(worst[0]["cost_gbp"]) >= abs(worst[1]["cost_gbp"])


def test_balancing_summary_keys_and_types():
    b = _book(
        DailyNomination(D1, "C1g", 1000.0, 1100.0, SPOT_CRISIS),
        DailyNomination(D2, "C1g", 1000.0, 950.0, SPOT_NORMAL),
    )
    s = b.balancing_summary()
    assert "total_nominations" in s
    assert "short_periods" in s
    assert "long_periods" in s
    assert "nomination_accuracy_pct" in s
    assert "total_cashout_gbp" in s
    assert "net_position" in s
    assert s["total_nominations"] == 2
    assert s["short_periods"] == 1
    assert s["long_periods"] == 1


def test_empty_book_safe():
    b = GasNominationBook()
    assert b.cash_out_cost_gbp(D1, "X") == 0.0
    assert b.imbalance_kwh(D1, "X") == 0.0
    assert b.nomination_accuracy_pct() == 0.0
    assert b.monthly_cashout_gbp(2022, 1) == 0.0
    assert b.annual_cashout_gbp(2022) == 0.0
    assert b.worst_imbalance_periods() == []
    s = b.balancing_summary()
    assert s["total_nominations"] == 0
    assert s["net_position"] == "balanced"
