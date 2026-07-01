import pytest
from datetime import date
from company.crm.life_events import LifeEvent, LifeEventType
from company.crm.life_event_impact import LifeEventImpact, LifeEventImpactAssessor, ImpactSeverity


def _ev(et, cid="C1", d=None):
    return LifeEvent(customer_id=cid, event_type=et, event_date=d or date(2022, 6, 1))


def test_serious_illness_is_critical():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.SERIOUS_ILLNESS))
    assert impact.severity == ImpactSeverity.CRITICAL
    assert impact.triggers_psr_review is True
    assert impact.vulnerability_flag is True
    assert impact.is_urgent is True


def test_job_loss_is_high_severity():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.JOB_LOSS))
    assert impact.severity == ImpactSeverity.HIGH
    assert impact.expected_consumption_delta_pct == 15.0
    assert impact.vulnerability_flag is True
    assert "payment plan" in impact.recommended_actions[0].lower()


def test_retirement_triggers_psr():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.RETIREMENT))
    assert impact.triggers_psr_review is True
    assert impact.expected_consumption_delta_pct > 0


def test_birth_low_severity():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.BIRTH))
    assert impact.severity == ImpactSeverity.LOW
    assert not impact.triggers_psr_review
    assert impact.expected_consumption_delta_pct > 0


def test_job_gain_negative_consumption_delta():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.JOB_GAIN))
    assert impact.expected_consumption_delta_pct < 0


def test_move_out_no_consumption_delta():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.MOVE_OUT))
    assert impact.expected_consumption_delta_pct == 0.0


def test_to_dict_keys():
    a = LifeEventImpactAssessor()
    d = a.assess(_ev(LifeEventType.DIVORCE)).to_dict()
    for k in ("customer_id", "event_type", "event_date", "severity",
              "consumption_delta_pct", "triggers_psr_review", "vulnerability_flag",
              "recommended_actions", "is_urgent"):
        assert k in d


def test_batch_assess_length():
    a = LifeEventImpactAssessor()
    evs = [_ev(LifeEventType.BIRTH), _ev(LifeEventType.JOB_LOSS, "C2"), _ev(LifeEventType.RETIREMENT, "C3")]
    impacts = a.batch_assess(evs)
    assert len(impacts) == 3


def test_urgent_impacts_filtered():
    a = LifeEventImpactAssessor()
    evs = [_ev(LifeEventType.BIRTH), _ev(LifeEventType.JOB_LOSS), _ev(LifeEventType.SERIOUS_ILLNESS, "C3")]
    urgent = a.urgent_impacts(evs)
    assert len(urgent) == 2
    assert all(i.is_urgent for i in urgent)


def test_psr_candidates():
    a = LifeEventImpactAssessor()
    evs = [_ev(LifeEventType.BIRTH), _ev(LifeEventType.SERIOUS_ILLNESS), _ev(LifeEventType.RETIREMENT, "C3")]
    psr = a.psr_candidates(evs)
    assert len(psr) == 2


def test_summary_keys():
    a = LifeEventImpactAssessor()
    evs = [_ev(et) for et in [LifeEventType.BIRTH, LifeEventType.JOB_LOSS, LifeEventType.DIVORCE]]
    s = a.summary(evs)
    for k in ("total_events", "urgent_count", "psr_candidates", "vulnerability_flags", "by_severity"):
        assert k in s
    assert s["total_events"] == 3


def test_impact_is_frozen():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.BIRTH))
    with pytest.raises((AttributeError, TypeError)):
        impact.severity = ImpactSeverity.CRITICAL


# --- Phase LS depth tests ---

def test_event_stored_in_impact():
    a = LifeEventImpactAssessor()
    ev = _ev(LifeEventType.BIRTH)
    impact = a.assess(ev)
    assert impact.event is ev


def test_death_high_severity():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.DEATH))
    assert impact.severity == ImpactSeverity.HIGH


def test_death_negative_consumption_delta():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.DEATH))
    assert impact.expected_consumption_delta_pct < 0


def test_marriage_not_psr():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.MARRIAGE))
    assert impact.triggers_psr_review is False


def test_divorce_vulnerability_flag():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.DIVORCE))
    assert impact.vulnerability_flag is True


def test_recommended_actions_tuple():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.BIRTH))
    assert isinstance(impact.recommended_actions, tuple)
    assert len(impact.recommended_actions) > 0


def test_is_urgent_false_for_low_severity():
    a = LifeEventImpactAssessor()
    impact = a.assess(_ev(LifeEventType.BIRTH))
    assert impact.is_urgent is False


def test_batch_assess_count():
    a = LifeEventImpactAssessor()
    evs = [_ev(LifeEventType.BIRTH), _ev(LifeEventType.DIVORCE)]
    results = a.batch_assess(evs)
    assert len(results) == 2


def test_psr_candidates_filters():
    a = LifeEventImpactAssessor()
    evs = [_ev(LifeEventType.SERIOUS_ILLNESS), _ev(LifeEventType.BIRTH)]
    cands = a.psr_candidates(evs)
    assert len(cands) == 1


def test_summary_keys():
    a = LifeEventImpactAssessor()
    s = a.summary([_ev(LifeEventType.JOB_LOSS)])
    for k in ('total_events', 'urgent_count', 'psr_candidates',
              'vulnerability_flags', 'by_severity'):
        assert k in s
