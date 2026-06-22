"""Phase 31a: Feed-in Tariff (FiT) levelisation levy tests.

FiT applies to ALL electricity demand segments — no domestic exemption.
Obligation year runs Apr-Mar (same as RO/CM). Rising trend 2016→2024.
Key dip: 2021/22 (£6.01/MWh) after 2020/21 peak (£7.10/MWh) — lower
generation tariffs on newer post-2016 installs entering the scheme.
"""

import pytest

from simulation.policy_costs import get_fit_levy_per_mwh
from simulation.hedged_settlement import run_hedged_term


# ── spot rate checks ──────────────────────────────────────────────────────────

def test_fit_rate_2021():
    """2021/22 is the post-peak dip — npower reconciled 0.601 p/kWh = £6.01/MWh."""
    rate = get_fit_levy_per_mwh("2021-06-15")
    assert abs(rate - 6.01) < 0.01


def test_fit_rate_2022():
    """2022/23 rebounds to £7.25/MWh — npower reconciled 0.725 p/kWh."""
    rate = get_fit_levy_per_mwh("2022-08-01")
    assert abs(rate - 7.25) < 0.01


def test_fit_rate_2023():
    """2023/24 highest in npower series — npower reconciled 0.763 p/kWh = £7.63/MWh."""
    rate = get_fit_levy_per_mwh("2023-11-30")
    assert abs(rate - 7.63) < 0.01


def test_fit_rate_2024():
    """2024/25 initial billing rate 0.847 p/kWh = £8.47/MWh."""
    rate = get_fit_levy_per_mwh("2024-07-01")
    assert abs(rate - 8.47) < 0.01


def test_fit_rate_2019():
    """2019/20: £1.60bn ÷ 245 TWh = £6.40/MWh (medium confidence)."""
    rate = get_fit_levy_per_mwh("2019-09-01")
    assert abs(rate - 6.40) < 0.01


def test_fit_rate_2016():
    """2016/17 lowest rate — smallest installed base: £4.10/MWh."""
    rate = get_fit_levy_per_mwh("2016-05-01")
    assert abs(rate - 4.10) < 0.01


# ── obligation year boundary ──────────────────────────────────────────────────

def test_fit_oy_boundary_jan_uses_prior_year():
    """Jan 2022 is in 2021/22 OY — should return 2021 rate (£6.01/MWh)."""
    rate = get_fit_levy_per_mwh("2022-01-15")
    assert abs(rate - 6.01) < 0.01


def test_fit_oy_boundary_apr_uses_new_year():
    """Apr 2022 starts 2022/23 OY — should return 2022 rate (£7.25/MWh)."""
    rate = get_fit_levy_per_mwh("2022-04-01")
    assert abs(rate - 7.25) < 0.01


def test_fit_oy_boundary_mar_uses_prior_year():
    """Mar 2023 is still in 2022/23 OY — should return 2022 rate (£7.25/MWh)."""
    rate = get_fit_levy_per_mwh("2023-03-31")
    assert abs(rate - 7.25) < 0.01


# ── clamp / range behaviour ───────────────────────────────────────────────────

def test_fit_pre_2016_clamps_to_2016():
    """Dates before 2016 OY clamp to lowest known rate."""
    rate_2010 = get_fit_levy_per_mwh("2010-06-01")
    rate_2016 = get_fit_levy_per_mwh("2016-04-01")
    assert abs(rate_2010 - rate_2016) < 1e-9


def test_fit_post_2024_clamps_to_2024():
    """Dates after 2024 OY clamp to highest known rate."""
    rate_2030 = get_fit_levy_per_mwh("2030-01-01")
    rate_2024 = get_fit_levy_per_mwh("2024-04-01")
    assert abs(rate_2030 - rate_2024) < 1e-9


def test_all_fit_rates_positive():
    """All FiT levy rates must be positive (unlike CfD which can be negative)."""
    for year in range(2016, 2025):
        rate = get_fit_levy_per_mwh(f"{year}-06-01")
        assert rate > 0, f"FiT rate for {year} should be positive, got {rate}"


def test_fit_trend_rising_2016_to_2020():
    """Rate rises 2016→2020 as installed fleet grew."""
    r2016 = get_fit_levy_per_mwh("2016-06-01")
    r2020 = get_fit_levy_per_mwh("2020-06-01")
    assert r2020 > r2016, f"Expected 2020 ({r2020}) > 2016 ({r2016})"


def test_fit_2021_lower_than_2020():
    """2021 dips below 2020 — characteristic FiT pattern (lower tariffs on newer installs)."""
    r2020 = get_fit_levy_per_mwh("2020-06-01")
    r2021 = get_fit_levy_per_mwh("2021-06-01")
    assert r2021 < r2020, f"Expected 2021 ({r2021}) < 2020 ({r2020})"


# ── settlement record integration ─────────────────────────────────────────────

def _make_price_records(date_str: str, price: float = 80.0) -> list[dict]:
    return [
        {"settlementDate": date_str, "settlementPeriod": sp, "systemSellPrice": price}
        for sp in range(1, 49)
    ]


def _flat_shape(_date):
    return [1.0] * 48


def test_settlement_records_have_fit_levy_gbp():
    """Settlement records must include fit_levy_gbp (Phase 31a)."""
    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-06-01",
        term_end_date="2022-06-02",
        fixed_tariff_rate_gbp_per_mwh=150.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=_flat_shape,
        system_price_records=_make_price_records("2022-06-01"),
        segment="resi",
    )
    assert len(records) == 48
    assert "fit_levy_gbp" in records[0], f"fit_levy_gbp missing from record keys: {list(records[0].keys())}"


def test_fit_included_in_policy_cost():
    """policy_cost_gbp must equal RO + CfD + CCL + CM + FiT for every record."""
    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-06-01",
        term_end_date="2022-06-02",
        fixed_tariff_rate_gbp_per_mwh=150.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=_flat_shape,
        system_price_records=_make_price_records("2022-06-01"),
        segment="resi",
    )
    for rec in records:
        expected = (
            rec["ro_levy_gbp"] + rec["cfd_levy_gbp"]
            + rec.get("ccl_gbp", 0.0)
            + rec.get("cm_levy_gbp", 0.0)
            + rec.get("fit_levy_gbp", 0.0)
        )
        assert abs(rec["policy_cost_gbp"] - expected) < 1e-9, (
            f"policy_cost_gbp={rec['policy_cost_gbp']:.9f} != expected={expected:.9f}"
        )


def test_fit_applies_to_resi_customer():
    """FiT has no domestic exemption — resi settlement records have fit_levy_gbp > 0."""
    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2021-06-01",
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=70.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=_flat_shape,
        system_price_records=_make_price_records("2021-06-01"),
        segment="resi",
    )
    fit_total = sum(r["fit_levy_gbp"] for r in records)
    assert fit_total > 0, "Resi customer should pay FiT levy (no domestic exemption)"
    # 2021 OY rate = £6.01/MWh; 48 periods × 1kWh = 0.048 MWh
    expected = 6.01 * 0.048
    assert abs(fit_total - expected) < 0.001


def test_fit_value_per_period_2022():
    """Verify FiT levy per settlement period at known 2022 rate."""
    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2022-06-01",
        term_end_date="2022-06-02",
        fixed_tariff_rate_gbp_per_mwh=200.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=_flat_shape,
        system_price_records=_make_price_records("2022-06-01"),
        segment="resi",
    )
    # 2022 OY rate = £7.25/MWh; 1 kWh per period = 0.001 MWh
    expected_per_period = 7.25 * 0.001
    assert abs(records[0]["fit_levy_gbp"] - expected_per_period) < 1e-9


def test_policy_costs_section_shows_fit_column():
    """Annual report _section_policy_costs must show FiT column when fit_levy_gbp present."""
    from saas.reporting.annual_report import _section_policy_costs
    data = {
        "years": {
            "2022": {
                "ro_levy_gbp": 1000.0,
                "cfd_levy_gbp": -200.0,
                "ccl_gbp": 150.0,
                "cm_levy_gbp": 80.0,
                "fit_levy_gbp": 300.0,
                "policy_cost_gbp": 1330.0,
            }
        }
    }
    result = _section_policy_costs(data)
    assert "FiT levy" in result, "Section should include FiT levy column"
    assert "31a" in result, "Section header should reference Phase 31a"
    assert "300" in result, "FiT levy total should appear in table"


def test_policy_costs_backward_compat_no_fit():
    """Pre-31a run data (no fit_levy_gbp key) should not show FiT column."""
    from saas.reporting.annual_report import _section_policy_costs
    data = {
        "years": {
            "2022": {
                "ro_levy_gbp": 1000.0,
                "cfd_levy_gbp": -200.0,
                "ccl_gbp": 100.0,
                "cm_levy_gbp": 50.0,
                "policy_cost_gbp": 950.0,
            }
        }
    }
    result = _section_policy_costs(data)
    assert "FiT" not in result
    assert "31a" not in result
    assert "RO + CfD + CCL + CM" in result
