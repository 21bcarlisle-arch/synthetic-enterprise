"""Tests for Wholesale Position Report (Phase DV)."""
import datetime as dt
import pytest
from company.trading.wholesale_position_report import (
    HedgePosture, PositionRAG, DeliveryMonthPosition,
    WholesalePositionReport,
    _GREEN_HEDGE_FLOOR, _AMBER_HEDGE_FLOOR,
)


REPORT_MONTH = dt.date(2024, 1, 1)
DELIV = dt.date(2024, 6, 1)


def make_pos(retail=1000.0, hedged=800.0, wapp=80.0, market=90.0,
             fuel="ELECTRICITY", deliv=DELIV):
    return DeliveryMonthPosition(
        delivery_month=deliv,
        retail_load_mwh=retail,
        hedged_volume_mwh=hedged,
        wapp_gbp_per_mwh=wapp,
        current_market_price_gbp_per_mwh=market,
        fuel=fuel,
    )


@pytest.fixture
def report():
    return WholesalePositionReport(REPORT_MONTH, "Risk Desk")


class TestDeliveryMonthPosition:
    def test_hedge_fraction_pct(self):
        p = make_pos(retail=1000, hedged=800)
        assert p.hedge_fraction_pct == pytest.approx(80.0)

    def test_nop_positive(self):
        p = make_pos(retail=1000, hedged=1100)
        assert p.nop_mwh == pytest.approx(100.0)

    def test_nop_negative(self):
        p = make_pos(retail=1000, hedged=600)
        assert p.nop_mwh == pytest.approx(-400.0)

    def test_posture_under_hedged(self):
        p = make_pos(retail=1000, hedged=800)  # 80% = under 95% = under-hedged
        assert p.posture == HedgePosture.UNDER_HEDGED

    def test_posture_near_flat(self):
        p = make_pos(retail=1000, hedged=970)  # 97% = within ±5%
        assert p.posture == HedgePosture.NEAR_FLAT

    def test_posture_over_hedged(self):
        p = make_pos(retail=1000, hedged=1100)  # 110% = over-hedged
        assert p.posture == HedgePosture.OVER_HEDGED

    def test_rag_green(self):
        p = make_pos(retail=1000, hedged=800)  # 80% >= 70%
        assert p.rag == PositionRAG.GREEN

    def test_rag_amber(self):
        p = make_pos(retail=1000, hedged=500)  # 50% = 40-70%
        assert p.rag == PositionRAG.AMBER

    def test_rag_red(self):
        p = make_pos(retail=1000, hedged=200)  # 20% < 40%
        assert p.rag == PositionRAG.RED

    def test_mtm_positive(self):
        p = make_pos(retail=1000, hedged=800, wapp=80.0, market=90.0)
        # (90-80) * 800 = £8,000 profit
        assert p.mtm_gbp == pytest.approx(8000.0)

    def test_mtm_negative(self):
        p = make_pos(retail=1000, hedged=800, wapp=90.0, market=80.0)
        assert p.mtm_gbp == pytest.approx(-8000.0)
        assert p.is_mtm_loss

    def test_commodity_cost(self):
        p = make_pos(hedged=500, wapp=75.0)
        assert p.commodity_cost_gbp == pytest.approx(37500.0)

    def test_hedge_fraction_zero_load(self):
        p = make_pos(retail=0, hedged=100)
        assert p.hedge_fraction_pct == pytest.approx(0.0)


class TestWholesalePositionReport:
    def test_add_and_list(self, report):
        report.add_position(make_pos())
        assert len(report.positions()) == 1

    def test_filter_by_fuel(self, report):
        report.add_position(make_pos(fuel="ELECTRICITY"))
        report.add_position(make_pos(fuel="GAS"))
        assert len(report.positions("ELECTRICITY")) == 1

    def test_red_positions(self, report):
        report.add_position(make_pos(retail=1000, hedged=200))  # RED
        report.add_position(make_pos(retail=1000, hedged=800))  # GREEN
        assert len(report.red_positions()) == 1

    def test_over_hedged_positions(self, report):
        report.add_position(make_pos(retail=1000, hedged=1100))
        report.add_position(make_pos(retail=1000, hedged=800))
        assert len(report.over_hedged_positions()) == 1

    def test_total_mtm_gbp(self, report):
        report.add_position(make_pos(hedged=800, wapp=80, market=90))  # +8000
        report.add_position(make_pos(hedged=200, wapp=90, market=80))  # -2000
        assert report.total_mtm_gbp() == pytest.approx(6000.0)

    def test_portfolio_hedge_fraction(self, report):
        report.add_position(make_pos(retail=1000, hedged=800))
        report.add_position(make_pos(retail=500, hedged=300))
        # total: 1100 hedged / 1500 retail = 73.3%
        assert report.portfolio_hedge_fraction_pct() == pytest.approx(73.333, rel=0.001)

    def test_largest_nop(self, report):
        p1 = make_pos(retail=1000, hedged=1200)  # NOP=+200
        p2 = make_pos(retail=1000, hedged=600, deliv=dt.date(2024, 7, 1))  # NOP=-400
        report.add_position(p1)
        report.add_position(p2)
        largest = report.largest_nop_position()
        assert largest is not None
        assert abs(largest.nop_mwh) == pytest.approx(400.0)

    def test_largest_nop_empty(self, report):
        assert report.largest_nop_position() is None

    def test_constants(self):
        assert _GREEN_HEDGE_FLOOR == 70.0
        assert _AMBER_HEDGE_FLOOR == 40.0

    def test_report_summary(self, report):
        report.add_position(make_pos())
        s = report.report_summary()
        assert "Wholesale Position Report" in s
        assert "Jan 2024" in s
