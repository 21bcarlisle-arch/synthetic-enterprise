"""Phase 130: ECO tracker tests."""

from company.regulatory.eco_tracker import EcoMeasure, EcoTracker


def _tracker_small():
    return EcoTracker(account_count=100_000)  # exempt


def _tracker_contrib():
    return EcoTracker(account_count=200_000)  # contribution tier


def _tracker_full():
    return EcoTracker(account_count=300_000)  # must deliver directly


def test_small_supplier_exempt():
    t = _tracker_small()
    assert t.is_exempt is True
    assert t.annual_obligation_twhd == 0.0
    assert t.status() == "EXEMPT"


def test_contribution_tier():
    t = _tracker_contrib()
    assert t.pays_contribution is True
    assert t.must_deliver_directly is False
    assert t.annual_obligation_twhd > 0


def test_full_obligation_supplier():
    t = _tracker_full()
    assert t.must_deliver_directly is True
    assert t.annual_obligation_twhd > 0


def test_record_measure_adds_to_delivered():
    t = _tracker_full()
    m = EcoMeasure("ECO001", "cavity_wall_insulation", "C1", "1 Test St", "2024-03-01", 95.0, 1200.0, verified=True)
    t.record_measure(m)
    assert t.delivered_twhd() == 95.0


def test_unverified_not_counted():
    t = _tracker_full()
    m = EcoMeasure("ECO002", "loft_insulation_100mm", "C2", "2 Test St", "2024-03-01", 65.0, 500.0, verified=False)
    t.record_measure(m)
    assert t.delivered_twhd() == 0.0
    assert t.delivered_twhd_unverified() == 65.0


def test_shortfall_reduces_with_delivery():
    t = _tracker_full()
    full_shortfall = t.shortfall_twhd()
    m = EcoMeasure("ECO003", "solid_wall_insulation_external", "C3", "3 St", "2024-03-01", 290.0, 8000.0, verified=True)
    t.record_measure(m)
    assert t.shortfall_twhd() < full_shortfall


def test_completion_pct_zero_initially():
    t = _tracker_full()
    assert t.completion_pct() == 0.0


def test_status_breach_with_no_measures():
    t = _tracker_full()
    assert t.status() == "BREACH"


def test_measure_scores_catalogue():
    t = _tracker_full()
    scores = t.measure_scores()
    assert "cavity_wall_insulation" in scores
    assert scores["heat_pump_air_source"] > 0


def test_summary_structure():
    t = _tracker_full()
    s = t.summary()
    for k in ("annual_obligation_twhd", "delivered_twhd", "shortfall_twhd", "completion_pct", "status"):
        assert k in s


# --- Phase LE depth tests ---

def test_account_count_stored():
    t = EcoTracker(account_count=5000)
    assert t._account_count == 5000


def test_scheme_year_stored():
    t = EcoTracker(account_count=5000, scheme_year=2025)
    assert t._scheme_year == 2025


def test_small_supplier_pays_no_contribution():
    t = _tracker_small()
    assert t.pays_contribution is False


def test_full_must_deliver():
    t = _tracker_full()
    assert t.must_deliver_directly is True


def test_contribution_not_exempt():
    t = _tracker_contrib()
    assert t.is_exempt is False


def test_measure_id_stored():
    m = EcoMeasure('M_LE', 'loft_insulation_100mm', 'C1', 'Addr', '2024-01-01', 65.0, 500.0)
    assert m.measure_id == 'M_LE'


def test_measure_type_stored():
    m = EcoMeasure('M1', 'cavity_wall_insulation', 'C1', 'Addr', '2024-01-01', 95.0, 600.0)
    assert m.measure_type == 'cavity_wall_insulation'


def test_measure_customer_id_stored():
    m = EcoMeasure('M1', 'loft_insulation_100mm', 'C_LE', 'Addr', '2024-01-01', 65.0, 500.0)
    assert m.customer_id == 'C_LE'


def test_measure_score_stored():
    m = EcoMeasure('M1', 'loft_insulation_100mm', 'C1', 'Addr', '2024-01-01', 80.0, 500.0)
    assert m.score_twhd == 80.0


def test_eco_tracker_measures_empty_initially():
    t = EcoTracker(account_count=300_000)
    assert len(t._measures) == 0
