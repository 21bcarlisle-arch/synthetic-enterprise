import pytest
from company.regulatory.regulatory_dashboard import (
    RegulatoryDashboard, ComplianceObligation, ComplianceArea, FilingStatus
)


def _ob(area=ComplianceArea.FINANCIAL_RESILIENCE, name="SFR Q1", due="2022-05-01",
        status=FilingStatus.FILED, rag="GREEN", notes=None):
    return ComplianceObligation(area=area, obligation_name=name, due_date=due,
                                status=status, rag=rag, notes=notes)


def test_is_breach_red():
    ob = _ob(rag="RED")
    assert ob.is_breach is True


def test_is_breach_overdue():
    ob = _ob(status=FilingStatus.OVERDUE, rag="GREEN")
    assert ob.is_breach is True


def test_not_breach_green_filed():
    ob = _ob(rag="GREEN", status=FilingStatus.FILED)
    assert ob.is_breach is False


def test_needs_attention_amber():
    ob = _ob(rag="AMBER")
    assert ob.needs_attention is True


def test_needs_attention_due():
    ob = _ob(status=FilingStatus.DUE, rag="GREEN")
    assert ob.needs_attention is True


def test_overall_rag_green():
    dash = RegulatoryDashboard()
    dash.add_obligation(_ob(rag="GREEN", status=FilingStatus.FILED))
    assert dash.overall_rag() == "GREEN"


def test_overall_rag_red_if_any_red():
    dash = RegulatoryDashboard()
    dash.add_obligation(_ob(rag="GREEN"))
    dash.add_obligation(_ob(rag="RED"))
    assert dash.overall_rag() == "RED"


def test_overall_rag_overdue_is_red():
    dash = RegulatoryDashboard()
    dash.add_obligation(_ob(rag="GREEN", status=FilingStatus.OVERDUE))
    assert dash.overall_rag() == "RED"


def test_breaches_list():
    dash = RegulatoryDashboard()
    dash.add_obligation(_ob(rag="RED"))
    dash.add_obligation(_ob(rag="GREEN"))
    assert len(dash.breaches()) == 1


def test_filed_on_time_rate():
    dash = RegulatoryDashboard()
    dash.add_obligation(_ob(status=FilingStatus.FILED))
    dash.add_obligation(_ob(status=FilingStatus.FILED))
    dash.add_obligation(_ob(status=FilingStatus.OVERDUE))
    assert abs(dash.filed_on_time_rate() - (2/3*100)) < 0.1


def test_area_rag_keys():
    dash = RegulatoryDashboard()
    dash.add_obligation(_ob(area=ComplianceArea.MARKET_CONDUCT, rag="AMBER"))
    ar = dash.area_rag()
    assert ComplianceArea.MARKET_CONDUCT.value in ar
    assert ar[ComplianceArea.MARKET_CONDUCT.value] == "AMBER"


def test_dashboard_summary_keys():
    dash = RegulatoryDashboard()
    dash.add_obligation(_ob())
    s = dash.dashboard_summary()
    for k in ("total_obligations", "breaches", "attention_items",
               "overall_rag", "filed_on_time_rate_pct", "area_rag"):
        assert k in s


# --- Phase MC depth tests ---

def test_area_stored():
    ob = _ob(area=ComplianceArea.ENVIRONMENTAL)
    assert ob.area == ComplianceArea.ENVIRONMENTAL


def test_obligation_name_stored():
    ob = _ob(name='REGO Filing')
    assert ob.obligation_name == 'REGO Filing'


def test_due_date_stored():
    ob = _ob(due='2023-09-30')
    assert ob.due_date == '2023-09-30'


def test_status_stored():
    ob = _ob(status=FilingStatus.OVERDUE)
    assert ob.status == FilingStatus.OVERDUE


def test_rag_stored():
    ob = _ob(rag='AMBER')
    assert ob.rag == 'AMBER'


def test_notes_none_default():
    ob = _ob()
    assert ob.notes is None


def test_add_obligation_returns_obligation():
    d = RegulatoryDashboard()
    result = d.add_obligation(_ob())
    assert isinstance(result, ComplianceObligation)


def test_compliance_area_has_8_members():
    assert len(list(ComplianceArea)) == 8


def test_filing_status_has_4_members():
    assert len(list(FilingStatus)) == 4


def test_needs_attention_filed_green_false():
    ob = _ob(status=FilingStatus.FILED, rag='GREEN')
    assert ob.needs_attention is False
