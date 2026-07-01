import pytest
from company.market.imbalance_ledger import (
    ImbalanceLedger, ImbalanceRecord, ImbalanceDirection
)


def _rec(date="2022-09-15", sp=35, metered=5.0, contracted=6.0,
         sbp=200.0, ssp=180.0):
    return ImbalanceRecord(
        settlement_date=date, settlement_period=sp,
        metered_volume_mwh=metered, contracted_volume_mwh=contracted,
        system_buy_price_gbp_per_mwh=sbp,
        system_sell_price_gbp_per_mwh=ssp,
    )


def test_imbalance_mwh_long():
    r = _rec(metered=5.0, contracted=6.0)
    assert abs(r.imbalance_mwh - 1.0) < 0.001


def test_imbalance_mwh_short():
    r = _rec(metered=6.0, contracted=5.0)
    assert abs(r.imbalance_mwh - (-1.0)) < 0.001


def test_direction_long():
    r = _rec(metered=4.0, contracted=6.0)
    assert r.direction == ImbalanceDirection.LONG


def test_direction_short():
    r = _rec(metered=6.0, contracted=4.0)
    assert r.direction == ImbalanceDirection.SHORT


def test_direction_flat():
    r = _rec(metered=5.0, contracted=5.0)
    assert r.direction == ImbalanceDirection.FLAT


def test_long_imbalance_charge_positive():
    r = _rec(metered=4.0, contracted=6.0, ssp=180.0)
    # 2 MWh long, sold at SSP 180
    assert abs(r.imbalance_charge_gbp - 360.0) < 0.01


def test_short_imbalance_charge_negative():
    r = _rec(metered=6.0, contracted=4.0, sbp=200.0)
    # -2 MWh short, bought at SBP 200
    assert abs(r.imbalance_charge_gbp - (-400.0)) < 0.01


def test_is_crisis_price():
    r = _rec(sbp=600.0)
    assert r.is_crisis_price is True


def test_not_crisis_price():
    r = _rec(sbp=200.0)
    assert r.is_crisis_price is False


def test_cashout_spread():
    r = _rec(sbp=200.0, ssp=180.0)
    assert abs(r.cashout_spread_gbp_per_mwh - 20.0) < 0.01


def test_net_imbalance_cost_by_date():
    ledger = ImbalanceLedger()
    ledger.record(_rec(date="2022-09-15", metered=5.0, contracted=6.0, ssp=180.0))  # +180
    ledger.record(_rec(date="2022-09-15", metered=7.0, contracted=6.0, sbp=200.0))  # -200
    net = ledger.net_imbalance_cost_gbp("2022-09-15")
    assert abs(net - (180.0 - 200.0)) < 0.01


def test_imbalance_summary_keys():
    ledger = ImbalanceLedger()
    ledger.record(_rec())
    s = ledger.imbalance_summary("2022-09-15")
    for k in ("total_periods", "net_imbalance_cost_gbp", "short_periods",
               "crisis_periods", "mean_cashout_spread_gbp_per_mwh"):
        assert k in s


# --- Phase LX depth tests ---

def test_settlement_date_stored():
    r = _rec(date='2022-09-15')
    assert r.settlement_date == '2022-09-15'


def test_settlement_period_stored():
    r = _rec(sp=20)
    assert r.settlement_period == 20


def test_metered_volume_stored():
    r = _rec(metered=8.0)
    assert r.metered_volume_mwh == pytest.approx(8.0)


def test_contracted_volume_stored():
    r = _rec(contracted=10.0)
    assert r.contracted_volume_mwh == pytest.approx(10.0)


def test_sbp_stored():
    r = _rec(sbp=300.0)
    assert r.system_buy_price_gbp_per_mwh == pytest.approx(300.0)


def test_ssp_stored():
    r = _rec(ssp=280.0)
    assert r.system_sell_price_gbp_per_mwh == pytest.approx(280.0)


def test_is_crisis_price_false_below_500():
    r = _rec(sbp=499.0)
    assert r.is_crisis_price is False


def test_is_crisis_price_true_above_500():
    r = _rec(sbp=501.0)
    assert r.is_crisis_price is True


def test_cashout_spread_is_sbp_minus_ssp():
    r = _rec(sbp=200.0, ssp=180.0)
    assert r.cashout_spread_gbp_per_mwh == pytest.approx(20.0)


def test_record_returns_imbalance_record():
    ledger = ImbalanceLedger()
    r = _rec()
    result = ledger.record(r)
    assert result is r
