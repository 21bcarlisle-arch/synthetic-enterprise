import pytest
from company.market.gas_imbalance_ledger import (
    GasImbalanceDirection,
    GasImbalanceRecord,
    GasImbalanceLedger,
)


def _rec(nominated, metered, sbp=15.0, ssp=13.0, mprn="M001", date="2022-01-15"):
    return GasImbalanceRecord(
        mprn=mprn,
        trade_date=date,
        nominated_mwh=nominated,
        metered_mwh=metered,
        sbp_gbp_per_mwh=sbp,
        ssp_gbp_per_mwh=ssp,
    )


# --- GasImbalanceRecord properties ---

class TestGasImbalanceRecord:
    def test_imbalance_mwh_short(self):
        r = _rec(nominated=100.0, metered=105.0)
        assert r.imbalance_mwh == 5.0

    def test_imbalance_mwh_long(self):
        r = _rec(nominated=100.0, metered=95.0)
        assert r.imbalance_mwh == -5.0

    def test_direction_short(self):
        r = _rec(nominated=100.0, metered=105.0)
        assert r.direction == GasImbalanceDirection.SHORT

    def test_direction_long(self):
        r = _rec(nominated=100.0, metered=95.0)
        assert r.direction == GasImbalanceDirection.LONG

    def test_direction_flat_within_tolerance(self):
        # 0.5% deviation is within 1% linepack tolerance
        r = _rec(nominated=100.0, metered=100.5)
        assert r.direction == GasImbalanceDirection.FLAT

    def test_direction_flat_exact(self):
        r = _rec(nominated=100.0, metered=100.0)
        assert r.direction == GasImbalanceDirection.FLAT

    def test_imbalance_charge_short_is_negative(self):
        # short: company buys shortfall at SBP -- cost
        r = _rec(nominated=100.0, metered=110.0, sbp=20.0)
        # imbalance = 10 MWh, charge = -10 * 20 = -200
        assert r.imbalance_charge_gbp == pytest.approx(-200.0)

    def test_imbalance_charge_long_is_positive(self):
        # long: company sells surplus at SSP -- revenue
        r = _rec(nominated=100.0, metered=90.0, ssp=12.0)
        # imbalance = -10, charge = -(-10) * 12 = +120
        assert r.imbalance_charge_gbp == pytest.approx(120.0)

    def test_imbalance_charge_flat_is_zero(self):
        r = _rec(nominated=100.0, metered=100.0)
        assert r.imbalance_charge_gbp == 0.0

    def test_is_crisis_price_false(self):
        r = _rec(nominated=100.0, metered=105.0, sbp=50.0)
        assert not r.is_crisis_price

    def test_is_crisis_price_true(self):
        r = _rec(nominated=100.0, metered=105.0, sbp=189.0)
        assert r.is_crisis_price

    def test_cashout_spread(self):
        r = _rec(nominated=100.0, metered=105.0, sbp=20.0, ssp=16.0)
        assert r.cashout_spread == pytest.approx(4.0)


# --- GasImbalanceLedger price helpers ---

class TestGasImbalanceLedgerPrices:
    def setup_method(self):
        self.ledger = GasImbalanceLedger()

    def test_nbp_annual_rate_known_year(self):
        assert self.ledger.nbp_annual_rate(2022) == pytest.approx(180.0)

    def test_nbp_annual_rate_unknown_year_default(self):
        assert self.ledger.nbp_annual_rate(2030) == pytest.approx(30.0)

    def test_sbp_above_ssp(self):
        sbp = self.ledger.nbp_sbp_for_month(2022, 1)
        ssp = self.ledger.nbp_ssp_for_month(2022, 1)
        assert sbp > ssp

    def test_winter_sbp_above_summer_same_year(self):
        jan_sbp = self.ledger.nbp_sbp_for_month(2022, 1)
        jul_sbp = self.ledger.nbp_sbp_for_month(2022, 7)
        assert jan_sbp > jul_sbp

    def test_crisis_year_sbp_above_threshold(self):
        # 2022 annual avg 180, Jan factor 1.18, * 1.05 = 180*1.18*1.05 ~ 223 > 100
        sbp_2022_jan = self.ledger.nbp_sbp_for_month(2022, 1)
        assert sbp_2022_jan > 100.0

    def test_normal_year_sbp_below_threshold(self):
        # 2016 avg 12.0 -- well below 100
        sbp_2016 = self.ledger.nbp_sbp_for_month(2016, 1)
        assert sbp_2016 < 100.0


# --- GasImbalanceLedger record management and analytics ---

class TestGasImbalanceLedger:
    def _make_ledger(self):
        ledger = GasImbalanceLedger()
        ledger.record(_rec(100.0, 110.0, sbp=189.0, ssp=171.0, mprn="M001", date="2022-01-10"))
        ledger.record(_rec(100.0, 95.0,  sbp=189.0, ssp=171.0, mprn="M001", date="2022-01-11"))
        ledger.record(_rec(100.0, 100.3, sbp=12.6,  ssp=11.4,  mprn="M002", date="2016-06-01"))
        return ledger

    def test_record_and_retrieve_by_date(self):
        ledger = self._make_ledger()
        assert len(ledger.records_for_date("2022-01-10")) == 1

    def test_records_for_mprn(self):
        ledger = self._make_ledger()
        assert len(ledger.records_for_mprn("M001")) == 2

    def test_net_imbalance_cost_year(self):
        ledger = self._make_ledger()
        # 2022 records: -10*189 + 5*171 = -1890 + 855 = -1035
        net = ledger.net_imbalance_cost_gbp(2022)
        assert net == pytest.approx(-1035.0, abs=1.0)

    def test_crisis_periods(self):
        ledger = self._make_ledger()
        crises = ledger.crisis_periods()
        assert len(crises) == 2

    def test_short_periods(self):
        ledger = self._make_ledger()
        shorts = ledger.short_periods()
        assert len(shorts) == 1

    def test_mean_cashout_spread(self):
        ledger = self._make_ledger()
        spread = ledger.mean_cashout_spread(2022)
        assert spread == pytest.approx(18.0)

    def test_gas_imbalance_summary_keys(self):
        ledger = self._make_ledger()
        summary = ledger.gas_imbalance_summary()
        for key in ("total_records", "net_imbalance_cost_gbp", "short_periods",
                    "long_periods", "crisis_periods", "mean_cashout_spread_gbp_per_mwh"):
            assert key in summary

    def test_summary_total_records(self):
        ledger = self._make_ledger()
        assert ledger.gas_imbalance_summary()["total_records"] == 3

    def test_empty_ledger_summary(self):
        ledger = GasImbalanceLedger()
        s = ledger.gas_imbalance_summary()
        assert s["total_records"] == 0
        assert s["net_imbalance_cost_gbp"] == 0.0

    def test_empty_ledger_mean_spread(self):
        ledger = GasImbalanceLedger()
        assert ledger.mean_cashout_spread() == 0.0
