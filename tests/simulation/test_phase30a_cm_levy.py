"""Phase 30a: Capacity Market (CM) levy for all electricity demand customers."""

import json

import pytest

from simulation.policy_costs import (
    _CM_LEVY_ARTEFACT,
    _CM_LEVY_BY_YEAR,
    get_cm_levy_per_mwh,
)


def test_cm_levy_2017():
    """2017/18: £1.10/MWh — first T-4 delivery year prep, Annex 9 direct."""
    assert get_cm_levy_per_mwh("2017-06-01") == pytest.approx(1.10)


def test_cm_levy_2018():
    """2018/19: £3.67/MWh — first full T-4 delivery year (T-4 at £19.40/kW)."""
    assert get_cm_levy_per_mwh("2018-06-01") == pytest.approx(3.67)


def test_cm_levy_2020():
    """2020/21: £5.86/MWh — T-4 at £22.50/kW, most expensive T-4 in window."""
    assert get_cm_levy_per_mwh("2020-06-01") == pytest.approx(5.86)


def test_cm_levy_2021():
    """2021/22: £4.67/MWh — cheapest year; 2017 T-4 cleared at only £8.40/kW."""
    assert get_cm_levy_per_mwh("2021-06-01") == pytest.approx(4.67)


def test_cm_levy_2022():
    """2022/23: £3.37/MWh — T-4 suspended; T-3 + small high-price T-1."""
    assert get_cm_levy_per_mwh("2022-06-01") == pytest.approx(3.37)


def test_cm_levy_oy_boundary_jan():
    """Jan dates use prior OY — Jan 2022 → OY 2021/22 → £4.67/MWh."""
    assert get_cm_levy_per_mwh("2022-01-15") == pytest.approx(4.67)


def test_cm_levy_oy_boundary_apr():
    """Apr dates use current OY — Apr 2022 → OY 2022/23 → £3.37/MWh."""
    assert get_cm_levy_per_mwh("2022-04-01") == pytest.approx(3.37)


def test_all_years_defined():
    """Every year Annex 9 covers has a rate, with no hole in the middle.

    KEYED TO THE RECORD, NOT TO 2024. This asserted `range(2016, 2025)` until 2026-09-07, which
    was a floor rather than a span: it stayed green when the record GREW and could not notice a
    year appearing out of order. The record now runs to 2025/26 and will keep moving.
    """
    years = sorted(_CM_LEVY_BY_YEAR)
    assert years[0] == 2016, "the record starts at 2016/17; the sim clamps below it"
    assert years == list(range(years[0], years[-1] + 1)), (
        f"the CM levy record has a hole in it: {years}. Every obligation year between the first "
        "and last must be priced, because the sim buckets every settlement record by date and a "
        "missing middle year would silently clamp to the wrong end"
    )


def test_clamps_pre_2016():
    """Dates before 2016 clamp to the 2016 rate."""
    assert get_cm_levy_per_mwh("2010-01-01") == pytest.approx(_CM_LEVY_BY_YEAR[2016])


def test_clamps_past_the_published_record():
    """Dates past Annex 9's coverage clamp to the LAST PUBLISHED year, whichever that is.

    RENAMED AND RE-KEYED 2026-09-07, from `test_clamps_post_2024` asserting
    `_CM_LEVY_BY_YEAR[2024]`. That is the shape CLAUDE.md names: pinned to today's answer, so it
    went red when the record became MORE complete (v1.11 added 2025/26) while saying nothing
    about the property it existed for. The carry-forward is the world's own reading -- the
    company side returns None out here instead -- and what it promises is "the nearest published
    year", not "2024".

    NOT `_CM_LEVY_BY_YEAR[max(_CM_LEVY_BY_YEAR)]`, which was the first re-key written here and
    was withdrawn before it landed: `get_cm_levy_per_mwh` computes that exact expression, so the
    assertion would have restated the implementation and only survived as a control by accident.
    The last published year is taken from the COMMONS ARTEFACT instead -- an independent route to
    the same boundary -- and both sides go through the public reader.
    """
    last_published = max(
        int(row["obligation_year"])
        for row in json.loads(_CM_LEVY_ARTEFACT.read_text())["levy_gbp_per_mwh"]
    )
    assert get_cm_levy_per_mwh("2030-01-01") == pytest.approx(
        get_cm_levy_per_mwh(f"{last_published}-06-01")
    )
    # ...and it is not clamping to the wrong END. Without this a table that had collapsed to a
    # single repeated rate, or a clamp that returned the FIRST year, would pass the line above.
    assert get_cm_levy_per_mwh("2030-01-01") != pytest.approx(
        get_cm_levy_per_mwh("2016-06-01")
    )


def test_all_rates_positive():
    """All CM levy rates are positive (no rebate mechanism unlike CfD)."""
    for year, rate in _CM_LEVY_BY_YEAR.items():
        assert rate > 0, f"Year {year} rate {rate} should be positive"


def test_settlement_record_has_cm_levy_field():
    """Settlement records include cm_levy_gbp field (Phase 30a)."""
    from simulation.hedged_settlement import run_hedged_term

    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def shape(_date):
        return [1.0] * 48

    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2021-06-01",
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=shape,
        system_price_records=price_records,
        segment="resi",
    )
    assert len(records) == 48
    assert "cm_levy_gbp" in records[0]
    # resi 2021: OY 2021/22 → £4.67/MWh; 1 kWh = 0.001 MWh per period
    expected_per_period = 4.67 * (1.0 / 1000)
    assert records[0]["cm_levy_gbp"] == pytest.approx(expected_per_period)


def test_cm_levy_included_in_policy_cost():
    """policy_cost_gbp includes CM levy alongside RO, CfD, and CCL."""
    from simulation.hedged_settlement import run_hedged_term

    price_records = [
        {"settlementDate": "2020-06-01", "settlementPeriod": sp, "systemSellPrice": 50.0}
        for sp in range(1, 49)
    ]

    def shape(_date):
        return [1.0] * 48

    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2020-06-01",
        term_end_date="2020-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=50.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=shape,
        system_price_records=price_records,
        segment="resi",
    )
    rec = records[0]
    expected_policy = (
        rec["ro_levy_gbp"] + rec["cfd_levy_gbp"] + rec["ccl_gbp"]
        + rec["cm_levy_gbp"] + rec.get("fit_levy_gbp", 0.0)
    )
    assert rec["policy_cost_gbp"] == pytest.approx(expected_policy)


def test_cm_levy_applies_to_resi():
    """CM levy applies to domestic (resi) customers — no exemption unlike CCL."""
    from simulation.hedged_settlement import run_hedged_term
    from simulation.policy_costs import get_ccl_per_mwh

    # Resi CCL should be 0; resi CM should be non-zero
    assert get_ccl_per_mwh("2021-06-01", segment="resi") == 0.0
    assert get_cm_levy_per_mwh("2021-06-01") > 0.0

    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]
    records = run_hedged_term(
        customer_id="C1",
        term_start_date="2021-06-01",
        term_end_date="2021-06-02",
        fixed_tariff_rate_gbp_per_mwh=100.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.85,
        monthly_cost_of_capital_gbp=0.0,
        consumption_shape=lambda _: [1.0] * 48,
        system_price_records=price_records,
        segment="resi",
    )
    assert records[0]["ccl_gbp"] == pytest.approx(0.0)    # resi CCL exempt
    assert records[0]["cm_levy_gbp"] > 0.0                 # resi CM not exempt


def test_policy_costs_section_shows_cm_column():
    """_section_policy_costs renders CM levy column when cm_levy_gbp data present."""
    from saas.reporting.annual_report import _section_policy_costs

    data = {
        "years": {
            "2021": {
                "ro_levy_gbp": 5000.0,
                "cfd_levy_gbp": 300.0,
                "ccl_gbp": 200.0,
                "cm_levy_gbp": 800.0,
                "policy_cost_gbp": 6300.0,
            },
        }
    }
    result = _section_policy_costs(data)
    assert "CM levy" in result or "cm" in result.lower()
    assert "6,300" in result or "6300" in result
    assert "800" in result


def test_policy_costs_section_backward_compat_no_cm():
    """_section_policy_costs works correctly when no cm_levy_gbp in data (pre-30a runs)."""
    from saas.reporting.annual_report import _section_policy_costs

    data = {
        "years": {
            "2021": {
                "ro_levy_gbp": 5000.0,
                "cfd_levy_gbp": 300.0,
                "ccl_gbp": 200.0,
                "policy_cost_gbp": 5500.0,
            },
        }
    }
    result = _section_policy_costs(data)
    assert "RO + CfD + CCL" in result
    assert "CM" not in result
