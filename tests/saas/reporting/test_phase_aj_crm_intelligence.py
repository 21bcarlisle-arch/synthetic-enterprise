"""Phase AJ: CRM Intelligence Risk Triage section tests."""
import pytest
from saas.reporting.annual_report import _section_crm_intelligence


def _cbr(cid, term_start, sim_p, co_est=0.0, rate_vs_svt=0.0):
    return {
        "customer_id": cid,
        "term_start": term_start,
        "sim_churn_probability": sim_p,
        "company_churn_estimate": co_est,
        "churn_estimate_error_pct": co_est - sim_p,
        "is_active_renewal": False,
        "unit_rate_gbp_per_mwh": 250.0,
        "svt_rate_gbp_per_mwh": 248.6,
        "rate_vs_svt_pct": rate_vs_svt,
    }


def _pcl(cid, segment="resi", net_margin=5000.0):
    return {
        "segment": segment,
        "net_margin_after_cost_to_serve_gbp": net_margin,
    }


def _data(cbr_entries, pcl_dict=None):
    return {
        "churn_basis_risk": cbr_entries,
        "per_customer_lifetime": pcl_dict or {},
    }


# ── 1. Empty churn_basis_risk returns empty string ──────────────────────────

def test_empty_returns_empty():
    assert _section_crm_intelligence({}) == ""
    assert _section_crm_intelligence({"churn_basis_risk": []}) == ""


# ── 2. Header present ────────────────────────────────────────────────────────

def test_header_present():
    data = _data([_cbr("C1", "2024-01-01", 0.35)])
    result = _section_crm_intelligence(data)
    assert "## CRM Intelligence: Risk Triage" in result


# ── 3. HIGH band for sim_p = 0.38 ────────────────────────────────────────────

def test_high_band_classification():
    data = _data([_cbr("C1", "2024-01-01", 0.38)])
    result = _section_crm_intelligence(data)
    assert "HIGH" in result
    assert "38%" in result


# ── 4. CRITICAL band for sim_p = 0.55 ────────────────────────────────────────

def test_critical_band_classification():
    data = _data([_cbr("C1", "2024-01-01", 0.55)])
    result = _section_crm_intelligence(data)
    assert "CRITICAL" in result
    assert "55%" in result


# ── 5. MEDIUM band for sim_p = 0.20 ──────────────────────────────────────────

def test_medium_band_classification():
    data = _data([_cbr("C1", "2024-01-01", 0.20)])
    result = _section_crm_intelligence(data)
    assert "MEDIUM" in result


# ── 6. LOW band for sim_p = 0.08 ─────────────────────────────────────────────

def test_low_band_classification():
    data = _data([_cbr("C1", "2024-01-01", 0.08)])
    result = _section_crm_intelligence(data)
    assert "LOW" in result


# ── 7. Latest renewal used (not all renewals) ────────────────────────────────

def test_uses_latest_renewal_per_customer():
    # C1 had HIGH risk in 2022, but LOW in 2025 — should show LOW
    entries = [
        _cbr("C1", "2022-03-01", 0.38),
        _cbr("C1", "2025-03-01", 0.08),
    ]
    data = _data(entries)
    result = _section_crm_intelligence(data)
    assert "LOW" in result
    # HIGH should not appear in the triage table row (only band summary for HIGH=0)
    lines = result.split("\n")
    table_rows = [l for l in lines if l.startswith("| C1")]
    assert len(table_rows) == 1
    assert "LOW" in table_rows[0]


# ── 8. Overpriced rate flag ───────────────────────────────────────────────────

def test_overpriced_rate_flag():
    data = _data([_cbr("C2_2", "2025-03-30", 0.38, rate_vs_svt=14.0)])
    result = _section_crm_intelligence(data)
    assert "overpriced" in result.lower() or "+14.0" in result


# ── 9. Competitive rate flag ──────────────────────────────────────────────────

def test_competitive_rate_flag():
    data = _data([_cbr("C8", "2024-03-01", 0.38, rate_vs_svt=-24.9)])
    result = _section_crm_intelligence(data)
    assert "competitive" in result.lower() or "-24.9" in result


# ── 10. Band summary counts ───────────────────────────────────────────────────

def test_band_summary_counts():
    entries = [
        _cbr("C1", "2025-01-01", 0.55),  # CRITICAL
        _cbr("C2", "2025-01-01", 0.38),  # HIGH
        _cbr("C3", "2025-01-01", 0.20),  # MEDIUM
        _cbr("C4", "2025-01-01", 0.08),  # LOW
    ]
    data = _data(entries)
    result = _section_crm_intelligence(data)
    assert "CRITICAL (>=50%): 1 accounts" in result
    assert "HIGH (>=30%): 1 accounts" in result
    assert "MEDIUM (>=15%): 1 accounts" in result
    assert "LOW (<15%): 1 accounts" in result


# ── 11. At-risk lifetime margin computed ─────────────────────────────────────

def test_lifetime_margin_at_risk():
    entries = [
        _cbr("C1", "2025-01-01", 0.38),  # HIGH
        _cbr("C2", "2025-01-01", 0.08),  # LOW
    ]
    pcl = {
        "C1": _pcl("C1", net_margin=10000.0),
        "C2": _pcl("C2", net_margin=5000.0),
    }
    data = _data(entries, pcl)
    result = _section_crm_intelligence(data)
    # Only C1 (HIGH) margin should be at-risk
    assert "10,000" in result
    assert "15,000" not in result  # C2 (LOW) should not be included


# ── 12. Company blind spot detected ──────────────────────────────────────────

def test_blind_spot_detected():
    entries = [
        _cbr("C8", "2024-03-01", 0.38, co_est=0.0),  # sim HIGH, company 0%
    ]
    data = _data(entries)
    result = _section_crm_intelligence(data)
    assert "Company blind spot" in result or "blind spot" in result.lower()
    assert "C8" in result


# ── 13. Missing per_customer_lifetime handled gracefully ─────────────────────

def test_missing_pcl_handled():
    data = _data([_cbr("C_NEW", "2025-01-01", 0.38)])
    result = _section_crm_intelligence(data)
    # Should not crash, segment shows "?"
    assert "C_NEW" in result
    assert "?" in result


# ── 14. No blind spot when company estimates correctly ────────────────────────

def test_no_blind_spot_when_company_accurate():
    entries = [
        _cbr("C1", "2025-01-01", 0.38, co_est=0.35),  # company close to sim
    ]
    data = _data(entries)
    result = _section_crm_intelligence(data)
    assert "blind spot" not in result.lower()
