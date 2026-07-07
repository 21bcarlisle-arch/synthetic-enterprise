"""Tests for tools/generate_case_study_recommender.py's Phase RU addition:
_silent_middle_drop identifies a household whose SIM-true satisfaction fell
across the run but who never once responded to a solicited survey.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from tools.generate_case_study_recommender import _silent_middle_drop


def _sample(entries):
    return {"C1": {"feedback_survey_history": entries}}


def test_silent_middle_drop_detects_true_decline_with_zero_responses():
    entries = [
        {"term_start": "2017-01-01", "true_satisfaction": 0.8, "csat_responded": False, "nps_responded": False},
        {"term_start": "2024-01-01", "true_satisfaction": 0.6, "csat_responded": False, "nps_responded": False},
    ]
    result = _silent_middle_drop(_sample(entries), "C1")
    assert result is not None
    assert result["drop"] == pytest.approx(0.2)


def test_silent_middle_drop_none_when_any_response_recorded():
    entries = [
        {"term_start": "2017-01-01", "true_satisfaction": 0.8, "csat_responded": False, "nps_responded": False},
        {"term_start": "2024-01-01", "true_satisfaction": 0.6, "csat_responded": True, "nps_responded": False},
    ]
    assert _silent_middle_drop(_sample(entries), "C1") is None


def test_silent_middle_drop_none_when_satisfaction_did_not_fall():
    entries = [
        {"term_start": "2017-01-01", "true_satisfaction": 0.6, "csat_responded": False, "nps_responded": False},
        {"term_start": "2024-01-01", "true_satisfaction": 0.8, "csat_responded": False, "nps_responded": False},
    ]
    assert _silent_middle_drop(_sample(entries), "C1") is None


def test_silent_middle_drop_none_with_fewer_than_two_entries():
    entries = [
        {"term_start": "2017-01-01", "true_satisfaction": 0.8, "csat_responded": False, "nps_responded": False},
    ]
    assert _silent_middle_drop(_sample(entries), "C1") is None


def test_silent_middle_drop_none_when_customer_missing():
    assert _silent_middle_drop({}, "C_unknown") is None
