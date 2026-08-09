"""`background/lcl_household_anchors.py` — the external anchors, put on trial.

An anchor is the one number in a control that cannot be derived from anything else
in this repository, so it is the number most able to be wrong without anybody
noticing. Every constant the module exports is RE-DERIVED here from the raw CSV
with INDEPENDENT inline arithmetic — this file deliberately does not call the
module's own quantile, bootstrap or parsing helpers for the values it checks,
because a re-derivation that shares the code it is checking asserts nothing (the
R15 TAUTOLOGY pattern, which this suite's sibling caught inside a test named for
the rule).

Also proven here: every failure mode RAISES. A band whose anchor silently
defaults when the panel is missing, empty, short of columns, or carrying a
non-finite figure is a band with an invented threshold, and an unavailable check
is a FAILED check.
"""

from __future__ import annotations

import csv
import math
import random

import pytest

from background import lcl_household_anchors as anchors

# ---------------------------------------------------------------------------
# INDEPENDENT re-derivation — nothing below imports a helper from the module
# ---------------------------------------------------------------------------


def _raw_rows():
    with anchors.LCL_PANEL_PATH.open() as fh:
        return list(csv.DictReader(fh))


def _q(values, q):
    """Deliberately a second implementation of the quantile. If this and the
    module's disagree, one of them is wrong and the anchor is not what it says."""
    ordered = sorted(values)
    pos = q * (len(ordered) - 1)
    lo = int(pos // 1)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def test_the_panel_is_the_one_the_docstring_describes():
    """304 real households. If the file on disk is not that file, every threshold
    downstream is a number about something else."""
    rows = _raw_rows()
    assert len(rows) == 304
    assert {"LCLid", "stdorToU", "mean_daily_kwh", "archetype_k2"} <= set(rows[0])
    assert all(f"wd_{i}" in rows[0] and f"we_{i}" in rows[0] for i in range(48))


def test_the_L2_4_FLOOR_re_derives_from_the_raw_CSV():
    """The live anchor: the bootstrap P05 of the panel's P90/P10 consumption ratio.

    Re-derived with this file's own quantile and its own resampling loop. The seed
    and resample count come from the module because they are part of the
    THRESHOLD's definition — a bootstrap at a different seed is a different number,
    and pretending otherwise would make this test pass on any value.
    """
    daily = [float(r["mean_daily_kwh"]) for r in _raw_rows()]
    point = _q(daily, 0.90) / _q(daily, 0.10)
    assert point == pytest.approx(5.3769, abs=0.001), (
        "the panel's own P90/P10 — the number the band's anchor_source quotes"
    )

    rnd = random.Random(anchors.BOOTSTRAP_SEED)
    draws = []
    for _ in range(anchors.BOOTSTRAP_RESAMPLES):
        sample = [rnd.choice(daily) for _ in daily]
        draws.append(_q(sample, 0.90) / _q(sample, 0.10))
    floor = _q(draws, anchors.BOOTSTRAP_QUANTILE)

    assert floor == pytest.approx(anchors.LCL_SCALE_SPREAD_P90_P10_FLOOR, abs=5e-5)
    assert floor < point, "a bootstrap LOW quantile must sit below the point estimate"


def test_the_L1_4_FLOOR_re_derives_from_the_raw_CSV():
    """The derived-but-UNWIRED anchor. It is checked to the same standard as the
    live one precisely because it is not in a band: an unused number nobody checks
    is the one that gets wired in later on trust.

    See `tests/harness/test_premise_two_level.py::
    test_the_L1_4_ANCHOR_DOES_NOT_TRANSFER_to_a_120_day_window` for why it is not
    a band.
    """
    rows = _raw_rows()
    tv = []
    for r in rows:
        wd = [float(r[f"wd_{i}"]) for i in range(48)]
        we = [float(r[f"we_{i}"]) for i in range(48)]
        tv.append(0.5 * sum(abs(a - b) for a, b in zip(wd, we)))

    assert _q(tv, 0.50) == pytest.approx(0.0724, abs=0.001), "the panel median"
    assert _q(tv, 0.05) == pytest.approx(0.0279, abs=0.001), "the panel P05"

    rnd = random.Random(anchors.BOOTSTRAP_SEED)
    draws = []
    for _ in range(anchors.BOOTSTRAP_RESAMPLES):
        sample = [rnd.choice(tv) for _ in tv]
        draws.append(_q(sample, anchors.BOOTSTRAP_QUANTILE))
    floor = _q(draws, anchors.BOOTSTRAP_QUANTILE)

    assert floor == pytest.approx(anchors.LCL_WEEKDAY_WEEKEND_TV_FLOOR, abs=5e-5)


def test_the_panel_STILL_CANNOT_close_L1_4s_magnitude_question():
    """A FALSIFIER FOR THE ONE CLAIM IN THIS MODULE THAT IS ONLY PROSE.

    `LCL_WEEKDAY_WEEKEND_TV_FLOOR` is derived and DELIBERATELY not wired into a
    band. The reason, stated in `fabric_gap_ledger`'s L1.4n note and in this
    module's docstring, is a fact about THIS FILE and not about the statistic: the
    extract carries each household's ANNUAL MEAN weekday and weekend shape, so the
    panel's own permutation null cannot be computed from it — and null-correcting
    the model's side while leaving the panel's raw is the same window-mismatch
    error in new coordinates (the finding that took this anchor out).

    That reason is a claim about a file that a later tick could change. Fetch a
    day-level panel into the same path and every word above silently becomes
    false, the constant stays unwired, and the magnitude question stays open for
    no reason at all. So the claim is asserted rather than written down.

    IF THIS TEST REDS, IT IS NOT A REGRESSION — it is the work becoming
    available: null-correct BOTH sides (panel and model) with
    `weekday_weekend_separation_vs_own_null`, and L1.4 gets the magnitude band it
    has carried `AnchorStatus.NEED` for since the suite was written.
    """
    columns = set(_raw_rows()[0])
    # Day-level data would arrive as per-day columns or a date/day key. Neither
    # naming convention is guessed at singly: the check is that NOTHING beyond the
    # four identity columns and the two annual-mean 48-vectors is present, which
    # is true of an annual-mean extract and false of any day-level one.
    expected = {"LCLid", "stdorToU", "mean_daily_kwh", "archetype_k2"}
    expected |= {f"wd_{i}" for i in range(48)} | {f"we_{i}" for i in range(48)}
    assert columns == expected, (
        f"the anchor panel has grown {sorted(columns - expected)} — if any of that "
        "is day-level, the L1.4 magnitude anchor is now BUILDABLE and "
        "LCL_WEEKDAY_WEEKEND_TV_FLOOR should stop being an unwired constant"
    )
    # And the constant is still unwired, so this test and the code agree about
    # which state the world is in rather than each describing its own.
    from background import fabric_gap_ledger as fgl

    assert fgl.BANDS["L1.4_weekday_weekend_separation"].threshold is None
    assert fgl.RATE_BANDS["L1.4_weekday_weekend_separation"].threshold is None


def test_the_shapes_the_L1_4_anchor_reads_are_actually_NORMALISED():
    """The statistic is a total-variation distance between two probability-like
    48-vectors. Against un-normalised vectors it is a different quantity that would
    still return a plausible float, so the assumption is checked rather than
    assumed — the module raises on this, and here is the evidence it never has to.
    """
    for r in _raw_rows():
        for prefix in ("wd", "we"):
            total = sum(float(r[f"{prefix}_{i}"]) for i in range(48))
            assert total == pytest.approx(1.0, abs=1e-6), r["LCLid"]


def test_the_bootstrap_is_DETERMINISTIC_at_a_named_seed():
    """A threshold derived from a resample is only a threshold if the resample is
    reproducible. Two calls must agree exactly, and a different seed must NOT (or
    the seed is not doing anything and the reproducibility is an accident)."""
    a = anchors.derive_scale_spread_floor()
    b = anchors.derive_scale_spread_floor()
    assert a == b
    shifted = anchors.bootstrap_low_quantile(
        anchors.panel_daily_kwh(),
        lambda s: anchors._quantile(s, 0.90) / anchors._quantile(s, 0.10),
        seed=anchors.BOOTSTRAP_SEED + 1,
    )
    assert shifted != a
    # ...and the seed must not be able to move the number far enough to matter.
    # A bootstrap whose answer swings with the seed is sampling noise wearing a
    # threshold's clothes.
    assert abs(shifted - a) < 0.25


# ---------------------------------------------------------------------------
# FAIL-CLOSED — every way of not having the panel RAISES
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_panel_cache():
    anchors.load_panel.cache_clear()
    yield
    anchors.load_panel.cache_clear()


def test_a_MISSING_panel_raises_rather_than_defaulting(tmp_path):
    with pytest.raises(anchors.AnchorUnavailable, match="not on disk"):
        anchors.load_panel(str(tmp_path / "nope.csv"))


def test_an_EMPTY_panel_raises(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("mean_daily_kwh\n")
    with pytest.raises(anchors.AnchorUnavailable, match="no households"):
        anchors.load_panel(str(p))


def test_a_panel_MISSING_THE_SHAPE_COLUMNS_raises(tmp_path):
    p = tmp_path / "short.csv"
    p.write_text("LCLid,mean_daily_kwh\nMAC1,10.0\n")
    with pytest.raises(anchors.AnchorUnavailable, match="missing"):
        anchors.load_panel(str(p))


def _synthetic_panel(path, *, daily="10.0", scale_wd=1.0):
    header = (
        ["LCLid", "mean_daily_kwh"]
        + [f"wd_{i}" for i in range(48)]
        + [f"we_{i}" for i in range(48)]
    )
    wd = [f"{scale_wd / 48:.12f}"] * 48
    we = [f"{1 / 48:.12f}"] * 48
    rows = [",".join(header)]
    for k in range(3):
        rows.append(",".join([f"MAC{k}", daily] + wd + we))
    path.write_text("\n".join(rows) + "\n")
    return str(path)


def test_a_NON_FINITE_consumption_figure_raises(tmp_path):
    p = _synthetic_panel(tmp_path / "nan.csv", daily="nan")
    with pytest.raises(anchors.AnchorUnavailable, match="non-positive or non-finite"):
        anchors.panel_daily_kwh(p)


def test_a_ZERO_consumption_figure_raises(tmp_path):
    """Zero is the fail-open direction specifically: it would sail through a
    finiteness check and then divide into a P90/P10 ratio."""
    p = _synthetic_panel(tmp_path / "zero.csv", daily="0.0")
    with pytest.raises(anchors.AnchorUnavailable):
        anchors.panel_daily_kwh(p)


def test_an_UN_NORMALISED_shape_raises(tmp_path):
    p = _synthetic_panel(tmp_path / "unnorm.csv", scale_wd=2.0)
    with pytest.raises(anchors.AnchorUnavailable, match="supposed to be normalised"):
        anchors.panel_weekday_weekend_separation(p)


def test_a_TWO_HOUSEHOLD_bootstrap_is_allowed_but_a_ONE_HOUSEHOLD_one_is_not():
    """Input sufficiency, at the only boundary that means anything here: a
    'bootstrap' over a single value returns that value with total confidence."""
    with pytest.raises(anchors.AnchorUnavailable, match="theatre"):
        anchors.bootstrap_low_quantile([1.0], lambda s: sum(s))
    assert math.isfinite(anchors.bootstrap_low_quantile([1.0, 2.0], lambda s: sum(s)))
