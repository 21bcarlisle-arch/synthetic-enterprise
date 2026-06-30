"""Phase JE coverage expansion: ets_registry, flexible_asset, desnz_returns."""
import datetime as dt
import unittest


class TestETSRegistry(unittest.TestCase):

    def _reg(self):
        from company.regulatory.ets_registry import ETSRegistry, AllowanceSource
        return ETSRegistry(), AllowanceSource

    def test_purchase_and_total_cost(self):
        reg, S = self._reg()
        p = reg.purchase("P1", 2023, dt.date(2023, 3, 1), 1000.0, 50.0, S.AUCTION)
        self.assertAlmostEqual(p.total_cost_gbp, 50_000.0)

    def test_holding_tonnes(self):
        reg, S = self._reg()
        reg.purchase("P1", 2023, dt.date(2023, 3, 1), 500.0, 50.0, S.AUCTION)
        reg.purchase("P2", 2023, dt.date(2023, 6, 1), 300.0, 55.0, S.SECONDARY_MARKET)
        self.assertAlmostEqual(reg.holding_tonnes(2023), 800.0)

    def test_surrender_reduces_holding(self):
        reg, S = self._reg()
        reg.purchase("P1", 2023, dt.date(2023, 3, 1), 1000.0, 50.0, S.AUCTION)
        reg.surrender(2023, 400.0)
        self.assertAlmostEqual(reg.holding_tonnes(2023), 600.0)

    def test_total_spend_gbp(self):
        reg, S = self._reg()
        reg.purchase("P1", 2023, dt.date(2023, 3, 1), 100.0, 50.0, S.AUCTION)
        reg.purchase("P2", 2023, dt.date(2023, 6, 1), 200.0, 60.0, S.FORWARD_PURCHASE)
        self.assertAlmostEqual(reg.total_spend_gbp(2023), 17_000.0)

    def test_record_obligation_gross_and_net(self):
        reg, _ = self._reg()
        ob = reg.record_obligation(2023, 1000.0, 0.5, free_allocation=100.0)
        self.assertAlmostEqual(ob.gross_obligation_tonnes, 500.0)
        self.assertAlmostEqual(ob.net_obligation_tonnes, 400.0)

    def test_net_obligation_never_negative(self):
        reg, _ = self._reg()
        ob = reg.record_obligation(2023, 100.0, 0.1, free_allocation=500.0)
        self.assertAlmostEqual(ob.net_obligation_tonnes, 0.0)

    def test_compliance_position_is_compliant(self):
        reg, S = self._reg()
        reg.purchase("P1", 2023, dt.date(2023, 1, 1), 500.0, 50.0, S.AUCTION)
        reg.record_obligation(2023, 500.0, 0.5)  # net=250t
        pos = reg.compliance_position(2023)
        self.assertTrue(pos["is_compliant"])
        self.assertGreater(pos["surplus_deficit_tonnes"], 0)

    def test_compliance_position_not_compliant(self):
        reg, S = self._reg()
        reg.purchase("P1", 2023, dt.date(2023, 1, 1), 10.0, 50.0, S.AUCTION)
        reg.record_obligation(2023, 5000.0, 0.5)  # net=2500t, holding=10t
        pos = reg.compliance_position(2023)
        self.assertFalse(pos["is_compliant"])

    def test_compliance_position_none_when_no_obligation(self):
        reg, _ = self._reg()
        self.assertIsNone(reg.compliance_position(2023))

    def test_holding_filtered_by_year(self):
        reg, S = self._reg()
        reg.purchase("P1", 2022, dt.date(2022, 1, 1), 100.0, 50.0, S.AUCTION)
        reg.purchase("P2", 2023, dt.date(2023, 1, 1), 200.0, 55.0, S.AUCTION)
        self.assertAlmostEqual(reg.holding_tonnes(2023), 200.0)


class TestFlexibleAsset(unittest.TestCase):

    def _asset(self, capacity_mw=2.0, storage_mwh=4.0, soc=0.0, efficiency=100.0):
        from company.market.flexible_asset import FlexibleAsset, AssetType
        return FlexibleAsset("FA1", AssetType.BATTERY_STORAGE, capacity_mw,
                              storage_mwh, efficiency, soc)

    def test_soc_pct(self):
        asset = self._asset(storage_mwh=4.0, soc=2.0)
        self.assertAlmostEqual(asset.soc_pct, 50.0)

    def test_can_charge_when_not_full(self):
        asset = self._asset(storage_mwh=4.0, soc=0.0)
        self.assertTrue(asset.can_charge)

    def test_can_not_charge_when_full(self):
        asset = self._asset(storage_mwh=4.0, soc=4.0)
        self.assertFalse(asset.can_charge)

    def test_can_discharge_when_has_energy(self):
        asset = self._asset(storage_mwh=4.0, soc=2.0)
        self.assertTrue(asset.can_discharge)

    def test_can_not_discharge_when_empty(self):
        asset = self._asset(storage_mwh=4.0, soc=0.0)
        self.assertFalse(asset.can_discharge)

    def test_dispatch_discharge_energy_mwh(self):
        from company.market.flexible_asset import DispatchMode
        asset = self._asset(storage_mwh=4.0, soc=4.0)
        interval = asset.dispatch(dt.date(2023, 1, 1), 35, DispatchMode.DISCHARGE, 2.0, 200.0)
        self.assertAlmostEqual(interval.energy_mwh, 1.0)  # 2MW * 0.5h

    def test_dispatch_discharge_revenue(self):
        from company.market.flexible_asset import DispatchMode
        asset = self._asset(storage_mwh=4.0, soc=4.0)
        interval = asset.dispatch(dt.date(2023, 1, 1), 35, DispatchMode.DISCHARGE, 2.0, 200.0)
        self.assertAlmostEqual(interval.revenue_gbp, 200.0)  # 1MWh * £200/MWh

    def test_dispatch_charge_reduces_soc(self):
        from company.market.flexible_asset import DispatchMode
        asset = self._asset(storage_mwh=4.0, soc=4.0, efficiency=100.0)
        asset.dispatch(dt.date(2023, 1, 1), 35, DispatchMode.DISCHARGE, 2.0, 100.0)
        self.assertAlmostEqual(asset.current_soc_mwh, 3.0)  # 4 - 1MWh

    def test_total_revenue_gbp_year_filter(self):
        from company.market.flexible_asset import DispatchMode
        asset = self._asset(storage_mwh=4.0, soc=4.0, efficiency=100.0)
        asset.dispatch(dt.date(2023, 1, 1), 35, DispatchMode.DISCHARGE, 2.0, 100.0)
        asset.dispatch(dt.date(2024, 1, 1), 35, DispatchMode.DISCHARGE, 2.0, 150.0)
        self.assertAlmostEqual(asset.total_revenue_gbp(2023), 100.0)

    def test_asset_summary_structure(self):
        asset = self._asset()
        s = asset.asset_summary(2023)
        self.assertIn("asset_id", s)
        self.assertIn("capacity_mw", s)
        self.assertIn("current_soc_pct", s)
        self.assertIn("total_revenue_gbp", s)


class TestDESNZReturns(unittest.TestCase):

    def test_sdr_total_customers(self):
        from company.regulatory.desnz_returns import SupplierDataReturn
        sdr = SupplierDataReturn(
            reference_month="2023-06",
            electricity_customers=1000,
            gas_customers=800,
            dual_fuel_customers=600,
            smart_meter_customers=400,
            prepayment_meter_customers=100,
            fixed_tariff_customers=700,
            variable_tariff_customers=500,
        )
        # total = elec + gas - dual = 1000 + 800 - 600 = 1200
        self.assertEqual(sdr.total_customers, 1200)

    def test_sdr_smart_meter_pct(self):
        from company.regulatory.desnz_returns import SupplierDataReturn
        sdr = SupplierDataReturn("2023-06", 1000, 500, 300, 600, 0, 800, 700)
        # total = 1000 + 500 - 300 = 1200; smart_meter_pct = 600/1200*100 = 50.0
        self.assertAlmostEqual(sdr.smart_meter_pct, 50.0)

    def test_fuel_poverty_rate_pct(self):
        from company.regulatory.desnz_returns import FuelPovertyDeclaration
        fp = FuelPovertyDeclaration(2023, 1000, 150)
        self.assertAlmostEqual(fp.fuel_poverty_rate_pct, 15.0)

    def test_fuel_poverty_rate_zero_when_no_customers(self):
        from company.regulatory.desnz_returns import FuelPovertyDeclaration
        fp = FuelPovertyDeclaration(2023, 0, 0)
        self.assertAlmostEqual(fp.fuel_poverty_rate_pct, 0.0)

    def test_estimate_fuel_poor_customers_above_threshold(self):
        from company.regulatory.desnz_returns import estimate_fuel_poor_customers
        result = estimate_fuel_poor_customers(1000, 4000.0)
        self.assertGreater(result, 0)

    def test_estimate_fuel_poor_customers_below_threshold(self):
        from company.regulatory.desnz_returns import estimate_fuel_poor_customers
        result = estimate_fuel_poor_customers(1000, 500.0)
        self.assertEqual(result, 0)

    def test_carbon_intensity_pure_renewable(self):
        from company.regulatory.desnz_returns import CarbonIntensityReturn
        cir = CarbonIntensityReturn(2023, 1_000_000, 1_000_000, 0, 0, 0, 0)
        self.assertAlmostEqual(cir.co2_intensity_g_per_kwh, 15.0)

    def test_carbon_intensity_pure_gas(self):
        from company.regulatory.desnz_returns import CarbonIntensityReturn
        cir = CarbonIntensityReturn(2023, 1_000_000, 0, 0, 1_000_000, 0, 0)
        self.assertAlmostEqual(cir.co2_intensity_g_per_kwh, 490.0)

    def test_renewable_pct(self):
        from company.regulatory.desnz_returns import CarbonIntensityReturn
        cir = CarbonIntensityReturn(2023, 1_000_000, 400_000, 0, 600_000, 0, 0)
        self.assertAlmostEqual(cir.renewable_pct, 40.0)

    def test_sdr_submitted_false_by_default(self):
        from company.regulatory.desnz_returns import SupplierDataReturn
        sdr = SupplierDataReturn("2023-06", 500, 300, 200, 100, 50, 400, 200)
        self.assertFalse(sdr.submitted)


if __name__ == "__main__":
    unittest.main()
