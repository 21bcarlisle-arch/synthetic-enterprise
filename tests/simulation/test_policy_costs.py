"""Tests for simulation.policy_costs — Phase 21a."""

import pytest
from simulation.policy_costs import (
    get_cfd_levy_per_mwh,
    get_electricity_policy_cost_per_mwh,
    get_ro_cost_per_mwh,
)


class TestROCost:
    def test_2016_obligation_year(self):
        # OY 2016-17: starts April 2016. April-Dec 2016 → OY key 2016.
        assert abs(get_ro_cost_per_mwh("2016-07-01") - 15.6) < 1e-9

    def test_jan_mar_use_prior_oy(self):
        # Jan 2017 is still OY 2016-17 (Apr 2016 – Mar 2017) → key 2016.
        assert abs(get_ro_cost_per_mwh("2017-01-15") - 15.6) < 1e-9

    def test_april_advances_oy(self):
        # April 2017 starts OY 2017-18 → key 2017.
        assert abs(get_ro_cost_per_mwh("2017-04-01") - 18.6) < 1e-9

    def test_2024_highest_known(self):
        assert abs(get_ro_cost_per_mwh("2024-09-01") - 31.8) < 1e-9

    def test_clamp_below_range(self):
        # Before 2016: clamp to 2016 value.
        assert abs(get_ro_cost_per_mwh("2010-06-01") - 15.6) < 1e-9

    def test_clamp_above_range(self):
        # After 2024: clamp to 2024 value.
        assert abs(get_ro_cost_per_mwh("2030-01-01") - 31.8) < 1e-9


class TestCFDLevy:
    def test_2016_near_zero(self):
        assert abs(get_cfd_levy_per_mwh("2016-03-01") - 0.1) < 1e-9

    def test_2022_negative(self):
        # 2022 is the crisis rebate year — CfD levy is negative.
        assert get_cfd_levy_per_mwh("2022-06-01") < 0.0
        assert abs(get_cfd_levy_per_mwh("2022-06-01") - (-5.0)) < 1e-9

    def test_2024_highest_positive(self):
        assert abs(get_cfd_levy_per_mwh("2024-01-01") - 11.0) < 1e-9

    def test_clamp_below_range(self):
        assert abs(get_cfd_levy_per_mwh("2010-01-01") - 0.1) < 1e-9

    def test_clamp_above_range(self):
        assert abs(get_cfd_levy_per_mwh("2030-01-01") - 11.0) < 1e-9


class TestTotalPolicyCost:
    def test_2022_total_is_ro_minus_cfd_rebate(self):
        # 2022: RO £26 + CfD -£5 = £21/MWh (rebate reduces total)
        total = get_electricity_policy_cost_per_mwh("2022-06-01")
        expected = 26.0 + (-5.0)
        assert abs(total - expected) < 1e-9

    def test_2024_total_additive(self):
        # 2024: RO £31.8 + CfD £11 = £42.8/MWh
        total = get_electricity_policy_cost_per_mwh("2024-06-01")
        assert abs(total - 42.8) < 1e-9

    def test_2016_total_small(self):
        # 2016: £15.6 + £0.1 = £15.7/MWh
        total = get_electricity_policy_cost_per_mwh("2016-06-01")
        assert abs(total - 15.7) < 1e-9


class TestPolicyInSettlementRecords:
    """Integration: policy cost fields appear in hedged_settlement records."""

    def test_settlement_records_have_policy_fields(self):
        from simulation.hedged_settlement import run_hedged_term

        date_str = "2022-06-01"  # 2022: negative CfD
        records_stub = [
            {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 300.0}
            for p in range(1, 49)
        ]
        shape_stub = lambda d: [1.0] * 48  # 1 kWh per period

        result = run_hedged_term(
            "TEST", date_str, "2022-06-02",
            120.0, 100.0, 0.85, 0.0,
            shape_stub, records_stub,
        )

        assert len(result) == 48
        rec = result[0]
        assert "ro_levy_gbp" in rec
        assert "cfd_levy_gbp" in rec
        assert "ccl_gbp" in rec
        assert "cm_levy_gbp" in rec
        assert "fit_levy_gbp" in rec
        assert "policy_cost_gbp" in rec
        # In 2022, CfD is negative so cfd_levy_gbp < 0
        assert rec["cfd_levy_gbp"] < 0.0
        # Phase 31a: policy_cost_gbp = ro + cfd + ccl + cm + fit
        expected_policy = (
            rec["ro_levy_gbp"] + rec["cfd_levy_gbp"]
            + rec.get("ccl_gbp", 0.0) + rec.get("cm_levy_gbp", 0.0)
            + rec.get("fit_levy_gbp", 0.0)
        )
        assert abs(rec["policy_cost_gbp"] - expected_policy) < 1e-9

    def test_net_margin_deducts_policy_cost(self):
        from simulation.hedged_settlement import run_hedged_term

        date_str = "2024-01-01"  # 2024: high policy costs
        records_stub = [
            {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 100.0}
            for p in range(1, 49)
        ]
        shape_stub = lambda d: [1.0] * 48

        result = run_hedged_term(
            "TEST", date_str, "2024-01-02",
            200.0, 100.0, 0.85, 0.0,
            shape_stub, records_stub,
        )

        for rec in result:
            # Phase 29a: net_margin_gbp = margin_gbp - policy_cost_gbp - network_cost_gbp - capital_cost_gbp
            expected_net = (
                rec["margin_gbp"] - rec["policy_cost_gbp"]
                - rec["network_cost_gbp"] - rec["capital_cost_gbp"]
            )
            assert abs(rec["net_margin_gbp"] - expected_net) < 1e-9

    def test_2022_cfd_rebate_reduces_policy_cost(self):
        """2022 negative CfD levy means policy_cost_gbp is reduced vs no-rebate total."""
        from simulation.hedged_settlement import run_hedged_term
        from simulation.policy_costs import (
            get_ro_cost_per_mwh, get_cm_levy_per_mwh, get_fit_levy_per_mwh,
        )

        date_str = "2022-06-01"
        records_stub = [
            {"settlementDate": date_str, "settlementPeriod": p, "systemSellPrice": 300.0}
            for p in range(1, 49)
        ]
        shape_stub = lambda d: [1.0] * 48

        result = run_hedged_term(
            "TEST", date_str, "2022-06-02",
            350.0, 300.0, 0.85, 0.0,
            shape_stub, records_stub,
        )

        rec = result[0]
        consumption_mwh = rec["consumption_kwh"] / 1000.0
        # 2022 CfD is a negative rebate — verify it reduces total vs RO+CM+FiT
        ro_cm_fit = (
            get_ro_cost_per_mwh(date_str)
            + get_cm_levy_per_mwh(date_str)
            + get_fit_levy_per_mwh(date_str)
        ) * consumption_mwh
        assert rec["policy_cost_gbp"] < ro_cm_fit, (
            "2022 negative CfD should reduce policy_cost below RO+CM+FiT subtotal"
        )
        # Verify CfD is actually negative
        assert rec["cfd_levy_gbp"] < 0


class TestTariffIncludesPolicyCost:
    """price_fixed_tariff includes policy cost in unit rate."""

    def test_policy_cost_added_to_unit_rate(self):
        from saas.tariff_pricing import price_fixed_tariff

        base = price_fixed_tariff(100.0, 2500, "2024-01-01")
        with_policy = price_fixed_tariff(100.0, 2500, "2024-01-01", policy_cost_per_mwh=30.0)
        assert abs(with_policy - base - 30.0) < 1e-9

    def test_zero_policy_cost_unchanged(self):
        from saas.tariff_pricing import price_fixed_tariff

        base = price_fixed_tariff(100.0, 2500, "2020-01-01")
        with_zero = price_fixed_tariff(100.0, 2500, "2020-01-01", policy_cost_per_mwh=0.0)
        assert abs(with_zero - base) < 1e-9
