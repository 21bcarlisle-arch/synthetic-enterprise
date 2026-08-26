"""Phase 27b: CCL (Climate Change Levy) for business electricity customers.

RE-PINNED 2026-08-17 against the statute
(WORKER_FINDING_THE_ELECTRICITY_LEVY_TABLE_DIVERGES_FROM_THE_STATUTE_ITS_GAS_TWIN_MATCHES).
Five assertions here pinned the mis-transcribed table, and one of them —
`test_ccl_april_2020_step_change` — asserted a RISE in April 2020 that the statute records as a
CUT (FA2020 s.92: 0.00847 -> 0.00811). These tests are part of why the defect was durable: a
value test that pins whatever the table happens to say converts a transcription error into a
specified behaviour, and then defends it. The values below now come from
docs/domain_artefact_library/regulatory/ccl_main_rates.json, which carries the legislation URL
per year; tests/simulation/test_policy_cost_values_vs_source.py is the control that holds the
table to it. The BEHAVIOURAL assertions here (resi exemption, SME==I&C, obligation-year basis,
settlement plumbing) were correct and are unchanged in intent.
"""

import pytest

from simulation.policy_costs import (
    _CCL_ELECTRICITY_RATE_BY_YEAR,
    get_ccl_per_mwh,
)


def test_ccl_resi_exempt():
    """Domestic (resi) electricity is exempt from CCL."""
    assert get_ccl_per_mwh("2021-06-01", segment="resi") == 0.0
    assert get_ccl_per_mwh("2016-01-01", segment="resi") == 0.0
    assert get_ccl_per_mwh("2024-01-01", segment="resi") == 0.0


def test_ccl_business_segments_pay_main_rate():
    """SME and I&C customers pay the main CCL rate. FA2020 s.93: £0.00775/kWh from 1 Apr 2021."""
    rate_2021 = get_ccl_per_mwh("2021-06-01", segment="SME")
    assert rate_2021 == pytest.approx(7.75)
    rate_ic = get_ccl_per_mwh("2021-06-01", segment="I&C")
    assert rate_ic == pytest.approx(7.75)


def test_ccl_april_2019_step_change_up_then_april_2020_cut():
    """The real shape: a SPIKE in April 2019 and a TAPER after — not a monotonic climb.

    This replaces a test that asserted the step-change was in April 2020 and was a rise. Both
    halves were wrong: the Budget-2016 rebalancing raised electricity CCL from £5.83 to £8.47 on
    1 April 2019 (FA2016 s.147), and 1 April 2020 CUT it to £8.11 (FA2020 s.92) as gas CCL
    climbed to meet it. Asserting the direction as well as the levels is deliberate — the old
    table's error was a wrong SHAPE, and only a direction assertion can fail on that.
    """
    oy_2018 = get_ccl_per_mwh("2018-12-01", segment="SME")   # OY 2018-19
    oy_2019 = get_ccl_per_mwh("2019-12-01", segment="SME")   # OY 2019-20
    oy_2020 = get_ccl_per_mwh("2020-12-01", segment="SME")   # OY 2020-21
    assert oy_2018 == pytest.approx(5.83)
    assert oy_2019 == pytest.approx(8.47)
    assert oy_2020 == pytest.approx(8.11)
    assert oy_2019 > oy_2018, "April 2019 was the step UP"
    assert oy_2020 < oy_2019, "April 2020 was a CUT, not a rise"


def test_ccl_2016_rate():
    """CCL electricity rate for 2016-17 obligation year.

    NOTE: 0.559 p/kWh is the one electricity figure still marked `recalled` in the commons —
    not fetched, and an open item there. Pinned so the table cannot drift silently, but it is
    weaker evidence than the years around it.
    """
    assert get_ccl_per_mwh("2016-06-01", segment="SME") == pytest.approx(5.59)


def test_ccl_uses_obligation_year_not_calendar_year():
    """CCL year is Apr-Mar. Jan 2020 is in OY 2019-20 (key 2019), not 2020.

    A sharper probe than it was: OY 2019 (8.47) and OY 2020 (8.11) now differ by 0.36, and in
    opposite direction to the old table's monotonic climb, so keying this date on the calendar
    year fails loudly instead of by 1.06 in the direction the reader would expect.
    """
    jan_2020 = get_ccl_per_mwh("2020-01-15", segment="SME")  # OY 2019-20 → key 2019
    assert jan_2020 == pytest.approx(8.47)  # 2019 rate, not 2020 rate (8.11)


def test_ccl_all_years_defined():
    """All years 2016-2024 have CCL rates defined."""
    for year in range(2016, 2025):
        assert year in _CCL_ELECTRICITY_RATE_BY_YEAR


def test_ccl_settlement_record_has_ccl_field():
    """Settlement records for business customers include ccl_gbp field."""
    from unittest.mock import patch

    from simulation.hedged_settlement import run_hedged_term

    # Simple 1-day price record
    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def flat_shape(date_str):
        return [10.0] * 48  # 10 kWh per period

    records = run_hedged_term(
        "C_IC1", "2021-06-01", "2021-06-02",
        100.0, 80.0, 0.85, 0.0, flat_shape, price_records,
        segment="I&C",
    )
    assert len(records) > 0
    assert "ccl_gbp" in records[0]
    assert records[0]["ccl_gbp"] > 0  # I&C pays CCL


def test_ccl_resi_settlement_record_ccl_zero():
    """Settlement records for resi customers have ccl_gbp = 0."""
    from simulation.hedged_settlement import run_hedged_term as rht
    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def flat_shape(date_str):
        return [10.0] * 48

    records = rht(
        "C1", "2021-06-01", "2021-06-02",
        100.0, 80.0, 0.85, 0.0, flat_shape, price_records,
        segment="resi",
    )
    assert len(records) > 0
    assert "ccl_gbp" in records[0]
    assert records[0]["ccl_gbp"] == pytest.approx(0.0)


def test_ccl_included_in_policy_cost():
    """policy_cost_gbp includes CCL for business customers."""
    from simulation.hedged_settlement import run_hedged_term as rht
    price_records = [
        {"settlementDate": "2021-06-01", "settlementPeriod": sp, "systemSellPrice": 80.0}
        for sp in range(1, 49)
    ]

    def flat_shape(date_str):
        return [10.0] * 48

    records = rht(
        "C_IC1", "2021-06-01", "2021-06-02",
        100.0, 80.0, 0.85, 0.0, flat_shape, price_records,
        segment="I&C",
    )
    rec = records[0]
    expected_policy = (
        rec["ro_levy_gbp"] + rec["cfd_levy_gbp"] + rec["ccl_gbp"]
        + rec.get("cm_levy_gbp", 0.0) + rec.get("fit_levy_gbp", 0.0)
        + rec.get("mutualization_levy_gbp", 0.0)
    )
    assert rec["policy_cost_gbp"] == pytest.approx(expected_policy)


def test_ccl_fell_after_the_2019_peak():
    """Was `test_ccl_increases_after_2020`, asserting the opposite of the statute.

    OY 2019 is the peak of the electricity main rate (£8.47) and every year since is lower.
    Kept as a direction test rather than deleted, because the defect was directional.
    """
    rate_2019 = get_ccl_per_mwh("2019-06-01", segment="I&C")
    rate_2020 = get_ccl_per_mwh("2020-06-01", segment="I&C")
    assert rate_2020 < rate_2019
    assert rate_2019 == max(
        get_ccl_per_mwh(f"{y}-06-01", segment="I&C") for y in range(2016, 2025)
    ), "OY 2019 is the peak of the published electricity main rate"


def test_ccl_sme_equals_ic_rate():
    rate_sme = get_ccl_per_mwh("2022-01-01", segment="sme")
    rate_ic = get_ccl_per_mwh("2022-01-01", segment="I&C")
    assert rate_sme == pytest.approx(rate_ic)


def test_ccl_rate_positive_for_all_business_years():
    for year in range(2016, 2025):
        rate = get_ccl_per_mwh(f"{year}-06-01", segment="I&C")
        assert rate > 0


# 13. CCL rate for electricity is positive for I&C 2023
def test_ccl_ic_2023_positive():
    from simulation.policy_costs import get_ccl_per_mwh
    rate = get_ccl_per_mwh("2023-06-01", segment="I&C")
    assert rate > 0.0


# 14. CCL electricity dict has at least one year entry
def test_ccl_electricity_rate_table_nonempty():
    from simulation.policy_costs import _CCL_ELECTRICITY_RATE_BY_YEAR
    assert len(_CCL_ELECTRICITY_RATE_BY_YEAR) > 0


# 15. CCL rate for 2016 is non-negative
def test_ccl_2016_nonnegative():
    from simulation.policy_costs import get_ccl_per_mwh
    rate = get_ccl_per_mwh("2016-01-01", segment="I&C")
    assert rate >= 0.0
