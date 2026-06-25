"""Phase 56: Gas pass-through customers must have hedge_fraction = 0."""

import pytest
from simulation.gas_settlement import run_gas_term


def _gas_recs(start_day, month, year, spot, n_days):
    return [{"settlementDate": f"{year}-{month:02d}-{start_day+d:02d}", "systemSellPrice": spot}
            for d in range(n_days)]


GAS_RECORDS_LOW = _gas_recs(1, 1, 2021, 20.0, 30)
GAS_RECORDS_HIGH = _gas_recs(1, 10, 2022, 120.0, 30)
GAS_RECORDS_REVERSION = _gas_recs(1, 5, 2023, 30.0, 30)


class TestPassThroughZeroHedge:
    """Pass-through gas uses hf=0: margin = service_fee × volume only."""

    def test_pass_through_hf_zero_positive_margin(self):
        """With hf=0, gross > 0 regardless of spot level."""
        records = run_gas_term(
            customer_id="TEST",
            term_start="2021-01-01",
            term_end="2021-01-30",
            aq_kwh=50000,
            unit_rate_gbp_mwh=20.0,
            hedge_fraction=0.0,
            forward_price=30.0,
            monthly_cost_of_capital_gbp=0.0,
            gas_price_records=GAS_RECORDS_LOW,
            segment="I&C",
            pass_through=True,
        )
        assert sum(r["margin_gbp"] for r in records) > 0

    def test_pass_through_hf_nonzero_windfall_when_spot_above_fwd(self):
        """hf=0.85 with spot>>fwd: margin inflated far above service_fee amount."""
        records = run_gas_term(
            "TEST", "2022-10-01", "2022-10-30", 50000, 120.0,
            0.85, 30.0, 0.0, GAS_RECORDS_HIGH, "I&C", pass_through=True,
        )
        total_margin = sum(r["margin_gbp"] for r in records)
        total_vol_mwh = sum(r["consumption_kwh"] / 1000.0 for r in records)
        service_fee_only = 2.0 * total_vol_mwh
        # Wrong-way hedge inflates margin >> service fee
        assert total_margin > service_fee_only * 5

    def test_pass_through_hf_nonzero_loss_when_spot_below_fwd(self):
        """hf=0.85 with spot<<fwd: catastrophic loss (2023-type reversion)."""
        records = run_gas_term(
            "TEST", "2023-05-01", "2023-05-30", 50000, 120.0,
            0.85, 120.0, 0.0, GAS_RECORDS_REVERSION, "I&C", pass_through=True,
        )
        # cost = 0.85×120 + 0.15×30 = 106.5; revenue = 30 + service ≈ 35 → loss
        assert sum(r["margin_gbp"] for r in records) < 0

    def test_pass_through_hf_zero_cost_equals_spot(self):
        """At hf=0, wholesale_cost = spot × volume (no forward exposure)."""
        records = run_gas_term(
            "TEST", "2021-01-01", "2021-01-07", 50000, 20.0,
            0.0, 30.0, 0.0, GAS_RECORDS_LOW, "I&C", pass_through=True,
        )
        for rec in records:
            expected = rec["consumption_kwh"] / 1000.0 * 20.0
            assert abs(rec["wholesale_cost_gbp"] - expected) < 0.01

    def test_pass_through_hf_zero_margin_stable_across_spot_levels(self):
        """At hf=0, margin per MWh is similar regardless of spot (±tolerance for policy/network)."""
        records_low = run_gas_term(
            "TEST", "2021-01-01", "2021-01-30", 50000, 20.0,
            0.0, 20.0, 0.0, GAS_RECORDS_LOW, "I&C", pass_through=True,
        )
        records_high = run_gas_term(
            "TEST", "2022-10-01", "2022-10-30", 50000, 120.0,
            0.0, 120.0, 0.0, GAS_RECORDS_HIGH, "I&C", pass_through=True,
        )
        vol_low = sum(r["consumption_kwh"] / 1000.0 for r in records_low)
        vol_high = sum(r["consumption_kwh"] / 1000.0 for r in records_high)
        margin_per_mwh_low = sum(r["margin_gbp"] for r in records_low) / vol_low
        margin_per_mwh_high = sum(r["margin_gbp"] for r in records_high) / vol_high
        # Both should be in £2-25/MWh range (service fee + network + policy)
        assert 1.5 < margin_per_mwh_low < 30
        assert 1.5 < margin_per_mwh_high < 30
        # And similar to each other (no spot exposure)
        assert abs(margin_per_mwh_low - margin_per_mwh_high) < 15
