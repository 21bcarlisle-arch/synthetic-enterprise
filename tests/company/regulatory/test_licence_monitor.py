"""Phase 119: Licence condition monitoring tests."""

from company.regulatory.licence_monitor import LicenceMonitor, SLCStatus


def _monitor():
    return LicenceMonitor()


def test_set_and_get_status():
    m = _monitor()
    s = m.set_status("SLC 14", "COMPLIANT", "All complaints resolved within 8 weeks")
    assert s.status == "COMPLIANT"
    assert m.get("SLC 14") is s


def test_description_from_catalogue():
    m = _monitor()
    s = m.set_status("SLC 14", "COMPLIANT")
    assert "Complaints" in s.description


def test_unknown_slc_uses_number():
    m = _monitor()
    s = m.set_status("SLC 99", "NOT_ASSESSED")
    assert "99" in s.description


def test_breaches_list():
    m = _monitor()
    m.set_status("SLC 7", "COMPLIANT")
    m.set_status("SLC 21C", "BREACH", "Unit rate exceeds cap Q1 2022")
    assert len(m.breaches()) == 1
    assert m.breaches()[0].slc_number == "SLC 21C"


def test_under_monitor_list():
    m = _monitor()
    m.set_status("SLC 27", "MONITOR", "Smart meter rollout 42% vs 50% target")
    m.set_status("SLC 36", "COMPLIANT")
    assert len(m.under_monitor()) == 1


def test_compliance_summary_green():
    m = _monitor()
    m.set_status("SLC 7", "COMPLIANT")
    m.set_status("SLC 14", "COMPLIANT")
    s = m.compliance_summary()
    assert s["rag"] == "GREEN"
    assert s["compliant"] == 2
    assert s["breach"] == 0


def test_compliance_summary_red_on_breach():
    m = _monitor()
    m.set_status("SLC 7", "COMPLIANT")
    m.set_status("SLC 21C", "BREACH")
    s = m.compliance_summary()
    assert s["rag"] == "RED"


def test_compliance_summary_amber_on_monitor():
    m = _monitor()
    m.set_status("SLC 27", "MONITOR")
    s = m.compliance_summary()
    assert s["rag"] == "AMBER"


def test_all_statuses():
    m = _monitor()
    m.set_status("SLC 7", "COMPLIANT")
    m.set_status("SLC 14", "MONITOR")
    assert len(m.all_statuses()) == 2


def test_catalogue_contains_key_slcs():
    m = _monitor()
    cat = m.catalogue()
    for key in ("SLC 7", "SLC 14", "SLC 21C", "SLC 36", "SLC 47"):
        assert key in cat


# --- Phase LD depth tests ---

def test_slc_number_stored():
    m = _monitor()
    s = m.set_status('SLC 7', 'COMPLIANT', 'Bills issued within 12 months')
    assert s.slc_number == 'SLC 7'


def test_status_stored():
    m = _monitor()
    s = m.set_status('SLC 14', 'BREACH', 'Complaint overdue')
    assert s.status == 'BREACH'


def test_evidence_stored():
    m = _monitor()
    s = m.set_status('SLC 14', 'COMPLIANT', 'All on time')
    assert s.evidence == 'All on time'


def test_description_is_string():
    m = _monitor()
    s = m.set_status('SLC 7', 'COMPLIANT')
    assert isinstance(s.description, str)


def test_get_none_for_unknown():
    m = _monitor()
    assert m.get('SLC_UNKNOWN_XYZ') is None


def test_breaches_empty_initially():
    m = _monitor()
    assert m.breaches() == []


def test_under_monitor_empty_initially():
    m = _monitor()
    assert m.under_monitor() == []


def test_compliance_summary_is_dict():
    m = _monitor()
    s = m.compliance_summary()
    assert isinstance(s, dict)


def test_compliance_summary_has_overall():
    m = _monitor()
    s = m.compliance_summary()
    assert 'rag' in s


def test_all_statuses_values():
    valid = {'COMPLIANT', 'MONITOR', 'BREACH', 'NOT_ASSESSED'}
    m = _monitor()
    m.set_status('SLC 7', 'MONITOR')
    m.set_status('SLC 14', 'BREACH')
    all_s = m.all_statuses()
    assert all(s.status in valid for s in all_s)
