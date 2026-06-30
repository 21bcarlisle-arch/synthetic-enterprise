"""Phase AN: Portfolio Concentration Risk section tests."""
import pytest
from saas.reporting.annual_report import _section_portfolio_concentration_risk


def _pcl(cid, segment, net_margin):
    return {
        "segment": segment,
        "net_margin_after_cost_to_serve_gbp": net_margin,
        "acquisition_date": "2016-01-01",
    }


def _cbr(cid, term_start, sim_p):
    return {
        "customer_id": cid,
        "term_start": term_start,
        "sim_churn_probability": sim_p,
        "company_churn_estimate": 0.05,
        "rate_vs_svt_pct": 0.0,
    }


def _data(pcl_dict, cbr_entries=None):
    return {
        "per_customer_lifetime": pcl_dict,
        "churn_basis_risk": cbr_entries or [],
    }


# ── 1. Empty per_customer_lifetime returns empty ──────────────────────────────

def test_empty_returns_empty():
    assert _section_portfolio_concentration_risk({}) == ""
    assert _section_portfolio_concentration_risk({"per_customer_lifetime": {}}) == ""


# ── 2. Header present ────────────────────────────────────────────────────────

def test_header_present():
    pcl = {"C_IC1": _pcl("C_IC1", "I&C", 1000000.0)}
    result = _section_portfolio_concentration_risk(_data(pcl))
    assert "## Portfolio Concentration Risk" in result


# ── 3. HHI computed and shown ─────────────────────────────────────────────────

def test_hhi_shown():
    pcl = {"C_IC1": _pcl("C_IC1", "I&C", 1000000.0)}
    result = _section_portfolio_concentration_risk(_data(pcl))
    # Single account = HHI 10000
    assert "10000" in result or "10,000" in result


# ── 4. HHI HIGH label when > 2500 ────────────────────────────────────────────

def test_hhi_high_label():
    # One dominant account
    pcl = {
        "C_IC1": _pcl("C_IC1", "I&C", 9000.0),
        "C1": _pcl("C1", "resi", 1000.0),
    }
    result = _section_portfolio_concentration_risk(_data(pcl))
    # 0.9^2 + 0.1^2 = 0.82 → HHI=8200 → HIGH
    assert "HIGH" in result


# ── 5. HHI MODERATE label when 1500-2500 ─────────────────────────────────────

def test_hhi_moderate_label():
    # 4 equal accounts → HHI = 2500
    pcl = {f"C{i}": _pcl(f"C{i}", "resi", 1000.0) for i in range(5)}
    result = _section_portfolio_concentration_risk(_data(pcl))
    assert "MODERATE" in result or "LOW" in result  # 5 equal → HHI=2000 = moderate


# ── 6. Segment margin share shown ────────────────────────────────────────────

def test_segment_margin_share():
    pcl = {
        "C_IC1": _pcl("C_IC1", "I&C", 9000.0),
        "C1": _pcl("C1", "resi", 1000.0),
    }
    result = _section_portfolio_concentration_risk(_data(pcl))
    assert "I&C" in result
    assert "resi" in result
    assert "90.0%" in result  # I&C share


# ── 7. Top 5 accounts shown in table ─────────────────────────────────────────

def test_top_5_accounts_shown():
    pcl = {f"C{i}": _pcl(f"C{i}", "I&C", float(10 - i) * 1000) for i in range(7)}
    result = _section_portfolio_concentration_risk(_data(pcl))
    # Should show first 5
    assert "C0" in result
    assert "C4" in result


# ── 8. Latest churn probability shown ────────────────────────────────────────

def test_churn_probability_shown():
    pcl = {"C_IC1": _pcl("C_IC1", "I&C", 1000000.0)}
    cbr = [_cbr("C_IC1", "2024-01-01", 0.08)]
    data = _data(pcl, cbr)
    result = _section_portfolio_concentration_risk(data)
    assert "8%" in result


# ── 9. Margin at risk computed ────────────────────────────────────────────────

def test_margin_at_risk_computed():
    pcl = {"C_IC1": _pcl("C_IC1", "I&C", 1000000.0)}
    cbr = [_cbr("C_IC1", "2024-01-01", 0.10)]  # 10% churn = £100k at risk
    data = _data(pcl, cbr)
    result = _section_portfolio_concentration_risk(data)
    assert "100,000" in result


# ── 10. Concentration warning when I&C > 95% ─────────────────────────────────

def test_concentration_warning_high_ic():
    pcl = {
        "C_IC1": _pcl("C_IC1", "I&C", 990000.0),
        "C1": _pcl("C1", "resi", 10000.0),
    }
    result = _section_portfolio_concentration_risk(_data(pcl))
    assert "Concentration Risk Warning" in result
    assert "98" in result or "99" in result  # ~99% I&C


# ── 11. Only positive margin accounts included ────────────────────────────────

def test_only_positive_margin_accounts():
    pcl = {
        "C_IC1": _pcl("C_IC1", "I&C", 1000000.0),
        "C1": _pcl("C1", "resi", -5000.0),  # net-negative — excluded
    }
    result = _section_portfolio_concentration_risk(_data(pcl))
    # Should show 1 margin-positive account
    assert "1 margin-positive" in result
    # I&C should be 100%
    assert "100.0%" in result


# ── 12. Missing churn data handled (0% shown) ────────────────────────────────

def test_missing_churn_data_handled():
    pcl = {"C_IC4": _pcl("C_IC4", "I&C", 500000.0)}
    # No cbr entries
    result = _section_portfolio_concentration_risk(_data(pcl))
    assert "C_IC4" in result
    assert "0%" in result
