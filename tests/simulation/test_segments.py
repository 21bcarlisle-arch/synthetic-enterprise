"""Tests for Phase 10a segment customer model."""

import pytest

from simulation.segments import (
    ELEC_SEGMENTS,
    GAS_SEGMENTS,
    SEGMENT_BY_ID,
    SEGMENTS,
    CustomerSegment,
    apply_annual_headcount_changes,
)

# ---- Dataclass / property tests ----

def test_segment_total_eac_kwh():
    seg = SEGMENT_BY_ID["resi_standard"]
    assert seg.total_eac_kwh == pytest.approx(seg.headcount * seg.avg_kwh_per_customer)


def test_segment_shape_scale_resi():
    seg = SEGMENT_BY_ID["resi_standard"]
    from simulation.segments import PC1_CALIBRATION_KWH
    assert seg.shape_scale == pytest.approx(seg.avg_kwh_per_customer / PC1_CALIBRATION_KWH)


def test_segment_shape_scale_sme():
    seg = SEGMENT_BY_ID["sme_standard"]
    from simulation.segments import PC3_CALIBRATION_KWH
    assert seg.shape_scale == pytest.approx(seg.avg_kwh_per_customer / PC3_CALIBRATION_KWH)


def test_all_segments_defined():
    sids = {s.segment_id for s in SEGMENTS}
    assert sids == {"resi_standard", "resi_smart", "sme_standard", "sme_smart", "gas_resi"}


def test_elec_gas_split():
    assert len(ELEC_SEGMENTS) == 4
    assert len(GAS_SEGMENTS) == 1
    assert all(s.commodity == "electricity" for s in ELEC_SEGMENTS)
    assert all(s.commodity == "gas" for s in GAS_SEGMENTS)


def test_as_weather_customer_keys():
    seg = SEGMENT_BY_ID["resi_standard"]
    wc = seg.as_weather_customer()
    assert "customer_id" in wc
    assert "location" in wc
    assert "lat" in wc["location"]
    assert "lon" in wc["location"]


def test_segment_by_id_lookup():
    assert SEGMENT_BY_ID["gas_resi"].commodity == "gas"
    assert SEGMENT_BY_ID["sme_smart"].profile_class == 3


# ---- Smart upgrade rates ----

def test_resi_standard_has_upgrades_to():
    seg = SEGMENT_BY_ID["resi_standard"]
    assert seg.upgrades_to == "resi_smart"


def test_resi_smart_no_upgrades_to():
    seg = SEGMENT_BY_ID["resi_smart"]
    assert seg.upgrades_to is None


def test_smart_upgrade_rate_increases_over_time():
    seg = SEGMENT_BY_ID["resi_standard"]
    assert seg.smart_upgrade_rates["2016"] < seg.smart_upgrade_rates["2025"]


# ---- apply_annual_headcount_changes ----

def _initial_headcounts() -> dict[str, int]:
    return {s.segment_id: s.headcount for s in SEGMENTS}


def test_headcount_changes_returns_new_dict():
    initial = _initial_headcounts()
    updated = apply_annual_headcount_changes(initial, "2020")
    assert updated is not initial


def test_headcount_changes_does_not_mutate_input():
    initial = _initial_headcounts()
    original_resi = initial["resi_standard"]
    apply_annual_headcount_changes(initial, "2020")
    assert initial["resi_standard"] == original_resi


def test_standard_headcount_transfers_to_smart():
    initial = {s.segment_id: s.headcount for s in SEGMENTS}
    # Set headcounts to simple known values
    initial["resi_standard"] = 100
    initial["resi_smart"] = 10
    updated = apply_annual_headcount_changes(initial, "2020")
    # 2020 rate is 5%: 5 upgrades from resi_standard → resi_smart
    # (before churn/acquisition)
    # resi_smart should have grown due to upgrades
    assert updated["resi_smart"] > initial["resi_smart"]


def test_headcount_never_drops_below_one():
    initial = {s.segment_id: 1 for s in SEGMENTS}
    updated = apply_annual_headcount_changes(initial, "2020")
    for sid in updated:
        assert updated[sid] >= 1


def test_churn_reduces_headcount_before_acquisition():
    # With headcount=100, churn_rate=0.15 → 15 churned
    # Then acquisition replaces some
    initial = _initial_headcounts()
    initial["resi_standard"] = 100
    updated = apply_annual_headcount_changes(initial, "2020")
    # Net effect should be near break-even (churn replaced by acquisition)
    # Just verify headcount isn't wildly different
    assert 80 <= updated["resi_standard"] <= 150


def test_multi_year_headcount_trend():
    """Smart segments should grow over time due to upgrade flow."""
    headcounts = _initial_headcounts()
    for year in ["2016", "2017", "2018", "2019", "2020"]:
        headcounts = apply_annual_headcount_changes(headcounts, year)
    assert headcounts["resi_smart"] > SEGMENT_BY_ID["resi_smart"].headcount


def test_gas_segment_not_upgraded():
    """Gas residential has no upgrades_to — headcount change is churn + acquisition only."""
    initial = _initial_headcounts()
    initial["gas_resi"] = 100
    updated = apply_annual_headcount_changes(initial, "2020")
    seg = SEGMENT_BY_ID["gas_resi"]
    assert seg.upgrades_to is None
    # Gas should still change (churn + acquisition)
    assert updated["gas_resi"] != 0


# ---- Volume / treasury sizing sanity ----

def test_total_initial_elec_volume():
    total = sum(s.total_eac_kwh for s in ELEC_SEGMENTS)
    # 150*3100 + 20*2800 + 40*35000 + 5*32000 = 465k + 56k + 1.4M + 160k = 2,081,000
    assert total == pytest.approx(2_081_000.0)


def test_total_initial_gas_volume():
    total = sum(s.total_eac_kwh for s in GAS_SEGMENTS)
    # 80 * 13250 = 1,060,000
    assert total == pytest.approx(1_060_000.0)


def test_resi_standard_initial_headcount():
    assert SEGMENT_BY_ID["resi_standard"].headcount == 150


def test_gas_resi_initial_headcount():
    assert SEGMENT_BY_ID["gas_resi"].headcount == 80
