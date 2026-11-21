"""The world's media term holds the shapes the record shows, and reaches a household only
through the price that household pays.

Each control is keyed to a property of the frozen extract
(`sim/data/media_coverage_energy_price_weekly_2016_2025.json`), not to today's numbers. The
defects each one catches are named in its docstring.
"""
import datetime as dt
import statistics
from pathlib import Path

import pytest

from simulation.activation_energy import (
    MEDIA_CONTACT_COUPLING,
    MEDIA_EXTRACT_PATH,
    MEDIA_SWITCHING_COUPLING,
    MEDIA_SWITCHING_COUPLING_RANGE,
    ActionType,
    ActivationEnergyProfile,
    MediaMoment,
    _media_extract,
    media_attention_ratio,
    media_moments,
    media_switching_ae_factor,
)

FAILURE_WEEK = dt.date(2021, 9, 20)
LOUD_CAP_WEEK = dt.date(2024, 8, 23)  # cap announcement; reads well above its background
ILLUSTRATIVE_COUPLING = 0.04  # the top of the measured range, so the branch moves a number


def _median_by_moment() -> dict:
    _, moments = _media_extract()
    readings: dict = {}
    for week, kinds in moments.items():
        ratio = media_attention_ratio(week)
        if ratio is None:
            continue
        for kind in kinds:
            readings.setdefault(kind, []).append(ratio)
    return {kind: statistics.median(v) for kind, v in readings.items()}


def test_a_cap_has_two_pulses_and_the_announcement_is_the_larger():
    """Defect: a cap term with one pulse, or an effective pulse louder than the announcement."""
    med = _median_by_moment()
    assert med[MediaMoment.CAP_EFFECTIVE] > 1.0
    assert med[MediaMoment.CAP_ANNOUNCEMENT] > med[MediaMoment.CAP_EFFECTIVE]


def test_a_supplier_change_has_one_pulse_at_its_announcement():
    """Defect: a supplier effective date treated as a media moment (the record reads it below 1)."""
    med = _median_by_moment()
    assert med[MediaMoment.SUPPLIER_ANNOUNCEMENT] > 1.0
    assert med[MediaMoment.SUPPLIER_EFFECTIVE] < 1.0


def test_the_supplier_failure_week_is_its_own_event_and_holds_no_price_moment():
    """Defect: a term keyed only to price announcements, which misses the failure week."""
    kinds = media_moments(FAILURE_WEEK)
    assert kinds == (MediaMoment.SUPPLIER_FAILURE,)
    med = _median_by_moment()
    assert media_attention_ratio(FAILURE_WEEK) > max(
        med[k] for k in (MediaMoment.CAP_ANNOUNCEMENT, MediaMoment.SUPPLIER_ANNOUNCEMENT)
    )


def test_coverage_reaches_a_household_only_through_the_price_it_pays():
    """Defect: a term keyed to the headline. Both branches are asserted reachable first, so a
    factor stuck at 1.0 cannot pass."""
    moved = media_switching_ae_factor(LOUD_CAP_WEEK, True, coupling=ILLUSTRATIVE_COUPLING)
    unmoved = media_switching_ae_factor(LOUD_CAP_WEEK, False, coupling=ILLUSTRATIVE_COUPLING)
    assert moved < 1.0
    assert unmoved == 1.0
    # A failure is news about the household's own supplier, so it reaches without a price move.
    assert media_switching_ae_factor(FAILURE_WEEK, False, coupling=ILLUSTRATIVE_COUPLING) < 1.0


def test_an_incomplete_week_is_cannot_tell_not_zero():
    """Defect: a week emptied at source (w/c 16 Jun 2025) read as a quiet week."""
    assert media_attention_ratio(dt.date(2025, 6, 18)) is None
    assert media_attention_ratio(dt.date(2015, 12, 30)) is None


def test_the_carried_coupling_is_inside_its_measured_interval():
    """Defect: a coupling raised past what 59 calm months of QEP 2.7.1 allow."""
    lo, hi = MEDIA_SWITCHING_COUPLING_RANGE
    assert lo < 0.0 < hi
    assert lo <= MEDIA_SWITCHING_COUPLING <= hi
    assert MEDIA_CONTACT_COUPLING is None, "no contact series measures this yet (G6)"


def test_the_media_factor_reaches_switching_and_nothing_else():
    """Defect: an unmeasured coupling leaking into complaint activation energy."""
    base = dict(account_id="C1", base_ae_switching=100.0, tenure_years=1.0, is_ppm=False)
    plain = ActivationEnergyProfile(**base)
    media = ActivationEnergyProfile(**base, media_switching_factor=0.5)
    assert media.switching_ae() == pytest.approx(plain.switching_ae() * 0.5)
    assert media.complaint_ae() == plain.complaint_ae()
    assert media.effective_ae_for(ActionType.ESCALATE_TO_OMBUDSMAN) == plain.effective_ae_for(
        ActionType.ESCALATE_TO_OMBUDSMAN
    )


def test_the_company_never_reads_the_extract():
    """W6: the extract is a world input; no file in company/ or saas/ names it."""
    root = Path(__file__).resolve().parents[2]
    name = MEDIA_EXTRACT_PATH.stem
    hits = [
        str(p.relative_to(root))
        for side in ("company", "saas")
        for p in (root / side).rglob("*.py")
        if name in p.read_text(errors="ignore") or "media_attention_ratio" in p.read_text(errors="ignore")
    ]
    assert hits == []
