"""Phase CE: SLC Compliance Tracker tests."""
import pytest
from company.regulatory.slc_compliance_tracker import (
    SLCComplianceTracker, SLCStatus, SLCCategory, SLCObservation
)


def _tracker():
    return SLCComplianceTracker()


# 1. Record observation returns correct SLCObservation
def test_record_returns_observation():
    t = _tracker()
    obs = t.record("SLC 6", SLCCategory.BILLING, "Bills timely", SLCStatus.COMPLIANT)
    assert obs.slc_ref == "SLC 6"
    assert obs.is_compliant is True


# 2. Compliant status: is_compliant True, is_breached False
def test_compliant_flags():
    obs = SLCObservation("SLC 6", SLCCategory.BILLING, "Bills", SLCStatus.COMPLIANT)
    assert obs.is_compliant is True
    assert obs.is_breached is False


# 3. Breached status: is_compliant False, is_breached True
def test_breached_flags():
    obs = SLCObservation("SLC 27", SLCCategory.DEBT, "Debt", SLCStatus.BREACHED, breach_count=1)
    assert obs.is_compliant is False
    assert obs.is_breached is True


# 4. Severity scores: COMPLIANT=0, BREACH_RISK=1, BREACHED=2
def test_severity_scores():
    c = SLCObservation("A", SLCCategory.BILLING, "", SLCStatus.COMPLIANT)
    r = SLCObservation("B", SLCCategory.BILLING, "", SLCStatus.BREACH_RISK)
    b = SLCObservation("C", SLCCategory.BILLING, "", SLCStatus.BREACHED)
    assert c.severity_score == 0
    assert r.severity_score == 1
    assert b.severity_score == 2


# 5. Overall RAG is RED when any breach
def test_rag_red_with_breach():
    t = _tracker()
    t.record("SLC 27", SLCCategory.DEBT, "", SLCStatus.BREACHED, breach_count=1)
    assert t.overall_rag == "RED"


# 6. Overall RAG is AMBER when at-risk and no breach
def test_rag_amber_with_risk():
    t = _tracker()
    t.record("SLC 14", SLCCategory.CREDIT, "", SLCStatus.BREACH_RISK, at_risk_count=2)
    assert t.overall_rag == "AMBER"


# 7. Overall RAG is GREEN when all compliant
def test_rag_green_all_compliant():
    t = _tracker()
    t.record("SLC 6", SLCCategory.BILLING, "", SLCStatus.COMPLIANT)
    t.record("SLC 14", SLCCategory.CREDIT, "", SLCStatus.COMPLIANT)
    assert t.overall_rag == "GREEN"


# 8. breached property returns only BREACHED observations
def test_breached_list():
    t = _tracker()
    t.record("SLC 27", SLCCategory.DEBT, "", SLCStatus.BREACHED, breach_count=1)
    t.record("SLC 6", SLCCategory.BILLING, "", SLCStatus.COMPLIANT)
    assert len(t.breached) == 1
    assert t.breached[0].slc_ref == "SLC 27"


# 9. total_breach_count sums across all observations
def test_total_breach_count():
    t = _tracker()
    t.record("SLC 27", SLCCategory.DEBT, "", SLCStatus.BREACHED, breach_count=3)
    t.record("SLC 14", SLCCategory.CREDIT, "", SLCStatus.BREACHED, breach_count=2)
    assert t.total_breach_count == 5


# 10. by_category filters correctly
def test_by_category():
    t = _tracker()
    t.record("SLC 6", SLCCategory.BILLING, "", SLCStatus.COMPLIANT)
    t.record("SLC 27", SLCCategory.DEBT, "", SLCStatus.COMPLIANT)
    t.record("SLC 31A", SLCCategory.BILLING, "", SLCStatus.COMPLIANT)
    billing = t.by_category(SLCCategory.BILLING)
    assert len(billing) == 2
    assert all(o.category == SLCCategory.BILLING for o in billing)


# 11. highest_severity_slcs returns top-n by severity+breach
def test_highest_severity():
    t = _tracker()
    t.record("SLC 6", SLCCategory.BILLING, "", SLCStatus.COMPLIANT)
    t.record("SLC 27", SLCCategory.DEBT, "", SLCStatus.BREACHED, breach_count=5)
    t.record("SLC 14", SLCCategory.CREDIT, "", SLCStatus.BREACH_RISK, at_risk_count=2)
    top = t.highest_severity_slcs(2)
    assert top[0].slc_ref == "SLC 27"  # Most severe first
    assert top[1].slc_ref == "SLC 14"


# 12. compliance_summary contains key fields
def test_compliance_summary():
    t = _tracker()
    t.record("SLC 6", SLCCategory.BILLING, "", SLCStatus.COMPLIANT)
    t.record("SLC 27", SLCCategory.DEBT, "", SLCStatus.BREACHED, breach_count=1)
    summary = t.compliance_summary()
    assert "Overall RAG" in summary
    assert "Compliant" in summary
    assert "SLC 27" in summary


# --- Phase MB depth tests ---

def test_slc_ref_stored():
    t = _tracker()
    obs = t.record('SLC 6', SLCCategory.BILLING, 'Bills timely', SLCStatus.COMPLIANT)
    assert obs.slc_ref == 'SLC 6'


def test_category_stored():
    t = _tracker()
    obs = t.record('SLC 14', SLCCategory.CREDIT, 'Refunds', SLCStatus.COMPLIANT)
    assert obs.category == SLCCategory.CREDIT


def test_description_stored():
    t = _tracker()
    obs = t.record('SLC 6', SLCCategory.BILLING, 'My description', SLCStatus.COMPLIANT)
    assert obs.description == 'My description'


def test_status_stored():
    t = _tracker()
    obs = t.record('SLC 6', SLCCategory.BILLING, 'Bills', SLCStatus.BREACH_RISK)
    assert obs.status == SLCStatus.BREACH_RISK


def test_breach_count_default_zero():
    t = _tracker()
    obs = t.record('SLC 6', SLCCategory.BILLING, 'Bills', SLCStatus.COMPLIANT)
    assert obs.breach_count == 0


def test_at_risk_count_default_zero():
    t = _tracker()
    obs = t.record('SLC 6', SLCCategory.BILLING, 'Bills', SLCStatus.COMPLIANT)
    assert obs.at_risk_count == 0


def test_notes_default_empty():
    t = _tracker()
    obs = t.record('SLC 6', SLCCategory.BILLING, 'Bills', SLCStatus.COMPLIANT)
    assert obs.notes == ''


def test_is_compliant_compliant_status():
    t = _tracker()
    obs = t.record('SLC 6', SLCCategory.BILLING, 'Bills', SLCStatus.COMPLIANT)
    assert obs.is_compliant is True


def test_is_breached_false_for_risk():
    t = _tracker()
    obs = t.record('SLC 6', SLCCategory.BILLING, 'Bills', SLCStatus.BREACH_RISK)
    assert obs.is_breached is False


def test_record_returns_slc_observation():
    t = _tracker()
    result = t.record('SLC 6', SLCCategory.BILLING, 'Bills', SLCStatus.COMPLIANT)
    assert isinstance(result, SLCObservation)
