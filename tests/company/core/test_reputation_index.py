"""Tests for Global Reputation Index (Phase EB)."""
import datetime as dt
import pytest
from company.core.reputation_index import (
    ReputationBand, ReputationEventType, ReputationEvent,
    GlobalReputationIndex,
    _GRI_IMPACT, _GRI_BASELINE, _ACTIVATION_ENERGY_MULTIPLIER,
)


DATE = dt.date(2024, 6, 15)
PREV = dt.date(2024, 1, 1)


@pytest.fixture
def gri():
    return GlobalReputationIndex(starting_gri=50.0)


class TestGRIImpact:
    def test_ofgem_hardest_hit(self):
        assert _GRI_IMPACT[ReputationEventType.OFGEM_ENFORCEMENT_ACTION] == pytest.approx(-12.0)

    def test_resolved_on_time_positive(self):
        assert _GRI_IMPACT[ReputationEventType.COMPLAINT_RESOLVED_ON_TIME] > 0

    def test_tariff_award_positive(self):
        assert _GRI_IMPACT[ReputationEventType.TARIFF_TRANSPARENCY_AWARD] > 0


class TestGlobalReputationIndex:
    def test_starting_score(self, gri):
        assert gri.score(DATE) == pytest.approx(50.0)

    def test_positive_event_raises_score(self, gri):
        gri.record(ReputationEventType.TARIFF_TRANSPARENCY_AWARD, DATE)
        assert gri.score(DATE) > 50.0

    def test_negative_event_lowers_score(self, gri):
        gri.record(ReputationEventType.OFGEM_ENFORCEMENT_ACTION, DATE)
        assert gri.score(DATE) < 50.0

    def test_score_clamped_min(self):
        g = GlobalReputationIndex(starting_gri=5.0)
        for _ in range(10):
            g.record(ReputationEventType.OFGEM_ENFORCEMENT_ACTION, DATE)
        assert g.score(DATE) >= 0.0

    def test_score_clamped_max(self):
        g = GlobalReputationIndex(starting_gri=95.0)
        for _ in range(10):
            g.record(ReputationEventType.TARIFF_TRANSPARENCY_AWARD, DATE)
        assert g.score(DATE) <= 100.0

    def test_band_strong(self):
        g = GlobalReputationIndex(starting_gri=75.0)
        assert g.band(DATE) == ReputationBand.STRONG

    def test_band_adequate(self, gri):
        assert gri.band(DATE) == ReputationBand.ADEQUATE

    def test_band_weak(self):
        g = GlobalReputationIndex(starting_gri=40.0)
        assert g.band(DATE) == ReputationBand.WEAK

    def test_band_crisis(self):
        g = GlobalReputationIndex(starting_gri=25.0)
        assert g.band(DATE) == ReputationBand.CRISIS

    def test_activation_energy_strong(self):
        g = GlobalReputationIndex(starting_gri=75.0)
        assert g.activation_energy_multiplier(DATE) == pytest.approx(1.3)

    def test_activation_energy_crisis(self):
        g = GlobalReputationIndex(starting_gri=25.0)
        assert g.activation_energy_multiplier(DATE) == pytest.approx(0.5)

    def test_events_in_period(self, gri):
        gri.record(ReputationEventType.COMPLAINT_RESOLVED_ON_TIME, PREV)
        gri.record(ReputationEventType.OFGEM_ENFORCEMENT_ACTION, DATE)
        in_period = gri.events_in_period(DATE, DATE)
        assert len(in_period) == 1

    def test_worst_event_in_period(self, gri):
        gri.record(ReputationEventType.COMPLAINT_RESOLVED_LATE, DATE)
        gri.record(ReputationEventType.OFGEM_ENFORCEMENT_ACTION, DATE)
        worst = gri.worst_event_in_period(DATE, DATE)
        assert worst is not None
        assert worst.event_type == ReputationEventType.OFGEM_ENFORCEMENT_ACTION

    def test_future_events_not_counted(self, gri):
        future = dt.date(2025, 1, 1)
        gri.record(ReputationEventType.OFGEM_ENFORCEMENT_ACTION, future)
        assert gri.score(DATE) == pytest.approx(50.0)

    def test_amplifier(self, gri):
        gri.record(ReputationEventType.OFGEM_ENFORCEMENT_ACTION, DATE, amplifier=2.0)
        assert gri.score(DATE) == pytest.approx(50.0 - 24.0)  # -12 * 2

    def test_trend_improving(self):
        g = GlobalReputationIndex(starting_gri=40.0)
        g.record(ReputationEventType.TARIFF_TRANSPARENCY_AWARD, dt.date(2024, 3, 1))
        g.record(ReputationEventType.TARIFF_TRANSPARENCY_AWARD, dt.date(2024, 4, 1))
        g.record(ReputationEventType.TARIFF_TRANSPARENCY_AWARD, dt.date(2024, 5, 1))
        assert g.trend(6, DATE) == "improving"

    def test_trend_declining(self, gri):
        gri.record(ReputationEventType.OFGEM_ENFORCEMENT_ACTION, dt.date(2024, 4, 1))
        assert gri.trend(6, DATE) == "declining"

    def test_gri_summary(self, gri):
        s = gri.gri_summary(DATE)
        assert "Global Reputation Index" in s
        assert "50.0" in s

    def test_constants(self):
        assert _GRI_BASELINE == pytest.approx(50.0)
        assert _ACTIVATION_ENERGY_MULTIPLIER[ReputationBand.STRONG] == pytest.approx(1.3)
        assert _ACTIVATION_ENERGY_MULTIPLIER[ReputationBand.CRISIS] == pytest.approx(0.5)
