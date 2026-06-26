"""Phase 45b: Gas pass-through bills at actual spot + service fee.

Previously, gas pass-through used unit_rate = company_fwd × (1 + 20% risk premium) + £2/MWh,
creating ~15-20% net margin. True pass-through should bill at daily spot + thin service fee.
"""
import pytest


def _make_gas_records(start="2021-01-01", days=3, price=30.0):
    from datetime import date, timedelta
    d = date.fromisoformat(start)
    return [{"settlementDate": (d + timedelta(i)).isoformat(), "systemSellPrice": price} for i in range(days)]


class TestPassThroughSpotBilling:
    def test_pass_through_uses_spot_not_unit_rate(self):
        """Pass-through revenue uses spot price, not the locked unit_rate."""
        from simulation.gas_settlement import run_gas_term, GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH

        spot = 50.0
        high_unit_rate = 200.0  # company forward with large risk premium
        recs = run_gas_term(
            customer_id="T",
            term_start="2022-01-01",
            term_end="2022-01-02",
            aq_kwh=5_000_000,
            unit_rate_gbp_mwh=high_unit_rate,
            hedge_fraction=0.85,
            forward_price=48.0,
            monthly_cost_of_capital_gbp=0.0,
            gas_price_records=_make_gas_records("2022-01-01", 1, spot),
            segment="I&C",
            pass_through=True,
        )
        assert len(recs) == 1
        r = recs[0]
        # Use actual daily_mwh from record (accounts for I&C seasonal profile)
        daily_mwh = r["consumption_kwh"] / 1000
        # billed energy component = spot + service_fee (not high_unit_rate)
        expected_billed = daily_mwh * (spot + GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH)
        # revenue also includes policy + network passthrough
        energy_revenue = r["revenue_gbp"] - r["gas_policy_cost_gbp"] - r["gas_network_cost_gbp"]
        assert abs(energy_revenue - expected_billed) < 0.01

    def test_pass_through_net_margin_approx_service_fee(self):
        """When spot == forward, pass-through net ≈ service_fee × volume."""
        from simulation.gas_settlement import run_gas_term, GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH

        spot = forward = 40.0
        recs = run_gas_term(
            customer_id="T",
            term_start="2020-06-01",
            term_end="2020-06-02",
            aq_kwh=5_000_000,
            unit_rate_gbp_mwh=60.0,  # irrelevant for pass-through
            hedge_fraction=1.0,       # fully hedged → no spot basis
            forward_price=forward,
            monthly_cost_of_capital_gbp=0.0,
            gas_price_records=_make_gas_records("2020-06-01", 1, spot),
            segment="I&C",
            pass_through=True,
        )
        assert len(recs) == 1
        r = recs[0]
        # Use actual daily_mwh from record (accounts for I&C seasonal profile)
        daily_mwh = r["consumption_kwh"] / 1000
        expected_net = GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH * daily_mwh
        # net should equal service_fee × volume (policy+network cancel, no basis)
        assert abs(r["net_margin_gbp"] - expected_net) < 0.5

    def test_pass_through_net_margin_lower_than_old_model(self):
        """Pass-through net margin should be much lower than when using company_fwd × 1.2."""
        from simulation.gas_settlement import run_gas_term

        # Simulate a case where company_fwd (unit_rate) is 20% above spot forward
        spot = 40.0
        company_fwd_with_premium = 50.0  # unit_rate that old model would have used

        pt_recs = run_gas_term(
            customer_id="T",
            term_start="2020-06-01",
            term_end="2020-06-02",
            aq_kwh=5_000_000,
            unit_rate_gbp_mwh=company_fwd_with_premium,
            hedge_fraction=1.0,
            forward_price=40.0,
            monthly_cost_of_capital_gbp=0.0,
            gas_price_records=_make_gas_records("2020-06-01", 1, spot),
            segment="I&C",
            pass_through=True,
        )
        # old net would have been: (50-40) × daily_mwh = £10/MWh × daily_mwh (large)
        # new net is ≈ service_fee × daily_mwh = £2/MWh × daily_mwh (thin)
        r = pt_recs[0]
        daily_mwh = 5_000_000 / 1000 / 365
        # net should be near £2/MWh × daily_mwh, not £10/MWh × daily_mwh
        assert r["net_margin_gbp"] < 5.0 * daily_mwh

    def test_pass_through_constant_fee_not_default(self):
        """GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH should be 2.0."""
        from simulation.gas_settlement import GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH
        assert GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH == 2.0

    def test_fixed_gas_unaffected(self):
        """Fixed gas term still uses unit_rate for billing, not spot."""
        from simulation.gas_settlement import run_gas_term

        unit_rate = 60.0
        spot = 30.0  # very different from unit_rate
        recs = run_gas_term(
            customer_id="T",
            term_start="2020-06-01",
            term_end="2020-06-02",
            aq_kwh=5_000_000,
            unit_rate_gbp_mwh=unit_rate,
            hedge_fraction=1.0,
            forward_price=55.0,
            monthly_cost_of_capital_gbp=0.0,
            gas_price_records=_make_gas_records("2020-06-01", 1, spot),
            segment="I&C",
            pass_through=False,
        )
        r = recs[0]
        # Use actual daily_mwh from record (accounts for I&C seasonal profile)
        daily_mwh = r["consumption_kwh"] / 1000
        expected_revenue = unit_rate * daily_mwh
        assert abs(r["revenue_gbp"] - expected_revenue) < 0.01

    def test_pass_through_high_spot_passes_through(self):
        """During crisis (high spot), pass-through customer pays the high price."""
        from simulation.gas_settlement import run_gas_term, GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH

        crisis_spot = 300.0
        recs = run_gas_term(
            customer_id="T",
            term_start="2022-01-01",
            term_end="2022-01-02",
            aq_kwh=5_000_000,
            unit_rate_gbp_mwh=50.0,   # old locked rate (irrelevant for pass-through)
            hedge_fraction=0.85,
            forward_price=50.0,        # locked forward much lower than spot
            monthly_cost_of_capital_gbp=0.0,
            gas_price_records=_make_gas_records("2022-01-01", 1, crisis_spot),
            segment="I&C",
            pass_through=True,
        )
        r = recs[0]
        daily_mwh = 5_000_000 / 1000 / 365
        # energy component of bill should reflect crisis spot
        energy_billed = r["revenue_gbp"] - r["gas_policy_cost_gbp"] - r["gas_network_cost_gbp"]
        assert energy_billed > daily_mwh * (crisis_spot + GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH) * 0.99
