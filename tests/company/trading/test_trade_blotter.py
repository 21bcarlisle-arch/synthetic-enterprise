"""Phase 131: Trade blotter tests."""

from company.trading.trade_blotter import TradeEntry, TradeBlotter


def _entry(direction="buy", volume=100.0, price=50.0, counterparty="EDF", reported=False):
    return TradeEntry(
        trade_id="",
        trade_date="2024-01-15",
        trade_time="10:00",
        direction=direction,
        commodity="electricity",
        volume_mwh=volume,
        price_gbp_per_mwh=price,
        counterparty=counterparty,
        delivery_period="2024-Q2",
        reported_to_remit=reported,
    )


def test_record_assigns_id():
    blotter = TradeBlotter()
    t = blotter.record(_entry())
    assert t.trade_id.startswith("TRD-")


def test_notional_gbp():
    e = _entry(volume=100.0, price=55.0)
    assert e.notional_gbp == 5500.0


def test_buys_and_sells():
    blotter = TradeBlotter()
    blotter.record(_entry(direction="buy"))
    blotter.record(_entry(direction="sell"))
    assert len(blotter.buys()) == 1
    assert len(blotter.sells()) == 1


def test_net_position_long():
    blotter = TradeBlotter()
    blotter.record(_entry(direction="buy", volume=150.0))
    blotter.record(_entry(direction="sell", volume=100.0))
    assert blotter.net_position_mwh() == 50.0


def test_by_counterparty():
    blotter = TradeBlotter()
    blotter.record(_entry(counterparty="EDF"))
    blotter.record(_entry(counterparty="Shell"))
    blotter.record(_entry(counterparty="EDF"))
    assert len(blotter.by_counterparty("EDF")) == 2


def test_remit_reportable():
    e = _entry(volume=0.05)
    assert e.is_remit_reportable is True


def test_unreported_remit():
    blotter = TradeBlotter()
    blotter.record(_entry(volume=100.0, reported=False))
    blotter.record(_entry(volume=100.0, reported=True))
    assert len(blotter.unreported_remit()) == 1


def test_mark_reported():
    blotter = TradeBlotter()
    t = blotter.record(_entry())
    result = blotter.mark_reported(t.trade_id)
    assert result is True
    assert blotter.get(t.trade_id).reported_to_remit is True


def test_counterparty_exposure():
    blotter = TradeBlotter()
    blotter.record(_entry(counterparty="EDF", volume=100.0, price=50.0))
    blotter.record(_entry(counterparty="Shell", volume=200.0, price=60.0))
    exp = blotter.counterparty_exposure()
    assert exp["EDF"] == 5000.0
    assert exp["Shell"] == 12000.0


def test_summary_structure():
    blotter = TradeBlotter()
    blotter.record(_entry())
    s = blotter.summary()
    for k in ("total_trades", "buys", "sells", "net_position_mwh", "unreported_remit", "counterparties"):
        assert k in s
