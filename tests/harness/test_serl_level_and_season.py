"""The level-and-season cells grade a gas-heated home's electricity against SERL 2022.

Built on synthetic years so the gate stays fast; the live reading over the drawn
homes is `tools/couple_fabric.py --serl 200`.
"""

import datetime as dt

import pytest

from background import fabric_gap_ledger as fgl

YEAR = [dt.date(2022, 1, 1) + dt.timedelta(days=i) for i in range(365)]


def _home(*, peak: float, trough: float = 0.13, winter_over_summer: float = 1.42):
    """A year whose median-of-means profile has `trough` at 04:30 and `peak` at
    18:30 (kWh/h), with each day scaled so January sits `winter_over_summer` above July."""
    shape = [trough] * 48
    shape[fgl.SERL_PEAK_PERIOD] = peak
    days = []
    for d in YEAR:
        # 1.0 in July, winter_over_summer in January, smooth between.
        k = 1.0 + (winter_over_summer - 1.0) * abs(d.month - 7) / 6
        # Scale only the non-trough periods, so the trough and the peak stay at
        # their means over the year.
        mean_k = sum(1.0 + (winter_over_summer - 1.0) * abs(x.month - 7) / 6 for x in YEAR) / 365
        day = [v / 2 for v in shape]
        day = [v * k / mean_k if i != fgl.SERL_TROUGH_PERIOD else v for i, v in enumerate(day)]
        days.append((d, day))
    return days


def _cells(homes):
    return {c.statistic: c for c in fgl.level_and_season_vs_serl(homes)}


def test_every_judged_cell_can_pass_and_can_fail():
    """The whole partition first: a guard that fails everything passes every
    'does it fail' test."""
    real = _cells([_home(peak=0.48)] * 5)
    flat = _cells([_home(peak=0.63, winter_over_summer=1.29)] * 5)
    for name in ("S1_trough_kwh_per_h", "S2_peak_kwh_per_h", "S3_month_max_over_min"):
        assert real[name].verdict is fgl.Verdict.PASS, (name, real[name].value)
    assert flat["S2_peak_kwh_per_h"].verdict is fgl.Verdict.FAIL
    assert flat["S3_month_max_over_min"].verdict is fgl.Verdict.FAIL


def test_the_peak_is_read_in_kwh_per_hour_not_per_half_hour():
    assert _cells([_home(peak=0.48)] * 3)["S2_peak_kwh_per_h"].value == pytest.approx(0.48, abs=0.005)


def test_a_peak_below_serls_lowest_year_fails_too():
    """Two-sided: a world fixed by overshooting is not fixed."""
    assert _cells([_home(peak=0.40)] * 3)["S2_peak_kwh_per_h"].verdict is fgl.Verdict.FAIL


def test_the_annual_level_is_measured_and_not_judged_until_the_months_are_read():
    cell = _cells([_home(peak=0.48)] * 3)["S4_annual_kwh_sum_of_monthly_medians"]
    assert cell.verdict is fgl.Verdict.UNVALIDATED and cell.value > 0
    assert "Table 3" in cell.band.anchor_source


def test_a_part_year_home_is_refused_not_graded():
    with pytest.raises(fgl.InsufficientEvidence, match="twelve"):
        fgl.level_and_season_vs_serl([_home(peak=0.48)[:200]])


def test_a_non_finite_reading_fails_closed():
    assert fgl.SERL_BANDS["S2_peak_kwh_per_h"].judge(float("nan")) is fgl.Verdict.FAIL


def test_every_edge_is_a_published_figure_at_its_published_precision():
    """Each band's edges sit within half a unit in the third decimal of a figure
    its source text names, so an edge cannot be moved without moving the citation."""
    for band in fgl.SERL_BANDS.values():
        if band.anchor is fgl.AnchorStatus.NEED:
            continue
        for edge in (band.low, band.high):
            named = [float(t.rstrip(".,)")) for t in band.anchor_source.replace("/", " ").split()
                     if t.rstrip(".,)").replace(".", "", 1).isdigit() and "." in t]
            assert any(abs(edge - v) <= 0.0005 + 1e-9 for v in named), (band.statistic, edge, named)
